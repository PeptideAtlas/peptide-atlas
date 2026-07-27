#!/usr/bin/env python3
"""Deterministisches Importwerkzeug fuer research_candidate_manifest (siehe ADR-0056).

Baut/aktualisiert die protokoll- und datenbankgebundenen Candidate Manifests unter
research/candidates/ aus den bereits versionierten research_search_result_manifest-Datensaetzen
(research/search_results/**) -- niemals umgekehrt. Erzeugt und setzt KEINE Screening-Entscheidung,
KEINE Evidenzbewertung und KEINE kanonische Quelle/Studie/Claim. Laedt ausschliesslich stabile
Identifikatoren und (im --refresh-metadata-Modus) sparsame technische/bibliographische Metadaten
ueber die offiziellen APIs -- niemals Volltexte oder PDFs.

Zwei getrennte Modi:

    python tools/build_research_candidates.py --from-manifests --protocol-id <id>
        Offline. Liest die Search Result Manifests des Protokolls, bildet je Datenbank die
        vollstaendige Vereinigungsmenge samt Suchlauf-Herkunft, und schreibt/aktualisiert das
        jeweilige Candidate Manifest unter research/candidates/. Bestehende candidate_id-Werte
        und bereits abgerufene Metadaten bleiben dabei fuer unveraendert entdeckte Identifikatoren
        erhalten (siehe find_existing_manifest). Wiederholte Ausfuehrung ohne geaenderte Eingaben
        erzeugt denselben fachlichen Output (updated_at bleibt in diesem Fall ebenfalls unveraendert).

    python tools/build_research_candidates.py --refresh-metadata --protocol-id <id>
        Online. Ruft fuer Kandidaten mit metadata_status: not_fetched/fetch_error Metadaten ueber
        NCBI ESummary (PubMed) bzw. die ClinicalTrials.gov API v2 (studies) ab. Ein fehlgeschlagener
        Abruf entfernt NIE die Discovery-Identitaet eines Kandidaten -- er setzt lediglich
        metadata_status: fetch_error/not_found mit einer knappen technischen Begruendung.

Sortierung ist deterministisch: numerisch aufsteigend fuer PMIDs, lexikografisch aufsteigend fuer
NCT-IDs (dieselbe Konvention wie research_search_result_manifest, siehe ADR-0055).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import load_yaml_file, normalize_pmcid  # noqa: E402
from _researchlib import NORMALIZERS, REPO_ROOT, RESEARCH_DIR  # noqa: E402

CANDIDATES_DIR = RESEARCH_DIR / "candidates"
SEARCH_RUNS_DIR = RESEARCH_DIR / "search_runs"
SEARCH_RESULTS_DIR = RESEARCH_DIR / "search_results"

DATABASE_TO_NAMESPACE = {"pubmed": "pmid", "clinicaltrials_gov": "nct_id"}

PUBMED_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
CTGOV_STUDIES_URL = "https://clinicaltrials.gov/api/v2/studies"

BATCH_SIZE = 50
REQUEST_TIMEOUT_SECONDS = 30
POLITE_DELAY_SECONDS = 0.4

# ISO 639-2/B (wie von NCBI ESummary im Feld "lang" geliefert) -> ISO 639-1 (wie von
# common.schema.json#/$defs/language_code verlangt). Bewusst nur eine kleine, dokumentierte
# Zuordnung haeufiger Sprachen -- ein unbekannter Code ergibt language: null statt eines
# geratenen Wertes.
LANG_639_2_TO_1 = {
    "eng": "en", "fre": "fr", "fra": "fr", "ger": "de", "deu": "de", "spa": "es", "ita": "it",
    "jpn": "ja", "chi": "zh", "zho": "zh", "por": "pt", "rus": "ru", "dut": "nl", "nld": "nl",
    "pol": "pl", "kor": "ko", "ara": "ar", "swe": "sv", "nor": "no", "dan": "da", "fin": "fi",
    "tur": "tr", "gre": "el", "ell": "el", "heb": "he", "hin": "hi", "cze": "cs", "ces": "cs",
}

_FULL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _today() -> str:
    return date.today().isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _http_get_json(url: str, params: dict) -> dict:
    query = "&".join(f"{key}={urllib.parse.quote(str(value), safe=',.')}" for key, value in params.items())
    request = urllib.request.Request(
        f"{url}?{query}", headers={"User-Agent": "peptide-atlas-research-tool/1.0 (build_research_candidates.py)"}
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _dump_yaml(data: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)


def find_existing_manifest(protocol_id: str, database: str) -> tuple[Path, dict] | None:
    """Sucht ein bereits vorhandenes Candidate Manifest fuer dieses Protokoll+Datenbank --
    liefert dessen Pfad und Inhalt, damit id/created_at/candidate_id/Metadaten erhalten
    bleiben statt bei jedem Lauf neu erzeugt zu werden (siehe Modulbeschreibung)."""
    if not CANDIDATES_DIR.exists():
        return None
    for path in sorted(CANDIDATES_DIR.glob("*.yaml")):
        data = load_yaml_file(path)
        if isinstance(data, dict) and data.get("protocol_id") == protocol_id and data.get("database") == database:
            return path, data
    return None


def collect_search_runs_and_manifests(protocol_id: str, database: str) -> list[tuple[str, dict]]:
    """Findet alle research_search_run-Datensaetze fuer dieses Protokoll+Datenbank sowie deren
    jeweils ueber result_capture.manifest_id verknuepftes research_search_result_manifest. Ein
    Suchlauf ohne vollstaendiges Manifest (result_capture.status: unavailable) traegt nichts bei."""
    search_runs: list[tuple[str, dict]] = []
    if SEARCH_RUNS_DIR.exists():
        for path in sorted(SEARCH_RUNS_DIR.glob("*.yaml")):
            data = load_yaml_file(path)
            if isinstance(data, dict) and data.get("protocol_id") == protocol_id and data.get("database") == database:
                search_runs.append((data.get("id") or path.stem, data))

    manifests_by_id: dict[str, dict] = {}
    if SEARCH_RESULTS_DIR.exists():
        for path in sorted(SEARCH_RESULTS_DIR.glob("*.yaml")):
            data = load_yaml_file(path)
            if isinstance(data, dict) and data.get("id"):
                manifests_by_id[data["id"]] = data

    resolved: list[tuple[str, dict]] = []
    for search_run_id, run_data in search_runs:
        manifest_id = (run_data.get("result_capture") or {}).get("manifest_id")
        manifest_data = manifests_by_id.get(manifest_id)
        if manifest_data is not None:
            resolved.append((search_run_id, manifest_data))
    return resolved


def build_candidate_manifest(protocol_id: str, database: str) -> tuple[dict, Path | None]:
    namespace = DATABASE_TO_NAMESPACE[database]
    normalize = NORMALIZERS[namespace]
    resolved = collect_search_runs_and_manifests(protocol_id, database)
    if not resolved:
        raise LookupError(
            f"no search run with a complete search result manifest found for protocol={protocol_id!r} "
            f"database={database!r}"
        )

    discovered: dict[str, set[str]] = {}
    raw_values: dict[str, str] = {}
    source_search_run_ids: set[str] = set()
    source_result_manifest_ids: set[str] = set()

    for search_run_id, manifest_data in resolved:
        source_search_run_ids.add(search_run_id)
        source_result_manifest_ids.add(manifest_data["id"])
        for raw_identifier in manifest_data.get("identifiers") or []:
            normalized = normalize(raw_identifier)
            discovered.setdefault(normalized, set()).add(search_run_id)
            raw_values.setdefault(normalized, raw_identifier)

    existing = find_existing_manifest(protocol_id, database)
    existing_path, existing_data = existing if existing else (None, {})
    existing_by_value: dict[str, dict] = {}
    for candidate in existing_data.get("candidates") or []:
        value = (candidate.get("primary_identifier") or {}).get("value")
        if value:
            existing_by_value[value] = candidate

    sorted_identifiers = sorted(discovered, key=int) if namespace == "pmid" else sorted(discovered)

    candidates = []
    for normalized in sorted_identifiers:
        raw_value = raw_values[normalized]
        existing_candidate = existing_by_value.get(raw_value)
        candidates.append({
            "candidate_id": (
                existing_candidate["candidate_id"] if existing_candidate else f"research-candidate-{uuid.uuid4()}"
            ),
            "primary_identifier": {"namespace": namespace, "value": raw_value},
            "discovered_in_search_run_ids": sorted(discovered[normalized]),
            "metadata": existing_candidate.get("metadata") if existing_candidate else None,
            "metadata_status": existing_candidate.get("metadata_status") if existing_candidate else "not_fetched",
            "metadata_fetch_note": existing_candidate.get("metadata_fetch_note") if existing_candidate else None,
            "metadata_provenance": existing_candidate.get("metadata_provenance") if existing_candidate else None,
        })

    manifest_id = existing_data.get("id") or f"candidate-manifest-{uuid.uuid4()}"
    created_at = existing_data.get("created_at") or _today()

    manifest = {
        "schema_version": "1.0.0",
        "id": manifest_id,
        "protocol_id": protocol_id,
        "database": database,
        "identifier_namespace": namespace,
        "source_search_run_ids": sorted(source_search_run_ids),
        "source_result_manifest_ids": sorted(source_result_manifest_ids),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "created_at": created_at,
        "updated_at": _today(),
    }

    if existing_data:
        unchanged = (
            manifest["source_search_run_ids"] == existing_data.get("source_search_run_ids")
            and manifest["source_result_manifest_ids"] == existing_data.get("source_result_manifest_ids")
            and manifest["candidate_count"] == existing_data.get("candidate_count")
            and manifest["candidates"] == existing_data.get("candidates")
        )
        if unchanged:
            manifest["updated_at"] = existing_data.get("updated_at")

    return manifest, existing_path


def write_manifest(manifest: dict, existing_path: Path | None) -> Path:
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    path = existing_path if existing_path else CANDIDATES_DIR / f"{manifest['id']}.yaml"
    _dump_yaml(manifest, path)
    return path


def _full_date_or_none(value) -> str | None:
    return value if isinstance(value, str) and _FULL_DATE_RE.match(value) else None


def _parse_pubmed_record(record: dict) -> dict:
    title = record.get("title") or None
    publication_year = None
    for date_field in ("sortpubdate", "pubdate", "epubdate"):
        value = record.get(date_field)
        if value:
            match = re.search(r"(1[89]\d{2}|20\d{2})", value)
            if match:
                publication_year = int(match.group(1))
                break
    journal = record.get("fulljournalname") or record.get("source") or None
    publication_types = list(record.get("pubtype") or [])
    doi = None
    pmcid = None
    for article_id in record.get("articleids") or []:
        idtype = article_id.get("idtype")
        if idtype == "doi" and not doi:
            doi = article_id.get("value") or None
        if idtype in ("pmc", "pmcid") and not pmcid and article_id.get("value"):
            pmcid = normalize_pmcid(article_id["value"])
    authors = [author.get("name") for author in record.get("authors") or [] if author.get("name")]
    abstract_available = "Has Abstract" in (record.get("attributes") or [])
    language = None
    langs = record.get("lang") or []
    if langs:
        language = LANG_639_2_TO_1.get(str(langs[0]).lower())
    return {
        "title": title,
        "publication_year": publication_year,
        "journal": journal,
        "publication_types": publication_types,
        "doi": doi,
        "pmcid": pmcid,
        "authors": authors,
        "abstract_available": abstract_available,
        "language": language,
    }


def _parse_ctgov_study(study: dict) -> dict:
    protocol = study.get("protocolSection") or {}
    identification = protocol.get("identificationModule") or {}
    status = protocol.get("statusModule") or {}
    sponsor_module = protocol.get("sponsorCollaboratorsModule") or {}
    design = protocol.get("designModule") or {}
    conditions_module = protocol.get("conditionsModule") or {}
    arms = protocol.get("armsInterventionsModule") or {}
    return {
        "brief_title": identification.get("briefTitle"),
        "official_title": identification.get("officialTitle"),
        "overall_status": status.get("overallStatus"),
        "phases": list(design.get("phases") or []),
        "sponsor": (sponsor_module.get("leadSponsor") or {}).get("name"),
        "interventions": [i.get("name") for i in arms.get("interventions") or [] if i.get("name")],
        "conditions": list(conditions_module.get("conditions") or []),
        "study_type": design.get("studyType"),
        "start_date": _full_date_or_none((status.get("startDateStruct") or {}).get("date")),
        "primary_completion_date": _full_date_or_none((status.get("primaryCompletionDateStruct") or {}).get("date")),
        "completion_date": _full_date_or_none((status.get("completionDateStruct") or {}).get("date")),
        "has_results": study.get("hasResults") if isinstance(study.get("hasResults"), bool) else None,
        "last_update_posted": _full_date_or_none((status.get("lastUpdatePostDateStruct") or {}).get("date")),
    }


def fetch_pubmed_batch(pmids: list[str]) -> dict[str, tuple[dict | None, str | None, dict]]:
    """Ruft ESummary fuer bis zu BATCH_SIZE PMIDs je HTTP-Anfrage ab. Liefert je PMID
    (metadata|None, fetch_note|None, metadata_provenance) -- ein fehlgeschlagener Request
    verliert dabei keine Kandidaten, sondern markiert jeden betroffenen PMID mit fetch_error."""
    results: dict[str, tuple[dict | None, str | None, dict]] = {}
    for start in range(0, len(pmids), BATCH_SIZE):
        chunk = pmids[start:start + BATCH_SIZE]
        retrieved_at = _now_iso()
        try:
            payload = _http_get_json(PUBMED_ESUMMARY_URL, {"db": "pubmed", "id": ",".join(chunk), "retmode": "json"})
            error: Exception | None = None
        except Exception as exc:  # noqa: BLE001 -- ein Netzwerkfehler darf Kandidaten nie verlieren
            payload = {}
            error = exc

        result_block = payload.get("result", {}) if not error else {}
        for pmid in chunk:
            provenance = {
                "source_interface": "NCBI E-utilities ESummary",
                "retrieved_at": retrieved_at,
                "request_reference": f"NCBI ESummary db=pubmed id={pmid} (batch size {len(chunk)})",
                "response_locator": None,
            }
            if error is not None:
                results[pmid] = (None, f"HTTP request failed: {error}", provenance)
            elif pmid not in result_block:
                results[pmid] = (None, "PMID not present in ESummary response (not found)", provenance)
            else:
                results[pmid] = (_parse_pubmed_record(result_block[pmid]), None, provenance)
        time.sleep(POLITE_DELAY_SECONDS)
    return results


def fetch_ctgov_batch(nct_ids: list[str]) -> dict[str, tuple[dict | None, str | None, dict]]:
    """Ruft die ClinicalTrials.gov API v2 fuer bis zu BATCH_SIZE NCT-IDs je HTTP-Anfrage ueber
    filter.ids ab. Liefert je NCT-ID (metadata|None, fetch_note|None, metadata_provenance)."""
    results: dict[str, tuple[dict | None, str | None, dict]] = {}
    for start in range(0, len(nct_ids), BATCH_SIZE):
        chunk = nct_ids[start:start + BATCH_SIZE]
        retrieved_at = _now_iso()
        try:
            payload = _http_get_json(
                CTGOV_STUDIES_URL, {"filter.ids": ",".join(chunk), "format": "json", "pageSize": len(chunk)}
            )
            error: Exception | None = None
        except Exception as exc:  # noqa: BLE001 -- ein Netzwerkfehler darf Kandidaten nie verlieren
            payload = {}
            error = exc

        studies_by_id: dict[str, dict] = {}
        if not error:
            for study in payload.get("studies") or []:
                nct_id = ((study.get("protocolSection") or {}).get("identificationModule") or {}).get("nctId")
                if nct_id:
                    studies_by_id[nct_id] = study

        for nct_id in chunk:
            provenance = {
                "source_interface": "ClinicalTrials.gov API v2",
                "retrieved_at": retrieved_at,
                "request_reference": f"ClinicalTrials.gov API v2 studies filter.ids batch (n={len(chunk)})",
                "response_locator": None,
            }
            if error is not None:
                results[nct_id] = (None, f"HTTP request failed: {error}", provenance)
            elif nct_id not in studies_by_id:
                results[nct_id] = (None, "NCT ID not present in API v2 response (not found)", provenance)
            else:
                results[nct_id] = (_parse_ctgov_study(studies_by_id[nct_id]), None, provenance)
        time.sleep(POLITE_DELAY_SECONDS)
    return results


def _classify_completeness(database: str, metadata: dict) -> str:
    if database == "pubmed":
        core_ok = bool(metadata.get("title")) and metadata.get("abstract_available") is not None
    else:
        core_ok = (
            bool(metadata.get("brief_title"))
            and bool(metadata.get("overall_status"))
            and metadata.get("has_results") is not None
        )
    return "fetched" if core_ok else "partial"


def refresh_metadata(protocol_id: str, database: str) -> None:
    found = find_existing_manifest(protocol_id, database)
    if found is None:
        print(f"no candidate manifest found for protocol={protocol_id!r} database={database!r}, skipping")
        return
    path, data = found
    candidates = data.get("candidates") or []
    to_refresh = [
        candidate["primary_identifier"]["value"] for candidate in candidates
        if candidate.get("metadata_status") in ("not_fetched", "fetch_error")
    ]
    if not to_refresh:
        print(f"{path.name}: nothing to refresh ({len(candidates)} candidate(s) already fetched/partial/not_found)")
        return

    fetched = fetch_pubmed_batch(to_refresh) if database == "pubmed" else fetch_ctgov_batch(to_refresh)

    changed = False
    for candidate in candidates:
        value = candidate["primary_identifier"]["value"]
        if value not in fetched:
            continue
        metadata, note, provenance = fetched[value]
        changed = True
        candidate["metadata_provenance"] = provenance
        if metadata is not None and note is None:
            candidate["metadata"] = metadata
            candidate["metadata_fetch_note"] = None
            candidate["metadata_status"] = _classify_completeness(database, metadata)
        else:
            candidate["metadata"] = None
            candidate["metadata_fetch_note"] = note or "unknown fetch error"
            candidate["metadata_status"] = "fetch_error" if note and "HTTP request failed" in note else "not_found"

    if changed:
        data["updated_at"] = _today()
        _dump_yaml(data, path)
    print(f"{path.name}: refreshed metadata for {len(to_refresh)} candidate(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--protocol-id", required=True, help="z. B. research-protocol-retatrutide-v1")
    parser.add_argument(
        "--database", choices=sorted(DATABASE_TO_NAMESPACE), default=None,
        help="Beschraenkt auf eine Datenbank (Default: pubmed UND clinicaltrials_gov)",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--from-manifests", action="store_true",
        help="Offline: baut/aktualisiert Candidate Manifests aus den vorhandenen Search Result Manifests",
    )
    mode.add_argument(
        "--refresh-metadata", action="store_true",
        help="Online: ruft fehlende Metadaten ueber die offiziellen APIs ab",
    )
    args = parser.parse_args(argv)

    databases = [args.database] if args.database else list(DATABASE_TO_NAMESPACE)

    if args.from_manifests:
        for database in databases:
            try:
                manifest, existing_path = build_candidate_manifest(args.protocol_id, database)
            except LookupError as exc:
                print(str(exc))
                continue
            path = write_manifest(manifest, existing_path)
            action = "updated" if existing_path else "created"
            print(f"{path.relative_to(REPO_ROOT).as_posix()}: {manifest['candidate_count']} candidate(s) ({action})")
    else:
        for database in databases:
            refresh_metadata(args.protocol_id, database)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

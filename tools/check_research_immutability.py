#!/usr/bin/env python3
"""Prueft, dass bereits committete research/search_runs/**.yaml-Dateien nicht rueckwirkend
veraendert werden (siehe Scientific Research Protocol, Abschnitt 7: ein Suchlauf wird nie
nachtraeglich veraendert -- eine Korrektur oder Wiederholung erhaelt eine neue id).

Vergleicht den aktuellen Arbeitsbaum (inkl. noch nicht committeter Aenderungen) gegen den
Merge-Base mit einem Basis-Ref (typischerweise der Zielbranch eines Pull Requests). Erlaubt
sind ausschliesslich Aenderungen an status/updated_at/review/notes. Jede Aenderung an einem
Ausfuehrungsfeld (id, schema_version, protocol_id, database, interface, executed_at,
executed_by, exact_query, filters, date_range, result_count, export_reference) sowie das
Loeschen oder Umbenennen einer bereits committeten Datei ist ein Fehler.

Bekannte Grenze (siehe Scientific Research Protocol, Abschnitt 34): dieser Check vergleicht
nur gegen einen einzelnen Basis-Ref und erkennt daher keine Manipulation, die bereits vor
diesem Vergleichszeitpunkt auf dem Zielbranch selbst stattgefunden hat, und keine Historie
ueber mehrere aufeinanderfolgende Commits hinweg (nur den Nettounterschied zum Merge-Base).
Er ersetzt keine serverseitige Branch Protection auf `main` und laeuft nur sinnvoll, wenn der
Basis-Ref lokal aufloesbar ist (in CI: `fetch-depth: 0` beim Checkout noetig). Ist der Basis-Ref
nicht aufloesbar (z. B. lokaler Push-Build ohne PR-Kontext), wird der Check uebersprungen statt
hart zu scheitern -- kein falscher Alarm, aber auch keine Garantie in diesem Fall.

Exitcode 0 bei Erfolg oder wenn der Check uebersprungen wurde, 1 bei mindestens einer Verletzung.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import DataFileError, load_yaml_file  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SEARCH_RUNS_PATHSPEC = "research/search_runs"

MUTABLE_FIELDS = {"status", "updated_at", "review", "notes"}


class GitError(RuntimeError):
    pass


def _run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def find_merge_base(repo_root: Path, base_ref: str) -> str:
    return _run_git(repo_root, ["merge-base", base_ref, "HEAD"]).strip()


def diff_status(repo_root: Path, merge_base: str) -> list[tuple[str, str]]:
    """Liefert (status, path)-Paare fuer research/search_runs/** zwischen merge_base und dem
    aktuellen Arbeitsbaum (inkl. noch nicht committeter Aenderungen). --no-renames sorgt
    dafuer, dass eine Umbenennung als Loeschen + Hinzufuegen erscheint, nicht als 'R' --
    Umbenennen einer bereits committeten Suchlaufdatei soll denselben Fehler ausloesen wie
    ein Loeschen."""
    output = _run_git(
        repo_root, ["diff", "--no-renames", "--name-status", merge_base, "--", SEARCH_RUNS_PATHSPEC]
    )
    entries = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        entries.append((parts[0][0], parts[-1]))
    return entries


def load_at_ref(repo_root: Path, ref: str, path: str):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=repo_root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return None
    return yaml.safe_load(result.stdout)


def check(repo_root: Path, base_ref: str) -> list[str]:
    errors: list[str] = []
    merge_base = find_merge_base(repo_root, base_ref)

    for status, path in diff_status(repo_root, merge_base):
        if not path.endswith((".yaml", ".yml")):
            continue

        if status == "D":
            errors.append(
                f"{path}: already-committed search run file was deleted or renamed -- search runs are "
                "immutable, a correction or repeated search run must get a new id instead"
            )
            continue
        if status == "A":
            continue
        if status == "M":
            old_data = load_at_ref(repo_root, merge_base, path)
            new_path = repo_root / path
            if old_data is None or not new_path.exists():
                continue
            try:
                new_data = load_yaml_file(new_path)
            except DataFileError as exc:
                errors.append(f"{path}: could not parse working tree version: {exc}")
                continue
            if not isinstance(old_data, dict) or not isinstance(new_data, dict):
                continue
            changed_keys = {
                key for key in set(old_data) | set(new_data) if old_data.get(key) != new_data.get(key)
            }
            disallowed = changed_keys - MUTABLE_FIELDS
            if disallowed:
                errors.append(
                    f"{path}: modifies execution field(s) {sorted(disallowed)} of an already-committed "
                    "search run -- only status/updated_at/review/notes may change; a corrected or "
                    "repeated search run must get a new id instead"
                )
            continue
        errors.append(f"{path}: unexpected git status '{status}' for a committed search run file")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--base-ref", default=None,
        help="Vergleichsbasis (z. B. origin/main). Fallback: $GITHUB_BASE_REF (mit 'origin/'-Praefix), "
             "sonst 'origin/main'.",
    )
    args = parser.parse_args(argv)

    base_ref = args.base_ref
    if not base_ref:
        gh_base = os.environ.get("GITHUB_BASE_REF")
        base_ref = f"origin/{gh_base}" if gh_base else "origin/main"

    try:
        errors = check(REPO_ROOT, base_ref)
    except GitError as exc:
        print(f"could not compute diff against '{base_ref}': {exc}")
        print("skipping immutability check (no resolvable base ref, e.g. a non-PR build)")
        return 0

    for error in errors:
        print(f"ERROR {error}")

    if errors:
        print()
        print(f"{len(errors)} immutability violation(s) in research/search_runs/**")
        return 1

    print("No immutability violations in research/search_runs/**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

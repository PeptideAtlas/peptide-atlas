---
title: Decision Log
description: Protokoll getroffener und vorgeschlagener Architekturentscheidungen für Peptide Atlas.
tags:
  - Architektur
  - Projekt
---

# Decision Log

Kurze, strukturierte Architecture Decision Records (ADRs): Kontext, Entscheidung, Konsequenz. Neue Entscheidungen werden **angehängt**, bestehende Einträge werden nicht rückwirkend verändert — bei Revision wird ein neuer Eintrag ergänzt, der auf den alten verweist.

| ID | Titel | Status | Kurzfassung |
|---|---|---|---|
| ADR-0001 | MkDocs Material statt individuellem Framework | Entschieden (v0.1) | Ausgereiftes, wartungsarmes Static-Site-Framework mit nativer Suche/Tags/Theming — passend zu einer reinen Content-Plattform ohne Backend-Bedarf. |
| ADR-0002 | GitHub Actions Deployment statt `gh-pages`-Branch | Entschieden (v0.1) | Modernere offizielle Methode (`upload-pages-artifact`/`deploy-pages`), kein separater Branch, kein zusätzliches Push-Token nötig. |
| ADR-0003 | Deutschsprachiger Content, englische Fachbegriffe erlaubt | Entschieden (v0.1) | Zielgruppe ist primär deutschsprachig; etablierte englische Fachtermini (GPCR, Research Peptide …) werden nicht künstlich eingedeutscht. |
| ADR-0004 | Evidenzsystem A–E als verbindliches Bewertungsschema | Entschieden (v0.1) | Einheitliche, einfache Klassifikation der Belegstärke, siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md). |
| ADR-0005 | Architektur-Dokumente in `docs/project/` mit eigener Namenskonvention | Entschieden (v0.2) | `PascalCase_With_Underscores.md` als bewusste Ausnahme zur sonstigen `lowercase_snake_case`-Konvention der Content-Dateien — explizit vorgegebenes Format für diese Dokumentkategorie, siehe [Naming Conventions](Naming_Conventions.md). Empfehlung: langfristig vereinheitlichen, aber nicht isoliert deswegen migrieren. |
| ADR-0006 | Mermaid-Diagramme aktiviert | Entschieden (v0.2) | `pymdownx.superfences` um `custom_fences` für `mermaid` ergänzt, um Architektur- und Graph-Diagramme direkt in Markdown darstellen zu können — keine externe Abhängigkeit, da in MkDocs Material bereits gebündelt. |
| ADR-0007 | Markdown+Frontmatter bleibt vorerst alleinige Source of Truth | Entschieden (v0.2) | Strukturierte Daten (`data/*.json`) und Knowledge Graph werden **abgeleitet**, nicht umgekehrt. Verhindert doppelte Pflege und Synchronisationsprobleme, solange kein konkreter Anwendungsfall eine andere Quelle erfordert. Siehe [Architecture](Architecture.md), [Knowledge Graph](Knowledge_Graph.md). |
| ADR-0008 | Evidenz wird an Beziehungen (Edges), nicht an Objekten (Nodes) verankert | Entschieden (v0.2) | Ein Objekt wie ein Wirkstoff hat keine einzelne Evidenzstufe — jede einzelne Aussage/Beziehung über ihn hat ihre eigene. Siehe [Data Model](Data_Model.md). |
| ADR-0009 | Neuer Status `Zurückgezogen` vorgeschlagen | Vorgeschlagen, nicht umgesetzt (v0.2) | Ergänzung zum bestehenden Status-Schema (`Entwurf`/`In Prüfung`/`Aktiv`) im [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md), für veraltete/widerrufene, aber aus Transparenzgründen weiter sichtbare Artikel. Muss vor Einführung mit der Redaktion abgestimmt werden. |
| ADR-0010 | Branch-Protection auf `main` empfohlen | Vorgeschlagen, nicht umgesetzt | Repository ist öffentlich, `main` deployt automatisch — Pflicht-Review und Pflicht-CI-Check werden empfohlen. Umsetzung liegt bei der Repository-Administration, siehe [Workflow](Workflow.md). |
| ADR-0011 | `data/catalog.json` perspektivisch in typ-spezifische Dateien aufteilen | Vorgeschlagen, nicht umgesetzt | Statt eines einzelnen Katalogs künftig z. B. `data/drugs.json`, `data/receptors.json` gemäß [Data Model](Data_Model.md) — erst sinnvoll, sobald reale Einträge entstehen. |
| ADR-0012 | `CHANGELOG.md` einführen | Vorgeschlagen, nicht umgesetzt | Aktuell fehlt eine zusammenfassende Änderungsdokumentation auf Repository-Ebene, siehe [Versioning](Versioning.md). Empfohlen ab v0.3. |
| ADR-0013 | `LICENSE`-Datei ergänzen | Vorgeschlagen, nicht umgesetzt | Repository ist öffentlich, aber unlizenziert (bestätigt über GitHub-API, 404 auf `/license`). Rechtlich zu klären, bevor Dritte substanziell beitragen oder Inhalte nachnutzen. |
| ADR-0014 | Frontmatter-/Schema-Validator als CI-Schritt | Vorgeschlagen, nicht umgesetzt | Automatisierte Prüfung der Pflichtfelder aus [Quality Standards](Quality_Standards.md) — technisch sinnvoll, aber erst mit wachsender Artikelzahl priorisiert. |
| ADR-0015 | `substance` statt getrennter `Peptide`/`Drug`-Objekte | Entschieden (Phase 3) | Vereinheitlichtes Objekt mit `substance_classes` statt separater Typen aus [Data Model](Data_Model.md), verhindert Doppelanlage desselben Moleküls. Ein konkretes Markenprodukt folgt später als eigenes `medicinal_product`-Objekt (nicht Teil von Phase 3). Siehe [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md). |
| ADR-0016 | Claim als zentrales wissenschaftliches Objekt; Evidenzkategorie und Sicherheit getrennt bewertet | Entschieden (Phase 3) | Setzt ADR-0008 konkret um und löst das einteilige A–E-Modell für neue Claims ab: sieben Evidenzkategorien (`established_knowledge` … `personal_experience`) plus separat und redaktionell vergebenes `certainty`. Siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md), [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md). |
| ADR-0017 | Eine YAML-Datei pro kanonischem Objekt, Quelle und Claim; JSON/Graph deterministisch generiert | Entschieden (Phase 3) | Setzt ADR-0007 technisch um. Ausführliches ADR mit Alternativenvergleich siehe Abschnitt „Ausführliche ADRs" unten. |
| ADR-0018 | `evidenzstufe` als veraltetes Legacy-Feld markiert | Entschieden (Phase 3) | Validator gibt eine Deprecation-Warnung aus, kein Build-Abbruch. Neue wissenschaftliche Objektseiten bewerten Evidenz claim-basiert über `entity_id`/`claim_ids` statt einer pauschalen Artikel-Evidenznote. Vollständige Entfernung frühestens Phase 4. Siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md). |
| ADR-0019 | Artikel-Frontmatter-Status bleibt deutsch; Datenebene (`data/**`) nutzt englische Statuswerte | Entschieden (Phase 3) | Löst einen Konflikt zwischen dem Prinzip „maschinenlesbare Enums englisch, Anzeige deutsch" und der bestehenden, redaktionell direkt bearbeiteten deutschen Frontmatter-Konvention (siehe [Naming Conventions](Naming_Conventions.md)). Artikel-Status bleibt `Entwurf`/`In Prüfung`/`Aktiv`/`Zurückgezogen`; die neue Datenebene nutzt `draft`/`in_review`/`active`/`withdrawn` mit deutschen Anzeigenamen aus `data/vocabularies/editorial_statuses.yaml`. Keine Migration bestehender Artikel-Frontmatter-Statuswerte. |
| ADR-0020 | `data/catalog.json` entfernt, ersetzt durch generiertes `build/catalog.json` | Entschieden (Phase 3) | Setzt ADR-0011 um: das leere Phase-1-Gerüst wird gelöscht, der Katalog wird bei jedem Build aus `data/**` generiert und nicht committed (siehe `.gitignore`). |
| ADR-0021 | CI validiert Daten und Tests vor `mkdocs build --strict`; Deploy-Workflow gleichermaßen abgesichert | Entschieden (Phase 3) | Setzt ADR-0014 um: neuer `.github/workflows/ci.yml` für Pull Requests; `deploy.yml` um `validate_data.py` und `pytest` vor dem Seiten-Build erweitert. Ein ungültiger wissenschaftlicher Datensatz wird dadurch nie auf GitHub Pages veröffentlicht. |
| ADR-0022 | Indikation als Claim statt eigenes Objekt; `condition` für Erkrankung/Zustand | Entschieden (Phase 3) | Verhindert ein redundantes Indikationsobjekt pro Substanz-Erkrankung-Kombination. „Zugelassen für"/„untersucht für" werden als Claims (`approved_for`/`not_approved_for`/`studied_for`) modelliert, die Erkrankung selbst als eigenständiges `condition`-Objekt. |
| ADR-0023 | Reduzierter Objekttyp-Katalog für Phase 3 (sieben Entitätstypen statt der vollen Data-Model-Liste) | Entschieden (Phase 3) | Konsolidierung bzw. Zurückstellung mehrerer in [Data Model](Data_Model.md) skizzierter Objekttypen (Publication/Journal/Author, Institution/Company/Agency, Target/Mechanism, Gene, Organ/Tissue/Biomarker, Country) zugunsten der einfachsten belastbaren Lösung für den aktuellen Bedarf. Details je Typ siehe [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md). |
| ADR-0024 | Whitelist für `source_requirement: exempt`; Begründungsfelder schema-seitig erzwungen | Entschieden (Phase 3, Review-Härtung) | Nach wissenschaftlichem Review konnte ein aktiver medizinischer Claim die Quellenpflicht mit `source_exemption_reason: null` umgehen. Behoben: `certainty_rationale` und `source_exemption_reason` müssen (wo gefordert) nicht-leere Strings sein (JSON-Schema-`if`/`then` mit `minLength`), und `source_requirement: exempt` ist strukturell auf `claim_type: identity`/`classification` beschränkt — medizinisch relevante Claimtypen (`mechanism` … `comparison`) können nie ausgenommen werden. |
| ADR-0025 | Evidenzkategorie muss zum tatsächlichen Quellentyp passen; `claimed_by`/`reported_by` für attribuierte Aussagen | Entschieden (Phase 3, Review-Härtung) | Ein Claim, dessen einzige Quellen `merchant_page`/`personal_report` sind, muss als `merchant_claim`/`personal_experience` klassifiziert sein — unabhängig von Status oder `certainty`; eine „bessere" Kategorie darf eine schwache Quellenlage nicht verschleiern. Aktive, medizinisch relevante Claims dürfen nie ausschließlich auf solchen Quellen beruhen, unabhängig von `certainty`. Für legitime attribuierte Aussagen („Händler X behauptet Y") wurden die Prädikate `claimed_by`/`reported_by` ergänzt (`data/vocabularies/predicates.yaml`) — modelliert als `claim_type: other`, nicht als wissenschaftlicher Wirksamkeits-/Sicherheits-/Mechanismusclaim. |
| ADR-0026 | Quellen-Deduplizierung über normalisierte externe Kennungen | Entschieden (Phase 3, Review-Härtung) | Zwei Source-Dateien mit demselben DOI/PMID/PMCID/ISBN unter verschiedenen IDs blieben bisher unentdeckt. `tools/validate_data.py` normalisiert diese Kennungen (Groß-/Kleinschreibung, DOI-URL-Form, führende Nullen bei PMID, `PMC`-Präfix, ISBN-Trennzeichen) und meldet Kollisionen als Fehler; identische kanonische URLs nur als Warnung, da Redirects/Mirrors legitime Abweichungen erzeugen können. |
| ADR-0027 | `schema_version` in Phase 3 auf `"1.0.0"` fixiert | Entschieden (Phase 3, Review-Härtung) | Bislang akzeptierte das Schema jede syntaktisch gültige SemVer-Zeichenkette als `schema_version`, auch `"2.0.0"` ohne existierenden Migrationspfad. `common.schema.json` erzwingt jetzt `const: "1.0.0"`; eine künftige Schema-Version erfordert einen dokumentierten Migrationspfad (siehe [Versioning](Versioning.md)) statt stillschweigender Akzeptanz. |
| ADR-0028 | Reviewmetadaten für Quellen; echte Kalenderdatumsprüfung | Entschieden (Phase 3, Review-Härtung) | `source.schema.json` erhält `created_at`/`updated_at`/`review` analog zu Entitäten und Claims; `status: active` erfordert Reviewdatum und Reviewer. Zusätzlich erzwingt ein aktivierter `jsonschema.FormatChecker` (`format: date`) echte Kalenderdaten — das bisherige Regex-Pattern akzeptierte auch nicht existierende Daten wie `2026-02-31`. |
| ADR-0029 | Fehlendes Artikel-Frontmatter ist ein Fehler, keine stille Auslassung | Entschieden (Phase 3, Review-Härtung) | Der Validator übersprang Content-Artikel ohne YAML-Frontmatter bisher stillschweigend. Außerhalb der dokumentierten Ausnahmen (`docs/project/**`, `index.md`, `tags.md`) erzeugt fehlendes Frontmatter jetzt einen verständlichen Fehler. |
| ADR-0030 | Zusätzliche Evidenzintegrität: Richtung und Teil-Retraktion | Entschieden (Phase 3, Review-Härtung) | Ein aktiver Claim benötigt jetzt mindestens einen Evidenzlink mit `direction: supports`/`mixed` (sonst stützt nichts die Aussage). Nutzt ein aktiver Claim mindestens eine zurückgezogene Quelle neben weiteren, gültigen Quellen, warnt der Validator (vollständig zurückgezogene Evidenz bleibt ein Fehler, unverändert aus Phase 3 v1). |
| ADR-0031 | Vokabular-/Schema-Duplikation als dokumentierte technische Schuld, gegen Drift abgesichert | Entschieden (Phase 3, Review-Härtung) | Statt die Schemas in diesem Härtungscommit vollständig auf dynamisch aus `data/vocabularies/*.yaml` generierte Enums umzustellen (unverhältnismäßiger Umfang für diesen Commit), sichert `tests/test_vocabulary_consistency.py` die bestehende Doppelpflege ab: der Test vergleicht jedes doppelt gepflegte Enum (evidence_category, certainty_level, evidence_direction, study_design, editorial_status, source_type, entity_type, substance_classes) gegen sein Vokabular und schlägt fehl, sobald beide Seiten auseinanderlaufen. Echte Konsolidierung bleibt für eine spätere Phase vorgemerkt. |
| ADR-0032 | Quellenpflicht für aktive Claims gilt für jeden `claim_type`, nicht nur für `MEDICALLY_RELEVANT_CLAIM_TYPES` | Entschieden (Phase 3, Review-Härtung Runde 3) | Die bisherige Regel prüfte fehlende Evidenz nur bei Claimtypen aus `MEDICALLY_RELEVANT_CLAIM_TYPES` — ein aktiver Claim vom Typ `structure`, `historical` oder `other` mit `source_requirement: required` und leerem `evidence[]` blieb dadurch unbeanstandet. Die Regel gilt jetzt für **jeden** aktiven Claim mit `source_requirement: required` (dem Standardwert), unabhängig vom `claim_type`. Die Whitelist aus ADR-0024 (nur `identity`/`classification` dürfen `source_requirement: exempt` mit Begründung verwenden) bleibt unverändert die einzige Ausnahme. Die Fehlermeldung empfiehlt nicht mehr, `source_requirement: exempt` zu setzen, da das für die meisten Claimtypen ausdrücklich verboten ist. |
| ADR-0033 | `research/**` als separate Provenienz- und Arbeitsdatenebene neben `data/**` | Entschieden (Phase 4A) | Rechercheverlauf, Kandidaten, Screening und Extraktion sind wichtig für Auditierbarkeit, aber nicht identisch mit kanonischem Wissen. Ausführliches ADR siehe Abschnitt „Ausführliche ADRs" unten. |
| ADR-0034 | Studie und Publikation bleiben getrennte Objekte; mehrere Publikationen dürfen nicht als mehrere Studien gezählt werden | Entschieden (Phase 4A) | Setzt die bereits in [Data Model](Data_Model.md) angelegte Trennung für die Recherche-Ebene konsequent fort. Ausführliches ADR siehe unten. |
| ADR-0035 | Automatisierte Extraktion und KI dürfen keine aktiven kanonischen Claims freigeben | Entschieden (Phase 4A) | Kernregel des [Evidence Curation Workflow](Evidence_Curation_Workflow.md): kein Werkzeug in Phase 4A schreibt `status: active` in `data/claims/**`. Ausführliches ADR siehe unten. |
| ADR-0036 | Protokoll- und Referenzkonsistenz strukturell erzwungen (Version/ID, Suchlauf-Freigabestatus, protokollübergreifende Ketten, `discovery_only`) | Entschieden (Phase 4A, Review-Härtung) | `tools/validate_research.py` erzwingt jetzt: `protocol.version` muss dem `-vN`-Suffix der `id` entsprechen; ein `search_run` darf nur gegen ein Protokoll mit Status `approved`/`superseded` ausgeführt werden; `screening_record`/`search_run` sowie `extraction_record`/`screening_record` müssen jeweils dieselbe `protocol_id` tragen; widersprechende `canonical_source_id` zwischen Screening und Extraktion ist ein Fehler. `google_scholar`/`manufacturer_registry` sind jetzt schema-seitig (nicht mehr nur redaktionell) auf `role: discovery_only` beschränkt. Ausführliches ADR siehe unten. |
| ADR-0037 | Vollständige Screening-Historie (`decision_history`) und maschinenlesbare Claim-Promotion-Kette (`promotion_record`) | Entschieden (Phase 4A, Review-Härtung) | Löst zwei bislang nur behauptete, aber nicht durchgesetzte Aussagen der Phase-4A-Dokumentation strukturell ein. Ausführliches ADR siehe unten. |
| ADR-0038 | Eigenständiges `search_run_status`-Vokabular; CI-Check gegen rückwirkende Suchlauf-Änderungen (mit dokumentierter Grenze) | Entschieden (Phase 4A, Review-Härtung) | `research_search_run.status` nutzt nicht mehr `editorial_status` (`draft`/`in_review`/`active`/`withdrawn`), sondern ein eigenes Vokabular (`executed`/`superseded`/`withdrawn`), das zum Ereignischarakter eines Suchlaufs passt. `tools/check_research_immutability.py` prüft in CI zusätzlich, dass bereits committete `research/search_runs/**`-Dateien nur in `status`/`updated_at`/`review`/`notes` verändert werden. Ausführliches ADR siehe unten. |
| ADR-0039 | Echte Identifier-Deduplizierung und strukturelle Zwei-Personen-Kontrolle (Dual-Reviewer, Adjudikation, Extraktionsverifikation) | Entschieden (Phase 4A, Review-Härtung) | Die in der Dokumentation seit Phase 4A behauptete Identifier-Normalisierung und Zweitprüfung war bislang nicht tatsächlich implementiert. `tools/validate_research.py` erkennt jetzt normalisierte DOI/PMID/PMCID/NCT-ID-Kollisionen innerhalb desselben Protokolls, erzwingt `second_review` in `screening_policy.dual_reviewer_stages`, Reviewer-Unabhängigkeit, eine kontrollierte Konfliktlösung (Adjudikation durch eine dritte Person oder `decision: uncertain`) sowie `verified_by != extracted_by`, sofern `extraction_policy.verification_required: true`. Ausführliches ADR siehe unten. |

## Ausführliche ADRs

### ADR-0017: Eine YAML-Datei pro kanonischem Objekt, Quelle und Claim; JSON/Graph deterministisch generiert

- **Status:** Entschieden
- **Datum:** 2026-07-24
- **Kontext:** Phase 2 hatte festgelegt, dass strukturierte Daten und der Knowledge Graph aus einer Source of
  Truth abgeleitet werden, ohne die technische Umsetzung festzulegen (ADR-0007). Phase 3 muss diese Umsetzung
  konkretisieren: Peptide Atlas soll langfristig mindestens 5.000 Fachartikel und 100.000 Quellen tragen können,
  mit nachvollziehbarer Historie, geringen Merge-Konflikten bei parallelen redaktionellen Beiträgen und ohne
  Datenbankbetrieb (Prinzip „Static-First", siehe [Architecture](Architecture.md)).
- **Entscheidung:** Jedes kanonische Objekt (Entität, Studie, Quelle, Claim) wird als eigene YAML-Datei unter
  `data/**` geführt, validiert gegen JSON Schema (Draft 2020-12). `build/catalog.json` und `build/graph.json`
  werden bei jedem Build deterministisch aus diesen Dateien generiert, nicht committed und dienen als Grundlage
  für eine künftige read-only API.
- **Alternativen:**
    1. *Markdown bleibt alleinige Source of Truth* — verworfen: maschinenlesbare Fakten (Evidenzkategorie,
       Studiendesign, Quellen-IDs) lassen sich aus Freitext nicht zuverlässig und ohne Duplizierung ableiten;
       widerspricht dem data-first Hybridmodell (siehe [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md)).
    2. *Ein einzelnes großes `catalog.json`* — verworfen: bei 5.000+ Objekten führt jede Änderung zu einem
       Merge-Konflikt auf derselben Datei; keine granulare Git-Historie pro Objekt; schlecht in Pull Requests
       reviewbar.
    3. *Relationale Datenbank* — verworfen: erfordert Datenbankbetrieb, widerspricht dem Static-First-Prinzip
       und macht Peptide Atlas von einer laufenden Infrastruktur abhängig, ohne dass ein konkreter Schreibfall
       (Nutzeranmeldung, Transaktionen) das erfordert.
    4. *Graphdatenbank (z. B. Neo4j)* — verworfen: zusätzliche Infrastruktur, zusätzlicher Betriebsaufwand, für
       die aktuelle Lese-/Export-Anforderung nicht nötig; ein statischer, deterministischer JSON-Graphexport
       genügt (siehe [Knowledge Graph](Knowledge_Graph.md)).
    5. *Eine YAML-Datei pro Objekt plus generierte JSON-Exporte* — **gewählt**.
- **Konsequenzen:** Geringe Merge-Konflikte, gute Reviewbarkeit in Pull Requests, granulare Git-Historie pro
  Objekt, kein Datenbankbetrieb, statische Plattform bleibt möglich, mehrsprachige Felder sind nativ abbildbar,
  spätere Migration zu einer Datenbank bleibt offen, sollte Schreiblast oder Abfragekomplexität das erfordern.
  Nachteil: viele kleine Dateien erfordern Tooling (Validator, Katalog-/Graphexport) statt eines einzelnen
  Abfragepunkts — dieses Tooling ist Teil von Phase 3 (`tools/`).
- **Migrationsstrategie:** Es existieren noch keine realen Objektinstanzen; es ist daher keine Datenmigration
  nötig. Das Format des leeren `data/catalog.json` (Phase 1) wird durch das generierte `build/catalog.json`
  ersetzt (siehe ADR-0020). Reale Inhalte (z. B. Retatrutid als Pilotobjekt, siehe [Roadmap](../roadmap.md))
  werden ab Phase 4 direkt im neuen Format angelegt.

### ADR-0033: `research/**` als separate Provenienz- und Arbeitsdatenebene neben `data/**`

- **Status:** Entschieden
- **Datum:** 2026-07-24
- **Kontext:** Phase 3 etablierte `data/**` als kanonische, geprüfte Wissensebene. Für Phase 4A musste geklärt
  werden, wo Rechercheverlauf, gefundene Kandidaten, Screening-Entscheidungen und Extraktionsnotizen
  gespeichert werden — Informationen, die für Auditierbarkeit und Reproduzierbarkeit unverzichtbar sind, aber
  zum Zeitpunkt ihrer Entstehung noch nicht geprüftes Wissen darstellen. Würde man sie direkt in `data/**`
  ablegen, entstünde die Gefahr, dass ein ungeprüfter Kandidat mit einem kanonischen Objekt verwechselt wird.
- **Entscheidung:** Eine eigenständige Ebene `research/**` wird eingeführt, strukturell getrennt von `data/**`:
  `research/protocols/`, `research/search_runs/`, `research/screening/`, `research/extractions/`. Ein
  Forschungsdatensatz gilt **nie automatisch** als wissenschaftliche Erkenntnis. Eine Information wird erst
  dann kanonisches Wissen, wenn sie nach manueller Prüfung ausdrücklich als Entität, Quelle, Studie oder Claim
  unter `data/**` angelegt wurde (siehe [Evidence Curation Workflow](Evidence_Curation_Workflow.md)).
  `research/**` fließt **nicht** in `build/catalog.json` oder `build/graph.json` ein und wird von einem
  eigenständigen Validator geprüft (`tools/validate_research.py`, getrennt von `tools/validate_data.py`).
- **Alternativen:**
    1. *Recherchedaten direkt in `data/**` mit Status `draft`* — verworfen: `data/**`-Schemas sind auf geprüfte
       kanonische Objekte zugeschnitten (z. B. `claim.schema.json` erwartet `evidence_category`/`certainty`
       bereits final); Recherche-Zwischenstände (Screening-Entscheidungen, unverifizierte Extraktion) passen
       strukturell nicht in dieses Modell, ohne es zu verwässern.
    2. *Recherchedaten in einem externen Tool (Zotero, ein Tabellenblatt, ein separates Repository)* —
       verworfen: keine Versionierung im selben Repository, kein gemeinsamer Validator, keine Nachvollziehbarkeit
       über Git-Historie, kein einheitliches Schema-Ökosystem.
    3. *Gar keine strukturierte Recherche-Ebene, nur Freitext-Notizen* — verworfen: bei einem Zielbild von
       100.000 Quellen ist Freitext nicht mehr auditierbar oder maschinell prüfbar (siehe
       [Scientific Research Protocol](Scientific_Research_Protocol.md), Abschnitt 33).
    4. *Eigenständige Ebene `research/**` mit eigenen Schemas und eigenem Validator* — **gewählt**.
- **Konsequenzen:** Klare Trennung zwischen „wurde gefunden/geprüft" und „ist kanonisches Wissen". Zusätzlicher
  Pflegeaufwand (zwei Validatoren, acht zusätzliche Schemas), aber keine Vermischung von Provenienz und
  Wissen. `research/raw/**` bleibt zusätzlich als nicht versionierter lokaler Arbeitsbereich für Volltexte/
  Exporte ausgeschlossen (siehe `.gitignore`).
- **Migrationsstrategie:** Nicht zutreffend — `research/**` ist komplett neu, keine bestehenden Daten müssen
  migriert werden. Die Promotion von `research/**` nach `data/**` bleibt in Phase 4A ausdrücklich manuell;
  eine spätere Phase könnte Teile davon (z. B. Identifikator-Normalisierung) stärker automatisieren, ohne die
  grundsätzliche Trennung aufzuheben.

### ADR-0034: Studie und Publikation bleiben getrennte Objekte; mehrere Publikationen zählen nicht als mehrere Studien

- **Status:** Entschieden
- **Datum:** 2026-07-24
- **Kontext:** [Data Model](Data_Model.md) legte bereits fest, dass eine Studie mehrere Publikationen haben
  kann. Phase 4A musste diese Regel für die Recherche-Ebene konkretisieren: Ein Registereintrag (z. B.
  ClinicalTrials.gov) und ein späterer Fachartikel zur selben Studie dürfen beim Screening/bei der Extraktion
  nicht versehentlich als zwei unabhängige Studien behandelt werden — das würde Evidenz künstlich verdoppeln.
- **Entscheidung:** Ein `extraction_record` kann sowohl `canonical_source_id` (die konkrete Publikation/den
  Registereintrag) als auch `canonical_study_id` (die zugrunde liegende Studie) referenzieren — getrennt.
  Die `deduplication_policy` eines Protokolls priorisiert stabile externe Kennungen (insbesondere `nct_id`), um
  zu erkennen, dass Registereintrag und Publikation dieselbe Studie beschreiben (siehe
  [Scientific Research Protocol](Scientific_Research_Protocol.md), Abschnitte 13–16).
- **Alternativen:**
    1. *Studie und Publikation als ein Objekt behandeln* — verworfen: verhindert die korrekte Modellierung von
       Zwischen-/End-/Sicherheits-Updates derselben Studie und würde bei mehreren Publikationen zu doppelt
       gezählter Evidenz führen.
    2. *Nur die Publikation referenzieren, Studienzuordnung dem Claim überlassen* — verworfen: verlagert die
       Verantwortung für Doppelzählungsvermeidung vom Extraktionsschritt (wo die Information vorliegt) auf den
       späteren, isolierten Claim-Erstellungsschritt.
    3. *Getrennte Referenzierung von Quelle und Studie bereits im Extraktionsdatensatz* — **gewählt**.
- **Konsequenzen:** Follow-up-, Subgruppen- und Sicherheitsanalysen lassen sich korrekt mit der Ursprungsstudie
  verknüpfen, ohne die zugrunde liegende Studie zu duplizieren. Erfordert redaktionelle Sorgfalt beim Anlegen
  neuer Studien (Abgleich per Registerkennung, bevor eine neue `data/entities/studies/*.yaml` entsteht).
- **Migrationsstrategie:** Nicht zutreffend, da `data/entities/studies/**` in Phase 4A noch keine realen
  Objekte enthält. Die Regel gilt ab dem ersten realen Promotion-Schritt (Phase 4B).

### ADR-0035: Automatisierte Extraktion und KI dürfen keine aktiven kanonischen Claims freigeben

- **Status:** Entschieden
- **Datum:** 2026-07-24
- **Kontext:** [Architecture](Architecture.md) legte bereits fest, dass KI die Redaktion unterstützt, aber keine
  eigenständigen medizinischen Aussagen erzeugt oder autonom veröffentlicht. Phase 4A musste diese Grundregel
  für den konkreten Recherche-Workflow strukturell (nicht nur redaktionell) absichern.
- **Entscheidung:** `candidate_claims[]` in einem `extraction_record` tragen strukturell **kein** Status-Feld
  (`additionalProperties: false` in `schemas/research_extraction_record.schema.json` verhindert, dass ein
  Status wie „aktiv" dort überhaupt eingetragen werden kann) und sind immer `is_provisional: true` (per
  `const`-Constraint erzwungen). Kein Werkzeug in Phase 4A schreibt eine Datei unter `data/claims/**` oder
  setzt `status: active` — dieser Schritt bleibt manuell (siehe [Evidence Curation Workflow](Evidence_Curation_Workflow.md),
  Abschnitt 12).
- **Alternativen:**
    1. *Ein `status`-Feld an `candidate_claims` zulassen, aber redaktionell vorschreiben, es nie auf „aktiv" zu
       setzen* — verworfen: eine rein redaktionelle Regel ohne strukturelle Durchsetzung kann versehentlich
       oder durch ein zukünftiges Automatisierungs-Update umgangen werden.
    2. *Ein separates „Freigabe-Tool" bauen, das Kandidatenclaims nach Prüfung automatisch in `data/claims/**`
       schreibt* — verworfen für Phase 4A: das würde die Promotion nur technisch bequemer machen, ohne einen
       zusätzlichen Sicherheitsgewinn, und ist verfrüht, solange noch keine echten Kandidatenclaims vorliegen.
       Bleibt als mögliche Komfortfunktion für eine spätere Phase vorgemerkt (siehe [Future Roadmap](Future_Roadmap.md)).
    3. *Strukturelle Unmöglichkeit eines aktiven Status auf Kandidatenclaims, Promotion bleibt manuell* —
       **gewählt**.
- **Konsequenzen:** Ein Kandidatenclaim kann nicht versehentlich als aktiver Claim missverstanden oder
  fehlerhaft automatisiert übernommen werden — der Validator (`tools/validate_research.py`) würde einen
  zusätzlichen Status-Schlüssel ohnehin ablehnen. Der manuelle Promotion-Schritt bleibt Mehraufwand für die
  Redaktion, ist aber angesichts der medizinischen Tragweite aktiver Claims bewusst in Kauf genommen.
- **Migrationsstrategie:** Nicht zutreffend — die Regel gilt von Anfang an für jeden neu erstellten
  Extraktionsdatensatz.

### ADR-0036: Protokoll- und Referenzkonsistenz strukturell erzwungen

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** Der ursprüngliche Phase-4A-Validator prüfte nur, dass referenzierte IDs (`protocol_id`,
  `search_run_ids`, ...) überhaupt existieren, nicht aber, ob die referenzierten Objekte inhaltlich
  zusammenpassen. Dadurch konnte ein `search_run` gegen ein noch gar nicht freigegebenes (`draft`)
  Protokoll ausgeführt werden, ein `screening_record` Suchläufe verschiedener Protokollversionen
  mischen, oder eine Extraktion eine andere `protocol_id` tragen als das zugehörige Screening — ohne
  dass der Validator das bemerkte. Ebenso war `discovery_only` für `google_scholar`/
  `manufacturer_registry` nur redaktionell vorgeschrieben (Abschnitt 5 des Scientific Research
  Protocol), nicht strukturell.
- **Entscheidung:** `tools/validate_research.py` prüft jetzt zusätzlich: (1) `protocol.version` muss
  exakt dem `-vN`-Suffix der `id` entsprechen; (2) ein `search_run` darf nur auf ein Protokoll mit
  Status `approved` oder `superseded` zeigen; (3) jeder in `screening_record.search_run_ids`
  referenzierte Suchlauf muss dieselbe `protocol_id` tragen wie das Screening selbst; (4) ein
  `extraction_record` muss dieselbe `protocol_id` tragen wie das referenzierte Screening; (5) tragen
  Screening und Extraktion beide eine `canonical_source_id`, müssen diese übereinstimmen. Zusätzlich
  erzwingt `schemas/research_protocol.schema.json` per `if`/`then` je Array-Element, dass
  `database: google_scholar`/`manufacturer_registry` ausschließlich mit `role: discovery_only`
  kombiniert werden darf.
- **Alternativen:**
    1. *Nur redaktionelle Konvention, keine strukturelle Prüfung* — verworfen: genau dieser Zustand
       bestand bereits und wurde im Review als Lücke identifiziert.
    2. *Protokollstatus zur Ausführungszeit historisch statt aktuell prüfen* (d. h. "war das Protokoll
       zum Zeitpunkt von `executed_at` freigegeben?") — verworfen für Phase 4A: erfordert eine
       Versionierungshistorie pro Protokollversion, die aktuell nicht vorliegt; die einfachere Prüfung
       "Status zum Validierungszeitpunkt" genügt, solange Protokolle nach Freigabe nicht mehr in
       `draft` zurückversetzt werden (redaktionelle Konvention, siehe `amendment_policy`).
    3. *Vollständige Cross-Referenz-Konsistenzprüfung wie beschrieben* — **gewählt**.
- **Konsequenzen:** Ein Suchlauf gegen ein unfertiges Protokoll oder eine versehentlich vermischte
  Protokollkette wird jetzt als Fehler erkannt statt still akzeptiert. Erfordert etwas zusätzliche
  Sorgfalt beim Anlegen von Testdaten (Protokolle müssen für zugehörige Suchläufe `approved` sein) —
  entsprechend wurden alle bestehenden Test-Fixtures angepasst.
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten (das Retatrutid-Protokoll bleibt
  `draft` und hat keine Suchläufe). Bestehende Test-Fixtures und `research/examples/**` wurden im
  selben Commit angepasst.

### ADR-0037: Vollständige Screening-Historie (`decision_history`) und maschinenlesbare Claim-Promotion-Kette (`promotion_record`)

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** Der [Evidence Curation Workflow](Evidence_Curation_Workflow.md) behauptete bereits vor
  diesem Commit, die „vollständige Screening-Historie bleibt in der Datei erhalten (keine
  Überschreibung)" — tatsächlich speicherte `research_screening_record.schema.json` nur den letzten
  Zustand; ein früherer Titel-/Abstract-Entscheid war nach einem Volltext-Entscheid nicht mehr
  rekonstruierbar. Ebenso behauptete das Scientific Research Protocol eine durchgängige Kette von
  `search_run` bis zum kanonischen Claim, ohne dass zwischen einem verifizierten Kandidatenclaim
  (`extraction_record.candidate_claims[]`) und einer später manuell angelegten
  `data/claims/*.yaml`-Datei irgendeine maschinenlesbare Verknüpfung existierte.
- **Entscheidung:** (1) `research_screening_record.schema.json` erhält ein Pflichtfeld
  `decision_history[]`: ein Append-only-Protokoll aller Screening-Zustände (Stufe, Entscheidung,
  Grund, verantwortliche Person, Zeitpunkt, ggf. Zweitprüfung). Die bestehenden Top-Level-Felder
  (`decision`, `decision_stage`, ...) bleiben als validierte **Projektion** des letzten
  `decision_history`-Eintrags erhalten (bewusste Denormalisierung für einfache Abfragen, siehe
  Abschnitt „Alternativen"). Der Validator prüft lückenlose `sequence`, dass Stufen nicht rückwärts
  laufen und dass die Projektion konsistent bleibt. (2) Ein neues fünftes Research-Objekt
  `promotion_record` (`schemas/research_promotion_record.schema.json`, `research/promotions/`)
  verbindet `extraction_record_id` + `candidate_working_id` mit einer späteren
  `canonical_claim_id` unter `data/claims/**`. `promotion_status: approved_for_creation`/`promoted`
  erfordern dokumentierte Reviewer und Begründung und dürfen — wie schon für `data/claims/**` in
  ADR-0035 festgelegt — nie automatisiert durch Automatisierung/KI gesetzt werden.
- **Alternativen (Screening-Historie):**
    1. *Top-Level-Felder als einzige Quelle, keine Historie* — verworfen: genau das war der bisherige,
       im Review beanstandete Zustand.
    2. *Separates, unveränderliches Screening-Event-Objekt statt eines Arrays im selben Datensatz* —
       erwogen, aber verworfen: ein Screening-Datensatz ist konzeptionell "ein Kandidat, eine sich
       entwickelnde Bewertung" — ein separates Event-Objekt pro Zustandsübergang würde denselben
       Kandidaten künstlich über mehrere Dateien verteilen und die bestehende 1-Datei-pro-Kandidat-
       Struktur (analog ADR-0017) aufbrechen, ohne einen zusätzlichen Sicherheitsgewinn gegenüber
       einem geprüften Append-only-Array in derselben Datei.
    3. *`decision_history[]` als Pflichtarray mit Top-Level-Feldern als geprüfte Projektion* —
       **gewählt**.
- **Alternativen (Claim-Promotion):**
    1. *Keine explizite Verknüpfung, Nachvollziehbarkeit nur über redaktionelle Sorgfalt/Commit-
       Beschreibungen* — verworfen: bei einem Zielbild von 100.000 Quellen nicht mehr auditierbar
       (siehe Scientific Research Protocol, Abschnitt 33).
    2. *`data/claims/*.yaml` erhält rückwirkend ein Feld mit Verweis auf den Recherche-Ursprung* —
       verworfen: vermischt die kanonische Wissensebene mit Provenienzdaten (widerspricht ADR-0033).
    3. *Eigenständiges `promotion_record`-Objekt in `research/**`* — **gewählt**.
- **Konsequenzen:** Die im Evidence Curation Workflow beschriebene Historien- und Kettenaussage ist
  jetzt strukturell wahr, nicht nur behauptet. Etwas höherer Pflegeaufwand beim manuellen Anlegen
  eines Screening-Datensatzes (ein Historieneintrag statt nur Top-Level-Felder) und ein zusätzliches
  Schema/Vokabular (`promotion_statuses.yaml`). `research/promotions/**` bleibt wie alle
  `research/**`-Objekte außerhalb von `build/catalog.json`/`build/graph.json` (ADR-0033).
- **Migrationsstrategie:** Alle bestehenden Screening-Datensätze (Produktivbeispiele und
  Test-Fixtures) wurden im selben Commit um einen `decision_history`-Eintrag ergänzt, der ihren
  bisherigen einzigen Zustand als `sequence: 1` abbildet — keine inhaltliche Änderung.

### ADR-0038: Eigenständiges `search_run_status`-Vokabular; CI-Check gegen rückwirkende Suchlauf-Änderungen

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** `research_search_run.status` nutzte bislang `common.schema.json#/$defs/editorial_status`
  (`draft`/`in_review`/`active`/`withdrawn`) — ein Vokabular für redaktionelle Dokumente mit
  Entwurfs-/Freigabezyklus. Ein Suchlauf ist aber kein redaktionelles Dokument, sondern das Protokoll
  eines bereits ausgeführten, laut Schema-Beschreibung „unveränderlichen" Ereignisses; ein Suchlauf
  wird nie als „Entwurf" angelegt. Diese Unveränderlichkeit war zudem bislang nur eine Behauptung in
  der Schema-Beschreibung, nicht technisch durchgesetzt — ein bereits gemergter Suchlauf hätte in
  einem späteren Pull Request unbemerkt nachträglich verändert werden können.
- **Entscheidung:** Ein neues, eigenständiges Vokabular `search_run_status`
  (`executed`/`superseded`/`withdrawn`, `research/vocabularies/search_run_statuses.yaml`) ersetzt
  `editorial_status` für `research_search_run.status`. Zusätzlich prüft ein neues CI-Werkzeug
  (`tools/check_research_immutability.py`, Schritt in `.github/workflows/ci.yml`) bei jedem Pull
  Request, ob eine bereits gegenüber dem Zielbranch committete `research/search_runs/**`-Datei
  gelöscht, umbenannt oder in einem anderen Feld als `status`/`updated_at`/`review`/`notes` verändert
  wurde.
- **Alternativen:**
    1. *`editorial_status` beibehalten* — verworfen: semantisch unpassend (kein Entwurfszustand für
       ein bereits ausgeführtes Ereignis) und vermischt zwei unterschiedliche Lebenszyklus-Konzepte.
    2. *Unveränderlichkeit ausschließlich redaktionell/durch Dokumentation durchsetzen* — verworfen:
       genau das war der bisherige, unzureichende Zustand.
    3. *Serverseitige Branch Protection allein* — ergänzend sinnvoll (siehe ADR-0010), aber kein
       Ersatz für eine inhaltliche Prüfung, welche Felder sich geändert haben.
    4. *Eigenes Vokabular plus CI-Diff-Check mit dokumentierter Grenze* — **gewählt**.
- **Konsequenzen:** Klarere Semantik für `research_search_run.status`. Der Immutability-Check ist
  bewusst **kein** vollständiger Schutz: er vergleicht nur gegen den Merge-Base mit einem Basis-Ref
  und wird übersprungen (nicht hart abgelehnt), wenn dieser Ref nicht auflösbar ist (z. B. lokale
  Pushes ohne PR-Kontext) — siehe Docstring von `tools/check_research_immutability.py` und Abschnitt
  34 des Scientific Research Protocol. Er ersetzt keine Branch Protection auf `main` (weiterhin nur
  als ADR-0010 vorgeschlagen, nicht umgesetzt).
- **Migrationsstrategie:** Alle bestehenden `search_run`-Datensätze (Produktivbeispiele,
  Test-Fixtures) wurden von `active`/`draft` auf `executed` migriert — reine Statuswert-Umbenennung,
  keine inhaltliche Änderung der Ausführungsfelder.

### ADR-0039: Echte Identifier-Deduplizierung und strukturelle Zwei-Personen-Kontrolle

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** Das Scientific Research Protocol (Abschnitt 8) und der Evidence Curation Workflow
  beschrieben bereits vor diesem Commit eine Identifier-Normalisierung zur Duplikaterkennung sowie
  eine verpflichtende Zweitprüfung bei Volltext-Screening und Extraktion — beides war jedoch nicht
  tatsächlich im Validator implementiert. Zwei Screening-Datensätze mit identischem DOI (nur in
  unterschiedlicher Schreibweise) konnten unbemerkt beide als eigenständige, aktive Kandidaten
  bestehen bleiben; eine fehlende oder von derselben Person stammende Zweitprüfung wurde nicht
  erkannt; ein Widerspruch zwischen Erst- und Zweitprüfung (`decision_confirmed: false`) hatte keine
  vorgeschriebene Auflösung.
- **Entscheidung:** (1) `tools/_researchlib.py` ergänzt einen `normalize_nct_id`-Normalisierer
  (analog zu den bestehenden DOI/PMID/PMCID/ISBN/URL-Normalisierern aus `tools/_datalib.py`, die
  hier wiederverwendet werden). `tools/validate_research.py` erkennt normalisierte
  DOI/PMID/PMCID/NCT-ID/ISBN-Kollisionen zwischen aktiven (nicht als `duplicate` markierten)
  Screening-Datensätzen **innerhalb desselben Protokolls** als Fehler; URL-Kollisionen bleiben eine
  Warnung (Redirects/Mirrors, analog zur bestehenden Quellen-Deduplizierung in ADR-0026). Kollisionen
  über verschiedene Protokolle hinweg sind ausdrücklich erlaubt (dieselbe Publikation kann in
  mehreren Reviews vorkommen). (2) `screening_policy.dual_reviewer_stages` wird jetzt erzwungen: eine
  finale `include`/`exclude`-Entscheidung auf einer solchen Stufe benötigt `second_review`, dessen
  `reviewed_by` von `screened_by` abweichen muss. `second_review.adjudication` (neues Feld) löst
  einen Widerspruch (`decision_confirmed: false`) durch eine von beiden vorherigen Personen
  unabhängige dritte Person auf; ohne Adjudikation muss die Entscheidung `uncertain` bleiben. Ein
  finaler Einschluss auf `full_text`/`final`-Stufe erfordert `full_text_status: obtained`. (3)
  `verified_by != extracted_by` wird erzwungen, sofern `extraction_policy.verification_required:
  true` gesetzt ist — bewusst nicht unbedingt, siehe Konsequenzen.
- **Alternativen:**
    1. *Deduplizierung/Zweitprüfung weiterhin nur redaktionell vorschreiben* — verworfen: identische
       Lücke wie in ADR-0026 (Quellenebene) bereits einmal geschlossen; auf der Recherche-Ebene aber
       noch offen.
    2. *Identifier-Kollisionen auch über verschiedene Protokolle hinweg als Fehler behandeln* —
       verworfen: dieselbe Publikation kann legitim in mehreren, unabhängigen Recherche-Vorhaben
       auftauchen; eine protokollübergreifende Fehlermeldung würde falsch-positive Befunde erzeugen.
    3. *`verified_by != extracted_by` immer erzwingen, unabhängig von `verification_required`* —
       erwogen, aber verworfen: das Protokoll legt bewusst pro Vorhaben fest, ob eine unabhängige
       Zweitprüfung verpflichtend ist (`extraction_policy.verification_required`); eine unbedingte
       Erzwingung würde diese protokollseitige Entscheidung entwerten.
    4. *Vollstaendige, protokollabhaengige Deduplizierung, Dual-Review- und Adjudikationslogik wie
       beschrieben* — **gewählt**.
- **Konsequenzen:** Screening-Daten mit unentdeckten Duplikaten oder unzureichender Zweitprüfung
  werden jetzt zuverlässig zurückgewiesen statt still akzeptiert. Erfordert bei protokollseitig
  vorgeschriebener Zweitprüfung zwingend zwei unterschiedliche Personenkürzel in den Testdaten.
  Dokumentiertes, bewusst nicht erzwungenes Verhalten: ist `extraction_policy.verification_required`
  `false`, wird `verified_by == extracted_by` nicht beanstandet (siehe Scientific Research Protocol,
  Abschnitt 27a).
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten (noch keine realen Screening-/
  Extraktionsdatensätze). Bestehende Test-Fixtures wurden im selben Commit angepasst bzw. um
  gezielte neue Negativ-/Positivszenarien ergänzt.

## Format für neue Einträge

```markdown
### ADR-00XX: <Titel>
- **Status:** Entschieden | Vorgeschlagen | Verworfen
- **Datum:** YYYY-MM-DD
- **Kontext:** Was war die Ausgangslage/das Problem?
- **Entscheidung:** Was wurde entschieden?
- **Konsequenzen:** Was folgt daraus, welche Alternativen wurden verworfen und warum?
```

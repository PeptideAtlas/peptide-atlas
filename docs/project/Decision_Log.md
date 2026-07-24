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

## Format für neue Einträge

```markdown
### ADR-00XX: <Titel>
- **Status:** Entschieden | Vorgeschlagen | Verworfen
- **Datum:** YYYY-MM-DD
- **Kontext:** Was war die Ausgangslage/das Problem?
- **Entscheidung:** Was wurde entschieden?
- **Konsequenzen:** Was folgt daraus, welche Alternativen wurden verworfen und warum?
```

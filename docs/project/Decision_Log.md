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
| ADR-0039 | Echte Identifier-Deduplizierung und strukturelle Zwei-Personen-Kontrolle (Dual-Reviewer, Adjudikation, Extraktionsverifikation) | Entschieden (Phase 4A, Review-Härtung Runde 2) | Die in der Dokumentation seit Phase 4A behauptete Identifier-Normalisierung und Zweitprüfung war bislang nicht tatsächlich implementiert. `tools/validate_research.py` erkennt jetzt normalisierte DOI/PMID/PMCID/NCT-ID-Kollisionen innerhalb desselben Protokolls, erzwingt `second_review` in `screening_policy.dual_reviewer_stages`, Reviewer-Unabhängigkeit, eine kontrollierte Konfliktlösung (Adjudikation durch eine dritte Person oder `decision: uncertain`) sowie (in dieser Runde noch protokollabhängig) `verified_by != extracted_by`. Die protokollabhängige Ausnahme wurde in Runde 3 durch ADR-0040 wieder entfernt. Ausführliches ADR siehe unten. |
| ADR-0040 | `extraction_status: verified` bedeutet unbedingt unabhängige Zweitprüfung; neuer Status `self_checked` | Entschieden (Phase 4A, Review-Härtung Runde 3) | Löst die in ADR-0039 eingeführte protokollabhängige Ausnahme ab: `verified_by != extracted_by` gilt jetzt immer, ohne Opt-out. Ausführliches ADR siehe unten. |
| ADR-0041 | `claim_promotion_policy.requires_second_review` technisch erzwungen; Grenze zur menschlichen Reviewer-Identität dokumentiert | Entschieden (Phase 4A, Review-Härtung Runde 3) | `promotion_record`-Datensätze mit `approved_for_creation`/`promoted` benötigen jetzt mindestens zwei unterschiedliche, nicht-leere Reviewer-Kürzel, wenn das Protokoll das verlangt — bewusst ohne Actor-Registry (Lösung B). Ausführliches ADR siehe unten. |
| ADR-0042 | Terminale Screening-Stufe als einzige Extraktionsvoraussetzung; vollständige `decision_history`-Validierung; `duplicate_of`-Kettenprüfung; Suchlauf-Datenbank muss geplant sein | Entschieden (Phase 4A, Review-Härtung Runde 3) | Schließt vier zusammenhängende, in der unabhängigen Prüfung von Runde 2 gefundene Lücken: uneindeutige `full_text`/`final`-Semantik, nur oberflächliche Workflow-Prüfung des aktuellen Zustands statt der gesamten Historie, protokollübergreifende `duplicate_of`-Ketten, und Suchläufe gegen nicht geplante Datenbanken. Ausführliches ADR siehe unten. |
| ADR-0043 | Erst-, Zweit- und Endentscheidung strukturell getrennt (`primary_decision` vs. `decision`); zentrale Stage-/Decision-Matrix | Entschieden (Phase 4A, Review-Härtung Runde 4) | Behebt eine Modellierungslücke, bei der die Erstentscheidung verloren ging, sobald eine Adjudikation oder ein ungelöster Widerspruch die effektive `decision` änderte, und bei der `decision_confirmed` fälschlich gegen die effektive statt die Erstentscheidung geprüft wurde. Ausführliches ADR siehe unten. |
| ADR-0044 | Zeitliche Provenienzkette objektübergreifend validiert (Screening → Extraktion → Verifikation → Promotion) | Entschieden (Phase 4A, Review-Härtung Runde 4) | Eine Extraktion konnte bislang zeitlich vor ihrer eigenen terminalen Einschlussentscheidung liegen, eine Promotion vor der zugehörigen Verifikation. Ausführliches ADR siehe unten. |
| ADR-0045 | Promotion-Reviewer-Liste schema-seitig auf Eindeutigkeit und Nicht-Leerheit geprüft, ohne die gemeinsame `review_block`-Definition zu verändern | Entschieden (Phase 4A, Review-Härtung Runde 4) | `research_promotion_record.schema.json` definiert `review.reviewers` jetzt eigenständig (`uniqueItems`, Nicht-Leerzeichen-Pattern) statt des gemeinsamen `common.schema.json#/$defs/review_block`, um andere Objektarten nicht zu berühren. Ausführliches ADR siehe unten. |
| ADR-0046 | Stage-/Decision-Matrix auch gegen `second_review.reviewer_decision` geprüft; `deduplication` unterstützt strukturell keine Adjudikation | Entschieden (Phase 4A, Review-Härtung Runde 5) | ADR-0043s Matrix wurde bislang nur gegen `primary_decision` und die effektive `decision` geprüft, nicht gegen die eigenständige Entscheidung der Zweitprüfung. Zusätzlich hätte ein Dedup-Konflikt nur teilweise per Adjudikation lösbar sein können. Ausführliches ADR siehe unten. |
| ADR-0047 | Vollständige, verlustfreie Drei-Ebenen-Entscheidungsprovenienz (`primary_decision_reason`/`primary_duplicate_of`, `second_review.reviewer_decision_reason`/`reviewer_duplicate_of`) | Entschieden (Phase 4A, Review-Härtung Runde 5) | Gründe und Duplikatverweise existierten bislang nur für die effektive Entscheidung — bei einer Abweichung zwischen Erst-, Zweit- und Endentscheidung gingen die jeweils eigenständigen Begründungen verloren. Ausführliches ADR siehe unten. |
| ADR-0048 | Objektinterne zeitliche Vollständigkeit: jedes dokumentierte Ereignisdatum liegt innerhalb von `[created_at, updated_at]` desselben Objekts | Entschieden (Phase 4A, Review-Härtung Runde 5) | ADR-0044 prüft die Kette objektübergreifend, aber nicht, dass ein Objekt nicht angeblich vor einem von ihm selbst gespeicherten Ereignis zuletzt aktualisiert wurde. Ausführliches ADR siehe unten. |
| ADR-0049 | `rejected`-Promotions erfordern dieselbe Mindest-Audit-Spur wie `approved_for_creation`/`promoted` | Entschieden (Phase 4A, Review-Härtung Runde 5) | Eine Ablehnung konnte bislang ohne Reviewer, Reviewdatum oder Begründung existieren, obwohl sie eine ebenso konsequenzreiche wissenschaftliche/redaktionelle Entscheidung ist. Ausführliches ADR siehe unten. |
| ADR-0050 | Stabile Research-Actor-ID-Syntax (`research_actor_id`) ohne Actor-Registry | Entschieden (Phase 4A, Review-Härtung Runde 5) | Alle Research-Akteursfelder verwendeten bislang ein reines `minLength: 1`-Feld — Leerzeichenvarianten oder Groß-/Kleinschreibung hätten Gleichheits-/Unabhängigkeitsprüfungen (z. B. Zweitprüfer ≠ Erstprüfer) unterlaufen können. Ausführliches ADR siehe unten. |
| ADR-0051 | `screening_policy.dual_reviewer_stages` muss Teilmenge von `screening_policy.stages` sein | Entschieden (Phase 4A, Review-Härtung Runde 5) | Ein Protokoll konnte bislang eine Zweitprüferstufe verlangen, die gar nicht als Screening-Stufe konfiguriert war. Ausführliches ADR siehe unten. |
| ADR-0052 | Historische Duplikatverweise referenziell geprüft; unterschiedliche Duplikatziele als Konflikt behandelt | Entschieden (Phase 4A, Review-Härtung Runde 5B) | `primary_duplicate_of`, `second_review.reviewer_duplicate_of` und `decision_history[].duplicate_of` waren bislang nur formatgeprüft, nicht referenziell — ein Verweis auf einen nicht existierenden, protokollfremden oder den eigenen Datensatz blieb unbemerkt. Zusätzlich zählte eine übereinstimmende `duplicate`-Entscheidung als „bestätigt", auch wenn Erst- und Zweitprüfung unterschiedliche Hauptdatensätze meinten. Ausführliches ADR siehe unten. |
| ADR-0053 | Effektives `duplicate_of` deterministisch an das bestätigte Duplikatziel gebunden | Entschieden (Phase 4A, Review-Härtung Runde 5C) | ADR-0052 prüfte `primary_duplicate_of == second_review.reviewer_duplicate_of` bei bestätigtem Konsens, aber nicht, dass die effektive `duplicate_of` tatsächlich dieses bestätigte Ziel bindet — ein davon abweichender, sonst gültiger dritter Hauptdatensatz blieb unbemerkt möglich. Ausführliches ADR siehe unten. |

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

### ADR-0040: `extraction_status: verified` bedeutet unbedingt unabhängige Zweitprüfung; neuer Status `self_checked`

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** ADR-0039 (Runde 2) erzwang `verified_by != extracted_by` nur, wenn das referenzierte Protokoll
  `extraction_policy.verification_required: true` setzte. Eine unabhängige Prüfung des Heads dieser Runde
  bemängelte zu Recht, dass dadurch `extraction_status: verified` **nicht zuverlässig** „durch eine andere
  Person geprüft" bedeutete — ein Protokoll mit `verification_required: false` konnte eine Ein-Personen-
  Selbstbestätigung als `verified` ausgeben, obwohl der Name des Status genau das Gegenteil suggeriert.
- **Entscheidung:** `verified_by != extracted_by` wird jetzt **immer** erzwungen, sobald
  `extraction_status: verified` gesetzt ist — die protokollabhängige Ausnahme aus ADR-0039 entfällt ersatzlos.
  Für rein technische Ein-Personen-Durchläufe (Strukturtests, Platzhalterdaten) wird stattdessen ein neuer,
  eigenständiger Status `self_checked` eingeführt (`common.schema.json#/$defs/extraction_status`,
  `research/vocabularies/extraction_statuses.yaml`). `tools/validate_research.py` stellt zusätzlich sicher,
  dass ein `promotion_record` sich niemals auf eine `self_checked`-Extraktion beziehen kann — nur `verified`
  ist promotion-fähig.
- **Alternativen:**
    1. *Protokollabhängige Ausnahme aus ADR-0039 beibehalten* — verworfen: genau das war die im Review
       bemängelte Lücke; „verified" hätte je nach Protokoll zwei unterschiedliche Bedeutungen gehabt.
    2. *`verification_required` ganz entfernen, `verified_by != extracted_by` immer erzwingen, ohne
       Alternativstatus* — verworfen: es gibt legitime Faelle (Strukturtests, Platzhalterbeispiele), in denen
       eine einzelne Person einen Durchlauf technisch abschließt, ohne dass eine zweite Person real verfügbar
       ist; ein Zwang zu einem irreführenden `verified` (mit einer erfundenen zweiten Person) wäre schlimmer
       als ein ehrlich benannter Alternativstatus.
    3. *Unbedingtes `verified` plus neuer, nie promotion-fähiger `self_checked`-Status* — **gewählt**.
- **Konsequenzen:** `extraction_status: verified` ist jetzt eine verlässliche, protokollunabhängige Garantie.
  Bestehende Test-Fixtures und `research/examples/**`, die zuvor auf die protokollabhängige Ausnahme setzten,
  wurden im selben Commit auf `self_checked` umgestellt bzw. entfernt (siehe
  `tests/fixtures/research/valid_scenarios/independently_verified_extraction_can_be_promoted` und
  `self_verified_extraction_cannot_be_promoted`).
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten (noch keine realen Extraktionsdatensätze). Ein
  künftiges reales Protokoll, das bislang `verification_required: false` gesetzt hätte, muss stattdessen für
  Ein-Personen-Durchläufe `self_checked` verwenden.

### ADR-0041: `claim_promotion_policy.requires_second_review` technisch erzwungen; Grenze zur menschlichen Reviewer-Identität dokumentiert

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** `claim_promotion_policy.requires_second_review` existierte im Protokollschema bereits seit
  Phase 4A, wurde aber von keinem Validator ausgewertet — ein Protokoll konnte diese Pflicht setzen, ohne dass
  sie irgendeine Wirkung auf `promotion_record`-Datensätze hatte. Die Review-Runde 3 verlangte außerdem eine
  explizite Entscheidung zwischen einer maschinenlesbaren Actor-Registry (human/automation/ai_assistant/
  service) und einer ehrlich dokumentierten Grenze ohne Registry.
- **Entscheidung:** `tools/validate_research.py` prüft jetzt: Setzt das referenzierte Protokoll
  `claim_promotion_policy.requires_second_review: true`, müssen `promotion_record`-Datensätze mit
  `promotion_status: approved_for_creation`/`promoted` mindestens **zwei unterschiedliche, nicht-leere**
  Einträge in `review.reviewers` tragen. Es wird **keine** Actor-Registry eingeführt (Lösung B aus dem
  Reviewauftrag): Die Prüfung stellt nur sicher, dass zwei unterschiedliche *Kürzel* vorhanden sind, nicht,
  dass es sich um zwei unterschiedliche *menschliche* Personen handelt. Diese Garantie bleibt organisatorisch
  (Reviewprozess, Repository-Zugriffskontrolle) — die Dokumentation behauptet an keiner Stelle mehr eine
  stärkere, technisch erzwungene Garantie (siehe Scientific Research Protocol, Abschnitt 34).
- **Alternativen:**
    1. *Actor-Registry einführen* (`id`, `actor_type: human|automation|ai_assistant|service`, `roles[]`,
       Reviewerfelder referenzieren Actor-IDs) — inhaltlich die langfristig sauberere Lösung für
       Auditierbarkeit bei 100.000 Quellen und zunehmendem KI-Einsatz, aber verworfen für diesen Commit: sie
       berührt praktisch jedes bestehende Reviewer-Feld in fünf Schemas (`review_block`, `second_review`,
       `adjudication`, `promotion_record.review`, kanonische `data/**`-Reviewmetadaten) und wäre damit kein
       kleiner, fokussierter Fix mehr, sondern eine eigenständige Migration — verfrüht, solange noch keine
       realen Reviewer-Daten existieren. Bleibt für eine spätere Phase vorgemerkt.
    2. *Nur Anzahl pruefen (>= 2 Eintraege), keine Eindeutigkeit* — verworfen: zwei identische Kürzel hätten
       die Prüfung sonst trivial umgangen (siehe Testszenario `promotion_duplicate_reviewers`).
    3. *Zwei-distinkte-Kürzel-Pruefung ohne Actor-Registry, Grenze explizit dokumentiert* — **gewählt**.
- **Konsequenzen:** Die im Protokoll dokumentierte Absicht (`requires_second_review`) hat jetzt tatsächlich
  eine Wirkung. Die verbleibende Lücke (Kürzel statt verifizierter Identität) ist an mehreren Stellen
  (Scientific Research Protocol Abschnitt 29/34, `research/promotions/README.md`, `research/README.md`)
  ausdrücklich als organisatorische, nicht technische Garantie benannt.
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten. Bestehende Test-Fixtures wurden um gezielte
  neue Szenarien ergänzt (`promotion_policy_requires_two_reviewers`,
  `promotion_single_reviewer_when_two_required`, `promotion_duplicate_reviewers`,
  `promotion_two_reviewers_when_required`).

### ADR-0042: Terminale Screening-Stufe als einzige Extraktionsvoraussetzung; vollständige `decision_history`-Validierung; `duplicate_of`-Kettenprüfung; Suchlauf-Datenbank muss geplant sein

- **Status:** Entschieden
- **Datum:** 2026-07-25
- **Kontext:** Eine unabhängige Prüfung des Runde-2-Heads fand vier zusammenhängende strukturelle Lücken: (1)
  `decision_stage: full_text` und `final` wurden nebeneinander als potenziell extraktionsfähig behandelt, ohne
  eindeutige Regel, wann welche Stufe terminal ist — eine Extraktion konnte bereits nach einem vorläufigen
  Volltext-Einschluss entstehen. (2) Die Workflow-Invarianten (Dual-Reviewer, Reviewer-Unabhängigkeit,
  Konfliktlösung, Volltextregeln) wurden nur auf die Top-Level-Felder angewandt, nicht auf jeden Eintrag in
  `decision_history[]` — ein älterer, fehlerhafter Historieneintrag blieb unentdeckt. (3) `duplicate_of` prüfte
  nur, dass das Ziel existiert, nicht, dass es demselben Protokoll angehört (auch nicht über mehrere
  Kettenglieder hinweg). (4) `search_run.database` musste keiner im Protokoll geplanten Datenbank entsprechen
  — eine stille Erweiterung der Recherche nach Protokollfreigabe blieb unentdeckt. Zusätzlich war
  `second_review.reviewer_decision` weiterhin nullable und `decision_confirmed` frei editierbar, ohne dass der
  Validator die Konsistenz zwischen beiden prüfte.
- **Entscheidung:**
    1. `decision_stage: final` ist ab sofort die **einzige** extraktionsfähige Stufe; `full_text` dokumentiert
       nur die Volltextbewertung. Eine Extraktion erfordert `decision: include`, `decision_stage: final`,
       `full_text_status: obtained`, eine vorhandene, für `final` konfigurierte Zweitprüfung sowie keinen
       ungelösten Zweitprüfungskonflikt (Scientific Research Protocol, Abschnitt 9b).
    2. `second_review.reviewer_decision` ist schema-seitig nicht mehr nullable. `tools/validate_research.py`
       validiert **jeden** Eintrag in `decision_history[]` (nicht nur den letzten) gegen dieselben Invarianten:
       Stufe im Protokoll vorgesehen, Dual-Reviewer-Pflicht, Reviewer-/Adjudikator-Unabhängigkeit, `decision_
       confirmed` als geprüfte Projektion von `reviewer_decision == Erstentscheidung`, Konfliktlösung,
       Volltextregeln und Datumsreihenfolge. `full_text_status` wird dafür auch je Historieneintrag
       gespeichert (`schemas/research_screening_record.schema.json`).
    3. `duplicate_of` und die **gesamte** Kette verketteter Duplikate müssen innerhalb derselben `protocol_id`
       bleiben wie der Ausgangsdatensatz — nicht nur der unmittelbare Verweis.
    4. `search_run.database` muss unter `protocol.planned_information_sources[].database` stehen; eine neue
       Datenbank erfordert eine neue, vor der Suchausführung freigegebene Protokollversion.
- **Alternativen:**
    1. *`full_text` als terminale Stufe beibehalten, `final` als optionale zusätzliche Stufe* — verworfen: der
       Reviewauftrag verlangte ausdrücklich eine eindeutige, nicht mehrdeutige Regel; eine Menge
       `{full_text, final}` ohne klare Rangfolge hätte dieselbe Unklarheit nur verschoben.
    2. *Nur den letzten `decision_history`-Eintrag prüfen (bisheriger Zustand)* — verworfen: das war exakt die
       im Review gefundene Lücke.
    3. *`duplicate_of` protokollübergreifend erlauben* — verworfen: ein Duplikat und sein Hauptdatensatz
       müssen in derselben Recherche verortet bleiben, sonst verliert `duplicate_of` seine Bedeutung als
       „gleicher Kandidat in dieser Recherche".
    4. *Suchlauf-Datenbanken nicht gegen den Plan prüfen* — verworfen: das hätte eine stille
       Scope-Erweiterung nach Protokollfreigabe ermöglicht, ohne dass dafür eine neue Protokollversion
       nötig gewesen wäre.
- **Konsequenzen:** Deutlich strengere, aber eindeutige Extraktionsvoraussetzungen; alle bestehenden
  Beispiel- und Test-Fixtures mit `decision_stage: full_text` + Extraktion wurden auf `final` migriert
  (`research/examples/**`, `tests/fixtures/research/valid/**`, betroffene `valid_scenarios/**`).
  `decision_history`-Einträge tragen jetzt zusätzlich `full_text_status`. Höherer Pflegeaufwand pro
  Screening-Datensatz, aber strukturell konsistente, vollständig geprüfte Historie statt nur des aktuellen
  Zustands.
- **Migrationsstrategie:** Alle betroffenen Produktivbeispiele und Test-Fixtures wurden im selben Commit
  migriert. Für Produktivdaten nicht zutreffend (noch keine realen Screening-Datensätze zu Retatrutid).

### ADR-0043: Erst-, Zweit- und Endentscheidung strukturell getrennt; zentrale Stage-/Decision-Matrix

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** Im bisherigen Modell (ADR-0039/ADR-0042) trug jeder `decision_history`-Eintrag nur ein
  einzelnes `decision`-Feld, das gleichzeitig als Erstentscheidung UND als effektive/adjudizierte
  Entscheidung diente. Dadurch waren zwei Dinge nicht korrekt abbildbar: (1) eine Adjudikation, die
  die Zweitentscheidung übernimmt (Erst `include` → Zweit `exclude` → Adjudikation `exclude`) ließ
  sich nicht von einer Adjudikation unterscheiden, die die Erstentscheidung bestätigt, ohne die
  urspüngliche Erstentscheidung zu überschreiben; (2) bei einem ungelösten Widerspruch
  (`decision: uncertain`) ging die eigentliche Erstentscheidung vollständig verloren -- niemand
  konnte nachtraeglich sehen, ob urspruenglich `include` oder `exclude` vorgeschlagen war. Zusaetzlich
  erlaubte das allgemeine `screening_decision`-Vokabular fachlich unsinnige Kombinationen wie
  `decision_stage: final` mit `decision: pending` oder `duplicate`.
- **Entscheidung:** Jeder `decision_history`-Eintrag trennt jetzt strukturell:
    - `primary_decision` -- die Entscheidung des Erstpruefers (`decided_by`/`decided_at`), bleibt
      unveraendert erhalten, auch wenn eine Zweitpruefung/Adjudikation die effektive `decision`
      spaeter davon abweichen laesst oder auf `uncertain` setzt.
    - `decision` -- die effektive/aktuelle Entscheidung: identisch mit `primary_decision`, wenn keine
      Zweitpruefung vorliegt oder beide uebereinstimmen; sonst `uncertain` (ungeloest) oder
      `second_review.adjudication.final_decision` (geloest, kann sowohl die Erst- als auch die
      Zweitentscheidung bestaetigen).
    - `second_review.decision_confirmed` ist eine vom Validator geprueft abgeleitete Projektion von
      `reviewer_decision == primary_decision` -- NICHT gegen die effektive `decision` verglichen (das
      war der konkrete Fehler: ein Vergleich gegen die effektive Entscheidung haette einen bereits
      korrekt geloesten Widerspruch faelschlich als "bestaetigt" erscheinen lassen koennen, sobald
      `adjudication.final_decision` zufaellig dem `reviewer_decision` entspricht).
    - Eine Adjudikation ist strukturell verboten, wenn `reviewer_decision == primary_decision` ist
      (kein Konflikt zum Aufloesen), und `adjudication.final_decision` ist auf `include`/`exclude`
      beschraenkt (schema-seitiges Enum).
    - Eine zentrale, wiederverwendbare Stage-/Decision-Matrix (`tools/_researchlib.py::
      ALLOWED_DECISIONS_BY_STAGE`) legt fest, welche Entscheidungen an welcher Stufe fachlich
      sinnvoll sind (z. B. `final` erlaubt nur `include`/`exclude`/`uncertain`, nicht `pending`/
      `duplicate`/`awaiting_full_text`) und wird sowohl gegen `primary_decision` als auch gegen
      `decision` jedes Eintrags geprueft.
    - `duplicate_of` wird zusaetzlich je `decision_history`-Eintrag gespeichert (nicht nur auf
      Top-Level-Ebene), damit der historische Hauptdatensatz-Verweis bei einem Duplikat-Entscheid
      nicht verloren geht.
- **Alternativen:**
    1. *Bisheriges einzelnes `decision`-Feld beibehalten, `decision_confirmed` entfernen* -- verworfen:
       loest das Kernproblem nicht, dass die Erstentscheidung bei einem ungeloesten Widerspruch
       verloren geht.
    2. *Separates `first_review`-Objekt zusaetzlich zu den bestehenden `screened_by`/`screened_at`/
       `decision`-Feldern einfuehren* (wie im Reviewauftrag als Beispiel skizziert) -- verworfen:
       redundant, da `decided_by`/`decided_at`/`primary_decision` bereits exakt die Erstentscheidung
       vollstaendig abbilden; ein zusaetzliches Objekt haette dieselbe Information doppelt gepflegt.
    3. *`primary_decision`/`decision`-Trennung plus zentrale Stage-/Decision-Matrix, bestehende
       Struktur erweitert statt neu aufgebaut* -- **gewählt** (rueckwaertskompatibler Vorschlag aus
       dem Reviewauftrag).
- **Konsequenzen:** Beide zuvor nicht darstellbaren Faelle (Adjudikation bestaetigt vs. ueberstimmt
  die Erstentscheidung) sind jetzt sowohl datenmodellseitig unterscheidbar als auch durch dedizierte
  Tests abgesichert (`adjudication_confirms_primary_decision`,
  `adjudication_overturns_primary_decision`, `unresolved_conflict_preserves_primary_decision`). Alle
  bestehenden `decision_history`-Eintraege in Fixtures und Beispielen mussten um `primary_decision`
  und `duplicate_of` ergaenzt werden (siehe Migrationsstrategie).
- **Migrationsstrategie:** Alle bestehenden `screening_record`-Dateien (Produktivbeispiele,
  Test-Fixtures) wurden automatisiert migriert: `primary_decision` wird, wo nicht explizit ein
  Konflikt modelliert war, auf den bisherigen `decision`-Wert gesetzt (semantisch neutral, da diese
  Faelle nie einen Konflikt hatten); `duplicate_of` je Eintrag wird aus dem Top-Level-Feld
  uebernommen. Fuer Produktivdaten nicht zutreffend (noch keine realen Screening-Datensaetze).

### ADR-0044: Zeitliche Provenienzkette objektübergreifend validiert

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** Bisherige Datumspruefungen (ADR-0037, ADR-0039) waren auf einzelne Objekte oder direkt
  benachbarte Felder beschraenkt (`created_at <= updated_at`, `extracted_at <= verified_at`,
  `screened_at` gegen referenzierte Suchlaeufe). Es gab keine Pruefung, dass eine Extraktion
  tatsaechlich NACH der terminalen Einschlussentscheidung (inkl. Zweitpruefung/Adjudikation) ihres
  Screening-Datensatzes stattfand, oder dass eine Promotion nach der Verifikation ihrer Extraktion
  angelegt wurde -- eine Extraktion haette rechnerisch vor ihrer eigenen wissenschaftlichen
  Freigabe "stattgefunden" haben koennen, ohne dass der Validator das bemerkte.
- **Entscheidung:** `tools/validate_research.py::check_temporal_chain` erzwingt:
  `terminale Screening-Entscheidung/-Zweitpruefung/-Adjudikation <= extraction.extracted_at <=
  extraction.verified_at <= promotion.created_at <= promotion.updated_at`, sowie zusaetzlich fuer
  `promotion_status` `approved_for_creation`/`promoted`/`rejected`:
  `extraction.verified_at <= promotion.review.last_reviewed_at <= promotion.updated_at`. Fuer
  `proposed`/`in_review` gilt diese zweite Regel nicht, da `review.last_reviewed_at` in diesen
  Stadien typischerweise noch `null` ist (kein Review hat stattgefunden) -- das ist kein Fehler,
  sondern der erwartete Zustand vor Abschluss des Reviews.
- **Historische Suchlauf-Provenienz:** Die bereits in ADR-0042 eingefuehrte Pruefung
  "`screened_at` (Top-Level) gegen jeden referenzierten Suchlauf" wurde verallgemeinert auf JEDEN
  einzelnen `decision_history`-Eintrag (nicht nur den letzten): kein Screening-Entscheid (auch kein
  frueher Titel-/Abstract-Entscheid) darf vor dem `executed_at` eines der in `search_run_ids[]`
  referenzierten Suchlaeufe liegen. Eine bewusste, dokumentierte Grenze: `search_run_ids[]` ist eine
  einzige, undifferenzierte Liste ohne Zeitstempel pro Zuordnung. Eine legitime spaetere
  Wiederentdeckung desselben Kandidaten ueber einen neuen Suchlauf sollte deshalb als **neuer**
  `screening_record` modelliert werden (ggf. spaeter ueber `candidate_identifiers` als Duplikat des
  urspruenglichen erkannt, siehe Abschnitt 8), statt `search_run_ids[]` eines bestehenden,
  bereits gescreenten Datensatzes rueckwirkend um einen neueren Suchlauf zu erweitern. Es wurde
  bewusst **keine** zusaetzliche `discovery_events[]`-Struktur mit Suchlauf-zu-Zeitpunkt-Zuordnung
  eingefuehrt, um den Umfang dieser Haertungsrunde nicht ueber die gefundenen Luecken hinaus
  auszudehnen; diese Grenze ist in Abschnitt 34 des Scientific Research Protocol dokumentiert.
- **Alternativen:**
    1. *Keine objektuebergreifende Zeitpruefung, nur die bestehenden lokalen Datumsvergleiche* --
       verworfen: genau diese Luecke wurde im Review explizit benannt.
    2. *`discovery_events[]`-Struktur mit expliziter Suchlauf-zu-Zeitpunkt-Zuordnung sofort
       einfuehren* -- verworfen fuer diese Runde: der Reviewauftrag warnt ausdruecklich davor, eine
       Regel einzufuehren, die legitime spaetere Wiederentdeckungen faelschlich verhindert; eine
       vollstaendige Modellierung dieses Falls ist eine groessere Erweiterung, die eine eigene
       Entscheidung verdient, sobald ein realer Anwendungsfall dafuer vorliegt.
    3. *Objektuebergreifende Kettenpruefung ueber die spaeteste bekannte Freigabe (Adjudikation >
       Zweitpruefung > Erstentscheidung), historische Suchlauf-Pruefung auf alle Historieneintraege
       verallgemeinert, keine `discovery_events`-Struktur* -- **gewählt**.
- **Konsequenzen:** Eine Extraktion, die vor ihrer eigenen Einschlussfreigabe oder vor Abschluss
  einer noetigen Zweitpruefung/Adjudikation datiert ist, wird jetzt zuverlaessig zurueckgewiesen.
  Mehrere bestehende Test-Fixtures aus Runde 2/3 (`promotion_two_reviewers_when_required` u. a.)
  hatten inkonsistente Platzhalter-Datumswerte, die durch diese neue Pruefung aufgedeckt und
  korrigiert wurden.
- **Migrationsstrategie:** Nicht zutreffend fuer Produktivdaten. Betroffene Test-Fixtures wurden im
  selben Commit korrigiert.

### ADR-0045: Promotion-Reviewer-Liste schema-seitig auf Eindeutigkeit und Nicht-Leerheit geprüft

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** ADR-0041 (Runde 3) erzwang nur die *Anzahl* unterschiedlicher, nicht-leerer Reviewer
  (validator-seitig gezaehlt), nicht aber strukturell, dass die einzelnen Kuerzel selbst frei von
  Duplikaten oder Nur-Leerzeichen-Werten sind -- `["reviewer-1", "reviewer-1", "reviewer-2"]` waere
  als "drei Eintraege" durchgerutscht, wenn nur die Rohlaenge gezaehlt worden waere (die Runde-3-
  Implementierung zaehlte zwar bereits `set()`-Distinktheit, aber nicht auf Schema-Ebene, wo es
  jede Konsumentin/jeder Konsument des Schemas direkt sehen kann).
- **Entscheidung:** `schemas/research_promotion_record.schema.json` definiert `review.reviewers`
  jetzt **eigenstaendig** (`uniqueItems: true`, `items.pattern: ".*\\S.*"` fuer mindestens ein
  Nicht-Leerzeichen-Zeichen) statt des gemeinsamen `common.schema.json#/$defs/review_block`, das von
  Entitaeten, Quellen, Claims und Protokollen unveraendert weiterverwendet wird. Der Validator prueft
  nur noch die protokollabhaengige *Mindestanzahl* (>= 2 bei `requires_second_review: true`), da
  Eindeutigkeit/Nicht-Leerheit bereits schema-seitig garantiert ist.
- **Alternativen:**
    1. *`common.schema.json#/$defs/review_block` global um `uniqueItems`/Pattern verschaerfen* --
       verworfen: haette rueckwirkend alle anderen Verwenderinnen (Entitaeten, Quellen, Claims,
       Protokolle) betroffen, ohne dass dort ein gemeldetes Problem vorlag -- eine migrationssichere,
       bewusste allgemeine Entscheidung waere theoretisch moeglich, ist aber ein groesserer Schritt
       als der hier gefundene, promotion-spezifische Mangel rechtfertigt.
    2. *Nur validator-seitige Pruefung verschaerfen (Runde-3-Ansatz beibehalten)* -- verworfen:
       Schema-seitige Constraints sind fuer jede Konsumentin/jeden Konsumenten des Schemas direkt
       sichtbar (z. B. bei Validierung ausserhalb dieses Tools) und nicht auf die Python-Logik in
       `tools/validate_research.py` angewiesen.
    3. *Promotion-spezifische Verschaerfung nur in `research_promotion_record.schema.json`,
       `common.schema.json` unveraendert* -- **gewählt**.
- **Konsequenzen:** Duplikate und Nur-Leerzeichen-Kuerzel werden jetzt bereits beim Schema-Check
  abgelehnt (`has non-unique elements` bzw. Pattern-Fehler), nicht erst durch validator-spezifische
  Logik. Wie bereits in ADR-0041 festgehalten, bleibt unveraendert: Schema und Validator pruefen nur
  die Kuerzel selbst -- ob zwei unterschiedliche Kuerzel tatsaechlich zwei unterschiedliche
  *menschliche* Personen bezeichnen, ist weiterhin organisatorisch, nicht maschinenlesbar
  kontrolliert (keine Actor-Registry in Phase 4A).
- **Migrationsstrategie:** Nicht zutreffend -- betrifft nur `research/promotions/**`, das noch keine
  realen Objekte enthaelt.

### ADR-0046: Stage-/Decision-Matrix auch gegen `second_review.reviewer_decision` geprüft; `deduplication` unterstützt strukturell keine Adjudikation

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** Die in ADR-0043 eingeführte zentrale Stage-/Decision-Matrix
  (`tools/_researchlib.py::ALLOWED_DECISIONS_BY_STAGE`) wurde bislang nur gegen `primary_decision`
  und die effektive `decision` jedes `decision_history`-Eintrags geprüft, nicht aber gegen
  `second_review.reviewer_decision` selbst — eine Zweitprüfung hätte an der Stufe `final` z. B.
  `reviewer_decision: pending` oder `duplicate` eintragen können, obwohl diese Werte an dieser Stufe
  fachlich nie sinnvoll sind. Zusätzlich blieb offen, wie ein Widerspruch an der Stufe
  `deduplication` behandelt wird: `adjudication.final_decision` ist strukturell auf
  `include`/`exclude` beschränkt (ADR-0043), aber `exclude` ist an dieser Stufe fachlich nie
  zulässig und `duplicate` als bestätigtes Adjudikationsergebnis war überhaupt nicht abbildbar — ein
  verpflichtendes Zweitreview mit Adjudikation an dieser Stufe wäre damit nur halb unterstützt
  gewesen.
- **Entscheidung:**
    - `tools/validate_research.py::_check_decision_snapshot` prüft `second_review.reviewer_decision`
      jetzt ebenfalls gegen `ALLOWED_DECISIONS_BY_STAGE[stage]` (dieselbe Matrix, dieselbe Fehlermeldungsform
      wie bei `primary_decision`/`decision`).
    - `deduplication` unterstützt strukturell **keine** Adjudikation: sobald ein
      `decision_history`-Eintrag an dieser Stufe `second_review.adjudication` gesetzt hat, ist das ein
      Validierungsfehler, unabhängig vom Inhalt der Adjudikation. Ein Dedup-Widerspruch (Erst- und
      Zweitprüfung sind sich uneinig, ob ein Kandidat ein Duplikat ist) bleibt stattdessen immer
      `decision: uncertain` (bereits über die bestehende "ohne Adjudikation muss uncertain bleiben"-Regel
      abgedeckt) und wird durch einen **neuen**, späteren `decision_history`-Eintrag aufgelöst, nicht
      rückwirkend durch eine dritte Person an derselben Stufe. `second_review` selbst bleibt an der Stufe
      `deduplication` weiterhin erlaubt (Erst-/Zweitprüfung können sich einig sein oder unaufgelöst
      widersprechen) — nur die Adjudikation ist ausgeschlossen.
    - `screening_policy.dual_reviewer_stages` ist jetzt schema-seitig auf eine neue, engere Aufzählung
      `common.schema.json#/$defs/dual_reviewable_screening_stage` (`title_abstract`/`full_text`/`final`)
      beschränkt statt des allgemeinen `screening_stage`-Vokabulars — `deduplication` kann dort gar nicht
      erst eingetragen werden. Ein verpflichtendes Zweitreview mit Adjudikation ist damit ausschließlich für
      inhaltliche Screening-Entscheidungen vorgesehen, nicht für die rein mechanische Duplikaterkennung
      (die ohnehin bereits durch die separate, identifierbasierte `check_deduplication`-Prüfung abgedeckt
      ist).
- **Alternativen:**
    1. *Adjudikationsmodell stufenspezifisch erweitern, sodass `deduplication` ein drittes
       Adjudikationsergebnis (`duplicate`) zulässt* — verworfen: hätte eine parallele,
       stufenabhängige Variante von `adjudication.final_decision` erfordert (unterschiedliche gültige
       Werte je nachdem, ob das umschließende `second_review` zum Top-Level-Feld oder zu einem
       `decision_history`-Eintrag gehört, mit unterschiedlichen Sibling-Feldnamen `decision_stage` vs.
       `stage`) — deutlich höhere Schema-Komplexität für einen Anwendungsfall, der auch einfacher (durch
       Re-Screening statt Adjudikation) lösbar ist.
    2. *`dual_reviewer_stages` weiterhin frei konfigurierbar lassen, nur validator-seitig vor
       `deduplication` warnen* — verworfen: eine Warnung hätte die halb unterstützte Konfiguration
       weiterhin technisch zugelassen; der Reviewauftrag verlangt ausdrücklich, keine halb unterstützte
       Konfiguration zuzulassen.
    3. *`deduplication` schema-seitig aus `dual_reviewer_stages` ausschließen, Adjudikation an dieser
       Stufe validator-seitig strukturell verbieten, `second_review` selbst dort weiterhin optional
       zulassen* — **gewählt**.
- **Konsequenzen:** Eine Zweitprüfung mit fachlich unpassender Entscheidung an einer Stufe wird jetzt
  zuverlässig zurückgewiesen, unabhängig davon, ob es sich um `primary_decision`, `second_review.
  reviewer_decision` oder die effektive `decision` handelt. Ein Dedup-Konflikt bleibt immer
  nachvollziehbar `uncertain`, statt eine strukturell unvollständige Adjudikation vorzutäuschen.
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten (keine realen `research/**`-Objekte
  außerhalb von Beispielen). Test-Fixtures wurden im selben Commit ergänzt.

### ADR-0047: Vollständige, verlustfreie Drei-Ebenen-Entscheidungsprovenienz

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** ADR-0043 trennte `primary_decision` (Erstentscheidung) strukturell von der effektiven
  `decision`, aber `decision_reason` und `duplicate_of` existierten weiterhin nur einmal — für die
  effektive Ebene. Wich die Endentscheidung von der Erstentscheidung ab (z. B. eine Adjudikation
  überstimmt einen ursprünglichen `exclude`-Entscheid mit Begründung `wrong_substance`), ging die
  Begründung/der Duplikatverweis der Erstentscheidung vollständig verloren. Dasselbe Problem bestand
  für die Begründung der Zweitprüfung selbst, sobald sie von der Erst- oder Endentscheidung abwich.
- **Entscheidung:** Jeder `decision_history`-Eintrag und jedes `second_review`-Objekt speichern jetzt
  drei vollständig unabhängige, verlustfreie Ebenen:
    - `primary_decision_reason`/`primary_duplicate_of` (Erstentscheidung, `decision_history`-Eintrag)
    - `second_review.reviewer_decision_reason`/`second_review.reviewer_duplicate_of` (Zweitprüfung)
    - `decision_reason`/`duplicate_of` (effektive/adjudizierte Entscheidung, unverändert seit ADR-0043)

  Für jede der drei Ebenen gilt schema-seitig dieselbe bedingte Regel wie bisher nur für die effektive
  Ebene: der jeweilige Grund ist Pflicht (nicht `null`) genau dann, wenn die zugehörige Entscheidung
  `exclude` ist, und der jeweilige Duplikatverweis ist Pflicht (nicht `null`) genau dann, wenn die
  zugehörige Entscheidung `duplicate` ist — je unabhängig für Erst-, Zweit- und Endentscheidung. Die
  neuen `_duplicate_of`-Felder werden ausschließlich schema-seitig auf Formatgültigkeit geprüft (Pattern),
  nicht referenziell gegen existierende `screening_record`-IDs — anders als das bestehende, effektive
  `duplicate_of` (siehe Grenzen unten).
- **Alternativen:**
    1. *Alternative, umbenannte Objektstruktur (`primary_review`/`second_review`/`effective_decision`
       als drei parallele Unterobjekte)* — im Reviewauftrag als langfristig sauberer bezeichnet, aber
       verworfen für diese Runde: hätte `primary_decision`/`decision` (ADR-0043, bereits durch mehrere
       Testrunden gehärtet) umbenennen und alle bestehenden Konsumenten/Fixtures migrieren müssen, ohne
       einen zusätzlichen fachlichen Nutzen gegenüber der additiven Lösung zu bieten.
    2. *Nur eine gemeinsame `decision_reason`/`duplicate_of` für alle drei Ebenen beibehalten, Verlust
       bei Abweichung in Kauf nehmen* — verworfen: genau das ist die im Reviewauftrag benannte Lücke.
    3. *Additive, gleich benannte Felder je Ebene (`primary_decision_reason`/`primary_duplicate_of`,
       `reviewer_decision_reason`/`reviewer_duplicate_of`), bestehende Feldnamen unverändert* —
       **gewählt**.
- **Konsequenzen:** Ein überstimmter Erstentscheid (z. B. `primary_decision: exclude` mit Grund
  `wrong_substance`, später durch Adjudikation zu `include` überstimmt) bleibt jetzt vollständig
  nachvollziehbar, ebenso ein unaufgelöster Duplikat-Widerspruch (`primary_decision: duplicate` mit
  `primary_duplicate_of`, während die Zweitprüfung widerspricht und die effektive Entscheidung
  `uncertain` bleibt). **Bekannte Grenze:** `primary_duplicate_of`/`reviewer_duplicate_of` werden — anders
  als das effektive `duplicate_of` — nicht referenziell gegen existierende `screening_record`-IDs oder auf
  Zyklen geprüft; dies wurde bewusst nicht ergänzt, um den Umfang dieser Runde nicht über die im
  Reviewauftrag benannte Lücke hinaus auszudehnen (siehe Scientific Research Protocol, Abschnitt 34).
- **Migrationsstrategie:** Alle bestehenden `screening_record`-Dateien (Produktivbeispiele,
  Test-Fixtures) wurden automatisiert migriert: `primary_decision_reason`/`primary_duplicate_of`
  wurden aus dem jeweiligen Eintrags-`decision_reason`/`duplicate_of` übernommen (semantisch neutral
  für alle Fälle ohne Konflikt zwischen Erst- und Endentscheidung), `reviewer_decision_reason`/
  `reviewer_duplicate_of` analog aus dem umschließenden Objekt. Für Produktivdaten nicht zutreffend
  (noch keine realen Screening-Datensätze).

### ADR-0048: Objektinterne zeitliche Vollständigkeit (`created_at`/`updated_at` gegen jedes dokumentierte Ereignis)

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** ADR-0044 prüft die zeitliche Provenienzkette OBJEKTÜBERGREIFEND (Screening →
  Extraktion → Verifikation → Promotion), und `check_misc_consistency` prüfte bereits die einfache
  Reihenfolge `created_at <= updated_at` je Objekt. Es fehlte jedoch eine Prüfung, dass jedes von
  einem Objekt SELBST dokumentierte Ereignisdatum (z. B. `decision_history[].decided_at`,
  `second_review.reviewed_at`, `adjudication.resolved_at`, `extracted_at`, `verified_at`,
  `review.last_reviewed_at`, das Datum aus `executed_at`) tatsächlich innerhalb von dessen eigenem
  `[created_at, updated_at]`-Intervall liegt. Zwei bereits akzeptierte Positiv-Fixtures
  (`valid_stage_decision_matrix`, `valid_full_temporal_chain`) hatten `updated_at` VOR einer
  Entscheidung/Zweitprüfung/Adjudikation, die im selben Datensatz dokumentiert war — ein Datensatz kann
  nicht vor einem in ihm dokumentierten Ereignis zuletzt aktualisiert worden sein.
- **Entscheidung:** Eine neue Prüfung `tools/validate_research.py::check_object_temporal_bounds`
  erzwingt für jede der fünf Research-Objektarten `created_at <= Ereignisdatum <= updated_at`,
  unabhängig für jedes gespeicherte Ereignis:
    - `screening_record`: für JEDEN `decision_history`-Eintrag `decided_at`, und wo vorhanden
      `second_review.reviewed_at` sowie `second_review.adjudication.resolved_at`.
    - `extraction_record`: `extracted_at`, und wo gesetzt `verified_at`.
    - `promotion_record`: wo nicht `null`, `review.last_reviewed_at`.
    - `research_search_run`: das Kalenderdatum aus `executed_at` (Zeitanteil wird für den Vergleich
      abgeschnitten, da `created_at`/`updated_at` reine Kalenderdaten sind).
    - `research_protocol`: wo nicht `null`, `review.last_reviewed_at`.

  Konvention (einheitlich für alle fünf Objektarten, siehe Scientific Research Protocol, Abschnitt 9d):
  `created_at` ist der Zeitpunkt, zu dem der Recherche-Datensatz (der Fall/Vorgang) angelegt wurde —
  typischerweise VOR den darin dokumentierten Ereignissen (ein Screening-Datensatz wird angelegt,
  sobald ein Kandidat gefunden wurde; die eigentliche Entscheidung folgt später). `updated_at` ist der
  Zeitpunkt der letzten Bearbeitung und muss daher mindestens so aktuell sein wie jedes im Datensatz
  gespeicherte Ereignisdatum. Diese Konvention gilt unverändert auch für `research_search_run` — kein
  objektspezifisches, abweichendes Datumsmodell.
- **Alternativen:**
    1. *Keine zusätzliche Prüfung, da `check_temporal_chain` (ADR-0044) die fachlich wichtigste Kette
       bereits objektübergreifend absichert* — verworfen: die beiden betroffenen Positiv-Fixtures
       zeigen konkret, dass ein Objekt intern inkonsistent sein kann, ohne dass die objektübergreifende
       Kette das bemerkt (die Kettenprüfung vergleicht nur Objektgrenzen, nicht `updated_at` gegen
       Ereignisse INNERHALB desselben Objekts an jeder Stelle).
    2. *Nur `updated_at` gegen das jeweils letzte/aktuellste Ereignis prüfen, nicht gegen jeden
       einzelnen `decision_history`-Eintrag* — verworfen: hätte eine inkonsistente Datumsangabe bei
       einem NICHT-terminalen Historieneintrag übersehen.
    3. *Einheitliche, objektartenübergreifende `created_at <= Ereignis <= updated_at`-Prüfung für alle
       fünf Research-Objektarten, mit explizit dokumentierter `created_at`-Konvention* — **gewählt**.
- **Konsequenzen:** Die beiden betroffenen Positiv-Fixtures wurden korrigiert (`updated_at`
  entsprechend angehoben). Ein Objekt mit einem `updated_at` vor einem selbst dokumentierten Ereignis
  wird jetzt zuverlässig zurückgewiesen, mit klarer Fehlermeldung je betroffenem Feldpaar.
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten. Betroffene Test-Fixtures wurden im
  selben Commit korrigiert.

### ADR-0049: `rejected`-Promotions erfordern dieselbe Mindest-Audit-Spur wie `approved_for_creation`/`promoted`

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** `research_promotion_record.schema.json` erzwang eine vollständige Audit-Spur
  (`review.last_reviewed_at`, mindestens ein Reviewer, nicht-leere `decision_rationale`) bislang nur
  für `promotion_status: approved_for_creation`/`promoted`. Ein `promotion_status: rejected` konnte
  ohne Reviewdatum, Reviewer oder Begründung existieren — eine Ablehnung ist jedoch eine ebenso
  konsequenzreiche wissenschaftliche/redaktionelle Entscheidung wie eine Freigabe und muss ebenso
  nachvollziehbar sein.
- **Entscheidung:** Die bestehende schema-seitige `allOf`-Regel (bislang nur für
  `approved_for_creation`/`promoted`) gilt jetzt symmetrisch auch für `rejected`: `review.
  last_reviewed_at` (String, nicht `null`), `review.reviewers` (mindestens ein Eintrag) und
  `decision_rationale` (nicht-leerer String) sind für jede der drei ENDGÜLTIGEN Promotion-Entscheidungen
  Pflicht. `proposed`/`in_review`/`withdrawn` sind davon unverändert ausgenommen, da dort noch keine
  endgültige Entscheidung getroffen wurde. Zusätzlich prüft `tools/validate_research.py::
  check_promotion_records` die protokollabhängige Mindestanzahl unterschiedlicher Reviewer
  (`claim_promotion_policy.requires_second_review`, ADR-0041) jetzt ebenfalls symmetrisch für
  `approved_for_creation`/`promoted`/`rejected` statt nur für die ersten beiden — eine Ablehnung bei
  aktivierter Zweitprüfpflicht benötigt also ebenfalls mindestens zwei unterschiedliche Reviewer-Kürzel.
  `canonical_claim_id: null` bei `rejected` bleibt unverändert (bereits seit Runde 1 erzwungen).
- **Alternativen:**
    1. *`rejected` benötigt bewusst nur einen Reviewer, auch wenn `requires_second_review: true` gilt*
       — verworfen: eine Ablehnung kann ebenso strittig/folgenreich sein wie eine Freigabe (ein zu
       Unrecht abgelehnter Kandidatenclaim geht ohne Zweitmeinung verloren); der Reviewauftrag verlangt
       ausdrücklich eine bewusste, dokumentierte Entscheidung statt einer stillschweigenden Ausnahme.
    2. *Eigene, von `approved_for_creation`/`promoted` unabhängige (schwächere) Mindestanforderung für
       `rejected`* — verworfen: keine fachliche Begründung, warum eine Ablehnung eine geringere
       Nachvollziehbarkeitspflicht haben sollte als eine Freigabe.
    3. *Symmetrische Mindest-Audit-Spur (Reviewdatum, Reviewer, Begründung) UND symmetrische
       Zweitprüfpflicht für alle drei endgültigen Promotion-Zustände* — **gewählt**.
- **Konsequenzen:** Ein `rejected`-Datensatz ohne Reviewer/Reviewdatum/Begründung wird jetzt
  schema-seitig zurückgewiesen; bei aktivierter Zweitprüfpflicht wird ein einzelner Reviewer bei
  `rejected` validator-seitig zurückgewiesen (dieselbe Fehlermeldung wie bei
  `approved_for_creation`/`promoted`, siehe ADR-0041). Ein bereits bestehendes Produktivbeispiel
  (`research/examples/promotions/promotion-record-b0000000-…-000000000001.yaml`, `rejected` mit nur
  einem Reviewer bei aktivierter Zweitprüfpflicht) wurde im selben Commit auf zwei Reviewer erweitert.
- **Migrationsstrategie:** Ein Produktivbeispiel wurde angepasst (siehe oben; `research/examples/**`
  ist kein kanonisches Wissen, sondern illustratives Beispielmaterial). Betroffene Test-Fixtures wurden
  im selben Commit korrigiert/ergänzt.

### ADR-0050: Stabile Research-Actor-ID-Syntax (`research_actor_id`) ohne Actor-Registry

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** Research-Akteursfelder (`screened_by`, `decided_by`, `second_review.reviewed_by`,
  `adjudication.resolved_by`, `extracted_by`, `verified_by`, `promotion.review.reviewers[]`,
  `protocol.review.reviewers[]`) verwendeten bislang uneinheitliche, schwache Constraints (`type:
  string, minLength: 1` bzw., für `promotion.review.reviewers[]` seit ADR-0045, ein reines
  Nicht-Leerzeichen-Pattern). Ein Kürzel mit führendem/nachgestelltem Leerzeichen oder abweichender
  Groß-/Kleinschreibung (`"reviewer-1"` vs. `" reviewer-1"` vs. `"Reviewer-1"`) hätte dieselbe Person
  syntaktisch als zwei unterschiedliche Kürzel erscheinen lassen können oder umgekehrt eine
  Unabhängigkeitsprüfung (z. B. `second_review.reviewed_by != decided_by`, ADR-0039) durch eine
  triviale Leerzeichenvariante unterlaufen können.
- **Entscheidung:** `common.schema.json` definiert eine neue, wiederverwendbare Definition
  `research_actor_id` (`^[a-z0-9][a-z0-9._-]*$` — beginnt mit einem alphanumerischen Kleinbuchstaben,
  danach nur Kleinbuchstaben, Ziffern, Punkt, Unterstrich, Bindestrich; kein Leerzeichen, keine
  Großschreibung). Angewendet auf alle acht oben genannten Felder in
  `research_screening_record.schema.json`, `research_extraction_record.schema.json`,
  `research_promotion_record.schema.json` und `research_protocol.schema.json` (jeweils inkl.
  `verified_by`, das weiterhin `null` sein darf, solange keine Verifikation stattgefunden hat). Die
  gemeinsame `common.schema.json#/$defs/review_block` (verwendet von Entitäten, Quellen, Claims,
  Protokollen außerhalb der Research-Ebene, sowie von `research_search_run.review`) bleibt bewusst
  unangetastet (siehe bereits ADR-0045) — `research_search_run.review.reviewers`/`executed_by` sind
  nicht Teil dieser Härtung, da im Reviewauftrag nicht benannt.
- **Grenze (ausdrücklich dokumentiert):** Die Syntax stellt nur sicher, dass zwei unterschiedliche
  Kürzel STABIL unterscheidbar sind. Sie beweist NICHT, dass zwei unterschiedliche Kürzel zwei
  unterschiedliche MENSCHLICHE Personen repräsentieren — das bleibt wie bereits in ADR-0041
  festgehalten organisatorisch, nicht maschinenlesbar kontrolliert (keine Actor-Registry, weiterhin
  Lösung B).
- **Alternativen:**
    1. *Actor-Registry mit vordefinierten, verifizierten Kürzeln einführen* — verworfen: bereits in
       ADR-0041 explizit gegen eine Actor-Registry entschieden (Lösung B); dieser Reviewauftrag
       bestätigt ausdrücklich, dass diese Entscheidung bestehen bleibt.
    2. *Nur validator-seitiges Trimmen/Normalisieren der Kürzel vor dem Vergleich, Schema unverändert*
       — verworfen: hätte das Problem verschleiert statt es sichtbar zu machen — ein Kürzel mit
       Leerzeichen wäre weiterhin in der YAML-Datei sichtbar uneinheitlich geblieben.
    3. *Restriktives, dokumentiertes Format schema-seitig erzwingen (keine Registry, keine
       Normalisierung), einheitlich über alle Research-Actor-Felder* — **gewählt**.
- **Konsequenzen:** Kürzel mit Leerzeichen oder Großschreibung werden jetzt bereits beim Schema-Check
  abgelehnt. Alle bestehenden Kürzel in Produktivbeispielen und Test-Fixtures (`reviewer-1` …
  `reviewer-4`) erfüllten das neue Muster bereits ohne Änderung.
- **Migrationsstrategie:** Nicht zutreffend — keine bestehenden Werte mussten angepasst werden.

### ADR-0051: `screening_policy.dual_reviewer_stages` muss Teilmenge von `screening_policy.stages` sein

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** Ein Protokoll konnte bislang eine Stufe in `screening_policy.dual_reviewer_stages`
  eintragen, die gar nicht in `screening_policy.stages` konfiguriert war — die Zweitprüferpflicht
  hätte damit auf eine Stufe verwiesen, die für dieses Protokoll überhaupt nicht durchlaufen wird.
- **Entscheidung:** `tools/validate_research.py::check_misc_consistency` prüft jetzt zusätzlich, dass
  jede Stufe in `screening_policy.dual_reviewer_stages` auch in `screening_policy.stages` enthalten
  ist. `deduplication` kann dort ohnehin nicht mehr eingetragen werden (schema-seitig durch ADR-0046
  ausgeschlossen); diese Prüfung sichert zusätzlich, dass die verbleibenden Werte
  (`title_abstract`/`full_text`/`final`) tatsächlich zu den für dieses Protokoll konfigurierten
  Stufen gehören.
- **Alternativen:**
    1. *Keine zusätzliche Prüfung, da eine nicht konfigurierte Stufe ohnehin nie einen
       `decision_history`-Eintrag erhält und die Regel damit praktisch folgenlos bliebe* — verworfen:
       ein widersprüchlich konfiguriertes Protokoll ist redaktionell irreführend, unabhängig davon, ob
       der Widerspruch je praktisch relevant wird — der Reviewauftrag verlangt ausdrücklich, dies als
       Validierungsfehler zu behandeln.
    2. *Teilmengenbeziehung schema-seitig statt validator-seitig erzwingen* — verworfen: JSON Schema
       kann eine Teilmengenbeziehung zwischen zwei Arrays desselben Objekts nicht ohne unverhältnismäßig
       komplexe `contains`/`not`-Konstruktionen ausdrücken; eine einfache validator-seitige Prüfung ist
       hier die klarere Lösung (analog zu vielen anderen Cross-Field-Prüfungen in diesem Validator).
    3. *Validator-seitige Teilmengenprüfung* — **gewählt**.
- **Konsequenzen:** Ein Protokoll mit einer nicht konfigurierten Zweitprüferstufe wird jetzt
  zuverlässig zurückgewiesen.
- **Migrationsstrategie:** Nicht zutreffend — alle bestehenden Protokolle (Produktivbeispiele,
  Test-Fixtures) erfüllten die Teilmengenbeziehung bereits.

### ADR-0052: Historische Duplikatverweise referenziell geprüft; unterschiedliche Duplikatziele als Konflikt behandelt

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** Runde 5 (ADR-0047) führte `primary_duplicate_of` und `second_review.
  reviewer_duplicate_of` als eigenständige, verlustfreie Duplikatverweise je Entscheidungsebene ein,
  prüfte sie aber ausdrücklich nur auf Formatgültigkeit (Pattern), nicht referenziell — dokumentiert
  als bewusste Grenze, um den Umfang von Runde 5 nicht auszudehnen. Diese Grenze erwies sich als zu
  weitreichend: ein `primary_duplicate_of`, das auf einen nicht existierenden, protokollfremden oder
  den eigenen Datensatz verweist, blieb unbemerkt — obwohl genau dieselbe Prüfung für die effektive
  Top-Level-`duplicate_of` bereits seit Runde 2/4 (ADR-0039/ADR-0042) besteht. Zusätzlich behandelte
  die bestehende `decision_confirmed`-Projektion (`reviewer_decision == primary_decision`, ADR-0043)
  zwei `duplicate`-Entscheidungen bereits als „bestätigt", sobald nur die Entscheidungs**kategorie**
  übereinstimmte — auch wenn `primary_duplicate_of` und `second_review.reviewer_duplicate_of` auf
  **unterschiedliche** Hauptdatensätze zeigten. Zwei Prüfungen, die beide „ist ein Duplikat" sagen,
  aber unterschiedlicher Meinung sind, WESSEN Duplikat es ist, sind keine echte Übereinstimmung.
- **Entscheidung:**
    1. **Referenzielle Prüfung historischer Duplikatverweise** (`tools/validate_research.py::
       check_historical_duplicate_targets`): für `decision_history[].primary_duplicate_of`,
       `decision_history[].second_review.reviewer_duplicate_of` und `decision_history[].duplicate_of`
       gilt bei nicht-`null`-Wert je Feld unabhängig: das Ziel muss als `screening_record` existieren,
       zum selben `protocol_id` gehören, und darf nicht der eigene Datensatz sein. Fehler werden am
       exakten Feldpfad gemeldet (z. B. `$.decision_history[0].primary_duplicate_of`). Bewusst **nur
       ein einzelner Hop** — anders als die bestehende Ketten-/Zyklenprüfung für die EFFEKTIVE
       Top-Level-`duplicate_of` (unverändert, siehe unten) läuft hier keine Kettenverfolgung: die
       historischen Felder sind Momentaufnahmen einer einzelnen Entscheidung, keine fortlaufend
       gepflegte Verweiskette.
    2. **Zielkonflikt bei `duplicate`**: `_check_decision_snapshot` erweitert die Definition von
       „übereinstimmend" (bislang nur `reviewer_decision == primary_decision`) für den Fall
       `reviewer_decision == primary_decision == 'duplicate'` um eine zusätzliche Bedingung:
       `second_review.reviewer_duplicate_of == primary_duplicate_of`. `decision_confirmed` muss diese
       erweiterte Übereinstimmung korrekt projizieren — `decision_confirmed: true` bei unterschiedlichen
       Zielen ist ein Validierungsfehler. Da `deduplication` seit ADR-0046 strukturell keine Adjudikation
       unterstützt, folgt aus der bestehenden Konfliktlogik automatisch: die effektive `decision` bleibt
       `uncertain`, `duplicate_of` bleibt `null` (schema-seitig erzwungen), und der Widerspruch wird durch
       einen **neuen** `decision_history`-Eintrag aufgelöst, nicht durch Adjudikation. Für alle anderen
       Entscheidungswerte (`include`/`exclude`/`pending`/`awaiting_full_text`/`uncertain`) bleibt die
       bisherige reine Wertegleichheit unverändert maßgeblich.
- **Alternativen (zu Punkt 1):**
    1. *Auch die historischen Felder mit voller Ketten-/Zyklenverfolgung prüfen* — verworfen: eine
       historische Momentaufnahme repräsentiert nicht „die aktuell gültige Kette", sondern nur, was zu
       diesem Zeitpunkt von dieser einen Person eingetragen wurde — eine Kettenverfolgung würde eine
       Vollständigkeits-/Aktualitätsgarantie vortäuschen, die für vergangene Einzelentscheidungen fachlich
       nicht sinnvoll ist. Die volle Ketten-/Zyklensemantik bleibt bewusst auf die effektive,
       redaktionell gepflegte Top-Level-`duplicate_of` beschränkt.
    2. *Weiterhin nur Formatprüfung, keine referenzielle Prüfung* — verworfen: genau diese Lücke wurde
       im Folgeauftrag benannt; die Inkonsistenz zur bereits bestehenden Prüfung der effektiven
       `duplicate_of` war nicht mehr zu rechtfertigen.
    3. *Referenzielle Einzel-Hop-Prüfung für alle drei historischen Felder, volle Ketten-/
       Zyklensemantik weiterhin nur für die effektive Top-Level-`duplicate_of`* — **gewählt**.
- **Alternativen (zu Punkt 2):**
    1. *Zielkonflikt ignorieren, nur die Entscheidungskategorie vergleichen (bisheriges Verhalten)* —
       verworfen: genau der im Folgeauftrag benannte Fehler.
    2. *Adjudikationsmodell für `deduplication` doch öffnen, um einen Zielkonflikt aufzulösen* —
       verworfen: widerspricht der in ADR-0046 bewusst getroffenen, begründeten Entscheidung, dass
       `deduplication` keine Adjudikation unterstützt (siehe dortige Alternativenabwägung); ein
       Zielkonflikt ist inhaltlich derselbe Fall wie ein Entscheidungskonflikt und verdient dieselbe
       Lösung (neuer Historieneintrag).
    3. *`decisions_agree` bei `duplicate` inhaltlich erweitern (Entscheidung UND Ziel), bestehende
       Konflikt-/Adjudikationslogik unverändert wiederverwenden* — **gewählt**: nutzt die bereits
       vorhandene, gehärtete Infrastruktur (uncertain-Fallback, Adjudikationsverbot bei
       `deduplication`) ohne Sonderfallcode.
- **Konsequenzen:** Ein historischer Duplikatverweis auf einen nicht existierenden, protokollfremden
  oder den eigenen Datensatz wird jetzt zuverlässig zurückgewiesen, unabhängig davon, ob es sich um
  `primary_duplicate_of`, `second_review.reviewer_duplicate_of` oder `decision_history[].duplicate_of`
  handelt. Zwei `duplicate`-Entscheidungen mit unterschiedlichen Zielen werden nicht mehr fälschlich als
  Konsens akzeptiert. Ein bereits akzeptiertes Runde-5-Positiv-Fixture
  (`primary_duplicate_target_preserved_during_conflict`) verwies auf einen nicht existierenden
  Platzhalter-Datensatz und wurde um einen echten, protokollinternen Zieldatensatz ergänzt.
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten. Ein Test-Fixture wurde im selben Commit
  korrigiert (siehe oben).

### ADR-0053: Effektives `duplicate_of` deterministisch an das bestätigte Duplikatziel gebunden

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** ADR-0052 prüfte bei einer bestätigten `duplicate`-Übereinstimmung
  (`decision_confirmed: true`), dass `primary_duplicate_of == second_review.reviewer_duplicate_of`
  gilt — stellte aber nicht sicher, dass die **effektive** `duplicate_of` dieses bestätigte Ziel
  tatsächlich übernimmt. Ein Datensatz konnte also z. B. `primary_duplicate_of: A`,
  `second_review.reviewer_duplicate_of: A` (beide einig, `decision_confirmed: true`) tragen, während
  die effektive `duplicate_of` unbemerkt auf einen dritten, ansonsten vollständig gültigen
  Screening-Datensatz `C` zeigte. Dieselbe Lücke bestand ohne Zweitprüfung: `primary_decision:
  duplicate` mit `primary_duplicate_of: A`, aber effektive `duplicate_of: B`, ohne dass irgendeine
  Prüfung das als Widerspruch erkannte.
- **Entscheidung:** `_check_decision_snapshot` bindet das effektive `duplicate_of` jetzt
  deterministisch an das durch die vorhandene Provenienz bestätigte Ziel:
    - **Ohne Zweitprüfung:** bei `primary_decision: duplicate` muss `duplicate_of ==
      primary_duplicate_of` gelten.
    - **Mit bestätigtem Duplikatkonsens** (`reviewer_decision == primary_decision == 'duplicate'`
      UND `reviewer_duplicate_of == primary_duplicate_of`, siehe ADR-0052): `duplicate_of` muss
      ebenfalls diesem gemeinsamen Ziel entsprechen. Alle drei Ebenen — `primary_duplicate_of`,
      `second_review.reviewer_duplicate_of`, effektive `duplicate_of` — müssen identisch sein.
    - **Bei Zielkonflikt** (unterschiedliche Ziele, `decision_confirmed: false`): unverändert nach
      ADR-0052/ADR-0046 — `decision` bleibt `uncertain`, `duplicate_of` bleibt `null` (bereits
      schema-seitig erzwungen, da `duplicate_of` nur bei `decision: duplicate` gesetzt sein darf),
      keine Adjudikation möglich, Auflösung nur durch einen neuen `decision_history`-Eintrag.
- **Alternativen:**
    1. *Keine zusätzliche Prüfung, da `primary_duplicate_of`/`reviewer_duplicate_of` bereits die
       inhaltlich relevante Information tragen* — verworfen: die effektive `duplicate_of` ist das
       Feld, das andere Prüfungen (Referenzintegrität, Top-Level-Projektion, künftige Auswertungen)
       tatsächlich konsumieren; ein unbemerkter dritter Wert dort untergräbt die gesamte
       Drei-Ebenen-Provenienz aus ADR-0047/ADR-0052.
    2. *Effektives Ziel nur bei bestätigtem Konsens prüfen, den Fall ohne Zweitprüfung offen lassen*
       — verworfen: der Reviewauftrag benennt beide Fälle ausdrücklich als gleichwertig zu schließende
       Lücken; ohne Zweitprüfung ist die Erstentscheidung die einzige Quelle des effektiven Zustands,
       eine Abweichung dort ist ebenso unbegründet.
    3. *Deterministische Bindung in beiden Fällen (ohne Zweitprüfung, bei bestätigtem Konsens), Konflikt-
       fall unverändert nach ADR-0052* — **gewählt**.
- **Konsequenzen:** Ein effektives `duplicate_of`, das vom bestätigten Ziel abweicht, wird jetzt
  zuverlässig zurückgewiesen — auch wenn der abweichende Wert selbst ein vollständig gültiger,
  protokollinterner, existierender Screening-Datensatz ist (der reine Referenzcheck aus ADR-0052
  allein hätte diesen Fall nicht erkannt). Vorher als „nur formatgeprüft, nicht referenziell"
  dokumentierte Stellen in Schema-Beschreibungen und Projektdokumentation, die durch ADR-0052 bereits
  überholt, aber nicht überall konsistent nachgezogen worden waren, wurden im selben Commit korrigiert
  (`schemas/research_screening_record.schema.json`, Scientific Research Protocol Abschnitt 9c,
  Evidence Curation Workflow, `research/screening/README.md`).
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten. Keine bestehenden Test-Fixtures
  verletzten die neue Regel (die betroffenen Runde-5B-Fixtures verwendeten bereits konsistente
  Zielwerte).

### ADR-0054: Formale Freigabe des Retatrutid-Rechercheprotokolls v1 (Phase 4B-0)

- **Status:** Entschieden
- **Datum:** 2026-07-26
- **Kontext:** `research-protocol-retatrutide-v1.yaml` lag seit Phase 4A als vollständig
  ausgearbeitetes, aber unfreigegebenes Protokoll (`status: draft`) vor. Phase 4B (die
  eigentliche, reale Recherche zu Retatrutid) darf laut Protokoll und Scientific Research
  Protocol erst nach formalem Review und Freigabe des Protokolls beginnen.
- **Entscheidung:** Das Protokoll wurde ausschließlich in seinen formalen Freigabefeldern
  geändert (`status: draft` → `approved`, `updated_at`, `review.last_reviewed_at`,
  `review.reviewers`, `review.approval_decision`). Freigebende Projektrolle ist
  `cso-chatgpt` — dies bezeichnet ausdrücklich den KI-basierten Chief Scientific Officer des
  Projekts, keine menschliche Person. Forschungsfragen, Suchbegriffe, Ein-/Ausschlusskriterien,
  Quellenprioritäten, Dedup-/Screening-/Extraktions-/Evidenzregeln bleiben unverändert. Diese
  Freigabe erlaubt ausschließlich die kontrollierte Recherche gemäß dem bestehenden Protokoll
  (Search Runs, Screening, Extraktion). Sie erlaubt **keine** automatische Übernahme von
  Research-Daten in kanonische Claims, den Katalog oder den Knowledge Graph — jede Promotion
  bleibt an `claim_promotion_policy` (Second Review) gebunden, `research/**` fließt weiterhin
  nicht automatisch in Katalog/Graph.
- **Konsequenzen:** Phase 4B-0 (Protokollfreigabe) ist damit abgeschlossen. Die reale
  Recherche (Search Runs, Screening, Extraktion) ist ab diesem Zeitpunkt protokollkonform
  zulässig, wurde aber im Rahmen dieser Änderung selbst noch nicht begonnen — es wurden keine
  Search-Run-, Screening-, Extraction- oder Promotion-Datensätze angelegt und keine realen
  Quellen, Studien oder Claims ergänzt.

### ADR-0055: Versionierte Identifier-Manifeste für reproduzierbare Search Runs

- **Status:** Entschieden
- **Datum:** 2026-07-27
- **Kontext:** Phase 4B-1A legte vier `research_search_run`-Datensätze für Retatrutid-Basissuchen an
  (PubMed via NCBI E-utilities ESearch, ClinicalTrials.gov API v2), die jeweils nur Query, Zeitpunkt
  und Trefferzahl (`result_count`) speicherten. Die vollständigen PMID-/NCT-ID-Listen lagen
  ausschließlich unter `research/raw/**` — per `.gitignore` nicht versioniert. Datenbanken verändern
  sich jedoch über Zeit (neue Publikationen, zurückgezogene Einträge, geänderte Indexierung): eine
  identische Query zu einem späteren Zeitpunkt kann eine andere Treffermenge liefern. Die reine
  Trefferzahl reicht damit für historische Reproduzierbarkeit nicht aus — ohne die tatsächlich
  erhaltene Identifikatormenge selbst wäre das ursprüngliche Result Set nach einer erneuten Ausführung
  nicht mehr rekonstruierbar, und ein späterer Prüfer könnte nicht nachvollziehen, welche konkreten
  Datensätze ein Suchlauf tatsächlich gefunden hat.
- **Entscheidung:**
    - Neue Research-Objektart `research_search_result_manifest` (Schema
      `schemas/research_search_result_manifest.schema.json`, Ordner `research/search_results/`,
      Dateiname `search-result-manifest-<uuid4>.yaml`): enthält ausschließlich die kanonisch
      sortierten, eindeutigen stabilen Identifikatoren (`identifier_type: pmid` numerisch aufsteigend,
      `nct_id` lexikografisch aufsteigend), `count`, einen verbindlichen SHA-256-Hash über
      `("\n".join(identifiers) + "\n").encode("utf-8")`, und einen Verweis auf den lokalen,
      NICHT versionierten Rohexport (`source_export_reference`, Pfadhinweis unter `research/raw/`,
      nicht die Datei selbst). Enthält bewusst KEINE Abstracts, Titel, Volltexte oder sonstigen
      urheberrechtlich geschützten Inhalte — stabile Identifikatoren allein dürfen versioniert werden,
      vollständige API-Antworten/Abstracts/PDFs bleiben weiterhin außerhalb von Git.
    - `research_search_run` erhält ein Pflichtfeld `result_capture`: `status: complete` (mit
      `manifest_id`, `rationale: null`) verweist auf ein existierendes Manifest, das seinerseits über
      `search_run_id` gegenseitig zurückverweist; `status: unavailable` (mit `manifest_id: null`,
      Pflicht-`rationale`) dokumentiert einen echten Grund, warum kein Manifest erzeugt wurde (z. B.
      keine stabile Gesamttrefferzahl, gesperrte automatisierte Anfrage). `result_capture` ist für
      JEDEN ausgeführten Suchlauf Pflicht.
    - Zusätzliches Pflichtfeld `request_parameters` auf `research_search_run`: rein technische,
      niemals geheime API-Parameter (z. B. `db`/`retmode`/`retmax`/`retstart` bei NCBI E-utilities,
      `query_parameter`/`countTotal`/`pageSize`/`format` bei ClinicalTrials.gov API v2) — bewusst
      getrennt von `filters` (inhaltliche/wissenschaftliche Sucheinschränkungen). Optionales Feld
      `pagination` (`pages_retrieved`, `completion_confirmed`) dokumentiert bei einem paginierenden
      Interface, dass tatsächlich alle Seiten abgerufen wurden.
    - `research_search_run.executed_by` referenziert jetzt `common.schema.json#/$defs/research_actor_id`
      (statt eines unbeschränkten Strings) — dieselbe restriktive, leerzeichen-/
      grossschreibungsfreie Kürzel-Syntax wie bei allen anderen Research-Akteursfeldern (ADR-0050).
      Bekannte Grenze bleibt unverändert bestehen: eine syntaktisch stabile Actor-ID beweist nicht,
      dass dahinter eine bestimmte menschliche Person steht.
    - `tools/validate_research.py::check_search_result_manifests` prüft: referenzielle Existenz von
      `search_run_id`, gegenseitige Verknüpfung über `result_capture.manifest_id`, höchstens ein
      aktives Manifest je Suchlauf, keine verwaisten Manifeste, `count == len(identifiers)` UND
      `count == search_run.result_count`, `identifier_type` passend zur Datenbank des Suchlaufs
      (`pubmed` → `pmid`, `clinicaltrials_gov` → `nct_id`), kanonische Sortierreihenfolge (numerisch/
      lexikografisch — JSON Schema allein kann Sortierreihenfolge nicht ausdrücken), und den
      SHA-256-Hash gegen die verbindliche Hash-Regel. Identifikator-Pattern (`^[1-9][0-9]*$` für PMID,
      `^NCT[0-9]{8}$` für NCT-ID) und Eindeutigkeit (`uniqueItems`) sind bereits schema-seitig
      erzwungen.
    - `tools/check_research_immutability.py` erweitert um `research/search_results/**` als zweites,
      eigenständiges Ziel: dort ist JEDES Feld unveränderlich (kein `status`/`review` wie bei
      `research_search_run` — ein Manifest ist reine Tatsachenfeststellung, kein Workflow-Dokument).
      `request_parameters`/`result_capture` auf `research_search_run` sind implizit bereits durch die
      bestehende "alles außer status/updated_at/review/notes ist unveränderlich"-Logik abgedeckt.
    - Die vier bereits angelegten Phase-4B-1A-Suchläufe (PubMed retatrutide/LY3437943,
      ClinicalTrials.gov retatrutide/LY3437943) wurden auf `result_capture.status: complete` mit den
      vier neuen, aus den ursprünglich gespeicherten lokalen Rohantworten erzeugten Manifesten
      nachgerüstet — keine erneute Suche, keine neuen/späteren Treffer wurden eingemischt.
- **Alternativen:**
    1. *Nur die Trefferzahl dokumentieren (Status quo)* — verworfen: reicht für historische
       Reproduzierbarkeit nicht aus, siehe Kontext.
    2. *Vollständige Rohantworten (JSON-Exporte) versionieren* — verworfen: würde ggf. urheberrechtlich
       geschützte Metadaten/Abstracts mitversionieren und widerspricht der bestehenden
       `research/raw/`-Politik (Abschnitt 32 im Scientific Research Protocol); stabile Identifikatoren
       allein sind dagegen unproblematisch.
    3. *Identifikatorliste direkt als zusätzliches Feld auf `research_search_run` speichern, kein
       eigenes Objekt* — verworfen: vermischt das ausgeführte Suchereignis (Suchlauf) mit der
       tatsächlich erhaltenen Ergebnismenge (Manifest); ein eigenes, vollständig unveränderliches
       Objekt macht die Unterscheidung sowohl inhaltlich als auch technisch (getrennte
       Immutability-Policy) sauberer.
    4. *Separates Objekt mit gegenseitiger Referenz Suchlauf↔Manifest, optionalem `unavailable`-Pfad
       für nicht erfassbare Fälle* — **gewählt**.
- **Konsequenzen:** Ein historisches Result Set ist jetzt entweder über sein Manifest exakt
  rekonstruierbar, oder es ist dokumentiert, warum das nicht möglich war — kein stiller Datenverlust.
  Jeder zukünftige Suchlauf muss `result_capture` setzen; ein vollständiges Manifest ohne begründete
  Ausnahme ist damit der Normalfall. Test-Fixtures unter `tests/fixtures/research/**` (158 bestehende
  `search_run`-Dateien) wurden mechanisch um `request_parameters: {}` und
  `result_capture: {status: unavailable, ...}` ergänzt, da sie keine echten Suchläufe mit lokal
  vorliegendem Rohexport repräsentieren.
- **Migrationsstrategie:** Nicht zutreffend für Produktivdaten außerhalb der vier genannten
  Suchläufe (Phase 4B-1A ist der erste reale Rechercheschritt). Keine bestehenden bestätigten
  Suchläufe erforderten eine inhaltliche Korrektur — nur die Ergänzung der neuen Pflichtfelder.

**Nachtrag (R2, 2026-07-27) — Härtung, kein neuer ADR:** Die Korrekturrunde R2 identifizierte vier
weitere Lücken zwischen dem, was `request_parameters`/`result_capture` inhaltlich versprechen, und
dem, was tatsächlich maschinell geprüft wurde:

1. *Fehlender API-Parameter nachgetragen:* Die tatsächlich ausgeführten ClinicalTrials.gov-Anfragen
   enthielten `fields=NCTId` (eingrenzt die Antwort auf die NCT-ID), das aber in den ursprünglich in
   R1 dokumentierten `request_parameters` fehlte. Beide produktiven ClinicalTrials.gov-Suchläufe
   sowie alle Beispiele/Fixtures mit einem echten ClinicalTrials.gov-API-v2-Profil wurden um
   `fields: NCTId` ergänzt.
2. *API-Profil-Mindestvalidierung:* `request_parameters` war zuvor ein vollständig offenes Objekt
   (`additionalProperties: true`) ohne inhaltliche Prüfung — ein Suchlauf hätte z. B. `retmax: 1`
   bei `result_count: 157` eintragen können, ohne dass der Validator das bemerkt hätte. Neue Funktion
   `tools/validate_research.py::check_search_run_interface_profiles` erzwingt fuer die beiden
   tatsächlich verwendeten Profile (NCBI E-utilities ESearch, ClinicalTrials.gov API v2 —
   erkannt über `database` UND einen textuellen Hinweis in `interface`, NIE pauschal über
   `database` allein) vollständige, konsistente `request_parameters` sowie bei
   `result_capture.status: complete`: `retmax >= result_count` ohne dokumentierte Pagination (NCBI),
   bzw. verpflichtende `pagination` mit `completion_confirmed: true` und
   `pages_retrieved × pageSize >= result_count` (ClinicalTrials.gov).
3. *Zeitliche Provenienz Suchlauf→Manifest:* Bislang unabhängig von seinem Suchlauf. Neue Prüfung:
   das Datum von `executed_at` muss `<=` `manifest.created_at` sein — ein Manifest kann den
   Suchlauf, dessen Momentaufnahme es ist, nicht zeitlich vorwegnehmen.
4. *Exportreferenz-Konsistenz:* `search_run.export_reference` und `manifest.source_export_reference`
   konnten unabhängig voneinander beliebige Werte tragen (inkl. `export_reference: null` bei einem
   sonst vollständigen Suchlauf). Neue Prüfung: bei `result_capture.status: complete` müssen beide
   Felder exakt übereinstimmen.

Alle vier produktiven Suchläufe und Manifeste (Phase 4B-1A) erfüllten Punkt 3 und 4 bereits ohne
inhaltliche Korrektur (nur `fields: NCTId` war nachzutragen, Punkt 1). 15 Test-Fixtures aus R1 mit
`result_capture.status: complete`, aber `export_reference: null`, wurden auf die jeweils
übereinstimmende Exportreferenz ihres Manifests korrigiert (reine Testdaten-Konsistenz, keine
inhaltliche Regeländerung). Keine der vier Identifikatorlisten, Counts oder SHA-256-Werte wurde
verändert, keine Datenbanksuche wurde erneut ausgeführt.

**Nachtrag (R3, 2026-07-27) — maschinenlesbare Interface-Profile, kein neuer ADR:** R2 entschied
die anzuwendenden API-Profilregeln anhand von `database` UND einem Textfragment im frei
formulierten `interface`-Feld (z. B. „enthält 'E-utilities' und 'ESearch'"). Das ist strukturell
unsicher: `interface` ist per Definition eine menschenlesbare Beschreibung ohne Formatgarantie —
eine harmlos wirkende Umformulierung (Tippfehler-Korrektur, interne Umbenennung, Übersetzung)
hätte die Profilvalidierung unbemerkt stillgelegt, ohne dass sich an der tatsächlich verwendeten
Schnittstelle etwas geändert hätte.

**Entscheidung:** Neues kontrolliertes Vokabular `research/vocabularies/search_interface_profiles.yaml`
(`ncbi_eutils_esearch_v1`, `clinicaltrials_gov_api_v2_v1`, `unprofiled`) sowie neues Pflichtfeld
`interface_profile` auf `research_search_run`:

```yaml
interface_profile:
  id: ncbi_eutils_esearch_v1
  rationale: null
```

- `interface` bleibt unverändert die freie, menschenlesbare Bezeichnung — weiterhin anzeigbar und
  dokumentierend, aber ab sofort NICHT mehr die Quelle der Profilsemantik.
- `interface_profile.id` ist die alleinige, maschinenlesbare Quelle: `check_search_run_interface_profiles`
  dispatcht ausschließlich darüber. Die vormaligen Text-Dispatcher
  `_is_ncbi_eutils_esearch_interface`/`_is_clinicaltrials_gov_api_v2_interface` wurden entfernt.
  Zusätzlich neu: fuer die beiden bekannten Profile wird jetzt auch die passende `database` erzwungen
  (`ncbi_eutils_esearch_v1` → `pubmed`, `clinicaltrials_gov_api_v2_v1` → `clinicaltrials_gov`) — in R2
  war das nur implizit ueber die Text-Erkennung der Fall, nicht als eigene Regel geprueft.
  Die bereits in R2 eingefuehrten Parameter-/Pagination-Regeln je Profil bleiben inhaltlich unveraendert.
- Fuer bekannte Profile (`ncbi_eutils_esearch_v1`, `clinicaltrials_gov_api_v2_v1`) ist `rationale`
  schema-seitig auf `null` beschraenkt. Fuer `id: unprofiled` ist `rationale` schema-seitig als
  nicht-leerer String erzwungen -- ein transparenter, begruendeter Fallback fuer Suchlaeufe gegen
  Interfaces, fuer die noch keine maschinelle Profilvalidierung implementiert ist, kein stiller
  Verzicht auf Profilierung.
- Die Versionsnummer ist bewusst Teil des Profilnamens selbst (`_v1`): eine kuenftige Aenderung an
  den Profilregeln fuehrt ein NEUES Profil (`_v2` usw.) ein, statt bereits ausgefuehrte historische
  Search Runs rueckwirkend unter geaenderten Regeln umzudeuten.
- `interface_profile` ist ein Ausfuehrungsfeld und damit unveraenderlich nach dem Merge (bereits
  strukturell durch die bestehende `check_research_immutability.py`-Logik abgedeckt, jetzt zusaetzlich
  durch einen expliziten Test abgesichert): eine nachtraegliche Aenderung wuerde einen bereits
  ausgefuehrten Suchlauf rueckwirkend einem anderen, ggf. erst spaeter eingefuehrten Profil unterwerfen.
- Alle vier produktiven Suchläufe erhielten das jeweils zutreffende bekannte Profil
  (`ncbi_eutils_esearch_v1` für die beiden PubMed-Läufe, `clinicaltrials_gov_api_v2_v1` für die
  beiden ClinicalTrials.gov-Läufe), `rationale: null` — keine inhaltliche Änderung an Query,
  Zeitpunkt, Trefferzahl, Identifikatorliste oder Hash. Bestehende generische Test-Fixtures ohne
  echten Profilbezug erhielten mechanisch `id: unprofiled` mit einer klaren Testbegründung; echte
  Profil-Fixtures aus R2 erhielten das jeweils passende bekannte Profil.
- Zwei neue kritische Tests beweisen die eigentliche Motivation dieser Härtung: ein Suchlauf mit
  bekanntem Profil, absichtlich umformuliertem `interface`-Text UND einem ungültigen Parameter
  (`retmax` zu klein bzw. fehlendes `fields`) schlägt weiterhin fehl — die Umformulierung von
  `interface` kann die Profilvalidierung nicht mehr umgehen.

**Konsequenzen:** Die Profilzuordnung ist jetzt ein expliziter, versionierter, unveränderlicher
Datenpunkt statt einer aus Freitext abgeleiteten Heuristik. `interface` kann frei redigiert werden,
ohne die Validierung zu beeinflussen. Keine der vier Identifikatorlisten, Counts, SHA-256-Werte,
Queries, Ausführungszeitpunkte oder Exportreferenzen wurde verändert; keine Datenbanksuche wurde
erneut ausgeführt.

### ADR-0056: `research_candidate_manifest` als technische Discovery-Bruecke zwischen Search Result Manifest und Screening Record
- **Status:** Entschieden
- **Datum:** 2026-07-27
- **Kontext:** Phase 4B-1B-0 (Retatrutide-Screening-Preflight) benoetigte eine reproduzierbare, validierbare
  Bruecke zwischen den vier Phase-4B-1A-Suchlaeufen/-Search-Result-Manifesten und den zukuenftigen
  `research_screening_record`-Dateien: welche Identifikatoren wurden entdeckt, aus welchen Suchlaeufen stammt
  jeder Identifikator, welche Datenbank hat ihn geliefert, wurde jeder Manifest-Identifikator genau einem
  protokollspezifischen Kandidaten zugeordnet, und ist noch keine wissenschaftliche Screening-Entscheidung
  getroffen worden? Ein globales kanonisches Candidate-Objekt unter `data/**` waere verfrueht gewesen (echte
  Screening-Entscheidungen fehlen noch); 197 einzelne Kandidatendateien (162 PMID + 35 NCT-ID) waeren
  unpraktikabel gewesen und haetten die Herkunfts-/Vereinigungslogik nicht als ein zusammenhaengendes,
  pruefbares Objekt abgebildet.
- **Entscheidung:** Neue, ausschliesslich technisch-bibliographische Objektart `research_candidate_manifest`
  (Schema `schemas/research_candidate_manifest.schema.json`, Ordner `research/candidates/`, ID-Muster
  `candidate-manifest-<uuid4>`) — ein Manifest je Protokoll **und** Datenbank (nicht je Kandidat), das die
  normalisierte Vereinigungsmenge mehrerer Search Result Manifests derselben Datenbank/desselben Protokolls
  buendelt. Jeder Kandidat traegt eine stabile `candidate_id` (`research-candidate-<uuid4>`), ein strukturiertes
  `primary_identifier` (`namespace: pmid|nct_id` + `value`, nie freier String), die vollstaendige
  `discovered_in_search_run_ids`-Herkunft (nicht auf einen "primaeren" Suchlauf reduzierbar) sowie sparsame,
  datenbankspezifische Metadatenfelder (siehe `#/$defs/pubmed_metadata`/`#/$defs/clinicaltrials_gov_metadata`)
  mit einem rein technischen `metadata_status` (neues Vokabular
  `research/vocabularies/candidate_metadata_statuses.yaml`: `not_fetched`/`fetched`/`partial`/`not_found`/
  `fetch_error` — bewusst ohne wissenschaftliche Begriffe wie `relevant`/`included`/`excluded`) und
  nachvollziehbarer `metadata_provenance` (Interface, Zeitpunkt, technische Anfragereferenz, niemals geheime
  Tokens oder vollstaendige API-URLs). `identifier_namespace` referenziert bewusst das bereits bestehende
  `common.schema.json#/$defs/search_result_identifier_type` (kein neues, redundantes
  `identifier_namespaces.yaml`-Vokabular, da dieselbe Werte-Menge `pmid`/`nct_id` bereits fuer
  `research_search_result_manifest.identifier_type` gilt und schema-seitig ohne eigene YAML-Vokabulardatei
  auskommt).

  `tools/validate_research.py::check_candidate_manifests` erzwingt referenzielle Existenz (Protokoll,
  Suchlaeufe, Search Result Manifests, jeweils gleiches Protokoll), Datenbank-/Namespace-Konsistenz, die
  bijektive Abdeckung (jeder Manifest-Identifikator kommt genau einmal vor, kein zusaetzlicher unentdeckter
  Identifikator), projektweite Eindeutigkeit von `candidate_id`, protokoll-/namespace-weite Eindeutigkeit von
  `primary_identifier`, vollstaendige und korrekte `discovered_in_search_run_ids` (weder zu wenig noch zu
  viele Suchlaeufe), zeitliche Provenienz (`created_at <= metadata_provenance.retrieved_at <= updated_at`) und
  die je Datenbank definierten Pflichtmetadaten bei `metadata_status: fetched`. `tools/check_research_immutability.py`
  erhaelt ein drittes `ImmutableTarget` mit einer eigenen, verschachtelten Vergleichsfunktion (anders als der
  flache Feldvergleich fuer Suchlaeufe/Manifeste): Discovery-Identitaet (Top-Level-Felder ausser `updated_at`,
  sowie `candidate_id`/`primary_identifier`/`discovered_in_search_run_ids` je Kandidat) ist unveraenderlich und
  darf nicht entfernt werden; Metadatenfelder je Kandidat sowie `updated_at` bleiben mutable.

  Deterministisches Importwerkzeug `tools/build_research_candidates.py` mit zwei getrennten Modi:
  `--from-manifests` (offline, baut/aktualisiert Candidate Manifests aus den Search Result Manifests, erhaelt
  bestehende `candidate_id`/Metadaten) und `--refresh-metadata` (online, ruft Metadaten ueber NCBI ESummary
  bzw. ClinicalTrials.gov API v2 ab; ein Netzwerkfehler setzt nur `metadata_status: fetch_error`, verliert aber
  nie die Discovery-Identitaet). Beide Modi erzeugen niemals einen `screening_record` und setzen niemals eine
  Entscheidung.

  Migrationsstrategie fuer `research_screening_record`: zwei neue, **optionale** Felder
  `candidate_manifest_id`/`candidate_id` (schema-seitig entweder beide gesetzt oder beide `null`, referenziell
  gegen das Manifest geprueft inkl. Identifikator-Konsistenz) — `schema_version` bleibt bei `1.0.0` (keine
  Schema-Versionsbump noetig, da additiv-optional). Bestehende Fixtures/Beispiele unter `research/examples/**`
  bleiben unveraendert gueltig. Eine neue, explizite Protokoll-Allowlist
  `CANDIDATE_REFERENCE_REQUIRED_PROTOCOLS` (aktuell nur `research-protocol-retatrutide-v1`) macht die Referenz
  fuer neue, nicht unter `research/examples/**` liegende Screening Records dieser Protokolle verpflichtend —
  greift in Phase 4B-1B-0 selbst noch nicht (keine realen Screening Records in diesem PR), erst im
  Folge-PR Phase 4B-1B-1.

  Die zwei realen Candidate Manifests fuer Retatrutid (162 PubMed-Kandidaten, 35 ClinicalTrials.gov-Kandidaten
  — Vereinigung der vier Phase-4B-1A-Suchlaeufe/-Manifeste, siehe ADR-0055) wurden aus den bereits
  versionierten Search Result Manifests erzeugt, ohne einen einzigen Kandidaten wegen Publikationstyp, Titel
  oder vermuteter Relevanz vorab auszuschliessen.

- **Konsequenzen:** `research/**` erhaelt eine sechste Objektart, `RESEARCH_KINDS`/`RESEARCH_KIND_TO_FOLDER`/
  `RESEARCH_KIND_TO_SCHEMA_ID`/`RESEARCH_KIND_TO_ID_PREFIX`/`RESEARCH_VOCABULARY_NAMES` in `tools/_researchlib.py`
  wachsen entsprechend. `data/**`, `build/catalog.json` und `build/graph.json` bleiben unveraendert (0 Objekte/
  Knoten/Kanten) — ein Candidate Manifest ist Provenienz-/Arbeitsebene, kein kanonisches Wissen (ADR-0033
  gilt unveraendert). Kein Kandidat in den beiden erzeugten Manifesten stellt eine wissenschaftliche
  Screening-Entscheidung, eine kanonische Quelle, eine Studie oder einen Claim dar. Verworfen wurde: ein
  globales `data/**`-Candidate-Objekt (verfrueht vor echten Screening-Entscheidungen), 197 einzelne
  Kandidatendateien (unpraktikabel, verliert die Vereinigungs-/Herkunftslogik als ein Objekt), sowie ein
  eigenes `identifier_namespaces.yaml`-Vokabular (redundant zum bereits bestehenden
  `search_result_identifier_type`-Enum).

**Nachtrag (CSO-Review, 2026-07-27) — datengetriebene Referenzpflicht statt Protokoll-Allowlist, kein neuer
ADR:** die urspruengliche Migrationsstrategie (`CANDIDATE_REFERENCE_REQUIRED_PROTOCOLS`, eine hartkodierte
Menge von Protokoll-IDs, fuer die `candidate_manifest_id`/`candidate_id` bei neuen Screening Records
verpflichtend war) haette bei jedem neuen Protokoll mit einem Candidate Manifest eine manuelle
Code-Aenderung erfordert und war damit nicht selbsterklaerend an den tatsaechlichen Datenzustand gekoppelt.

**Entscheidung:** Die Pflicht ist jetzt **datengetrieben**: `check_screening_candidate_references` bildet die
Menge aller `protocol_id`-Werte, fuer die mindestens ein `research_candidate_manifest` existiert, und
erzwingt die Referenz fuer jeden neuen (nicht unter `research/examples/**` liegenden) Screening Record eines
Protokolls in dieser Menge. Existiert (noch) kein Candidate Manifest fuer ein Protokoll, bleibt dessen
Screening Records weiterhin migrationskompatibel (keine Pflicht) — die Konstante
`CANDIDATE_REFERENCE_REQUIRED_PROTOCOLS` entfaellt ersatzlos. `research/examples/**` bleibt davon
unabhaengig immer ausgenommen.

Zusaetzlich verschaerft: liegt eine aufgeloeste Kandidatenreferenz vor (Manifest und Kandidat existieren),
muss der zum `primary_identifier.namespace` des Kandidaten passende externe Identifikator
(`candidate_identifiers.pmid` fuer `pmid`, `.nct_id` fuer `nct_id`) im Screening Record gesetzt sein.
Zuvor wurde ein fehlender (`null`) Identifikator stillschweigend akzeptiert -- nur ein tatsaechlich
abweichender Wert wurde als Konflikt gemeldet. Jetzt erzeugen ein fehlender und ein abweichender
Identifikator zwei strukturell getrennte Validierungsfehler (unterschiedliche Meldungstexte, beide am
selben JSON-Pfad `$.candidate_identifiers.<namespace>`), damit ein Screening Record mit Kandidatenreferenz
den referenzierten externen Identifikator nicht mehr unbemerkt aussparen kann.

**Konsequenzen:** `schemas/research_screening_record.schema.json` (Feldbeschreibung),
`docs/project/Scientific_Research_Protocol.md` (Abschnitt 7b) und `research/candidates/README.md` wurden
entsprechend aktualisiert. Bestehende Fixtures/Beispiele unter `research/examples/**` bleiben unveraendert
gueltig. Die beiden bereits erzeugten realen Retatrutide-Candidate-Manifests (162 PubMed + 35
ClinicalTrials.gov) sind von dieser Aenderung inhaltlich nicht betroffen -- es existieren weiterhin keine
realen Screening Records (Phase 4B-1B-1 bleibt ein separater Folge-PR).

### ADR-0057: Automatische, rein administrative Screening-Initialisierung (`tools/initialize_screening_records.py`)
- **Status:** Entschieden
- **Datum:** 2026-07-27
- **Kontext:** Phase 4B-1B-1 sollte fuer alle 197 Retatrutide-Candidate-Manifest-Eintraege (162 PubMed +
  35 ClinicalTrials.gov) genau einen realen `research_screening_record` erzeugen, OHNE eine
  wissenschaftliche Bewertung durchzufuehren -- der Arbeitsauftrag verlangte einen deterministischen,
  netzwerkfreien, idempotenten Initialisierer, der jeden Datensatz im Zustand `decision: pending`
  belaesst.
- **Entscheidung:** Neues Werkzeug `tools/initialize_screening_records.py` erzeugt genau einen
  Screening Record je Kandidat (`candidate_manifest_id`/`candidate_id`, `search_run_ids` exakt aus
  `discovered_in_search_run_ids` uebernommen, `candidate_title` deterministisch aus den
  Candidate-Manifest-Metadaten abgeleitet -- nie erfunden, siehe `tools/_researchlib.py::
  derive_candidate_title`), zugeschrieben dem neuen technischen Akteur
  `system-screening-initializer` (`tools/_researchlib.py::SYSTEM_SCREENING_INITIALIZER_ACTOR`).
  `candidate_source_type` ist je Datenbank ein einzelner, neutraler, bereits im kontrollierten
  Vokabular vorhandener Wert (`CANDIDATE_SOURCE_TYPE_BY_DATABASE`: `pubmed` ->
  `peer_reviewed_publication`, `clinicaltrials_gov` -> `trial_registry`) -- bewusst keine feinere
  Ableitung aus PubMed `publication_types` (z. B. `Review` -> `systematic_review`), da das selbst
  schon eine wissenschaftliche Einordnung waere.

  Zwei Abweichungen vom woertlichen Arbeitsauftrag, beide durch das bereits vor dieser Phase
  etablierte Screening-Schema erzwungen:
  - `decision_stage: deduplication` statt des im Auftrag genannten `title_abstract`:
    `tools/_researchlib.py::ALLOWED_DECISIONS_BY_STAGE` erlaubt `pending` ausschliesslich an Stufe
    `deduplication`; `title_abstract` verlangt bereits eine inhaltliche Entscheidung. `deduplication`
    ist zudem der semantisch zutreffendere Ausgangszustand fuer "gerade entdeckt, noch nicht
    gesichtet".
  - `full_text_status: not_yet_obtained` statt des im Auftrag genannten `not_requested`: letzterer
    Wert existiert nicht im kontrollierten Vokabular (`research/vocabularies/full_text_statuses.yaml`);
    `not_yet_obtained` ("Noch nicht beschafft") ist die vorhandene, inhaltlich passende Entsprechung.

  Neue Validator-Pruefungen in `tools/validate_research.py`:
  - `check_screening_system_actor_invariants`: JEDER `decision_history`-Eintrag mit
    `decided_by: system-screening-initializer` muss `primary_decision: pending`/
    `stage: deduplication`/`full_text_status: not_yet_obtained` ohne Duplikatverweis/Zweitpruefung
    tragen -- der technische Akteur kann strukturell NIE `include`/`exclude`/`duplicate`
    dokumentieren. Solange er der aktuelle effektive Bearbeiter ist, muss `canonical_source_id`
    `null` bleiben und `candidate_title` exakt der abgeleitete Titel sein.
  - `check_screening_candidate_uniqueness`: hoechstens ein Screening Record je
    (`candidate_manifest_id`, `candidate_id`)-Paar.
  - `check_screening_candidate_references` erweitert: `search_run_ids` muss bei aufgeloester
    Kandidatenreferenz exakt (nicht nur teilweise) `discovered_in_search_run_ids` entsprechen.
  - `check_screening_initialization_completeness`: die Vollstaendigkeitsregel "jeder Candidate
    braucht einen Screening Record" greift ausschliesslich fuer Protokolle, die im neuen, rein
    technischen Kontrollartefakt `research/screening_status/initialization_manifest.yaml`
    (Schema `schemas/research_screening_initialization_manifest.schema.json`, KEIN eigener
    `RESEARCH_KINDS`-Eintrag, keine wissenschaftliche Aussage) als `status: complete` markiert sind
    -- ein teilweise durchgelaufener Import macht die CI dadurch nicht zwischenzeitlich rot. Wird
    von `tools/initialize_screening_records.py` selbst nach jedem Lauf aktualisiert
    (`status: complete` nur nach einem vollstaendig fehler- und konfliktfreien Durchlauf, sonst
    `status: in_progress`), inkl. Gegenpruefung von `expected_candidate_count` gegen den
    tatsaechlichen Datenbestand (verhindert eine stillschweigend veraltete `complete`-Markierung).

  **Nutzerentscheidung zur Deduplizierungs-Kollision echter Daten:** die Initialisierung der 197
  echten Retatrutide-Kandidaten deckte eine reale Identifikator-Kollision auf (drei PubMed-PMIDs mit
  derselben DOI `10.1056/NEJMc2310645` -- ein NEJM-Correspondence-Letter, offenbar doppelt
  indexiert, plus dessen separat indexierte Reply). Der bereits bestehende, mehrfach CSO-geprueft
  `check_deduplication` (Phase 4A) haette dafuer zwingend eine Duplikat-Entscheidung verlangt, die
  die rein technische Initialisierung laut Arbeitsauftrag nicht treffen darf. Nach expliziter
  Rueckfrage entschied der Nutzer: alle drei Kandidaten vollstaendig initialisieren (keine Daten
  verwerfen, PMID bleibt die massgebliche Identitaet, DOI bleibt als bibliographisches Metadatum
  erhalten), `check_deduplication` darf vor Abschluss der Deduplizierungsphase keine Fehler wegen
  gemeinsamer Identifikatoren erzeugen (nur eine Warnung), und erst nach menschlicher Uebernahme
  ALLER beteiligten Datensaetze wird eine ungeloeste Kollision zum Fehler. `check_deduplication`
  wurde entsprechend angepasst (siehe oben, gilt fuer alle `DEDUPLICATION_IDENTIFIER_FIELDS`, nicht
  nur DOI).
- **Konsequenzen:** 197 reale Screening Records fuer `research-protocol-retatrutide-v1` (162 PMID +
  35 NCT-ID) wurden erzeugt, alle `decision: pending`. `data/**`, `build/catalog.json` und
  `build/graph.json` bleiben unveraendert (0 Objekte/Knoten/Kanten) -- keine wissenschaftliche
  Entscheidung, keine Extraktion, keine Promotion. Drei Screening Records tragen weiterhin eine
  ungeloeste DOI-Kollisionswarnung, bis ein Mensch die bibliographische Frage (dieselbe Publikation
  vs. Letter+Reply mit gemeinsamer DOI) klaert. `docs/project/Scientific_Research_Protocol.md`
  (neuer Abschnitt 7c), `docs/project/Evidence_Curation_Workflow.md`,
  `research/screening/README.md`, `research/candidates/README.md` und `research/README.md` wurden
  entsprechend aktualisiert. Verworfen wurde: eine hartkodierte Retatrutide-Sonderregel fuer die
  Vollstaendigkeitspruefung (stattdessen das generische, protokollunabhaengige Kontrollartefakt);
  eine automatische Deduplizierungs-Entscheidung durch den Initialisierer (haette eine
  bibliographische Einschaetzung ohne ausreichende Grundlage erfordert).

### ADR-0058: Workflow-State-Modell, vollstaendige Deduplizierungsarchitektur und erweitertes Source-Type-Modell (Phase 4B-1B-2)
- **Status:** Vorgeschlagen (Architektur-Entwurf, keine Implementierung)
- **Datum:** 2026-07-27
- **Kontext:** Der CSO-Review von PR #6 (Phase 4B-1B-1) hat die ADR-0057-Loesung fuer die DOI-Kollision
  (drei PubMed-PMIDs mit gemeinsamer DOI `10.1056/NEJMc2310645`) explizit als provisorisch eingestuft und
  einen eigenstaendigen Architektur-Entwurf angefordert, bevor eine Implementierung erfolgt. Drei
  strukturelle Probleme der ADR-0057-Loesung: (1) `check_screening_system_actor_invariants` und
  `check_deduplication` leiten den Bearbeitungszustand eines Screening Records redundant aus
  `screened_by == system-screening-initializer` her -- eine Akteursidentitaet wird als Workflow-Zustand
  zweckentfremdet; (2) `decision: duplicate` kennt nur eine einzige Beziehungsart zwischen Kandidaten
  ("identisch, einer redundant"), obwohl der reale Kollisionsfall zeigt, dass geteilte Identifikatoren
  (insbesondere DOI bei Correspondence-Paaren) auch eigenstaendige, aber inhaltlich verwandte
  Publikationen verbinden koennen (Letter + Reply); (3) `candidate_source_type` (ein Wert je Datenbank)
  kann Letter/Reply/Editorial/Corrigendum/Retraction Notice nicht unterscheiden, obwohl PubMed dafuer
  bereits strukturierte Metadaten (`publication_types`) liefert.
- **Entscheidung (vorgeschlagen, siehe vollstaendigen Entwurf in
  [Phase_4B_1B_2_Deduplication_and_Workflow_Architecture.md](Phase_4B_1B_2_Deduplication_and_Workflow_Architecture.md)):**
  - Neues, additiv-optionales Feld `workflow_state` auf `research_screening_record`
    (`system_initialized`/`under_human_review`/`finalized`, kontrolliertes Vokabular
    `research/vocabularies/screening_workflow_states.yaml`) -- wie `decision`/`decision_stage` eine vom
    Validator geprueft Projektion von `decision_history[]`, keine zweite Wahrheitsquelle. Ersetzt die
    `screened_by`-basierte Herleitung in `check_screening_system_actor_invariants` und
    `check_deduplication`.
  - Neues, additiv-optionales Feld `related_records[]` auf `research_screening_record`
    (`screening_record_id`, `relationship_type`, Pflicht-Freitext `rationale`, `identified_by`,
    `identified_at`) fuer eigenstaendige, aber inhaltlich verwandte Publikationen -- strukturell getrennt
    von `duplicate_of`, das ausschliesslich fuer bibliographische Dubletten reserviert bleibt. Neues
    kontrolliertes Vokabular `research/vocabularies/screening_relationship_types.yaml`:
    `letter_and_reply`, `interim_and_final_results`, `subgroup_or_secondary_analysis`, `safety_update`,
    `preprint_and_published_version`, `registry_entry_and_publication`, `correction_or_erratum`,
    `expression_of_concern`, `retraction_notice`, `editorial_comment`, `other`. Referenziell und
    symmetrisch geprueft (neu: `check_screening_related_records`); `identified_by` darf nicht der
    technische Systemakteur sein. Eine Identifikator-Kollision, die vollstaendig durch `duplicate_of`
    und/oder eine symmetrische `related_records`-Beziehung erklaert ist, loest weder Fehler noch Warnung
    in `check_deduplication` aus.
  - `common.schema.json#/$defs/source_type` additiv um sieben Werte erweitert: `letter_or_comment`,
    `reply_or_response`, `editorial`, `case_report`, `corrigendum_or_erratum`, `retraction_notice`,
    `expression_of_concern_notice`. Fuer PubMed-Kandidaten technische (nicht wissenschaftliche)
    Ableitung aus dem bereits vorhandenen `metadata.publication_types` (von der NLM selbst vergeben,
    keine eigene Einordnung) moeglich -- explizit NICHT fuer `reply_or_response` (PubMed unterscheidet
    Letter und Reply strukturell nicht, das bleibt menschlicher `related_records`-Klassifikation
    vorbehalten).
  - Begriffliche Grundlage: Identifikator-Uebereinstimmung (insbesondere DOI) ist ein Signal fuer eine
    moegliche Beziehung, nie ein Beweis fuer eine bestimmte Beziehungsart -- PMID/PMCID sind praktisch
    1:1 mit einem Dokument, DOI ist es bei Correspondence-Paaren nachweislich nicht, NCT-ID ist 1:n mit
    Publikationen (eine Studie, mehrere Berichte). `related_records[]` ist die Recherche-Ebenen-Vorstufe
    der bereits bestehenden kanonischen Trennung `study.source_ids[]` (Abschnitt 13-16 im Scientific
    Research Protocol) -- keine kanonische Aussage, analog zu Candidate Manifest (ADR-0056) und
    Screening Record selbst.
- **Konsequenzen (bei Umsetzung):** alle Aenderungen additiv-optional, kein Schema-Versionsbump, keine
  Migration der 197 bestehenden Retatrutide-Records noetig. Keine Aenderung an bestehenden Daten oder
  Code in diesem ADR selbst -- reine Spezifikation. Offene Fragen (Richtungsabhaengigkeit von
  `related_records`, Notwendigkeit eines vierten Workflow-Zustands, Vollstaendigkeit der
  `source_type`-Erweiterung, Reihenfolge der Umsetzung) bleiben bis zur CSO-Freigabe unentschieden, siehe
  Abschnitt 9 des Entwurfsdokuments.

**Nachtrag (CSO-Review Runde 1, 2026-07-27) -- sechs verbindliche Aenderungen vor Umsetzung, Entwurf
Version 2, weiterhin Status "Vorgeschlagen":** die Grundarchitektur wurde freigegeben; sechs konkrete
Aenderungen wurden vor einem Merge verlangt und im Entwurfsdokument (jetzt v2) umgesetzt:

1. **`workflow_state` nicht als persistentes Schemafeld.** Ersetzt durch eine reine, nicht gespeicherte
   Helferfunktion `tools/_researchlib.py::derive_workflow_state()`, berechnet ausschliesslich aus
   `decision_history` sowie den bereits validierten Top-Level-Projektionen `decision`/`decision_stage`.
   Kein neues Vokabular, keine Migration, kein `check_screening_workflow_state_projection` mehr noetig
   (entfaellt ersatzlos gegenueber der ursprruenglichen v1-Fassung dieses ADRs).
2. **`related_records[]` referenziert Kandidaten statt Screening Records.** Statt
   `screening_record_id` tragen Eintraege `related_candidate_manifest_id`/`related_candidate_id` --
   candidate_id ist seit ADR-0056 technisch erzwungen unveraenderlich
   (`tools/check_research_immutability.py::CANDIDATE_ENTRY_IMMUTABLE_FIELDS`), waehrend fuer
   `research_screening_record.id` keine vergleichbare technische Garantie existiert. Zusaetzlich
   semantisch korrekter: die Beziehung ist eine Aussage ueber die zugrunde liegenden Dokumente, nicht
   ueber ihre Screening-Workflow-Huelle.
3. **Source-Type-Vokabular um zwoelf gepruefte Kandidaten erweitert:** `meta_analysis`,
   `practice_guideline` sicher automatisierbar (eigene PubMed-Publication-Type-Werte);
   `narrative_review` eingeschraenkt automatisierbar (Ausschlussregel); `consensus_statement`,
   `technical_report`, `dataset` mit unsicherem, vor Umsetzung technisch zu verifizierendem
   Automatisierungsstatus; `scoping_review`, `umbrella_review`, `living_systematic_review`,
   `white_paper`, `software`, `protocol_paper` ausschliesslich menschlich vergeben (kein
   entsprechendes PubMed-Publication-Type-Tag bzw. nur ueber vom Projekt bewusst vermiedene
   Freitexterkennung feststellbar).
4. **`relationship_type` auf gerichtete Beziehungspaare umgestellt** (z. B. `replies_to`/`has_reply`,
   `corrects`/`corrected_by`, `retracts`/`retracted_by`, `updates`/`updated_by` als generisches Paar
   fuer verwandte v1-Konzepte wie Zwischen-/Endergebnis und Sicherheits-Update, um die in v1 unter
   "Option B" befuerchtete Vokabular-Verdopplung zu vermeiden) -- 9 Konzeptpaare, 17 Werte insgesamt
   (16 gerichtete + `other_related_to` als einzige bewusst symmetrische Ausnahme). Neue
   Symmetriepruefung: Gegenrichtung muss den hinterlegten inversen Typ tragen, nicht denselben Typ.
5. **Identifier-Grundsatz verschaerft und um ISBN erweitert:** "Kein bibliographischer Identifier
   beweist allein eine wissenschaftliche Beziehung" gilt ausdruecklich fuer DOI, PMID, PMCID, NCT-ID
   UND ISBN (ISBN zuvor nicht Teil der Kardinalitaetstabelle) -- ISBN ist strukturell derselbe
   Unzuverlaessigkeitstyp wie DOI (mehrere ISBNs pro inhaltlich identischem Werk durch
   Auflagen-/Formatvarianten).
6. **Kollisionsgruppen werden als Zusammenhangskomponente statt paarweise geprueft.** Statt
   vollstaendiger paarweiser Klassifikation (quadratischer Aufwand bei groesseren Gruppen) bildet der
   Validator einen Graphen je Kollisionsgruppe (Kanten: `duplicate_of` und `related_records` zwischen
   Gruppenmitgliedern) und verlangt genau eine Zusammenhangskomponente -- Union-Find, nahezu lineare
   Laufzeit. Transitive Erklaerung wird dadurch korrekt anerkannt (Beispiel: PMID 37888925↔37888926
   per `duplicate_of`, 37888926↔37888927 per `replies_to`/`has_reply` -> alle drei bereits eine
   Komponente, ohne dass 37888925↔37888927 zusaetzlich direkt dokumentiert werden muesste).

Weiterhin unveraendert **keine Implementierung** in diesem Nachtrag -- reine Entwurfsrevision. Acht
neue bzw. fortbestehende offene Fragen fuer die naechste CSO-Runde, siehe Abschnitt 9 des
Entwurfsdokuments (u. a. Prioritaet bei gleichzeitigem `Meta-Analysis`+`Systematic Review`-Tag,
Verhaeltnis `practice_guideline` zu bestehendem `guideline`, Notwendigkeit von
`living_systematic_review`, technische Verifikation der drei unsicheren Source-Type-Werte).

**Nachtrag (CSO-Review Runde 2, 2026-07-27) -- eigenstaendiges Evidenz-Konzept fuer Beziehungen, Entwurf
Version 3, weiterhin Status "Vorgeschlagen":** die Architektur wurde als nahezu vollstaendig bestaetigt;
eine letzte Ergaenzung vor Merge-Freigabe verlangt:

- **Neues verschachteltes Feld `relationship_metadata`** auf jedem `related_records[]`-Eintrag, buendelt
  `identified_by`/`identified_at` (zuvor direkt am Eintrag, siehe Runde-1-Nachtrag) zusammen mit zwei
  neuen Pflichtfeldern: `evidence_source` (Array aus dem neuen kontrollierten Vokabular
  `research/vocabularies/screening_relationship_evidence_sources.yaml`: `title_similarity`, `doi`,
  `pmid`, `pmcid`, `nct_cross_reference`, `publication_types`, `author_list`,
  `manual_title_abstract_review`, `manual_full_text_review`, `other`) und `confidence` (Konzept
  dokumentiert, bewusst OHNE festgelegten Typ/Skala -- CSO-Vorgabe: "noch keine Skala implementieren";
  drei Optionen -- kategorial-ordinal, numerisch, Freitext -- als offene Frage festgehalten, vorlaeufige
  unverbindliche Tendenz zu kategorial-ordinal).
- **Ausdruecklich dokumentierte Trennung (siehe Entwurfsdokument Abschnitt 2.6.1):**
  `relationship_metadata` beschreibt AUSSCHLIESSLICH die Evidenz dafuer, DASS zwei Kandidaten in der
  dokumentierten Beziehung zueinander stehen (ein bibliographisch-struktureller Sachverhalt) -- NIEMALS
  die wissenschaftliche Evidenzstufe, methodische Qualitaet oder inhaltliche Verlaesslichkeit der
  beteiligten Studie(n)/Publikation(en) selbst. Fliesst nie automatisch in `Evidenzstufe`,
  `evidence_category` oder ein anderes Feld des kanonischen Evidenzmodells ein -- dieselbe
  Ebenentrennung wie zwischen `research/**` und `data/**` (ADR-0033), nur eine Ebene tiefer.
- `check_screening_related_records` prueft `relationship_metadata.identified_by != 
  system-screening-initializer` (Feldpfad angepasst, Regel unveraendert aus Runde 1).

Weiterhin **keine Implementierung**. Zwei neue offene Fragen (Vollstaendigkeit von `evidence_source`,
Skala fuer `confidence`) ergaenzen die acht aus Runde 1, siehe Abschnitt 9 des Entwurfsdokuments (v3).

### ADR-0059: Title & Abstract Screening Architektur -- Reviewer-Modell, Wiederaufnahme, Historienschutz (Phase 4B-1B-3)
- **Status:** Vorgeschlagen (Architektur-Entwurf, keine Implementierung)
- **Datum:** 2026-07-27
- **Kontext:** Nach Abschluss von Phase 4B-1B-1 (ADR-0057, reale Screening-Record-Initialisierung) und
  Phase 4B-1B-2 (ADR-0058, Deduplizierungsarchitektur) ist der naechste inhaltliche Schritt das reale
  Titel-/Abstract-Screening der 197 Retatrutide-Kandidaten. Der Arbeitsauftrag verlangte einen
  Architektur-Entwurf fuer zehn Themen, bevor irgendeine echte Screening-Entscheidung getroffen wird.
  Eine Bestandsaufnahme zeigt: der grosse Teil der angefragten Mechanik (Include-/Exclude-Vokabular,
  kontrollierte Exclude-Gruende, Erst-/Zweitpruefung, Adjudikation, vollstaendige `decision_history`-
  Versionierung, protokollskalierte Architektur) ist bereits seit Phase 4A (PR #2, ADR-0037/ADR-0042/
  ADR-0043/ADR-0046/ADR-0047/ADR-0052/ADR-0053) vollstaendig vorhanden -- echte Luecken bestehen nur bei
  drei Themen: einem strukturellen Akteurstyp (Mensch/KI/Automatisierung), einer semantischen Schicht
  fuer die Wiederaufnahme bereits ausgeschlossener Kandidaten, und einem technischen Schreibschutz fuer
  bereits committete `decision_history`-Eintraege.
- **Entscheidung (vorgeschlagen, siehe vollstaendigen Entwurf in
  [Phase_4B_1B_3_Title_Abstract_Screening_Architecture.md](Phase_4B_1B_3_Title_Abstract_Screening_Architecture.md)):**
  - **Reviewer-Modell:** neue, optionale Objektart `research_reviewer` (`research/reviewers/`,
    `actor_type: human|automation|ai_assistant|service`) -- greift die in ADR-0041 explizit als
    "spaeter vorgemerkt" zurueckgestellte Actor-Registry-Idee wieder auf, jetzt mit echtem
    Anwendungsfall. Bewusst nicht-invasiv: kein bestehendes `research_actor_id`-Feld aendert Typ oder
    Struktur, Registrierung ist nur fuer `ai_assistant`/`automation`-Akteure verpflichtend, fuer
    `human` optional (dieselbe organisatorische Grenze wie ADR-0041). Neue Regel: jede Erstentscheidung
    eines nicht-menschlichen Akteurs erfordert ein Zweitreview, unabhaengig von
    `screening_policy.dual_reviewer_stages` -- Erweiterung, nicht Ersatz des bestehenden Mechanismus.
    Adjudikation bleibt ausschliesslich menschlichen Akteuren vorbehalten (hart, nicht
    protokollkonfigurierbar).
  - **Wiederaufnahme:** neues optionales Feld `decision_history[].revision_context`
    (`reason`/`reference`/`triggered_by`, neues Vokabular `screening_revision_reasons.yaml`: 
    `protocol_amendment`/`new_evidence`/`reviewer_error_correction`/`periodic_reevaluation`/`other`),
    Pflicht genau dann, wenn ein neuer Eintrag eine vorherige Entscheidung umkehrt statt sie nur um
    eine neue Stufe zu ergaenzen. Macht die bereits bestehende Verbindung zu Protokolländerungen
    (Abschnitt 31 im Scientific Research Protocol) erstmals maschinenlesbar.
  - **Historienschutz:** viertes `ImmutableTarget` in `tools/check_research_immutability.py` fuer
    `research/screening/**` -- schuetzt ausschliesslich bereits committete `decision_history[]`-
    Eintraege vor rueckwirkender Aenderung (nur Anhaengen erlaubt); alle uebrigen Felder bleiben nach
    den bereits in Phase 4B-1B-1/-2 festgelegten Regeln veraenderlich.
  - **Alle uebrigen sieben angefragten Themen** (Include-/Exclude-Entscheidungen, kontrollierte
    Exclude-Gruende, Konfliktaufloesung, Dokumentation/Versionierung, Trennung technisch/
    wissenschaftlich, Mehrsubstanz-Faehigkeit, Skalierung) sind bereits durch bestehende Mechanik
    abgedeckt und werden im Entwurfsdokument nur explizit auf diese Phase angewendet und dokumentiert,
    nicht neu gebaut -- Skalierung auf zehntausende Records erhaelt zwei Empfehlungen (flaches
    Dateilayout beibehalten, Validator-Laufzeit-Beobachtungsschwelle ~5 Minuten) statt einer
    verfruehten Optimierung.
- **Konsequenzen (bei Umsetzung):** alle Aenderungen additiv-optional, kein Schema-Versionsbump, keine
  Migration der 197 bestehenden Records noetig. Keine Aenderung an bestehenden Daten oder Code in
  diesem ADR selbst -- reine Spezifikation. Neun offene Fragen fuer die naechste CSO-Runde, siehe
  Abschnitt 13 des Entwurfsdokuments (u. a. Registry-Option A vs. B, Vollstaendigkeit der
  Wiederaufnahme-Gruende, Notwendigkeit eines protokollweiten KI-Screening-Opt-in-Felds).

**Nachtrag (CSO-Review, 2026-07-28) -- vollstaendige Freigabe der Architektur, Entwurf Version 2,
weiterhin Status "Vorgeschlagen" (keine Implementierung in diesem Merge):** der CSO hat die Architektur
vollstaendig freigegeben und alle neun offenen Fragen aus Abschnitt 13 des Entwurfsdokuments (v1)
entschieden. Version 2 des Entwurfsdokuments setzt sie um:

1. **Actor-Registry: Option A** (leichtgewichtige neue Objektart `research_reviewer`) -- Option B
   entfaellt.
2. **`actor_type` langfristig um zwei weitere Werte reserviert, nicht implementiert:**
   `external_expert` (externe fachliche Gutachter) und `editorial_board` (institutioneller Akteur) --
   ausdruecklich eine Zukunftsperspektive, nicht Teil des aktuellen Schema-Entwurfs (weiterhin nur
   `human`/`ai_assistant`/`automation`/`service`).
3. **Registrierungspflicht erweitert:** verpflichtend fuer `ai_assistant`, `automation`, `service`
   sowie -- sobald eingefuehrt -- `external_expert`/`editorial_board`; `human` bleibt optional.
4. **Kein `screening_policy.ai_screening_enabled`-Opt-in-Feld** -- die automatische
   Zweitreview-Pflicht bei nicht-menschlicher Erstentscheidung bleibt alleinige Absicherung.
5. **Adjudikation bleibt zwingend menschlich, hart, nicht protokollkonfigurierbar** -- bestaetigt.
6. **`revision_context.reason` um drei Werte erweitert:** `external_peer_review`, `quality_control`,
   `data_correction` (jetzt 8 Werte insgesamt im neuen Vokabular
   `screening_revision_reasons.yaml`).
7. **`language_not_supported` wird nicht als Exclude-Grund ergaenzt** -- `other` bleibt ausreichend.
8. **Validator-Beobachtungsschwellenwert (~5 Minuten) beibehalten** -- keine inkrementelle
   Validierungsstrategie von Anfang an.
9. **Freigabe zur Implementierung erteilt** -- in einer eigenstaendigen, kuenftigen
   Phase-4B-1B-3-Implementierungs-PR; dieser Merge selbst enthaelt weiterhin keine Implementierung.

Zusaetzlich, ausserhalb der urspruenglichen neun Fragen, verlangte der CSO eine dokumentierte
**Zukunftsperspektive**: die Objektart `research_reviewer` ist nicht auf Titel-/Abstract-Screening
beschraenkt, sondern als universelles wissenschaftliches Reviewer-Modell konzipiert und perspektivisch
auch fuer Promotion Review, Evidence Review, Editorial Review und Quality Audit vorgesehen (Abschnitt 1.8
des Entwurfsdokuments) -- ebenfalls ohne Implementierung, ohne zusaetzliche Felder, ohne Schemaaenderung.

**Weiterhin keine Implementierung in diesem Nachtrag oder dem zugehoerigen Merge** -- reine
Entwurfsrevision und Dokumentation der CSO-Entscheidungen. Eine Frage bleibt fuer die kuenftige
Implementierungsphase offen (keine CSO-Vorgabe in dieser Runde): ob `revision_context.triggered_by`
zwingend ein `human`-Akteur sein muss.

**Nachtrag (Implementierung, Phase 4B-1B-3) -- die in diesem ADR und seinen beiden vorherigen
Nachtraegen freigegebene Architektur ist jetzt real implementiert (Schema, Validator, echte
Reviewer-Registrierungen, Tests, Dokumentation). Fuer die tatsaechlich umgesetzten Teile ist dieses
ADR damit inhaltlich "Entschieden" -- der urspruengliche Status-Text oben bleibt unveraendert
(append-only-Konvention), diese Einordnung steht bewusst nur hier:**

- **`research_reviewer`** (`schemas/research_reviewer.schema.json`, `research/reviewers/`) wie in
  Option A entworfen: `id` = das bereits verwendete `research_actor_id`-Kuerzel selbst,
  `actor_type` mit genau den vier freigegebenen Werten (`human`/`ai_assistant`/`automation`/
  `service`) -- `external_expert`/`editorial_board` bewusst NICHT im Enum, nur als Kommentar im
  Schema und in `research/reviewers/README.md` als langfristig reserviert dokumentiert.
- **Zwei reale Registrierungen angelegt**, nach tatsaechlicher Bestandsaufnahme aller in
  `research/**` verwendeten Akteurskuerzel (keine erfunden): `system-screening-initializer`
  (`automation`) und `cso-chatgpt` (`ai_assistant`). Ein dritter, real vorgefundener Kuerzel,
  `claude-code-operator` (`research_search_run.executed_by`, 4 Suchlaeufe aus Phase 4B-1A), wurde
  bewusst NICHT registriert -- sein `actor_type` ist nirgends im Projekt dokumentiert, und
  `executed_by` liegt ohnehin ausserhalb des Geltungsbereichs der neuen Regeln (die sich auf
  Screening-Entscheidungsakteure beschraenken: `decided_by`/`reviewed_by`/`resolved_by`/
  `triggered_by`).
- **`tools/validate_research.py::check_research_reviewers`**: Pflichtregistrierung nur fuer die
  beiden oben genannten, real bekannten Akteure -- und nur, wenn ein konkreter Datensatz sie
  tatsaechlich verwendet (datengetrieben, nicht pauschal fuer jedes `research/**`-Verzeichnis,
  sonst waeren z. B. unabhaengige Testfixtures faelschlich betroffen gewesen).
- **Zweitreview-/Adjudikations-/`revision_context.triggered_by`-Regeln** wie freigegeben in
  `_check_decision_snapshot`/`check_decision_history` umgesetzt. Ein **unregistriertes** Kuerzel
  wird fuer alle drei Regeln wie `human` behandelt (dieselbe Grenze wie die fuer `human` optionale
  Registrierung) -- damit ist die oben offen gelassene Frage ("muss `triggered_by` zwingend
  `human` sein?") in der Implementierung so beantwortet: **ja, aber nur wenn registriert**,
  identisch zur bereits freigegebenen Adjudikator-Regel. Keine gesonderte CSO-Vorgabe hierzu
  eingeholt -- als Implementierungsdetail dokumentiert, nicht als neue Grundsatzentscheidung.
- **"Reversal"-Definition praezisiert:** ein `decision_history[]`-Eintrag kehrt eine vorherige
  Entscheidung nur um, wenn die vorangegangene EFFEKTIVE Entscheidung an derselben Stufe bereits
  **settled** war (nicht `pending`/`uncertain`) und die neue `primary_decision` davon abweicht. Ein
  Uebergang von `uncertain` zu einer konkreten Entscheidung (z. B. der bereits bestehende
  Zielkonflikt-Mechanismus aus ADR-0052/ADR-0053) ist damit ausdruecklich KEINE Umkehrung, sondern
  die erste tatsaechliche Entscheidung -- ohne diese Praezisierung haette die Regel einen bereits
  bestehenden, laengst freigegebenen Mechanismus faelschlich mit einer neuen `revision_context`-
  Pflicht belegt.
- **`revision_context` als echtes optionales Feld** (nicht required-aber-nullable wie
  `decision_reason`) im Schema umgesetzt -- dadurch war **keine Migration** der 197 bestehenden
  Retatrutide-Screening-Records noetig, obwohl das Feld neu eingefuehrt wurde.
- **Viertes `ImmutableTarget`** (`research/screening`) in `tools/check_research_immutability.py`:
  ausschliesslich bereits committete `decision_history[]`-Eintraege sind geschuetzt (Anhaengen
  erlaubt, Aendern/Entfernen/Umsortieren nicht); alle uebrigen Screening-Felder bleiben unveraendert
  frei kontrolliert veraenderlich, wie im urspruenglichen Entwurf verlangt.
- 21 neue Tests (positiv und negativ) fuer alle oben genannten Regeln, zusaetzlich zu den
  bestehenden 410 -- keine Aenderung an den bestehenden 197 realen Retatrutide-Screening-Records,
  keine Aenderung unter `data/**`, keine Extraction-/Promotion-Records, keine echten
  Include-/Exclude-Entscheidungen. Dokumentation aktualisiert: `research/README.md`,
  `research/screening/README.md`, `research/reviewers/README.md` (neu),
  `docs/project/Scientific_Research_Protocol.md` (neuer Abschnitt 9e, Ergaenzungen 9a/34),
  `docs/project/Evidence_Curation_Workflow.md`, `docs/project/Data_Model.md`.
- Das eigentliche Titel-/Abstract-Screening der 197 Retatrutide-Kandidaten (echte
  Include-/Exclude-Entscheidungen) bleibt weiterhin eine eigene, kuenftige Phase -- nicht
  Bestandteil dieser Implementierung.

## Format für neue Einträge

```markdown
### ADR-00XX: <Titel>
- **Status:** Entschieden | Vorgeschlagen | Verworfen
- **Datum:** YYYY-MM-DD
- **Kontext:** Was war die Ausgangslage/das Problem?
- **Entscheidung:** Was wurde entschieden?
- **Konsequenzen:** Was folgt daraus, welche Alternativen wurden verworfen und warum?
```

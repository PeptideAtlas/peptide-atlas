# data/ — Anleitung fuer die wissenschaftliche Redaktion

Dieser Ordner enthaelt die strukturierten, maschinenlesbaren Daten von Peptide Atlas: Entitaeten (Substanzen,
Rezeptoren, Signalwege, Erkrankungen, Nebenwirkungen, Organisationen, Studien), Quellen und Claims. Diese Seite
richtet sich an wissenschaftliche Redakteur:innen, nicht nur an Entwickler:innen. Der technische Hintergrund
steht in [docs/project/Phase_3_Scientific_Data_Architecture.md](../docs/project/Phase_3_Scientific_Data_Architecture.md).

## Grundregel

Fakten (Substanznamen, Studien, Quellen, wissenschaftliche Aussagen/Claims) gehoeren hierher, nach `data/`. Die
verstaendliche Erklaerung, Einordnung und Diskussion gehoert nach `docs/` als Markdown-Artikel. Ein Artikel
verweist auf ein Objekt (`entity_id`) und auf Claims (`claim_ids`) — er dupliziert deren Inhalt nicht.

## Wo lege ich ein neues Objekt an?

| Ich moechte ... | ... dann lege ich eine Datei an unter |
|---|---|
| eine neue Substanz (Peptid, Protein, Hormon, Wirkstoff ...) | `data/entities/substances/<id>.yaml` |
| einen neuen Rezeptor | `data/entities/receptors/<id>.yaml` |
| einen neuen Signalweg | `data/entities/pathways/<id>.yaml` |
| eine neue Erkrankung/einen Zustand | `data/entities/conditions/<id>.yaml` |
| eine neue Nebenwirkung | `data/entities/adverse_events/<id>.yaml` |
| eine neue Organisation (Hersteller, Sponsor, Institut, Behoerde) | `data/entities/organizations/<id>.yaml` |
| eine neue Studie | `data/entities/studies/<id>.yaml` |
| eine neue Quelle | `data/sources/<id>.yaml` |
| einen neuen Claim (wissenschaftliche Aussage) | `data/claims/<id>.yaml` |

Der **Dateiname muss exakt mit dem Feld `id` in der Datei uebereinstimmen** (ohne `.yaml`). Kopiere am besten ein
bestehendes Beispiel aus `data/examples/` als Ausgangspunkt.

## Wie erstelle ich eine ID?

IDs sind stabil, ASCII-lowercase-kebab-case und werden nie geaendert oder wiederverwendet. Erzeuge sie nicht von
Hand, sondern mit dem Hilfsskript:

```bash
python tools/new_id.py entity substance "Placeholder Substance"
# -> substance-placeholder-substance

python tools/new_id.py claim
# -> claim-<zufaellige-uuid>

python tools/new_id.py source --pmid 12345678
# -> source-pmid-12345678
python tools/new_id.py source --nct NCT00000000
# -> source-nct-nct00000000
python tools/new_id.py source --doi 10.1000/beispiel.doi
# -> source-doi-10-1000-beispiel-doi
python tools/new_id.py source
# -> source-<uuid>, falls keine stabile externe Kennung vorhanden ist
```

## Wie lege ich eine Quelle an?

Jede Quelle ist eine eigene Datei unter `data/sources/`, unabhaengig davon, welche Studien oder Claims sie
belegt. Bevor du eine neue Quelle anlegst, pruefe, ob sie nicht schon existiert (z. B. per PMID/DOI-Suche in
`data/sources/`). Wichtige Felder:

- `source_type`: Art der Quelle, siehe `data/vocabularies/source_types.yaml`. **Haendlerseiten**
  (`merchant_page`) und **persoenliche Berichte** (`personal_report`) sind zulaessig, muessen aber klar so
  gekennzeichnet werden — sie duerfen nie der einzige Beleg fuer eine aktive Wirksamkeitsaussage sein (siehe
  unten).
- `retraction_status`: `not_retracted`, solange nichts anderes bekannt ist. Wird eine Quelle spaeter
  zurueckgezogen, aktualisiere dieses Feld — der Validator warnt oder blockiert dann automatisch aktive Claims,
  die ausschliesslich auf dieser Quelle beruhen.

## Wie lege ich einen Claim an?

Ein Claim ist eine einzelne, pruefbare Aussage — nicht ein ganzer Artikelabschnitt. Beispiel: „Substanz X bindet
an Rezeptor Y" ist ein Claim; „Substanz X: Uebersicht" ist ein Artikel mit mehreren Claims.

1. `subject_id`: die ID der Substanz/Entitaet, um die es geht.
2. `predicate`: **nur** ein Wert aus `data/vocabularies/predicates.yaml` (z. B. `binds_to`, `studied_for`,
   `approved_for`). Fehlt dir ein passendes Praedikat, ergaenze es dort — erfinde keins direkt im Claim.
3. `object`: entweder eine andere Entitaet (`entity_id: receptor-...`), ein Zahlenwert (`value`, `unit`,
   `value_type: number`) oder ein mehrsprachiger Text (`value: {de: ...}`, `value_type: localized_text`).
   Verwende **genau eine** dieser drei Varianten.
4. `evidence_category`: die Art der Evidenz (siehe
   [Evidenzsystem](../docs/00_grundlagen/evidenzsystem.md)) — **nicht** dasselbe wie `certainty`.
5. `certainty`: wie sicher/vertrauenswuerdig die Aussage insgesamt ist, mit `certainty_rationale` als kurzer
   Begruendung (ausser bei `not_assessed`).
6. `evidence[]`: die Quellen, die diesen Claim stuetzen, relativieren oder nur Kontext liefern
   (`direction: supports/contradicts/mixed/context_only`).

### Haendlerangaben und persoenliche Erfahrung

Verwende `evidence_category: merchant_claim`, wenn eine Aussage ausschliesslich auf einer Haendler-/
Herstellerangabe beruht, und `evidence_category: personal_experience` fuer Einzelberichte/Erfahrungsberichte
ausserhalb systematischer Datenerhebung. Beide sind zulaessige, ehrliche Kennzeichnungen — sie duerfen aber
niemals der alleinige Beleg fuer einen **aktiven** Wirksamkeitsanspruch sein und niemals mit `certainty: high`
kombiniert werden. Der Validator lehnt das ab.

## Wie verbinde ich einen Claim mit einem Artikel?

Ergaenze im YAML-Frontmatter des Markdown-Artikels:

```yaml
entity_id: substance-placeholder
claim_ids:
  - claim-00000000-0000-4000-8000-000000000000
```

`entity_id` und alle `claim_ids` muessen existieren und inhaltlich zum Artikel passen (der referenzierte Claim
sollte dieselbe Substanz/Entitaet betreffen). Der Validator prueft das automatisch.

## Wie validiere ich meine Aenderungen?

```bash
pip install -r requirements-dev.txt
python tools/validate_data.py --verbose
pytest
```

`validate_data.py` gibt lesbare Fehler- und Warnmeldungen mit Dateipfad aus, z. B.:

```
ERROR data/claims/claim-beispiel.yaml
  $.evidence[0].source_id: references missing source: source-nicht-vorhanden
```

Fehler (`ERROR`) muessen behoben werden, bevor ein Pull Request gemergt werden kann. Warnungen (`WARNING`,
z. B. zum veralteten Feld `evidenzstufe`) blockieren nichts, sollten aber beachtet werden.

## Welche Dateien sind generiert und duerfen NIE manuell bearbeitet werden?

- `build/catalog.json` — generiert durch `python tools/build_catalog.py`.
- `build/graph.json` — generiert durch `python tools/export_graph.py`.

Beide liegen unter `build/`, sind in `.gitignore` eingetragen und werden nicht committed. Wenn du eine
Aenderung im Katalog oder Graph siehst, die du dir nicht erklaeren kannst: sie kommt aus den YAML-Quelldateien
unter `data/`, nicht umgekehrt.

## `data/examples/`

Dieser Ordner enthaelt ausschliesslich offensichtlich fiktive Platzhalterdaten (`Placeholder Substance` usw.)
zur Illustration des Datenmodells und fuer die Testsuite. Er ist ein eigener, in sich geschlossener Namensraum
und geht **nicht** in den echten Katalog/Graph ein. Trage hier keine echten Substanzen ein.

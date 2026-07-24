---
title: Evidenzsystem
description: Klassifikation der Evidenzstärke für medizinisch relevante Aussagen in Peptide Atlas.
tags:
  - Grundlagen
  - Methodik
status: Aktiv
---

# Evidenzsystem

!!! warning "Neues Modell seit Phase 3 — dieser Abschnitt beschreibt das Legacy-System"
    Das hier beschriebene einfache A–E-Modell ist seit Phase 3 **Legacy**. Es gilt weiterhin für bestehende
    Artikel, die es bereits verwenden, wird aber für **neue wissenschaftliche Objektseiten nicht mehr
    verwendet**. Das aktuelle, mehrdimensionale Modell steht im Abschnitt „Claim-basiertes Evidenzmodell (seit
    Phase 3)" weiter unten. Es ersetzt die einfache A–E-Logik für neue Claims, nicht nur ergänzt sie.

## Legacy: Stufen A–E

Jede medizinisch relevante Aussage in bestehenden Artikeln erhält eine Evidenzstufe (A–E), die angibt, auf welcher Art von Beleg die Aussage beruht. Die Evidenzstufe wird direkt neben der Aussage oder im YAML-Frontmatter des Artikels (`evidenzstufe:`) angegeben.

| Stufe | Bedeutung |
|---|---|
| **A** | Mehrere hochwertige Humanstudien oder anerkannte Leitlinien |
| **B** | Einzelne kontrollierte Humanstudien |
| **C** | Kleine oder frühe Humanstudien (z. B. offene Studien, kleine Fallzahlen) |
| **D** | Tier- oder Zellstudien (präklinisch) |
| **E** | Hypothese, Anekdote oder Marketingaussage |

## Grundregeln (gelten für beide Systeme)

1. **Keine Aussage ohne Quelle.** Jede medizinisch relevante Aussage muss mit einer nachvollziehbaren Quelle belegt sein.
2. **Trennung der Evidenzebenen.** Zulassungsstatus, klinische Forschung, präklinische Forschung und Händlerangaben werden strikt getrennt dargestellt und nicht vermischt.
3. **Sichtbare Kennzeichnung von Unsicherheit.** Aussagen, die auf unsicherer oder vorläufiger Datenlage beruhen, werden explizit als *unklar* oder *experimentell* markiert — unabhängig von der vergebenen Stufe.
4. **Keine Aufwertung durch Sprache.** Die Formulierung einer Aussage darf ihre tatsächliche Evidenzstufe nicht verschleiern oder aufwerten.

## Anwendung im Artikel

Empfohlenes Format für einzelne Aussagen im Fließtext:

```markdown
Substanz X zeigte in einer kleinen offenen Studie (n=12) einen Effekt auf Y [Quelle, Jahr] `[Evidenz: C]`.
```

Im YAML-Frontmatter eines Artikels, der überwiegend einer Stufe zuzuordnen ist:

```yaml
evidenzstufe: C
```

Weitere Details zur redaktionellen Umsetzung siehe [Redaktionsstandard](redaktionsstandard.md).

## Claim-basiertes Evidenzmodell (seit Phase 3)

Das einfache A–E-Modell vermischt vier unterschiedliche Dimensionen: Art der Evidenz, Studiendesign, Qualität
und Sicherheit der Aussage. Seit Phase 3 werden diese Dimensionen getrennt bewertet — und zwar **pro Claim**
(einzelne, pruefbare Aussage), nicht pauschal pro Artikel. Ein Artikel kann gleichzeitig gut gesicherte
molekulare Eigenschaften, hochwertige Humanstudien, frühe klinische Ergebnisse, Tierstudien und theoretische
Hypothesen enthalten — ein einzelner Artikel-Wert würde das unweigerlich glätten.

**Wichtige Grundsätze:**

- Das neue mehrdimensionale Modell **ersetzt** die einfache A–E-Logik für neue Claims — es ergänzt sie nicht
  nur als zweite, gleichwertige Option.
- Bestehende A–E-Angaben in Artikeln sind **Legacy-Metadaten** (siehe Kasten oben) und werden toleriert, aber
  nicht weiter ausgebaut.
- Neue Artikel erhalten **keine pauschale Evidenznote** mehr. Stattdessen verweist das Frontmatter über
  `entity_id`/`claim_ids` auf die einzelnen, jeweils separat bewerteten Claims (siehe
  [Data Model](../project/Data_Model.md), [Phase 3 Dokumentation](../project/Phase_3_Scientific_Data_Architecture.md)).
- Evidenz wird **pro Claim** bewertet, nicht am Objekt (Substanz, Rezeptor, ...) selbst — ein Objekt hat keine
  eigene Evidenzstufe.

### Evidenzkategorie (Art der Evidenz)

| Kategorie | Bedeutung |
|---|---|
| `established_knowledge` (Gesicherte Erkenntnis) | Robuste, reproduzierte Daten, fachlicher Konsens, anerkannte Referenzwerke oder verbindliche regulatorische Dokumente. Nicht allein aufgrund einer einzelnen positiven Studie vergeben. |
| `clinical_evidence` (Klinische Evidenz) | Direkte Evidenz aus Humanstudien mit ausreichender methodischer Aussagekraft (RCTs, kontrollierte Studien, starke Metaanalysen). |
| `limited_evidence` (Begrenzte Evidenz) | Direkte Humaninformationen, aber begrenzt (kleine Stichprobe, frühe Phase, fehlende Kontrollgruppe, Fallserie, Konferenzabstract ...). |
| `preclinical_evidence` (Präklinische Evidenz) | Evidenz aus nichtmenschlichen/experimentellen Modellen (Tierstudie, Zellkultur, Organoid, ex-vivo, biochemischer Assay). |
| `theoretical_hypothesis` (Theoretische Hypothese) | Theoretische oder indirekt abgeleitete Annahme ohne ausreichenden direkten experimentellen Beleg. |
| `merchant_claim` (Händlerangabe) | Angabe eines Verkäufers/Händlers, nicht ausreichend durch unabhängige wissenschaftliche Quellen bestätigt. Niemals alleiniger Wirksamkeitsnachweis. |
| `personal_experience` (Persönliche Erfahrung) | Einzelbericht/Testimonial außerhalb systematischer Datenerhebung. Niemals als allgemeiner Wirksamkeitsnachweis dargestellt. |

**Wichtig:** Eine methodisch gute Tierstudie bleibt `preclinical_evidence` — sie wird nicht zu klinischer
Wirksamkeit umformuliert, nur weil sie sauber durchgeführt wurde. Umgekehrt ist eine Humanstudie nicht
automatisch hochwertige Evidenz: eine kleine, unkontrollierte Studie am Menschen ist `limited_evidence`, nicht
automatisch `clinical_evidence`.

### Sicherheit/Vertrauenswürdigkeit (`certainty`) — getrennt von der Evidenzkategorie

| Wert | Bedeutung |
|---|---|
| `high` (Hoch) | |
| `moderate` (Moderat) | |
| `low` (Niedrig) | |
| `very_low` (Sehr niedrig) | |
| `not_assessed` (Nicht bewertet) | Einzige Stufe, die ohne Begründung verwendet werden darf. |

Evidenzart und Sicherheit sind **zwei getrennte Dimensionen**: Evidenzkategorie beschreibt, *welche Art* von
Beleg vorliegt; `certainty` beschreibt, *wie sicher* die Redaktion sich der Aussage insgesamt ist. `certainty`
wird redaktionell vergeben (nicht automatisch aus dem Studiendesign berechnet) und braucht — außer bei
`not_assessed` — eine kurze Begründung (`certainty_rationale`). `certainty: high` ist ausgeschlossen, wenn die
einzige Evidenz eine Händlerseite oder ein persönlicher Bericht ist.

Vollständige technische Definition, Studiendesign-Vokabular und Validierungsregeln:
[Phase 3 Dokumentation](../project/Phase_3_Scientific_Data_Architecture.md).

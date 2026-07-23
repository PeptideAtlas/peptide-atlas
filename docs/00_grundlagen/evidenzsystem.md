---
title: Evidenzsystem
description: Klassifikation der Evidenzstärke für medizinisch relevante Aussagen in Peptide Atlas.
tags:
  - Grundlagen
  - Methodik
status: Aktiv
---

# Evidenzsystem

Jede medizinisch relevante Aussage in Peptide Atlas erhält eine Evidenzstufe (A–E), die angibt, auf welcher Art von Beleg die Aussage beruht. Die Evidenzstufe wird direkt neben der Aussage oder im YAML-Frontmatter des Artikels (`evidenzstufe:`) angegeben.

## Stufen

| Stufe | Bedeutung |
|---|---|
| **A** | Mehrere hochwertige Humanstudien oder anerkannte Leitlinien |
| **B** | Einzelne kontrollierte Humanstudien |
| **C** | Kleine oder frühe Humanstudien (z. B. offene Studien, kleine Fallzahlen) |
| **D** | Tier- oder Zellstudien (präklinisch) |
| **E** | Hypothese, Anekdote oder Marketingaussage |

## Grundregeln

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

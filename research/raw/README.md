# research/raw/ — lokaler Arbeitsbereich (nicht versioniert)

Dieser Ordner ist ausschließlich ein **optionaler lokaler Arbeitsbereich** für Datenbank-Exporte, Volltexte oder
andere Rohdateien, die aus rechtlichen (Urheberrecht, Lizenzbedingungen der Datenbankanbieter) oder technischen
Gründen (Größe, Binärformat) **nicht in Git versioniert werden dürfen**.

## Regeln

- Alles außer dieser `README.md` ist per `.gitignore` (`research/raw/*` / `!research/raw/README.md`) von der
  Versionierung ausgeschlossen.
- **Committe hier niemals** echte PDFs, RIS-, BibTeX-, CSV-Exporte oder sonstige Volltextdateien.
- Wenn du auf eine Datei aus `research/raw/` verweisen musst (z. B. aus einem `search_run`), referenziere sie
  über `export_reference` als **Beschreibung/Pfadhinweis**, nicht durch Einchecken der Datei selbst.
- Dieser Ordner ist kein Ersatz für ein Referenzverwaltungssystem (Zotero, EndNote o. ä.) — er ist nur temporärer
  lokaler Zwischenspeicher.

## Warum nicht einfach committen?

Viele Datenbankanbieter (PubMed/NCBI, Elsevier, Wiley, ...) und Volltextquellen untersagen die
Weiterverbreitung von Exporten oder Volltexten. Ein öffentliches Git-Repository ist Weiterverbreitung. Die
kanonische, versionierte Ablage für tatsächlich verwendete Informationen sind stattdessen die strukturierten
Kurz-Paraphrasen und Fundstellenangaben in `research/extractions/**` (siehe
[Scientific Research Protocol](../../docs/project/Scientific_Research_Protocol.md), Abschnitt „Urheberrecht und
Volltextspeicherung").

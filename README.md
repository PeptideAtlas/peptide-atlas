# Peptide Atlas

Eine deutschsprachige, wissenschaftlich orientierte Wissensdatenbank über Peptide, peptidbasierte Arzneimittel, Rezeptoren, Signalwege und experimentelle Forschungsstoffe.

Die Seite wird mit [MkDocs](https://www.mkdocs.org/) und dem [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) Theme gebaut und automatisch auf GitHub Pages veröffentlicht.

> **Hinweis:** Dieses Repository enthält ausschließlich die technische Umsetzung. Medizinische Inhalte werden separat geliefert, redaktionell geprüft und nach dem [Redaktionsstandard](docs/00_grundlagen/redaktionsstandard.md) sowie dem [Evidenzsystem](docs/00_grundlagen/evidenzsystem.md) eingeordnet. Siehe auch den [Haftungshinweis](docs/haftungshinweis.md).

## Projektstruktur

```
Peptide-Atlas/
├── docs/                    # Alle Inhaltsseiten (Markdown)
│   ├── index.md
│   ├── 00_grundlagen/
│   ├── 01_wirkstoffe/
│   ├── 02_biologie/
│   ├── 03_indikationen/
│   ├── 04_studien/
│   ├── 05_vergleiche/
│   ├── 06_medien/
│   ├── 07_glossar/
│   └── project/             # Architektur-/Projektdokumentation, siehe Phase_3_Scientific_Data_Architecture.md
├── schemas/                 # JSON Schema (Draft 2020-12) je Objektart, siehe data/README.md
├── data/                    # Strukturierte YAML-Daten (Entitäten, Quellen, Claims) — siehe data/README.md
│   ├── entities/
│   ├── sources/
│   ├── claims/
│   ├── vocabularies/        # kontrollierte Vokabulare (Prädikate, Evidenzkategorien, ...)
│   └── examples/            # ausschließlich fiktive Platzhalterdaten
├── tools/                   # validate_data.py, build_catalog.py, export_graph.py, new_id.py
├── tests/                   # pytest-Tests + Fixtures für die Datenvalidierung
├── build/                   # generierte Artefakte (catalog.json, graph.json) — nicht committed
├── templates/
│   └── artikelvorlage.md    # Wiederverwendbare Vorlage für neue Artikel
├── mkdocs.yml                # MkDocs-/Material-Konfiguration, Navigation
├── requirements.txt
├── requirements-dev.txt     # zusätzlich pytest, für lokale Entwicklung/CI
├── README.md
└── .github/workflows/       # ci.yml (Validierung + Tests) und deploy.yml (GitHub Pages)
```

Die wissenschaftliche Datenarchitektur (`schemas/`, `data/`, `tools/`, `tests/`) ist in
[docs/project/Phase_3_Scientific_Data_Architecture.md](docs/project/Phase_3_Scientific_Data_Architecture.md)
beschrieben; die Anleitung für Redakteur:innen steht in [data/README.md](data/README.md).

## Lokale Entwicklung

Voraussetzungen: Python 3.10+

```bash
python -m venv .venv
```

Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

Lokalen Entwicklungsserver mit Live-Reload starten:

```bash
mkdocs serve
```

Die Seite ist danach unter `http://127.0.0.1:8000/peptide-atlas/` erreichbar (der Pfad-Präfix ergibt sich aus `site_url` in `mkdocs.yml`).

Produktions-Build lokal testen (bricht bei Konfigurations- oder Link-Warnungen ab):

```bash
mkdocs build --strict
```

Das Ergebnis liegt danach im Ordner `site/` (nicht versioniert, siehe `.gitignore`).

### Wissenschaftliche Daten validieren

```bash
pip install -r requirements-dev.txt
python tools/validate_data.py --verbose
pytest
python tools/build_catalog.py
python tools/export_graph.py
```

Details und Anleitung für Redakteur:innen: [data/README.md](data/README.md).

## Deployment

Das Deployment auf GitHub Pages erfolgt automatisch über GitHub Actions (`.github/workflows/deploy.yml`) bei jedem Push auf `main`:

1. Checkout des Repositories
2. Installation der Abhängigkeiten aus `requirements.txt`
3. `mkdocs build --strict`
4. Upload und Veröffentlichung des `site/`-Verzeichnisses über die offiziellen GitHub-Pages-Actions

**Einmalige manuelle Einrichtung (im GitHub-Repository):** Unter *Settings → Pages* muss die *Source* einmalig auf **„GitHub Actions"** gestellt werden, damit der Workflow die Seite veröffentlichen darf.

## Redaktionelle Grundlagen

- [Was sind Peptide?](docs/00_grundlagen/was_sind_peptide.md)
- [Evidenzsystem](docs/00_grundlagen/evidenzsystem.md) — Klassifikation A–E nach Beleglage
- [Redaktionsstandard](docs/00_grundlagen/redaktionsstandard.md) — verbindliche Regeln für alle Inhalte
- [Roadmap](docs/roadmap.md) — aktueller Ausbaustand
- [Haftungshinweis](docs/haftungshinweis.md)

## Versionsstand

**Version 0.1** — funktionsfähiges Grundgerüst mit Navigation, Suche, Tags, hellem/dunklem Design und ersten Grundlagenartikeln. Details siehe [Roadmap](docs/roadmap.md).

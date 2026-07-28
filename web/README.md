# Peptide Atlas — Developer Preview (v0.1)

Eine echte, lokal lauffähige Web-Oberfläche auf der bestehenden Peptide-Atlas-Architektur — kein
Mockup, kein Figma-Export, keine Wegwerf-Demo. Sie liest **live** aus `research/**` und `data/**`
des Repos, das eine Ebene über `web/` liegt, und zeigt echte, aktuelle Projektzahlen (z. B. 197
pending Screening Records) — keine erfundenen oder gecachten Daten.

## Zweck dieser Phase

- Informationsarchitektur validieren (Dashboard / Protokoll / Kandidaten / Pipeline / Architektur)
- Navigation testen
- Datenmodell sichtbar machen (`research/**` → `data/**`, Objektbeziehungen)
- Eine wiederverwendbare Komponentenbibliothek aufbauen, auf der die eigentliche Plattform
  aufsetzen kann, ohne neu geschrieben zu werden

## Schnellstart

Voraussetzung: Node.js 20+ (getestet mit Node 22), npm.

```bash
cd web
npm install
npm run dev
```

Öffnet auf `http://localhost:3000`. Der Dev-Server muss aus `web/` heraus gestartet werden — die
Datenschicht liest per `process.cwd()/..` relativ zu `web/`, also aus dem Repo-Root
(`research/**`, `data/**`, `build/**`).

Production-Build (rein zur Verifikation, siehe „Offene Punkte" unten zur Live-Daten-Einschränkung):

```bash
npm run build && npm run start
```

Typecheck / Lint:

```bash
npx tsc --noEmit
npm run lint
```

## Seiten

| Route | Inhalt |
|---|---|
| `/` | Dashboard — Projektfortschritt, Pipeline-Status, Screening-Verteilung, Protokollübersicht, Graph-Stand |
| `/retatrutide` | Protokoll-Detail: Status, Screening-Pipeline nach Stufe, Kandidaten nach Datenbank, Search Runs, Review |
| `/candidates` | Candidate Explorer — alle 197 Kandidaten, Volltextsuche, Filter (Datenbank/Entscheidung), Detail-Slide-over |
| `/pipeline` | Research Pipeline — klickbare Stufen-Kette Protocol → SearchRun → … → data/**, mit echten Zählern je Stufe |
| `/architecture` | Objektarten und ihre Beziehungen, inkl. explizit als „Vorgeschlagen" markierter, noch nicht implementierter Objekte (`ResearchReviewer`, PR #8 / ADR-0059) |

## Architekturübersicht

**Stack:** Next.js 16 (App Router, Turbopack), React 19, TypeScript (strict), Tailwind CSS v4,
`js-yaml`, `lucide-react`. Kein zusätzliches State-Management, keine Chart-Bibliothek, kein
Graph-Rendering-Framework — bewusst schlank gehalten, siehe „Offene Punkte".

**Kein Backend, keine Datenbank.** Genau wie die bestehende Python-Toolchain
(`tools/validate_research.py`, `tools/build_catalog.py`, …) liest die App direkt aus den
YAML/JSON-Dateien des Repos — dieselbe Quelle der Wahrheit, kein zweites Datenmodell, keine
Synchronisation nötig.

```
web/
  app/                        Next.js App Router — eine Route je Seite oben
    page.tsx                  Dashboard
    retatrutide/page.tsx
    candidates/page.tsx
    pipeline/page.tsx
    architecture/page.tsx
    layout.tsx                Root Layout: Sidebar, Theme-Bootstrap-Script, Fonts
    globals.css                Design-Tokens (CSS-Variablen, hell/dunkel)
  components/
    layout/                   Sidebar (responsive, Mobile-Drawer), ThemeToggle
    ui/                       Card, StatCard, Badge, BreakdownBar, PageHeader, EmptyState
    candidates/                CandidateExplorer (Client-Komponente: Suche/Filter/Detail)
    pipeline/                  PipelineFlow (Client-Komponente: Stufen-Auswahl)
    architecture/               ArchitectureDiagram (Client-Komponente: Objekt-Auswahl)
  lib/
    data/
      paths.ts                 Pfade ins Repo-Root (research/, data/, build/, schemas/)
      yaml.ts                  YAML/JSON-Lesehelfer (kein Caching, jeder Request liest frisch)
      types.ts                 Handgeschriebene TS-Typen, gespiegelt von schemas/*.schema.json
      repository.ts            Rohdaten-Zugriff (getProtocols, getScreeningRecords, …)
      stats.ts                 Aggregation (Pipeline-Stats, Protokoll-Stats, Candidate-Explorer-Zeilen)
      pipeline.ts               Statische Pipeline-Stufenbeschreibung + Live-Zähler
      architecture.ts            Statische Objektart-/Beziehungsbeschreibung (Diagramm-Daten)
    cn.ts                       Kleiner classnames-Helfer
```

**Datenfluss:** Jede Seite ist eine React-Server-Component, die synchron (`fs.readFileSync`) aus
`lib/data/repository.ts` liest — kein Caching-Layer, keine `use cache`-Direktive, jeder
Seitenaufruf im Dev-Server sieht den aktuellen Dateisystemzustand. Interaktive Teile (Suche,
Filter, Detail-Panel, Diagramm-Auswahl, Theme, mobiles Menü) sind bewusst kleine, isolierte Client-
Komponenten, die fertig geladene Daten als Props bekommen — kein Client-seitiges Nachladen nötig,
da die Datenmengen (197 Kandidaten, 197 Screening Records) für eine In-Memory-Filterung im Browser
trivial klein sind.

**Design-System:** CSS-Variablen in `globals.css` (`--bg`, `--surface`, `--border`, `--text`,
`--accent`, Statusfarben) mit einer `.dark`-Klassen-Variante — hell/dunkel ist keine zwei
getrennten Stylesheets, sondern derselbe Variablensatz mit anderen Werten. Tailwind-Utility-Klassen
für Layout/Spacing, die Variablen für Farbe. Ein Blocking-Inline-Script im Root-Layout setzt die
`.dark`-Klasse vor dem ersten Paint (kein Flash of Unstyled Theme).

## Design-Referenz

Angelehnt an Apple / Linear / Stripe / Notion: neutrale Grundfarbe (Zinc-Skala), ein Akzentton
(Indigo), hairline-Borders statt schwerer Schatten, `rounded-xl`-Karten, großzügiger Weißraum,
Geist-Schriftfamilie. Responsive: Sidebar wird unterhalb `md` (768px) zu einem Hamburger-Menü mit
Slide-in-Drawer; der Candidate-Detail-Panel wird auf Mobile zum Vollbild-Overlay statt einer festen
384px-Seitenleiste.

## Verifikation (dieser Durchlauf)

- `npx tsc --noEmit` — 0 Fehler
- `npm run lint` — 0 Fehler, 0 Warnungen
- `npm run build` — erfolgreich, alle 5 Routen als statische Seiten vorgerendert
- Live im Dev-Server geprüft (Konsole/Server-Log fehlerfrei): Dashboard, Retatrutide, Candidate
  Explorer (Suche, Filter, Detail-Panel), Research Pipeline (Stufen-Auswahl), Architektur
  (Objekt-Auswahl) — alle mit den tatsächlichen, aktuellen Repo-Zahlen (u. a. 1 Protokoll, 197
  Kandidaten, 197 Screening Records, 0 Studies/Claims/Sources, Graph 0/0)
- Dark Mode per Toggle verifiziert (tatsächliche Hintergrundfarbe geprüft, nicht nur Klassenwechsel)
- Mobile-Viewport (375×812) verifiziert: kein horizontales Scrollen, Sidebar korrekt zu
  Hamburger-Menü reduziert

## CI

Eigenständiger GitHub-Actions-Job `web-validate-and-build` (`.github/workflows/ci.yml`, getrennt
vom bestehenden Python-Job `validate-and-test`), läuft bei jedem Pull Request und bei jedem Push
auf `main`: Node.js 22 (`actions/setup-node`, npm-Cache über `web/package-lock.json`), `npm ci`,
`npm run lint`, `npx tsc --noEmit`, `npm run build` — alle Schritte über
`defaults.run.working-directory: web`. Keine Deployment-Logik. Kein `.env`, kein Secret, keine
global installierten Pakete nötig — `web/package-lock.json` ist versioniert, CI installiert
ausschließlich darüber (`npm ci`, nie `npm install`).

## npm audit — transparent geprüft

```
npm audit             -> 12 High-Severity-Funde
npm audit --omit=dev  ->  3 High-Severity-Funde
```

Alle 3 produktionsrelevanten Funde (`postcss`, `sharp`) liegen **ausschließlich in von `next`
selbst gebündelten, verschachtelten Kopien**, nicht in unserem tatsächlichen Build-/Laufzeitpfad:

- **`postcss`** (verschachtelt unter `next/node_modules/postcss@8.4.31`, next-intern) — der
  tatsächliche CSS-Build läuft über `@tailwindcss/postcss@8.5.24` (oberhalb der als verwundbar
  gemeldeten Version `<=8.5.17`), aufgelöst über die oberste `node_modules/postcss`-Ebene.
- **`sharp`** (`node_modules/sharp@0.34.5`, direkte Abhängigkeit von `next` für dessen
  Bild-Optimierungs-Feature) — `next/image` wird im gesamten `app/`/`components/`/`lib/`-Code
  nicht ein einziges Mal importiert (`grep -rn "next/image"` liefert keinen Treffer), der Pfad ist
  in dieser App also inaktiv.

Die restlichen 9 Funde (`brace-expansion`/`minimatch`/`@eslint/*`) sind reine
Dev-Tooling-Abhängigkeiten von `eslint`/`eslint-config-next`, laufen nie im Produktionscode oder
im Build-Output. `npm audit fix --force` würde `next` auf 9.x und `eslint` auf eine deutlich
ältere Major-Version zurückstufen — bewusst nicht ohne Rücksprache gemacht, da das die App aktiv
beschädigen würde. Kein Blocker für diese Vorschau; wird bei künftigen `next`/`eslint`-Minor-
Updates automatisch mit aufgelöst, sobald die Upstream-Pakete selbst aktualisieren.

## Sicherheitsgrenze

- **Developer Preview v0.1 ist ausschließlich für lokale/interne Nutzung bestimmt** — gestartet per
  `npm run dev` auf dem eigenen Rechner bzw. in einer internen, nicht öffentlich erreichbaren
  Umgebung.
- **Es gibt noch kein öffentliches Produktions-Deployment.** Diese Vorschau wurde nicht auf einer
  öffentlich erreichbaren URL bereitgestellt und ist dafür in diesem Zustand nicht vorgesehen (siehe
  „`next build` prerendert aktuell statisch" oben — vor jedem öffentlichen Deployment ist ohnehin
  eine explizite Live-Daten-/Revalidierungsentscheidung fällig).
- **Die bekannten `npm audit`-Funde (siehe oben) werden vor einem öffentlichen Deployment erneut
  geprüft** — unabhängig davon, ob sie bis dahin durch reguläre `next`/`eslint`-Updates bereits
  aufgelöst sind. Ein interner/lokaler Vorschau-Status ist kein Freibrief, offene
  Sicherheitsbefunde dauerhaft zu ignorieren.
- **Wichtig für die Einordnung:** dass `next/image`/`sharp` im Code nicht aufgerufen wird und der
  next-interne `postcss`-Pfad nicht der tatsächliche Build-Pfad ist, **reduziert das praktische
  Risiko dieser Vorschau, beseitigt aber nicht den formalen `npm audit`-Befund selbst.** Die
  verwundbaren Paketversionen sind weiterhin in `node_modules` vorhanden, solange `next` sie
  bündelt — „aktuell inaktiv genutzt" ist kein Ersatz für eine tatsächliche Behebung und wird
  entsprechend nicht als erledigt behandelt.
- **Keine erzwungenen Downgrades:** `npm audit fix --force` wurde bewusst **nicht** ausgeführt (es
  würde `next` auf 9.x und `eslint` auf eine deutlich ältere Major-Version zurückstufen und die App
  aktiv beschädigen). Die Funde bleiben offen dokumentiert statt scheinbar per Downgrade "gelöst".

## Offene Punkte

- **Screenshots konnten in dieser Session nicht automatisiert erzeugt werden** — das Browser-Pane-
  Tool konnte den Viewport in dieser Umgebung nicht kompositieren (Anzeige nicht sichtbar). Die
  App wurde stattdessen strukturell verifiziert (Seiteninhalt, Konsole, Interaktionstests per
  DOM/JS). Screenshots lassen sich jederzeit nachreichen, sobald das Browser-Pane sichtbar ist,
  oder manuell durch Öffnen von `http://localhost:3000` erzeugen.
- **`next build` prerendert aktuell statisch** — für den lokalen Entwicklungsbetrieb (`npm run dev`,
  der primäre Anwendungsfall dieser Phase) ist das irrelevant, jeder Request liest live. Für einen
  späteren Produktivbetrieb mit `next build`/`next start` müsste je nach gewünschtem Verhalten
  entweder `export const dynamic = "force-dynamic"` gesetzt oder eine echte Revalidierungsstrategie
  entworfen werden, sobald `research/**`/`data/**` sich zur Laufzeit ändern können sollen.
  Kein Blocker für diese Vorschau, aber Teil der Roadmap-Entscheidung.
- **Architektur- und Pipeline-Diagramme sind handgepflegte Beschreibungen** (`lib/data/pipeline.ts`,
  `lib/data/architecture.ts`), keine automatische Introspektion der JSON-Schemas. Bei einer echten
  Schema-Änderung müssen diese beiden Dateien manuell nachgezogen werden — eine spätere Version
  könnte die Objekt-/Beziehungsliste direkt aus `schemas/*.schema.json` generieren.
- **Kein echtes Node-Graph-Rendering** (Zoom/Pan/Drag) für die Architektur-Seite — bewusst als
  klickbare Kartenreihen umgesetzt statt mit einer Graph-Bibliothek (react-flow o. ä.), um die
  Abhängigkeitsfläche für v0.1 klein zu halten. Wäre der naheliegende nächste Schritt, falls die
  Objektzahl wächst oder Freitext-Beziehungen (nicht nur Vorwärtspfeile) dargestellt werden sollen.
- **Kein automatisierter Test (Playwright/Vitest) vorhanden** — alle Verifikation in dieser Phase
  war manuell/interaktiv. Für eine produktivere Plattform wäre mindestens ein Smoke-Test je Route
  sinnvoll, der prüft, dass reale Repo-Zahlen (z. B. Kandidatenanzahl) korrekt gerendert werden.
- **Keine Barrierefreiheitsprüfung (a11y-Audit)** durchgeführt — Fokuszustände, Tastaturnavigation
  im Candidate-Explorer und Kontrastwerte im Dark Mode sind nicht systematisch geprüft.
- **Kein API-/Auth-Layer** — bewusst, da diese Phase nur die Informationsarchitektur validieren
  soll. Sobald es einen Schreibpfad geben soll (z. B. echtes Screening im Browser durchführen),
  ist das ein eigenständiger, deutlich größerer Architekturschritt (Server Actions oder Route
  Handlers, plus dieselben CSO-Guardrails wie im Python-Tooling).
- **`decision_history`/`revision_context`/Reviewer-Modell (PR #8) sind nur in der Architektur-Seite
  als „Vorgeschlagen" dokumentiert**, nicht interaktiv nachgebildet — konsistent mit dem Stand des
  Hauptrepos (reine Spezifikation, keine Implementierung).

## Was diese Vorschau **nicht** tut

- Keine Fake- oder Platzhalterdaten — jede Zahl kommt live aus `research/**`/`data/**`.
- Keine wissenschaftlichen Behauptungen — Kandidaten werden als Discovery-Funde angezeigt, nie als
  geprüfte oder eingeschlossene Evidenz.
- Kein Schreibzugriff — reine Leseansicht, ändert nichts an den Projektdaten.

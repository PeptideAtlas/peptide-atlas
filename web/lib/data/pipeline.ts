import { getPipelineStats } from "./stats";

export interface PipelineStageDef {
  id: string;
  title: string;
  count: number;
  path: string;
  description: string;
  breakdown?: { label: string; value: number }[];
}

/** Static description of the research pipeline, with live counts merged in. */
export function getPipelineStageDefs(): PipelineStageDef[] {
  const s = getPipelineStats();

  return [
    {
      id: "protocol",
      title: "Research Protocol",
      count: s.protocols,
      path: "research/protocols/**",
      description:
        "Definiert Forschungsfragen, Suchdatenbanken, Screening-/Extraktions-Policy und Ein-/Ausschlusskriterien, bevor irgendeine Recherche beginnt. Muss vom CSO freigegeben sein (status: approved).",
    },
    {
      id: "search_run",
      title: "Search Run",
      count: s.searchRuns,
      path: "research/search_runs/**",
      description:
        "Ein unveränderlicher Protokoll-Datenbank-Suchlauf (z. B. PubMed ESearch, ClinicalTrials.gov API v2) mit exakter Query, Zeitpunkt und Trefferzahl. Nach dem Merge technisch schreibgeschützt.",
    },
    {
      id: "search_result",
      title: "Search Result Manifest",
      count: s.searchResultManifests,
      path: "research/search_results/**",
      description:
        "Die unveränderte Trefferliste eines einzelnen Suchlaufs (Identifikatoren wie PMID/NCT-ID), mit Pflicht-Hash über die sortierte Liste.",
    },
    {
      id: "candidate_manifest",
      title: "Candidate Manifest",
      count: s.candidateManifests,
      path: "research/candidates/**",
      description:
        `Protokoll- und datenbankgebundene Vereinigungsmenge über mehrere Search Result Manifests hinweg — ${s.candidatesTotal} Kandidaten insgesamt. Kein Beweis für Relevanz, nur ein Discovery-Snapshot.`,
    },
    {
      id: "screening",
      title: "Screening Record",
      count: s.screeningRecords,
      path: "research/screening/**",
      description:
        "Ein Screening-Datensatz je Kandidat: Ein-/Ausschlussentscheidung mit Begründung, Erst-/Zweitprüfung, Adjudikation bei Konflikt. Vierstufig: Deduplizierung → Titel/Abstract → Volltext → Abschließend.",
      breakdown: Object.entries(s.screeningByStage).map(([label, value]) => ({ label, value })),
    },
    {
      id: "extraction",
      title: "Extraction Record",
      count: s.extractionRecords,
      path: "research/extractions/**",
      description:
        "Getrennte Extraktion je Forschungsbereich (Identität, Mechanismus, Pharmakokinetik, klinisch, Sicherheit, …) aus final eingeschlossenen Kandidaten, mit Verifikationspflicht.",
    },
    {
      id: "promotion",
      title: "Promotion Record",
      count: s.promotionRecords,
      path: "research/promotions/**",
      description:
        "Dokumentiert die Entscheidung, eine extrahierte Beobachtung als kanonischen Claim/Source unter data/** zu veröffentlichen — erfordert Zweitreview, nie automatisch.",
    },
    {
      id: "canonical",
      title: "data/** (kanonisch)",
      count: s.claims + s.sources + s.studies,
      path: "data/**",
      description:
        `Die veröffentlichte Wissensbasis: ${s.sources} Sources, ${s.studies} Studies, ${s.claims} Claims. Aktuell leer — noch keine Promotion durchgeführt.`,
    },
  ];
}

import {
  getProtocols,
  getSearchRuns,
  getSearchResultManifests,
  getCandidateManifests,
  getAllCandidates,
  getScreeningRecords,
  getExtractionRecordCount,
  getPromotionRecordCount,
  getDataEntityCounts,
  getGraph,
} from "./repository";
import type {
  ScreeningDecision,
  ScreeningStage,
  PubmedCandidateMetadata,
  ClinicalTrialsCandidateMetadata,
} from "./types";

function countBy<T extends string>(items: T[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const item of items) out[item] = (out[item] ?? 0) + 1;
  return out;
}

export interface PipelineStats {
  protocols: number;
  searchRuns: number;
  searchResultManifests: number;
  candidateManifests: number;
  candidatesTotal: number;
  screeningRecords: number;
  screeningByDecision: Record<string, number>;
  screeningByStage: Record<string, number>;
  extractionRecords: number;
  promotionRecords: number;
  claims: number;
  sources: number;
  studies: number;
  graphNodes: number;
  graphEdges: number;
}

export function getPipelineStats(): PipelineStats {
  const screening = getScreeningRecords();
  const dataCounts = getDataEntityCounts();
  const graph = getGraph();

  return {
    protocols: getProtocols().length,
    searchRuns: getSearchRuns().length,
    searchResultManifests: getSearchResultManifests().length,
    candidateManifests: getCandidateManifests().length,
    candidatesTotal: getAllCandidates().length,
    screeningRecords: screening.length,
    screeningByDecision: countBy(screening.map((s) => s.decision as ScreeningDecision)),
    screeningByStage: countBy(screening.map((s) => s.decision_stage as ScreeningStage)),
    extractionRecords: getExtractionRecordCount(),
    promotionRecords: getPromotionRecordCount(),
    claims: dataCounts.claims,
    sources: dataCounts.sources,
    studies: dataCounts.studies,
    graphNodes: graph?.nodes.length ?? 0,
    graphEdges: graph?.edges.length ?? 0,
  };
}

export interface ProtocolStats {
  protocolId: string;
  candidatesByDatabase: Record<string, number>;
  screeningByDecision: Record<string, number>;
  screeningByStage: Record<string, number>;
  searchRuns: { database: string; interface: string; resultCount: number; executedAt: string }[];
}

export function getProtocolStats(protocolId: string): ProtocolStats {
  const candidates = getAllCandidates().filter((c) => c.protocolId === protocolId);
  const screening = getScreeningRecords().filter((s) => s.protocol_id === protocolId);
  const searchRuns = getSearchRuns().filter((r) => r.protocol_id === protocolId);

  const candidatesByDatabase: Record<string, number> = {};
  for (const c of candidates) {
    candidatesByDatabase[c.database] = (candidatesByDatabase[c.database] ?? 0) + 1;
  }

  return {
    protocolId,
    candidatesByDatabase,
    screeningByDecision: countBy(screening.map((s) => s.decision)),
    screeningByStage: countBy(screening.map((s) => s.decision_stage)),
    searchRuns: searchRuns.map((r) => ({
      database: r.database,
      interface: r.interface,
      resultCount: r.result_count,
      executedAt: r.executed_at,
    })),
  };
}

function isPubmedMetadata(
  m: PubmedCandidateMetadata | ClinicalTrialsCandidateMetadata | null
): m is PubmedCandidateMetadata {
  return !!m && "title" in m;
}

export interface CandidateExplorerRow {
  candidateId: string;
  manifestId: string;
  database: string;
  identifierNamespace: string;
  identifierValue: string;
  title: string;
  subtitle: string | null;
  metadataStatus: string;
  decision: string;
  decisionStage: string;
  screeningRecordId: string | null;
  doi: string | null;
}

/** Every candidate joined with its screening decision (if a screening record already exists). */
export function getCandidateExplorerRows(): CandidateExplorerRow[] {
  const candidates = getAllCandidates();
  const screening = getScreeningRecords();

  const screeningByCandidateId = new Map(
    screening.filter((s) => s.candidate_id).map((s) => [s.candidate_id as string, s])
  );

  return candidates.map((c) => {
    const meta = c.metadata;
    let title = "(kein Titel — Metadaten noch nicht abgerufen)";
    let subtitle: string | null = null;
    let doi: string | null = null;

    if (isPubmedMetadata(meta)) {
      title = meta.title;
      subtitle = [meta.journal, meta.publication_year].filter(Boolean).join(" · ") || null;
      doi = meta.doi;
    } else if (meta) {
      title = meta.brief_title;
      subtitle = [meta.sponsor, meta.phases?.join("/"), meta.overall_status]
        .filter(Boolean)
        .join(" · ") || null;
    }

    const screeningRecord = screeningByCandidateId.get(c.candidate_id);

    return {
      candidateId: c.candidate_id,
      manifestId: c.manifestId,
      database: c.database,
      identifierNamespace: c.primary_identifier.namespace,
      identifierValue: c.primary_identifier.value,
      title,
      subtitle,
      metadataStatus: c.metadata_status,
      decision: screeningRecord?.decision ?? "pending",
      decisionStage: screeningRecord?.decision_stage ?? "deduplication",
      screeningRecordId: screeningRecord?.id ?? null,
      doi,
    };
  });
}

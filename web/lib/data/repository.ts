import fs from "node:fs";
import path from "node:path";
import { readYamlDir, readYamlDirRecursive, readJsonFile, readYamlFile } from "./yaml";
import {
  RESEARCH_DIR,
  DATA_DIR,
  BUILD_DIR,
} from "./paths";
import type {
  ResearchProtocol,
  ResearchSearchRun,
  ResearchSearchResultManifest,
  ResearchCandidateManifest,
  CandidateEntry,
  ResearchScreeningRecord,
  InitializationManifest,
  CatalogJson,
  GraphJson,
  Vocabulary,
} from "./types";

// ---------------------------------------------------------------------------
// research/** -- live, real project data (Retatrutide pilot + protocol shell)
// ---------------------------------------------------------------------------

export function getProtocols(): ResearchProtocol[] {
  return readYamlDir<ResearchProtocol>(path.join(RESEARCH_DIR, "protocols"))
    .map((e) => e.data)
    .filter(Boolean);
}

export function getProtocol(id: string): ResearchProtocol | undefined {
  return getProtocols().find((p) => p.id === id);
}

export function getSearchRuns(): ResearchSearchRun[] {
  return readYamlDir<ResearchSearchRun>(path.join(RESEARCH_DIR, "search_runs"))
    .map((e) => e.data)
    .filter(Boolean);
}

export function getSearchResultManifests(): ResearchSearchResultManifest[] {
  return readYamlDir<ResearchSearchResultManifest>(path.join(RESEARCH_DIR, "search_results"))
    .map((e) => e.data)
    .filter(Boolean);
}

export function getCandidateManifests(): ResearchCandidateManifest[] {
  return readYamlDir<ResearchCandidateManifest>(path.join(RESEARCH_DIR, "candidates"))
    .map((e) => e.data)
    .filter(Boolean);
}

export interface FlatCandidate extends CandidateEntry {
  manifestId: string;
  protocolId: string;
  database: string;
  identifierNamespace: string;
}

/** Every candidate across every candidate manifest, flattened for display. */
export function getAllCandidates(): FlatCandidate[] {
  const manifests = getCandidateManifests();
  const out: FlatCandidate[] = [];
  for (const m of manifests) {
    for (const c of m.candidates) {
      out.push({
        ...c,
        manifestId: m.id,
        protocolId: m.protocol_id,
        database: m.database,
        identifierNamespace: m.identifier_namespace,
      });
    }
  }
  return out;
}

export function getScreeningRecords(): ResearchScreeningRecord[] {
  return readYamlDir<ResearchScreeningRecord>(path.join(RESEARCH_DIR, "screening"))
    .map((e) => e.data)
    .filter(Boolean);
}

export function getExtractionRecordCount(): number {
  return readYamlDir(path.join(RESEARCH_DIR, "extractions")).filter((e) => e.data).length;
}

export function getPromotionRecordCount(): number {
  return readYamlDir(path.join(RESEARCH_DIR, "promotions")).filter((e) => e.data).length;
}

export function getInitializationManifest(): InitializationManifest | null {
  return readYamlFile<InitializationManifest>(
    path.join(RESEARCH_DIR, "screening_status", "initialization_manifest.yaml")
  );
}

export function getVocabulary(name: string): Vocabulary | null {
  return readYamlFile<Vocabulary>(path.join(RESEARCH_DIR, "vocabularies", `${name}.yaml`));
}

export function vocabLabel(vocab: Vocabulary | null, value: string, lang: "de" | "en" = "de"): string {
  const entry = vocab?.values.find((v) => v.value === value);
  return entry?.labels[lang] ?? value;
}

// ---------------------------------------------------------------------------
// data/** -- the canonical published knowledge base (currently empty; the
// scientific screening/extraction/promotion pipeline has not produced any
// canonical Source/Study/Claim/Entity yet -- shown honestly as 0, not hidden)
// ---------------------------------------------------------------------------

function countYamlRecursive(dir: string): number {
  if (!fs.existsSync(dir)) return 0;
  return readYamlDirRecursive(dir).length;
}

export interface DataEntityCounts {
  claims: number;
  sources: number;
  studies: number;
  substances: number;
  receptors: number;
  pathways: number;
  conditions: number;
  organizations: number;
  adverseEvents: number;
}

export function getDataEntityCounts(): DataEntityCounts {
  return {
    claims: countYamlRecursive(path.join(DATA_DIR, "claims")),
    sources: countYamlRecursive(path.join(DATA_DIR, "sources")),
    studies: countYamlRecursive(path.join(DATA_DIR, "entities", "studies")),
    substances: countYamlRecursive(path.join(DATA_DIR, "entities", "substances")),
    receptors: countYamlRecursive(path.join(DATA_DIR, "entities", "receptors")),
    pathways: countYamlRecursive(path.join(DATA_DIR, "entities", "pathways")),
    conditions: countYamlRecursive(path.join(DATA_DIR, "entities", "conditions")),
    organizations: countYamlRecursive(path.join(DATA_DIR, "entities", "organizations")),
    adverseEvents: countYamlRecursive(path.join(DATA_DIR, "entities", "adverse_events")),
  };
}

// ---------------------------------------------------------------------------
// build/** -- catalog.json / graph.json build artefacts (gitignored, may be
// stale or absent if `python tools/build_catalog.py` hasn't run recently)
// ---------------------------------------------------------------------------

export function getCatalog(): CatalogJson | null {
  return readJsonFile<CatalogJson>(path.join(BUILD_DIR, "catalog.json"));
}

export function getGraph(): GraphJson | null {
  return readJsonFile<GraphJson>(path.join(BUILD_DIR, "graph.json"));
}

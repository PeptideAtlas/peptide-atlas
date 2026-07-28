/**
 * Hand-written TypeScript mirrors of the JSON Schemas under schemas/*.schema.json.
 * These intentionally only cover the fields the preview actually renders --
 * see docs/project/Data_Model.md and schemas/**.schema.json for the full,
 * authoritative definitions. This preview does NOT re-validate data (that
 * remains tools/validate_research.py / validate_data.py's job); it assumes
 * the repo is in a state where those pass.
 */

export type ResearchProtocolStatus = "draft" | "approved" | "amended" | "retired";

export interface ResearchQuestion {
  id: string;
  topic: string;
  question: Record<string, string>;
}

export interface ResearchProtocol {
  schema_version: string;
  id: string;
  title: string;
  subject: { working_name: string; notes?: Record<string, string> };
  status: ResearchProtocolStatus;
  version: number;
  objectives: Record<string, string>[];
  research_questions: ResearchQuestion[];
  scope: {
    description: Record<string, string>;
    in_scope: string[];
    out_of_scope: string[];
  };
  planned_information_sources: { database: string; role: string; notes?: string }[];
  planned_search_concepts: string[];
  eligibility: { inclusion_criteria: string[]; exclusion_criteria: string[] };
  screening_policy: {
    description: Record<string, string>;
    stages: string[];
    dual_reviewer_stages: string[];
  };
  extraction_policy?: { fields_to_extract: string[] };
  created_at: string;
  updated_at: string;
  review?: {
    last_reviewed_at: string | null;
    reviewers: string[];
    approval_decision?: string;
  };
}

export interface ResearchSearchRun {
  schema_version: string;
  id: string;
  protocol_id: string;
  database: string;
  interface: string;
  interface_profile?: { id: string; rationale: string | null };
  executed_at: string;
  executed_by: string;
  exact_query: string;
  result_capture: { status: string; manifest_id: string | null; rationale: string | null };
  result_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ResearchSearchResultManifest {
  schema_version: string;
  id: string;
  search_run_id: string;
  identifier_type: string;
  identifiers: string[];
}

export interface CandidatePrimaryIdentifier {
  namespace: string;
  value: string;
}

export interface PubmedCandidateMetadata {
  title: string;
  publication_year: number | null;
  journal: string | null;
  publication_types: string[];
  doi: string | null;
  pmcid: string | null;
  authors: string[];
  abstract_available: boolean;
  language: string | null;
}

export interface ClinicalTrialsCandidateMetadata {
  brief_title: string;
  official_title: string | null;
  overall_status: string | null;
  phases: string[];
  sponsor: string | null;
  interventions?: string[];
}

export interface CandidateEntry {
  candidate_id: string;
  primary_identifier: CandidatePrimaryIdentifier;
  discovered_in_search_run_ids: string[];
  metadata: PubmedCandidateMetadata | ClinicalTrialsCandidateMetadata | null;
  metadata_status: string;
  metadata_fetch_note: string | null;
}

export interface ResearchCandidateManifest {
  schema_version: string;
  id: string;
  protocol_id: string;
  database: string;
  identifier_namespace: string;
  source_search_run_ids: string[];
  source_result_manifest_ids: string[];
  candidate_count: number;
  candidates: CandidateEntry[];
}

export type ScreeningDecision =
  | "pending"
  | "include"
  | "exclude"
  | "duplicate"
  | "awaiting_full_text"
  | "uncertain";

export type ScreeningStage = "deduplication" | "title_abstract" | "full_text" | "final";

export interface DecisionHistoryEntry {
  sequence: number;
  stage: ScreeningStage;
  primary_decision: ScreeningDecision;
  primary_decision_reason: string | null;
  decision: ScreeningDecision;
  decision_reason: string | null;
  duplicate_of: string | null;
  primary_duplicate_of: string | null;
  decided_by: string;
  decided_at: string;
  full_text_status: string;
  second_review?: SecondReview | null;
}

export interface SecondReview {
  reviewer_decision: ScreeningDecision;
  reviewer_decision_reason: string | null;
  reviewer_duplicate_of: string | null;
  reviewed_by: string;
  reviewed_at: string;
  decision_confirmed: boolean;
  adjudication?: {
    resolved_by: string;
    resolved_at: string;
    final_decision: "include" | "exclude";
    rationale: string;
  } | null;
}

export interface CandidateIdentifiers {
  doi: string | null;
  pmid: string | null;
  pmcid: string | null;
  nct_id: string | null;
  isbn: string | null;
  url: string | null;
}

export interface ResearchScreeningRecord {
  schema_version: string;
  id: string;
  protocol_id: string;
  search_run_ids: string[];
  candidate_identifiers: CandidateIdentifiers;
  candidate_title: string;
  candidate_source_type: string;
  decision: ScreeningDecision;
  decision_stage: ScreeningStage;
  decision_reason: string | null;
  duplicate_of: string | null;
  full_text_status: string;
  screened_by: string;
  screened_at: string;
  second_review: SecondReview | null;
  decision_history: DecisionHistoryEntry[];
  canonical_source_id: string | null;
  candidate_manifest_id: string | null;
  candidate_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface InitializationManifestEntry {
  protocol_id: string;
  notes: string | null;
  status: string;
  expected_candidate_count: number;
  initialized_by: string;
  completed_at: string;
}

export interface InitializationManifest {
  schema_version: string;
  protocols: InitializationManifestEntry[];
}

export interface CatalogJson {
  schema_version: string;
  generated_at: string;
  counts: { claims: number; sources: number };
  entities: unknown[];
  studies: unknown[];
  sources: unknown[];
  claims: unknown[];
}

export interface GraphJson {
  schema_version: string;
  generated_at: string;
  nodes: unknown[];
  edges: unknown[];
}

export interface VocabValue {
  value: string;
  labels: { de?: string; en?: string };
}

export interface Vocabulary {
  schema_version: string;
  values: VocabValue[];
}

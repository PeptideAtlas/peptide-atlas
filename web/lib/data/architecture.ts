export interface ArchitectureNode {
  id: string;
  label: string;
  schema: string | null;
  status: "implemented" | "proposed";
  description: string;
  fields: string[];
}

export const RESEARCH_PIPELINE_NODES: ArchitectureNode[] = [
  {
    id: "protocol",
    label: "ResearchProtocol",
    schema: "research_protocol.schema.json",
    status: "implemented",
    description: "Forschungsfragen, Datenbanken, Screening-/Extraktionspolicy, Ein-/Ausschlusskriterien.",
    fields: ["id", "status", "screening_policy.stages", "screening_policy.dual_reviewer_stages"],
  },
  {
    id: "search_run",
    label: "ResearchSearchRun",
    schema: "research_search_run.schema.json",
    status: "implemented",
    description: "Ein unveränderlicher Suchlauf gegen eine Datenbank mit exakter Query.",
    fields: ["protocol_id", "database", "exact_query", "result_count"],
  },
  {
    id: "search_result",
    label: "ResearchSearchResultManifest",
    schema: "research_search_result_manifest.schema.json",
    status: "implemented",
    description: "Unveränderte Trefferliste eines Suchlaufs, Hash-gesichert.",
    fields: ["search_run_id", "identifier_type", "identifiers[]"],
  },
  {
    id: "candidate_manifest",
    label: "ResearchCandidateManifest",
    schema: "research_candidate_manifest.schema.json",
    status: "implemented",
    description: "Protokoll×Datenbank-Normalisierung mehrerer Suchläufe zu stabilen Kandidaten.",
    fields: ["protocol_id", "database", "candidates[].candidate_id", "candidates[].metadata"],
  },
  {
    id: "screening",
    label: "ResearchScreeningRecord",
    schema: "research_screening_record.schema.json",
    status: "implemented",
    description: "Ein-/Ausschlussentscheidung je Kandidat, Erst-/Zweitprüfung, Adjudikation, decision_history.",
    fields: ["candidate_id", "decision", "decision_stage", "decision_history[]", "second_review"],
  },
  {
    id: "extraction",
    label: "ResearchExtractionRecord",
    schema: "research_extraction_record.schema.json",
    status: "implemented",
    description: "Bereichsweise Extraktion (Identität, Mechanismus, PK, klinisch, Sicherheit, …) mit Verifikation.",
    fields: ["screening_record_id", "fields_extracted", "verification_required"],
  },
  {
    id: "promotion",
    label: "ResearchPromotionRecord",
    schema: "research_promotion_record.schema.json",
    status: "implemented",
    description: "Entscheidung, eine Extraktion als kanonischen Claim/Source zu veröffentlichen — Zweitreview-Pflicht.",
    fields: ["extraction_record_id", "review.reviewers[]", "promoted_source_id"],
  },
];

export const CANONICAL_NODES: ArchitectureNode[] = [
  {
    id: "source",
    label: "Source",
    schema: "source.schema.json",
    status: "implemented",
    description: "Eine kanonische, zitierfähige Quelle (Publikation, Registereintrag, Dokument).",
    fields: ["id", "source_type", "identifiers"],
  },
  {
    id: "study",
    label: "Study",
    schema: "study.schema.json",
    status: "implemented",
    description: "Eine wissenschaftliche Studie, kann mehrere Sources (Publikationen/Registereinträge) bündeln.",
    fields: ["id", "source_ids[]", "design"],
  },
  {
    id: "claim",
    label: "Claim",
    schema: "claim.schema.json",
    status: "implemented",
    description: "Eine einzelne, evidenzbasierte wissenschaftliche Aussage mit Evidenzstufe und Quelle.",
    fields: ["id", "evidence_category", "certainty", "source_id", "status"],
  },
  {
    id: "entity",
    label: "Entity (Substance/Receptor/…)",
    schema: "substance.schema.json u. a.",
    status: "implemented",
    description: "Substanzen, Rezeptoren, Pathways, Conditions, Organisationen, Adverse Events.",
    fields: ["id", "entity_type"],
  },
];

export const PROPOSED_NODES: ArchitectureNode[] = [
  {
    id: "reviewer",
    label: "ResearchReviewer",
    schema: "research_reviewer.schema.json (Entwurf)",
    status: "proposed",
    description:
      "PR #8 / ADR-0059 (CSO-freigegeben, noch nicht implementiert): struktureller Akteurstyp für research_actor_id-Felder — human/ai_assistant/automation/service, künftig external_expert/editorial_board.",
    fields: ["id", "actor_type", "active"],
  },
];

export const PROPOSED_REFERENCES = [
  { from: "screening.decided_by", to: "reviewer" },
  { from: "screening.second_review.reviewed_by", to: "reviewer" },
  { from: "screening.second_review.adjudication.resolved_by", to: "reviewer" },
];

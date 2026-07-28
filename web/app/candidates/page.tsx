import { PageHeader } from "@/components/ui/PageHeader";
import { CandidateExplorer } from "@/components/candidates/CandidateExplorer";
import { getCandidateExplorerRows } from "@/lib/data/stats";

export default function CandidatesPage() {
  const rows = getCandidateExplorerRows();

  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Candidate Explorer"
        description={`Alle ${rows.length} Discovery-Kandidaten aus research/candidates/** — Suche, Filter und Detailansicht. Ein Kandidat ist ein Discovery-Fund, keine Relevanz- oder Einschlussentscheidung.`}
      />
      <div className="min-h-0 flex-1">
        <CandidateExplorer rows={rows} />
      </div>
    </div>
  );
}

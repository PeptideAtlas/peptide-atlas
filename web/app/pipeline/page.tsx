import { PageHeader } from "@/components/ui/PageHeader";
import { PipelineFlow } from "@/components/pipeline/PipelineFlow";
import { getPipelineStageDefs } from "@/lib/data/pipeline";

export default function PipelinePage() {
  const stages = getPipelineStageDefs();

  return (
    <div>
      <PageHeader
        title="Research Pipeline"
        description="Der vollständige Weg eines Kandidaten von der Suche bis zur kanonischen Veröffentlichung — jede Stufe zeigt die tatsächliche Objektzahl aus diesem Checkout. Auf eine Stufe klicken für Details."
      />
      <div className="p-8">
        <PipelineFlow stages={stages} />
      </div>
    </div>
  );
}

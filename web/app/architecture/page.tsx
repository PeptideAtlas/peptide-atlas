import { PageHeader } from "@/components/ui/PageHeader";
import { ArchitectureDiagram } from "@/components/architecture/ArchitectureDiagram";
import {
  RESEARCH_PIPELINE_NODES,
  CANONICAL_NODES,
  PROPOSED_NODES,
} from "@/lib/data/architecture";

export default function ArchitecturePage() {
  return (
    <div>
      <PageHeader
        title="Architektur"
        description="Objektarten und ihre Beziehungen — von der Recherche-Provenienz (research/**) bis zum kanonischen Wissensmodell (data/**). Auf ein Objekt klicken für Schema und Felder."
      />
      <div className="p-8">
        <ArchitectureDiagram
          research={RESEARCH_PIPELINE_NODES}
          canonical={CANONICAL_NODES}
          proposed={PROPOSED_NODES}
        />
      </div>
    </div>
  );
}

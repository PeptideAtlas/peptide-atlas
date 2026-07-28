import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardHeader } from "@/components/ui/Card";
import { Badge, decisionTone, statusTone } from "@/components/ui/Badge";
import { BreakdownBar } from "@/components/ui/BreakdownBar";
import { getPipelineStats } from "@/lib/data/stats";
import { getProtocols, getVocabulary, vocabLabel } from "@/lib/data/repository";
import {
  FileStack,
  Beaker,
  ClipboardList,
  Microscope,
  Quote,
  BookMarked,
  GitBranch,
  ArrowRight,
} from "lucide-react";

export default function DashboardPage() {
  const stats = getPipelineStats();
  const protocols = getProtocols();
  const decisionVocab = getVocabulary("screening_decisions");
  const stageVocab = getVocabulary("screening_stages");

  const decisionRows = Object.entries(stats.screeningByDecision)
    .sort((a, b) => b[1] - a[1])
    .map(([decision, value]) => ({
      label: vocabLabel(decisionVocab, decision),
      value,
      tone: decisionTone(decision),
    }));

  const stageRows = Object.entries(stats.screeningByStage)
    .sort((a, b) => b[1] - a[1])
    .map(([stage, value]) => ({
      label: vocabLabel(stageVocab, stage),
      value,
      tone: "accent" as const,
    }));

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Live-Stand der Research-Pipeline — direkt aus research/** und data/** dieses Checkouts gelesen, keine gecachten oder erfundenen Zahlen."
      />

      <div className="space-y-8 p-8">
        <section>
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
            Projektfortschritt
          </h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            <StatCard label="Protokolle" value={stats.protocols} icon={<FileStack size={16} />} />
            <StatCard
              label="Kandidaten"
              value={stats.candidatesTotal}
              hint={`${stats.candidateManifests} Candidate Manifests`}
              icon={<Beaker size={16} />}
            />
            <StatCard
              label="Screening Records"
              value={stats.screeningRecords}
              hint={`${stats.screeningByDecision.pending ?? 0} pending`}
              icon={<ClipboardList size={16} />}
              tone="accent"
            />
            <StatCard label="Studies" value={stats.studies} icon={<Microscope size={16} />} />
            <StatCard label="Claims" value={stats.claims} icon={<Quote size={16} />} />
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
            Pipeline-Status
          </h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            <StatCard label="Search Runs" value={stats.searchRuns} />
            <StatCard label="Result Manifests" value={stats.searchResultManifests} />
            <StatCard label="Extraction Records" value={stats.extractionRecords} />
            <StatCard label="Promotion Records" value={stats.promotionRecords} />
            <StatCard
              label="Evidence (Sources)"
              value={stats.sources}
              icon={<BookMarked size={16} />}
            />
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader
              title="Screening-Entscheidungen"
              subtitle={`${stats.screeningRecords} Screening Records insgesamt, Retatrutide-Pilotprotokoll`}
            />
            <BreakdownBar rows={decisionRows} />
          </Card>

          <Card>
            <CardHeader title="Nach Screening-Stufe" />
            <BreakdownBar rows={stageRows} />
          </Card>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader
              title="Protokolle"
              subtitle="research/protocols/**"
              action={
                <Link
                  href="/retatrutide"
                  className="flex items-center gap-1 text-xs font-medium text-[var(--accent-text)] hover:underline"
                >
                  Details <ArrowRight size={12} />
                </Link>
              }
            />
            <ul className="divide-y" style={{ borderColor: "var(--border)" }}>
              {protocols.map((p) => (
                <li key={p.id} className="flex items-center justify-between py-2.5 text-sm">
                  <div>
                    <div className="font-medium text-[var(--text)]">{p.subject.working_name}</div>
                    <div className="text-xs text-[var(--text-muted)]">{p.id}</div>
                  </div>
                  <Badge tone={statusTone(p.status)}>{p.status}</Badge>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <CardHeader
              title="Knowledge Graph"
              subtitle="build/graph.json — aus data/** exportiert"
              action={
                <span className="flex items-center gap-1 text-xs text-[var(--text-faint)]">
                  <GitBranch size={12} /> read-only Artefakt
                </span>
              }
            />
            <div className="flex items-center gap-8">
              <div>
                <div className="text-2xl font-semibold tabular-nums text-[var(--text)]">
                  {stats.graphNodes}
                </div>
                <div className="text-xs text-[var(--text-muted)]">Knoten</div>
              </div>
              <div>
                <div className="text-2xl font-semibold tabular-nums text-[var(--text)]">
                  {stats.graphEdges}
                </div>
                <div className="text-xs text-[var(--text-muted)]">Kanten</div>
              </div>
            </div>
            <p className="mt-3 text-xs text-[var(--text-faint)]">
              {stats.graphNodes === 0
                ? "0 Knoten, 0 Kanten — data/** enthält noch keine kanonischen Objekte; der Graph wird erst nach Promotion echter Claims/Sources befüllt."
                : "Ausschnitt der aktuellen data/**-Objektbeziehungen."}
            </p>
          </Card>
        </section>
      </div>
    </div>
  );
}

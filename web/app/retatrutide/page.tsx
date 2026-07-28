import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardHeader } from "@/components/ui/Card";
import { Badge, statusTone } from "@/components/ui/Badge";
import { BreakdownBar } from "@/components/ui/BreakdownBar";
import { decisionTone } from "@/components/ui/Badge";
import { getProtocol, getVocabulary, vocabLabel } from "@/lib/data/repository";
import { getProtocolStats } from "@/lib/data/stats";
import { notFound } from "next/navigation";
import { CalendarDays, Users, Database } from "lucide-react";

const PROTOCOL_ID = "research-protocol-retatrutide-v1";

const DATABASE_LABELS: Record<string, string> = {
  pubmed: "PubMed",
  clinicaltrials_gov: "ClinicalTrials.gov",
  fda: "FDA",
  ema: "EMA",
  who_ictrp: "WHO ICTRP",
};

export default function RetatrutidePage() {
  const protocol = getProtocol(PROTOCOL_ID);
  if (!protocol) notFound();

  const stats = getProtocolStats(PROTOCOL_ID);
  const decisionVocab = getVocabulary("screening_decisions");
  const stageVocab = getVocabulary("screening_stages");

  const decisionRows = Object.entries(stats.screeningByDecision)
    .sort((a, b) => b[1] - a[1])
    .map(([decision, value]) => ({
      label: vocabLabel(decisionVocab, decision),
      value,
      tone: decisionTone(decision),
    }));

  const stageOrder = protocol.screening_policy.stages;
  const stageRows = stageOrder
    .map((stage) => ({
      label: vocabLabel(stageVocab, stage),
      value: stats.screeningByStage[stage] ?? 0,
      tone: "accent" as const,
      isDual: protocol.screening_policy.dual_reviewer_stages.includes(stage),
    }))
    .filter((r) => r.value > 0 || true);

  const candidatesTotal = Object.values(stats.candidatesByDatabase).reduce((a, b) => a + b, 0);

  return (
    <div>
      <PageHeader
        title={protocol.subject.working_name}
        description={protocol.title}
        action={<Badge tone={statusTone(protocol.status)}>{protocol.status}</Badge>}
      />

      <div className="space-y-8 p-8">
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Kandidaten" value={candidatesTotal} />
          <StatCard
            label="Screening Records"
            value={Object.values(stats.screeningByDecision).reduce((a, b) => a + b, 0)}
          />
          <StatCard label="Search Runs" value={stats.searchRuns.length} />
          <StatCard
            label="Protokollversion"
            value={`v${protocol.version}`}
            hint={`aktualisiert ${protocol.updated_at}`}
          />
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader
              title="Screening-Statistik (Titel-/Abstract-Stufe folgt)"
              subtitle="Aktueller Stand aller 197 Screening Records"
            />
            <BreakdownBar rows={decisionRows} />
          </Card>
          <Card>
            <CardHeader title="Kandidaten nach Datenbank" />
            <ul className="space-y-3">
              {Object.entries(stats.candidatesByDatabase).map(([db, count]) => (
                <li key={db} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-[var(--text)]">
                    <Database size={14} className="text-[var(--text-faint)]" />
                    {DATABASE_LABELS[db] ?? db}
                  </span>
                  <span className="font-medium tabular-nums text-[var(--text)]">{count}</span>
                </li>
              ))}
            </ul>
          </Card>
        </section>

        <section>
          <Card>
            <CardHeader
              title="Screening-Pipeline (Protokoll-Policy)"
              subtitle="research_protocol.schema.json — screening_policy.stages"
            />
            <div className="flex flex-col gap-2 sm:flex-row">
              {stageRows.map((stage, i) => (
                <div key={stage.label} className="flex flex-1 items-center gap-2">
                  <div
                    className="flex-1 rounded-lg border p-3"
                    style={{ borderColor: "var(--border)" }}
                  >
                    <div className="text-xs font-medium text-[var(--text-muted)]">{stage.label}</div>
                    <div className="mt-1 text-xl font-semibold tabular-nums text-[var(--text)]">
                      {stage.value}
                    </div>
                    {stage.isDual && (
                      <Badge tone="accent" className="mt-2">
                        Zweitreview Pflicht
                      </Badge>
                    )}
                  </div>
                  {i < stageRows.length - 1 && (
                    <span className="hidden text-[var(--text-faint)] sm:block">→</span>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </section>

        <section>
          <Card padded={false}>
            <div className="p-5 pb-0">
              <CardHeader title="Search Runs" subtitle="research/search_runs/**" />
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr
                    className="border-y text-left text-xs uppercase tracking-wide text-[var(--text-muted)]"
                    style={{ borderColor: "var(--border)" }}
                  >
                    <th className="px-5 py-2 font-medium">Datenbank</th>
                    <th className="px-5 py-2 font-medium">Interface</th>
                    <th className="px-5 py-2 font-medium text-right">Treffer</th>
                    <th className="px-5 py-2 font-medium">Ausgeführt am</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.searchRuns.map((run, i) => (
                    <tr
                      key={i}
                      className="border-b last:border-0"
                      style={{ borderColor: "var(--border)" }}
                    >
                      <td className="px-5 py-2.5 font-medium text-[var(--text)]">
                        {DATABASE_LABELS[run.database] ?? run.database}
                      </td>
                      <td className="px-5 py-2.5 text-[var(--text-muted)]">{run.interface}</td>
                      <td className="px-5 py-2.5 text-right tabular-nums text-[var(--text)]">
                        {run.resultCount}
                      </td>
                      <td className="px-5 py-2.5 text-[var(--text-muted)]">
                        <span className="flex items-center gap-1.5">
                          <CalendarDays size={12} />
                          {new Date(run.executedAt).toLocaleString("de-DE")}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader title="Review" />
            <div className="flex items-center gap-2 text-sm text-[var(--text)]">
              <Users size={14} className="text-[var(--text-faint)]" />
              {protocol.review?.reviewers.join(", ") || "—"}
            </div>
            {protocol.review?.approval_decision && (
              <p className="mt-2 text-xs text-[var(--text-muted)]">
                {protocol.review.approval_decision}
              </p>
            )}
          </Card>
          <Card>
            <CardHeader title="Geltungsbereich (Auszug)" />
            <ul className="list-inside list-disc space-y-1 text-sm text-[var(--text)]">
              {protocol.scope.in_scope.slice(0, 6).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </Card>
        </section>
      </div>
    </div>
  );
}

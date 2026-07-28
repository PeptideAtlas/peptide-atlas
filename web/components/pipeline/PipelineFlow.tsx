"use client";

import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/cn";
import type { PipelineStageDef } from "@/lib/data/pipeline";
import { Card } from "@/components/ui/Card";
import { BreakdownBar } from "@/components/ui/BreakdownBar";

const STAGE_LABELS: Record<string, string> = {
  deduplication: "Deduplizierung",
  title_abstract: "Titel/Abstract",
  full_text: "Volltext",
  final: "Abschließend",
};

export function PipelineFlow({ stages }: { stages: PipelineStageDef[] }) {
  const [selected, setSelected] = useState(stages[0]?.id ?? null);
  const active = stages.find((s) => s.id === selected) ?? stages[0];

  return (
    <div className="space-y-6">
      <div className="scrollbar-thin flex items-stretch gap-1 overflow-x-auto pb-2">
        {stages.map((stage, i) => (
          <div key={stage.id} className="flex items-center">
            <button
              onClick={() => setSelected(stage.id)}
              className={cn(
                "flex w-40 shrink-0 flex-col gap-1 rounded-xl border px-4 py-3 text-left transition-all",
                selected === stage.id
                  ? "border-[var(--accent)] bg-[var(--accent-soft)] shadow-sm"
                  : "bg-[var(--surface)] hover:bg-[var(--surface-hover)]"
              )}
              style={{ borderColor: selected === stage.id ? undefined : "var(--border)" }}
            >
              <span
                className={cn(
                  "text-xs font-medium",
                  selected === stage.id ? "text-[var(--accent-text)]" : "text-[var(--text-muted)]"
                )}
              >
                {stage.title}
              </span>
              <span className="text-2xl font-semibold tabular-nums text-[var(--text)]">
                {stage.count}
              </span>
            </button>
            {i < stages.length - 1 && (
              <ArrowRight size={16} className="mx-1 shrink-0 text-[var(--text-faint)]" />
            )}
          </div>
        ))}
      </div>

      {active && (
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-[var(--text)]">{active.title}</h3>
              <code className="mt-1 inline-block text-xs text-[var(--text-faint)]">{active.path}</code>
              <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--text-muted)]">
                {active.description}
              </p>
            </div>
            <div className="shrink-0 text-right">
              <div className="text-3xl font-semibold tabular-nums text-[var(--text)]">
                {active.count}
              </div>
            </div>
          </div>

          {active.breakdown && active.breakdown.some((b) => b.value > 0) && (
            <div className="mt-5 max-w-md">
              <BreakdownBar
                rows={active.breakdown.map((b) => ({
                  label: STAGE_LABELS[b.label] ?? b.label,
                  value: b.value,
                  tone: "accent" as const,
                }))}
              />
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

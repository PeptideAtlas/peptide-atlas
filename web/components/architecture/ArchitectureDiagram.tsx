"use client";

import { useState } from "react";
import { ArrowRight, ArrowDown } from "lucide-react";
import { cn } from "@/lib/cn";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { ArchitectureNode } from "@/lib/data/architecture";
import { PROPOSED_REFERENCES } from "@/lib/data/architecture";

function NodeBox({
  node,
  selected,
  onClick,
}: {
  node: ArchitectureNode;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-44 shrink-0 flex-col gap-1.5 rounded-xl border px-3.5 py-3 text-left transition-all",
        node.status === "proposed" && "border-dashed",
        selected
          ? "border-[var(--accent)] bg-[var(--accent-soft)] shadow-sm"
          : "bg-[var(--surface)] hover:bg-[var(--surface-hover)]"
      )}
      style={{ borderColor: selected ? undefined : "var(--border)" }}
    >
      <span
        className={cn(
          "text-xs font-semibold leading-snug",
          selected ? "text-[var(--accent-text)]" : "text-[var(--text)]"
        )}
      >
        {node.label}
      </span>
      <Badge tone={node.status === "proposed" ? "warning" : "success"} className="w-fit">
        {node.status === "proposed" ? "Vorgeschlagen" : "Implementiert"}
      </Badge>
    </button>
  );
}

export function ArchitectureDiagram({
  research,
  canonical,
  proposed,
}: {
  research: ArchitectureNode[];
  canonical: ArchitectureNode[];
  proposed: ArchitectureNode[];
}) {
  const all = [...research, ...canonical, ...proposed];
  const [selectedId, setSelectedId] = useState(research[0]?.id);
  const selected = all.find((n) => n.id === selectedId);

  return (
    <div className="space-y-8">
      <div>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
          research/** — Provenienz-Pipeline
        </h3>
        <div className="scrollbar-thin flex items-center gap-1 overflow-x-auto pb-2">
          {research.map((node, i) => (
            <div key={node.id} className="flex items-center">
              <NodeBox
                node={node}
                selected={selectedId === node.id}
                onClick={() => setSelectedId(node.id)}
              />
              {i < research.length - 1 && (
                <ArrowRight size={16} className="mx-1 shrink-0 text-[var(--text-faint)]" />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-center">
        <ArrowDown size={18} className="text-[var(--text-faint)]" />
      </div>

      <div>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
          data/** — kanonisches Wissensmodell
        </h3>
        <div className="flex flex-wrap items-center gap-3">
          {canonical.map((node) => (
            <NodeBox
              key={node.id}
              node={node}
              selected={selectedId === node.id}
              onClick={() => setSelectedId(node.id)}
            />
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
          Vorgeschlagen, noch nicht implementiert (PR #8 / ADR-0059)
        </h3>
        <div className="flex flex-wrap items-center gap-3">
          {proposed.map((node) => (
            <NodeBox
              key={node.id}
              node={node}
              selected={selectedId === node.id}
              onClick={() => setSelectedId(node.id)}
            />
          ))}
        </div>
        {selected?.status === "proposed" && (
          <ul className="mt-3 space-y-1 text-xs text-[var(--text-faint)]">
            {PROPOSED_REFERENCES.map((ref) => (
              <li key={ref.from} className="font-mono">
                {ref.from} → {selected.label}
              </li>
            ))}
          </ul>
        )}
      </div>

      {selected && (
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-[var(--text)]">{selected.label}</h3>
                <Badge tone={selected.status === "proposed" ? "warning" : "success"}>
                  {selected.status === "proposed" ? "Vorgeschlagen" : "Implementiert"}
                </Badge>
              </div>
              {selected.schema && (
                <code className="mt-1 inline-block text-xs text-[var(--text-faint)]">
                  {selected.schema}
                </code>
              )}
              <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--text-muted)]">
                {selected.description}
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-1.5">
            {selected.fields.map((f) => (
              <code
                key={f}
                className="rounded-md px-2 py-1 text-xs"
                style={{ background: "var(--neutral-soft)" }}
              >
                {f}
              </code>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

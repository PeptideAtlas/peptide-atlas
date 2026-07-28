import { cn } from "@/lib/cn";
import type { ReactNode } from "react";
import { Card } from "./Card";

export function StatCard({
  label,
  value,
  hint,
  icon,
  tone = "neutral",
}: {
  label: string;
  value: string | number;
  hint?: string;
  icon?: ReactNode;
  tone?: "neutral" | "accent" | "warning" | "success";
}) {
  const toneClasses: Record<string, string> = {
    neutral: "text-[var(--text)]",
    accent: "text-[var(--accent-text)]",
    warning: "text-[var(--warning)]",
    success: "text-[var(--success)]",
  };

  return (
    <Card>
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
          {label}
        </span>
        {icon && (
          <span className="text-[var(--text-faint)]" aria-hidden>
            {icon}
          </span>
        )}
      </div>
      <div className={cn("mt-2 text-3xl font-semibold tabular-nums", toneClasses[tone])}>
        {value}
      </div>
      {hint && <p className="mt-1 text-xs text-[var(--text-muted)]">{hint}</p>}
    </Card>
  );
}

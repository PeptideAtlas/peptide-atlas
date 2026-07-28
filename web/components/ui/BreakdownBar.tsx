import { cn } from "@/lib/cn";

export interface BreakdownRow {
  label: string;
  value: number;
  tone?: "neutral" | "accent" | "success" | "warning" | "danger";
}

const TONE_BG: Record<string, string> = {
  neutral: "var(--text-faint)",
  accent: "var(--accent)",
  success: "var(--success)",
  warning: "var(--warning)",
  danger: "var(--danger)",
};

/** Horizontal breakdown bars -- e.g. screening decisions or stages by count. */
export function BreakdownBar({ rows }: { rows: BreakdownRow[] }) {
  const total = rows.reduce((sum, r) => sum + r.value, 0);

  if (total === 0) {
    return <p className="text-sm text-[var(--text-faint)]">Keine Datensätze.</p>;
  }

  return (
    <div className="space-y-3">
      {rows.map((row) => {
        const pct = total > 0 ? (row.value / total) * 100 : 0;
        return (
          <div key={row.label}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="font-medium text-[var(--text)]">{row.label}</span>
              <span className="tabular-nums text-[var(--text-muted)]">
                {row.value} · {pct.toFixed(0)}%
              </span>
            </div>
            <div
              className={cn("h-1.5 w-full overflow-hidden rounded-full")}
              style={{ background: "var(--neutral-soft)" }}
            >
              <div
                className="h-full rounded-full transition-all"
                style={{ width: `${pct}%`, background: TONE_BG[row.tone ?? "neutral"] }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

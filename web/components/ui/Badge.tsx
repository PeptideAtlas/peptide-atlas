import { cn } from "@/lib/cn";

export type BadgeTone = "neutral" | "accent" | "success" | "warning" | "danger";

const TONE_STYLES: Record<BadgeTone, string> = {
  neutral: "bg-[var(--neutral-soft)] text-[var(--text-muted)]",
  accent: "bg-[var(--accent-soft)] text-[var(--accent-text)]",
  success: "bg-[var(--success-soft)] text-[var(--success)]",
  warning: "bg-[var(--warning-soft)] text-[var(--warning)]",
  danger: "bg-[var(--danger-soft)] text-[var(--danger)]",
};

export function Badge({
  children,
  tone = "neutral",
  className,
}: {
  children: React.ReactNode;
  tone?: BadgeTone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium whitespace-nowrap",
        TONE_STYLES[tone],
        className
      )}
    >
      {children}
    </span>
  );
}

/** Screening decision -> badge tone, consistent across every page. */
export function decisionTone(decision: string): BadgeTone {
  switch (decision) {
    case "include":
      return "success";
    case "exclude":
      return "danger";
    case "duplicate":
      return "warning";
    case "uncertain":
      return "warning";
    case "awaiting_full_text":
      return "accent";
    case "pending":
    default:
      return "neutral";
  }
}

export function statusTone(status: string): BadgeTone {
  switch (status) {
    case "approved":
    case "complete":
    case "fetched":
    case "executed":
      return "success";
    case "draft":
    case "not_fetched":
      return "neutral";
    case "amended":
    case "partial":
      return "warning";
    case "retired":
    case "not_found":
    case "fetch_error":
      return "danger";
    default:
      return "accent";
  }
}

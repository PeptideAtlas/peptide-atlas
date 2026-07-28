import type { ReactNode } from "react";

export function EmptyState({
  icon,
  title,
  description,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      {icon && <div className="text-[var(--text-faint)]">{icon}</div>}
      <p className="text-sm font-medium text-[var(--text-muted)]">{title}</p>
      {description && (
        <p className="max-w-sm text-xs text-[var(--text-faint)]">{description}</p>
      )}
    </div>
  );
}

import type { ReactNode } from "react";

export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div
      className="flex flex-wrap items-start justify-between gap-4 border-b px-8 py-6"
      style={{ borderColor: "var(--border)" }}
    >
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-[var(--text)]">{title}</h1>
        {description && (
          <p className="mt-1 max-w-2xl text-sm text-[var(--text-muted)]">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}

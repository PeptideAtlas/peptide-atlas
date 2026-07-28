"use client";

import { useMemo, useState } from "react";
import { Search, X, ExternalLink } from "lucide-react";
import { Badge, decisionTone } from "@/components/ui/Badge";
import { cn } from "@/lib/cn";
import type { CandidateExplorerRow } from "@/lib/data/stats";

const DATABASE_LABELS: Record<string, string> = {
  pubmed: "PubMed",
  clinicaltrials_gov: "ClinicalTrials.gov",
};

const DECISION_LABELS: Record<string, string> = {
  pending: "Ausstehend",
  include: "Eingeschlossen",
  exclude: "Ausgeschlossen",
  duplicate: "Duplikat",
  awaiting_full_text: "Volltext ausstehend",
  uncertain: "Unklar",
};

export function CandidateExplorer({ rows }: { rows: CandidateExplorerRow[] }) {
  const [query, setQuery] = useState("");
  const [database, setDatabase] = useState<string | null>(null);
  const [decision, setDecision] = useState<string | null>(null);
  const [selected, setSelected] = useState<CandidateExplorerRow | null>(null);

  const databases = useMemo(() => Array.from(new Set(rows.map((r) => r.database))), [rows]);
  const decisions = useMemo(() => Array.from(new Set(rows.map((r) => r.decision))), [rows]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((r) => {
      if (database && r.database !== database) return false;
      if (decision && r.decision !== decision) return false;
      if (!q) return true;
      return (
        r.title.toLowerCase().includes(q) ||
        r.identifierValue.toLowerCase().includes(q) ||
        (r.doi ?? "").toLowerCase().includes(q)
      );
    });
  }, [rows, query, database, decision]);

  return (
    <div className="flex h-full">
      <div className="flex min-w-0 flex-1 flex-col">
        <div
          className="flex flex-wrap items-center gap-3 border-b px-8 py-4"
          style={{ borderColor: "var(--border)" }}
        >
          <div className="relative min-w-[240px] flex-1">
            <Search
              size={14}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-faint)]"
            />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Titel, PMID, NCT-ID oder DOI suchen…"
              className="w-full rounded-lg border bg-[var(--surface)] py-2 pl-9 pr-3 text-sm outline-none placeholder:text-[var(--text-faint)] focus:border-[var(--accent)]"
              style={{ borderColor: "var(--border)" }}
            />
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {databases.map((db) => (
              <FilterChip
                key={db}
                active={database === db}
                onClick={() => setDatabase(database === db ? null : db)}
              >
                {DATABASE_LABELS[db] ?? db}
              </FilterChip>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {decisions.map((d) => (
              <FilterChip
                key={d}
                active={decision === d}
                onClick={() => setDecision(decision === d ? null : d)}
              >
                {DECISION_LABELS[d] ?? d}
              </FilterChip>
            ))}
          </div>

          <span className="ml-auto text-xs tabular-nums text-[var(--text-muted)]">
            {filtered.length} / {rows.length}
          </span>
        </div>

        <div className="scrollbar-thin flex-1 overflow-auto">
          <table className="w-full min-w-[640px] text-sm">
            <thead className="sticky top-0 z-10 bg-[var(--bg)]">
              <tr
                className="border-b text-left text-xs uppercase tracking-wide text-[var(--text-muted)]"
                style={{ borderColor: "var(--border)" }}
              >
                <th className="px-8 py-2.5 font-medium">Titel</th>
                <th className="px-3 py-2.5 font-medium">Quelle</th>
                <th className="px-3 py-2.5 font-medium">Identifier</th>
                <th className="px-3 py-2.5 font-medium">Entscheidung</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr
                  key={row.candidateId}
                  onClick={() => setSelected(row)}
                  className={cn(
                    "cursor-pointer border-b transition-colors last:border-0 hover:bg-[var(--surface-hover)]",
                    selected?.candidateId === row.candidateId && "bg-[var(--accent-soft)]"
                  )}
                  style={{ borderColor: "var(--border)" }}
                >
                  <td className="max-w-md px-8 py-2.5">
                    <div className="truncate font-medium text-[var(--text)]">{row.title}</div>
                    {row.subtitle && (
                      <div className="truncate text-xs text-[var(--text-muted)]">{row.subtitle}</div>
                    )}
                  </td>
                  <td className="px-3 py-2.5 text-[var(--text-muted)]">
                    {DATABASE_LABELS[row.database] ?? row.database}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-xs text-[var(--text-muted)]">
                    {row.identifierValue}
                  </td>
                  <td className="px-3 py-2.5">
                    <Badge tone={decisionTone(row.decision)}>
                      {DECISION_LABELS[row.decision] ?? row.decision}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <p className="p-8 text-center text-sm text-[var(--text-faint)]">
              Keine Kandidaten für diese Filter.
            </p>
          )}
        </div>
      </div>

      {selected && (
        <CandidateDetailPanel row={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-md border px-2.5 py-1 text-xs font-medium transition-colors",
        active
          ? "border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent-text)]"
          : "text-[var(--text-muted)] hover:bg-[var(--surface-hover)]"
      )}
      style={{ borderColor: active ? undefined : "var(--border)" }}
    >
      {children}
    </button>
  );
}

function CandidateDetailPanel({
  row,
  onClose,
}: {
  row: CandidateExplorerRow;
  onClose: () => void;
}) {
  const externalUrl =
    row.database === "pubmed"
      ? `https://pubmed.ncbi.nlm.nih.gov/${row.identifierValue}/`
      : row.database === "clinicaltrials_gov"
        ? `https://clinicaltrials.gov/study/${row.identifierValue}`
        : null;

  return (
    <div
      className="fixed inset-0 z-40 overflow-y-auto bg-[var(--surface)] p-6 md:static md:z-auto md:w-96 md:shrink-0 md:border-l"
      style={{ borderColor: "var(--border)" }}
    >
      <div className="mb-4 flex items-start justify-between gap-2">
        <Badge tone={decisionTone(row.decision)}>{DECISION_LABELS[row.decision] ?? row.decision}</Badge>
        <button
          onClick={onClose}
          className="text-[var(--text-faint)] hover:text-[var(--text)]"
          aria-label="Schließen"
        >
          <X size={16} />
        </button>
      </div>

      <h2 className="text-base font-semibold leading-snug text-[var(--text)]">{row.title}</h2>
      {row.subtitle && <p className="mt-1 text-sm text-[var(--text-muted)]">{row.subtitle}</p>}

      <dl className="mt-5 space-y-3 text-sm">
        <Field label="Kandidaten-ID" value={row.candidateId} mono />
        <Field label="Datenbank" value={DATABASE_LABELS[row.database] ?? row.database} />
        <Field
          label={row.identifierNamespace.toUpperCase()}
          value={row.identifierValue}
          mono
        />
        {row.doi && <Field label="DOI" value={row.doi} mono />}
        <Field label="Metadaten-Status" value={row.metadataStatus} />
        <Field label="Screening-Stufe" value={row.decisionStage} />
        <Field label="Candidate Manifest" value={row.manifestId} mono small />
        {row.screeningRecordId && (
          <Field label="Screening Record" value={row.screeningRecordId} mono small />
        )}
      </dl>

      {externalUrl && (
        <a
          href={externalUrl}
          target="_blank"
          rel="noreferrer"
          className="mt-6 flex items-center gap-1.5 text-sm font-medium text-[var(--accent-text)] hover:underline"
        >
          Auf {DATABASE_LABELS[row.database]} öffnen <ExternalLink size={13} />
        </a>
      )}
    </div>
  );
}

function Field({
  label,
  value,
  mono,
  small,
}: {
  label: string;
  value: string;
  mono?: boolean;
  small?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-[var(--text-faint)]">
        {label}
      </dt>
      <dd
        className={cn(
          "mt-0.5 break-words text-[var(--text)]",
          mono && "font-mono",
          small ? "text-xs" : "text-sm"
        )}
      >
        {value}
      </dd>
    </div>
  );
}

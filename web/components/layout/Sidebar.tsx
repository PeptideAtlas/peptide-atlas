"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FlaskConical,
  ListFilter,
  Workflow,
  Network,
  ExternalLink,
  Menu,
  X,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { ThemeToggle } from "./ThemeToggle";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/retatrutide", label: "Retatrutide", icon: FlaskConical },
  { href: "/candidates", label: "Candidate Explorer", icon: ListFilter },
  { href: "/pipeline", label: "Research Pipeline", icon: Workflow },
  { href: "/architecture", label: "Architektur", icon: Network },
];

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div
        className="flex h-7 w-7 items-center justify-center rounded-lg text-sm font-bold text-white"
        style={{ background: "var(--accent)" }}
      >
        P
      </div>
      <div>
        <div className="text-sm font-semibold leading-none text-[var(--text)]">Peptide Atlas</div>
        <div className="mt-0.5 text-[10px] font-medium uppercase tracking-wider text-[var(--text-faint)]">
          Developer Preview
        </div>
      </div>
    </div>
  );
}

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  return (
    <nav className="flex-1 space-y-0.5 px-3">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-[var(--accent-soft)] text-[var(--accent-text)]"
                : "text-[var(--text-muted)] hover:bg-[var(--surface-hover)] hover:text-[var(--text)]"
            )}
          >
            <Icon size={16} strokeWidth={2} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

function Footer() {
  return (
    <div
      className="flex items-center justify-between gap-2 border-t px-4 py-4"
      style={{ borderColor: "var(--border)" }}
    >
      <a
        href="https://github.com/PeptideAtlas/peptide-atlas"
        target="_blank"
        rel="noreferrer"
        className="flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text)]"
      >
        <ExternalLink size={13} />
        Repo
      </a>
      <ThemeToggle />
    </div>
  );
}

export function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile top bar (below md) */}
      <div
        className="fixed inset-x-0 top-0 z-30 flex h-14 items-center justify-between border-b bg-[var(--surface)] px-4 md:hidden"
        style={{ borderColor: "var(--border)" }}
      >
        <Logo />
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          aria-label="Menü öffnen"
          className="flex h-8 w-8 items-center justify-center rounded-lg border text-[var(--text-muted)]"
          style={{ borderColor: "var(--border)" }}
        >
          <Menu size={16} />
        </button>
      </div>

      {/* Mobile drawer backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden
        />
      )}

      {/* Sidebar: static on md+, sliding drawer below md */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex h-full w-64 shrink-0 flex-col border-r bg-[var(--surface)] transition-transform duration-200 md:static md:z-auto md:w-60 md:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
        style={{ borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between px-5 py-5">
          <Logo />
          <button
            type="button"
            onClick={() => setMobileOpen(false)}
            aria-label="Menü schließen"
            className="text-[var(--text-faint)] hover:text-[var(--text)] md:hidden"
          >
            <X size={18} />
          </button>
        </div>

        <NavLinks onNavigate={() => setMobileOpen(false)} />
        <Footer />
      </aside>
    </>
  );
}

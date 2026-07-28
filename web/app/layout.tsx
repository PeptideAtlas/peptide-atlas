import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Sidebar } from "@/components/layout/Sidebar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Peptide Atlas — Developer Preview",
  description:
    "Lokale Developer Preview auf Basis der echten research/**-Projektdaten von Peptide Atlas.",
};

const THEME_SCRIPT = `
(function () {
  try {
    var stored = localStorage.getItem('pa-theme');
    var dark = stored ? stored === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (dark) document.documentElement.classList.add('dark');
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="de"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="flex h-full min-h-screen bg-[var(--bg)] text-[var(--text)]">
        <Sidebar />
        <main className="min-w-0 flex-1 overflow-y-auto pt-14 md:pt-0">{children}</main>
      </body>
    </html>
  );
}

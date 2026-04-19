import { useEffect, useState } from "react";
import { Link, NavLink, Route, Routes } from "react-router-dom";
import { loadCompanies } from "./lib/data";
import { Home } from "./routes/Home";
import { Company } from "./routes/Company";
import { Change } from "./routes/Change";
import { About } from "./routes/About";

function useLastUpdated(): string | null {
  const [value, setValue] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    loadCompanies()
      .then((file) => {
        if (!cancelled) setValue(file.generated_at);
      })
      .catch(() => {
        // Swallow: the footer is purely informational.
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return value;
}

function formatLastUpdated(iso: string | null): string {
  if (!iso) return "unknown";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toISOString().slice(0, 16).replace("T", " ") + " UTC";
}

const navItemClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-1.5 text-sm font-medium transition ${
    isActive
      ? "bg-slate-900 text-white"
      : "text-slate-600 hover:bg-slate-200 hover:text-slate-900"
  }`;

export function App() {
  const lastUpdated = useLastUpdated();
  return (
    <div className="mx-auto flex min-h-full max-w-5xl flex-col px-4 py-6">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <Link to="/" className="flex items-center gap-2">
          <svg
            width="28"
            height="28"
            viewBox="0 0 64 64"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden
          >
            <rect width="64" height="64" rx="12" fill="#0f172a" />
            <path
              d="M16 42 L32 18 L48 42 Z"
              fill="#38bdf8"
              stroke="#e2e8f0"
              strokeWidth={2}
            />
            <circle cx="32" cy="36" r="4" fill="#0f172a" />
          </svg>
          <span className="text-lg font-semibold text-slate-900">
            AI Privacy Tracker
          </span>
        </Link>
        <nav className="flex gap-1">
          <NavLink to="/" end className={navItemClass}>
            Timeline
          </NavLink>
          <NavLink to="/about" className={navItemClass}>
            About
          </NavLink>
        </nav>
      </header>

      <main className="flex-1 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/companies/:slug" element={<Company />} />
          <Route path="/changes/:id" element={<Change />} />
          <Route path="/about" element={<About />} />
          <Route
            path="*"
            element={
              <div className="rounded-md border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
                Not found. <Link to="/" className="underline">Back to timeline</Link>.
              </div>
            }
          />
        </Routes>
      </main>

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 py-4 text-xs text-slate-500">
        <span>
          Heuristic, not legal advice. Source code on{" "}
          <a
            href="https://github.com/masonlavinder/ai-tracking"
            className="underline"
            target="_blank"
            rel="noreferrer noopener"
          >
            GitHub
          </a>
          .
        </span>
        <span>
          Last updated{" "}
          <time dateTime={lastUpdated ?? undefined} className="font-mono">
            {formatLastUpdated(lastUpdated)}
          </time>
        </span>
      </footer>
    </div>
  );
}

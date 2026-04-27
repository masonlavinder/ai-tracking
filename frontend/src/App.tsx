import { useEffect, useState } from "react";
import { Link, NavLink, Route, Routes } from "react-router-dom";
import { loadCompanies } from "@api";
import Logo from "@components/Logo";
import { Home } from "@pages/Home/Home";
import { TimelinePage } from "@pages/Timeline/Timeline";
import { Company } from "@pages/Company/Company";
import { Change } from "@pages/Change/Change";
import { About } from "@pages/About/About";
import { Learn } from "@pages/Learn/Learn";
import { OptOut } from "@pages/OptOut/OptOut";
import { NotFound } from "@pages/NotFound/NotFound";

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

export const App = () => {
  const lastUpdated = useLastUpdated();
  return (
    <div className="mx-auto flex min-h-full max-w-5xl flex-col px-4 py-6">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <Link to="/" className="flex items-center gap-2">
          <Logo size="sm" />
          <span className="text-lg font-semibold text-slate-900">
            Watch the Diff
          </span>
        </Link>
        <nav className="flex gap-1">
          <NavLink to="/" end className={navItemClass}>
            Home
          </NavLink>
          <NavLink to="/timeline" className={navItemClass}>
            Timeline
          </NavLink>
          <NavLink to="/learn" className={navItemClass}>
            Learn
          </NavLink>
          <NavLink to="/about" className={navItemClass}>
            About
          </NavLink>
        </nav>
      </header>

      <main className="flex-1 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/companies/:slug" element={<Company />} />
          <Route path="/changes/:id" element={<Change />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/opt-out" element={<OptOut />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
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

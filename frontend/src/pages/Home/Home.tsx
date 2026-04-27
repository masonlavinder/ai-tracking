// Home: hero + live stats + how-it-works blurb + companies grid.
// The full chronological change list lives on /timeline.

import { useEffect, useState } from "react";
import { loadCompanies, loadTimeline } from "@api";
import type { CompanySummary, TimelineFile } from "@types";
import { formatLocalDate } from "../../utils/date";
import { Hero } from "./components/Hero";
import { StatsBar } from "./components/StatsBar";
import { HowItWorks } from "./components/HowItWorks";
import { CompaniesSection } from "./components/CompaniesSection";
import { TimelineCTA } from "./components/TimelineCTA";

function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return formatLocalDate(d);
}

export const Home = () => {
  const [timeline, setTimeline] = useState<TimelineFile | null>(null);
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([loadTimeline(), loadCompanies()])
      .then(([tl, co]) => {
        if (cancelled) return;
        setTimeline(tl);
        setCompanies(co.companies);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="rounded-md border border-rose-300 bg-rose-50 p-4 text-sm text-rose-900">
        Failed to load data: {error}
      </div>
    );
  }

  const totalChanges = timeline?.changes.length ?? 0;
  const lastUpdated = formatDate(timeline?.generated_at);
  const threshold = timeline ? timeline.threshold : 4;

  return (
    <div className="flex flex-col gap-8">
      <Hero />
      <StatsBar
        companyCount={companies.length}
        totalChanges={totalChanges}
        lastUpdated={lastUpdated}
      />
      <HowItWorks threshold={threshold} />
      <CompaniesSection companies={companies} />
      <TimelineCTA />
    </div>
  );
}

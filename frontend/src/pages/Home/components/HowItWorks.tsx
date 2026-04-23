import { Link } from "react-router-dom";

export function HowItWorks({ threshold }: { threshold: number }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 text-sm leading-relaxed text-slate-700">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        How it works
      </h2>
      <p className="mt-2">
        Every day we scrape the published privacy and AI-data policies of
        each tracked company. When the text changes, a rule-based
        classifier compares paragraphs, tags the topics involved, and
        assigns a significance score. The{" "}
        <Link
          to="/timeline"
          className="font-medium text-brand-700 hover:text-brand-800 underline"
        >
          timeline
        </Link>{" "}
        lists every change rated ≥ {threshold}.{" "}
        <Link
          to="/about"
          className="font-medium text-brand-700 hover:text-brand-800 underline"
        >
          Read the methodology
        </Link>{" "}
        or subscribe to the{" "}
        <a
          href="feed.xml"
          className="font-medium text-brand-700 hover:text-brand-800 underline"
        >
          RSS feed
        </a>
        .
      </p>
    </section>
  );
}

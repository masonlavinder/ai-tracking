import { useMemo, useState } from "react";
import Logo from "@components/Logo";
import { articleMatches, termMatches } from "./filter";

const ARTICLE_PREVIEW_LIMIT = 3;

interface Term {
  term: string;
  definition: string;
}

interface Section {
  title: string;
  terms: Term[];
}

interface Article {
  category: string;
  title: string;
  source: string;
  summary: string;
  why?: string;
  href: string;
}

const articles: Article[] = [
  {
    category: "Tracking",
    title: "Cover Your Tracks: how trackers see your browser",
    source: "EFF",
    summary:
      "How third-party cookies, browser fingerprinting, and ad-tech identifiers combine to follow you across the web.",
    why: "Includes a hands-on tool that shows what your browser is leaking right now.",
    href: "https://coveryourtracks.eff.org/learn",
  },
  {
    category: "Tracking",
    title: "Is my phone listening to me?",
    source: "EFF",
    summary:
      "Why ads can feel like they're reading your mind even though your microphone almost certainly isn't being recorded — and what's actually happening behind the scenes.",
    why: "Addresses the privacy question regular people ask most. The real answer is creepier than “they're listening.”",
    href: "https://www.eff.org/deeplinks/2024/10/my-phone-listening-me",
  },
  {
    category: "AI & training",
    title: "How apps like ChatGPT do (and don't) protect your user data",
    source: "Mozilla Foundation",
    summary:
      "What major AI chatbots actually collect, how they use it for training, and where the disclosures fall short.",
    why: "Names specific companies and points at the gap between policy language and practice.",
    href: "https://foundation.mozilla.org/en/blog/ai-privacy-data-chatgpt/",
  },
  {
    category: "Your rights",
    title: "Ten questions and answers about the California Consumer Privacy Act",
    source: "EFF",
    summary:
      "What CCPA actually gives you the right to do — access, deletion, opt-out of sale — and where the law falls short.",
    why: "Plain-language Q&A format. The most cited US privacy law, explained without legalese.",
    href: "https://www.eff.org/deeplinks/2020/01/ten-questions-and-answers-about-california-consumer-privacy-act",
  },
];

const sections: Section[] = [
  {
    title: "Tracking & advertising",
    terms: [
      {
        term: "Cookie",
        definition:
          "A small piece of data a website saves in your browser. First-party cookies — from the site you're actually on — keep you logged in or remember preferences. The privacy concerns center on cookies that follow you across sites.",
      },
      {
        term: "Third-party cookie",
        definition:
          "A cookie placed by a domain other than the site you're visiting, usually an ad network or analytics company. Lets companies you've never heard of build a profile of every site you visit. Most major browsers now block these by default, which is why tracking has shifted to fingerprinting and server-side methods.",
      },
      {
        term: "Tracking pixel",
        definition:
          "A 1×1 invisible image embedded in a page or email that pings a tracker's server when loaded. Reveals that you opened the page or email, your IP address, and enough metadata to identify you. Common in marketing emails.",
      },
      {
        term: "Browser fingerprinting",
        definition:
          "Identifying a browser by its combination of attributes — fonts installed, screen size, time zone, GPU details, and more. Unlike cookies, you can't clear it, and it works in private browsing. Increasingly used as a cookie replacement.",
      },
      {
        term: "Cross-site tracking",
        definition:
          "Linking your activity across multiple websites into a single profile. Built on third-party cookies, fingerprinting, or shared login IDs. The reason an ad for something you looked at on one site follows you everywhere else.",
      },
      {
        term: "Behavioral / targeted advertising",
        definition:
          "Ads chosen based on inferred interests, demographics, or recent activity, rather than just the page you're on. Requires cross-site tracking to work. The reason “personalized ads” exists as a setting at all.",
      },
    ],
  },
  {
    title: "Your data",
    terms: [
      {
        term: "Personal information (PII)",
        definition:
          "Any data that identifies you, alone or combined with other data. The obvious examples: name, email, phone, address. Less obvious but still PII: device IDs, precise location, IP address, cookie identifiers, account numbers.",
      },
      {
        term: "Sensitive personal information",
        definition:
          "A subset of personal information that gets stronger legal protection: health, biometric, race, religion, sexual orientation, precise location, financial details, government IDs. Most privacy laws require explicit opt-in consent before these can be used.",
      },
      {
        term: "First-party vs. third-party data",
        definition:
          "First-party data is what a company collects from you directly — your account, your activity on their site. Third-party data is what they buy or receive from someone else. Privacy policies often draw a sharp line between these, but what counts as “first-party” depends entirely on whose policy you're reading.",
      },
      {
        term: "Anonymization vs. pseudonymization",
        definition:
          "Anonymized data has identifiers stripped and supposedly cannot be linked back to you. Pseudonymized data has direct identifiers replaced with a token that the company can still reverse. Companies often use these terms loosely; research has repeatedly shown that “anonymized” datasets can be re-identified by combining them with other public data.",
      },
      {
        term: "Data broker",
        definition:
          "A company whose business is buying, aggregating, and selling personal data. Most people have never heard of the brokers holding detailed dossiers on them. A handful of US states (California, Vermont, Texas, Oregon) require brokers to register; most don't.",
      },
      {
        term: "Data retention",
        definition:
          "How long a company keeps your data. “We retain data as long as necessary to provide the service” is the standard vague phrasing. Meaningful retention policies state actual time limits and what triggers deletion.",
      },
    ],
  },
  {
    title: "AI & training",
    terms: [
      {
        term: "Training data",
        definition:
          "The text, images, code, or other content used to teach an AI model. When a privacy policy says “we may use your information to improve our services,” AI training is often what they mean. The line between “improving the service” and “training a model on your messages” is rarely defined precisely.",
      },
      {
        term: "Opt-out (of AI training)",
        definition:
          "A setting that prevents your content — chats, prompts, uploaded files — from being used to train future models. Usually opt-out by default rather than opt-in, and often buried several menus deep. Some companies don't offer it at all for free-tier users.",
      },
      {
        term: "Inference",
        definition:
          "When an AI model generates an output — the run-time use of the model on your input. This is distinct from training. Many companies promise they don't train on your data while still processing it through their models, and those are very different commitments.",
      },
      {
        term: "Data scraping",
        definition:
          "Automated collection of content from public web pages. Most foundation models are trained on data scraped from the open web. The legal status is unsettled: courts may rule a scrape lawful even when the scraped site's terms of service forbid it.",
      },
    ],
  },
  {
    title: "Your rights",
    terms: [
      {
        term: "Consent (opt-in vs. opt-out)",
        definition:
          "Opt-in means a company can't do the thing until you actively agree — the standard under GDPR for many uses. Opt-out means they can do it by default until you tell them to stop — the standard in most US contexts. The difference is enormous in practice.",
      },
      {
        term: "Right to deletion",
        definition:
          "The right to ask a company to delete your data. Codified in GDPR (Article 17, “right to erasure”) and in CCPA. Companies must honor verified requests within set timeframes — but exceptions are broad, and “delete” doesn't necessarily mean removing your data from models that have already been trained on it.",
      },
      {
        term: "GDPR",
        definition:
          "The EU's General Data Protection Regulation, in effect since 2018. Sets a global high-water mark for privacy: requires a lawful basis for processing, explicit consent for sensitive uses, breach notification, and grants EU residents rights to access, correct, and delete their data. Fines can reach 4% of a company's global revenue.",
      },
      {
        term: "CCPA / CPRA",
        definition:
          "California's Consumer Privacy Act (2020) and its expansion, the Privacy Rights Act (2023). Gives California residents the right to know what data is collected, request deletion, and opt out of sale. Weaker than GDPR but the most-cited US privacy law because of California's market size.",
      },
    ],
  },
];

function ArticleCard({ article }: { article: Article }) {
  return (
    <a
      href={article.href}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex h-full flex-col rounded-xl border border-slate-200 bg-white p-4 transition hover:border-brand-300 hover:shadow-sm"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-brand-700">
          {article.category}
        </span>
        <span className="text-[11px] font-medium text-slate-500">
          {article.source} ↗
        </span>
      </div>
      <h3 className="mt-2 text-base font-semibold leading-snug text-slate-900 group-hover:text-brand-800">
        {article.title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">
        {article.summary}
      </p>
      {article.why && (
        <p className="mt-3 border-t border-slate-100 pt-3 text-xs italic text-slate-500">
          {article.why}
        </p>
      )}
    </a>
  );
}

export function Learn() {
  const [query, setQuery] = useState("");
  const [articlesExpanded, setArticlesExpanded] = useState(false);

  const isSearching = query.trim().length > 0;

  const filteredArticles = useMemo(
    () => articles.filter((a) => articleMatches(a, query)),
    [query],
  );

  const visibleArticles =
    isSearching || articlesExpanded
      ? filteredArticles
      : filteredArticles.slice(0, ARTICLE_PREVIEW_LIMIT);
  const hasMoreArticles =
    !isSearching &&
    !articlesExpanded &&
    filteredArticles.length > ARTICLE_PREVIEW_LIMIT;

  const filteredSections = useMemo(() => {
    if (!isSearching) return sections;
    return sections
      .map((section) => ({
        ...section,
        terms: section.terms.filter((t) => termMatches(t, query)),
      }))
      .filter((section) => section.terms.length > 0);
  }, [query, isSearching]);

  return (
    <div className="flex flex-col gap-8">
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-gradient-to-br from-brand-100 via-white to-white px-6 py-8 sm:px-10 sm:py-10">
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-6">
          <Logo size="lg" className="shrink-0 drop-shadow-sm" />
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
              Learn
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-700">
              A plain-language reference for the terms that turn up most
              often in privacy policies, AI data-use disclosures, and the
              change diffs on this site.
            </p>
          </div>
        </div>
      </section>

      <div className="relative">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search articles and terms..."
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 pr-8 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
          aria-label="Search articles and glossary terms"
        />
        {query && (
          <button
            type="button"
            onClick={() => setQuery("")}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-700"
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      <section>
        <div className="flex items-baseline justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Deep dives</h2>
          <span className="text-xs text-slate-500">
            Curated explainers from privacy advocates and researchers
          </span>
        </div>
        {visibleArticles.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">
            No articles match “{query}”.
          </p>
        ) : (
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {visibleArticles.map((article) => (
              <ArticleCard key={article.title} article={article} />
            ))}
          </div>
        )}
        {hasMoreArticles && (
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setArticlesExpanded(true)}
              className="text-xs font-medium text-brand-700 hover:text-brand-800"
            >
              Show all {filteredArticles.length} articles
            </button>
          </div>
        )}
        {articlesExpanded && !isSearching && (
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setArticlesExpanded(false)}
              className="text-xs font-medium text-brand-700 hover:text-brand-800"
            >
              Show fewer
            </button>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold text-slate-900">Glossary</h2>

        {filteredSections.length === 0 ? (
          <p className="mt-6 text-sm text-slate-500">
            No terms match “{query}”.
          </p>
        ) : (
          <div className="flex flex-col gap-2">
            {filteredSections.map((section) => (
              <section key={section.title}>
                <h3 className="mt-4 text-base font-semibold text-slate-900">
                  {section.title}
                </h3>
                <dl className="mt-3 space-y-4">
                  {section.terms.map(({ term, definition }) => (
                    <div key={term}>
                      <dt className="text-sm font-semibold text-slate-900">
                        {term}
                      </dt>
                      <dd className="mt-1 text-sm leading-relaxed text-slate-700">
                        {definition}
                      </dd>
                    </div>
                  ))}
                </dl>
              </section>
            ))}
          </div>
        )}

        <p className="mt-8 text-xs italic text-slate-500">
          A reference, not legal advice. Definitions here are simplified for
          clarity — consult original policies and qualified counsel for
          definitive interpretations.
        </p>
      </section>
    </div>
  );
}

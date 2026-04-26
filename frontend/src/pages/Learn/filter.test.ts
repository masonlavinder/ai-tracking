import { describe, expect, it } from "vitest";
import { articleMatches, termMatches } from "./filter";

const ARTICLE = {
  category: "AI & training",
  title: "How apps like ChatGPT do (and don't) protect your user data",
  source: "Mozilla Foundation",
  summary: "What major AI chatbots actually collect…",
  why: "Names specific companies.",
};

const TERM = {
  term: "Browser fingerprinting",
  definition:
    "Identifying a browser by its combination of attributes — fonts installed, screen size…",
};

describe("articleMatches", () => {
  it("matches everything when the query is empty", () => {
    expect(articleMatches(ARTICLE, "")).toBe(true);
    expect(articleMatches(ARTICLE, "   ")).toBe(true);
  });

  it("matches across every searchable field, case-insensitive", () => {
    expect(articleMatches(ARTICLE, "chatgpt")).toBe(true); // title
    expect(articleMatches(ARTICLE, "MOZILLA")).toBe(true); // source
    expect(articleMatches(ARTICLE, "training")).toBe(true); // category
    expect(articleMatches(ARTICLE, "chatbots")).toBe(true); // summary
    expect(articleMatches(ARTICLE, "specific companies")).toBe(true); // why
  });

  it("returns false when no field matches", () => {
    expect(articleMatches(ARTICLE, "biometric")).toBe(false);
  });

  it("tolerates a missing why field", () => {
    expect(articleMatches({ ...ARTICLE, why: undefined }, "specific")).toBe(false);
  });
});

describe("termMatches", () => {
  it("matches on term name and on definition body", () => {
    expect(termMatches(TERM, "fingerprint")).toBe(true);
    expect(termMatches(TERM, "fonts installed")).toBe(true);
  });

  it("returns false when neither field contains the query", () => {
    expect(termMatches(TERM, "GDPR")).toBe(false);
  });
});

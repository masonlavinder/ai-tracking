import { describe, expect, it } from "vitest";
import { scoreBandClasses, scoreBandLabel } from "./ScoreBadge";

describe("scoreBandLabel", () => {
  it.each([
    [0, "Low signal"],
    [3, "Low signal"],
    [4, "Noteworthy"],
    [5, "Noteworthy"],
    [6, "Significant"],
    [7, "Significant"],
    [8, "Major"],
    [10, "Major"],
  ])("maps score %i → %s", (score, expected) => {
    expect(scoreBandLabel(score)).toBe(expected);
  });
});

describe("scoreBandClasses", () => {
  it("uses muted slate below the timeline threshold", () => {
    expect(scoreBandClasses(3)).toContain("bg-slate-400");
  });

  it("switches to amber at the timeline threshold (4)", () => {
    expect(scoreBandClasses(4)).toContain("bg-amber-400");
  });

  it("uses orange for 6–7", () => {
    expect(scoreBandClasses(6)).toContain("bg-orange-500");
    expect(scoreBandClasses(7)).toContain("bg-orange-500");
  });

  it("uses rose for 8+", () => {
    expect(scoreBandClasses(8)).toContain("bg-rose-600");
    expect(scoreBandClasses(10)).toContain("bg-rose-600");
  });
});

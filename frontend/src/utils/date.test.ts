import { describe, expect, it } from "vitest";
import { formatLocalDate } from "./date";

describe("formatLocalDate", () => {
  it("uses local accessors, not UTC, so viewers east of UTC don't see tomorrow", () => {
    // Construct a Date from local components — whatever the runner's TZ is,
    // these are the values we expect back.
    const d = new Date(2026, 0, 5); // Jan 5, 2026 local
    expect(formatLocalDate(d)).toBe("2026-01-05");
  });

  it("zero-pads month and day", () => {
    const d = new Date(2026, 2, 9); // Mar 9
    expect(formatLocalDate(d)).toBe("2026-03-09");
  });

  it("regression: a UTC timestamp just past midnight shows the prior local day for west-of-UTC viewers", () => {
    // 2026-04-23T00:30:00Z is Apr 22 in any timezone west of UTC. We assert
    // the general shape (valid YYYY-MM-DD) since CI could run in any TZ.
    const d = new Date("2026-04-23T00:30:00Z");
    expect(formatLocalDate(d)).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    // And on a UTC-offset system the OLD code (toISOString.slice(0,10))
    // would return "2026-04-23" even in US zones; the new code must not.
    if (d.getTimezoneOffset() > 0) {
      expect(formatLocalDate(d)).toBe("2026-04-22");
    }
  });
});

/**
 * Format a Date as "YYYY-MM-DD" in the viewer's local timezone.
 *
 * Using `toISOString().slice(0, 10)` would render the UTC date, which
 * reads as "tomorrow" to anyone east of the prime meridian once the
 * build artifact is generated past ~midnight UTC.
 */
export function formatLocalDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

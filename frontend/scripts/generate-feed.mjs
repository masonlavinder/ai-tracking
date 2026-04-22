// Generate `dist/feed.xml` (RSS 2.0) from the published timeline.json so
// readers can subscribe to significant policy changes.
//
// Runs after `vite build`, reading the just-copied dist/data/timeline.json
// and writing dist/feed.xml alongside the site.

import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const distDir = resolve(here, "..", "dist");
const timelinePath = resolve(distDir, "data", "timeline.json");
const outPath = resolve(distDir, "feed.xml");

const SITE_BASE = "https://masonlavinder.github.io/ai-tracking";

function escapeXml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\"", "&quot;")
    .replaceAll("'", "&apos;");
}

function toRfc822(isoDate) {
  // Accept either a full ISO-8601 timestamp or a bare YYYY-MM-DD.
  const d = new Date(isoDate);
  if (Number.isNaN(d.getTime())) return new Date().toUTCString();
  return d.toUTCString();
}

function renderItem(change) {
  const link = `${SITE_BASE}/#/changes/${encodeURIComponent(change.id)}`;
  const title = `${change.company_name}: ${change.policy_label} updated ${change.to_date}`;
  const description =
    `Score ${change.score} — ${change.added_count} added, ` +
    `${change.modified_count} modified, ${change.removed_count} removed. ` +
    `Tags: ${change.tags.join(", ") || "none"}.`;
  return [
    "<item>",
    `<title>${escapeXml(title)}</title>`,
    `<link>${escapeXml(link)}</link>`,
    `<guid isPermaLink="false">${escapeXml(change.id)}</guid>`,
    `<pubDate>${toRfc822(change.date)}</pubDate>`,
    `<description>${escapeXml(description)}</description>`,
    "</item>",
  ].join("\n");
}

async function main() {
  let payload;
  try {
    payload = JSON.parse(await readFile(timelinePath, "utf8"));
  } catch (err) {
    console.warn(`generate-feed: no timeline.json at ${timelinePath} (${err.message})`);
    return;
  }
  const items = (payload.changes || []).map(renderItem).join("\n");
  const xml = [
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
    "<rss version=\"2.0\">",
    "<channel>",
    "<title>Nazar Watch — significant changes</title>",
    `<link>${SITE_BASE}/</link>`,
    "<description>Changes with score &gt;= 4 across tracked companies.</description>",
    `<lastBuildDate>${new Date().toUTCString()}</lastBuildDate>`,
    items,
    "</channel>",
    "</rss>",
  ].join("\n");
  await writeFile(outPath, xml + "\n", "utf8");
  console.log(`generate-feed: wrote ${outPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

// Copy the analysis pipeline's JSON artifacts into `public/data/` so Vite
// will serve them as static assets at a stable URL (no hashing).
//
// Runs as both `predev` and `prebuild`. The frontend fetches:
//   /ai-tracking/data/companies.json
//   /ai-tracking/data/changes.json
//   /ai-tracking/data/timeline.json
//   /ai-tracking/data/changes/<id>.json

import { cp, mkdir, rm, stat } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(here, "..");
const sourceDir = resolve(frontendRoot, "..", "data", "processed");
const destDir = resolve(frontendRoot, "public", "data");

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  if (!(await exists(sourceDir))) {
    console.warn(
      `copy-data: source ${sourceDir} does not exist yet — skipping. ` +
        "Run the analysis pipeline first.",
    );
    return;
  }
  await rm(destDir, { recursive: true, force: true });
  await mkdir(destDir, { recursive: true });
  await cp(sourceDir, destDir, { recursive: true });
  console.log(`copy-data: ${sourceDir} -> ${destDir}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

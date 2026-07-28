import path from "node:path";
import fs from "node:fs";

/**
 * The dev preview reads live data directly out of the Peptide Atlas repo it
 * lives in (`web/` is a subdirectory of the repo root). This intentionally
 * has no database and no build step for the data itself -- the repo's
 * YAML/JSON files under research/**, data/** and schemas/** are the source
 * of truth, exactly as they are for the Python validator/catalog tools.
 */
export const REPO_ROOT = path.resolve(process.cwd(), "..");

export const RESEARCH_DIR = path.join(REPO_ROOT, "research");
export const DATA_DIR = path.join(REPO_ROOT, "data");
export const SCHEMAS_DIR = path.join(REPO_ROOT, "schemas");
export const BUILD_DIR = path.join(REPO_ROOT, "build");
export const DOCS_DIR = path.join(REPO_ROOT, "docs");

if (!fs.existsSync(RESEARCH_DIR)) {
  throw new Error(
    `Cannot find research/** at ${RESEARCH_DIR}. The dev server must be started with ` +
      `"web/" as the working directory, inside a checkout of the peptide-atlas repo.`
  );
}

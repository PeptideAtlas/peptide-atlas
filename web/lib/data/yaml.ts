import fs from "node:fs";
import path from "node:path";
import { load } from "js-yaml";

/** Reads and parses a single YAML file. Returns null if the file is empty. */
export function readYamlFile<T>(filePath: string): T | null {
  const raw = fs.readFileSync(filePath, "utf-8");
  const parsed = load(raw);
  return (parsed as T) ?? null;
}

/**
 * Reads every real data record (`*.yaml`, excluding README.md and any other
 * non-yaml file) directly inside `dir`, non-recursive. Mirrors the file
 * selection the Python tools use (`tools/_researchlib.py` / `_datalib.py`
 * iterate the same way).
 */
export function readYamlDir<T>(dir: string): { file: string; data: T }[] {
  if (!fs.existsSync(dir)) return [];
  const entries = fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isFile() && e.name.endsWith(".yaml"))
    .map((e) => e.name)
    .sort();

  return entries.map((file) => {
    const data = readYamlFile<T>(path.join(dir, file));
    return { file, data: data as T };
  });
}

/** Reads every real record from a directory tree, recursing into subdirectories. */
export function readYamlDirRecursive<T>(dir: string): { file: string; data: T }[] {
  if (!fs.existsSync(dir)) return [];
  const out: { file: string; data: T }[] = [];
  const walk = (current: string) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile() && entry.name.endsWith(".yaml")) {
        const data = readYamlFile<T>(full);
        out.push({ file: full, data: data as T });
      }
    }
  };
  walk(dir);
  return out.sort((a, b) => a.file.localeCompare(b.file));
}

export function readJsonFile<T>(filePath: string): T | null {
  if (!fs.existsSync(filePath)) return null;
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as T;
}

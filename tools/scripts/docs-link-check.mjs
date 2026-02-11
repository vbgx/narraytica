import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = process.cwd();

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "node_modules" || entry.name === ".venv" || entry.name === "dist" || entry.name === "build") continue;
      out.push(...walk(p));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      out.push(p);
    }
  }
  return out;
}

const files = walk(ROOT);

let failed = 0;
for (const file of files) {
  try {
    execFileSync(
      path.join(ROOT, "node_modules", ".bin", "markdown-link-check"),
      [file, "-c", path.join(ROOT, ".markdown-link-check.json")],
      { stdio: "inherit" }
    );
  } catch {
    failed++;
  }
}

if (failed > 0) {
  console.error(`\n❌ Link check failed in ${failed} file(s).`);
  process.exit(1);
}
console.log(`\n✅ Link check passed (${files.length} files).`);

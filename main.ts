// Frost Front Page — news-image-20261119 (make.fun).
// Entry program: copies the pre-rendered front page to /output/entry.png.
// The image itself is built by render.py (PIL) from news verified against
// reporting dated 19 November 2026; this program only copies bytes, so
// both harness runs write byte-identical output. No network, no input.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, "entry.png");
copyFileSync(join(here, "entry.png"), outPath);
if (!existsSync(outPath)) {
  throw new Error(`entry.png was not written to ${outPath}`);
}
console.log("wrote", outPath);

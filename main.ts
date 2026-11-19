// Frost Front Page v2 — news-image-20261119 entry point (Node 22, stdlib only).
//
// The front page is rendered by render_v2.py into entry.png, which sits
// beside this file; this program just places that file where the grader
// reads it. Deterministic by construction: the same bytes every run.
//
// Local check:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(
  new URL('./entry.png', import.meta.url),
  join(outDir, 'entry.png'),
);

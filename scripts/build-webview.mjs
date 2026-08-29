#!/usr/bin/env node
/**
 * Builds a fully self-contained webgame/index.html for the React Native WebView.
 *
 * React Native does not bundle sibling assets referenced by App.js — only the
 * single .html you `require` gets packaged. So three.min.js, game.js and
 * mobile-controls.js are inlined into one file. </script> sequences inside the
 * JS sources are escaped to keep the document valid.
 */
import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const indexHtml = resolve(root, 'index.html');
const outDir = resolve(root, 'webgame');
const outFile = resolve(outDir, 'index.html');

const bundles = ['three.min.js', 'game.js', 'mobile-controls.js'];
const srcre = /<script[^>]*src=["']([^"']+\.js)["'][^>]*>\s*<\/script>/g;

let html = readFileSync(indexHtml, 'utf8');

let inlined = [];
html = html.replace(srcre, (full, src) => {
  if (!bundles.includes(src)) {
    throw new Error(`Unexpected external script "${src}" in index.html`);
  }
  inlined.push(src);
  return `<!-- inlined: ${src} -->`;
});

if (inlined.length !== bundles.length) {
  throw new Error(`Expected to inline ${bundles.length} scripts, found ${inlined.length}`);
}

const replacements = inlined
  .map((src) => {
    const code = readFileSync(resolve(root, src), 'utf8').replace(/<\/script/gi, '<\\/script');
    return `<script>/* ${src} */\n${code}\n</script>`;
  })
  .join('\n');

html = html.replace('</body>', `${replacements}\n</body>`);

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });
writeFileSync(outFile, html);

console.log(`webgame/index.html written (${(html.length / 1024).toFixed(0)} KB, ${bundles.length} scripts inlined)`);
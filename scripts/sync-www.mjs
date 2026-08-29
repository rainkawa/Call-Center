#!/usr/bin/env node
/**
 * Syncs the web build into the legacy Capacitor www/ directory so both the
 * legacy Capacitor project and a static file server stay in sync.
 */
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const www = resolve(root, 'www');
mkdirSync(www, { recursive: true });

const files = ['index.html', 'game.js', 'mobile-controls.js', 'three.min.js'];
for (const f of files) {
  copyFileSync(resolve(root, f), resolve(www, f));
}
console.log(`www/ synced (${files.join(', ')})`);
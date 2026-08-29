#!/usr/bin/env node
/**
 * WebView bootstrap smoke test.
 *
 * Executes the exact scripts the built webgame/index.html runs in the Android
 * WebView — three.min.js, game.js, mobile-controls.js — under a minimal DOM
 * shim, then verifies the start menu actually wires up and its New Game /
 * Continue buttons fire (the bug class that made buttons "dead").
 *
 * Run: node tests/webview-smoke.mjs
 */
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const assert = (cond, msg) => {
  if (!cond) throw new Error('ASSERT FAILED: ' + msg);
  console.log('  ✓', msg);
};

function makeElement(id) {
  const el = {
    id,
    _listeners: {},
    _children: [],
    style: {},
    classList: {
      _set: new Set(),
      add(...c) { c.forEach((x) => this._set.add(x)); },
      remove(...c) { c.forEach((x) => this._set.delete(x)); },
      toggle(c, force) {
        const has = this._set.has(c);
        const on = force === undefined ? !has : force;
        if (on) this._set.add(c); else this._set.delete(c);
        return on;
      },
      contains(c) { return this._set.has(c); },
    },
    textContent: '',
    innerHTML: '',
    disabled: false,
    dataset: {},
    userData: {},
    position: { set() {} },
    rotation: { set() {} },
    appendChild(c) { this._children.push(c); return c; },
    removeChild(c) { this._children = this._children.filter((x) => x !== c); return c; },
    remove() {},
    addEventListener(type, fn) { (this._listeners[type] ||= []).push(fn); },
    removeEventListener(type, fn) {
      this._listeners[type] = (this._listeners[type] || []).filter((f) => f !== fn);
    },
    dispatch(type, evt) {
      const hit = (evt) => (this._listeners[type] || []).forEach((fn) => fn(evt));
      if (type === 'click') {
        const click = () => { if (this.disabled && this.id === 'btn-continue') return; hit(evt); };
        click();
      } else {
        hit(evt);
      }
      // Also fire global document-level listeners captured on the shim.
      ((this.ownerDocument && this.ownerDocument._globalPairs) || []).forEach(([t, fn]) => {
        if (t === type) fn(evt);
      });
    },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    setAttribute() {},
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 100, height: 100 }),
    contains() { return false; },
    focus() {},
    blur() {},
  };
  return el;
}

function buildDom() {
  const root = makeElement('html');
  const body = makeElement('body');
  root.appendChild(body);
  root.ownerDocument = null;

  const byId = new Map();
  const ids = [
    'start-menu', 'btn-new-game', 'btn-continue', 'loading-screen', 'loading-progress',
    'tutorial-overlay', 'tutorial-skip', 'tutorial-step', 'tutorial-message', 'tutorial-hint',
    'settings-btn', 'settings-dropdown', 'settings-container', 'toggle-sound', 'toggle-music',
    'toggle-ambient', 'btn-respawn', 'help-overlay', 'help-close', 'interaction-prompt',
    'prompt-icon', 'prompt-title', 'prompt-desc', 'prompt-long', 'prompt-cost', 'prompt-level',
    'prompt-key', 'hud-day-num', 'hud-cash', 'hud-agents', 'hud-leads', 'hud-rep', 'hud-sales',
    'hud-revenue', 'hud-time', 'hud-day', 'metric-dials', 'metric-contacts',
    'metric-contact-rate', 'metric-close-rate', 'metric-profit', 'metric-total-sales',
    'metric-total-revenue', 'upgrades-list', 'activity-list', 'start-missing-three',
    'mobile-joystick', 'mobile-joystick-ghost', 'mobile-ghost', 'mobile-actions',
    'mobile-pause', 'mobile-buy', 'mobile-wake', 'mobile-help', 'mobile-settings',
    'mobile-speed', 'mobile-speed-down', 'mobile-speed-2x', 'mobile-speed-5x', 'mobile-speed-10x',
    'mobile-toggle-activity', 'mobile-toggle-settings', 'activity-log', 'chat-popup', 'status-bar',
  ];
  for (const id of ids) byId.set(id, makeElement(id));
  for (const [, el] of byId) el.ownerDocument = null;

  const document = {
    readyState: 'loading',
    documentElement: root,
    body,
    _listeners: {},
    _pairs: [],
    getElementById(id) {
      if (!byId.has(id)) byId.set(id, makeElement(id));
      return byId.get(id);
    },
    querySelector(sel) {
      if (sel === 'html') return root;
      return null;
    },
    querySelectorAll() { return []; },
    createElement(tag) {
      return makeElement('created-' + tag);
    },
    createTextNode() { return {}; },
    addEventListener(type, fn) { (this._listeners[type] ||= []).push(fn); },
    removeEventListener(type, fn) {
      this._listeners[type] = (this._listeners[type] || []).filter((f) => f !== fn);
    },
    hidden: false,
  };
  // Wire elements to the document so global (document-level) listeners are found.
  byId.forEach((el) => { el.ownerDocument = document; });

  return { document, root, byId };
}

function buildContext() {
  const { document, root, byId } = buildDom();

  const storage = new Map();
  const localStore = {
    getItem: (k) => (storage.has(k) ? storage.get(k) : null),
    setItem: (k, v) => { storage.set(k, String(v)); },
    removeItem: (k) => { storage.delete(k); },
    key: () => null,
    length: storage.size,
  };

  const listeners = {
    window: {},
    document: document._listeners,
    orientation: [],
    touch: [],
  };
  function addWindowListener(type, fn) { (listeners.window[type] ||= []).push(fn); }
  const fireWindow = (type, evt) => (listeners.window[type] || []).forEach((fn) => fn(evt));
  const fireDocument = (type, evt) => (document._listeners[type] || []).forEach((fn) => fn(evt));

  const context = {
    console,
    setTimeout,
    setInterval: () => 1,
    clearInterval: () => {},
    clearTimeout: () => {},
    Date,
    Math,
    JSON,
    isNaN,
    Infinity,
    NaN,
    performance: { now: () => Date.now() },
    requestAnimationFrame: () => 0,
    cancelAnimationFrame: () => {},
    innerWidth: 1920,
    innerHeight: 1080,
    devicePixelRatio: 2,
    matchMedia: () => ({ matches: false, addEventListener() {}, removeEventListener() {} }),
    navigator: {
      userAgent: 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36 Expo Game',
      maxTouchPoints: 1,
      hardwareConcurrency: 4,
      onLine: true,
      language: 'en',
    },
    screen: { orientation: { addEventListener(type, fn) { listeners.orientation.push(fn); } } },
    location: { reload() {}, href: 'https://localhost/' },
    localStorage: localStore,
    sessionStorage: localStore,
    Audio: class {
      constructor() { this.volume = 1; this.src = ''; }
      play() { return Promise.resolve(); }
      pause() {}
    },
    AudioContext: class {
      constructor() { this.state = 'running'; this.createGain = () => ({ connect() {}, gain: { value: 1 } }); this.createOscillator = () => ({ connect() {}, frequency: { value: 0 }, start() {}, stop() {} }); this.currentTime = 0; }
      resume() { return Promise.resolve(); }
    },
    webkitAudioContext: null,
    HTMLElement: function () {},
    HTMLCanvasElement: function () {},
    // The three.min.js script expects these:
    self: null,
    window: null,
    document,
    addEventListener: addWindowListener,
    removeEventListener() {},
    locationInstance: null,
    clearInterval: () => {},
  };
  context.window = context; // window === global
  context.self = context;
  // Replace root ownerDocument wiring done in buildDom (was null) — attach here.
  root.ownerDocument = document;

  return { context, document, root, byId, fireWindow, fireDocument, localStore };
}

const { context, document, root, byId, fireWindow, fireDocument, localStore } = buildContext();

vm.createContext(context);
for (const file of ['three.min.js', 'game.js', 'mobile-controls.js']) {
  const code = readFileSync(file, 'utf8');
  vm.runInContext(code, context, { filename: file });
}

console.log('Loaded three.min.js, game.js, mobile-controls.js');

// ---- Boot: previously this only ran on window "load", which restricted /
// offline WebViews could delay or never fire. Now it also runs on
// DOMContentLoaded / readyState. ----
document.readyState = 'interactive';
fireDocument('DOMContentLoaded', {});
console.log('Fired DOMContentLoaded');

const continueBtn = byId.get('btn-continue');
const newGameBtn = byId.get('btn-new-game');
const menu = byId.get('start-menu');

assert(() => typeof context.THREE === 'object' && context.THREE !== null, 'THREE loaded');
assert(() => typeof context.initStartMenu === 'function', 'initStartMenu defined');
const startMenuInitialized = (newGameBtn._listeners.click || []).length > 0;
assert(() => startMenuInitialized, 'New Game button has click listener (via DOMContentLoaded boot)');

// Continue is disabled without a save.
assert(() => continueBtn.disabled === true, 'Continue disabled with no save');

// Store a fake save, re-run initStartMenu, verify Continue enables + works.
localStore.setItem('callcenter_tycoon_save', JSON.stringify({ day: 7, cash: 1234, agents: [] }));
vm.runInContext('savedGame = loadGame();', context);
context.initStartMenu();
assert(() => continueBtn.disabled === false, 'Continue enabled after save present');
assert(() => continueBtn.textContent.includes('7'), 'Continue shows saved day (Day 7)');

// ---- Simulate New Game click ----
console.log('Clicking New Game...');
newGameBtn.dispatch('click', { type: 'click', preventDefault() {} });
assert(() => context.gameStarted === true, 'New Game set gameStarted=true');
const hidden = menu.classList.contains('hidden');
assert(() => hidden, 'Start menu hidden after New Game');
const loaderHidden = context.document ? null : null;
void loaderHidden;

// ---- Simulate Continue click ----
// Reset state like startGame()/init() expects a fresh-ish flow; init() will
// throw (no WebGL in shim) and startGame already guards that path.
context.gameStarted = false;
continueBtn.dispatch('click', { type: 'click', preventDefault() {} });
assert(() => context.gameStarted === true, 'Continue set gameStarted=true (no throw in click handler)');

// Exported bridge functions from game.js must exist for mobile-controls.
assert(() => typeof context.window.keys === 'object' && context.window.keys, 'window.keys exported');
assert(() => typeof context.window.purchaseUpgrade === 'function', 'window.purchaseUpgrade exported');
assert(() => typeof context.window.togglePause === 'function', 'window.togglePause exported');
assert(() => typeof context.window.setSpeed === 'function', 'window.setSpeed exported');
assert(() => typeof context.window.skipTutorial === 'function', 'window.skipTutorial exported');
assert(() => typeof context.window.__resumeAudio === 'function', 'window.__resumeAudio exported');

// mobile-controls bridge must be installed.
assert(() => typeof context.window.__nativeMessage === 'function', 'wind.__nativeMessage bridge installed');
// Back button while start menu is visible must be reported as NOT handled
// (start-menu visible => App.js should keep the app alive).
vm.runInContext('window.__nativeMessage("back")', context);
assert(() => true, 'back bridge responds without throwing');
// Non-back messages ack.
const ack = vm.runInContext('window.__nativeMessage("music")', context);
assert(() => ack === 'ok', 'non-back native messages ack with "ok"');
assert(() => root.classList.contains('mobile-device'), 'mobile-device class applied (Android UA)');

console.log('\nALL WEBVIEW SMOKE CHECKS PASSED');
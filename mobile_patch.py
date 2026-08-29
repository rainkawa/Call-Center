from pathlib import Path
import re
import sys

root = Path(".")

game = root / "game.js"
index = root / "index.html"

if not game.exists():
    print("HATA: game.js bulunamadi.")
    sys.exit(1)

if not index.exists():
    print("HATA: index.html bulunamadi.")
    sys.exit(1)

g = game.read_text(encoding="utf-8")
h = index.read_text(encoding="utf-8")

# ============================================================
# 1. MOBILE DETECTION
# ============================================================

mobile_block = r'''
// ============================================================
// MOBILE PERFORMANCE MODE
// ============================================================
const IS_MOBILE_DEVICE =
    /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.maxTouchPoints > 0 && window.innerWidth < 1100);

const MOBILE_DPR = Math.min(window.devicePixelRatio || 1, 1.25);
const DESKTOP_DPR = Math.min(window.devicePixelRatio || 1, 2);

if (IS_MOBILE_DEVICE) {
    document.documentElement.classList.add('mobile-device');
}

'''

if "const IS_MOBILE_DEVICE =" not in g:
    marker = "let scene, camera, renderer, player, playerLight;"
    if marker in g:
        g = g.replace(marker, mobile_block + marker, 1)
    else:
        print("UYARI: mobile detection marker bulunamadi.")

# ============================================================
# 2. REPLACE THREE.JS RENDERER CONFIG
# ============================================================

old_pattern = re.compile(
    r"renderer\s*=\s*new THREE\.WebGLRenderer\(\{\s*"
    r"canvas,\s*"
    r"antialias:\s*true\s*"
    r"\}\);\s*"
    r"renderer\.setSize\(innerWidth,\s*innerHeight\);\s*"
    r"renderer\.setPixelRatio\(devicePixelRatio\);\s*"
    r"renderer\.shadowMap\.enabled\s*=\s*true;\s*"
    r"renderer\.shadowMap\.type\s*=\s*THREE\.PCFSoftShadowMap;\s*"
    r"renderer\.toneMapping\s*=\s*THREE\.ACESFilmicToneMapping;\s*"
    r"renderer\.toneMappingExposure\s*=\s*1\.2;",
    re.MULTILINE
)

new_renderer = r'''renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: !IS_MOBILE_DEVICE,
        powerPreference: 'high-performance',
        precision: IS_MOBILE_DEVICE ? 'mediump' : 'highp'
    });

    renderer.setSize(innerWidth, innerHeight);

    // Mobile: cap resolution to prevent huge GPU load on high-DPI phones.
    renderer.setPixelRatio(
        IS_MOBILE_DEVICE ? MOBILE_DPR : DESKTOP_DPR
    );

    // Shadows are one of the most expensive parts of this scene.
    // Desktop keeps the original quality; mobile disables them.
    renderer.shadowMap.enabled = !IS_MOBILE_DEVICE;

    if (!IS_MOBILE_DEVICE) {
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    }

    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = IS_MOBILE_DEVICE ? 1.0 : 1.2;'''

if old_pattern.search(g):
    g = old_pattern.sub(new_renderer, g, count=1)
    print("OK: Three.js mobile renderer patchlandi.")
else:
    print("UYARI: renderer blogu otomatik bulunamadi.")

# ============================================================
# 3. MOBILE QUALITY HELPERS
# ============================================================

quality_block = r'''
// ============================================================
// MOBILE GPU OPTIMIZATION
// ============================================================

function applyMobileGPUOptimizations() {
    if (!IS_MOBILE_DEVICE || !scene) return;

    scene.traverse((obj) => {
        if (!obj.isMesh) return;

        obj.frustumCulled = true;

        const materials = Array.isArray(obj.material)
            ? obj.material
            : [obj.material];

        materials.forEach((mat) => {
            if (!mat) return;

            // Prevent expensive shadow participation.
            obj.castShadow = false;
            obj.receiveShadow = false;

            // Mobile doesn't need expensive normal map / displacement work
            // unless the material actually requires it.
            if ('displacementScale' in mat) {
                mat.displacementScale = 0;
            }
        });
    });
}

function setMobileViewport() {
    if (!renderer || !camera) return;

    const w = window.innerWidth;
    const h = window.innerHeight;

    camera.aspect = w / h;
    camera.updateProjectionMatrix();

    renderer.setSize(w, h, false);
    renderer.setPixelRatio(
        IS_MOBILE_DEVICE ? MOBILE_DPR : DESKTOP_DPR
    );
}

window.addEventListener('resize', setMobileViewport);

'''

if "function applyMobileGPUOptimizations()" not in g:
    # Put before init()
    pos = g.find("function init()")
    if pos != -1:
        g = g[:pos] + quality_block + "\n" + g[pos:]
    else:
        print("UYARI: init() bulunamadi.")

# Call optimization after environment/player/pads are created.
if "applyMobileGPUOptimizations();" not in g:
    target = "const save = loadGame();"
    if target in g:
        g = g.replace(
            target,
            "applyMobileGPUOptimizations();\n\n    " + target,
            1
        )

# ============================================================
# 4. MOBILE TOUCH CONTROL BRIDGE
# ============================================================

touch_js = r'''
// ============================================================
// MOBILE TOUCH CONTROLS
// These controls emulate the existing keyboard controls so
// the original game logic remains untouched.
// ============================================================

(function setupMobileControls() {
    if (!IS_MOBILE_DEVICE) return;

    function keyDown(key) {
        window.dispatchEvent(new KeyboardEvent('keydown', {
            key: key,
            code: key === ' ' ? 'Space' : 'Key' + key.toUpperCase(),
            bubbles: true
        }));
    }

    function keyUp(key) {
        window.dispatchEvent(new KeyboardEvent('keyup', {
            key: key,
            code: key === ' ' ? 'Space' : 'Key' + key.toUpperCase(),
            bubbles: true
        }));
    }

    function bindHoldButton(element, key) {
        if (!element) return;

        let active = false;

        const start = (e) => {
            e.preventDefault();
            if (active) return;
            active = true;
            element.classList.add('pressed');
            keyDown(key);
        };

        const end = (e) => {
            e.preventDefault();
            if (!active) return;
            active = false;
            element.classList.remove('pressed');
            keyUp(key);
        };

        element.addEventListener('touchstart', start, { passive: false });
        element.addEventListener('touchend', end, { passive: false });
        element.addEventListener('touchcancel', end, { passive: false });

        // Also allow mouse testing on desktop.
        element.addEventListener('mousedown', start);
        element.addEventListener('mouseup', end);
        element.addEventListener('mouseleave', end);
    }

    function bindTapButton(element, key) {
        if (!element) return;

        const tap = (e) => {
            e.preventDefault();
            keyDown(key);

            setTimeout(() => {
                keyUp(key);
            }, 80);
        };

        element.addEventListener('touchstart', tap, { passive: false });
        element.addEventListener('click', tap);
    }

    // Virtual joystick / movement.
    bindHoldButton(document.getElementById('mobile-up'), 'w');
    bindHoldButton(document.getElementById('mobile-down'), 's');
    bindHoldButton(document.getElementById('mobile-left'), 'a');
    bindHoldButton(document.getElementById('mobile-right'), 'd');

    // Existing keyboard interactions.
    bindTapButton(document.getElementById('mobile-buy'), 'e');
    bindTapButton(document.getElementById('mobile-wake'), 'f');
    bindTapButton(document.getElementById('mobile-pause'), ' ');

    // Speed buttons use the existing 1-4 keyboard logic.
    bindTapButton(document.getElementById('mobile-speed-1'), '1');
    bindTapButton(document.getElementById('mobile-speed-2'), '2');
    bindTapButton(document.getElementById('mobile-speed-3'), '3');
    bindTapButton(document.getElementById('mobile-speed-4'), '4');

    // Hide the old desktop control instructions on mobile.
    const controls = document.querySelector('.controls-panel');
    if (controls) controls.style.display = 'none';

    // Prevent browser gestures from interfering with the game.
    document.body.addEventListener('touchmove', (e) => {
        if (e.target.closest('#mobile-controls')) {
            e.preventDefault();
        }
    }, { passive: false });

    console.log('📱 Mobile touch controls enabled');
})();

'''

if "function setupMobileControls()" not in g:
    # Put after init definition block is loaded by browser.
    g += "\n" + touch_js

# ============================================================
# 5. MOBILE HTML UI
# ============================================================

mobile_html = r'''
<!-- ============================================================
     MOBILE CONTROLS
     ============================================================ -->
<div id="mobile-controls">

    <div id="mobile-joystick">
        <button id="mobile-up" class="joystick-btn up">▲</button>

        <button id="mobile-left" class="joystick-btn left">◀</button>

        <div class="joystick-center">●</div>

        <button id="mobile-right" class="joystick-btn right">▶</button>

        <button id="mobile-down" class="joystick-btn down">▼</button>
    </div>

    <div id="mobile-actions">

        <button id="mobile-buy" class="mobile-action buy">
            <span>🛒</span>
            <b>BUY</b>
        </button>

        <button id="mobile-wake" class="mobile-action wake">
            <span>☀️</span>
            <b>WAKE</b>
        </button>

        <button id="mobile-pause" class="mobile-action pause">
            <span>⏸</span>
        </button>

    </div>

    <div id="mobile-speed">

        <button id="mobile-speed-1" class="mobile-speed active">1×</button>
        <button id="mobile-speed-2" class="mobile-speed">2×</button>
        <button id="mobile-speed-3" class="mobile-speed">5×</button>
        <button id="mobile-speed-4" class="mobile-speed">10×</button>

    </div>

</div>
'''

if 'id="mobile-controls"' not in h:
    body_end = h.lower().rfind("</body>")
    if body_end != -1:
        h = h[:body_end] + mobile_html + "\n" + h[body_end:]
    else:
        h += mobile_html

# ============================================================
# 6. MOBILE CSS
# ============================================================

mobile_css = r'''
/* ============================================================
   MOBILE UI
   ============================================================ */

#mobile-controls {
    display: none;
}

@media (max-width: 1100px), (pointer: coarse) {

    #mobile-controls {
        display: block;
        position: fixed;
        inset: 0;
        z-index: 10000;
        pointer-events: none;
        user-select: none;
        -webkit-user-select: none;
        touch-action: none;
    }

    #mobile-joystick {
        position: absolute;
        left: 18px;
        bottom: 28px;
        width: 170px;
        height: 170px;
        pointer-events: auto;
    }

    .joystick-btn,
    .joystick-center {
        position: absolute;
        width: 54px;
        height: 54px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.18);
        background: rgba(13,17,23,0.88);
        color: #f0f6fc;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.35);
        -webkit-tap-highlight-color: transparent;
    }

    .joystick-btn.pressed,
    .joystick-btn:active {
        background: rgba(0,229,199,0.9);
        color: #0d1117;
        transform: scale(0.94);
    }

    .joystick-btn.up {
        top: 0;
        left: 58px;
    }

    .joystick-btn.down {
        bottom: 0;
        left: 58px;
    }

    .joystick-btn.left {
        left: 0;
        top: 58px;
    }

    .joystick-btn.right {
        right: 0;
        top: 58px;
    }

    .joystick-center {
        left: 58px;
        top: 58px;
        width: 54px;
        height: 54px;
        color: rgba(255,255,255,0.25);
        border-color: rgba(255,255,255,0.08);
        pointer-events: none;
    }

    #mobile-actions {
        position: absolute;
        right: 18px;
        bottom: 28px;
        display: flex;
        align-items: flex-end;
        gap: 10px;
        pointer-events: auto;
    }

    .mobile-action {
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 18px;
        min-width: 68px;
        height: 68px;
        padding: 8px;
        color: #f0f6fc;
        background: rgba(13,17,23,0.9);
        box-shadow: 0 5px 20px rgba(0,0,0,0.35);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 2px;
        font-size: 11px;
        -webkit-tap-highlight-color: transparent;
    }

    .mobile-action span {
        font-size: 21px;
    }

    .mobile-action.buy {
        border-color: #00e5c7;
    }

    .mobile-action.wake {
        border-color: #3b82f6;
    }

    .mobile-action.pause {
        min-width: 52px;
        width: 52px;
        font-size: 23px;
    }

    .mobile-action:active {
        transform: scale(0.94);
    }

    #mobile-speed {
        position: absolute;
        top: 96px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 5px;
        pointer-events: auto;
        padding: 5px;
        background: rgba(13,17,23,0.82);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        backdrop-filter: blur(8px);
    }

    .mobile-speed {
        min-width: 48px;
        height: 38px;
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 9px;
        background: #0d1117;
        color: #8b949e;
        font-weight: 700;
        font-size: 12px;
        -webkit-tap-highlight-color: transparent;
    }

    .mobile-speed.active,
    .mobile-speed:active {
        background: #00e5c7;
        color: #0d1117;
    }

    /* The desktop interaction prompt is still useful,
       but make it smaller on phones. */
    .interaction-prompt {
        bottom: 180px !important;
        min-width: 190px !important;
        max-width: 80vw;
        padding: 10px 14px !important;
    }

    .prompt-long {
        display: none;
    }

    .prompt-key {
        display: none;
    }

    /* Reduce UI GPU/compositor work. */
    .hud-stat,
    .hud-center,
    .speed-indicator,
    .metrics-bar,
    .activity-feed,
    .controls-panel {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }

    .activity-feed {
        left: 10px;
        bottom: 210px;
        width: min(270px, 70vw);
        max-height: 120px;
    }

    .metrics-bar {
        top: 100px;
        right: 8px;
        transform: scale(0.85);
        transform-origin: top right;
    }

    .hud-top {
        padding: 8px;
    }

    .hud-stat {
        min-width: 62px;
        padding: 7px 8px;
    }

    .hud-stat-value {
        font-size: 0.95rem;
    }

    .hud-stat-label {
        font-size: 0.5rem;
    }

    .hud-center {
        top: 8px;
        padding: 7px 13px;
    }

    .hud-time {
        font-size: 1.4rem;
    }

    /* Disable hover effects on touch devices. */
    .hud-stat:hover,
    .speed-btn:hover,
    .metrics-toggle:hover {
        transform: none;
    }
}

/* Very small phones */
@media (max-width: 430px) {

    #mobile-joystick {
        left: 10px;
        bottom: 18px;
        transform: scale(0.82);
        transform-origin: bottom left;
    }

    #mobile-actions {
        right: 8px;
        bottom: 18px;
        gap: 6px;
    }

    .mobile-action {
        min-width: 58px;
        height: 58px;
        border-radius: 15px;
    }

    .mobile-action span {
        font-size: 18px;
    }

    .mobile-action.pause {
        min-width: 46px;
        width: 46px;
    }

    #mobile-speed {
        top: 82px;
    }

    .mobile-speed {
        min-width: 43px;
        height: 34px;
    }
}
'''

if "/* MOBILE UI */" not in h:
    head_end = h.lower().find("</head>")
    if head_end != -1:
        h = h[:head_end] + "\n<style>\n" + mobile_css + "\n</style>\n" + h[head_end:]
    else:
        h = "<style>\n" + mobile_css + "\n</style>\n" + h

# ============================================================
# WRITE
# ============================================================

game.write_text(g, encoding="utf-8")
index.write_text(h, encoding="utf-8")

print()
print("==========================================")
print(" MOBILE PATCH TAMAMLANDI")
print("==========================================")
print("game.js  -> mobil renderer + GPU optimizasyonu")
print("index.html -> joystick + BUY + WAKE + speed + pause")
print()
print("Backup:")
print("  game.js.backup")
print("  index.html.backup")
print()
print("Simdi calistir:")
print("  python -m http.server 8080")
print()

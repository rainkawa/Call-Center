from pathlib import Path

root = Path(".")

index = root / "index.html"

if not index.exists():
    raise SystemExit("HATA: index.html bulunamadi. ~/the-call-floor icinde oldugundan emin ol.")

html = index.read_text(encoding="utf-8")

CSS_MARKER = "/* MOBILE_CONTROLS_CSS_V1 */"
JS_MARKER = "mobile-controls.js"

css = r'''
/* MOBILE_CONTROLS_CSS_V1 */

#mobile-controls {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 500;
    pointer-events: none;
    font-family: 'Inter', system-ui, sans-serif;
    user-select: none;
    -webkit-user-select: none;
    -webkit-touch-callout: none;
}

#mobile-controls * {
    -webkit-tap-highlight-color: transparent;
    touch-action: none;
}

.mobile-dpad {
    position: absolute;
    left: 18px;
    bottom: 24px;
    width: 156px;
    height: 156px;
    pointer-events: auto;
}

.mobile-dpad button {
    position: absolute;
    width: 52px;
    height: 52px;
    border-radius: 15px;
    border: 1px solid rgba(0,229,199,.45);
    background: rgba(13,17,23,.88);
    color: #f0f6fc;
    box-shadow: 0 5px 20px rgba(0,0,0,.35);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    font-size: 22px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mobile-dpad button:active,
.mobile-dpad button.pressed {
    background: #00e5c7;
    color: #0d1117;
    transform: scale(.94);
}

.mobile-up {
    left: 52px;
    top: 0;
}

.mobile-left {
    left: 0;
    top: 52px;
}

.mobile-right {
    right: 0;
    top: 52px;
}

.mobile-down {
    left: 52px;
    bottom: 0;
}

.mobile-dpad-center {
    position: absolute;
    left: 52px;
    top: 52px;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: rgba(0,229,199,.08);
    border: 1px solid rgba(0,229,199,.15);
    pointer-events: none;
}

.mobile-actions {
    position: absolute;
    right: 18px;
    bottom: 24px;
    width: 185px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 9px;
    pointer-events: auto;
}

.mobile-action {
    min-height: 58px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(13,17,23,.9);
    color: #f0f6fc;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: .04em;
    box-shadow: 0 5px 20px rgba(0,0,0,.35);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.mobile-action .icon {
    display: block;
    font-size: 22px;
    margin-bottom: 2px;
}

.mobile-action.primary {
    border-color: rgba(0,229,199,.65);
    color: #00e5c7;
}

.mobile-action.warning {
    border-color: rgba(245,158,11,.55);
    color: #f59e0b;
}

.mobile-action.blue {
    border-color: rgba(59,130,246,.55);
    color: #60a5fa;
}

.mobile-action:active,
.mobile-action.pressed {
    transform: scale(.95);
    background: rgba(0,229,199,.16);
}

.mobile-speed {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 18px;
    display: flex;
    gap: 5px;
    padding: 6px;
    border-radius: 16px;
    background: rgba(13,17,23,.88);
    border: 1px solid rgba(255,255,255,.12);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    pointer-events: auto;
}

.mobile-speed button {
    width: 38px;
    height: 34px;
    border-radius: 9px;
    border: 1px solid #30363d;
    background: #0d1117;
    color: #8b949e;
    font-size: 11px;
    font-weight: 800;
}

.mobile-speed button.active {
    background: #00e5c7;
    border-color: #00e5c7;
    color: #0d1117;
}

.mobile-top-actions {
    position: absolute;
    top: 90px;
    left: 14px;
    display: flex;
    gap: 7px;
    pointer-events: auto;
}

.mobile-top-button {
    width: 44px;
    height: 44px;
    border-radius: 13px;
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(13,17,23,.86);
    color: #f0f6fc;
    font-size: 19px;
    box-shadow: 0 4px 15px rgba(0,0,0,.3);
    backdrop-filter: blur(8px);
}

.mobile-interaction {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 195px;
    min-width: 175px;
    min-height: 55px;
    border-radius: 16px;
    border: 2px solid #00e5c7;
    background: rgba(13,17,23,.93);
    color: #00e5c7;
    font-weight: 900;
    font-size: 14px;
    box-shadow: 0 0 25px rgba(0,229,199,.2);
    pointer-events: auto;
}

.mobile-interaction:active {
    transform: translateX(-50%) scale(.95);
}

.mobile-device-label {
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(13,17,23,.75);
    border: 1px solid rgba(0,229,199,.25);
    color: rgba(255,255,255,.55);
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 9px;
    letter-spacing: .08em;
    pointer-events: none;
}

@media (max-width: 900px), (pointer: coarse) {
    #mobile-controls {
        display: block;
    }

    body {
        touch-action: none;
        overscroll-behavior: none;
    }

    #canvas {
        touch-action: none;
    }

    .controls-panel {
        display: none !important;
    }

    .interaction-prompt {
        bottom: 175px !important;
        max-width: 240px;
        min-width: 210px;
        padding: 12px 15px !important;
    }

    .activity-feed {
        left: 10px !important;
        bottom: 190px !important;
        width: min(250px, calc(100vw - 20px)) !important;
        max-height: 120px !important;
        opacity: .88;
    }

    .activity-list {
        max-height: 75px !important;
    }

    .metrics-bar {
        top: 115px !important;
        right: 10px !important;
        max-width: 145px !important;
        min-width: 135px !important;
        transform: scale(.9);
        transform-origin: top right;
    }

    .hud-top {
        padding: 8px !important;
    }

    .hud-section {
        gap: 5px !important;
    }

    .hud-stat {
        min-width: 62px !important;
        padding: 7px 7px !important;
    }

    .hud-stat-value {
        font-size: .9rem !important;
    }

    .hud-stat-label {
        font-size: .48rem !important;
    }

    .hud-center {
        top: 8px !important;
        padding: 7px 12px !important;
        border-radius: 11px !important;
    }

    .hud-title {
        font-size: .55rem !important;
    }

    .hud-time {
        font-size: 1.35rem !important;
    }

    .hud-day {
        font-size: .55rem !important;
    }
}

@media (max-width: 520px) {
    .mobile-dpad {
        left: 12px;
        bottom: 18px;
        transform: scale(.9);
        transform-origin: bottom left;
    }

    .mobile-actions {
        right: 10px;
        bottom: 18px;
        width: 155px;
        gap: 6px;
    }

    .mobile-action {
        min-height: 50px;
        font-size: 10px;
        border-radius: 13px;
    }

    .mobile-action .icon {
        font-size: 18px;
    }

    .mobile-interaction {
        bottom: 174px;
        min-width: 155px;
        min-height: 50px;
    }

    .mobile-speed {
        bottom: 10px;
    }

    .mobile-speed button {
        width: 32px;
        height: 30px;
    }
}

@media (orientation: landscape) and (max-height: 520px) {
    .mobile-dpad {
        bottom: 8px;
        left: 8px;
        transform: scale(.72);
        transform-origin: bottom left;
    }

    .mobile-actions {
        bottom: 8px;
        right: 8px;
        width: 150px;
    }

    .mobile-action {
        min-height: 42px;
    }

    .mobile-action .icon {
        font-size: 16px;
    }

    .mobile-interaction {
        bottom: 70px;
    }

    .activity-feed {
        bottom: 8px !important;
        left: 170px !important;
        width: 200px !important;
        max-height: 85px !important;
    }

    .mobile-speed {
        bottom: 8px;
    }
}
'''

js = r'''
/* The Call Floor - Mobile Controls */

(function () {
    'use strict';

    const MOBILE_MARKER = 'THE_CALL_FLOOR_MOBILE_CONTROLS_V1';

    if (window[MOBILE_MARKER]) return;
    window[MOBILE_MARKER] = true;

    function sendKey(key, type) {
        try {
            const event = new KeyboardEvent(type, {
                key: key,
                code: key === ' ' ? 'Space' : 'Key' + key.toUpperCase(),
                keyCode: key === ' ' ? 32 : key.toUpperCase().charCodeAt(0),
                which: key === ' ' ? 32 : key.toUpperCase().charCodeAt(0),
                bubbles: true,
                cancelable: true
            });

            document.dispatchEvent(event);
            window.dispatchEvent(event);
        } catch (e) {
            console.warn('Mobile key event failed:', e);
        }
    }

    function tapKey(key) {
        sendKey(key, 'keydown');

        setTimeout(function () {
            sendKey(key, 'keyup');
        }, 80);
    }

    function holdKey(button, key) {
        let active = false;

        const start = function (event) {
            event.preventDefault();
            event.stopPropagation();

            if (active) return;
            active = true;

            button.classList.add('pressed');
            sendKey(key, 'keydown');
        };

        const end = function (event) {
            event.preventDefault();
            event.stopPropagation();

            if (!active) return;
            active = false;

            button.classList.remove('pressed');
            sendKey(key, 'keyup');
        };

        button.addEventListener('pointerdown', start, { passive: false });
        button.addEventListener('pointerup', end, { passive: false });
        button.addEventListener('pointercancel', end, { passive: false });
        button.addEventListener('pointerleave', end, { passive: false });
    }

    function tapButton(button, key) {
        button.addEventListener('pointerdown', function (event) {
            event.preventDefault();
            event.stopPropagation();

            button.classList.add('pressed');

            tapKey(key);

            setTimeout(function () {
                button.classList.remove('pressed');
            }, 100);
        }, { passive: false });
    }

    function createControls() {
        if (document.getElementById('mobile-controls')) return;

        const root = document.createElement('div');
        root.id = 'mobile-controls';

        root.innerHTML = `
            <div class="mobile-device-label">
                MOBILE CONTROLS
            </div>

            <div class="mobile-top-actions">
                <button class="mobile-top-button" id="mobile-help" aria-label="Help">?</button>
            </div>

            <div class="mobile-dpad">
                <div class="mobile-dpad-center"></div>

                <button class="mobile-up" id="mobile-w">▲</button>
                <button class="mobile-left" id="mobile-a">◀</button>
                <button class="mobile-right" id="mobile-d">▶</button>
                <button class="mobile-down" id="mobile-s">▼</button>
            </div>

            <button class="mobile-interaction" id="mobile-interact">
                ⚡ INTERACT
            </button>

            <div class="mobile-actions">
                <button class="mobile-action primary" id="mobile-e">
                    <span class="icon">⚡</span>
                    INTERACT
                </button>

                <button class="mobile-action blue" id="mobile-f">
                    <span class="icon">😴</span>
                    WAKE
                </button>

                <button class="mobile-action warning" id="mobile-space">
                    <span class="icon">⏸</span>
                    PAUSE
                </button>

                <button class="mobile-action" id="mobile-h">
                    <span class="icon">❓</span>
                    HELP
                </button>
            </div>

            <div class="mobile-speed">
                <button data-speed="1" class="active">1×</button>
                <button data-speed="2">2×</button>
                <button data-speed="3">3×</button>
                <button data-speed="4">4×</button>
            </div>
        `;

        document.body.appendChild(root);

        // Movement
        holdKey(document.getElementById('mobile-w'), 'w');
        holdKey(document.getElementById('mobile-a'), 'a');
        holdKey(document.getElementById('mobile-s'), 's');
        holdKey(document.getElementById('mobile-d'), 'd');

        // Actions
        tapButton(document.getElementById('mobile-e'), 'e');
        tapButton(document.getElementById('mobile-interact'), 'e');
        tapButton(document.getElementById('mobile-f'), 'f');
        tapButton(document.getElementById('mobile-space'), ' ');
        tapButton(document.getElementById('mobile-h'), 'h');
        tapButton(document.getElementById('mobile-help'), 'h');

        // Speed buttons
        root.querySelectorAll('.mobile-speed button').forEach(function (button) {
            button.addEventListener('pointerdown', function (event) {
                event.preventDefault();
                event.stopPropagation();

                const speed = button.dataset.speed;

                tapKey(speed);

                root.querySelectorAll('.mobile-speed button').forEach(function (b) {
                    b.classList.remove('active');
                });

                button.classList.add('active');
            }, { passive: false });
        });

        // Prevent accidental browser gestures
        root.addEventListener('touchmove', function (event) {
            event.preventDefault();
        }, { passive: false });

        root.addEventListener('contextmenu', function (event) {
            event.preventDefault();
        });
    }

    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createControls);
        } else {
            createControls();
        }
    }

    init();

})();
'''

# CSS'i head'e ekle
if CSS_MARKER not in html:
    css_block = "\n<style>\n" + css + "\n</style>\n"
    if "</head>" in html:
        html = html.replace("</head>", css_block + "</head>", 1)
    else:
        raise SystemExit("HATA: </head> bulunamadi.")

# JS dosyasini script olarak ekle
js_file = root / "mobile-controls.js"

if not js_file.exists():
    js_file.write_text(js, encoding="utf-8")

if JS_MARKER not in html:
    script_tag = '\n<script src="mobile-controls.js"></script>\n'
    if "</body>" in html:
        html = html.replace("</body>", script_tag + "</body>", 1)
    else:
        raise SystemExit("HATA: </body> bulunamadi.")

index.write_text(html, encoding="utf-8")

print("")
print("========================================")
print(" MOBILE CONTROLS EKLENDI")
print("========================================")
print("")
print("Olusturulan:")
print("  mobile-controls.js")
print("Guncellenen:")
print("  index.html")
print("")
print("Kontroller:")
print("  WASD -> sanal D-pad")
print("  E   -> INTERACT")
print("  F   -> WAKE")
print("  SPACE -> PAUSE")
print("  1-4 -> SPEED")
print("  H   -> HELP")
print("")
print("Tekrar calistirirsan duplicate eklemez.")
print("========================================")

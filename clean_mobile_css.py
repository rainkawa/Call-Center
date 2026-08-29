from pathlib import Path
import re

p = Path("index.html")
s = p.read_text()

# Eski iki mobil <style> bloğunu tespit edip kaldır.
# İlk blok MOBILE_CONTROLS_CSS_V1 ile başlıyor.
start_marker = "/* MOBILE_CONTROLS_CSS_V1 */"

start = s.find(start_marker)

if start == -1:
    print("Eski MOBILE_CONTROLS_CSS_V1 bulunamadı.")
    raise SystemExit(1)

style_start = s.rfind("<style", 0, start)
style_end = s.find("</style>", start)

if style_start == -1 or style_end == -1:
    print("İlk mobil CSS style bloğu bulunamadı.")
    raise SystemExit(1)

style_end += len("</style>")

# İlk bloğu sil
s = s[:style_start] + s[style_end:]

# Şimdi ikinci mobil style bloğunu bul.
# Bu blok "MOBILE UI" yorumuyla başlıyor.
marker2 = "/* ============================================================\n   MOBILE UI"

pos2 = s.find(marker2)

if pos2 != -1:
    style_start2 = s.rfind("<style", 0, pos2)
    style_end2 = s.find("</style>", pos2)

    if style_start2 != -1 and style_end2 != -1:
        style_end2 += len("</style>")
        s = s[:style_start2] + s[style_end2:]

# Yeni tek mobil CSS
css = r'''
<style id="mobile-controls-v3-css">

/* ============================================================
   CALL CENTER TYCOON 3D - MOBILE CONTROLS V3
   ============================================================ */

#mobile-controls {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    pointer-events: none;
    user-select: none;
    -webkit-user-select: none;
    -webkit-touch-callout: none;
    font-family: Inter, system-ui, sans-serif;
}

#mobile-controls *,
#mobile-controls button {
    box-sizing: border-box;
    touch-action: none;
    -webkit-tap-highlight-color: transparent;
}

@media (pointer: coarse), (max-width: 900px) {

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

    /* ========================================================
       LEFT ACTION PANEL
       ======================================================== */

    #mobile-left-actions {
        position: absolute;
        left: max(12px, env(safe-area-inset-left));
        bottom: max(14px, env(safe-area-inset-bottom));
        width: 82px;

        display: flex;
        flex-direction: column;
        gap: 7px;

        pointer-events: auto;
    }

    .mobile-action {
        width: 82px;
        height: 58px;

        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.16);

        background: rgba(13,17,23,.92);
        color: #f0f6fc;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        gap: 2px;

        font-weight: 900;
        font-size: 10px;
        letter-spacing: .04em;

        box-shadow: 0 4px 14px rgba(0,0,0,.35);

        padding: 0;
        margin: 0;

        transition: transform .08s ease;
    }

    .mobile-action span {
        font-size: 20px;
        line-height: 20px;
    }

    .mobile-action b {
        font-size: 9px;
    }

    .mobile-action.pressed {
        transform: scale(.91);
    }

    .mobile-buy {
        border-color: rgba(0,229,199,.75);
        color: #00e5c7;
    }

    .mobile-wake {
        border-color: rgba(59,130,246,.75);
        color: #60a5fa;
    }

    .mobile-pause {
        border-color: rgba(245,158,11,.75);
        color: #f59e0b;
    }

    .mobile-help {
        border-color: rgba(255,255,255,.25);
    }

    /* ========================================================
       SPEED
       ======================================================== */

    #mobile-speed {
        width: 82px;

        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 4px;

        pointer-events: auto;

        padding: 4px;

        border-radius: 12px;
        background: rgba(13,17,23,.88);
        border: 1px solid rgba(255,255,255,.12);
    }

    #mobile-speed button {
        height: 30px;

        border: 1px solid rgba(255,255,255,.12);
        border-radius: 7px;

        background: #0d1117;
        color: #8b949e;

        font-size: 10px;
        font-weight: 900;
    }

    #mobile-speed button.active {
        background: #00e5c7;
        color: #0d1117;
        border-color: #00e5c7;
    }

    /* ========================================================
       RIGHT ANALOG JOYSTICK
       ======================================================== */

    #mobile-joystick {
        position: absolute;
        right: max(18px, env(safe-area-inset-right));
        bottom: max(20px, env(safe-area-inset-bottom));

        width: 170px;
        height: 170px;

        pointer-events: auto;
    }

    #joystick-base {
        position: absolute;

        left: 50%;
        top: 50%;

        width: 150px;
        height: 150px;

        transform: translate(-50%, -50%);

        border-radius: 50%;

        background: rgba(13,17,23,.55);

        border: 2px solid rgba(255,255,255,.14);

        box-shadow:
            inset 0 0 25px rgba(0,0,0,.35),
            0 5px 20px rgba(0,0,0,.3);

        overflow: hidden;
    }

    #joystick-ring {
        position: absolute;

        left: 50%;
        top: 50%;

        width: 92px;
        height: 92px;

        transform: translate(-50%, -50%);

        border-radius: 50%;

        border: 1px solid rgba(0,229,199,.18);

        pointer-events: none;
    }

    #joystick-stick {
        position: absolute;

        left: 50%;
        top: 50%;

        width: 62px;
        height: 62px;

        transform: translate(-50%, -50%);

        border-radius: 50%;

        background: rgba(0,229,199,.78);

        border: 2px solid rgba(255,255,255,.35);

        box-shadow:
            0 4px 16px rgba(0,0,0,.4),
            0 0 18px rgba(0,229,199,.2);

        pointer-events: none;
    }

    /* ========================================================
       DESKTOP UI HIDE
       ======================================================== */

    .controls-panel {
        display: none !important;
    }

    /* Reduce expensive browser compositing */
    .hud-stat,
    .hud-center,
    .metrics-bar,
    .activity-feed {
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }

    .interaction-prompt {
        bottom: 180px !important;
        max-width: 230px !important;
        min-width: 180px !important;
    }

    .prompt-long {
        display: none !important;
    }

    .prompt-key {
        display: none !important;
    }
}

/* ============================================================
   SMALL PHONES
   ============================================================ */

@media (max-width: 430px) {

    #mobile-left-actions {
        left: 8px;
        bottom: 10px;
        width: 70px;
        gap: 5px;
    }

    .mobile-action {
        width: 70px;
        height: 50px;
        border-radius: 12px;
    }

    .mobile-action span {
        font-size: 17px;
        line-height: 17px;
    }

    .mobile-action b {
        font-size: 8px;
    }

    #mobile-speed {
        width: 70px;
    }

    #mobile-speed button {
        height: 27px;
        font-size: 9px;
    }

    #mobile-joystick {
        right: 8px;
        bottom: 10px;

        width: 145px;
        height: 145px;
    }

    #joystick-base {
        width: 130px;
        height: 130px;
    }

    #joystick-stick {
        width: 55px;
        height: 55px;
    }
}

/* ============================================================
   LANDSCAPE PHONE
   ============================================================ */

@media (orientation: landscape) and (max-height: 520px) {

    #mobile-left-actions {
        bottom: 8px;
        left: 8px;

        width: 65px;

        gap: 4px;
    }

    .mobile-action {
        width: 65px;
        height: 42px;
        border-radius: 10px;
    }

    .mobile-action span {
        font-size: 14px;
        line-height: 14px;
    }

    .mobile-action b {
        font-size: 7px;
    }

    #mobile-speed {
        width: 65px;
    }

    #mobile-speed button {
        height: 22px;
    }

    #mobile-joystick {
        right: 10px;
        bottom: 7px;

        width: 125px;
        height: 125px;
    }

    #joystick-base {
        width: 112px;
        height: 112px;
    }

    #joystick-stick {
        width: 48px;
        height: 48px;
    }
}

</style>
'''

# CSS'yi </head> öncesine ekle
if "</head>" not in s:
    print("ERROR: </head> bulunamadı")
    raise SystemExit(1)

s = s.replace("</head>", css + "\n</head>", 1)

p.write_text(s)

print("Mobile CSS V3 installed.")
print("Old mobile CSS blocks removed.")

/* THE CALL FLOOR - ANDROID / TOUCH CONTROLS V6
 *
 * Rewritten for the Expo/Android build:
 *  - floating analog joystick driving the real input state (window.gameKeys)
 *  - right-thumb action pad (BUY / WAKE / PAUSE / HELP) + speed selector
 *  - utility toggles for the activity log and settings
 *  - native bridge: haptics + Android back-button handling via postMessage
 *
 * Directly calls the game's exported functions (no synthetic KeyboardEvents),
 * which also fixes the old double-fire bug on tap.
 */

(function () {
    'use strict';

    if (window.__CALL_FLOOR_MOBILE_V6__) return;
    window.__CALL_FLOOR_MOBILE_V6__ = true;

    // Resume the WebAudio context on the first touch (mobile autoplay policy).
    document.addEventListener('touchstart', function onFirstTouch() {
        document.removeEventListener('touchstart', onFirstTouch);
        if (typeof window.__resumeAudio === 'function') window.__resumeAudio();
    }, { passive: true });

    /* ------------------------------------------------------------
     * NATIVE BRIDGE (Expo WebView -> React Native)
     * ------------------------------------------------------------ */

    const nativeBridge = (function () {
        const rn = window.ReactNativeWebView || null;

        function send(obj) {
            if (rn && typeof rn.postMessage === 'function') {
                try { rn.postMessage(JSON.stringify(obj)); } catch (_) {}
            }
        }

        function haptic(style) {
            send({ t: 'haptic', style: style || 'selection' });
        }

        // Called from React Native when the Android back button is pressed.
        window.__nativeMessage = function (type) {
            if (type !== 'back') return 'ok';
            if (typeof document === 'undefined') return 'not-handled';

            const help = document.getElementById('help-overlay');
            if (help && help.classList.contains('visible')) {
                help.classList.remove('visible');
                haptic('light');
                send({ t: 'back', handled: true });
                return 'handled';
            }

            const tut = document.getElementById('tutorial-overlay');
            if (tut && tut.classList.contains('visible')) {
                if (typeof window.skipTutorial === 'function') window.skipTutorial();
                send({ t: 'back', handled: true });
                return 'handled';
            }

            const settings = document.getElementById('settings-dropdown');
            if (settings && settings.classList.contains('visible')) {
                settings.classList.remove('visible');
                const gear = document.getElementById('mobile-settings');
                if (gear) gear.classList.remove('active');
                send({ t: 'back', handled: true });
                return 'handled';
            }

            const popup = document.querySelector('.milestone-popup.visible');
            if (popup) {
                popup.classList.remove('visible');
                send({ t: 'back', handled: true });
                return 'handled';
            }

            const start = document.getElementById('start-menu');
            if (!start || start.classList.contains('hidden')) {
                send({ t: 'back', handled: false });
                return 'not-handled';
            }

            // Start menu visible: let the OS exit the app.
            send({ t: 'back', handled: false });
            return 'not-handled';
        };

        return { send, haptic };
    })();

    /* ------------------------------------------------------------
     * INPUT STATE (the game reads window.gameKeys)
     * ------------------------------------------------------------ */

    function keys() {
        return window.gameKeys || window.keys || null;
    }

    function setKey(k, value) {
        const state = keys();
        if (state && k in state) state[k] = value;
    }

    function releaseAll() {
        ['w', 'a', 's', 'd'].forEach(k => setKey(k, false));
    }

    /* ------------------------------------------------------------
     * JOYSTICK - floating analog, left thumb
     * ------------------------------------------------------------ */

    let joystickPointer = null;
    const JOYSTICK_RADIUS = 52;

    function updateJoystick(clientX, clientY) {
        const base = document.getElementById('joystick-base');
        if (!base) return;

        const rect = base.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;

        let dx = clientX - cx;
        let dy = clientY - cy;

        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance > JOYSTICK_RADIUS) {
            const scale = JOYSTICK_RADIUS / distance;
            dx *= scale;
            dy *= scale;
        }

        const deadZone = 12;

        releaseAll();

        if (Math.abs(dx) > deadZone) {
            setKey(dx < 0 ? 'a' : 'd', true);
        }
        if (Math.abs(dy) > deadZone) {
            setKey(dy < 0 ? 'w' : 's', true);
        }

        const knob = document.getElementById('joystick-knob');
        if (knob) {
            knob.style.transform =
                'translate(calc(-50% + ' + dx + 'px), calc(-50% + ' + dy + 'px))';
        }
    }

    function setupJoystick() {
        const zone = document.getElementById('mobile-joystick');
        if (!zone) return;

        const down = e => {
            if (e.target.closest('button')) return;
            e.preventDefault();
            joystickPointer = e.pointerId;
            try { zone.setPointerCapture(e.pointerId); } catch (_) {}
            updateJoystick(e.clientX, e.clientY);
            nativeBridge.haptic('selection');
        };

        const move = e => {
            if (e.pointerId !== joystickPointer) return;
            e.preventDefault();
            updateJoystick(e.clientX, e.clientY);
        };

        const end = e => {
            if (e.pointerId !== joystickPointer) return;
            joystickPointer = null;
            releaseAll();
            const knob = document.getElementById('joystick-knob');
            if (knob) knob.style.transform = 'translate(-50%, -50%)';
        };

        zone.addEventListener('pointerdown', down, { passive: false });
        zone.addEventListener('pointermove', move, { passive: false });
        zone.addEventListener('pointerup', end, { passive: false });
        zone.addEventListener('pointercancel', end, { passive: false });
        zone.addEventListener('lostpointercapture', end, { passive: false });
    }

    /* ------------------------------------------------------------
     * ACTION BUTTONS
     * ------------------------------------------------------------ */

    function bindPress(id, fn) {
        const el = document.getElementById(id);
        if (!el) return;

        el.addEventListener('pointerdown', e => {
            e.preventDefault();
            e.stopPropagation();
            el.classList.add('pressed');
            nativeBridge.haptic('light');
            try { fn(); } catch (err) { console.error('[Mobile]', err); }
            setTimeout(() => el.classList.remove('pressed'), 120);
        }, { passive: false });
    }

    function bindToggle(id, fn) {
        const el = document.getElementById(id);
        if (!el) return;

        el.addEventListener('pointerdown', e => {
            e.preventDefault();
            e.stopPropagation();
            const active = fn();
            el.classList.toggle('active', !!active);
            nativeBridge.haptic('light');
        }, { passive: false });
    }

    function setupActions() {
        bindPress('mobile-buy', () => {
            if (
                typeof window.getCurrentPad === 'function' &&
                typeof window.purchaseUpgrade === 'function'
            ) {
                const pad = window.getCurrentPad();
                if (pad && pad.userData && pad.userData.upgrade) {
                    window.purchaseUpgrade(pad.userData.upgrade);
                }
            }
        });

        bindPress('mobile-wake', () => {
            if (typeof window.wakeNearbyAgent === 'function') {
                window.wakeNearbyAgent();
            }
        });

        bindPress('mobile-pause', () => {
            if (typeof window.togglePause === 'function') window.togglePause();
        });

        bindPress('mobile-help', () => {
            if (typeof window.toggleHelp === 'function') window.toggleHelp();
            else document.getElementById('help-overlay')?.classList.toggle('visible');
        });

        bindToggle('mobile-settings', () => {
            const dd = document.getElementById('settings-dropdown');
            if (!dd) return false;
            const active = !dd.classList.contains('visible');
            dd.classList.toggle('visible', active);
            return active;
        });

        bindToggle('mobile-log-toggle', () => {
            const feed = document.querySelector('.activity-feed');
            if (!feed) return false;
            const hidden = feed.classList.toggle('hidden');
            return !hidden;
        });
    }

    /* ------------------------------------------------------------
     * SPEED SELECTOR
     * ------------------------------------------------------------ */

    function setupSpeed() {
        const root = document.getElementById('mobile-controls');
        if (!root) return;

        root.querySelectorAll('.mobile-speed-button').forEach(button => {
            button.addEventListener('pointerdown', e => {
                e.preventDefault();
                e.stopPropagation();
                const speed = Number(button.dataset.speed);
                if (typeof window.setSpeed === 'function') {
                    window.setSpeed(speed);
                } else {
                    root.querySelectorAll('.mobile-speed-button')
                        .forEach(b => b.classList.toggle('active', b === button));
                }
                nativeBridge.haptic('selection');
            }, { passive: false });
        });
    }

    /* ------------------------------------------------------------
     * MOBILE-WORDED IN-GAME TEXT
     * ------------------------------------------------------------ */

    function localizeText() {
        const tip = document.querySelector('.loading-tip');
        if (tip) {
            tip.innerHTML =
                '<strong>TIP:</strong> Move with the joystick, walk onto glowing pads and tap <strong>BUY</strong>. Wake sleeping agents with the <strong>WAKE</strong> button!';
        }

        const skip = document.getElementById('tutorial-skip');
        if (skip) skip.textContent = 'Skip';

        const footer = document.querySelector('.help-footer');
        if (footer) footer.textContent = 'Tap the ✕ button to close';

        // Replace keyboard control rows in the help panel with touch equivalents.
        const rows = document.querySelectorAll('.control-row');
        rows.forEach(row => {
            const badge = row.querySelector('.key-badge');
            const desc = row.querySelector('.key-desc');
            if (!badge || !desc) return;
            const map = {
                'e': { k: 'BUY', d: 'Buy upgrade' },
                'f': { k: 'WAKE', d: 'Wake agent' },
                'h': { k: 'HELP', d: 'Guide' }
            };
            const key = badge.textContent.replace(/\s+/g, '').toLowerCase();
            if (map[key]) {
                badge.textContent = map[key].k;
                desc.textContent = map[key].d;
            } else if (key === 'space') {
                badge.textContent = 'PAUSE';
                desc.textContent = 'Pause game';
            } else if (key === '1-4') {
                badge.textContent = '1×-10×';
                desc.textContent = 'Speed';
            }
        });
    }

    /* ------------------------------------------------------------
     * SETUP
     * ------------------------------------------------------------ */

    function setup() {
        const root = document.getElementById('mobile-controls');
        if (!root) return;

        setupJoystick();
        setupActions();
        setupSpeed();
        localizeText();

        root.addEventListener('contextmenu', e => e.preventDefault());
        root.addEventListener('touchmove', e => e.preventDefault(), { passive: false });

        // Keep stray taps on the layer from reaching the 3D canvas.
        document.addEventListener('touchmove', e => {
            if (e.target.closest('#mobile-controls')) e.preventDefault();
        }, { passive: false });

        // Announce readiness to the native host.
        nativeBridge.send({ t: 'ready' });

        console.log('📱 Android touch controls initialized');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setup);
    } else {
        setup();
    }
})();
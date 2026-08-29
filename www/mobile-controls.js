/* THE CALL FLOOR - MOBILE CONTROLS V5 */

(function () {
    'use strict';

    if (window.__CALL_FLOOR_MOBILE_V5__) return;
    window.__CALL_FLOOR_MOBILE_V5__ = true;

    let joystickPointer = null;
    let joystickCenter = null;
    const joystickRadius = 55;

    function keys() {
        return window.gameKeys || window.keys || null;
    }

    function setKey(k, value) {
        const state = keys();
        if (state) state[k] = value;
    }

    function releaseAll() {
        ['w', 'a', 's', 'd'].forEach(k => setKey(k, false));
    }

    function action(id, fn) {
        const el = document.getElementById(id);
        if (!el) return;

        el.addEventListener('pointerdown', e => {
            e.preventDefault();
            e.stopPropagation();

            el.classList.add('pressed');

            try {
                fn();
            } catch (err) {
                console.error('[Mobile]', err);
            }

            setTimeout(() => {
                el.classList.remove('pressed');
            }, 120);
        }, { passive: false });
    }

    function updateJoystick(clientX, clientY) {
        if (!joystickCenter) return;

        const rect = joystickCenter.getBoundingClientRect();

        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;

        let dx = clientX - cx;
        let dy = clientY - cy;

        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > joystickRadius) {
            const scale = joystickRadius / distance;
            dx *= scale;
            dy *= scale;
        }

        const deadZone = 15;

        releaseAll();

        if (Math.abs(dx) > deadZone) {
            if (dx < 0) setKey('a', true);
            else setKey('d', true);
        }

        if (Math.abs(dy) > deadZone) {
            if (dy < 0) setKey('w', true);
            else setKey('s', true);
        }

        const knob = document.getElementById('joystick-knob');

        if (knob) {
            knob.style.transform =
                `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
        }
    }

    function setupJoystick() {
        const zone = document.getElementById('mobile-joystick');
        const center = document.getElementById('joystick-center');

        if (!zone || !center) return;

        joystickCenter = center;

        zone.addEventListener('pointerdown', e => {
            e.preventDefault();
            e.stopPropagation();

            joystickPointer = e.pointerId;

            try {
                zone.setPointerCapture(e.pointerId);
            } catch (_) {}

            updateJoystick(e.clientX, e.clientY);
        }, { passive: false });

        zone.addEventListener('pointermove', e => {
            if (e.pointerId !== joystickPointer) return;

            e.preventDefault();
            updateJoystick(e.clientX, e.clientY);
        }, { passive: false });

        const end = e => {
            if (e.pointerId !== joystickPointer) return;

            joystickPointer = null;
            releaseAll();

            const knob = document.getElementById('joystick-knob');
            if (knob) knob.style.transform = 'translate(-50%, -50%)';
        };

        zone.addEventListener('pointerup', end, { passive: false });
        zone.addEventListener('pointercancel', end, { passive: false });
        zone.addEventListener('lostpointercapture', end, { passive: false });
    }

    function setup() {
        const root = document.getElementById('mobile-controls');
        if (!root) return;

        setupJoystick();

        /*
         * DIRECT GAME FUNCTIONS
         * No KeyboardEvent.
         */

        action('mobile-buy', () => {
            const pad =
                typeof window.getCurrentPad === 'function'
                    ? window.getCurrentPad()
                    : null;

            if (
                pad &&
                pad.userData &&
                pad.userData.upgrade &&
                typeof window.purchaseUpgrade === 'function'
            ) {
                window.purchaseUpgrade(pad.userData.upgrade);
            }
        });

        action('mobile-wake', () => {
            if (typeof window.wakeNearbyAgent === 'function') {
                window.wakeNearbyAgent();
            }
        });

        action('mobile-pause', () => {
            if (typeof window.togglePause === 'function') {
                window.togglePause();
            }
        });

        root.querySelectorAll('.mobile-speed-button').forEach(button => {
            button.addEventListener('pointerdown', e => {
                e.preventDefault();
                e.stopPropagation();

                const speed = Number(button.dataset.speed);

                if (typeof window.setSpeed === 'function') {
                    window.setSpeed(speed);
                }

                root
                    .querySelectorAll('.mobile-speed-button')
                    .forEach(b => b.classList.remove('active'));

                button.classList.add('active');
            }, { passive: false });
        });

        root.addEventListener('touchmove', e => {
            e.preventDefault();
        }, { passive: false });

        root.addEventListener('contextmenu', e => {
            e.preventDefault();
        });

        console.log('📱 Mobile Controls V5 initialized');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setup);
    } else {
        setup();
    }

})();

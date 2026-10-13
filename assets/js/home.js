// Homepage motion (index.html only): scroll reveals, stat count-up,
// magnetic primary buttons, cursor spotlight on work cards, and the
// experience route that fills as you scroll. Everything is skipped under
// prefers-reduced-motion; content is fully visible without this file.
(function () {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const main = document.getElementById('main');
    if (!main || reduce || !('IntersectionObserver' in window)) return;

    // Scroll reveal: hide only once JS is known to be running.
    function reveal() {
        const els = main.querySelectorAll('.rv');
        document.documentElement.classList.add('js-rv');
        const io = new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (!e.isIntersecting) return;
                e.target.classList.add('in');
                io.unobserve(e.target);
            });
        }, { rootMargin: '0px 0px -60px 0px' });
        els.forEach(el => io.observe(el));
    }

    // Count stat numbers up from zero when the band comes into view.
    function countUp() {
        const nums = main.querySelectorAll('[data-count]');
        const io = new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (!e.isIntersecting) return;
                io.unobserve(e.target);
                const el = e.target;
                const to = parseFloat(el.dataset.count);
                const dec = parseInt(el.dataset.dec || '0', 10);
                const start = performance.now();
                const dur = 1400;
                (function step(now) {
                    const t = Math.min(1, (now - start) / dur);
                    const eased = 1 - Math.pow(1 - t, 4);
                    el.textContent = (to * eased).toFixed(dec);
                    if (t < 1) requestAnimationFrame(step);
                })(start);
            });
        }, { threshold: 0.6 });
        nums.forEach(n => io.observe(n));
    }

    // Magnetic CTA: the wrapper leans toward the pointer, springs back on leave.
    function magnets() {
        if (!window.matchMedia('(hover: hover)').matches) return;
        main.querySelectorAll('.magnet').forEach(m => {
            const strength = 6;
            m.addEventListener('pointermove', e => {
                const r = m.getBoundingClientRect();
                const s = Math.max(r.width, r.height);
                const dx = (e.clientX - (r.left + r.width / 2)) / s;
                const dy = (e.clientY - (r.top + r.height / 2)) / s;
                m.style.transform = `translate(${dx * strength * 2}px, ${dy * strength * 2}px)`;
            });
            m.addEventListener('pointerleave', () => { m.style.transform = ''; });
        });
    }

    // Spotlight that follows the cursor across a work card.
    function spotlight() {
        main.querySelectorAll('.feat').forEach(card => {
            card.addEventListener('pointermove', e => {
                const r = card.getBoundingClientRect();
                card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
                card.style.setProperty('--my', (e.clientY - r.top) + 'px');
            });
        });
    }

    // Experience route: line fills to the viewport midpoint; stops light as passed.
    function route() {
        const ol = document.getElementById('route');
        if (!ol) return;
        const stops = [...ol.querySelectorAll('.stop')];
        let queued = false;
        function paint() {
            queued = false;
            const r = ol.getBoundingClientRect();
            const mid = window.innerHeight * 0.55;
            const p = Math.max(0, Math.min(1, (mid - r.top) / r.height));
            ol.style.setProperty('--p', p.toFixed(4));
            stops.forEach(s => s.classList.toggle('passed', s.getBoundingClientRect().top + 10 < mid));
        }
        function onScroll() { if (!queued) { queued = true; requestAnimationFrame(paint); } }
        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', onScroll);
        paint();
    }

    reveal();
    countUp();
    magnets();
    spotlight();
    route();
})();

// IDE shell behaviour shared by every page: builds the file tree, expands the
// current page's sections, scroll-spy (tree + crumb + status bar), mobile
// drawer, theme chip, and the typed role line on the homepage.
(function() {
    const SITE = [
        { path: '/', label: 'about', file: '~/about.md' },
        { path: '/projects/', label: 'projects/', file: '~/projects/' },
        { path: '/opensource/', label: 'opensource/', file: '~/opensource/' },
        { path: '/projects/#blog', label: 'writing/', file: '~/writing/' },
        { path: '/trending-gitrepos/', label: 'trending/', file: '~/trending/' },
        { path: '/contact/', label: 'contact', file: '~/contact.md' }
    ];

    const here = location.pathname.replace(/index\.html$/, '');
    const page = SITE.find(p => p.path === here) || null;
    const main = document.querySelector('main');

    // In-page sections: explicit data-file sections, else <section id> with a heading.
    function sections() {
        if (!main) return [];
        let list = [...main.querySelectorAll('section[id][data-file]')];
        if (!list.length) {
            list = [...main.querySelectorAll('section[id]')].filter(s => s.querySelector('h2'));
            list.forEach(s => {
                s.dataset.file = (page ? page.file : '~/') + s.id;
                s.dataset.label = s.querySelector('h2').textContent.trim().toLowerCase();
            });
        }
        return list;
    }

    function esc(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

    function buildTree(secs) {
        const tree = document.getElementById('tree');
        if (!tree || tree.dataset.static === 'true') return;
        const items = SITE.map(p => {
            const isHere = page && p === page;
            let sub = '';
            if (isHere && secs.length) {
                sub = '<ul class="sub">' + secs.map(s =>
                    `<li><a href="#${s.id}">${esc(s.dataset.label || s.id)}</a></li>`).join('') + '</ul>';
            }
            return `<li class="${isHere ? 'here' : ''}"><a href="${p.path}"${isHere ? ' aria-current="page"' : ''}>${p.label}</a>${sub}</li>`;
        }).join('');
        tree.insertAdjacentHTML('afterbegin', `<nav class="tree-nav" aria-label="Site"><ul>${items}</ul></nav>`);
    }

    function cmdLine() {
        const h1 = document.querySelector('.page-header h1');
        if (!h1 || !page || document.querySelector('.page-header .cmd')) return;
        const p = document.createElement('p');
        p.className = 'cmd';
        p.textContent = '$ cd ' + page.file;
        h1.before(p);
    }

    function drawer() {
        const btn = document.getElementById('menu-btn');
        const tree = document.getElementById('tree');
        if (!btn || !tree) return;
        btn.addEventListener('click', () => {
            const open = document.body.classList.toggle('tree-open');
            btn.setAttribute('aria-expanded', open);
        });
        tree.addEventListener('click', e => {
            if (!e.target.closest('a')) return;
            document.body.classList.remove('tree-open');
            btn.setAttribute('aria-expanded', 'false');
        });
    }

    function themeChip() {
        const btn = document.getElementById('theme-btn');
        if (!btn) return;
        function paint() {
            const t = document.documentElement.getAttribute('data-theme');
            btn.querySelectorAll('[data-t]').forEach(s => { s.className = s.dataset.t === t ? 'on' : 'off'; });
        }
        new MutationObserver(paint).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
        paint();
    }

    function typed() {
        const el = document.getElementById('typed');
        if (!el || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        const roles = (el.dataset.roles || el.textContent).split('|');
        if (roles.length < 2) return;
        let r = 0, i = roles[0].length, del = true;
        function tick() {
            const word = roles[r];
            i += del ? -1 : 1;
            el.textContent = word.slice(0, i);
            let wait = del ? 35 : 70;
            if (!del && i === word.length) { del = true; wait = 2200; }
            else if (del && i === 0) { del = false; r = (r + 1) % roles.length; wait = 350; }
            setTimeout(tick, wait);
        }
        el.textContent = roles[0];
        setTimeout(tick, 2600);
    }

    function spy(secs) {
        const crumb = document.getElementById('crumb');
        const status = document.getElementById('status-file');
        const base = page ? page.file : '~/';
        if (crumb) crumb.textContent = base;
        if (status) status.textContent = base;
        if (!secs.length || !('IntersectionObserver' in window)) return;
        const links = document.querySelectorAll('.tree a[href^="#"]');
        const io = new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (!e.isIntersecting) return;
                const file = e.target.dataset.file;
                if (crumb) crumb.textContent = file;
                if (status) status.textContent = file;
                let marked = false;
                links.forEach(a => {
                    const hit = !marked && a.getAttribute('href') === '#' + e.target.id;
                    a.classList.toggle('current', hit);
                    if (hit) marked = true;
                });
            });
        }, { rootMargin: '-45% 0px -50% 0px' });
        secs.forEach(s => io.observe(s));
    }

    function init() {
        const secs = sections();
        buildTree(secs);
        cmdLine();
        drawer();
        themeChip();
        typed();
        spy(secs);
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();

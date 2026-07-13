#!/usr/bin/env node
/**
 * render.mjs — build /trending-gitrepos/index.html.
 *
 * Enterprise dashboard styling on top of the sudhakarchundu.org design system:
 * loads the site's assets/css/style.css (NVIDIA-green accent, dark/light themes,
 * Mona Sans + JetBrains Mono), reuses its nav / footer / neural-bg / theme
 * toggle and .kpi-* components, and adds a page-scoped card grid + velocity bars
 * built entirely on the site's CSS tokens (so both themes stay correct).
 *
 * Run (called by fetch.mjs after each refresh):
 *   node trending-gitrepos/scripts/render.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

// Layout: <site>/trending-gitrepos/scripts/render.mjs -> BASE = trending-gitrepos/
const BASE = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const JSON_PATH = resolve(BASE, 'data/trending.json');
const HTML_PATH = resolve(BASE, 'index.html');

const esc = (s) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
const fmt = (n) => Number(n).toLocaleString('en-US');

// Nav + footer copied verbatim from the site's subpages so chrome is identical.
const NAV = `
    <nav>
        <div class="nav-container">
            <a href="../" class="logo">
                <img src="../assets/images/profile.jpg" alt="Sudhakar Chundu" class="logo-icon">
                Sudhakar Chundu
            </a>
            <ul class="nav-links">
                <li><a href="../">Overview</a></li>
                <li><a href="../projects/">Projects</a></li>
                <li><a href="../opensource/">Open Source</a></li>
                <li><a href="./" class="active">Trending</a></li>
                <div class="nav-social">
                    <a href="https://github.com/schundu007" target="_blank" rel="noopener noreferrer" title="GitHub"><i class="fab fa-github"></i></a>
                    <a href="https://www.linkedin.com/in/babucs/" target="_blank" rel="noopener noreferrer" title="LinkedIn"><i class="fab fa-linkedin"></i></a>
                </div>
                <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
                    <i class="fas fa-moon"></i>
                    <i class="fas fa-sun"></i>
                </button>
                <div class="nav-auth">
                    <button class="btn-signin" onclick="showLoginModal()">Sign In</button>
                </div>
            </ul>
            <button class="mobile-menu-btn" aria-label="Menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>`;

const FOOTER = `
    <footer>
        <div class="footer-content">
            <span class="footer-logo">Sudhakar Chundu</span>
            <div class="footer-links">
                <a href="../#resume">Resume</a>
                <a href="../projects/">Projects</a>
                <a href="./">Trending</a>
                <a href="../contact/">Contact</a>
            </div>
            <div class="footer-social">
                <a href="https://github.com/schundu007" target="_blank" rel="noopener noreferrer" title="GitHub"><i class="fab fa-github"></i></a>
                <a href="https://www.linkedin.com/in/babucs/" target="_blank" rel="noopener noreferrer" title="LinkedIn"><i class="fab fa-linkedin"></i></a>
                <a href="https://schundu.medium.com/" target="_blank" rel="noopener noreferrer" title="Medium"><i class="fab fa-medium"></i></a>
            </div>
        </div>
        <p>&copy; 2026 Sudhakar Chundu. All rights reserved.</p>
    </footer>`;

const STYLE = `
    <style>
        /* ============ Trending page — enterprise layout on site tokens ============ */
        .main-content { max-width: 1360px; }

        /* Hero */
        .tg-hero { position: relative; }
        .tg-hero h1 { font-size: 2.75rem; line-height: 1.05; letter-spacing: -0.03em; margin: 0 0 0.5rem; }
        .tg-hero .tg-lead { font-size: 1.1rem; line-height: 1.6; color: var(--text-secondary); max-width: 72ch; margin: 0 0 1.5rem; }
        .tg-hero .tg-lead strong { color: var(--text-primary); }
        .tg-kpis { margin: 0 0 1.75rem; }
        .tg-kpis .kpi-value { font-size: 1.6rem; }

        /* Sticky category nav */
        .tg-catnav {
            display: flex; flex-wrap: wrap; gap: 0.5rem;
            padding: 0.25rem 0 1rem; margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--bg-tertiary);
        }
        .tg-catnav a {
            display: inline-flex; align-items: center; gap: 0.45rem;
            font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
            padding: 0.4rem 0.85rem; border-radius: var(--radius-full);
            color: var(--text-secondary); background: var(--bg-secondary);
            border: 1px solid var(--bg-tertiary); text-decoration: none;
            transition: var(--transition-fast);
        }
        .tg-catnav a:hover { color: var(--text-primary); border-color: var(--glass-border-hover); }
        .tg-catnav a .n { font-size: 0.7rem; color: var(--text-muted); }

        /* Category section */
        .tg-section { margin-top: 2.75rem; scroll-margin-top: 90px; }
        .tg-sec-head { display: flex; align-items: baseline; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.1rem; padding-bottom: 0.75rem; border-bottom: 2px solid var(--bg-tertiary); }
        .tg-sec-head h2 { font-size: 1.6rem; letter-spacing: -0.02em; margin: 0; }
        .tg-count { font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; color: var(--accent-highlight); background: rgba(118,185,0,0.12); padding: 0.15rem 0.55rem; border-radius: var(--radius-full); }
        .tg-topics-line { font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); margin-left: auto; }

        /* Card grid */
        .tg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.1rem; }
        .tg-card {
            display: flex; flex-direction: column; gap: 0.7rem;
            background: var(--bg-card); border: 1px solid var(--bg-tertiary);
            border-radius: var(--radius-lg); padding: 1.15rem 1.2rem;
            box-shadow: var(--shadow-sm); transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
        }
        .tg-card:hover { transform: translateY(-3px); border-color: var(--glass-border-hover); box-shadow: var(--shadow-md); }
        .tg-card--lead { border-color: var(--accent-highlight); box-shadow: var(--glow-ai); }

        .tg-card-top { display: flex; align-items: center; gap: 0.6rem; }
        .tg-rank { display: inline-flex; align-items: center; justify-content: center; min-width: 2rem; height: 2rem; padding: 0 0.4rem; border-radius: var(--radius-md); font-family: var(--font-mono); font-size: 0.85rem; font-weight: 800; color: var(--text-secondary); background: var(--bg-secondary); border: 1px solid var(--bg-tertiary); }
        .tg-card--lead .tg-rank { color: #0d1117; background: var(--gradient-primary); border-color: transparent; }
        .tg-lang { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-muted); display: inline-flex; align-items: center; gap: 0.35rem; }
        .tg-lang.empty { visibility: hidden; }
        .tg-updated { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-muted); margin-left: auto; white-space: nowrap; }

        .tg-name { font-size: 1.12rem; font-weight: 700; line-height: 1.3; color: var(--text-primary); text-decoration: none; display: inline-flex; align-items: center; gap: 0.45rem; word-break: break-word; }
        .tg-name:hover { color: var(--accent-highlight); }
        .tg-name i { font-size: 0.7rem; opacity: 0.5; }
        .tg-desc { font-size: 0.95rem; line-height: 1.55; color: var(--text-secondary); margin: 0; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

        .tg-metrics { display: grid; grid-template-columns: auto 1fr; gap: 0.4rem 1.2rem; align-items: end; margin-top: auto; padding-top: 0.6rem; }
        .tg-stars { font-family: var(--font-mono); font-size: 1.5rem; font-weight: 800; color: var(--text-primary); line-height: 1; font-variant-numeric: tabular-nums; white-space: nowrap; }
        .tg-stars i { color: var(--accent-highlight); font-size: 1rem; margin-right: 0.2rem; }
        .tg-stars .lab { display: block; font-size: 0.65rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; margin-top: 0.25rem; }
        .tg-vel { min-width: 0; }
        .tg-vel .val { font-family: var(--font-mono); font-size: 0.9rem; font-weight: 700; color: var(--accent-highlight); font-variant-numeric: tabular-nums; }
        .tg-vel .lab { font-size: 0.65rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; margin-left: 0.4rem; }
        .tg-bar { height: 6px; border-radius: var(--radius-full); background: var(--bg-tertiary); overflow: hidden; margin-top: 0.4rem; }
        .tg-bar > span { display: block; height: 100%; border-radius: var(--radius-full); background: var(--gradient-primary); }

        .tg-topics { display: flex; flex-wrap: wrap; gap: 0.4rem; }
        .tg-chip { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-secondary); background: var(--bg-secondary); border: 1px solid var(--bg-tertiary); padding: 0.15rem 0.55rem; border-radius: var(--radius-full); }

        @media (max-width: 820px) {
            .tg-hero h1 { font-size: 2.1rem; }
            .tg-grid { grid-template-columns: 1fr; }
            .tg-topics-line { display: none; }
        }
    </style>`;

export function renderHtml(data) {
  const updated = (data.generated_at || '').slice(0, 10);
  const totalRepos = data.categories.reduce((a, c) => a + c.repos.length, 0);

  const catNav = data.categories
    .map((c) => `<a href="#${esc(c.key)}">${esc(c.title)} <span class="n">${c.repos.length}</span></a>`)
    .join('');

  const sections = data.categories
    .map((cat) => {
      const maxVel = Math.max(1, ...cat.repos.map((r) => r.velocity_per_month || 0));
      const cards = cat.repos
        .map((r) => {
          const pct = Math.max(6, Math.round(((r.velocity_per_month || 0) / maxVel) * 100));
          const chips = (r.topics || [])
            .slice(0, 5)
            .map((t) => `<span class="tg-chip">${esc(t)}</span>`)
            .join('');
          return `
                <article class="tg-card${r.rank === 1 ? ' tg-card--lead' : ''}">
                    <div class="tg-card-top">
                        <span class="tg-rank">#${r.rank}</span>
                        <span class="tg-lang${r.language ? '' : ' empty'}"><i class="fas fa-circle" aria-hidden="true" style="font-size:0.5rem;color:var(--accent-highlight)"></i> ${esc(r.language) || '&nbsp;'}</span>
                        <span class="tg-updated"><i class="fas fa-rotate" aria-hidden="true"></i> ${esc((r.pushed_at || '').slice(0, 10))}</span>
                    </div>
                    <a class="tg-name" href="${esc(r.html_url)}" target="_blank" rel="noopener noreferrer">${esc(r.full_name)} <i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
                    <p class="tg-desc">${esc(r.description) || '&mdash;'}</p>
                    <div class="tg-metrics">
                        <div class="tg-stars"><i class="fas fa-star" aria-hidden="true"></i>${fmt(r.stars)}<span class="lab">stars</span></div>
                        <div class="tg-vel">
                            <span class="val">${fmt(r.velocity_per_month)}</span><span class="lab">★ / month</span>
                            <div class="tg-bar"><span style="width:${pct}%"></span></div>
                        </div>
                    </div>
                    ${chips ? `<div class="tg-topics">${chips}</div>` : ''}
                </article>`;
        })
        .join('');
      return `
        <section class="tg-section" id="${esc(cat.key)}">
            <div class="tg-sec-head">
                <h2>${esc(cat.title)}</h2>
                <span class="tg-count">${cat.repos.length} repos</span>
                <span class="tg-topics-line">${cat.queried_topics.map((t) => esc(t)).join(' · ')}</span>
            </div>
            <div class="tg-grid">${cards}
            </div>
        </section>`;
    })
    .join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNQHMGCLH"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-GGNQHMGCLH');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trending GitHub Repos | Sudhakar Chundu</title>
    <meta name="description" content="Weekly-maintained top-10 trending GitHub repositories across DevOps, Platform Engineering, MLOps, SRE, LLMOps, and GPU infrastructure, ranked by star velocity.">
    <link rel="icon" type="image/x-icon" href="../favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Mona+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="../assets/css/style.css?v=12">
    <!-- Theme JS (load early to prevent flash) -->
    <script src="../assets/js/theme.js"></script>

    <!-- Firebase SDK (for the shared Sign In button in the nav) -->
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore-compat.js"></script>
${STYLE}
</head>
<body>
    <!-- Neural Network Background -->
    <canvas id="neural-bg"></canvas>
${NAV}

    <main class="main-content">
        <header class="page-header tg-hero">
            <h1>Trending GitHub Repos</h1>
            <p class="tg-lead">Top ${esc(data.top_n)} per category across DevOps, Platform Engineering, MLOps, SRE, LLMOps, and GPU infrastructure &mdash; ranked by <strong>star velocity</strong> (average stars gained per month over each repo's lifetime, so fast risers beat all-time giants).</p>
            <div class="kpi-strip tg-kpis">
                <div class="kpi-cell"><div class="kpi-value">${totalRepos}</div><div class="kpi-label">Repos tracked</div></div>
                <div class="kpi-cell"><div class="kpi-value">${data.categories.length}</div><div class="kpi-label">Categories</div></div>
                <div class="kpi-cell"><div class="kpi-value">&#9733;/mo</div><div class="kpi-label">Ranked by velocity</div></div>
                <div class="kpi-cell"><div class="kpi-value">${esc(updated)}</div><div class="kpi-label">Last updated</div></div>
            </div>
        </header>

        <nav class="tg-catnav" aria-label="Categories">${catNav}</nav>
${sections}
    </main>
${FOOTER}

    <!-- Firebase Config and Auth (shared nav Sign In) -->
    <script src="../assets/js/firebase-config.js"></script>
    <script src="../assets/js/auth.js"></script>

    <script>
        // Mobile menu toggle (same behavior as the rest of the site)
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const navLinks = document.querySelector('.nav-links');
        if (mobileMenuBtn && navLinks) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenuBtn.classList.toggle('active');
                navLinks.classList.toggle('active');
            });
            navLinks.querySelectorAll('a').forEach((link) => {
                link.addEventListener('click', () => {
                    mobileMenuBtn.classList.remove('active');
                    navLinks.classList.remove('active');
                });
            });
        }
    </script>
    <!-- Neural Network Background -->
    <script src="../assets/js/neural-bg.js"></script>
</body>
</html>
`;
}

// CLI: read the committed JSON and write index.html.
if (import.meta.url === `file://${process.argv[1]}`) {
  const data = JSON.parse(readFileSync(JSON_PATH, 'utf8'));
  writeFileSync(HTML_PATH, renderHtml(data));
  console.error(`Wrote ${HTML_PATH}`);
}

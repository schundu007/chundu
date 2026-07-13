#!/usr/bin/env node
/**
 * render.mjs — build /trending-gitrepos/index.html.
 *
 * Styled to match the sudhakarchundu.org site: it loads the site's own
 * assets/css/style.css, fonts, nav, footer, neural-bg, and theme toggle, and
 * renders the repos with the site's native components (.section / .panel /
 * .ledger-row / .tag). Only a few page-specific helpers are added inline,
 * built on the site's CSS tokens.
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

export function renderHtml(data) {
  const updated = (data.generated_at || '').slice(0, 10);

  const catNav = data.categories
    .map((c) => `<a class="tag" href="#${esc(c.key)}">${esc(c.title)}</a>`)
    .join('');

  const sections = data.categories
    .map((cat) => {
      const rows = cat.repos
        .map((r) => {
          const tags = (r.topics || [])
            .slice(0, 5)
            .map((t) => `<span class="tag">${esc(t)}</span>`)
            .join('');
          const facts = [
            `<span><i class="fas fa-bolt" aria-hidden="true"></i> ${fmt(r.velocity_per_month)} ★/mo</span>`,
            r.language ? `<span><i class="fas fa-code" aria-hidden="true"></i> ${esc(r.language)}</span>` : '',
            `<span><i class="fas fa-rotate" aria-hidden="true"></i> ${esc((r.pushed_at || '').slice(0, 10))}</span>`,
          ].filter(Boolean).join('');
          return `
                <div class="ledger-row repo-row">
                    <div class="ledger-meta">
                        <span class="repo-rank">#${r.rank}</span>
                        <span class="repo-stars"><i class="fas fa-star" aria-hidden="true"></i> ${fmt(r.stars)}</span>
                    </div>
                    <div>
                        <div class="ledger-title"><a class="ledger-link" href="${esc(r.html_url)}" target="_blank" rel="noopener noreferrer">${esc(r.full_name)} <i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
                        <div class="ledger-sub">${esc(r.description) || '&mdash;'}</div>
                        <div class="repo-facts">${facts}</div>
                        ${tags ? `<div class="row-tags">${tags}</div>` : ''}
                    </div>
                </div>`;
        })
        .join('');
      return `
        <section class="section" id="${esc(cat.key)}">
            <div class="section-header">
                <h2>${esc(cat.title)}</h2>
                <p>Topics: ${cat.queried_topics.map((t) => `<code>${esc(t)}</code>`).join(', ')}</p>
            </div>
            <div class="panel">${rows}
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

    <style>
        /* Trending page — built on the site's own CSS tokens */
        .cat-nav { display: flex; flex-wrap: wrap; gap: 0.375rem; margin: 0.75rem 0 0; }
        .section-header p code { font-family: var(--font-mono); font-size: 0.6875rem; color: var(--text-secondary); }
        .repo-row .ledger-meta { display: flex; flex-direction: column; gap: 0.25rem; align-items: flex-start; }
        .repo-rank { font-family: var(--font-mono); font-size: 0.6875rem; font-weight: 700; letter-spacing: 0.06em; color: var(--text-muted); }
        .repo-stars { font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; color: var(--accent-highlight, var(--accent-blue)); white-space: nowrap; }
        .ledger-title .ledger-link { display: inline-flex; align-items: center; gap: 0.4rem; }
        .ledger-title .ledger-link i { font-size: 0.625rem; opacity: 0.55; }
        .repo-facts { display: flex; flex-wrap: wrap; gap: 0.25rem 1.1rem; font-family: var(--font-mono); font-size: 0.6875rem; color: var(--text-muted); margin: 0.375rem 0 0.5rem; }
        .repo-facts i { opacity: 0.7; margin-right: 0.15rem; }
    </style>
</head>
<body>
    <!-- Neural Network Background -->
    <canvas id="neural-bg"></canvas>
${NAV}

    <main class="main-content">
        <header class="page-header">
            <h1>Trending GitHub Repos</h1>
            <p>Top ${esc(data.top_n)} per category across DevOps, Platform Engineering, MLOps, SRE, LLMOps, and GPU infrastructure &mdash; ranked by <strong>star velocity</strong> (average stars gained per month over each repo's lifetime, so fast risers beat all-time giants). Auto-refreshed weekly &middot; last updated <strong>${esc(updated)}</strong>.</p>
            <div class="cat-nav">${catNav}</div>
        </header>
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

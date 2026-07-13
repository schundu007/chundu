#!/usr/bin/env node
/**
 * build-directory.mjs — regenerate the "Live Apps & Tools" directory on the
 * homepage so shipped apps never get lost.
 *
 * Auto-discovers your PUBLIC, non-fork repos that have a homepage URL set
 * (via the public GitHub API, so it runs identically locally and in CI where
 * the token can only read public data), plus a small PINNED list for on-site
 * pages and private-repo apps. Writes directory/links.json and injects the
 * cards into index.html between the <!-- DIRECTORY:START/END --> markers.
 *
 * Run:  GITHUB_TOKEN=$(gh auth token) node directory/scripts/build-directory.mjs
 * (Token is optional — only raises the API rate limit.)
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..'); // repo root
const INDEX = resolve(ROOT, 'index.html');
const JSON_OUT = resolve(ROOT, 'directory/links.json');
const USER = 'schundu007';

const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || '';
const esc = (s) =>
  String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Friendly labels for known repos; anything else Title-cases the repo name.
const LABELS = {
  camora: 'Camora',
  lumora: 'Lumora',
  capra: 'Capra',
  'git-dboard': 'IsaacLab DevOps Dashboard',
};
const IGNORE = new Set(['chundu', 'git-dboard']); // site itself; git-dboard superseded by GitPulser

// Always present: on-site pages + apps whose repo is private (not in public API).
const PINNED = [
  { name: 'Trending GitHub Repos', url: '/trending-gitrepos/', description: 'Weekly-ranked trending repos across DevOps, Platform, MLOps, SRE, LLMOps, and GPU infra.', host: 'sudhakarchundu.org/trending-gitrepos' },
  { name: 'Cariara', url: 'https://jobs.cariara.com', description: 'AI-powered job portal — discovery, matching, and auto-apply.', host: 'jobs.cariara.com' },
  { name: 'GitPulser', url: 'https://gitpulser.vercel.app/dashboard', description: 'GitHub activity & PR pulse dashboard.', host: 'gitpulser.vercel.app/dashboard' },
];

const titleCase = (n) => n.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
const hostOf = (u) => {
  try {
    const x = new URL(u);
    return (x.host + (x.pathname !== '/' ? x.pathname : '')).replace(/^www\./, '').replace(/\/$/, '');
  } catch {
    return String(u).replace(/^https?:\/\//, '').replace(/\/$/, '');
  }
};

async function fetchRepos() {
  const headers = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'chundu-directory',
    ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
  };
  const out = [];
  for (let page = 1; page <= 5; page++) {
    const res = await fetch(`https://api.github.com/users/${USER}/repos?type=owner&per_page=100&sort=pushed&page=${page}`, { headers });
    if (!res.ok) throw new Error(`GitHub ${res.status}: ${await res.text()}`);
    const arr = await res.json();
    out.push(...arr);
    if (arr.length < 100) break;
  }
  return out;
}

function renderCards(entries) {
  return entries
    .map((e) => {
      const external = /^https?:\/\//.test(e.url);
      return `                <a class="dir-card" href="${esc(e.url)}"${external ? ' target="_blank" rel="noopener noreferrer"' : ''}>
                    <div class="dir-card-top"><span class="dir-name">${esc(e.name)}</span><i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i></div>
                    ${e.description ? `<p class="dir-desc">${esc(e.description)}</p>` : ''}
                    <span class="dir-url">${esc(e.host)}</span>
                </a>`;
    })
    .join('\n');
}

const START = '<!-- DIRECTORY:START -->';
const END = '<!-- DIRECTORY:END -->';

async function main() {
  const repos = await fetchRepos();
  const apps = repos
    .filter((r) => !r.fork && !r.archived && !IGNORE.has(r.name) && r.homepage && /^https?:\/\//.test(r.homepage))
    .map((r) => ({
      name: LABELS[r.name] || titleCase(r.name),
      url: r.homepage,
      description: (r.description || '').trim(),
      host: hostOf(r.homepage),
      ts: new Date(r.pushed_at).getTime(),
    }))
    .sort((a, b) => b.ts - a.ts);

  const entries = [...PINNED, ...apps];

  mkdirSync(dirname(JSON_OUT), { recursive: true });
  writeFileSync(
    JSON_OUT,
    JSON.stringify({ generated_at: new Date().toISOString(), count: entries.length, entries }, null, 2) + '\n',
  );

  const html = readFileSync(INDEX, 'utf8');
  const s = html.indexOf(START);
  const e = html.indexOf(END);
  if (s === -1 || e === -1 || e < s) {
    console.error('ERROR: DIRECTORY markers not found in index.html — aborting without changes.');
    process.exit(1);
  }
  const next = html.slice(0, s + START.length) + '\n' + renderCards(entries) + '\n                ' + html.slice(e);
  writeFileSync(INDEX, next);

  console.error(`Directory: ${entries.length} entries (${apps.length} auto + ${PINNED.length} pinned)`);
  entries.forEach((x) => console.error(`  - ${x.name.padEnd(28)} ${x.url}`));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

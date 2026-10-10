# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website for Sudhakar Chundu hosted on GitHub Pages at [www.sudhakarchundu.org](https://www.sudhakarchundu.org/). The site showcases cloud infrastructure and DevOps expertise. It includes a static frontend, a FastAPI backend for job tracking, and a Python CLI tool for automated job searching.

## Development Commands

### Frontend Development
```bash
# Start local server (port 8000)
python -m http.server 8000
# Then open http://localhost:8000
```
No build step required — edit HTML/CSS/JS and refresh.

### Database Setup
```bash
# Create PostgreSQL database
createdb job_search

# Run schema
psql job_search < api/schema.sql
```

### API Backend
```bash
cd api
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings

# Start API server (port 8001)
uvicorn main:app --reload --port 8001
```

### Job Automation Tool (tools/)
```bash
cd tools
pip install -r requirements.txt

# Basic job search
python job_automation.py

# Search with custom keywords
python job_automation.py -k "Platform Engineering Kubernetes"

# Generate cover letters and resumes for top matches
python job_automation.py --generate --top 5

# Custom output directory
python job_automation.py -o my_results
```

### Environment Variables
Copy `api/.env.example` to `api/.env` and configure:
- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://localhost:5432/job_search`)
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - for AI-powered document generation
- `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` - for Adzuna job search API
- `ALLOWED_ORIGINS` - comma-separated CORS origins (default: `http://localhost:8000,https://www.sudhakarchundu.org`)
- `API_HOST` / `API_PORT` - API bind settings (default: `0.0.0.0:8001`)

## Architecture

### Static Website Structure

The frontend is a static HTML/CSS/JS site served via GitHub Pages. No build step or framework.

**Main pages:**
- `index.html` - Single-page overview in an IDE-style shell (sticky top bar, file-tree sidebar with scroll-spy, vim-like status bar): `$ cat ~/about.md` hero with typed role line, `~/experience` + credentials/education, `~/work` (3 headline projects + earlier list), the auto-generated `~/apps` directory, recommendations, and `~/contact` with the `#resume` card. Its tree is hand-written (`data-static="true"`)
- `404.html` - Terminal-style 404 (`cd: no such file or directory`) with a did-you-mean suggestion; served for any missing path, so all its URLs are absolute. GitHub Pages only supports a custom 404 — 403/5xx responses come from GitHub's edge and cannot be customised
- `projects/index.html` - Enterprise projects, conference talks, publications, and the blog index (anchors: `#conferences`, `#publications`, `#blog`)
- `opensource/index.html` - Upstream OSDU contributions, GitHub repos/gists (live API), and Medium articles
- `contact/index.html` - Contact channels
- `trending-gitrepos/index.html` - Weekly-refreshed trending repo rankings (generated)
- `blog/*.html` - Standalone long-form engineering deep dives
- `jobs/index.html` - Job listings page with `JobsAPI` client connecting to backend API (falls back to localStorage if API unavailable)
- `jobs/applied/index.html` - Applied jobs tracker

**Redirect stubs** (meta-refresh, kept for old inbound links — do not add content here):
`about/` → `/#about`, `resume/` → `/#resume`, `profile/` → `/`,
`blog/` → `/projects/#blog`, `conferences/` → `/projects/#conferences`,
`publications/` → `/projects/#publications`

**Content accuracy:** `PORTFOLIO_MASTER.md` at the repo root is the canonical fact
sheet (roles, dates, metrics, certs, links) derived from the resumes. Any claim
added to the site must match it; update that file first if a fact changes.

**Generated content — edit the generator, not the output:**
- `directory/scripts/build-directory.mjs` → writes `directory/links.json` and injects
  the Live Apps cards into `index.html` between the `<!-- DIRECTORY:START/END -->` markers.
  Pinned apps live in the `PINNED` array. Run:
  `GITHUB_TOKEN=$(gh auth token) node directory/scripts/build-directory.mjs`
- `trending-gitrepos/scripts/render.mjs` → renders `trending-gitrepos/index.html`.
  Contains hard-coded social links; update them there too.

**Site-wide files:** `favicon.ico`, `apple-touch-icon.png`, `robots.txt`, `sitemap.xml`
(regenerate the sitemap when adding a page); JSON-LD `Person` schema lives in `index.html`.

**Shared assets:**
- `assets/css/style.css` - Global design system (~1,760 lines) using CSS custom properties; dark (default) and light themes with glassmorphism effects, gradient accents, and responsive breakpoints
- `assets/css/genz.css` - **The look (loaded last on every page):** Google, Gen-Z register. Google Sans display at 500 weight, Google's four colours only as accents (blue primary action/links, green status, the four-colour rule and Gemini backdrop glow), all text ink/grey, 1px hairlines, 20–28px cards, pill controls. It remaps style.css's tokens under `html[data-theme]`, so a page must load `theme.js`; standalone blog posts carry the same tokens in their own inline CSS. Each fact/label appears once per page (no repeated banners, tags or stats).
- `assets/css/shell.css` + `assets/js/shell.js` - **IDE shell chrome on every page** (load after genz.css). All classes are `sh-` prefixed so it can sit on pages with their own CSS, and chrome link styles are pinned with `!important`. Two variants:
  - *Full shell* (index, projects, opensource, contact, trending, 404, MLOps + iOS posts): `header.sh-topbar` → `div.sh-shell > aside.sh-tree#tree + main#main` → `footer.sh-status`.
  - *Drawer* (`body.sh-drawer` — long-form posts with their own TOC/layout, and the jobs dashboards): top bar + status bar, tree slides in from the menu button. Each post carries a small inline `<style>` that moves its own sticky bars/sidebars below the 56px top bar.
  shell.js fills the tree from its `SITE` list (and `POSTS` under writing/ — add new posts there), expands the current page's `section[id]` headings, adds the `$ cd`/`$ cat` line above `.page-header h1`, and runs scroll-spy (crumb + status bar), drawer and theme chip. `body[data-file]` overrides the crumb; `body[data-toc="auto"]` lists a post's sections in the tree. Pages without `data-theme` (most posts) get light chrome tokens and no theme chip.
- **Type scale** (end of shell.css, px tokens because style.css pages set an 18px root): `--t-display` 40–52 (page h1; homepage name steps up to 64), `--t-h2` 24 (section headings, `~/` accent), `--t-h3` 18 (panel/card titles), `--t-lead` 17, `--t-body` 15, `--t-meta` 12.5 mono, `--t-label` 11 uppercase. New page content should use these tokens instead of its own sizes.
- **Cache-busting:** GitHub Pages serves assets with `max-age=14400` (4 h). Every page links shell.css / home.css / shell.js with `?v=<stamp>`; after editing any of them, bump the stamp everywhere (all pages + `trending-gitrepos/scripts/render.mjs`) or returning visitors get stale CSS against new markup.
- `assets/css/home.css` - Homepage-only content styles (hero, ~/experience, ~/work, ~/apps cards, contact/resume).
- `assets/js/theme.js` - Theme toggle (dark/light mode persistence via localStorage, key: `portfolio-theme`)
- `assets/js/neural-bg.js` - Animated neural network canvas background (`NeuralNetwork` class with particles and mouse interaction)
- `assets/js/firebase-config.js` - Firebase initialization (Firestore + Auth); gracefully falls back when not configured
- `assets/js/auth.js` - Firebase authentication module (Google, GitHub, Facebook sign-in); provides stub functions when Firebase is unconfigured
- `assets/js/comments.js` - Firestore-backed comments system scoped by page URL
- `assets/icons/` - SVG technology icons (AWS, Kubernetes, Terraform, Docker, Grafana, Helm, etc.)
- `assets/images/` - Profile photo, architecture diagrams, conference photos
- `assets/images/logos/` - Company logos (Amazon, Google, Microsoft, NVIDIA, Meta, etc.)
- `assets/resume/manifest.json` - Resume/cover letter metadata with active flag; `.docx` files for download

**External dependencies (CDN):**
- Google Fonts: Google Sans, Roboto Mono (genz.css); Mona Sans / JetBrains Mono still linked by style.css pages
- Font Awesome 6.5.1
- Firebase SDK 9.23.0 (app, auth, firestore — compat mode)
- marked.js (Markdown rendering on jobs page)
- docx.js + FileSaver.js (Word document generation on jobs page)
- Google Analytics 4 (G-GGNQHMGCLH) on all pages

**Design conventions:**
- Dark-first theme using CSS custom properties (`--bg-primary`, `--text-primary`, `--accent-blue`, etc.)
- Light theme via `[data-theme="light"]` attribute on `<html>`
- Glassmorphism UI: `--glass-bg`, `--glass-border`, backdrop-filter blur
- Gradient accents: `--gradient-primary` (blue → purple → pink)
- All pages share a consistent nav bar with logo, nav links, social icons, theme toggle, and mobile hamburger menu
- Typography: Sora (headings), Plus Jakarta Sans (body), JetBrains Mono (code)

### API Backend (api/)

FastAPI backend with PostgreSQL database for job tracking and document generation.

**Key files:**
- `main.py` - FastAPI application entry point with CORS, lifespan-based DB init, and localStorage migration endpoint (`POST /api/migration/import`)
- `database.py` - SQLAlchemy engine/session with `init_db()` that auto-creates tables and seeds a default user; handles `postgres://` vs `postgresql://` URL format
- `config.py` - Pydantic `BaseSettings` with `.env` file support (cached via `@lru_cache`)
- `models/` - SQLAlchemy ORM models:
  - `user.py` - `UserProfile`
  - `job.py` - `Company`, `Job`
  - `application.py` - `JobApplication`, `ExcludedJob`, `GeneratedDocument`, `UserSetting`
- `schemas/` - Pydantic request/response schemas:
  - `job.py` - `JobBase`, `JobCreate`, `JobResponse`, `JobListResponse`, `CompanyBase`, `CompanyCreate`, `CompanyResponse`
  - `application.py` - `ApplicationBase`, `ApplicationCreate`, `ApplicationResponse`, `ExcludedJobCreate`, `ExcludedJobResponse`, `DocumentCreate`, `DocumentResponse`
  - `settings.py` - `SettingsUpdate`, `SettingsResponse`
- `routers/` - API endpoint modules (all prefixed with `/api`):
  - `jobs.py` - CRUD for job listings with filtering, pagination, and batch create
  - `applications.py` - Track applied and excluded jobs
  - `documents.py` - Generate cover letters and resumes via AI (OpenAI or Anthropic)
  - `settings.py` - User settings management

**API routes:**
- `GET /` and `GET /api/health` - Health checks
- `POST /api/migration/import` - Import localStorage data to database
- Jobs, applications, documents, settings CRUD under `/api`

**Dependencies (`api/requirements.txt`):**
- fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, pydantic-settings, python-dotenv, openai, anthropic

### Database Schema (api/schema.sql)

PostgreSQL tables: `user_profiles`, `companies`, `jobs`, `job_applications`, `excluded_jobs`, `generated_documents`, `user_settings`

Key indexes: full-text search GIN index on jobs (`title` + `description`), B-tree indexes on foreign keys, status, dates, match scores, and `external_id`.

### Job Automation Tool (tools/)

Python CLI tool (`job_automation.py`) for automated job searching and AI-powered document generation.

**Components:**
- `JobListing` - Dataclass representing a job listing
- `ResumeProfile` - Dataclass with personal info, skills, and experience (customize for matching)
- `JobSearcher` - Fetches jobs from Remotive (free), Arbeitnow (free), and Adzuna (API key required)
- `JobMatcher` - Ranks jobs by keyword match score (0–100) against `ResumeProfile` skills with title bonuses
- `DocumentGenerator` - Creates tailored cover letters and resumes using OpenAI (`gpt-4o`) or Anthropic (`claude-sonnet-4-20250514`); falls back to templates when no API key is set
- `save_results()` - Exports results as JSON and formatted text files to an output directory

**CLI arguments:**
- `-k/--keywords` - Search keywords (default: "Cloud Architect DevOps Platform Engineering")
- `-d/--days` - Days to look back (default: 7)
- `-g/--generate` - Generate cover letters and tailored resumes
- `-t/--top` - Number of top jobs for document generation (default: 5)
- `-o/--output` - Output directory (default: "job_results")

**Dependencies (`tools/requirements.txt`):**
- requests, openai, anthropic, python-dotenv, rich

### Deployment

- **Frontend:** GitHub Pages deploys automatically from `main` branch. Custom domain via `CNAME` file (`www.sudhakarchundu.org`).
- **API backend:** Runs locally or on a server (port 8001). `database.py` handles Railway-style `postgres://` URLs.
- No CI/CD pipeline, GitHub Actions, Dockerfile, or test suite exists.

## Key Conventions

- **No build step:** The frontend is plain HTML/CSS/JS — edit files and refresh.
- **Python:** Uses modern Python (3.10+) with type hints. `pip` with `requirements.txt` for dependency management (no Poetry/pipenv).
- **Git branching:** Deploys from `main` branch (locally named `master`). No PR workflow or branch protection.
- **Code style:** API follows FastAPI conventions with separate `models/`, `schemas/`, `routers/` packages. Frontend uses vanilla JS with IIFEs for module encapsulation.
- **Theme system:** Dark mode is default. Theme preference persists via `localStorage`. CSS custom properties used throughout for consistent theming.
- **Firebase:** Used for authentication and comments only. Gracefully degrades when unconfigured — stub functions prevent errors, sign-in buttons are hidden.

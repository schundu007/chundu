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
- `index.html` - Portfolio landing page with hero section, skills grid, experience timeline, company logos, and neural network animated background
- `404.html` - Custom 404 error page
- `about/index.html` - About / professional background
- `resume/index.html` - Resume display
- `projects/index.html` - Achievements page
- `opensource/index.html` - Open source contributions
- `conferences/index.html` - Conference talks and events
- `publications/index.html` - Publications
- `contact/index.html` - Contact form
- `blog/index.html` - Technical blog with category filters (Kubernetes, DevOps, SRE, GPU/ML, FinOps); links to Medium
- `jobs/index.html` - Job listings page with `JobsAPI` client connecting to backend API (falls back to localStorage if API unavailable)
- `jobs/applied/index.html` - Applied jobs tracker

**Shared assets:**
- `assets/css/style.css` - Global design system (~1,760 lines) using CSS custom properties; dark (default) and light themes with glassmorphism effects, gradient accents, and responsive breakpoints
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
- Google Fonts: Sora, Plus Jakarta Sans, JetBrains Mono
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

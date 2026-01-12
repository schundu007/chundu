# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website for Sudhakar Chundu hosted on GitHub Pages at [www.sudhakarchundu.org](https://www.sudhakarchundu.org/). The site showcases cloud infrastructure and DevOps expertise.

## Development Commands

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

### Frontend Development
```bash
# Start local server (port 8000)
python -m http.server 8000
# Then open http://localhost:8000
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
```

### Environment Variables
Copy `api/.env.example` to `api/.env` and configure:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - for AI-powered document generation
- `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` - for Adzuna job search API

## Architecture

### API Backend (api/)
FastAPI backend with PostgreSQL database for job tracking and document generation:
- `main.py` - FastAPI application entry point
- `database.py` - SQLAlchemy connection and session management
- `config.py` - Environment configuration via pydantic-settings
- `models/` - SQLAlchemy ORM models (Job, Company, JobApplication, ExcludedJob, GeneratedDocument, UserSetting)
- `schemas/` - Pydantic request/response schemas
- `routers/` - API endpoints:
  - `jobs.py` - CRUD for job listings
  - `applications.py` - Track applied and excluded jobs
  - `documents.py` - Generate cover letters and resumes via AI
  - `settings.py` - User settings management

### Database Schema (api/schema.sql)
PostgreSQL tables: `user_profiles`, `companies`, `jobs`, `job_applications`, `excluded_jobs`, `generated_documents`, `user_settings`

### Static Website Structure
- `index.html` - Main portfolio page with inline styles for hero section, neural network background
- `assets/css/style.css` - Global styles using CSS custom properties for theming (dark/light mode)
- `assets/js/` - JavaScript modules:
  - `theme.js` - Theme toggle (dark/light mode persistence)
  - `neural-bg.js` - Animated neural network canvas background
  - `auth.js`, `comments.js`, `firebase-config.js` - Firebase-based authentication and comments
- Section pages in subdirectories: `about/`, `conferences/`, `contact/`, `opensource/`, `projects/`, `publications/`, `resume/`
- `jobs/index.html` - Job listings page with `JobsAPI` client connecting to backend API (falls back to localStorage if API unavailable)

### Job Automation Tool (tools/)
Python CLI tool (`job_automation.py`) with these components:
- `JobSearcher` - Fetches jobs from Remotive, Arbeitnow, and Adzuna APIs
- `JobMatcher` - Ranks jobs by skill match against `ResumeProfile`
- `DocumentGenerator` - Creates tailored cover letters and resumes using OpenAI or Anthropic
- `ResumeProfile` - Customize this class to update personal info and skills for job matching

### Deployment
GitHub Pages automatically deploys from `main` branch. Custom domain configured via `CNAME` file.
API backend runs locally or on a server (port 8001).

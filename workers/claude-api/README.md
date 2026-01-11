# Claude Job Assistant - Cloudflare Worker

This worker proxies requests to Claude API for job analysis, skills matching, cover letter generation, and resume tailoring.

## Features

1. **Analyze JD** - Extract key requirements, responsibilities, tech stack
2. **Match Skills** - Compare your profile against job requirements
3. **Cover Letter** - Generate tailored cover letters
4. **Resume** - Create ATS-optimized resumes for specific jobs

## Deployment

### Prerequisites

1. [Cloudflare account](https://dash.cloudflare.com/sign-up)
2. [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
3. [Anthropic API key](https://console.anthropic.com/)

### Steps

```bash
# 1. Install Wrangler
npm install -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Navigate to worker directory
cd workers/claude-api

# 4. Set your Anthropic API key as a secret
wrangler secret put ANTHROPIC_API_KEY
# (paste your key when prompted)

# 5. Deploy
wrangler deploy
```

### Get Your Worker URL

After deployment, you'll see:
```
Published claude-job-assistant (1.0.0)
  https://claude-job-assistant.<your-subdomain>.workers.dev
```

### Update Frontend

Update the `CLAUDE_WORKER_URL` in your jobs page:
```javascript
const CLAUDE_WORKER_URL = 'https://claude-job-assistant.<your-subdomain>.workers.dev';
```

## API Usage

### Analyze Job Description
```javascript
POST /
{
  "action": "analyze",
  "jobData": {
    "title": "Senior DevOps Engineer",
    "company": "Acme Inc",
    "location": "San Francisco, CA",
    "description": "Full job description text..."
  }
}
```

### Match Skills
```javascript
POST /
{
  "action": "match",
  "jobData": { ... }
}
```

### Generate Cover Letter
```javascript
POST /
{
  "action": "cover_letter",
  "jobData": { ... }
}
```

### Generate Resume
```javascript
POST /
{
  "action": "resume",
  "jobData": { ... }
}
```

## Customization

Edit `worker.js` to update:
- `USER_PROFILE` - Your personal profile and skills
- `CLAUDE_MODEL` - Claude model to use
- Prompt templates for each feature

## Cost Estimate

Claude Sonnet costs ~$3/M input tokens, $15/M output tokens.
Typical usage: ~$0.01-0.05 per job analysis.

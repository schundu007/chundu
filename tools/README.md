# Job Search Automation Tools

Automated job search and application document generation tools.

## Features

- **Multi-source Job Search**: Fetches jobs from Remotive, Arbeitnow, and Adzuna APIs
- **Smart Matching**: Ranks jobs based on skill match with your resume profile
- **AI-Powered Generation**: Creates tailored cover letters and resume summaries using OpenAI or Anthropic
- **Export Results**: Saves jobs to JSON and readable text files

## Quick Start

### 1. Install Dependencies

```bash
cd tools
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional but Recommended)

Create a `.env` file or set environment variables:

```bash
# For AI-powered document generation (choose one or both)
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Adzuna job search (free tier available at https://developer.adzuna.com/)
export ADZUNA_APP_ID="your-app-id"
export ADZUNA_APP_KEY="your-app-key"
```

### 3. Run the Tool

```bash
# Basic search
python job_automation.py

# Search with custom keywords
python job_automation.py -k "Platform Engineering Kubernetes"

# Generate cover letters and resumes for top 5 matches
python job_automation.py --generate --top 5

# Full options
python job_automation.py -k "Cloud Architect" -d 7 -g -t 3 -o ./my_results
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--keywords` | `-k` | Search keywords | "Cloud Architect DevOps Platform Engineering" |
| `--days` | `-d` | Days to look back | 7 |
| `--generate` | `-g` | Generate cover letters and resumes | False |
| `--top` | `-t` | Number of top jobs for document generation | 5 |
| `--output` | `-o` | Output directory | "job_results" |

## Output Structure

```
job_results/
├── jobs_20250101_120000.json    # All jobs in JSON format
├── jobs_20250101_120000.txt     # Readable job listings
└── applications/
    ├── 01_cover_letter_CompanyA.txt
    ├── 01_resume_CompanyA.txt
    ├── 02_cover_letter_CompanyB.txt
    └── 02_resume_CompanyB.txt
```

## Customizing Your Profile

Edit the `ResumeProfile` class in `job_automation.py` to update:
- Personal information
- Professional summary
- Skills list
- Work experience

## API Sources

| Source | API Key Required | Focus |
|--------|------------------|-------|
| Remotive | No | Remote tech jobs |
| Arbeitnow | No | European tech jobs |
| Adzuna | Yes (free tier) | Global job aggregator |

## Tips

1. **Get Better Matches**: Update the skills list in `ResumeProfile` to match your actual expertise
2. **More Jobs**: Sign up for Adzuna API (free) to access more job listings
3. **Better Documents**: Use OpenAI GPT-4 or Anthropic Claude for higher quality cover letters
4. **Regular Runs**: Set up a cron job to run daily and get fresh job listings

## Example Workflow

```bash
# 1. Search and save jobs
python job_automation.py -k "SRE Manager Site Reliability" -d 3

# 2. Review results in job_results/jobs_*.txt

# 3. Generate documents for promising matches
python job_automation.py -k "SRE Manager" --generate --top 3

# 4. Review and customize generated cover letters before applying
```

## Troubleshooting

**No jobs found?**
- Try broader keywords
- Check if Adzuna API keys are set correctly
- Some APIs have rate limits

**AI generation not working?**
- Verify API keys are set: `echo $OPENAI_API_KEY`
- Check API quota/credits
- Tool falls back to templates if AI unavailable

## License

MIT License - Feel free to modify and use for your job search!

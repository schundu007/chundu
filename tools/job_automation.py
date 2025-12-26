#!/usr/bin/env python3
"""
Job Search Automation Tool
--------------------------
Fetches jobs from multiple sources, matches against your resume,
and generates tailored resumes and cover letters using AI.

Author: Sudhakar Chundu
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Optional
import requests
from dataclasses import dataclass, asdict

# Optional imports - install as needed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Run: pip install openai")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class JobListing:
    """Represents a job listing"""
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: str
    source: str
    salary: Optional[str] = None
    match_score: Optional[float] = None


@dataclass
class ResumeProfile:
    """Your resume profile for matching"""
    name: str = "Sudhakar Chundu"
    title: str = "Cloud AI Architect"
    email: str = "chundubabu@gmail.com"
    phone: str = ""
    linkedin: str = "https://www.linkedin.com/in/schundu"
    github: str = "https://github.com/schundu007"

    summary: str = """Cloud AI Architect with 18+ years of experience in enterprise infrastructure,
    AI/ML platforms, and DevOps transformation. Expert in Kubernetes, GPU infrastructure,
    and building scalable cloud-native platforms. Proven track record of leading large-scale
    migrations and implementing platform engineering practices."""

    skills: list = None
    experience: list = None

    def __post_init__(self):
        if self.skills is None:
            self.skills = [
                "Cloud Architecture (AWS, Azure, GCP)",
                "Kubernetes & Container Orchestration",
                "GPU Infrastructure & AI/ML Platforms",
                "Terraform & Infrastructure as Code",
                "GitOps (ArgoCD, Flux)",
                "Prometheus, Grafana, Datadog",
                "Site Reliability Engineering",
                "Platform Engineering",
                "DevSecOps & Compliance (SOC2, HIPAA)",
                "Team Leadership & Mentoring",
                "Python, Go, Shell Scripting",
                "CI/CD (GitHub Actions, Jenkins, GitLab)"
            ]

        if self.experience is None:
            self.experience = [
                {
                    "title": "Cloud Architect",
                    "company": "Harvard Pilgrim Health Care",
                    "period": "2021 - Present",
                    "highlights": [
                        "Led Azure cloud migration for enterprise healthcare platform",
                        "Implemented Kubernetes platform serving 500+ microservices",
                        "Reduced infrastructure costs by 40% through optimization"
                    ]
                },
                {
                    "title": "Cloud Senior Engineer",
                    "company": "CNA Insurance",
                    "period": "2019 - 2021",
                    "highlights": [
                        "Designed multi-cloud architecture for insurance applications",
                        "Built CI/CD pipelines reducing deployment time by 70%"
                    ]
                }
            ]


class JobSearcher:
    """Fetches jobs from various sources"""

    def __init__(self):
        self.jobs = []

    def search_adzuna(self, keywords: str, location: str = "us", days: int = 7) -> list:
        """Search jobs using Adzuna API (free tier available)"""
        app_id = os.getenv("ADZUNA_APP_ID")
        app_key = os.getenv("ADZUNA_APP_KEY")

        if not app_id or not app_key:
            print("Adzuna API credentials not found. Set ADZUNA_APP_ID and ADZUNA_APP_KEY")
            return []

        url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": keywords,
            "max_days_old": days,
            "results_per_page": 50,
            "sort_by": "date"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for job in data.get("results", []):
                self.jobs.append(JobListing(
                    title=job.get("title", ""),
                    company=job.get("company", {}).get("display_name", ""),
                    location=job.get("location", {}).get("display_name", ""),
                    description=job.get("description", ""),
                    url=job.get("redirect_url", ""),
                    posted_date=job.get("created", ""),
                    source="Adzuna",
                    salary=job.get("salary_max")
                ))

            print(f"Found {len(data.get('results', []))} jobs from Adzuna")

        except Exception as e:
            print(f"Error fetching from Adzuna: {e}")

        return self.jobs

    def search_remotive(self, keywords: str) -> list:
        """Search remote jobs from Remotive (free, no API key needed)"""
        url = "https://remotive.com/api/remote-jobs"
        params = {"search": keywords}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            seven_days_ago = datetime.now() - timedelta(days=7)

            for job in data.get("jobs", []):
                posted = datetime.fromisoformat(job.get("publication_date", "").replace("Z", "+00:00"))
                if posted.replace(tzinfo=None) >= seven_days_ago:
                    self.jobs.append(JobListing(
                        title=job.get("title", ""),
                        company=job.get("company_name", ""),
                        location="Remote",
                        description=job.get("description", ""),
                        url=job.get("url", ""),
                        posted_date=job.get("publication_date", ""),
                        source="Remotive",
                        salary=job.get("salary")
                    ))

            print(f"Found {len([j for j in self.jobs if j.source == 'Remotive'])} remote jobs from Remotive")

        except Exception as e:
            print(f"Error fetching from Remotive: {e}")

        return self.jobs

    def search_github_jobs_api(self, keywords: str) -> list:
        """Search jobs from public job APIs"""
        # Using Arbeitnow as GitHub Jobs API is deprecated
        url = "https://www.arbeitnow.com/api/job-board-api"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            keywords_lower = keywords.lower().split()
            seven_days_ago = datetime.now() - timedelta(days=7)

            for job in data.get("data", []):
                title_lower = job.get("title", "").lower()
                desc_lower = job.get("description", "").lower()

                if any(kw in title_lower or kw in desc_lower for kw in keywords_lower):
                    try:
                        posted = datetime.fromisoformat(job.get("created_at", "").replace("Z", "+00:00"))
                        if posted.replace(tzinfo=None) < seven_days_ago:
                            continue
                    except:
                        pass

                    self.jobs.append(JobListing(
                        title=job.get("title", ""),
                        company=job.get("company_name", ""),
                        location=job.get("location", ""),
                        description=job.get("description", "")[:500],
                        url=job.get("url", ""),
                        posted_date=job.get("created_at", ""),
                        source="Arbeitnow"
                    ))

            print(f"Found {len([j for j in self.jobs if j.source == 'Arbeitnow'])} jobs from Arbeitnow")

        except Exception as e:
            print(f"Error fetching from Arbeitnow: {e}")

        return self.jobs


class JobMatcher:
    """Matches jobs against your resume profile"""

    def __init__(self, profile: ResumeProfile):
        self.profile = profile
        self.skill_keywords = self._extract_keywords()

    def _extract_keywords(self) -> set:
        """Extract keywords from skills"""
        keywords = set()
        for skill in self.profile.skills:
            # Split by common delimiters and add individual words
            words = skill.lower().replace(",", " ").replace("(", " ").replace(")", " ").split()
            keywords.update(words)
        return keywords

    def calculate_match_score(self, job: JobListing) -> float:
        """Calculate how well a job matches the profile (0-100)"""
        text = f"{job.title} {job.description}".lower()

        # Count matching keywords
        matches = sum(1 for kw in self.skill_keywords if kw in text and len(kw) > 2)

        # Bonus for title matches
        title_keywords = ["architect", "director", "manager", "lead", "senior", "principal",
                         "cloud", "platform", "sre", "devops", "infrastructure", "ai", "ml"]
        title_matches = sum(2 for kw in title_keywords if kw in job.title.lower())

        # Calculate score
        max_possible = len(self.skill_keywords) + len(title_keywords) * 2
        score = min(100, ((matches + title_matches) / max_possible) * 100 * 2)

        return round(score, 1)

    def rank_jobs(self, jobs: list) -> list:
        """Rank jobs by match score"""
        for job in jobs:
            job.match_score = self.calculate_match_score(job)

        return sorted(jobs, key=lambda x: x.match_score or 0, reverse=True)


class DocumentGenerator:
    """Generates tailored resumes and cover letters using AI"""

    def __init__(self, profile: ResumeProfile):
        self.profile = profile
        self.client = None
        self.provider = None

        # Try to initialize AI client
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI()
            self.provider = "openai"
            print("Using OpenAI for document generation")
        elif ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.client = Anthropic()
            self.provider = "anthropic"
            print("Using Anthropic for document generation")
        else:
            print("No AI API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for AI-powered generation")

    def generate_cover_letter(self, job: JobListing) -> str:
        """Generate a tailored cover letter for a job"""
        if not self.client:
            return self._generate_template_cover_letter(job)

        prompt = f"""Write a professional cover letter for the following job application.

APPLICANT PROFILE:
Name: {self.profile.name}
Title: {self.profile.title}
Summary: {self.profile.summary}
Key Skills: {', '.join(self.profile.skills[:8])}

JOB DETAILS:
Title: {job.title}
Company: {job.company}
Description: {job.description[:1500]}

Requirements:
1. Keep it concise (3-4 paragraphs)
2. Highlight relevant experience and skills
3. Show enthusiasm for the role
4. Be professional but personable
5. Include a call to action

Write the cover letter now:"""

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_cover_letter(job)

    def _generate_template_cover_letter(self, job: JobListing) -> str:
        """Generate a template-based cover letter"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With over 18 years of experience in cloud infrastructure, AI/ML platforms, and DevOps leadership, I am confident in my ability to make significant contributions to your team.

In my current role as Cloud AI Architect, I have led enterprise-scale cloud migrations, implemented Kubernetes platforms serving hundreds of microservices, and built GPU infrastructure for AI/ML workloads. My expertise in {', '.join(self.profile.skills[:4])} aligns well with your requirements.

Key achievements that demonstrate my qualifications:
- Led Azure cloud migration for enterprise healthcare platform
- Reduced infrastructure costs by 40% through optimization
- Built CI/CD pipelines reducing deployment time by 70%

I am excited about the opportunity to bring my technical expertise and leadership experience to {job.company}. I would welcome the chance to discuss how my background can contribute to your team's success.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{self.profile.name}
{self.profile.email}
{self.profile.linkedin}
"""

    def generate_tailored_resume(self, job: JobListing) -> str:
        """Generate a tailored resume summary for a job"""
        if not self.client:
            return self._generate_template_resume(job)

        prompt = f"""Create a tailored professional summary and skills section for the following job.

APPLICANT PROFILE:
Name: {self.profile.name}
Current Title: {self.profile.title}
Original Summary: {self.profile.summary}
All Skills: {', '.join(self.profile.skills)}

JOB DETAILS:
Title: {job.title}
Company: {job.company}
Description: {job.description[:1500]}

Requirements:
1. Rewrite the professional summary to highlight relevant experience
2. Reorder skills to prioritize those mentioned in job description
3. Keep summary to 3-4 sentences
4. Be specific about achievements

Output format:
PROFESSIONAL SUMMARY:
[summary]

KEY SKILLS:
[bullet list of top 10 relevant skills]
"""

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.7
                )
                return response.choices[0].message.content
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_resume(job)

    def _generate_template_resume(self, job: JobListing) -> str:
        """Generate a template-based resume section"""
        return f"""PROFESSIONAL SUMMARY:
{self.profile.summary}

KEY SKILLS:
• {chr(10).join('• ' + skill for skill in self.profile.skills[:10])}

Tailored for: {job.title} at {job.company}
"""


def save_results(jobs: list, output_dir: str = "job_results"):
    """Save job search results to files"""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save as JSON
    json_file = os.path.join(output_dir, f"jobs_{timestamp}.json")
    with open(json_file, "w") as f:
        json.dump([asdict(job) for job in jobs], f, indent=2)
    print(f"Saved {len(jobs)} jobs to {json_file}")

    # Save as readable text
    txt_file = os.path.join(output_dir, f"jobs_{timestamp}.txt")
    with open(txt_file, "w") as f:
        f.write(f"Job Search Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 80 + "\n\n")

        for i, job in enumerate(jobs[:20], 1):
            f.write(f"{i}. {job.title}\n")
            f.write(f"   Company: {job.company}\n")
            f.write(f"   Location: {job.location}\n")
            f.write(f"   Match Score: {job.match_score}%\n")
            f.write(f"   Source: {job.source}\n")
            f.write(f"   URL: {job.url}\n")
            f.write(f"   Posted: {job.posted_date}\n")
            f.write("-" * 80 + "\n")

    print(f"Saved readable results to {txt_file}")
    return json_file, txt_file


def main():
    parser = argparse.ArgumentParser(description="Job Search Automation Tool")
    parser.add_argument("--keywords", "-k", default="Cloud Architect DevOps Platform Engineering",
                       help="Search keywords")
    parser.add_argument("--days", "-d", type=int, default=7,
                       help="Number of days to look back")
    parser.add_argument("--generate", "-g", action="store_true",
                       help="Generate cover letters and tailored resumes for top matches")
    parser.add_argument("--top", "-t", type=int, default=5,
                       help="Number of top jobs to generate documents for")
    parser.add_argument("--output", "-o", default="job_results",
                       help="Output directory")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("Job Search Automation Tool")
    print(f"{'='*60}\n")

    # Initialize components
    profile = ResumeProfile()
    searcher = JobSearcher()
    matcher = JobMatcher(profile)

    # Search for jobs
    print(f"Searching for jobs with keywords: {args.keywords}")
    print(f"Looking back {args.days} days...\n")

    searcher.search_remotive(args.keywords)
    searcher.search_github_jobs_api(args.keywords)
    searcher.search_adzuna(args.keywords, days=args.days)

    if not searcher.jobs:
        print("No jobs found. Try different keywords or check API credentials.")
        return

    # Rank jobs by match score
    ranked_jobs = matcher.rank_jobs(searcher.jobs)

    print(f"\nFound {len(ranked_jobs)} total jobs")
    print(f"\nTop {min(10, len(ranked_jobs))} matches:")
    print("-" * 60)

    for i, job in enumerate(ranked_jobs[:10], 1):
        print(f"{i}. [{job.match_score}%] {job.title}")
        print(f"   {job.company} - {job.location}")
        print(f"   Source: {job.source}")
        print()

    # Save results
    save_results(ranked_jobs, args.output)

    # Generate documents for top matches
    if args.generate:
        print(f"\nGenerating documents for top {args.top} matches...")
        generator = DocumentGenerator(profile)

        docs_dir = os.path.join(args.output, "applications")
        os.makedirs(docs_dir, exist_ok=True)

        for i, job in enumerate(ranked_jobs[:args.top], 1):
            print(f"\n[{i}/{args.top}] Generating for: {job.title} at {job.company}")

            # Generate cover letter
            cover_letter = generator.generate_cover_letter(job)
            cl_file = os.path.join(docs_dir, f"{i:02d}_cover_letter_{job.company[:20].replace(' ', '_')}.txt")
            with open(cl_file, "w") as f:
                f.write(cover_letter)
            print(f"   Saved cover letter to {cl_file}")

            # Generate tailored resume section
            resume = generator.generate_tailored_resume(job)
            resume_file = os.path.join(docs_dir, f"{i:02d}_resume_{job.company[:20].replace(' ', '_')}.txt")
            with open(resume_file, "w") as f:
                f.write(resume)
            print(f"   Saved tailored resume to {resume_file}")

    print(f"\n{'='*60}")
    print("Done! Check the output directory for results.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

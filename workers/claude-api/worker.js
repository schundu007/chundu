/**
 * Cloudflare Worker - Claude API Proxy for Job Assistant
 *
 * Features:
 * 1. Analyze & Summarize Job Descriptions
 * 2. Match Skills to JD Requirements
 * 3. Generate Tailored Cover Letters
 * 4. Generate Tailored Resumes
 *
 * Deploy: wrangler deploy
 * Set secret: wrangler secret put ANTHROPIC_API_KEY
 */

const CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages';
const CLAUDE_MODEL = 'claude-sonnet-4-20250514';

// User Profile - Sudhakar Chundu
const USER_PROFILE = {
    name: "Sudhakar Chundu",
    title: "Staff DevOps/SRE Engineer | Cloud Infrastructure Architect",
    experience: "18+ years",
    location: "San Jose, CA",
    email: "sudhakar@example.com",
    linkedin: "linkedin.com/in/sudhakarchundu",
    summary: `Staff-level DevOps/SRE leader with 18+ years of experience building and scaling
cloud infrastructure for AI/ML workloads. Expert in Kubernetes, Terraform, and GPU cluster
orchestration. Proven track record of achieving 99.95% SLO, reducing deploy failures by 68%,
and managing 40+ production services. Strong background in incident response, observability,
and platform engineering.`,

    coreSkills: [
        // Cloud Platforms
        "AWS", "Azure", "GCP", "OCI",
        // Container & Orchestration
        "Kubernetes", "Docker", "Helm", "ArgoCD", "Istio",
        // IaC & Configuration
        "Terraform", "Ansible", "Pulumi", "CloudFormation",
        // CI/CD
        "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "Spinnaker",
        // Observability
        "Prometheus", "Grafana", "Datadog", "Splunk", "ELK Stack", "New Relic",
        // GPU/HPC
        "NVIDIA DGX", "CUDA", "Slurm", "Ray", "vLLM",
        // Languages
        "Python", "Go", "Bash", "TypeScript",
        // Databases
        "PostgreSQL", "Redis", "MongoDB", "Elasticsearch",
        // Security
        "Vault", "SAML", "OAuth", "mTLS"
    ],

    experience_highlights: [
        "Led platform engineering team managing 40+ microservices with 99.95% SLO",
        "Reduced deployment failures by 68% through GitOps and progressive delivery",
        "Built GPU cluster orchestration for AI/ML training workloads (1000+ GPUs)",
        "Decreased MTTR from 45min to 12min through automated incident response",
        "Migrated legacy infrastructure to Kubernetes, reducing costs by 40%",
        "Implemented zero-trust security architecture across multi-cloud environment"
    ],

    certifications: [
        "AWS Solutions Architect Professional",
        "Certified Kubernetes Administrator (CKA)",
        "Google Cloud Professional Cloud Architect",
        "HashiCorp Terraform Associate"
    ]
};

// CORS headers
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export default {
    async fetch(request, env) {
        // Handle CORS preflight
        if (request.method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders });
        }

        if (request.method !== 'POST') {
            return new Response(JSON.stringify({ error: 'Method not allowed' }), {
                status: 405,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        try {
            const { action, jobData } = await request.json();

            let prompt, systemPrompt;

            switch (action) {
                case 'analyze':
                    ({ prompt, systemPrompt } = buildAnalyzePrompt(jobData));
                    break;
                case 'match':
                    ({ prompt, systemPrompt } = buildMatchPrompt(jobData));
                    break;
                case 'cover_letter':
                    ({ prompt, systemPrompt } = buildCoverLetterPrompt(jobData));
                    break;
                case 'resume':
                    ({ prompt, systemPrompt } = buildResumePrompt(jobData));
                    break;
                default:
                    return new Response(JSON.stringify({ error: 'Invalid action' }), {
                        status: 400,
                        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                    });
            }

            const response = await callClaude(env.ANTHROPIC_API_KEY, systemPrompt, prompt);

            return new Response(JSON.stringify({
                success: true,
                result: response,
                action: action
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });

        } catch (error) {
            return new Response(JSON.stringify({
                error: error.message,
                success: false
            }), {
                status: 500,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
    }
};

async function callClaude(apiKey, systemPrompt, userPrompt) {
    const response = await fetch(CLAUDE_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
            'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
            model: CLAUDE_MODEL,
            max_tokens: 4096,
            system: systemPrompt,
            messages: [{ role: 'user', content: userPrompt }]
        })
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Claude API error: ${error}`);
    }

    const data = await response.json();
    return data.content[0].text;
}

// ============ PROMPT BUILDERS ============

function buildAnalyzePrompt(jobData) {
    const systemPrompt = `You are an expert job description analyzer. Your task is to extract and summarize
key information from job descriptions in a structured, actionable format. Be concise but comprehensive.`;

    const prompt = `Analyze this job description and provide a structured summary:

**Job Title:** ${jobData.title}
**Company:** ${jobData.company}
**Location:** ${jobData.location}

**Job Description:**
${jobData.description}

Please provide:

1. **Role Summary** (2-3 sentences)
2. **Key Responsibilities** (bullet points, max 5)
3. **Must-Have Requirements** (non-negotiable skills/experience)
4. **Nice-to-Have Requirements** (preferred but not required)
5. **Technical Stack** (tools, languages, platforms mentioned)
6. **Team/Culture Signals** (what we can infer about the team)
7. **Red Flags or Concerns** (if any)
8. **Salary Analysis** (if mentioned, or market estimate)

Format your response in clean markdown.`;

    return { prompt, systemPrompt };
}

function buildMatchPrompt(jobData) {
    const systemPrompt = `You are an expert career advisor and skills matcher. Your task is to honestly
evaluate how well a candidate matches a job description. Be realistic and specific about gaps.`;

    const prompt = `Compare this candidate profile against the job requirements:

**CANDIDATE PROFILE:**
Name: ${USER_PROFILE.name}
Title: ${USER_PROFILE.title}
Experience: ${USER_PROFILE.experience}

Core Skills: ${USER_PROFILE.coreSkills.join(', ')}

Experience Highlights:
${USER_PROFILE.experience_highlights.map(h => `- ${h}`).join('\n')}

Certifications: ${USER_PROFILE.certifications.join(', ')}

**JOB DETAILS:**
Title: ${jobData.title}
Company: ${jobData.company}
Location: ${jobData.location}

Description:
${jobData.description}

**Please provide:**

1. **Overall Match Score:** X/100
   - Technical Skills: X/100
   - Experience Level: X/100
   - Domain Expertise: X/100

2. **Strong Matches** (skills/experience that align perfectly)

3. **Partial Matches** (related experience that could transfer)

4. **Gaps to Address** (missing skills or experience)

5. **Talking Points** (how to position experience in an interview)

6. **Risk Assessment** (honest evaluation of candidacy strength)

7. **Recommendation** (Apply Now / Apply with Prep / Consider Carefully / Skip)

Be honest and specific. Format in clean markdown.`;

    return { prompt, systemPrompt };
}

function buildCoverLetterPrompt(jobData) {
    const systemPrompt = `You are an expert cover letter writer for senior engineering roles.
Write compelling, authentic cover letters that are:
- Professional but not stiff
- Specific to the role and company
- Highlighting relevant achievements with metrics
- Showing genuine interest without being sycophantic
- Concise (under 400 words)`;

    const prompt = `Write a tailored cover letter for this position:

**CANDIDATE:**
${USER_PROFILE.name}
${USER_PROFILE.title}
${USER_PROFILE.location}
${USER_PROFILE.email}

**Summary:** ${USER_PROFILE.summary}

**Key Achievements:**
${USER_PROFILE.experience_highlights.map(h => `- ${h}`).join('\n')}

**Certifications:** ${USER_PROFILE.certifications.join(', ')}

**JOB DETAILS:**
Title: ${jobData.title}
Company: ${jobData.company}
Location: ${jobData.location}

Description:
${jobData.description}

**Requirements:**
1. Write a compelling cover letter (under 400 words)
2. Open with a hook relevant to the company/role
3. Highlight 2-3 most relevant achievements with specific metrics
4. Show understanding of the company's challenges
5. Close with confidence and clear call to action
6. Be authentic - avoid clichés and buzzwords

Format: Ready to copy/paste, with proper formatting.`;

    return { prompt, systemPrompt };
}

function buildResumePrompt(jobData) {
    const systemPrompt = `You are an expert resume writer for senior DevOps/SRE engineering roles.
Create ATS-optimized resumes that:
- Use strong action verbs and quantifiable metrics
- Match keywords from the job description
- Highlight relevant experience prominently
- Are honest and accurate (never fabricate)
- Follow modern resume best practices`;

    const prompt = `Create a tailored resume optimized for this specific position:

**CANDIDATE:**
${USER_PROFILE.name}
${USER_PROFILE.title}
${USER_PROFILE.location}
Email: ${USER_PROFILE.email}
LinkedIn: ${USER_PROFILE.linkedin}

**Summary:** ${USER_PROFILE.summary}

**Core Skills:** ${USER_PROFILE.coreSkills.join(', ')}

**Experience Highlights:**
${USER_PROFILE.experience_highlights.map(h => `- ${h}`).join('\n')}

**Certifications:** ${USER_PROFILE.certifications.join(', ')}

**TARGET JOB:**
Title: ${jobData.title}
Company: ${jobData.company}
Location: ${jobData.location}

Description:
${jobData.description}

**Requirements:**
1. Create a tailored 1-page resume in clean text format
2. Reorder and emphasize skills matching the JD
3. Rewrite bullet points to match job requirements
4. Include relevant keywords from the JD for ATS
5. Use metrics and achievements prominently
6. Professional Summary tailored to this specific role

Format the resume in clean, copy-pasteable text format:
- Use clear section headers
- Bullet points for experience
- Easy to parse for ATS systems`;

    return { prompt, systemPrompt };
}

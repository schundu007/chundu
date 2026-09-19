# Portfolio Master — Canonical Facts

Single source of truth for every claim on sudhakarchundu.org.
Derived 2026-09-18 from **all 41 resumes** in `~/Downloads` (`Misc/`,
`Consolidated_Resumes/Austin`, `Consolidated_Resumes/Milpitas`), with
`Sudhakar_Ch_DevOps_Platform_Master_Resume_Corrected.docx` (18 Sep 2026) as the
tie-breaker. Counts below are agreement across those 41 files.

**Rule:** the site must never state a fact that is not in this file. Tailored resumes
may re-frame titles per application; the site uses the *Canonical* column only.

---

## 1. Identity & contact

| Field | Canonical value | Agreement |
| --- | --- | --- |
| Display name | Sudhakar Chundu (resumes head "SUDHAKAR CH") | — |
| Resume headline | Staff DevOps and Platform Engineering Leader | master resume |
| Location | Milpitas, CA (Bay Area); Austin, TX on relocation variants | 41/41 |
| Email (public / site) | chundubabu@gmail.com | both addresses in use; see note |
| Phone | +1 (408) 409-6448 | **41/41 unanimous** |
| LinkedIn | linkedin.com/in/schundu007 | **41/41 unanimous, zero `babucs`** |
| GitHub | github.com/schundu007 | 41/41 |
| Medium | schundu.medium.com (handle `@schundu`) | 41/41 |
| ORCID | orcid.org/0009-0001-5038-5936 | **41/41** |

> **Email (2026-09-18):** both addresses are in active use by design —
> `chundubabu@gmail.com` (16 resumes) and `subach2026@gmail.com` (15). This is not a
> discrepancy to fix. **`chundubabu@gmail.com` is the public, site-facing address**:
> it is what the portfolio, the hosted resume, and the cover-letter generator use.
> `subach2026@gmail.com` stays available for tailored resumes as you choose.
> The only rule: one address per document, so a single recruiter never sees both.

## 2. Employment history

| Period | Employer | Canonical title | Location |
| --- | --- | --- | --- |
| Feb 2026 – present | **CloudScouts** — contracted to IBM; client **AT&T**, on IBM watsonx | **Platform & DevOps Architect** | Plano, TX (remote) |
| Oct 2023 – Jan 2026 | Trackonomy Systems Inc | **Principal Cloud Architect** | San Jose, CA |
| Feb 2020 – Oct 2023 | Wipro Technologies (OSDU — Azure as FTE, then AWS as contractor) | **Cloud & SRE Architect, OSDU Data Platform** | Hyderabad, India |
| Aug 2018 – Feb 2020 | NTT Data Services | Cloud & DevOps Architect (Healthcare) | Hyderabad, India |
| May 2007 – Jun 2018 | Tata Consultancy Services | Multi-Cloud Architect / Senior Infrastructure Engineer | Hyderabad, India + onsite FL, MD, OH |

Date agreement across all 41 resumes is total: CloudScouts Feb 2026–Present,
Trackonomy Oct 2023–Jan 2026 (40/40), Wipro Feb 2020–Oct 2023 (22, with 4 splitting
the Azure phase at Mar 2022), NTT Data Aug 2018–Feb 2020 (40/40), TCS May 2007–Jun 2018 (38/39).

**Titles are heavily tailored per application and have no single canonical form.**
The site must use the defensible one, not the most senior one. Most-used variants:
Trackonomy — Principal Cloud Architect (6), Staff SRE (6), Cloud Architect (3);
Wipro — Senior DevOps Engineer (4); NTT Data — Cloud Architect, Healthcare Infrastructure (7);
TCS — Multi-Cloud Architect / Senior Infrastructure Engineer (17).

**Trackonomy decision (2026-09-18): Principal Cloud Architect.** Confirmed as the
defensible title; it is also the most-used variant across the resume set (6 of 41).
The site, the hosted resume (.docx and .pdf), and the cover-letter generator in
`jobs/index.html` all carry it. Elsewhere the site uses the corrected master's wording.

- Total experience: **18+ years** (2007 →). TCS tenure is **11 years**, not 13.
- TCS clients: **CNA, PwC, Verizon, Owens Corning** (ASML 2009–11 as Senior Linux Admin).
- Harvard Pilgrim belongs to **NTT Data (2018–2020)** — never to TCS.
- OSDU energy clients: **ExxonMobil, Chevron, BP, Shell**. TotalEnergies is not supported.
- Leadership: **6-engineer platform team** at Trackonomy; **teams of up to 14** across
  15+ years of technical leadership.

## 3. Approved metrics

Use these numbers verbatim; do not round, restate, or invent siblings.

**Platform & delivery**
- CI/CD for **100+ applications**; **50+ daily zero-downtime deployments**
- **6,000+ pipeline runs/day**, 100x scale-out on ephemeral/self-hosted runners
- Deployment time **days → 15 minutes** (−95%); production issues **−90%**
- **5+ reusable Terraform modules**; golden paths serving **50+ engineers**
- **50+ enterprise data sources** onboarded with policy-as-code

**GPU / AI-ML**
- **65 GPUs across 8 bare-metal nodes**, Slurm / Slinky / LSF / NVIDIA BCM
- GPU utilisation **45% → 78%**; queue wait **−60%**; p99 **−40%**
- Inference cost **−65%**, **5M+ daily predictions** across 15+ edge locations
- **30+ production models** with GitOps blue-green

**Reliability**
- **99.97% uptime** on the GPU/ML platform (the headline reliability number)
- 99.95%–99.99% availability for OSDU ML inference; 99.9% on the Azure AKS estate
- **MTTR −60%**, incident volume **−65%**, on-call response **<15 min**
- RPO <1h / RTO <4h validated

**Cost / FinOps**
- **73% infrastructure cost reduction** ($10M → $2.7M/yr) = **$8M+ annual savings**
- Azure resource sprawl **−87%** (8.7K → 1.1K)

**Compliance** — zero critical findings across **SOC 2, HIPAA, FedRAMP**
(also HITRUST, ISO 27001, PCI, GDPR experience).

**Frequency check** (mentions across all 41 resumes — these are the load-bearing claims):
65-GPU cluster 66 · 99.9x% uptime 168 · 73% cost reduction 89 · cloudforge 81 ·
$8M savings 48 · 6,000+ pipeline runs/day 40 ·
6-engineer team 33 · teams up to 14 → 28.

⚠️ Retired / unsupported numbers currently on the site: "13 years" at TCS,
"20+ facility buildouts" (canonical: 12+), "$15M+ budget" attributed to PwC,
"−55% downtime reduction" (OSDU), "40+ apps migrated" (canonical: 100+),
"4 compliance certs" (name the three), "99.99% SLO" as a Trackonomy headline.

## 4. Certifications & education

- AWS Certified Solutions Architect – Professional
- Microsoft Azure Solutions Architect Expert
- Certified Kubernetes Administrator (CKA)
- HashiCorp Terraform Associate
- **B.E. Mechanical Engineering — Acharya Nagarjuna University, 2005** (missing from the site entirely)

**Resolved:** GCP Professional Cloud Architect appears in **22 of 41** resumes, so it is
a real credential you claim regularly — it stays on the site. The corrected master simply
omits it. (GCP certs expire after 2 years; re-check the date before an interview.)

The other four appear in **41/41**.

## 5. Open source (the strongest unused asset)

| Project | Proof | On site? |
| --- | --- | --- |
| OSDU `infra-azure-provisioning` | Upstream contributor, community.opengroup.org | on Open Source page |
| OSDU `terraform-deployment-aws` | same forum, AWS deployment | on Open Source page |
| github.com/schundu007 | CI/CD automation, Terraform modules, git-dboard, cloudforge | live counters show `--` |

Upstream contribution to an Open Group platform is among the most verifiable
credentials here — the repos are public.

## 6. Live apps — canonical list

Resume-declared, all verified HTTP 200 on 2026-09-18:

| Tool | URL | One-liner |
| --- | --- | --- |
| CloudForge | https://forc.cariara.com | Agentic infra coding agent (Claude + MCP): writes pipelines and Terraform, verifies with dry-run/plan/policy tests, opens a reviewable PR |
| GitPulse | https://gitpulse.cariara.com/dashboard | CI and DORA metrics dashboard |
| idman | https://idm.cariara.com | Identity manager |
| Terraform Studio | https://ts.cariara.com | Resource discovery, import automation, drift detection |
| Trending GitHub Repos | /trending-gitrepos/ | Weekly star-velocity ranking across DevOps/MLOps/SRE/GPU |

**Excluded by decision (2026-09-18):** Cariara (`jobs.cariara.com`), Camora, Lumora
(AI interview assistant) and Capra are deliberately **kept off the portfolio** — a
job portal and interview tooling signal job-hunting, not engineering capability.
They are in the `IGNORE` set in `directory/scripts/build-directory.mjs`, so the weekly
refresh will not re-add them. `gitpulser.vercel.app` is superseded by `gitpulse.cariara.com`.

**cloudforge is the flagship differentiator** — an agentic MCP tool that writes and
self-verifies infrastructure changes. It leads the Live Apps directory and appears in
the Open Source page and the experience ledger.

## 7. Naming rules

- **Never publish a commit count for the OSDU repos.** The 2,317 figure was the
  repos' combined total, not a personal attribution — removed 2026-09-18. Refer to
  the work as upstream contribution and let the public repos speak.
- **Never write "AT&T Chief Data Office"** — the client is **AT&T**, full stop.
  Always name the chain: *CloudScouts &rarr; contracted to IBM &rarr; client AT&T*.
- **Site positioning headline: "Platform & DevOps Architect"** (decided 2026-09-18),
  used in the hero, `<title>`, og tags, contact page, blog bylines and JSON-LD.
  "Staff DevOps Engineer" is retained only as a search keyword in `<meta keywords>`.
- **Titles must not dip below architect level** across the ledger — the progression
  reads Architect &rarr; Principal &rarr; Architect &rarr; Architect &rarr; Architect.
  The `~/Downloads/Misc` tailored resumes are left as-is by owner's instruction.

## 8. Positioning tracks

The `Consolidated_Resumes` sets define five reusable positioning tracks — use these as the
frame for any new portfolio section:

1. **DevOps / Platform** — Azure & multi-cloud, Terraform/Bicep, CI/CD & GitOps, developer productivity
2. **SRE / Infrastructure** — SRE practice, Kubernetes, GitOps & IaC, observability, incident management
3. **AI-ML Infrastructure** — distributed training, GPU orchestration, model serving & MLOps, edge AI
4. **Performance / HPC** — systems performance analysis, GPU optimisation, Linux kernel tuning, Slurm
5. **Cloud Architect** — architecture, landing zones, reference patterns, governance

## 9. Positioning

- Target: Staff / Principal IC — DevOps, Platform Engineering, SRE, GPU-AI infrastructure
- Bay Area (Milpitas) · open to Austin/Plano · full-time or contract
- Differentiators, in order: 65-GPU bare-metal platform ownership · 
  $8M cost takeout · agentic infra tooling (cloudforge) · 18 years from Linux admin to GPU platforms

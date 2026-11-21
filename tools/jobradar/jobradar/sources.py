"""Job feed readers for each careers-site type.

Each reader returns a list of job dicts:
  uid, company, title, location, url, posted (YYYY-MM-DD or ""), desc (text or None), pay
A job with desc None gets a `detail` callable that fetches the description and real location
only when the job passes the title check (saves hundreds of calls per run).
"""
import datetime as dt
import html
import json
import re
import urllib.parse

from .net import fetch

TAG = re.compile(r"<[^>]+>")


def clean(htmltext):
    if not htmltext:
        return ""
    t = html.unescape(html.unescape(htmltext))
    t = TAG.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def iso_from_epoch(sec):
    try:
        return dt.datetime.fromtimestamp(int(sec), dt.timezone.utc).date().isoformat()
    except Exception:
        return ""


def iso_date(s):
    return (s or "")[:10]


def workday_age_to_date(posted_on):
    """'Posted Today' / 'Posted Yesterday' / 'Posted 5 Days Ago' / 'Posted 30+ Days Ago'."""
    s = (posted_on or "").lower()
    today = dt.date.today()
    if "today" in s:
        return today.isoformat()
    if "yesterday" in s:
        return (today - dt.timedelta(days=1)).isoformat()
    m = re.search(r"(\d+)\+?\s*days?", s)
    if m:
        return (today - dt.timedelta(days=int(m.group(1)))).isoformat()
    return ""


# ---------------------------------------------------------------- Ashby (OpenAI, Perplexity, ...)
def ashby(c, cfg):
    d = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{c['slug']}?includeCompensation=true")
    out = []
    for j in d.get("jobs", []):
        if not j.get("isListed", True):
            continue
        locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        country = (((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry")) or ""
        loc = "; ".join(x for x in locs if x)
        if country and country not in loc:
            loc += f" ({country})"
        if j.get("isRemote") and "remote" not in loc.lower():
            loc += " (Remote)"
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or ""
        out.append(dict(uid=f"ashby:{c['slug']}:{j['id']}", company=c["name"], title=j["title"].strip(),
                        location=loc, url=j.get("jobUrl"), posted=iso_date(j.get("publishedAt")),
                        desc=j.get("descriptionPlain") or "", pay=comp))
    return out


# ---------------------------------------------------------------- Greenhouse (Anthropic, Stripe, ...)
def greenhouse(c, cfg):
    d = fetch(f"https://boards-api.greenhouse.io/v1/boards/{c['slug']}/jobs?content=true")
    out = []
    for j in d.get("jobs", []):
        desc = clean(j.get("content"))
        m = re.search(r"\$\s?\d{2,3}[,\d]*(?:\s?[-–]\s?\$\s?\d{2,3}[,\d]*)?(?:\s?USD)?", desc)
        out.append(dict(uid=f"gh:{c['slug']}:{j['id']}", company=c["name"], title=j["title"].strip(),
                        location=(j.get("location") or {}).get("name", ""), url=j.get("absolute_url"),
                        posted=iso_date(j.get("first_published") or j.get("updated_at")),
                        desc=desc, pay=m.group(0) if m else ""))
    return out


# ---------------------------------------------------------------- Workday (NVIDIA, Intel, Salesforce, ...)
def workday(c, cfg):
    tenant, host, site = c["tenant"], c["host"], c["site"]
    base = f"https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}"
    public = f"https://{tenant}.{host}.myworkdayjobs.com/en-US/{site}"
    seen, out = set(), []
    pages = int(cfg.get("workday_pages", 2))
    for q in cfg["search_queries"]:
        for p in range(pages):
            d = fetch(base + "/jobs", {"appliedFacets": {}, "limit": 20, "offset": p * 20, "searchText": q})
            posts = d.get("jobPostings") or []
            for j in posts:
                path = j.get("externalPath")
                if not path or path in seen:
                    continue
                seen.add(path)
                loc = j.get("locationsText") or ""
                # externalPath often starts with the location, e.g. /job/US-CA-Santa-Clara/...
                hint = path.split("/")[2] if path.count("/") >= 3 else ""
                job = dict(uid=f"wd:{tenant}:{path.rsplit('_', 1)[-1]}", company=c["name"],
                           title=(j.get("title") or "").strip(), location=f"{loc} [{hint.replace('-', ' ')}]",
                           url=public + path, posted=workday_age_to_date(j.get("postedOn")), desc=None, pay="")
                job["detail"] = (lambda path=path: _workday_detail(base, path))
                out.append(job)
            if len(posts) < 20:
                break
    return out


def _workday_detail(base, path):
    d = fetch(base + path).get("jobPostingInfo", {})
    locs = [d.get("location") or ""] + list(d.get("additionalLocations") or [])
    country = (d.get("country") or {}).get("descriptor", "")
    loc = "; ".join(x for x in locs if x) + (f" ({country})" if country else "")
    desc = clean(d.get("jobDescription"))
    m = re.search(r"\$?\d{2,3},\d{3}(?:\.\d\d)?\s?(?:USD)?\s?[-–]\s?\$?\d{2,3},\d{3}(?:\.\d\d)?\s?(?:USD)?", desc)
    return dict(location=loc, desc=desc, posted=iso_date(d.get("startDate")),
                url=d.get("externalUrl"), pay=m.group(0) if m else "")


# ---------------------------------------------------------------- AMD (Jibe API)
def amd(c, cfg):
    seen, out = set(), []
    for q in cfg["search_queries"]:
        d = fetch("https://careers.amd.com/api/jobs?" + urllib.parse.urlencode({"keywords": q, "limit": 100, "page": 1}))
        for w in d.get("jobs", []):
            j = w.get("data", {})
            rid = j.get("req_id")
            if not rid or rid in seen:
                continue
            seen.add(rid)
            pay = ""
            lo, hi = (j.get("tags5") or [""])[0], (j.get("tags6") or [""])[0]
            if lo and hi:
                pay = f"{lo} – {hi}"
            out.append(dict(uid=f"amd:{rid}", company=c["name"], title=(j.get("title") or "").strip(),
                            location=f"{j.get('full_location') or j.get('location_name', '')} ({j.get('country', '')})",
                            url=f"https://careers.amd.com/careers-home/jobs/{rid}",
                            posted=iso_date(j.get("posted_date") or j.get("create_date")),
                            desc=clean((j.get("description") or "") + " " + (j.get("responsibilities") or "")), pay=pay))
    return out


# ---------------------------------------------------------------- Eightfold (Qualcomm, ...)
def eightfold(c, cfg):
    host, domain = c["host"], c["domain"]
    seen, out = set(), []
    for q in cfg["search_queries"]:
        for start in (0, 10, 20):
            d = fetch(f"https://{host}/api/pcsx/search?" + urllib.parse.urlencode(
                {"domain": domain, "query": q, "location": "United States", "start": start}))
            posts = (d.get("data") or {}).get("positions") or []
            for j in posts:
                pid = j.get("id")
                if not pid or pid in seen:
                    continue
                seen.add(pid)
                job = dict(uid=f"ef:{domain}:{pid}", company=c["name"], title=(j.get("name") or "").strip(),
                           location="; ".join(j.get("locations") or []), url=f"https://{host}/careers/job/{pid}",
                           posted=iso_from_epoch(j.get("postedTs")), desc=None, pay="")
                job["detail"] = (lambda pid=pid: _eightfold_detail(host, domain, pid))
                out.append(job)
            if len(posts) < 10:
                break
    return out


def _eightfold_detail(host, domain, pid):
    d = fetch(f"https://{host}/api/pcsx/position_details?" + urllib.parse.urlencode(
        {"position_id": pid, "domain": domain, "hl": "en"})).get("data", {})
    desc = clean(d.get("jobDescription"))
    m = re.search(r"\$\d{2,3},\d{3}(?:\.\d\d)?\s?[-–]\s?\$\d{2,3},\d{3}(?:\.\d\d)?", desc)
    return dict(desc=desc, pay=m.group(0) if m else "")


# ---------------------------------------------------------------- Google (careers page data)
def google(c, cfg):
    seen, out = set(), []
    for q in cfg["search_queries"]:
        for page in (1, 2):
            t = fetch("https://www.google.com/about/careers/applications/jobs/results/?" + urllib.parse.urlencode(
                {"q": q, "location": "United States", "page": page}), as_json=False)
            i = t.find("AF_initDataCallback({key: 'ds:1'")
            if i < 0:
                break
            j0 = t.find("data:", i) + 5
            k = t.find(", sideChannel", j0)
            try:
                rows = json.loads(t[j0:k])[0] or []
            except Exception:
                break
            for r in rows:
                gid = r[0]
                if gid in seen:
                    continue
                seen.add(gid)
                locs = "; ".join(x[0] for x in (r[9] or []) if x)
                parts = [r[n][1] for n in (3, 4, 10, 19) if len(r) > n and isinstance(r[n], list) and len(r[n]) > 1 and r[n][1]]
                created = r[12][0] if len(r) > 12 and r[12] else None
                out.append(dict(uid=f"google:{gid}", company=c["name"], title=r[1].strip(), location=locs,
                                url=f"https://www.google.com/about/careers/applications/jobs/results/{gid}",
                                posted=iso_from_epoch(created) if created else "", desc=clean(" ".join(parts)), pay=""))
            if len(rows) < 20:
                break
    return out


# ---------------------------------------------------------------- Apple (jobs.apple.com page data)
def apple(c, cfg):
    seen, out = set(), []
    for q in cfg["search_queries"]:
        for page in (1, 2):
            t = fetch("https://jobs.apple.com/en-us/search?" + urllib.parse.urlencode(
                {"search": q, "location": "united-states-USA", "page": page}), as_json=False)
            m = re.search(r'__staticRouterHydrationData = JSON.parse\((".*?")\);', t, re.S)
            if not m:
                break
            res = (json.loads(json.loads(m.group(1)))["loaderData"].get("search") or {}).get("searchResults") or []
            for r in res:
                pid = r.get("positionId")
                if not pid or pid in seen:
                    continue
                seen.add(pid)
                locs = "; ".join(f"{x.get('name', '')} ({x.get('countryName', '')})" for x in r.get("locations") or [])
                url = f"https://jobs.apple.com/en-us/details/{r.get('id') or pid}/{r.get('transformedPostingTitle', '')}"
                job = dict(uid=f"apple:{pid}", company=c["name"], title=(r.get("postingTitle") or "").strip(),
                           location=locs, url=url, posted=iso_date(r.get("postDateInGMT")), desc=None, pay="")
                job["detail"] = (lambda url=url, summary=r.get("jobSummary") or "": _apple_detail(url, summary))
                out.append(job)
            if len(res) < 20:
                break
    return out


def _apple_detail(url, summary):
    t = fetch(url, as_json=False)
    m = re.search(r'__staticRouterHydrationData = JSON.parse\((".*?")\);', t, re.S)
    text = summary
    page = clean(json.loads(m.group(1)) if m else t)
    pay = re.search(r"base pay range[^.]{0,200}", page, re.I)  # pay sentence sits deep in the page data
    i = page.find("jobSummary")
    body = page[i:i + 12000] if i >= 0 else page[:12000]
    return dict(desc=((pay.group(0) + " ") if pay else "") + text + " " + body)


# ---------------------------------------------------------------- ASML (job sitemap + job page)
def asml(c, cfg):
    t = fetch("https://www.asml.com/en/job_posting-sitemap.xml", as_json=False)
    out = []
    for loc, lastmod in re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]*)</lastmod>", t):
        slug = loc.rstrip("/").rsplit("/", 1)[-1]
        m = re.search(r"-?(j\d{6,})$", slug)
        jid = m.group(1) if m else slug
        title = re.sub(r"-+j\d{6,}$", "", slug).replace("--", " - ").replace("-", " ").strip().title()
        job = dict(uid=f"asml:{jid}", company=c["name"], title=title, location="", url=loc,
                   posted=iso_date(lastmod), desc=None, pay="")
        job["detail"] = (lambda loc=loc: _asml_detail(loc))
        out.append(job)
    return out


def _asml_detail(url):
    t = fetch(url, as_json=False)
    g = lambda k: (re.search(r'"%s"\s*:\s*"([^"]*)"' % k, t) or [None, ""])[1]
    title = re.search(r"<title>([^<|]+)", t)
    body = t
    m = re.search(r"<main.*?</main>", t, re.S)
    if m:
        body = m.group(0)
    res = dict(location=f"{g('location')} ({g('country')})", posted=iso_date(g("datePosted")), desc=clean(body)[:12000])
    if title:
        res["title"] = clean(title.group(1)).strip()
    return res


# ---------------------------------------------------------------- SmartRecruiters (ServiceNow, ...)
def smartrecruiters(c, cfg):
    co = c["slug"]
    seen, out = set(), []
    for q in cfg["search_queries"]:
        d = fetch(f"https://api.smartrecruiters.com/v1/companies/{co}/postings?" + urllib.parse.urlencode(
            {"q": q, "country": "us", "limit": 100}))
        for j in d.get("content", []):
            jid = j.get("id")
            if not jid or jid in seen:
                continue
            seen.add(jid)
            l = j.get("location") or {}
            loc = ", ".join(x for x in (l.get("city"), l.get("region"), (l.get("country") or "").upper()) if x)
            if l.get("remote"):
                loc += " (Remote)"
            job = dict(uid=f"sr:{co}:{jid}", company=c["name"], title=(j.get("name") or "").strip(), location=loc,
                       url=f"https://jobs.smartrecruiters.com/{co}/{jid}", posted=iso_date(j.get("releasedDate")),
                       desc=None, pay="")
            job["detail"] = (lambda ref=j.get("ref"): _sr_detail(ref))
            out.append(job)
    return out


def _sr_detail(ref):
    d = fetch(ref)
    sec = ((d.get("jobAd") or {}).get("sections") or {})
    desc = clean(" ".join((sec.get(k) or {}).get("text", "") for k in ("jobDescription", "qualifications", "additionalInformation")))
    m = re.search(r"\$\d{2,3},\d{3}\s?[-–]\s?\$\d{2,3},\d{3}", desc)
    return dict(desc=desc, pay=m.group(0) if m else "", url=d.get("postingUrl"))


READERS = dict(smartrecruiters=smartrecruiters, ashby=ashby, greenhouse=greenhouse, workday=workday, amd=amd, eightfold=eightfold,
               google=google, apple=apple, asml=asml)

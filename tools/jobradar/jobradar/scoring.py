"""Role-fit scoring. Score 0-100 = title (max 45) + level (max 15) + skills (max 30) + location (max 10) - penalties."""
import datetime as dt
import re

US_STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH "
             "OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US_STATE_NAMES = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
                  "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
                  "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri",
                  "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
                  "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
                  "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington",
                  "west virginia", "wisconsin", "wyoming"]
US_WORDS = ["united states", "usa", "u.s.", "us-", "us,", "(us)", "us remote", "remote us", "us - remote",
            "remote - us", "remote, us", "north america", "san francisco", "new york", "seattle", "austin",
            "sunnyvale", "santa clara", "san jose", "mountain view", "palo alto", "bay area", "boston", "chicago",
            "los angeles", "denver", "atlanta", "portland", "san diego", "milpitas", "redmond", "bellevue", "hillsboro",
            "folsom", "phoenix", "chandler", "raleigh", "dallas", "washington, dc", "nyc", "sfo"]
NON_US = ["india", "bangalore", "bengaluru", "hyderabad", "pune", "chennai", "noida", "gurgaon", "israel", "tel aviv",
          "united kingdom", "uk", "london", "ireland", "dublin", "germany", "munich", "berlin", "france", "paris",
          "netherlands", "veldhoven", "eindhoven", "amsterdam", "poland", "romania", "spain", "italy", "switzerland",
          "zurich", "sweden", "finland", "denmark", "norway", "belgium", "austria", "czech", "hungary", "ukraine",
          "canada", "toronto", "vancouver", "montreal", "mexico", "brazil", "argentina", "colombia", "costa rica",
          "china", "shanghai", "beijing", "shenzhen", "taiwan", "taipei", "hsinchu", "japan", "tokyo", "korea",
          "seoul", "singapore", "malaysia", "penang", "vietnam", "philippines", "australia", "sydney", "melbourne",
          "new zealand", "uae", "dubai", "saudi", "qatar", "south africa", "egypt", "turkey", "armenia", "serbia",
          "portugal", "lisbon", "greece", "kyiv", "kraków", "krakow", "gdansk", "wroclaw", "cluj", "bucharest"]


def _has(text, word):
    if len(word) <= 4 or word.isalpha() and len(word) <= 5:
        return re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", text) is not None
    return word in text


def location_info(loc, prefs):
    """Return (is_us: True/False/None, points 0-10, label)."""
    t = (loc or "").lower()
    if not t.strip(" ;()[]"):
        return None, 3, "location unknown"
    us = any(_has(t, w) for w in US_WORDS) or any(n in t for n in US_STATE_NAMES) or \
        re.search(r",\s*(" + "|".join(US_STATES) + r")\b", loc or "") is not None or \
        re.search(r"\bUS\b", loc or "") is not None
    non = any(_has(t, w) for w in NON_US)
    remote = "remote" in t
    if not us and remote and not non:
        us = True
    if not us and non:
        return False, 0, "outside US"
    if not us:
        return None, 3, "location unclear"
    if any(c in t for c in prefs.get("preferred_cities", [])):
        return True, 10, "Bay Area"
    if remote:
        return True, 8, "US remote"
    if "california" in t or re.search(r",\s*CA\b", loc or ""):
        return True, 8, "California"
    return True, 5, "US"


def title_check(title, prof):
    t = " " + title.lower().replace("/", " / ") + " "
    for x in prof["title_exclude"]:
        if _has(t, x):
            return None, [f"excluded: {x}"]
    hits = [(w, p) for w, p in prof["title_core"].items() if _has(t, w)]
    if not hits:
        return None, []
    hits.sort(key=lambda x: -x[1])
    pts = hits[0][1] + min(10, 4 * (len(hits) - 1))
    return min(45, pts), [h[0] for h in hits[:3]]


def score_job(job, cfg):
    prof = cfg["profile"]
    title_pts, title_hits = title_check(job["title"], prof)
    if title_pts is None or title_pts < prof.get("min_title_points", 14):
        return None
    reasons, flags = [], []
    reasons.append("title: " + ", ".join(title_hits))

    t = " " + job["title"].lower() + " "
    lvl = max([p for w, p in prof["seniority"].items() if _has(t, w)] or [0])
    if lvl:
        reasons.append("senior level")

    desc = (job.get("desc") or "").lower()
    skill_pts, found = 0, []
    for w, p in prof["skills"].items():
        if _has(desc, w) or _has(t, w):
            skill_pts += p
            found.append(w)
    skill_pts = min(30, skill_pts)
    if found:
        reasons.append("skills: " + ", ".join(found[:8]))

    is_us, loc_pts, loc_label = location_info(job.get("location"), prof)
    if cfg["filters"].get("us_only", True) and is_us is False:
        return None
    reasons.append(loc_label)

    penalty = 0
    for pat, label, pen in [
        (r"(not|unable to|cannot|can't|won't|will not)\s+(be\s+)?(eligible\s+for\s+|offer\s+|provide\s+|able to\s+)?(visa\s+)?sponsor",
         "No visa sponsorship", prof.get("no_sponsorship_penalty", 15)),
        (r"(security clearance|active clearance|ts/sci|top secret)", "Clearance needed", 10),
        (r"(must be a|requires?|required to be a)\s+u\.?s\.?\s+citizen", "US citizen only", 15),
    ]:
        if re.search(pat, desc):
            flags.append(label)
            penalty += pen

    # first "N+ years of ... experience" phrase is usually the real requirement
    m = re.search(r"(\d{1,2})\+?\s*(?:or more\s+)?years?(?:\s+of)?[^.]{0,60}?experience", desc)
    if m and 2 <= int(m.group(1)) <= 20:
        reasons.append(f"asks {m.group(1)}+ yrs")

    score = max(0, min(100, title_pts + lvl + skill_pts + loc_pts - penalty))
    return dict(score=score, reasons=reasons, flags=flags)


def age_days(posted):
    try:
        return (dt.date.today() - dt.date.fromisoformat(posted[:10])).days
    except Exception:
        return None

#!/usr/bin/env python3
"""Job Radar for the portfolio site.

Runs one check across all companies in config.json, writes the matches to
jobs/radar/data/jobs.json (read by /jobs/radar/), and emails new matches when the
JOBRADAR_GMAIL_APP_PASSWORD secret is set. Run by .github/workflows/jobradar.yml.

  python tools/jobradar/publish.py            check + publish + email
  python tools/jobradar/publish.py --no-email  check + publish only
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from jobradar import mailer  # noqa: E402
from jobradar.engine import Runner  # noqa: E402
from jobradar.scoring import age_days  # noqa: E402
from jobradar.store import Store  # noqa: E402

OUT = os.path.join(ROOT, "jobs", "radar", "data", "jobs.json")
PAGE = "https://www.sudhakarchundu.org/jobs/radar/"


def load_cfg():
    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        return json.load(f)


def seed_from_published(store):
    """When the Actions cache is empty, rebuild 'already emailed' state from the last published file."""
    if store.get("seeded") or store.jobs() or not os.path.exists(OUT):
        return
    with open(OUT, encoding="utf-8") as f:
        old = json.load(f)
    for j in old.get("jobs", []):
        store.upsert(dict(uid=j["uid"], company=j["company"], title=j["title"], location=j.get("location", ""),
                          url=j.get("url", ""), posted=j.get("posted", ""), pay=j.get("pay", ""), desc=""),
                     dict(score=j["score"], reasons=j.get("reasons", []), flags=j.get("flags", [])))
    store.mark_emailed([j["uid"] for j in old.get("jobs", [])])
    store.put("emailed_once", True)
    store.put("seeded", True)
    print(f"Seeded {len(old.get('jobs', []))} jobs from the last published file")


def export(cfg, store):
    f = cfg["filters"]
    blocked = {b.lower() for b in cfg.get("exclude_companies", [])}
    max_age, min_show = int(f.get("max_age_days", 45)), int(f.get("min_score_show", 45))
    jobs = []
    for j in store.jobs(min_show):
        if j["company"].lower() in blocked:
            continue
        a = age_days(j.get("posted") or "")
        if a is not None and a > max_age:
            continue
        loc = (j.get("location") or "").split(" [")[0].replace(" (United States of America)", "")
        jobs.append(dict(uid=j["uid"], company=j["company"], title=j["title"], location=loc[:160], url=j["url"],
                         posted=j.get("posted") or "", pay=j.get("pay") or "", score=j["score"],
                         reasons=j["reasons"], flags=j["flags"], first_seen=int(j["first_seen"])))
    src = store.get("sources", {})
    meta = dict(updated=int(time.time()), every_hours=cfg["schedule"]["every_hours"],
                companies=sorted(c["name"] for c in cfg["companies"]
                                 if c.get("enabled", True) and c["name"].lower() not in blocked),
                sites_ok=sum(1 for v in src.values() if v.get("ok")),
                sites_failed=sorted(k for k, v in src.items() if not v.get("ok")))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, jobs=jobs), fh, separators=(",", ":"))
    print(f"Published {len(jobs)} jobs to {os.path.relpath(OUT, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-email", action="store_true")
    a = ap.parse_args()
    cfg = load_cfg()
    db = os.environ.get("JOBRADAR_DB", os.path.join(HERE, "data", "jobradar.db"))
    os.makedirs(os.path.dirname(db), exist_ok=True)
    store = Store(db)
    seed_from_published(store)
    runner = Runner(lambda: cfg, store)
    runner.run()
    bad = [k for k, v in store.get("sources", {}).items() if not v.get("ok")]
    print(f"Check done: {runner.state['new']} new matches; sites with errors: {', '.join(bad) or 'none'}")
    export(cfg, store)
    if not a.no_email:
        try:
            r = mailer.digest(cfg, store, PAGE)
            print("Email:", r)
        except Exception as e:  # never fail the publish because of email
            print("Email failed:", e)


if __name__ == "__main__":
    main()

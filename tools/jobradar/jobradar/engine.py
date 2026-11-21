"""One check run: read every enabled company, score jobs, save matches."""
import concurrent.futures as cf
import threading
import time
import traceback

from .net import FetchError
from .pay import fmt, parse_pay
from .scoring import age_days, location_info, score_job, title_check
from .sources import READERS


def set_pay(job):
    raw = job.get("pay") or ""
    rng = parse_pay(raw)
    if not rng or rng[0] == rng[1]:  # single figure: look for the full range in the job text
        rng = parse_pay(job.get("desc") or "") or rng
    job["pay"] = fmt(rng, raw) if rng else ""


class Runner:
    def __init__(self, cfg_loader, store):
        self.cfg_loader = cfg_loader
        self.store = store
        self.lock = threading.Lock()
        self.state = dict(running=False, done=0, total=0, current="", started=None, finished=None, new=0)

    def blocked(self, cfg):
        return {b.lower() for b in cfg.get("exclude_companies", [])}

    def companies(self, cfg):
        bl = self.blocked(cfg)
        return [c for c in cfg["companies"] if c.get("enabled", True) and c["name"].lower() not in bl]

    def run(self):
        if not self.lock.acquire(blocking=False):
            return False
        try:
            cfg = self.cfg_loader()
            comps = self.companies(cfg)
            self.state.update(running=True, done=0, total=len(comps), current="", started=time.time(), new=0)
            results = self.store.get("sources", {})
            with cf.ThreadPoolExecutor(int(cfg.get("parallel", 6))) as ex:
                futs = {ex.submit(self._one, c, cfg): c for c in comps}
                for f in cf.as_completed(futs):
                    c = futs[f]
                    results[c["name"]] = f.result()
                    self.state["done"] += 1
                    self.state["current"] = c["name"]
            self.store.put("sources", results)
            self.store.put("last_run", time.time())
            self.state.update(running=False, finished=time.time())
            return True
        finally:
            self.state["running"] = False
            self.lock.release()

    def _one(self, c, cfg):
        t0 = time.time()
        try:
            listed = READERS[c["type"]](c, cfg)
        except FetchError as e:
            return dict(ok=False, error=str(e), at=time.time())
        except Exception as e:
            return dict(ok=False, error=f"{type(e).__name__}: {e}", at=time.time(), trace=traceback.format_exc()[-800:])
        prof, filt = cfg["profile"], cfg["filters"]
        max_age = int(filt.get("max_age_days", 45))
        detail_left = int(cfg.get("detail_limit_per_company", 80))
        in_db = {j["uid"] for j in self.store.jobs()}
        matched, new, errors = 0, 0, 0
        need_detail = [j for j in listed if j.get("desc") is None]
        seen = self.store.known([j["uid"] for j in need_detail])
        touched, fresh_seen = [], []
        for job in listed:
            tp, _ = title_check(job["title"], prof)
            if tp is None or tp < prof.get("min_title_points", 14):
                continue
            a = age_days(job.get("posted", ""))
            if a is not None and a > max_age:
                continue
            if job.get("desc") is None:
                if job["uid"] in in_db:  # already have its details: just re-score with current settings
                    old = self.store.saved_detail(job["uid"])
                    job.pop("detail", None)
                    job.update({k: v for k, v in old.items() if v})
                    set_pay(job)
                    res = score_job(job, cfg)
                    if res:
                        self.store.upsert(job, res)
                        matched += 1
                    continue
                if job["uid"] in seen:
                    continue
                is_us, _, _ = location_info(job.get("location"), prof)
                if filt.get("us_only", True) and is_us is False:
                    continue
                if detail_left <= 0:
                    continue
                detail_left -= 1
                try:
                    extra = job.pop("detail")()
                    job.update({k: v for k, v in extra.items() if v})
                    job.setdefault("desc", "")
                    if job["desc"] is None:
                        job["desc"] = ""
                    fresh_seen.append(job["uid"])
                except Exception:
                    errors += 1
                    continue
                a = age_days(job.get("posted", ""))
                if a is not None and a > max_age:
                    continue
            job.pop("detail", None)
            set_pay(job)
            res = score_job(job, cfg)
            if not res:
                continue
            matched += 1
            if self.store.upsert(job, res):
                new += 1
        self.store.touch(touched)
        self.store.mark_seen(fresh_seen)
        self.state["new"] += new
        return dict(ok=True, listed=len(listed), matched=matched, new=new, detail_errors=errors,
                    seconds=round(time.time() - t0, 1), at=time.time())

"""SQLite store: remembers every matched job, when it was first seen, and what you did with it."""
import json
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs(
  uid TEXT PRIMARY KEY, company TEXT, title TEXT, location TEXT, url TEXT, posted TEXT, pay TEXT,
  score INTEGER, reasons TEXT, flags TEXT, snippet TEXT,
  first_seen REAL, last_seen REAL, status TEXT DEFAULT 'new', emailed INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS seen(uid TEXT PRIMARY KEY, first_seen REAL);
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
CREATE INDEX IF NOT EXISTS jobs_score ON jobs(score);
"""


class Store:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        with self._db() as db:
            db.executescript(SCHEMA)

    def _db(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    # "seen" = every job we already looked at (matched or not), so details are fetched only once
    def known(self, uids):
        with self._db() as db:
            rows = db.execute("SELECT uid FROM seen").fetchall()
        s = {r[0] for r in rows}
        return {u for u in uids if u in s}

    def mark_seen(self, uids):
        now = time.time()
        with self.lock, self._db() as db:
            db.executemany("INSERT OR IGNORE INTO seen VALUES(?,?)", [(u, now) for u in uids])

    def upsert(self, job, res):
        now = time.time()
        with self.lock, self._db() as db:
            cur = db.execute("SELECT uid FROM jobs WHERE uid=?", (job["uid"],)).fetchone()
            vals = (job["company"], job["title"], job.get("location", ""), job.get("url", ""), job.get("posted", ""),
                    job.get("pay", ""), res["score"], json.dumps(res["reasons"]), json.dumps(res["flags"]),
                    (job.get("desc") or "")[:15000])
            if cur:
                db.execute("""UPDATE jobs SET company=?,title=?,location=?,url=?,posted=?,pay=?,score=?,reasons=?,
                              flags=?,snippet=?,last_seen=? WHERE uid=?""", vals + (now, job["uid"]))
                return False
            db.execute("""INSERT INTO jobs(company,title,location,url,posted,pay,score,reasons,flags,snippet,
                          uid,first_seen,last_seen) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                       vals + (job["uid"], now, now))
            return True

    def saved_detail(self, uid):
        with self._db() as db:
            r = db.execute("SELECT snippet, location, url, posted, pay FROM jobs WHERE uid=?", (uid,)).fetchone()
        return dict(desc=r[0] or "", location=r[1], url=r[2], posted=r[3], pay=r[4]) if r else None

    def touch(self, uids):
        now = time.time()
        with self.lock, self._db() as db:
            db.executemany("UPDATE jobs SET last_seen=? WHERE uid=?", [(now, u) for u in uids])

    def jobs(self, min_score=0, status=None):
        q, a = "SELECT * FROM jobs WHERE score>=?", [min_score]
        if status and status != "all":
            q += " AND status=?"
            a.append(status)
        with self._db() as db:
            rows = [dict(r) for r in db.execute(q + " ORDER BY score DESC, first_seen DESC", a)]
        for r in rows:
            r["snippet"] = (r["snippet"] or "")[:300]
            r["reasons"] = json.loads(r["reasons"] or "[]")
            r["flags"] = json.loads(r["flags"] or "[]")
        return rows

    def set_status(self, uid, status):
        with self.lock, self._db() as db:
            db.execute("UPDATE jobs SET status=? WHERE uid=?", (status, uid))

    def to_email(self, min_score):
        with self._db() as db:
            rows = [dict(r) for r in db.execute(
                "SELECT * FROM jobs WHERE emailed=0 AND status IN ('new','saved') AND score>=? "
                "ORDER BY score DESC", (min_score,))]
        for r in rows:
            r["flags"] = json.loads(r["flags"] or "[]")
            r["reasons"] = json.loads(r["reasons"] or "[]")
        return rows

    def mark_emailed(self, uids):
        with self.lock, self._db() as db:
            db.executemany("UPDATE jobs SET emailed=1 WHERE uid=?", [(u,) for u in uids])

    def get(self, k, default=None):
        with self._db() as db:
            r = db.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        return json.loads(r[0]) if r else default

    def put(self, k, v):
        with self.lock, self._db() as db:
            db.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (k, json.dumps(v)))

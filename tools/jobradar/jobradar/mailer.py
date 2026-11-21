"""Gmail digest: new role-fit jobs since the last email, sent through Gmail SMTP with an app password."""
import html
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .pay import parse_pay
from .scoring import age_days


def app_password(cfg):
    e = cfg["email"]
    return (os.environ.get(e.get("app_password_env", "JOBRADAR_GMAIL_APP_PASSWORD")) or e.get("app_password") or "").replace(" ", "")


def is_ready(cfg):
    e = cfg["email"]
    return bool(e.get("enabled") and e.get("to") and e.get("from") and app_password(cfg))


def _row(j):
    a = age_days(j.get("posted") or "")
    age = "today" if a == 0 else (f"{a}d ago" if a is not None else "")
    flags = "".join(f'<span style="background:#fde8e8;color:#9b1c1c;border-radius:4px;padding:1px 6px;'
                    f'margin-left:4px;font-size:11px">{html.escape(f)}</span>' for f in j.get("flags", []))
    color = "#0e7a3e" if j["score"] >= 75 else ("#1a73e8" if j["score"] >= 60 else "#666")
    loc = (j.get("location") or "").split(" [")[0].replace(" (United States of America)", "")
    pay = html.escape(j.get("pay") or "not listed")
    return (f'<tr><td style="padding:7px 8px;font-weight:700;color:{color};font-size:15px;vertical-align:top">{j["score"]}</td>'
            f'<td style="padding:7px 8px;vertical-align:top"><a href="{html.escape(j["url"] or "")}" style="color:#1f1f1f;'
            f'font-weight:600;text-decoration:none">{html.escape(j["title"])}</a>{flags}<br>'
            f'<span style="color:#5e5e5e;font-size:12px">{html.escape(loc[:90])}</span></td>'
            f'<td style="padding:7px 8px;vertical-align:top;font-size:13px;white-space:nowrap;color:#188038">{pay}</td>'
            f'<td style="padding:7px 8px;vertical-align:top;color:#5e5e5e;font-size:12px;white-space:nowrap">{age}</td></tr>')


def build(groups, ui_url, total, floor=0):
    """groups: list of (company, shown_jobs, hidden_count)."""
    pay_note = f"${floor // 1000}K or more" if floor else "any amount"
    parts = []
    for company, jobs, more in groups:
        parts.append(f'<tr><td colspan="4" style="padding:14px 8px 4px;font-size:15px;font-weight:700;'
                     f'border-bottom:1px solid #e1e3e1">{html.escape(company)}</td></tr>')
        parts.extend(_row(j) for j in jobs)
        if more:
            parts.append(f'<tr><td></td><td colspan="3" style="padding:2px 8px 6px;font-size:12px">'
                         f'<a href="{ui_url}" style="color:#1a73e8">and {more} more {html.escape(company)} '
                         f'job{"s" if more > 1 else ""} on the page</a></td></tr>')
    names = [g[0] for g in groups]
    body = (f'<div style="font-family:Arial,Helvetica,sans-serif;max-width:780px;color:#1f1f1f">'
            f'<h2 style="margin:0 0 4px">Job Radar: {total} new role-fit jobs at {len(names)} companies</h2>'
            f'<p style="color:#5e5e5e;margin:0 0 6px">Best 3 per company shown. Pay range reaches {pay_note}. Fit is a score out of 100.</p>'
            f'<table style="border-collapse:collapse;width:100%">'
            f'<tr style="text-align:left;color:#5e5e5e;font-size:12px"><th style="padding:6px 8px">Fit</th>'
            f'<th style="padding:6px 8px">Job and location</th><th style="padding:6px 8px">Pay</th>'
            f'<th style="padding:6px 8px">Posted</th></tr>{"".join(parts)}</table>'
            f'<p style="color:#777;font-size:12px;margin-top:14px">See every match, and mark jobs saved or applied, at '
            f'<a href="{ui_url}">{ui_url}</a></p></div>')
    subject = f"Job Radar: {total} new jobs at {len(names)} companies ({', '.join(names[:5])}{'…' if len(names) > 5 else ''})"
    return subject, body


def pick(cfg, jobs):
    """Group by company, top companies first, at most N jobs each."""
    per = int(cfg["email"].get("per_company", 3))
    tier = {c["name"]: c.get("tier", 2) for c in cfg["companies"]}
    by = {}
    for j in sorted(jobs, key=lambda x: -x["score"]):
        by.setdefault(j["company"], []).append(j)
    order = sorted(by, key=lambda c: (tier.get(c, 3), -by[c][0]["score"]))
    groups = [(c, by[c][:per], max(0, len(by[c]) - per)) for c in order]
    return groups[: int(cfg["email"].get("max_companies", 30))]


def send(cfg, subject, body_html):
    e = cfg["email"]
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, e["from"], e["to"]
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    with smtplib.SMTP(e.get("smtp_host", "smtp.gmail.com"), int(e.get("smtp_port", 587)), timeout=30) as s:
        s.starttls()
        s.login(e["from"], app_password(cfg))
        s.sendmail(e["from"], [x.strip() for x in e["to"].split(",")], msg.as_string())


def digest(cfg, store, ui_url, force=False, out_dir=None):
    """Email new matches since the last email, grouped by company."""
    f = cfg["filters"]
    blocked = {b.lower() for b in cfg.get("exclude_companies", [])}
    first = not store.get("emailed_once", False)
    max_age = int(f.get("max_age_days" if first else "email_max_age_days", 14))  # first email covers the backlog
    cands = [j for j in store.to_email(int(f.get("min_score_email", 60)))
             if j["company"].lower() not in blocked and (age_days(j.get("posted") or "") or 0) <= max_age]
    floor = int(f.get("min_pay_top", 0))
    if floor:  # pay range must reach the floor (top of range); jobs with no pay listed only if allowed
        def pay_ok(j):
            r = parse_pay(j.get("pay") or "")
            return r[1] >= floor if r else bool(f.get("include_unlisted_pay", False))
        cands = [j for j in cands if pay_ok(j)]
    if cfg["email"].get("skip_no_sponsorship", True):
        cands = [j for j in cands if not any("sponsor" in x.lower() or "citizen" in x.lower() for x in j["flags"])]
    backlog = [j["uid"] for j in store.to_email(0)]
    if not cands and not force:
        return dict(sent=False, reason="no new matches")
    groups = pick(cfg, cands)
    if groups:
        subject, body = build(groups, ui_url, len(cands), floor)
    else:
        subject, body = ("Job Radar: test email, no new matches right now",
                         "<p>Job Radar email is working. New matches will arrive here.</p>")
    if out_dir:
        with open(os.path.join(out_dir, "last_digest.html"), "w", encoding="utf-8") as fh:
            fh.write(body)
    if not is_ready(cfg):
        return dict(sent=False, reason="email not set up (add your Gmail app password)", count=len(cands))
    send(cfg, subject, body)
    # everything considered this time is marked sent; the extra jobs per company stay on the page
    store.mark_emailed(backlog if not store.get("emailed_once", False) else [j["uid"] for j in cands])
    store.put("emailed_once", True)
    store.put("last_email", time.time())
    return dict(sent=True, count=len(cands), companies=len(groups))

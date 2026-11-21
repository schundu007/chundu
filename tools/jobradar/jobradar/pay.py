"""Pull a yearly US pay range out of any posting text and show it the same way for every company."""
import re

_AMT = r"\$\s?(\d{2,3}(?:,\d{3})+|\d{5,7}(?![\d,])|\d{2,3}(?:\.\d+)?\s?[kK])(?:\.\d{2})?|(\d{2,3},\d{3})(?:\.\d{2})?\s?USD"
_RANGE = re.compile(r"(?:%s)(?:\s?USD)?(?:\s?/\s?(?:yr|year)\.?)?\s{0,3}(?:-|–|—|to|and)\s{0,3}(?:USD\s?)?(?:%s)" % (_AMT, _AMT),
                    re.I)
_ONE = re.compile(_AMT, re.I)
_BARE = re.compile(r"(?<![\d,.])(\d{2,3},\d{3})(?:\.\d{2})?\s{0,3}(?:-|–|—|to)\s{0,3}(\d{2,3},\d{3})(?:\.\d{2})?(?![\d,])")
_HINT = re.compile(r"salary|pay|compensation|base|range|ote|annual|usd", re.I)


def _num(s):
    s = (s or "").replace(",", "").replace(" ", "").lower()
    if not s:
        return None
    if s.endswith("k"):
        return int(float(s[:-1]) * 1000)
    try:
        return int(float(s))
    except ValueError:
        return None


def _ok(n):
    return n is not None and 40_000 <= n <= 2_500_000


def parse_pay(text):
    """Return (low, high) in dollars per year, or None."""
    if not text:
        return None
    text = text.replace(" ", " ")
    best = None
    for m in _RANGE.finditer(text):
        lo, hi = _num(m.group(1) or m.group(2)), _num(m.group(3) or m.group(4))
        if not (_ok(lo) and _ok(hi)):
            continue
        if hi < lo:
            lo, hi = hi, lo
        near = _HINT.search(text[max(0, m.start() - 220): m.end() + 40]) is not None
        if near:
            return lo, hi
        best = best or (lo, hi)
    if best:
        return best
    for m in _BARE.finditer(text):  # "165,500 - 313,500" with no $ sign (HPE, Marvell)
        lo, hi = _num(m.group(1)), _num(m.group(2))
        if _ok(lo) and _ok(hi) and (len(text) < 40 or _HINT.search(text[max(0, m.start() - 220): m.start()])):
            return min(lo, hi), max(lo, hi)
    for m in _ONE.finditer(text):  # a single figure next to pay words, e.g. "base salary $250,000"
        n = _num(m.group(1) or m.group(2))
        if _ok(n) and _HINT.search(text[max(0, m.start() - 120): m.end() + 20]):
            return n, n
    return None


def fmt(rng, raw=""):
    if not rng:
        return ""
    k = lambda n: f"${round(n / 1000)}K"
    s = k(rng[0]) if rng[0] == rng[1] else f"{k(rng[0])} – {k(rng[1])}"
    if "equity" in (raw or "").lower() or "rsu" in (raw or "").lower() or "stock" in (raw or "").lower():
        s += " + equity"
    return s

"""Small HTTP helper: polite per-host rate limiting, retries, clear SSL error messages."""
import json
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (JobRadar personal job search; +https://github.com/schundu007)"

_host_locks = {}
_host_last = {}
_guard = threading.Lock()
MIN_GAP = 0.35  # seconds between calls to the same host
HOST_GAP = {"careers.qualcomm.com": 2.0}  # slower sites


def _ssl_context():
    try:
        import certifi  # optional, helps on python.org builds for macOS
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_CTX = _ssl_context()


class FetchError(Exception):
    pass


def _wait_turn(host):
    with _guard:
        lock = _host_locks.setdefault(host, threading.Lock())
    with lock:
        gap = time.time() - _host_last.get(host, 0)
        need = HOST_GAP.get(host, MIN_GAP)
        if gap < need:
            time.sleep(need - gap)
        _host_last[host] = time.time()


def fetch(url, data=None, as_json=True, timeout=30, retries=3):
    host = urllib.parse.urlparse(url).netloc
    body = json.dumps(data).encode() if data is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.5"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    last = None
    for attempt in range(retries):
        _wait_turn(host)
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
                text = r.read().decode("utf-8", "replace")
            return json.loads(text) if as_json else text
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1) + (8 * (attempt + 1) if e.code == 429 else 0))
                continue
            raise FetchError(f"HTTP {e.code} from {host}")
        except urllib.error.URLError as e:
            last = e
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise FetchError(
                    "SSL certificates are missing for Python. On a Mac, open "
                    "Applications > Python 3.x and run 'Install Certificates.command', then restart Job Radar."
                )
            time.sleep(2 * (attempt + 1))
        except (TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise FetchError(f"{host}: {last}")

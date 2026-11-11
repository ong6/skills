#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "readabilipy", "markdownify", "protego"]
# ///
"""Read one page that sits behind a Cloudflare browser challenge, through a local FlareSolverr.

FlareSolverr (https://github.com/FlareSolverr/FlareSolverr) opens the URL in its own Chrome, waits
for the challenge to clear and returns the HTML. This script starts its container when none is
answering, checks robots.txt through it (a challenged host serves robots.txt behind the same
challenge), prints the page as readable markdown in fetch.py's format. The container is shared by every
session on the machine and stops itself after IDLE_MINUTES without a request.

It clears the automatic "Just a moment..." check only. It does not solve CAPTCHAs, log in or pass
paywalls; those end as VERDICT: challenge and go to the human.

Usage:
  flare.py <url> [--raw] [--max-length N] [--start-index N] [--ignore-robots] [--timeout S]
  flare.py --stop        stop the container now

  FLARESOLVERR_URL   use an already running instance instead (it is never started or stopped)

Exit codes: 0 useful content · 1 refused (robots.txt or off-limits host) · 2 fetch or setup error ·
3 thin page · 4 challenge not cleared.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch import MIN_USEFUL_CHARS, UA_AUTONOMOUS, blocked_host, html_to_markdown, robots_url  # noqa: E402

IMAGE = "ghcr.io/flaresolverr/flaresolverr:v3.5.2"
CONTAINER = "web-extract-flaresolverr"
LOCAL_URL = "http://127.0.0.1:8191"
IDLE_MINUTES = 5
STAMP = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "web-extract" / "flaresolverr.stamp"
CHALLENGE_TITLES = ("just a moment", "attention required", "security check", "access denied")


class FlareError(Exception):
    def __init__(self, verdict: str, hint: str, code: int):
        super().__init__(hint)
        self.verdict, self.hint, self.code = verdict, hint, code


def ready(base: str) -> bool:
    import httpx

    try:
        return "ready" in httpx.get(base + "/", timeout=3).text.lower()
    except httpx.HTTPError:
        return False


def touch_stamp() -> None:
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.touch()


def start_reaper() -> None:
    """Detached loop: stop the container once no request has touched the stamp for IDLE_MINUTES."""
    loop = (f'while sleep 30; do docker inspect {CONTAINER} >/dev/null 2>&1 || exit 0; '
            f'[ -n "$(find "$1" -mmin +{IDLE_MINUTES} 2>/dev/null)" ] && {{ docker stop {CONTAINER} >/dev/null 2>&1; exit 0; }}; done')
    subprocess.Popen(["sh", "-c", loop, "flare-reaper", str(STAMP)], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def start_container(wait: int = 90) -> None:
    """Start the pinned image bound to localhost only, and wait until it answers."""
    if not shutil.which("docker"):
        raise FlareError("error", "docker is not installed; FlareSolverr needs it (or set FLARESOLVERR_URL)", 2)
    run = subprocess.run(
        ["docker", "run", "-d", "--rm", "--name", CONTAINER, "-p", "127.0.0.1:8191:8191",
         "-e", "LOG_LEVEL=info", IMAGE],
        capture_output=True, text=True)
    racing = run.returncode != 0 and "already in use" in run.stderr  # another session is starting it
    if run.returncode != 0 and not racing:
        err = run.stderr.strip().splitlines()[-1] if run.stderr.strip() else "docker run failed"
        hint = "start the Docker daemon first (for example `colima start`)" if "daemon" in err.lower() else err
        raise FlareError("error", f"could not start FlareSolverr: {hint}", 2)
    if not racing:
        touch_stamp()
        start_reaper()
    deadline = time.time() + wait
    while time.time() < deadline:
        if ready(LOCAL_URL):
            return
        time.sleep(2)
    raise FlareError("error", f"FlareSolverr did not become ready within {wait}s", 2)


def stop_container() -> None:
    if shutil.which("docker"):
        subprocess.run(["docker", "stop", CONTAINER], capture_output=True)


def solve(base: str, url: str, timeout: int) -> dict:
    """One request.get; returns FlareSolverr's `solution`, or raises FlareError."""
    import httpx

    try:
        r = httpx.post(base + "/v1", json={"cmd": "request.get", "url": url, "maxTimeout": timeout * 1000},
                       timeout=timeout + 30)
        data = r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise FlareError("error", f"FlareSolverr request failed: {e!r}", 2) from e
    if data.get("status") != "ok":
        msg = data.get("message") or "unknown FlareSolverr error"
        if "challenge" in msg.lower() or "captcha" in msg.lower() or "timeout" in msg.lower():
            raise FlareError("challenge", f"{msg} A CAPTCHA or a stricter check needs a human; try Wayback.", 4)
        raise FlareError("error", msg, 2)
    return data.get("solution") or {}


def pre_text(page: str) -> str:
    """Chrome wraps a text/plain body in <pre>; return the plain text."""
    m = re.search(r"<pre[^>]*>([\s\S]*?)</pre>", page, re.I)
    return html.unescape(m.group(1) if m else re.sub(r"<[^>]+>", "", page))


def robots_allows(base: str, url: str, timeout: int) -> tuple[bool, str]:
    from protego import Protego

    r_url = robots_url(url)
    try:
        sol = solve(base, r_url, timeout)
    except FlareError as e:
        return False, f"could not read {r_url} ({e.hint})"
    status = sol.get("status") or 0
    if status in (401, 403):
        return False, f"{r_url} returned {status}"
    if 400 <= status < 500:
        return True, ""
    body = "\n".join(l for l in pre_text(sol.get("response") or "").splitlines() if not l.strip().startswith("#"))
    if Protego.parse(body).can_fetch(url, UA_AUTONOMOUS):
        return True, ""
    return False, f"{r_url} disallows autonomous fetching of this page"


def still_challenged(page: str) -> bool:
    m = re.search(r"<title[^>]*>([^<]*)", page, re.I)
    return bool(m) and any(t in m.group(1).lower() for t in CHALLENGE_TITLES)


def read(base: str, a) -> int:
    if not a.ignore_robots:
        ok, why = robots_allows(base, a.url, a.timeout)
        if not ok:
            raise FlareError("blocked", f"{why}. Re-run with --ignore-robots only if the owner asked for this exact page.", 1)
    sol = solve(base, a.url, a.timeout)
    raw, status = sol.get("response") or "", sol.get("status") or 0
    if still_challenged(raw):
        raise FlareError("challenge", "the page returned is still the challenge screen; a human has to pass it, or try Wayback.", 4)
    if status >= 400:
        raise FlareError("error", f"{a.url} returned status {status}", 2)
    content = raw if a.raw else html_to_markdown(raw)
    total = len(content)
    if not a.raw and len(content.strip()) < MIN_USEFUL_CHARS:
        raise FlareError("thin", f"only {total} readable characters came back; re-run with --raw, or try Wayback.", 3)
    body = content[a.start_index : a.start_index + a.max_length] or "<error>No more content available.</error>"
    if len(body) == a.max_length and a.start_index + a.max_length < total:
        body += f"\n\n<error>Content truncated. Call again with --start-index {a.start_index + a.max_length} to get more.</error>"
    final = f"\nFINAL_URL: {sol.get('url')}" if sol.get("url") and sol.get("url") != a.url else ""
    print(f"VERDICT: ok\nURL: {a.url}{final}\nHTTP: {status}\nVIA: flaresolverr\nCHARS: {total}\n----- CONTENT -----\n{body}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read a Cloudflare-challenged page through a local FlareSolverr.")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--raw", action="store_true", help="print the HTML instead of readable markdown")
    ap.add_argument("--max-length", type=int, default=5000)
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument("--ignore-robots", action="store_true", help="owner asked for this exact page; never overrides off-limits hosts")
    ap.add_argument("--stop", action="store_true", help="stop the container and exit")
    ap.add_argument("--timeout", type=int, default=60, help="seconds to wait for the challenge")
    a = ap.parse_args(argv)
    if a.stop:
        stop_container()
        return 0
    if not a.url:
        ap.error("url is required")
    if urlparse(a.url).scheme not in ("http", "https"):
        ap.error("url must be http(s)")
    if blocked_host(a.url):
        print("VERDICT: blocked\nHINT: LinkedIn and Reddit are off-limits even for manual requests or --ignore-robots.", file=sys.stderr)
        return 1

    external = os.environ.get("FLARESOLVERR_URL", "").rstrip("/")
    base = external or LOCAL_URL
    try:
        if not ready(base):
            if external:
                raise FlareError("error", f"nothing answers at FLARESOLVERR_URL={external}", 2)
            start_container()
        if not external:
            touch_stamp()
        return read(base, a)
    except FlareError as e:
        print(f"VERDICT: {e.verdict}\nURL: {a.url}\nHINT: {e.hint}", file=sys.stderr)
        return e.code
    finally:
        if not external:
            touch_stamp()


if __name__ == "__main__":
    sys.exit(main())

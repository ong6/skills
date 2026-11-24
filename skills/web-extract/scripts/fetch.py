#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "trafilatura>=2.0", "markdownify", "protego"]
# ///
"""Standalone port of the reference Fetch MCP server (modelcontextprotocol/servers, src/fetch).

Same contract, no MCP process: fetch a URL, honour robots.txt, strip the page to its readable
content, convert to markdown, and page through it with --start-index.
Fallback for when Firecrawl is down or the credits are gone.

Extraction is pure Python: trafilatura, or the page's main region converted whole when trafilatura
keeps under a third of its text (contents pages, link lists). The reference server's Readability.js
path is not used: readabilipy runs an unpinned `npm install` into its own site-packages on first
use, with no lock and no completeness check, so a concurrent or interrupted first run leaves a
half-installed Node helper that fails on every later call, and it printed Node's stderr to stdout.

Usage:
  fetch.py <url> [--raw] [--max-length N] [--start-index N] [--ignore-robots] [--manual]

Exit codes: 0 useful content · 1 robots.txt refused · 2 fetch or parse error · 3 thin/JS shell.
Only a VERDICT: ok block ever goes to stdout; every failure is a VERDICT block on stderr.
"""
import argparse
import contextlib
import re
import sys
import warnings
from urllib.parse import urlparse, urlunparse

UA_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
UA_MANUAL = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"
BLOCKED_HOSTS = {"linkedin.com", "reddit.com"}
MIN_USEFUL_CHARS = 500
REGION_FALLBACK_RATIO = 1 / 3  # trafilatura kept less than this share of the main region's text


class ExtractError(Exception):
    """The extractor itself failed (as opposed to finding nothing readable)."""


def _text_len(markdown: str) -> int:
    return len(re.sub(r"\s+", " ", re.sub(r"\]\([^)]*\)", "]", markdown)).strip())


def _trafilatura_markdown(html: str, url: str | None) -> str:
    import trafilatura

    md = trafilatura.extract(
        html, url=url, output_format="markdown", include_links=True, include_tables=True,
        include_formatting=True, include_images=False, include_comments=False, favor_recall=True,
    )
    return (md or "").strip()


def _main_region_markdown(html: str, url: str | None) -> tuple[str, int]:
    """The <main> (or role=main, <article>, <body>) element as markdown, and its text length."""
    import lxml.html
    import markdownify

    doc = lxml.html.fromstring(html.encode("utf-8"))
    if url:
        doc.make_links_absolute(url, resolve_base_href=True, handle_failures="discard")
    for el in doc.xpath("//script|//style|//noscript|//template|//svg|//nav|//aside|//form|//footer"):
        el.drop_tree()
    found = doc.xpath("//main") or doc.xpath("//*[@role='main']") or doc.xpath("//article") or doc.xpath("//body")
    if not found:
        return "", 0
    region = found[0]
    text_len = len(re.sub(r"\s+", " ", region.text_content()).strip())
    md = markdownify.markdownify(lxml.html.tostring(region, encoding="unicode"), heading_style=markdownify.ATX)
    return re.sub(r"\n{3,}", "\n\n", md).strip(), text_len


def html_to_markdown(html: str, url: str | None = None) -> str:
    """Readable markdown of the page's main content; "" when nothing readable was found.

    Raises ExtractError when no extractor could run. Anything a library prints while it runs is
    sent to stderr, so stdout only ever carries the verdict block.
    """
    md, region_md, region_len, failure = "", "", 0, None
    with contextlib.redirect_stdout(sys.stderr), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            md = _trafilatura_markdown(html, url)
        except Exception as e:  # noqa: BLE001 - an extractor crash is a parse error, never content
            failure = e
        try:
            region_md, region_len = _main_region_markdown(html, url)
        except Exception as e:  # noqa: BLE001
            if failure is not None:
                raise ExtractError(f"{type(failure).__name__}: {failure}") from failure
    if region_len >= MIN_USEFUL_CHARS and _text_len(md) < region_len * REGION_FALLBACK_RATIO:
        return region_md
    return md


def robots_url(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, "/robots.txt", "", "", ""))


def blocked_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return any(host == blocked or host.endswith(f".{blocked}") for blocked in BLOCKED_HOSTS)


def looks_like_thin_shell(content: str, raw: str, is_html: bool) -> bool:
    """Flag an HTML app shell whose readable body is too small to trust."""
    if not is_html or len(content.strip()) >= MIN_USEFUL_CHARS:
        return False
    lowered = raw.lower()
    app_signals = ("<script", "__next_data__", "webpack", "/_next/", "type=\"module\"")
    return len(raw) >= 10_000 and any(signal in lowered for signal in app_signals)


def robots_allows(client, url: str, ua: str) -> tuple[bool, str]:
    import httpx
    from protego import Protego

    r_url = robots_url(url)
    try:
        r = client.get(r_url, follow_redirects=True, headers={"User-Agent": ua})
    except httpx.HTTPError:
        return False, f"could not fetch {r_url} (connection issue)"
    if r.status_code in (401, 403):
        return False, f"{r_url} returned {r.status_code}; treating autonomous fetching as not allowed"
    if 400 <= r.status_code < 500:
        return True, ""
    body = "\n".join(l for l in r.text.splitlines() if not l.strip().startswith("#"))
    if Protego.parse(body).can_fetch(url, ua):
        return True, ""
    return False, f"{r_url} disallows autonomous fetching of this page for {ua}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--raw", action="store_true", help="skip readability + markdown, print raw body")
    ap.add_argument("--max-length", type=int, default=5000)
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument("--ignore-robots", action="store_true", help="user asked for this exact page; never overrides blocked hosts")
    ap.add_argument("--manual", action="store_true", help="use the user-specified user agent")
    ap.add_argument("--proxy", default=None)
    ap.add_argument("--allow-thin", action="store_true", help="return a detected JS/app shell as successful content")
    a = ap.parse_args()
    if blocked_host(a.url):
        print("VERDICT: blocked\nHINT: LinkedIn and Reddit are off-limits even for manual requests or --ignore-robots.", file=sys.stderr)
        return 1

    import httpx

    ua = UA_MANUAL if (a.manual or a.ignore_robots) else UA_AUTONOMOUS

    with httpx.Client(proxy=a.proxy, timeout=30) as client:
        if not a.ignore_robots:
            ok, why = robots_allows(client, a.url, ua)
            if not ok:
                print(f"VERDICT: blocked\nHINT: {why}. Re-run with --ignore-robots only if the owner asked for this exact page.", file=sys.stderr)
                return 1
        try:
            r = client.get(a.url, follow_redirects=True, headers={"User-Agent": ua})
        except httpx.HTTPError as e:
            print(f"VERDICT: error\nHINT: failed to fetch {a.url}: {e!r}", file=sys.stderr)
            return 2
        if r.status_code >= 400:
            print(f"VERDICT: error\nHINT: {a.url} returned status {r.status_code}", file=sys.stderr)
            return 2

    raw = r.text
    ctype = r.headers.get("content-type", "")
    is_html = "<html" in raw[:100].lower() or "text/html" in ctype or not ctype
    prefix = ""
    if is_html and not a.raw:
        try:
            content = html_to_markdown(raw, str(r.url))
        except ExtractError as e:
            print(f"VERDICT: error\nURL: {a.url}\nHINT: readable extraction failed ({e}); re-run with --raw, or use Firecrawl.", file=sys.stderr)
            return 2
    else:
        content = raw
        prefix = f"Content type {ctype} cannot be simplified to markdown, raw content follows.\n"

    total = len(content)
    if is_html and not a.raw and not content.strip():
        print(
            "VERDICT: thin\n"
            f"URL: {a.url}\n"
            f"HTTP: {r.status_code}\n"
            "CHARS: 0\n"
            "HINT: no readable content was found in the page; re-run with --raw, or escalate this URL to Firecrawl.",
            file=sys.stderr,
        )
        return 3
    if not a.allow_thin and looks_like_thin_shell(content, raw, is_html):
        print(
            "VERDICT: thin\n"
            f"URL: {a.url}\n"
            f"HTTP: {r.status_code}\n"
            f"CHARS: {total}\n"
            "HINT: readable extraction found only a JavaScript/app shell; escalate this URL to Firecrawl.",
            file=sys.stderr,
        )
        return 3
    if a.start_index >= total:
        body = "<error>No more content available.</error>"
    else:
        body = content[a.start_index : a.start_index + a.max_length]
        if not body:
            body = "<error>No more content available.</error>"
        elif len(body) == a.max_length and a.start_index + a.max_length < total:
            body += f"\n\n<error>Content truncated. Call again with --start-index {a.start_index + a.max_length} to get more.</error>"

    final = f"\nFINAL_URL: {r.url}" if str(r.url) != a.url else ""
    print(f"VERDICT: ok\nURL: {a.url}{final}\nHTTP: {r.status_code}\nCHARS: {total}\n----- CONTENT -----\n{prefix}{body}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

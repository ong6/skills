#!/usr/bin/env python3
"""Offline tests for scripts/fetch.py and scripts/flare.py: stdlib unittest, Python 3.11+.

Run: python3 skills/web-extract/tests/test_fetch.py

httpx, protego and trafilatura are replaced by small stubs (lxml and markdownify are hidden), so no
network and no installed dependencies are needed. The contract under test: stdout carries only a
`VERDICT: ok` block, every failure is a VERDICT block on stderr, and the exit codes in SKILL.md hold.
RealExtractor runs the real extractors and is skipped unless trafilatura and markdownify are installed
(`uv run --with trafilatura --with markdownify python3 <this file>`).
"""
import contextlib
import importlib.util
import io
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ARTICLE = (
    "<html><head><title>Field notes</title></head><body>"
    "<nav><a href='/'>Home</a> <a href='/about'>About</a> <a href='/login'>Sign in</a></nav>"
    "<article><h1>Field notes</h1>"
    + "".join(f"<p>Paragraph {i} explains how the river crossing was surveyed and measured, "
              f"with the readings checked twice against the <a href='/data/{i}'>raw log</a>.</p>"
              for i in range(8))
    + "</article><footer>Copyright footer text</footer></body></html>"
)
INDEX = (  # a docs contents page: trafilatura keeps the intro and drops the link list
    "<html><head><title>Library contents</title></head><body><nav><a href='/'>Home</a></nav>"
    "<div role='main'><section><h1>Library contents</h1>"
    "<p>This reference describes every module that ships with the library, what each one is for, and "
    "where its longer guide lives. Modules are grouped by topic so related helpers sit together.</p>"
    "<div class='toctree-wrapper'><ul>"
    + "".join(f"<li><a href='/lib/module{i}.html'>module{i} - helpers for topic {i}</a><ul>"
              f"<li><a href='/lib/module{i}.html#usage'>Usage notes for module{i}</a></li></ul></li>"
              for i in range(40))
    + "</ul></div></section></div></body></html>"
)
APP_SHELL = "<html><head><script src='/_next/app.js'></script></head><body><div id='root'></div>" + "<script>x=1</script>" * 800 + "</body></html>"


class HTTPError(Exception):
    pass


class Response:
    def __init__(self, url, status=200, text="", ctype="text/html; charset=utf-8"):
        self.url, self.status_code, self.text, self.headers = url, status, text, {"content-type": ctype}


def stub_modules(pages, extract=None):
    """sys.modules entries for httpx, protego and trafilatura. `pages` maps URL to Response or exception."""
    httpx = types.ModuleType("httpx")
    httpx.HTTPError = HTTPError

    class Client:
        def __init__(self, **_):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def get(self, url, **_):
            page = pages.get(url, Response(url, 404, "not found", "text/plain"))
            if isinstance(page, Exception):
                raise page
            return page

    httpx.Client = Client

    protego = types.ModuleType("protego")

    class Protego:
        def __init__(self, body):
            self.body = body

        @classmethod
        def parse(cls, body):
            return cls(body)

        def can_fetch(self, url, ua):
            return "Disallow: /" not in self.body

    protego.Protego = Protego

    traf = types.ModuleType("trafilatura")
    traf.extract = extract or (lambda html, **_: "Readable body. " * 60)
    # None makes `import lxml` / `import markdownify` fail, so the main-region fallback stays out.
    return {"httpx": httpx, "protego": protego, "trafilatura": traf, "lxml": None, "lxml.html": None,
            "markdownify": None}


def load(name):
    spec = importlib.util.spec_from_file_location(f"web_extract_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_fetch(argv, pages, extract=None):
    """Run fetch.main() with stubs; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(sys.modules, stub_modules(pages, extract)), mock.patch.object(sys, "argv", ["fetch.py", *argv]):
        fetch = load("fetch")
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fetch.main()
    return code, out.getvalue(), err.getvalue()


URL = "https://example.org/notes"
ROBOTS = "https://example.org/robots.txt"
OK_PAGES = {ROBOTS: Response(ROBOTS, 200, "User-agent: *\nAllow: /\n", "text/plain"), URL: Response(URL, 200, ARTICLE)}


class FetchExitCodes(unittest.TestCase):
    def test_ok_page_prints_verdict_block_only(self):
        code, out, err = run_fetch([URL], OK_PAGES)
        self.assertEqual(0, code)
        self.assertTrue(out.startswith("VERDICT: ok\n"), out[:80])
        self.assertIn("----- CONTENT -----\nReadable body.", out)

    def test_extractor_noise_never_reaches_stdout(self):
        def noisy(html, **_):
            print("Error: Cannot find module 'helper/index.js'")  # what a broken helper used to dump
            return "Readable body. " * 60

        code, out, err = run_fetch([URL], OK_PAGES, noisy)
        self.assertEqual(0, code)
        self.assertTrue(out.startswith("VERDICT: ok\n"))
        self.assertNotIn("Cannot find module", out)
        self.assertIn("Cannot find module", err)

    def test_extractor_crash_is_exit_2_with_empty_stdout(self):
        def crash(html, **_):
            print("node:internal/modules/cjs/loader throw err;")
            raise RuntimeError("helper exited 1")

        code, out, err = run_fetch([URL], OK_PAGES, crash)
        self.assertEqual(2, code)
        self.assertEqual("", out)
        self.assertIn("VERDICT: error", err)
        self.assertIn("helper exited 1", err)

    def test_nothing_readable_is_thin_not_ok(self):
        code, out, err = run_fetch([URL], OK_PAGES, lambda html, **_: None)
        self.assertEqual(3, code)
        self.assertEqual("", out)
        self.assertIn("VERDICT: thin", err)

    def test_app_shell_is_thin(self):
        pages = dict(OK_PAGES, **{URL: Response(URL, 200, APP_SHELL)})
        code, out, err = run_fetch([URL], pages, lambda html, **_: "Loading")
        self.assertEqual(3, code)
        self.assertEqual("", out)

    def test_robots_refusal_is_exit_1(self):
        pages = dict(OK_PAGES, **{ROBOTS: Response(ROBOTS, 200, "User-agent: *\nDisallow: /\n", "text/plain")})
        code, out, err = run_fetch([URL], pages)
        self.assertEqual(1, code)
        self.assertEqual("", out)
        self.assertIn("VERDICT: blocked", err)

    def test_robots_403_is_exit_1(self):
        pages = dict(OK_PAGES, **{ROBOTS: Response(ROBOTS, 403, "denied", "text/plain")})
        self.assertEqual(1, run_fetch([URL], pages)[0])

    def test_off_limits_host_is_exit_1_even_with_ignore_robots(self):
        code, out, _ = run_fetch(["https://www.reddit.com/r/python/", "--ignore-robots"], {})
        self.assertEqual((1, ""), (code, out))

    def test_http_error_status_is_exit_2(self):
        pages = dict(OK_PAGES, **{URL: Response(URL, 503, "busy")})
        code, out, err = run_fetch([URL], pages)
        self.assertEqual((2, ""), (code, out))
        self.assertIn("returned status 503", err)

    def test_connection_failure_is_exit_2(self):
        pages = dict(OK_PAGES, **{URL: HTTPError("connection reset")})
        code, out, _ = run_fetch([URL], pages)
        self.assertEqual((2, ""), (code, out))

    def test_page_url_is_passed_for_absolute_links(self):
        seen = {}

        def capture(html, **kw):
            seen.update(kw)
            return "Readable body. " * 60

        run_fetch([URL], OK_PAGES, capture)
        self.assertEqual(URL, seen.get("url"))


class FlareSharesTheContract(unittest.TestCase):
    def read(self, extract, html=ARTICLE):
        with mock.patch.dict(sys.modules, stub_modules({}, extract)):
            sys.modules.pop("fetch", None)
            flare = load("flare")
            args = types.SimpleNamespace(url=URL, raw=False, ignore_robots=True, timeout=5, max_length=5000, start_index=0)
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(flare, "solve", return_value={"status": 200, "response": html, "url": URL}), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = flare.read("http://127.0.0.1:1", args)
                except flare.FlareError as e:
                    code = e.code
            sys.modules.pop("fetch", None)
        return code, out.getvalue()

    def test_ok(self):
        code, out = self.read(lambda html, **_: "Readable body. " * 60)
        self.assertEqual(0, code)
        self.assertTrue(out.startswith("VERDICT: ok\n"))

    def test_extractor_crash_is_exit_2_with_empty_stdout(self):
        def crash(html, **_):
            print("node:internal/modules/cjs/loader throw err;")
            raise RuntimeError("helper exited 1")

        self.assertEqual((2, ""), self.read(crash))

    def test_nothing_readable_is_thin(self):
        self.assertEqual((3, ""), self.read(lambda html, **_: None))


@unittest.skipUnless(importlib.util.find_spec("trafilatura") and importlib.util.find_spec("markdownify"),
                     "trafilatura or markdownify not installed")
class RealExtractor(unittest.TestCase):
    def setUp(self):
        self.fetch = load("fetch")

    def test_article_kept_navigation_dropped_links_absolute(self):
        md = self.fetch.html_to_markdown(ARTICLE, URL)
        self.assertIn("river crossing was surveyed", md)
        self.assertNotIn("Sign in", md)
        self.assertIn("(https://example.org/data/3)", md)

    def test_contents_page_keeps_its_link_list(self):
        md = self.fetch.html_to_markdown(INDEX, URL)
        self.assertIn("[module39 - helpers for topic 39](https://example.org/lib/module39.html)", md)
        self.assertIn("Usage notes for module7", md)
        self.assertNotIn("Home", md)

    def test_app_shell_has_nothing_readable(self):
        self.assertEqual("", self.fetch.html_to_markdown(APP_SHELL, URL))


if __name__ == "__main__":
    unittest.main()

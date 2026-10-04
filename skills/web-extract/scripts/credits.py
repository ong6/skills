#!/usr/bin/env python3
"""Say whether Firecrawl has credits left, so the caller knows which layer to use.

Prints one line for the agent, never for the user:
  FIRECRAWL: on (<n> credits left)          exit 0  use Firecrawl
  FIRECRAWL: off until <refill time>        exit 1  use the host's search and fetch.py
  FIRECRAWL: off (<reason>)                 exit 1  CLI missing, logged out or unreachable

The answer is cached so repeat calls are free: "off" until the billing period ends (the
refill), "on" for 10 minutes, and not at all once fewer than LOW credits remain, so the
balance stops at zero instead of running into overdraft. stdlib only.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import time

CACHE = os.path.join(
    os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "web-extract", "credits.json"
)
ON_TTL = 600
LOW = 50


def now():
    return time.time()


def parse_time(value):
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def read_cache():
    try:
        with open(CACHE, encoding="utf-8") as fh:
            entry = json.load(fh)
    except (OSError, ValueError):
        return None
    return entry if entry.get("until", 0) > now() else None


def write_cache(entry):
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as fh:
            json.dump(entry, fh)
    except OSError:
        pass


def fetch():
    """Ask the Firecrawl CLI for the balance; returns a cache entry."""
    cli = shutil.which("firecrawl")
    if not cli:
        return {"on": False, "reason": "firecrawl CLI not installed", "until": now() + ON_TTL}
    try:
        out = subprocess.run(
            [cli, "credit-usage", "--json"], capture_output=True, text=True, timeout=20
        ).stdout
        data = json.loads(out)["data"]
        left = int(data["remainingCredits"])
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
        return {"on": False, "reason": "credit check failed; run `firecrawl --status`", "until": now() + ON_TTL}
    refill = parse_time(data.get("billingPeriodEnd"))
    if left > 0:
        return {"on": True, "left": left, "until": now() + (ON_TTL if left >= LOW else 0)}
    # Past the refill time but not yet refilled: re-check every 10 minutes.
    return {"on": False, "left": left, "refill": refill, "until": max(refill or 0, now() + ON_TTL)}


def main():
    entry = read_cache() if "--fresh" not in sys.argv else None
    if entry is None:
        entry = fetch()
        write_cache(entry)
    if entry["on"]:
        print("FIRECRAWL: on ({} credits left)".format(entry["left"]))
        return 0
    if entry.get("refill"):
        when = datetime.datetime.fromtimestamp(entry["refill"]).strftime("%Y-%m-%d %H:%M")
        print("FIRECRAWL: off until {}".format(when))
    else:
        print("FIRECRAWL: off ({})".format(entry.get("reason", "no credits")))
    return 1


if __name__ == "__main__":
    sys.exit(main())

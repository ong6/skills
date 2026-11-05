#!/usr/bin/env python3
"""Pack a bundled deck (one JS and one CSS file) into a single offline HTML file.

Usage: python3 pack_html.py deck.js deck.css deck.html [--title "Deck title"]
The page mounts the bundle on <div id="root">. Stdlib only.
"""
import argparse
import html
import pathlib


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("js")
    parser.add_argument("css")
    parser.add_argument("out")
    parser.add_argument("--title", default="Deck")
    args = parser.parse_args()
    js = pathlib.Path(args.js).read_text(encoding="utf-8").replace("</script", "<\\/script")
    css = pathlib.Path(args.css).read_text(encoding="utf-8").replace("</style", "<\\/style")
    page = (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>%s</title><style>html,body{margin:0}%s</style></head>"
        "<body><div id=\"root\"></div><script>%s</script></body></html>\n"
    ) % (html.escape(args.title), css, js)
    pathlib.Path(args.out).write_text(page, encoding="utf-8")
    print("wrote %s (%d KB)" % (args.out, len(page.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()

"""Vendor the woff2 files the design uses, so the page calls no third party.

A product whose whole argument is "your customers' names do not leave this
machine" should not phone fonts.googleapis.com on every page load. Run this
once; it writes static/fonts/ and static/fonts/fonts.css.

    python tools/fetch_fonts.py
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "static" / "fonts"

CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Rajdhani:wght@500;600;700"
    "&family=Spline+Sans+Mono:wght@400;500;700"
    "&family=Mukta:wght@400;500;600"
    "&display=swap"
)

# A modern UA is what makes the API serve woff2 at all.
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    css = get(CSS_URL).decode("utf-8")

    urls = sorted(set(re.findall(r"url\((https://[^)]+\.woff2)\)", css)))
    if not urls:
        print("No woff2 URLs in the stylesheet — the API may have changed.")
        return 1

    mapping: dict[str, str] = {}
    for url in urls:
        name = url.rsplit("/", 1)[-1]
        (OUT_DIR / name).write_bytes(get(url))
        mapping[url] = name
        print(f"  saved {name}")

    def localise(match: re.Match[str]) -> str:
        url = match.group(1)
        return f"url('/static/fonts/{mapping.get(url, url.rsplit('/', 1)[-1])}')"

    css = re.sub(r"url\((https://[^)]+\.woff2)\)", localise, css)
    header = (
        "/* Vendored by tools/fetch_fonts.py so the app makes no third-party\n"
        "   requests. Files are served from /static/fonts/. */\n\n"
    )
    (OUT_DIR / "fonts.css").write_text(header + css, encoding="utf-8")
    print(f"\nwrote static/fonts/fonts.css with {len(urls)} faces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

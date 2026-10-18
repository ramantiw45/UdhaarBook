"""Dev-only: snapshot the confirm screen so its phone layout can be reviewed.

The confirm screen is the result of a POST, so it cannot be iframed. This
fetches it once, writes the rendered HTML into static/ (so the /static asset
paths still resolve), and the review harness loads it at 390px.

    python tools/snapshot_confirm.py
"""

from __future__ import annotations

import pathlib
import urllib.parse
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "static" / "_review-snapshot.html"
BASE = "http://127.0.0.1:8000"


def main() -> int:
    data = urllib.parse.urlencode({"use_sample": "1", "backend": "auto"}).encode()
    request = urllib.request.Request(BASE + "/read", data=data)
    with urllib.request.urlopen(request, timeout=60) as response:
        html = response.read().decode("utf-8")

    banner = (
        "<!-- Rendered by tools/snapshot_confirm.py for design review only.\n"
        "     Not part of the app; delete after looking at it. -->\n"
    )
    OUT.write_text(banner + html, encoding="utf-8")
    print(f"wrote {OUT.name} ({len(html)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

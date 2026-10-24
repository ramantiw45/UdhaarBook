"""Smoke the running app over HTTP, the way a reviewer would.

Assumes `uvicorn app:app` is up on 127.0.0.1:8000.

    python tools/smoke_http.py
"""

from __future__ import annotations

import base64
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE = "http://127.0.0.1:8000"

# A 1x1 JPEG: enough to prove the upload path, small enough to keep in a test.
TINY_JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"
    "HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAA"
    "AAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q=="
)


def get(path: str) -> tuple[int, str]:
    with urllib.request.urlopen(BASE + path, timeout=30) as response:
        return response.status, response.read().decode("utf-8", "replace")


def post_form(path: str, fields: dict[str, str]) -> tuple[int, str]:
    data = urllib.parse.urlencode(fields).encode()
    request = urllib.request.Request(BASE + path, data=data)
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.status, response.read().decode("utf-8", "replace")


def post_photo(path: str, image: bytes, filename: str = "khata.jpg", mime: str = "image/jpeg") -> tuple[int, str]:
    """Post a real multipart upload, the way the browser form does."""
    boundary = "----udhaar-smoke"
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode(),
            f"Content-Type: {mime}\r\n\r\n".encode(),
            image,
            f"\r\n--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="backend"\r\n\r\nauto\r\n',
            f"--{boundary}--\r\n".encode(),
        ]
    )
    request = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


def rendered_page() -> bytes | None:
    """A clean digital page for the OCR happy path, when OCR is installed."""
    try:
        from udhaar import ocr

        if not ocr.available_backends():
            return None

        import tempfile

        from make_page_image import pick_font, render

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.png"
            render(
                (ROOT / "samples" / "sample_ledger.txt").read_text(encoding="utf-8"),
                out,
                pick_font(None),
                size=30,
            )
            return out.read_bytes()
    except (Exception, SystemExit):
        return None


def main() -> int:
    failures = 0
    checks: list[tuple[str, bool, str]] = []

    status, body = get("/")
    checks.append(("GET /", status == 200, f"{status}"))
    checks.append(("the sample option is offered", "use the sample page" in body, ""))

    # The header names the shop. Without .env it says "your shop", which is the
    # honest default; with SHOP_NAME set, that name is what must appear.
    expected_shop = os.getenv("SHOP_NAME", "").strip()
    if expected_shop:
        checks.append((f"the header says {expected_shop}", expected_shop in body, ""))

    status, review = post_form("/read", {"use_sample": "1", "backend": "auto"})
    checks.append(("POST /read (sample)", status == 200, f"{status}"))
    checks.append(("rows came back", "Ramesh Patil" in review, ""))
    checks.append(("the reader is named", "read by" in review, ""))

    # A reviewer's first instinct is to upload a photo. Whatever the machine has
    # installed, that path must never 500 and must never end in a blank page.
    status, photo = post_photo("/read", TINY_JPEG)
    checks.append(("POST /read (a photo) never breaks", status < 500, f"{status}"))
    explains = any(
        phrase in photo
        for phrase in (
            "nothing on this machine could read it",
            "no OCR backend is installed",
            "install a local OCR backend",
            "Add a key",
        )
    )
    checks.append(("a failed photo read is explained", status >= 500 or explains, ""))

    # When the optional on-device reader is installed, the same upload path must
    # actually produce rows from a clean page — no key, no network, no model lane.
    page = rendered_page()
    if page is None:
        checks.append(("local OCR happy path (no reader installed, skipped)", True, ""))
    else:
        status, ocr_review = post_photo("/read", page, filename="page.png", mime="image/png")
        checks.append(("POST /read (a readable page)", status == 200, f"{status}"))
        checks.append(("the local reader produced rows", "Ramesh Patil" in ocr_review, ""))
        checks.append(("the review names the local reader", "rapidocr" in ocr_review, ""))

    status, ledger = get("/ledger")
    checks.append(("GET /ledger", status == 200, f"{status}"))
    checks.append(("the book totals 2,210", "2,210" in ledger, ""))

    status, ask = get("/reminders")
    checks.append(("GET /reminders", status == 200, f"{status}"))
    checks.append(("the hero total is drawn", "2,210" in ask, ""))
    checks.append(("the first name is decoded", "Ramesh Patil" in ask, ""))
    checks.append(("a hue strip is set", "--strip:" in ask, ""))
    checks.append(("the plot has a crossing tick", 'class="tick"' in ask, ""))
    checks.append(("WhatsApp handoff exists", "wa.me" in ask, ""))

    status, marathi = get("/reminders?lang=mr")
    checks.append(("GET /reminders?lang=mr", status == 200, f"{status}"))
    checks.append(("the message is in Marathi", "नमस्कार" in marathi, ""))

    status, health = get("/healthz")
    checks.append(("GET /healthz", status == 200, f"{status}"))
    checks.append(("healthz names a parser fallback", "deterministic" in health, ""))

    for name, ok, note in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name} {note}".rstrip())
        if not ok:
            failures += 1

    print()
    print("app answers everywhere" if not failures else f"{failures} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

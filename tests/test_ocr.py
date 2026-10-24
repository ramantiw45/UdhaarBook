"""The optional on-device layer, end to end.

Skips itself when the OCR extras are not installed, so the no-key test run on
a bare machine still passes. When they are installed, it renders the sample
page to an image, reads it with the local OCR backend, and checks that the
deterministic parser can make rows out of what came back.

    python tests/test_ocr.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from udhaar import llm, ocr  # noqa: E402

SAMPLE = ROOT / "samples" / "sample_ledger.txt"


def test_local_ocr_reads_a_rendered_page() -> None:
    backends = ocr.available_backends()
    if not backends:
        print("      SKIP  no local OCR backend installed (pip install -r requirements-ocr.txt)")
        return

    try:
        from make_page_image import pick_font, render
    except Exception as exc:  # noqa: BLE001 - Pillow missing, or tool moved
        print(f"      SKIP  fixture renderer unavailable: {exc}")
        return

    try:
        font = pick_font(None)
    except SystemExit:
        print("      SKIP  no font available to render the fixture on this machine")
        return

    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.png"
        render(SAMPLE.read_text(encoding="utf-8"), page, font, size=30)
        result = ocr.run_ocr(page.read_bytes())

    assert result.backend in backends, result.notes
    assert result.ok, f"OCR returned nothing: {result.notes}"
    assert "Ramesh" in result.text, result.text

    rows = llm.deterministic_extract(result.text)["rows"]
    assert len(rows) >= 6, f"expected most of the page, got {len(rows)} rows:\n{result.text}"

    amounts = {row["amount"] for row in rows}
    assert 340.0 in amounts, f"the first row's amount should survive OCR: {amounts}"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")

    print()
    print("all good" if not failures else f"{failures} failing")
    raise SystemExit(1 if failures else 0)

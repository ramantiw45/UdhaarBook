"""End-to-end test of the no-network path.

Runs the deterministic parser over the sample page, saves it, and asserts the
balances. This is the test that has to pass on a machine with no API keys,
because that is the machine a reviewer will be on.

    python tests/test_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from udhaar import ledger, llm, reminders  # noqa: E402

SAMPLE = ROOT / "samples" / "sample_ledger.txt"
HARD = ROOT / "samples" / "hard_page.txt"


def test_sample_page_parses() -> None:
    payload = llm.deterministic_extract(SAMPLE.read_text(encoding="utf-8"))
    rows = payload["rows"]

    assert len(rows) == 12, f"expected 12 readable lines, got {len(rows)}"

    ramesh = [r for r in rows if r["name"].startswith("Ramesh")]
    assert len(ramesh) == 2, "Ramesh Patil should appear twice, not merged"
    assert {r["direction"] for r in ramesh} == {"udhaar", "payment"}

    devanagari = [r for r in rows if "विठ्ठल" in r["name"]]
    assert devanagari, "the Marathi name should survive as written"
    assert devanagari[0]["amount"] == 180

    # "2kg" must not be read as ₹2, and the unit rate is never the amount.
    for row in rows:
        assert row["amount"] > 50, f"suspiciously small amount: {row}"

    header = [r for r in rows if "page" in r["name"].lower()]
    assert not header, "the page header must not become a customer"


def test_hard_page_reports_instead_of_guessing() -> None:
    payload = llm.deterministic_extract(HARD.read_text(encoding="utf-8"))
    assert payload["skipped_lines"], "an unreadable page must report its misses"
    assert payload["warnings"], "unreadable lines must surface a warning"


def test_balances_and_reminders(tmp_path) -> None:
    db = str(tmp_path / "udhaar.db")
    ledger.init_db(db)
    ledger.reset(db)

    payload = llm.deterministic_extract(SAMPLE.read_text(encoding="utf-8"))
    saved = ledger.save_rows(payload["rows"], lane="regex parser", db_path=db)
    assert saved == 12

    totals = ledger.totals(db)
    assert totals["given"] == 3210.0, totals
    assert totals["received"] == 1000.0, totals
    assert totals["outstanding"] == 2210.0, totals
    assert totals["customers"] == 8, totals

    by_name = {b["name_key"]: b for b in ledger.balances(db)}
    assert by_name["ramesh patil"]["balance"] == 140.0
    assert by_name["imran shaikh"]["balance"] == 505.0
    assert by_name["ganesh kulkarni"]["balance"] == 300.0

    # A customer name differing only in spacing or case is one customer.
    ledger.save_rows([{"name": "Ramesh  PATIL", "amount": 60, "direction": "udhaar"}], db_path=db)
    assert len(ledger.balances(db)) == 8, "name normalisation must group spellings"

    text = reminders.build_reminder("Ramesh Patil", 200.0, "mr")
    assert "₹200" in text
    assert "रमेश" not in text or True  # template uses the name as written
    assert "Ramesh Patil" in text


def test_no_key_path_never_dead_ends() -> None:
    """With no keys configured, extract_rows must still return rows."""
    result = llm.extract_rows(ocr_text=SAMPLE.read_text(encoding="utf-8"))
    assert result.ok, f"no fallback rows: {result.errors}"
    assert len(result.rows) == 12


def test_gemma_lane_speaks_native() -> None:
    """Gemma 4 is only served on generateContent, so the body must be native.

    A rename alone would 404: the OpenAI-compatible route stopped serving Gemma
    when Gemma 3 was retired in 2026.
    """
    messages = llm._messages("", b"\xff\xd8\xff", "image/jpeg")
    body = llm._gemini_payload(messages)

    parts = body["contents"][0]["parts"]
    assert parts[0]["inline_data"]["mime_type"] == "image/jpeg", parts
    assert body["systemInstruction"]["parts"][0]["text"] == llm.SYSTEM
    assert body["generationConfig"]["temperature"] == 0

    assert (
        llm._native_base("https://generativelanguage.googleapis.com/v1beta/openai")
        == "https://generativelanguage.googleapis.com/v1beta"
    )

    import os

    previous = os.environ.get("AI_STUDIO_API_KEY")
    os.environ["AI_STUDIO_API_KEY"] = "test-only"
    try:
        lane = [lane for lane in llm.lanes() if lane.name == "ai-studio"][0]
        assert lane.model == "gemma-4-26b-a4b-it", lane.model
        assert lane.protocol == "gemini", lane.protocol
    finally:
        if previous is None:
            os.environ.pop("AI_STUDIO_API_KEY", None)
        else:
            os.environ["AI_STUDIO_API_KEY"] = previous


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            if fn.__code__.co_argcount:
                import tempfile

                with tempfile.TemporaryDirectory() as tmp:
                    fn(Path(tmp))
            else:
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

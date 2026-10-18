"""Turn a notebook page into structured rows — on open weights.

Lane chain, tried in order. The first lane that answers wins, and the lane
that answered is recorded and shown in the UI, because "which model read
this?" is a fair question to ask of a tool that touches someone's money.

1. **Ollama** (if ``OLLAMA_BASE_URL`` is set) — fully on-device, nothing leaves.
2. **Google AI Studio** — ``gemma-3-27b-it``, open weights, free tier.
3. **Groq** — ``qwen/qwen3.8-27b``, open weights, free tier. Failover.
4. **Deterministic parser** — no keys, no network, no model. Last resort so
   the demo is never a dead end.

Every lane speaks the OpenAI chat-completions shape, so swapping lanes is one
env var and zero code changes. That portability is the point.
"""

from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass, field

import httpx

TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)


# --------------------------------------------------------------------------
# lanes
# --------------------------------------------------------------------------
@dataclass
class Lane:
    name: str
    base_url: str
    model: str
    api_key: str = ""
    vision: bool = True
    local: bool = False
    note: str = ""

    @property
    def label(self) -> str:
        if self.local:
            return f"{self.name} · {self.model} · on-device"
        if not self.api_key:
            return f"{self.name} · {self.model} · free tier"
        return f"{self.name} · {self.model} · free tier"


def lanes() -> list[Lane]:
    """Build the chain from the environment. Missing keys simply drop out."""
    out: list[Lane] = []

    ollama_base = os.getenv("OLLAMA_BASE_URL", "").strip()
    if ollama_base:
        out.append(
            Lane(
                name="ollama",
                base_url=ollama_base.rstrip("/"),
                model=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
                api_key="ollama",  # Ollama ignores this, httpx wants something
                local=True,
                note="running on this machine",
            )
        )

    if os.getenv("AI_STUDIO_API_KEY", "").strip():
        out.append(
            Lane(
                name="ai-studio",
                base_url=os.getenv(
                    "AI_STUDIO_BASE_URL",
                    "https://generativelanguage.googleapis.com/v1beta/openai",
                ).rstrip("/"),
                model=os.getenv("AI_STUDIO_MODEL", "gemma-3-27b-it"),
                api_key=os.environ["AI_STUDIO_API_KEY"].strip(),
                note="Gemma 3, open weights",
            )
        )

    if os.getenv("GROQ_API_KEY", "").strip():
        out.append(
            Lane(
                name="groq",
                base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
                model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
                api_key=os.environ["GROQ_API_KEY"].strip(),
                note="Qwen 3.8, open weights",
            )
        )

    return out


def describe_lanes() -> list[dict]:
    """For the UI: what will actually be tried, in order."""
    rows = [
        {"name": lane.name, "model": lane.model, "label": lane.label, "local": lane.local}
        for lane in lanes()
    ]
    rows.append(
        {
            "name": "deterministic",
            "model": "regex parser",
            "label": "deterministic parser · always available",
            "local": True,
        }
    )
    return rows


# --------------------------------------------------------------------------
# prompting
# --------------------------------------------------------------------------
SYSTEM = (
    "You read a small shopkeeper's handwritten khata (udhaar / credit) notebook. "
    "You transcribe each transaction into compact JSON. Never invent a "
    "transaction. If a line is unreadable, put it in skipped_lines instead of "
    "guessing. Names are usually in Marathi, Hindi or English, and you should "
    "keep the name exactly as written, in its original script."
)

SCHEMA_HINT = """Return ONLY this JSON object, no commentary and no markdown fences:
{
  "rows": [
    {
      "name": "customer name exactly as written",
      "amount": 0,
      "direction": "udhaar",
      "note": "what it was for, short",
      "date": "DD/MM or null"
    }
  ],
  "skipped_lines": ["lines you could not read"],
  "warnings": ["anything the shopkeeper should double-check"]
}

direction rules:
- "udhaar"  = credit given, the customer now owes money ("udhaar", "udhar", "उधार", "बाकी")
- "payment" = money received, reduces the balance ("jama", "जमा", "paid", "received", "chuka", "चुका")

Other rules:
- amount is a positive number, always the line total (not a unit rate).
- one row per line. Same customer may appear many times; do not merge them.
- date is exactly as written, or null if there is no date on the line."""


def _user_prompt(ocr_text: str) -> str:
    if ocr_text.strip():
        return (
            "Here is text read off one page by the shop's own OCR. Extract "
            "every transaction.\n\n"
            f"<page>\n{ocr_text.strip()}\n</page>\n\n{SCHEMA_HINT}"
        )
    return (
        "Here is a photo of one page of the shop's khata. Read it and extract "
        f"every transaction.\n\n{SCHEMA_HINT}"
    )


def _messages(ocr_text: str, image_bytes: bytes | None, mime: str) -> list[dict]:
    """Gemma 3 has no system role, so the system prompt rides as the first turn."""
    content: list[dict] = [{"type": "text", "text": _user_prompt(ocr_text)}]
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        content.insert(
            0,
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        )
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": content},
    ]


# --------------------------------------------------------------------------
# response parsing
# --------------------------------------------------------------------------
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)
DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def parse_json_blob(raw: str) -> dict:
    """Models wrap JSON in prose and fences. Dig it out without giving up."""
    if not raw:
        raise ValueError("empty model response")
    text = raw.strip()

    fenced = _FENCE.search(text)
    if fenced:
        text = fenced.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Trailing commas are the single most common breakage.
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            return json.loads(cleaned)
    raise ValueError("no JSON object found in the model response")


def normalize_rows(payload: dict) -> tuple[list[dict], list[str], list[str]]:
    """Coerce whatever the model returned into our row shape."""
    rows_in = payload.get("rows")
    if not isinstance(rows_in, list):
        raise ValueError("model response had no 'rows' array")

    rows: list[dict] = []
    for item in rows_in:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip().translate(DEVANAGARI_DIGITS)
        if not name:
            continue
        try:
            amount = float(str(item.get("amount", "")).replace(",", "").strip() or 0)
        except ValueError:
            amount = 0.0
        if amount <= 0:
            continue

        direction = str(item.get("direction", "udhaar")).strip().lower()
        direction = "payment" if direction in {"payment", "jama", "paid", "received"} else "udhaar"

        rows.append(
            {
                "name": name,
                "amount": round(amount, 2),
                "direction": direction,
                "note": str(item.get("note", "") or "").strip(),
                "date": (str(item.get("date")).strip() if item.get("date") else ""),
            }
        )

    skipped = [str(s) for s in (payload.get("skipped_lines") or []) if str(s).strip()]
    warnings = [str(w) for w in (payload.get("warnings") or []) if str(w).strip()]
    return rows, skipped, warnings


# --------------------------------------------------------------------------
# the no-key lane: a deterministic parser
# --------------------------------------------------------------------------
_DATE = re.compile(r"\b\d{1,2}[/.-]\d{1,2}(?:[/.-]\d{2,4})?\b")
_STANDALONE_NUMBER = re.compile(r"(?<!\S)(\d+(?:\.\d+)?)(?!\S)")
_PAYMENT_WORDS = ("jama", "jamā", "जमा", "paid", "payment", "received", "chuka", "चुका", "चुकता", "मिळाले")
_CREDIT_WORDS = ("udhaar", "udhar", "उधार", "बाकी", "bak", "credit")
_NOISE = ("page", "khata", "vahi", "वही", "खाता", "total", "एकूण", "===", "---", "shri", "श्री")
_DIRECTION_IN_NOTE = re.compile(
    r"\b(?:udhaar|udhar|jama|paid|payment|received|uchal|उधार|जमा|बाकी|चुका)\b",
    re.IGNORECASE,
)


def deterministic_extract(ocr_text: str) -> dict:
    """Read rows with plain regex. No model, no network, no keys.

    This exists so that anyone reviewing the project can click through the
    whole flow without signing up for anything.
    """
    rows, skipped = [], []

    for raw_line in ocr_text.splitlines():
        line = raw_line.strip().translate(DEVANAGARI_DIGITS)
        if not line:
            continue
        low = line.lower()
        if any(token in low for token in _NOISE):
            continue

        # Mask dates first, so 12/10 is not mistaken for two amounts, and
        # match only whitespace-delimited numbers so "2kg" never reads as ₹2.
        masked = _DATE.sub(lambda m: " " * len(m.group(0)), line)
        matches = list(_STANDALONE_NUMBER.finditer(masked))
        if not matches:
            skipped.append(raw_line.strip())
            continue

        amount_match = matches[-1]
        amount = float(amount_match.group(1))
        date_match = _DATE.search(line)
        date = date_match.group(0) if date_match else ""

        if any(word in low for word in _PAYMENT_WORDS):
            direction = "payment"
        elif any(word in low for word in _CREDIT_WORDS):
            direction = "udhaar"
        else:
            direction = "udhaar"

        # Name sits left of the date; the note is whatever sits between the
        # date and the amount. Anything past the first wide gap is the note.
        if date_match:
            name_raw = line[: date_match.start()]
            note_raw = line[date_match.end() : amount_match.start()]
        else:
            name_raw = line[: amount_match.start()]
            note_raw = ""

        if "  " in name_raw:
            name, _, spill = name_raw.partition("  ")
            note_raw = f"{spill} {note_raw}"
        else:
            name = name_raw

        name = name.strip(" -–:|\t")
        note = re.sub(r"\s+", " ", note_raw).strip(" -–:|\t,")
        note = _DIRECTION_IN_NOTE.sub("", note).strip(" ()-–:,")

        if not name:
            skipped.append(raw_line.strip())
            continue

        rows.append(
            {
                "name": name,
                "amount": amount,
                "direction": direction,
                "note": note,
                "date": date,
            }
        )

    warnings = []
    if skipped:
        warnings.append(f"{len(skipped)} line(s) could not be read — check them by hand.")
    return {"rows": rows, "skipped_lines": skipped, "warnings": warnings}


# --------------------------------------------------------------------------
# public entry point
# --------------------------------------------------------------------------
@dataclass
class ExtractResult:
    rows: list[dict] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    lane: str = "deterministic"
    lane_kind: str = "fallback"
    errors: list[str] = field(default_factory=list)
    used_image: bool = False

    @property
    def ok(self) -> bool:
        return bool(self.rows)


def _call_lane(lane: Lane, messages: list[dict]) -> str:
    url = f"{lane.base_url}/chat/completions"
    body = {
        "model": lane.model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 4000,
    }
    headers = {
        "Authorization": f"Bearer {lane.api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(url, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"] or ""


def extract_rows(
    ocr_text: str = "",
    image_bytes: bytes | None = None,
    mime: str = "image/jpeg",
    allow_deterministic: bool = True,
) -> ExtractResult:
    """Read every transaction on the page, trying each lane until one works."""
    result = ExtractResult()

    for lane in lanes():
        image_for_lane = image_bytes if (lane.vision and image_bytes) else None
        try:
            raw = _call_lane(lane, _messages(ocr_text, image_for_lane, mime))
            rows, skipped, warnings = normalize_rows(parse_json_blob(raw))
        except Exception as exc:
            result.errors.append(f"{lane.name}: {type(exc).__name__}: {exc}")
            continue

        if not rows:
            result.errors.append(f"{lane.name}: answered, but found no transactions")
            continue

        result.rows = rows
        result.skipped = skipped
        result.warnings = warnings
        result.lane = lane.model
        result.lane_kind = "on-device" if lane.local else lane.name
        result.used_image = bool(image_for_lane)
        return result

    # Nothing answered. Never leave the reviewer with a dead end.
    if allow_deterministic and ocr_text.strip():
        payload = deterministic_extract(ocr_text)
        result.rows = payload["rows"]
        result.skipped = payload["skipped_lines"]
        result.warnings = payload["warnings"]
        result.lane = "regex parser"
        result.lane_kind = "deterministic"
        if lanes():
            result.warnings.append(
                "No model lane answered, so the built-in parser read the page instead."
            )
        return result

    if not result.errors:
        result.errors.append(
            "Nothing to read: no OCR text and no model lane available. "
            "Add a key in .env or install a local OCR backend."
        )
    return result


def polish_reminder(draft: str) -> str:
    """Optional: let the model soften the wording. Falls back to the draft."""
    for lane in lanes():
        try:
            raw = _call_lane(
                lane,
                [
                    {
                        "role": "system",
                        "content": (
                            "You rewrite a shopkeeper's payment reminder so it "
                            "is polite, short and never threatening. Keep the "
                            "amount, the name and the language. Return only the message."
                        ),
                    },
                    {"role": "user", "content": draft},
                ],
            )
            cleaned = raw.strip().strip('"')
            if cleaned:
                return cleaned
        except Exception:
            continue
    return draft

"""Udhaar Book — FastAPI app.

Flow:  photo -> local OCR -> open-weight model -> confirm table -> ledger -> reminder.
The confirm table is not a compromise; a book about money should be checked by
a human before it is written.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # before importing udhaar.*, which reads config at import time

from fastapi import FastAPI, File, Form, Request, UploadFile  # noqa: E402
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.templating import Jinja2Templates  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from udhaar import ledger, llm, ocr, plot, reminders  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = BASE_DIR / "samples" / "sample_ledger.txt"

app = FastAPI(title="Udhaar Book", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["strip_for"] = plot.strip_for


@app.on_event("startup")
def _startup() -> None:
    ledger.init_db()


def _context(request: Request, **extra) -> dict:
    backends = ocr.available_backends()
    lane_rows = llm.describe_lanes()
    ctx = {
        "shop_name": reminders.shop_name(),
        "shop_lang": reminders.shop_lang(),
        "langs": reminders.LANGS,
        "lang_short": reminders.LANGS_SHORT,
        "lanes": lane_rows,
        "ocr_backends": backends,
        "reader_line": _reader_line(backends, lane_rows),
        "reader_state": _reader_state(backends, lane_rows),
        "nav": "",
    }
    ctx.update(extra)
    return ctx


def _reader_state(backends: list[str], lane_rows: list[dict]) -> str:
    """What can actually read a photo on this machine right now.

    The read screen used to promise that a page "goes to the model lane" even
    when no lane had a key, which is the same overclaim the footer carried.
    """
    if backends:
        return "ocr"
    if any(row["name"] != "deterministic" for row in lane_rows):
        return "lane"
    return "none"


PROVIDER = {"ollama": "Ollama", "ai-studio": "AI Studio", "groq": "Groq"}


def _reader_line(backends: list[str], lane_rows: list[dict]) -> str:
    """One honest sentence about who reads a page on *this* machine.

    The footer used to claim a model lane whenever no OCR backend was installed,
    which on a keyless machine is a lie: the deterministic parser did the work.
    """
    configured = [row for row in lane_rows if row["name"] != "deterministic"]
    if backends and configured:
        return f"{', '.join(backends)} on this machine, then {configured[0]['model']}"
    if backends:
        return f"{', '.join(backends)} on this machine"
    if configured:
        first = configured[0]
        where = "this machine" if first["local"] else PROVIDER.get(first["name"], first["name"])
        return f"{first['model']} via {where}"
    return "the built-in parser (no model, no network)"


def _render(request: Request, name: str, status_code: int = 200, **extra):
    """Starlette 1.x takes the request first; the old argument order is gone."""
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=_context(request, **extra),
        status_code=status_code,
    )


def _sample_text() -> str:
    return SAMPLE_FILE.read_text(encoding="utf-8") if SAMPLE_FILE.exists() else ""


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return _render(request, "index.html", nav="read", sample_text=_sample_text())


@app.post("/read", response_class=HTMLResponse)
async def read_page(
    request: Request,
    photo: UploadFile | None = File(default=None),
    use_sample: str = Form(default=""),
    backend: str = Form(default="auto"),
):
    image_bytes: bytes | None = None
    mime = "image/jpeg"
    page_name = ""

    if photo is not None and photo.filename:
        image_bytes = await photo.read()
        mime = photo.content_type or "image/jpeg"
        page_name = photo.filename

    if image_bytes:
        result = ocr.run_ocr(image_bytes, backend=backend)
    elif use_sample and SAMPLE_FILE.exists():
        result = ocr.from_fixture(_sample_text())
        page_name = "sample_ledger.txt"
    else:
        return _render(
            request,
            "index.html",
            status_code=400,
            nav="read",
            error="Add a photo of a page, or tick 'use the sample page'.",
            sample_text=_sample_text(),
        )

    extract = llm.extract_rows(
        ocr_text=result.text,
        image_bytes=image_bytes,
        mime=mime,
    )

    scan_id = ledger.start_scan(
        backend=result.backend,
        lane=extract.lane,
        ocr_text=result.text,
        page_name=page_name,
    )

    # Say exactly who read this page, in one grammatical sentence. "Nothing
    # could read it" is a fact worth stating plainly, not a blank table.
    reader = result.backend if result.backend not in ("", "none") else ""
    if not reader and extract.used_image and extract.lane not in ("", "regex parser"):
        reader = extract.lane
    if not reader:
        source_note = (
            f"{page_name or 'this page'} · nothing on this machine could read it — "
            "no OCR backend is installed and no model lane has a key"
        )
    else:
        source_note = f"{page_name or 'this page'} · read by {reader} · structured by {extract.lane}"

    return _render(
        request,
        "review.html",
        nav="read",
        source_note=source_note,
        rows=extract.rows,
        skipped=extract.skipped,
        warnings=extract.warnings + result.notes,
        errors=extract.errors,
        ocr_backend=result.backend,
        ocr_text=result.text,
        lane=extract.lane,
        lane_kind=extract.lane_kind,
        used_image=extract.used_image,
        scan_id=scan_id,
        page_name=page_name,
    )


class SavePayload(BaseModel):
    scan_id: int | None = None
    lane: str = ""
    rows: list[dict] = []


@app.get("/read", include_in_schema=False)
def read_page_again():
    """The confirm screen is a step, not a page.

    A refresh or a bookmark used to land on raw JSON (`Method Not Allowed`),
    which is a dead end for a shopkeeper and for anyone reviewing the app.
    Send them back to the page that starts the step.
    """
    return RedirectResponse("/", status_code=303)


@app.post("/save")
def save(payload: SavePayload):
    saved = ledger.save_rows(payload.rows, lane=payload.lane, scan_id=payload.scan_id)
    return JSONResponse({"saved": saved, "redirect": "/ledger"})


@app.get("/ledger", response_class=HTMLResponse)
def ledger_view(request: Request):
    return _render(
        request,
        "ledger.html",
        nav="ledger",
        balances=ledger.balances(),
        totals=ledger.totals(),
        recent=ledger.recent(limit=15),
    )


@app.get("/reminders", response_class=HTMLResponse)
def reminders_view(request: Request):
    lang = request.query_params.get("lang") or reminders.shop_lang()
    if lang not in reminders.LANGS:
        lang = "en"

    pending = [b for b in ledger.balances() if b["balance"] > 0]
    entries = []
    for item in pending:
        lines = int(item["entries"])
        entries.append(
            {
                **item,
                "strip": plot.strip_for(item["name_key"]),
                "lines_label": f"{lines} line" + ("" if lines == 1 else "s"),
                "message": reminders.build_reminder(item["name"], item["balance"], lang),
            }
        )

    return _render(
        request,
        "reminders.html",
        nav="reminders",
        entries=entries,
        plot=plot.plot_rows(pending),
        active_lang=lang,
        total_outstanding=sum(b["balance"] for b in pending),
        totals=ledger.totals(),
    )


@app.post("/reset")
def reset():
    ledger.reset()
    return RedirectResponse("/ledger", status_code=303)


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "ocr_backends": ocr.available_backends(),
        "lanes": [lane["name"] for lane in llm.describe_lanes()],
        "db": os.getenv("UDHAAR_DB", "data/udhaar.db"),
    }

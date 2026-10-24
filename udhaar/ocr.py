"""Local OCR. Runs on CPU, needs no GPU, needs no network.

This is the layer that keeps the promise about customer data: the *page*
is read here, on the shop's own machine. Only text ever has to leave, and
if you point ``OLLAMA_BASE_URL`` at a local model, nothing leaves at all.

Backends are optional by design. ``auto`` probes for whatever is installed
and reports honestly what it used, rather than silently pretending.
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from typing import Iterable

# Probe order: lightest and most reliable first.
BACKEND_ORDER = ("rapidocr", "paddleocr", "tesseract")


@dataclass
class OcrResult:
    """What we managed to read, and how."""

    text: str
    lines: list[str] = field(default_factory=list)
    backend: str = "none"
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.text.strip())


class OcrUnavailable(RuntimeError):
    """Raised when no OCR backend can be loaded."""


# --------------------------------------------------------------------------
# backend probing
# --------------------------------------------------------------------------
def available_backends() -> list[str]:
    """Return installed backends, in preference order."""
    found: list[str] = []
    for name in BACKEND_ORDER:
        if _probe(name):
            found.append(name)
    return found


def _probe(name: str) -> bool:
    import importlib.util

    modules = {
        # RapidOCR renamed its package in 3.x; both import paths are real.
        "rapidocr": ("rapidocr", "rapidocr_onnxruntime"),
        "paddleocr": ("paddleocr",),
        "tesseract": ("pytesseract",),
    }[name]
    for module in modules:
        try:
            if importlib.util.find_spec(module) is not None:
                return True
        except (ImportError, ValueError):
            continue
    return False


def _ocr_lang() -> str:
    """Which recognition model to load.

    ``auto`` keeps the shipped Chinese/English model, which is the one that
    reads Latin names, digits and dates. Devanagari needs its own model and
    reads Latin badly, so it is opt-in rather than a guess.
    """
    raw = (os.getenv("OCR_LANG", "auto") or "auto").strip().lower()
    if raw in {"hi", "mr", "marathi", "hindi", "devanagari", "देवनागरी"}:
        return "devanagari"
    return "auto"


def _group_lines(boxes, texts) -> list[str]:
    """Rebuild text lines from per-box OCR output.

    Detection boxes split one written line into several fragments ("Ramesh
    Patil", "12/10 cheeni 2kg", "340 udhaar"). The rest of the pipeline reads
    line by line, so fragments are grouped by **vertical overlap** and joined
    left to right. Centres alone are not enough: a Devanagari fragment is
    taller than the digits beside it and drifts away from their centre line.
    """
    items: list[dict] = []
    for box, text in zip(
        boxes if boxes is not None else [],
        texts if texts is not None else [],
    ):
        text = str(text).strip()
        if not text:
            continue
        try:
            points = [(float(p[0]), float(p[1])) for p in box]
        except (TypeError, ValueError, IndexError):
            continue
        if not points:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        items.append(
            {
                "x": min(xs),
                "top": min(ys),
                "bottom": max(ys),
                "text": text,
            }
        )

    if not items:
        return []

    items.sort(key=lambda item: ((item["top"] + item["bottom"]) / 2, item["x"]))
    lines: list[str] = []
    current: list[dict] = []
    span: tuple[float, float] | None = None

    def flush() -> None:
        nonlocal current, span
        if current:
            ordered = sorted(current, key=lambda item: item["x"])
            lines.append("  ".join(item["text"] for item in ordered))
        current, span = [], None

    for item in items:
        if span is None:
            current.append(item)
            span = (item["top"], item["bottom"])
            continue

        overlap = min(span[1], item["bottom"]) - max(span[0], item["top"])
        shorter = min(span[1] - span[0], item["bottom"] - item["top"]) or 1.0
        if overlap / shorter >= 0.4:
            current.append(item)
            span = (min(span[0], item["top"]), max(span[1], item["bottom"]))
        else:
            flush()
            current = [item]
            span = (item["top"], item["bottom"])

    flush()
    return lines


def _decode(image_bytes: bytes):
    """Decode to a numpy array, or None if we have no image library."""
    try:
        from PIL import Image
        import numpy as np

        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return np.array(pil)
    except Exception:
        pass
    try:
        import cv2
        import numpy as np

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


# --------------------------------------------------------------------------
# backends
# --------------------------------------------------------------------------
def _run_rapidocr(image_bytes: bytes, notes: list[str]) -> list[str]:
    """PP-OCR through ONNX Runtime. Runs on CPU, no network after install."""
    payload = _decode(image_bytes)
    if payload is None:
        payload = image_bytes

    try:
        from rapidocr import LangRec, ModelType, OCRVersion, RapidOCR  # 3.x
    except ImportError:
        # 1.x/2.x kept the same engine under a different package name.
        from rapidocr_onnxruntime import RapidOCR  # type: ignore[no-redef]

        engine = RapidOCR()
        try:
            result, _elapsed = engine(payload)
        except TypeError:
            result, _elapsed = engine(payload, use_det=True, use_cls=True, use_rec=True)
        notes.append("rapidocr 1.x = PP-OCR (open source) via ONNX Runtime, CPU only")
        return _group_lines(
            [item[0] for item in result or []],
            [item[1] for item in result or []],
        )

    lang = _ocr_lang()
    params = None
    if lang == "devanagari":
        # PP-OCRv5 mobile is the only shipped combination with a Devanagari
        # recognizer; v6 small and v4 mobile either reject the language or
        # garbled it. The model is fetched once (7 MB) and cached beside the
        # package, so later runs are offline.
        params = {
            "Rec.lang_type": LangRec.DEVANAGARI,
            "Rec.ocr_version": OCRVersion.PPOCRV5,
            "Rec.model_type": ModelType.MOBILE,
        }

    engine = RapidOCR(params=params)
    output = engine(payload)

    texts = getattr(output, "txts", None) or ()
    boxes = getattr(output, "boxes", None)
    lines = _group_lines(boxes, texts) if boxes is not None else [
        str(text).strip() for text in texts if str(text).strip()
    ]
    script = "devanagari" if lang == "devanagari" else "Latin + digits"
    notes.append(f"rapidocr 3.x = PP-OCR ({script}) via ONNX Runtime, CPU only")
    return lines


def _run_paddleocr(image_bytes: bytes, notes: list[str]) -> list[str]:
    from paddleocr import PaddleOCR

    engine = PaddleOCR(use_angle_cls=True, lang="hi", show_log=False)
    decoded = _decode(image_bytes)
    if decoded is None:
        raise OcrUnavailable("paddleocr needs PIL or opencv to decode the image")

    raw = engine.ocr(decoded, cls=True)
    lines: list[str] = []
    for page in raw or []:
        for item in page or []:
            # item is [box, (text, score)]
            try:
                text = str(item[1][0]).strip()
            except (IndexError, TypeError):
                continue
            if text:
                lines.append(text)
    notes.append("paddleocr (PaddleOCR, open source) on CPU")
    return lines


def _run_tesseract(image_bytes: bytes, notes: list[str]) -> list[str]:
    import pytesseract
    from PIL import Image

    image = Image.open(io.BytesIO(image_bytes))
    try:
        text = pytesseract.image_to_string(image, lang="hin+mar+eng")
    except pytesseract.TesseractError:
        # Language packs for Hindi/Marathi are not always installed.
        notes.append("tesseract: hin/mar language packs missing, fell back to eng")
        text = pytesseract.image_to_string(image, lang="eng")
    notes.append("tesseract on CPU")
    return [line.strip() for line in text.splitlines() if line.strip()]


_RUNNERS = {
    "rapidocr": _run_rapidocr,
    "paddleocr": _run_paddleocr,
    "tesseract": _run_tesseract,
}


# --------------------------------------------------------------------------
# public entry point
# --------------------------------------------------------------------------
def run_ocr(image_bytes: bytes, backend: str = "auto") -> OcrResult:
    """Read a notebook page locally.

    ``backend``: ``auto`` picks the best installed backend, ``none`` skips
    OCR entirely (the vision lane will read the image instead). Never raises
    for a missing backend — it reports it in ``notes``.
    """
    notes: list[str] = []
    if backend == "none":
        return OcrResult(text="", backend="none", notes=["OCR skipped by request"])

    if backend == "auto":
        # A shop that pins a backend in .env means it, so auto honours it.
        pinned = (os.getenv("OCR_BACKEND", "auto") or "auto").strip().lower()
        if pinned and pinned != "auto":
            backend = pinned

    if backend == "auto":
        installed = available_backends()
        if not installed:
            return OcrResult(
                text="",
                backend="none",
                notes=[
                    "No local OCR backend installed. See requirements-ocr.txt "
                    "for the on-device layer."
                ],
            )
        backend = installed[0]

    runner = _RUNNERS.get(backend)
    if runner is None:
        return OcrResult(text="", backend="none", notes=[f"Unknown backend {backend!r}"])

    try:
        lines = runner(image_bytes, notes)
    except OcrUnavailable as exc:
        return OcrResult(text="", backend="none", notes=[str(exc)])
    except Exception as exc:  # a broken install must not take the app down
        return OcrResult(
            text="",
            backend="none",
            notes=[f"{backend} failed at runtime ({type(exc).__name__}: {exc})"],
        )

    return OcrResult(text="\n".join(lines), lines=lines, backend=backend, notes=notes)


def from_fixture(payload: str) -> OcrResult:
    """Wrap a stored OCR dump so the flow stays identical in demos/tests."""
    lines: Iterable[str] = [line.strip() for line in payload.splitlines() if line.strip()]
    lines = list(lines)
    return OcrResult(
        text="\n".join(lines),
        lines=lines,
        backend="fixture",
        notes=["fixture text (no OCR run) — clearly labelled, not a field result"],
    )

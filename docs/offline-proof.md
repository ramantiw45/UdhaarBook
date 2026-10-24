# The offline / on-device test

This file exists because "runs locally" is the easiest claim in this project to
fake, and the easiest for a reviewer to check. Run the test, then write only
what actually happened.

## The test

1. Install the on-device reader: `pip install -r requirements-ocr.txt`
2. Confirm it loaded: `python -c "from udhaar import ocr; print(ocr.available_backends())"`
   — should print at least one backend. Empty list means the on-device claim
   does **not** hold on this machine yet.
3. Cut the machine off from the network — physically, or for a scripted check
   point every proxy at a dead port:
   `HTTP_PROXY=http://127.0.0.1:9 HTTPS_PROXY=http://127.0.0.1:9` (PowerShell:
   `$env:HTTP_PROXY="http://127.0.0.1:9"`). RapidOCR downloads models with
   `requests`, so a blocked proxy is enough to prove the run itself is local.
4. Read a page. With no photo handy, render one:
   `python tools/make_page_image.py` then run the reader over
   `data/page_render.png`, or open the app and choose the file.
5. The OCR step must still return text. The photo never left the machine.

Record what you saw: a screenshot with the Wi-Fi indicator visible, plus the
`OCR_BACKEND` shown on the review screen.

## What was actually run here

2026-10-24, Windows 11, Python 3.14.0, `rapidocr 3.10.0` + `onnxruntime 1.31.0`
(CPU, wheels; no GPU, no torch).

| Page | Reader | Result |
|---|---|---|
| `data/page_render.png` — the 12-line sample, Latin/digits | `rapidocr`, PP-OCRv6 small | 13 lines, **10 rows**; 2 lines skipped (the two Devanagari lines, unreadable to the Latin model) |
| `data/dev_page.png` — the same page rendered in Devanagari | `rapidocr`, PP-OCRv5 mobile Devanagari (`OCR_LANG=mr`) | 13 lines, **6 rows**; amounts for 6 lines were detected, 6 lines skipped and shown for hand-checking |

Both runs completed with `HTTP_PROXY`/`HTTPS_PROXY` pointed at a dead port, so
the OCR pass made no network request. The Devanagari recognizer is the one
model that is not inside the wheel: it is fetched once (~7 MB) on first use and
cached next to the package.

What this does **not** prove: that OCR reads a real shop's handwriting, a
smudged page, or a phone photo at an angle. The fixtures are clean digital
renders. The confirm table exists for exactly that gap.

## What each outcome lets you write

| What happened | What you may claim |
|---|---|
| OCR ran with the network blocked | "The page is read on the device. Photograph, read, confirm — no network for the reading step." |
| OCR installed, but you did not run it blocked | "An open-source on-device reader is wired in and one install away." |
| No OCR backend available on this Python | "On this machine the page goes to the free model lane; the on-device path is documented in `requirements-ocr.txt` and in the README." |
| You pointed `OLLAMA_BASE_URL` at a local model and ran it | "The whole pipeline — reading and structuring — ran on this machine with no network." |

## What you may never write

- "100% offline" if a hosted lane served the request.
- "Your data never leaves your device" when the configured lane is a hosted one.
- "Runs on the shop's phone." It does not. A 4B model needs a machine; the
  phone is the camera. If that changes, change this file first.

## The honest version, if the local model never gets run

> The reading layer is open source and runs on CPU, so the *page* — the part
> with your customers' names on it — can stay on the machine that owns it. The
> structuring layer is an open-weight model; on this deployment it is served
> from a free tier, and the self-hosted path is one environment variable and
> one `ollama pull` away. The free lane's own terms allow training on inputs,
> which is exactly why that path exists.

That paragraph is true, checkable, and stronger than a claim nobody can
reproduce.

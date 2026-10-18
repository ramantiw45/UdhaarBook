# The offline / on-device test

This file exists because "runs locally" is the easiest claim in this project to
fake, and the easiest for a reviewer to check. Run the test, then write only
what actually happened.

## The test

1. Install the on-device reader: `pip install -r requirements-ocr.txt`
2. Confirm it loaded: `python -c "from udhaar import ocr; print(ocr.available_backends())"`
   — should print at least one backend. Empty list means the on-device claim
   does **not** hold on this machine yet.
3. Turn the machine's Wi-Fi off. Physically, not by pretending.
4. Open the app, choose a photo of a page, submit.
5. The OCR step must still return text. The photo never left the machine.

Record what you saw: a screenshot with the Wi-Fi indicator visible, plus the
`OCR_BACKEND` shown on the review screen.

## What each outcome lets you write

| What happened | What you may claim |
|---|---|
| OCR ran with Wi-Fi off | "The page is read on the device. Photograph, read, confirm — no network." |
| OCR installed, but you did not run it offline | "An open-source on-device reader is wired in and one install away." |
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

# Finish review packet — Udhaar Book

**Revision 5.** Revision 2 was the build after the first finish review. Since
then the model lane moved to Gemma 4's native route, a second finish review
closed six findings, and the optional on-device OCR layer was installed and
measured on this machine (`docs/offline-proof.md`). The captures in this packet
were taken at revision 2 and have not been re-shot; the layout they show is the
shipped layout. The disposition requested is a **score**, not a new hunt.

This is a **code-led build** (no approved comp exists, and no comp round was
run; the direction was locked from a dealt hand and the world was built
directly in code). Treat the direction contract below as the binding promise,
judge TYPE/MATERIAL against OWN-WORLD, and mark the comp-dependent checks as not
applicable rather than failing them silently.

## Primary surface

`/reminders` — the Ask screen. This is the screen that has to be undeniable: the
shopkeeper, alone at closing time, sees who still owes and gets a message in the
customer's own language to send on WhatsApp.

## Captures (read these files)

| file | what it is |
|---|---|
| `.impeccable/review/desktop.png` | `/reminders`, full page, **1119×1914 px** (CSS viewport 895px, device scale 1.25). The app's desktop layout is a centred 760px column, so a wider viewport adds margin only. |
| `.impeccable/review/mobile.png` | `/reminders`, full page, **true 390×1790 CSS px**. Captured through a same-origin harness that renders the app in a 390px iframe, zoomed to land on 1:1 device pixels, so the layout viewport inside is exactly 390px. |
| `docs/screens/01-read.jpg` | `/` — photograph a page (desktop). The reader-state sentence now names what can actually read a photo on this machine. |
| `docs/screens/05-confirm-before-writing.jpg` | `/read` after a sample read: the confirm table (desktop). |
| `docs/screens/02-the-book.jpg` | `/ledger` — the book itself: every customer, given / paid / balance, page numbers. |
| `docs/screens/03-who-to-ask.jpg` | `/reminders` (desktop, second angle). |
| `docs/screens/03b-who-to-ask-greyscale.jpg` | the same screen with colour stripped — the world must survive it. |
| `docs/screens/04-on-a-phone.jpg` | four screens at 390px in one image (read, confirm, book, ask). |

**What the captures cannot show.** The signature interaction is a tap: a row
expands to reveal the name and the message (`grid-template-rows: 0fr → 1fr`).
A collapse never hides text from the document — the panel is clipped, never
`opacity: 0` / `visibility: hidden` — so a screen reader, a text search and the
printed page still reach every word. The panel's controls, though, are `inert`
while it is closed, so fourteen invisible buttons never sit in the tab order.
The first row is decoded on load, so the screen at rest shows one full example.

## What changed after the first finish review

1. **Truth in the footer and on the read screen.** The footer used to name a
   model lane even when the built-in parser had read the page. It now renders
   what actually read it (`Read by the built-in parser (no model, no network)`),
   and `/` explains, in three branches, whether an on-device reader is ready, a
   model lane is configured, or nothing can read a photo yet. The confirm
   screen's "raw text" fallback no longer claims a model read the image when
   nothing did.
2. **The plot band is bounded.** Height capped at 118px; past eighteen dues the
   remainder is one dashed hairline standing for everyone else, and the count
   above the band keeps naming the true total (25 still to ask, 19 hairlines,
   one of them dashed — proved on a throwaway database, not by eye).
3. **Collapsed panels are `inert`.** At rest the page exposes 18 tab stops, not 32.
4. **One action per row.** Copy is the single solid, full-width (up to 420px)
   button in a decoded row; WhatsApp is a quiet caps text link on a hairline,
   44px tall, ranked underneath. The eye is never asked to choose between equals.
5. **The identity device commits.** The hue strip is 6px at rest (was 8px), and
   the decoded row — the only row whose name is showing — carries the mark at
   plate scale (10×44px) with the entry number stepping from 11px to 15px.
6. **The filler is gone.** At rest a row is the catalogue entry: number, mark,
   empty name slot, amount. The page number and line count moved into the opened
   panel's lineage (`Page 1 · 1 line · last 15/10 · ₹560 given`), so nothing on
   the screen says "2 lines" eight times.
7. **The dealt hand is on record.** `options-bolder.json` now carries
   `seed: d2007df6`, the hand the world was dealt from.
8. **The system is written down and reconciled.** `DESIGN.md` +
   `.impeccable/design.json` describe the shipped build — including the 6px
   strip, the plate-scale mark, the three action ranks, the dashed remainder and
   the print-only paper colours. The detector's design-system advisories went
   from 27 to zero once the system declared what the code actually uses.

Also fixed while verifying: a refresh or bookmark on `/read` used to return raw
JSON (`Method Not Allowed`); it now 303s to `/`, the page that starts the step.
Dead weight removed (`--track` token, `static/reminders.js`), and the review
component's comment corrected to say what it draws.

## Since revision 2 (shipping build)

1. **Gemma 4 on its native route.** Gemma 3 was retired from the Gemini API in
   2026, so the AI Studio lane posts to `models/{model}:generateContent` through
   a small adapter. The default is `gemma-4-26b-a4b-it` (26B-A4B MoE, steadier on
   the free tier); `gemma-4-31b-it` is one env var away. A 5xx gets one retry; a
   429 is not retried. `tests/test_pipeline.py` asserts the native body, so a
   rename alone cannot pass.
2. **Second finish review: six findings, all closed.** `inert` moved to the tools
   inside a decoded row, so the panel's own links stay reachable while a closed
   panel is out of the tab order; the row `aria-label` is rebuilt on open and
   close with the customer's name; copy confirmation is filled amber with a
   polite live region; the reader select is shortened to "Auto — best reader
   here"; step numbers use `--red-bright`; `DESIGN.md` and `design.json` were
   reconciled and the sample row in `design.json` fixed.
3. **The local reader is installed and measured.** RapidOCR 3.10 + ONNX Runtime
   1.31 on Python 3.14, CPU only. Detection fragments are regrouped by vertical
   overlap before parsing (a row is one line, not three), unit quantities
   ("10 किलो") are never read as money, and `OCR_LANG=mr` loads the PP-OCRv5
   Devanagari recognizer. `docs/offline-proof.md` records 10/12 rows on the
   Latin render and 6/12 on the Devanagari render, with the network blocked.
4. **Honest lane states.** `describe_lanes()` carries `vision`; a text-only lane
   with no OCR text is skipped instead of being asked to invent rows, and the
   read screen and footer only promise a model lane when one can actually see a
   photo.

## Measured in the live page (not asserted)

- At 390px: `scrollWidth` 390 (no horizontal scroll), and the four children of a
  row have **no overlapping boxes** at either viewport.
- Plot band with 8 dues: 106px, 8 hairlines, no remainder. With 25 dues:
  105px, 18 hairlines + one `line rest`, `<line>` count 19, count label
  "25 still to ask", aria-label naming the dashed remainder, and all 25 entries
  present in the document.
- Tap → one row opens; Reveal → all 8 open and the key becomes Conceal;
  Conceal → 0 open, panels clipped to 0 height, content still
  `visibility: visible; opacity: 1`, and 24 panels `inert`.

## Contracts and inputs

- `PRODUCT.md` — the product truth (who the user is, why they pay, the one
  scene, what "wrong" would feel like).
- `.impeccable/surface-brief-reminders.md` — the binding direction contract for
  this surface.
- `.impeccable/decision/options-bolder.json` — the bolder hand the world was
  dealt from (seed `d2007df6`); the locked card is the one marked `assigned`.
- `DESIGN.md` and `.impeccable/design.json` — the written system, derived from
  the shipped code after the first review.
- Craft floor:
  `C:\Users\Raman Tiwari\.config\opencode\skills\impeccable\reference\craft-floor.md`

## Detector state (impeccable detect --json)

Files: `.impeccable/review/detect-desktop.json`, `detect-mobile.json`,
`detect-files.json`. Current state: **no errors, no text-occlusion.** With what
was measured rather than assumed:

- `side-tab` ×2 (URL scans) + ×2 (file scan) — the customer hue strip. Deliberate
  and load-bearing: the strip *is* the customer's code on a screen other people
  can see, not decoration on a card. It is extended by the `received` variant
  (hollow outline + strike) so the state never rides on colour alone. At 6px it
  is the contract's own mass, and it is a bare mark in a grid — not a coloured
  border on a card.
- `low-contrast` ×2 — **static-scan false positive.** These come only from
  `detect-files.json`, which assumes a white background (`#8a8a85` on `#fff` =
  3.5:1). On the app's actual dark ground the same values measure 5.7:1 and
  6.9:1, and the live URL passes at both viewports report no contrast finding.
- `em-dash-overuse` (advisory) — the copy is written in the voice of a shop
  notice; em dashes are the author's habit and are left in deliberately.
- The four `text-occlusion` warnings from revision 1 are **gone**, and they are
  gone for real: re-running the URL scan with `--no-design-system` still finds
  none, so the disappearance is the layout change (the empty name slot and the
  single action), not a config effect.

## Honest limits

- **No real user has used this.** No field test happened. `samples/*` are
  synthetic fixtures, and the "shop" is a fixture shop (`Suresh Kirana`).
- **The photo path is now proven on this machine, but only on rendered pages.**
  `rapidocr 3.10` + `onnxruntime 1.31` install on Python 3.14; with the network
  blocked, the local reader took the 12-line rendered sample to 10 rows (Latin
  model) and the Devanagari render to 6 rows (`OCR_LANG=mr`). The two Devanagari
  lines the Latin model cannot read are reported, not guessed. What remains
  unproven is a real shop's handwriting, a smudged page, and a phone photo at an
  angle — see `docs/offline-proof.md` for the exact numbers and the gaps.
- **Coded is a visual measure, not a data one.** When a row is open the customer's
  name is inside the reminder text by design — the message has to greet them. The
  coding protects against a passer-by reading the list at rest; it does not make
  the document anonymous. No rule in `DESIGN.md` claims otherwise.
- Language support is template-based for three languages (English, Hindi,
  Marathi — see `udhaar/reminders.py`); only Marathi is exercised in the
  captures. The app's operating labels are English.

# Finish review packet — Udhaar Book

**Disposition requested:** the finish review contract in `reviewer-contract.md`.
This is a **code-led build** (no approved comp exists, and no comp round was run;
the direction was locked from a dealt hand and the world was built directly in
code). Treat the direction contract below as the binding promise, judge
TYPE/MATERIAL against OWN-WORLD, and mark the comp-dependent checks as not
applicable rather than failing them silently.

## Primary surface

`/reminders` — the Ask screen. This is the screen that has to be undeniable: the
shopkeeper, alone at closing time, sees who still owes and gets a message in the
customer's own language to send on WhatsApp.

## Captures (read these files)

| file | what it is |
|---|---|
| `.impeccable/review/desktop.png` | `/reminders`, full page. CSS viewport 895px wide (the review browser's window), captured at device scale 1.25 → 1119×1844 px. The app's desktop layout is a centred 760px column, so a wider viewport adds margin only. |
| `.impeccable/review/mobile.png` | `/reminders`, full page, **true 390×1780 CSS px**. Captured through a same-origin harness that renders the app in a 390px iframe; the harness was zoomed to land on 1:1 device pixels, so the layout viewport inside is exactly 390px. |
| `docs/screens/01-read.jpg` | `/` — photograph a page (desktop). |
| `docs/screens/05-confirm-before-writing.jpg` | `/read` after a sample read: the confirm table (desktop). |
| `docs/screens/02-the-book.jpg` | `/ledger` — the book itself: every customer, given / paid / balance, page numbers. |
| `docs/screens/03-who-to-ask.jpg` | `/reminders` (desktop, second angle). |
| `docs/screens/03b-who-to-ask-greyscale.jpg` | the same screen with colour stripped — the world must survive it. |
| `docs/screens/04-on-a-phone.jpg` | four screens at 390px in one image (read, confirm, book, ask). |

**What the captures cannot show.** The signature interaction is a tap: a coded
row expands to reveal the name and the message (`grid-template-rows: 0fr → 1fr`).
A collapse never hides text from the document — the panel is clipped, never
`opacity: 0` / `visibility: hidden` — so a screen reader, a text search and the
printed page still reach every word. The first row is decoded on load, so the
screen at rest shows one full example.

## Contracts and inputs

- `PRODUCT.md` — the product truth (who the user is, why they pay, the one scene,
  what "wrong" would feel like).
- `.impeccable/surfaces/route-reminders.md` — the direction contract for this surface.
- `.impeccable/surface-brief-reminders.md` — the surface brief.
- `.impeccable/decision/options-bolder.json` — the bolder hand the world was dealt
  from; the locked card is the one marked `assigned`.
- Craft floor: `C:\Users\Raman Tiwari\.config\opencode\skills\impeccable\reference\craft-floor.md`

## Detector state (impeccable detect --json)

Files: `.impeccable/review/detect-desktop.json`, `detect-mobile.json`,
`detect-files.json`. Current state: **no errors**. Remaining warnings, with what
was measured rather than assumed:

- `text-occlusion` ×4 on `/` — **measured false positives.** The file input is
  1×1 at (433,234); the hint it is said to cover sits at (104,305). The select and
  its caption, the code line and the button, likewise do not intersect (checked by
  bounding boxes in the live page). The detector appears to read container/child
  relationships as overlap.
- `side-tab` ×2 — `.mark::before`, the 8px customer hue strip. Deliberate and
  load-bearing: the strip *is* the customer's code on a screen other people can
  see, not decoration on a card. It is extended by the `received` variant
  (hollow outline + strike) so the state never rides on colour alone.
- `low-contrast` ×2 — **static-scan false positive.** These come only from
  `detect-files.json`, which assumes a white background (`#8a8a85` on `#fff` =
  3.5:1). On the app's actual dark ground the same values measure 5.7:1 and 6.9:1,
  and the live URL passes at both viewports report no contrast finding.
- `em-dash-overuse` (advisory) — the copy is written in the voice of a shop
  notice; em dashes are the author's habit and are left in deliberately.

## Honest limits

- **No real user has used this.** No field test happened. `samples/*` are
  synthetic fixtures, and the "shop" is a fixture shop (`Suresh Kirana`).
- **The photo path is wired but unproven on this machine.** No OCR backend is
  installed (Python 3.14 has no wheels for the usual runtimes), and no model lane
  has a key, so an uploaded photo is answered honestly ("nothing on this machine
  could read it — no OCR backend is installed and no model lane has a key") and
  the reviewer is handed the sample page instead. The text-fixture path, the
  parsing, the ledger and the reminder screen are all exercised end to end.
- Language support is template-based for three languages (English, Hindi,
  Marathi — see `udhaar/reminders.py`); only Marathi is exercised in the
  captures. (An earlier draft of this packet said four and named Gujarati; that
  was wrong. Corrected here.)

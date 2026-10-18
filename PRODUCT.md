# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Existing scaffold, chosen at build time rather than specified by the user: FastAPI + Jinja2 templates + SQLite, no JavaScript framework. Phone-first web app with camera capture in the browser. Kept deliberately small so the whole thing can be self-hosted on one cheap machine behind a shop counter. Revisit if the phone ever becomes the only device that exists.

## Users

Neighbourhood shop owner — kirana, medical, or vegetable shop in a tier-2 Indian town. One shared Android phone, a paper khata (udhaar notebook), no laptop at the counter, and possibly not comfortable reading English.

Their job, in their words: know who owes what, and get it back without souring the relationship. It happens at closing time or at month end, on a phone, often on a slow connection.

## Product Purpose

Read a page of the credit notebook the shop already keeps and maintain a running balance per customer, so that credit given stops being credit forgotten. Success is money recovered that would otherwise have been quietly written off — and a ledger that stays a file the shop owns.

## Positioning

The only new step is a photograph of the book the shop already writes in. No new habit, no retyping, no app for the customer to install. Because the intelligence is open-weight and self-hostable, a shop is never renting access to its own ledger — the same page can be read by a model running on a machine it controls, at no per-entry cost.

## Operating Context

- Paper khata, kept in the shop, one page per day or section, mixed Marathi / Hindi / English, rupee amounts, landlord-style shorthand.
- Android phone, mobile browser, patchy signal, camera as the only input device.
- End of day or month end, when attention is short and money is tight.
- The follow-up happens on WhatsApp, where the customer actually is.
- No laptop may be assumed at any point in the flow.

## Capabilities and Constraints

- Accepts a photo page, or a text page for demos with no camera.
- OCR layer is local and optional; the model lane chain is open-weight and swappable by environment variable.
- A human confirms every row before the ledger is written. Non-negotiable.
- Storage is a single SQLite file. No account, no sign-up, no hosted dependency.
- Must run with zero API keys, falling back to a deterministic parser, so any reviewer can click through the whole flow.
- Amounts always come from the ledger, never from a model. A model may only soften reminder wording.
- Open decisions: whether the phone captures while a counter device processes, or the phone does everything; whether a UPI payment link ships; whether an on-device model on a mid-range phone is ever realistic.

## Brand Commitments

Name: **Udhaar Book**. Voice: plain, warm, never accusatory. A reminder is a reminder, not a demand — no fear, no deadlines, no predatory-lending register, in any language.

## Evidence on Hand

- `samples/sample_ledger.txt` — a synthetic fixture for demos. It is **not** a real page and must never be presented as field evidence.
- **No real shop user yet.** Any field test must be genuinely performed and labelled as such; nothing may be invented.
- Absent, and not to be fabricated: real customer data, testimonials, benchmarks, pricing, adoption numbers.

## Product Principles

1. The book they already keep is the interface. Never ask a shopkeeper to change their habit to suit the software.
2. A wrong number is worse than no number — a human confirms before the ledger writes.
3. A customer's name and debt should never require trusting a company.
4. The page must not have to leave the device to be useful.
5. Recover the money without costing the relationship. Language is part of the product, not decoration.

## Accessibility & Inclusion

- Phone-first: 360px is the baseline, not the fallback. Primary action thumb-reachable, camera capture native to the browser.
- Designed for low English literacy: numbers and icons carry the meaning, labels stay short and may be shown bilingually, no idioms.
- Must remain usable on a mid-range Android phone over a slow connection.

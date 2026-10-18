---
name: Udhaar Book
description: A neighbourhood shop's credit book printed as a Factory-era catalogue sleeve — matte black, one white hairline per customer, names coded in hue until decoded on touch, the amount the only headline.
colors:
  sleeve-black: "#0b0b0c"
  catalogue-white: "#f2f2ef"
  structure-red: "#c8102e"
  text-red: "#ff4d63"
  control-amber: "#f5c518"
  link-blue: "#2b6cd4"
  rule-grey: "#3a3a3c"
  hairline-grey: "#242426"
  dim-grey: "#9a9a96"
  faint-grey: "#8a8a85"
  hover-ground: "#121213"
  field-ground: "#131314"
  capture-ground: "#101011"
  paper-white: "#ffffff"
  paper-ink: "#000000"
  paper-dim: "#333333"
typography:
  display:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "clamp(40px, 13vw, 62px)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Rajdhani, Segoe UI Semibold, system-ui, sans-serif"
    fontSize: "26px"
    fontWeight: 600
    letterSpacing: "0.02em"
  amount:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "21px"
    fontWeight: 400
    letterSpacing: "-0.01em"
  figure:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "16px"
    fontWeight: 400
  body:
    fontFamily: "Mukta, Nirmala UI, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Rajdhani, Segoe UI Semibold, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    letterSpacing: "0.14em"
  code:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "11px"
    fontWeight: 500
    letterSpacing: "0.04em"
  lineage:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "11.5px"
    fontWeight: 400
  control-label:
    fontFamily: "Rajdhani, Segoe UI Semibold, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    letterSpacing: "0.16em"
  hint:
    fontFamily: "Mukta, Nirmala UI, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  table:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "14px"
    fontWeight: 400
  reading:
    fontFamily: "Mukta, Nirmala UI, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
  message:
    fontFamily: "Mukta, Nirmala UI, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.75
  entry-number:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "15px"
    fontWeight: 500
  field-value:
    fontFamily: "Spline Sans Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "20px"
    fontWeight: 400
rounded:
  control: "2px"
spacing:
  page-pad: "18px"
  gutter: "20px"
  gap-tight: "8px"
  gap-row: "14px"
  gap-block: "22px"
  gap-section: "26px"
components:
  action-outline:
    backgroundColor: "none"
    textColor: "{colors.catalogue-white}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "52px"
    width: "100%"
  action-outline-hover:
    backgroundColor: "{colors.catalogue-white}"
    textColor: "{colors.sleeve-black}"
  action-outline-small:
    padding: "0 16px"
    height: "44px"
    width: "auto"
  action-outline-disabled:
    backgroundColor: "none"
    textColor: "{colors.faint-grey}"
  action-solid:
    backgroundColor: "{colors.catalogue-white}"
    textColor: "{colors.sleeve-black}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "52px"
  action-solid-hover:
    backgroundColor: "{colors.control-amber}"
    textColor: "{colors.sleeve-black}"
  key:
    backgroundColor: "none"
    textColor: "{colors.dim-grey}"
    rounded: "{rounded.control}"
    size: "44px"
    padding: "0 10px"
  key-active:
    backgroundColor: "{colors.control-amber}"
    textColor: "{colors.sleeve-black}"
  field:
    backgroundColor: "{colors.field-ground}"
    textColor: "{colors.catalogue-white}"
    rounded: "{rounded.control}"
    padding: "12px"
    height: "48px"
  row:
    backgroundColor: "none"
    textColor: "{colors.dim-grey}"
    height: "68px"
  row-hover:
    backgroundColor: "{colors.hover-ground}"
---

# Design System: Udhaar Book

## Overview

**Creative North Star: "The Catalogue"**

A Saville catalogue sleeve: a matte black board with one white hairline plot printed across it, hue strips standing where the names should be, and the amount as the only headline. The sleeve is the whole page — there is no card, no panel, no raised surface anywhere in it. Everything the eye needs is drawn in 1px rules on the black. The world was chosen for a counter that other people can see: a screen facing a shop does not get to print a customer's name by default, so identity is issued as a code and the code is only decoded when someone touches it.

The screen's job supplies its discipline. The shopkeeper's question is "who do I ask tonight, and what do I say to them", never "how much is owed in total" — so the figure is the page's largest type, the sequence runs in the order the money stands, and the message is written in the customer's own language and script. Rate the world by its own promise: strip the copy and it is still recognisable as black field, hairline ruling, one white plot, four columns. Strip the colour and it still reads, because given and received are drawn in the mark's form, not in its hue.

The material is deliberately flat and deliberately printed: no shadow, no gradient, no blur, no illustration, no photograph, no icon font. Two category defaults are rejected by name — the white dashboard ground with stat cards above a table and a blue primary action below, and the warm cream paper ground that finance apps reach for when they want to look human. This system takes the cold sleeve instead, and keeps its affection for the millimetres a customer's colour occupies.

**Key Characteristics:**
- Matte sleeve-black ground (#0b0b0c); nothing sits on it — everything is drawn on it.
- One white hairline plot owns the field on the ask screen; one hairline per customer still to ask.
- Identity is a 26×34px mark built from a 6px hue slab, in one of six hues hashed from the name — and the same mark at 10×44px on the one row whose name is showing.
- State is carried in code as well as colour: a filled slab is credit given, a hollow slab with a struck rule is money received.
- Every rupee figure is Spline Sans Mono with tabular numerals, right-aligned to one shared edge.
- The amount is the only headline; nothing else on a page is allowed that size.
- Collapsed rows are clipped, never hidden — search, screen readers and print still reach every word.
- No cards, no shadows, no elevation; structure is 1px rules and 2px corners.
- Phone-first: 390px is the composition, 44px is the minimum target, and the review grid stacks rather than clips.

## Colors

One black, one white, one structural red, one control amber, one link blue, and a ladder of greys that says how close to the page a thing is.

### Primary
- **Catalogue White** (#f2f2ef): the page's ink. Plot hairlines, the headline figure, row figures, decoded names and body copy on the ask screen all take it. It is the only light allowed to carry a whole screen, and the only colour the plot is drawn in.

### Secondary
- **Structure Crimson** (#c8102e): red as structure — plot crossing ticks, the lane counters, the camera glyph, the underline of the current page. It is never used to set words.
- **Text Red** (#ff4d63): the same red brightened for copy — page codes, red captions, the brand's one tick. Any red small enough to need contrast becomes this one.
- **Control Amber** (#f5c518): the live-control colour — pressed keys, the focus ring, the caret, text selection, the copied confirmation. It marks where the finger is, or what just answered.
- **Link Blue** (#2b6cd4): inline links in prose, and nothing else.

### Neutral
- **Sleeve Black** (#0b0b0c): the ground, and every surface that is not a drawn rule.
- **Hover Ground** (#121213): a row or table line under the pointer.
- **Field Ground** (#131314): input backgrounds and inline `code` chips.
- **Capture Ground** (#101011): the dashed photograph drop.
- **Rule Grey** (#3a3a3c): the 1px rules that structure the page — entry separators, table headers, control borders, input borders.
- **Hairline Grey** (#242426): the faintest dividers — table row rules, the raw-text block, the footer top, the plot's left rail.
- **Dim Grey** (#9a9a96): secondary data — coded row labels, table header caps, pair keys, the received figure.
- **Faint Grey** (#8a8a85): hints, captions, the shop name, placeholders, disabled controls.
- **Paper White (#ffffff), Paper Ink (#000000), Paper Dim (#333333):** the print flattening only. `@media print` turns the sleeve inside out — white ground, black rules and marks, grey for a struck-through received figure — because ink on paper is the one ground this system cannot choose. These three never appear on screen.

A customer's hue is not in this list on purpose. The six identity hues are data, not system colour: `udhaar/plot.py` hashes the customer's name and picks from a fixed set (crimson, amber, blue, green, violet, teal) so the same person is the same colour on every page and in every session. They are recorded in `.impeccable/design.json` under `extensions.identityHues`.

### Named Rules
**The Structural Red Rule.** #c8102e is for structure, never for words: ticks, counters, rules, the camera glyph. Any red that has to be read is #ff4d63. The two are not interchangeable, and the darker one never sets text on the black.

**The Six Hues Rule.** A strip's colour is identity, not state. It says which customer, never what happened — the mark's form carries given and received — so the same hue can sit on a paid row and an unpaid one, and a hue is never spent on decoration, a series, or a legend.

**The Amber-Is-a-Control Rule.** Amber appears only where the finger is or where the page has just answered: the active key, the focus ring, the caret, selection, the copied flash. It is never a headline, a section marker, a badge, or a decorative underline.

## Typography

**Display Font:** Spline Sans Mono (with ui-monospace, Cascadia Mono, Consolas)
**Body Font:** Mukta (with Nirmala UI, system-ui)
**Label Font:** Rajdhani (with Segoe UI Semibold, system-ui; self-hosted, vendored in `static/fonts/`)

**Character:** Two voices that are not allowed to swap. Rajdhani is the shop's engraved nameplate — narrow, tracked, at label scale; in sentence case when it has to speak as a heading. Spline Sans Mono is the arithmetic: every figure, page code and field value is tabular mono, so columns compare without a legend. Mukta is the human voice — prose, hints, and the reminder message — and the only face asked to set Devanagari at reading size.

### Hierarchy
- **Display** (400, clamp(40px, 13vw, 62px), line-height 1, −0.02em): the total outstanding. The page's largest type, right-aligned to the same edge as every figure below it, and the only thing on the ask screen allowed to be a headline.
- **Amount** (400, 21px, −0.01em): the row figure in the sequence. The `₹` rides smaller (15px) and fainter, so the number is what gets read.
- **Headline** (600, 24–26px, 0.02em): page titles in Rajdhani, sentence case — "Read one page of the book", "The book".
- **Body** (400, 16px, 1.55): Mukta for prose and hints. The reminder message is set 16px/1.6 and capped at 34ch, stepping to 17px/1.75 for Devanagari so Marathi and Hindi read at the same size as Latin.
- **Figure** (400, 16px, tabular numerals): pair values and field text. Table numerals take the table's own 14px step and page codes 11px, all in the same mono.
- **Label** (600, 11px, 0.14em, uppercase): the tracked-caps voice — field captions, table headers, key faces, nav, controls. Across those ranks it flexes 0.10–0.16em and 11–14px, which is the whole of the scale.

### Named Rules
**The Figure Rule.** Every rupee figure is Spline Sans Mono with tabular numerals, and every figure on a page shares one right edge. No figure is set in Mukta and no prose in mono; the two voices do not swap. The rupee sign is the one character outside the face's coverage — measured, it resolves to the system mono — so the mark is allowed to come from the platform while the digits, separators and tabular alignment stay in the figure face.

**The Caps-Are-Labels Rule.** Uppercase Rajdhani belongs to labels — captions, table headers, key faces, nav, controls — at 11–14px with 0.10–0.16em of tracking. Anything that has to speak at heading scale is the same face in sentence case.

## Layout

One centred column, 760px maximum, 18px of page padding, under a 56px sticky topbar ruled along its bottom edge. The rhythm is a page of blocks separated by air and hairline: 8px inside a group, 14px between the columns of a row, 22px between blocks, 26px between sections, and the sequence ruled top and bottom. Nothing is a container: the ask screen is a single column of ruled rows all the way down, so a wider viewport only adds margin.

The phone is the baseline, not the fallback. At ≤560px the brand's shop name drops, table padding tightens, the page-code column collapses, and the sequence grid narrows from `44px 6px 1fr auto` to `38px 6px 1fr auto`. The review grid is `table-layout: fixed` with declared column widths (21%, 96px, 176px, 26%, 88px, 52px) because a clipped money field is a wrong money field; at ≤640px it stacks, every field keeping its `data-label` caption and every control at 44px. The primary action stops stretching at ≥600px (max-width 420px) — it stops being a bar once there is room to be a button.

Measure is capped by role rather than by container: 34ch for the reminder message, 40ch for the plot legend, 46ch for an empty-state paragraph, 60ch for hints, 62ch for callouts.

### Named Rules
**The One Right Edge Rule.** Every figure on a page — the total, the row amounts, the given/paid/balance columns, the pair values — right-aligns to one edge, so magnitudes compare without a legend or a chart.

**The Phone-Is-the-Baseline Rule.** 390px is the composition, not the compression: 18px page padding, 44px minimum target, 48px fields, 52px primary action inside thumb reach. A layout that only works because the phone was an afterthought is wrong.

## Elevation & Depth

This system has no shadows and no elevation, and it is not flat-with-shadows — it is flat. Depth is drawn instead: a 1px rule separates, a hairline suggests, and the closest thing to a surface change is a two-value shift of near-black — the hover ground (#121213) on a row or table line, the field ground (#131314) inside an input, the capture ground (#101011) behind the dashed drop. Nothing floats: across the four screens there is no card, panel, modal, tooltip, or sticky element other than the topbar.

The single `box-shadow` in the stylesheet is a 2px inset red underline marking the current page in the topbar — an underline drawn with the shadow property, never depth. In the plot, hairlines are protected from scale with `vector-effect: non-scaling-stroke`, and the band's height is fixed in pixels and capped at 118px, so a hairline is exactly 1px on a phone, on a desk, and on paper — and a shop with forty dues still shows its total and its first message above the fold. Past eighteen lines the remainder is drawn as one dashed hairline, never dropped.

### Shadow Vocabulary
- **current-page-underline** (`box-shadow: inset 0 -2px 0 0 #c8102e`): the only shadow token in the system; a 2px inset underline on the active topbar link.

### Named Rules
**The No-Elevation Rule.** No shadow, no glow, no blur, no gradient, no raised surface. If something must separate, draw a 1px rule; if something must respond, shift two greys.

## Shapes

Rectangles, ruled. Corners stop at 2px — controls, fields, keys, callouts and the capture drop all take the same barely-there radius, and nothing in the system is a pill. Form is otherwise drawn from the smallest possible geometry: 1px rules spanning the column, a 6px × 34px hue slab (10px × 44px on the decoded row), a 26px × 34px mark, a 16px × 1px strike, a 10px tick at 1.5 stroke.

Icons are authored SVG at one stroke: 15px in buttons, 20px in the brand, 30px for the camera over the capture drop, 1.4–1.6 stroke, `fill: none`, `currentColor` — a camera, a copy square, a WhatsApp ring, an arrow, a plus, a cross. The disclosure chevron is drawn too: an 8px square of two 1.5px borders rotated 45°, flipping to −135° when open. No glyph, no dingbat, no icon font, no emoji, anywhere.

The mark is the world's geometry in miniature: a solid slab when credit was given, the same slab hollowed to a 1px outline with a rule struck across it when money came back. Greyscale, print and glare all still read it, because the difference is a drawn form rather than a colour.

### Named Rules
**The Two-Pixel Corner Rule.** Corners stay at 2px. Nothing is a pill, nothing is a rounded card, nothing is a circle — the camera lens is a drawn path inside a drawn glyph, not a radius.

**The Drawn-Affordance Rule.** Every affordance is geometry, not a character: chevrons are borders, icons are inline SVG on a 24-unit grid at 1.4–1.6 stroke, and no Unicode glyph, emoji or dingbat stands in for a drawn mark.

## Components

### The Customer Mark (signature)
- **Shape:** 26 × 34px, drawn from a 6px slab — the contract's mass, held at rest; 22px tall where it sits inline in a table row, and 10 × 44px on the one row whose name is showing, so identity gains weight exactly where it is revealed.
- **Credit given:** the slab filled in the customer's hue (`--strip`, set inline from `plot.strip_for(name_key)`).
- **Money received:** the same slab hollowed to a 1px outline, with a 16px × 1px rule struck across its middle and overhanging 3px on each side.
- **Rule:** direction never rides on colour alone — the form carries given/received, so greyscale, colour-blindness and print all survive.
- **On the ledger:** inline in the customer column, marked `aria-hidden`, with the name beside it — the book is read by the shop, not by the counter.

### The Decode (signature)
- **Trigger:** the whole row is a button — minimum 68px tall, grid `44px 6px 1fr auto`, dropping to `38px 6px 1fr auto` under 560px, 44px targets everywhere.
- **At rest:** the entry number at 11px mono in Text Red — the catalogue code, 01 upward in the order to ask · the hue mark · nothing where the name goes · the amount right-set in mono. The row's accessible name carries the figure ("Entry 03, ₹300 outstanding. Show the name and the message.").
- **Opening:** `grid-template-rows` from `0fr` to `1fr` over 460ms on `cubic-bezier(0.16, 1, 0.3, 1)`; the panel's inner block lifts from −4px to none over 320ms with an 80ms delay. Nothing else on the page moves except the devices that commit: the entry number steps to 15px and the mark to 10 × 44px.
- **Content:** the lineage line in 11.5px mono (`Page 1 · 1 line · last 15/10 · ₹560 given`), the reminder in Mukta at reading size, then one solid full-width Copy action and a quiet text-link WhatsApp handoff beneath it, with a sentence of explanation under both.
- **Ground truth:** a closed panel is clipped by an `overflow: hidden` wrapper inside the collapsible row — never `opacity: 0`, never `visibility: hidden` — so a text search, a screen reader and the printed page still reach every word (`@media print` forces every panel open). Its buttons, though, are `inert` while the panel is closed, so fourteen invisible controls never sit in the tab order.
- **State:** `aria-expanded` on the row and `aria-controls` to the panel; the first row ships decoded so the mechanism is visible without a tap, and Reveal opens every row at once for when the shop is empty.

### Buttons
- **Shape:** 2px corners, a 1px hairline border, a caps label at 0.16em, an optional 15px drawn icon.
- **Primary (`.act.solid`):** Catalogue White ground, sleeve-black text, 52px tall, full width up to 420px; hover flips to amber. A decoded row has exactly one — Copy.
- **Secondary (`.act`):** transparent with a white hairline; hover inverts to white ground with black text. `.act.small` returns to auto width, 16px padding, 44px height.
- **Quiet (`.tools .quiet`):** a caps text link on a 1px Rule Grey bottom border, 44px tall, Dim Grey lifting to white on hover — the WhatsApp handoff, ranked under the one primary action rather than beside it.
- **Disabled:** faint-grey text on a Rule Grey border, no ground, not-allowed cursor.
- **Icons:** 15px inline SVG, `stroke: currentColor`, drawn beside the label and never alone.

### Keys (the small square control)
- **Style:** 44 × 44px minimum, 2px corners, a Rule Grey hairline, 11px caps in Dim Grey — the three language keys and the Reveal/Conceal toggle.
- **Active / pressed:** amber ground with black text, on `aria-pressed="true"`; the only filled key on the screen.

### Fields
- **Style:** mono 16px text on the field ground (#131314), a Rule Grey hairline, 2px corners, 12px padding, 48px minimum height, amber caret, faint placeholder.
- **Hover:** the border lifts to Faint Grey. **Focus:** the global amber ring — 2px, 2px offset.
- **Number fields:** spinners removed; a money field is typed, not nudged by accident.

### Tables
- **Header:** 11px Rajdhani caps at 0.12em, ruled below in Rule Grey.
- **Rows:** Hairline Grey rules between, no vertical rules, no zebra; hover darkens the whole line to #121213.
- **Numerals:** mono, right-aligned; a cleared balance drops to Dim Grey so an outstanding figure and a settled one are distinguishable without colour.
- **Review grid:** fixed columns; at ≤640px each row becomes a labelled block via `data-label` captions, nothing clipped.

### Navigation
- **Style:** a 56px sticky topbar ruled below in Rule Grey. The brand is a drawn glyph (three rules and one red tick) plus Rajdhani 700 caps at 0.16em, with the shop's name in 11px Faint Grey caps — dropped under 560px.
- **Items:** caps at 11px in Dim Grey, 44px targets; hover to white; the current page takes the 2px inset red underline.

### Data rows and callouts
- **Pair rows:** key in 12px caps Dim Grey, value in 16px mono, separated by hairlines rather than boxed.
- **Callout:** a top rule only — amber for a notice, red for a stop — with the body in Dim Grey capped at 62ch. The system never draws a side accent.

### Plot band (signature)
- **Geometry:** inline SVG, `viewBox 0 0 700 {height}`, `preserveAspectRatio="none"`, height fixed in pixels and capped at 118px (12px rows from a 6px top, compressing to 4px before anything is dropped) so the band is the same physical height on a phone as on a desk; `vector-effect: non-scaling-stroke` keeps every line exactly 1px.
- **Per customer:** one white hairline whose length carries the balance (minimum 8px, so a small debt is still a line), the selected line at 2.5 weight, and a 10px red tick at 1.5 stroke where a customer both owes and has paid — placed where the return meets the advance.
- **The remainder:** past eighteen customers the rest are drawn as one dashed hairline (2px dash, 4px gap) standing for everyone else added together; the count above the band still names the true total, and the SVG's accessible label says what the dashed line is.
- **Key:** "8 still to ask" in caps, the legend in sentence case at 13px and 40ch, the language keys pushed right on the same line.

### Named Rules
**The Clip-Not-Hide Rule.** When a panel closes, its words stay in the document: collapse by clipping — an `overflow: hidden` wrapper inside a `0fr` row — never `opacity: 0`, `visibility: hidden` or `display: none` on the panel's text. Search, screen readers, and print all reach a row nobody has opened.

**The First Row Decoded Rule.** Any screen that ships a sequence of coded rows arrives with its first row decoded. The mechanism is shown, not explained.

## Do's and Don'ts

### Do:
- **Do** draw structure with 1px rules — Rule Grey (#3a3a3c) to separate, Hairline Grey (#242426) to whisper — and let the black ground show through everywhere else.
- **Do** put every rupee figure in Spline Sans Mono with tabular numerals on the page's one right edge.
- **Do** carry state in form as well as colour: filled slab versus hollow-and-struck, figure plain versus figure struck through.
- **Do** keep targets at 44px minimum, the primary action at 52px, fields at 48px, and page padding at 18px.
- **Do** use Structure Crimson (#c8102e) for structure and Text Red (#ff4d63) whenever red must be read.
- **Do** ship the first row decoded, and give every disclosure a drawn chevron and a 44px target.
- **Do** keep the reminder message at 34ch and step Devanagari to 17px/1.75.

### Don't:
- **Don't** add a card, a shadow, a glow, or a raised surface: depth is at most a two-grey value shift (#121213, #131314, #101011).
- **Don't** put a customer's name into a closed row's visible text — it carries the page code, the hue mark, the line count and the figure, and the name arrives through the decode.
- **Don't** spend amber on anything but a live control, focus, selection, or a confirmation.
- **Don't** swap the two voices: no figures in Mukta, no prose in mono.
- **Don't** round a corner past 2px, and don't draw a pill.
- **Don't** use a glyph, emoji, dingbat or icon font where a drawn mark belongs.
- **Don't** invent a new grey or a new red; the surface ladder and the two reds are closed sets.
- **Don't** let a table clip or scroll sideways — on the phone the review grid stacks with its labels instead.

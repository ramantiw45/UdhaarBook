"""The plot, and the hue strip that stands in for a name.

Two jobs, both about not putting a customer's name on a screen that faces a
shop counter:

* ``strip_for`` gives a customer a stable hue, derived from the name, so the
  same person is the same colour on every page and in every session — and the
  colour means nothing to anyone who has not been told.
* ``plot_rows`` lays out the field: one white hairline per customer still to be
  asked, its length carrying the amount, with a red crossing tick where that
  customer both owes money and has already paid some of it back.

The tick is the honest part. A single number hides the customer who borrowed
₹5,000 and returned ₹4,900 — they look nearly as bad as someone who never paid.
"""

from __future__ import annotations

import hashlib

# Hues that survive on a matte black field and stay identifiable in greyscale
# by their luminance order.
HUES = (
    "#c8102e",  # crimson
    "#f5c518",  # amber
    "#2b6cd4",  # blue
    "#6aa84f",  # green
    "#a15ee0",  # violet
    "#2aa8a0",  # teal
)


def strip_for(name_key: str) -> str:
    """A stable hue for a customer. Same name, same colour, always."""
    digest = hashlib.sha1(name_key.encode("utf-8")).digest()
    return HUES[digest[0] % len(HUES)]


def plot_rows(
    balances: list[dict],
    width: int = 700,
    top: int = 6,
    max_rows: int = 18,
    max_height: int = 118,
) -> dict:
    """Geometry for the plot band. Pure numbers, rendered as inline SVG.

    The band has a hard ceiling. The first viewport has to hold the total, the
    pre-decoded row and its Copy action on a 390x844 phone, and a shop with
    forty dues would otherwise push all three below the fold. Past ``max_rows``
    the remainder becomes one dashed hairline standing for everyone else, so the
    band never withholds what it is not drawing.
    """
    pending = [b for b in balances if b["balance"] > 0]
    if not pending:
        return {"width": width, "height": 0, "rows": [], "rest": 0}

    peak = max(b["balance"] for b in pending)
    usable = width - 2  # keep the longest line off the right edge

    shown = pending[:max_rows]
    rest = pending[max_rows:]
    slots = len(shown) + (1 if rest else 0)
    row_height = max(4, min(12, (max_height - top - 4) // max(slots, 1)))

    rows = []
    for index, item in enumerate(shown):
        length = max(8, round(item["balance"] / peak * usable))
        crossing = None
        if item["received"] > 0 and item["given"] > 0:
            # Where the money returned meets the money given.
            crossing = max(6, min(length - 2, round(length * item["received"] / item["given"])))
        rows.append(
            {
                "y": top + index * row_height,
                "length": length,
                "crossing": crossing,
                "selected": index == 0,
                "rest": False,
                "name": item["name"],
                "balance": item["balance"],
                "given": item["given"],
                "received": item["received"],
            }
        )

    if rest:
        rows.append(
            {
                "y": top + len(shown) * row_height,
                "length": usable,
                "crossing": None,
                "selected": False,
                "rest": True,
                "name": f"{len(rest)} more",
                "balance": sum(b["balance"] for b in rest),
                "given": sum(b["given"] for b in rest),
                "received": sum(b["received"] for b in rest),
            }
        )

    return {"width": width, "height": top + slots * row_height + 4, "rows": rows, "rest": len(rest)}

"""Udhaar Book — turn a shop's handwritten credit notebook into balances.

Layers, top to bottom:

* ``udhaar.ocr``       — reads the page locally, on CPU, with no network.
* ``udhaar.llm``       — structures the text (or the image) into rows, on a
                         lane chain of open-weight models.
* ``udhaar.ledger``    — SQLite: what is owed, by whom.
* ``udhaar.reminders`` — writes the polite nudge, in the customer's language.
"""

__version__ = "0.1.0"

"""Write the nudge — in the customer's language, without the guilt trip.

A shopkeeper who chases money badly loses the customer. The templates are
deliberately plain and the model, when one is available, is only allowed to
soften them, never to invent a figure.
"""

from __future__ import annotations

import os

LANGS = {
    "en": "English",
    "hi": "हिंदी",
    "mr": "मराठी",
}

# Short key labels, in the language's own script.
LANGS_SHORT = {
    "en": "EN",
    "hi": "हिं",
    "mr": "मर",
}

_TEMPLATES: dict[str, str] = {
    "en": (
        "Namaste {name} ji, this is {shop}. "
        "Small reminder — {balance} is pending in your khata as of today. "
        "No rush at all; send it whenever it is easy, or tell me a date that suits you. "
        "Thank you, {shop}."
    ),
    "hi": (
        "नमस्ते {name} जी, {shop} से। "
        "आपके खाते में आज {balance} बाकी है — छोटी सी याद दिला रहा हूँ। "
        "कोई जल्दी नहीं, जब सुविधा हो तब भेज दीजिए, या कोई तारीख बता दीजिए। "
        "धन्यवाद, {shop}।"
    ),
    "mr": (
        "नमस्कार {name} जी, {shop} मधून. "
        "तुमच्या खात्यात आज {balance} बाकी आहे — फक्त आठवण. "
        "घाई अजिबात नाही; सोयीचे असेल तेव्हा पाठवा, किंवा तारीख सांगा. "
        "धन्यवाद, {shop}."
    ),
}

PAISE_PER_RUPEE = 100


def format_amount(value: float, lang: str = "en") -> str:
    """₹1,234 and ₹1,234.50 — no trailing .00 noise."""
    if abs(value - round(value)) < 0.005:
        body = f"{int(round(value)):,}"
    else:
        body = f"{value:,.2f}"
    return f"₹{body}"


def shop_name() -> str:
    return os.getenv("SHOP_NAME", "your shop").strip() or "your shop"


def shop_lang() -> str:
    lang = os.getenv("SHOP_LANG", "en").strip().lower()
    return lang if lang in _TEMPLATES else "en"


def build_reminder(name: str, balance: float, lang: str | None = None) -> str:
    """A ready-to-paste WhatsApp message. Balance must be positive."""
    lang = (lang or shop_lang()).lower()
    if lang not in _TEMPLATES:
        lang = "en"
    return _TEMPLATES[lang].format(
        name=name.strip() or "customer",
        shop=shop_name(),
        balance=format_amount(balance, lang),
    )


def payment_link_hint(balance: float) -> str:
    """What a real deployment would add next. Kept explicit, not faked."""
    return (
        f"Next step for a real shop: attach a UPI request for "
        f"{format_amount(balance)} so the customer can pay in one tap."
    )

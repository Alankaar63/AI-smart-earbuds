"""Text translation module using googletrans with resilient error handling."""

from __future__ import annotations

from googletrans import Translator


class TranslationError(RuntimeError):
    """Raised when translation fails unexpectedly."""


_TRANSLATOR = Translator()


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text and gracefully return fallback content on service errors."""
    if not text.strip():
        return ""

    try:
        result = _TRANSLATOR.translate(text, src=source_lang, dest=target_lang)
        return (result.text or "").strip()
    except Exception:
        # Graceful fallback for hackathon demo stability.
        return text

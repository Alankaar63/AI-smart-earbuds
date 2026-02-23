"""Text-to-speech service wrapper around pyttsx3."""

from __future__ import annotations

import threading

import pyttsx3


class TextToSpeechError(RuntimeError):
    """Raised when TTS synthesis/playback fails."""


def _configure_engine(
    engine: pyttsx3.Engine,
    rate: int,
    volume: float,
    voice_id: str = "",
) -> None:
    """Apply runtime TTS engine settings."""
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    if voice_id:
        engine.setProperty("voice", voice_id)


def _speak(text: str, rate: int, volume: float, voice_id: str) -> None:
    """Internal blocking speech runner."""
    try:
        engine = pyttsx3.init()
        _configure_engine(engine, rate=rate, volume=volume, voice_id=voice_id)
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        raise TextToSpeechError(f"TTS failed: {exc}") from exc


def speak_text(
    text: str,
    rate: int,
    volume: float,
    voice_id: str = "",
    non_blocking: bool = True,
) -> None:
    """Speak translated text through speaker; optionally in background thread."""
    if not text.strip():
        return

    if non_blocking:
        thread = threading.Thread(
            target=_speak,
            args=(text, rate, volume, voice_id),
            daemon=True,
            name="tts-thread",
        )
        thread.start()
        return

    _speak(text, rate, volume, voice_id)

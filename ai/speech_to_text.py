"""Speech-to-text service powered by faster-whisper with singleton model loading."""

from __future__ import annotations

from pathlib import Path
from threading import Lock

from faster_whisper import WhisperModel


class SpeechToTextError(RuntimeError):
    """Raised when transcription fails."""


_MODEL_INSTANCE: WhisperModel | None = None
_MODEL_SIGNATURE: tuple[str, str, str] | None = None
_MODEL_LOCK = Lock()


def _get_whisper_model(model_size: str, device: str, compute_type: str) -> WhisperModel:
    """Return global Whisper model, loading once per configuration signature."""
    global _MODEL_INSTANCE
    global _MODEL_SIGNATURE

    signature = (model_size, device, compute_type)

    with _MODEL_LOCK:
        if _MODEL_INSTANCE is None or _MODEL_SIGNATURE != signature:
            _MODEL_INSTANCE = WhisperModel(model_size, device=device, compute_type=compute_type)
            _MODEL_SIGNATURE = signature

    return _MODEL_INSTANCE


def transcribe_audio(
    audio_path: Path,
    model_size: str,
    device: str,
    compute_type: str,
    beam_size: int,
) -> str:
    """Transcribe a WAV file and return the joined text output."""
    if not audio_path.exists():
        raise SpeechToTextError(f"Transcription input file not found: {audio_path}")

    model = _get_whisper_model(model_size=model_size, device=device, compute_type=compute_type)

    try:
        segments, _ = model.transcribe(str(audio_path), beam_size=beam_size)
        text = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        raise SpeechToTextError(f"Whisper transcription failed: {exc}") from exc

    return text

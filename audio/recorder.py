"""Audio recording module for capturing mono 16-bit PCM WAV input."""

from __future__ import annotations

from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write


class AudioRecordingError(RuntimeError):
    """Raised when microphone recording fails."""


def record_audio(
    output_path: Path,
    sample_rate: int,
    channels: int,
    dtype: str,
    duration_s: int,
) -> Path:
    """Record microphone input and persist to a WAV file.

    Args:
        output_path: Destination WAV path.
        sample_rate: Recording sample rate (Hz).
        channels: Number of channels, should be 1 for mono.
        dtype: PCM data type, expected int16.
        duration_s: Recording duration in seconds.

    Returns:
        Path to the recorded WAV file.

    Raises:
        AudioRecordingError: On missing/invalid input device or PortAudio errors.
    """
    if duration_s <= 0:
        raise AudioRecordingError("Recording duration must be > 0 seconds")

    try:
        device_info = sd.query_devices(kind="input")
    except Exception as exc:  # broad by design for driver/backend issues
        raise AudioRecordingError(
            "No usable microphone input device found. Connect a microphone and retry."
        ) from exc

    max_channels = int(device_info.get("max_input_channels", 0))
    if max_channels < channels:
        raise AudioRecordingError(
            f"Input device does not support {channels} channel(s); max is {max_channels}"
        )

    frames = int(duration_s * sample_rate)

    try:
        audio = sd.rec(frames, samplerate=sample_rate, channels=channels, dtype=dtype)
        sd.wait()
    except Exception as exc:
        raise AudioRecordingError(f"Microphone capture failed: {exc}") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write(str(output_path), sample_rate, audio)
    return output_path

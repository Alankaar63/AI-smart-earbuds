"""RNNoise-based denoising utilities using ffmpeg and rnnoise_demo subprocesses."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Sequence


class NoiseReductionError(RuntimeError):
    """Raised when audio denoising pipeline fails."""


def _run_command(cmd: Sequence[str], stage: str) -> None:
    """Run command and raise a detailed error on failure."""
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise NoiseReductionError(f"Missing executable during {stage}: {cmd[0]}") from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr if stderr else stdout
        raise NoiseReductionError(f"{stage} failed (exit={result.returncode}): {detail}")


def _ensure_executable(path: Path, label: str) -> None:
    """Ensure an executable file exists and has execute permission."""
    if not path.exists():
        raise NoiseReductionError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise NoiseReductionError(f"{label} is not a file: {path}")
    if not path.stat().st_mode & 0o111:
        raise NoiseReductionError(f"{label} is not executable: {path}")


def denoise_with_rnnoise(
    input_wav: Path,
    rnnoise_binary: Path,
    ffmpeg_bin: str,
    input_raw_48k: Path,
    output_raw_48k: Path,
    output_wav_48k: Path,
    output_wav_16k: Path,
) -> Path:
    """Run full denoising pipeline and return denoised 16k WAV path.

    Pipeline:
    1. WAV -> 48k mono s16le raw PCM
    2. RNNoise denoise raw -> raw
    3. raw -> 48k WAV
    4. 48k WAV -> 16k WAV for Whisper
    """
    if not input_wav.exists():
        raise NoiseReductionError(f"Input WAV not found: {input_wav}")

    if shutil.which(ffmpeg_bin) is None:
        raise NoiseReductionError(
            f"ffmpeg executable '{ffmpeg_bin}' not found in PATH. Install ffmpeg first."
        )

    _ensure_executable(rnnoise_binary, "RNNoise binary")

    for path in (input_raw_48k, output_raw_48k, output_wav_48k, output_wav_16k):
        path.parent.mkdir(parents=True, exist_ok=True)

    # Convert microphone WAV to RNNoise input format (mono 48k s16le raw).
    _run_command(
        [
            ffmpeg_bin,
            "-y",
            "-i",
            str(input_wav),
            "-ac",
            "1",
            "-ar",
            "48000",
            "-f",
            "s16le",
            str(input_raw_48k),
        ],
        stage="WAV->RAW conversion",
    )

    # Execute RNNoise denoiser.
    _run_command(
        [str(rnnoise_binary), str(input_raw_48k), str(output_raw_48k)],
        stage="RNNoise denoising",
    )

    # Convert denoised raw back to WAV at 48k.
    _run_command(
        [
            ffmpeg_bin,
            "-y",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-ac",
            "1",
            "-i",
            str(output_raw_48k),
            str(output_wav_48k),
        ],
        stage="RAW->WAV conversion",
    )

    # Resample final audio to 16k mono for Whisper.
    _run_command(
        [
            ffmpeg_bin,
            "-y",
            "-i",
            str(output_wav_48k),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(output_wav_16k),
        ],
        stage="48k->16k resample",
    )

    return output_wav_16k

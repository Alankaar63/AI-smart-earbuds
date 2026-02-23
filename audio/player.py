"""Optional local audio playback utilities."""

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path


class AudioPlaybackError(RuntimeError):
    """Raised when local playback command fails."""


def play_wav_file(file_path: Path) -> None:
    """Play a WAV file using OS tools.

    macOS: afplay
    Linux: aplay (ALSA)
    """
    if not file_path.exists():
        raise AudioPlaybackError(f"Playback file not found: {file_path}")

    system_name = platform.system().lower()

    if "darwin" in system_name:
        player = shutil.which("afplay")
        cmd = [player, str(file_path)] if player else None
    elif "linux" in system_name:
        player = shutil.which("aplay")
        cmd = [player, str(file_path)] if player else None
    else:
        cmd = None

    if not cmd:
        raise AudioPlaybackError(
            "No supported CLI player found. Install 'afplay' (macOS) or 'aplay' (Linux)."
        )

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise AudioPlaybackError(result.stderr.strip() or "Audio playback failed")

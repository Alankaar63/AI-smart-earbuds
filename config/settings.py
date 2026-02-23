"""Application configuration loader for the smart earphone translator pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class AppConfig:
    """Top-level app file path configuration."""

    temp_dir: Path
    input_wav: Path
    rnnoise_input_raw: Path
    rnnoise_output_raw: Path
    denoised_wav_48k: Path
    whisper_wav_16k: Path


@dataclass(frozen=True)
class AudioConfig:
    """Audio recording configuration."""

    sample_rate_record: int
    channels: int
    dtype: str
    record_seconds: int


@dataclass(frozen=True)
class RNNoiseConfig:
    """RNNoise and ffmpeg runtime configuration."""

    binary_path: Path
    ffmpeg_bin: str


@dataclass(frozen=True)
class WhisperConfig:
    """Whisper inference configuration."""

    model_size: str
    device: str
    compute_type: str
    beam_size: int


@dataclass(frozen=True)
class TranslationConfig:
    """Translation configuration."""

    default_target_lang: str
    source_lang: str


@dataclass(frozen=True)
class TTSConfig:
    """Text-to-speech configuration."""

    rate: int
    volume: float
    voice_id: str
    non_blocking: bool


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime toggles and display options."""

    print_cpu_usage: bool
    realtime_mode: bool


@dataclass(frozen=True)
class Settings:
    """Combined settings object for all modules."""

    app: AppConfig
    audio: AudioConfig
    rnnoise: RNNoiseConfig
    whisper: WhisperConfig
    translation: TranslationConfig
    tts: TTSConfig
    runtime: RuntimeConfig


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "settings.yaml"


def _read_yaml(path: Path) -> Dict[str, Any]:
    """Read and parse a YAML config file into a dict."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file) or {}
    if not isinstance(content, dict):
        raise ValueError(f"Invalid YAML structure in {path}; expected top-level mapping")
    return content


def load_settings(config_path: str | Path | None = None) -> Settings:
    """Load settings from YAML and resolve relative paths from project root."""
    cfg_path = Path(config_path).expanduser().resolve() if config_path else DEFAULT_CONFIG_PATH
    data = _read_yaml(cfg_path)

    project_root = cfg_path.parent.parent
    app_raw = data["app"]

    temp_dir = (project_root / app_raw["temp_dir"]).resolve()

    app_cfg = AppConfig(
        temp_dir=temp_dir,
        input_wav=temp_dir / app_raw["input_wav"],
        rnnoise_input_raw=temp_dir / app_raw["rnnoise_input_raw"],
        rnnoise_output_raw=temp_dir / app_raw["rnnoise_output_raw"],
        denoised_wav_48k=temp_dir / app_raw["denoised_wav_48k"],
        whisper_wav_16k=temp_dir / app_raw["whisper_wav_16k"],
    )

    rnnoise_binary = Path(data["rnnoise"]["binary_path"])
    if not rnnoise_binary.is_absolute():
        rnnoise_binary = (project_root / rnnoise_binary).resolve()

    return Settings(
        app=app_cfg,
        audio=AudioConfig(**data["audio"]),
        rnnoise=RNNoiseConfig(binary_path=rnnoise_binary, ffmpeg_bin=data["rnnoise"]["ffmpeg_bin"]),
        whisper=WhisperConfig(**data["whisper"]),
        translation=TranslationConfig(**data["translation"]),
        tts=TTSConfig(**data["tts"]),
        runtime=RuntimeConfig(**data["runtime"]),
    )

"""Smart Earphone Translation System.

Pipeline:
1) Record microphone audio (16k mono WAV)
2) Denoise with RNNoise
3) Transcribe with Whisper
4) Translate text
5) Speak translated text
6) Print timings + CPU metrics
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai.speech_to_text import SpeechToTextError, transcribe_audio
from ai.text_to_speech import TextToSpeechError, speak_text
from ai.translator import translate_text
from audio.noise_reduction import NoiseReductionError, denoise_with_rnnoise
from audio.recorder import AudioRecordingError, record_audio
from config.settings import Settings, load_settings
from utils.logger import setup_logger
from utils.metrics import StageMetrics, get_cpu_percent, timed_stage


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for runtime overrides."""
    parser = argparse.ArgumentParser(description="AI-driven smart earphone translation pipeline")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config file")
    parser.add_argument("--duration", type=int, default=None, help="Recording duration in seconds")
    parser.add_argument(
        "--target-lang",
        type=str,
        default=None,
        help="Translation target language code (example: es, fr, hi, de)",
    )
    parser.add_argument(
        "--realtime-mode",
        choices=["on", "off"],
        default=None,
        help="Toggle placeholder real-time mode (future streaming support)",
    )
    return parser.parse_args()


def resolve_runtime_target_language(cli_lang: str | None, settings: Settings) -> str:
    """Resolve target language using CLI override or interactive input."""
    if cli_lang:
        return cli_lang.strip().lower()

    user_input = input(
        f"Enter target language code [default={settings.translation.default_target_lang}]: "
    ).strip()

    if not user_input:
        return settings.translation.default_target_lang
    return user_input.lower()


def resolve_realtime_mode(cli_mode: str | None, settings: Settings) -> bool:
    """Resolve real-time mode using CLI override or interactive prompt."""
    if cli_mode is not None:
        return cli_mode == "on"

    user_input = input(
        f"Enable real-time mode placeholder? (y/N) [default={settings.runtime.realtime_mode}]: "
    ).strip().lower()

    if not user_input:
        return settings.runtime.realtime_mode

    return user_input in {"y", "yes", "true", "1"}


def ensure_temp_dir(path: Path, logger) -> None:
    """Ensure temp directory exists and is writable."""
    if not path.exists():
        logger.warning("Temp directory missing. Creating: %s", path)
        path.mkdir(parents=True, exist_ok=True)

    if not path.is_dir():
        raise RuntimeError(f"Temp path exists but is not a directory: {path}")


def run_pipeline(
    settings: Settings,
    record_seconds: int,
    target_lang: str,
    realtime_mode: bool,
) -> int:
    """Run full translation pipeline and return process exit code."""
    logger = setup_logger()
    metrics = StageMetrics(timings={})

    logger.info("Starting smart earphone translation pipeline")
    logger.info("Real-time mode: %s", "ON (placeholder)" if realtime_mode else "OFF")
    logger.info("Target language: %s", target_lang)

    if realtime_mode:
        logger.info("Streaming is not implemented yet. Running single-shot mode.")

    try:
        ensure_temp_dir(settings.app.temp_dir, logger)

        if settings.runtime.print_cpu_usage:
            logger.info("CPU usage before pipeline: %.1f%%", get_cpu_percent())

        with timed_stage(metrics, "recording"):
            record_audio(
                output_path=settings.app.input_wav,
                sample_rate=settings.audio.sample_rate_record,
                channels=settings.audio.channels,
                dtype=settings.audio.dtype,
                duration_s=record_seconds,
            )

        with timed_stage(metrics, "noise reduction"):
            denoised_16k = denoise_with_rnnoise(
                input_wav=settings.app.input_wav,
                rnnoise_binary=settings.rnnoise.binary_path,
                ffmpeg_bin=settings.rnnoise.ffmpeg_bin,
                input_raw_48k=settings.app.rnnoise_input_raw,
                output_raw_48k=settings.app.rnnoise_output_raw,
                output_wav_48k=settings.app.denoised_wav_48k,
                output_wav_16k=settings.app.whisper_wav_16k,
            )

        with timed_stage(metrics, "transcription"):
            transcript = transcribe_audio(
                audio_path=denoised_16k,
                model_size=settings.whisper.model_size,
                device=settings.whisper.device,
                compute_type=settings.whisper.compute_type,
                beam_size=settings.whisper.beam_size,
            )

        if not transcript:
            logger.error("Empty transcription result. Nothing to translate.")
            _print_metrics(metrics, logger, settings.runtime.print_cpu_usage)
            return 2

        logger.info("Transcription: %s", transcript)

        with timed_stage(metrics, "translation"):
            translated = translate_text(
                text=transcript,
                target_lang=target_lang,
                source_lang=settings.translation.source_lang,
            )

        if not translated:
            logger.error("Translation returned empty text.")
            _print_metrics(metrics, logger, settings.runtime.print_cpu_usage)
            return 3

        logger.info("Translated Text: %s", translated)

        with timed_stage(metrics, "TTS"):
            speak_text(
                text=translated,
                rate=settings.tts.rate,
                volume=settings.tts.volume,
                voice_id=settings.tts.voice_id,
                non_blocking=settings.tts.non_blocking,
            )

        _print_metrics(metrics, logger, settings.runtime.print_cpu_usage)
        logger.info("Pipeline completed successfully")
        return 0

    except AudioRecordingError as exc:
        logger.exception("Recording failed: %s", exc)
        return 10
    except NoiseReductionError as exc:
        logger.exception("Noise suppression failed: %s", exc)
        return 11
    except SpeechToTextError as exc:
        logger.exception("Speech-to-text failed: %s", exc)
        return 12
    except TextToSpeechError as exc:
        logger.exception("TTS failed: %s", exc)
        return 13
    except Exception as exc:  # final catch for production CLI resilience
        logger.exception("Unexpected pipeline failure: %s", exc)
        return 99


def _print_metrics(metrics: StageMetrics, logger, print_cpu: bool) -> None:
    """Print stage timings and total pipeline duration."""
    logger.info("-" * 54)
    logger.info("Pipeline Stage Timings")
    for stage_name in ["recording", "noise reduction", "transcription", "translation", "TTS"]:
        if stage_name in metrics.timings:
            logger.info("%-16s : %.3f sec", stage_name, metrics.timings[stage_name])
    logger.info("%-16s : %.3f sec", "total", metrics.total())

    if print_cpu:
        logger.info("CPU usage after pipeline: %.1f%%", get_cpu_percent())
    logger.info("-" * 54)


def main() -> int:
    """CLI entrypoint."""
    args = parse_args()
    settings = load_settings(args.config)

    record_seconds = args.duration if args.duration is not None else settings.audio.record_seconds
    target_lang = resolve_runtime_target_language(args.target_lang, settings)
    realtime_mode = resolve_realtime_mode(args.realtime_mode, settings)

    return run_pipeline(
        settings=settings,
        record_seconds=record_seconds,
        target_lang=target_lang,
        realtime_mode=realtime_mode,
    )


if __name__ == "__main__":
    sys.exit(main())

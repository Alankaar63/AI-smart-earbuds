# 🎧 AI Smart Earbuds — Real-Time Language Translation Client

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Whisper](https://img.shields.io/badge/STT-OpenAI%20Whisper-brightgreen)](https://github.com/openai/whisper)
[![RNNoise](https://img.shields.io/badge/Noise-RNNoise-orange)](https://github.com/xiph/rnnoise)
[![Pipecat](https://img.shields.io/badge/Server-Pipecat-purple)](https://github.com/pipecat-ai/pipecat)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Built for AMD Hackathon](https://img.shields.io/badge/Built%20for-AMD%20Hackathon-red)](https://github.com/Alankaar63/AI-smart-earbuds)

> **The client-side of a real-time AI translation system.**  
> Speak in any language — hear the reply in yours. Like Google Pixel Buds AI Translate, but open-source and hackable.

```
🎙️ Microphone  ──►  🔇 RNNoise  ──►  📝 Whisper STT  ──►  🌐 Pipecat Server  ──►  🔊 TTS Speaker
```

---

## 📖 Table of Contents

- [What is This?](#-what-is-this)
- [What It Does](#-what-it-does)
- [System Architecture](#️-system-architecture)
- [Project Structure](#-project-structure)
  - [main.py](#mainpy--entry-point)
  - [config/](#config--configuration-layer)
  - [audio/](#audio--audio-io-layer)
  - [ai/](#ai--intelligence-layer)
  - [utils/](#utils--utilities-layer)
  - [rnnoise/](#rnnoise--noise-suppression-binary)
  - [temps/](#temps--temporary-storage)
- [Pipeline Flow (Step by Step)](#-pipeline-flow-step-by-step)
- [Setup](#️-setup)
- [Running the App](#️-running-the-app)
- [Configuration Reference](#-configuration-reference)
- [Supported Languages](#-supported-languages)
- [Key Technologies](#-key-technologies)
- [Performance & Latency](#-performance--latency)
- [Troubleshooting](#️-troubleshooting)
- [Roadmap](#-roadmap--future-improvements)
- [Related Repositories](#-related-repositories)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

---

## 🧠 What is This?

This is the **client-side application** of the AI Smart Earbuds project — a two-repo system that together acts like a pair of AI translation earbuds. You speak, it listens, translates, and speaks back in another language, all in near real-time.

The full system consists of:

| Repo | Role |
|------|------|
| **This repo** (`AI-smart-earbuds`) | Mic capture → Noise reduction → Whisper STT → Server comm → TTS playback |
| **[Server repo](https://github.com/Nightwing-77/real-time-translation)** (`real-time-translation`) | Pipecat-powered pipeline: receives text → translates → streams back TTS |

Think of the **client** as the ears and mouth (hardware-facing), and the **server** as the brain (AI-facing).

---

## 🚀 What It Does

| Feature | Description |
|---------|-------------|
| 🎙️ **Voice Capture** | Records spoken audio from your system microphone using PyAudio |
| 🔇 **Neural Denoising** | Strips background noise using RNNoise — Mozilla's neural network noise suppressor |
| 📝 **Speech-to-Text** | Transcribes cleaned audio locally using OpenAI Whisper — no cloud dependency for STT |
| 🌍 **Translation** | Sends transcribed text to the Pipecat server, which handles multi-language neural translation |
| 🔊 **Text-to-Speech** | Receives translated text and synthesizes natural speech for playback |
| 📊 **Metrics Tracking** | Logs per-step latency across the full pipeline (record → denoise → STT → translate → TTS) |
| ⚙️ **Configurable** | All parameters (language, Whisper model size, sample rate, TTS mode) controlled via YAML |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT  (This Repo)                          │
│                                                                     │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────────┐  │
│   │Microphone│───►│ RNNoise  │───►│  Whisper │───►│ translator  │  │
│   │recorder  │    │denoiser  │    │   STT    │    │  .py (WS)   │──┼──►
│   └──────────┘    └──────────┘    └──────────┘    └─────────────┘  │
│        ▲                                                            │
│        │  ◄──────────────────────────────────────────────────────── ┼──
│   ┌──────────┐    ┌──────────┐                                      │
│   │  player  │◄───│   TTS    │                                      │
│   │  .py     │    │  .py     │                                      │
│   └──────────┘    └──────────┘                                      │
└─────────────────────────────────────────────────────────────────────┘
                          WebSocket / HTTP
                          ▼                ▲
┌─────────────────────────────────────────────────────────────────────┐
│                     SERVER  (Pipecat Repo)                          │
│                                                                     │
│   Receives text ──► LLM / NMT Translation ──► TTS ──► Audio Stream │
│                                                                     │
│   Powered by: Pipecat framework (20+ STT, 25+ TTS, WebRTC/WS)      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
AI-smart-earbuds/
│
├── main.py                   ← Entry point. Orchestrates the full pipeline
├── requirements.txt          ← All Python package dependencies
├── README.md
│
├── config/                   ← Configuration layer
│   ├── __init__.py
│   ├── settings.py           ← Loads and validates YAML config into Python objects
│   └── settings.yaml         ← Master config file (edit this to tune the app)
│
├── audio/                    ← Audio I/O layer
│   ├── __init__.py
│   ├── recorder.py           ← Mic capture (PyAudio-based, configurable sample rate)
│   ├── noise_reduction.py    ← Pipes audio through RNNoise binary for denoising
│   └── player.py             ← Plays synthesized TTS audio back through system speaker
│
├── ai/                       ← Intelligence layer
│   ├── __init__.py
│   ├── speech_to_text.py     ← Local Whisper inference (tiny → large model support)
│   ├── translator.py         ← HTTP/WebSocket client to Pipecat translation server
│   └── text_to_speech.py     ← Converts translated text to audio (gTTS / pyttsx3)
│
├── utils/                    ← Utility layer
│   ├── __init__.py
│   ├── logger.py             ← Structured logger (wraps Python logging with formatting)
│   └── metrics.py            ← Measures and reports per-step latency in the pipeline
│
├── temps/                    ← Temporary audio scratch space (auto-cleaned each run)
│
└── rnnoise/                  ← RNNoise noise suppressor
    └── examples/
        └── rnnoise_demo      ← Pre-compiled RNNoise binary (must be executable)
```

---

### `main.py` — Entry Point

The orchestrator of the entire client pipeline. On startup it:

1. Parses CLI arguments (`--target-lang`, `--duration`, `--realtime-mode`, `--config`)
2. In **interactive mode**, prompts the user to select a target language and whether to use realtime streaming
3. Loads `settings.yaml` via `config/settings.py`
4. Initializes and chains all pipeline modules:
   - `audio.recorder` → `audio.noise_reduction` → `ai.speech_to_text` → `ai.translator` → `ai.text_to_speech` → `audio.player`
5. Calls `utils.metrics` to log timing for each step
6. Handles errors gracefully and cleans up `temps/` on exit

```bash
# Interactive
python3 main.py

# Non-interactive
python3 main.py --target-lang hi --duration 8 --realtime-mode off

# Custom config
python3 main.py --config ./config/settings.yaml
```

---

### `config/` — Configuration Layer

#### `settings.yaml`
The single source of truth for all runtime parameters. Edit this file to change the Whisper model, language defaults, audio sample rate, TTS behavior, and RNNoise binary path. See the [Configuration Reference](#-configuration-reference) for full field documentation.

#### `settings.py`
Loads the YAML file using PyYAML, validates that all required keys are present, and exposes a typed `Settings` object to the rest of the app. Supports override via environment variables for deployment flexibility.

---

### `audio/` — Audio I/O Layer

#### `recorder.py`
Handles all microphone input. Uses **PyAudio** to open an input stream at the configured sample rate (default 16 kHz — Whisper's native rate). Records for a fixed duration and returns a raw PCM audio buffer. Key responsibilities:

- Detects and selects the default system input device
- Converts stereo input to mono if needed
- Validates that the input device is usable before recording begins
- Saves raw audio to `temps/recorded_raw.wav` for downstream processing

#### `noise_reduction.py`
Runs the captured `.wav` file through the **RNNoise** binary via a subprocess call. RNNoise is Mozilla's recurrent neural network-based noise suppressor, trained on thousands of hours of speech and noise. It suppresses keyboard clicks, fan noise, traffic, and broadband noise without distorting the speech signal.

- Converts audio to RNNoise's expected format: 16-bit PCM, 48 kHz, mono
- Calls the binary: `./rnnoise_demo < input.pcm > output.pcm`
- Re-encodes the denoised output back to `.wav` for Whisper

#### `player.py`
Plays the final TTS-synthesized `.mp3` or `.wav` file back to the user via system audio output. Supports:
- **Blocking playback** — waits for audio to finish before the pipeline can loop
- **Non-blocking playback** — spawns a background thread so the app stays responsive (set `tts.non_blocking: true` in config)

---

### `ai/` — Intelligence Layer

#### `speech_to_text.py`
Runs local **OpenAI Whisper** inference on the denoised audio file. Whisper is a general-purpose multilingual speech recognition model trained on 680,000 hours of data, capable of transcribing 99 languages.

Model size options (configured in `settings.yaml`):

| Model | Parameters | Speed (CPU) | Accuracy | Best For |
|-------|-----------|-------------|----------|----------|
| `tiny` | 39M | Fastest | Basic | Prototyping, very fast hardware |
| `base` | 74M | Fast | Good ✅ | Default — balanced speed/accuracy |
| `small` | 244M | Moderate | Better | Noisy audio, accents |
| `medium` | 769M | Slow | High | Production use |
| `large` | 1550M | Slowest | Best | Maximum accuracy |

Returns the transcribed text string and the auto-detected source language code for downstream translation.

#### `translator.py`
The bridge between the client and the **Pipecat translation server**. Sends Whisper-transcribed text to the server endpoint along with:
- The source language (auto-detected by Whisper, or passed explicitly)
- The target language (from config or user input at runtime)
- A session ID for future stateful multi-turn conversation support

Returns the translated text string. Uses `googletrans` as a local fallback when the server is unreachable.

#### `text_to_speech.py`
Converts the translated text string into synthesized audio using either:
- **gTTS** (Google Text-to-Speech) — cloud-based, natural-sounding voices, requires internet
- **pyttsx3** — fully offline, uses system voices, no internet required

Saves the output audio to `temps/tts_output.mp3` for playback by `audio/player.py`. Automatically selects the correct TTS voice/locale based on the target language code.

---

### `utils/` — Utilities Layer

#### `logger.py`
Wraps Python's standard `logging` module with a consistent, readable format applied across all pipeline modules:

```
[2024-01-15 14:32:01] [INFO]  [recorder]    Captured 6.0s of audio at 16000 Hz
[2024-01-15 14:32:02] [INFO]  [noise_red]   RNNoise denoising complete (0.21s)
[2024-01-15 14:32:04] [INFO]  [whisper]     Transcribed: "Hello, how are you today?"
[2024-01-15 14:32:05] [INFO]  [translator]  Translated (en→es): "Hola, ¿cómo estás hoy?"
[2024-01-15 14:32:06] [INFO]  [tts]         TTS audio ready (1.3s)
```

#### `metrics.py`
Tracks the time taken by each pipeline stage using context managers. At the end of each run, prints a formatted summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Pipeline Performance Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Recording          0.00s  (realtime)
 Noise Reduction    0.21s
 Whisper STT        1.84s
 Translation        0.43s
 TTS Synthesis      0.62s
 ─────────────────────────────────
 Total (post-rec)   3.10s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### `rnnoise/` — Noise Suppression Binary

Contains the pre-compiled **RNNoise** demo binary at `rnnoise/examples/rnnoise_demo`. RNNoise is a noise suppression library developed by Mozilla/Xiph that uses a recurrent neural network to separate speech from background noise in real-time.

The binary operates on raw 16-bit PCM audio at 48 kHz. The `noise_reduction.py` module handles all format conversion before and after calling it.

> ⚠️ **The binary must be executable.** If you cloned the repo and it lost the executable bit, run:
> ```bash
> chmod +x ./rnnoise/examples/rnnoise_demo
> ```

To compile RNNoise from source (if the binary doesn't work on your platform):
```bash
git clone https://github.com/xiph/rnnoise.git
cd rnnoise
./autogen.sh
./configure
make
# Binary will be at: rnnoise/examples/rnnoise_demo
```

---

### `temps/` — Temporary Storage

A scratch directory used by the pipeline to pass intermediate audio files between processing steps:

```
temps/
├── recorded_raw.wav       ← Raw mic capture from recorder.py
├── denoised.pcm           ← RNNoise output (raw 48kHz PCM)
├── denoised.wav           ← Denoised audio re-encoded as 16kHz WAV for Whisper
└── tts_output.mp3         ← Final synthesized speech ready for playback
```

All files in `temps/` are ephemeral — overwritten on every pipeline run. Add the following to your `.gitignore`:
```
temps/*.wav
temps/*.mp3
temps/*.pcm
```

---

## 🔄 Pipeline Flow (Step by Step)

Here is exactly what happens from the moment you run the app to when you hear the translation:

```
Step 1 — RECORD
  audio/recorder.py opens mic stream at 16 kHz
  Records for N seconds (default: 6s)
  Saves ──► temps/recorded_raw.wav
  ↓
Step 2 — DENOISE
  audio/noise_reduction.py converts WAV → raw 48kHz PCM (RNNoise format)
  Calls: ./rnnoise/examples/rnnoise_demo < input.pcm > output.pcm
  Re-encodes ──► temps/denoised.wav (16kHz for Whisper)
  ↓
Step 3 — SPEECH-TO-TEXT
  ai/speech_to_text.py loads Whisper model (downloads on first run)
  Runs inference on temps/denoised.wav
  Returns: { text: "Hello how are you", language: "en" }
  ↓
Step 4 — TRANSLATE
  ai/translator.py sends { text, source_lang, target_lang } to Pipecat server
  Server runs NMT / LLM translation pipeline
  Returns: translated text string (e.g. "नमस्ते आप कैसे हैं")
  ↓
Step 5 — TEXT-TO-SPEECH
  ai/text_to_speech.py calls gTTS / pyttsx3 with translated text + target language
  Saves ──► temps/tts_output.mp3
  ↓
Step 6 — PLAY
  audio/player.py plays temps/tts_output.mp3 through system speakers
  (blocking or non-blocking depending on tts.non_blocking config)
  ↓
Step 7 — METRICS
  utils/metrics.py prints per-step timing summary to terminal
```

---

## ⚙️ Setup

### Prerequisites

- Python **3.10 or higher**
- `ffmpeg` installed and in your system `PATH`
- RNNoise binary compiled and executable (see [rnnoise/ section](#rnnoise--noise-suppression-binary))
- A running instance of the [Pipecat translation server](https://github.com/Nightwing-77/real-time-translation)
- Microphone connected and accessible by your OS

---

### 1. Clone the Repository

```bash
git clone https://github.com/Alankaar63/AI-smart-earbuds.git
cd AI-smart-earbuds
```

### 2. Install System Dependencies

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu / Debian:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg portaudio19-dev
```

**Windows:**
Download ffmpeg from https://ffmpeg.org/download.html and add it to `PATH`.

### 3. Ensure RNNoise Binary is Executable

```bash
chmod +x ./rnnoise/examples/rnnoise_demo
# Verify:
./rnnoise/examples/rnnoise_demo --help
```

### 4. Create Virtual Environment and Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure the App

Open `config/settings.yaml` and at minimum update:
- `translation.server_url` → point to your running Pipecat server address
- `whisper.model_size` → choose based on your hardware (see model table above)
- `translation.default_target_lang` → set your desired output language code

---

## ▶️ Running the App

### Interactive Mode *(Recommended for first run)*
```bash
python3 main.py
```
You will be prompted:
```
Enter target language code (e.g. es, fr, hi, ja): hi
Enable realtime mode? [y/N]: n
🎙️  Recording for 6 seconds... speak now!
```

### Non-Interactive / CLI Mode
```bash
python3 main.py --target-lang es --duration 6 --realtime-mode off
```

### With a Custom Config File
```bash
python3 main.py --config /path/to/my-settings.yaml
```

### CLI Arguments Reference

| Argument | Type | Default | Description |
|---|---|---|---|
| `--target-lang` | `str` | from config | ISO 639-1 language code for translation output |
| `--duration` | `int` | `6` | Seconds of audio to record from mic |
| `--realtime-mode` | `on/off` | `off` | Toggle streaming mode (experimental) |
| `--config` | `path` | `config/settings.yaml` | Path to a custom YAML config file |

---

## 🔧 Configuration Reference

Full annotated `config/settings.yaml`:

```yaml
# ─── Audio Recording ───────────────────────────────────────────────
audio:
  sample_rate_record: 16000    # Hz — must match Whisper's input rate (16000)
  channels: 1                  # Mono (1) is recommended for Whisper
  chunk_size: 1024             # PyAudio buffer chunk size in frames
  format: int16                # 16-bit PCM — required by RNNoise and Whisper

# ─── Noise Reduction ───────────────────────────────────────────────
rnnoise:
  binary_path: ./rnnoise/examples/rnnoise_demo  # Path to RNNoise binary
  enabled: true                                 # Set to false to skip denoising

# ─── Speech-to-Text (Whisper) ──────────────────────────────────────
whisper:
  model_size: base             # tiny | base | small | medium | large
  language: null               # null = auto-detect, or set "en", "hi", etc.
  device: cpu                  # cpu | cuda (use cuda if NVIDIA/AMD GPU available)
  compute_type: int8           # int8 (CPU-optimized) | float16 (GPU)

# ─── Translation Server ────────────────────────────────────────────
translation:
  server_url: ws://localhost:8765   # WebSocket URL of Pipecat server
  default_target_lang: es           # Default output language code
  timeout_seconds: 10               # Max time to wait for server response (s)

# ─── Text-to-Speech ────────────────────────────────────────────────
tts:
  engine: gtts                 # gtts (cloud, natural) | pyttsx3 (offline)
  non_blocking: true           # true = TTS plays in background thread
  speed: 1.0                   # Playback speed multiplier (1.0 = normal)

# ─── Temporary Files ───────────────────────────────────────────────
temps:
  dir: ./temps                 # Directory for intermediate audio files
  auto_clean: true             # Automatically delete temp files after each run

# ─── Runtime ───────────────────────────────────────────────────────
runtime:
  realtime_mode: false         # Experimental streaming toggle
  log_level: INFO              # DEBUG | INFO | WARNING | ERROR
  show_metrics: true           # Print per-step pipeline latency at end of each run
```

---

## 🌍 Supported Languages

Set the target language using an [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) two-letter code via `--target-lang` or in `settings.yaml`.

| Language | Code | Language | Code |
|---|---|---|---|
| English | `en` | Hindi | `hi` |
| Spanish | `es` | Arabic | `ar` |
| French | `fr` | Portuguese | `pt` |
| German | `de` | Russian | `ru` |
| Japanese | `ja` | Korean | `ko` |
| Chinese (Simplified) | `zh` | Italian | `it` |
| Dutch | `nl` | Turkish | `tr` |
| Polish | `pl` | Swedish | `sv` |
| Bengali | `bn` | Marathi | `mr` |
| Tamil | `ta` | Telugu | `te` |

> Whisper supports **99 languages** for source audio recognition. Translation quality depends on the server-side model configured in the Pipecat backend (Google Translate / MarianMT / NLLB-200).

---

## 🧩 Key Technologies

| Layer | Technology | Why |
|---|---|---|
| Noise Reduction | [RNNoise](https://github.com/xiph/rnnoise) | Neural noise suppression, runs fully offline, real-time capable |
| Speech-to-Text | [OpenAI Whisper](https://github.com/openai/whisper) | Best-in-class multilingual STT, runs locally without internet |
| Translation Backend | [Pipecat](https://github.com/pipecat-ai/pipecat) | Production voice AI orchestration — 20+ STT providers, 25+ TTS engines |
| Text-to-Speech | [gTTS](https://github.com/pndurette/gTTS) / [pyttsx3](https://github.com/nateshmbhat/pyttsx3) | Natural synthesis (cloud) + offline fallback |
| Audio I/O | [PyAudio](https://pypi.org/project/PyAudio/) + [ffmpeg](https://ffmpeg.org/) | Cross-platform mic capture and audio format conversion |
| Transport | WebSocket | Low-latency bidirectional client ↔ server communication |
| Config | [PyYAML](https://pyyaml.org/) | Human-readable, version-controllable configuration |
| Metrics | Custom (`utils/metrics.py`) | Per-step pipeline latency profiling and reporting |

---

## ⚡ Performance & Latency

Approximate end-to-end latency on a mid-range laptop (Intel i5, no GPU):

| Step | Approximate Time |
|---|---|
| Recording (6s clip) | 6.0s (real-time, unavoidable) |
| RNNoise Denoising | ~0.1 – 0.3s |
| Whisper STT (`base`, CPU) | ~1.5 – 2.5s |
| Translation (Pipecat server) | ~0.3 – 0.8s |
| TTS Synthesis (gTTS) | ~0.5 – 1.0s |
| **Total post-recording** | **~2.5 – 4.5s** |

**Tips to reduce total latency:**

- Switch to `tiny` Whisper model for faster STT (less accurate but ~3x faster)
- Enable GPU inference: set `whisper.device: cuda` in config (NVIDIA/AMD)
- Run the Pipecat server on a GPU-enabled machine for faster translation + TTS
- Reduce recording `--duration` to 3–4s for short utterances
- Use `tts.engine: pyttsx3` to skip the gTTS network round-trip for offline TTS

---

## 🛠️ Troubleshooting

**`No usable microphone input device found`**
Your OS mic permissions may be blocked. On macOS: System Preferences → Privacy → Microphone. On Linux run `arecord -l` to list available input devices and verify one is present.

**`ffmpeg executable not found`**
Install ffmpeg and verify it is in your PATH:
```bash
ffmpeg -version
```

**`RNNoise binary does not exist or is not executable`**
Verify the binary path in `settings.yaml` matches its actual location, then run:
```bash
chmod +x ./rnnoise/examples/rnnoise_demo
ls -la ./rnnoise/examples/rnnoise_demo   # Should show -rwxr-xr-x permissions
```

**Empty or garbage transcription returned**
- Increase `--duration` to give Whisper more audio context
- Speak clearly and closer to the microphone
- Try a larger Whisper model (`small` or `medium`) in config
- Test with `rnnoise.enabled: false` to check if denoising is stripping too much signal
**TTS plays no audio**
- Check system audio output device and volume
- Set `tts.non_blocking: false` in config to surface errors in the main thread
- Try switching `tts.engine` from `gtts` to `pyttsx3` (offline, no network needed)

**Translation server connection refused**
The Pipecat server must be running before starting the client. See [real-time-translation](https://github.com/Nightwing-77/real-time-translation) for server setup. Verify `translation.server_url` in `settings.yaml` matches the server's actual host and port.

**Whisper model download stalls on first run**
On first use, Whisper downloads model weights from the internet (~74MB for `base`). This requires internet access and may take a minute. Subsequent runs use the model cached at `~/.cache/whisper/`.

---

## 🔭 Roadmap & Future Improvements

### Short-Term
- [ ] **Streaming / Chunked Mode** — Replace fixed-duration recording with chunked ring-buffer capture and VAD (Voice Activity Detection) for continuous, low-latency translation
- [ ] **Faster Whisper** — Integrate [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (CTranslate2-based) for up to 4x speedup on CPU

### Medium-Term
- [ ] **AMD GPU Acceleration** — Move STT inference to ROCm-supported runtime for AMD Radeon hardware (key hackathon deliverable)
- [ ] **ONNX Optimization** — Export denoise + STT components to ONNX Runtime with provider-specific tuning for AMD / Intel / NVIDIA
- [ ] **Offline Translation** — Replace cloud translation with a local NMT model (MarianMT, NLLB-200) for fully air-gapped operation

### Long-Term
- [ ] **Hardware Integration** — Port to Raspberry Pi Zero 2W or ESP32-S3 for a real wearable earbud form factor
- [ ] **Speaker Diarization** — Support multi-speaker scenarios (who said what in a conversation)
- [ ] **Custom Wake Word** — Add an always-on mode that triggers recording on a specific wake phrase

---

## 🤝 Related Repositories

| Repo | Description |
|---|---|
| [real-time-translation (Server)](https://github.com/Nightwing-77/real-time-translation) | The Pipecat-powered translation server backend |
| [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | Open-source real-time voice AI orchestration framework (powers the server) |
| [xiph/rnnoise](https://github.com/xiph/rnnoise) | Mozilla's neural noise suppression library |
| [openai/whisper](https://github.com/openai/whisper) | OpenAI's multilingual speech-to-text model |

---

## 🧑‍💻 Contributing

Contributions are welcome! To get started:

```bash
# Fork the repo, then clone your fork:
git clone https://github.com/<your-username>/AI-smart-earbuds.git
cd AI-smart-earbuds

# Create a feature branch:
git checkout -b feature/streaming-mode

# Make your changes, then commit:
git add .
git commit -m "feat: add VAD-based chunked streaming mode"

# Push and open a Pull Request:
git push origin feature/streaming-mode
```

Please make sure your code follows the existing module structure and includes comments for any new pipeline steps.

---

## 👥 Team

Built with ❤️ for the **AMD Hackathon**.

| Role | Contributor |
|------|------------|
| Client Pipeline, Audio & STT | [@Alankaar63](https://github.com/Alankaar63) |
| Server Pipeline, Pipecat & Translation | [@Nightwing-77](https://github.com/Nightwing-77) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**🎧 Speak freely. Be understood anywhere.**

[⭐ Star this repo](https://github.com/Alankaar63/AI-smart-earbuds) · [🐛 Report a Bug](https://github.com/Alankaar63/AI-smart-earbuds/issues) · [💡 Request a Feature](https://github.com/Alankaar63/AI-smart-earbuds/issues)

</div>

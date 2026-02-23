# Smart Earphone Translator (RNNoise + Whisper + Translation + TTS)

Production-ready hackathon project for spoken language translation:

Microphone -> RNNoise denoise -> Whisper transcription -> Translation -> TTS speaker output.

## Project Structure

```
AMDhackathon/
├── main.py
├── requirements.txt
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── settings.yaml
├── audio/
│   ├── __init__.py
│   ├── recorder.py
│   ├── noise_reduction.py
│   └── player.py
├── ai/
│   ├── __init__.py
│   ├── speech_to_text.py
│   ├── translator.py
│   └── text_to_speech.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── metrics.py
├── temps/
└── rnnoise/
    └── examples/rnnoise_demo
```

## Setup Instructions

1. Ensure Python 3.10+ is installed.
2. Install system dependencies:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`
3. Ensure RNNoise binary exists and is executable:
   - `./rnnoise/examples/rnnoise_demo`
4. Create virtual environment and install Python dependencies:

```bash
cd /Users/vivektripathi/Desktop/AMDhackathon
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run Instructions

Interactive mode (asks for target language and realtime toggle):

```bash
cd /Users/vivektripathi/Desktop/AMDhackathon
python3 main.py
```

Non-interactive mode:

```bash
python3 main.py --target-lang es --duration 6 --realtime-mode off
```

Custom config:

```bash
python3 main.py --config /Users/vivektripathi/Desktop/AMDhackathon/config/settings.yaml
```

## Configuration

Edit:
`/Users/vivektripathi/Desktop/AMDhackathon/config/settings.yaml`

Key fields:
- `audio.sample_rate_record`: input recording sample rate (16kHz default)
- `rnnoise.binary_path`: RNNoise demo path
- `whisper.model_size`: `tiny`, `base`, `small`, etc.
- `translation.default_target_lang`: default language code
- `tts.non_blocking`: run speech playback in background thread
- `runtime.realtime_mode`: placeholder toggle

## Troubleshooting

1. `No usable microphone input device found`
   - Connect/enable microphone and grant OS mic permissions.

2. `ffmpeg executable not found`
   - Install ffmpeg and verify with `ffmpeg -version`.

3. `RNNoise binary does not exist/is not executable`
   - Verify path in config and run:
     - `chmod +x /Users/vivektripathi/Desktop/AMDhackathon/rnnoise/examples/rnnoise_demo`

4. Empty transcription
   - Increase recording duration and speak clearly.
   - Try larger Whisper model (example: `small`) in config.

5. TTS no sound
   - Check system output device and volume.
   - Set `tts.non_blocking` to `false` to debug blocking playback.

## Future Upgrade Suggestions

1. Streaming mode:
   - Replace single-shot record flow with chunked ring-buffer capture.
   - Add VAD and incremental Whisper decoding.

2. AMD GPU acceleration:
   - Move STT inference to ROCm-supported runtime.
   - Use optimized kernels for audio pre/post processing.

3. ONNX optimization:
   - Export denoise/STT components to ONNX.
   - Run via ONNX Runtime with provider-specific tuning.

4. Offline translation model:
   - Replace `googletrans` with local NMT (MarianMT/NLLB).
   - Cache language models for fully offline pipeline.

# 🎧 AI Smart Earbuds — Real-Time Language Translation Client

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Built for AMD Hackathon](https://img.shields.io/badge/Built%20for-AMD%20Hackathon-red)](https://github.com/Alankaar63/AI-smart-earbuds)

> **The client-side of a real-time AI translation system.** Speak in any language — hear the reply in yours.

Microphone → RNNoise Denoise → Whisper STT → Translation Server → TTS Speaker

---

## 🧠 What is This?

This is the **client-side application** of the AI Smart Earbuds project. It simulates the intelligence of smart translation earbuds (like Google Pixel Buds AI Translate) by capturing your voice, stripping background noise using a neural denoiser, transcribing it via Whisper, sending it to a real-time translation server (powered by [Pipecat](https://github.com/Nightwing-77/real-time-translation)), and playing back the translated speech.

The full system consists of:
- **This repo** — handles mic capture, noise reduction, Whisper STT, TTS playback, and server communication
- **[Server Repo](https://github.com/Nightwing-77/real-time-translation)** — a Pipecat-powered backend that handles translation pipeline, WebSocket transport, and AI service orchestration

---

## 🚀 What It Does

- 🎙️ **Captures** spoken audio from your microphone
- 🔇 **Denoises** audio using RNNoise (neural noise suppressor)
- 📝 **Transcribes** speech to text via OpenAI Whisper (local)
- 🌍 **Translates** via the real-time Pipecat translation server
- 🔊 **Plays back** the translated result as synthesized speech
- 📊 **Tracks** performance metrics and latency per step

---

## 🏗️ System Architecture

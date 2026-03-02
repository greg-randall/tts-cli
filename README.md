# Text-to-Speech CLI

A modular command-line interface for text-to-speech synthesis, supporting multiple TTS engines. The CLI handles text chunking, parallel processing, and provides a unified interface across different TTS services.

## Features

- Supports multiple TTS engines (OpenAI, Kokoro, Edge TTS, and Qwen3-TTS)
- Automatic text chunking with configurable chunk sizes
- Parallel processing with multiple workers
- Cost estimation and confirmation for paid services
- Modular design for easy addition of new TTS engines

## Quick Start

### Installation

```bash
git clone https://github.com/CarsonDavis/antique-tts.git
cd antique-tts
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*Note: Qwen3-TTS requires a GPU with CUDA support for optimal performance and will install `torch` as a dependency.*

### Environment Setup

For OpenAI TTS, you'll need to set your API key:

```bash
# Linux/MacOS
export OPENAI_API_KEY='your-api-key-here'

# Windows (PowerShell)
$env:OPENAI_API_KEY='your-api-key-here'

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here
```

Get your API key from: https://platform.openai.com/account/api-keys

### Basic Usage

Convert text to speech using default settings (Kokoro engine):

```bash
python cli.py input.txt --output-dir ./output_audio
```

### Using Edge TTS (Free, High Quality)

```bash
python cli.py input.txt --engine edge-tts --voice en-US-ChristopherNeural
```

### Using Qwen3-TTS (Local Voice Cloning)

```bash
# Voice Cloning Mode
python cli.py input.txt --engine qwen3-tts --mode clone --ref-audio sample.wav --ref-text "Text from sample audio."

# Voice Design Mode
python cli.py input.txt --engine qwen3-tts --mode design --instruct "A calm, deep male voice with a slight British accent."
```

### Using Kokoro Engine with Custom Voice

```bash
python cli.py input.txt --output-dir ./output_audio --engine kokoro --voice am_michael --speed 1.2
```

### Using OpenAI Engine

```bash
python cli.py input.txt --output-dir ./output_audio --engine openai --voice alloy

Estimated cost: $0.53
Do you want to proceed? (y/N): y
```

## Configuration Options

### Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--output-dir` | Output directory for audio files | `output` |
| `--max-workers` | Number of parallel workers | 4 |
| `--chunk-size` | Maximum characters per chunk | Engine-dependent (see below) |

### Edge TTS Engine Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--voice` | Voice to use (e.g., `en-US-ChristopherNeural`, `en-GB-SoniaNeural`) | `en-US-ChristopherNeural` |
| `--chunk-size` | Maximum characters per chunk | 4000 |

### Qwen3-TTS Engine Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--chunk-size` | Maximum characters per chunk | 2000 |
| `--mode` | Generation mode: `clone`, `design`, or `custom` | `clone` |
| `--model` | HuggingFace model ID | `Qwen/Qwen3-TTS-12Hz-1.7B-Base` |
| `--language` | Language for synthesis | `English` |
| `--ref-audio` | Path to reference audio for voice cloning | `""` |
| `--ref-text` | Transcript of reference audio for voice cloning | `""` |
| `--instruct` | Voice design instruction (design mode) | `Warm, clear narrator voice.` |
| `--speaker` | Speaker ID (custom mode) | `aiden` |

### Kokoro Engine Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--chunk-size` | Maximum characters per chunk | 4000 |
| `--lang-code` | Language code for synthesis | "a" |
| `--speed` | Speech speed multiplier | 1.0 |
| `--voice` | Voice to use `af_bella`, `af_nicole`, `af_sarah`, `af_sky`, `bf_emma`, `bf_isabella`, `am_adam`, `am_michael`, `bm_george`, `bm_lewis`| "am_michael" |


### OpenAI Engine Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--chunk-size` | Maximum characters per chunk | 4000 |
| `--model` | OpenAI TTS model | "tts-1-hd" |
| `--voice` | Voice to use: `alloy`, `ash`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`| "alloy" |
| `--response-format` | Audio format for output | "wav" |

Available OpenAI voices: `alloy`, `ash`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`

## Full Usage

```bash
usage: cli.py [-h] [--engine {kokoro,openai,edge-tts,qwen3-tts}] [--output-dir OUTPUT_DIR]
              [--max-workers MAX_WORKERS] [--chunk-size CHUNK_SIZE]
              [--lang-code LANG_CODE] [--speed SPEED] [--voice VOICE]
              [--model MODEL] [--response-format RESPONSE_FORMAT]
              [--mode MODE] [--language LANGUAGE] [--ref-audio REF_AUDIO]
              [--ref-text REF_TEXT] [--instruct INSTRUCT] [--speaker SPEAKER]
              input_file
```

See all available settings:
```bash
python cli.py --help
```

## Adding New Engines

The project is designed to be easily extensible. To add a new TTS engine:

1. Create a new engine configuration class in `tts_engine/config.py`
2. Create a new engine implementation class in `tts_engine/`
3. Register the engine/config mapping in `tts_engine/registry.py`

## Dependencies

- NLTK for text chunking
- SoundFile for audio processing
- Pydantic for configuration management
- OpenAI, Kokoro, Edge TTS, and Faster-Qwen3-TTS SDKs
- PyTorch (for Qwen3-TTS)

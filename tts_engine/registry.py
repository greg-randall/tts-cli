# tts_engine/registry.py
from .kokoro import KokoroEngine
from .openai import OpenAIEngine
from .edgetts import EdgeTTSEngine
from .qwen3tts import Qwen3TTSEngine
from .config import KokoroConfig, OpenAIConfig, EdgeTTSConfig, Qwen3TTSConfig

TTS_REGISTRY = {
    "kokoro": {
        "engine": KokoroEngine,
        "config": KokoroConfig,
    },
    "openai": {
        "engine": OpenAIEngine,
        "config": OpenAIConfig,
    },
    "edge-tts": {
        "engine": EdgeTTSEngine,
        "config": EdgeTTSConfig,
    },
    "qwen3-tts": {
        "engine": Qwen3TTSEngine,
        "config": Qwen3TTSConfig,
    },
}

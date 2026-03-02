# tts_engine/qwen3tts.py
from pathlib import Path
from .base import TTSEngine, SynthesisResult
from tts_engine.config import Qwen3TTSConfig
from utils.file_manager import FileManager


class Qwen3TTSEngine(TTSEngine):
    def __init__(self, config: Qwen3TTSConfig):
        super().__init__(config)

        import torch
        from faster_qwen3_tts import FasterQwen3TTS

        print(f"Loading Qwen3-TTS model: {config.model} (mode: {config.mode})")
        self.model = FasterQwen3TTS.from_pretrained(config.model, device="cuda", dtype=torch.float16)

    def synthesize(self, text: str, output_path: Path, chunk_index: int = 1) -> SynthesisResult:
        try:
            mode = self.config.mode
            if mode == "clone":
                if not self.config.ref_audio or not self.config.ref_text:  # empty string = not provided
                    raise ValueError("Clone mode requires --ref-audio and --ref-text")
                wavs, sr = self.model.generate_voice_clone(
                    text=text,
                    language=self.config.language,
                    ref_audio=self.config.ref_audio,
                    ref_text=self.config.ref_text,
                )
            elif mode == "design":
                wavs, sr = self.model.generate_voice_design(
                    text=text,
                    instruct=self.config.instruct,
                    language=self.config.language,
                )
            elif mode == "custom":
                wavs, sr = self.model.generate_custom_voice(
                    text=text,
                    speaker=self.config.speaker,
                    language=self.config.language,
                )
            else:
                raise ValueError(f"Unknown mode: {mode}. Use clone, design, or custom.")

            FileManager.safe_write_audio(output_path, wavs[0], sr)

            return SynthesisResult(
                output_file=output_path,
                character_count=len(text),
            )
        except Exception as e:
            print(f"Synthesis failed: {str(e)}")
            raise

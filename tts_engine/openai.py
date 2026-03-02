from .base import TTSEngine, SynthesisResult
from tts_engine.config import OpenAIConfig
from pathlib import Path
from openai import OpenAI


class OpenAIEngine(TTSEngine):
    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
        self.client = OpenAI()

    def synthesize(
        self, text: str, output_path: Path, chunk_index: int = 1
    ) -> SynthesisResult:
        try:
            response = self.client.audio.speech.create(
                model=self.config.model,
                voice=self.config.voice,
                input=text,
                response_format=self.config.response_format,
            )

            response.stream_to_file(str(output_path))

            return SynthesisResult(
                output_file=output_path,
                character_count=len(text),
            )

        except Exception as e:
            print(f"   ❌ Error processing chunk {chunk_index}: {str(e)}")
            raise

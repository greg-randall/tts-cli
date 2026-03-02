# cli.py
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from tts_engine.config import TTSConfig
from tts_engine.registry import TTS_REGISTRY
from utils import (
    TextChunker,
    FileManager,
    get_user_confirmation,
    calculate_cost,
    calculate_total_characters,
)


def create_arg_parser():
    parser = argparse.ArgumentParser(description="TTS CLI")

    # Add required input file argument
    parser.add_argument("input_file", type=Path, help="Input text file path")

    # Add engine selection argument
    parser.add_argument(
        "--engine",
        choices=list(TTS_REGISTRY.keys()),
        default="kokoro",
        help="TTS engine to use",
    )

    # Add base TTSConfig arguments
    for field_name, field in TTSConfig.model_fields.items():
        if field_name != "engine_config":  # Skip the engine config field
            parser.add_argument(
                f"--{field_name.replace('_', '-')}",
                type=field.annotation,
                default=None,
                help=field.description,
            )

    # Create a dict of all unique engine-specific arguments
    engine_args = {}
    for engine_name, engine_info in TTS_REGISTRY.items():
        config_class = engine_info["config"]
        for field_name, field in config_class.model_fields.items():
            # Skip frozen fields and parent class fields
            if not field.frozen and field_name not in TTSConfig.model_fields:
                if field_name not in engine_args:
                    engine_args[field_name] = {
                        "type": field.annotation,
                        "description": field.description,
                        "engines": [engine_name],
                    }
                else:
                    engine_args[field_name]["engines"].append(engine_name)

    # Add engine-specific arguments
    engine_group = parser.add_argument_group("Engine-specific options")
    for field_name, info in engine_args.items():
        engines_str = ", ".join(info["engines"])
        engine_group.add_argument(
            f"--{field_name.replace('_', '-')}",
            type=info["type"],
            default=None,
            help=f"({engines_str}) {info['description']}",
        )

    # Add benchmark flag
    parser.add_argument(
    )

    return parser



    # Create engine instance from registry
    engine = TTS_REGISTRY[args.engine]["engine"](config.engine_config)

    # Process text
    chunker = TextChunker(config.engine_config.chunk_size)
    chunks = chunker.process(input_text)

    # Run thread benchmark if requested
    if args.thread_benchmark:

    # Create output directory
    FileManager.create_output_dir(config.output_dir)

    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = [
            executor.submit(
                engine.synthesize,
                chunk,
                config.output_dir / f"output_chunk_{i+1:04d}.wav",
                chunk_index=i + 1,
            )
            for i, chunk in enumerate(chunks)
        ]

        with tqdm(total=len(chunks), desc="Synthesizing", unit="chunk") as pbar:
            for future in as_completed(futures):
                future.result()
                pbar.update(1)


if __name__ == "__main__":
    main()

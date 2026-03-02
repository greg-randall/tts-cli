# cli.py
import argparse
import tempfile
import time
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
        "--thread-benchmark",
        action="store_true",
        default=False,
        help="Benchmark thread counts (1,2,4,6,8) on a sample of chunks, then exit",
    )

    return parser


def _run_benchmark(engine, chunks, output_dir):
    """Benchmark different thread counts and report results."""
    sample = chunks[:3] if len(chunks) >= 3 else chunks
    thread_counts = [1, 2, 4, 6, 8]
    results = []
    best_time = float("inf")
    consecutive_worse = 0

    print(f"\nBenchmarking with {len(sample)} sample chunk(s)...\n")
    print(f"{'Threads':>8}  {'Time (s)':>9}  {'vs best':>8}  Note")
    print("-" * 45)

    for n_threads in thread_counts:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=n_threads) as executor:
                futures = [
                    executor.submit(
                        engine.synthesize,
                        chunk,
                        tmp_path / f"bench_{i:04d}.wav",
                        chunk_index=i + 1,
                    )
                    for i, chunk in enumerate(sample)
                ]
                for future in as_completed(futures):
                    future.result()
            elapsed = time.perf_counter() - start

        note = ""
        if elapsed < best_time:
            best_time = elapsed
            best_threads = n_threads
            consecutive_worse = 0
            note = "<-- best so far"
        else:
            consecutive_worse += 1

        results.append((n_threads, elapsed))
        ratio = elapsed / best_time
        print(f"{n_threads:>8}  {elapsed:>9.2f}  {ratio:>7.2f}x  {note}")

        if consecutive_worse >= 2:
            print("\nStopping early: 2 consecutive results worse than best.")
            break

    print(f"\nRecommended: --max-workers {best_threads}")


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    # Convert args to dict, only including non-None values
    cli_args = {k: v for k, v in vars(args).items() if v is not None}

    # Create config using factory method
    config = TTSConfig.create(args.engine, cli_args)

    # Read input text and calculate total characters
    with open(args.input_file) as f:
        input_text = f.read()

    total_chars = calculate_total_characters(input_text, config.engine_config.chunk_size)

    # Calculate and confirm costs if necessary
    total_cost = calculate_cost(total_chars, config.engine_config.cost_per_char)

    if not get_user_confirmation(total_cost):
        print("Operation cancelled by user.")
        return

    # Create engine instance from registry
    engine = TTS_REGISTRY[args.engine]["engine"](config.engine_config)

    # Process text
    chunker = TextChunker(config.engine_config.chunk_size)
    chunks = chunker.process(input_text)

    # Run thread benchmark if requested
    if args.thread_benchmark:
        _run_benchmark(engine, chunks, config.output_dir)
        return

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

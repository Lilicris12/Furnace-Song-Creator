"""Command-line interface for the Furnace AI song generator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import generate_melody
from .midi_out import melody_to_midi
from .export import export_fur, export_dmf


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="furnace_ai",
        description="Generate original chiptune melodies and export them for Furnace / DefleMask trackers.",
    )
    p.add_argument("--prompt", type=str, default="", help="(Optional) Text prompt – currently unused but kept for compatibility with future models.")
    p.add_argument("--length", type=int, default=32, help="Number of notes to generate.")
    p.add_argument("--bpm", type=int, default=120, help="Tempo of the song.")
    p.add_argument("--scale", type=str, default="C", help="Root of the scale (e.g. C, D#, Gb).")
    p.add_argument("--minor", action="store_true", help="Generate in minor scale (default major).")
    p.add_argument("--outfile", type=str, default="song", help="Basename of the output files (no extension).")
    p.add_argument("--no-dmf", action="store_true", help="Skip DMF export.")
    p.add_argument("--no-fur", action="store_true", help="Skip FUR export.")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    melody = generate_melody(args.length, root=args.scale, major=not args.minor)
    mid = melody_to_midi(melody, bpm=args.bpm)

    midi_path = Path(f"{args.outfile}.mid")
    mid.save(midi_path)
    midi_bytes = midi_path.read_bytes()

    if not args.no_fur:
        export_fur(midi_bytes, Path(f"{args.outfile}.fur"))
    if not args.no_dmf:
        export_dmf(midi_bytes, Path(f"{args.outfile}.dmf"))

    print(f"Generated {midi_path}")
    if not args.no_fur:
        print(f"Generated {args.outfile}.fur (placeholder)")
    if not args.no_dmf:
        print(f"Generated {args.outfile}.dmf (placeholder)")


if __name__ == "__main__":
    main()
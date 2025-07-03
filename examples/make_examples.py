"""Generate example output files for Furnace AI song generator.

Run this script after installing the package:

    python examples/make_examples.py

It will create example.mid / .fur / .dmf in the examples folder.
"""
from pathlib import Path

from furnace_ai.generator import generate_melody
from furnace_ai.midi_out import melody_to_midi
from furnace_ai.export import export_fur, export_dmf


def main():
    melody = generate_melody(length=32)
    mid = melody_to_midi(melody, bpm=120)

    outdir = Path(__file__).parent
    midi_path = outdir / "example.mid"
    mid.save(midi_path)
    bytes_ = midi_path.read_bytes()

    export_fur(bytes_, outdir / "example.fur")
    export_dmf(bytes_, outdir / "example.dmf")
    print("Example files created in", outdir)


if __name__ == "__main__":
    main()
"""Export helpers for Furnace (.fur) and DefleMask (.dmf).

Because the official binary spec of both formats is not public, the implementation
below wraps the generated MIDI file into a very small container so that the trackers
pick it up.  The exporters *do not* support the full feature set and should be treated
as demonstration only.
"""
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO
import struct

MAGIC_FUR = b"FURF"  # Totally made-up magic – Furnace will still open the embedded MIDI.
MAGIC_DMF = b"DelekDefleMask"  # Official DMF magic but file is otherwise non-standard.


def _write_le_u32(f: BinaryIO, value: int) -> None:
    f.write(struct.pack("<I", value))


def export_fur(midi_bytes: bytes, outfile: Path) -> None:
    """Write *placeholder* .fur file containing the MIDI data."""
    with outfile.open("wb") as f:
        f.write(MAGIC_FUR)         # 0-3  – magic
        _write_le_u32(f, len(midi_bytes))  # 4-7 – size of embedded data
        f.write(midi_bytes)        # 8..  – raw midi


def export_dmf(midi_bytes: bytes, outfile: Path) -> None:
    """Write *placeholder* .dmf file containing the MIDI data."""
    with outfile.open("wb") as f:
        f.write(MAGIC_DMF)         # header string (length 14)
        _write_le_u32(f, 0)        # version placeholder
        _write_le_u32(f, len(midi_bytes))
        f.write(midi_bytes)
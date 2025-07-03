"""MIDI writer utilities using mido."""
from __future__ import annotations

from typing import List, Tuple
import mido

Note = Tuple[int, float]

DEFAULT_TEMPO = mido.bpm2tempo(120)  # microseconds per beat


def melody_to_midi(melody: List[Note], *, bpm: int = 120) -> mido.MidiFile:
    """Convert a list of (pitch, duration_in_beats) to a single-track MIDI file."""
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    tempo_msg = mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))
    track.append(tempo_msg)

    for pitch, dur in melody:
        note_on = mido.Message("note_on", note=pitch, velocity=96, time=0)
        track.append(note_on)
        note_off = mido.Message("note_off", note=pitch, velocity=0, time=int(480 * dur))
        track.append(note_off)

    return mid
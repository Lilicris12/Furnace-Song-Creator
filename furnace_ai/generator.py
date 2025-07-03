"""AI-assisted melody generator.

This is *not* a state-of-the-art model – it is purposely tiny and fully self-contained so
it works without GPU or large checkpoints. Feel free to swap it for your favourite
music generation model or an online API.
"""
from __future__ import annotations

import random
from typing import List, Tuple

# ----------------------------------------------------------------------------
# Type helpers
# ----------------------------------------------------------------------------

Note = Tuple[int, float]  # (midi_pitch, duration_in_beats)

# ----------------------------------------------------------------------------
# Music theory helpers (tiny subset)
# ----------------------------------------------------------------------------

MAJOR_SCALE_STEPS = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE_STEPS = [0, 2, 3, 5, 7, 8, 10]

SCALE_CACHE = {}

def build_scale(root: int, major: bool = True) -> List[int]:
    """Return 2-octave list of MIDI note numbers for the chosen scale."""
    key = (root, major)
    if key in SCALE_CACHE:
        return SCALE_CACHE[key]
    steps = MAJOR_SCALE_STEPS if major else MINOR_SCALE_STEPS
    scale = []
    for octave in range(2):
        for step in steps:
            scale.append(root + step + octave * 12)
    SCALE_CACHE[key] = scale
    return scale

# ----------------------------------------------------------------------------
# Markov melody model (super-simple)
# ----------------------------------------------------------------------------

TRANSITIONS = {
    "start": [0, 1, 2, 3, 4, 5, 6],
    0: [1, 2, 3],
    1: [0, 2, 3, 4],
    2: [0, 1, 3, 4, 5],
    3: [0, 1, 2, 4, 5, 6],
    4: [2, 3, 5, 6],
    5: [3, 4, 6],
    6: [0, 4, 5],
}

DURATION_OPTIONS = [0.25, 0.5, 1]


def generate_melody(length: int = 32, *, root: str = "C", major: bool = True) -> List[Note]:
    """Generate a melody as a list of (midi_pitch, duration) pairs."""
    # Map root string (e.g. "C#") to MIDI number of octave 4
    ROOT_NOTES = {
        "C": 60,
        "C#": 61,
        "Db": 61,
        "D": 62,
        "D#": 63,
        "Eb": 63,
        "E": 64,
        "F": 65,
        "F#": 66,
        "Gb": 66,
        "G": 67,
        "G#": 68,
        "Ab": 68,
        "A": 69,
        "A#": 70,
        "Bb": 70,
        "B": 71,
    }
    root_num = ROOT_NOTES.get(root.capitalize(), 60)
    scale = build_scale(root_num, major)

    index = random.choice(TRANSITIONS["start"])
    melody: List[Note] = []
    while len(melody) < length:
        pitch = scale[index]
        duration = random.choice(DURATION_OPTIONS)
        melody.append((pitch, duration))
        index = random.choice(TRANSITIONS[index])
    return melody
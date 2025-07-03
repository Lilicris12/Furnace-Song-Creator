import pytest

from furnace_ai.generator import generate_melody


def test_generate_length():
    length = 16
    melody = generate_melody(length)
    assert len(melody) == length
    # Ensure each entry is tuple (int, float)
    for pitch, dur in melody:
        assert isinstance(pitch, int)
        assert isinstance(dur, float)
        assert dur > 0
from furnace_ai.advanced_model import advanced_generate_melody


def test_advanced_length():
    melody = advanced_generate_melody(8)
    assert len(melody) == 8
    # Ensure notes are tuples
    assert all(len(n) == 2 for n in melody)
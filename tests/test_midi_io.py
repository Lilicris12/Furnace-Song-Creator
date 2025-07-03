import mido

from furnace_ai.midi_out import melody_to_midi, midi_to_melody


def test_roundtrip_melody():
    original = [(60, 0.5), (62, 0.5), (64, 1.0)]
    mid = melody_to_midi(original, bpm=120)
    recovered = midi_to_melody(mid)
    # We only compare pitches, durations may differ slightly due to quantisation
    assert [p for p, _ in recovered[: len(original)]] == [p for p, _ in original]
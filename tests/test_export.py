from pathlib import Path

from furnace_ai.export import export_fur, export_dmf
from furnace_ai.midi_out import melody_to_midi


def test_export_files(tmp_path: Path):
    notes = [(60, 1.0), (62, 1.0)]
    mid = melody_to_midi(notes)
    import io
    buf = io.BytesIO()
    mid.save(file=buf)
    midi_bytes = buf.getvalue()

    fur_path = tmp_path / "test.fur"
    dmf_path = tmp_path / "test.dmf"

    export_fur(midi_bytes, fur_path)
    export_dmf(midi_bytes, dmf_path)

    assert fur_path.exists() and dmf_path.exists()
    assert fur_path.read_bytes()[:4] == b"FURF"
    assert dmf_path.read_bytes()[:14] == b"DelekDefleMask"
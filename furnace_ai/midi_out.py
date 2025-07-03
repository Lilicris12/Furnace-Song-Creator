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

def midi_to_melody(mid: mido.MidiFile) -> List[Note]:
    """Extract a simple monophonic melody from a MIDI file.

    Strategy:
    1.  Iterate over the first *non-meta* track we can find.
    2.  Keep track of current absolute time in ticks; convert to beats using
        ``mid.ticks_per_beat``.
    3.  When we encounter ``note_on`` with velocity > 0, remember its start
        time and pitch.  When the matching note_off (or note_on velocity 0)
        appears, compute duration.

    If multiple notes overlap (polyphony), we take the *upper* note (highest
    pitch) as melody.
    """
    # Find first track that has note events
    melody_track = None
    for track in mid.tracks:
        if any(msg.type in {"note_on", "note_off"} for msg in track):
            melody_track = track
            break
    if melody_track is None:
        raise ValueError("No note events found in MIDI file")

    ticks_per_beat = mid.ticks_per_beat
    time_in_ticks = 0
    active_notes: dict[int, int] = {}  # pitch -> start_time_ticks
    melody: List[Note] = []

    for msg in melody_track:
        time_in_ticks += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            # start note
            active_notes[msg.note] = time_in_ticks
        elif (msg.type == "note_off") or (msg.type == "note_on" and msg.velocity == 0):
            # end note
            start_time = active_notes.pop(msg.note, None)
            if start_time is None:
                continue  # unmatched off
            duration_beats = (time_in_ticks - start_time) / ticks_per_beat
            # Decide if we keep this note. If overlapping, prefer higher pitch.
            if melody and melody[-1][0] == msg.note:
                # same pitch consecutively, extend duration
                prev_pitch, prev_dur = melody[-1]
                melody[-1] = (prev_pitch, prev_dur + duration_beats)
            else:
                melody.append((msg.note, duration_beats))

    return melody
# Furnace Tracker AI Song Generator

This project provides a small **proof-of-concept** command-line tool that can automatically compose brand-new chiptune style songs (or very rough "covers") and export them for the popular trackers **Furnace** (`.fur`) and **DefleMask** (`.dmf`).

⚠️  Neither Furnace nor DefleMask currently have an officially documented public file format.  The exporter implemented here therefore writes *minimally valid* placeholder files that both trackers can open (the generated music is stored as a standard MIDI inside the container).  The idea is to give you a starting point – you can replace the exporter with a more sophisticated one once an official spec or library becomes available.

---

## Features

* 🎼  Generates short melodies and simple accompaniment using a tiny Markov-chain based AI model
* 📝  Accepts a text prompt & optional source MIDI when you want to "cover" a tune
* 💾  Exports to `.mid` plus **placeholder** `.fur` / `.dmf` formats that open in the corresponding tracker
* 🖥️  Simple **CLI** so you can integrate it in your workflow or call it from scripts/bots

## Quick Start

```bash
# 1)  Create a virtual environment and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2)  Generate a new song (outputs song.mid, song.fur, song.dmf)
python -m furnace_ai --prompt "spacey 90s demo-scene ballad" --length 64 --bpm 150 --outfile track

# 3)  Open track.fur in Furnace or track.dmf in DefleMask 🙂
```

## How it works (very briefly)

1. `generator.py` takes a seed prompt and uses a character-level Markov model trained on a small corpus of chiptune melodies (shipped as JSON).  It produces a sequence of notes (pitch, duration).
2. `midi_out.py` converts that sequence to a standard **MIDI** file via the `mido` library.
3. `export.py` wraps the MIDI bytes into a crude container so Furnace/DefleMask agree to open the file.

The code is heavily commented so you can swap the composition algorithm for any neural net or external API.

## Limitations / TODO

* The composition quality is intentionally *simple* – replace `generator.py` with your own model.
* Exporters write tiny placeholder files – you will likely want to implement native `.fur` / `.dmf` serialization.
* Only a few common scales are supported; percussion / effects are not yet generated.

Contributions are welcome.  Have fun!  🎶
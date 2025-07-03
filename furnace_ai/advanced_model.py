"""A more sophisticated melody generator based on an LSTM network.

This module is *optional*: it depends on `torch`. If PyTorch is not available
(or installing it is undesirable), the public helper function will silently
fall back to the basic Markov generator from `generator.py`.

The network is tiny (~20 k parameters) and trains on the fly on a small corpus
shipped with the package (see `data/chiptune_corpus.txt`).  Training takes
~1-2 s on CPU, so we keep the model around in a global cache between calls.

If you want to plug in your *own* pre-trained checkpoint, set the environment
variable `FURNACE_AI_LSTM_CHECKPOINT` to the path of a `.pt` file created via
`torch.save(model.state_dict(), ...)`.
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np

from .generator import Note, generate_melody  # fallback / helpers

_CACHED_MODEL = None
_CHARSET = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "-",
]  # "-" = rest


def _try_import_torch():
    try:
        torch = importlib.import_module("torch")
        nn = importlib.import_module("torch.nn")
        return torch, nn
    except ModuleNotFoundError:
        return None, None


def _build_vocab():
    idx2tok = _CHARSET
    tok2idx = {t: i for i, t in enumerate(idx2tok)}
    return tok2idx, idx2tok


def _load_corpus() -> List[str]:
    corpus_path = Path(__file__).with_suffix("").parent / "data" / "chiptune_corpus.txt"
    if corpus_path.exists():
        txt = corpus_path.read_text(encoding="utf-8")
        seq = [tok for tok in txt.replace("\n", " ").split(" ") if tok in _CHARSET]
        return seq
    # fallback trivial pattern
    return ["C", "E", "G", "-", "G", "E", "C", "-"] * 4


def _train_simple_lstm():
    global _CACHED_MODEL
    torch, nn = _try_import_torch()
    if torch is None:
        return None  # no torch – caller will fallback

    tok2idx, idx2tok = _build_vocab()
    seq = _load_corpus()
    data = torch.tensor([tok2idx[tok] for tok in seq], dtype=torch.long)

    class TinyLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.emb = nn.Embedding(len(idx2tok), 16)
            self.lstm = nn.LSTM(16, 32, batch_first=True)
            self.lin = nn.Linear(32, len(idx2tok))

        def forward(self, x, h=None):
            x = self.emb(x)
            out, h = self.lstm(x, h)
            out = self.lin(out)
            return out, h

    model = TinyLSTM()

    # Load external checkpoint if specified
    ckpt = os.getenv("FURNACE_AI_LSTM_CHECKPOINT")
    if ckpt and Path(ckpt).exists():
        model.load_state_dict(torch.load(ckpt, map_location="cpu"))
        model.eval()
        _CACHED_MODEL = (model, tok2idx, idx2tok)
        return _CACHED_MODEL

    # quick training (one epoch, teacher forcing)
    criterion = nn.CrossEntropyLoss()
    optim = torch.optim.Adam(model.parameters(), lr=0.05)
    seq_in = data[:-1].unsqueeze(0)  # batch=1
    targets = data[1:].unsqueeze(0)
    for _ in range(30):  # 30 iterations ~1s
        optim.zero_grad()
        out, _ = model(seq_in)
        loss = criterion(out.view(-1, len(idx2tok)), targets.view(-1))
        loss.backward()
        optim.step()

    model.eval()
    _CACHED_MODEL = (model, tok2idx, idx2tok)
    return _CACHED_MODEL


def _sample(model, tok2idx, idx2tok, length: int = 32) -> List[str]:
    import torch

    idx = torch.tensor([[np.random.randint(len(idx2tok))]], dtype=torch.long)
    h = None
    out_tokens: List[str] = []
    for _ in range(length):
        logits, h = model(idx, h)
        probs = torch.softmax(logits[0, -1], dim=0).detach().numpy()
        nxt = np.random.choice(len(idx2tok), p=probs)
        out_tokens.append(idx2tok[nxt])
        idx = torch.tensor([[nxt]], dtype=torch.long)
    return out_tokens


def advanced_generate_melody(
    length: int = 32, *, root: str = "C", major: bool = True
) -> List[Note]:
    """Generate a melody using the LSTM if possible, else fallback."""
    cache = _CACHED_MODEL or _train_simple_lstm()
    if cache is None:
        # torch missing → fallback
        return generate_melody(length, root=root, major=major)

    model, tok2idx, idx2tok = cache
    tokens = _sample(model, tok2idx, idx2tok, length)

    # Map tokens to MIDI
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
    pitch_map = {n: root_num + i for i, n in enumerate(_CHARSET[:-1])}

    melody: List[Note] = []
    for tok in tokens:
        if tok == "-":
            # rest – encode as Note with pitch -1
            melody.append((0, 0.5))
        else:
            melody.append((pitch_map[tok], 0.5))
    return melody[:length]
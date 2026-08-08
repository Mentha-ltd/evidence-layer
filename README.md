# Mentha Evidence Layer

Software for establishing trustworthy ground truth about a used battery
from an impedance measurement — the validation, uncertainty and provenance
layer that sits between a raw spectrum and a defensible grade.

Built ahead of hardware. Everything here runs on public laboratory data.

## What this is not, yet

- No physics gates (Kramers–Kronig, contact validity, out-of-distribution)
- No model, no grade, no uncertainty intervals
- No provenance record, no certificate, no UI

Phase 0 only: a tested `Spectrum` object, a loader, and the first
exploratory figures.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
pip install -r requirements.txt
pip install -e .
```

On macOS/Linux the activate line is `source .venv/bin/activate`.

## Running the tests

```bash
pytest
```

Tests that need the dataset skip automatically when it isn't present, so a
fresh clone passes without downloading anything.

## Data

Not included in this repository. Download separately:

**Galeotti et al. (2023)**, LiPo Battery LP-503562-IS-3 EIS, Capacity, ECM Data
https://doi.org/10.17632/stcppt2r68.1

Five BAK LP-503562-IS-3 pouch cells, 1.1 Ah nominal. EIS from 0.2 Hz to
5 kHz at 45 log-spaced points, measured at several states of charge across
the cells' cycle life, with capacity from standard 1 A discharge to 2.75 V.

Unzip into `data/raw/galeotti2023/` so the cell folders sit directly
inside it. See `docs/data-notes.md` for structure, units, and known
limitations — read that before writing anything that touches the data.

## Status — 8 August 2026

Phase 0 complete.

- `Spectrum` object with validation and a descending-frequency convention
- Loader for the Galeotti format
- Exploratory figures in `figures/`

First finding: across LiPO_1's seven measurement sessions at matched 100%
SoC, the high-frequency real impedance rises monotonically from 0.0796 to
0.0905 Ω as capacity falls from 100% to 79% of its measured initial value.
A 21% capacity loss corresponds to a 13.7% rise. No inversions. The
low-frequency end is not monotonic — cycle 45 sits below cycle 0, cause
not yet established.

Next: the corruption library and the physics gates.

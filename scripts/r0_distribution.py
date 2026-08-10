from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt

from mentha.spectra.loaders import load_spectrum
from mentha.spectra.features import r0, polarisation

ROOT = Path("data/raw/galeotti2023")

# record layout: (cell_id, cycle, r0, polarisation, ratio)
CELL, CYCLE, R0, POL, RATIO = 0, 1, 2, 3, 4



def collect():
    records, failures = [], []

    for cell_dir in sorted(ROOT.glob("LiPO_[1-5]")):
        cell_id = cell_dir.name
        for path in sorted(cell_dir.glob("EIS_Charge_discharge/EIS_*/*_EIS.csv")):
            if path.name != "0_EIS.csv":
                continue                      # only 100% SoC — isolate ageing
            cycle = int(path.parent.name.split("_")[1])
            try:
                s = load_spectrum(path, cell_id)
                r, p = r0(s), polarisation(s)
                records.append((cell_id, cycle, r, p, r / p))
            except ValueError as e:
                failures.append((str(path), str(e)))

    return records, failures


def report(records, failures, index, name):
    values = np.array([rec[index] for rec in records])
    print(f"\n=== {name} ===")
    print(f"n {len(values)}   failures {len(failures)}")
    print(f"min {values.min():.4f}  max {values.max():.4f}  "
          f"mean {values.mean():.4f}  median {np.median(values):.4f}")
    for cell_id in sorted({rec[CELL] for rec in records}):
        v = np.array([rec[index] for rec in records if rec[CELL] == cell_id])
        print(f"  {cell_id}  n={len(v):4d}  "
              f"min {v.min():.4f}  max {v.max():.4f}  mean {v.mean():.4f}")


def spread_vs_signal(records, index, name):
    values = np.array([rec[index] for rec in records])
    spread = values.max() - values.min()

    signals = []
    for cell_id in sorted({rec[CELL] for rec in records}):
        v = np.array([rec[index] for rec in records if rec[CELL] == cell_id])
        signals.append(v.max() - v.min())
    signal = np.mean(signals)

    print(f"{name:14s}  spread {spread:.4f}  signal {signal:.4f}  "
          f"ratio {spread / signal:.2f}")


def plot(records, index, name, filename):
    plt.figure(figsize=(8, 5))
    for cell_id in sorted({rec[CELL] for rec in records}):
        v = [rec[index] for rec in records if rec[CELL] == cell_id]
        plt.hist(v, bins=25, alpha=0.6, label=f"{cell_id} (n={len(v)})")
    plt.xlabel(name)
    plt.ylabel("count")
    plt.title(f"{name} across all Galeotti spectra")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f"figures/{filename}", dpi=150)
    plt.close()


if __name__ == "__main__":
    records, failures = collect()

    report(records, failures, R0, "R0 (ohm)")
    report(records, failures, POL, "polarisation (ohm)")
    report(records, failures, RATIO, "R0 / polarisation")

    print("\n=== H1: spread vs within-cell ageing signal ===")
    spread_vs_signal(records, R0, "R0")
    spread_vs_signal(records, POL, "polarisation")
    spread_vs_signal(records, RATIO, "ratio")

    plot(records, R0, "R0 (ohm)", "r0_distribution.png")
    plot(records, POL, "polarisation (ohm)", "polarisation_distribution.png")
    plot(records, RATIO, "R0 / polarisation", "ratio_distribution.png")

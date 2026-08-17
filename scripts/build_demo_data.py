import json
from pathlib import Path
import numpy as np

from mentha.spectra.loaders import load_spectrum

ROOT = Path("data/raw/galeotti2023")
OUT = Path("data/demo_spectra.json")


def build():
    records = []
    for cell_dir in sorted(ROOT.glob("LiPO_[1-5]")):
        cell_id = cell_dir.name
        cap = np.loadtxt(cell_dir / "Capacity" / "Capacity_std.csv")
        initial = cap[0, 1]

        for session in sorted(cell_dir.glob("EIS_Charge_discharge/EIS_*")):
            if not session.is_dir():
                continue
            cycle = int(session.name.split("_")[1])
            match = cap[cap[:, 0] == cycle, 1]
            if len(match) == 0:
                continue

            path = session / "0_EIS.csv"          # index 0 = 100% SoC
            if not path.exists():
                continue

            s = load_spectrum(path, cell_id)
            records.append({
                "cell_id": cell_id,
                "cycle": cycle,
                "true_soh": round(100 * float(match[0]) / initial, 2),
                "frequency_hz": [round(float(v), 4) for v in s.frequency_hz],
                "z_real_ohm": [round(float(v), 7) for v in s.z_real_ohm],
                "z_imag_ohm": [round(float(v), 7) for v in s.z_imag_ohm],
            })
    return records


if __name__ == "__main__":
    records = build()
    OUT.write_text(json.dumps(records))
    kb = OUT.stat().st_size / 1024
    print(f"{len(records)} spectra, {kb:.0f} KB")
    lows = sorted(r["true_soh"] for r in records)[:3]
    print(f"lowest SoH in demo set: {lows}")
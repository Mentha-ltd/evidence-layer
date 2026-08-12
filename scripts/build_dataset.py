from pathlib import Path
import numpy as np
import pandas as pd

from mentha.spectra.loaders import load_spectrum
from mentha.spectra.features import extract

ROOT = Path("data/raw/galeotti2023")


def build():
    rows = []
    for cell_dir in sorted(ROOT.glob("LiPO_[1-5]")):
        cell_id = cell_dir.name
        cap = np.loadtxt(cell_dir / "Capacity" / "Capacity_std.csv")
        initial = cap[0, 1]

        for session in sorted(cell_dir.glob("EIS_Charge_discharge/EIS_*")):
            if not session.is_dir():        # <-- these two lines are new
                continue
            cycle = int(session.name.split("_")[1])
            match = cap[cap[:, 0] == cycle, 1]
            if len(match) == 0:
                continue
            soh = 100 * match[0] / initial

            soc = np.loadtxt(session / "SOC.csv")
            for path in sorted(session.glob("*_EIS.csv")):
                idx = int(path.stem.split("_")[0])
                if idx >= len(soc):
                    continue
                try:
                    s = load_spectrum(path, cell_id)
                    rows.append({
                        "cell_id": cell_id, "cycle": cycle,
                        "soc": float(soc[idx]), "soh": soh,
                        **extract(s),
                    })
                except ValueError:
                    pass

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build()
    df.to_csv("data/dataset.csv", index=False)
    print(df.shape)
    print(df.groupby("cell_id")[["soh"]].describe().round(1))
    print(df.head())
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES=["r0","polarisation","arc_height","arc_peak_freq","lf_slope"]
NOMINAL= 0.099
OUT= Path("models")

def boosting():
    return make_pipeline(StandardScaler(), HistGradientBoostingRegressor(
        max_iter=100, learning_rate=0.05, min_samples_leaf=20,
        max_depth=3, random_state=0))

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv("data/dataset.csv")

    # conformal quantile: each cell serves as calibration once
    residuals = []
    for cal in sorted(df.cell_id.unique()):
        inner, held = df[df.cell_id != cal], df[df.cell_id == cal]
        m = boosting()
        m.fit(inner[FEATURES], inner.soh)
        residuals.extend(np.abs(m.predict(held[FEATURES]) - held.soh))
    q = float(np.quantile(residuals, NOMINAL))

    # final model on everything
    model = boosting()
    model.fit(df[FEATURES], df.soh)

    joblib.dump(model, OUT / "soh_model.joblib")
    (OUT / "calibration.json").write_text(json.dumps({
        "nominal": NOMINAL,
        "half_width": round(q, 3),
        "n_cells": int(df.cell_id.nunique()),
        "n_spectra": int(len(df)),
        "features": FEATURES,
        "trained_on": "Galeotti et al. 2023",
    }, indent=2))

    print(f"half-width ±{q:.2f}%  ({len(df)} spectra, {df.cell_id.nunique()} cells)")
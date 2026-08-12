import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES = ["r0", "polarisation", "arc_height", "arc_peak_freq", "lf_slope"]


def leave_one_cell_out(df, features, name):
    print(f"\n=== {name}  (n={len(df)}, {len(features)} features) ===")
    errors = []
    for held in sorted(df.cell_id.unique()):
        train = df[df.cell_id != held]
        test = df[df.cell_id == held]

        model = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))
        model.fit(train[features], train.soh)
        pred = model.predict(test[features])

        mae = np.abs(pred - test.soh).mean()
        errors.append(mae)
        print(f"  held out {held}  n={len(test):4d}  MAE {mae:5.2f}%")

    print(f"  mean MAE {np.mean(errors):5.2f}%   worst {max(errors):5.2f}%")
    return np.mean(errors)


if __name__ == "__main__":
    df = pd.read_csv("data/dataset.csv")

    # trivial baseline: always predict the training mean
    baseline = np.abs(df.soh - df.soh.mean()).mean()
    print(f"baseline (predict the mean): MAE {baseline:.2f}%")

    leave_one_cell_out(df, FEATURES, "A — no SoC knowledge")
    leave_one_cell_out(df, FEATURES + ["soc"], "B — SoC known")
    leave_one_cell_out(df[df.soc > 0.99], FEATURES, "C — preconditioned to 100% SoC")
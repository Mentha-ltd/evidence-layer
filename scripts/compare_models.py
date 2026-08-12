import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES = ["r0", "polarisation", "arc_height", "arc_peak_freq", "lf_slope"]


def ridge():
    return make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))


def boosting():
    return make_pipeline(
        StandardScaler(),
        HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05,
                                      min_samples_leaf=5, random_state=0),
    )


def leave_one_cell_out(df, make_model):
    errors = {}
    for held in sorted(df.cell_id.unique()):
        train = df[df.cell_id != held]
        test = df[df.cell_id == held]
        model = make_model()
        model.fit(train[FEATURES], train.soh)
        pred = model.predict(test[FEATURES])
        errors[held] = np.abs(pred - test.soh).mean()
    return errors


if __name__ == "__main__":
    df = pd.read_csv("data/dataset.csv")

    baseline = np.abs(df.soh - df.soh.mean()).mean()
    r = leave_one_cell_out(df, ridge)
    b = leave_one_cell_out(df, boosting)

    print(f"baseline (predict the mean)  MAE {baseline:.2f}%\n")
    print(f"{'cell':10s} {'ridge':>8s} {'boosting':>10s} {'delta':>8s}")
    for cell in sorted(r):
        print(f"{cell:10s} {r[cell]:7.2f}% {b[cell]:9.2f}% {b[cell]-r[cell]:+7.2f}")

    print(f"\n{'mean':10s} {np.mean(list(r.values())):7.2f}% "
          f"{np.mean(list(b.values())):9.2f}% "
          f"{np.mean(list(b.values()))-np.mean(list(r.values())):+7.2f}")
    print(f"{'worst':10s} {max(r.values()):7.2f}% {max(b.values()):9.2f}%")
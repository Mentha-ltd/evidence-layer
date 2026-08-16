import numpy as np
import pandas as pd
from scipy.spatial.distance import mahalanobis
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES = ["r0", "polarisation", "arc_height", "arc_peak_freq", "lf_slope"]


def boosting():
    return make_pipeline(StandardScaler(), HistGradientBoostingRegressor(
        max_iter=100, learning_rate=0.05, min_samples_leaf=20,
        max_depth=3, random_state=0))


def population_distance(train_X, test_X):
    """Mahalanobis distance from the training feature distribution.
    Accounts for feature covariance, so no scaling needed."""
    mu = train_X.mean(axis=0)
    inv_cov = np.linalg.pinv(np.cov(train_X.T))
    return np.array([mahalanobis(x, mu, inv_cov) for x in test_X])


if __name__ == "__main__":
    df = pd.read_csv("data/dataset.csv")

    rows = []
    all_dist, all_err = [], []

    for held in sorted(df.cell_id.unique()):
        train = df[df.cell_id != held]
        test = df[df.cell_id == held]

        model = boosting()
        model.fit(train[FEATURES], train.soh)
        err = np.abs(model.predict(test[FEATURES]) - test.soh.values)

        dist = population_distance(train[FEATURES].values, test[FEATURES].values)

        rows.append((held, dist.mean(), err.mean()))
        all_dist.extend(dist)
        all_err.extend(err)

    print(f"{'cell':10s} {'mean distance':>14s} {'MAE':>8s}")
    for cell, d, e in sorted(rows, key=lambda r: r[1]):
        print(f"{cell:10s} {d:14.2f} {e:7.2f}%")

    d = np.array([r[1] for r in rows])
    e = np.array([r[2] for r in rows])
    print(f"\nper-cell correlation (n=5): {np.corrcoef(d, e)[0,1]:+.2f}")
    print(f"per-spectrum correlation (n={len(all_dist)}): "
          f"{np.corrcoef(all_dist, all_err)[0,1]:+.2f}")
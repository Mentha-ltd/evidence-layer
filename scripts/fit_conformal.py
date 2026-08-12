import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES = ["r0", "polarisation", "arc_height", "arc_peak_freq", "lf_slope"]
NOMINAL = 0.90


def ridge():
    return make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))


def boosting():
    # conventional defaults, NOT the best row from the sweep — picking that
    # would be selecting a hyperparameter on the held-out folds
    return make_pipeline(
        StandardScaler(),
        HistGradientBoostingRegressor(max_iter=100, learning_rate=0.05,
                                      min_samples_leaf=20, max_depth=3,
                                      random_state=0),
    )


def fit(train, make_model):
    m = make_model()
    m.fit(train[FEATURES], train.soh)
    return m


def calibrate(pool, make_model, nominal):
    """Cross-conformal: each cell in the pool serves as calibration once."""
    residuals = []
    for cal_cell in sorted(pool.cell_id.unique()):
        inner = pool[pool.cell_id != cal_cell]
        cal = pool[pool.cell_id == cal_cell]
        pred = fit(inner, make_model).predict(cal[FEATURES])
        residuals.extend(np.abs(pred - cal.soh))
    return np.quantile(residuals, nominal)


def run(df, make_model, name):
    print(f"\n=== {name}  (nominal {NOMINAL:.0%}) ===")
    covs = []
    for test_cell in sorted(df.cell_id.unique()):
        pool = df[df.cell_id != test_cell]
        test = df[df.cell_id == test_cell]

        q = calibrate(pool, make_model, NOMINAL)
        pred = fit(pool, make_model).predict(test[FEATURES])
        covered = (np.abs(pred - test.soh) <= q).mean()
        covs.append(covered)

        print(f"  {test_cell}  half-width ±{q:5.2f}%  "
              f"coverage {covered:6.1%}  n={len(test)}")

    print(f"  worst coverage {min(covs):.1%}")


def sweep_nominal(df, make_model):
    """What nominal level delivers >=90% realised coverage on every cell?"""
    print("\n=== nominal vs realised (boosting) ===")
    for nominal in [0.90, 0.93, 0.95, 0.97, 0.99]:
        covs, widths = [], []
        for test_cell in sorted(df.cell_id.unique()):
            pool = df[df.cell_id != test_cell]
            test = df[df.cell_id == test_cell]

            q = calibrate(pool, make_model, nominal)
            pred = fit(pool, make_model).predict(test[FEATURES])
            covs.append((np.abs(pred - test.soh) <= q).mean())
            widths.append(q)

        print(f"  nominal {nominal:.0%}  worst realised {min(covs):6.1%}  "
              f"mean half-width ±{np.mean(widths):.2f}%")

THRESHOLD = 80.0   # second-life cutoff, % SoH


def decision_rates(df, make_model, nominal=0.99):
    """At an honest interval width, how many modules can we actually decide?"""
    print(f"\n=== decisions at {nominal:.0%} nominal (threshold {THRESHOLD:.0f}%) ===")

    rows = []
    for test_cell in sorted(df.cell_id.unique()):
        pool = df[df.cell_id != test_cell]
        test = df[df.cell_id == test_cell]

        q = calibrate(pool, make_model, nominal)
        pred = fit(pool, make_model).predict(test[FEATURES])

        sellable = pred - q >= THRESHOLD
        scrap = pred + q < THRESHOLD
        abstain = ~(sellable | scrap)

        truth = test.soh.values >= THRESHOLD
        false_sellable = (sellable & ~truth).sum()
        false_scrap = (scrap & truth).sum()

        rows.append((test_cell, len(test), sellable.mean(), scrap.mean(),
                     abstain.mean(), false_sellable, false_scrap))

        print(f"  {test_cell}  n={len(test):4d}  "
              f"sellable {sellable.mean():5.1%}  scrap {scrap.mean():5.1%}  "
              f"abstain {abstain.mean():5.1%}  "
              f"false-sellable {false_sellable}  false-scrap {false_scrap}")

    total = sum(r[1] for r in rows)
    dec = sum(r[1] * (r[2] + r[3]) for r in rows) / total
    fs = sum(r[5] for r in rows)
    fc = sum(r[6] for r in rows)
    print(f"\n  overall: decided {dec:.1%}, abstained {1-dec:.1%}")
    print(f"  false-sellable {fs} (bad module passed as good)")
    print(f"  false-scrap    {fc} (good module rejected)")

if __name__ == "__main__":
    df = pd.read_csv("data/dataset.csv")
    run(df, ridge, "ridge")
    run(df, boosting, "boosting")
    sweep_nominal(df, boosting)
    decision_rates(df, boosting)
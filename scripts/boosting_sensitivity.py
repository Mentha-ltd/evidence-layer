import numpy as np
import pandas as pd 
from itertools import product
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES= ['r0', 'polarisation','arc_height','arc_peak_freq','lf_slope']

def loco(df,model_fn):
    errs=[]
    for held in sorted(df.cell_id.unique()):
        tr, te= df[df.cell_id != held], df[df.cell_id==held]
        m=model_fn()
        m.fit(tr[FEATURES], tr.soh)
        errs.append(np.abs(m.predict(te[FEATURES]) - te.soh).mean())
    return np.mean(errs), max(errs)

if __name__=="__main__":
    df = pd.read_csv("data/dataset.csv")

    print(f"{'iters':>6} {'lr':>6} {'leaf':>5} {'depth':>6} {'mean':>7} {'worst':>7}")
    grid = product([50, 100, 300, 600], [0.02, 0.05, 0.1], [5, 20], [None, 3])
    results = []
    for it, lr, leaf, depth in grid:
        def make(it=it, lr=lr, leaf=leaf, depth=depth):
            return make_pipeline(StandardScaler(), HistGradientBoostingRegressor(
                max_iter=it, learning_rate=lr, min_samples_leaf=leaf,
                max_depth=depth, random_state=0))
        mean, worst = loco(df, make)
        results.append((mean, worst, it, lr, leaf, depth))
        print(f"{it:6d} {lr:6.2f} {leaf:5d} {str(depth):>6} {mean:6.2f}% {worst:6.2f}%")

    means = [r[0] for r in results]
    worsts = [r[1] for r in results]
    print(f"\nacross {len(results)} configs:")
    print(f"  mean MAE  range {min(means):.2f}% – {max(means):.2f}%")
    print(f"  worst MAE range {min(worsts):.2f}% – {max(worsts):.2f}%")
    print(f"  configs beating ridge's 3.13% mean: "
          f"{sum(m < 3.13 for m in means)}/{len(results)}")
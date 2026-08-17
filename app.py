
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


import json
from pathlib import Path

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from mentha.spectra.spectrum import Spectrum
from mentha.spectra.corruption import add_series_resistance
from mentha.pipeline import grade, verify, THRESHOLD

st.set_page_config(page_title="Mentha — Evidence Layer", layout="wide")


@st.cache_data
def load_demo():
    return json.loads(Path("data/demo_spectra.json").read_text())


records = load_demo()

st.title("Mentha — Evidence Layer v0")
st.caption(
    "Replayed from the Galeotti et al. 2023 public dataset. "
    "**Not a live instrument measurement.** Five laboratory pouch cells, "
    "1.1 Ah — not EV modules."
)

# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Measurement")
    cells = sorted({r["cell_id"] for r in records})
    cell = st.selectbox("Cell", cells)

    options = sorted((r for r in records if r["cell_id"] == cell),
                     key=lambda r: r["cycle"])
    chosen = st.selectbox(
        "Cycle", options,
        format_func=lambda r: f"{r['cycle']} — true SoH {r['true_soh']:.1f}%")

    st.header("Decision threshold")
    threshold = st.slider(
        "Minimum acceptable SoH (%)", 60, 95, int(THRESHOLD),
        help="80% is the automotive retirement convention. "
             "A stationary buyer may accept far less.")

    st.header("Inject a fault")
    st.caption("Simulates a poorly seated probe adding resistance in series.")
    r_add = st.slider("Contact resistance (mΩ)", 0, 80, 0, step=2) / 1000

spectrum = Spectrum(
    frequency_hz=np.array(chosen["frequency_hz"]),
    z_real_ohm=np.array(chosen["z_real_ohm"]),
    z_imag_ohm=np.array(chosen["z_imag_ohm"]),
    cell_id=chosen["cell_id"],
)
if r_add > 0:
    spectrum = add_series_resistance(spectrum, r_add)

record = grade(spectrum, threshold=threshold)

# ---------------- outcome ----------------
STYLE = {
    "sellable": ("Sellable", "success"),
    "scrap": ("Scrap", "error"),
    "abstain": ("No decision", "warning"),
    "refused_measurement": ("Measurement refused", "error"),
}
label, kind = STYLE[record["outcome"]]

left, right = st.columns([1, 1])

with left:
    st.subheader(label)
    getattr(st, kind)(record["reason"])

    if "soh" in record:
        lo, hi = record["interval"]
        st.metric("State of health — inferred", f"{record['soh']:.1f}%",
                  delta=f"± {record['half_width']:.2f}%", delta_color="off")
        st.caption(f"Interval {lo:.1f}% – {hi:.1f}%  ·  "
                   f"threshold {threshold}%  ·  90% coverage, "
                   "leave-one-cell-out")

    st.metric("Internal resistance — measured, not inferred",
              f"{record['features']['r0'] * 1000:.1f} mΩ")
    st.caption(
        f"Carries no model uncertainty. Determines power capability: "
        f"at 50 A, {record['features']['r0'] * 50:.2f} V sag and "
        f"{record['features']['r0'] * 2500:.0f} W loss. "
        "Temperature not recorded in this dataset."
    )

    st.markdown("**Validity checks**")
    for g in record["gates"]:
        mark = "PASS" if g["passed"] else "FAIL"
        st.write(f"`{mark}` **{g['gate']}** — {g['value']:.4f} "
                 f"(expected {g['threshold']})")
        if not g["passed"]:
            st.caption(g["reason"])

with right:
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(spectrum.z_real_ohm, -spectrum.z_imag_ohm, "o-", ms=4,
            color="#0E7C5A")
    ax.set_xlabel("Z' (ohm)")
    ax.set_ylabel("-Z'' (ohm)")
    ax.set_aspect("equal")
    ax.set_title("Measured spectrum — always shown")
    st.pyplot(fig)
    st.caption(f"True SoH for this measurement: {chosen['true_soh']:.1f}% "
               "(known here because it is public lab data)")

# ---------------- record ----------------
st.divider()
st.subheader("Provenance record")
st.caption("Everything needed to re-derive this grade years from now.")

c1, c2 = st.columns([1, 3])
with c1:
    if st.button("Verify this record"):
        if verify(record):
            st.success("PASS — re-derived from the stored spectrum")
        else:
            st.error("FAIL")
    st.code(record["hash"], language=None)

with c2:
    display = {k: v for k, v in record.items()
               if k not in ("frequency_hz", "z_real_ohm", "z_imag_ohm")}
    display["raw_spectrum"] = f"{record['n_points']} points (stored, omitted here)"
    st.json(display, expanded=False)
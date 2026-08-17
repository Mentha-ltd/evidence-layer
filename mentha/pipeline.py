import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from mentha.spectra.features import extract
from mentha.gates.contact import contact_gate

MODEL_DIR = Path("models")
THRESHOLD = 80.0

_model = joblib.load(MODEL_DIR / "soh_model.joblib")
_cal = json.loads((MODEL_DIR / "calibration.json").read_text())
FEATURES = _cal["features"]
HALF_WIDTH = _cal["half_width"]


def grade(spectrum, operator="demo",threshold=THRESHOLD):
    """Everything the interface needs, in one dict. No logic in the UI."""
    gates = [contact_gate(spectrum)]
    feats = extract(spectrum)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cell_id": spectrum.cell_id,
        "operator": operator,
        "n_points": len(spectrum),
        "frequency_hz": spectrum.frequency_hz.tolist(),
        "z_real_ohm": spectrum.z_real_ohm.tolist(),
        "z_imag_ohm": spectrum.z_imag_ohm.tolist(),
        "features": {k: round(float(v), 6) for k, v in feats.items()},
        "gates": [g.__dict__ for g in gates],
        "model": _cal,
    }

    if not all(g.passed for g in gates):
        failed = next(g for g in gates if not g.passed)
        record.update(outcome="refused_measurement", reason=failed.reason)
        return _seal(record)

    
    x = pd.DataFrame([[feats[f] for f in FEATURES]], columns=FEATURES)
    soh = float(_model.predict(x)[0])
    low, high = soh - HALF_WIDTH, min(soh + HALF_WIDTH, 100.0)

    if low >= threshold:
        outcome = "sellable"
        reason = f"Entire interval clears the {threshold:.0f}% threshold."
    elif high < threshold:
        outcome = "scrap"
        reason = f"Entire interval sits below the {threshold:.0f}% threshold."
    else:
        outcome = "abstain"
        reason = (f"Interval spans the {threshold:.0f}% threshold. "
                  "A full discharge test is needed to decide.")

  
    record.update(outcome=outcome, reason=reason, soh=round(soh, 2),
                  interval=[round(low, 2), round(high, 2)],
                  half_width=HALF_WIDTH, threshold=threshold)
    return _seal(record)


def _seal(record):
    body = json.dumps(record, sort_keys=True).encode()
    record["hash"] = hashlib.sha256(body).hexdigest()[:16]
    return record


def verify(record):
    """Re-derive the grade from the stored raw spectrum."""
    from mentha.spectra.spectrum import Spectrum

    s = Spectrum(
        frequency_hz=np.array(record["frequency_hz"]),
        z_real_ohm=np.array(record["z_real_ohm"]),
        z_imag_ohm=np.array(record["z_imag_ohm"]),
        cell_id=record["cell_id"],
    )
    fresh = grade(s, operator=record["operator"],
                  threshold=record.get("threshold", THRESHOLD))
    return (fresh["outcome"] == record["outcome"]
            and fresh.get("soh") == record.get("soh"))
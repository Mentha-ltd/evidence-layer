import numpy as np
import pytest
from mentha.spectra.spectrum import Spectrum
from mentha.spectra.features import r0 , arc_height, polarisation

from mentha.spectra.corruption import add_series_resistance


def test_r0_interpolates_the_zero_crossing():
    s = Spectrum(
        frequency_hz=np.array([1000.0, 100.0, 10.0]),
        z_real_ohm=np.array([0.010, 0.020, 0.030]),
        z_imag_ohm=np.array([0.002, -0.002, -0.005]),
        cell_id="TEST",
    )
    assert r0(s) == pytest.approx(0.015)

def test_features_are_contact_invariant():
    s = Spectrum(
        frequency_hz=np.array([1000.0, 100.0, 10.0, 1.0]),
        z_real_ohm=np.array([0.010, 0.020, 0.030, 0.040]),
        z_imag_ohm=np.array([0.002, -0.002, -0.008, -0.003]),
        cell_id="TEST",
    )
    bad = add_series_resistance(s, 0.020)

    assert arc_height(bad) == pytest.approx(arc_height(s))
    assert polarisation(bad) == pytest.approx(polarisation(s))
    assert r0(bad) == pytest.approx(r0(s) + 0.020)
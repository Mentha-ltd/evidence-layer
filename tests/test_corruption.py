import numpy as np
import pytest
from mentha.spectra.spectrum import Spectrum
from mentha.spectra.corruption import add_series_resistance, truncate, add_noise, add_drift


def make_spectrum():
    return Spectrum(
        frequency_hz=np.array([1000.0, 100.0, 10.0]),
        z_real_ohm=np.array([0.010, 0.020, 0.030]),
        z_imag_ohm=np.array([-0.002, -0.003, -0.001]),
        cell_id="TEST",
    )


def test_series_resistance_shifts_real_only():
    s = make_spectrum()
    bad = add_series_resistance(s, 0.005)

    assert bad.z_real_ohm[0] == pytest.approx(0.015)
    assert bad.z_imag_ohm[0] == pytest.approx(-0.002)
    assert s.z_real_ohm[0] == pytest.approx(0.010)

def test_truncate_drops_low_frequencies():
    s = make_spectrum()
    short = truncate(s, 2)

    assert len(short) == 2
    assert short.frequency_hz[0] == pytest.approx(1000.0)
    assert short.frequency_hz[-1] == pytest.approx(100.0)
    assert len(s) == 3

def test_noise_is_reproducible():
    s = make_spectrum()
    a = add_noise(s, sigma=0.001, seed=42)
    b = add_noise(s, sigma=0.001, seed=42)
    c = add_noise(s, sigma=0.001, seed=99)

    assert np.allclose(a.z_real_ohm, b.z_real_ohm)
    assert not np.allclose(a.z_real_ohm, c.z_real_ohm)
    assert np.allclose(s.z_real_ohm, [0.010, 0.020, 0.030])

def test_drift_is_zero_at_start_and_full_at_end():
    s = make_spectrum()
    bad = add_drift(s, 0.006)

    assert bad.z_real_ohm[0] == pytest.approx(0.010)
    assert bad.z_real_ohm[-1] == pytest.approx(0.036)
    assert bad.z_imag_ohm[0] == pytest.approx(-0.002)
    assert s.z_real_ohm[-1] == pytest.approx(0.030)
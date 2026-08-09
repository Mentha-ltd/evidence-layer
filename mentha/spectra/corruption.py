import numpy as np
from mentha.spectra.spectrum import Spectrum


def add_series_resistance(spectrum, r_ohm):

    return Spectrum(
        frequency_hz=spectrum.frequency_hz.copy(),
        z_real_ohm=spectrum.z_real_ohm + r_ohm,
        z_imag_ohm=spectrum.z_imag_ohm.copy(),
        cell_id=spectrum.cell_id,
        temperature_c=spectrum.temperature_c
    )

def truncate(spectrum, n_points):
    """A sweep cut short — time pressure, or an aborted measurement."""
    return Spectrum(
        frequency_hz=spectrum.frequency_hz[:n_points].copy(),
        z_real_ohm=spectrum.z_real_ohm[:n_points].copy(),
        z_imag_ohm=spectrum.z_imag_ohm[:n_points].copy(),
        cell_id=spectrum.cell_id,
        temperature_c=spectrum.temperature_c,
    )

def add_noise(spectrum, sigma, seed=0):
    """Instrument noise, or electrical interference in a warehouse."""
    rng = np.random.default_rng(seed)
    return Spectrum(
        frequency_hz=spectrum.frequency_hz.copy(),
        z_real_ohm=spectrum.z_real_ohm + rng.normal(0, sigma, len(spectrum)),
        z_imag_ohm=spectrum.z_imag_ohm + rng.normal(0, sigma, len(spectrum)),
        cell_id=spectrum.cell_id,
        temperature_c=spectrum.temperature_c,
    )

def add_drift(spectrum, total_shift):
    """The cell changing DURING the sweep — warming, or SoC relaxing.

    Measurements run sequentially from high to low frequency, so a ramp
    across the array index means later (slower) points describe a
    different system than earlier ones. This is what breaks the
    stationarity assumption.
    """
    ramp = np.linspace(0, total_shift, len(spectrum))
    return Spectrum(
        frequency_hz=spectrum.frequency_hz.copy(),
        z_real_ohm=spectrum.z_real_ohm + ramp,
        z_imag_ohm=spectrum.z_imag_ohm.copy(),
        cell_id=spectrum.cell_id,
        temperature_c=spectrum.temperature_c,
    )
from dataclasses import dataclass

import numpy as np

@dataclass

class Spectrum:
    frequency_hz: np.ndarray
    z_real_ohm: np.ndarray
    z_imag_ohm: np.ndarray
    cell_id: str
    temperature_c: float | None= None

    def __post_init__(self):
        #validation and ordering
        n_freq=len(self.frequency_hz)
        n_z_real=len(self.z_real_ohm)
        n_z_imag=len(self.z_imag_ohm)
      # compare and raise if there are diff
        if not (n_freq == n_z_real == n_z_imag):
            raise ValueError("frequency_hz, z_real_ohm and z_imag_ohm must have the same length")
        if np.any(self.frequency_hz <= 0):
            raise ValueError('frequency_hz must be positive')

        if self.frequency_hz[0]< self.frequency_hz[-1]:
            #ascending reverse all three
            self.frequency_hz=self.frequency_hz[::-1]
            self.z_real_ohm=self.z_real_ohm[::-1]
            self.z_imag_ohm=self.z_imag_ohm[::-1]

    def __len__(self):
        return len(self.frequency_hz)

    @property
    def impedance(self):
        return self.z_real_ohm + 1j * self.z_imag_ohm
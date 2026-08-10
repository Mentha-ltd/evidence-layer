import numpy as np


def r0(spectrum):
    """Real impedance where the imaginary part crosses zero.

    This is the ohmic resistance — the point where the cell behaves as a
    pure resistance, with no capacitive or inductive component.
    """
    zr = spectrum.z_real_ohm
    zi = spectrum.z_imag_ohm

    # Find where zi changes sign. np.sign() gives -1/0/+1 per element;
    # np.diff() of that is non-zero exactly at a sign change.
    crossings = np.where(np.diff(np.sign(zi)) != 0)[0]

    if len(crossings) == 0:
        # No zero crossing means the imaginary part never changes sign, so
        # there is no frequency at which the cell behaves as a pure
        # resistance within this sweep. R0 is not measurable here.
        # Returning zr[0] would substitute a different quantity under the
        # same name — the caller would have no way to know.
        raise ValueError(
            f"no zero crossing in z_imag for {spectrum.cell_id}; "
            f"R0 is not measurable from this spectrum"
        )

    # Take the first crossing.
    i = crossings[0]

    # How far between point i and i+1 does zero fall?
    fraction = zi[i] / (zi[i] - zi[i + 1])

    # Interpolate z_real the same distance.
    return zr[i] + fraction * (zr[i + 1] - zr[i])

def arc_height(spectrum):
    """Peak of -Z_imag. Purely imaginary, so series resistance can't touch it."""
    return float(np.max(-spectrum.z_imag_ohm))


def polarisation(spectrum):
    """Z_real from R0 out to the lowest frequency. Both ends shift equally
    under series resistance, so the difference is invariant."""
    return float(spectrum.z_real_ohm[-1] - r0(spectrum))
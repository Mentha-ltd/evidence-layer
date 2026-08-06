from pathlib import Path
import pytest

from mentha.spectra.loaders import load_spectrum

DATA= Path("data/raw/galeotti2023/LiPO_1/EIS_Charge_discharge/EIS_90/6_EIS.csv")

pytestmark= pytest.mark.skipif(not DATA.exists(), reason="dataset not present")


def test_loads_a_spectrum():
    s=load_spectrum(DATA, cell_id= "LiPO_1")
    assert len(s)== 45
    assert s.cell_id== "LiPO_1"


def test_frequencies_descending():
    s=load_spectrum(DATA, cell_id= "LiPO_1")
    assert s.frequency_hz[0]> s.frequency_hz[-1]


def test_columns_not_swapped():
    s=load_spectrum(DATA, cell_id= "LiPO_1")
    assert s.frequency_hz[0] == pytest.approx(4998.181)
    assert s.z_real_ohm[0] == pytest.approx(0.0845769)
    assert s.z_imag_ohm[0] == pytest.approx(0.0041859)
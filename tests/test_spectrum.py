import	numpy	as	np
import	pytest
from	mentha.spectra.spectrum	import	Spectrum
def	arrays(n=5):
				f	=	np.array([1000.0,	100.0,	10.0,	1.0,	0.1])[:n]
				zr	=	np.linspace(0.010,	0.050,	n)
				zi	=	np.linspace(-0.020,	0.000,	n)
				return	f,	zr,	zi
def	test_holds_its_arrays():
				f,	zr,	zi	=	arrays()
				s	=	Spectrum(f,	zr,	zi,	cell_id="B0005")
				assert	len(s)	==	5
				assert	s.cell_id	==	"B0005"
def	test_mismatched_lengths_rejected():
				f,	zr,	zi	=	arrays()
				with	pytest.raises(ValueError):
								Spectrum(f[:3],	zr,	zi,	cell_id="B0005")
def	test_non_positive_frequency_rejected():
				f,	zr,	zi	=	arrays()
				f	=	f.copy()
				f[2]	=	0.0
				with	pytest.raises(ValueError):
								Spectrum(f,	zr,	zi,	cell_id="B0005")
def	test_frequencies_stored_descending():
				f,	zr,	zi	=	arrays()
				s	=	Spectrum(f[::-1],	zr[::-1],	zi[::-1],	cell_id="B0005")
				assert	s.frequency_hz[0]	>	s.frequency_hz[-1]
				assert	s.z_real_ohm[0]	==	pytest.approx(0.010)
def	test_impedance_is_complex():
				f,	zr,	zi	=	arrays()
				s	=	Spectrum(f,	zr,	zi,	cell_id="B0005")
				assert	np.iscomplexobj(s.impedance)
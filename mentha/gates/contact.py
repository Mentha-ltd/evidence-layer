from dataclasses import dataclass
from mentha.spectra.features import r0

R0_MIN,R0_MAX= 0.060 , 0.130

@dataclass

class GateResult:
    gate:str
    passed: bool
    reason: str
    value: float
    threshold: str 

def contact_gate(spectrum):
    """Reject a spectrum whose ohmic resistance is implausible for this cell type."""
    value =r0(spectrum)
    passed =R0_MIN <=value <=R0_MAX
    if passed:
        reason ='Ohmic resistance within the expected range.'
    elif value > R0_MAX:
        reason=("Ohmic resistance too high — likely a poorly seated probe "
                  "or an oxidised terminal. Reseat and measure again.")

    else:
        reason="Ohmic resistance too low — check the connection and cell type."

    return GateResult("contact", passed,reason,value,
                      f"{R0_MIN:.3f}-{R0_MAX:.3f} ohm")


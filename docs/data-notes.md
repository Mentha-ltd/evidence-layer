# Data notes - Galeotti et al. 2023

Source : Mendeley 10.17632/stcppt2r68.1
Five BAK LP-503562-IS-3 LiPo cells, 1.1 Ah nominal

tags: [observed] I ran a command and saw it
[documented] The README or a paper says no.
[inferred] I worked it out
[unknown] Still open.

## Structure

-[observed] Each LiPo\_# has Capacity/,Discharge_curve/, EIS_Charge_discharge/ -[observed] EIS folders: EIS_0, 45, 90, 116, 135, 180, 204- matches EIS_cycles.csv -[observed] Each EIS folder: 0_EIS.csv .. 9_EIS.csv plus SOC.csv

## The spectrum files

-[observed] 3columns, no header, WHITESPACE seperated despite the .csv name -[observed] 45 rows: confirmed twice -wc- l, and the frequency ratio 1.2587 -[observed] Column 1 frequency Hz, descending from ~4998 -[inferred] Column 2 real impedance in ohms (~0.085 is sensible for a 1.1 Ah cell; units atre not stated anywhere) -[observed] Column 3 imaginary, positive at high frequency, crosses zero ~ 2500-3000

## SOH definition

-[obeserved] Capacity_std.csv: cycle number, capacity in Ah -[observed] LiPo_1 at cycle 0 mesasures 1.0266 Ah against 1.1 Ah nominal

- DECISION: SoH = capacity_now / capacity_at_cycle_0 (measured, this cell)
- REASON: isolates degradation from manufacturing spread. This cell was born at
  1.0266 Ah against 1.1 Ah nominal; nothing had degraded at cycle 0, so nominal
  would score a new cell at 93%.
- ALWAYS carried with the number: the discharge protocol (1 A CC to 2.75 V) and
  which denominator was used. A percentage without its convention is incomplete.
- [limitation] Requires a beginning-of-life measurement. Unavailable for a used
  module with no history — the field product will need a different reference,
  which is an open question for Phase 4.

## Sample size

- [observed] Spectra per cell: LiPO_1 63, LiPO_2 170, LiPO_3 109, LiPO_4 79, LiPO_5 130 (551 total)
- [inferred] The real sample size is the number of EIS sessions, not spectra —
  the ~10 spectra in one session share one health value
- [inferred] Cells were cycled and sampled on different schedules, so cycle number
  is not comparable across cells. Use measured capacity for health.
- [inferred] LiPO_2 has ~3x the spectra of LiPO_1. Weight by cell, not by spectrum,
  and report per-cell error separately in Phase 2.

- [observed] 57 EIS sessions total: LiPO_1 7, LiPO_2 17, LiPO_3 12, LiPO_4 8, LiPO_5 13
- [observed] Spectra per session is ~9-10, NOT fixed. LiPO_2 and LiPO_5 are always 10;
  the others vary. Loader must read what's present, not assume 10.
- [inferred] 57 distinct health states is the real sample size for SoH modelling.

-[reasoning] Arc= interfacial charge transfer (desolvation + electron transfer at the surface)
Tail = solid_state diffusion inside particle. Different processes. -[reasoning] R_ct peaks at BOTH SOC extremes -at either end one electrodes lacks ions and the other lacks vacancies.

- [reasoning] R_ct responds to ageing AND SoC. Not a SoC-only feature. Confounded,
  not useless.
- [reasoning] Degradation raises R0, not the reverse. R0 is a proxy — a failure mode
  that spares R0 would be invisible to it.
- [unknown] Cathode chemistry. Not stated in the dataset.

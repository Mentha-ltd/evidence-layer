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

- [observed] LiPO_1 R0 (Z_real at highest freq) rises monotonically across all 7
  sessions: 0.0796 → 0.0905 Ω as SoH falls 100% → 79%. No inversions.
- [observed] 21% capacity loss ↔ 13.7% R0 increase.
- [observed] Low-frequency end is NOT monotonic — cycle 45 (0.1198) sits below
  cycle 0 (0.1215). Cause unknown: noise, early-life SEI effect, or fixture.
- [observed] All 7 sessions have n=45. Frequency grid is uniform.
- [lesson] The seven-curve figure hid the diffusion tails behind an opaque legend.
  Confirm figures against printed numbers.

- [decision] Second dataset (Zhang 2020, Zenodo 3633835) deferred to end of Phase 2.
  Needed for: the OOD gate, and a held-out generalisation claim.
- [constraint] Features must be defined physically, not by array index — Zhang's
  frequency grid will differ from Galeotti's 45 points.

## Session hypotheses — 10 August 2026

### H1: polarisation is more identifiable than R0

- BELIEF: polarisation resistance (Z_real[-1] − R0) separates health across cells
  better than absolute R0. Grounds: in LiPO_1 it grew 21% over life vs R0's 13.7%,
  and it is invariant to series contact resistance by construction.
- TEST: compute polarisation for all 549 spectra; compare population spread against
  within-cell ageing signal, exactly as done for R0.
- DECIDED IN ADVANCE — spread ÷ signal:
  < 1.0 → better than R0; blind grading of an unknown module becomes plausible
  1–2 → improvement but not identifiable alone; needs a multi-feature model
  > 2.0 → no better than R0; manufacturing spread dominates
  > R0 scored 2.0. That is the bar.
- PRODUCT: decides whether a grade requires a declared module type. Above 2.0, the
  operator must state what the module is — which changes the workflow, the UI, and
  what the certificate can claim.

### H2: the R0/polarisation ratio detects contact faults

- BELIEF: the ratio is stable under ageing but shifts under series resistance,
  because ageing raises both terms while a bad probe raises only the numerator.
  LiPO_1 ran 1.90 → 1.78 across its whole life; a 20 mΩ fault would give ~2.38.
- TEST: compute the ratio across all 549 real spectra to establish the normal band.
  Inject series resistance at 0.005 / 0.011 / 0.020 / 0.050 Ω and find the smallest
  fault the band rejects.
- DECIDED IN ADVANCE: worth shipping only if it catches faults at or below 0.011 Ω
  (the size of the entire ageing signal). Larger, and it remains a gross-fault
  filter — no better than the absolute-R0 gate.
- PRODUCT: this is the refusal screen. No detection threshold, no refusal, and the
  demo has nothing behind its central claim.

### What would kill this line

If the ratio band across real cells is wider than the shift produced by a 0.05 Ω
fault, no single-measurement gate works. The fallback is measure-reseat-measure,
which is a workflow change and a hardware requirement, not a software feature.

### H1 RESULT — not supported (10 Aug 2026, n=57 at 100% SoC)

- R0 spread÷signal 1.51; polarisation 1.59. Polarisation is marginally worse.
- Both in the "multi-feature model required" band. No single scalar identifies
  health across cells.

### H2 RESULT — fails criterion

- Ratio band at fixed SoC: 1.81–3.40. Trips at ~0.034 Ω series resistance,
  3x the ageing signal. Criterion was 0.011 Ω.
- Filtering to fixed SoC tightened the lower bound (1.02→1.81) but not the upper.
- CONSEQUENCE: single-measurement contact gate is a gross-fault filter only.
  Medium faults need measure-reseat-measure, or four-wire sensing in hardware.

### Open

- LiPO_5 is an outlier: ratio mean 2.93 vs 1.9–2.4 elsewhere, owns the 3.40 max
  that breaks the gate. Excluding it moves sensitivity to ~0.016 Ω. Why?

## Pre-registered test — results, 10 August 2026

Both hypotheses were registered before the measurement was run (see above).
Both failed their stated criteria. Recorded as negative results.

### Method

n = 57 spectra, one per EIS session, index 0 only (SoC = 1.000 in every session)
to remove SoC as a confounder. Discrimination metric: between-cell spread
divided by mean within-cell ageing range.

### H1 — univariate identifiability: NOT SUPPORTED

| Feature      | Between-cell spread | Within-cell range | Discrimination ratio |
| ------------ | ------------------- | ----------------- | -------------------- |
| R0           | 0.0183 Ω            | 0.0121 Ω          | 1.51                 |
| Polarisation | 0.0259 Ω            | 0.0163 Ω          | 1.59                 |

Polarisation is marginally worse than R0, not better. Both ratios > 1, meaning
unit-to-unit variability exceeds the ageing signal. Neither feature is
identifiable univariately: a single scalar reading does not determine SoH for a
cell of unknown provenance.

### H2 — ratio-based contact gate: FAILS CRITERION

Reference band across real spectra at fixed SoC: R0/polarisation ∈ [1.81, 3.40].
Limit of detection for injected series resistance, evaluated at the population
median (R0 0.0836, pol 0.0346): approximately 0.034 Ω.

Criterion was 0.011 Ω, the magnitude of the full-life ageing signal. Actual LoD
is ~3x that. The gate therefore has no sensitivity in the region where a contact
fault is confusable with degradation.

Restricting to fixed SoC tightened the lower bound (1.02 → 1.81) but left the
upper bound unchanged at 3.40, which is what sets the LoD.

### Interpretation

Two features, two failures, same underlying cause: between-cell variance is
comparable to within-cell ageing variance for every scalar tested. This is a
property of the population, not of the features.

Consequences:

1. Univariate grading is ruled out. A multivariate model is required, not preferred.
2. The single-measurement contact gate ships as a gross-fault filter only. Faults
   between ~0.011 and ~0.034 Ω are undetectable by this method.
3. Mitigation for the undetectable band is procedural or hardware, not software:
   repeat-and-reseat, or four-wire Kelvin sensing in the clip-head.

### Outlier

LiPO_5 is anomalous: ratio mean 2.93 against 1.9–2.4 for the other four cells,
and it contributes the 3.40 maximum that sets the LoD. Excluding it moves the LoD
to ~0.016 Ω. Cause unknown — candidate out-of-distribution case. Open.

# M3 physical contact measurement requirements

**Status: proposed acquisition requirements; no specimen or measurement is supplied.**
Follow [A1–A6](CALIBRATION_NEXT_ACQUISITION.md) and the existing
[capture protocol](CAPTURE_PROTOCOL.md). The immediate deliverable is an actual
specimen/configuration lock, an external-output pilot, then a synchronized contact
pilot where qualified access permits. Basis: atlas pp. 109–120 and the
[A02 reading](development/2026-11-15-execution-continuation/notes/A02.md).

## Independent review conditions

The [A42 review](reviews/CONTACT_MEASUREMENT_REQUIREMENTS_REVIEW.md) accepts
specimen-lock and pilot planning. Admit a real recorder file before acquisition:
the current WAV reader supports ordinary tags 1/3, not WAVE_FORMAT_EXTENSIBLE.
Freeze event-table raw channel/frame references, time origin, correction and
detection identities, uncertainty-interval meaning, phase wrapping and ambiguous
bin handling. Explicit corpus relationships must bind chunks, recorders, gestures
and derivatives; a shared specimen identifier alone does not create those groups.
These are pilot requirements, not measurements already acquired.

## 1. Lock one instrument and one route

The acquisition lead must identify an actual electromechanical B-3/AO-28, its
revision, condition, modifications and connected load. None is currently known.
Assign a stable anonymizable `specimen_id`; keep serial photographs and the private
ID-to-instrument mapping under recorded restrictions. Derivatives retain that alias
and configuration identity. A service or load
change creates a new configuration.

Start with **Upper physical playing key 25**, counted from the lowest C
(project index 24; MIDI 60), **8-foot rank d3/project contact index 2**, expected
**source ID 37**. This is documentary routing from
[Table III](FACTORY_REFERENCE.md), PDF 155/printed 3-76, row 25; a source number
is not a physical terminal number. The technician must map the actual contact,
wire/terminal and source to dated specimen evidence before claiming this route.
Record all nine contacts while isolating this rank. Keep percussion off,
scanner bypassed, expression fixed/observed, and registration/gain unchanged
within each comparison.

Assign actual people to acquisition lead/owner, qualified technician, acquisition
engineer/player, data steward, analyst and independent admission reviewer. The
technician owns the approved electrical interface and loading assessment; this
document supplies no powered-circuit probing procedure. Use available, qualified
equipment. An inaccessible contact/source boundary stays unmeasured; external
audio alone supports only its stated output behavior.

## 2. Capture synchronized causes and output

The target observation set is continuous key travel, nine individual contact
observations, the active source waveform/phase reference, and dry electrical audio:
twelve simultaneous signals where the approved sensors provide voltage outputs.
Prefer a shared converter clock; otherwise retain separate manifests and measured
synchronization. Record baseline, complete gesture, sustain, release and recovery
without resetting source phase.

Identify the source boundary as `generator_loaded_terminal` when appropriate;
record its connected network and acquisition load. Identify dry output as
`preamp_GG` only for the verified differential G–G boundary, otherwise name its
actual electrical port. Retain polarity, receiving load and effects already
embedded in each trace; never import a loaded waveform as an unloaded pickup or
apply its filtering twice. Acoustic clatter is a separate optional observation.

Retain before/after chain calibration references, method, validity interval,
instrument/recorder identities, settings and original calibration assets.
Qualify voltage scale, gain/phase response, noise, overload, bandwidth, channel
skew and sensor latency, including DC preservation for position/contact channels.
Travel needs displacement calibration, endpoints,
hysteresis and sensor-induced mechanical influence; normalized position is a
derived quantity. Header sample rate does not establish physical clock accuracy.

Budget edge timing from sampling, clock drift/skew, sensor/filter delay and
detector ambiguity. Propagate timing into phase: a timing uncertainty `u_t`
contributes `f*u_t` turns, alongside source-frequency and phase-estimation
uncertainty and correlations. Define phase zero by a positive-going fundamental
crossing; retain actual waveform value and slope because waveform extrema/zeros
need not coincide with fundamental phase. Separate voltage-scale, frequency
response and load uncertainty from repeat variability; state coverage factors.
Freeze main-study timing
resolution, phase bins and amplitude margins from the pilot; unresolved bins or
differences smaller than expanded uncertainty remain inconclusive.

## 3. Repeatable pilot cases

Use the protocol's proposed **three whole repeats per candidate condition**,
then choose the main counts from observed variability. Retain every attempt.

| Case | Required observable and exit evidence |
| --- | --- |
| Full slow press and struck press, full release | Selected-contact make and break near both source peaks and both zero-crossing directions; at least three qualified occurrences per frozen phase bin, separately for make/break. Classify observed phase; never retime audio or restart the source. |
| Partial press/hold | Stops below and between observed contact transitions; approach the same displacement from both directions. Retain all nine state histories and displacement uncertainty; do not reuse synthetic thresholds. |
| Release/repress and reversal | Slow/quick releases, partial return before all contacts open, and reversal before/after an observed transition. Resolve make/break separately and retain complete recovery and held-neighbor history. |
| Stable holds and loading controls | Quiet/open and held baselines; A alone, B alone, A+B with continuous source reference. Proposed B is Lower key 37, 16-foot d1, also documentary source 37. Verify both actual routes and keep manual networks distinct. |

Repeat the admitted schedule on representative black keys and both manuals;
reserve complete later-session groups and keys for the declared generalization
claim.

Preserve raw contact disturbances without debouncing. A bounce claim requires
resolved repeated contact transitions above calibrated noise/time-resolution
limits; sensor ringing, threshold chatter and mechanical clatter remain separate
explanations. A+B residuals may reveal loading or downstream nonlinearity, not
automatically bounce. Bare-contact resistance requires independently qualified
voltage/current and separation from resistance-wire/network contributions;
otherwise it remains unidentified.

## 4. Reuse the archive; add only missing contact detail

Use [capture v1](CAPTURE_FORMAT.md) unchanged:
`captures/<session-id>/<capture-id>/capture.json`, `raw/stream-001.wav` and the
existing specimen-lock, permissions, setup, calibration, clock, controls,
conditions and QA support files. Use lowercase stable IDs, recorder-native chunk
order and original filename records. Hash every existing artifact with SHA-256,
record byte size, verify a restored copy, and bind manifest hashes in the corpus.
Preserve raw bytes; every transformed trace has parents and a reproducible recipe.

Add only missing contact detail:

- `support/setup.md`: physical-contact-to-rank/project-index/source/terminal map,
  route evidence locator, sensor coordinate and mechanical influence.
- `support/chain-calibration.md` and `support/clock-sync.md`: contact detector
  definition, detection limits, correlated timing/phase/scale uncertainty.
- `derived/contact-events.csv`: contact identity, make/break, `t_lo_s`, `t_hi_s`,
  travel in mm, source phase in turns, value in V, slope in V/s, uncertainties,
  detector/version and ambiguity reason. These are proposed review columns,
  not an implemented schema.

Respect v1's 16-channel, 32-artifact and size limits. Native CSV/video clocks stay
in the reviewed external inventory; do not disguise them as audio. Keep related
channels, chunks, derivatives and sessions together under the existing corpus
and fit/validation/final split records.

## 5. Admission and first analysis

Missing evidence stays null with reasons; unacquired work stays `planned`.
Actual but unqualified or failed takes remain `recorded`/`unassigned`, with QA
reasons. Overload, dropouts, unresolved synchronization or absent source/contact
observations block the affected inference. Preserve negative results and genuine
instrument anomalies. The reviewer must admit identity, rights, calibration,
loading, uncertainty, complete history and group independence separately from
software checks.

**First analysis after arrival:** verify manifest bytes/files, audio and complete
corpus with the existing [runbook](CALIBRATION_RUNBOOK.md); retain commands,
source hashes and exits. Then derive interval-valued contact events and plot
travel/contact/source/dry traces on the calibrated common timeline. Report
make/break displacement distributions, bounce-resolution limits and phase-bin
coverage before fitting. Fit contact history against observed contacts first;
only afterward evaluate electrical prediction using the measured source and
qualified transfer. Freeze corrections/windows before held-out evaluation.

Pilot qualification requires verified files/calibration, complete declared case
coverage/counts, immutable splits, reproducible event derivation and independent
admission. Gaps leave the affected gate incomplete. Parameter replacement requires
a versioned specimen-specific fit and untouched held-out results.

The current [36 synthetic fixtures](CONTACT_SWITCHING_RESULTS.md) validate the
declared finite, acausal, fixed-load switched-sine implementation: four factors,
all 289 samples for convergence, and 64 independent continuous probes per fixture.
They do not measure timing, bounce, resistance, loading or keyboard variability;
they establish neither causal streaming, Engine parity, full-window atlas `1e-4`
acceptance nor physical fidelity. Preserve them as numerical evidence.

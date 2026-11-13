# Physical acquisition and capture admission protocol

This is a **proposed project procedure**, paired with [capture contract v1](CAPTURE_FORMAT.md).
No specimen, permission, recording, calibration or physical acceptance is established
by this document or the [planned example](../data/capture-planned-example.json).
Its first deliverable is an approved, executable acquisition plan; its eventual
deliverable is a reviewed corpus supporting a named specimen and operating domain.
The nominal engine remains useful while these physical gates are open.

Source basis: [research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
chapters 17–24, pp. 109–156; chapters 57–59, pp. 349–366. These are atlas proposals
and documentary interpretations, not newly observed hardware. [PLAN.md](PLAN.md)
and the [atlas review](research/ATLAS_REVIEW.md) define M0–M9 and downstream scope.

## 1. Assign people and lock the acquisition subject

The acquisition lead owns the plan and chain qualification; a qualified technician
owns the initial external recording configuration and any internal electrical
measurement, using appropriate documented equipment and a reviewed procedure.
Start with an approved external-output or microphone pilot and a condition assessment.
This protocol provides no instruction to open or touch powered high-voltage hardware,
improvise a probe connection, or restrain a rotor. Inaccessible nodes stay unmeasured.
The player performs the documented gestures, the data steward preserves bytes and
split assignments, and a second reviewer admits evidence. An agent may prepare
metadata and analysis but cannot supply a missing observation (atlas pp. 349–354).

Before physical acquisition, complete these records or mark the affected activity
blocked. A later service intervention, load change, wiring change or changed cabinet
configuration creates a new configuration identity; preserve the previous one.

| Minimum lock | Required retained evidence | v1 location |
|---|---|---|
| Specimen | Stable project ID; actual model and serial/other identifying marks; dated identity photographs; current condition and known modifications. An unreadable marking stays unknown. | `specimen.specimen_id`, `variant`, `identity_evidence` |
| Organ revision | AO-28 chassis stamp and revision evidence; generator identification; relevant source drawing edition/page/hash; repair and component-change history. An inventory or redraw date does not establish installed connectivity. | `specimen.revision`; detailed configuration in `identity_evidence` and support files |
| Connected equipment | Cabinet model, serial, amplifier revision, fitted drivers, panels, accessories and power variant; or an explicit statement that the cabinet is absent from this path. Keep 122 and 147 configurations separate. | `signal_path.description`; individually identified hardware in `specimen.identity_evidence` |
| Access and permissions | Permission evidence for the actual planned access, recording and photography; separate decisions for storing, analyzing, deriving a model, and redistributing each relevant asset/model. Record grant scope, restrictions, authority, date and evidence locator. | `rights` referencing a retained permission record |
| Operating state | Observed mains conditions, temperature, instrument condition, warmup observations and control state; units and uncertainty or a reason for each unresolved quantity. | `stimulus.conditions`, `stimulus.controls` |

Do not acquire/upload assets into the project without the applicable storage
permission. Storage permission alone does not admit analysis or model fitting;
redistribution is a separate release decision. A public URL, access to an organ or
a schema-valid string supplies none of these permissions (atlas pp. 354, 359).
Keep rights evidence access-restricted when necessary; use a stable retrievable
locator and reviewer record rather than asserting a grant that has not been seen.

## 2. Use these filenames and responsibilities

The following names are an archive convention for **future real artifacts**. No
files at these paths are supplied or implied. Use an approved capture archive,
with one directory `captures/<session-id>/<capture-id>/` per manifest. Keep large
or restricted audio outside ordinary source commits unless its approved storage
and distribution policy permits inclusion.

| Relative filename | `files[].kind` / owner | Contents and rule |
|---|---|---|
| `capture.json` | Manifest; steward | Exact v1 object; do not list the manifest as its own artifact. |
| `raw/stream-001.wav` | `raw`; acquisition lead | Untouched recorder bytes. Use the real format extension; number recorder-native successive chunks consistently. Retain the recorder's original filename in setup notes if a byte-identical copy is renamed. |
| `support/specimen-lock.md` | `support`; technician/lead | Identity, configuration ID, revisions, condition, source references and photograph inventory. Include actual photographs as additional support records when permitted. |
| `support/permissions.md` | `support`; steward | Separate store/analyze/derive-model/redistribute decisions and evidence references; no assumed grant. A restricted external rights locator is permissible but needs a review record. |
| `support/setup.md` | `support`; technician/lead | Approved procedure ID/revision; instrument and interface inventory/serials; port and channel map; polarity; load; bypass; recorder configuration; all gain/filter settings. |
| `support/chain-calibration.md` | `support`; acquisition lead | Before/after scale checks, reference identity, complex response, noise, clipping margin, uncertainty budget and valid time/configuration interval. Include actual reference files as needed. |
| `support/clock-sync.md` | `support`; acquisition lead | Clock source, calibration method/result or unknown, synchronization markers, offsets/drift/skew and their uncertainties; clock-sharing evidence. |
| `support/controls.csv` | `support`; player/lead | Original command and observed-state annotations: time basis, event order, manual/key/rank IDs, all bank/tablet/expression settings and actual deviations. Commands are not contact measurements. |
| `support/conditions.csv` | `support`; lead | Observed warmup, temperature, mains and equipment/configuration changes with timestamps, units and evidence basis. |
| `support/qa.md` | `support`; reviewer | Header/content checks, signal and timing inspection, before/after calibration comparison, failures, exclusions and permitted analysis scope. |
| `derived/contact-events.csv` | `derived`; analyst | Optional events extracted from raw sensor channels, with local raw parents and exact detector/version/parameters. Preserve nine individual contact identities. |
| `derived/analysis-stream.wav` | `derived`; analyst | Optional aligned/cropped/resampled analysis copy, with raw ancestry and every transform recorded. Never replace the raw stream. |

Add files only when they exist, and compute `size_bytes`/`sha256` from their bytes.
Raw and support files have empty `parents` and null `derivation`; derived files
must reach a local raw ancestor and name `operation`, `tool`, `tool_version` and
`parameters`. An extracted trace is derived even if somebody places it in a
directory named `support`. A measured sensor voltage can be a raw acquisition
channel; its conversion to position, contact state or rotor angle needs a separate
sensor calibration and derived trace.

V1 allows 16 channels, 32 artifacts, 256 MiB per artifact and 512 MiB total per
manifest. Plan recorder-native chunking within these limits without discarding
history. If multiple manifests describe one run, keep their order/continuity in
the corpus inventory and give all of them the same acquisition group. Do not
crop, transcode or drop channels and relabel the result raw merely to fit a bound.
An existing oversized original remains outside v1 admission until its storage and
contract path is resolved. Independently clocked recorders need separate manifests;
v1 cannot natively describe a video- or CSV-only sensor clock. Retain such originals
with a reviewed external inventory and synchronization report, without inventing
an audio stream declaration.

## 3. Declare the physical boundary before choosing a fit

Use each channel's `boundary`, `port_reference` and `calibration`, and summarize
the full chain in `signal_path.description`, `bypass` and `loading`. A known
boundary needs a node pair or microphone identity, polarity/reference convention,
connected network, receiving load and added acquisition load. Record resistance
and capacitance or an evidenced frequency-dependent impedance; “high impedance”
alone does not quantify loading (atlas pp. 350–357).

| v1 boundary | Physical scale | Permitted interpretation and admission condition |
|---|---|---|
| `pickup_unloaded` | `V/FS` | Pickup-specific voltage only after the technician/reviewer justifies the unloaded approximation and its uncertainty. Probe presence does not make a pickup unloaded. |
| `generator_loaded_terminal` | `V/FS` | Terminal waveform with named fitted filtering/coupling and receiving load. Declare effects already present before importing it into a source model. |
| `preamp_GG` | `V/FS` | Differential voltage across the identified G terminals with controls, transformer/output load and full upstream path. It cannot become a pickup gain. |
| `electrical_voltage` / `electrical_current` | `V/FS` / `A/FS` | Explicit technician-approved port and sign convention; retain voltage/current sensor transfer and coupled load. |
| `acoustic_microphone` | `Pa/FS` | Microphone/sensor/recorder chain plus pose, orientation, coordinate system, cabinet panels and room. Electrical gain cannot be inferred from pressure alone. |

For each complete chain record the PCM-to-full-scale convention, physical scale,
analysis bandwidth, complex magnitude/phase response, sensor latency, interchannel
skew, noise and overload behavior. Scalar `calibration.value` is only units per
full-scale sample; it does not describe those other properties. A valid positive
scale and standard uncertainty need a retained method/reference and evidence
locator. Separate common calibration uncertainty from repeat-to-repeat spread.
Never use factory Table V G-G service readings as per-wheel amplitudes or as
project fidelity tolerances (atlas pp. 350–351, 354–356, 361–364).

`digital.sample_rate_hz` is the raw stream's header/declaration rate. Verify it,
format and channel count independently against the actual stream. `physical_clock`
describes the independently qualified sampling clock in Hz with standard
uncertainty; a plausible header rate does not fill it. A shared clock or loopback
can establish relative timing without establishing absolute clock accuracy.
Use one shared converter clock for audio, phase and voltage sensor channels where
the approved setup permits. Preserve independent synchronization observations for
separate clocks; store any resampling/offset correction as a derived transformation.
A common `group_id` does not establish coherence (atlas pp. 351, 356, 364).

### Honest known/unknown examples

These are field fragments for a planning record, not a new recorded manifest.
The known string describes an intended experiment; the numeric calibration is
still unknown. All other required keys come from the actual v1 contract.

```json
{
  "description": {
    "value": "Proposed dry G-G acquisition after specimen and chain review.",
    "unknown_reason": null
  }
}
```

```json
{
  "status": "uncalibrated",
  "value": null,
  "unit": "V/FS",
  "standard_uncertainty": null,
  "evidence": null,
  "unknown_reason": "The proposed G-G chain has not been calibrated or recorded."
}
```

The first fragment belongs at `stimulus`; the second belongs at a planned
`preamp_GG` channel's `calibration`. The hardware clock has the same uncalibrated
shape with unit `Hz` and its own reason. Unknown `specimen_id` and `rights` use
`{"value": null, "unknown_reason": "...specific missing evidence..."}`.
Keep `status: "planned"`, a nonblank `status_reason`, null acquisition timestamp
and `files: []` until acquisition actually occurs. Never prefill a timestamp,
hash, calibrated value or permission merely to make a record pass.

## 4. Run this setup checklist for every configuration

1. **Freeze the plan.** Name the question, specimen/configuration, approved
   boundary, observable, controls, exclusions and responsible people. Start with
   `partition.role: "unassigned"`; reserve prospective groups before fitting.
2. **Verify identity and permission.** Match the physical setup to the lock and
   rights record. Record any modification before proceeding. Do not silently
   substitute a C-3, modern B-3, another AO-28 revision or another Leslie variant.
3. **Qualify the complete chain.** Confirm channel order, polarity, load, gain,
   filters, bandwidth and recorder format. Disable undocumented automatic gain,
   normalization, noise reduction and other processing. Retain calibration
   evidence before and after the session; distinguish instrument distortion from
   probe, interface or converter saturation.
4. **Establish time and conditions.** Record clocks/synchronization and sensor
   delay; observe warmup until chosen observables meet a declared repeatability
   band. Record that band and its rationale. A fixed elapsed warmup time alone
   does not close this gate.
5. **Run a bounded pilot.** As a proposed scheduling minimum, start with three
   whole repeats of each candidate pilot condition. Use observed variability,
   noise, recovery and bandwidth to freeze the main repetition count, hold/gap
   durations and analysis windows. Three repeats are not a fidelity threshold.
6. **Capture the whole history.** Include quiet baseline, initial state, commands,
   observed gestures, sustain, release and complete recovery. Preserve unexpected
   or incomplete releases with an annotation. Do not restart free-running source
   phase to make individual takes align.
7. **Close the take.** Record actual UTC start, operator/session IDs, final control
   state and deviations. Hash untouched bytes before analysis; keep an approved
   second copy and verify restoration of actual objects, not only pointer files.
8. **Review before admission.** Check header/content, missing samples/dropouts,
   acquisition overload, timing continuity and end calibration. Quarantine the
   affected interval/configuration when a check fails; retain reasons and raw
   evidence where storage permission permits. Freeze numerical QA budgets from
   the pilot before evaluating the main corpus (atlas pp. 349–354, 358–359).

## 5. Acquire in this order

All quantities below are **targets to observe**, not supplied measurements.
Keep one fixed acquisition gain across comparative conditions. Any necessary gain
change starts a new qualified configuration. Do not normalize each note,
registration or percussion take independently.

| Priority / family | Executable acquisition sequence | Evidence before a physical fit |
|---|---|---|
| **P0 — identity and external pilot** | Complete sections 1–4. Record quiet baseline and isolated sustained notes through the approved external path; establish usable bandwidth, warmup, repeatability and duration. | Lock, permissions, chain/clock reports and pilot QA. An acoustic pilot only supports its combined pressure path. |
| **P1 — dry source and routing** | Scanner bypassed, percussion off, expression fixed and recorded. Screen every key/rank route on both manuals: 61 keys × 9 ranks × 2 manuals = 1,098 proposed route checks. Keep source number, physical terminal, manual/key/rank and MIDI identifiers separate. Obtain the 91 source identities at qualified boundaries where accessible, including low sources; capture sustain spectrum/frequency, source-phase reference and coupling. | Reviewed source/route census; exact boundary/load; frequency, level and phase uncertainty; source effects already embedded in each waveform. Output-only observations cannot certify an unloaded pickup. |
| **P1 — drawbars and coherent collisions** | At low/middle/high source regions and foldback boundaries, sweep physical markings 0–8 with other ranks muted on both manuals. Capture branch A, branch B and A+B with continuous phase reference, then distinct-source combinations. Record slow drawbar travel both directions. Hold keys through bank changes, inactive-bank edits, Cancel and reselect. | Raw level/phase ratios to marking 8, mute/noise residual, loading interactions and control history. Unrelated phase takes are not an algebraic-sum oracle. |
| **P2 — nine contacts** | Select representative white/black keys across both manuals, foldback boundaries and pilot anomalies. Acquire individual ranks before mixtures. Repeat pressed, struck, partial, held-chord/rearticulated and release gestures. The approved setup should observe key position, all nine contact states, phase reference and dry output together. | Sensor calibration/latency, actual make/break histories, per-contact source map, held-out keys/takes. If only audio is observable, admit only a scoped behavioral comparison; individual contact thresholds remain unidentified. |
| **P2 — shared percussion** | Under verified upper B routing, capture second/third × normal/soft × fast/slow (eight proposed combinations), plus percussion-off comparisons. Start with all drawbars closed and a demonstrated recovered reference; add the corresponding sustained rank and 1-foot route checks. Repeat isolated notes, joining notes during decay, legato overlaps, complete releases and decreasing all-up gaps. | Complete envelopes and measured open-contact histories; fixed-gain level relationships; uncertainty in recovery and contact timing. Derive gap range from the pilot, not nominal RC products. |
| **P2 — percussion routing histories** | While upper keys remain held, record B→other preset→B, Cancel/reselect and percussion off/on. Repeat with lower/pedal notes held; observe whether upper all-up timing changes. Include normal/soft steady-state comparisons after the transient and selected-drawbar travel. | Separate detector connectivity, sustained return, upper attenuation and shared decay/recharge. Neither per-note resets nor a MIDI-only all-up counter establishes these transitions. |
| **P3 — expression** | Calibrate position endpoints; propose stationary travel coordinates 0, .05, .25, .5, .75, .95, 1 in both approach directions. These are sampling choices, not gain values. Use identical tone material, fixed recorder/master gain, several levels/registrations and quiet captures at each position. Then record slow/quick heel-to-toe, reverse and interrupted movements with position traces. | Absolute level and complex spectral response, endpoint noise limits, position uncertainty and withheld gestures. Separate the expression network from downstream drive and monitoring gain. |
| **P3 — presets and pedal extension** | Review actual preset wiring before comparing all 18 fixed registrations with equivalent banks. Screen all 25 pedals and exceptional source-map boundaries. Once the dry path is qualified, expand pedal drawbar axes and mixtures using the 475-state proposal on atlas p. 143, with attack/sustain/release and manual unisons. | Specimen routing evidence, separate contact branches for duplicate sources, pedal shaping/load response and held-out mixtures. This extension is not a prerequisite to the first small dry pilot. |

These sequences follow atlas pp. 113, 119, 125, 131, 137, 143, 149 and 352.
Pilot observations determine repetitions and durations; missing internal access
narrows the claim instead of justifying inferred circuit measurements. Record
both intended commands and actual gestures. A MIDI velocity or note time is not
a measured contact trajectory, and acoustic clatter is separate from electrical
click (atlas pp. 115–119, 131).

## 6. Separate retention, qualification and split assignment

Maintain `corpus-index.csv` and `admission-report.md` outside the per-capture
schema. These are proposed review records, not implemented validator formats.
For each capture, retain its manifest hash, raw hashes, group/configuration IDs,
purpose, disposition, reviewer/date, allowed claims and unresolved gates.

| Corpus disposition | Manifest state / intended role | Decision |
|---|---|---|
| Planned | `planned` / normally `unassigned` | No acquisition timestamp or artifacts; known text describes intentions only. |
| Retained, unqualified | `recorded` / `unassigned` | Actual raw bytes and required acquisition/digital/group identities exist; storage is permitted. Unknown scale, clock, revision or loading remains explicit. Only separately authorized, clearly limited exploratory analysis is allowed. |
| Quarantined | `recorded` / `unassigned` | Preserve failed/ambiguous bytes and the reason; do not silently delete a hard case or admit affected intervals. |
| Qualified for fitting | `recorded` / `fit` | All gates below are reviewed for the declared boundary, parameter family and domain. |
| Qualified holdout | `recorded` / `held_out` | Same physical gates, plus frozen independence and validation/final-test purpose. No iterative fitting on a final holdout. |

Qualification requires actual specimen/configuration identity; permitted analysis
and model derivation; known port/polarity/load/bypass; independently checked raw
headers; valid scale, physical clock and relevant sensor/chain response with
uncertainty; synchronization adequate for the claimed observable; retained
controls/conditions; actual-byte integrity and restore evidence; and a reviewed
split/lineage inventory. Analysis-specific tolerances and exclusions must be
declared before assessing a model. Acquisition overload or dropout in the target
interval blocks that fit; genuine instrument distortion remains target behavior.
Do not repair missing metrology by fitting a free gain or source detuning.

A relative-level exploration with unresolved clock/scale is not this physical-fit
admission. An output-only calibrated behavioral fit may be scoped to its actual
loaded boundary, but cannot certify internal component values that the experiment
cannot identify. Reviewer decisions state that distinction (atlas pp. 361–366).

Run the metadata command first. For an actual recorded directory, run the
explicit byte check; its default artifact root is the manifest's parent:

```sh
python tools/validate_capture.py --input data/capture-planned-example.json
python tools/validate_capture.py --input /approved/archive/capture.json --check-files
```

The second path is a usage placeholder, not a supplied recording. Retain stdout,
stderr and validator revision in the review record. Neither command checks audio
headers/content or grants the qualification above; see [validation limits](CAPTURE_VALIDATION.md).

## 7. Freeze whole acquisition groups before fitting

The steward creates `split-lock.json` alongside the corpus index after pilot
design and before any parameter or model selection. Record the evaluation claim
(unseen takes of one specimen, unseen sessions, or unseen specimens), grouping
rule, group membership, capture/raw identities, role, purpose, split revision,
reviewer and freeze date. V1 does not define this ledger's machine schema.

- **Union physically related evidence.** One group contains the whole take or
  performance, every synchronized channel, each complete rotor run/ramp and its
  state-establishing history, every recorder chunk, crop, resample, normalized
  export, extracted feature and derivative. Separate files/manifests do not make
  these observations independent. Resolve cross-manifest parent relationships
  and duplicate raw/derived digests before assigning a role.
- **Choose a sufficiently broad group.** Use session/configuration groups by
  default. A narrower whole-take split needs a reviewer rationale limiting the
  claim to within-session prediction and retaining common calibration uncertainty.
  Unseen-session and unseen-specimen claims require those entire units withheld.
  Reserve different keys/registrations/gesture histories only where the intended
  evaluation actually tests them; adjacent windows never become separate holdouts.
- **Represent the three analysis purposes honestly.** Training uses v1 `fit`.
  Development validation and untouched final testing both use `held_out`, with
  distinct `purpose` entries in the ledger and matching `partition.rationale`.
  No acquisition group may span either roles or these two holdout purposes.
  V1's role enum has no separate validation/final-test field.
- **Keep independent chain references distinct.** Calibration-only recordings
  use `unassigned` with that purpose in the ledger. Their fixed, independently
  obtained metrology may support multiple groups; sharing a calibration report
  does not make sound recordings duplicate takes. Record shared uncertainty.
  Reclassify a reference used to optimize the sound model as fitting evidence,
  then audit all dependencies again.
- **Protect the final set.** Reserve complete acquisition groups for each claimed
  domain, including a return session when session generalization is claimed.
  Do not force percentages when too few independent groups exist. Keep final
  material under steward control until model, parameters, analysis recipe and
  tolerances are frozen. If final results influence a revision, retire that whole
  final set from the untouched claim and acquire fresh final evidence.

Audit the union of all manifests, not just one valid local DAG. Unresolved parentage,
shared original takes or conflicting group assignments block independent-holdout
admission. Publish split and manifest hashes with the fit report and retain failed
and inconclusive outcomes. A changed dependency requires an explicit new ledger
revision and reconsideration of affected claims (atlas pp. 354, 359, 364–366).

## 8. Keep downstream fitting behind its own gates

| Stage | Prerequisite and next physical evidence | Do not infer |
|---|---|---|
| **M4 scanner** | Accepted source/routing baseline; revision-qualified loaded scanner topology and resolution of [scanner errata](research/ERRATA.md); signed input/output and phase references for bypass, V1–V3/C1–C3 and Swell/Great combinations. Retain continuous scanner history and relevant pedal routing. | A generic modulation waveform or corrected pseudocode is a measured scanner. |
| **M5 AO-28** | Identified connected circuit or explicitly scoped behavioral model; calibrated input/output pairs, transformer/load evidence, several levels/registrations/expression positions and recovery histories. Validate the complete dry G-G path with upstream uncertainty retained. | An inventory is a complete netlist, or end-to-end gain uniquely identifies internal components. |
| **M6 Leslie 122 / 147** | Separate cabinet/amplifier revisions and approved interfaces; qualified electrical ports, polarity, coupled driver loads and voltage/current response at several levels. Keep the two variants' evidence and models distinct. | A 122 fit or adapter establishes 147 behavior. |
| **M7 rotor/cabinet/room** | Accepted dry-organ and electrical baselines; approved stationary references, microphone pose/axis in a named coordinate system, cabinet/driver/panel state and room. Then synchronized horn and drum angle traces, commands, full slow/fast cycles, both transition directions and interrupted ramps. | A changing-angle sweep is a stationary impulse response, or cancellation-null frequency spikes measure acceleration. |
| **M8 integrated claim** | Frozen upstream models, uncertainty and independent groups; unseen musical/control histories, retained direct-organ reference where available, named microphone scenes and actual held-out/listening results. | Cabinet/room EQ can close an upstream routing, polarity, timing or expression failure. |

See [PLAN.md](PLAN.md), [ATLAS_REVIEW.md](research/ATLAS_REVIEW.md), and atlas
pp. 353–354, 361–366. Changing microphones, panels, drivers, room or connected
load changes the configuration. Preserve the dependency chain when admitting a
new capture; downstream success cannot certify unobserved internal parameters.

## 9. What v1 cannot validate

V1 enforces structure, local declarations and optional byte identity. It does not
verify physical acquisition or rights authority; inspect WAV/FLAC headers or
sample content; qualify a probe/load, gain, bandwidth, physical clock, sensor,
position, geometry or synchronization; establish calibration validity; distinguish
instrument distortion from chain overload; verify controls or warmup; reproduce
derived transforms; resolve cross-manifest ancestry or duplicate takes; enforce
corpus split purposes; protect an untouched final test; prove archive restoration;
or admit a hardware fit. Detailed control schemas, native position/video clocks,
multi-clock records, multiple specimen objects and a machine-checked corpus ledger
are outside v1. Do not add unofficial keys: use its text/evidence locators and
support artifacts, with explicit external review and limitations.

## 10. Next dependency-ready tasks

| Task | Dependency | Concrete deliverable / pass evidence |
|---|---|---|
| **A1 — obtain access and lock** | Actual owner/specimen and qualified technician | Completed identity/configuration/permission records; approved external pilot scope. No hardware claim while these are missing. |
| **A2 — qualify and pilot** | A1; recorder, references and appropriate interfaces | Actual before/after chain/clock evidence, pilot raw files, reviewed QA, measured repeatability and frozen main schedule. |
| **A3 — acquire dry corpus** | A2; accessible qualified boundaries | P1 source/routing and P2 contact/percussion captures, P3 expression as setup permits; explicit unobserved quantities and retained failures. |
| **A4 — audit admission and splits** | Actual A2/A3 files; reviewed rights | Actual header/content check, restored-byte check, cross-manifest ancestry/duplicate audit, reviewer dispositions and frozen group/purpose ledger. This needs new tooling or documented manual review. |
| **A5 — fit and validate M3** | Qualified dry corpus; dependency-ready M3 implementation | Boundary-scoped parameters, raw/derived provenance, uncertainty, fixed analysis, development-validation results and untouched final evaluation. |
| **A6 — extend downstream** | Applicable M4–M7 gates in section 8 | New revision/port/rotor/scene evidence; separate acceptance for scanner, AO-28, 122, 147 and acoustics. |

Until A1–A4 have actual evidence, the concrete next engineering work is the
named nominal M3 contact/percussion implementation in [NEXT_STEPS.md](NEXT_STEPS.md).
This protocol prepares its acquisition replacement path without claiming that
the measurements, permissions or physical acceptance have already occurred.

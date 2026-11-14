# Next acquisition and calibration phase

The next physical deliverable is an identified external-output pilot archive,
with a reviewed measurement chain, uncertainty record and explicit disposition.
The implemented M0/M8 tools make that evidence inspectable. They have not acquired
an instrument, identified its internal parameters or completed M8 calibration.

This plan implements the dependency order in [PLAN.md](PLAN.md) and the existing
[capture protocol](CAPTURE_PROTOCOL.md). The software interfaces below were
checked against accepted local source
`48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a`, tree
`3edea0838b75feb06c19e151ec8539e80646fc03`. These identify the inspected source,
not the latest published main. Read the integrator's current
[handoff](CALIBRATION_HANDOFF.md), [status](STATUS.md),
[next steps](NEXT_STEPS.md) and actual session manifests before resuming; concurrent
standalone completion is incorporated there. The
[assignment record](development/2026-11-13-calibration/53-next-acquisition.md)
retains this plan's checks and source basis.

## What is ready, and what is still missing

| Available engineering | What it establishes | Physical input still required |
| --- | --- | --- |
| Capture v1 validation and declaration readiness | Admitted metadata, explicit unknowns and declaration gaps | Actual specimen/revision, access and rights records, observed configuration and acquisition history |
| Audio inspection and optional artifact checks | Actual byte identities, admitted stream geometry and digital statistics | Complete physical scale, clock, loading, bandwidth, phase, noise and overload evidence |
| Global corpus audit within its declared input | Declared ancestry, relationship components, split conflicts and requested byte/audio coverage | Complete relationship inventory, justified independence and the history of holdout use |
| Fixed metrics, policies, jobs and studies | Comparisons under declared windows and numerical criteria; retained failed/inconclusive results | Qualified observations, defensible uncertainty margins, predeclared physical criteria and an identifiable model |
| Complete report replay and relocatable CaptureTools | Re-execution and complete canonical report comparison under recorded source/runtime identities | Acquisition authenticity, physical fidelity, listening results and product qualification |

Currently missing real inputs include the chosen organ's identity and condition,
AO-28 revision and connected configuration, cabinet/driver identity for later
work, actual permission scopes, assigned acquisition personnel, chain and clock
calibration records, synchronized raw recordings, observed controls/conditions,
pilot repeatability, reviewed uncertainty, qualified split membership and
untouched final evidence. Internal connectivity, source/load observations,
contact trajectories, scanner captures and rotor/geometry records are likewise
unmeasured. No new values or permissions are supplied by this plan.

Keep a future hardware capture `planned` until acquisition actually occurs.
Preserve null values and specific `unknown_reason` text; never turn missing
calibration into unity gain, an absent clock into the WAV header rate, or an
unassigned group into invented history. A valid recorded but unqualified capture
can remain `recorded` / `unassigned`. Qualification is a separate retained review.
The [planned capture](../data/capture-planned-example.json) and
[planned corpus](../data/corpus-planned-example.json) remain examples of missing
evidence, not templates to populate with fictional observations.

## Responsibilities and dependency order

These responsibilities come from the existing protocol. Actual people and
locators remain to be assigned; this document adds no permission process.

| Role | Responsibility |
| --- | --- |
| Acquisition lead and instrument owner | Identify the target, condition, permitted scope and intended claim; record configuration changes and actual permission decisions |
| Qualified technician, where the existing scope requires one | Identify revision, ports, loading and the reviewed interface for authorized electrical observations; report inaccessible boundaries as unmeasured |
| Acquisition engineer and player | Qualify the chain, record timing/conditions and perform the declared complete control histories |
| Data steward | Preserve permitted originals, inventory/hash/restore them, maintain ancestry, rights locators, split history and quarantine reasons |
| Analyst and subsystem owner | Choose observables, document uncertainty/identifiability, freeze comparisons and implement or fit only the owned model boundary |
| Second reviewer and integrator | Review physical admissibility and bounded claims; integrate evidence and dependency changes, preserving earlier results |

| Stage | Required inputs | Concrete next output | Exit evidence |
| --- | --- | --- | --- |
| **A1 — identity, rights, configuration** | Real access and owner records | Specimen/configuration lock and permission record, linked from a still-honest v1 plan | Reviewed identities and allowed uses for the selected target; unresolved items explicitly scoped |
| **A2 — chain and pilot** | A1, actual equipment and approved boundary | Chain/clock records, untouched pilot captures, repeatability/uncertainty and QA report | Evidence supports the chosen observables and a bounded main acquisition design |
| **A3 — dry corpus** | A2's accepted setup, pilot-derived schedule and physical scope | Raw dry recordings, complete control histories, v1 manifests and support/derivation records | Each retained run has a disposition, correct boundary and reproducible byte ancestry |
| **A4 — admission and splits** | Complete related acquisition inventory from A3 | Machine corpus index plus reviewed admission and frozen split records | Requested software audit completes; physical qualification and group/history review are separately recorded |
| **A5 — fixed comparison and fitting** | Qualified A4 fit/validation/final evidence and an identified candidate boundary | Frozen policies/jobs/studies, constrained fitting record, residual/uncertainty and replay reports | Declared boundary criteria tested on the appropriate unseen groups; failures and unsupported parameters retained |
| **A6 — downstream stages** | Relevant upstream dry acceptance and each subsystem's own evidence/numerical gates | Revision-specific scanner/AO-28/Leslie/rotary acquisition and model reports | Each boundary closes only its own declared claim; complete instrument and release claims remain separate |

### A1. Lock the actual subject and allowed uses

The acquisition lead, owner, technician and steward assemble the protocol's
`support/specimen-lock.md`, `support/permissions.md` and `support/setup.md` when
those records exist. Include actual identifiers and dated identity evidence,
revision/source-sheet identity, known service changes, connected equipment,
control/bypass state, intended port and receiving load. State explicitly when a
cabinet is absent from the pilot path. Leslie 122 and 147 are separate targets.

Record store, analyze, derive-model and redistribute decisions separately, with
their authority, scope, date and evidence locator. A public URL, nonblank rights
field or file hash supplies none of those decisions. Restricted evidence can
retain an appropriate external locator and review record; do not publish assets
beyond their recorded scope. A later service, load, panel, driver or other material
configuration change creates a new configuration identity and identifies affected
recaptures. Do not overwrite the former target.

Use [capture v1](CAPTURE_FORMAT.md), its
[schema](../data/capture.schema.json), metadata validation and declaration readiness
to identify missing records. An A1 review is not a claim that audio exists, that
the measurement chain is qualified or that declarations were independently proved
by software. The first handoff is the identified pilot scope and its remaining
unknowns, not a manufactured recorded manifest. Atlas basis: pp. 349–350, 355–356.

### A2. Qualify the chain and use a pilot to design acquisition

The acquisition engineer retains `support/chain-calibration.md`,
`support/clock-sync.md`, `support/conditions.csv` and `support/qa.md`, backed by
actual calibration assets and pilot files. The chain record identifies sensor or
interface, cables, gain, converter, filters and recorder; physical units per FS,
complex response over the proposed analysis band, noise, overload margin, load,
channel polarity/skew, uncertainty and calibration validity interval travel with
the observation. Before/after observations and deviations determine which actual
intervals the record supports.

Keep the digital header rate separate from physical clock calibration. A shared
clock can support relative timing without establishing its absolute accuracy.
Separate clocks need their own records and retained synchronization evidence;
uncertain timing stays uncertain. Retain any alignment/resampling as a derivative
with its original parents and uncertainty. The tools do not estimate these
quantities or apply calibration automatically.

Follow the protocol's external-output pilot and existing repeat proposal.
Observe warmup and complete attack, sustain, release and recovery histories.
Choose the main repetition count, duration, bandwidth, windows, QA criteria and
proposed tolerances from actual pilot variability and the intended claim. No
new numerical threshold or hardware setting is supplied here. Separate
repeat-to-repeat variation from common scale, clock, load and geometry errors.
A failed or ambiguous run remains recorded with a quarantine reason; repeated
measurements do not remove a common calibration bias.

The exit artifact is a pilot review stating which observables are identifiable,
which intervals are qualified, what uncertainty remains, and exactly which A3
captures can proceed using that setup. Digital decoding and metadata completeness
are supporting checks. Atlas basis: pp. 351–354, 364, 484.

### A3. Acquire dry evidence at its actual boundary

Start with the protocol's P0/P1 order and bounded pilot-derived schedule. Preserve
the declared scanner/percussion/bypass and expression state for dry source and
routing work. Expand into P2 contact/percussion histories and P3 expression,
presets and pedals only with the observations each question needs. The full route
screening proposal is a campaign objective, not a reason to fabricate a complete
corpus or make every route a separately independent recording.

| Observation | What the record must distinguish |
| --- | --- |
| Isolated source/routing and coherent combinations | Source ID, terminal and playing-key identity; fitted filtering/coupling/load; continuous phase/history and actual control state |
| Key/contact behavior | Attack and release, observed trajectory/contact evidence when available, per-contact identity and sensor derivation; command/MIDI history alone is not measured contact timing |
| Percussion/expression/preset/pedal behavior | Complete prior state, recharge/recovery, held-key transitions, bank eligibility and actual control trajectories/load; avoid independently normalized takes |
| Dry output only | The identified output boundary and its supported behavioral claim; it does not identify every upstream component or unloaded pickup amplitude |

Use the exact physical boundary tokens from v1: `pickup_unloaded` requires a
justified unloaded approximation; `generator_loaded_terminal` retains the connected
network; `preamp_GG` is the identified differential G–G path and load.
`electrical_voltage`, `electrical_current` and `acoustic_microphone` retain their
respective port/sign or microphone/pose meaning. Factory Table V's service readings
are not per-wheel gains or emulation tolerances. If only the final dry boundary is
observable, retain an effective behavioral model or an unresolved parameter
instead of inferring internal values from a small output residual.

The steward stores each actual `capture.json` with untouched native raw streams,
the protocol's support records, observed UTC/operator/session/control histories
and exact sizes/hashes. `files` describes only existing assets. Raw/support files
retain their v1 empty-parent/null-derivation meaning; derived assets retain parents,
operation, tool/version and parameters, reaching a local raw ancestor. A calibrated
position or angle estimate is distinct from its raw sensor observation. An analysis
crop, channel selection, gain change or resampling is a derivative, not a replacement
raw file. Preserve restoration evidence for actual objects, including external
objects when used; a pointer file is not the recording.

The existing inspector accepts ordinary-tag PCM16/24/32 and float32/64 RIFF WAV,
or explicitly declared little-endian raw float32. Capture-v1 FLAC metadata remains
valid, but requested audio inspection currently rejects FLAC. Retain unsupported
originals and, if needed, create a documented supported analysis derivative; do
not relabel or discard the raw acquisition. A derivative alone does not make an
unsupported raw format eligible for a full audio audit or job: those operations
still inspect the raw files. Such archives need separately qualified decoder
support before those workflows can admit them. The v1 digital declaration still
describes the raw stream. Sensor-only CSV/video or separate-clock evidence outside
the present contract remains in the reviewed external inventory; do not disguise
it as compatible audio. See [audio formats and bounds](CAPTURE_AUDIO.md).

Plan within existing resource limits: v1 permits 16 channels, 32 artifacts,
256 MiB per artifact and 512 MiB in one manifest. Native recording chunks must
retain their common take/group, channel map, order and complete histories.
An oversized original stays preserved outside current admission until an explicit
storage/contract solution exists. Atlas basis: pp. 350–352, 355–359, 361–362.

### A4. Admit complete groups and freeze their purposes

The steward and second reviewer review physical eligibility, then produce an
actual machine `corpus.json` under the implemented
[corpus schema](../data/capture-corpus.schema.json) and
[corpus guide](CAPTURE_CORPUS.md). Bind exact manifest bytes and list all capture
parents, relation labels and derived-audio descriptors. The protocol's proposed
`corpus-index.csv`, `admission-report.md` and `split-lock.json` are separate human
review records; they are not inputs with an implemented machine schema.

The review records every retained capture's disposition, responsible reviewer,
configuration, allowed claim and unresolved issue. Keep plans, unqualified records
and quarantined runs visible. Record the intended generalization domain: another
take, another session of this specimen, or another specimen. A valid metadata
document and a clean graph do not establish those physical relationships.

Audit the union of related takes, session histories, synchronized channels,
chunks, rotor runs, gesture families and all derivatives before assigning splits.
The tool joins equal session/group IDs, relation labels, ancestry, raw/derived
content and, when requested, decoded-stream identity. Shared support files and
specimen IDs alone do not create graph edges; missing labels or unequal digests
do not prove independence. Declare genuine relationships rather than altering
session IDs to avoid a conflict.

Use `fit`, `validation` and `final` purposes in the companion. Their v1 roles are
respectively `fit`, `held_out`, `held_out`; `unassigned` maps to `unassigned`.
Related components cannot cross the three assigned purposes. Preserve freeze
chronology, group membership and rationale outside the schema as well. Calibration
references used only for metrology retain their separate purpose and common
uncertainty; if later used to optimize sound, record that change and re-audit the
dependencies. Final evidence used for revision loses its untouched-final claim.

There is a concrete scale boundary: a corpus admits at most 512 captures, while a
job admits at most 64 captures and 256 artifact references. A study admits at most
eight jobs sharing one exact corpus identity; it is not a cross-corpus aggregator.
Artifact/audio aggregate limits also apply. A global structural audit can precede
smaller comparison subsets, but retain an explicit mapping and complete global
review; a subset pass proves only the subset checks. Splitting related captures
among files to fit limits does not establish global independence. A larger campaign
needs a reviewed complete inventory and, where necessary, a separately specified
and qualified versioned audit extension before making the broader software claim.
Atlas basis: pp. 354, 359, 366, 378, 484.

### A5. Freeze comparisons, then fit only supported parameters

The analyst and subsystem owner first select a physically qualified boundary and
the actual observations it can identify. Freeze the candidate/model identity,
analysis windows, channels, rates, units, spectral window/floor/frequencies,
uncertainty treatment, permissible correction and decision criteria before the
corresponding confirmation. Keep the original
[policy](../data/capture-policy.schema.json),
[job](../data/capture-job.schema.json) and
[study](../data/capture-study.schema.json) bytes, not only their parsed copies.
The retained [synthetic policy](../data/capture-policy-synthetic-example.json)
illustrates a format; its zero margin is not a hardware tolerance.

Both selected captures must be recorded, share the same corpus purpose and admit
the declared comparison geometry. Retain the candidate render's own model/source
identity and provenance. Current jobs compare all declared channels in index
order, with `pairing: index` and `transform: none`. They do not convert FS to
volts/pascals, match boundaries,
search alignment, resample, normalize, fit nuisance parameters or optimize a
physical model. Any permitted calibrated correction needs a separately retained
derivation and uncertainty review. A derivative's raw ancestor metadata does not
automatically calibrate that derivative. Keep uncompensated and permitted
compensated comparisons identifiable; do not hide wrong wiring, timing, phase or
levels through per-note corrections or residual EQ.

Actual constrained fitting is the next implementation/evidence task after those
inputs exist. Its retained record must identify parameter units, boundary,
evidence, feasible bounds and unknowns; objective/features; code/profile/data;
initializations, seeds and warmup/state histories; solver termination, active
bounds, alternative solutions and numerical refinement; and supported domain,
correlations and unresolved identifiability. Use fit groups to estimate, validation
groups to choose structure, then lock the candidate and evaluate final groups.
Unknown internal quantities remain unknown or explicitly effective parameters.
Solver termination and a numerical comparison pass are not physical acceptance.

The output is a boundary-specific residual/uncertainty report, every completed
job/study outcome, complete replay record and reviewed claim statement. Missing
observations or unresolved precision produce an honest inconclusive or not-run
physical gate. A passing all-fit study does not supply validation or final evidence.
Listening needs its own actual captures, panel, pilot variance, justified margins,
frozen protocol and responses; no listening result is supplied here.
Atlas basis: pp. 361–366, 378, 449, 484.

### A6. Continue downstream through the correct owners

| Track and owner | Inputs before physical fitting or integration | Retained boundary |
| --- | --- | --- |
| M4 scanner owner | Identified revision/topology/loading, qualified input/output and bypass captures, stationary/rotating mode histories; its independent numerical gates | [G5 same-hertz qualification still fails](SCANNER_AC_PARITY.md) for the retained realization. Acquisition or a capture-tool pass cannot clear that numerical gate. Follow [SCANNER_HANDOFF.md](SCANNER_HANDOFF.md) before Engine integration. |
| M5 AO-28 owner | Connected revision-specific circuit or an explicitly bounded behavioral model; calibrated input/output pairs, several levels/loads and recovery, upstream source/routing/state evidence | Validate the complete dry organ before cabinet fitting; component inventory alone is not connectivity. |
| M6 Leslie electronics owner | Actual 122 revision, ports/polarity, amplifier/transformer/divider/driver loading, appropriate voltage/current observations and dry-organ baseline | Keep 147 as a separate model; downstream gain/EQ must not repair an upstream error. |
| M7 rotary owner | Relevant M5/M6 boundary evidence, independent horn/drum angle and command histories, stationary references, microphone pose/cabinet/room configuration | Preserve one physical trajectory per rotor and explicit propagation/filter/room ownership. A moving sweep is not automatically a stationary IR. Follow [ROTARY_SCOPE.md](ROTARY_SCOPE.md) and its actual manifest. |
| M8 integrated assessment and M9 product owners | Frozen subsystem profiles, held-out complete performances and the separate listening/device/host protocol | Partial dry calibration does not establish a complete instrument; product, deadline, accessibility and distribution claims retain their own observed gates. |

Motion transitions include complete histories and interrupted/reversed commands
when the declared experiment calls for them; choose coverage and durations from
pilot evidence. No internal access or rotor-manipulation procedure is added here.
Atlas basis: pp. 353, 362, 449, 485–486.

## Software checks to attach to the handoff

Use Python 3.10+ from a coherent checkout or complete relocated package. Record
source/tree, runtime, exact command, exit, stdout/stderr and report identities.
Paths beginning `/path/to/` below are placeholders for future actual artifacts.
Run commands separately and retain completed nonzero outcomes.

| Stage/check | Command from repository root | Expected interpretation |
| --- | --- | --- |
| A1 structure | `python3 tools/validate_capture.py --input data/capture-planned-example.json` | Supplied plan exits 0; structural validity supplies no recording. Add `--check-files` for actual recorded artifact verification. |
| A1 declaration gaps | `python3 tools/capture_readiness.py --input data/capture-planned-example.json` | Supplied plan exits 3, `planned`, with 20 missing declarations. Recorded inputs may be `declarations_incomplete` (3) or `declarations_complete` (0); both keep physical claims unestablished. |
| A2/A3 actual digital stream | `python3 tools/capture_audio.py --input /path/to/archive/raw/stream-001.wav` | 0 admits the complete stream and reports digital statistics; it neither proves absence of upstream clipping nor applies physical calibration. Headerless raw requires its actual explicit format/rate/channel declaration. |
| A4 planned graph | `python3 tools/capture_corpus.py --input data/corpus-planned-example.json` | Supplied plan exits 3 with `planned_capture` and `unassigned_capture`. |
| A4 actual inventory | `python3 tools/capture_corpus.py --input /path/to/archive/corpus.json --check-files --check-audio` | 0/1/3 means complete pass/failed/inconclusive requested checks. Audio mode requires file checks; no `--output` option exists. Preserve complete stdout explicitly. |
| A5 fixed pair | `python3 tools/capture_job.py --input /path/to/archive/job.json --output /path/to/reports/new-job-report.json` | 0/1/3 means complete pass/failed/inconclusive; a rejected input also exits 1 but has no completed report and a diagnostic. |
| A5 fixed collection | `python3 tools/capture_study.py --input /path/to/archive/study.json --output /path/to/reports/new-study-report.json` | Same complete-outcome distinctions; every complete job remains, including failed and inconclusive neighbors. |
| A5 reproduction | `python3 tools/verify_capture_report.py --kind study --input /path/to/archive/study.json --report /path/to/reports/new-study-report.json --output /path/to/reports/new-replay-summary.json` | 0 is a complete byte match; 1 is mismatch or rejection. A matching failed/inconclusive study retains its original engineering status. There is no replay exit 3. |

Usage errors exit 2. An audio/input rejection is not a completed numerical failure;
inspect the diagnostic and full report rather than reducing all nonzero exits to
one category. For tools with `--output`, use a new destination in an existing
directory; they preserve existing destinations and still emit stdout. A late
stream failure can coexist with a complete published file, so retain both the
artifact and the error. The [operational handoff](CALIBRATION_HANDOFF.md),
[job guide](CAPTURE_JOB.md), [study guide](CAPTURE_STUDY.md) and
[replay guide](CAPTURE_REPLAY.md) contain the full contracts.

The [synthetic demo](CAPTURE_DEMO.md) provides deliberate pass/inconclusive/failed
jobs and a failed study for operational practice. Its generator creates fixtures,
not captures of hardware. No tool automatically promotes specimen identity,
permissions, calibration, independence, freeze chronology or physical fidelity.

## Useful work while real inputs are pending

Continue bounded engineering with named ownership. Prepare still-planned A1/A2
record outlines and an actual missing-input queue; map known source sheets and
unresolved ports without inventing a connected netlist. Preflight the intended
archive's format/size/channel needs against current contracts. Specify a versioned
extension if sensor timing, larger global inventories, physical-unit transforms
or required observables exceed them; qualify that extension before using it to
make an evidence claim. Rehearse existing ingestion/replay with clearly synthetic
fixtures and retain every status.

Preserve the independent scanner and rotary work rather than taking their active
paths. The completed standalone session's next contracts cover external MIDI,
native semantic accessibility and a typed fixed-registration selector under
[NEXT_STEPS.md](NEXT_STEPS.md) and [STANDALONE_HANDOFF.md](STANDALONE_HANDOFF.md).
Those are useful independent M9/M3 work after ownership is agreed; this acquisition
plan does not assign them to the calibration track. Preserve the 45 public controls,
state migrations, source/profile/map identities and native UUIDs until their owners
implement and qualify an explicit change.

## Concrete completion and resume checklist

- Actual specimen/configuration and permission records, named responsible people,
  scope/evidence locators, unresolved inputs and the next obtainable observation.
- Untouched permitted raw objects, exact inventory/hashes, v1 manifests, channel
  maps and boundary/load/polarity records; verified restoration of actual objects.
- Chain and physical-clock evidence, before/after validity intervals, synchronization,
  conditions, actual control histories, pilot repeatability and uncertainty review.
- Per-run QA/disposition, retained failures/quarantine reasons and explicit limits
  on the claim; every analysis derivative's complete parents and reproducible recipe.
- Complete relationship inventory, machine corpus index, reviewed admission and
  frozen fit/validation/final membership/history, including mappings for subsets.
- Original policy/job/study bytes; justified units, windows, margins and correction
  rules; candidate/model/parameter identities and the separate fitting record.
- Complete reports, commands/exits/stdout/stderr, source/runtime identities and
  replay summaries, preserving pass, fail, inconclusive, rejected and not-run scopes.
- A boundary-specific claim and unresolved-parameter list, affected downstream
  owners, and the exact next artifact needed. Any changed source, profile, setup,
  threshold or data names the dependent gates requiring fresh evidence.

Future agents follow [AGENTS.md](../AGENTS.md): read the current plan and actual
ownership, take a dependency-ready task, retain evidence and failures, and hand
shared status/next-step/log updates to the integrator. Completed authorized work
is committed and pushed with concurrent changes preserved and the fetched remote
identity checked. This durable workflow does not turn a plan, tool pass, publication
or agent count into physical acceptance.

Source basis: the unchanged [500-page atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
pp. 349–359, 361–366, 378, 449 and 484–486, together with the
[fresh full-text review](research/CALIBRATION_ATLAS_REVIEW.md). The atlas supplies
the acquisition and evidence requirements, not newly acquired measurements or
universal fidelity tolerances.

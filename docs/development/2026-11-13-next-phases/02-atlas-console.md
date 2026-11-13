# Assignment 02 - atlas console and generator review

## Identity, ownership and executed scope

- Actual worker: `/root/w01_a02_atlas_console`; wave 1, assignment 02 of the new
  next-phases session. Earlier review assignments are not counted again.
- Inspected repository: `tomasedisonn80/Hammond-B3-Organ`, starting commit
  `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`, tree
  `51fd7b24d2f373a693ced8dbde0fba762a3cc434`.
- Owned output: this note only. No source, shared handoff, prior ledger or
  concurrent scanner checkout was changed. No commit or push was performed by
  this worker.
- Read **all 84 pages, 85-168 inclusive**, from the complete extraction,
  continuously rather than by keyword snippets. These are chapters 013-026.
- Rendered and visually inspected atlas pages **122 and 151** at 1700-pixel scale.
  Page 122's entire upper/lower registration table was legible and matched the
  extraction; page 151 confirmed the ownership architecture. This is not an
  assertion that every image or underlying external source was inspected.
- Source PDF SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

The source stays unchanged. `AGENTS.md`, the current status/next-step context,
plan, research review, scanner handoff and current development-log entries were
consulted. Current console and input declarations and the relevant Engine
control/render paths were inspected. No numerical acceptance test was run in
this read-only assignment; all new acceptance items below are proposed work.

## Full assigned-page findings

| Pages | Chapter | Engineering consequence and evidence boundary |
| --- | --- | --- |
| 85-90 | 013: mechanical modulation | Common drive timing and local shaft/gap changes are distinct states. A Model A observation or a 100/120 Hz mains forcing calculation does not supply B-3 modulation depth. Keep nominal residuals explicitly proposed and deterministic across blocks. |
| 91-96 | 014: calibration data | Immutable observations, model profiles, compiled banks and runtime histories are separate. Preserve units, unknowns and source boundaries. Factory Table V measures preamp G-G service output, not oscillator amplitudes. Serial-number inference must permit documented retrofit. |
| 97-102 | 015: manual mapping | Preserve all 549 routes, repeated upper folds, low 16-foot fold and separate identifiers. Colliding drawbar paths share one source while retaining separate contacts; manual mapping does not replace pedal mapping. |
| 103-108 | 016: shared sources | Produce each shared source once per sample; notes, presets and ordinary transport do not restart it. Numerical oracle/optimized agreement is separate from hardware fidelity. Rate preparation, state migration and zero-frame calls have explicit rules. |
| 109-114 | 017: drawbars and loading | Nominal 3 dB gains are a reference, not a production transformer model. The historical patent turns do not identify B-3 winding turns. Continuous contact overlap and its documented resistance do not identify all loading. Preserve the nominal reference while preparing a separately identified network model. |
| 115-120 | 018: contacts and click | A switched shared waveform makes phase-dependent transients; source-zero-crossing edges can still introduce slope discontinuities. Partial travel, distinct make/break and fractional edge timing need independent histories. The proposed normalized RMS bound of `1e-4` requires a converged high-rate reference, not an upsampled aliased signal. |
| 121-126 | 019: presets | C is a momentary Cancel with no contacts; C-sharp through A select nine fixed registrations; A-sharp/B select retained banks. The full two-manual chapel matrix is supplied on p. 122. A physical simultaneous latch mask is broader than an exclusive software selector, and overlapping routes require the loaded network. |
| 127-132 | 020: percussion keying | Use one upper-manual-wide detector/history. The eighth harmonic is the ninth physical drawbar, 1 foot. Duplicate ownership, same-offset release/press and preset changes must not invent charge recovery. Retain unknown specimen-dependent switching behavior. |
| 133-138 | 021: percussion circuitry | Nominal RC products are not measured audible decay lengths. Sustained return, upper compensation and percussion gain are separate. Fast/slow bias and decay are distinct. No new per-note oscillator or duplicate return path is justified. |
| 139-144 | 022: pedals | The 25-by-8 map has 195 connections and five nulls; repeated sources retain separate paths. Four buses and two coupled mixtures do not establish a reactor model. Intrinsic low-wheel harmonics differ from borrowed sources and must keep their own phase semantics. |
| 145-150 | 023: expression | Expression belongs within the loaded common AO-28 preamp and differs from final monitoring gain. Unknown capacitance curves, loading and feedback prevent component claims. A moving capacitor needs `d(C*v)/dt`, including `v*dC/dt`; a fixed-coefficient approximation needs declared limits. |
| 151-156 | 024: console/input | Audio owns applied controls; input adapters retain source/destination ownership. Persistent controls and replay checkpoints are different artifacts. MIDI and VST3 semantics require separate adapters; routing changes must not strand held-note releases. Panic, channel modes, transport and virtual power are distinct policies. |
| 157-162 | 025: scanner line | The documented nominal circuit has 18 inductors, 18 capacitors and 19 outputs, with common-return and divider loading. Independent complex response and persistent energy-state tests precede physical acceptance. This session should preserve the ongoing scanner worker ownership. |
| 163-168 | 026: scanner rotor | Sixteen physical positions, nine selected terminals and nineteen ladder outputs are different domains. The printed p. 166 traversal has fifteen entries despite modulo-16 indexing; this is already retained as E01 in the repository errata. Capacitive interpolation is not a succession of metallic switches. |

## Current implementation compared with the atlas

At the inspected revision, `ControlSnapshot` holds four nine-position A/B banks,
two selected-bank values, two route-enable flags, expression, percussion settings
and two pedal positions. It has no fixed-registration selection. `ControlState`
explicitly describes itself as an early exclusive A/B selector.

`Engine::rebuild_coefficients()` reads the selected A/B bank directly and enables
percussion when the upper route is enabled, its bank is B and the tablet is on.
Any fixed-preset integration must change the resolved route deliberately; merely
copying preset digits into bank B would destroy inactive-bank memory and could
leave percussion incorrectly enabled. `SelectBank` reconnects the route, while
Cancel preserves held keys, banks and source history. The existing `PerformanceInput`
transaction already provides a bounded shared note/control timeline; a new preset
event must participate in its admission and rollback policy.

The nominal contact model already has independent thresholds and make/break travel
for all 1,098 manual contacts, partial-position targets, stopped rate migration
and processing-thread ownership. Its 8/12 ms travel and threshold values are
clearly proposed. Percussion already uses one `shared-readiness-v1` state with
documentary RC hypotheses and preserved history. Reimplementing those completed
surrogates would add less value than exposing the missing fixed-registration
domain or a standalone adapter to the same controls.

## Recommended next dependency-ready slice

The integrator selected a conflict-free **M9 native standalone adapter using
pinned SDL2 2.32.10 against the unchanged core** for this session. This is a
session implementation decision, not a dependency verification performed by this
reviewer. Pages 151-156 support the central architectural requirement: the
standalone must reuse the existing canonical commands, ownership and applied
state instead of introducing a second DSP authority. The fixed-preset proposal
below is retained as the next source-backed M3 recommendation, not current
implementation scope.

**Implement the named documentary chapel presets with an exclusive selector,
then carry that behavior through snapshots, automation, rendering and the actual
native module.** This advances a specific unfinished M3 item without requiring
new scanner mathematics or fabricated component measurements. The scoped result
is an exclusive nominal preset model, not complete physical cradle/loading
behavior.

The p. 122 table, visually checked in this assignment, is:

| Preset | Upper | Lower |
| --- | --- | --- |
| C-sharp | `005320000` | `004545440` |
| D | `004432000` | `004423220` |
| D-sharp | `008740000` | `007373430` |
| E | `004544222` | `004544220` |
| F | `005403000` | `006644322` |
| F-sharp | `004675300` | `005642200` |
| G | `005644320` | `006845433` |
| G-sharp | `006876540` | `008030000` |
| A | `327645222` | `427866244` |

These 162 digits are an atlas transcription of the approved factory chapel
arrangement. They are not a measured specimen, universal surviving-organ defaults
or a recovered companion file. Require an independent comparison with the named
factory Table IV, printed 4-1, before calling the factory transcription fully
reviewed. An atlas-only provisional import must retain that narrower evidence.

### Concrete acceptance and integration contract

1. Give the table a versioned identity, exact digit strings, source/page/hash,
   interpretation and review status. Reject wrong dimensions, dropped leading
   zeros, digits outside 0-8, duplicate/missing manual/preset identities and broken
   references without replacing an admitted profile.
2. Add a typed exclusive selector for nine fixed routes plus A-sharp/B, with
   Cancel as a separate action. Keep all four banks intact. Editing a bank under
   a fixed preset must not change sound or select that bank.
3. For each of eighteen fixed registrations, compare nominal audio with an
   independently initialized equivalent drawbar bank using the same source
   state. Include colliding foldback notes and held chords. Do not accept table
   self-consistency alone as the audio gate.
4. Exercise upper B to fixed preset to B, including held ninth-contact detector
   activity, same-offset events and partly recovered percussion. Preserve the
   documented nominal recharge policy without claiming measured transition
   equivalence. Lower selection/Cancel must preserve upper percussion and pedal
   ownership/settings.
5. Preserve all existing parameter IDs, event values and state readers. Append
   controls and specify migration before changing the saved format. Ordinary
   restore contains controls only; a fixed registration must never resurrect
   notes or restart sources. Test malformed late fields atomically.
6. Verify partition invariance, zero-frame behavior, failed-callback rollback,
   allocation boundaries and unchanged legacy audio where no fixed preset is
   selected. Qualify one coherent source snapshot after scanner changes have
   been integrated; Engine/ControlSnapshot header changes require rebuilding all
   consumers together.
7. Expose the selection in the actual native controller/processor and strict
   offline fixtures, with a reproducible musical demonstration and source/data
   identities. Keep actual host execution distinct from a standalone device or
   UI claim.

The shared Engine/state paths overlap a possible future scanner-integration phase,
so the integrator must coordinate those paths and reserved parameter/state
versions. The new preset data, compiler, independent source review and acceptance
fixtures can begin without touching scanner modules. If conflict-free product
work is preferred, a standalone adapter using the canonical input and control
interfaces is also dependency-ready under pp. 151-156; it should not create a
second DSP or state authority.

Continuous loaded drawbars, simultaneous-latch audio, full expression and pedal
reactor physics remain open. Their source/measurement gaps are concrete and must
stay visible rather than being filled with generic filters or attractive curves.

## Reproduction record

Working directory for repository reads:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

The extracted text input was
`/workspace/scratch/5ba97739b54c/atlas/part2.txt`, 5,001 lines. All lines were read
using contiguous `sed -n` ranges `1,612`, `613,1211`, `1212,1801`, `1802,2409`,
`2410,2985`, `2986,3587`, `3588,4217`, and `4218,5001`; none of those text-read
outputs was truncated. Some later broad repository-document inspections were
truncated and were not used to claim complete-file coverage. Source checks used
`git status --short`, `git rev-parse HEAD HEAD^{tree}`, `rg`, and `sha256sum`.

Visual commands were `pdftoppm -f 122 -l 122 -scale-to 1700 -png -singlefile`
and the corresponding page-151 command on the source PDF, followed by actual
image inspection. Temporary images remain outside the repository. No new test,
measurement, host run, publication or physical-fidelity pass is asserted here.

# A02 — full atlas console reading and next product work

Assignment: `/root/w01_a02_atlas_console`, wave 1. Scope is this note only;
no product edits, builds, runtime tests, commits or hardware acquisitions.

## Coverage and method

Read all 84 PDF pages **85–168**, including their equations, tables, pseudocode,
source qualifications and acceptance proposals, from the supplied page-delimited
`part02-085-168.txt`. Reads covered 85–94, 95–104, 105–114, 115–124, 125–134,
135–144, 145–154, 155–164 and 165–168 without truncated PDF output. This is
complete extracted-text coverage, not a claim to have visually verified each
embedded photograph or source schematic. Read `AGENTS.md` and the complete
M0–M9 `docs/PLAN.md`; retained current ownership and preservation rules.

The unchanged atlas SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`;
this extracted part's SHA-256 is
`2ee316a331cead940fd04cb36beada8128795511afa314388ea43a01945670b9`.

Inspected `ConsoleModel.h`, `ControlState.h`, `FixedRegistration.h/.cpp`,
`Engine.cpp`, `Percussion.cpp`, `MidiInput.h/.cpp`, preset drawing/selection code,
the frozen preset contract and relevant MIDI/remaining-M3 contracts. Findings
are source inspection at starting commit `647ae1b`, not newly executed tests.

## Requirements recovered from every chapter in this range

| Pages | Requirement and evidence boundary |
| --- | --- |
| 85–90 | Separate common mechanical timing, local shaft/gap residuals, electrical hum, scanner and cabinet motion. Preserve shared phases through silence and notes; deterministic sample-indexed residuals require analytic sideband tests. Historical forcing rates do not determine measured modulation depths. |
| 91–96 | Keep immutable observations, editable profiles, compiled banks and playback state distinct. Strict parsing, complete unique 1–91 IDs, units, explicit unknowns, waveform boundary and immutable provenance are mandatory. Table V G–G service voltages are not raw oscillator gains. Serial-number inference cannot override observed retrofit evidence. |
| 97–108 | Compile all 549 manual routes with low-fold and repeated high-fold rules. Shared source collisions retain separate contact/gain paths. One free-running source field supplies both manuals; sample-rate changes preserve phase. Numerical oracle, interpolation, bandwidth and callback cost require separate evidence. |
| 109–120 | Retain nominal ascending 3 dB gains and coherent sums separately from loaded transformer networks. Continuous drawbar travel is conductance/connectivity, not an assumed crossfade. Contact attacks and releases need independent histories; phase-dependent value and slope jumps both matter. The proposed switching RMS budget is a project target, not a measured pass. |
| 121–126 | Ordinary exclusive presets preserve all inactive banks and held keys. C is momentary Cancel and never a latched key. Eighteen chapel rows contain 162 documentary tap assignments. Simultaneous physical latching needs eleven contacts and an electrical loading model; summing presets is unsupported. Patch recall differs from runtime continuation. |
| 127–138 | Percussion is shared, upper-B eligible, keyed by the physical 1-foot contact. Joining notes do not reset readiness; zero-time off/on gives zero recharge. Borrowed harmonic audio, sustained return, upper attenuation and envelope gain remain distinct. Calculated RC products are not measured audible decay times. |
| 139–144 | Pedals use the shared field, eight contacts, four buses and two mixtures. Preserve all 200 positions including five disconnections and unusual third-contact routing. Low-wheel spectra, reactor/load values and proposed 475-state acquisition remain unmeasured. |
| 145–150 | Expression separates controller calibration, mechanical travel, loaded AO-28 transfer and downstream monitor gain. CC11 mapping may calibrate endpoints/inversion before the instrument curve. Moving capacitance requires charge-aware analysis; photoreal pedal artwork supplies no electrical evidence. |
| 151–156 | One audio-owned state, stable origin/destination ownership, deterministic same-sample ordering and applied snapshots. CC120, CC121 and CC123 require distinct scoped semantics. Virtual power, transport and rotor commands are independent; ordinary controls never promise sample-exact continuation. |
| 157–168 | Scanner domains are 18 LC sections, 19 circuit outputs, nine terminals and 16 positions. Preserve loading, signed return and physical state. Page 166 prints only fifteen traversal entries despite indexing sixteen; retain the existing erratum rather than copying it. Physical overlap/loading remain unknown. |

## Current implementation versus next work

The nominal core already retains four banks, exclusive fixed selection,
non-latching Cancel paint, shared source phase and shared percussion readiness.
`Engine::process()` still applies expression as a final normalized scalar.
This is accurately declared in `ControlSnapshot`; replacing it silently with
guessed AO-28 coloration would violate the baseline contract. Physical multi-latch,
continuous tap loading, loaded expression and calibrated percussion remain open.

Two bounded M9 tasks are ready without changing the **47 parameter identities**,
**B3CONTROLS4**, readers 1–3 or the dry sound model:

1. **Expression-controller calibration.** Add an adapter-owned, versioned CC11
   endpoint/inversion configuration before parameter 8192 conversion. Accept
   monotonic endpoint mapping, range/clamp rejection, identity-default equivalence,
   identical GUI/engine-applied values, epoch-safe changes and continued held-note
   ownership. Device settings must not enter sound state4. State the existing
   nominal expression law honestly.
2. **Explicit MIDI channel-mode extension.** `MidiInput` presently admits CC123
   and deliberately rejects CC120/121. Freeze their separate semantics before
   implementation: addressed sound suppression must preserve other origins and
   divisions; controller reset must not reset presets, source phase or ownership.
   Acceptance needs repeated commands, shared-pitch UI/MIDI ownership, held pedal
   cases, complete snapshot acknowledgment, queue failure and partition invariance.
   Do not simply map CC120 to CC123 or global Panic.

These are candidate tickets for integrator selection, not permission to expand
another session's R4 ownership. Physical fidelity, connected scanner/cabinet
audio and whole-interface 1:1 equality remain separate unclosed gates.

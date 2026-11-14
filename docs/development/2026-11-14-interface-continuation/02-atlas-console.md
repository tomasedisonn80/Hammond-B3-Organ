# A02 — Complete atlas reading: pages 85–167

## Actual scope and source

- Actual worker: `/root/w01_a02_atlas_console`, wave 1, assignment 02.
- Source checkout inspected at `d493e998e5dd7cf44db46854e87309745063ac54`.
- Read all **83 pages, inclusive 85–167**, from the unchanged
  [500-page atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf).
  Its retained SHA-256 is
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Method: complete `pdftotext -layout` reading in bounded page ranges, recovering
  the initially truncated 85–96 range in full; original PDF page 166 additionally
  rendered with Poppler and visually inspected. This is not a claim that every
  referenced external source or figure received a new independent review.
- Read `AGENTS.md`, the inherited current plan/status/README/next-step context,
  and the current preset handoff, atlas review and latest development-log entries.
  The sole owned repository output is this note. No code, shared status files,
  source PDF, historical records, builds, commits or remote refs were changed.

## Complete chapter coverage and software dependencies

| Chapter / PDF pages read | Main requirements and dependencies |
| --- | --- |
| 013 / 85–90 — Mechanical modulation | Separate drive/shaft angular error, changing pickup gap, electrical hum, scanner and Leslie motion. The derived 100/120 Hz mains forcing rates are not measured modulation depths. Common phase and sample-indexed seeded residuals continue through silence and notes. Validate steady rotation before optional startup/coast; the latter also needs an electrical-output model. Model-A measurements cannot become B-3 defaults. |
| 014 / 91–96 — Calibration data | Separate immutable observations, authored model profiles, compiled runtime data and playback state. Preserve one-based tone IDs, units, waveform boundary and phase domain. Unknown is null with a reason; strict admission rejects duplicate names/IDs, nonfinite numbers, dangling references and contradictory signal boundaries. Table V G–G service readings are not pickup gains. An invalid load leaves the previous bank and playback state intact. |
| 015 / 97–102 — Manual routing | Distinguish 61 playing-key indices, nine drawbar indices, electrical tones, physical terminals and storage offsets. The specified MIDI 36–96 range is a software adapter convention. Preserve all 549 routes, low 16-foot fold and repeated upper octave subtraction. Folded collisions share one source waveform but retain separate contacts and branches. The second manual has the same source map and distinct ownership/downstream paths. |
| 016 / 103–108 — Shared generator runtime | One 91-source field owns continuing phase; keys and drawbars do not allocate oscillators. The same coefficient/profile data feeds the scalar oracle and optimized paths. Rate preparation, no-sample flush, sample-offset ordering, immutable publication and off-thread reclamation are explicit lifecycle contracts. Bandwidth and interpolation error are separate; switching/nonlinear stages need their own alias analysis. |
| 017 / 109–114 — Drawbars/mixing | Physical 0 is mute and 8 is full. The nominal ascending 3 dB law is a declared reference, not a measured transformer response. Preserve four banks, source coherence, separate manual networks and lower/pedal connection. A continuous-contact travel model needs branch connectivity/conductance and the overlap resistor; a smooth slider is not that circuit. Production winding/load data remains unknown. |
| 018 / 115–120 — Contacts/key click | Nine histories per key share a mechanical cause; make and break require separate models. Ordinary MIDI selects a named synthetic gesture and need not scale sustained loudness. Source phase at each edge determines switching transients. Fractional timing, bounded event capacity, deterministic ordering, retained filter tails and a high-rate/edge-correction reference are required. The cited C-3 onset study does not calibrate B-3 release or universal click spectra. |
| 019 / 121–126 — Presets | Twelve reversed keys per manual: momentary C Cancel; nine fixed C#–A routes; A#/B select existing adjustable banks. Table IV's 18 rows are an approved chapel arrangement, with 162 tap assignments and preserved leading zeros. Ordinary exclusive selection is a useful abstraction; simultaneous physical latching and loaded switching are additional, unqualified behavior. Upper-B percussion interlock and charge history share the event timeline. |
| 020 / 127–132 — Percussion trigger | One manual-wide control state follows the upper-B 1-foot keying route, not one envelope per note. A silent audible drawbar does not remove its keying contact. Multiple owners of one pitch require bounded matching/release rules. Zero-time off/on supplies no recharge interval; preset/tablet changes preserve history. Structural, host-policy and specimen-dependent acceptance are separate. |
| 021 / 133–138 — Percussion circuit | Freeze AO-28 revision and schematic identity. Borrow the selected harmonic, preserve its sustained return and model normal attenuation separately from percussion level. The isolated RC calculations are electrical time constants, not audible decay durations. Fast/slow affects bias as well as rate; output/loading/valve parameters need captures. Percussion bypasses scanner, and the sustained return must not be added twice. |
| 022 / 139–144 — Pedals | 25 pedals, eight contacts, four buses and two coupled drawbar mixtures consume the common generator. Preserve the unusual third-contact mapping and its five absent positions: 195 connected entries in 200 slots. Intrinsic low-wheel partials and borrowed sources have different phase/frequency meanings. Reactor, contact, spectrum and loading values remain unmeasured. Optional monophonic/sustain behavior is a separate extension. |
| 023 / 145–150 — Expression | Separate physical position, controller calibration, loaded AO-28 electrical transfer and final monitoring gain. The capacitive loud/soft paths are not established as a linear crossfade. Parameter motion preserves generator/percussion/scanner history; simultaneous input sources resolve to one trajectory. Stationary fitting precedes moving-gesture comparisons. An expression position display and final-output meter describe different quantities. |
| 024 / 151–156 — Console state/adapters | Audio owns applied control/history; UI/MIDI/host adapters request changes through one ordered contract and copied display state. Releases use the destination retained by the original owner. Continuous curves, discrete selectors and same-offset note order must remain deterministic. Patches preserve controls; exact checkpoints additionally require dynamic histories. Virtual power, rotary command and host transport are independent. Panic and MIDI channel-mode actions have distinct scopes. |
| 025 / 157–162 — Scanner line | The selected nominal research circuit has 18 inductors, 18 capacitors and 19 voltages. Preserve signed common-return references, compensated early taps, termination, source/load identity and actual reactive state. Independently solve the complete graph before realtime parity; numerical parity and specimen agreement are different exits. The paper's nineteen-stage prose is inconsistent with its explicit graph. |
| 026 / 163–167 — Scanner rotor, first five pages | Distinguish 16 stator positions, nine scanner terminals and 19 ladder outputs. Factory 412 rpm is nominal, with a derived 6.8667 Hz rate, not a measured precision value. Capacitive plate transfer and conductive output brushes are different mechanisms. The two-neighbor crossfade is an unloaded approximation. Rotor angle continues through silence/bypass/mode changes; angle-resolved transfer and independent loading evidence are still needed. Page 168 belongs to the next reader's range. |

## Concrete consequences for the next M9 interface work

1. **Keep views as views.** Workspace changes, redraws, resizing and help or
   inspection panels must consume copied state. They must not reset phase,
   rebuild the generator, retrigger notes, change registration, retire another
   input's owner or recreate percussion readiness (pp. 105–106, 151, 155).
   An applied-state acknowledgement can distinguish pending input from the
   actual sounding selection; a visually selected control alone is not proof
   the audio thread accepted it.
2. **Preserve the playable inventory and correct semantics while matching art.**
   Each manual has 61 playing keys plus a separate 12-key reversed octave, with
   C visually returning after its Cancel action (pp. 97, 121). Four adjustable
   banks retain independent positions; fixed selection must not overwrite them
   or make edits to an inactive bank sound immediately (pp. 114, 123–126).
   C cancels only that manual's registration and preserves held keys, the other
   manual and pedals. It is distinct from emergency Panic.
3. **Separate a displayed bank from a sounding fixed route.** Show the selected
   route and the bank being edited as different state. A#/B expose existing bank
   positions without copying; C#–A select immutable documentary tap rows.
   Preserve the physical footage order and 0→8 direction (pp. 109–114, 122).
   Labels should identify the chapel documentary basis and nominal gain model
   where evidence status is relevant.
4. **Do not turn cabinet/service art into fictional audio controls.** Scanner,
   Leslie and power widgets may show truthful implementation status or inspect
   a schematic, but their presence must not imply a connected audio effect or
   measured motion model (pp. 85–90, 154, 157–167). A scanner view should label
   stators, terminals, line outputs, rotor and brushes separately. Use a stated
   schematic scale unless dimensions exist (p. 164).
5. **Retain correct coupled controls.** Percussion eligibility depends on the
   upper B route, with separate normal/soft, fast/slow and harmonic decisions;
   a lit tablet alone is insufficient (pp. 124, 127–138). Expression shows one
   common position, with its nominal status preserved; do not present it as a
   calibrated AO-28 electrical transfer or conflate it with an output meter
   (pp. 145–150).
6. **Keep saves and view settings scoped.** Ordinary instrument settings must
   not save held ownership or claim sample-exact engine continuation. Reverse
   keys do not recall Leslie speed, scanner, expression or generator profiles.
   Any new view preference belongs in a clearly scoped UI setting, without
   silently changing the existing parameter/state schema (pp. 126, 155).

Useful acceptance scenarios for a new interface surface are a held chord while
switching views/resizing; independent UI and MIDI owners; fixed→Cancel→bank
selection; inactive-bank edits; upper-B percussion during route changes; and
save/load with explicit raw versus applied state. These are proposed next checks,
not tests performed by this reading assignment.

## Confirmed source erratum and limits

Original page **166**, checked in the rendered PDF, calls its rotor order a
16-entry sequence but prints only 15 values:
`[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2]`. Its modulo-16 indexing and stated terminal-2
to terminal-1 wrap require the missing final interval. Preserve the repository's
existing [erratum](../../research/ERRATA.md) and frozen scanner contract; do not
copy the printed pseudocode into a new diagnostic illustration or runtime.

The atlas repeatedly distinguishes documentary data, derived numerical checks,
provisional models and specimen measurements. Its companion-file references do
not establish that those companions are present in this checkout. This reading
performed no DSP, UI, realtime, host, device or physical acceptance and supplies
no 1:1 sound/appearance result. It supports the next software scope while keeping
electrical loading, contact physics, scanner audible policy and hardware capture
dependencies explicit.

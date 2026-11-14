# A04 - Complete atlas reading: Leslie electronics, motion and acoustics

## Assignment and verified source

- Actual worker: `/root/w01_a04_atlas_rotary`, wave 1 of this new session.
- Owned output: this note only. No code, shared status, historical ledger or
  publication changes are included.
- Inspected repository HEAD: `0f7b90037e51e101d8fa0bfe31af40209d751659`.
- Source: [unchanged research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Read every extracted word on **PDF pages 253-336 inclusive**, 84 pages,
  **217,020 characters**, covering all of chapters 041-054. Page numbers below
  refer to this PDF's numbered pages, not to the service manuals it cites.
- The first combined tool output was truncated. I reread both six-page halves
  of pp. 253-264 separately; all retained coverage was then available in
  untruncated batches: 253-258, 259-264, 265-276, 277-288, 289-300, 301-312,
  313-324 and 325-336.
- Rendered and visually inspected PDF **pp. 272 and 283** at 1600-pixel longest
  dimension. The former confirms the floating treble-return drawing; the
  latter confirms a stationary woofer over a separate rotating deflector.
- Read `AGENTS.md`, the new [MIDI/UI scope](../../MIDI_UI_SCOPE.md), the
  separately owned [rotary scope](../../ROTARY_SCOPE.md), and the current
  status/development-log entry. Other workers' untracked session files were
  preserved.

This is source and architecture review. It does not execute a new DSP module,
MIDI backend, physical-device comparison or acoustic-fidelity gate.

## Findings across every assigned chapter

| Pages / chapter | Requirements and limits relevant to continuation |
| --- | --- |
| 253-258 / 041: 122 input and control | The vintage baseline is the 1971 117 V, 60 Hz amplifier assembly 036616 without optional reverb. Audio driver, control detector, relay and mechanical motion are separate responsibilities. Differential voltage means the full leg-to-leg voltage. A slow/fast command never resets rotor angle or source phase. Requested speed and actual rotor states must be distinct in the UI. |
| 259-264 / 042: 147 differences | A 147 has a separate single-ended port, control and feedback topology. Shared transformers or exterior dimensions do not establish a common transfer function. Cabinet, amplifier and source-adapter identities remain separate. A 122/147 UI choice requires actual corresponding blocks; a generic brightness control cannot stand in for that implementation. |
| 265-270 / 043: power stage | The output pair, transformer, reactive load, bias and supply belong to a connected model. Numerical-reference agreement, measured electrical agreement and listening evidence are different gates. Missing transformer ratios, valve curves and supply/load data remain explicit. A cabinet illustration or distortion plot cannot qualify these dependencies. |
| 271-276 / 044: crossover | Source values are L2 3.2 mH, L3 5.2 mH, C16A 7.8 microfarads and C16B 12.5 microfarads. The treble branch has a floating return, visually confirmed on p. 272. The nominal 800 Hz identity is not permission to substitute a generic crossover. Electrical port phase, driver loading and later radiation ownership must remain explicit. |
| 277-282 / 045: horn | The compression driver is stationary; one horn is fed and the opposite structure balances it. Photograph dimensions are unqualified without a scale. A Leslie 600 research dataset or ID-40 example supports a method, not a calibrated vintage-122 preset. Every microphone consumes the same mechanical trajectory at its own relevant emission time. |
| 283-288 / 046: lower rotor | The woofer basket is fixed; a separate deflector rotates. A frozen rotor remains a static acoustic filter and need not mute bass. Transmission, delay and cabinet interference cannot be collapsed into independent arbitrary tremolo oscillators. Bass has its own evidence, geometry and response boundary. |
| 289-294 / 047: motor/belt dynamics | Horn and drum have independent mechanical profiles and directions. Shaft speed and rotor speed differ. Vintage baseline commands are Slow/Fast. Brake/coast/Stop is a separately identified extension; neither instantaneously zeros angular velocity or parks at a chosen angle. The documented 5-8-second bass service criterion is not a universal exponential time constant. |
| 295-300 / 048: cabinet | Appearance and acoustic geometry have separate evidence states. Outer dimensions cannot determine hidden cavity volume, wood substrate or internal construction. Rear-panel state changes the acoustic profile. Cabinet, room and measured-kernel effects each need one owner. A visually convincing cabinet can be delivered while physical acoustic fields remain unknown. |
| 301-306 / 049: propagation | Use one source trajectory and solve emission time for each receiver/path. The atlas independently flags sign and interpolation-endpoint errors in a cited paper; copy no pseudocode without checking its convention. Runtime work is bounded, histories cover the largest path, and algorithmic latency is separate from physical transit. The atlas's synthetic solver result is not a repository runtime or hardware result. |
| 307-312 / 050: directivity | Directional response is complex and frequency dependent. Retain absolute angular gain, phase and measured boundaries. A complete cabinet response cannot be rotated as if the cabinet walls moved with the horn. Null-related phase spikes are not independent motor accelerations. Smooth animation does not establish acceptable acoustic interpolation or alias behavior. |
| 313-318 / 051: microphones | Scene identity is independent of organ/electronics identity. Capsule position, aim and rotor angle are different quantities. Stereo receivers share sources and motion while preserving separate delay/phase. A knob labeled horn/bass must not imply band-isolated physical receivers. Generic cardioid geometry is not a calibrated commercial microphone model. |
| 319-324 / 052: state/scheduler | Notes, tempo, repeated unchanged commands, editor closure and UI refresh cannot restart or drive rotors. Canonical sample events have deterministic equal-time ordering and explicit bounded overflow. The UI reads snapshots. Rate changes preserve physical state under a new clock epoch, and ordinary musical presets are separate from complete transient-history checkpoints. |
| 325-330 / 053: time-varying convolution | Input-time and observation-time angular weighting are different systems, even when their frozen-angle responses agree. Keep filters/histories running through angle changes. New profiles require warmed history and explicit transitions. Matching a static image or spectrum cannot qualify moving behavior; retained tails and live transitions require their own tests. |
| 331-336 / 054: room/RV | Direct electrical organ output, captured cabinet sound and optional studio reverb are distinct modes. Full two-input/two-output convolution needs four kernels unless absent coupling is established. 122RV spring/return electronics and its stationary speaker are a separate optional branch. Do not add rotor Doppler to that fixed speaker or import optional reverb into the baseline 122. |

## Decisions for the reference-oriented native interface

### Cabinet imagery can advance before cabinet audio

The current scope can show the supplied reference cabinet as artwork. Its status
must distinguish appearance from an implemented, calibrated acoustic scene.
Pages 295 and 300 expressly allow polished visual work with unresolved hidden
geometry while rejecting a measured-CAD claim. The same distinction must survive
the README: an actual application screenshot demonstrates the application's
layout and state, while the reference image remains design evidence.

The right-side cabinet composition should not display invented rotor RPM, model
confidence, microphone distance or audio levels. With the current dry output,
scanner and rotary controls can be visibly unavailable, and a service view can
explain their current implementation status. A lit control must correspond to an
actual retained setting or an explicitly identified preview mode. Artwork must
not make an unconnected cabinet appear to process the rendered audio.

### Preserve physical distinctions if animation is added later

Keep separate render objects for the stationary treble driver, one active horn,
the balancing side, stationary woofer and moving lower deflector (pp. 277-286).
Do not orbit the speaker basket. At integration, use copied horn/drum state from
the owning module; each rotor keeps its own phase and speed. A UI-frame stall,
tab change, close or note event cannot advance/reset those states (pp. 292,
319-322). Decorative preview motion, if offered, must be identified as such and
must not masquerade as those snapshots.

The concept's Stop control conflicts with the ordinary two-speed baseline in
pp. 256, 289 and 294. Preserve that discrepancy in the design comparison; do not
silently add a historical Stop mode to match generated artwork. Likewise,
microphone geometry controls require a real scene contract before they can
claim acoustic effect. Editing camera position must not rewrite microphone
coordinates or the audio state.

### Keep service information specific and readable

A useful initial service view can show the exact nominal dry model and which
future modules are unconnected. It can separate documented source values,
derived numerical fixtures, proposed parameters and missing physical captures
without decorative telemetry. Do not show a universal similarity percentage:
pp. 282, 288, 300 and 318 require named boundaries and independent held-out
evidence for stronger claims.

## Decisions for external MIDI and adapter integration

The selected MIDI work is independent of the unfinished M5/M6 physical chain.
It should preserve the current Session and Engine semantics while adding a
bounded, explicitly owned input path.

1. **Freeze event time and order.** Pages 256, 292 and 321 require timestamped
   canonical commands and deterministic ties. The current Session admits
   offset-zero events, so an adapter can honestly deliver at the next callback
   boundary. Device arrival timestamps do not by themselves provide
   sample-accurate rendering. Retain the chosen ordering and late/out-of-order
   policy in the contract and diagnostics.
2. **Keep the UI out of the engine clock.** Serialize device input through the
   main producer and its bounded inbox, rather than making a MIDI callback a
   second Session producer. Rendering and window refresh must consume copied
   state without entering live DSP or altering its timing (pp. 304, 310,
   321-322 and 328).
3. **Make exhaustion and lifecycle observable.** Define the admitted event
   density, overflow response, disconnect release, reconnect/start policy and
   joined shutdown before implementation. No unbounded event retry, memory
   allocation, file access or blocking synchronization belongs in the audio
   callback (pp. 256, 280, 298, 304 and 328).
4. **Preserve stable identity across control changes.** Page 321 explicitly
   preserves public parameter IDs and saved-state mappings when extending
   controls. A MIDI mapping is an adapter contract, not permission to rewrite
   the existing 45 controls or save transient note/motion histories in an
   ordinary musical snapshot (p. 322).
5. **Keep future cabinet control separate.** If rotary integration arrives
   later, map a controller to semantic Slow/Fast commands with stable discrete
   rules; do not map it directly to arbitrary instantaneous speed or phase.
   Repeated messages must retain motion continuity. The present UI/MIDI scope
   must not quietly attach the research rotor module to the dry graph.

## Concrete acceptance recommendations

For this session, retain independent tests of UI/device note ownership,
velocity-zero release, deterministic equal-time/arrival order, event queue
exhaustion, disconnect/restart, empty processing and UI focus loss. Include a
simultaneously held UI note while the device disconnects. Verify control loads
and editor changes do not silently replay or release device notes. Separate
synthetic transport injection, actual backend startup and physical-controller
observations in the report.

Capture the actual application at the reference size and minimum supported
size, with readable musical state and honest module availability. Compare
major panel landmarks, materials, key fronts, control spacing, label clipping
and active state with the supplied image; keep intentional semantic corrections
and remaining visual differences explicit. A frozen reference bitmap alone
does not satisfy a working-UI gate.

Do not broaden this session into an unsupported acoustic completion claim.
The next end-to-end cabinet integration still depends on connected dry-organ
electronics, a declared loaded Leslie/driver boundary, completed numerical
rotary gates, and physical captures for specimen calibration. Keep the existing
separate rotary ownership and its current acceptance results intact.

## Verification and handoff

Executed source checks: read the stated 84 page files completely; recomputed
the original PDF SHA-256; counted the assigned extracted characters; inspected
the repository HEAD/worktree; rendered pp. 272 and 283 with `pdftoppm`; displayed
and reviewed both rendered pages. No build or runtime test was necessary for
this read-only source assignment, and none is claimed. The full scope, source
locator and findings are now retained here for the contract and UI workers.

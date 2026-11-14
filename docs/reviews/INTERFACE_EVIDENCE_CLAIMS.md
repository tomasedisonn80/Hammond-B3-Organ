# Interface implementation and evidence claims

**A38: the inspected sound-model and inspector claims are supported; root corrected
the observed documentation wording.** This is source/evidence review,
not new execution. The initial recorded read snapshot is based on HEAD
`5d81199a9822874b55f3b0a124715cbd6eadf0e5`, with an active working overlay.
[Read identities](../development/2026-11-14-interface-continuation/reports/a38-read-snapshot.json)
and the [closing record](../development/2026-11-14-interface-continuation/reports/a38-evidence-claims.json)
identify each inspected input and concurrent changes; HEAD alone does not identify
the UI. A23's 34-row acceptance and A28's scale/text work were read, not repeated.

## Claim-to-implementation matrix

Source locators below are repository-relative, with line numbers at this reading.

| Current claim | Implementation/evidence | Qualification |
| --- | --- | --- |
| 47 sound parameters; state4 writer and readers 1–3 | `include/hammond/ParameterBridge.h:12`; `src/ControlStateIO.cpp:173–196,239`; retained `root-protected-boundary-recheck.json` reports 114 protected inputs unchanged from `d493e998`. | UI workspace/focus/Flat choices are outside this registry and persisted controls. No new preservation test is claimed. |
| 91 continuously shared sources; two 61-key manuals and 25 pedals | `include/hammond/Types.h:8–10`; `include/hammond/PedalRouting.h:14`; `src/TonewheelBank.cpp:91–103`; `src/Engine.cpp:240–275,429–473`. | One source frame feeds both manuals, nominal percussion and pedals during processing, including silence/disconnected output. Fixed rows reuse profile gain indices; documentary routing does not calibrate loaded gains. |
| Active `ideal-contacts-v1` | `apps/standalone/Session.cpp:219–220` calls the two-argument prepare; `src/Engine.cpp:69–70` selects `include/hammond/ConsoleModel.h:13,19–20`. | The separately available `nominal-linear-travel-v1` and its proposed 8/12 ms defaults are not the active standalone contact path. |
| Nominal profile frequency/gain | `apps/standalone/InspectionModel.cpp:272–287` reads `profile.sources[45].frequency_hz` and `profile.output_gain`; `include/hammond/Profile.h:16–35`. | Values are loaded software data, not measurements or hardcoded live readings. The supplied authoring profile proposes 440 Hz and 0.03 output gain; a valid supplied profile remains authoritative. |
| Copied applied state, pending edits and unknowns remain distinct | `InspectionModel.cpp:128–134,150–245,270,295–303`; `apps/standalone/main.cpp:1678–1686,2262–2263`. | Applied values use the copied snapshot; Edit uses transient UI state. Unprepared/unavailable observations remain words. Retained/stopped copies are explicitly classified; no private readiness telemetry is invented. |
| Scanner, complete AO-28 and Leslie audio are unconnected | `InspectionModel.cpp:316–374`; complete dry mix in `src/Engine.cpp:240–282`. | Scanner is explicitly a research module; percussion is a nominal surrogate. V/rpm/m labels accompany unavailable/unacquired physical quantities. Leslie 122 is a documentary target, with 147 separate; Stop/brake is not modeled. |
| Original reference and actual captures have different provenance | `docs/design/atlas-reference.json`; `examples/demos/standalone-interface-preview-v1/provenance.json`; A32 comparison. | Original JPEG is PDF object 3, pages 1/409. A22's eight images are actual dummy-driver captures of executable `005db1e2…`, before A28/A31/A34. They do not qualify the later renderer or physical devices. |

## Qualification and wording findings

The eleven hosted passes belong to published **5d81199**. The initial UI run
remains **146/147**, executable `55b094…`; A35 then passed twelve methods/24
processes on that frozen executable and two affected methods/nine prefixes on
`968938…`. A31's separate raster repair is retained. README/status correctly
avoid turning these records into a full pass on an unbuilt later revision.

1. **Resolved:** the first-read current session `README.md:3` said **“It has its own 60 actual
   agents”**. At the recorded audit reading the manifest contained 37 dispatched
   rows, 34 accepted and three running. Root now explicitly says **“It requests
   60 distinct actual agents”** and defers actual counts to the manifest. The
   corrected wording was read directly; historical workers are not recounted.
2. **Resolved:** root `README.md:32` previously said **“All control text … come
   from live copied state”**. Stable labels are native literals, while focus/Edit
   are transient UI state. Root now says the application renders native labels,
   values, positions, focus and held indicators, with applied sound values from
   copied state. This corrected sentence was read directly.
3. `apps/standalone/main.cpp:1800`, **“Loaded controls; waiting for the audio
   callback.”**, is the already retained A30 stale-notice finding, assigned to
   A36. Do not infer waiting from a static success notice after acknowledgment.

The first-read checkpoint's obsolete counts and pending A31 diagnosis were
**resolved by root's concurrent rewrite**, observed directly. Old/new hashes are
retained. Earlier 45-parameter/state3 sections explicitly retained as dated
history are not new-interface claims and should not be silently rewritten.

## Whole-plan boundary and next dependency

M0 has contracts with specimen/acquisition gaps; M1–M2 provide nominal engineering;
M3 implements substantial console behavior without measured contacts/loading.
M4 remains separate research with the observed G5 same-hertz failure. M5/M6 need
complete identified electrical graphs; M7 remains independent motion/propagation
research. M8 tooling cannot replace physical captures. M9 has working adapters
and this interface slice, with exact-source platform/device/accessibility/release
gates still separate. Six complete atlas readings and sixty eventual assignments
do not close M0–M9.

Next: finish A34 labels/title and A36 status, then A37's final operator flow.
A46 must create a **new source-qualified gallery** and update README while
preserving A22. Retain A32's **literal 1:1 not met** conclusion until an actual
later comparison changes it. Retain the corrected wording during the final
documentation/publication pass; no optional rerun follows this audit.

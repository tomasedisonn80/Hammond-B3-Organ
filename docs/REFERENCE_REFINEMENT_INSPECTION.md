# Inspection wording and genuine pending capture

## Reviewed scope

A11, wave 2, source `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`; implementation
and new capture acceptance remain pending. This contract follows the
[current scope](REFERENCE_REFINEMENT_SCOPE.md) and A01/A02 findings: rendering
observes copied state, desired controls await acknowledgement, and held targets
do not establish audibility (atlas pp. 34, 40, 151–156). Preserve 47 parameters,
state4/readers 1–3, owners, clocks, dry sound and unavailable model facts.

## Minimal wording repair

In `apps/standalone/InspectionModel.cpp::held_count`, after counting an observed
array, assign `target.unit = count == 1 ? "target" : "targets";`. Keep the existing
early return for `!observed`, decimal formatting, availability and evidence.
The three initial rows retain `"targets"`; no header, snapshot or parameter
change is required. `InstrumentView.cpp::inspection_value` already appends the
row unit, so the repair reaches actual Service text.

Apply these expectations independently to `contacts.upper_held`,
`contacts.lower_held` and `contacts.pedals_held`:

| Copied observation | Value | Unit | Availability / evidence |
|---|---|---|---|
| Prepared; none held | `0` | `targets` | Available / Software |
| Prepared; one target | `1` | `target` | Available / Software |
| Prepared; two or more | decimal count | `targets` | Available / Software |
| No snapshot, or unprepared | `Not observed` | `targets` | NotObserved / Unknown |
| Retained prepared copy | retained count | singular only for one | Available / Software |

Extend `test_standalone_inspection_author.cpp` with zero/one/two/maximum cases
(61/61/25), unavailable/unprepared cases containing nonzero backing arrays,
and retained singular cases. Extend independent
`test_standalone_inspection_acceptance.cpp` through real queued notes and
publications: two owners of one Upper key still mean `1 target`; releasing one
owner preserves it; releasing the last yields `0 targets`; two distinct keys
yield `2 targets`. Exercise Lower and pedals through their proper event types.
Keep cancellation, stopped-state clearing and failed-read retention assertions.
Invalid control formatting must not reinterpret separately observed held booleans.

## Existing boundary and missing capture

`UiModel::activate` publishes a desired `ControlSnapshot`; `Session::post`
copies it into the queue and returns a sequence; `UiModel::submitted` records
that sequence. `Session::render` applies the frozen queue prefix. A zero-frame
render flushes without advancing time. `UiModel::observe` retains desired state
until `resolved_sequence` acknowledges it. The existing inspection acceptance
test already exercises this deterministic boundary without forged Session state.

There is no deterministic whole-application pending capture switch. `main.cpp`
observes snapshots before painting, while callbacks run independently. Its
replay capture waits for completion and acknowledgement.
`tools/capture_standalone_interface.py::validate` expressly requires pending to
be false and desired/applied controls equal. Preserve that eight-view gallery
contract. Enlarging buffers, racing screenshots or sleeping the callback is
not a reliable replacement. The existing preset raster test paints pending
fixtures but constructs its applied snapshots; it cannot prove a Session queue.

## Bounded native harness

Add proposed `native_tests/test_standalone_inspection_raster.cpp` and CMake target
`test_standalone_inspection_raster`, compiling actual `InstrumentView.cpp` and
linking `hammond_standalone_drawing` plus `hammond_standalone_support`. Match the
existing native target conventions, define `HAMMOND_TEST_PROFILE`, and depend
on `hammond_profile`. Use `load_runtime_profile_file` with the compiled nominal
profile unchanged. No `main.cpp`, Session, callback, or production timing hook
is needed.

1. Prepare `Session` with `{48000.0, 64, 819, 0}`, start, read successfully and
   `ui.observe(snapshot)`. Resize to 1672×941. Submit the actual action from
   `ui.key({UiKey::A, true})`, immediately feed each `SubmitResult` to
   `ui.submitted`, then `session.render(32, stereo)` and observe. Require one
   held Upper target and zero faults.
2. In Play, call `ui.activate({UiControlKind::PresetKey, Manual::Upper,
   DrawbarBank::A, static_cast<std::uint8_t>(PresetSelection::F)})` and dispatch
   its sole command identically. Require successful nonzero sequence `q`.
   Before any further render, successfully read/observe the actual publication.
   Assert `resolved_sequence < q`, desired F, applied Bank B, differing whole
   controls, `controls_pending`, and the unchanged held target/frame/revision.
3. Build `make_inspection_document(profile, ui.view(), {true, true})`. Require
   Current, pending, `Sound Bank B / Edit B`, and `1 target`. Paint Play and
   Service using this actual model/document. Workspace changes emit no commands.
4. Call `session.render(0, {})`, read and observe. Require resolved and applied
   sequences equal `q`, desired/applied equality, pending cleared, unchanged
   frame/holds, and a newer publication. Paint acknowledged Play and Service.
   Release the real key, flush and stop; require cleared holds and no faults.

Use `SDL_Init(0)`, `SDL_CreateRGBSurfaceWithFormat`,
`SDL_CreateSoftwareRenderer`, `Drawing::initialize`, `paint_instrument`,
`SDL_RenderFlush` and `Drawing::save_bmp` **before** `SDL_RenderPresent`.
Do not invent AudioDevice facts in `InstrumentViewInfo`: no device is opened.
Run pending/acknowledged Service at 960×700 too; review label clipping and
singular/plural text visually. The native painter supplies every pixel.

An optional proposed `--capture-dir` writes into a new directory only; ordinary
CTest writes no gallery. Retain lossless frames and JSON containing loaded
profile, source/executable hashes, renderer, dimensions, actual command/sequence,
desired/applied copies, frame/publication values, row text, and before/after
assertions. Label these **native rendering harness captures, no application
window or audio device**. Keep whole-app desktop/gallery evidence separate.

## Commands and acceptance

From the repository root, after implementation and coherent rebuilding:

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --target test_standalone_inspection_author test_standalone_inspection_acceptance test_standalone_inspection_raster
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -R '^test_standalone_inspection_(author|acceptance|raster)$' --output-on-failure --no-tests=error
../build-native/apps/standalone/test_standalone_inspection_raster --capture-dir ../inspection-pending-capture
```

The raster target/option above are proposed, not currently available. Acceptance
requires real pre-flush and acknowledged records plus reviewed native pixels;
a passing string test alone does not close visual capture or desktop gates.

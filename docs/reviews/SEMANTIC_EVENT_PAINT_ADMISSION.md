# Semantic event paint admission — A58, wave 10

## Decision and scope

**Admit the narrow event-dispatch correction below for independent implementation
and genuine before/after qualification.** During an input-script replay, an SDL
event that actually changes workspace, presentation, or overlay should end that
turn's remaining event drain. The existing ordinary render then gets its
opportunity before another queued event can replace that semantic view. Compare
three scalar values around the unchanged `handle_event` call; do not infer a
transition from an absent previous frame, changed dimensions, or event type.

This is an implementation admission, not an executed candidate pass. A58 changed
only this review, its [evidence receipt](../development/2026-11-16-heading-title-continuation/reports/a58-semantic-paint-admission.json),
and its worker note. Root owns native execution, source integration, CMake,
acceptance, publication, and preservation of the completed original run. The
first timestamp-zero regression must run against the genuine current application
before production code changes. A59 owns that independent fixture.

## Retained failure and source identities

The completed workspace block in the
[serialized candidate log](../development/2026-11-16-heading-title-continuation/reports/serialized-final-ctest.log)
reports one failure in six methods, thirty actual application subprocesses, and
50.38 seconds at CTest. The failing subcase is
`test_pointer_header_matrix_preserves_keyboard_space_and_exact_save`, 1400×819.
The generated [test discovery](../development/2026-11-16-heading-title-continuation/reports/serialized-final-test-discovery.json)
sets `RUN_SERIAL` to boolean true and retains its 90-second timeout. The log
places this test after the completed MIDI suite and before the next test starts.
Therefore the semantic omission remains observed with the admitted CTest
isolation; this does not establish an operating-system scheduling cause.

| Inspected input | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `361ae03aa9e1a369a8fd8d125c21b10e40841d08d768a4c5637b2a3ecf0232f3` |
| Genuine current application | `2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479` |
| `apps/standalone/InstrumentView.cpp` | `0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d` |
| Completed 32,449-byte workspace failure block | `1f230e420547b6d974fc439e0261646b5e2520d94b53edf48c03413c9e654d54` |

The receipt preserves the exact completed block losslessly and pins the other
inspected inputs. The now-complete serialized run is **238/241**, exit 8,
686.4455 seconds at root and 686.18 seconds at CTest, with all 474 frozen code
inputs unchanged. Its 77,140-byte log has SHA-256
`ba6261b1c014a7fb28d01680f74a9de0c6c07e3cab8695931bcb28b3306751b1`;
its [coherent result](../development/2026-11-16-heading-title-continuation/reports/serialized-final-coherent-results.json)
and [observed scheduling](../development/2026-11-16-heading-title-continuation/reports/serialized-observed-scheduling.json)
retain the exact invocation and exclusion evidence. The other failures are
native calibration and MIDI CLI, outside this admission's diagnosis. The
original log and every earlier failure remain untouched.

All retained frames in the failing child have dimensions 1400×819. After
deduplicating consecutive semantic visits, the observed sequence is:

| First retained image | Elapsed ms | Workspace | Presentation | Overlay |
| --- | --- | --- | --- | --- |
| 1 | 0 | Play | Dimensional | none |
| 16 | 1356 | Rotary | Flat | none |
| 21 | 1516 | Service | Flat | none |
| 34 | 1871 | Play | Flat | none |
| 37 | 2066 | Play | Dimensional | none |

The missing second visit is **Rotary/Dimensional**. The script requests Rotary
with pointer Down/Up at 1100/1120 ms, then Flat at 1300/1320 ms, with no resize
anywhere in its 24 actions. The application delivers all 24 actions, finishes
with final acknowledgment, records no application or audio-render/format/
nonfinite/overrange failures, and paints 48 images. Its presentation history is
not truncated. Two original owners remain held across the retained navigation
visits and are eventually released; no extra note commands are reported.

The test's control-path, held-prefix, and command-count assertions precede
`assert_views` and returned. The later pointer-capture-refusal, canonical
saved-byte, and screenshot-held assertions were not reached. The copied
diagnostics cannot establish the missing saved-file assertion. A successful
eventual final state does not satisfy the missing actual painted visit.

## Ordering mechanism and relationship to A46

In [Application::run](../../apps/standalone/main.cpp), `pump_replay` runs at the
start of a turn, followed by `SDL_PumpEvents`, an initial
`SDL_WaitEventTimeout(..., 12)`, and a bounded drain using
**`SDL_PeepEvents(..., SDL_GETEVENT, ...)`**. The latter is the actual dispatch
path in this source; it is not `SDL_PollEvent`. Both dispatch sites currently
call `handle_event` without checking whether that event changed the semantic
view. Observation, audio monitoring, MIDI discovery/delivery, save completion,
replay completion, and one ordinary `render_frame` follow the drain.

[ScriptedInput::pump](../../apps/standalone/ScriptedInput.cpp) posts due
non-resize actions in source order. A catch-up prefix can therefore contain both
Rotary and Flat actions. Their successive handling can replace the first view
before the one normal paint. The source supplies a direct omission path matching
the observed history. There is no per-event dispatch trace proving the precise
delay or the identity of a blocking scheduler operation; retain that distinction.

The [A44/A46 admission](WORKSPACE_PAINT_REPLAY_DIAGNOSIS.md) addresses a different
boundary. Before a synchronous resize, `ScriptedInput` posts a consumed-prefix
marker; a resize posts another marker afterward. A46 conditionally suppresses
the marker handler's eager pump when the final semantic view of that prefix has
not been painted. Its explicit guarantee excludes intermediate semantic events
inside one non-resize prefix. That correct, bounded guarantee remains intact.

Keep that marker branch byte-identical. When the new event-level boundary ends a
drain, an already pending marker prevents the next outer pump from running past
it. If a previously future resize becomes due, unequal acknowledged/pushed
counts cause a marker to be posted before the resize is applied. Thus queued
semantic input is still handled at the correct dimensions. Pure resize events
do not trigger the new boundary.

## Exact admitted code shape

One local dispatcher in `run`, created before the loop, can implement the change
without a new member, allocation, schema field, or changed handler signature:

```cpp
const auto dispatch_event = [this](const SDL_Event& event) {
    const auto workspace = ui_.view().workspace;
    const auto presentation = ui_.view().presentation;
    const auto overlay = overlay_;
    handle_event(event);
    return !options_.input_script.empty() &&
        (workspace != ui_.view().workspace ||
         presentation != ui_.view().presentation || overlay != overlay_);
};
```

At the existing first-event site, initialize
`bool semantic_transition = dispatch_event(event);`. Add
`&& !semantic_transition` to the existing `count < 256 && running_` drain
condition. At the existing `SDL_PeepEvents` dispatch site, assign
`semantic_transition = dispatch_event(event);`. Retain its exact error branch,
empty-queue break, and counter initialization at one. Describe this ordering in
the local comment. No other execution path needs to change.

Capture the three enums **by value** before dispatch; a reference to mutable
`ui_.view()` is not a before snapshot. Dispatch each received event exactly once.
Check actual state, not a hardcoded list of F keys or pointer locations, so
keyboard, pointer, modal-open, and modal-close transitions share the rule.
Normal interactive, smoke, and MIDI-only operation keep their existing batching
because no UI input script is active. The additional work there is only fixed
scalar reads/comparisons. Existing quit/failure handling and final rendering
order stay unchanged.

Reject a `last_painted_ == null` trigger: timestamp-zero F7 must not gain an
invented pre-action frame when an unrelated startup event arrives first.
Reject dimensions as a trigger: 256 tied resizes must not become 256 required
paints. Also exclude controls, modal focus, ownership, snapshot availability,
clock, publication revision, and pending state. They have separate observation
contracts. Do not add `render_frame` calls, manufacture presentation records,
alter callback or musical observations, relax final acknowledgment, or change
any timeout to make the new case pass.

The guarantee is one ordinary paint opportunity after a dispatched event's
actual semantic transition, before another queued event is handled. A single
event that internally changes and restores the same three values creates no
new obligation. Renderer failure and history truncation remain truthful. This
does not promise visibility of every modal-focus change or resize-only size.

## Work and compatibility bounds

The first event plus at most 255 subsequent events still caps a turn at 256.
The wrapper stores three scalar enums and a Boolean on the main-thread stack;
there is no copied `UiView`, heap container, persistent state, new thread, or
recursive rendering. Each scripted action can cause at most one new drain stop.
The parser still admits at most 256 actions, 64 KiB, and durations 250–10000 ms.
The UI and painted histories remain at 512 entries, and replay drain remains
2000 ms. Marker identity, source order, sticky failure, elapsed-time monotonicity,
and completion conditions do not change.

Additional real paints and ordinary observation turns cost real time. No
argument here guarantees that 256 expensive semantic transitions finish under
the fixed deadline; such overload must retain its existing failure behavior.
More turns also interleave existing MIDI/observation processing with UI input.
That is why mixed-input ownership and timing suites need affected qualification
even though no musical command handler changes. The earlier 256-resize gates
remain mandatory and must not be replaced by this narrower regression.

The [native calibration driver](../../apps/standalone/native_tests/calibration_lifecycle_driver.cpp)
includes the real `main.cpp` and invokes `guarded_application`; it requires
rebuilding with the changed event loop. No test-only branch or direct access to
application internals is admitted. The
[ScriptedInput native helper](../../apps/standalone/native_tests/test_standalone_input_replay.cpp)
does use its own `SDL_PollEvent` loop, but it tests the unchanged helper API and
needs no source edit. Keep `record_replay_observation`'s musical guard,
`replay_acknowledged`, `handle_event`, and `render_frame` unchanged. The nominal
dry Engine, 47 parameters, `B3CONTROLS4`, musical ownership, and painter remain
outside this correction.

## Independent deterministic regression

The initially proposed Ctrl+M sequence is syntactically and semantically valid;
its diagnostic overlay is `midi`. However, on a compiled native backend it opens
asynchronous MIDI discovery, which can legitimately report enumeration failure.
Existing modal tests explicitly distinguish that outcome. Copying A45's strict
no-MIDI common helper would be invalid. An empty synthetic MIDI companion could
avoid hardware discovery, but it adds an unnecessary replay mode to this case.

Following root's allowed alternative and A59's independent finding, **admit
Ctrl+Comma and the `audio` overlay** for this prospective fixture. It enumerates
only the already initialized dummy SDL output. Escape closes without Apply;
configuration, one device start, controls, and source clock retain their normal
semantics. Keep the strict zero-error and no-MIDI predicates.

A58 read all 339 lines of A59's independent fixture and admitted its final
one-line `applied == resolved` strengthening before native execution. The
[frozen fixture](../../apps/standalone/native_tests/test_standalone_semantic_paint_boundary.py)
is 16,743 bytes, SHA-256
`8a6ecd4ac9747c3596983d345afb789163ad2fff2e880db198bdcc6e31361048`.
Its required visits come only from `presentation.observations`; `last_painted`
is checked for final consistency and cannot fill a missing visit. Neither A58
nor A59 ran its native children. Root retains the genuine-before and candidate
execution gates below.

At initial 1280×900, use this exact no-resize input in each initial presentation:

```text
B3UIREPLAY1
duration_ms 250
0 key_down F5 none 0
0 key_up F5 none
0 key_down F7 none 0
0 key_up F7 none
0 key_down Comma ctrl 0
0 key_up Comma ctrl
0 key_down Escape none 0
0 key_up Escape none
0 key_down F6 none 0
0 key_up F6 none
0 key_down F4 none 0
0 key_up F4 none
```

Starting Dimensional, require exactly these consecutive actual painted visits:
Rotary/Dimensional/none, Rotary/Flat/none, Rotary/Flat/audio,
Rotary/Flat/none, Service/Flat/none, Play/Flat/none. Starting Flat, exchange the
two presentation labels. All sizes remain 1280×900 and required image indices
strictly increase. Do not require an initial Play frame before zero-time input.
UI-event history is supplementary; only records made after successful painting
and `SDL_RenderFlush` establish the required visits.

Require all twelve actions delivered, the unchanged literal complete controls
in every musical observation and final state, unchanged noncanonical input
state bytes, zero note-on/off commands, empty held targets, no pointer capture,
no pending controls/save, untruncated histories, one device start, finite clean
audio/session lifecycle, and final acknowledgment under the original 250 ms
plan plus 2000 ms drain. Keep the finite two-child/output/diagnostics bounds
from the independently prepared harness.

Opening the overlay calls `lose_input`, which submits the existing
`ReleaseUiNotes`; Escape also submits that command even with empty owners.
Therefore the fixture must not copy A45's assertion that every observation
already equals the final sequence. Require monotone applied/resolved/submitted
values, `applied == resolved <= submitted <= final` in observed running data,
and full final equality. These ordinary empty releases neither create note-on/
off commands nor authorize changing the production acknowledgment guard.

## Root qualification gates and retained limits

### A60 source conformance

After root's genuine-before release, A58 independently read the complete A60
diff against `../semantic-replay-before-native/main.cpp`. Candidate main is
147,938 bytes, SHA-256
`0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537`.
It implements exactly the admitted local dispatcher, two dispatch substitutions,
Boolean drain condition, and explanatory comment. All 27,566 bytes preceding
`run` are identical; all 118,527 bytes from the ordinary post-drain `observe()`
to EOF are identical, SHA-256
`f7e93e097ca042736316c07b670b912800b7ae2a568c40633e0b779c410dba51`.
This includes the A46 marker branch, handler, acknowledgment and musical
observation guards, rendering, and member state. The painter is unchanged.
**Source conformance is admitted; candidate native qualification remains
root-owned and pending in this review.** A58 performed no native execution.

### Execution sequence

Root has completed the genuine-before gate once. The
[full before receipt](../development/2026-11-16-heading-title-continuation/reports/semantic-paint-genuine-before.json),
SHA-256 `45e4d5bf293d3e02731c2fc7fabc3ca900494814b401ef4f69c93c2d50e4d66a`,
and [root wrapper](../development/2026-11-16-heading-title-continuation/reports/semantic-paint-genuine-before-root.json)
retain both children and unchanged inputs. Both genuine `2c64…` application
children exit zero, pass the preceding strict lifecycle/control/byte/sequence
checks, and fail the six-visit assertion. Starting Dimensional paints only
Play/Flat, image 1 at 1 ms; starting Flat paints only Play/Dimensional, image 1
at 0 ms. This establishes the deterministic omission independently of the
earlier wall-clock catch-up failure. Candidate after qualification is pending.

1. Preserve the genuine `361ae…` source and `2c64…` application, then run both
   independently frozen A59 cases once before implementation. Require genuine
   failure specifically at the missing ordered actual visits, with valid
   parser/process/lifecycle evidence. A prospective source argument alone is
   insufficient before evidence.
2. Apply only the admitted `run` change, rebuild the application and calibration
   probe, record source/binary identities, and run the unchanged new fixture.
   Require both cases to pass with their original controls, input bytes,
   deadlines, and actual-frame predicates.
3. Run the unchanged A45 zero-time F7/resize cases, both maximum-256-resize
   plans, tied resize/pointer ownership, and ScriptedInput helper. Preserve the
   A45 genuine earlier failure and current accepted after results separately.
4. Run affected workspace, workflows, MIDI CLI/expression, native MIDI replay,
   and calibration paths at the coherent new app/probe. In particular execute
   the original pointer-header case through its formerly unreached file tail.
   Retain the scheduling admission and original failures; do not use this
   semantic change to declare unrelated clock-window failures repaired.
5. Freeze coherent inputs, complete the integrated gate, then bind installed
   and exact-published-source hosted evidence to that changed source. Record
   failed, unrun, and passed outcomes separately. Root owns any additional
   independently admitted correction and final publication.

No physical-device, callback-deadline, native accessibility, connected rotary
audio, specimen-calibration, or literal whole-interface 1:1 gate is closed by
this review. The H1 painter and its scoped gallery evidence retain their own
identities; a different event loop needs its own runtime qualification.

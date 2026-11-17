# Workspace paint replay diagnosis

## Decision and scope

**Proposed, not implemented or executed by A44.** The missing old-size Flat
frame has a concrete event-ordering explanation: a consumed-prefix marker
immediately pumps the next resize inside the same SDL drain, before the outer
loop paints. A narrow correction should defer that eager pump only when the
current workspace, presentation, or overlay has not yet been actually painted.
Resize-only batches must retain eager draining. Unconditionally deferring every
marker is rejected because an existing acceptance case requires 256 tied
resizes to succeed within the unchanged drain allowance.

This is a separate replay qualification issue. The failed journey uses
1280×900 and 960×700, where the H1 header field is inactive. It does not reverse
the independently recorded H1 visual, numerical, or timing results, and those
results do not qualify this replay correction. Root owns implementation,
genuine before/after runs, rebuilding, final acceptance, and publication.

## Frozen evidence

The [A44 receipt](../development/2026-11-16-heading-title-continuation/reports/a44-workspace-replay-diagnosis.json)
pins all inspected source hashes and embeds gzip/base64 copies of the exact
complete failure blocks, input script, and copied diagnostics. The original
[full-suite log](../development/2026-11-16-heading-title-continuation/reports/h1-final-ctest.log)
remains untouched. A44 captured completed failure blocks while that log was
still growing; it does not claim a final whole-log identity.

| Input | SHA-256 |
| --- | --- |
| `main.cpp` | `89b24fdeae438b77309904d12c32e3e2ae5e964e99968a8656c5b0a710e237c4` |
| Application | `bfe8e36d16f4c5fd15009f2fc4707c06c93388f40870dc9f84696d3367447e7b` |
| Painter | `0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d` |
| Original workspace failure block | `1fe187207314c02ab8d6ea6c11d39e95ed792abe41108146f67edaf7eeca1c85` |
| A44 receipt | `940d456cc214693c899c7f347d2c6378fea3c4e1151ca90a62f89c11623f80c1` |

`test_focus_memory_restores_drawbar_save_and_load_after_returns` delivered all
87 actions and completed with final acknowledgment, no pending controls/save,
no application errors, and zero audio render/format/nonfinite/overrange
failures. Its preceding control assertions passed. Its exact painted-visit
assertion failed because `("play", "flat", 1280, 900, "none")` was absent.

The retained image 13 at elapsed 1740ms is Play/Dimensional at 1280×900.
Image 14 at 2209ms is Play/Flat at 960×700. The relevant script contains Flat
pointer Down/Up at 1830/1850ms, Right Down/Up at 2000/2010ms, and the resize at
2170ms. These are elapsed observation values; they do not establish which
scheduler or rendering activity consumed the interval. No per-marker timing
trace exists. The source establishes an omission path matching the evidence;
it does not justify blaming a particular CPU contention or cold-cache cause.

## Source mechanism and contract

[ScriptedInput::pump](../../apps/standalone/ScriptedInput.cpp) posts due input in
source order. Before a resize it posts a marker if the preceding input has not
been acknowledged. A resize then changes the SDL window synchronously, queries
its actual dimensions, posts a size event and another marker, and returns.
Marker identity includes the instance, window, registered type, and consumed
count. Only acknowledgment of the complete plan marks delivery finished.

In [Application::handle_event](../../apps/standalone/main.cpp), successful
marker acknowledgment currently calls `pump_replay` immediately. The new
resize and following prefix can therefore enter the same bounded event drain.
Only afterward does the outer loop observe, process MIDI/save completion,
check replay completion and call `render_frame`. A catch-up prefix containing
Flat followed by the due resize can change both presentation and size before
any old-size Flat frame is painted.

`record_painted_presentation` runs after `paint_instrument` and successful
`SDL_RenderFlush`; the history retains visible-state transitions. Its omission
is truthful. The [workspace contract](../INTERFACE_WORKSPACE_CONTRACT.md)
requires records of actually painted views and forbids substituting final
shutdown state. Do not create a presentation record in the input handler,
reinterpret a UI-event trace as a painted frame, or relax `assert_views`.

## Recommended source change

Keep `ScriptedInput` unchanged. In the existing acknowledgment branch, use the
last genuinely painted semantic view to decide whether eager delivery may
continue. The following is a review sketch, not an applied patch:

```cpp
if (!options_.input_script.empty() && replay_.acknowledge(event)) {
    const auto& view = ui_.view();
    const bool semantic_view_painted = last_painted_ &&
        last_painted_->workspace == view.workspace &&
        last_painted_->presentation == view.presentation &&
        last_painted_->overlay == overlay_;
    if (running_ && semantic_view_painted) {
        const bool pumped = pump_replay(SDL_GetTicks64() - replay_started_);
        (void)pumped;
    }
    return;
}
```

Update both the marker-handler and outer-loop comments to describe conditional
continuation. Compare only workspace, presentation, and overlay. Dimensions,
controls, pending state, frame clock, publication revision, held targets, and
modal focus have separate purposes and must not become additional paint gates.
In particular, dimensions would make every resize expensive again.

The guarantee is deliberately precise: if the final semantic view of a
resize-separated consumed prefix differs from the last actual painted view,
ordinary painting gets its opportunity at the current size before delivery of
the next prefix. This does not promise a separate frame for every resize-only
state or every intermediate semantic event inside one non-resize prefix.
The actual renderer and its failure path remain authoritative.

## Why unconditional deferral is rejected

The native helper's
[`test_resize_order`](../../apps/standalone/native_tests/test_standalone_input_replay.cpp)
already uses pump → poll/ack → next iteration; it does not require recursive
application pumping. However,
[`test_maximum_resize_plan_drains_without_extending_grace`](../../apps/standalone/native_tests/test_standalone_replay_boundaries.py)
requires two full 256-action scripts, repeated and alternating sizes, to pass
within the original 250ms plan plus 2000ms drain. Unconditional deferral could
require 256 full paints. It is therefore not an acceptable complete proposal.

The selective comparison retains eager resize-only draining after at most one
initial paint establishes `last_painted_`. Keep the 256-event per-turn drain,
256-action plan, 64KiB source cap, 10000ms duration maximum, 512-entry painted
history, and 2000ms drain. No storage, explicit extra render call, sleep, retry,
or new clock is needed. At most 256 distinct consumed-prefix markers exist:
each successful marker advances a strictly increasing consumed count.

Partial markers still cannot finish replay. Final delivery still requires
the existing musical/save acknowledgment. An eager final-marker pump remains
a harmless no-op. A deferred next-loop pump uses the same monotonic clock and
sticky queue/resize failure propagation. Normal operation and MIDI-only replay
do not enter this UI-marker branch. Mixed MIDI/UI and expensive semantic
scripts still require real acceptance under the unchanged fixed drain.

## Deterministic regression and acceptance

Use a new case with duration 250ms, initial size 1280×900, and six timestamp-zero
actions; preserve all original workspace cases, timestamps, and assertions:

```text
0 key_down F7 none 0
0 key_up F7 none
0 resize 960 700
0 key_down F7 none 0
0 key_up F7 none
0 resize 1280 900
```

Starting Dimensional, require actual ordered visits Flat/1280×900,
Dimensional/960×700, and Dimensional/1280×900, with no overlay. Starting Flat,
require the inverse presentation sequence. Each retained visit must identify
an increasing rendered image. The intervening resize-only Flat/960×700 in the
first variant is intentionally outside the guarantee. A45 owns the independent
fixture proposal; A44 owns no fixture edits.

The original eager handler collapses these prefixes before the ordinary paint,
so genuine original-binary failure does not rely on a lucky scheduler delay.
Require complete unchanged controls and saved bytes, zero note commands, empty
held targets, strict lifecycle/error/final acknowledgment checks, and actual
painted observations. Do not add a pre-action timing expectation to an all-zero
script. Root must preserve the original failure, demonstrate corrected success,
and retain both maximum-resize cases and tied pointer-geometry/owner checks.
Then run the unchanged workspace, input replay, workflows and MIDI gates and
the coherent final suite. Bind new runtime/publication evidence to the changed
application; retain the independent H1 galleries and original failures.

## Separate starter-load finding

The same log later failed
`test_materialized_scopes_keep_their_expression_when_generically_loaded`,
performance scope. Its complete failure block is embedded in the receipt,
SHA-256 `e2c471d4df21003754935f45b7e2aac4f60fc412943eafcccfdccd47d4c7e7e2`.
[Its script](../../apps/standalone/native_tests/test_standalone_starter_load.py)
contains no resize. At 2097ms the retained snapshot had applied/resolved
sequence 5 while edit 6 was submitted. Sequence 6 first appears in retained
history at 2255ms, after the 2200ms Load timestamp, with Load sequence 7 already
submitted. This establishes a missing timely copied acknowledgment, not the
callback's exact acknowledgment time. Final controls and replay acknowledgment
passed, with zero application errors.

The semantic paint proposal cannot repair this separate musical-observation
gap. Preserve its original script, guards, assertions, and timeouts. Root should
perform one isolated same-source diagnostic after the full suite, retaining
both outcomes. An isolated pass indicates sensitivity; it does not erase or
repair the original failure. Root also owns the independent archival Markdown
relative-link failure and source-context repair. Neither issue permits
weakening acceptance. No physical, hardware deadline, accessibility, display,
or literal whole-interface 1:1 gate is closed by this review.

# Standalone replay boundary acceptance

[`test_standalone_replay_boundaries.py`](../apps/standalone/native_tests/test_standalone_replay_boundaries.py)
runs the actual application with explicit SDL dummy audio/video and private
temporary files. It supplements the [musical workflows](STANDALONE_WORKFLOWS.md)
and [replay-helper acceptance](STANDALONE_REPLAY_ACCEPTANCE.md). The suite imports
no production parser, UI geometry calculation, Engine or control serializer.

## Bounded event-drain repair

A valid 256-resize plan at time zero and duration 250 ms exposed a main-loop
gap: the previous executable stopped after its two-second drain grace with
only 110 actions pushed in this worker's reproduction. A marker handler could
append the next due prefix after `SDL_PollEvent` reached a polling-cycle boundary,
causing an unnecessary wait/render turn per prefix. The helper's queue ordering
and final-acknowledgment contract were already correct.

The application now gathers native input with `SDL_PumpEvents` once per turn,
waits for the first event, then uses the public `SDL_PeepEvents(SDL_GETEVENT)`
queue operation for the remainder of that turn. The first event plus drain
still process at most **256 events**. Newly queued prefixes can proceed within
that budget; a negative queue result reports failure and shuts down safely.
The drain stops immediately when a handler requests shutdown, so later queued
Save or note actions are not handled after Quit. This uses public SDL APIs and
does not inspect, disable or depend on private sentinel values.

The allowed script size, 256-action limit, 250–10000 ms declared duration,
two-second grace, ordinary handlers, Session acknowledgments and audio callback
remain unchanged. The repaired exact formerly failing plan delivered all 256
actions and exited successfully in 0.319 seconds in the recorded local run.
That elapsed time describes this execution, not a device deadline guarantee.

## Maintained checks

| Boundary | Independent expectation |
| --- | --- |
| Maximum resize plan | 256 repeated or alternating real window resizes finish with every action delivered and acknowledged, correct final dimensions and no injected note. |
| Event capacity | Zero and 256 unmatched key-ups succeed without notes; a 257-action file rejects before state/output changes. |
| Stable time ties | Down/Up and Up/Down at the same time produce different literal final holds and accepted command counts. |
| Tied geometry | The literal point `(35,500)` is Lower C at 960×700 and Upper C at 1280×900. A Space-held Lower C remains addressed to Lower across the second tied resize/click. |
| Held final state | Replay can finish with Upper MIDI 60 held; copied pre-shutdown state and note counts retain it while joined shutdown clears all holds. A real BMP has valid dimensions/size and is captured during that held state. |
| Interrupted Quit | Returns nonzero, does not claim delivery/completion, joins the device and releases all notes; later queued Save and note actions do not execute. |
| Input aliases | Exact paths, real hardlinks and symbolic parent aliases to state, screenshot or diagnostics reject with the entire existing tree unchanged. |
| Input admission | Missing, malformed, non-ASCII, oversized, directory, FIFO and symbolic/dangling leaves reject; mixed smoke/replay rejects as usage error. |
| Byte limit and paths | An exact 65536-byte valid file succeeds through space/Unicode paths; 65537 bytes reject without replacing sentinels. |

Successful runs require positive real dummy callback progress, no render/format/
nonfinite/overrange error, no recovery/overflow/rejection/fault, exact proposed
controls, complete pre-shutdown command acknowledgment and no automatic state
save. A redundant scoped close release can contribute at most one lifecycle
discard in these single-device fixtures. Accepted posts, observed holds and
audibility are different facts; the suite does not equate them.

Rejection snapshots retain regular-file bytes, types, modes, inode/link identity
and symbolic destinations without following symbolic directories. All Linux
branches executed. Unsupported Windows FIFO creation or unavailable symbolic-link
privileges are explicitly skipped in those particular branches, not silently
reported as equivalent coverage.

## Run and observed scope

From a configured native build, first build `hammond_standalone`, then:

```sh
ctest --test-dir ../build-native-app -C Release \
  -R '^test_standalone_(app|workflows|replay_boundaries)$' \
  --no-tests=error --output-on-failure --parallel 2 -V
```

Root registers the new test with `HAMMOND_STANDALONE_EXECUTABLE` and a 60-second
CTest timeout. Missing executable configuration fails as a prerequisite; every
subprocess has an eight-second guard. No exact callback count or speed threshold
is used as a correctness criterion.

The completed local group passed **3/3 suites**, **38 methods and 208 actual
executable runs** in 22.80 seconds. Its new boundary suite passed **9 methods,
29 runs and 19 preserved setup rejections**, with zero Linux skips. Exact hashes,
the original failure, a corrected test coordinate and commands are retained in
[assignment 37](development/2026-11-13-next-phases/37-replay-boundaries.md).

This qualifies the named Linux software event loop and finite workloads. Physical
capture, hardware latency, native accessibility, high-DPI operation, hostile file
races, every scheduler history and final hosted platforms remain separate gates.
The queue-error branch was reviewed, not dynamically injected here; existing
helper acceptance separately exercises actual filtered/full SDL push failures.

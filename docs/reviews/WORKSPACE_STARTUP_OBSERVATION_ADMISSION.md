# Workspace startup observation admission

## Frozen decision and scope

**Admit a prospective fixture correction using seven independently executed,
matching startup prefixes and stronger copied-state chronology. Do not admit
a relaxed numerical deadline or a missing copied startup state.** Root accepted
this direction before implementation. A53 performed source and retained-data
review only; this frozen proposal is not a passing execution result. A59 owns
the separately reviewed implementation after root's release. Root owns native
execution, acceptance and publication.

The exact failing guard is in `assert_commands`, not `assert_control_path`.
The latter compares the complete ordered control path and has no time cutoff.
The old guard demonstrably fails its own 180 ms requirement. However, the
reviewed replay and Session contracts do not promise a loaded-state copy before
180 ms: they distinguish scripted eligibility, queued commands, audio-boundary
application and a later main-thread snapshot copy. Treating those as the same
instant is an incorrect oracle for whether the loaded state preceded musical
application. The proposed change replaces that inference with independent
origin evidence and stricter chronology. It does not certify startup latency.

The [frozen A53 receipt](../development/2026-11-16-heading-title-continuation/reports/a53-workspace-startup-observation.json)
retains the complete original failure block losslessly, exact source hashes,
all call sites/configurations, immutable earlier-evidence identities and the
admission requirements. Future conformance and runtime evidence must be separate
artifacts; do not rewrite this proposal to match an implementation or result.

## Observed failure and unreached checks

The [semantic candidate result](../development/2026-11-16-heading-title-continuation/reports/semantic-final-coherent-results.json)
records 240/242 tests passing in 614.403 seconds, no changed code/build inputs,
and verified serial nonoverlap. Workspace CTest was actually `RUN_SERIAL`,
with its existing 90-second limit. It still failed, so scheduling isolation
does not establish the disputed sampling guarantee. The separate starter-Load
failure is outside this admission.

The unchanged workspace fixture is SHA
`9a226a6b17b1d7eb84a079a113f5ef97a6f37935ba16d1d3f55876bed907d6f3`.
The candidate main is
`0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537`;
the actual application is
`1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a`.
The workspace suite ran 30 native children across six methods. Its failing
subcase is hidden Play regions, Rotary, Dimensional. The child completed in
2.724 seconds; CTest failed at 49.51 seconds.

| Recorded stage | Elapsed ms | Submitted | Applied/resolved | Musical holds |
| --- | ---: | ---: | ---: | --- |
| Complete loaded controls | 197 | 4 | 3 | Empty |
| First Upper C4 acknowledgment | 283 | 4 | 4 | Upper 60 |
| Final original release acknowledgment | 2486 | 9 | 9 | Empty |

The initial sample fails `197 < 180`. The immediately following old assertion,
`initial.submitted == initial.applied`, would also fail: `4 != 3`. Merely
raising the clock cutoff would therefore leave the underlying mistaken
equivalence intact. The original A press remains scheduled at 180 ms.

Before the failure, the native test verified the full unchanged control path,
the exact seven-stage musical held path and its painted held-count path, and
three accepted note-on/three note-off commands. All 50 UI actions were pushed;
delivery, completion and final acknowledgment are true, controls/Save are not
pending, histories are not truncated, and application/audio failure counts are
zero. Retained counters account for six commands after startup sequence three.

The subsequent view assertion was not reached. Read-only inspection finds
its three actual visits: Play image 1 at 0 ms, Rotary image 4 at 352 ms, and
Play image 28 at 1728 ms, all Dimensional/1280×900 with no overlay. Inspection
clock and snapshot predicates also hold in the retained data. These findings
are not executed native assertions. The final `saved_bytes == STATE` check
was likewise unreached, and the copied diagnostics do not embed those bytes.
No final-control or acknowledgment observation certifies that file tail.

## Source acknowledgment semantics

The [input replay contract](../STANDALONE_INPUT_REPLAY.md) defines wall-clock
UI scheduling and separately requires Session acknowledgment. An empty plan
is valid and delivered at initialization; completion still requires its
duration and successful acknowledgment. `ScriptedInput::pump` admits actions
when their scheduled time is less than or equal to the observed elapsed time;
it supplies no upper bound on audio application or snapshot copying.

The [Session contract](../STANDALONE_SESSION.md) and
[`Session.h`](../../apps/standalone/Session.h) explicitly distinguish queued
acceptance from application. Each audio callback captures one finite FIFO
prefix, applies it and publishes coherent controls/holds/counters. Later posts
wait for a later callback. `resolved_sequence` may include unsuccessful
outcomes; `last_applied_sequence` records actual application, so their equality
and the full musical state remain essential to this successful journey.

In [`main.cpp`](../../apps/standalone/main.cpp), `handle_key` dispatches first.
`record_accepted` immediately advances the submitted counter. The subsequent
`record_replay_observation` copies the already retained snapshot and the
current submitted counter; it does not force a new callback or snapshot read.
`observe()` refreshes that snapshot separately, and a failed read preserves
the prior coherent value. Musical history is guarded until a running restored
snapshot is available. Thus submitted 4 with copied applied/resolved 3 is a
valid representation of a queued first note and a retained loaded state.

The 197/283 ms observations do not locate the callback's exact acknowledgment
instant or prove an OS/CPU cause. A real hardware or startup-latency deadline
would require its own specified start/end events and measurement. The existing
9-second child limit, 90-second CTest limit, original replay durations and
2-second completion drain remain real bounds and must not change.

## Existing callers and affected configurations

All eight `assert_commands` call sites were reviewed. The three header call
sites run at seven sizes: a completed nonmusical prefix, a completed Upper-only
prefix, and the full header journey. They already pass an independently
established startup sequence. Their precise held-prefix oracle explicitly
permits only the documented missing Upper-only sample in the full journey,
proven separately by its prefix. Preserve that exception and its required
remaining stages; do not broaden it.

The mixed MIDI/full-UI caller also already obtains its origin from a completed
250 ms prefix containing the original pre-180 ms UI navigation and synthetic
MIDI connect. Its connected state, zero accepted/dropped prefix packets, exact
state bytes, six full-run packets, ten note commands, independent owner holds,
and acknowledged `[2100,2350)` ms owner-survival window remain unchanged.
Do not substitute an empty, MIDI-free prefix for that existing mixed prefix.

Only these four currently implicit-origin methods gain new prefixes:

| Full method | Matching initial configuration | New children |
| --- | --- | ---: |
| Hidden Play regions | Rotary target, initial Play/Dimensional, 1280×900 | 1 |
| Hidden Play regions | Rotary target, initial Play/Flat, 1280×900 | 1 |
| Hidden Play regions | Service target, initial Play/Dimensional, 1280×900 | 1 |
| Hidden Play regions | Service target, initial Play/Flat, 1280×900 | 1 |
| Focus memory | Initial Play/Dimensional, 1280×900 | 1 |
| Capture failure closes parameter gesture | Initial Play/Dimensional, 1280×900 | 1 |
| Pointer capture preserves keyboard owner | Initial Play/Dimensional, 1280×900 | 1 |

All seven use the original complete canonical `STATE`. The hidden target is
reached only in the unchanged full script; its matching prefix starts in Play.
Each prefix is a fresh actual child, not cached state or a warm-up inside the
full process. This raises the full six-method suite from 30 to **37 actual
children**. Record the count and actual duration; do not enlarge its timeout.

## Admitted predicate

For each affected configuration, first execute the genuine empty
`B3UIREPLAY1` plan with `duration_ms 250`, identical state, size, presentation,
dummy backend and current executable. Retain the ordinary schema, transport,
lifecycle, no-error, no-truncation and private-file checks. Require the exact
complete loaded controls, empty musical and painted holds, zero accepted
note commands, no pending controls/Save, and unchanged exact state bytes.
Its final submitted/applied/resolved counter must be one positive value `S`.
Every retained prefix musical sample must agree with this completed origin.

Then run the original full script unchanged. For each of these seven full
children, independently require its **first copied** musical observation to
have applied/resolved `S`, exact loaded controls and empty holds. Submitted
may exceed `S`: application must not be inferred from queue acceptance. A
missing copied startup remains a failure even if the separate prefix passed.

For every `assert_commands` chronology, including the existing explicit-origin
callers, require nondecreasing copied elapsed times, applied counters and
submitted counters; `resolved == applied`; and
`S ≤ applied ≤ submitted ≤ final`. Two samples with the same applied counter
must have identical complete controls, manual-note sets and pedal IDs.
Retain the exact accepted note counts, `final - S == on + off + controls`,
and before-shutdown applied/resolved equality with final. The independently
executed prefix supplies `S`; never compute it only as `final - expected`
or take it only from the same failing full run.

Keep every existing caller's exact control path, held path, permitted pointer
coalescing alternatives, actual painted visits, capture checks and saved bytes.
In particular, the pointer test's actual final-empty observation must remain
at or after 2050 ms; the mixed MIDI owner window and header per-command earliest
times remain. Do not invent a new requirement that every audio command have
its own copied sample: existing documented coalescing remains legal.

A pure chronology helper that derives `S` from the same full run could be
self-consistent with a shifted or omitted origin. Monotonicity alone also
cannot prove the first copied state is the complete loaded baseline. The
admitted prefix plus full-run baseline plus unchanged state paths addresses
both gaps. It is stronger semantic evidence; it is explicitly not logically
stronger than the old numerical cutoff in every dimension, because the
unsupported sampling deadline is being replaced, not silently retained.

## Required before/after acceptance

Preserve the exact original fixture and complete failed invocation before any
edit. A53's frozen review/receipt precedes implementation. A59 must expose a
narrow diff implementing this admission, with all original full scripts,
times, bounds and downstream predicates preserved. A53 will inspect that diff
and record conformance separately, including all seven prefix/full bindings
and the existing header/mixed cases.

Root must then execute the amended fixture on the same actual candidate,
retain 37 actual child records and unchanged executable/input hashes, and
exercise the previously unreached view and exact saved-byte tails. The
original failure remains failed. A full coherent suite and exact-source
hosted qualification remain necessary; this proposal performs neither.
Physical devices, native accessibility, real display, literal whole-interface
1:1 and audio deadline qualification remain open.

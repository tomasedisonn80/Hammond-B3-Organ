# Final native callback, automation and state protocol review

Assignment 50 independently reviewed the production processor, controller,
stream boundary, host timeline and state exchange. **No actionable production
defect was found in the reviewed contract.** Seven selected executable gates
were actually run and passed, including four tests that load the real VST3
module. This review makes no new DAW, device-deadline, sanitizer, signed-release
or physical-fidelity claim.

The source is the initial coherent wave-7 tree
`7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73`. All 495 archived files were checked
against their actual Git blob identities before execution. Fifty-three relevant
compiled-input files also matched published commit
`7fb9b6121b729f46a9e18d80e8620eb21dc0847b` and the live checkout. After the run,
those files plus the two selected core test sources still matched exactly.
The published tree is `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`; its later
Python/Markdown repairs do not change these compiled inputs. The associated
[assignment note](../development/2026-11-13-pedals/50-native-protocol-audit.md)
retains commands, source/module/log hashes and the one setup-only discovery error.

## Source basis and scope

The review read the production implementations and public headers of
[Processor](../../plugins/vst3/Processor.cpp),
[Controller](../../plugins/vst3/Controller.cpp),
[StateStream](../../plugins/vst3/StateStream.cpp),
[HostTimeline](../../src/HostTimeline.cpp) and
[StateExchange](../../src/StateExchange.cpp), together with the fixed
[parameter conversion](../../src/ParameterBridge.cpp),
[decimal conversion guard](../../include/hammond/detail/Decimal.h), native build
policy and relevant independent-oracle/rejection test code.

Freshly reread complete extracted atlas pages 389–394 and 400–401. Their relevant
requirements are stable parameter identity, the previous-sample automation
anchor, explicit boundary ordering, zero-frame flushes without advancing DSP
history, controls-only persistence, safe concurrent state transfer, and separate
qualification of actual host/device behavior. The atlas's one-input proposal,
continuous physical drawbars and broader proposed saved-state inventory are not
silently substituted for the implemented three-event-bus, 45-control nominal
contract. The current [spike contract](../VST3_SPIKE_CONTRACT.md),
[processor contract](../VST3_PROCESSOR.md),
[controller contract](../VST3_CONTROLLER.md),
[timeline contract](../HOST_TIMELINE.md) and
[state-exchange contract](../STATE_EXCHANGE.md) define that explicitly narrower
engineering surface. No new review of every atlas page or external source is
claimed by this assignment.

## Reviewed failure boundaries

| Risk | Production behavior checked | Meaningful executed coverage |
| --- | --- | --- |
| Host buffer mutation before admission | `process()` admits format, mode, frame count and complete output layout before translating any host input or peeking state. Samples, flags and last successful diagnostics publish only after success. | Actual-module ABI and behavior reject bad layouts, partial stereo overlap, bad counts and late input while preserving sentinel buffers and later audio. Exact left/right alias is a declared supported case. |
| A filtered event bypasses validation or work bounds | Raw native events, every parameter point and retained carry share the 1,024-record budget. Recognized notes are checked for bus/channel/pitch/velocity/ID/tuning before pitch filtering. Valid unsupported input is counted and filtered without dereferencing its external data/text payload. | Native behavior covers malformed scalar/pointer/count shapes, filtered pitches, supported notes on inactive buses, full raw budgets and one-over rejection. A supported release on an inactive event bus rejects rather than silently disappearing. |
| A queue is reduced to its final point | Every queue point is copied into fixed storage and checked. The timeline independently evaluates all active curves from the sample-minus-one anchor, in permanent parameter-ID order. | Core long-double barycentric oracle, exact adjacent-threshold cases, and actual-module all-45-curve oracle compare audio and complete controls. The latter uses literal IDs and independent integer half-up conversion, not production `HostTimeline` or `ParameterBridge` as its oracle. |
| A boundary point applies early, disappears or repeats | Positive-frame offset-N points influence interpolation but remain carry for the next accepted boundary. The anchor is the actual last rendered normalized value. Zero-frame callbacks apply the boundary once and retain no new carry. | Core and native gates exercise endpoint carry, rejected callbacks with carry, zero-frame flushes, absent/empty queues, duplicate point ties and irregular partitions. |
| State restores erase physical or ownership history | Restores run on the candidate Engine before ordinary controls, reset curve anchors, and retain owners and DSP histories. Route-enable bits remain distinct from selected-bank values. | Core state/history checks and actual-module queued-restore/carry/Cancel tests compare subsequent audio with a separately prepared or copied plain Engine. Same-value selector gestures reconnect Cancel only when an explicit point exists. |
| Dense automation exceeds physical event storage | The timeline preflights all musical ownership transitions, copies live state into fixed workspace, and renders bounded slices when the 1,024-physical-event buffer fills. A current-sample tail flush advances zero frames. | The native automation gate supplies 239 raw records whose expression ramps alone require 12,288 physical control events across three long callbacks; all samples and later audio match a one-frame Engine oracle. |
| A successful render is followed by a fallible state acknowledgement | The processor peeks and preflights one token before timeline rendering. The sole audio consumer does not perform an intervening commit. UI appends cannot invalidate that token, and a successful Engine supplies a valid snapshot. | Core stale/foreign token and append-after-preflight checks, plus actual concurrent native failed-callback/four-pending-state/acknowledgement rounds, execute this protocol. |
| Concurrent state publication tears ordinary snapshot memory | UI and audio exclusively own opposite queue-slot phases through release/acquire cursors. Published controls and acknowledgement use 48 atomic 64-bit cells with sequentially consistent odd/even revisions. Readers have at most eight attempts and preserve the destination on failure. | Core producer/audio/observer stress and actual native UI/audio stress independently check whole control patterns. Publication-only saves prevent pending UI values from hiding a broken published payload. |
| Partial state text or a conversion error escapes to audio | Streams are parsed and serialized off audio, retain no stream pointer, and are bounded at 16 KiB plus one overflow-detection byte. Full values validate before queue publication or controller assignment. | Controller gate covers versions 1/2/3, exact byte bound, malformed/future state, partial I/O, error/count/progress/exception cases and unchanged destinations. |
| Floating-point policy changes discrete meaning or state bits | Discrete thresholds are explicit comparisons against exact binary fractions. Plain-to-normalized discrete division is exact. Decimal formatting/parsing uses the scoped nearest-rounding guard; native MSVC targets request strict floating-point behavior after removing inherited SDK shortcuts. | Controller's 3,720 threshold cases cover all four standard rounding modes, with 387 string round trips and signed-zero/subnormal cases. This assignment reran those checks on the identified Linux build; it does not claim a new Windows execution. |

Accessible, correctly typed SDK interface objects and caller-owned spans remain
preconditions. Count, null, alignment and range validation cannot prove an
arbitrary forged address is safe to dereference. Inactive stereo output and the
special zero-frame/zero-channel flush retain their separate documented behavior;
the latter has no described output channels and writes zero silence flags.

## Why the render-to-publication boundary is sound

The ignored return value of the processor's final `audio_commit()` deserves
explicit review: it is justified by the preflight contract, not by a general
assumption that errors are harmless. The token captures this exchange, consumer
sequence and publication revision. Only the same audio owner can advance the
latter two. The UI can append only to free slots and increase the queued cursor;
it cannot consume or recycle an unretired slot. Publication exhaustion was
checked before processing. The controls snapshot after a successful Engine call
has already satisfied the same domain validation. There is consequently no
remaining allocation, queue-capacity reservation or external resource decision
between successful timeline commit and host output copy.

Changing this protocol to allow a second consumer, an intervening commit,
concurrent lifecycle mutation, a mutable external token or an invalid Engine
snapshot would invalidate that argument. Such a change needs a new transaction
contract and tests; merely checking a late failure after Engine mutation would
not restore atomicity.

The queue and publication are distinct mechanisms. Queue slots contain ordinary
copied values protected by exclusive ownership transfers. Publication payload
cells are atomic even during a rejected read. Sequentially consistent revision
and payload operations place the writer's odd revision before its new cells and
its even revision after them. A reader accepting matching even revisions cannot
straddle a payload generation. Both sequence families reject before addition
would wrap; smaller immutable limits exercise exhaustion without billions of
callbacks. A token must not outlive its object. No reset or cross-object token
reuse is permitted by the API.

A save while a UI load remains pending returns the newest accepted UI snapshot.
After acknowledgement it returns coherent audio controls, including later
automation. The UI never calls `Engine::controls_snapshot()` directly. Bounded
busy-read failure is explicit; it is not reported as a successful fresh save
using cached data. The 123,056 bounded core read failures and 13,332 busy native
saves observed in this stress run are expected admission outcomes, not failed
test assertions or unbounded spinning on audio.

## Executed result

The two core executables came from the SDK-free build, and five native
executables came from the native build of the same frozen source. The native
build-only aggregate does not build unrelated core test executables. Actual
commands and configured test environment/working directory were discovered from
CTest's JSON definitions, then invoked directly. **All seven executables exited
zero in a combined 4.353 seconds, with no omitted or skipped execution.** This
was a selected direct execution pass, not another complete CTest or TSAN run.

| Executable | Seconds | Observed result |
| --- | ---: | --- |
| `test_host_timeline` | 0.385 | 4,759 accepted calls, 43 rejections, 39 later-audio probes, 933 threshold cases, 21 partitions; zero maximum curve/audio error |
| `test_state_exchange` | 0.026 | Queue/publication/migration/history assertions passed; 6,211 concurrent callbacks, 4,468 successful producer reads and 12,210 observer reads |
| `test_native_controller` | 0.007 | 41,795 checks; 3,720 threshold cases, 387 string round trips, 306 rejected stream/load cases |
| `test_native_abi` | 0.872 | 691,878 assertions; 229,725 compared frames, 217,972 audible frames, zero maximum audio error; checksum `af029009868faa04` |
| `test_native_behavior` | 2.157 | 1,030 accepted/72 rejected callbacks, 59 rollback cases, 233,792 direct-reference frames, 81,302 later-audio samples; checksum `3c4b24caebfdd1b9` |
| `test_native_automation` | 0.530 | 231 callbacks, 18 zero-frame calls, 89,979 reference frames, 179,958 exact channel samples, 39,948 later channel samples; zero error, checksum `5ea365699a5717c9` |
| `test_native_concurrency` | 0.364 | Three rates; 24 controlled rounds, 3,072 accepted stress loads, 3,072 publication-only saves, 64,625 exact audible reference frames and 6,168 future frames; zero error |

The actual module was 434,168 bytes with SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.
Its compiled nominal profile remained 4,545 bytes, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Variable concurrency counts are observations of this run, not golden totals or
latency guarantees. The four loaded-module tests instantiate through the bundle's factory and SDK
interfaces; they do not substitute a directly constructed production processor
for the binary under review. The separate controller executable compiles the
actual controller/stream sources against the pinned SDK.

## Handoff and remaining gates

No production or test change was necessary. Preserve the fixed state/curve
ownership, exact control IDs and supported-rate contract during subsequent M3/M4
work. Add physical models behind those boundaries; do not make UI or host state
operations owners of source time.

The final section of [VST3_PROCESSOR.md](../VST3_PROCESSOR.md) still describes
building the complete bundle and running ABI/validator/allocation gates as the
next work. Keep its assignment-31 syntax result as history, then link the
implemented [ABI](../VST3_ABI_ACCEPTANCE.md),
[behavior](../VST3_BEHAVIOR_ACCEPTANCE.md),
[automation](../VST3_AUTOMATION_REVIEW.md),
[concurrency](../VST3_CONCURRENCY.md) and
[allocation](../VST3_REALTIME.md) gates. Root was notified for the separately
owned handoff audit. This documentation observation does not require changing
production code or rewriting the original worker's evidence.

Lifecycle changes still require actual processing/UI quiescence. Current tests
exercise valid serialized transitions and stable-lifecycle UI/audio concurrency;
they do not promise safety for concurrent destruction or uncoordinated setup.
The stopped/active flags are not synchronization primitives. Actual DAW project
save/reopen, audio-device scheduling, independent supported-host compatibility,
custom accessible UI, distribution rights/signing and specimen matching remain
separate gates. The integrator must qualify and publish its final combined
source and observe the corresponding hosted workflows; this selected review
cannot close unexecuted platform jobs.

# Final continuation review: input, parameters and musical state

Date: 2026-11-13 UTC. Reviewer: `/root/w10_a56_final_input_review`.

**Result:** no actionable runtime defect was found in the reviewed ownership,
input transaction, parameter conversion or control-persistence scope. Six focused
Release test binaries passed. Two documentation inconsistencies were found and
corrected: the older native-host proposal still described superseded behavior,
and the ownership introduction called Engine's physical target Boolean after
explicit partial-key targets had been added. Native host/device qualification
remains open.

## Source and review boundary

The reviewed frozen tree is `805900d2339eb3975019581de5f8469e72e7509f`, archived as
`checkpoint-w09-src`. Its 13 relevant production headers/implementations and
seven relevant test files were compared byte-for-byte with that Git tree and
published commit `2046b9388f6aab1122e37646b2f20199b5c6079f`; all 20 matched.
The matching `checkpoint-w09-build` CMake cache identifies that source directory
and Release configuration. No old library was combined with later live headers.

Review used the standing instructions, current status/next steps, plan and handoff,
the contracts linked below, complete relevant implementation files and selected
independent test oracles. The six complete extracted atlas pages 130, 132, 151,
397, 398 and 401 were reread for ownership, retained destinations, permanent IDs,
normalized laws and separation of musical controls from dynamic histories. This
is a targeted review, not another full-PDF coverage claim. Atlas proposals and
absent native SDK exports are not treated as executed native acceptance evidence.

The two contract corrections belong to the live wave-10 documentation overlay,
outside the frozen wave-09 tree. Production and test code did not change in this
assignment. Root owns their combined publication and subsequent qualification.

## Runtime findings

| Boundary | Reviewed behavior and evidence |
| --- | --- |
| [Note ownership](../../include/hammond/NoteOwnership.h), [implementation](../../src/NoteOwnership.cpp) | Payload/order checks precede candidate state work. Identified identity is `(bus, channel, note_id)`; same-pitch duplicates are idempotent, conflicting pitch rejects, and missing releases are no-ops. Anonymous repeats create separate owners and release by FIFO. The original destination survives bus remapping. |
| Owner/output capacity | Fixed storage holds 256 owners and 1,024 emitted events. Output capacity can be smaller, but a larger span cannot remove the fixed limit. Sixteen-bit physical counts cannot exceed 256. Candidate translation and delayed prefix copy preserve the entire caller output and ownership on every reported failure. |
| Channel releases | AllNotesOff removes only the matching bus/channel's owners in surviving insertion order. It emits final-owner NoteOffs, never a manual Engine AllNotesOff. Remaining owners continue holding their physical keys. Nominal contacts then follow ordinary release travel. |
| [Input transaction](../../src/InputProcessor.cpp) | The facade copies ownership, translates into fixed storage, calls the preflighted Engine, and commits owners only after success. Translation errors precede Engine errors. Empty input still processes elapsed frames; zero-frame commands advance no DSP history. Failure returns both counts as zero and leaves output untouched. |
| [Parameter bridge](../../src/ParameterBridge.cpp) | All 43 descriptors use fixed identities and immutable metadata. Exact binary thresholds implement the retained law without intermediate rounding shifts. Binary controls use 0.5; drawbars use odd sixteenths. Expression preserves the scalar, including signed zero. Invalid IDs, nonfinite/out-of-domain values and nonintegral discrete values leave destinations unchanged. Offset admission remains Engine's responsibility. |
| [Control state](../../src/ControlState.cpp) and [I/O](../../src/ControlStateIO.cpp) | Complete candidates validate before assignment. Canonical writes use B3CONTROLS2; a fresh version-1 candidate supplies Off/Second/Normal/Slow independently of the previous destination. Missing version-2 fields and unsupported versions reject. The bounded parser reads at most 16,385 bytes to enforce the 16,384-byte limit. Serialization and parsing remain allocating operations outside processing. |
| [Engine restoration](../../src/Engine.cpp) | A successful restore replaces musical controls and marks mixing coefficients dirty. It does not replace contact trajectories, shared readiness, phases, held targets or frame count. Ownership is a separate object and is unaffected. Failed restore preserves the previous controls and dynamic continuation. |
| [Stopped lifecycle](../SAMPLE_RATE_LIFECYCLE.md) | Rate reconfiguration preserves existing targets and histories, so current external owners remain valid. A deliberate successful prepare resets Engine and therefore requires coordinated ownership replacement. Same-thread/stopped access and one playing-note authority are explicit in the public input headers and contracts. |

The meaningful failure checks compare semantic state and future behavior, not
object padding. Ownership rejection also checks a later channel-retirement and
fresh-note sequence. Facade rejection compares future samples and diagnostics
far enough for newly commanded nominal contacts to become audible. Parameter
tests independently enumerate targets and threshold neighbors under all four
standard rounding modes. Migration tests start from active contact/percussion
histories, verify their preservation, and probe future output after rejection.

These contracts require valid caller-owned spans and nonconcurrent access.
They do not validate arbitrary pointers or provide a concurrent UI publication
protocol. Two independent ownership objects must not control the same physical
key. The facade does not merge note/control streams, implement raw MIDI decoding,
silence failed output, or perform native fault recovery automatically. Those
limits are now consistent across the current handoff and native proposal.

## Executed verification

After checking the CMake source/configuration, each named binary below was run
directly from the coherent `checkpoint-w09-build`. This avoided competing with
root's CTest log writer. All six exited zero with empty stderr. Total observed
test-process time was approximately 1.12 seconds; it is test execution time, not
an audio processing benchmark or deadline result.

| Binary | Actual observed result |
| --- | --- |
| `test_note_ownership` | 2,127 accepted calls; 2,264 atomic rejections with future checks; 5,226 expected physical events; 541 retained owner rows; 16 partition/flush cases. |
| `test_input_processor` | 66,072 calls; 44 atomic rejections and 44 future probes; 814 complete state comparisons; 816 hand-authored reference events; 66 partition variants; 459,896 exact sample comparisons. |
| `test_parameter_bridge` | 5,635 independent conversions; 25,243 atomic conversion rejections; 43 live Engine targets; all four rounding modes passed. |
| `test_control_io` | Control persistence passed; 570 malformed inputs preserved destination semantics. |
| `test_percussion_controls` | Percussion control/history migration tests passed. |
| `test_owned_lifecycle` | 12 mixed-rate runs; 156 preserved rate boundaries; 14 rejected rates; 42 rejected input blocks; 50 future probes; 10,086 exact state comparisons; 2,408,812 exact sample comparisons. |

All 44 relative links across the four owned Markdown files resolve. UTF-8, LF
final-newline, trailing-whitespace and scoped `git diff --check` checks passed.
The identified stale current-tense claims are absent or explicitly relabeled.

This review did not rerun the entire CTest matrix, launch a native plugin/device,
measure callback deadlines, repeat allocation instrumentation or independently
audit hosted logs. Root's integration gate and other scoped reviews retain those
results separately. No new regression test was needed because the observed
defects were factual documentation mismatches and no runtime change was made.

## Documentation finding and correction

The frozen [host proposal](../HOST_INTEGRATION.md) had a later introductory link
to the new adapters but retained several current-tense instructions from the
original session. The correction preserves its unrun native acceptance plan and
the original dated assignment note while reconciling the following facts:

| Earlier wording | Corrected current contract |
| --- | --- |
| Next M3 implementation was contacts, then percussion | Those nominal paths exist; the [prepared pedal kernel](../M3_NEXT_GATE.md) is next, with full M3 still open. |
| Rate changes required reprepare and could not preserve phase | Explicit stopped/same-thread rate reconfiguration preserves histories and owners; deliberate reprepare remains a separate reset. |
| The proposed owner table held 1,024 entries | The implemented table holds 256 owners; proposed native queues remain separately bounded. Multi-device origin mapping into the two-bus typed domain still requires a declared policy. |
| Anonymous repeats were idempotent | Anonymous repeats use separate FIFO owners. Identified duplicates alone are idempotent under matching pitch. |
| Registry/model and saved format were version 1 with 39 controls | Current internal registry is version 2 with 43 records; original 39 remain unchanged; B3CONTROLS2 writes all controls and reads the explicit version-1 migration. |
| The native qualification table enumerated 39 exports | Future approved exports must be compared with the current 43 internal records; no native exports are claimed now. |

The [ownership introduction](../NOTE_OWNERSHIP.md) now describes this adapter's
binary NoteOn/NoteOff commands separately from Engine's explicit partial-key
targets and repeats the prohibition on uncoordinated input bypassing ownership.
No new host mapping, capacity, reset API, state format or control law was invented.

## Exact next action

Integrate the two documentation corrections with this review and
[assignment 56's note](../development/2026-11-13-continuation/56-final-input-review.md),
then apply the actual final source/publication checks. Continue the prepared
pedal-routing gate under its separate typed admission and all-cell acceptance
contract. If native work proceeds in parallel, first define origin mapping,
note/control ordering and coordinated lifecycle/recovery around the existing
typed APIs, then qualify the actual backend and host contracts. Native export,
device, concurrency, accessibility, deadline and physical-fidelity gates remain
pending until their own retained evidence exists.

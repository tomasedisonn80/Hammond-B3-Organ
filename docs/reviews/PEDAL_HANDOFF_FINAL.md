# Final review of future-agent resumability

## Scope and conclusion

Assignment 55 reviewed the current standing instructions and four contracts
whose next-step language still described implemented work as future work. The
review changed only [AGENTS.md](../../AGENTS.md),
[PEDAL_NOTE_OWNERSHIP.md](../PEDAL_NOTE_OWNERSHIP.md),
[PERFORMANCE_INPUT.md](../PERFORMANCE_INPUT.md),
[VST3_PROCESSOR.md](../VST3_PROCESSOR.md), [VST3_BUILD.md](../VST3_BUILD.md),
this review and its [assignment record](../development/2026-11-13-pedals/55-future-agent-handoff.md).
No implementation, test, CMake, profile, SDK, shared status or assignment manifest
was edited. The integrator retains ownership of publication and final counts.

The observed published checkout was commit
`d601eb166ea3206748f8e012b20a463ff365c0b1`, tree
`8af684dfe56f88222c52ff71d85a911ee1192fa1`. Root's
[wave-8 integration record](PEDAL_WAVE8_INTEGRATION.md) identifies qualified
source tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e`, its subsequent
Markdown-only result delta and its actual 71-suite ordinary/eight-suite native
local execution. This documentation review inspected that retained evidence;
it did not perform another full build, CTest run, native execution or TSAN run.
Later live tool and review changes belong to their own integration checkpoint.

## Findings and repairs

| Current document | Resumability problem | Implemented correction and basis |
| --- | --- | --- |
| `AGENTS.md` | The start-here list still called the preceding console handoff current; the new session checker and concrete scanner gate were not named. | Point to the current pedal handoff, newest status/next steps/log, current session checker and remaining M3/scanner contract. Preserve earlier handoffs and all actual ledgers. Make actual source, owned paths, command prerequisites, result scope and expected-head publication explicit. |
| `PEDAL_NOTE_OWNERSHIP.md` | Native conversion and the unified Engine transaction were described as future work. | Name the implemented native bus/pitch-to-pedal policy and link the actual combined transaction, timeline and acceptance records. Keep native bus indices distinct from pedal ownership origins. |
| `PERFORMANCE_INPUT.md` | End-boundary carry and callback slicing still referred to a later wrapper; independent acceptance and native/state work were described only as subsequent gates. | Link the implemented HostTimeline/StateExchange and executed independent/core/native gates. Preserve the facade's own half-open interval, one-Engine-call and ownership transaction contract. |
| `VST3_PROCESSOR.md` | The final paragraph asked the next agent to build and qualify a bundle that now exists. | Retain assignment 31's syntax-only result as history, then link the actual ABI, behavior, automation, concurrency, allocation, validator and relocation records. Point next development at current model and remaining product gates. |
| `VST3_BUILD.md` | Assignment 33's focused result appeared final, and already executed ABI/package work remained the next action. Reused build directories could retain disabled testing. | Label the three-suite result as assignment 33's dated gate; link subsequent executed evidence and actual platform records. Explicitly configure `BUILD_TESTING=ON` and require `--no-tests=error` for filtered acceptance. Link the implemented explicit native install. |

The earliest recorded results, source identities, failure records and validator
limitations remain. Updating a current instruction does not retroactively make
an earlier assignment's syntax or build check a later runtime test.

### Native input is a separate policy boundary

Source inspection of [Processor.cpp](../../plugins/vst3/Processor.cpp) confirms
that native event bus 2 admits pedal pitches 36–60, maps `pitch - 35` to the
one-based pedal identity, and constructs the typed record with pedal origin 0.
The native bus index is not reused as the typed pedal-origin index. Validation
and filtering precede that conversion. The updated contract states this actual
policy without implying that the core consumes raw MIDI or that a physical
pedalboard's wiring or calibration was measured.

The [combined input implementation](../../src/PerformanceInput.cpp) calls Engine
once after preparing both ownership candidates. The
[HostTimeline implementation](../../src/HostTimeline.cpp) separately maintains
candidate Engine/ownership/history and performs bounded internal slices and
zero-duration boundary flushes. It does not call `process_performance_input()`.
The [native processor](../VST3_PROCESSOR.md) invokes HostTimeline once for an
admitted callback. These distinctions matter when adding another adapter:
calling both processing paths for the same interval would double advancement.
No API or ordering rule was changed by this review.

## Standing workflow retained for every future agent

The repaired instructions retain the owner's authorization to continue the next
dependency-ready phase and publish completed development work to `main`. Agents
must inspect the actual source and remote state, preserve unrelated changes,
coordinate owned paths, qualify coherent code/headers/data, retain failures and
limits, and leave the next task's inputs and acceptance criteria concrete.
The integrator uses an expected-head update, never force-pushes, verifies the
fetched result and reports only observed CI execution. A later user instruction
or repository protection can change the branch/review path.

The current request remains exactly sixty new assignments in ten logical waves.
Earlier original/console sessions retain their own histories and provide no
credit to this one. A planned row is not a worker, a running note is not an
accepted result, and a text-consistency checker is not dispatch attestation.
The instructions name the current read-only progress command:

```sh
python3 tools/check_pedal_session.py --repo . --json
```

The explicit `--expected-complete 60` gate belongs after all sixty actual
assignments have completed and the integrator has accepted their work. Future
separate sessions must retain their own actual scope and records rather than
rewriting this session or assuming that every later small task requires sixty
workers.

Freshly reread atlas pages 130, 132, 151, 445, 446 and 450 from the complete
retained text extraction. They support the input-owner/clock separation,
engineering-versus-fidelity distinction, independent evidence classes and the
permission to start a minimal M9 adapter after M1/M2. This is a focused reread;
assignment 55 does not claim another complete 500-page or diagram review.

The [remaining M3/scanner gate](../M3_REMAINING_AND_SCANNER_GATE.md) is a concrete
next implementation plan. Its candidate graph, numerical oracle and acquisition
criteria do not establish an implemented scanner, measured AO-28/Leslie model,
actual DAW/device behavior, deadline performance, accessible UI or release rights.
The [current handoff](../PEDAL_HANDOFF.md), [status](../STATUS.md) and
[next steps](../NEXT_STEPS.md) remain the authorities for those evolving outcomes.

## Executed documentation verification

Observed the maintained `HammondB3`, `hammond_vst3_test_inputs` and `check_vst3`
targets through actual CMake target discovery in the coherent wave-8 native
build. Filtered CTest JSON discovery returned eight actual registered native
entries, and every command's executable exists. This establishes discoverability,
not another execution pass. Read actual CMake declarations: `HAMMOND_BUILD_VST3`
defaults off, `BUILD_TESTING` controls test registration, and `check_vst3` uses
`--no-tests=error`. No `HAMMOND_BUILD_TOOLS` configure option exists or is proposed
by the repaired commands.

The current-session checker exited zero at the first recorded observation with
53 complete, two running and five planned assignments, representing 55 distinct
dispatched identities. That observation is preserved rather than relabeled as a
sixty-complete result. Later accepted workers can change the live counts.

Final checks resolved **106 local links** in the seven owned
Markdown files, including the changed qualification anchor. The repository
integrity/navigation checker passed. UTF-8/LF, final newline, whitespace and
scoped `git diff --check` checks passed. The eleven inspected source/reference
inputs remained byte-identical, including the original 500-page PDF. Exact
commands, source identities, results and receipt hashes are in the assignment
record. No new tests were added for these documentation-only corrections.

## Integration handoff

Root should include the seven frozen Markdown files in the next appropriate
checkpoint, update only root-owned current summaries as other reviews finish,
run the applicable record/link gates and retain the exact published identity.
The [reparse repair review](PEDAL_TOOLS_EVIDENCE_FINAL.md) has a separate actual
Windows-junction execution gate. This review does not convert its Linux probes
or an earlier native artifact result into that Windows pass. Keep current
hosted/platform and rights decisions in their own records rather than freezing
an unobserved outcome into a stable API contract.

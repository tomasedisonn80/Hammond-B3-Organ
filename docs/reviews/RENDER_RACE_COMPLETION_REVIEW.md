# Renderer publication-race completion budget

17 November 2026. A31, `/root/w06_a31`, wave 6 of the heading/title
continuation. This is the narrow harness investigation and repair recommendation;
root owns final changed-source qualification, acceptance and publication.

## Decision and boundary

Change only the post-`SIGCONT` `process.communicate` timeout in
`tests/test_render_controls_admission.py` from **15 to 45 seconds**, with an
explanatory comment. The full 1,200,000-frame, block-1 workload and every
correctness assertion remain unchanged. The ordinary small-render 15-second
guard and existing **90-second CTest suite limit** remain unchanged.

The evidence supports separating this long completion wait from the small-render
guard: the unchanged method timed out locally with ASan, UBSan and leak checks;
an isolated ASan/UBSan diagnostic subsequently completed the original race and
all its assertions after **16.474323 seconds** of post-resume waiting. This is a
bounded test-harness allowance, not a renderer performance guarantee or a claim
that the revised source has passed hosted qualification.

Retain the original hosted failure, both local failures and the diagnostic
limitations. The [machine-readable receipt](../development/2026-11-16-heading-title-continuation/reports/a31-render-race.json)
contains commands, environments, complete small outputs, source/binary hashes
and the reproducible in-memory diagnostic source.

## Preserved failure and measured executions

The [original T2 investigation](T2_HOSTED_SANITIZER_REVIEW.md) identifies hosted
job `133715652514` at commit
`6047723b595259de355c74342e48a8ae2ee1e228`. Its CTest run passed 201/202 in
408.26 seconds; the five-method renderer-admission suite raised
`subprocess.TimeoutExpired` at the 15-second post-resume wait. A31 verified the
retained decoded log's 465,655 bytes and SHA-256
`058cd0f6dc6bbb94ececb420f825cb4dad0cac6807d0e50639deb7573107c320`.
The original receipt and log were not modified. No ASan/LSan/UBSan diagnostic
was reported in that original hosted log; its eventual renderer exit and later
assertions were unobserved.

All local executions below used the genuine existing compiled profile
`../build-native/nominal.b3p`. The local Debug compiler was Debian GCC 14.2.0;
the original hosted compiler was Ubuntu GCC 13.3.0. Their results remain
source- and environment-specific.

| Execution | Outcome | Timing and limitation |
| --- | --- | --- |
| Unchanged entire suite, existing Release renderer | 5/5 methods, 45 actual CLI invocations passed | 3.277927 s external; unittest 3.166 s. Sanitizers OFF; this cannot select a sanitizer budget. |
| Unchanged exact race method, Debug ASan + UBSan + leaks | One error: original 15-second `TimeoutExpired` | 15.288052 s external; unittest 15.092 s. Later refusal/sentinel assertions were not reached. |
| In-memory 60-second completion diagnostic, Debug ASan + UBSan + leaks | Failed unchanged expected-exit assertion: child exited 23 | Post-resume completion 15.501138 s; 15.926576 s external. Expected publication refusal was followed by a fatal LeakSanitizer runtime error. |
| Same in-memory diagnostic, ASan + UBSan with local leak checking disabled for this one process | One method passed; all original correctness assertions reached | Post-resume completion 16.474323 s; unittest 16.523 s; 16.732026 s external. This is explicitly not full sanitizer qualification. |

Root configured and built the separate `../build-race-sanitizer/hammond_render`
with Debug, `-fsanitize=address,undefined`, `-fno-omit-frame-pointer`, standalone
OFF and VST3 OFF. A31 ran no build or configuration. Root's configure/build logs
are identified in the receipt. The exact unchanged first run and first diagnostic
used the workflow's environment:

```text
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=exitcode=23
```

The first diagnostic's stderr contained the expected `Cannot publish WAV without
overwriting` refusal and then `LeakSanitizer has encountered a fatal error`, with
a hint that LSan does not work under ptrace. That hint does not establish the
underlying local ptrace/seccomp cause. It is an instrumentation-runtime failure,
not an observed leak finding or a pass. Because the exit assertion failed, that
execution did not reach the later sentinel/inode/snapshot assertions.

Root explicitly authorized one further isolation diagnostic with only local
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`. ASan and UBSan remained active;
the test source and all assertions remained unchanged. That execution returned
renderer status 1, empty stdout and the expected refusal, and passed the exact
sentinel-byte, device/inode, input-preservation and staging-cleanup assertions.
The hosted workflow and committed test never disable leak checking.

Both diagnostics altered only the in-memory post-resume timeout from 15 to 60
seconds and observed `communicate` duration without changing its result. Both
had an external 90-second timeout. Their result does not count as a pass of the
original 15-second method or of the subsequently changed 45-second source.

After the repair, root separately ran the actual modified five-method suite.
Both runs exited 0 with 45 CLI invocations: Release in **4.253 seconds**, and
Debug ASan/UBSan with local leak checking disabled in **20.095 seconds**.
A31 inspected their complete success logs; the receipt pins both log hashes.
These qualify the modified local harness in those configurations, while full
ASan/UBSan/LSan qualification remains pending at its published source.

## Why 45 seconds

`tools/render.cpp` validates inputs before staging, renders the entire requested
workload, flushes and closes the temporary WAV, then attempts create-only hard-link
publication. Observing staging and resuming the stopped renderer does not mean
that render work has finished. The 1,200,000-frame/block-1 fixture remains useful
for making the race observable; reducing it would change the admitted workload.

The measured complete ASan/UBSan race required 16.474323 seconds after resume.
A fixed 45-second allowance provides about **2.73 times** that observation and
28.525677 seconds of margin. A 30-second choice would provide about 1.82 times
the observation; the selected value leaves more allowance for scheduling
variation without adopting the diagnostic's 60-second ceiling. This is an
engineering budget choice based on a concrete completion observation, not an
estimate of a platform latency percentile. Hosted success still requires an
actual observed run.

The unchanged surrounding bounds keep the complete suite bounded:

| Guard | Seconds |
| --- | ---: |
| Observe a staging event | 5 |
| Confirm the child stopped | 2 |
| Complete the long render after resume | 45 |
| Final child drain after termination | 5 |
| Whole registered CTest suite | 90 |

The first four maxima total 57 seconds, leaving 33 seconds within the suite
limit for remaining methods, Python/setup/assertion overhead and ordinary renders.
That allocation is not a guarantee that every possible combination of other
guards fits: CTest continues to enforce the independent 90-second total. The
44 ordinary renderer invocations keep their individual 15-second bounds.

## Exact scope and integrity

The changed test has SHA-256
`db5a60c091098c3f140d8704a50938ef75efd3b3058acae88370676b7a8a247e`;
its original SHA-256 was
`337c2396bddf564f38ac682ac1361ef7d50282385a5dc0d7179f9c99384cc411`.
An AST comparison replaces the one new timeout value with 15 and then requires
the entire module to equal the HEAD version, ignoring comments and source
locations. It passes; `git diff --check` also passes.

Preserved behavior includes observed inotify staging; confirmed `WIFSTOPPED`
after `SIGSTOP`; destination absence while stopped; exclusive sentinel creation;
`SIGCONT`; expected exit 1; empty stdout; the refusal diagnostic; identical
sentinel bytes and device/inode; unchanged complete input snapshot; staging
cleanup; and the existing `finally` resume/kill/drain behavior. The seed, sample
rate, ideal contacts, saved controls and render workload are unchanged. No
production source, CMake file, workflow, UI input or other test changed.

## Remaining acceptance and concrete next steps

Root has run the revised local suites described above and retains ownership of
coherent affected qualification and exact-published-source ASan/UBSan/**leak-checking**
evidence. Root reported that the one unchanged hosted rerun, job `133729308448`,
completed successfully at the old T2 source. That separate observation cannot
qualify this changed test or erase the original failure. A31 did not dispatch,
repeat or independently observe the provider's job; root retains its receipt.

Do not broaden exit codes, skip the Linux body, reduce frames, disable hosted
instrumentation or remove assertions if a later run fails. Preserve its precise
phase, elapsed time, stderr and source identities, then investigate that result.
This repair supplies no Windows/macOS execution, full-suite sanitizer acceptance,
device deadline, memory-safety proof, physical fidelity or whole-interface 1:1
claim. All standing M0–M9 exits remain open according to their existing owners.

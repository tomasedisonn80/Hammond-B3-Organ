# Starter Load scheduling admission — A54, wave 9 follow-up

## Decision after the single isolated diagnostic

**Admit `RUN_SERIAL TRUE` only for `test_standalone_starter_load`.** The
required single unchanged isolated materialized-scopes method passed after
the full suite finished: 6.032 seconds at the root wrapper, 5.797 seconds
reported by unittest, with both original scopes, two application children,
and two materialization children. A54 independently verified the exact
command, environment, success log, original binary/source identities, and
equal before/after input hashes in the
[diagnostic receipt](../development/2026-11-16-heading-title-continuation/reports/starter-load-one-isolated-diagnostic.json).
Complete candidate qualification remains pending. This review does not permit a source,
fixture, oracle, timestamp, duration, or timeout change. It does not expand
any other test's scheduling policy. Root owns the diagnostic, any subsequent
single-property edit, configuration, full qualification, and publication.

The prospective admission required one unchanged diagnostic and explicitly
excluded repeating it until green. That prerequisite is now satisfied.
Root may add the one property, then must independently qualify the complete
coherent candidate with generated metadata and actual nonoverlap evidence.
The existing admissions and their original failed runs remain unchanged.

The [bounded receipt](../development/2026-11-16-heading-title-continuation/reports/a54-starter-load-scheduling.json)
preserves the entire completed starter-load failure block, including its
complete copied diagnostics, losslessly with independent hashes. Its original
preparation record retains the bounded completed log prefix captured while
the full suite was running. A separate completion record now binds the complete
[full log](../development/2026-11-16-heading-title-continuation/reports/semantic-final-ctest.log)
to **240/242**, exit 8, 614.403 seconds at the wrapper and 614.38 seconds
reported by CTest. The final log is 105,585 bytes, SHA-256
`469020395283b24fdcafd76dd97262df67789865e85154b03378e0c21e0cf7ff`.
The complete
[result receipt](../development/2026-11-16-heading-title-continuation/reports/semantic-final-coherent-results.json)
reports unchanged code and build identities. Five previously serial tests
had actual nonoverlap. The other failure, workspace startup observation,
remains a separate review and is not assigned to this scheduling admission.
The [frozen input receipt](../development/2026-11-16-heading-title-continuation/reports/semantic-final-coherent-inputs.json)
names 475 code inputs and the discovery names 242 tests. No code, native
binary, or original fixture was changed by this review.

## What failed and why the current helper must reject it

CTest reported `test_standalone_starter_load` failed in 12.13 seconds. Its
eight Python methods comprised six pure chronology tests and two native
methods. The six pure checks and generic suffix method passed; the
materialized-scopes method failed its `registration` subcase. The complete
CTest ran four actual standalone children and two materialization children.
This is not a nine-second child timeout or a 60-second CTest timeout.

The failing registration materialization first passed the CLI outcome and
exact output-byte checks, including its explicit current-expression value
0.625. Its native application then returned success, retained all 152 replay
actions, and reported no application, audio, or session faults in the checks
preceding the failing chronology assertion. The complete endpoint,
producer-desired controls, and final diagnostics matched the expected loaded
controls; the final applied and resolved sequence was 7. These facts do not
prove the intermediate edited state was copied.

Let L denote the entire loaded control snapshot and E the entire edited
snapshot, including the hidden bank, selectors, routes, fixed modes, presets,
expression, percussion, and pedals. The retained observation array contains:

| Array index | Elapsed ms | Applied / resolved / submitted | Actual copied state |
| --- | ---: | --- | --- |
| 0 | 131 | 1 / 1 / 1 | Complete L, satisfying the existing startup bound |
| 7 | 2,226 | 3 / 3 / 6 | Earlier partial edits, with later edits submitted |
| 8 | 2,226 | 3 / 3 / 7 | Earlier partial edits, with Load submitted |
| 9 | 2,226 | 5 / 5 / 7 | Partial edits; `pedal_drawbars` still differs from complete E |
| 10 | 2,567 | 7 / 7 / 7 | Complete restored L |

There is **no copied complete E anywhere in the eleven observations**, and
no observation at applied sequence 6. A54 evaluated the exact unchanged
`applied_load_chain` function, extracted from the fixture, against this copied
diagnostic object without running a native process. It correctly returned
`None`. Observation truncation is false; this is a missing qualifying state,
not a truncated evidence buffer or just an E timestamp after Ctrl+O.

The [A47 diagnosis](STARTER_LOAD_OBSERVATION_DIAGNOSIS.md) admitted A48's
chronology helper for a different failure: genuine complete E existed after
the nominal Load timestamp while a later Load was pending. The current
[fixture](../../apps/standalone/native_tests/test_standalone_starter_load.py)
already accepts that case. It requires actual copied L→E→L states in array
order with strictly advancing applied sequences, monotonic chronology,
resolved=applied, full controls, startup before 750 ms, and restoration at or
after 2,200 ms at the final sequence. The earlier admission explicitly
requires a missing E to remain a failure. No FIFO inference, pending or
desired control snapshot, eventual restoration, or manufactured sequence
may fill this gap.

The failed native subcase did not reach the following endpoint-versus-E
sequence assertion or `run_load`'s subsequent private state/source/script-byte
and directory-inventory assertions. Do not report those assertions as
executed for that failed child. A separately successful isolated method must
execute the unchanged full method, including both original materialization
scopes and their native journeys.

## Scheduling evidence and causal limits

The log shows starter-load starting while `python_test_scanner_line_profile`
is active. That test then finishes and `python_test_capture_job` starts
before starter-load finishes. This proves overlapping CTest work. It does
not identify CPU contention, scheduler latency, a blocking thread, or the
precise cause of the missing copied E.

The application retains an asynchronous Session snapshot contract. Its
bounded event drain can process multiple eligible actions before a new
Session observation; `observe()` copies a coherent published snapshot, and
`record_replay_observation()` records that copied snapshot with the current
submitted sequence. A coherent snapshot is not a history of every applied
command. The retained 5→7 observation transition alone cannot establish
whether E was separately published, whether one callback applied both
commands, or whether the main thread missed a published E. Those stronger
claims would require evidence absent from this log.

The strict gate demands a copied complete E within its unchanged 2,700 ms
journey. A successful single isolated invocation would support scheduling
sensitivity as a bounded test-environment inference. It would not establish
the exact cause, repeated stability, a product repair, or a general callback
deadline. `RUN_SERIAL` excludes other jobs from the same CTest invocation;
unrelated host load remains outside that guarantee. The separate semantic
view-paint regression and runtime fix are not credited as evidence that
this musical-control observation was present.

## Exact diagnostic and subsequent qualification

After the complete run finished, root ran this exact command once from
the repository, without another project native job:

```sh
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5a28c3564dbf/build-native/apps/standalone/hammond_standalone \
HAMMOND_REGISTRATION_EXECUTABLE=/workspace/scratch/5a28c3564dbf/build-native/hammond_registration \
python3 -B apps/standalone/native_tests/test_standalone_starter_load.py \
  NativeStarterLoadAcceptance.test_materialized_scopes_keep_their_expression_when_generically_loaded
```

Retain both `registration` and `performance` subcases: two materializations
and two actual native journeys. The fixture already sets dummy SDL audio
and video plus the software renderer. Preserve its 152 actions, 2,700 ms
duration, Load at 2,200 ms, all literals and assertions, nine-second native
child bound, 15-second materializer bound, and 60-second CTest bound. Record
both binary identities, source/fixture/data hashes, exact command and
environment, output, exit, and elapsed time before any source change.

The original failed block identifies application
`1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a`,
materializer
`872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f`,
and frozen main source
`0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537`.
The unchanged A48 fixture hash is
`96139c491057d1b3c28e4a79b9ae2b89fb1118b1afcaff4c4dd67c4a0c56f060`.
The successful isolated diagnostic retained these exact inputs. Its log
SHA-256 is
`cdcb8577f8dee46b203e09e2e0c35c8e99394aeb531f0559d4810123121195d4`.
The previously unreached assertions executed in the separate successful
method; the original failed block and its copied diagnostics remain unchanged.

With the diagnostic condition satisfied, add only `RUN_SERIAL TRUE` to this CTest and retain
the five existing serial settings. After reconfiguration, verify actual
generated boolean metadata, unchanged commands/environments/labels/timeouts,
and all 242 discovered test names. Freeze the candidate inputs and run the
complete suite once with the original `--parallel 2`, `--output-on-failure`,
and `--no-tests=error` semantics, preserving separate original logs/JUnit.
Require all discovered tests to pass without exclusions or retries. For all
six serialized tests, retain actual evidence of an empty active-test set at
start and no other start before completion. A failed candidate remains a
failure and requires its own investigation.

No prior note, admission, fixture, production source, timestamp, duration,
timeout, or expected control was edited. Exact-source VST3 hosted validation
is still a separate pending duty. This review does not close physical
hardware, calibration, signing, all-host compatibility, or whole-UI 1:1 gates.

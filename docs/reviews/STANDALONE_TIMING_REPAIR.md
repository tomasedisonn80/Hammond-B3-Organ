# Standalone smoke capture and resize observation repair

Assignment 47 of the 2026-11-13 native standalone session, actual agent
`/root/w08_a47_timing_acceptance`. This report qualifies a narrow repair with
three native ASan/UBSan suites. It does not replace the earlier failed full
gate or claim that every test in a later integrated revision has run.

## Result and source identity

The clean repaired executable passed **3/3 selected CTest suites**, comprising
**38 Python test methods and 210 actual native subprocesses**. The smoke image
now reflects the applied state that was painted. A successful smoke requesting
a screenshot also requires a held-key image. The resize test accepts only
sequence-consistent sampled states and independently requires both an
acknowledged held endpoint and an acknowledged released endpoint.

The private source starts from commit
`c5452d10f3d6a9c861d1556ac030ada93b283000`, tree
`c2b1699e1ac5750d5eb9698ded72c5b9b4c2b6a9`. This includes the current-output
device-removal repair from assignments 43/44. Four explicit overlays were used:

| File | SHA-256 in the qualified source |
| --- | --- |
| `apps/standalone/main.cpp` | `d5728ab172e53cdb99e0f7d739ae2bc90344ff44f34140749812be1bb34fe26e` |
| `apps/standalone/native_tests/test_standalone_app.py` | `6f1841c3effcbf1d9996cd72269182a0b5b9aaa5e30403f4708ac2f6b93022ef` |
| `apps/standalone/native_tests/test_standalone_workflows.py` | `46f6e354f25082524c50034bc69a645322876bf2e9912932002b87b527864fc4` |
| `apps/standalone/InstrumentView.cpp`, integrator-owned removal of two unused constants | `1cfa38a407ad2b75c4f9fb910bfa7314c694c63b9e2dee4e41fb22faf0fd283a` |

The InstrumentView overlay changes no drawing expression. Assignment 47 does
not own that file. The private build additionally appends a qualification-only
CMake target and exact-source delayed main; neither is a repository change.
The **837-file** source archive, excluding generated Python caches, has SHA-256
`4ed91cc80a551687f48f1e369388b13ff41bdd7a4e3171232ab4deebf94483d0`.

| Identity | Baseline | Clean repaired |
| --- | --- | --- |
| Ordinary main source | `3190e9a3f4a4c156f6d54ae7ddc7efa675a99d86cf2703a57af2badd443e9dbe` | `d5728ab172e53cdb99e0f7d739ae2bc90344ff44f34140749812be1bb34fe26e` |
| Ordinary main object | `acd4aa3374be8490fa8465e6a5bee9cbaaa9966dd12dc99a74adfe610d3d03e2` | `797d2427b40cde1c04c6a827d875f13acaedfcb701612cabb79bc241db1bccc5` |
| Ordinary executable | `80fc3757d0e9f40e717e5667bb91db804562ed8f045a098463f8b623e652c0cd` | `6beb6705a4a967fe4cfb01a8f83fa4106dd646f08d86f250d9974f93fbd4b6b7` |

Core sound, parameter identities, saved-state formats, plugin UUIDs, Session,
UiModel, ScriptedInput, AudioDevice and the current-device-removal predicate
are unchanged by this repair. Concurrent chapel and concurrency-test changes
are outside this frozen qualification scope.

## Preserved failure and capture repair

The [earlier native sanitizer report](STANDALONE_NATIVE_SANITIZERS.md) remains a
**92/94 failed full gate** against its named frozen source. Its six smoke
subcases failed the held-screenshot assertion, and its 1600 × 1000 resize
subcase required a held note in a sampled state after release could already
have applied. No sanitizer diagnostic accompanied those acceptance failures.
Assignment 42's source, build and evidence were not changed.

The main loop observes a callback snapshot, schedules smoke key-up when due,
and paints. The old capture predicate used `smoke_held_observed_` together with
`!smoke_off_sent_`. Queuing key-up changes that second flag immediately. It
does not change `ui_.view().applied`, the main-thread copy from which
InstrumentView paints every key. Consequently the first genuinely held frame
could lose its capture opportunity merely because key-up was queued in the
same turn.

The new predicate tests Upper MIDI 60 in the **applied view used for painting**.
Replay screenshot labeling also uses that applied view. The requested smoke
image is therefore captured on an observed held frame even when release has
just been queued. A written but unheld requested image cannot produce a
successful smoke. The original release schedule, 250–10000 ms CLI bounds,
600 ms acceptance interval, interactive event handling and replay drain limit
remain unchanged. If the allotted interval cannot produce the required held
and released evidence, smoke still fails.

Two distinct baseline defects were observed and retained:

| Run, each with a 600 ms interval | Exit / smoke result | Held label | Actual captured Upper C4 | Callbacks / frames / images |
| --- | --- | --- | --- | --- |
| Ordinary baseline, first run | 0 / passed | false | held | 46 / 23552 / 5 |
| Baseline with first held observation delayed to 425 ms | 0 / passed | false | unheld | 52 / 26624 / 5 |
| Clean repaired ordinary run | 0 / passed | true | held | 52 / 26624 / 5 |
| Clean repaired delay probe, observed at 426 ms | 0 / passed | true | held | 47 / 24064 / 5 |

All four runs observed press and release, joined with no held notes, and
reported zero render/format/nonfinite/overrange faults. The ordinary baseline
demonstrated a false image label; the delayed baseline demonstrated a missed
held capture. They are not interchangeable descriptions of the same image.
The private delay uses `SDL_Delay` immediately before the first held observation
in an exact main-source copy. It adds no production option or replay verb.
The clean repaired delayed executable has SHA-256
`08add643e6c74f850cebfd66ac9a154222c3ec2f43a239605a1f1fe0e03a7945`.

The acceptance suite now checks the actual BMP as well as the flag. Literal
interior points identify C4 and neighboring unheld D4/E4 below the accidentals
at 1280 × 900 and 960 × 700. D4/E4 must match; C4 must differ. No production
layout or painter is imported to compute that expectation. In the retained
reference captures, the held C4 sample is RGB `(180,168,125)` and unheld
D4/E4 are `(243,237,215)`; the deliberately missed baseline C4 equals those
unheld neighbors. Both delayed BMPs were also visually inspected.

## Resize oracle and actual coalescence counterexample

Changed-state replay observations are explicitly lossy UI samples. They can
skip the interval between an accepted focused edit and the accepted key-up.
Requiring the third distinct control observation to contain Upper MIDI 60
therefore imposes an extra sampling guarantee that the application does not
offer.

The repaired test retains the original released 1600 ms script and adds a
separate **1100 ms held endpoint** at each of the two sizes. Both use the same
events through the focused Right edit. The held endpoint must acknowledge the
complete final controls with exactly Upper MIDI 60 held and exactly one note
On, zero Off. The released endpoint must acknowledge those controls with no
held note and exactly one On and one Off, including the original modified
key-up. Ordinary joined shutdown must still clear all owners.

Every observed state must match a literal script prefix:

| Relative script prefix | Complete controls | Held notes |
| --- | --- | --- |
| Startup | Loaded initial controls | None |
| Home | First upper edited-B drawbar set to 0; all other fields retained | None |
| A-down | Same complete controls | Upper MIDI 60 only |
| Right after resize | That drawbar set to 1; all other fields retained | Upper MIDI 60 only |
| Modified A-up | Same complete final controls | None |

The prefix offset accounts for ordinary startup scoped releases without
assuming their number. Any observed submission before the first control event
at 500 ms must agree with that startup offset. Applied sequences must be
monotonic, resolved and applied sequences must agree, submissions must cover
observed acknowledgments, and the final applied sequence must equal the final
submitted sequence. Missing short intermediate samples are allowed; a state
with incorrect controls, owners or sequence position is not.

An exact-source private probe forced the old failure. After the 1600 × 1000
resize it delayed the next due-event pump to 1300 ms, then allowed the real
callback 65 ms before sampling the posted edit and release. The unchanged old
test failed only the 1600 × 1000 subcase: the third control transition was
sampled at **1366 ms**, applied sequence **7**, with the correct final drawbar
value and no held notes. The same binary passed the new test's **four**
held/released size cases. Its 1600 × 1000 held endpoint acknowledged sequence
6 with Upper 60 held; its released endpoint sampled sequence 7 at 1366 ms with
no holds. Both retained the entire original musical file unchanged.

This probe has source SHA-256
`1be22b9553444ab0f1fe53262e4356a208588b1533cf4c1f93c2da67e80a4a84`
and executable SHA-256
`b4f836d3f2f1b46aabc4555acee2430ce3245dccc643923a455f52d420395f01`.
It uses the old ordinary main plus only the two private delays, real SDL,
real Session and the real callback. The test harness only copies temporary
artifacts before ordinary cleanup; it does not alter assertions or responses.
Old/new runs took 3.923/6.610 seconds and launched 2/4 processes respectively.

## Coherent sanitizer qualification and one invalidated attempt

The clean qualification uses GCC 14.2.0, Debug, Unix Makefiles and pinned SDL
2.32.10 at `5d249570393f7a37e037abf22cd6012a4cc56a71`. Configure took 33.217
seconds; compiling both the ordinary app and private smoke probe took 49.759
seconds. Global C, C++ and executable/shared-link sanitizer flags are present,
in addition to `HAMMOND_ENABLE_SANITIZERS=ON`:

```sh
cmake -S source -B build-repaired -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_ENABLE_SANITIZERS=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2 \
  '-DCMAKE_C_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer' \
  '-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer' \
  '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined' \
  '-DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined'
cmake --build build-repaired --target hammond_standalone hammond_timing_probe --parallel 4
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 \
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 \
ctest --test-dir build-repaired --output-on-failure \
  -R '^test_standalone_(app|workflows|replay_boundaries)$'
```

The command shown assumes the qualification-only probe target included in the
frozen source archive; an ordinary repository build does not have that target.
Exact executable paths, output-log settings and argv are retained with evidence.
There are 263 compile-database entries, of which **206 objects were actually
built**: 19 core, 11 standalone/application/probe and 176 SDL C objects. Every
built object has ASan, UBSan and frame pointers. All five resulting static
archives contain references to both sanitizer runtimes; the ordinary link is
also instrumented. Unbuilt test targets are not counted as compiled coverage.

| Suite | Methods | Actual subprocesses | CTest seconds | Result |
| --- | --- | --- | --- | --- |
| Native application | 18 | 164 | 14.36 | Passed |
| Musical workflows | 11 | 17 | 28.32 | Passed |
| Replay boundaries | 9 | 29, including 19 expected setup rejections | 7.39 | Passed |
| Selected gate | 38 | 210 | 50.084 measured wall time | 3/3, exit 0 |

No selected test was disabled or skipped. No ASan/UBSan report was emitted.
LeakSanitizer was explicitly disabled because assignment 42 already established
its fatal ptrace limitation in this environment; that probe was not repeated
and no leak-detection pass is claimed.

An earlier incremental attempt is explicitly **invalidated for repair
qualification**. Copying the repaired main with `copy2` preserved a timestamp
older than the already compiled baseline object. Make rebuilt the private
delay probe but retained the old ordinary executable. Its unchanged binary
SHA exposed the mismatch. The focused run against that old ordinary binary
failed 1/3 suites, specifically legacy-state version 2's screenshot label;
the new bounded failure payload retained its complete diagnostics. Its logs,
JUnit, source manifests, unchanged ordinary hash and LastTest.log were preserved
under `stale-*`. The clean result above came from a newly configured
`build-repaired` directory and verified changed source, object and executable
identities. The invalid attempt is not a successful retry or evidence for the
repair.

## Evidence locations and handoff

Frozen artifacts are under `/workspace/scratch/5ba97739b54c/a47-timing/`:

- `base.tar`, `baseline-source-manifest.json`, `baseline-overlays/`,
  `qualified-source.tar.gz`, `repaired-source-manifest.json` and
  `main-build-identity.json` identify the old/new source and builds.
- `before-ordinary/`, `before-delayed/`, `after-ordinary/` and
  `after-clean-delayed/` retain executables, invocation metadata, stdout/stderr,
  complete JSON, BMPs and sampled pixel values.
- `fixed-configure-argv.json`, `fixed-build-argv.json`, their logs/results,
  `final-instrumentation.json`, `sanitizer-environment.json`,
  `focused-ctest-argv.json`, `focused-ctest.log`, `focused-junit.xml` and
  `build-repaired/Testing/Temporary/LastTest.log` retain the actual gate.
- `resize-probe/` retains exact delayed source, old/new assertion logs,
  compile/link argv, binary and every before/after script, musical file and
  diagnostics JSON. `stale-*` and `stale-build-exclusion.json` retain the
  invalidated attempt rather than hiding it.

The repository change is limited to main, the two acceptance files, the
[application contract](../STANDALONE_APP.md), this report and the
[assignment note](../development/2026-11-13-next-phases/47-timing-acceptance.md).
Process-exit and new timing assertion failures include at most 65536 characters
of diagnostic evidence before fixture cleanup, with truncation marked.

The integrator must run the complete relevant gate against the final integrated
source, update current status and the actual assignment manifest, and commit
and push under the standing authorization. Later host builds qualify their own
revisions. Dummy audio/software rendering proves callback, event, image and
shutdown behavior for this scope; it does not qualify physical output,
audibility, hardware latency, device removal, distribution or acoustic fidelity.

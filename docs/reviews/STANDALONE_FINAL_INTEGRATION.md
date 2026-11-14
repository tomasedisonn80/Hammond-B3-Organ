# Final native integration and sampled-workflow oracle repairs

Worker `/root/w10_a55_full_integration`, actual assignment **55/60**, wave **10**.
Execution spans 2026-11-13–14 UTC. The current session remains
`2026-11-13-next-phases`. This report qualifies named snapshots and records the
two failed gates as well as the subsequent changed-test qualification.

## Observed outcome

| Source and scope | Observed result | Duration |
| --- | --- | --- |
| Published `0085e338`, complete native-enabled Linux Release registry | **105/105 CTest suites passed**, exit 0 | 118.19 s CTest; 118.205 s recorder |
| Same source, fresh fully instrumented Debug native group | **13/14 passed; chapel failed**, exit 8 | 104.89 s CTest; 104.897 s recorder |
| Repaired chapel test, unchanged Release executable | **2/2 methods passed; 22 exports and 22 actual SDL runs** | 19.526 s unittest; 19.726 s recorder |
| Repaired chapel test, unchanged original ASan/UBSan executable | **2/2 methods passed; 22 exports and 22 actual SDL runs** | 23.466 s unittest; 23.631 s recorder |
| Chapel-repaired snapshot, separate fresh fully instrumented build, complete native group | **13/14 passed; workflow failed**, exit 8; chapel passed all 22 auditions | 115.05 s CTest; 115.057 s recorder |
| Workflow-repaired snapshot, unchanged Release executable | **11/11 methods passed; 25 actual native processes** | 38.037 s unittest; 38.160 s recorder |
| Workflow-repaired snapshot, unchanged instrumented executable | **11/11 methods passed; 25 actual native processes** | 42.775 s unittest; 42.941 s recorder |
| Workflow-repaired snapshot, verified existing instrumented build, complete native group | **14/14 passed**, exit 0 | 117.28 s CTest; 117.292 s recorder |

Each named gate was executed once. The changed-test checks followed an explicit
oracle repair; they were not unchanged retries. The original failures, sources,
executables and logs remain intact. No ASan/UBSan diagnostic was observed in
the three complete instrumented executions, but each assertion failure still
made its gate unsuccessful. **Leak detection was disabled; no leak pass is
claimed.** These results do not qualify later concurrent calibration changes or
all platforms, and the repaired complete sanitizer run covers the fourteen
native suites rather than all 105 Release suites.

## Exact frozen inputs

The original source is local commit
`fa6df9d04916da8e23938cc3e85f524e3707e7d8`, published with the identical tree as
`0085e338388f2c7516a7d455f11692b94e9451f4`. Both resolve to tree
`19c763503f67e1f054d2d27b6ec3d8fca2e36474`. The 38,348,800-byte Git archive has
SHA-256 `20eead08efbea0dace72cd30c04af28b43ef7415140ed3f71e0fead48173fe20`.
All **894** tracked file blobs and executable modes matched Git before and after
execution; the source PDF is included in that unchanged inventory.

The first, chapel-repaired snapshot is a new extraction of that same archive
with exactly these two overlays:

| Changed path | Bytes | SHA-256 |
| --- | --- | --- |
| `apps/standalone/native_tests/test_standalone_chapel.py` | 14,969 | `18c645a30d6909ba331eac1f31abe71d9c8ccfe3c611278998f65f9ee5824323` |
| `docs/CHAPEL_CONTROLS_ACCEPTANCE.md` | 8,015 | `334de427be4f57bda85ab54c2181518b1ebd3f515425f29929a323870ccae695` |

Its other **892 files**, all C/C++ sources and headers, CMake inputs, generators,
model data, dependency records and installed payload inputs match the original
source byte for byte. The complete repaired inventory SHA-256 is
`120a814db7194030be88664d2686ba1f11a052953c2ef8a061b4f74854a86ce1`; its contents
and file modes remained unchanged after its focused and complete checks.

The final workflow snapshot is another extraction of the same original archive,
retaining those two overlays and adding exactly these two:

| Changed path | Bytes | SHA-256 |
| --- | --- | --- |
| `apps/standalone/native_tests/test_standalone_workflows.py` | 34,483 | `982d76999592838689f0918f8bb937d68082514158b64c1c9bcd94eca3856428` |
| `docs/STANDALONE_WORKFLOWS.md` | 9,316 | `fda4fd6564fb263ee83c4014db730371fbfd33c8403a5ba0686381eeb72524d2` |

All **890** remaining original files and all compiled inputs are unchanged.
Its complete inventory SHA-256 is
`9f73fe9599f583692292a16dc2357cb877549819d3322667019913ce883763a0`.
The reports themselves are later documentary output and are not part of any
execution snapshot. No production C++, model, parameter identity, state format,
plugin UUID or install rule was changed by this assignment.

Private evidence root:
`/workspace/scratch/5ba97739b54c/a55-full-integration`.
Its `source/`, `release/` and `asan-ubsan/` retain the original gate.
`repaired-source/`, `repaired-asan/` and `repaired-evidence/` retain the chapel-only
qualification and its workflow failure. `workflow-source/`, `workflow-ctest/`
and `workflow-evidence/` retain the final four-overlay source, independent CTest
driver and results. No binary or raw execution log was added to Git.

## Toolchain, build inputs and commands

Observed environment: Linux 6.18.57 x86-64, glibc 2.41, GCC/G++ 14.2.0,
CMake/CTest 4.4.4, Make 4.4.1 and Python 3.12.14. CPU affinity allowed CPUs 0–8;
the machine was shared, so these elapsed times are not controlled performance
measurements. CMake/CTest were invoked from
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin`.
The read-only SDL2 checkout was `/workspace/scratch/5ba97739b54c/SDL2`, version
2.32.10 at locked commit `5d249570393f7a37e037abf22cd6012a4cc56a71`.
The maintained verifier passed before and after the original gate and after the
repaired gate.

No C/C++/link flags, sanitizer options, generator or SDL driver overrides were
inherited at the initial environment inspection. Commands explicitly set
`PYTHONDONTWRITEBYTECODE=1` and `LC_ALL=C.UTF-8`. Native SDL fixtures set their
own dummy drivers. Sanitizer commands additionally set:

```sh
export ASAN_OPTIONS=detect_leaks=0:halt_on_error=1
export UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
```

The explicit leak exclusion follows the observed ptrace runtime failure in
[assignment 42](../development/2026-11-13-next-phases/42-native-sanitizers.md).
No new leak-runtime probe or leak qualification was attempted here.

Equivalent commands below use the evidence root as the working directory,
the frozen directories described above, and those exact CMake/CTest tools on
`PATH`. The original Release configure and full default build passed in 29.192
and 133.977 seconds. Its 260 actual compiled objects all contained `-O3` and
`-DNDEBUG`, with no sanitizer flag.

```sh
cmake -S source -B release -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2
cmake --build release --parallel 2
ctest --test-dir release -C Release --show-only=json-v1
ctest --test-dir release -C Release --parallel 2 --output-on-failure \
  --no-tests=error -V --output-junit release-junit.xml
cmake --install release --config Release --component Standalone \
  --prefix installed-release
```

Original and chapel-repaired instrumented builds used the following configuration,
substituting `source`/`asan-ubsan` for the original run. Original configure/build
times were 26.743/77.522 seconds; repaired configure/build times were
30.289/102.030 seconds. Each was a new build directory.

```sh
native_sanitizer_flags='-fsanitize=address,undefined -fno-omit-frame-pointer'
cmake -S repaired-source -B repaired-asan -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_ENABLE_SANITIZERS=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2 \
  -DCMAKE_C_FLAGS="$native_sanitizer_flags" \
  -DCMAKE_CXX_FLAGS="$native_sanitizer_flags" \
  -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined \
  -DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined
cmake --build repaired-asan --target hammond_standalone_test_inputs --parallel 2
ctest --test-dir repaired-asan -C Debug -R '^test_standalone_' --show-only=json-v1
ctest --test-dir repaired-asan -C Debug -R '^test_standalone_' \
  --output-on-failure --no-tests=error -V \
  --output-junit repaired-evidence/native-junit.xml
```

The sanitizer environment above applied to configure, build and CTest. The
aggregate target built the actual executable, benchmark and every native test
input before registry discovery and execution. Both native registries contained
fourteen suites. Focused checks used `python3 -B` on the repaired chapel test,
`-v`, the explicitly selected prior executable through
`HAMMOND_STANDALONE_EXECUTABLE`, and an outer `timeout --signal=TERM 90s`; the
ASan invocation also used the same explicit sanitizer environment. File and
binary hashes were checked before and after reuse. Nothing was relinked against
live or changed C++ headers.

The later workflow repair changes no compiled input. Root explicitly authorized
reuse of the verified chapel-repaired instrumented build instead of another
identical C++ rebuild. Before and after execution, all 213 object hashes, five
archive hashes, ten runtime executable hashes, generated profile/headers,
compile database and benchmark source-manifest bytes matched the retained build.
The final executable remains `0ba61b78...` below.

An isolated CTest driver copies the three generated `CTestTestfile.cmake` files,
substitutes only the exact frozen `workflow-source` path and explicitly preserves
working-directory selections with that same source substitution. Registry comparison requires
all fourteen names, commands, configurations, environments, timeouts, labels and
working directories to equal the original registry after that source substitution.
The original `DartConfiguration.tcl` default of 1,500 seconds is supplied
explicitly; 15/60/90-second per-test overrides remain unchanged. The final command
is therefore:

```sh
ctest --test-dir workflow-ctest -C Debug -R '^test_standalone_' \
  --timeout 1500 --output-on-failure --no-tests=error -V \
  --output-junit workflow-evidence/native-junit.xml
```

The old source snapshots, compiled outputs and CTest failure logs are preserved.
Install tests may update CMake's install manifest; its prior contents are retained
in `workflow-evidence/install-manifests-before.json`. All Python
test commands in the final registry point to the frozen four-overlay source.
The install test uses the existing compiled build and its byte-identical
installed payload inputs. Focused workflow checks used that same frozen source,
an outer 90-second timeout and the unchanged Release/instrumented executables.

## Counts, skips and the preserved original failure

The actual Release registry contained **105** tests. It has no disabled or
skipped CTest suites. The complete verbose log contains 57 Python method
summaries totaling 1,192 methods; these are not counts of subcases or external
processes. `python_test_capture_audio_admission` ran 62 methods and reported two
internal skips. The retained unittest class/method order identifies
`FilesystemAdmission.test_native_windows_reparse_fixture` and
`FilesystemAdmission.test_real_unix_socket_is_rejected_before_open`.
The former requires native Windows, and the latter depends on the native socket
fixture capability; the concise log did not retain its precise operating-system
error. Neither skip is counted as a disabled CTest suite.

All native runs also retain the state-file suite's explicit **NOT TESTED** case:
POSIX replacement failure after a complete temporary write has no deterministic
non-racing fixture. Its controlled `RLIMIT_FSIZE` write-failure case did run.
This limitation is separate from both CTest skips and Python skip counts.

The original sanitizer gate failed only
`test_standalone_chapel.test_paired_banks_and_binary64_expression_serialization`,
in the second paired audition: Upper **D#**, Lower **G**, bank **A**, expression
**0**. Its 900 ms replay accepted two note-ons and two note-offs, releasing
Lower MIDI 64 at 600 ms and Upper MIDI 60 at 700 ms. The exact-list oracle
expected empty → Upper → both → Upper → empty, but copied UI samples contained
empty → Upper → both → empty. The 100 ms Upper-only interval was not recorded.

Before the failing old line 190 assertion, the fixture had already checked
successful process exit, empty stderr, exact final controls, Save status, dummy
runtime, positive callback/frame counts, zero audio failures, zero recovery/
overflow/rejection/faults, zero peak at expression zero, full replay delivery
and acknowledgement, exact event and note-command counts, and controls in
each sampled snapshot. The later explicit final-empty, non-smoke, canonical
saved-byte and unchanged-input assertions **were not reached for that failed
case**. The old fixture cleaned its temporary diagnostic JSON; the retained
record includes the case, source/binary identities and assertion difference,
but not full per-process JSON or observation timestamps. Source inspection
shows that sampling may coalesce callback transitions; the missing trace does
not establish the exact timing of this individual run.

## Narrow oracle repair and changed-source qualification

The coordinator explicitly authorized changing the chapel test and its
[acceptance guide](../CHAPEL_CONTROLS_ACCEPTANCE.md). The two original paired
auditions retain their 900 ms scripts, two note-ons, two note-offs, complete
acknowledgement and empty endpoint. The eighteen single rows keep 700 ms
scripts. Every sampled snapshot must now equal the literal accepted-command
prefix corresponding to its applied sequence, preserve complete controls, have
equal applied/resolved values, progress monotonically and not exceed submitted
commands. No intermediate UI sample is required solely because a musical state
existed between scheduled events.

Two additional 650 ms auditions, one for each paired registration/expression,
omit only Upper's final release. They require two note-ons, exactly one Lower
note-off and an independently acknowledged endpoint holding **Upper MIDI 60**,
with Lower and pedals empty. Normal joined shutdown must still clear every
hold. This endpoint proves Upper ownership after Lower release without requiring
a sample in the original 100 ms interval. The suite now performs **22** real
exports and **22** actual application invocations in its existing two unittest
methods, eight-second process timeouts and 90-second CTest budget.

Final endpoint, non-smoke, canonical Save bytes and untouched catalog/script/file
set checks precede the sampled-prefix oracle. Every post-invocation exception
copies up to 65,536 diagnostic bytes into the failure message before cleanup,
with an explicit truncation or unavailability marker. Independent assignment 59
reviewed the failure boundary and repair and separately exercised that helper;
those reviewer probes are not counted as application runs by assignment 55.

Both focused chapel checks passed first. The subsequent fresh instrumented
build passed chapel's two methods and all 22 auditions in 23.942 seconds, but
the complete native gate failed **13/14** in 115.05 seconds. Its only failed
suite was the unchanged `test_standalone_workflows`, with two failed methods.

## Preserved workflow failures and second narrow repair

The Help method expected empty → Upper 60 → empty → Upper 60 → empty;
the sampled list was empty → Upper 60 → empty. Its second press at 1200 ms
and release at 1350 ms did not appear as a distinct sampled hold interval.
The target/octave method's list omitted the empty state between the pedal 17
release at 1900 ms and a fresh Upper 72 press at 2100 ms. Other recorded
hold sets matched the expected order. These observations are consistent with
the same sampled-snapshot limitation, but the missing original JSON prevents
reconstructing the exact command/timestamp history of either failed run.

Both stopped at old `assert_hold_path` line 269. Their shared `invoke()` checks
had passed process exit/stderr, dummy audio/window operation, positive callbacks
and frames, joined shutdown with empty holds, zero audio/session faults,
complete event delivery and final acknowledgement, and script/file-set integrity.
The helper's subsequent explicit pre-shutdown final-hold check and each method's
literal command-count, control and saved-state-byte checks **were not reached**.
The target case's release-timing/positive-peak checks and Help's release-before-
close timing check were also unreached. Later assertions did not retain full
JSON in that original workflow fixture. Both failed method traces are preserved;
no unchanged rerun was attempted.

Root then extended ownership to this workflow test and
[guide](../STANDALONE_WORKFLOWS.md). Only the two failed methods gained the new
prefix oracle. The original 2600 ms target/octave fixture and 2000 ms Help
fixture retain their complete scripts, full acknowledgement, exact 4/4 and 2/1
note On/Off counts, complete controls, unchanged initial state bytes and empty
pre-shutdown endpoints. All common input/audio/joined-shutdown checks remain.

Five new target/octave prefix endpoints at 1450, 1650, 1850, 2050 and 2250 ms
require, respectively, all three original owners (Upper 60/Lower 74/pedal 17),
Lower 74 plus pedal 17 after Upper's release, pedal 17 after Lower's release,
empty after pedal release, and fresh Upper 72 at the retained manual octave.
Three Help endpoints at 700, 1000 and 1300 ms require empty holds while Help
remains open, continued suppression after Return closes it before the original
physical Up, and fresh Upper 60 held before its later release. Their exact
note-command counts are literal and independently checked. These endpoints
require the critical musical states without imposing a short UI sampling window.

Counts, complete controls and saved bytes precede the sequence oracle; exact
final acknowledgement and endpoint holds precede its sample loop. Each sampled
state must match a literal command prefix with monotone applied/resolved
sequences, complete unchanged controls and no applied command earlier than its
scheduled time. The helper requires exactly one device start; it is not reused
across the Audio workflow's sequence epochs. All later assertions in these two
methods retain bounded JSON on failure. Nine-second per-process and 90-second
suite budgets remain. Eight extra endpoints bring workflows to **11 methods /
25 actual processes**. Other exact hold/control-path assertions remain unchanged
and are explicitly outside this narrow repair's independent endpoint coverage.

Independent assignment 59 reviewed both repairs and separately tested their
oracle/failure-retention helpers. Its synthetic probes are not SDL executions
or recovered diagnostics from the missing original traces. The workflow guide
also now selects `Release` explicitly for multi-configuration build/CTest use.

The changed workflow suite passed first in both configurations: 11/11 methods,
25 actual processes, 38.037 seconds Release and 42.775 seconds ASan/UBSan.
The final complete native group then ran once using the verified existing
instrumented artifacts and frozen four-overlay test source:

| CTest suite | Seconds | Result |
| --- | --- | --- |
| `test_standalone_install` | 4.819 | Passed |
| `test_standalone_concurrency` | 0.999 | Passed |
| `test_standalone_session` | 1.948 | Passed |
| `test_standalone_state_files` | 0.067 | Passed |
| `test_standalone_ui` | 0.080 | Passed |
| `test_standalone_benchmark` | 15.839 | Passed |
| `test_standalone_audio_device` | 3.510 | Passed |
| `test_standalone_device_removal` | 0.302 | Passed |
| `test_standalone_callback_allocation` | 1.338 | Passed |
| `test_standalone_app` | 14.501 | Passed |
| `test_standalone_workflows` | 42.270 | Passed |
| `test_standalone_replay_boundaries` | 7.519 | Passed |
| `test_standalone_chapel` | 23.948 | Passed |
| `test_standalone_input_replay` | 0.122 | Passed |

The final gate has zero disabled/skipped CTest suites and no reported internal
Python skips. Its six Python suites comprise 53 methods. The chapel suite's
22 auditions passed all complete controls, count, acknowledgement, final-state,
saved-byte and input-preservation checks. Workflows passed all 25 processes.
A fresh complete Release registry was not rerun by this worker after the
test-only repairs; the focused chapel and workflow Release checks provide the
affected-scope evidence. Later remote calibration/Python changes are outside
all three snapshots and require their own integrator-owned evidence.

## Instrumentation and exact artifacts

For each instrumented build, the audit inspected **213 existing object files**
from 260 compile database entries: 19 core C++ objects, 18 standalone runtime/
test/benchmark objects and all 176 SDL C objects. All actual compiler argument
vectors contain `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`. The other 47 entries were not built by the selected
native aggregate and are not claimed as instrumented execution. `nm -u` found
both ASan and UBSan references in the core, standalone support, audio, replay
and SDL archives. `ldd` identified both runtimes for the actual application.

An auxiliary audit error occurred after the original successful build and before
its first CTest run: the initial script resolved CMake's `output` metadata
relative to each compiler working directory. SDL's metadata was relative to the
top-level build, so this falsely classified its objects as absent. The corrected
audit resolves the actual compiler `-o` argument against its command directory
and independently requires agreement with the build-relative CMake field. The
original script/failure JSON remain retained. No build, source, functional
expectation or test was retried to correct this audit.

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| Original Release application | 2,598,768 | `def97cef70b3eafcd108170a985c61215b878c918debde6ff2fb236a2a9c3416` |
| Original instrumented application | 49,861,656 | `d877e0db60335b16e29642180ad82567e5b49f872fee755b5494f8b632d0f1c2` |
| Chapel-repaired instrumented application, reused unchanged for final workflow gate | 49,861,912 | `0ba61b78da4bf554951b777421752459c9b69ce9a16d29cce587f2e077594658` |
| `nominal.b3p`, all three builds | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Original Release `chapel-catalog.json` | 4,837 | `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91` |
| Unchanged `apps/standalone/main.cpp` | 67,766 | `d5728ab172e53cdb99e0f7d739ae2bc90344ff44f34140749812be1bb34fe26e` |

The generated pedal-routing header, scanner-line header and embedded-profile
header also byte-match between the original and repaired instrumented builds.
The fresh Debug executable has its own identity; no reproducible-binary claim
is inferred from unchanged C++ source. Assignment 56 used the original Release
application and its profile/catalog read-only for the separately documented
[chapel demo](STANDALONE_CHAPEL_DEMO.md).

## Installed payload and secondary SDL notices

The original explicit Release component install passed in 0.054 seconds.
Independent file-set and byte comparisons found exactly **nine ordinary files**,
with executable mode 0755 and data mode 0644. Metadata lives under
`share/hammond-b3-organ/standalone/`; the executable is `bin/hammond_standalone`.
The maintained install suite passed in both original configurations and the
repaired native gate, including its rejection/preservation checks.

| Installed filename | Bytes | SHA-256 |
| --- | --- | --- |
| `hammond_standalone` | 2,598,768 | `def97cef70b3eafcd108170a985c61215b878c918debde6ff2fb236a2a9c3416` |
| `STANDALONE_INSTALL.md` | 6,379 | `4b49aa3babff92869a07bf67798b84fe179039163ca231db62136dc8329bf9b1` |
| `STANDALONE_APP.md` | 14,757 | `9f362198397d15c8e7c1ef0a9c66f0e9a7c44763d073eaf70fe627fe9619c7ba` |
| `STANDALONE_MODEL.md` | 4,837 | `bc62dc35dcb39d6538ac2b8475bd9cd997fd439f11201a3b2701e798c62f6649` |
| `THIRD_PARTY_NOTICES.md` | 16,366 | `3d4acfae5c0c83b5184d3806b1ce70040beeaf027da28b541ab220e764ae4faa` |
| `LICENSE-SDL2.txt` | 884 | `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` |
| `LICENSE-DejaVu.txt` | 2,345 | `22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6` |
| `sdl2-lock.json` | 375 | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |
| `font-source-manifest.json` | 1,428 | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |

The installed combined notice reproduces the complete pinned yuv2rgb license
(1,480 bytes, SHA-256
`f7d74004cc75778cae46c5f0139f244d67c07ef64cf51937e8272352197dcb18`), HIDAPI BSD
text (1,534 bytes,
`30eb1bef29b46f8ba7ab8b416035dbd93cb034a45481dd97815b944284582cd2`) and Sun
notice from the first comment of `src/libm/e_pow.c` (379 bytes,
`0c3d0381d2cd647be68590170490be5f624c962d9f95eb698489e578c1de8f05`). These were
compared directly against the verified pinned SDL checkout. This is an actual
copy/text check of the selected payload, not full transitive licensing or
distribution clearance.

## Retained evidence and next action

These paths are relative to the private evidence root above. Full verbose logs
and `Testing/Temporary/LastTest.log` retain successful-test output that CTest's
JUnit representation may truncate. UTC process start/finish times come from
the recorder's `results/*.json`; the JUnit timestamp is the tool's local time.

| Evidence | SHA-256 |
| --- | --- |
| `logs/05-release-all-tests.log` | `b69a8a692032a4d26304f8a2e4a471b162251cff1cb1ba9d229d8bc2d10d9862` |
| `release-junit.xml` | `34a0239e160eb85dfaf8c7d45a0c725ab5105b665b1ad54e91b3855e6a0331fe` |
| `logs/10-sanitizer-native-tests.log` | `d2ab963c4a45c06940a0655993157be1bcbc4ce24c9ba8ddddb00575ed6afa66` |
| `sanitizer-native-junit.xml` | `01743110aae96e0c579ca7e3779b218444384de07d1a690b89c7e534c27bf632` |
| `logs/FAILED-test_standalone_chapel.log` | `a42347d3d95de4d6912886cd3b9583f085eefdbcdd209649c9983932ad9169f6` |
| `sanitizer-instrumentation.json` | `c5c22c630b79eef34f9c3fa092153cdb022fd89c734b80f733c9d77e5994d620` |
| `installed-payload-verification.json` | `059b8b381c2af3be7f7665345e26c8fdca7295c458b30a5526cb6f7030fe87c8` |
| `repaired-evidence/source-inventory-before.json` | `120a814db7194030be88664d2686ba1f11a052953c2ef8a061b4f74854a86ce1` |
| `repaired-evidence/logs/01-focused-release-chapel.log` | `01a2e7814495e66bb1b0fc9de614e5f72773d8eab52810ca3e2b3d24aa25caa9` |
| `repaired-evidence/logs/02-focused-sanitizer-chapel.log` | `154c1f60420399393184e670fcf131771cc5cab8ecf44113dba6263e2e202d40` |
| `repaired-evidence/logs/06-native-tests.log` | `2079aa51b33f0059a2767ad1c51f888665b3696a7e08469b98ed3910fe9b084c` |
| `repaired-evidence/native-junit.xml` | `e91079933b99c477ff251bb0f86c9be3b27acefcefebe38b09d75a8682b8a306` |
| `repaired-evidence/sanitizer-instrumentation.json` | `0bede93c60029c85ceaaecca4a9155d0c726be62b32c6437ea04e03712c6d58b` |
| `repaired-evidence/logs/FAILED-test_standalone_workflows.log` | `bce320a5e67425f7f06cca6245aa89f03fe742bb2c9bd6e6e5e3c2a15294c83f` |
| `workflow-evidence/source-inventory-before.json` | `9f73fe9599f583692292a16dc2357cb877549819d3322667019913ce883763a0` |
| `workflow-evidence/compiled-artifacts-before.json` | `a41357f19ec7324345d8d12553b9c6ea2c7eb633a949c119c05557074189368a` |
| `workflow-evidence/registry-comparison.json` | `c6416f5f3000b7ccbeee20277bb0105fab21e3f4d8354eb9e6ff6f580d091059` |
| `workflow-evidence/logs/01-focused-release-workflows.log` | `dd3938ac4162bcd1ec6d9f907be370fe193e8c04a8dfbf63477e26dad9ef0ef5` |
| `workflow-evidence/logs/02-focused-sanitizer-workflows.log` | `51f10fec48e5b6b2c618ab18f1a32d8125b44e9cbf649c5415ceab43fdd59507` |
| `workflow-evidence/logs/04-native-tests.log` | `9c4d163aa53581631d19763e32ea678c82a4ddb3e1ec6db81e165f7f3f43928a` |
| `workflow-evidence/native-junit.xml` | `88b2614bd98da3d6c659ca64e15c9bc6e7756e21ecdfd2f8d3b3fd5323f3e6fd` |

The evidence root also retains `run_gate.py`, its original audit-error version,
`continue_gate.py`, `repair_gate.py`, `workflow_gate.py`, exact command/environment/timing records,
original and repaired source inventories, compile argument/object/archive
manifests, linkage output, generated artifact identities, and the complete
two-file chapel repair and four-overlay final diffs. Raw artifacts remain private
as assigned.

The integrator should review the six owned repository paths, accept the repairs
with assignment 59's independent review, preserve both failed native gates, and
publish the reviewed result under the standing no-force-push workflow. The
integrator reported a separate Windows core failure at public `0085e338`
(92/96; capture audio/corpus CLI and path-fixture cases), then a concurrent
calibration advance to `955fc4c`. Root subsequently reported a fresh combined
Release **110/110** pass at public `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`
and publication of the exact final workflow test at
`6214032f3565f9e221fcf3988e33a22a73bb4ea8` (tree
`10f070c54d176571f1919d8141d24dd82db0e41c`). These facts were communicated by root, not
independently queried by this worker, and neither issue is closed by these Linux
results. Assignment 58/root own the Windows Python follow-up and combined-source
qualification. Check the current [handoff](../STANDALONE_HANDOFF.md) before
interpreting this snapshot as the current published repository.

Actual audio devices, musician latency/underruns, thread-race qualification,
assistive accessibility, signed/platform distribution, physical selector and
loaded-gain behavior, measured AO-28/scanner/Leslie fidelity and leak checking
retain their own gates. The next native runtime qualification needs a named
machine/device/backend and predeclared observed callback, concurrent-UI and
underrun/latency acceptance criteria. The dummy backend and this deterministic
test repair do not replace that acquisition.

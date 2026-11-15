# Product Linux hosted qualification — A49

**All six scoped Linux jobs are qualified at d8, 15 November 2026 UTC.** This review belongs to actual worker
`/root/w09_a49_linux_hosted`, wave 9 of the product continuation. It audits primary
GitHub job logs for the exact published source below. The expanded native
sanitizer repair passes 21/21; the earlier failed build remains retained.

## Exact source and method

- Commit: `d8c39f7986746eacc991747153c7dbb012bb9a32`.
- Tree: `edf67b978f93e8dbea6537ce92d3928c171bc1f3`.
- Parent: `d556da017ea0a5d4f2d231416782dbc5066e58c2`.
- [CI run 43668397337](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337), push attempt 1.
- [Native standalone run 43668397338](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338), push attempt 1.

GitHub's commit object independently matches the local commit/tree/parent. The
completed checkout and revision-recording lines identify that commit. The audit
uses decoded primary logs, completed step boundaries, exact CTest results and
the source of executed assertions; an API success status alone is insufficient.
Worktree changes for A46/A48 and later publication are outside this qualification.
The [bounded primary receipt](../development/2026-11-15-product-continuation/reports/A49-linux-hosted.json)
retains full decoded-log identities, exact excerpts with line locations, all
executed CTest names/timings and parsed material/calibration evidence.

## Observed Linux results

| Job | Actual result | Configuration and scope |
| --- | --- | --- |
| [Core Release, 132672791917](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337/job/132672791917) | **155/155**, 80.57 s | Release, GCC 13.3.0, CMake/CTest 3.31.6, Python 3.12.16; default core/support selection. |
| [Core sanitizers, 132672792034](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337/job/132672792034) | **155/155**, 234.39 s | Debug, GCC 13.3.0, CMake/CTest 3.31.6, Python 3.12.16; ASan/UBSan and the named leak-policy boundary below. |
| [Full R4, 132672791770](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337/job/132672791770) | **Full mode passed**, 722.029333257 s | Independent Release waveform experiment; 14 admission self-tests also pass. |
| [Native MIDI ON, 132672792114](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/job/132672792114) | **48/48**, 328.42 s | Release, compiled ALSA MIDI backend; dummy SDL acceptance. |
| [Native MIDI OFF, 132672792135](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/job/132672792135) | **48/48**, 327.47 s | Release, unavailable physical MIDI backend; dummy SDL acceptance. |
| [Native sanitizers, 132672791944](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/job/132672791944) | **21/21**, 342.06 s | Release with instrumented project C++ and pinned SDL C; exact 21-test selection. |

Core Release and sanitizer logs contain the same 155 unique executed names.
The crossover native response, allocation and lifecycle tests, Python response,
reference and installer, and native support channel/calibration gates all pass.
`python_test_crossover_install` passes in **1.03 s Release / 1.93 s Debug
sanitizers** on the older hosted CMake 3.31.6 path that exposed the original
installer policy defect. The logs report no sanitizer diagnostic. The core jobs
do not build the native SDL application.

The Linux Release log also records successful strict checks for the historical
interface and reference-refinement sessions. Those checks do not close the
current product session; its new A46 checker is absent from this tested source.

## Native Release and installed packages

Both native jobs use Ubuntu 24.04 x64, GCC/G++ 13.3.0, CMake/CTest 3.31.6 and
Python 3.12.16. They independently discover and execute the same 48 names with
`--no-tests=error`. Their locked SDL 2.32.10 input is commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. MIDI ON also verifies RtMidi 6.0.0 at
`1e5b49925aa60065db52de44c366d446a902547b`, its recorded prepared-source transform
and the ALSA compile definitions. Native X11/ALSA/PulseAudio backends are compiled;
the acceptance and relocation smoke use dummy audio/video drivers.

Each nine-method native calibration suite logs **10 actual subprocesses, seven
native lifecycles and two deliberately failed application replays**. The seven
scenarios cover identical Apply, changed calibration, changed route, changed
exact port, no-input then connect, failed reopen/retry and runtime fault/retry.
All nine methods pass. The probe SHA-256 is identical in both Release jobs:
`0ace48a7aee3de7ce1e19ae270c2a38c1ca05278e4f6864138916cb448046144`.
CTest times are **20.47 s ON / 20.40 s OFF**.

Both material JSON records report **1,293 checks, zero failures and 109 frames**,
including the original 901 checks, 170 header checks and A42's 222 modal checks.
All **212** clipped resampling differences belong to **38** intersected glyphs;
unexplained pixels and literal-plate mismatches are both zero. This is actual
execution of the expanded fixture at d8, preserving A42's original failures.

The install gate passes eight Python methods in each configuration. Subsequent
workflow output explicitly verifies **20 installed files ON / 16 OFF**, relocated
help and a **600 ms dummy smoke**, and exact archived bytes. Executed assertions
require callbacks/rendered frames, a written screenshot, unchanged musical-state
and installed-payload files, and quiescent closed/unavailable MIDI with no selected
physical port. The packages and diagnostics are uploaded under the exact source
identifier. These results are installation and dummy-driver qualification.

## Expanded native sanitizer qualification

The repaired GCC 13.3 Release build now executes all **21 unique required tests**.
Their actual names exactly match d8's frozen CTest-to-build-target map; native
calibration maps to `hammond_standalone_calibration_probe`, while the other twenty
names map to their same-named executable. The sixteen prior interface gates and
five added channel/calibration/product gates are retained. Discovery verifies
actual built commands, required timeouts and absence of sanitizer-policy
overrides, then CTest executes the exact anchored selection serially with
`--no-tests=error`.

Independent parsing of verbose compiler commands finds **260 distinct objects
across 27 targets: 196 SDL C objects and 64 project C++ objects**. Every command
contains `-fsanitize=address,undefined` and `-fno-omit-frame-pointer`; all **21
executable link commands** retain sanitizer linkage. The instrumented probe
compiles the real application entry through the fixture driver, plus actual
`MidiDevice.cpp` and `InstrumentView.cpp`. Its logged link command names all six
archives and `-lasan -lubsan`.

| Instrumented archive | Observed compiler commands |
| --- | ---: |
| `_sdl2/libSDL2.a` | 196 |
| `libhammond_core.a` | 25 |
| `apps/standalone/libhammond_standalone_support.a` | 7 |
| `apps/standalone/libhammond_standalone_drawing.a` | 1 |
| `apps/standalone/libhammond_standalone_audio.a` | 1 |
| `apps/standalone/libhammond_standalone_replay.a` | 1 |

The primary log records the executed instrumentation script: it requires
nonempty instrumented objects, the real driver/include ordering and source
groups, `nm -u` ASan **and** UBSan references in each of those six archives, and
`ldd` results containing both `libasan.so` and `libubsan.so` for all 21 binaries.
That step finishes before actual exact-21 discovery and execution. This is
corroborated by the verbose compile/link commands and completed tests, not only
by the job's status. System libraries are outside the rebuild.

The instrumented calibration probe is
`0fc8805dbb63ead64da7f9b8b81b4e9d960acf1a0028d9c86167124b11d4478a`.
Its log records nine passing methods, **10 subprocesses / seven lifecycles / two
intentional failed replays**, in **21.24 s CTest / 21.104 s Python**. The following
executed check matches that hash to the instrumentation inventory, requires all
seven exact scenario names and common assertions, and scans each retained
scenario's stderr for ASan, UBSan, LSan and `runtime error:` diagnostics. The final
success message follows those assertions. Both intended application failures
therefore remain distinguishable from sanitizer failures. No actual sanitizer
error appears in the primary log.

Instrumented material acceptance again reports **1,293/1,293 and 109 frames**
in **29.80 s**, with the same 212 explained pixels and zero unexplained/literal
mismatches. Product visual passes in **90.19 s**, inside the existing 240-second
sanitizer limit. These timings qualify the instrumented acceptance budgets, not
interactive frame rate. All source/dependency rechecks and diagnostics upload
then finish successfully.

The detailed `instrumentation.json`, per-binary `ldd` output and captured scenario
stderr reside in the uploaded artifact. A49 audits their executed fail-closed
checks and primary-log evidence; it does not claim a separate download or manual
review of every artifact byte. The retained receipt records log identities,
exact bounded excerpts, executed selections and observed assertion summaries.

## Independent full R4 receipt

The full-waveform job records the same d8 checkout, GCC 13.3.0, CMake 3.31.6 and
Python 3.12.16. Its **14 report-admission self-tests pass in 0.619 s**. The verbose
build then compiles and links the actual probe before invoking
`test_rotary_waveform_acceptance.py --mode full --probe ... --timeout-seconds 1500`.
The runner emits **`status: pass`, `mode: full`, `failures: []`**, with wall time
**722.029333257 s**, followed by successful completion of
`check_rotary_waveform_full` and artifact **14144010133**.

The emitted receipt is
`build-waveform/rotary-waveform/Release/full/full-20261115T023437.128607Z-809bf1ea/qualification.json`.
Source inspection verifies that a full pass requires native process success,
strict report admission, the selected independent Decimal cross-check, retained
static-grid admission and before/after source, build and executable stability.
The CTest waveform smoke remains a separate smaller workload. A49 observes the
full runner's successful primary summary and build-before-run evidence; it does
not claim an independent download or reanalysis of every detailed waveform
metric. Lifecycle/transaction, R5 audible policy, R6 integration/deadlines and
physical evidence retain the separate waveform owner's gates.

## Leak policy and retained failures

Both sanitizer jobs set `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and `LSAN_OPTIONS=exitcode=23`.
Exact-source inspection finds only the existing
`test_standalone_midi_backend_quarantine` override,
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`, for deliberately retained failed-close
contexts. That named test is included in the 155-test core job and excluded from
the focused 21-test native sanitizer selection. No new suppression or general
leak exception is present. The local ptrace-blocked sanitizer and empty-main
control remain blocked observations, independent of hosted evidence.

The original [d556 native sanitizer build failure](../development/2026-11-15-product-continuation/reports/d556-native-sanitizer-build-failure.json)
is preserved and was independently re-fetched from
[job 132664950656](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43665863538/job/132664950656).
GCC 13.3/O3 with instrumentation and warnings as errors rejected the test-only
RtMidi facade's singleton vector initializer assignment with
`-Werror=array-bounds`; the 21 tests did **not execute**. The exact d8 change uses
`clear()` and `push_back()` for the same API value. Warning and sanitizer policies
and production application sources are unchanged by that repair. The observed
21/21 pass qualifies d8 without rewriting the d556 failure.

Original b9 failures remain in the [integration review](PRODUCT_INTEGRATION_REVIEW.md):
Linux Release and core sanitizers exposed the installer ancestor-loop policy
defect; Windows core additionally exposed CRLF/LF comparison, and Windows native
had eight fixture setup failures inside its 47/48 CTest result. This Linux review
does not replace the independent Windows, macOS or VST3 audits.

## Boundaries and next gate

This worker performs read-only hosted/source inspection and writes only this
review, its short assignment note and bounded A49 reports. No local configure,
build, CTest, application run, workflow/source edit, commit or push occurs.

The next gate is publication and qualification of the accepted A46/A48 changes,
including their new product-record and plot-admission tests, followed by the
actual final-source and 60-worker closure gates. This audit does not transfer
d8 results to that later source. Dummy drivers and a substituted synchronous MIDI
dependency cannot establish physical devices, asynchronous OS-driver races,
callback deadlines, semantic accessibility, literal reference equality or
measured electrical/acoustic fidelity. R4 remains separately owned; R5/R6 and
the nominal dry Engine boundary are unchanged.

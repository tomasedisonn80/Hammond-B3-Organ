# Focused interface sanitizer qualification

**A41's original-limit local CTest gate is partial: 10 passes and three native
raster timeouts. Local leak checking is unqualified.** The complete run returned
8 in 171.50 seconds. No AddressSanitizer or UndefinedBehaviorSanitizer diagnostic
was reported. Three separately authorized, 240-second-bounded direct diagnostics
then completed all timed-out suites without assertion or sanitizer findings;
they do not replace the original failed gate. The [machine-readable result](../development/2026-11-14-interface-continuation/reports/a41-result.json)
retains exact commands, environments, source and executable identities.

## Coherent source and setup

The base is published `aea58bb85bc66a5feaff66a0b8a388e7c3f9e630`, with the frozen
A34 label/title, A36 status wording, A39 workflow and A40 test-portability overlay.
The [before-build snapshot](../development/2026-11-14-interface-continuation/reports/a41-source-before.json)
pins **354 inputs**, digest
`b4a1caa57a92b2caadb7c07d0c951de73b4ab86bbdde412bf5941a5a87c80b44`.
Every input matched after build and after CTest; all **114 protected files**
matched A12, and all thirteen executable hashes remained unchanged. The workflow
freeze was released to A43 only after the final check at 12:41:36 UTC. Subsequent
workflow work is a separately identified change.

One build, `/workspace/scratch/601951e27dc3/build-interface-asan`, reused the clean
pinned SDL2 **2.32.10** source at commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. Linux x86-64 used GCC **14.2.0**,
CMake/CTest **4.4.4**, Python **3.12.14**, Make **4.4.1** and glibc **2.41**.
Configuration took 31.99 seconds; the thirteen-target build took 259.66 seconds
with at most two build jobs. Its measured allocation is **374.02 MiB**; the
integrator requested retaining its reusable objects. No dependency was acquired
and neither existing shared build was modified.

Release, testing and native standalone were enabled; MIDI and VST3 were disabled.
`SDL_ALSA=OFF` retains the documented local header constraint.
`HAMMOND_ENABLE_SANITIZERS=ON` applies
`-fsanitize=address,undefined -fno-omit-frame-pointer` to project C++, with the
sanitizer link option. The identical `CMAKE_C_FLAGS` instruments SDL C.
[Object and linkage inspection](../development/2026-11-14-interface-continuation/reports/a41-instrumentation.json)
verified all **220 built translation units**: 20 core, 24 standalone and 176 SDL C.
All four static archives reference both sanitizer families, and all thirteen
executables require both runtimes. The other 75 configured units were not built;
system libraries were not instrumented.

## Actual execution and remaining boundary

The initial leak-enabled inspection acceptance probe failed at shutdown. Its
separate verbose diagnostic returned **23**: LeakSanitizer could not attach to
thread 6 (`errno 1`), failed to suspend threads and emitted its fatal ptrace hint.
[Both failures remain retained](../development/2026-11-14-interface-continuation/reports/a41-leak-runtime-diagnostic.json).
This is a runtime-environment blocker, not a detected leak or a leak pass.

The integrator then approved a distinct run with
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and `LSAN_OPTIONS=exitcode=23`.
Dummy video/audio and software-renderer variables were explicit. CTest used an
exact thirteen-name filter, `--no-tests=error`, verbose output and serial execution.
No source, assertion, warning policy or CTest deadline changed.

| Original CTest scope | Result | Seconds |
|---|---|---:|
| Eight SDK-free UI/inspection/geometry/continuity suites | 8 passed | 20.28 combined |
| `test_standalone_drawing` | Passed | 0.96 |
| `test_standalone_quad_drawing` | Passed | 0.05 |
| `test_standalone_workspace_raster` | Timeout | 60.03 |
| `test_standalone_scaled_view` | Timeout | 60.09 |
| `test_standalone_preset_raster` | Timeout | 30.06 |

The eight SDK-free names are `test_standalone_ui`, `test_standalone_preset_ui`,
`test_standalone_workspaces_author`, `test_standalone_workspace_acceptance`,
`test_standalone_projection`, `test_standalone_inspection_author`,
`test_standalone_inspection_acceptance` and `test_standalone_workspace_continuity`.
Their completed cases include 34 inspection rows with owned copies and malformed
input admission, 288 geometry layouts, 5,740 hidden-target rejections and 63
paired-session musical scores. The latter retained 719,289 frames and 1,662
presentation transitions with zero view commands. Drawing completed 298
full-target checks across 18,309,120 pixels; quad drawing completed seventeen.
The [full CTest log](../development/2026-11-14-interface-continuation/reports/a41-asan-ubsan.txt)
preserves these outputs and all three timeout failures.

Each direct diagnostic ran once, serially, with unchanged executable hashes,
assertions and leak-disabled environment:

| Direct diagnostic | Completed checks; failures=0 | Seconds |
|---|---|---:|
| Workspace raster | 150 frames; held/focus/front/occlusion/hidden-body matrix | 74.73 |
| Scaled view | 168 frames, 90 clips, 16 focus checks, 56 Service values | 172.51 |
| Preset raster | 192 labels/focus, 160 glyphs, 752 isolation, 96 state cases | 128.68 |

All returned zero with no ASan/UBSan diagnostics. These observed durations
support a separately declared instrumentation budget; they establish no physical
deadline. Full commands and output remain in the three `a41-direct-*` records.

Native tests use `SDL_Init(0)` and bounded software surfaces, at most 1920×1400
physical pixels. The application/main executable and wall-time Python suites
were not built or run; A36's wording is source-pinned only. These observations
establish no physical devices, display/pointer capture, native accessibility,
callback deadlines, other platforms or acoustic fidelity.

## Next step

A43 owns a hosted, source-identified native ASan/UBSan/leak job. The integrator
used these measurements to add subsequent sanitizer-only limits of 180/360/300
seconds for workspace/scaled/preset raster, preserving normal 60/60/30 limits.
That later CMake/workflow change is recorded separately in the
[final identity check](../development/2026-11-14-interface-continuation/reports/a41-final-identity.json);
A41 did not reconfigure or rerun against it. The reusable build is released for
root's property inspection. Observe the hosted leak-enabled execution before
declaring that boundary closed; no hosted result is claimed here.

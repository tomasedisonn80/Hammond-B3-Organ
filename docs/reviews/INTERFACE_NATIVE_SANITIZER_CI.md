# Native interface sanitizer CI — A43

Assignment 43/60, logical wave 8, actual worker
`/root/w08_a43_native_leak_ci`. This adds one focused Linux job to
`.github/workflows/standalone.yml`; hosted execution and leak qualification are
**pending**. The [machine inventory](../development/2026-11-14-interface-continuation/reports/a43-native-sanitizer-ci.json)
records the workflow, source mappings, validation and remaining observations.

## Why this job is needed

A41 built the selected project C++ and pinned SDL C with ASan/UBSan. Its
[leak-enabled diagnostic](../development/2026-11-14-interface-continuation/reports/a41-leak-runtime-diagnostic.json)
exited 23: the retained log reports a failed thread attachment with `errno 1`
and LeakSanitizer's ptrace limitation. Root separately authorized
`detect_leaks=0` locally. That run retained ten passes and three raster timeouts
at the original 60/60/30-second limits; it establishes neither a complete
13-suite pass nor a leak pass. The existing untraced Ubuntu CI runner is the
appropriate next place to execute the missing leak checks.

A41 explicitly released the workflow freeze after its final 354-input,
114-protected-file comparison at `2026-11-14T12:41:36Z`; source digest
`b4a1caa57a92b2caadb7c07d0c951de73b4ab86bbdde412bf5941a5a87c80b44`.
Root then staged A39's original workflow separately before A43 appended the job.

## Scope and instrumentation

`native-sanitizers` runs on `ubuntu-24.04`, with a 20-minute job ceiling,
Release configuration, native support enabled, MIDI/VST3 disabled, and two build
workers. It reuses the existing pinned actions, SDL acquisition/verification and
Ubuntu development-package list. SDL's normal ALSA detection remains enabled;
the local header workaround is not applied to this hosted toolchain.

| Compiled inputs | Instrumentation and link path |
| --- | --- |
| Project core, support, drawing and thirteen selected test targets | `HAMMOND_ENABLE_SANITIZERS=ON` applies ASan/UBSan and frame pointers through `hammond_configure_target`; public link options carry the runtimes. |
| Pinned static SDL2 C sources | `CMAKE_C_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer` instruments SDL's separate C targets. |
| `InstrumentView.cpp` and `UiModel.cpp` | The three raster targets compile InstrumentView; the shared support library compiles UiModel. Both use the project sanitizer helper. |

The job checks the selected compile commands and actual nonempty objects,
sanitizer references in SDL/core/support/drawing archives, and link flags plus
both dynamic runtimes for every selected executable. It records hashes and
compiler/configuration logs. External system libraries are not rebuilt.

Only these `test_standalone_` targets are built and selected: `ui`, `preset_ui`,
`workspaces_author`, `workspace_acceptance`, `projection`, `inspection_author`,
`inspection_acceptance`, `workspace_continuity`, `drawing`, `quad_drawing`,
`workspace_raster`, `scaled_view`, and `preset_raster`. An anchored filter must
discover exactly that thirteen-name set without duplicates or absent executable
commands. Tests that override the job's sanitizer environment are rejected.

CTest runs serially with `--no-tests=error`, dummy SDL drivers and software
rendering. `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and `LSAN_OPTIONS=exitcode=23`
match the existing sanitizer policy. Root is reviewing A41's separately bounded
direct raster diagnostics before deciding whether explicitly sanitizer-only
CTest allowances are necessary. Original Release deadlines remain preserved.

## Root integration after the independent measurements

A41 subsequently completed all three unchanged raster executables in separate
bounded runs with leak checking disabled only for the retained local runtime
restriction. Workspace raster took 74.730474 seconds, scaled view 172.510959,
and preset raster 128.676768; every assertion completed without ASan/UBSan
diagnostics. The original ten-pass/three-timeout CTest result remains unchanged.

Root added explicitly sanitizer-only CTest limits of **180 / 360 / 300 seconds**
for those three suites, respectively. Ordinary Release limits remain **60 / 60 /
30 seconds**. This gives the observed fully instrumented workload bounded room
without changing a test assertion, frame inventory or application deadline. The
new job verifies those configured limits during exact thirteen-test discovery.
The memory-checking job does not qualify rendering performance. Root's static
recheck is retained separately in `reports/root-a43-static-recheck.json`; its
workflow/source identity supersedes the initial A43 static snapshot for publication.
Root’s [configured-property check](../development/2026-11-14-interface-continuation/reports/root-sanitizer-budgets.json)
passes with unchanged binaries; A44 confirms the ordinary deadlines in both
Release configurations. Hosted execution remains the separate A48/A58 gate.

## Validation and acceptance boundary

Static checks parse all three workflows, 36 Bash blocks and 12 embedded Python
blocks. Existing CMake registrations and A41's retained configured discovery
contain the exact thirteen targets. The entire preexisting standalone workflow
prefix remains byte-identical to A39 SHA-256
`527d1cdb692cd5d837f0436ee68b2026878b10c5db1553459ca623060e4c1d34`:
four Release rows, 21 required names, 15/19-file packages, deadlines and artifact
rules are intact. The new job brings the expanded hosted inventory from eleven
to twelve. A43 performed no configure, build, test execution, dispatch, index
update or commit.

Diagnostics upload on success or failure, including provenance, dependency
verification, instrumentation, discovery, verbose CTest output, JUnit and CTest
failure logs. Root publishes the reviewed source. A48/A58 must observe its exact
commit, successful instrumentation checks and all thirteen leak-enabled passes,
then retain the job identity and artifact before closing leak qualification.
Timeouts and sanitizer findings remain failures. This focused gate does not
qualify application/Python timing suites, physical devices, native accessibility,
VST3, reference equality, measured sound or signed release.

Reproduce static inspection from the repository root:

```sh
python3 docs/development/2026-11-14-interface-continuation/reports/a43-verify-ci.py
```

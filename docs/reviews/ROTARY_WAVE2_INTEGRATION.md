# Rotary wave-2 coherent integration

## Frozen scope and identity

On 13 November 2026, the integrator staged only accepted wave-2 files and shared
records. `git write-tree` returned
`b4bf3bf65ef6706f2c613f875d759f9d71431d1f`. A fresh archive of that exact tree
was extracted to `/workspace/scratch/c9f9d8cb3889/w2-source`; build outputs went
to the separate `w2-build` directory. Active wave-3 geometry, delay, probes and
tests were excluded. The snapshot records 12 complete and three then-running
assignments; later completion is recorded in the next checkpoint.

The code includes the frozen contract/types, proposed fixture/schema/validator,
independent reference, native motion primitive and independent profile/reference
regression. This report and the corresponding shared-result paragraphs were
added after execution; no compiled code, fixtures, tests or build inputs changed
between the tested tree and its documentation supplement.

## Executed commands and outcome

Working directory for source checks: the frozen archive above. The successful
build used GCC **14.2.0**, CMake **4.4.4**, Ninja
**1.13.2.git.kitware.jobserver-pipe-1**, Python **3.12.14**, and default SDK-free
Release configuration. The initial bare `cmake` command exited 127 because this
workspace does not put the available build tools on PATH; the explicit PATH
below corrected setup before any project configure occurred.

```sh
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake -S /workspace/scratch/c9f9d8cb3889/w2-source -B /workspace/scratch/c9f9d8cb3889/w2-build -G Ninja -DCMAKE_BUILD_TYPE=Release
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake --build /workspace/scratch/c9f9d8cb3889/w2-build -j 6
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH ctest --test-dir /workspace/scratch/c9f9d8cb3889/w2-build --output-on-failure --no-tests=error -j 4
python3 tools/check_repository.py --json
python3 tools/check_rotary_session.py --repo . --expected-complete 12 --json
```

Configure and strict build passed. **81/81 CTest suites passed in 38.03 seconds**,
zero failed or disabled tests. Both new Python suites executed 33 methods each.
Repository integrity passed with zero errors: unchanged 500-page PDF, 80-chapter
index and 2,398 local links across 394 Markdown files. Its older agent-note count is
historical and is not this session's participation evidence. The separate rotary
checker passed: 12 complete, 3 running, 45 planned, 15 distinct actual identities and
completed waves 1 and 2. It checks retained consistency, not external dispatch.

The separate optional schema audit passed 358 cases before this coherent build;
its dependency and repaired control-character patterns are recorded in
[assignment 11](../development/2026-11-13-rotary/11-profile-tests.md).
The independent reference initially failed valid full-epoch decay cases. The
unmodified regressions passed after the state-exponent repair, as recorded in
[assignment 12](../development/2026-11-13-rotary/12-reference-tests.md).

## Limits and next gate

This is numerical/admission foundation and compatibility evidence. Native motion
has author checks, but full independent R2 acceptance is still active. R3
propagation and R4 history/rendering, R5 audible policy, R6 actual renderer runtime,
physical M7 capture/fidelity and Engine/native integration remain separate.
There is no new host/device or Windows/macOS execution claim here. The existing
dry Engine, 45 controls, saved-state formats and plugin identities are unchanged.

Next accept the independent motion grid, historical path solver and bounded
waveform history, then implement a dual-rotor transactional renderer and compare
actual outputs with an independent same-cubic reference. Preserve the scanner
and standalone tracks and the unresolved M5/M6 physical/electrical inputs.
Publication must verify exact remote tree identity and an expected-head update;
its observed commit is added by the following dated record.

## Concurrent standalone integration before publication

Before publishing, `main` advanced to
`219821dfaca6bfee8ba0905993ed8deec7a66396`, the independent standalone runtime,
installation, replay helper and workflow checkpoint. The integrator inspected
its 65 changed paths, merged it without conflicts and preserved both tracks.
A new coherent staged tree `1d78b5663b30cb48984e6b810ed33ede4894ced8` was
archived to `/workspace/scratch/c9f9d8cb3889/w2-merged-source` and built in
`w2-merged-build` with the same Release toolchain and commands above, substituting
those two directory names. No unfinished rotary worker file entered the archive.

The combined strict build passed. **85/85 CTest suites passed in 38.91 seconds**,
zero failures or disabled tests, including the four newly available portable
standalone suites. Repository integrity again passed with zero errors and
2,506 local links across 426 Markdown files. The explicit 12-complete rotary
snapshot check also passed. Optional SDL2/VST3 builds and physical devices were
not run in this gate. This section and the associated shared result paragraphs
are a documentation supplement to that exact tested source tree.

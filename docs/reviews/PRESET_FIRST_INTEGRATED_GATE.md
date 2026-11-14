# First coherent preset integration gate

A31 (`/root/w06_a31_integrated_gate`) qualified one copied Linux Release source
with the core, native standalone, MIDI and VST3 enabled together. The original
complete run passed **141/143 CTest suites in 385.91 seconds**. It exposed one
stale legacy test-array size and one broken installed-guide link. After the two
reviewed corrections, **both affected suites passed in 7.63 seconds**. This is
an original full run plus an affected recheck, not a claimed final single
143/143 execution. No production algorithm changed for either correction.

The [machine record](../development/2026-11-14-preset-continuation/reports/a31-integrated-gate.json)
contains commands, dependencies, every suite's result/time, artifact hashes,
source deltas and retained evidence. The [execution note](../development/2026-11-14-preset-continuation/31-integrated-gate.md)
gives the exact working directories and handoff.

## Source, build and test scope

Copied **1,287** tracked/untracked nonignored files after A28 confirmed executable
and test stability. Every copied file matched the live bytes immediately after
copying; subsequent live work could not change this build. Checkout context was
`35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`. That published baseline does not identify
the uncommitted preset overlay. The complete original source manifest is
`1f805c9257e2843c8ac1345938ff28603e2780e93831f0e2c02c907cc420ac8b`.

GNU C++ **14.2.0**, CMake/CTest **4.4.4**, Python **3.12.14**, Unix Makefiles and
repository strict warnings built the fresh combined tree. Configuration passed
in 20.44 seconds; all ordinary targets and both native test-input aggregates
built in 118.13 seconds. Pinned SDL 2.32.10, RtMidi 6.0.0 and the VST3 SDK were
verified. RtMidi uses ALSA; SDL's ALSA audio driver is disabled locally. Windowed
acceptance explicitly uses dummy audio/video and software rendering.

Discovery found exactly **143 suites**: 45 other core C++ tests, 63 root Python
suites, 27 `test_standalone_` suites and eight native VST3/validator/install
suites. CTest ran serially to avoid concurrent wall-clock native replay load.
No CTest suite was skipped. The audio-admission Python suite retained two
in-method capability skips for native Windows-reparse and Unix-domain-socket
fixtures; its unverbose progress does not print the precise native socket error.

The native selector workflow, saved-control migrations, all 24 preset keys,
independent UI geometry, raster focus repair, concurrent Session publication,
parameter boundaries, core/offline behavior and all eight VST3 suites passed
in the original complete run. The existing scanner tests retain their declared
numerical outcomes; a passing software suite does not clear the separate G5
same-hertz failure.

## Two observed integration repairs

**Retained realtime fixture.** `test_realtime_console` failed at its checked
fixture count before exercising that workload. Its original manual score emits
45 controls, but its array lengths used the now-47 `kParameterCount`. The repair
names `legacy_control_count = 45`, guards the current two-parameter append, and
uses that count only for the retained control/combined arrays. Original event
values and ordering remain unchanged. The separate registry allocation probe
still covers all 47 descriptors; A26 supplies independent selector-specific
realtime acceptance. No failed assertion was removed or weakened.

**Installed documentation.** Seven of eight installation methods passed; the
actual relocated component method correctly rejected a relative
`PRESET_NATIVE_WORKFLOWS.md` link in installed `STANDALONE_APP.md`, because that
repository-only contract was absent from the component. The repair changes that
one link to its absolute repository URL. The installed-link assertion remains.
The corrected suite passes all eight methods and the actual **17-file** MIDI-on
payload, including relocated schema-3 dummy-driver smoke. A36's planned addition
of the current preset runbook is a later package change, not part of this count.

The integrator authorized both narrow corrections. The completed original source
was then changed in exactly those two files. Only
`tests/test_realtime_console.cpp` was compiled; no core, standalone or plug-in
translation unit rebuilt. Corrected source-manifest SHA-256:
`db1001d3ab1b506c205aed06a347d2279d6aea0afa6f72b59949cf13e57eb8e5`.
The original transcript, both patches and corrected transcript/JUnit remain
retained. The corrected installer independently reports the same standalone
executable hash as the original gate.

## Counts and artifact identities

The SDK build-time selftest reports **51/51**. The separate plug-in validator
reports **47 internal checks passed / 0 counted failures**, with **16** teardown
diagnostics retained. These are distinct from the plug-in's **47 public
parameters**. [A29's exact-SDK review](PRESET_VST3_ACCEPTANCE.md) explains the
baseline-identical teardown/rate diagnostics and their limits. The newly built
module and metadata are byte-identical to A22's identified native result.

| Artifact | SHA-256 |
| --- | --- |
| Standalone executable | `8ced1de1771b98c938a84149055437b3807c393c7ecd8048d335979a3d3fc89a` |
| Offline renderer | `1f41ef4a9023c31228f86d851ae3220f1d1d78d48707b54875a6249949904730` |
| Native VST3 module | `36d02646e039d0748a2f01aa9e89dda07c5be816a3ab040b40ae694faad9889e` |
| Native module metadata | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| Immutable fixed-registration header | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Later source and remaining gates

A32 subsequently repaired stale Python bytecode admission in the fixed-data
build generator. That repair is outside this copied source. A32 independently
executed valid-output comparison and confirmed that **all 2,099 generated bytes**
match this build's header/hash above. Its admission regressions qualify that
later generator delta; this original runtime gate is not relabelled as a run of
later source. Likewise, subsequent gallery/README, CI and package changes retain
their own affected acceptance.

This is Linux Release engineering evidence. It is not a sanitizer, macOS,
Windows, DAW, physical MIDI/audio, callback-deadline, semantic-accessibility or
literal 1:1 visual result. The retained hosted macOS modal timeout remains
unclassified until a new actual hosted run supplies its diagnostic predicates.
Physical preset loading/latching, scanner/AO-28/Leslie integration and measured
instrument fidelity retain their separate dependencies.

A final read-only evidence-summary call encountered an exec-server disconnect
after both gates completed. The following read succeeded; no test was rerun for
that infrastructure event. Source/build directories remain available for read-only
use by later capture/compatibility consumers; neither preserved baseline build was
reconfigured. Root owns publication and the final coherent session gate.

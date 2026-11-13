# Standalone combined-source checkpoint through assignment 41

Root integration evidence, 2026-11-13. This record accepts the first 41 actual
assignments in the [standalone session](../development/2026-11-13-next-phases/README.md).
Six complete waves and five assignments of wave 7 are accepted. The next three
dispatched assignments cover native sanitizers and output-removal handling;
their running status is not a completed result. Other active sessions are not
included in this count.

## Exact frozen qualification

The immutable archive at local commit
`387275289410d12af27cf235d6e45fd91f29bafa`, tree
`0d6da163edd6531338938e12e0d393841d569a80`, incorporates remote rotary foundation
`38c1fac` and calibration scope `08fa8de`. It contains accepted work through 36
and the assignment-37 replay production repair/regression; the later exporter,
its tests and reports are separately qualified below. No live headers were
linked to an earlier library. A fresh native Release configure, full build and
CTest run passed **94/94 suites**, zero failures, in **98.80 seconds**.

Environment: Linux x86-64, GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14,
Make 4.4.1. VST3 was OFF, native standalone ON, testing ON. SDL 2.32.10 source
at `5d249570393f7a37e037abf22cd6012a4cc56a71` was verified separately. The
executed audio/video tests explicitly selected dummy transports; this container
does not provide the development inputs for ALSA/Pulse/X11/Wayland.

From the repository root, the equivalent single-configuration commands were:

```sh
git archive 387275289410d12af27cf235d6e45fd91f29bafa | tar -x -C ../checkpoint-w6-source
cmake -S ../checkpoint-w6-source -B ../build-w6-frozen \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT="$PWD/../SDL2"
cmake --build ../build-w6-frozen --parallel 2
ctest --test-dir ../build-w6-frozen --output-on-failure --no-tests=error --parallel 2
```

The source directory was created empty before extraction. The session's CMake
executable is under `/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/`.
The commands above use ordinary `cmake`/`ctest` names for portable reproduction.

| Retained artifact | SHA-256 |
| --- | --- |
| Fresh configure log | `faac8b4b05236a0ea0504c7fe76dc35bbe9877f9737b24ccb0c06893e7a86d40` |
| Full build log | `d07110571c1db3a1c712fafc84432f4d72cf670e48c42bf7c5d719ceea36d9cc` |
| Full CTest log | `995f305a137497a3b431a59ecd95212265c1384b69306614c01c2bb6c5e577c5` |
| Actual native executable | `7377e8c2c146636ef3b4ca28891d257bbfcc9db8b6f42caa257b6857d97d9925` |
| Benchmark executable | `0c97a79e8c49dbad961090727fe3ae1668a283bdc4d87f4d334fc9c604981f19` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Compiled chapel catalog, 4,837 bytes | `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91` |

The benchmark's generated manifest automatically expanded from 54 to 57 inputs
with the additive rotary source and two public headers. Its resulting source
fingerprint is `5fd7837b44dbe8fd09bfbd9931c20065e29acfffee10f3adca1a622cb18b9bb8`.
Those additions do not connect rotary processing to the dry Engine or application.

## New behavior and independent follow-up

The [replay boundary repair](../STANDALONE_REPLAY_BOUNDARIES.md) follows an actual
valid 256-resize script timing out after only 133 events. The main loop now
explicitly pumps SDL and drains the bounded public event queue, preserving the
256-event budget and two-second grace. The same maximum script completed in
0.319 seconds; nine maintained methods cover 29 app runs. The complete app,
workflow and boundary subset passed 3/3 in 22.80 seconds with 38 methods and
208 actual application invocations. No musical oracle was weakened.

The [chapel exporter](../CHAPEL_CONTROLS.md) copies documentary tap digits into
ordinary B3CONTROLS3 files. Assignment 39 independently passed 15 SDK-free
methods, 270 CLI calls, 205 exact-state cases, 264 API rejects and six publication
fault/race probes. Its native suite passed two methods and 20 actual app runs,
covering all eighteen registrations and two pairs. Save acceptance requires
observed successful status and rewrites accepted `0.1` input to canonical
`0.10000000000000001`; unchanged canonical input alone is not the oracle.

After adding the native CMake registration, root rebuilt the complete native
input target and executed this separate focused gate against the assembled
working source:

```sh
cmake --build ../build-native-app --target hammond_standalone_test_inputs --parallel 2
ctest --test-dir ../build-native-app \
  -R '^(python_test_chapel_controls|test_standalone_chapel)$' \
  --no-tests=error --output-on-failure --parallel 2
```

Both CTest suites passed: SDK-free 18.21 seconds, native 17.80 seconds, total
**18.22 seconds**. The app hash remained exactly the frozen value above. This
94-suite full gate plus later two-suite focus is **not** a claimed 96-suite run.
The exporter and exact test identities are in [assignment 39](../development/2026-11-13-next-phases/39-chapel-controls-acceptance.md).

## Retained visual and hosted evidence

Assignment 40's [four actual SDL backbuffers](STANDALONE_WINDOW_DEMO.md) use the
frozen executable above, with unchanged diagnostic JSON, scripts and provenance.
Root also inspected all four PNGs: reference/minimum keyboards, Help and Audio
states fit without observed clipping or overlap. Compact minimum-size labels
still need real-display usability review. These are software backbuffers, not
physical desktop or accessibility evidence.

Assignment 41 [downloaded and ran the actual Linux CI package](STANDALONE_HOSTED_LINUX_ARTIFACT.md)
from published `219821d`. Both ZIPs match GitHub digests, all nine installed files
match the inventory, and the actual ELF passes relocation and dummy smoke. Its
runtime needs GLIBC 2.38 and GLIBCXX 3.4.32. The archived nine CTest suites passed;
the state suite's internal unrun POSIX replacement-failure case remains explicit.
That older binary does not contain the later integrated replay CLI.

The [Windows/macOS test portability repairs](STANDALONE_PORTABILITY_REPAIR.md)
pass four local suites. Actual hosted reruns are still required. Physical audio,
hotplug, deadlines, high-DPI, screen readers, musician workflow, signing, project
rights and measured fidelity remain separate gates. Factory Table IV and loaded
preset gains are not established by the documentary exporter. Follow the
[handoff](../STANDALONE_HANDOFF.md) and current manifest for the next work.

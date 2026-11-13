# Assignment 24 — native executable acceptance

- Actual agent: `/root/w04_a24_app_acceptance`, wave 4 of the independent
  2026-11-13 next-phases sixty-assignment session; no earlier work is recounted.
- Owned: `apps/standalone/native_tests/test_standalone_app.py`,
  `docs/STANDALONE_APP_ACCEPTANCE.md`, and this report. Root owns all production
  sources, CMake, shared records and publication. No production edits or commits.
- Inspected HEAD: `738162f0bc36f88f8c76268d04831862a8118d10`, tree
  `915e55dc7c3ad022042b188498aa41f2a7f40795`. Concurrent work was preserved.
- Read AGENTS, current scope/handoffs/plan, product/closure reviews, main/app
  contract, assignment 18, state grammar and callback/Session implementation.

## Implemented evidence boundary

Python standard-library acceptance requires the actual executable. Subprocesses
set dummy audio/video (or the deliberate invalid driver), explicit private state
paths and temporary working directories. No default preferences, optional-binary
skip or production test double. Subprocess limits are 3/8 seconds; root added
native-only CTest `test_standalone_app` with a 60-second timeout.

Eighteen methods execute 164 application subprocesses: 3 help/list cases,
129 CLI rejections, 8 successful 600 ms smokes, 3 expected runtime failures and
21 filesystem admission failures. Four actual smoke configurations cover
1280×900 and 960×700 at default 48000/512, plus 44100/2048 and 96000/128;
the device suite retains responsibility for the full 15-pair matrix.

Strict JSON checks every schema/type, nominal identity/control, native format,
requested/obtained fields and coherent callback/frame/clock/publication/sequence/
discard counters. Runs observe On/held/Off, open/running before close, stopped
and no held state afterward. BMP structure/dimensions/nonblank pixels and
while-held capture are checked without exact bytes or callback counts.

Literal v1/v2/v3 controls migrate through actual startup, using Unicode/spaces
and a silent cancelled upper manual. Late malformed input reports its error,
preserves bytes and retains the complete audition fallback. Exit never saves.
No-audio has zero callback/frame claims; failed writes preserve musical files.

## Reproduced defects and root-owned repair

At original main `6b3e5b13dc362495f0bd224a3a046a1129652385faa4d20804a03edd162d6f78`
and binary `aa03875c8631337f4b42c9989b7877b2b5bc861891df187ec97c6e402c67abf6`,
an actual private probe used `alias parent -> real parent`, absent state
`real parent/fresh controls.b3controls`, and diagnostics at the alias of that
same leaf. The 600 ms smoke returned 0 with 58 callbacks and created JSON at
the musical-state path. Reported to root before any production change.

Root added `weakly_canonical` and output-symlink rejection. At interim main
`a10173c9b57434f7128c48628ce4c4cc467c9bc3618f0ec31884639ae9194698`, binary
`648c8168e1d242f813d5ea333898aab4854c3979c82631a6a9fed91a50155078`, a second
private probe found the reverse alias: dangling state symlink to absent
diagnostics target. Exit 0 / 60 callbacks / 30,720 frames again created JSON at
the musical path. Root now rejects symbolic-link leaves on all three paths;
ordinary parent aliases remain allowed and compared after resolution.
Regressions cover both directions, valid state-symlink rejection, three parent
alias pairs, nine existing collision pairs and directory outputs. They exercise
a stable private filesystem, without claiming race-resistant security.

## Executed checks, 2026-11-13

Linux, GCC 14.2.0, C++20 Release, CMake 4.4.4, Python 3.12.14; locked SDL2
2.32.10 at `5d249570393f7a37e037abf22cd6012a4cc56a71`. Build root:
`/workspace/scratch/5ba97739b54c/build-native-app`; repository working directory:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

```sh
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5ba97739b54c/build-native-app/apps/standalone/hammond_standalone \
  python3 apps/standalone/native_tests/test_standalone_app.py
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest \
  --test-dir ../build-native-app -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_app$' -V
```

First direct execution passed 17/17 methods, 161 subprocesses in 8.444 seconds.
Interim CTest passed 17/17 in 8.464 seconds; the additional probe above exposed
the missing symmetric case. Final CTest passed 1/1 in 9.03 seconds: **18/18
methods, 164 subprocesses in 8.870 seconds**, zero skips, on the final hashes.
Separate prerequisite probes confirm missing environment and missing executable
both fail setup. Linux exercised real hardlinks, parent and leaf symlinks.

Repaired main SHA-256:
`fd7095bde479c4acf3079f0972d6f907034f546a6a1d1cef398caad92eb0b212`.
Tested executable SHA-256:
`f820e7a619be733cd72ac9c3e0a12f2c5391518897608934cf055f94e9c03ce9`.
Final test-source SHA-256:
`0c2074b195ab17bba3b9e7d26572a7dc015a7061d60ee28f9686b0c951c179fc`.

## Remaining gates and handoff

Root owns coherent frozen-tree integration/publication; these are exact runtime
hashes from the coordinated live worktree. Native events beyond the single
smoke note, modal navigation, pointer/focus/resize/capture, explicit Save/Load,
reopen/hotplug/watchdog, visible desktop/high-DPI, physical audio and latency/
xruns, accessibility and Windows/macOS execution remain separate gates.
Windows has a required junction fallback for parent aliases; unavailable file
symlink privilege is explicitly reported as unexecuted dangling-file coverage.
No native-device, physical-fidelity, distribution or signing pass is claimed.

# Assignment 44 — independent device-removal acceptance

Actual agent `/root/w08_a44_audio_removal_acceptance`, wave 8, assignment 44 of
this session's sixty. A tool-host inventory interruption resumed this same
identity; it did not create an extra counted assignment. Owned only the native
test, [acceptance guide](../../STANDALONE_DEVICE_REMOVAL_ACCEPTANCE.md) and this
note. No production, CMake, shared status/ledger or commit changes were made.

Read AGENTS, current standalone scope/model/handoff/status/next steps, the plan,
source review and atlas chapter 064 (pp. 391–396) plus M9 p. 450. Inspected the
pinned SDL event declarations, removal implementation and close/ID-reuse
contract. The user-requested complete atlas reading belongs to assignments 1–6;
this assignment claims only its relevant-source review.

## Coherent qualification source

Published base: `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`. An immutable `git archive` was extracted
to `/workspace/scratch/5ba97739b54c/a44-source`, then overlaid with assignment 43's
frozen AudioDevice header/implementation and main, plus this new test. Only that
private copy received temporary CMake registration. Root separately registered
the maintained target in the shared repository.

All **831 frozen source files** were hashed before build and unchanged afterward.
The four overlays also still matched shared source after the test. Core, support,
adapter, SDL and test were built together in the new private `a44-build`; no stale
library was linked against a different live header. Main was retained/inspected
in the source freeze but is not compiled into this test executable.

| Input or artifact | SHA-256 |
| --- | --- |
| Maintained test, 450 lines | `4d69f220a6308f8a2166e4081abea0ae67183082f8b9724257c45a93c85ee3cd` |
| AudioDevice header | `75ac25e462afb85c64b0298bf4e8c30d4979d3d30f231edec75c8ba41818673a` |
| AudioDevice implementation | `3565139241941d108b18289b176f25732e0c9bf4d36a60844a297ba92499f2b0` |
| Main source, inspected | `3190e9a3f4a4c156f6d54ae7ddc7efa675a99d86cf2703a57af2badd443e9dbe` |
| Test executable | `586cb4d1024bb2c615e31df817f4bbcabdb53ae6ab47be30db15b82115cc2900` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| SDL static library | `34c9ffb7b608a0a38294d97d06852b4f36f81a419fb5dc2e3b0bb0f92e690e85` |
| Frozen input manifest | `71ac358e878107e99c840a2f766e04791779b9b19593d6449d82c9ed71d95401` |
| CTest verbose log | `cc762adbd56958206d83f58b6f663a4d50333090bd0910d3b5dddc0f1dda113a` |

Host: Linux x86-64, GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14, Release.
The clean SDL 2.32.10 source remained at commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. Actual test compile flags include
`-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
-Wshadow -Werror`; link inputs were the newly built adapter/support/core/SDL
libraries, `libm` and pthread. No sanitizer result is implied.

## Actual command and result

With CMake and CTest from
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin`
and working directory `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`:

```sh
cmake -S ../a44-source -B ../a44-build -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2
cmake --build ../a44-build --target test_standalone_device_removal --parallel 2
ctest --test-dir ../a44-build -R '^test_standalone_device_removal$' \
  --no-tests=error --output-on-failure -V
```

Configure, strict build and first execution all exited 0. CTest reports **1/1
passed**, zero failures/skips, 0.22 seconds for the case and **0.23 seconds total**.
Observed: **3 lifecycle cycles, 93 queued events, 78 ignored events, 10 matching
pure queries, 3 matched joined closes, 10 rejected opens, 2 reused IDs, 12 actual
callbacks and 3,584 rendered frames**. No assertion, fixture or producer changes
were required after this first successful execution.

Literal fixtures cover zero/unrelated output removal, capture flags 1/2/255,
added events, current matching IDs, paused/running/closed states and failed opens.
Actual status, coherent acknowledgments, exact manual/pedal holds, retained
controls, positive finite peaks, zero fault counters, joined cleanup and exact
callback/frame/clock accounting supply behavioral oracles. Both non-UI channels
are released by final close. Quiet observations prove no further callback
progress during their bounded intervals, not a hardware scheduling guarantee.

Scratch records are `../a44-frozen-inputs.json`, `../a44-configure.log`,
`../a44-build.log`, `../a44-tests.log` and the frozen source/build. Configure log
SHA-256 is `467f24d29ae0bb7fedbb1fed6567cd5895915b6883e2c6d6d3823db253c2321c`;
build log is `ca04f9ec0cfc77e5af7fdb377aaacef2cd4474573904790ad800683d3201ed9c`.
The maintained source and this note retain the result if scratch is later lost.

## Integration and next evidence

Root received the passing test identity and target recipe: link the actual audio
library, include `tests`, supply `SDL_MAIN_HANDLED`/profile/source definitions,
depend on the generated profile and select explicit dummy audio with a 15-second
timeout. Root owns canonical integration, shared records and commit/push.

The predicate was checked through SDL's public event queue with an independent
small routing fixture. Main's outer REMOVED guard and unchanged cleanup path
were source-inspected; this test does not execute the whole application handler.
Assignment 43 retains its separate application probe, including original failures.
No physical disconnect, successful reconnect, other OS, callback deadline,
latency, accessibility or fidelity result follows. Next acquire real desktop/audio
devices, repeat unrelated/current removal and explicit reopen while notes are
held, and retain per-platform logs with no stuck notes and preserved controls.

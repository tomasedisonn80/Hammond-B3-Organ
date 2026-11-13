# Assignment 27 — independent replay acceptance

Actual worker: `/root/w05_a27_replay_acceptance`; standalone wave 5, assignment
27 of this session's requested sixty. Owned only
`apps/standalone/native_tests/test_standalone_input_replay.cpp`,
`docs/STANDALONE_REPLAY_ACCEPTANCE.md`, and this note. No commits, production
changes or repository CMake edits were made by this worker.

## Basis and contract

Read AGENTS, active standalone scope/status/next steps, the current session,
plan/atlas evidence boundaries and relevant M9 review; inspected the frozen
public header before authoring independent literals. Agent 26 clarified exact
grammar and observable resize-marker semantics before those expectations were
written. The public contract requires mutable-plan validation at initialize;
it is tested, not treated as a caller precondition. Marker acknowledgment is
queue consumption only. The header/source were frozen before execution.

Starting repository HEAD: `738162f0bc36f88f8c76268d04831862a8118d10`, tree
`915e55dc7c3ad022042b188498aa41f2a7f40795`, with concurrent unfinished changes.
These helper-file hashes identify the tested work beyond that baseline:

| File/input | SHA-256 |
| --- | --- |
| `ScriptedInput.h` | `294b11d6a2c9b425d766b019b2ff1e7c460a308c93887c648dd7bce1d955c3d5` |
| `ScriptedInput.cpp` | `ed6987b1b134737842028e611ed5f03ea67e9b232984284d885ca2c29d27809e` |
| `test_standalone_input_replay.cpp` | `42564eff6d7c5c9c296079ec593fc26c340415af518b366efea5752996b110af` |
| External `sdl2-build/libSDL2.a` | `34c9ffb7b608a0a38294d97d06852b4f36f81a419fb5dc2e3b0bb0f92e690e85` |
| Direct GCC test executable | `6cbadcb03f23d54bf8c70118b39ca23c3be713fccb068d3f7863ddf33a0cedd4` |
| CMake Release test executable | `6c99ba215ef55eabcf921bf6b29592c91ed60bc0d759ab8b5e3c39e3165626a0` |

SDL2 is the existing locked 2.32.10 source at
`5d249570393f7a37e037abf22cd6012a4cc56a71`; no acquisition or new dependency.
Compiler: GCC 14.2.0; CMake/CTest: 4.4.4; Linux; explicit dummy video.

## Changes and executed checks

The [maintained acceptance document](../../STANDALONE_REPLAY_ACCEPTANCE.md)
lists the independent parser/file/plan/actual-SDL boundaries and direct GCC
command. It uses every literal allowed key, all 16 modifier masks, exact limits,
full destination preservation, bounded file rejection, real window geometry,
stable ties, distinct completion markers, legal lifetime order and genuine
SDL filtered/full-queue failures. No copied parser tables, fake backend,
private-member access, Session/DSP or whole-main workflow duplicate is used.

Working directory for commands:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
The isolated scratch CMake harness only builds the maintained test plus frozen
`ScriptedInput.cpp`, linking the existing static SDL library. Its canonical
test name and environment match the integration contract. Actual commands:

```sh
cmake_bin=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$cmake_bin/cmake" -S ../replay-acceptance-harness-a27 \
  -B ../build-replay-acceptance-a27 -DCMAKE_BUILD_TYPE=Release
"$cmake_bin/cmake" --build ../build-replay-acceptance-a27 --parallel 2
"$cmake_bin/ctest" --test-dir ../build-replay-acceptance-a27 \
  -R '^test_standalone_input_replay$' --output-on-failure --no-tests=error -V
```

Result: **1/1 PASS, 0.02 seconds**, with `SDL_VIDEODRIVER=dummy` and test timeout
15 seconds. Direct GCC used `-std=c++20 -Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror -O2`; CMake used `cxx_std_20` and Release.
Final output: **573** valid parses; **186** atomic parser rejects; **3** regular
loads; **12** atomic file rejects; **51** forged-plan rejects; **116** checked
queue actions; **13** counted markers; **5** expected runtime failures; **4**
lifetime cycles. A separate direct execution under Python `subprocess.run`
with timeout=15 passed in 0.022 seconds, child peak RSS 9248 KiB.

Initial strict test compilation caught two out-of-range SDL enum test casts and
a range-loop copy warning; safe in-range unsupported enum fixtures/reference
iteration fixed them. An initial timing wrapper could not execute because
`/usr/bin/time` is absent; Python supplied timing/resource observation. Neither
was a production failure. No frozen production behavior failed acceptance.
Review also corrected contract wording from merely polling a final marker to
explicitly acknowledging it; agent 26 owns that documentation correction.

## Handoff and limits

Root owns native `hammond_standalone_replay`/CTest registration and coherent
whole-project qualification. Assignment 28 owns actual application's replay
workflows; this helper result does not substitute for them. Integrator should
run canonical `test_standalone_input_replay` from its native build and retain
the staged source identity. No physical-device/OS capture, callback application,
timing, audio, cross-platform or fidelity pass is claimed. The live window must
outlive the helper; concurrent file races were not dynamically induced. Linux
symlink/FIFO checks executed; Windows/macOS remain unrun.

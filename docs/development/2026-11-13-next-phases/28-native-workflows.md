# Assignment 28 — independent native interaction workflows

- Actual agent: `/root/w05_a28_native_workflows`, wave 5, first batch of the
  independent sixty-assignment, ten-wave standalone session.
- Inspected baseline HEAD: `738162f0bc36f88f8c76268d04831862a8118d10`.
  The working tree also contains concurrent unfinished standalone assignments;
  this historical commit does not identify their later built executable.
- Owned paths: `apps/standalone/native_tests/test_standalone_workflows.py`,
  `examples/standalone-input/README.md`, the three `.b3ui` examples there,
  `docs/STANDALONE_WORKFLOWS.md`, and this note. No production, shared status,
  CMake, core/model, existing historical report, commit or remote was modified.
- Read standing instructions, current handoffs/status, the native main loop,
  UiModel interface/layout, control-state grammar and new replay interface.
  Atlas product/closure review informs the engineering boundary; this assignment
  does not claim another fresh full-atlas or external-source review.

## Work and acceptance contract

The maintained stdlib Python suite requires an actual native executable and
registers as `test_standalone_workflows`. Its eleven methods launch fifteen isolated
application processes with explicitly selected SDL dummy audio/video drivers.
Every state, input and output path is private; no default user state is touched.
The three retained examples are keyboard ownership, keyboard Audio Apply and
explicit Save/Load, and the test consumes those exact scripts.

Literal note/control/byte expectations cover target/octave ownership, focus
loss/repeat suppression, Help, Audio restart, edited/sounding bank independence,
Cancel versus Panic, all-bank/pedal persistence, actual window resize and pointer
cleanup. Bounded copied pre-shutdown observations prevent exit cleanup from
concealing a stuck note. App dispatch counts supplement snapshots for the dummy
capture-failure On/Off pair; callback counts are never fixed test oracles.
CLI setup cases require usage exit 2 for replay plus smoke, runtime exit 1 for
missing/malformed input, and exact state/output sentinel preservation.

Root owns production replay integration, diagnostics and CTest registration.
Assignment 26 owns the bounded parser/SDL replay helper; assignment 27 owns its
independent parser/queue tests. Defects in those boundaries are reported to
their owners instead of changing their files.

## Actual verification

- `python3` compilation of the new Python source succeeded. Its temporary
  bytecode was removed; normal test runs need no generated repository files.
- Removing `HAMMOND_STANDALONE_EXECUTABLE` produced a nonzero prerequisite
  failure, without a skipped native test or application invocation. The first
  auxiliary check expected exit 1 too narrowly; it was corrected to nonzero.
- First actual registered CTest: 11 methods / 14 processes, failed in 22.38 s.
  CLI rejection passed; runtime cases stopped at this suite's overly strict
  zero-discard assumption. Existing documented Session.stop may discard one
  redundant cleanup release per device close (Audio Apply plus final close).
  The oracle now permits that finite per-start bound while retaining strict
  script acknowledgment, holds/controls and zero recovery/overflow/rejection.
  This was a test assumption correction, not a demonstrated production defect.
- Corrected registered CTest: **1/1 passed in 22.91 s**, zero failures; its
  retained log records **11 Python methods / 15 actual app subprocesses**,
  `Ran 11 tests in 22.790s`, `OK`. All exact held/control paths, phase checks,
  note-command counts, canonical saved bytes, actual resize and CLI guards pass.
- Linux Release; GCC 14.2.0, Python 3.12.14, CMake/CTest 4.4.4, locked SDL 2.32.10.
  Inspected run HEAD: `219821dfaca6bfee8ba0905993ed8deec7a66396`; replay work is
  additional live-tree source, identified below rather than implied by HEAD.
- Owned documentation links resolve and each document remains below 100 lines.

## Executed identities (SHA-256)

| Input/artifact | SHA-256 |
| --- | --- |
| Native executable | `bfb1b30b0b94fdc69c2fc1be3711b4b6d048a9f4651e9346cd8c5bd003ecb7ca` |
| `main.cpp` | `e2fc28db7852c23b46615d6c97d7967d133be810ccdd32e05f244dcda606aecb` |
| `ScriptedInput.cpp` | `ed6987b1b134737842028e611ed5f03ea67e9b232984284d885ca2c29d27809e` |
| `ScriptedInput.h` | `294b11d6a2c9b425d766b019b2ff1e7c460a308c93887c648dd7bce1d955c3d5` |
| Maintained Python suite | `55519887b30ed6c4de92fb5e2b3888e98b99c85dbfe7694fc3394d61c4a7ecc1` |
| `keyboard-notes.b3ui` | `823a5618f104ffb4756ade749fb1990dcf087cc1319e35b5fc1ceac0af548384` |
| `audio-settings.b3ui` | `c24c7225a93381be0767b291f02161725c314da42f4bb0f073e165d2f0123702` |
| `save-controls.b3ui` | `b31bae7800d9fea2f05045f261bcbbbc9f68935705a2e5047ac80517b592191f` |

## Reproduce and next boundary

From the repository root, build the native target with the locked SDL dependency,
then set `HAMMOND_STANDALONE_EXECUTABLE` to its absolute path and execute
`python3 apps/standalone/native_tests/test_standalone_workflows.py`.
CTest uses `--no-tests=error -R '^test_standalone_workflows$'`; process/suite
timeouts are 9/90 seconds. Missing binaries fail prerequisites without a skip.
Actual build path: `/workspace/scratch/5ba97739b54c/build-native-app`; executable
is its `apps/standalone/hammond_standalone`. Actual CTest is
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest`.

Dummy capture failure is safe-cleanup evidence only. This assignment does not
qualify physical capture, real audio devices, native accessibility, high-DPI,
hotplug, real-time deadlines, hardware sound or signed distribution. Publication
and coherent-source integration remain root's separate observed gates.

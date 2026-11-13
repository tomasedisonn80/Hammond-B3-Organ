# Assignment 20 — standalone state-file acceptance

Actual agent: `/root/w04_a20_state_files`, wave 4 of the independent
sixty-assignment, ten-wave standalone session. This is the same dispatched
assignment throughout; no additional worker is counted. Owned only
`apps/standalone/tests/test_standalone_state_files.cpp`,
`docs/STANDALONE_STATE_FILES.md`, and this report. No production/core/state-format
edits or commits were made. Root owns integration, shared records and publication.

## Result and evidence

- Added a maintained SDK-free acceptance target through the existing CMake glob.
  Seven focused scenario groups use the real standalone helper and core parser.
  Literal v1/v2/v3 documents and separately specified snapshot fields provide
  independent file/field expectations; no production writer generates an oracle.
- Exercised all 45 controls and both route bits, exact overwrite bytes, native
  Unicode/space directories and filenames, old-format migration and v3 re-save,
  malformed/truncated/trailing/future/oversized loads, the inclusive 16,384-byte
  limit, and whole-snapshot/file preservation on rejected calls.
- Invalid drawbars, bank selection, expression, each percussion enum class and
  pedals preserve existing target bytes. Missing parents, nonregular directory
  leaves, file-as-parent paths and empty filenames reject without creating parents.
- Linux actually exercised both regular and dangling symbolic-link load/save
  rejection, unchanged links/referents, and deterministic `RLIMIT_FSIZE` failure
  after temporary-file creation. It verified unchanged original bytes, cleanup,
  restored process limits/signal handling and a successful subsequent save.
- Every helper call checks for orphan `.b3-save-*` entries. All fixtures are
  confined to an exclusively created temporary tree with RAII unwinding and
  explicitly checked cleanup. The test uses no real user-state files.
- Fresh Release target build passed strict warnings; final verbose CTest passed
  **1/1**, seven groups completed, **0.01 seconds**, zero failed tests. No production
  defect was found. The final rebuild followed a diagnostic-order refinement.

## Exact execution

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Observed HEAD: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`. This is a fresh focused
build of the coordinated live worktree, not a frozen all-suite qualification.
Toolchain: Linux x86-64, Debian GCC 14.2.0-19, CMake/CTest 4.4.4,
GNU Make 4.4.1, Python 3.12.14; C++20 Release with `-Wall -Wextra -Wpedantic
-Wconversion -Wsign-conversion -Wshadow -Werror`.

```sh
task_tools=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$task_tools/cmake" -S . -B ../build-state-tests -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
"$task_tools/cmake" --build ../build-state-tests --target test_standalone_state_files --parallel 3
"$task_tools/ctest" --test-dir ../build-state-tests -R '^test_standalone_state_files$' -C Release --output-on-failure --no-tests=error -V
```

SHA-256 identities at the final build/run; source hashes matched before and after:

| Input/output | SHA-256 |
| --- | --- |
| `apps/standalone/StateFiles.h` | `ccf0aa7cb6d88df7c5e582a6154a12d28d9db97ab97d2833529ba8a328354a67` |
| `apps/standalone/StateFiles.cpp` | `6cd0d2f26bb2f938781561d278f15f9230e5d84b6052e8554761dc8e96dfd3b6` |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `include/hammond/ControlStateIO.h` | `2b42270c1d32bb57f3240ed48db5a45b182aaa5cec0c501d65d9f698b7016127` |
| `src/ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |
| `src/ControlStateIO.cpp` | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |
| Acceptance source | `45d1257c12ebd8db310fa25dc68d548d84288b8fa3dc581ad0c4a76040effa13` |
| Acceptance executable | `aa77bca6aa30b6db7aed082d789a6951ae16585bfac6016e106ff8ee0dd77789` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Explicit limits and handoff

Windows and macOS were **not run** here. The Windows sharing-lock replacement
failure branch is maintained but unexecuted. POSIX final-rename failure after a
complete temporary write is explicitly **not tested**: no deterministic fixture
without a filesystem race or root-sensitive permissions was introduced. A runner
unable to create symbolic links prints a capability-specific **NOT TESTED** result.

The contract separates rename visibility from power-loss durability, documents
regular-file/final-symlink policy, caller-created parents and main-thread use,
and makes no security claim against hostile concurrent path replacement. Native
application state publication, abrupt termination, power loss and physical-device
or audio fidelity are outside this file-helper result.

Root should rerun the target from the coherent integration checkpoint and retain
actual native-platform results separately. A whole-worktree `git diff --check`
at this review reported unrelated `THIRD_PARTY_NOTICES.md` trailing whitespace
at lines 158, 166 and 170; that file was left to its owner. Root subsequently
reported normalizing it. The three owned additions passed the scoped
trailing-whitespace and final-newline check before this final report update.

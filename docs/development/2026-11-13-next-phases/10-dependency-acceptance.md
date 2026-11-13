# Assignment 10 — independent SDL2 dependency acceptance

## Identity and owned scope

Actual assignment: `/root/w02_a10_dependency_acceptance`, wave 2, second batch
of the new sixty-assignment standalone session. Owned files are
[`tests/test_sdl2_dependency.py`](../../../tests/test_sdl2_dependency.py) and
this report. No production implementation, shared status, actual SDL2 checkout,
commit or remote reference was modified by this assignment.

Observed repository HEAD was `2e917509b378d48c85cc1d52c3aa446eef9552c8`, committed
tree `ac5f1888569339a9a3fd6c396d4d58fbe71dd503`. The dependency implementation
was concurrent uncommitted work; these exact executed input hashes, rather than
that baseline commit alone, identify the qualified helper:

| Input | SHA-256 |
| --- | --- |
| `tools/acquire_sdl2.py` | `a0555aefe37b37621e2602eea9035b4d048c81c1cca0c3d5442c1f638d927ab3` |
| `data/dependencies/sdl2-lock.json` | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |
| `cmake/VerifySdl2.cmake` | `21e3bb4fd75cbcc2879f321dae3437a609cd08d88ff98120a8aade19126ffc7e` |
| `tests/test_sdl2_dependency.py` | `45e8cfe920019db217d438034536359be810ee446bef7541f3cdaa408bbbff2b` |

Read `AGENTS.md`, the current operational/session context, the
[dependency contract](../../STANDALONE_DEPENDENCY.md), the acquisition tool,
its lock/helper and existing VST3 dependency-test conventions. This task tests
dependency admission; it makes no new atlas or physical-model acceptance claim.

## Executed focused regression

On Linux, Python **3.12.14**, Git **2.52.0** and CMake **4.4.4**, from
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`:

```sh
PYTHONDONTWRITEBYTECODE=1 \
HAMMOND_TEST_CMAKE=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake \
python3 tests/test_sdl2_dependency.py
```

**Result: 22/22 methods passed in 1.112 seconds; zero failures or skips.** The
initial 21-method run also passed; the final addition checks a competing owner
creating a destination between preflight and the actual atomic reservation.
No production defect or production repair was required. New-file whitespace
checking produced no diagnostics.

| Boundary | Executed evidence |
| --- | --- |
| Real lock identity | Independent literal repository/version/tag/commit/license expectations; the synthetic lock is rejected when fixture patches are absent. |
| Strict lock parsing | Malformed/invalid UTF-8/oversized/deep/nonfinite JSON, wrong top-level types, duplicate root/nested fields, unknown/missing keys, substituted identities, wrong field types and license path/hash changes reject before Git; CLI exit codes and existing destination bytes are checked. |
| Checkout identity | Missing/non-Git roots, inherited parent repositories, changed HEAD, wrong/missing tags and annotated-tag resolution use actual local Git repositories. |
| Source integrity | Staged/unstaged changes, committed missing required sources, source/license symlinks, changed license length and same-length license corruption reject. |
| Hidden changes | Actual ignored and untracked CMake inputs, `assume-unchanged` modifications and `skip-worktree` missing files reject even where ordinary Git status is empty. Empty source-free directories and external build files remain allowed. |
| Offline/read-only behavior | Successful verification executes only observed inspection commands with protocol use forbidden, lazy fetch disabled and inherited Git redirection removed. File bytes/modes/mtimes, including Git metadata, remain identical; partial/promisor configuration rejects before HEAD object inspection. |
| Destination preservation | Existing directories/files/live and broken symlinks, missing parents, resolved project paths and a simulated reservation race reject without reuse. Injected clone failure retains partial evidence; an actual local clone that fails subsequent license verification remains intact. |
| CMake boundary | An isolated script rejects missing and synthetic sources using this repository's helper/lock; a fake verifier beneath an enclosing `PROJECT_SOURCE_DIR` is never executed. No external SDL checkout is required by the maintained suite. |

All source mutations occur in temporary synthetic repositories. Fixture-only
module constants are patched briefly to load a local synthetic lock; they are
then restored. Fixture version/tag/URL are explicitly synthetic, and successful
verification of them does not qualify an official SDL release. Two actual
shallow clone operations use only a temporary `file://` repository. The helper's
`network_used=true` result on that local positive acquisition is its acquisition
path marker, not evidence of a network transfer or official download. Clone
transport failure and reservation timing are controlled injections; the other
listed source/Git mutations exercise real local files and Git commands.

## Separate retained official-source checks

The actual external source at `/workspace/scratch/5ba97739b54c/SDL2` was only
inspected, never mutated. With the unmodified production constants and lock:

```sh
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
```

**Passed, exit 0:** version `2.32.10`, tag `release-2.32.10`, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`, official repository
`https://github.com/libsdl-org/SDL.git`, one verified primary license and
`network_used=false`.

A separate temporary `verify.cmake` script set `Python3_EXECUTABLE` to the
running Python, included this repository's `cmake/VerifySdl2.cmake`, and called
`hammond_verify_sdl2` with that actual SDL2 path. Running the CMake executable
above with `-P <temporary-script>` **passed, exit 0**, returning the same source
identity and `network_used=false`. The actual SDL2 `.git/index` SHA-256 and
nanosecond modification time were identical before and after this smoke check.

## Integration handoff and remaining gates

The integrator has wired `HAMMOND_TEST_CMAKE` for `python_test_sdl2_dependency`;
it owns shared CMake/status/manifest changes and coherent-tree publication.
The maintained suite uses the existing Python-test discovery convention.
Rerun its CTest entry from the integrated build with `--no-tests=error` after
the pending standalone implementation files are available.

The top-level standalone build was intentionally not configured during this
assignment because its implementation files were still being developed. The
positive CMake result above is an isolated verifier smoke, not an upstream SDL
build or application run. Official network acquisition, cross-platform runs,
native windows/audio devices, callback deadlines, accessibility, complete
distribution notices and release rights remain separate unexecuted gates.

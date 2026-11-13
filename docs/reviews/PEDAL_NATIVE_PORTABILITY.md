# First hosted native checkpoint: failures and repair

## Observed failures at the exact published source

The first native publication was `d7b886103f8c9d4649ffa1c35930b79808217a3d`.
Native [run 43411073407](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43411073407)
and core [run 43411073429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43411073429)
actually executed on all configured runners. These failures are project defects,
not runner-acquisition failures, and are not hidden by the earlier local passes.

| Job | Observed outcome |
| --- | --- |
| Native Linux 131837341190 | Successful build, four native suites, inventory and bundle artifact |
| Native macOS 131837341133 | Controller test link failed on unresolved CoreFoundation symbols from SDK strings |
| Native Windows 131837340833 | Build succeeded; validator, ABI and behavior passed; controller exact string-round-trip failed |
| Core Linux/macOS/sanitizer | All three jobs succeeded |
| Core Windows 131837341674 | 65/67 suites passed; new inventory and SDK-build-tools suites failed |

The Windows native compile log explicitly contains `/fp:fast` on HammondB3,
controller and native test targets. It comes from the pinned SDK's
`smtg_setup_platform_toolset` macro, invoked in the wrapper directory. Such
shortcuts conflict with finite-value admission and code accessing the floating
rounding environment. [Microsoft's floating-point option documentation](https://learn.microsoft.com/en-us/cpp/build/reference/fp-specify-floating-point-behavior)
specifies `/fp:strict` for environment-aware code. The failed string assertion
alone does not identify every affected optimization; the repaired hosted run is
required to establish recovery.

The Windows inventory compared full `lstat` and `fstat` metadata as though both
APIs expose identical fields. [CPython 3.12.10 fileutils](https://github.com/python/cpython/blob/v3.12.10/Python/fileutils.c)
and [posixmodule](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c)
show the differing Windows ctime paths: path stat preserves creation time while
the descriptor helper retains change time. Path-based execute bits can also be
synthesized differently. Several untouched fixtures therefore failed before
hashing. The existing render-evidence reader already documents this API boundary.

The SDK-build fixture tried to recursively unlink its synthetic `.git` objects;
Windows rejected a read-only object. This was fixture setup, before the intended
parent-checkout admission assertion, not a failure of SDK pin enforcement.

## Scoped changes

- Remove the SDK's directory-wide `/fp:fast`, `-ffast-math` and
  `-ffp-contract=fast` options before creating the project's native targets.
  Apply `/fp:strict` to those targets on MSVC. Already-created SDK dependencies
  keep their upstream policy; the core's build policy is unchanged.
- Link the standalone controller test explicitly with CoreFoundation on macOS.
- Retain the exact controller assertion and add parameter/text/binary-value
  diagnostics if it fails again. No tolerance replaces bit equality.
- Compare identity, regular type and size across path/descriptor APIs, then full
  metadata before/after within each API. Keep bounded hashing, byte counts,
  path stability, descriptor stability and no-clobber publication.
- Add regressions for legitimate cross-API ctime/mode differences and rejection
  of changed identity, size, descriptor timestamps or permissions.
- Move the private synthetic Git metadata directory outside its module instead
  of deleting read-only objects. The original parent-checkout rejection still
  runs, and the fixture's temporary-directory cleanup remains responsible for it.

## Local qualification and source coherence

The isolated native repair tree
`09e155a958ee4fb1310ef8f0d8cafa2f980d1125` was archived and freshly built with
GCC 14.2.0/CMake 3.31.6. Its build-only native aggregate succeeded. Focused
CTest passed **4/4 native suites, zero failures/skips, in 4.32 seconds**.
The Linux module remains byte-identical:
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.

The completed repair tree
`7bf8c8d63ec6d816cbae86a1b1ee874666929eb5` differs from that native source only
in the inventory tool and two Python test files. All compiled native inputs are
identical. It was separately archived and configured SDK-free, then the two
focused CTest suites passed **2/2 in 2.79 seconds**, comprising **32 Python
methods** (18 inventory and 14 build-tool methods), without skips. The first
manual Python invocation lacked `HAMMOND_TEST_CMAKE` and failed two explicit
CMake-availability assertions; the configured CTest run supplies the actual
CMake path and passed. No implementation was changed to suppress that setup gate.

Commands, with the task-local CMake/CTest executables on PATH:

```sh
cmake -S checkpoint-native-portability/source -B checkpoint-native-portability/build -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/vst3sdk"
cmake --build checkpoint-native-portability/build --target hammond_vst3_test_inputs --parallel 2
ctest --test-dir checkpoint-native-portability/build -C Release --output-on-failure -R '^(hammond_vst3_validator|test_native_)' --no-tests=error
cmake -S checkpoint-native-portability/source-complete -B checkpoint-native-portability/build-python -DCMAKE_BUILD_TYPE=Release
cmake --build checkpoint-native-portability/build-python --target hammond_profile
ctest --test-dir checkpoint-native-portability/build-python --output-on-failure -R '^python_test_(native_bundle_inventory|vst3_build_tools)$' --no-tests=error
```

Final publication differs from the qualified repair tree only in Markdown
result records. Ongoing seventh-wave sources and actual assignment metadata are
excluded. Native Windows/macOS recovery and the complete new hosted matrix remain
pending until observed at the repair commit. Quiescent bundle input remains a
requirement; these file checks are not a hostile concurrent-filesystem sandbox.


## Hosted repair outcome and fresh path metadata follow-up

Repair `9403debd754f771bf39bc8cd771ecfd86c0f14d6` was fetched with exact tree
`e2a00f7c270317b0f07be8a467120d8a573bb61a`. In core
[run 43413518927](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43413518927),
Linux, macOS and sanitizer jobs succeeded. Windows job 131845616581 passed
**66/67 suites**: the read-only Git fixture and original cross-API metadata
regressions passed, while two synthetic native-header cases still failed at the
final `bundle changed during inventory` check.

In native [run 43413518971](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43413518971),
Linux and macOS completed their tests, inventories and artifacts successfully.
Windows job 131845616021 passed **4/4 actual native suites in 2.63 seconds**,
including all 41,795 controller checks and exact ABI/behavior audio. Its later
bundle-inventory step still failed. Thus the CoreFoundation and floating-point
repairs have observed platform recovery, but the complete Windows artifact gate
remains open at this commit.

The inventory initially obtained tree metadata from `DirEntry.stat()`. The pinned
[CPython Windows implementation](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c)
reconstructs cached directory-enumeration metadata there; it is not a fresh path
query. Root now obtains each entry's before/after signature using `path.lstat()`
consistently, preserving device, inode, mode, size and nanosecond timestamps.
The cross-path/descriptor identity checks and full within-API before/after guards
remain. Assignment 46 independently reviewed that implementation rationale.
The exact field responsible for the previous hosted mismatch was not printed
by its old diagnostic, so no particular changed field or uninitialized-memory
cause is claimed. The new bounded diagnostic lists up to four changed entries
and metadata fields to make any remaining platform failure actionable.

A regression actually changes resource bytes or adds a bundle member during
header inspection; both mutations still reject. The repaired inventory's
**19 Python methods pass locally**. The [wave-7 integration record](PEDAL_WAVE7_INTEGRATION.md)
identifies its exact source and focused qualification. Fresh Windows execution
and artifact observation are required to close this follow-up.


## Observed wave-7 Windows recovery and retained artifacts

Published wave-7 commit `7fb9b6121b729f46a9e18d80e8620eb21dc0847b` has verified
local/remote tree `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`. In core
[run 43415692328](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692328),
Windows job 131852884476 passed **68/68 suites in 84.18 seconds**, including
both the install-schema regression and the full inventory suite. Linux Release
and leak-enabled ASan/UBSan also succeeded. macOS was still queued when this
observation was recorded; a four-job success is not claimed here.

In native [run 43415692247](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692247),
Windows job 131852884109 passed **7/7 suites in 5.80 seconds**, then successfully
completed build/copy inventories and uploaded the actual bundle. Linux job
131852884056 passed **8/8 suites in 5.70 seconds** and completed its inventory
and artifact. The extra Linux suite is the scoped allocation interposition gate.
macOS remained queued at this observation. These results close the observed
Windows defects at this revision, without guessing the precise metadata field
that caused the earlier uninformative failure.

Root downloaded both actual bundle artifact ZIPs through the connected Actions
API, verified their full ZIP SHA-256 against the API's digest, verified each
inner archive digest, then independently checked every tar file's size, bytes,
SHA-256 and permission mode against its inventory. Every entry matched; no links
or unexpected file members were present. The inventory's caller-declared commit
also matches the independently observed workflow revision. This is retained
source/run/package association, not an authenticated build attestation.

| Observed artifact | ZIP SHA-256 | Actual module SHA-256 |
| --- | --- | --- |
| Windows bundle 14032090890: 6 files, 658,056 payload bytes | `cf2ffb94459991446f2ebe1a8b04749680957f216d8e74b88863748e88d742fa` | `a05435f0d76704c36c8af6f2d64556e7325e2141790a9d8b56c474f305d5cdad` |
| Linux bundle 14032125757: 4 files, 456,767 payload bytes | `716a064d65e2127dbfb7ded5567d3d10a2c7dddd4a9c1afe494f6d1eb30561a9` | `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca` |

Complete downloaded ZIPs, inventories, archive hashes and native logs were
retained in root's local `w07-hosted-artifacts` evidence directory. Later audits
must inspect their own exact-source platform results rather than inheriting
these successes for changed production code.

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

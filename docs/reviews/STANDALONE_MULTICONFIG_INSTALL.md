# Standalone multi-configuration installation audit and repair

**Result:** actual Ninja Multi-Config Debug and Release builds, custom install
paths, component coexistence, data-root tracking, DESTDIR staging and relocated
runtime checks pass in the source scopes below. The audit also reproduced and
repaired an unknown-configuration defect: the old rules returned success after
copying eight metadata files without an executable. The repaired rules reject
that selection before any destination write.

Assignment **53/60**, wave **9**, actual agent
`/root/w09_a53_multiconfig_install`, executed on 2026-11-13. This is independent
of the earlier [single-configuration clean setup](STANDALONE_CLEAN_SETUP.md).
The [installation guide](../STANDALONE_INSTALL.md) now documents the corrected
configuration contract.

## Exact source and tool identities

| Item | Observed identity |
| --- | --- |
| Baseline published commit | `649b12c7d1faa7601fde1019e913347c65a6634a` |
| Baseline Git tree | `cf63327d857b02029e8c5c6f406cab3d3c6890d1` |
| Fresh archive | 37,068,800 bytes; SHA-256 `66fe3544c87f47b034ee33d97ac2ac4abf1e5af7bf50d90611098d5191069d36` |
| Source inventory | All **842 tracked blobs and executable modes** matched the named Git tree before building and after both baseline configurations. |
| Host | Linux 6.18.57, x86-64; GCC/G++ 14.2.0; Python 3.12.14 |
| CMake / CTest | 4.4.4 |
| Actual generator | `Ninja Multi-Config`; initial configurations `Debug;Release`; no `CMAKE_BUILD_TYPE` |
| Ninja | `1.13.2.git.kitware.jobserver-pipe-1`; executable SHA-256 `08639e194fffa7f08b259fc4abfa4803aff66b64de52549cee42ec527d55cea6` |
| SDL | 2.32.10; commit `5d249570393f7a37e037abf22cd6012a4cc56a71`; private non-hardlinked local clone, verified before and after execution |

Ninja was absent from PATH. Read-only inspection found the existing executable
at `/workspace/scratch/641ca55ce6de/native-toolchain/bin/ninja`; the configure
selected it explicitly with `CMAKE_MAKE_PROGRAM`. No package was installed,
shared tool changed or network dependency acquisition attempted. CMake/CTest
were the existing binaries under
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/`.

The private audit root is
`/workspace/scratch/5ba97739b54c/a53-multiconfig-install`. Source, build, SDL,
installation and runtime paths contained spaces and Unicode. The old archive,
a complete retained baseline source copy, full command logs, inventories and
all runtime diagnostics remain there.

## Actual failure and narrow correction

After building Debug but before building Release, this declared selection
correctly failed with exit 1 and left its fresh prefix absent:

```sh
cmake --install 'build multi é 音' --config Release \
  --component Standalone --prefix 'missing Release prefix'
```

The error named the absent `apps/standalone/Release/hammond_standalone` and
required building the selected configuration. The other configuration's real
executable did not satisfy preflight.

The following command on the same actual generated build instead returned
**exit 0**, created the prefix and copied all **eight metadata files**, with
no executable:

```sh
cmake --install 'build multi é 音' --config NotAConfiguration \
  --component Standalone --prefix 'unknown configuration prefix'
```

The generator emitted no matching branch for the target-dependent preflight
and executable-copy rules. The metadata rules remained unconditional. The
result was a successful but incomplete installation; the original log and
eight-file inventory were preserved, not overwritten by the corrected run.

Root authorized the worker to add a guard in `cmake/InstallStandalone.cmake`,
its maintained native regression and the affected guide. The guard reads the
actual `GENERATOR_IS_MULTI_CONFIG` property and, only for such generators,
installs an unconditional Standalone-scoped check before any target-dependent
rules or destination writes. It matches the configured names without case
sensitivity. It does not hard-code Debug/Release, change ordinary component
exclusion, affect the flag-OFF case, or bypass the existing input/identity/
destination preflight. Single-configuration selection remains unchanged.

The maintained test now executes unknown-name installation against the actual
configured project. For a multi-config build it requires nonzero status and
preserves both a fresh destination's absence and an existing tree containing
sentinel bytes plus an empty directory. For a single-config build it requires
its selected executable and all eight metadata files to be copied completely,
preserving unrelated entries. No new Ninja dependency or capability skip is
introduced by the test. The existing private-input, disabled-component,
overwrite, license-identity and selected-missing-binary checks remain.

### Frozen repair scope

The original private source was preserved before overlaying only these three
files. Their repaired hashes are:

| File | SHA-256 |
| --- | --- |
| `cmake/InstallStandalone.cmake` | `5a81d2689300a6fb58cf91a232dcd17c9ffbee209f311471fe5ccde8baed7f19` |
| `apps/standalone/native_tests/test_standalone_install.py` | `5ff17b66593b4b1b63f0aa193786ab7d38db40ebed6db00c46f2f212537ac9c1` |
| `docs/STANDALONE_INSTALL.md` | `4b49aa3babff92869a07bf67798b84fe179039163ca231db62136dc8329bf9b1` |

The other **839 tracked files** retain their baseline bytes and modes. The
repaired inventory also records two generated Python bytecode files; all **844
inventoried files** remained unchanged through the later checks. No C++ source,
header, generated profile, compiler flag or linked executable changed during
the installer repair. CMake regenerated the install/test rules using the same
actual Debug/Release executables. This is an installer qualification over the
named source plus exact overlays, not a claim of rebuilding later app code.

## Builds, configuration selection and installed identities

The following abbreviated paths correspond to the recorded argument vectors:

```sh
A53_ROOT='/workspace/scratch/5ba97739b54c/a53-multiconfig-install'
A53_CMAKE='/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake'
A53_CTEST='/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest'
A53_NINJA='/workspace/scratch/641ca55ce6de/native-toolchain/bin/ninja'
cd "$A53_ROOT"
"$A53_CMAKE" -S 'source é 音' -B 'build multi é 音' -G 'Ninja Multi-Config' \
  "-DCMAKE_MAKE_PROGRAM=$A53_NINJA" '-DCMAKE_CONFIGURATION_TYPES=Debug;Release' \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  "-DHAMMOND_SDL2_ROOT=$A53_ROOT/SDL2 private é 音" \
  '-DCMAKE_INSTALL_BINDIR=program files é/bin' \
  '-DCMAKE_INSTALL_DATAROOTDIR=readable data 音/share' \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
"$A53_CMAKE" --build 'build multi é 音' --config Debug \
  --target hammond_standalone hammond_standalone_benchmark \
  hammond_render hammond_model_info hammond_parameter_info --parallel 2
"$A53_CTEST" --test-dir 'build multi é 音' -C Debug \
  -R '^test_standalone_install$' --output-on-failure --no-tests=error -V
```

The same selected build and test commands were executed for Release. Fresh
configuration passed in **20.71 seconds**; first Debug and Release builds
passed in **48.26** and **76.57 seconds** respectively. These are build
observations in a shared container, not controlled speed comparisons.

| Scope | Actual result |
| --- | --- |
| Baseline Debug install CTest | 1/1 passed; 3 methods; 2.90 seconds CTest total |
| Baseline Release install CTest | 1/1 passed; 3 methods; 2.49 seconds CTest total |
| Repaired Debug install CTest | **1/1 passed; 4 methods; 2.88 seconds CTest total** |
| Repaired Release install CTest | **1/1 passed; 4 methods; 3.10 seconds CTest total** |
| Explicit Debug and Release stages | Exactly nine ordinary files each, all source/binary hashes and modes matched |
| Mixed-case `--config dEbUg` | Passed; installed executable byte-identical to Debug |
| Repaired unknown-name direct probes | Both exit 1; fresh prefix absent; existing sentinel bytes and empty directories unchanged |
| Declared custom `Audition`, selected as `aUdItIoN` | Name guard accepted it; required-input preflight correctly rejected its unbuilt executable, leaving no prefix |

All four CTest invocations ran once, with no skips, retries, suppressions or
weakened assertions. `Audition` was added to the actual configuration list for
the admission check; its application was not built or executed. CMake's real
single-config rules were inspected to confirm their unconditional target path;
the integrator's fresh single-config gate must execute the new corresponding
test branch in the final combined source.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Debug application | 8,953,864 | `5a1a12807f17e44bf8a447783ab2838d0b79307b8df31f29d15461bbfe85218e` |
| Release application | 2,602,864 | `4c4f9c0fa2a7cdfa37410192c67d6eeb827ebaca8910c8835fa115e85feadaa0` |
| Debug benchmark | — | `9b68177aebbf46d1c22a9d03d7bb03d3572cca3eb6cc419440f5120bba85a7e2` |
| Release benchmark | — | `0c97a79e8c49dbad961090727fe3ae1668a283bdc4d87f4d334fc9c604981f19` |
| Common generated nominal profile | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

One actual performance benchmark per configuration used 48 kHz, 512 frames,
100 measured calls and 16 warmup calls. Both returned `status: ok` and the same
57-input source fingerprint
`5fd7837b44dbe8fd09bfbd9931c20065e29acfffee10f3adca1a622cb18b9bb8`.
Debug reports `configuration: Debug`, `ndebug: false`; Release reports
`configuration: Release`, `ndebug: true`. The actual main.cpp compile commands
also contain Debug `-g` versus Release `-O3 -DNDEBUG`. No timing threshold or
device deadline claim was applied.

Executables install as mode 0755; eight metadata files install as 0644. Both
configurations use the same metadata bytes. In the repaired scope the install
guide is 6,379 bytes with the hash above; the other seven metadata identities
remain those of the named baseline and locked dependencies. The complete
nine-file inventories are retained separately for every staged layout.

## Custom directories, components and DESTDIR

The initial `CMAKE_INSTALL_BINDIR` was `program files é/bin` and the initial
`CMAKE_INSTALL_DATAROOTDIR` was `readable data 音/share`; the cache correctly
materialized `CMAKE_INSTALL_DATADIR` with the same value. Actual subsequent
configuration and installation verified these independent behaviors:

- Changing DATAROOTDIR to `changed root Ω/assets` moved automatic DATADIR to
  the same relative path and updated its automatic-origin marker.
- Setting explicit DATADIR to `explicit metadata é/share`, then changing
  DATAROOTDIR to `third root 音`, preserved the explicit path and removed the
  automatic-origin marker.
- Every fresh Standalone stage contained exactly the expected nine files under
  its selected binary/data paths, with no source, PDF, font or external profile
  added to the runtime payload.
- Ordinary installation contained **23 OfflineTools files and no Standalone
  files**. Adding Standalone to that actual prefix produced **32 files** and
  preserved every pre-existing file's bytes and mode.
- `DESTDIR` staging with `CMAKE_INSTALL_MODE=COPY` and logical prefix
  `/hammond-a53` produced the same exact nine-file payload under the private
  DESTDIR. It did not install at the host's logical prefix.

The first ordinary-install command was an **audit setup error**: only three of
the five required offline executables had been built. Its existing preflight
correctly returned 1, named `hammond_console_trace` and the five required
targets, and left the prefix absent. The audit then built both missing trace
targets (`hammond_console_trace`, `hammond_pedal_trace`) and executed the valid
ordinary/coexistence checks. The original failure is retained. No production
change, gate relaxation or unchanged-command retry was used to obtain success.

## Relocated Debug and Release runtime

After completing install checks and verifying source/dependency inventories,
only this worker's private source, build and SDL directories were moved under
`unavailable originals 音/`. Their three original paths were asserted absent.
Each repaired install prefix was separately renamed to `moved Debug é 音` or
`moved Release é 音`; its original stage path was absent. Shared sources,
dependencies and other workers' builds were untouched.

From a separate fresh cwd per configuration, each installed executable ran
three direct commands: `--help`, a 600 ms smoke with a real 960×700 BMP, and
the maintained 2,600 ms keyboard script. The entire child environment was:

```text
PATH=
LANG=C.UTF-8
LC_ALL=C.UTF-8
SDL_AUDIODRIVER=dummy
SDL_VIDEODRIVER=dummy
SDL_RENDER_DRIVER=software
```

All **six invocations returned zero**. The four window runs verified the
literal default controls and profile identity, actual images/callbacks/frames,
native float32 stereo, zero audio failures/nonfinite/overrange counters, zero
Session recovery/rejections/faults and stopped/no-held final state. Deliberately
missing state paths stayed absent; all installed bytes stayed unchanged.

| Relocated run | Callbacks | Frames | Rendered images |
| --- | ---: | ---: | ---: |
| Debug smoke | 56 | 28,672 | 13 |
| Debug keyboard replay | 218 | 111,616 | 31 |
| Release smoke | 57 | 29,184 | 19 |
| Release keyboard replay | 224 | 114,688 | 69 |

Both replays delivered all **18 events**, accepted **four On and four Off**
commands, and acknowledged the final scripted sequence before cleanup. Their
actual distinct held states matched all nine literal expectations: empty;
Upper 60; Upper 60/Lower 74; those manuals plus pedal 17; Lower 74/pedal 17;
pedal 17; empty; Upper 72; empty. Original ownership survived target/octave
changes. The final scripted prefix is sequence 9; one later redundant shutdown
release is discarded by the stopped lifecycle and resolves sequence 10. This
does not substitute cleanup for the required scripted releases.

The actual smoke BMPs are nonuniform, valid 960×700 images and byte-identical
between the configurations, SHA-256
`b9b24f56a6599c75b0a7c90d8468333eab98d7fd47cee20f73cca993f4baac13`.
Both smoke diagnostics report held and released observations and
`screenshot_while_held: true`. This audit does not replace the separate
[instrumented timing repair](STANDALONE_TIMING_REPAIR.md).

## Limits and next integration gate

The audit records **39 command invocations** with argument vectors, cwd,
explicit runtime environments, UTC times, exit codes and complete logs. Its
negative admission probes and the corrected setup failure are distinguished
from successful configuration/build/test/runtime commands. Baseline failures
and fixed-source identities remain separately reproducible.

This evidence covers Linux Ninja Multi-Config at the versions above and
explicit SDL dummy/software execution. It does not establish Visual Studio or
Xcode behavior, minimum supported tool versions, physical audio/desktop
operation, accessibility, callback deadlines, signed packages or redistribution
clearance. The historical baseline notice bytes were inventoried, not legally
approved; root's later secondary SDL notice additions are outside this source.
Assignments 47/50's later adapter/test changes and concurrent calibration work
are also excluded.

Root must integrate the exact guard/test/guide, execute the new maintained
single-config branch in a coherent fresh full-source build, inspect the actual
hosted configurations and qualify the final package bytes with the updated
notices. The worker made no commit, branch, publication or shared-ledger change.

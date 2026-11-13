# Assignment 38 — offline package and local native bundle staging

## Assignment and source basis

- Actual assignment: `38`, wave `7`, agent `/root/w07_a38_install_packages`.
- Date: 2026-11-13. Published checkout at assignment start:
  `88c36b4a72a07f6498f73279f25023278accd350`.
- Read `AGENTS.md`, current status/next-step/handoff records, the plan and atlas
  review, existing install/test rules and native build contracts. Read the complete
  relevant atlas chapter 064, PDF pp. 391–396, directly. Its separation of pinned
  wrapper dependencies, native interface acceptance, actual host sessions and
  device qualification governs this package's evidence boundaries. The prior
  complete 500-page review remains the separately retained research record.
- Source PDF SHA-256 remains
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`
  (21,248,265 bytes). No source PDF, profile, map, score, production DSP or native
  processor/controller implementation was modified.

Owned files are `cmake/InstallHammondTools.cmake`, `tests/test_install.py`,
`plugins/vst3/tests/test_native_install.py`, `docs/OFFLINE_INSTALL.md`,
`docs/VST3_LOCAL_INSTALL.md` and this note. The integrator owns root CMake, shared
status, assignment accounting and publication. No files were staged, committed
or pushed by this worker. No further agents were spawned.

## Implemented package contracts

### OfflineTools

Extracted the existing root install block into the new module and extended the
payload from 16 to **22 files**. The original four executable names, console
plotter, compiled profile, two catalogs and eight scores remain. Added
`hammond_pedal_trace` plus the existing pedal catalog and four existing scores
under `share/hammond-b3-organ/fixtures/pedals` by default. All catalog, score and
plotter files are copied unchanged. No benchmark, SDK, source headers, research
PDF, optional runtime library or future pedal SVG tool is installed.

The guard checks all five built executables and every data/script input before
copying. Both install directories must be nonempty and relative, with no parent
traversal or CMake list separators. Explicit invalid values are checked before
`GNUInstallDirs` can replace an empty data directory with a default. Copy mode is
required; an environment-requested symlink install is rejected. Normal successful
offline installs retain CMake's replacement behavior, so the user guide recommends
fresh prefixes for retaining older versions.

The expanded acceptance test preserves all previous assertions: exact original
payload/data bytes; moved-prefix A4/percussion PCM, full WAV and JSON agreement;
both metadata exporters; console CSV/SVG and trace hash; the explicit-profile
identity/zero-gain mutation; missing-profile errors; and absence of fallback
output. New coverage verifies the exact 22-file payload, all pedal score hashes,
pedal catalog/profile/map/parameter identity coupling, a 48,000-frame pedal
mixture render and all three 5,760-row pedal scenarios at 48 kHz. Build and moved
tool outputs must agree exactly. Reusing a pedal CSV output must preserve it.
Both trace tools now participate in the missing-profile check.

A separate private minimal project includes the **real install module** to
exercise its generated install rules without renaming shared source/build inputs.
An unbuilt component and eleven independently missing inputs must fail before
changing an older installed executable, unrelated files or directory entries.
The missing inputs include each of the five executables, the profile, plotter,
original catalog, console score, pedal catalog and pedal score. Invalid absolute,
parent-traversing (both slash conventions) and empty bindir/datadir values must
also fail.

### NativeVST3

The native-enabled build has an explicit `NativeVST3` component, excluded from
unqualified installation. Its source is the SDK target's actual
`SMTG_PLUGIN_PACKAGE_PATH`, including configuration; its actual binary is
`$<TARGET_FILE:HammondB3>`. It copies the whole self-contained bundle into relative
`${CMAKE_INSTALL_LIBDIR}/vst3`. There is no guessed platform architecture layout,
system-directory link, DAW registration, SDK/source distribution or validator
installation.

Preflight requires the bundle, its actual internal module, SDK-generated module
metadata, SDK notice and repository notice to be present and nonempty. macOS also
requires its `Info.plist`. Symlinks are rejected. An existing destination bundle
is never merged or replaced; a fresh destination bundle is required, while other
prefix files/plugins are preserved. Failed input preflight occurs before any
destination mutation. Later filesystem copy failure is not promised to be atomic.

`test_native_install` is registered only when native building/testing are enabled.
It installs the actual component, checks its entire file/hash and directory
inventory, rejects a repeat install without changes, moves the prefix and loads
the **relocated actual native module** through `test_native_abi` from an unrelated
cwd. All `HAMMOND_*` environment variables are removed. The harness uses an
explicit copy of the matched profile as reference equipment; the plugin's profile
is embedded. The harness itself is not installed. The source bundle must remain
unchanged. SDK module metadata is hashed as opaque bytes, preserving its trailing
commas instead of applying a strict Python JSON parser.

Private copied-bundle negatives cover an unbuilt bundle, each required file
missing, an empty notice, invalid relative-library destinations, and omission of
the explicit component. Both file hashes and directory entries must be unchanged
after failure. Tests do not rename any production bundle or SDK input.

## Frozen test source and environment

Used a fresh `/workspace/scratch/f364bc93d920/a38-source` copied from the coherent
`a33-native-source` archive after assignments 33–35 released it. Its basis is the
integrator's fifth-wave tree
`06786b70f1cffcc6371600fd6e14306f16e8c985` plus the frozen native overlays described
in [assignment 33](33-native-build.md). Overlaid only this assignment's module,
two Python tests and the reviewed root CMake include/native-test hook. The live
assignment-37 CLI edits were not included. Build output is separate in
`a38-build`; the previously retained a33 logs were not changed.

Environment: Linux x86-64, GCC 14.2.0, Python 3.12.14, CMake/CTest 3.31.6,
Release, two parallel build/test jobs. The existing verified external SDK was
`/workspace/scratch/f364bc93d920/vst3sdk`; CMake checked the project lock before
building. No source was built inside that checkout and no SDK file was modified.

The complete 459-file test-source input manifest, excluding Python bytecode, is
retained at `/workspace/scratch/f364bc93d920/a38-source-input-sha256.txt`, SHA-256
`c8bfcc328cf877b2e83747f6bc11ad119cae1b55bf42cb11e01cf13b74cc3820`.
This is an isolated worker gate, not a claim about the later combined publication.

The final tested implementation hashes are:

| File | SHA-256 |
| --- | --- |
| `cmake/InstallHammondTools.cmake` | `0d6a047f8544b9cf42a95dec8787e350a9bd1312b2624fe124022ba18ead2931` |
| `tests/test_install.py` | `da68710db99badbfe394d18fd6785800c6c7ea4321495b5616b14f922f48e4e7` |
| `plugins/vst3/tests/test_native_install.py` | `3f2a2e8b52ca2d647e4da45218ed68c748b7a5d5212b8254fad57e3b6965366e` |

## Executed commands and observed results

The actual CMake and CTest executables are in
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin`. With that directory first
on `PATH`, the executed build and focused gate correspond to:

```sh
cmake -S /workspace/scratch/f364bc93d920/a38-source \
  -B /workspace/scratch/f364bc93d920/a38-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/vst3sdk
cmake --build /workspace/scratch/f364bc93d920/a38-build \
  --config Release --parallel 2 --target hammond_render hammond_model_info \
  hammond_parameter_info hammond_console_trace hammond_pedal_trace test_native_abi
ctest --test-dir /workspace/scratch/f364bc93d920/a38-build -C Release \
  --parallel 2 -R '^(python_test_install|test_native_install)$' \
  --output-on-failure -V
```

Configuration and building succeeded. The native ABI dependency built the real
module and its embedded profile. CMake's optional LIBJACK discovery remained
missing; this headless target did not require it. The SDK stdatomic feature probe
reported its normal failed capability check; compilation/linking then succeeded.
These are retained configure output, not claims of a warning-free build.

| Gate | Observed result |
| --- | --- |
| First focused run | Native install passed; offline positive relocation passed, but its empty `CMAKE_INSTALL_DATADIR` negative failed |
| Correction | Validate explicitly defined directories before `GNUInstallDirs` default substitution; retained the failing test/log |
| Second focused run | 2/2 CTest tests passed in 3.19 s |
| Final run after directory-inventory assertion refinement | 2/2 CTest tests passed in 3.48 s; offline 2 Python cases passed in 3.246 s, native 2 Python cases passed in 1.091 s |
| Native-OFF fresh configure and discovery | `ctest -N -R '^test_native_install$'` reported `Total Tests: 0`; no skipped placeholder |
| Whitespace/syntax review | `git diff --check` passed for edited tracked files; Python AST parsing passed for both install tests |

The first failure was in the negative acceptance expectation: GNUInstallDirs
coerced an explicit empty data-directory argument into its default before the
original guard could inspect it. The positive 22-file package and native relocated
ABI were already passing. The fix tightened the real install contract; the test
was not weakened. No production DSP or binary change was needed.

The final relocated ABI summary was `native-abi-v1`: 9 instances, 691,878
assertions, 45 descriptors, 2,002 conversions, 73 accepted callbacks, 86 rejected
calls, 7 state round trips and 6 lifecycle sequences. It compared **229,725**
reference frames, including **217,972** audible frames, with maximum audio error
**0** and float hash `af029009868faa04`.

The Linux source/installed/moved bundle consisted of exactly four hash-identical
files:

| Bundle file | Bytes | SHA-256 |
| --- | ---: | --- |
| `Contents/x86_64-linux/HammondB3.so` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| `Contents/Resources/moduleinfo.json` | 1,090 | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| `Contents/Resources/VST3_SDK_LICENSE.txt` | 1,094 | `e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e` |
| `Contents/Resources/THIRD_PARTY_NOTICES.md` | 7,887 | `a3aa1900ec8b584bfe0879d0d8c7c1af3148dc23729d01a62e26ed428b61c2f6` |

The matched `nominal.b3p` remains 4,545 bytes, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

### Retained command logs

Files below remain in `/workspace/scratch/f364bc93d920`; this note retains their
identity and outcome even after temporary test prefixes are cleaned up.

| Log | SHA-256 |
| --- | --- |
| `a38-configure.log` | `3c868c70745638409cc43769d79a442957e1ef36d65b4aa43cca0c5dd8c652aa` |
| `a38-build.log` | `3e01423d16f2abf4bd27fef0a51806a4b16cb40e811000c2db0f009818cf402a` |
| `a38-install-attempt1.log` | `248e7312116022eff6d0325bb2adc60992bb85f92d26dc3bd66f35d027670c59` |
| `a38-install-attempt2.log` | `898377bd3fa75f5c66de0a7b790bb7a0145ba49c2f46bcf49566678de0a6b80a` |
| `a38-install-final.log` | `53c1a4fe5bab629db6f761d27664d49fecda5610489cebd553d71f5b56196670` |
| `a38-default-discovery.log` | `8fb8d4bcd80e4e1c9f88d98df6eac6b0e1033abb30abd81992e191d566e66db0` |

## Integration handoff and next step

The parent applied the reviewed live root hook while retaining its earlier W6
index/archive unchanged: include `cmake/InstallHammondTools.cmake` after all tests,
then register `test_native_install` only for native-enabled testing. Use
`get_target_property` to obtain the SDK bundle path before generating the test
environment so its nested configuration expression resolves. Supply exact CMake,
build, configuration, profile, bundle, actual module, ABI executable and relative
libdir paths. The module itself preserves the offline test's install environment.
The existing native aggregate already builds the bundle/profile/ABI prerequisites.

Next, the integrator should freeze the combined W7 source with assignment 37's
CLI changes, build the five offline tools and native test inputs, run both install
gates, and retain publication/hosted-platform results for that exact tree. Update
shared status, next steps and the manifest, then commit/push under the owner's
standing authorization. The code hashes above identify this worker's frozen
handoff; later modifications need their own affected gate.

Assignment 45 can extend packaging with a pedal plotter once that actual tool and
its acceptance contract exist. This assignment intentionally did not speculate
about an absent future file or silently make its installation conditional.

This evidence is local Linux same-host staging and relocation. The test temp
paths use ASCII names with spaces; Windows Unicode CLI work belongs to assignment
37 and was not claimed here. No Windows/macOS execution, clean-OS runtime test,
DAW scan/session, device handling, signing, notarization, redistributable installer,
hardware measurement or physical timbre calibration was performed. SDK validator
and wider native behavior results remain their separate assignments; this package
gate does not turn those or the atlas's M9 plan into product completion.

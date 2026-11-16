# Clean headless registration build admission — A38

16 November 2026; actual worker `/root/w07_a38`, wave 7.
**Admitted for the observed Linux headless build, focused tests and packaging.**
This is a fresh configuration with no SDL source or host SDK, distinct from
earlier native-build execution. No production blocker was found.

The [qualification receipt](../development/2026-11-16-preset-library-continuation/reports/a38-headless-qualification.json)
indexes original compressed configure/build/test/link/install logs, exact argv,
source and output hashes. Initial HEAD was
`d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93`, tree
`1e59776459a05a9d934d0b519a45cd4c61b13ae9`. Root subsequently added native starter
Load wiring inside `HAMMOND_BUILD_STANDALONE`; its exact patch is retained.
Regenerating this same OFF build required no recompilation. The
[test-source manifest](../development/2026-11-16-preset-library-continuation/reports/a38-headless-source-test.json)
binds that transition; all 540 recorded inputs remained unchanged through tests
and installation. The new native-only test was excluded by the OFF branch.

## Fresh configuration and built inventory

From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, with
`PYTHONDONTWRITEBYTECODE=1` and `LC_ALL=C`:

```sh
cmake -S . -B ../a38-headless -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT= -DHAMMOND_RTMIDI_ROOT= -DHAMMOND_VST3_SDK_ROOT=
cmake --build ../a38-headless --config Release --parallel 2 --target \
  hammond_registration hammond_render hammond_generate_starter_registrations \
  hammond_profile test_control_file_input test_control_io \
  test_standalone_registration_library test_standalone_state_files
```

The previously absent build completed **59 steps in 26.54 seconds**. Observed
tools were GCC 14.2.0, CMake/CTest 3.31.6, Ninja
1.11.1.git.kitware.jobserver-1 and Python 3.12.14, Linux x86-64/glibc 2.41.
These eight requested targets produced seven executables and `nominal.b3p`,
plus three required project archives and generated documentary headers.
The complete build/install directory used **6,884 KiB**, below the 250 MiB cap.

The [graph receipt](../development/2026-11-16-preset-library-continuation/reports/a38-headless-graph.json)
and final listing show empty SDK roots and no native application, SDL
drawing/audio, RtMidi production or VST3 target. Every configured compilation
input belongs to this checkout. `hammond_standalone_support` still compiles its
host-independent Session, UI model, storage and MIDI adapters with the physical
backend disabled; their presence does not introduce a windowing SDK.
The selected compilation/link commands remain byte-identical after regeneration.

## Executed test inventory

CTest used an anchored exact-name selection, `--no-tests=error`, Release,
`--parallel 2` and `--output-on-failure`. Its JSON inventory was checked against
the following twelve names before execution; required executable inputs existed.
The [command receipt](../development/2026-11-16-preset-library-continuation/reports/a38-headless-tests.json)
retains the complete regex and environment. **12/12 passed in 5.50 seconds.**

| CTest | Observed checks or methods |
| --- | --- |
| `test_control_file_input` | 107 checks; links available |
| `test_control_io` | 2,240 malformed-input preservation cases |
| `test_standalone_registration_library` | 195 checks; links available |
| `test_standalone_state_files` | Seven scenarios |
| `python_test_registration_cli` | 14 methods / 76 processes |
| `python_test_registration_cli_admission` | 10 / 46 |
| `python_test_render_controls` | 18 / 109 |
| `python_test_render_controls_admission` | 5 / 45 |
| `python_test_starter_registration_generator` | 20 methods |
| `python_test_starter_registration_oracle` | 8 / 122 |
| `python_test_registration_install` | 10 / 208 |
| `python_test_render` | 39 methods |

All 124 Python methods passed without skips. The original detailed
[LastTest output](../development/2026-11-16-preset-library-continuation/reports/a38-headless-tests-detail.log.gz)
retains the native state-file suite's explicit untested POSIX replacement-failure
scenario after a complete temporary write. No stronger fault coverage is claimed.
The full configured suite was not run. The audition CTest was deliberately
unrun because its setup repeats all 32 clips, which root prohibited for this
assignment; the existing audition evidence keeps its original native inputs.

## Actual installation and runtime dependencies

Two explicit `cmake --install ../a38-headless --config Release --prefix PREFIX
--component COMPONENT` calls used the fresh `../a38-headless/a38-package` prefix.
`RegistrationTools` installed exactly **two files**, then `StarterRegistrations`
added exactly **26**. All 28 final names and hashes match their source inputs,
with no symlinks. The
[installation receipt](../development/2026-11-16-preset-library-continuation/reports/a38-headless-install.json)
retains each command and file identity. The installer CTest separately exercised
relocation after deleting its private source/build inputs; A35's native
relocation was not repeated as a new independent result.

An installed `inspect` of `02 Warm Comp.b3registration`, from an empty unrelated
cwd with only `LC_ALL=C` and nonexistent `PATH`, returned exit 0, one JSON line,
empty stderr, 24 valid entries and exact canonical expression `0.625`.
Installed bytes and cwd remained unchanged. This invocation had no display,
Python, profile or user-directory environment.

For all three tools, [ELF/link evidence](../development/2026-11-16-preset-library-continuation/reports/a38-headless-links.json)
shows only `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6` and loader
`/lib64/ld-linux-x86-64.so.2`; no RPATH/RUNPATH. Python and CMake support source
generation/build; neither is an installed CLI runtime dependency. The two
components do not bundle the renderer, profile or system runtime libraries.

## Retained observer failures and limits

Two A38 receipt checks initially failed: the installed-inspect wrapper used the
renderer field `canonical_b3controls4` instead of CLI `canonical_controls`; a
complete Ninja-listing equality assumption overlooked 60 first-configure CMake
probe prerequisites removed during cached regeneration. Both failures, original
outputs and the graph diff are retained. Corrected observation validates the
actual CLI payload and unchanged selected build/link commands; no product test,
contract or production source was changed.

This admits the observed Linux configuration and compatible runtime only.
Windows/macOS execution, arbitrary Linux ABI portability, native browser/device
acceptance, signed distribution, physical fidelity and literal whole-interface
1:1 remain separate gates. Root should update the guide's pending clean-headless
sentence to this bounded result; the installed guide retains its original hash.

# Assignment 23 — explicit standalone installation

Actual agent: `/root/w04_a23_standalone_install`; wave 4 of the independent
2026-11-13 sixty-assignment, ten-wave standalone session. No commits by this
worker. The integrating agent owns CMake registration and shared status files.

## Ownership and implementation

- `cmake/InstallStandalone.cmake`
- `apps/standalone/native_tests/test_standalone_install.py`
- `docs/STANDALONE_INSTALL.md`
- This assignment note.

The component installs exactly nine files, is `EXCLUDE_FROM_ALL`, and accepts
only an explicit `--component Standalone`. It copies the selected executable,
readable install/app/model guides, third-party notice, exact SDL2 and DejaVu
licenses, SDL2 lock and font source manifest. Profile and glyph bytes remain
embedded. No SDK, source fonts, research PDF or generated profile is staged.

Preflight rejects every missing, empty, symlink or nonregular input before the
first prefix write. License hashes and configured identity-record hashes are
checked. Existing executable or dedicated metadata destinations are refused,
including empty directories and dangling links. Unrelated OfflineTools paths
can coexist. Valid relative install directories, space/Unicode paths and COPY
mode are supported. This does not promise filesystem transaction atomicity.

## Source basis and tools

Observed integration base HEAD:
`738162f0bc36f88f8c76268d04831862a8118d10`. The installation files are this
assignment's additive working changes; that commit alone does not contain them.
The full gate used the strictly rebuilt Release application after the integrator's
path-alias fix: `../build-native-app/apps/standalone/hammond_standalone`, SHA-256
`648c8168e1d242f813d5ea333898aab4854c3979c82631a6a9fed91a50155078`.
Application `main.cpp` SHA-256:
`a10173c9b57434f7128c48628ce4c4cc467c9bc3618f0ec31884639ae9194698`.
Install module SHA-256: `7148f18cb15bc5cf8f9fffc7462be9f1f858e5a59c5442107c6493f4fbc5c370`.
Test SHA-256: `dac74e16fea2cffa05ec762c9d08bb302db1b412c2c6e84eeaa6c73612f65d9a`.
SDL2: locked 2.32.10, commit `5d249570393f7a37e037abf22cd6012a4cc56a71`.
The exact locked license is 884 bytes, SHA-256
`97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127`.
DejaVu accompanying license SHA-256:
`22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6`.

CMake executable: `/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake`.
Checks ran from `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ` with Python 3.12.

## Executed acceptance

The test environment supplied the CMake path above, `HAMMOND_TEST_CONFIG=Release`,
`HAMMOND_TEST_BUILD_DIR=/workspace/scratch/5ba97739b54c/build-native-app`,
`HAMMOND_STANDALONE_EXECUTABLE` equal to that build's `apps/standalone/hammond_standalone`,
`HAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2`,
`HAMMOND_INSTALL_BINDIR=bin`, `HAMMOND_INSTALL_DATADIR=share` and
`PYTHONDONTWRITEBYTECODE=1`.

```sh
python3 apps/standalone/native_tests/test_standalone_install.py \
  StandaloneInstallTests.test_preflight_rejects_private_bad_inputs_before_any_destination_write \
  StandaloneInstallTests.test_custom_directories_copy_mode_and_disabled_component -v
```

Result: **2/2 passed in 2.430 seconds**. These use the real module with private
copies of the actual binary/metadata; no shared product is renamed or changed.
An unselected configuration exists while the missing selected one is rejected.
Checks cover each missing input; an empty binary; directory, valid/dangling
symlink and FIFO inputs; changed licenses/identity records; non-COPY modes;
existing file/directory/dangling-link destinations; default-install exclusion;
disabled-component absence; Unicode/custom directories; and moved `--help`
after deleting the private fixture's source/build trees. No permissions test
is claimed in this privileged executor. Missing prerequisites fail the suite.

After the integrator regenerated native scripts and rebuilt the alias fix:

```sh
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest \
  --test-dir ../build-native-app -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_install$' -V
```

Result: **1/1 CTest passed in 2.68 seconds; 3/3 Python methods in 2.537 seconds**.
The real nine-file payload and source/license hashes matched before and after
moving. Relocated help and 600 ms dummy/dummy smoke ran from an unrelated cwd
with an invalid coexisting external profile: 56 callbacks, 28,672 frames, 23
rendered images, 960×700 BMP captured while held, observed press/release, peak
0.08312442898750305 and zero audio failures, error reports or Session faults.
Profile authoring hash: `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
Controls were not implicitly saved; source binary and installed files survived
unchanged. `git diff --check` passed. No shared executable/source input was modified.

## Limits and next evidence

Linux dummy audio/video and local relocation cannot qualify physical hardware,
native desktop accessibility, latency, deadline/underrun behavior or fidelity.
Windows/macOS execution, signed packaging, platform runtime deployment, the
complete applicable SDL/backend notice inventory and project distribution rights
remain unrun/separate. No project-wide license or redistribution clearance is
invented. The integrated source freeze must rerun the native-only CTest gate.

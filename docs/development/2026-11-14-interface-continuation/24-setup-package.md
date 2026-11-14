# A24 — Current interface guide and package/CI integration

Actual worker `/root/w04_a24_setup_package`, assignment 24/60, logical wave 4,
14 November 2026. The checkout HEAD was
`5d81199a9822874b55f3b0a124715cbd6eadf0e5`; the interface is a separately recorded
working overlay. HEAD alone does not identify the tested new UI. Root owns shared
status/README, `apps/standalone/CMakeLists.txt`, integration and publication.

## Owned changes

- Added `docs/INTERFACE_RUNBOOK.md`: installed/source entry points; real
  Play/Rotary/Service and Flat workflows; F4–F7 and startup options; 68 controls,
  71/10 focus sets, 24 preset keys and 147 playing keys; focus/held ownership;
  applied/desired and snapshot classifications; read-only physical unknowns;
  nonblocking MIDI discovery, explicit refresh and recovery; actual gallery and
  capture reproduction links with source/physical qualification limits.
- Reconciled current facts and links in `STANDALONE_APP.md`,
  `STANDALONE_MODEL.md`, `STANDALONE_INSTALL.md` and `PRESET_RUNBOOK.md`.
  The model guide now identifies 47 parameters, state4/readers 1–3 and exclusive
  fixed selection; the preset guide identifies 71 Play/10 other focus stops and
  excludes workspace/presentation/focus from saved controls. Earlier retained
  galleries and historical evidence were not edited.
- Added both current runbooks to `cmake/InstallStandalone.cmake`, the independent
  `SOURCE_FILES`/`GUIDES` inventories in `test_standalone_install.py`, and the
  workflow's expected payload. Kept exact cardinality, ordinary-file admission,
  configured hashes, overwrite refusal, destination preservation and byte checks.
  Relocated `--help` now also must expose `--workspace` and `--flat`.
- Added the eight actual workspace/inspection/projection/MIDI-discovery/native
  drawing/replay names to `.github/workflows/standalone.yml`'s required set.
  `test_standalone_workspaces_author` is the actual plural filename/test name.
  No future gate names were invented; later CI inventory work can add newly
  implemented tests.

No production UI/audio/core, parameter/state, VST3, profile, license, atlas or
retained asset was changed by this assignment. No files were staged or committed.

## Exact package count

The [source inventory](reports/a24-inventory.json) compares all three inventories
and checks every installed relative guide link. The CMake module now starts with
**13 metadata source/name pairs**, then appends one generated capability file.
That is **14 common metadata files + one executable = 15 files** with MIDI off.
The enabled path adds exactly four RtMidi records: **19 files** with MIDI on.
The six operating/setup/model guides and the notice file all participate in
the installed-guide link gate. No runtime asset or extra license copy was added.

The configured native build discovers **35 standalone tests**, including all
**18 required workflow names**. This is discovery evidence; only the focused
install suite below was executed by A24. Workflow YAML and all six embedded
Python blocks parse successfully. Hosted jobs were not dispatched or claimed.
An initial ad hoc inventory probe selected an earlier unrelated `required` set;
its local Python parse failed before any build/mutation. Restricting the probe to
the standalone-test literal produced the retained passing inventory.

## Commands and actual gate

Working directory:
`/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
A22 explicitly released its capture freeze before configure. Root granted
exclusive use of the existing sibling `build-native`; it was released after
the focused gate and after-hash checks. No new repository, SDK copy or native
build tree was created.

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/601951e27dc3/Hammond-B3-Organ \
  -B /workspace/scratch/601951e27dc3/build-native \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_ENABLE_MIDI=ON -DSDL_ALSA=OFF

/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/601951e27dc3/build-native --config Release \
  --target hammond_standalone --parallel 3

/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native -C Release \
  --show-only=json-v1 -R '^test_standalone_'

/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native -C Release \
  --verbose --output-on-failure --no-tests=error -R '^test_standalone_install$'
```

Configure and build returned 0. The guide edits preceded reconfiguration, so
strict install metadata contains their final bytes. The native gate passed
**1/1 CTest suite, eight unittest methods**, in **7.09 s**. The
[complete verbose log](reports/a24-install-ctest.txt) retains the actual relocated
application diagnostics. Its 19-file MIDI-on/ALSA payload passed exact inventory
and source hashes, installed links, ordinary input/destination admission,
selected-configuration behavior, custom relative directories, copy mode,
overwrite refusal and source-unavailable fixture relocation. Missing/empty or
changed inputs include both new guides through the unchanged all-input loops.

The relocated real executable passed `--help` and a 600 ms 960×700 SDL dummy
audio/video smoke from an unrelated directory. Embedded profile/image checks,
held/release observations, joined shutdown and unchanged payload checks passed;
application error count was zero. No MIDI input was selected or enumerated by
that smoke. The disabled-MIDI install-rule fixture passed its exact 15-file
inventory without a dependency checkout or SDK lookup. That fixture uses the
actual enabled binary as a copied input; it does not qualify a separately built
MIDI-disabled runtime.

The reused cache identifies CMake 4.4.4, GCC 14.2.0, Python 3.12.14, Unix
Makefiles/Release, standalone ON, VST3 OFF, MIDI ON with RtMidi ALSA and
`SDL_ALSA=OFF`. It reuses SDL2 at
`/workspace/scratch/7ffc2842608b/SDL2`, RtMidi at
`/workspace/scratch/cd4bd06ce68f/rtmidi`, and the existing ALSA include/library
inputs beneath `/workspace/scratch/641ca55ce6de/native-sysroot/usr/`.
This configure command intentionally reuses that admitted cache; fresh setup is
documented in the installed guides, including platform prerequisites.

## Identities and remaining qualification

The [result report](reports/a24-setup-package.json) retains exact commands,
toolchain, nine relevant source hashes, all 18 enabled metadata source hashes,
log hashes and limits. The [before record](reports/a24-source-before.json),
[configure log](reports/a24-configure.txt) and [build log](reports/a24-build.txt)
remain available. Executable SHA-256 before and after was unchanged:

`005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364`.

All **114 protected files** in A12's boundary manifest matched their original
SHA-256 before and after the gate. The nine scoped source inputs also remained
unchanged through configure/build/test. No hash is treated as an independent
rebuild attestation; the current gallery and A20 author qualification retain
their own exact source/binary boundary.

A29's separately configured MIDI-off runtime/relocation, later packaged workspace
replays, the final coherent UI matrix and later hosted source remain separate
work. Physical audio/MIDI devices, native display/DPI/pointer capture, deadlines,
screen-reader integration, scanner/AO-28/Leslie connections, specimen calibration,
literal 1:1 reference equality, licensing/signing and release distribution are
not qualified by this local copying/dummy gate. Any later installed-guide edit
requires reconfigure before installation so the strict hash check remains valid.

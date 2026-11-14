# A26 — standalone MIDI and reference-art staging

Actual worker: `w05_a26_midi_packaging`, wave 5 of the separate requested
`2026-11-14-midi-ui` session. This records this assignment only; no earlier worker
is counted again.

## Owned scope and source boundary

Owned files:

- `cmake/InstallStandalone.cmake`
- `apps/standalone/native_tests/test_standalone_install.py`
- `THIRD_PARTY_NOTICES.md`
- `docs/STANDALONE_INSTALL.md`
- This evidence note.

Read `AGENTS.md`, the current entry points/scopes, existing installation module
and acceptance, SDL/font/reference identity records, atlas extraction/rights
records, RtMidi lock/preparation contract and target-property integration. The
observed repository HEAD was `e09107414896c2c53dad124a74f60c8043fadfe4`; concurrent
uncommitted work was present. This is not a claim that that commit already
contains the tested changes. No shared build was reconfigured or compiled by
this worker. No commits, subagents or edits outside the owned repository paths
were authored.

Root owns the root/application CMake wiring. Root supplied the additional CTest
environment for configured MIDI capability and the actual RtMidi target's
`HAMMOND_RTMIDI_PREPARED_ROOT` / `HAMMOND_RTMIDI_BACKEND` properties. A27 owns the
installed application/model/runbook guides. Final A27 guide bytes were copied
only after its explicit freeze:

| Guide | SHA-256 |
| --- | --- |
| `STANDALONE_APP.md` | `2f6d76e94ad16fbde2192e97bc7bb852b26620423155d03e2fccaeb283c34bab` |
| `STANDALONE_MODEL.md` | `a68ca7d836050f687ba0ec87933f7f3c0417356a03bf6d75aacfdf1409ed9051` |
| `MIDI_UI_RUNBOOK.md` | `bc088e41621a0fa5363b3206e1ca71bbf4518a0492f46d842c415ab116bb779d` |

## Implemented staging contract

The common payload is **13 files**: the selected executable, the existing eight
metadata files, and four additions: `MIDI_UI_RUNBOOK.md`,
`reference-source-manifest.json`, `atlas-reference.json` and
`standalone-capabilities.json`. The reference manifest and extraction record
preserve exact crop/source identities, page locators and evidence class; the
always-installed notices retain the unresolved use/publication-rights boundary.
No PDF, source JPEG, raw crop or authoring font is copied as a separate runtime
asset.

An explicitly MIDI-enabled build adds exactly four files, for **17 total**:
`LICENSE-RtMidi.txt`, `rtmidi-lock.json`, `rtmidi-prepared-source.json` and
`rtmidi-coremidi-zero-init.patch`. The license comes from the verified prepared
copy and remains byte-identical to the pinned upstream notice. The preparation
record contains the entire lock, prepared file identities and preparation-tool
hash; the exact patch preserves the two-allocation initialization correction.
The original or prepared C++ source/header is not installed.

The config-independent capability record is generated at
`${CMAKE_CURRENT_BINARY_DIR}/generated/standalone-capabilities.json`. It records
exact configured SDL/font/reference identities and either the actual selected
RtMidi backend/prepared identities or `enabled=false`, `backend="unavailable"`,
`rtmidi=null`. It contains no build or checkout paths. It describes compilation,
not device/service availability. Generation and installation never discover a
MIDI SDK, acquire a dependency, enumerate ports or construct a native MIDI input.
A disabled package has no RtMidi metadata inputs or conditional notice files.

All original fresh-destination rules remain. Installation uses the selected
binary's unchanged bytes, rejects a pre-existing binary or dedicated metadata
path, rejects symlink/non-directory ancestors, honors relative configured
install directories and copy-mode rules, and retains multi-configuration
selection guards. Before its first destination write, it checks **and reads**
every input as a nonempty ordinary file. It freezes all configured metadata
hashes, including guides and capability JSON, with reviewed license/patch hashes
as additional identity constraints. Missing, changed, empty, symlinked or special
metadata cannot leave an admitted partial payload.

Metadata paths are `CMAKE_CONFIGURE_DEPENDS` inputs. A normal rebuild refreshes
intentionally changed documentation; direct installation with stale configured
metadata fails. Preflight remains read-only, and there is no claim of atomicity
against later disk errors or concurrent filesystem mutation.

The install guide now works from a complete moved prefix, identifies optional
backend availability, lists the exact common/conditional inventory and links to
installed siblings or explicit repository URLs. Root-level notices likewise use
explicit repository links where their targets are not installed. A27 supplied
matching link and current-MIDI corrections in its three guides.

## Independent maintained acceptance

The Python suite now has **eight methods**. It independently inventories the
actual package, validates exact retained dependency/reference/preparation
relationships, checks installed guide links, and compares packaged MIDI
capability with the relocated executable's diagnostics. The existing binary,
profile, SDL version, image, audio, state and shutdown assertions remain. The
native diagnostics expectation is updated from the previous schema 1 to the
current exact schema 2.

Private fixtures exercise every input missing and empty, every metadata file
changed after configuration, reference/capability/enabled-MIDI records replaced
by directories, symlinks, dangling symlinks and POSIX FIFOs, source-binary
preservation, selected-configuration failure, excluded ordinary installation,
copy modes, existing destination kinds, ordinary destination ancestors and
custom relative Unicode/space paths. A disabled-MIDI fixture omits every RtMidi
input and explicitly disables ALSA/thread package lookup. The latter checks
install-rule selection only; the actual disabled executable below separately
establishes runtime/configuration agreement. The tests never rename shared build
products or silently skip a missing prerequisite.

## Executed verification

Toolchain: Linux, GNU C/C++ 14.2.0, Python 3.12.14, CMake/CTest 4.4.4 at
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin`.
SDL2 source was the existing pinned checkout at
`/workspace/scratch/7ffc2842608b/SDL2`. All work below was private to
`/workspace/scratch/cd4bd06ce68f/a26-packaging-check`.

| Executed check | Observed result |
| --- | --- |
| Final enabled installation suite around a private copy of the real shared ALSA executable | **8/8 methods pass**, 7.118 seconds; exact 17-file inventory and all final guide links. |
| Fresh full-project native build with `HAMMOND_ENABLE_MIDI=OFF`, absent RtMidi root and disabled ALSA lookup | Configure/build pass; actual unavailable-backend executable produced. |
| Maintained CTest installation gate against that actual disabled build | **1/1 CTest suite, 8/8 methods pass**, 5.916 seconds in Python / 6.06 seconds CTest total; exact 13-file inventory. |
| Relocated enabled and disabled application smoke | Both 600 ms SDL dummy audio/video runs pass from unrelated directories, after prefix moves; 960×700 actual images, embedded profile identity, clean audio/error counters and unchanged payload/source bytes. |
| Enabled relocated capability | `backend_available=true`, `backend="ALSA"`, no selected/opened port or callback messages; state remains closed. |
| Disabled relocated capability | `backend_available=false`, `backend="unavailable"`, no selected/opened port or callback messages; state remains unavailable. |
| `python3 -m py_compile apps/standalone/native_tests/test_standalone_install.py` | Pass during implementation; the final script is additionally executed completely by both passing suites. |
| Owned-file `git diff --check` | Pass. |
| Additional private `Ninja Multi-Config` configure | **Setup blocked**: Ninja build program absent; no multi-config run was claimed and no dependency was acquired. |

Both actual relocated runs reported SDL 2.32.10, 56 audio callbacks / 28,672
rendered frames, 16 rendered images, held/release observations, no post-shutdown
held notes and zero counted audio/application errors. Those measurements are
specific dummy-backend observations, not device-performance requirements.

### Disabled build commands and frozen source

The source was copied into `native-source`, excluding Git metadata and Python
bytecode caches. Its retained inventory contains 1,117 files. Only final
`STANDALONE_APP.md`, `MIDI_UI_RUNBOOK.md` and the test oracle changed after the
initial source snapshot; compiled source/header inputs remained byte-identical.
The final retained source inventory, `native-final-source-files.json`, has
SHA-256 `ebd3b3115a64b7e27c7ff129436070faed1a816aeec7e01caed5873f8c9647ae`.
Generated Python caches are excluded from this retained inventory.

With `cmake`/`ctest` denoting the exact tools above, these were executed:

```sh
cmake -S /workspace/scratch/cd4bd06ce68f/a26-packaging-check/native-source \
  -B /workspace/scratch/cd4bd06ce68f/a26-packaging-check/native-off \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 \
  -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/a26-packaging-check/absent-rtmidi \
  -DCMAKE_DISABLE_FIND_PACKAGE_ALSA=TRUE \
  -DSDL_ALSA=OFF -DSDL_DUMMYAUDIO=ON -DSDL_DUMMYVIDEO=ON
cmake --build /workspace/scratch/cd4bd06ce68f/a26-packaging-check/native-off \
  --config Release --target hammond_standalone --parallel 3
# After copying A27's final guides and the final test oracle into native-source:
cmake -S /workspace/scratch/cd4bd06ce68f/a26-packaging-check/native-source \
  -B /workspace/scratch/cd4bd06ce68f/a26-packaging-check/native-off
ctest --test-dir /workspace/scratch/cd4bd06ce68f/a26-packaging-check/native-off \
  -C Release --output-on-failure --no-tests=error -R '^test_standalone_install$' -V
```

The logs are `native-off-configure.log`, `native-off-build.log`,
`native-off-final-configure.log` and `native-off-install-check.log` in the private
check directory. The shared enabled executable was not rebuilt or altered.

### Enabled staging command and identities

The suite's own `fixture()` helper configured the real install modules around
private copies of the built executable, source notices/guides and the actual
prepared RtMidi metadata. The imported target exposes the actual `ALSA` backend
and prepared-root properties; there is no synthetic replacement executable.
The frozen source copy also includes the suite and nominal authoring profile.
The effective final child command was:

```sh
python3 /workspace/scratch/cd4bd06ce68f/a26-packaging-check/final-enabled/source/apps/standalone/native_tests/test_standalone_install.py -v
```

Its environment used `HAMMOND_TEST_CONFIG=Release`, `HAMMOND_INSTALL_BINDIR=bin`,
`HAMMOND_INSTALL_DATADIR=share`, `HAMMOND_TEST_ENABLE_MIDI=ON`,
`HAMMOND_RTMIDI_BACKEND=ALSA`, `PYTHONDONTWRITEBYTECODE=1`, the exact CMake tool
above, and these private paths:

| Environment input | Path beneath `a26-packaging-check/final-enabled` |
| --- | --- |
| `HAMMOND_TEST_BUILD_DIR` | `build` |
| `HAMMOND_STANDALONE_EXECUTABLE` | `build/Release/hammond_standalone` |
| `HAMMOND_SDL2_ROOT` | `SDL2 source` |
| `HAMMOND_STANDALONE_CAPABILITIES` | `build/generated/standalone-capabilities.json` |
| `HAMMOND_RTMIDI_PREPARED_ROOT` | `prepared RtMidi` |

Exact environment values and output are retained locally in
`final-enabled/test-environment.json` and `final-enabled/final-checks.log`.
This qualifies staging and relocated execution of the named existing ALSA
binary, not a new full enabled source compilation by A26.

| Tested artifact/input | SHA-256 |
| --- | --- |
| Enabled executable | `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d` |
| Fresh disabled executable | `be3a7f2f418a1c195c6c992386d3dd364726866be9b8bb33c25ac30ba7631495` |
| Enabled capability JSON | `57ccbbb25c2f868db64ff7aa17cf691e9fd92917b2e640b4fd1d5a623edcbc48` |
| Disabled capability JSON | `0aa7e692d1986def4e8f5f31f0104e49ec1e50dca162fb2a14343f458a6bb204` |
| RtMidi lock | `4e2923a57abfaa98d68d7b339ea9a39c420f40dc3b175a339be108eaf0a987aa` |
| RtMidi preparation manifest | `481095a20040ffe8c824200b3b20663ebc4c392f1fc535ead7f6e679f3a5b2ae` |
| `cmake/InstallStandalone.cmake` | `40471b704ddadb10a6d626b4c01e2683f6384064031e6cef5d0a39264f9b1982` |
| Installation acceptance script | `ca23d29d16f9affcda8dce254a5735fc51b721a0dfd3abf2b2174f35e3193c92` |
| `THIRD_PARTY_NOTICES.md` | `66d493ae0799798e4957fbcba299186c8d48e899b86846fc0bb2d7b7a92a96bb` |
| `STANDALONE_INSTALL.md` | `6e758ecca26ef8cb1fc4a39aed2c138b0de6f16f97ab7711f598d832dc1b8e75` |

## Original failures and limits

The first private run correctly exposed an old relative source link in a
pre-freeze A27 guide, and four new assertion failures caused by CMake wrapping a
long destination-parent diagnostic across lines. The installed destination was
correctly rejected in all four cases. The assertion now normalizes whitespace;
final guide bytes resolve only retained relative targets. A subsequent run
reached the actual relocated application and exposed the obsolete diagnostic
schema-1 oracle. Updating to exact schema 2 preserves the original substantive
assertions; the final 8/8 results above include the runtime checks. Earlier logs
remain in `initial-enabled/checks.log` and `final-enabled/checks.log`.

The optional additional multi-config command was:

```sh
cmake -S /workspace/scratch/cd4bd06ce68f/a26-packaging-check/final-enabled/source \
  -B /workspace/scratch/cd4bd06ce68f/a26-packaging-check/multi-enabled \
  -G 'Ninja Multi-Config'
```

It failed before configuration because `CMAKE_MAKE_PROGRAM` could not resolve
Ninja; `multi-enabled-configure.log` retains that setup failure. Maintained
acceptance adds no Ninja requirement or capability skip: its actual configured
build branch checks complete single-config payloads or multi-config destination
preservation as appropriate. This assignment executed the single-config branch.

Windows/WinMM, macOS/CoreMIDI, native desktop rendering, physical audio/MIDI,
latency/hotplug, system runtime bundling, signing and redistribution clearance
were not run or closed. Reference-art publication permissions remain unresolved.
The capability JSON does not attest to physical input availability. The new
package is a local byte-preserving payload, not a signed or self-contained system
runtime installer.

## Integrator handoff

Root should qualify the maintained install test after reconfiguring the final
coherent enabled build with the supplied CTest environment. A30 should use the
exact **13-file disabled / 17-file enabled** inventory listed in
[STANDALONE_INSTALL.md](../../STANDALONE_INSTALL.md); conditional RtMidi files
must not be silently accepted in an unavailable-backend artifact. Root owns
shared status/ledger, final platform results and publication. This assignment
introduces no changes to Engine, public parameter IDs, control-state formats or
runtime MIDI behavior.

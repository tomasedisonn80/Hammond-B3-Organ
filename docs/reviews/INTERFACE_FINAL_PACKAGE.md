# Final native interface package qualification

Actual assignment **A44**, worker `/root/w08_a44_final_package`, logical wave 8,
14 November 2026. **Passed for the two identified Linux Release packages.**
Both real component installations preserve their exact 19-file MIDI-on and
15-file MIDI-off contracts. Their relocated applications run with the checkout,
both builds, SDL, RtMidi and the ALSA development sysroot absent from a private
mount namespace. A subsequent, separately recorded guide refresh changes only
the intended MIDI guide bytes; the qualified executables remain unchanged.

The [final result](../development/2026-11-14-interface-continuation/reports/a44-final-package-result.json)
connects the original [runtime package result](../development/2026-11-14-interface-continuation/reports/a44-runtime-package-result.json)
to the [final metadata refresh](../development/2026-11-14-interface-continuation/reports/a44-package-refresh.json).
They are separate observations. The refreshed guide was not present in the
earlier runtime captures, and no later documentation or configuration edit is
silently called unchanged.

## Qualified source and executable identities

At configure/build/runtime qualification, HEAD was
`8673713a484c40e26ac7810c7c4cbc22fa874426`, committed tree
`e11bd68d6051f663631579ef235325a8775f8133`. All 98 production, asset and source-data
inputs match that commit; there was no production overlay. The complete
[before snapshot](../development/2026-11-14-interface-continuation/reports/a44-source-before.json)
and [input comparison](../development/2026-11-14-interface-continuation/reports/a44-input-comparison.json)
identify those bytes. Their sorted path/NUL/SHA-256/LF inventory digest is:

`ddf4f7658cfa9ed49ddac87902788c65531697551faab4dadd1dd57709d9e9ad`.

Compared with A29's earlier 98-input runtime, exactly four production files
changed: `Drawing.cpp`, `InstrumentView.cpp`, `UiModel.cpp` and `main.cpp`.
The qualified source includes the accepted raster repair, A34's accidental-label
and title correction, and A36's truthful live-Load message. The product inventory
remained constant through both builds, the installed runtime probes and the
later guide refresh. All **114 protected files** match A12's retained boundary.

| Configuration | Final executable SHA-256 | Bytes | Compiled MIDI |
| --- | --- | ---: | --- |
| MIDI on | `bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2` | 3,707,640 | `HAMMOND_HAS_RTMIDI=1`, RtMidi ALSA |
| MIDI off | `a09c9127b54ad1efae1ba0c332e4fecff5385d27a834a24ad6c3f7b47d474117` | 3,624,104 | `HAMMOND_HAS_RTMIDI=0`, unavailable |

The enabled executable is byte-identical to A36's pinned final binary. Its one
target build correctly found the product up to date. The distinct disabled
target rebuilt the changed inputs once and linked its own executable. The
[build record](../development/2026-11-14-interface-continuation/reports/a44-build-result.json)
retains exact configuration commands, flags, generated resources, libraries,
executable hashes and logs. MIDI-off is a real disabled runtime, not an enabled
executable copied into a disabled package fixture.

The [toolchain record](../development/2026-11-14-interface-continuation/reports/a44-toolchain.json)
identifies CMake/CTest 4.4.4, GCC 14.2.0, Python 3.12.14 and bubblewrap. Both builds
reuse Unix Makefiles/Release, testing and standalone ON, VST3 and sanitizers OFF,
and `SDL_ALSA=OFF`. SDL 2.32.10 is shared from the established checkout; the
enabled build uses the established RtMidi source and ALSA headers/library.
The disabled cache has no RtMidi root. No SDK or source checkout was copied.

## Executed gates and precise counts

| Gate | MIDI on | MIDI off |
| --- | --- | --- |
| Existing `test_standalone_install` CTest suite | 1/1 suite; 8 unittest methods, 7.36 s | 1/1 suite; 8 unittest methods, 6.54 s |
| Final independent relocated application invocations | 4 expected outcomes | 4 expected outcomes |
| Actual metadata/executable inventory before and after movement | 19 exact ordinary files | 15 exact ordinary files |
| Source/build/SDK/sysroot absence proof | Passed | Passed |
| Native screenshot | Play, dimensional, 960×700 | Service, Flat, 960×700 |
| Live Load and six-view UI replay | Passed, unchanged private state bytes | Passed, unchanged private state bytes |
| Final guide refresh | Exact inventory and movement only | Exact inventory and movement only |

The complete install logs retain [MIDI-on](../development/2026-11-14-interface-continuation/reports/a44-midi-on-install-ctest.txt)
and [MIDI-off](../development/2026-11-14-interface-continuation/reports/a44-midi-off-install-ctest.txt)
results. These **two suites / sixteen unittest methods** preserve the existing
strict package gates: configured source hashes, ordinary inputs/destinations,
complete cardinality, destination preservation and overwrite refusal,
configuration selection, custom relative locations, copy mode, guide links,
private negative fixtures and actual installed application smoke. A44 did not
repeat the full core or standalone test matrix.

The final independent probe has **eight native application invocations**:
`--help`, invalid workspace admission, a 600 ms native smoke/capture and a
1700 ms navigation/live-Load replay for each build. Help and usage rejection use
deliberately invalid SDL drivers and write no outputs. Invalid workspace returns
the documented usage exit **2**. The two successful runtime modes use explicit
SDL dummy audio/video and select no MIDI input.

## Actual runtime without source or development dependencies

The [MIDI-on relocation record](../development/2026-11-14-interface-continuation/reports/a44-midi-on-relocation.json)
and [MIDI-off relocation record](../development/2026-11-14-interface-continuation/reports/a44-midi-off-relocation.json)
retain each command, return code, output, capability, inventory and hash.
The real CMake `Standalone` component was installed to a new prefix, that prefix
was moved, and the original destination ceased to exist. The namespace mounts
the moved prefix read-only at `/app`, a private writable directory at `/run-work`,
system runtime directories and private `/tmp`, `/dev` and `/proc`. It starts in
the unrelated private working directory.

An executed Python probe inside each namespace confirms that all seven named
source/build/dependency/original-prefix paths are absent. Shared source and SDK
directories were never renamed or deleted. The installed application consumes
only the private state/replay inputs, and writes diagnostics and the capture
to that private directory. Its embedded nominal profile, fonts and reference
decoration therefore cannot be supplied by a visible checkout.

**The enabled binary retains its existing development RUNPATH.** Before
isolation it resolves `libasound.so.2` through the shared ALSA sysroot. Inside
the namespace that path does not exist; `ldd` resolves the system
`/lib/x86_64-linux-gnu/libasound.so.2`, and actual application loader diagnostics
confirm that library's initialization. The [enabled loader log](../development/2026-11-14-interface-continuation/reports/a44-midi-on-smoke-loader.txt)
retains the unavailable development lookups and successful system initialization.
The [disabled loader log](../development/2026-11-14-interface-continuation/reports/a44-midi-off-smoke-loader.txt)
has neither an ALSA dependency nor a development RUNPATH lookup. Both binaries
use the system loader and C/C++/math runtime libraries. This is a qualified
fallback on this system, not a claim that the payload bundles every platform
runtime or runs on a machine missing the required libraries.

All successful native probes report the actual SDL 2.32.10 software renderer,
real dummy audio callbacks and nonzero frames/images, the embedded
`nominal-unmeasured-v1` profile, zero render/format/nonfinite/overrange failures,
zero application errors, stopped/unheld Session state after shutdown, quiescent
MIDI and stable final diagnostics. MIDI source remains `none`; there are zero
native packets, callbacks, physical open failures or discovery starts. The
enabled backend reports ALSA/closed and the disabled backend unavailable.

The navigation replay preserves the exact noncanonical state4 file, all four
banks and Upper F#/Lower G# fixed choices. It holds one computer note through
Play → Rotary → Rotary Flat → Service Flat → Play Flat → Play, performs live
Load, and releases the original owner. Both modes accept exactly one Note On
and one Note Off, preserve controls, keep an increasing frame clock and finish
with **“Loaded saved controls.”** No saved presentation or audio-state migration
is introduced by those view changes.

## Captures and package contents

The actual [relocated Play capture](../development/2026-11-14-interface-continuation/reports/a44-midi-on-relocated-play.png)
shows the complete minimum-size instrument and common title/header with MIDI
not connected. The actual [relocated Service Flat capture](../development/2026-11-14-interface-continuation/reports/a44-midi-off-relocated-service.png)
shows six inspection cards, a current copied snapshot and the MIDI-unavailable
footer. Both were visually inspected. Their diagnostics identify the view at
the screenshot, with a held observation and later successful release. PNG
conversion preserves the decoded BMP pixels; that check concerns file
conversion only, not equality with the atlas reference. Only these two PNGs are
retained, and the reproducible BMPs were removed.

| Payload group | MIDI off | MIDI on |
| --- | ---: | ---: |
| Actual executable | 1 | 1 |
| Six setup/application/model/MIDI/preset/interface guides | 6 | 6 |
| Third-party notices | 1 | 1 |
| SDL and DejaVu licenses | 2 | 2 |
| SDL lock, font/reference manifests, atlas provenance, capability JSON | 5 | 5 |
| RtMidi license, lock, prepared-source manifest and preparation patch | 0 | 4 |
| **Total** | **15** | **19** |

Every metadata file matches its named source bytes, and each of the **30**
installed relative guide links resolves. Capability hashes agree with the
installed notices/manifests/licenses; MIDI enablement agrees with the actual
compiled runtime. No source tree, SDK, PDF, build cache or extra binary enters
the payload.

## Separately qualified final guide refresh

After A44 released the runtime guide freeze, A45 identified current MIDI-guide
text that still described 45 controls, state3 and superseded PLAY A/B/Cancel
controls. Root reviewed and applied ten exact replacements. A44 then observed:

| Input | Runtime qualification | Final package refresh |
| --- | --- | --- |
| `docs/MIDI_UI_RUNBOOK.md` | `bc088e41621a0fa5363b3206e1ca71bbf4518a0492f46d842c415ab116bb779d` | `f51b2c32f5f6e6aa062885bd2b1b64fee24faf85712f4bca9a3b8f1a600695a1` |
| `apps/standalone/CMakeLists.txt` | `6661ddf975af37b0b8720140afa857b6537c069d07f388ce0e8524befed97ffe` | `6b75fe8c73e4927b5fbe3c78e3ab7f88c92ba3f49eb2a5d3df269412cca1abc8` |

The CMake edit is root's separately owned sanitizer-conditional raster-test
budget allowance. Reconfiguration of both ordinary Release caches preserves
actual CTest TIMEOUT properties **60 / 60 / 30 seconds** for workspace raster,
scaled view and preset raster, respectively. The retained discovery JSON
records those three properties without executing or rebuilding those targets.

Fresh configuration renewed the strict install-time guide hash, then two new
complete component installations were moved and compared. Exactly one payload
entry changed: `MIDI_UI_RUNBOOK.md`, by **1,030 bytes**. Every executable,
capability file, other guide, notice, license and identity record is byte-equal
to its earlier qualified payload. Final package sizes are **3,854,706 bytes**
with MIDI on and **3,765,285 bytes** with MIDI off. No app rebuild, native replay
or CTest-suite rerun was needed or claimed for this metadata-only refresh.

The final prefixes are under
`/workspace/scratch/601951e27dc3/a44-final-packages-docs/`, with separate
`midi-on/relocated final Ω` and `midi-off/relocated final Ω` directories.
Earlier runtime prefixes remain separately identified under
`a44-final-packages-runtime/`. No compiled binaries are staged in the repository.

## Retained failures, reproduction and limits

The [correction record](../development/2026-11-14-interface-continuation/reports/a44-probe-corrections.json)
retains three harness/setup findings. First, CTest 4.4.4 omitted an older
summary phrase after a successful eight-method suite; the parser was corrected
and the unchanged suite was not rerun. Second, the new CLI probe initially
expected exit 1 for a usage error; the actual correct exit 2 was retained and
the expectation corrected. Third, optional `strace` failed with
`PTRACE_TRACEME`/`PTRACE_SETOPTIONS: Operation not permitted` before producing
native diagnostics. The final probe uses working namespace isolation and
ordinary loader diagnostics. No application source was changed for these
findings. Four additional CLI invocations from the two aborted preparations
are retained separately from the eight final runtime invocations; the blocked
tracer is not a successful native run.

The owned failed stages were removed only after their full payload identities
and original failure records were retained. They released 7,707,352 bytes.
Approximately 39.46 GB remained free after cleanup. The shared builds and source
were preserved; both A44 build leases were released after the final metadata
refresh.

Reproduction uses the retained [build driver](../development/2026-11-14-interface-continuation/reports/a44-build-packages.py),
[isolated relocation driver](../development/2026-11-14-interface-continuation/reports/a44-qualify-relocation.py)
and [one-change refresh driver](../development/2026-11-14-interface-continuation/reports/a44-refresh-package-docs.py).
Commands, prerequisite paths and fresh destination requirements are in their
reports and the [assignment note](../development/2026-11-14-interface-continuation/session44-final-package.md).
The refresh driver intentionally asserts the two recorded guide/configuration
snapshots; it is a replay of this transition, not a generic future updater.

This is local Linux Release qualification with explicit dummy audio/video,
not a physical controller/audio result, persistent desktop/pointer or DPI test,
callback deadline, screen-reader result, host qualification, signed installer,
distribution-rights clearance, measured organ model or 1:1 reference-image pass.
The normal system runtime-library requirements remain. Future product changes
require affected native qualification; a later intentional metadata-only change
requires reconfiguration and a fresh exact-inventory install. Root owns shared
documentation, accounting, integration and publication.

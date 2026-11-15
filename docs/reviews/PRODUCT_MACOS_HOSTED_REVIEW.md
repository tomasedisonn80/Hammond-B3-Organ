# Product macOS hosted review

**Result: the two assigned macOS jobs pass at the exact published product source.**
This is A51's independent primary-log audit on 15 November 2026. It qualifies
core Release, native Standalone Release, the expanded calibration/raster
fixtures and the installed CoreMIDI package. VST3 belongs to A52.

## Source and primary evidence

The queried [commit d8c39f7](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/d8c39f7986746eacc991747153c7dbb012bb9a32)
is `d8c39f7986746eacc991747153c7dbb012bb9a32`, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`, parent
`d556da017ea0a5d4f2d231416782dbc5066e58c2`. Commit, Git-tree, main-ref, run,
job-collection and artifact API responses agree with the local HEAD/tree.
The checkout also contains later integrator-owned work; this audit does not
qualify those dirty files. In particular, the working CI workflow differs from
the audited commit. All inspected native inputs match their committed bytes.

| Primary job | Observed outcome |
| --- | --- |
| [CI 43668397337 / job 132672792051](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337/job/132672792051), Release (macOS AppleClang) | Attempt 1; completed success at 02:37:53 UTC. **155/155 CTest**, 120.47 s. |
| [Native standalone 43668397338 / job 132672792209](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/job/132672792209), macOS AppleClang, MIDI ON | Attempt 1; completed success at 02:42:11 UTC. **48/48 discovered Standalone tests**, 312.67 s; post-test verification, install/relocation/archive and artifact upload also succeeded. |

A fresh run-level query at **02:47:04 UTC** reports both workflows completed
successfully. This does not replace the other workers' detailed platform audits.
The [bounded primary receipt](../development/2026-11-15-product-continuation/reports/A51-macos-primary.json)
retains API identities, source hashes, individual selected results, exact
timestamped log excerpts and their original line numbers. Counts were checked
against **155 and 48 distinct pass records**, not inferred from old runs.

## Actual toolchain and configuration

Both jobs used **macOS 15.8.2, build 24H232, arm64**, runner image
`macos-15-arm64` `20261104.0514.1`; AppleClang
**17.0.0.17000013** (banner `clang-1700.0.13.5`, Xcode 16.4);
**CMake/CTest 4.4.5**, **Python 3.12.10**, Unix Makefiles and Release.

Core configured the Release preset, built all its targets with parallelism two,
then ran `ctest --preset release --parallel 2 --timeout 300 --no-tests=error`.
The observed crossover native, allocation, lifecycle, reference, acceptance and
install gates all passed; `python_test_crossover_install` took **3.02 s**.

Native explicitly enabled Standalone, testing and MIDI, disabled VST3, and used
locked external SDL2/RtMidi. It built the application and
`hammond_standalone_test_inputs`, discovered the required names, and ran
`ctest --test-dir build-standalone -C Release -V --parallel 1 --no-tests=error --timeout 180 -R '^test_standalone_'`.
The successful compiler/backend assertion step required **Cocoa, CoreAudio and
both dummy SDL backends**. Runtime test environment selected **dummy audio and
video**. These are Release results, with no macOS sanitizer qualification.

## Executed feature acceptance

| Gate | Observed macOS result |
| --- | --- |
| Native calibration | **9 Python methods**, 20.426 s; **10 subprocesses, 7 native lifecycles and 2 deliberately failed replays**; CTest 20.61 s. All nine methods report `ok`. |
| Expression diagnostics | **4 Python methods**, 2.920 s; CTest 3.16 s. |
| A42 material fixture | **1,293 checks, zero failures, 109 frames**, CTest 3.96 s. Preserves 901 legacy + 170 header checks and adds 222 calibration-modal checks. |
| A43 installed workflow | **8 Python methods**, 9.405 s; CTest 9.50 s. Printed result identifies **20 files, MIDI enabled, CoreMIDI**. |

Calibration exercised healthy identical Apply, changed calibration, changed
route and exact port, no-input Apply, failed reopen/explicit retry, fault
retirement with surviving UI ownership, fixture enumeration and rejected
scenario setup. The two failed replay outcomes are expected negative-case
observations inside a passing fixture. Its executable SHA-256 is
`c5c646d83507f49353247169c0ed176f5ca097c2a51fe52d3636236e91ef9384`.

The [calibration fixture](../../apps/standalone/native_tests/test_standalone_native_calibration.py)
recompiles the real application/adapter against a substituted RtMidi API.
Callback offers are **synchronous at native API boundaries**; audio callbacks
are real SDL dummy callbacks. The ordinary backend gate also explicitly reports
15 fake-RtMidi groups, while quarantine reports six retained-context failure
paths. These are not native OS-driver fault or asynchronous CoreMIDI evidence.

A42's [exact committed oracle](../../apps/standalone/native_tests/test_standalone_material_acceptance.cpp)
executed four modal scenes/21 additional frames, 44 control records, 96 complete
literal glyph regions, 12 changed values, eight focus cases, two invalid frames,
two long-text frames and one fractional clip. **All 212 resampled pixels fall
within 38 individually identified boundary-crossing glyph rectangles; unexplained
pixels and literal/difference-set mismatches are zero.** At those rectangles,
both full and clipped pixels must match independent literal RGBA plates and
their exact difference set. Complete glyphs, nontext and focus remain identical;
surviving/hidden focus is required. There is no numeric pixel tolerance or whole
text-band exclusion. The earlier A42 failures remain in their
[original receipt](../development/2026-11-15-product-continuation/reports/A42-calibration-modal-raster.json).

## Prepared CoreMIDI dependency and installed package

SDL **2.32.10** is locked to
`5d249570393f7a37e037abf22cd6012a4cc56a71`; RtMidi **6.0.0** to
`1e5b49925aa60065db52de44c366d446a902547b`. Primary logs show offline
verification after explicit acquisition and again after acceptance. The actual
RtMidi compile command uses **`__MACOSX_CORE__` and the prepared static source**.
The [lock](../../data/dependencies/rtmidi-lock.json) applies exactly two
`CoreMidiData` zero-initializations in the build copy:

| Identity | Observed SHA-256 |
| --- | --- |
| Prepared `RtMidi.cpp` | `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a` |
| `rtmidi-coremidi-zero-init.patch` | `80aedddee9affe1c9ab305b605c6ca1f5c2209fd5d23da843c8c3f325426c4ad` |
| Prepared manifest | `481095a20040ffe8c824200b3b20663ebc4c392f1fc535ead7f6e679f3a5b2ae` |
| Installed application | `1cf70c4169b8bf7c9ae7431947cbc7481336da54a61fcab994a129efab10bbfa` |

This verifies the locked preparation and compilation. As the
[RtMidi build boundary](../RTMIDI_BUILD.md) states, zero-initializing those
allocations does not qualify physical port shutdown, driver failures, hotplug
or measured callback timing.

The executed [install test](../../apps/standalone/native_tests/test_standalone_install.py)
contains A43's new `MIDI_EXPRESSION_GUIDE.md`, private source/build/dependency
removal, relocated guide-link checks and the **800 ms synthetic replay**:
minimum 20, maximum 100, inverted raw CC11 40 yields **0.75**. Its assertions
require zero native MIDI callbacks, unchanged installed bytes, no implicit
musical-state save and preservation of four OfflineTools/CrossoverTools path
sentinels. The source of the passing eight-method test establishes these
assertions; its private calibration diagnostics were not separately downloaded.
Sentinels prove namespace preservation, not execution of the other components.

A separate successful workflow step installed **20 regular files**: one
executable plus 19 metadata files under
`share/hammond-b3-organ/standalone/`, including the new guide and all four
RtMidi license/lock/preparation/patch records. It verified the exact paths and
source hashes, relocated the prefix, ran help and a 600 ms dummy smoke, and
rechecked bytes/modes. That smoke logged **50 callbacks, 25,600 frames and
15 images**, with no selected/active MIDI input or native MIDI callback traffic.
The earlier install-test smoke printed 22 images; those are separate executions.

The runner reopened `HammondB3-Standalone-Release.tar.gz` and verified regular
members, exact payload paths, SHA-256, size and mode against its inventory.
The uploaded package contains that archive, `inventory.json` and
`SHA256SUMS`. The primary API and upload log agree:

| Retained artifact | ID | Bytes | SHA-256 of uploaded artifact |
| --- | --- | ---: | --- |
| [Core diagnostics](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337/artifacts/14143013792) | 14143013792 | 125,899 | `8c0fd0bcedc277f394096f94528594ba2fda5645897feb02df854209aa501bd4` |
| [Native diagnostics](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/artifacts/14142713230) | 14142713230 | 345,523 | `77ae83647fc37e0bc8d4472f0aaefb69fe5d1aa41e4b4b812df44b02c068271b` |
| [Native package](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/artifacts/14143117766) | 14143117766 | 1,487,410 | `d7fb9575ed663371882af35bcf09c4aeb2189d0b2a5e29dd16e3b68a57bccf7b` |

These are hosted verification and upload observations. A51 did not download or
independently unpack the binary artifacts; the uploaded-artifact digest is not
the inner tarball's digest.

## Limits and next gate

No new failure was observed in these two macOS jobs. Prior
`b9d352a` installer/Windows fixture failures and the `d556da01` GCC13 native
sanitizer build failure retain their original source-specific outcomes.
The named quarantine test's logged `ASAN_OPTIONS=detect_leaks=0` is not a
general leak exception, and these unsanitized macOS jobs supply no leak result.

The result establishes compiled platform support, software fixture execution
and the exact hosted installed payload. Physical controller/audio hardware,
OS fault injection, native display/Retina usability, semantic accessibility,
callback deadlines, DAW journeys, signing/notarization and literal whole-interface
1:1 equality remain separate gates.

**Next:** root accepts the separate platform audits and qualifies the actual
next publication; later checker/plot/workflow changes do not inherit this
source's pass. The next macOS product gate uses the relocated exact build on
an identified Cocoa/CoreAudio display, controller and device, records real
port callbacks, calibration/change/reconnect/fault behavior, held-note
focus/resize/release journeys and numeric shutdown status. A51 ran no local
build, CTest or application and changed only its review, note and report.

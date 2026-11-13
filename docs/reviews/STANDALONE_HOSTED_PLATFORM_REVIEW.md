# Hosted standalone platform and package review

Assignment 48/60, wave 8, actual agent
`/root/w08_a48_hosted_platform_review`, session 2026-11-13.

**Result:** the actual Linux and Windows standalone artifacts below pass this
archive, source identity, recorded acceptance and runtime inspection audit.
The downloaded Linux executable additionally passes an integrated input replay
after relocation. This checkpoint is **not an all-platform green release**:
native macOS compilation and three separate core Release jobs failed.

## Exact evidence boundary

All primary evidence in this review belongs to published commit
`5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`, workflow attempt 1.
Authenticated GitHub job metadata, downloaded artifact bytes and their embedded
provenance agree on that source. No locally rebuilt executable was substituted.
Windows execution results come from its hosted job; this Linux audit only
inspected its PE executable. There is no macOS standalone package for this run.

| Workflow / job | Observed result at this source | Scope |
| --- | --- | --- |
| [Native standalone 43523378962](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43523378962), Linux `132222980756` | Success | Build, 13 selected CTest suites, installation/relocation, diagnostics and package upload |
| Same run, Windows `132222981043` | Success | Build, 13 selected CTest suites, installation/relocation, diagnostics and package upload |
| Same run, macOS `132222981098` | Build failure | AppleClang rejected unused `kPanel` and `kLine` in `InstrumentView.cpp`; test/package steps did not execute |
| [Core CI 43523378849](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43523378849), Linux sanitizer `132222981313` | Success | This workflow's ASan/UBSan/leak configuration |
| Same core run, Linux Release `132222981693` | 89/90 passed | Concurrency oracle required an incidental positive `raced_discarded` count |
| Same core run, Windows Release `132222981820` | 87/90 passed | Calibration fixture path mismatch and rewritten chapel catalog/control admission failures |
| Same core run, macOS Release `132222981898` | 89/90 passed | Calibration fixture used `/var` while the checker resolved `/private/var` |
| [Native VST3 43523378803](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43523378803), Linux `132222980788`, Windows `132222980875`, macOS `132222980940` | All three jobs succeeded | Independently observed build, acceptance, inventory/archive and upload step conclusions; VST3 package bytes/JUnit were not downloaded in this assignment |

Job conclusions above were independently queried. Detailed core failure
diagnoses and the macOS compiler error are retained in the coordinator's
[platform follow-up](STANDALONE_PLATFORM_FOLLOWUP.md), which inspected their
failure logs. The 13-suite standalone successes do not supersede those failures.
The coordinator subsequently published `649b12c7d1faa7601fde1019e913347c65a6634a`,
tree `cf63327d857b02029e8c5c6f406cab3d3c6890d1`; its runs and later device/oracle
repairs require their own final-candidate review. This report does not transfer
the older results to that revision or wait for its jobs.

## Actual downloaded artifacts

Each ZIP's byte length and SHA-256 matched authenticated GitHub artifact
metadata before extraction. These artifacts expire on 2026-11-27; Actions
retention is not a permanent release distribution channel.

| Artifact | ID | ZIP bytes | Verified ZIP SHA-256 |
| --- | --- | ---: | --- |
| Linux package | `14083099657` | 1,112,007 | `6216ae49d055d69feb6969c53cceddf5459cd036e5651803f66b035fa01bdf8e` |
| Linux diagnostics | `14084546622` | 176,299 | `eaf8e5ff0bb6f961c86e86dfe84c280064d814fd5469b96006f20b17e0071fc6` |
| Windows package | `14083632691` | 829,090 | `e626fd57c2e870c47560ea6e0bd8ac92c726dbdadf7869a36cf7e7d690d61e1f` |
| Windows diagnostics | `14083592793` | 127,887 | `b4350154a9fe472e1ad4f2e21dff1ea686b4d230242232921e7b099cb9fd8385` |

Both package ZIPs contain exactly `HammondB3-Standalone-Release.tar.gz`,
`inventory.json` and `SHA256SUMS`. Both checksums inside `SHA256SUMS` matched:

| Inner file | Linux SHA-256 | Windows SHA-256 |
| --- | --- | --- |
| TAR.GZ | `3dc5595b80d0d62cb2101820b98c11d1a8b207b6d736df459b19e481a7fc3f6e` | `31666af7d9d9b5d5871dfb8f65237652083c12a687d581644307455f62b59ba7` |
| Inventory | `5d6ed2393d145be1f6dac7ce6e5fa1268184778c9c5a9048ba31bb3260e944f4` | `77684fa67feb2ae292f2078989f792bcf55b81fbdf6a98e0a7dc1f27928ee51f` |

Before manual extraction, the audit rejected absolute/traversal/ambiguous
paths, duplicate entries, encrypted ZIP entries, links, special files and
privileged permission bits. ZIP expansion was bounded to 20 MB and TAR payloads
to 10 MB. Reading every ZIP member also exercised CRC validation. Both TARs
contain exactly nine regular files and five directories under
`HammondB3-Standalone`; PAX metadata uses only `mtime`. Every file size/hash/mode
and every directory mode matches its inventory. Package inventory equals the
diagnostics' installed inventory; its payload equals the staged inventory, and
its provenance equals the separately archived provenance record. Archived BMP
and smoke JSON hashes also match the inventory.

### Installed payload and source comparison

The eight shared files below are under `share/hammond-b3-organ/standalone/`.
Seven match the exact source commit's documents, lock and font manifest byte
for byte. `LICENSE-SDL2.txt` matches `LICENSE.txt` at locked SDL commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`, release 2.32.10. Both platform
payloads contain identical shared-file bytes.

| Installed file | Bytes | SHA-256 |
| --- | ---: | --- |
| Linux `bin/hammond_standalone` | 2,773,792 | `dbae7012e63f5e7ba5caf22df20b04c523cb5c2545923ac4e16f1fa52fb4db44` |
| Windows `bin/hammond_standalone.exe` | 2,001,920 | `980688b720dc79ec0085378c50a9fd2805a72ed795e7da1fdd265b41328208cc` |
| `LICENSE-DejaVu.txt` | 2,345 | `22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6` |
| `LICENSE-SDL2.txt` | 884 | `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` |
| `STANDALONE_APP.md` | 13,842 | `74a1f16f82e164637f8bafada3812bdfb87087a90cae6c431d6621ddf946e2b8` |
| `STANDALONE_INSTALL.md` | 5,525 | `7ced9a7396b1a863c436a9f319309b8aac7fc31f98252ea68d8cf3fd75799f4c` |
| `STANDALONE_MODEL.md` | 4,837 | `bc62dc35dcb39d6538ac2b8475bd9cd997fd439f11201a3b2701e798c62f6649` |
| `THIRD_PARTY_NOTICES.md` | 10,792 | `ff72e873f84c98ce843bdcbe527ce4a5de9647aa67d5a703165093c04b9ab060` |
| `font-source-manifest.json` | 1,428 | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |
| `sdl2-lock.json` | 375 | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |

Each package has one executable, hence nine files rather than ten. Linux
directories/executable are `0755`, shared files `0644`. Windows TAR records
directories/executable as `0777` and shared files as `0666`; these are the
Windows staging mode representation, not an assertion about installed NTFS
ACLs. All nine file byte identities and recorded file modes remained unchanged
after this audit's inspection/execution.

Source mappings are `docs/` for the three standalone Markdown documents,
repository root for `THIRD_PARTY_NOTICES.md`, `assets/standalone/fonts/` for the
DejaVu notice/manifest, and `data/dependencies/sdl2-lock.json` for SDL. The font
manifest's source TTF sizes/hashes were also checked against that commit:
DejaVu Sans 759,720 bytes,
`57f73e11f51999432bf7ab22ce55b6f945d5eca1bf824404cfa9ec2e3718c84e`;
DejaVu Serif 380,660 bytes,
`8cb29f7db250ebb2551a6ce2c1e0bfd5a0eb520e9e233370db0493e82e1f36f7`.
These source TTFs are not extra files in the installed payload. The runtime
profile reports canonical authoring SHA-256
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`, verified
using the source profile's canonical JSON, not its formatted file-byte hash.

## Hosted acceptance and its exclusions

Actual `ctest.xml` files each contain 13 running test cases, zero failures,
disabled cases or JUnit skips. Reported suite times are 60 seconds on Linux and
72 seconds on Windows. This is the workflow's `^test_standalone_` selection,
not a claim that all 98 registered tests ran. Selected suites are install,
concurrency, session, state files, UI, benchmark, audio device, callback
allocation, app, workflows, replay boundaries, chapel and input replay.

Detailed logs retain exclusions that the outer JUnit count does not express:

- Linux state-file acceptance prints `NOT TESTED` for a POSIX failed replacement
  after a complete temporary write, because there is no deterministic
  non-racing fixture.
- Windows replay boundary acceptance skips one FIFO subcase because that
  platform cannot create it. Its Python result is `OK (skipped=1)` while the
  enclosing CTest case passes. Linux executes the FIFO boundary.

| Actual archived acceptance | Linux | Windows |
| --- | ---: | ---: |
| Install Python methods | 3 | 3 |
| App methods / actual subprocesses | 18 / 164 | 18 / 164 |
| Workflow methods / actual subprocesses | 11 / 15 | 11 / 15 |
| Replay boundary methods / subprocesses / preserved setup rejections | 9 / 29 / 19 | 9 / 28 / 18, plus the FIFO skip |
| Chapel methods / exported states / actual SDL application invocations | 2 / 20 / 20 | 2 / 20 / 20 |
| Benchmark methods / CLI calls | 9 / 111 | 9 / 111 |
| Device rate/buffer combinations / matrix callbacks / frames | 15 / 75 / 59,520 | 15 / 76 / 59,648 |
| Calibrated allocation workloads / observed callbacks / positive calibrations | 18 / 39 / 936 allocations and frees | 18 / 39 / 936 allocations and frees |
| Replay parser valid / rejected parses; atomic file rejections | 573 / 186; 12 | 573 / 186; 11 |

Allocation workloads observed zero production-region C++ `new/delete` counts
with positive callback-thread calibration; they do not cover C/system
allocation, locks, callback deadlines or physical devices. Replay helper logs
also record 51 forged-plan rejections, 116 checked queue actions, 13 acknowledged
markers, five expected runtime failures and four lifetime cycles per platform.
Native workflow/chapel logs name the matching packaged executable hashes;
chapel's application source hash is
`560f3f12cd0b9a081748d601ec8ad42c69b4e73b3d68ab6d583e4d5e9be1ea88`, matching
`apps/standalone/main.cpp` at the named commit.

Both archived relocation smokes use explicit dummy audio/video and software
rendering, 48 kHz, 512 frames and native float32 stereo. Linux records 57
callbacks/29,184 frames/18 rendered images; Windows records 60 callbacks/30,720
frames/17 images. Each observes note on, held state, note off, release and a
screenshot while held; both mark smoke passed. Audio render/format/nonfinite/
overrange counters, application errors, recovery/overflow/rejection counts and
session fault flags are zero. Shutdown leaves the session stopped and no held
notes. Each records one discarded shutdown cleanup command; it is preserved
here rather than described as an all-zero session counter set. Positive peaks
are approximately 0.08312443 and 0.08321372 respectively.

## Independent replay of the actual Linux package

The safely extracted Linux payload was moved to a separate directory containing
spaces and launched from a different working directory, outside checkout and
build trees. `--help` exited zero. The retained source script
[`examples/standalone-input/keyboard-notes.b3ui`](../../examples/standalone-input/keyboard-notes.b3ui)
was read with `git show` at `5b8e241`, not copied from a moving worktree. Its
711 bytes hash to
`823a5618f104ffb4756ade749fb1990dcf087cc1319e35b5fc1ceac0af548384`.

Execution used explicit dummy audio/video and software rendering on Linux
6.18.57 x86-64, glibc 2.41. The command below describes the executed invocation;
`$audit_run` and `$relocated` were absolute private scratch paths, and the
subprocess had a 30-second timeout.

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy SDL_RENDER_DRIVER=software \
  "$relocated/bin/hammond_standalone" \
  --input-script "$audit_run/keyboard-notes.b3ui" \
  --state "$audit_run/absent-controls.b3controls" \
  --diagnostics "$audit_run/replay.json" \
  --screenshot "$audit_run/replay.bmp"
```

The 2,600-ms script exited zero, delivered all 18/18 events and marked completed,
delivered, passed and final acknowledged. It accepted four note-on and four
note-off commands, with one device start. Observations contain simultaneous
Upper MIDI 60, Lower MIDI 74 and pedal ID 17; releases preserve each original
owner despite intervening destination/octave changes. The final new Upper
press is MIDI 72. Final submitted/applied/resolved sequence is 9, with empty
manual and pedal holds **before** shutdown. Observations were not truncated.

The actual callback recorded 247 calls/126,464 rendered frames, 63 images and
maximum peak `0.14220303297042847`. All audio failure counters, application
errors and session fault/recovery/overflow/rejection counters are zero. Shutdown
joins and leaves no held state; one cleanup command is discarded after the
final script acknowledgement. The automatic smoke mode was not requested;
its false diagnostic fields are not a replay failure. The screenshot is taken
before any held note in this invocation (`screenshot_while_held=false`). The
absent state file remains absent, and the executable/file hashes remain intact.

Independent replay JSON SHA-256:
`fda7aa50f2c4b10304c059909120bd211da6cb176961c743cb672b1bb96fcae9`.
BMP SHA-256:
`e7952752f8d2b21b5f1cf3bd06edc9320fe2266ed640a62525b81b8fa0e667c9`.
The BMP was checked for identity/format, not treated as a physical-display or
visual accessibility assessment. Timing/callback counts describe this run and
are not performance acceptance thresholds.

## Compiler, backend and runtime requirements

| Evidence | Linux package | Windows package |
| --- | --- | --- |
| Hosted machine/image | x86-64, Ubuntu 24.04, image `20261111.370.1` | AMD64, Windows Server 2022 build 20348, image `20261112.366.7` |
| Compiler | GNU C/C++ 13.3.0 | MSVC C/C++ 19.44.35230.0, Hostx64/x64 |
| Python | 3.12.16 | 3.12.10 |
| Native video macro present | `SDL_VIDEO_DRIVER_X11` | `SDL_VIDEO_DRIVER_WINDOWS` |
| Native audio macros present | ALSA, PulseAudio, OSS | WASAPI, DSOUND, WINMM |
| Other compiled backends | Dummy audio/video, disk audio, offscreen video | Dummy audio/video, disk audio, offscreen video |
| Generated SDL config SHA-256 | `e551827eabe965364b38d46580abc2de7aea247fc2cece693ba245de6ea0abae` | `d3da4b23e0ae256bb84df02a0869eb1af01ca112fb3faffd42b30c7e40ec239b` |

Every archived audio/video macro agrees with its generated config header and
the package provenance; compiler versions agree with archived CMake compiler
files. Compiling a backend does not prove that its physical driver was selected
or exercised. All execution above selected dummy drivers.

`file`, `readelf -h -l -d -V` and `ldd` identify the actual Linux executable as
an unstripped ELF64 x86-64 PIE with loader `/lib64/ld-linux-x86-64.so.2`.
Direct runtime dependencies are `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`
and `libc.so.6`; no RPATH/RUNPATH is recorded. Required symbol versions reach
`GLIBC_2.38`, `GLIBCXX_3.4.32` and `CXXABI_1.3.9`. SDL is embedded, but this
application is not wholly static. Its native backends dynamically load
`libasound.so.2`, `libpulse.so.0` and the recorded X11 libraries, including
X11/Xcursor/Xext/Xfixes/Xi/Xrandr/Xss. These are compatibility prerequisites,
not proof of every distribution's support.

`file` and `objdump -p` identify the Windows executable as PE32+ x86-64, Windows
console subsystem. Its import table includes `MSVCP140.dll`, `VCRUNTIME140.dll`,
`VCRUNTIME140_1.dll` and Universal CRT API-set DLLs, alongside Windows system
libraries. The corresponding x64 Microsoft C++ runtime/UCRT must be available;
they are not bundled among the nine payload files. The PE security directory
is empty, so this artifact has no embedded Authenticode certificate. PE header
version fields do not establish a tested minimum Windows release. This audit
did not execute Windows code on Linux. The packages are TAR.GZ payloads, not
an MSI, desktop installer or macOS signed/notarized application.

## Reproduction and next gates

Session scratch evidence is under
`/workspace/scratch/5ba97739b54c/a48-hosted-platform/`: authenticated metadata,
the four original ZIPs, bounded verifier, per-platform inventories/diagnostics,
ELF/PE inspection logs, relocated Linux payload, retained script and its
command/JSON/BMP/verification records. Temporary signed download URLs were
deleted and are not repository content. The verifier uses fresh-directory
assertions; use new destinations when repeating it. To reproduce, reacquire the
named artifacts while retained, check the four API ZIP digests first, validate
archive membership before extraction, compare every inventory entry with the
named source objects, then execute the archived Linux program with the explicit
environment and fresh output paths above. A replacement build is a new result.

The next software gate is final-candidate verification of repaired core,
standalone and VST3 runs, including an actually successful macOS standalone
build/test/package and the repaired Windows/macOS file-admission fixtures.
Physical desktop/audio devices, device removal/reconnection, callback
deadlines, native accessibility, MIDI, acoustic/fidelity validation,
signing/notarization and permanent artifact retention remain separate gates.
Dependency notices are present and match their sources; the named revision's
missing project-wide LICENSE and unresolved supplied-atlas rights remain
unresolved. This inventory audit makes no release-rights determination.

Future agents must follow root `AGENTS.md`, preserve exact source/run/artifact
identities, retain failures and internal exclusions, document actual execution
versus inspection, and update the coordinator's handoff before making broader
claims. Later green results should cite their own source rather than rewrite
this historical checkpoint.

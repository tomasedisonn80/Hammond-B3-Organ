# Final standalone hosted platform and artifact audit

**PASS for the named software scopes at [6214032f3565f9e221fcf3988e33a22a73bb4ea8](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/6214032f3565f9e221fcf3988e33a22a73bb4ea8), tree
`10f070c54d176571f1919d8141d24dd82db0e41c`.** Assignment 60 independently observed all **ten completed successful
hosted jobs**, downloaded and verified all three standalone packages and their
diagnostics, and executed the downloaded Linux binary after relocation. The
complete [machine-readable evidence](STANDALONE_FINAL_PLATFORM_ARTIFACTS.json)
retains exact jobs, artifact IDs/digests, all 27 payload-file records, input and
output identities, runtime observations and the three private audit programs.

Reviewed **14 November 2026 UTC** by `/root/w10_a60_final_platform_audit`, actual
assignment 60/60, logical wave 10 of `2026-11-13-next-phases`. This assignment
owns only this report, its JSON evidence and its assignment note. Root owns
shared status, acceptance of all sixty results, the strict session gate and
guarded publication. This report does not itself attest sixty completed agents.

## Exact source and observed hosted results

The final candidate follows public `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`. Their Git-tree comparison contains
exactly two changed files: `apps/standalone/native_tests/test_standalone_workflows.py`
and `tests/test_capture_demo.py`. Production code, headers, CMake, data,
dependencies and all installed payload inputs are unchanged. The new workflow
oracle uses legal applied-command prefixes and independent musical endpoints;
the demo fixture checks the actual pre-call link target and identity after
rejection. Exact before/after file hashes are in the JSON record.

| Actual completed job | Job ID | Selected suites passed | CTest elapsed |
| --- | --- | ---: | ---: |
| [Release (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826025/job/132257832946) | `132257832946` | 101/101 | 58.50 s |
| [Release (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826025/job/132257832800) | `132257832800` | 101/101 | 97.85 s |
| [Release (Windows MSVC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826025/job/132257832603) | `132257832603` | 101/101 | 157.92 s |
| [Linux GCC ASan + UBSan + leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826025/job/132257832899) | `132257832899` | 101/101 | 177.40 s |
| [Native standalone (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826108/job/132257833166) | `132257833166` | 14/14 | 77.10 s |
| [Native standalone (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826108/job/132257832786) | `132257832786` | 14/14 | 82.33 s |
| [Native standalone (Windows MSVC x64)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826108/job/132257833093) | `132257833093` | 14/14 | 96.72 s |
| [Native VST3 (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826057/job/132257832888) | `132257832888` | 8/8 | 6.84 s |
| [Native VST3 (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826057/job/132257832817) | `132257832817` | 7/7 | 4.43 s |
| [Native VST3 (Windows MSVC x64)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826057/job/132257832551) | `132257832551` | 7/7 | 7.27 s |

Runs: [core CI 43533826025](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826025),
[native standalone 43533826108](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826108), and
[native VST3 43533826057](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43533826057), all attempt 1 at the
exact candidate. Statuses and completed steps were inspected through the
authenticated GitHub API; complete decoded logs were retrieved for all ten
jobs. Their source revision and completed CTest totals were checked. Each log's
UTF-8 byte length and SHA-256 are retained. The final run-level API responses
also reported completed/success; a dispatch or earlier partial poll was never
treated as a pass.

All three standalone archives independently contain JUnit with **14 run cases,
zero outer failures, disabled cases or skipped cases**, and matching exact test
names. Detailed archived output records **25 actual workflow processes** and
**22 exported chapel states / 22 actual application invocations** per platform.
Windows uses Release/x64; macOS uses ARM64. The core sanitizer job explicitly
uses ASan/UBSan and `detect_leaks=1`, with `LSAN_OPTIONS=exitcode=23`.

That core job does not substitute for the separately instrumented native/SDL
gate. [Assignment 55's final integration](STANDALONE_FINAL_INTEGRATION.md)
retains its earlier failures and later 14/14 native ASan/UBSan result with leak
detection explicitly disabled for the demonstrated ptrace limit. Root's
[combined Release evidence](STANDALONE_COMBINED_FINAL_GATE.md) is the distinct
110/110 run at preceding `183fc9e`; it is not relabeled a new 110-suite run here.

### Actual Windows regression closure and inner skips

The final Windows core log explicitly passes all four formerly failing capture
suites and the later demo suite. Its separately downloaded diagnostics ZIP has
the exact source-revision file, 101-case JUnit and complete `LastTest.log`:

| Windows suite | Actual methods | Passed | Reported inner skips |
| --- | ---: | ---: | ---: |
| Audio acceptance | 41 | 41 | 0 |
| Audio admission | 63 | 58 | 5 |
| Corpus acceptance | 47 | 47 | 0 |
| Corpus admission | 59 | 53 | 6 |
| Synthetic demo | 43 | 43 | 0 |

The four capture suites therefore execute **210 methods, 199 passing and 11
existing Windows capability skips**. These inner skips remain visible despite
zero outer CTest skips. The demo's 43 methods have no skips, so its repaired
dangling-link preservation case is exercised on Windows. No new skip or relaxed
producer policy was used to close the original failures. The quiet archived
summaries report these skip counts; this audit does not invent verbose per-skip
execution traces absent from those logs.

The source scopes remain separate: `0085e33` retained Windows 92/96 and all 41
original failure/error blocks in the [portability investigation](STANDALONE_CAPTURE_PORTABILITY.md).
The later `183fc9e` passed its four repaired capture suites but retained **100/101**
in Windows job `132254226441`: `Path.readlink()` returned the native `//?/C:/...`
spelling while its demo fixture expected `C:/...`. This worker discovered that
failure, preserved the complete log and reported the exact assertion to root.
Root's [narrow fixture correction](STANDALONE_FINAL_PORTABILITY_REPAIR.md) and
the unskipped final Windows pass close that separate issue. The former failures
and cancelled/unacquired macOS observations are not overwritten by these passes.

## Actual downloaded bytes and inventory

All six standalone ZIPs total **3,182,585 bytes**. The additional Windows core
diagnostics ZIP is **56,617 bytes**. Each actual download matched
the authenticated API size and SHA-256 before its contents were inspected.
Every artifact identifies the exact candidate and appropriate run, was not
expired when acquired, and carries a recorded expiry on **28 November 2026**.
Temporary signed download URLs are not retained. These are CI artifacts with
finite retention, not permanent release installers.

| Actual ZIP | Artifact ID | Bytes | Verified SHA-256 |
| --- | --- | ---: | --- |
| Linux package | `14088787592` | 1,114,543 | `728a3961af5bae6bea51abc87302ff2130039b119b4ec286881290da707ec87c` |
| Linux diagnostics | `14088612884` | 177,628 | `becbf9d5fc4fa47c77509de5a9ccd6a5d2b8bcaf2a403359261d68d942f3b696` |
| Windows package | `14089241253` | 831,459 | `4915f1d97621dce99b8a4a22f3a8a5a5833cdb241609f35b81643293ca20a767` |
| Windows diagnostics | `14089016720` | 128,950 | `b3f236dea991187a98c6f26caa47c3fc422722117bdf3c3a01acb3d476ada7d1` |
| Macos package | `14088701938` | 764,098 | `3b602a95dfbc9db20bdadf83ecb25ad3bb271738bb2e515d267193f59f7f0080` |
| Macos diagnostics | `14088248137` | 165,907 | `68ea2987745488f8afedb133ea684c2b1fcabf2a06e76de5065c1166d0356d70` |
| Windows core diagnostics | `14089381285` | 56,617 | `d31d6d880ec932dfe084983cbba9d3e0d02fbf5556553d37a4ad7c277a5e19d2` |

Before manual extraction, the audit rejected duplicate/unsafe paths, absolute
or parent traversal, backslashes/drive syntax, encryption, links, special types
and excessive declared expansion. Reading every ZIP entry verifies its CRC.
Each package contains exactly the TAR.GZ, `inventory.json` and `SHA256SUMS`.
Both inner checksums match. Each TAR contains exactly **nine regular files and
five directories**, with only finite `mtime` PAX metadata. Every path, size,
mode and SHA-256 matches the inventory, with no extra or duplicate canonical
member. No archive symlink was followed.

The package inventory equals the archived installed inventory byte for byte;
its payload equals the staged inventory; its provenance equals the archived
source/run/dependency provenance. The relocated smoke JSON and BMP hashes match
the package inventory. All seven repository metadata files match `git show
6214032f3565f9e221fcf3988e33a22a73bb4ea8:<path>`; SDL's primary notice matches the exact locked external source.

| Actual executable | Bytes | SHA-256 |
| --- | ---: | --- |
| Linux | 2,773,896 | `5dc3f75e4049044c1fc38c2a2eb2ac5370e9cd8012df2ec98de2f055368e19be` |
| Windows | 2,001,920 | `3bb9c4bf1638419b7fa906e1b30668f35ab9e25c20a5ec2bc357546a8e42d2e6` |
| Macos | 1,971,712 | `83a57523d7acaff6a1dcae275c9b4a5abb972a10fc3e4451ac880c0bc37b9f5c` |

The Linux and macOS executable bytes equal their separately downloaded `183fc9e`
predecessors. Windows has its own new output hash; source equality is not
misrepresented as universal binary reproducibility. The eight accompanying
files have identical bytes across all three final packages. Their recorded
TAR modes are `0644` on Linux/macOS and `0666` on Windows; these modes match
each platform's own inventory:

| Installed metadata/notice file | Bytes | SHA-256 |
| --- | ---: | --- |
| `LICENSE-DejaVu.txt` | 2,345 | `22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6` |
| `LICENSE-SDL2.txt` | 884 | `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` |
| `STANDALONE_APP.md` | 14,974 | `bddb315f1b56d0245d4095375dc545d6832a3e5e95ce9eef9639894faafe213a` |
| `STANDALONE_INSTALL.md` | 6,396 | `54cfe80cc4071aec1b95e40cc815b262c17f04d28e8d1e2a05497e0e52a06c74` |
| `STANDALONE_MODEL.md` | 4,837 | `bc62dc35dcb39d6538ac2b8475bd9cd997fd439f11201a3b2701e798c62f6649` |
| `THIRD_PARTY_NOTICES.md` | 16,366 | `3d4acfae5c0c83b5184d3806b1ce70040beeaf027da28b541ab220e764ae4faa` |
| `font-source-manifest.json` | 1,428 | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |
| `sdl2-lock.json` | 375 | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |

These files live under `share/hammond-b3-organ/standalone/`; the executable is
under `bin/`, with `.exe` on Windows. The copied app/install recipes explicitly
select `--config Release`, and the app guide explains the configuration
subdirectory. No raw TTF, Python, PDF, loose nominal profile or shared SDL library
is included in this nine-file payload.

### Exact notice and dependency checks

The package's complete combined notice was compared with the source revision.
Its fenced yuv2rgb text contains all **1,480 exact source bytes**, SHA-256
`f7d74004cc75778cae46c5f0139f244d67c07ef64cf51937e8272352197dcb18`. The selected HIDAPI BSD text
contains all **1,534 exact source bytes**, SHA-256
`30eb1bef29b46f8ba7ab8b416035dbd93cb034a45481dd97815b944284582cd2`. The Sun fallback notice is
present verbatim from the pinned `src/libm/e_pow.c`, whose complete source hash
is `ac26220798ad9f92bc051aa5102ae41a0fe50b1c8750f5f90353252c5a948512`; its conditional inclusion
wording remains intact. This does not assert that every compiled SDL archive
member was linked into every executable or that every distribution right is
cleared.

The SDL lock identifies 2.32.10, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`; its full primary notice and hash match.
The DejaVu 2.37 license, both original font byte identities and source manifest
match the exact repository objects. Their runtime glyphs are embedded. Archived
compiler records and generated `SDL_config.h` match provenance and the retained
backend macro inventory. The required X11/ALSA/PulseAudio, Cocoa/CoreAudio and
Windows/WASAPI macros are enabled on their respective builds; execution in this
audit and CI uses explicit dummy drivers.

## Independent execution of the downloaded Linux executable

After verification, the actual extracted payload was moved to
`../a60-final-platform/621/relocated Linux é 音/`. Its original extraction path
no longer exists. The run uses a separate fresh Unicode/space working directory,
an empty `PATH`, explicit dummy audio/video and the software renderer. Source
and build directories elsewhere were not hidden; this audit claims relocation
of the package, not an additional source-unavailability experiment.

Exactly two application invocations ran: `--help`, then the unchanged source's
**711-byte / 2,600 ms / 18-event `keyboard-notes.b3ui`**. The musical state is an
independent complete noncanonical B3CONTROLS3 fixture: expression 0.375,
different retained banks, Upper route off, Lower route on, pedal mixtures 2/7,
and enabled Third/Soft/Fast percussion. Its complete expected control snapshot
is retained in JSON. This exercises parsing/restoration independently of a
default-state guess; the script performs no Save.

Equivalent executed command, with the exact absolute paths and environment
retained in the JSON record:

```sh
env -i PATH= LANG=C.UTF-8 LC_ALL=C.UTF-8 \
  SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy SDL_RENDER_DRIVER=software \
  '/absolute/relocated Linux é 音/bin/hammond_standalone' \
  --state '/absolute/independent replay é 音/explicit-controls.b3controls' \
  --input-script '/absolute/independent replay é 音/keyboard-notes.b3ui' \
  --diagnostics '/absolute/independent replay é 音/keyboard-notes.json'
```

Both processes exit zero with empty stderr; replay stdout is empty. The actual
48 kHz / 512-frame float32 stereo callback records **238 callbacks / 121,856
frames** and copied maximum peak **0.04218863695859909**. All application errors,
audio format/render/nonfinite/overrange counters and Session fault/recovery/
overflow/rejection counters are zero. Exactly **4 note-ons / 4 note-offs** are
accepted. All nine legal applied-command prefixes are actually observed:
Upper 60, Lower 74 and pedal 17 retain their original owners across target and
octave changes, then a new Upper 72 is applied and released. Every sampled
prefix has the literal expected holds and complete controls; applied/resolved
sequences are equal, monotonic and bounded by submission.

Final sequence **9** is acknowledged with empty held notes before shutdown;
joined shutdown remains stopped and empty. One discarded redundant cleanup
command is within the single device-start allowance. Every state/script byte
and all nine payload hashes/modes remain unchanged. No replay was retried.
The diagnostics SHA-256 is `48bc088b36a6173cdfc229dd9de2d23ad85fc24168613e6b427a2388818dcb09`. These observations
are software callback and ownership evidence, not a listening comparison,
physical audio output or deadline/latency qualification.

## Actual runtimes, architecture and limits

| Package | Observed binary/runtime facts | Qualification limit |
| --- | --- | --- |
| Linux x86-64 | ELF PIE; `/lib64/ld-linux-x86-64.so.2`; direct dependencies `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6`; symbol maxima GLIBC 2.38, GLIBCXX 3.4.32, CXXABI 1.3.9 and GCC 3.0; no RPATH/RUNPATH/shared SDL dependency. | All resolve on this glibc 2.41 host. No arbitrary older-distro or real native backend claim. |
| Windows x64 | PE32+; imports MSVCP140, VCRUNTIME140, VCRUNTIME140_1, UCRT and the recorded Windows system DLLs; empty PE certificate directory. | Actual execution comes from Windows CI. No local Linux execution of PE, runtime deployment or signing qualification. |
| macOS ARM64 | 64-bit arm64 Mach-O; `LC_BUILD_VERSION` declares macOS 15.0.0 / SDK 15.5.0; system/framework and libc++ imports, no RPATH; a code-signature load command exists. | Actual execution comes from the macOS runner. Signing identity/notarization and other architectures/older OS versions were not verified. |

The Mach-O reader uses Apple's checked immutable
[loader header](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/EXTERNAL_HEADERS/mach-o/loader.h),
SHA-256 `8780a1e622375833b563f488bc820422c2fb5b8727bb8df8ceaa73ab6f0f88e3`.
It bounds every load command and string; the exact parsed imports/versions and
reader source are retained. `file`, `readelf`, `ldd` and `objdump` outputs have
their own hashes. No `otool` or macOS execution is claimed in this Linux audit.

Hosted native toolchains are GNU 13.3.0 / Ubuntu 24.04 X64,
MSVC 19.44.35230.0 / Windows Server 2022 X64, and AppleClang 17.0.0.17000013 /
macOS 15 ARM64. Exact runner image versions, dependency identities and compiler
paths are retained in each archived provenance. Local audit execution uses
Python 3.12.14 on Linux-6.18.57-x86_64-with-glibc2.41.

The native diagnostics still disclose **NOT TESTED: POSIX replacement failure
after a complete temporary write** on Linux/macOS, and one Windows FIFO
subcase capability skip. Neither is hidden by zero outer JUnit skips. The VST3
claims above come from its actual jobs and complete logs; this assignment did
not download VST3 bundle bytes. Physical devices/controllers, native semantic
accessibility, high-DPI desktop behavior, DAW workflows, deadlines/underruns,
clean-machine distribution, complete licensing review and measured Hammond/
Leslie fidelity remain separate gates.

## Reproduction and continuation

Private acquisition and raw logs are under `../a60-final-platform/183/` and
`../a60-final-platform/621/`; only the final scope is the headline pass. The
JSON evidence embeds the complete three standard-library audit programs and
their hashes. They inspect supplied downloads and immutable Git objects; no
local build is substituted for a downloaded executable. Reproduce by retrieving
the named ZIPs, verifying their public digests, retaining the named source and
SDL objects, and running these original commands with corresponding local paths:

```sh
python3 -B ../a60-final-platform/verify_artifacts.py ../a60-final-platform/621
python3 -B ../a60-final-platform/inspect_runtime.py ../a60-final-platform/621
python3 -B ../a60-final-platform/replay_downloaded.py ../a60-final-platform/621
```

Extraction and execution destinations are deliberately single-use. For another
workspace, adapt the recorded repository/SDL locations while preserving source
identities, file expectations and assertions. Artifact expiry requires a new
named build if the original bytes are no longer obtainable; a new build must
receive its own identities. The recorded byte manifests remain durable evidence
but are not signed source-to-binary attestations.

One attempt to transfer a large full API metadata object exceeded the process
argument-size limit. No product command executed in that failed transfer. The
relevant fields were compacted and saved in bounded chunks; actual bytes,
completed tests and successful product executions were not rerun or reclassified.
No product failure occurred in the final archive verification or relocated run.

Root should accept this actual assignment, reconcile all sixty owned records,
run the strict session checker, then commit/push the documentation closure with
expected-head protection and fetched tree equality. Preserve concurrent work
and these exact tested-source boundaries. The next product work is the named
external MIDI ownership/transport and native accessibility acceptance under the
[current handoff](../STANDALONE_HANDOFF.md) and [next steps](../NEXT_STEPS.md),
alongside the independently owned scanner, rotary and capture/calibration gates.
The standing [AGENTS workflow](../../AGENTS.md) remains mandatory.

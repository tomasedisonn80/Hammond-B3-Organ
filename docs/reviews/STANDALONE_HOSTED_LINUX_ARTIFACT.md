# Hosted Linux standalone artifact audit

Reviewed 2026-11-13 by development assignment 41/60, wave 7. **PASS for the actual Linux x86-64 package and the software checks below.** This audit downloaded the GitHub artifact bytes, inspected the archived test evidence and executed the archived ELF after relocation. It applies only to the named revision; later source and replay integration require their own evidence.

## Identity and acquisition

| Item | Exact identity |
| --- | --- |
| Repository source | `219821dfaca6bfee8ba0905993ed8deec7a66396` |
| Source tree | `f2db7aee1d45a897273e4e68a2fefc6a2de4d433` |
| Hosted execution | [Run 43517181978, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43517181978), Linux GCC job `132202000441` |
| Package artifact | `14081326408`; 1,092,688-byte ZIP; SHA-256 `bd98ecaae92fe111df9bb2b40adae4b4358399ba11a6cdd2967d7e8502dcb9ed` |
| Diagnostics artifact | `14080619532`; 172,555-byte ZIP; SHA-256 `61e303fbef03848ce3d4fa24de168508cf289be17e7b222e94ffc857c1d47fd2` |
| Inner TAR | `HammondB3-Standalone-Release.tar.gz`; 1,094,380 bytes; SHA-256 `ae49f6e5ae7bf44831545f110478cfd7ef00e80bc949b337f81290b1b7577689` |
| Inventory | `inventory.json`; 7,829 bytes; SHA-256 `87ce287e0f1088ebf6066953a20ad1e62e4d5a6535df9e664741afe89a7eece3` |

Acquisition used the connected GitHub account's `github_fetch_workflow_run_artifacts`, `github_download_workflow_artifact` and `github_fetch_workflow_run_jobs` for this repository/run. Returned file references supplied the actual ZIP bytes. Locally computed ZIP digests and lengths equal GitHub's authenticated metadata; both metadata records identify the named source commit. Temporary download URLs are not retained here. GitHub recorded expiry on 2026-11-27 (package 22:13:28 UTC, diagnostics 22:13:26 UTC), so these are retained CI artifacts rather than a permanent release.

## Archive, source and dependency checks

The package ZIP has three regular entries: TAR, `inventory.json` and `SHA256SUMS`; diagnostics has 31 regular entries. ZIP entries were checked for duplicates, absolute/parent traversal paths, backslashes, drive prefixes, encryption and nonregular types before manual extraction into a fresh directory. Declared expanded sizes were bounded and every entry was read with CRC verification. Both `SHA256SUMS` entries matched. The TAR contains exactly nine regular files and five directories under `HammondB3-Standalone`, with no links or special files. Its only PAX metadata is finite `mtime`; no path overrides occur.

All five directories (`.`, `bin`, `share`, `share/hammond-b3-organ`, `share/hammond-b3-organ/standalone`) are mode `0755`. Every regular-file path, length, mode and SHA-256 matches the inventory. Data paths below are relative to `share/hammond-b3-organ/standalone/`, except the executable.

| Installed file | Bytes / mode | SHA-256 |
| --- | --- | --- |
| `bin/hammond_standalone` | 2,725,096 / `0755` | `dd5f14731e88035c8b35c2e57524dfadf5a741aabf307d3a1a799483ed1c7f61` |
| `LICENSE-DejaVu.txt` | 2,345 / `0644` | `22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6` |
| `LICENSE-SDL2.txt` | 884 / `0644` | `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` |
| `STANDALONE_APP.md` | 11,141 / `0644` | `49fb5c12cac1c063cbee57437812d75c23e253023d6a086a632d711098582fb6` |
| `STANDALONE_INSTALL.md` | 5,525 / `0644` | `7ced9a7396b1a863c436a9f319309b8aac7fc31f98252ea68d8cf3fd75799f4c` |
| `STANDALONE_MODEL.md` | 4,501 / `0644` | `be1d2893f899b63498192d1905964cada8d1e2564124a10b05dbd2de759a7dc0` |
| `THIRD_PARTY_NOTICES.md` | 10,792 / `0644` | `ff72e873f84c98ce843bdcbe527ce4a5de9647aa67d5a703165093c04b9ab060` |
| `font-source-manifest.json` | 1,428 / `0644` | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |
| `sdl2-lock.json` | 375 / `0644` | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |

The seven repository data/document files were compared byte-for-byte with `git show 219821dfaca6bfee8ba0905993ed8deec7a66396:<source-path>`: the three `docs/STANDALONE_*.md` files, root notices, `data/dependencies/sdl2-lock.json`, and font license/manifest under `assets/standalone/fonts/`. SDL's complete license was compared with `git show 5d249570393f7a37e037abf22cd6012a4cc56a71:LICENSE.txt` in the external SDL repository. The locked source is SDL 2.32.10, tag `release-2.32.10`; archived acquisition and final verification logs name that exact commit.

Dependency identities embedded in provenance equal the parsed source lock/manifest and their byte hashes. Both source TTF inputs also match the manifest: Sans 759,720 bytes, `57f73e11f51999432bf7ab22ce55b6f945d5eca1bf824404cfa9ec2e3718c84e`; Serif 380,660 bytes, `8cb29f7db250ebb2551a6ce2c1e0bfd5a0eb520e9e233370db0493e82e1f36f7`. Runtime glyphs are embedded; these TTFs are not package files.

Archived `provenance.json` equals inventory provenance; `staged-inventory.json` equals its payload; `installed-inventory.json` is byte-identical to package inventory. Provenance records Ubuntu 24.04/X64 image `20261111.370.1`, Linux/glibc 2.39, Release, GCC/G++ 13.3.0, Python 3.12.16, CMake/CTest 3.31.6 and Git 2.56.1. `SDL_config-Release.h` hashes to `e551827eabe965364b38d46580abc2de7aea247fc2cece693ba245de6ea0abae` and enables X11, ALSA, PulseAudio and dummy video/audio. Compiler identity files and toolchain logs agree with provenance.

## Actual hosted acceptance evidence

Parsed `standalone-ci-logs/ctest.xml`: **9 test cases, all `run`, zero failures, disabled tests, skipped tests or error elements**. `ctest.log` reports 9/9 passed in 14.74 seconds; XML rounds total time to 14 seconds. XML SHA-256 is `83448eb1e310a6340a3bbe0c061712e6823ce87fc338e9aa117ff65beec30902`; log SHA-256 is `3299075da089fdd64c5d594a5f085179ca862e0f1c54a751cf66a28c9577edeb`.

| CTest case | Archived result / scope |
| --- | --- |
| `test_standalone_install` | 3 Python methods; nine-file install; relocated actual binary; hash equals package ELF |
| `test_standalone_concurrency` | 8,192 ordered posts; 64 recovery epochs; 16 active-overflow rounds; coherent readers and accounting checked |
| `test_standalone_session` | 9 rate/partition scores; 3,277 renders; 156,308 bit-exact stereo samples; 61 future-output probes |
| `test_standalone_state_files` | 7 scenarios; regular/dangling symlink rejection and RLIMIT_FSIZE write-failure cleanup tested |
| `test_standalone_ui` | 7 behavioral scenarios |
| `test_standalone_audio_device` | Dummy driver; 15 rate/buffer combinations; 75 callbacks; 59,520 frames; 31 rejected opens; 2 deliberately induced render faults; 8 close/destruction cycles |
| `test_standalone_callback_allocation` | 18 workloads; 39 SDL dummy callbacks; 936 positive calibration allocations and frees; production C++ `new=0/delete=0` |
| `test_standalone_app` | 18 Python methods; 164 actual native subprocesses; zero method skips reported |
| `test_standalone_input_replay` | Helper test: 573 valid parses, 186 parser rejects, 3 file loads, 12 file rejects, 51 forged-plan rejects, 116 queue actions, 13 markers, 5 expected runtime faults, 4 lifetimes |

The state-file suite explicitly prints **NOT TESTED: POSIX failed replacement after a complete temporary write; no deterministic non-racing fixture**. Zero CTest skips does not cover that internal exclusion. Callback allocation evidence excludes C/system allocation, locks, deadlines, physical devices and other platforms. The replay helper's acceptance does not imply integrated `--input-script` support in this older application.

After installation/relocation, CI ran `--help` and a 600-ms dummy smoke: 59 callbacks, 30,208 frames, 14 images, peak `0.0836980938911438`; held and released input observed, joined shutdown, zero application/audio/fault counters. Its JSON hashes to `6879423a12dc182a6597a688398967f47f37152b376e118ab3a9dc391993172c`. Its held-note BMP is 1,280×900, 32-bit, 4,608,122 bytes, SHA-256 `a774880df19f2efb9a3eb1534edfef5ad0f7a464cf0cefc900ec5cb6dbcf7097`; both hashes match inventory.

## Independent execution of downloaded ELF

Validated extraction was moved outside the archive directory to `/workspace/scratch/5ba97739b54c/a41-relocated-hosted-219821d`. Execution used a separate fresh `/workspace/scratch/5ba97739b54c/a41-hosted-run-219821d` working directory, private HOME, missing state and new output paths. Host: Linux 6.18.57 x86-64, glibc 2.41. The Python subprocess invocation is equivalent to:

```sh
bin=/workspace/scratch/5ba97739b54c/a41-relocated-hosted-219821d/bin/hammond_standalone
cd /workspace/scratch/5ba97739b54c/a41-hosted-run-219821d
env -i PATH=/usr/bin:/bin HOME="$PWD/home" LANG=C.UTF-8 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy SDL_RENDER_DRIVER=software "$bin" --help
env -i PATH=/usr/bin:/bin HOME="$PWD/home" LANG=C.UTF-8 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy SDL_RENDER_DRIVER=software "$bin" --smoke-ms 600 --state "$PWD/absent-controls.b3controls" --screenshot "$PWD/smoke.bmp" --diagnostics "$PWD/smoke.json"
readelf -h -l -d -V "$bin"
ldd "$bin"
```

Both application commands exited 0. Independent smoke: **56 callbacks, 28,672 frames, 12 images**, 48 kHz/512 frames, native float32 stereo, peak `0.08321372419595718`. Schema/profile, drivers, positive callback/frame totals, finite bounded peak, held screenshot, note-on/off, observed hold/release, completed smoke, joined shutdown and released final state were asserted. All format/render/overrange/nonfinite counters, queue overflow/recovery/rejection/fault counters and application error count were zero. One redundant shutdown command was discarded, as in CI; no held notes remained. State stayed absent and all nine payload hashes/modes remained unchanged.

The independently produced BMP has **exactly the same bytes/hash as CI**, and visual inspection showed the expected drawbars, held upper key, both manuals, pedals and dummy-audio status. Independent diagnostics SHA-256: `045021753f313f4c8f1696b2752eefe23766b8e0a71fbb5252f458ca8fc163f7`. Timing-dependent counts and diagnostic paths differ between runs; these diagnostics are not claimed deterministic. Scratch acquisition, verification scripts, logs and JSON summaries remain under `/workspace/scratch/5ba97739b54c/a41-hosted-linux` for this session.

## Runtime prerequisites and remaining work

`file`/`readelf` identify an unstripped x86-64 PIE ELF, build ID `1a02aaf46eecc59ac26f002e5c7644ba4b14d499`, interpreter `/lib64/ld-linux-x86-64.so.2`. Direct `NEEDED` entries are `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6`; all resolved here. Symbol requirements reach **GLIBC_2.38, GLIBCXX_3.4.32, CXXABI_1.3.9 and GCC_3.0**. No RPATH/RUNPATH or shared SDL dependency occurs. Static SDL therefore does not make the application wholly static or portable to arbitrary older Linux distributions.

Compiled SDL configuration dynamically loads `libasound.so.2`/`libpulse.so.0` for the respective audio backends and `libX11.so.6`, `libXext.so.6`, `libXcursor.so.1`, `libXfixes.so.3`, `libXi.so.6`, `libXrandr.so.2`, `libXss.so.1` for X11 and its extensions. Appropriate native runtime libraries, display/audio services and real-device checks remain necessary for those paths; this dummy run does not establish them. The package bundles no system libraries, raw fonts, VST3 SDK or PDF.

Live job metadata for this exact run reports Linux success; Windows `132202000157` and macOS `132202000415` failed the **build** step, with acceptance/package steps skipped. Subsequent repairs need separately named runs and artifacts. Physical audio/UI/MIDI, callback deadlines, other architectures, signing/notarization and release distribution remain outside this result. The named source has no project-wide LICENSE; retained dependency notices do not resolve project or supplied-atlas rights. Next: qualify the final newer source and its integrated replay path, repair/rerun other platform builds, then audit each successful platform package without reusing this older Linux result as blanket coverage.

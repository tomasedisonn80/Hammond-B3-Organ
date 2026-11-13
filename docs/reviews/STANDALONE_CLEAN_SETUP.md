# Standalone clean setup and relocation acceptance

**Result:** the documented ordinary build, optional native build, explicit
chapel export, benchmark location, and nine-file Standalone installation work
from a fresh Linux Release source archive in paths containing spaces and
Unicode. Eight selected SDK-free CTest suites and the complete **14/14 native
standalone group** passed. The relocated executable then passed seven direct
invocations with its original private source, SDL, build and staging paths
absent.

This is assignment **49**, `/root/w09_a49_clean_setup`, executed on
2026-11-13. It qualifies the frozen checkpoint below. It does not qualify the
concurrent timing repair or supersede the separate sanitizer failures retained
in [the sanitizer audit](STANDALONE_NATIVE_SANITIZERS.md).

## Frozen source and environment

| Item | Executed identity |
| --- | --- |
| Published source | `649b12c7d1faa7601fde1019e913347c65a6634a` |
| Equivalent local checkpoint | `79094d86316b99a8b3614fb1f41ba81a1a69840f` |
| Exact common Git tree | `cf63327d857b02029e8c5c6f406cab3d3c6890d1` |
| Archive | 37,068,800 bytes; SHA-256 `66fe3544c87f47b034ee33d97ac2ac4abf1e5af7bf50d90611098d5191069d36` |
| Source verification | All **842 tracked blobs** and executable modes match the frozen tree before building and after the build/tests. |
| Host | Linux 6.18.57, x86-64, glibc 2.41 |
| Compiler / build tools | GCC/G++ 14.2.0; CMake and CTest 4.4.4; GNU Make 4.4.1 |
| Authoring / dependency tools | Python 3.12.14; Git 2.52.0 |
| SDL | 2.32.10, tag `release-2.32.10`, commit `5d249570393f7a37e037abf22cd6012a4cc56a71` |

The coordinator supplied the exact committed tree before this agent created
the archive. The archive contains the accepted output-removal, Windows reader,
deterministic concurrency-test and calibration-mock fixes through assignment
46, plus removal of the unused drawing constants. Assignment 47's unfinished
timing edits are excluded. No live worktree source or old object files entered
these builds.

The private root was
`/workspace/scratch/5ba97739b54c/a49-clean-setup`. Source, both fresh build
directories, the private SDL checkout, install prefix and runtime cwd all used
spaces plus `é` and `音`. The SDL checkout was a fresh, non-hardlinked **local
clone of the available pinned cache**, outside the archived project. Both
pre-build and post-build `--verify-existing` invocations passed, reporting
`network_used: false`. This exercised dependency admission; it did not exercise
a fresh network download.

This machine satisfies the documented C++20, CMake 3.21+, Python 3.10+ and Git
prerequisites. Lower supported tool versions were not separately tested.

## Actual setup commands

The command recorder retained each argument vector, cwd, explicit environment,
UTC start, elapsed time, return code and complete combined output under the
private root's `results/` and `logs/`. The following aliases shorten the actual
paths; the command arguments are those executed. Build/configuration commands
inherited the session environment. No additional configuration switches were
introduced to make setup pass.

```sh
A49_ROOT='/workspace/scratch/5ba97739b54c/a49-clean-setup'
A49_CMAKE='/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake'
A49_CTEST='/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest'
cd "$A49_ROOT/source é 音"

"$A49_CMAKE" -S . -B '../build sdk free é 音' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
"$A49_CMAKE" --build '../build sdk free é 音' --parallel 2
"$A49_CTEST" --test-dir '../build sdk free é 音' -C Release \
  -R '^(test_console_engine|test_control_io|test_controls|test_parameter_bridge|python_test_cli_unicode|python_test_render|test_standalone_session|test_standalone_benchmark)$' \
  --output-on-failure --no-tests=error

python3 tools/acquire_sdl2.py --verify-existing "$A49_ROOT/SDL2 source é 音"
"$A49_CMAKE" -S . -B '../build native é 音' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON \
  "-DHAMMOND_SDL2_ROOT=$A49_ROOT/SDL2 source é 音"
"$A49_CMAKE" --build '../build native é 音' \
  --target hammond_standalone_test_inputs --parallel 2
"$A49_CTEST" --test-dir '../build native é 音' -C Release \
  -R '^test_standalone_' --output-on-failure --no-tests=error
```

The ordinary configure succeeded in 0.75 seconds and its default complete build
in 81.19 seconds. Its cache has `HAMMOND_BUILD_STANDALONE=OFF`,
`HAMMOND_BUILD_VST3=OFF` and an empty `HAMMOND_SDL2_ROOT`; it registers no C
compiler and creates no `_sdl2` build directory. Its eight selected suites
passed in **8.39 seconds**. There are 90 registered SDK-free suites in this
checkpoint; this assignment deliberately did not claim a full-core gate.

The native configure succeeded in 21.90 seconds and the fresh
`hammond_standalone_test_inputs` build in 84.44 seconds. All actual test inputs
were built before the required CTest group. Its single execution passed
**14/14 in 63.97 seconds**, with no skips, retries or relaxed expectations:

| Required native CTest | Result |
| --- | --- |
| `test_standalone_install` | Pass |
| `test_standalone_concurrency` | Pass |
| `test_standalone_session` | Pass |
| `test_standalone_state_files` | Pass |
| `test_standalone_ui` | Pass |
| `test_standalone_benchmark` | Pass |
| `test_standalone_audio_device` | Pass |
| `test_standalone_device_removal` | Pass |
| `test_standalone_callback_allocation` | Pass |
| `test_standalone_app` | Pass |
| `test_standalone_workflows` | Pass |
| `test_standalone_replay_boundaries` | Pass |
| `test_standalone_chapel` | Pass |
| `test_standalone_input_replay` | Pass |

SDL configuration reported missing ALSA/Pulse/PipeWire/JACK and X11/Wayland
development support. The generated configuration actually enables disk,
dummy and OSS audio; dummy and offscreen video; and the GLES2 renderer. These
are configuration observations. Every executed native audio/window case here
uses dummy audio/video and the software renderer. No physical backend was
silently substituted for missing development prerequisites.

The documented offline renderer command also ran, with a fresh Unicode output
path: `--frames 96000 --sample-rate 48000 --block-size 64 --seed 0 --drawbars
888000000 --note 60 --fail-on-clip`. The result contains 96,000 stereo PCM16
frames, bit-identical dry channels, positive nonzero sample content and zero
reported clipping. The 384,044-byte WAV has SHA-256
`f165a09c82bc3a70f91248dedf730c7fc190536a73008f4803067d000b142370`.

## Chapel and benchmark handoff recipes

Both targets were invoked explicitly from the frozen source cwd, followed by
the documented exporter and benchmark executable under `apps/standalone/`:

```sh
"$A49_CMAKE" -E make_directory '../run inputs é 音' '../new cwd é 音'
"$A49_CMAKE" --build '../build native é 音' \
  --target hammond_chapel_catalog --config Release
python3 tools/chapel_controls.py \
  --catalog '../build native é 音/chapel-catalog.json' \
  --upper 'C#' --lower off --bank A --expression 0.75 \
  --output '../run inputs é 音/chapel upper Csharp 音.b3controls'
"$A49_CMAKE" --build '../build native é 音' \
  --target hammond_standalone_benchmark --config Release
'../build native é 音/apps/standalone/hammond_standalone_benchmark' \
  --profile '../build native é 音/nominal.b3p' --sample-rate 48000 \
  --buffer-frames 512 --iterations 500 --warmup 16 --workload performance
```

The catalog is 4,837 bytes, SHA-256
`f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91`.
The 293-byte exported B3CONTROLS3 file exactly matches an independently
declared literal: upper A `005320000`, upper B zero, upper routed, both lower
banks zero and lower cancelled, pedals `00`, expression 0.75 and percussion
off/second/normal/slow. Its SHA-256 is
`a5af983f3a3b2bc37c09f9c6d150b448bdcd721a610e046b082f7686fcfebc98`.
It remained byte-identical after the relocated app loaded and auditioned it.
This is a documentary registration expressed through current nominal controls.

The benchmark returned schema `hammond-standalone-benchmark-v1`, status `ok`,
500 measured render calls / 256,000 frames, 16 warmup calls / 8,192 frames and
512,000 finite, bit-identical stereo samples. Seven setup commands were
accepted and applied; the measured stage reported zero discarded commands,
queue failures and recoveries. Its source fingerprint was independently
checked against all 57 manifest entries:
`5fd7837b44dbe8fd09bfbd9931c20065e29acfffee10f3adca1a622cb18b9bb8`.
Both builds generated the same 4,545-byte nominal profile, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

The benchmark executable is 154,568 bytes, SHA-256
`0c97a79e8c49dbad961090727fe3ae1668a283bdc4d87f4d334fc9c604981f19`.
It also built and passed its admission suite with native standalone OFF.
Timing was observed in this shared container, with other work active; no
performance comparison or device deadline conclusion is drawn. The JSON
explicitly retains `hard_realtime: false`, a null device deadline result and
`timing_threshold_applied: false`.

## Exact installed payload and runtime requirements

```sh
"$A49_CMAKE" --install '../build native é 音' --config Release \
  --component Standalone --prefix "$A49_ROOT/staged organ é 音"
```

The prefix contains exactly the following nine ordinary files. Every file
matches its frozen source or selected executable bytes. Metadata is mode
0644; the executable is 0755. In the table, `data/` abbreviates
`share/hammond-b3-organ/standalone/`.

| Installed file | Bytes | SHA-256 |
| --- | ---: | --- |
| `bin/hammond_standalone` | 2,602,864 | `f967f5fdab79e25d366d011b1f5e1fe719a8597f87265aa2d139a5c21079deed` |
| `data/STANDALONE_INSTALL.md` | 5,525 | `7ced9a7396b1a863c436a9f319309b8aac7fc31f98252ea68d8cf3fd75799f4c` |
| `data/STANDALONE_APP.md` | 13,842 | `74a1f16f82e164637f8bafada3812bdfb87087a90cae6c431d6621ddf946e2b8` |
| `data/STANDALONE_MODEL.md` | 4,837 | `bc62dc35dcb39d6538ac2b8475bd9cd997fd439f11201a3b2701e798c62f6649` |
| `data/THIRD_PARTY_NOTICES.md` | 10,792 | `ff72e873f84c98ce843bdcbe527ce4a5de9647aa67d5a703165093c04b9ab060` |
| `data/LICENSE-SDL2.txt` | 884 | `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` |
| `data/LICENSE-DejaVu.txt` | 2,345 | `22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6` |
| `data/sdl2-lock.json` | 375 | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |
| `data/font-source-manifest.json` | 1,428 | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |

`readelf -h -l -d -V` and `ldd` inspected this actual executable. Its ELF
interpreter is `/lib64/ld-linux-x86-64.so.2`. `DT_NEEDED` lists
`libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1` and `libc.so.6`; all resolve on
this host. There is no SDL shared-library entry and no RPATH/RUNPATH. Highest
referenced symbol versions are **GLIBC 2.38**, **GLIBCXX 3.4.32** and
**CXXABI 1.3.9**. This local package therefore still needs compatible OS and C++
runtimes. The observed symbol versions alone do not qualify every distribution
with those versions or a physical audio/window backend.

## Relocated execution with original paths absent

After all builds and CTests completed, the agent verified the 842 source blobs
and modes again, then moved only its private source, SDK-free build, native
build and SDL checkout into `unavailable originals é 音/`. The original four
paths were asserted absent. The private install prefix was renamed from
`staged organ é 音` to `moved organ é 音`; the original staging path was absent
too. The shared repository, shared SDL cache and other agents' builds were
never renamed or modified.

The two maintained replay files were copied byte-for-byte into the independent
`run inputs é 音/` directory before moving sources. A literal empty
`B3UIREPLAY1` input with `duration_ms 300` was added there for the fresh-process
reload. These and the ordinary controls file are explicit user inputs, separate
from embedded program resources.

Seven invocations used the relocated executable's absolute path from the fresh
cwd `new cwd é 音`. Their complete child environment was exactly:

```text
PATH=
LANG=C.UTF-8
LC_ALL=C.UTF-8
SDL_AUDIODRIVER=dummy
SDL_VIDEODRIVER=dummy
SDL_RENDER_DRIVER=software
```

The Python command recorder runs outside that child environment. The app had
no inherited `HOME`, `LD_LIBRARY_PATH`, source/build path or development-tool
PATH. The installed binary still uses the host's ordinary system loader and
libraries. This run establishes independence from the original input paths;
it is not a filesystem sandbox or a claim that no copy of the sources exists
elsewhere.

The shell equivalent of the recorded argument-array invocations is below.
The input copies and empty replay described above already exist; all output
filenames were fresh when executed.

```sh
A49_APP="$A49_ROOT/moved organ é 音/bin/hammond_standalone"
A49_INPUTS="$A49_ROOT/run inputs é 音"
A49_CWD="$A49_ROOT/new cwd é 音"
cd "$A49_CWD"
a49_run() {
  env -i PATH= LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy SDL_RENDER_DRIVER=software \
    "$A49_APP" "$@"
}
a49_run --help
a49_run --list-audio
a49_run --state "$A49_CWD/default missing 音.b3controls" --smoke-ms 600 \
  --screenshot "$A49_CWD/default window 音.bmp" \
  --diagnostics "$A49_CWD/default runtime 音.json"
a49_run --state "$A49_CWD/keyboard missing 音.b3controls" \
  --input-script "$A49_INPUTS/keyboard-notes 音.b3ui" \
  --diagnostics "$A49_CWD/keyboard runtime 音.json"
a49_run --state "$A49_INPUTS/chapel upper Csharp 音.b3controls" --smoke-ms 600 \
  --screenshot "$A49_CWD/chapel window 音.bmp" \
  --diagnostics "$A49_CWD/chapel runtime 音.json"
a49_run --state "$A49_CWD/saved registration 音.b3controls" \
  --input-script "$A49_INPUTS/save-controls 音.b3ui" \
  --diagnostics "$A49_CWD/save load runtime 音.json"
a49_run --state "$A49_CWD/saved registration 音.b3controls" \
  --input-script "$A49_INPUTS/reload only 音.b3ui" \
  --diagnostics "$A49_CWD/reloaded runtime 音.json"
```

| Invocation | Actual result |
| --- | --- |
| `--help` | Exit 0; prints the installed executable's usage. |
| `--list-audio` | Exit 0; reports dummy driver and `System audio output device`. |
| Fresh missing state, `--smoke-ms 600`, BMP and diagnostics | Exit 0; default proposed registration, 58 actual callbacks / 29,696 frames; held and released note observed. |
| Fresh missing state, maintained `keyboard-notes.b3ui`, diagnostics | Exit 0; all 18 events delivered, 4 On / 4 Off commands accepted, final command prefix acknowledged; 241 callbacks / 123,392 frames. |
| Exported chapel state, `--smoke-ms 600`, BMP and diagnostics | Exit 0; exact exported controls loaded; 57 callbacks / 29,184 frames. |
| Maintained `save-controls.b3ui`, fresh state path, diagnostics | Exit 0; Ctrl+S and Ctrl+O save/restore the expected state; 202 callbacks / 103,424 frames. |
| New process, saved state, empty 300 ms replay, diagnostics | Exit 0; identical saved controls, no held notes or injected On/Off commands; 30 callbacks / 15,360 frames. |

The keyboard replay's distinct observed states independently match upper MIDI
60, then lower MIDI 74, then pedal 17, their original releases in order, and a
new upper MIDI 72 press/release after the target/octave changes. The completion
snapshot is empty and acknowledges the last submitted sequence. This checks
the actually observed holds; it does not infer note application solely from
event delivery or treat the sampled observations as a latency measurement.

Save/Load produced an independently declared **290-byte B3CONTROLS3** file,
SHA-256 `2a020a124121138675c0804e9a2961c52656fd7d8edc28f59c20ab5b6cd67974`:
upper B `088000000`, lower B `008000000`, both routes enabled, pedals `80`,
expression 1, both A banks zero and percussion off. The script leaves upper
MIDI 60 held in its pre-shutdown snapshot; joined shutdown clears it. A new
process reloads the same controls with empty manual/pedal holds. The two
deliberately missing state paths remain absent, confirming these runs did not
silently auto-save on shutdown.

All five window runs report positive rendering and audio callback/frame counts,
zero recorded errors, zero audio render/format/nonfinite/overrange failures,
zero recovery/overflow/rejection/fault counts and a stopped Session with no held
notes after shutdown. Each records one discarded redundant lifecycle cleanup
command; the pre-shutdown replay prefixes are fully acknowledged. This count
is retained rather than presented as zero.

Both smoke BMPs are actual 1280×900 backbuffer captures, 4,608,122 bytes each,
with `screenshot_while_held: true`. SHA-256 values are
`a774880df19f2efb9a3eb1534edfef5ad0f7a464cf0cefc900ec5cb6dbcf7097` for the
default view and
`c4864aef0e90dfe03a0e7646e685c72cf55fc3a2ebc637ea56584c3178288707` for the
chapel view. The chapel image was visually inspected: it shows the native
instrument, upper Sounding A, lower Cancel, 75% expression and the held upper
key. Edit B remains selected independently of Sounding A, so the displayed
editable drawbars correctly show B's zero values.

All nine package files still match their original bytes and modes after these
runs, and all five original paths remain absent. Raw run evidence remains
under the private root; this report preserves the durable commands, identities,
observations and limitations. Moved CMake builds retain their original absolute
paths and should not be used as a new build tree.

## Findings, remaining prerequisites and next steps

No setup, build, required native test, documented target-path, export,
installation or relocation failure was found within this Linux Release scope.
No production or test change was needed for this assignment. The setup recipes
in the frozen [operational handoff](../STANDALONE_HANDOFF.md) and
[installation guide](../STANDALONE_INSTALL.md) are concrete and runnable with
the declared prerequisites.

The next source gate is a fresh coherent build of the completed timing repair,
including the failing sanitizer scenarios retained in the separate audit.
This report must not be relabeled as evidence for that later tree. The final
coordinator also owns the full-core gate, hosted Linux/macOS/Windows results,
shared status updates and commit/push verification.

No Windows or macOS build, fresh network dependency acquisition, oldest
supported toolchain, physical device, actual desktop capture, device hotplug,
high-DPI scaling, callback deadline, native accessibility, production signing
or measured instrument match was exercised here. Before extending those
claims, supply the relevant platform development libraries and real
device/window environment, then execute the corresponding gates on the exact
new checkpoint. Atlas pages 450–451 and [the project plan](../PLAN.md) keep this
M9 standalone adapter acceptance separate from integrated-model and product
release completion.

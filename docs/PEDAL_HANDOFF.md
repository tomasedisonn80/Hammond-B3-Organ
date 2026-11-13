# Pedal and native development handoff

This is the operational entry point for the active
[2026-11-13 pedal session](development/2026-11-13-pedals/README.md). The program
now renders both manuals and 25 pedals through one shared nominal source bank,
and has an optional, actual `HammondB3.vst3` instrument. Its physical models are
unmeasured; the full product remains in development. Read
[STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md) and the newest
[development log](DEVELOPMENT_LOG.md) before treating a dated result below as
the current release state.

## Resume from an identified source

Every future agent follows [AGENTS.md](../AGENTS.md): inspect the current
repository and plan, claim a dependency-ready scope in the newest ledger,
retain actual checks and failures in a substantive assignment note, and leave
the next step explicit. The integrator owns shared status and commit/push
publication. The owner has authorized that publication; preserve unrelated
work, use the expected remote head, and never force-push or claim an unobserved
remote result. Earlier sessions' sixty workers do not count toward this
session's sixty new assignments in ten waves.

From the repository root, inspect before building or changing files:

```sh
git status --short
git rev-parse HEAD
git rev-parse HEAD^{tree}
git log -5 --oneline
```

Read [PLAN.md](PLAN.md), the relevant current contracts below and the
[complete atlas review](research/ATLAS_REVIEW.md). The supplied 500-page PDF
remains unchanged: SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Six fresh readers in this session covered all pages and selected diagrams;
that is not independent verification of every figure or referenced external
asset. Companion captures referenced by the atlas were not supplied.

### Identified snapshots

| Identity | What it identifies |
| --- | --- |
| `d7b886103f8c9d4649ffa1c35930b79808217a3d`, tree `018c3897889aaae0070f632981e0c889a35cad30` | Published wave-6 native checkpoint; exact archived source of the retained pedal demo. |
| `9403debd754f771bf39bc8cd771ecfd86c0f14d6`, tree `e2a00f7c270317b0f07be8a467120d8a573bb61a` | Subsequent published native portability repair inspected by assignment 46. Its hosted Windows inventory failure is retained below. |
| `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`, tree `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac` | Published/fetched wave-7 checkpoint with exact local/remote identity confirmed by root. Only six Markdown result files differ from the repaired tree below. Its new core/native hosted runs were queued at publication. |
| `7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73` | Initial frozen wave-7 source tree inspected for this handoff's executable/CTest discovery checks. This is a tree identity, not a published commit or a claim that later repairs were already included. |
| `e50351633caddecc212aef3a934378aeda498870` | Repaired wave-7 tree: only the install assertion, inventory tests and inventory tool differ from the initial frozen tree. Root separately reran the two affected Python suites with the original configured environment and unchanged build inputs. |
| `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` | SHA-256 of the 4,545-byte compiled nominal profile used by the retained demo and inspected native build. |

Do not combine a new header with an older library or test executable. For an
isolated reproduction, select an existing committed revision and use a new
detached worktree and new build directories. For example, after selecting the
desired `HEAD`, `git worktree add --detach ../hammond-clean-source HEAD` creates
a committed source snapshot; it does not include uncommitted work. Record the
actual selected commit, toolchain and generated input identities with results.

## Default clean build and tests

Prerequisites are a C++20 toolchain, CMake/CTest 3.21+ and Python 3.10+. The
default build uses the standard libraries and downloads no dependencies.
From the selected clean source root, choose an unused `build-release` directory:

```sh
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-release --config Release --parallel 2
ctest --test-dir build-release -C Release --output-on-failure --no-tests=error
```

These explicit commands also work with Visual Studio from its developer
terminal; keep `--config Release` and `-C Release`. Single-configuration
executables are normally under `build-release/`; Visual Studio executables are
normally under `build-release/Release/` with `.exe`. The generated profile stays
at `build-release/nominal.b3p`. [BUILD.md](BUILD.md) documents presets,
compiler/Python selection and the separate sanitizer build.

Build before CTest: CTest does not compile its inputs. Discover the selected
configuration with `ctest --test-dir build-release -C Release -N`; its count
belongs to that configured source. The initial wave-7 Linux snapshot registered
68 ordinary suites and eight additional focused native suites when enabled.
New wave-8 tests change discovery; those earlier counts are not a permanent
allowlist or a substitute for executing the current suite.

## Render, retain and inspect the pedals

Use new output filenames/directories. The renderer, trace exporters and plotters
preserve existing destinations and require hard-link support for publication.
Output parent directories must exist. The following commands use the
single-configuration executable paths; adjust the configuration subdirectory
and `.exe` suffix on Windows.

```sh
cmake -E make_directory out
./build-release/hammond_render \
  --profile build-release/nominal.b3p \
  --events examples/fixtures/pedals/pedal-phrase-v1.events \
  --output out/pedal-phrase.wav \
  --sample-rate 48000 --frames 144000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 --contacts ideal \
  --percussion off --percussion-volume normal --percussion-decay slow \
  --fail-on-clip
./build-release/hammond_model_info
./build-release/hammond_parameter_info --normalized 0.5
```

The score sets expression `0.75` and the lower-manual registration. The output
is three seconds of stereo PCM16 with identical dry channels. The renderer
reports pre-encoding float metrics separately from serialized PCM measurements.
`hammond_parameter_info` reports 45 compiled mappings using diagnostic schema 2:
`verification_scope` is `sdk-free-core-parameter-mapping`, and
`host_exports_verified` and `native_host_curves_verified` are false. Those are
the offline command's evidence scope, not claims that the optional native
implementation is absent.

For a new schema-3 evidence bundle containing inputs, logs and audio:

```sh
python3 tools/render_fixture.py \
  --renderer build-release/hammond_render \
  --profile-json data/profiles/nominal-unmeasured-v1.json \
  --events examples/fixtures/pedals/pedal-phrase-v1.events \
  --output-dir out/pedal-phrase-evidence \
  --sample-rate 48000 --frames 144000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 --contacts ideal \
  --percussion off --percussion-volume normal --percussion-decay slow
python3 tools/verify_render.py out/pedal-phrase-evidence
python3 tools/analyze_wav.py --input out/pedal-phrase-evidence/render.wav
```

Inspect the producer's `status`; only `succeeded` is success. Read
[PEDAL_RENDER_EVIDENCE.md](PEDAL_RENDER_EVIDENCE.md) for the exact schema and
legacy acceptance boundaries. The independent verifier checks retained bytes
and numerical consistency. It does not execute a manifest's historical command
or authenticate source/build provenance on its own.

### Retained example

The complete demo lives at
[`examples/demos/pedal-phrase-v1/`](../examples/demos/pedal-phrase-v1/README.md),
including its actual WAV, source inventory, producer manifest and seven PCM
reports. Its complete WAV is 576,044 bytes, SHA-256
`a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1`.
The producer observed identical complete WAV bytes for blocks 64, 127 and 1024,
zero pre-encoding clipping, and exact leading/trailing silence. These are
same-build observations; no subjective listening or cross-compiler identity is
implied. The example README contains the exact recorded-source replay recipe.

```sh
python3 tools/verify_render.py examples/demos/pedal-phrase-v1/bundle
python3 tools/analyze_wav.py --input examples/demos/pedal-phrase-v1/bundle/render.wav
```

The previous console examples remain intact at
[`examples/rendered/nominal-console-v2/`](../examples/rendered/nominal-console-v2/README.md)
and [`examples/rendered/nominal-two-manual-v1/`](../examples/rendered/nominal-two-manual-v1/README.md).
Their older schemas and source identities remain historical compatibility cases.

### Same-frame traces and plots

```sh
./build-release/hammond_pedal_trace \
  --profile build-release/nominal.b3p --scenario routing \
  --sample-rate 48000 --seed 0 --output out/pedal-routing.csv
python3 tools/plot_pedal_trace.py \
  --input out/pedal-routing.csv --output out/pedal-routing.svg
```

Use `unmute`, `overlap` or `routing`; all three are fixed 120 ms scenarios at
44,100, 48,000 or 96,000 Hz. Change the output name for each invocation.
The CSV contains actual same-frame Engine buses, mixtures, contact bits, controls,
audio and source phase; it is not a trace of the three-second score above.
The standalone Python plotter reads that bounded CSV and retains its byte hash.
See [PEDAL_TRACE.md](PEDAL_TRACE.md) and
[PEDAL_TRACE_PLOTS.md](PEDAL_TRACE_PLOTS.md) for validation and display reductions.
Console CSV/plots keep their distinct tools and schema.

## Local offline installation

After the default build, choose a fresh local prefix:

```sh
cmake --install build-release --config Release --component OfflineTools \
  --prefix "$HOME/hammond-offline-stage"
```

The implemented wave-8 component contains **23 files**: five native offline
tools, both standalone plotters, one generated profile, three catalogs and
twelve scores. [OFFLINE_INSTALL.md](OFFLINE_INSTALL.md) and
`cmake/InstallHammondTools.cmake` own that exact payload. Root integrated pedal
plotter preflight/installation and relocated SVG comparisons for all three
scenarios. Root's [coherent wave-8 gate](reviews/PEDAL_WAVE8_INTEGRATION.md)
subsequently passed all 71 ordinary and eight focused native suites. Historical
8-, 16- and 22-file checks qualify their named versions. A checkout at the
published wave-7 commit still has the earlier 22-file component.

Keep `CMAKE_INSTALL_MODE` unset or `COPY`. Pass the installed compiled profile
and event paths explicitly after relocation; there is no implicit runtime
profile discovery. Native executables still require a compatible OS/compiler
runtime, and plotting requires Python. CMake's offline install can replace
existing files in its selected prefix, so choose a new prefix for a new version.
This package does not install the benchmark, SDK or an audio-device application.
For a prefix built from the wave-8 source, the installed pedal plot command is:

```sh
python3 "$HOME/hammond-offline-stage/bin/plot_pedal_trace.py" \
  --input out/pedal-routing.csv --output out/pedal-routing-installed.svg
```

## Optional actual VST3 build, test and staging

Native builds additionally require CMake 3.25+ and the explicitly acquired SDK
pinned by [vst3-sdk-lock.json](../data/dependencies/vst3-sdk-lock.json).
Configuration never fetches dependencies. Use a new external directory for
acquisition, or verify an existing one without modifying it:

```sh
cmake -E make_directory "$HOME/hammond-dependencies"
python3 tools/acquire_vst3_sdk.py \
  --destination "$HOME/hammond-dependencies/vst3sdk"
python3 tools/acquire_vst3_sdk.py \
  --verify-existing "$HOME/hammond-dependencies/vst3sdk"
```

| SDK input | Pinned commit |
| --- | --- |
| SDK 3.8.1, tag `v3.8.1_build_84` | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| `base` | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| `cmake` | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| `pluginterfaces` | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| `public.sdk` | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

The helper checks parent gitlinks, worktree cleanliness including ignored files,
five MIT license files and the embedded parser identity. Keep all builds outside
the SDK checkout. [VST3_BUILD.md](VST3_BUILD.md) explains acquisition failures,
platform configuration and the separate SDK/project build policies.

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT="$HOME/hammond-dependencies/vst3sdk" \
  -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build-native --config Release --parallel 2 \
  --target hammond_vst3_test_inputs
ctest --test-dir build-native -C Release --output-on-failure --no-tests=error \
  -R '^(hammond_vst3_validator|test_native_)'
cmake --install build-native --config Release --component NativeVST3 \
  --prefix "$HOME/hammond-native-stage"
```

`check_vst3` combines the maintained native input build and focused CTest run.
The generated `build-native/hammond-vst3-path-Release.txt` gives the actual
bundle path; do not assume every platform uses the Linux module layout. With
the explicit `lib` setting, installation stages
`$HOME/hammond-native-stage/lib/vst3/HammondB3.vst3`. The component requires an
absent destination bundle and refuses to merge or overwrite one. It copies the
complete bundle and notices without registering it or creating a DAW scan link.
See [VST3_LOCAL_INSTALL.md](VST3_LOCAL_INSTALL.md).

| Native surface | Supported contract |
| --- | --- |
| Audio | No audio input; one stereo float32 output with identical dry samples. Float64 is unsupported. |
| Rate and block | 44.1, 48 and 96 kHz; maximum 65,536 frames; zero-frame control/event flushes are supported. |
| Event buses | Upper `0`, Lower `1`, Pedals `2`; all 16 channels retain ownership identity. No MIDI output. |
| Notes | Manuals MIDI 36–96; pedal MIDI 36–60 maps to physical routing identifiers 1–25 under the named software policy. |
| Controls | 45 permanent parameter IDs; existing 43 records preserved, pedal mixtures appended as `0x4000`/`0x4001`, each position 0–8. Initial pedal positions are `00`. |
| State | Writes `B3CONTROLS3`; reads versions 1/2/3 with explicit muted-pedal migration. Musical controls and routing are saved; owners, phases and transient DSP histories are not. |
| Editor | Generic host parameter controls. No custom native editor or standalone device application. |

The processor/controller UUIDs remain
`19f9adc0-533f-42b4-b96b-d51d6547e838` and
`0dee76ab-26bc-475a-bf64-f138c89fb0e0`. Native processing uses one transactional
timeline, preallocated candidate rendering and the bounded concurrent state
exchange. The [processor](VST3_PROCESSOR.md),
[automation review](VST3_AUTOMATION_REVIEW.md),
[concurrency evidence](VST3_CONCURRENCY.md) and
[allocation audit](VST3_REALTIME.md) state the actual limits.

## Evidence and remaining gates

| Observed scope | Result and boundary |
| --- | --- |
| Wave-6 local coherent source | 67 ordinary Release suites and four actual native suites passed on the named source in the session log. Later changes require their own run. |
| Initial wave-7 local frozen source | Both builds succeeded; eight focused native suites passed in 6.68 seconds. The first ordinary run passed 67/68 in 70.98 seconds; its install fixture still expected parameter diagnostic schema 1. Root corrected the assertion to schema 2 and added scope checks. |
| Repaired wave-7 tree `e5035163…` | Root observed two install methods passing in 3.067 seconds and 19 inventory methods passing in 0.203 seconds with the original configured environment and unchanged build inputs. This focused repair execution is not a newly executed full 68/68 run. |
| Published wave-7 `7fb9b612…` | [Core run 43415692328](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692328) and [native run 43415692247](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692247) were queued at publication. Consult current status and the portability review for observed outcomes; this handoff does not infer a pass. |
| Hosted repair `9403debd…` | Actual four-suite native CTest passed on Linux, macOS and Windows. Complete Linux/macOS native jobs succeeded; Windows subsequently failed bundle inventory. Core Windows passed 66/67 suites, failing two synthetic final-inventory stability cases inside its inventory suite; Linux/macOS/sanitizer jobs passed. This is not a fully passing native or core matrix. See the [portability review](reviews/PEDAL_NATIVE_PORTABILITY.md) and [CI.md](CI.md). |
| Native validator | The retained actual-module run reported 47 passed, zero failed and exit 0, with 16 teardown diagnostics and nine unsupported-rate `ERROR` messages. The separate 51-case SDK selftest is not a module test. No warning-free validator claim is made. |
| Later Linux native audits | Scoped allocation checks, dense 45-parameter automation, actual moved-bundle ABI execution and concurrent state calls have separate retained evidence. Fully instrumented TSAN covers the recorded finite workload, not all possible interleavings or device deadlines. |
| Demo and compatibility | Actual retained schema-3 audio and old schema-1/2 examples exist. Legacy comparison preserves all eight prior fixture WAVs and all 43 prior registry records. A byte check is not physical calibration or signed provenance. |

The inventory's source revision field is caller-declared; its file hashes
identify bundle bytes and its parser identifies supported module headers.
Inventory success does not load a plugin or prove host compatibility. The native
workflow retains actual bundles separately from diagnostic logs; neither is a
signed release. [DEPENDENCIES_AND_RIGHTS.md](DEPENDENCIES_AND_RIGHTS.md) retains
the unresolved project-wide licensing and research-asset questions.

Wave-7 Windows now passed all 68 ordinary and seven native suites, completed
inventory and uploaded its bundle; Linux passed its ordinary, sanitizer and
eight native suites and uploaded its bundle. Root independently verified both
actual artifact archives. The [portability review](reviews/PEDAL_NATIVE_PORTABILITY.md)
retains exact jobs and hashes. macOS was still queued at that observation.
Qualify wave 8's retained demo replay, implemented plot/install extension and
operational records, then finish the independently assigned final review waves.
The [new session checker](PEDAL_SESSION_CHECKS.md) validates this session only:

```sh
python3 tools/check_pedal_session.py --repo . --json
```

Add `--expected-complete 60` only after all sixty actual assignments have been
accepted. The older repository/continuation checkers retain their historical
scope and cannot establish the new count.

For product development, follow [PLAN.md](PLAN.md) and
[M3_ACCEPTANCE_CONTRACT.md](M3_ACCEPTANCE_CONTRACT.md): physical preset latches,
continuous drawbars, switching bandwidth and loaded expression remain open.
The current pedal matrix/gain is a declared nominal surrogate; documentary
25-by-8 routing does not establish reactor loading, low-wheel spectra or
calibrated 16-foot/8-foot responses. M4 scanner work needs its reviewed topology,
corrected traversal and independent numerical oracle before implementation.
The [concrete remaining M3/scanner gate](M3_REMAINING_AND_SCANNER_GATE.md)
specifies the next graph/schema/compiler commit, candidate component endpoints,
independent DC/AC known answers and later integration/capture requirements.
AO-28, Leslie electronics/acoustics, actual specimen capture/calibration,
DAW project save/reopen, device scheduling, accessible UI and signing each retain
their separate M4–M9 gates. Record concrete next evidence, not an inferred product
completion from software tests.

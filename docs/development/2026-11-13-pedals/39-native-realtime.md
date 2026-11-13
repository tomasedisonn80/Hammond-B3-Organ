# Assignment 39 — actual module allocation qualification

- Actual worker: `/root/w07_a39_native_realtime`.
- Current session: 2026-11-13 pedal development; wave 7, assignment 39.
- Status: complete; owned code and evidence frozen for root integration.
- Owned files: `plugins/vst3/tests/test_native_realtime.cpp`, private helper
  `plugins/vst3/tests/NativeAllocationProbe.h`, `docs/VST3_REALTIME.md`, this note.
- Production source, SDK source, live CMake, shared handoff/manifest, staging,
  commit and push were not changed by this worker. Root owns the separate
  Linux target/link hook, integration and authorized publication.

## Scope and source basis

Read the standing agent instructions, current project/status/next-step and
handoff records, the plan/atlas review, the native processor/build contracts,
the existing enabled core allocation audit, and the frozen native harness.
The applicable atlas boundary is pp. 385–396: native host admission, bounded
callbacks, a single render timeline and separate product qualification.
This worker did not claim a new independent reading of all 500 PDF pages.

The missing gate was actual dynamically loaded module allocation evidence.
The core-only audit did not prove interception of a shared module or SDK
boundary. The deliverable measures the native virtual API, proves its probe
reaches the existing module, and retains direct-reference musical checks.
The report [VST3_REALTIME.md](../../VST3_REALTIME.md) records the full workload,
counts, timing observations, exclusions and reproduction path.

The coherent source copy is `/workspace/scratch/f364bc93d920/a39-native-source`,
created from the completed `a33-native-source` snapshot. That snapshot traces to
root's frozen fifth-wave tree `06786b70f1cffcc6371600fd6e14306f16e8c985` plus the
frozen assignment-31/32 native implementation, assignment-33 build inputs and
assignment-34/35 harness/ABI/behavior inputs. The two assignment-39 C++ files
and a scratch-only test registration/link hook were then overlaid. No live
headers were linked against an older core. A new
`/workspace/scratch/f364bc93d920/a39-native-build` rebuilt all consumed core,
SDK, loader, harness and module inputs. Existing A33/A34/A35 evidence was
preserved.

All `include/` and `src/` bytes match the subsequently frozen W6 source tree
`b2dae50dcde294bde8e7acb7addb14456197a779`. The native production and harness
identities below are unchanged. The resulting module is byte-identical to the
previous native ABI/behavior result. The final 51-file manifest of
`include/`, `src/`, and `plugins/vst3/` inputs is retained locally as
`a39-compile-inputs-final.json`, SHA-256
`946292a4f27e9015b5356b6e3fb83481187f329de9ad191bca38bd0f2b329054`.
It identifies this test snapshot; it is not a claim that this worker published
a new repository commit.

## Implementation and probe proof

`test_native_realtime` uses the actual SDK module loader, raw native factory,
`IComponent` and `IAudioProcessor`. It does not compile `Processor.cpp` into the
test executable or use `timeline_for_testing()` to impersonate native work.
The reference Engine runs outside the counted regions and supplies known
physical events or independently calculated per-sample expression values.
All host event/parameter storage is allocated before each measured call.

The private allocation helper reuses the established global C++ replacement
mechanism. Twelve calibration pairs cover eight allocation/twelve deletion
overloads, including zero-size, nothrow, sized and aligned forms. Calibration
calls use volatile function pointers to prevent allocation elision. The main
measurement resets counts for each call and asserts only after recording stops.

Actual module proof separately creates and releases an uninitialized processor
and controller through the raw module factory. Each measured construction
reported one allocation/zero frees; each release reported zero allocations/one
free and a zero remaining reference count. This construction is separate from
host object, loader and fixture setup. Positive balanced counts are required.

### Corrected instrumentation scope, retained as a failure

The initial `--export-dynamic` design successfully intercepted the module's
factory allocation. Its initial callback run also passed 132 regions. Inspection
then found that broad export published the host reference Engine's symbols,
which can substitute host DSP into an ELF module. That run is not accepted as
native allocation qualification. There was no production defect or module
change; the measurement scope was wrong.

The corrected Linux hook selectively exports only the four mangling families
`_Znw*`, `_Zna*`, `_Zdl*`, `_Zda*`. Root received this correction and owns the
live CMake edit. The final test adds a startup `dlsym` guard against exporting
the reference Engine. A separately relinked executable with broad export
returned exit **1**, with the expected diagnostic:

```text
test_native_realtime: reference Engine is dynamically exported; native module isolation is invalid
```

The final executable's dynamic symbol table contains all **20 allocation/
deletion replacement overloads and zero `hammond` exports**. A final-executable
`LD_DEBUG=bindings` run passed the test and yielded these observed bindings:

| Requested by the actual module | Resolved provider |
| --- | --- |
| 59 `hammond` function bindings, including const members | The same `HammondB3.so` |
| `Engine::process` and `HostTimeline::process` | The same `HammondB3.so` |
| State exchange audio peek, commit preflight and commit | The same `HammondB3.so` |
| `_Znwm` and `_ZdlPvm` (two exercised native allocation symbols) | `test_native_realtime` |

All 20 overloads have executable calibration/export evidence. The loader trace
only claims the two native allocation symbols actually exercised. Trace timing
is excluded from the observation table. No production module instrumentation,
SDK patch, or new third-party dependency was needed.

## Actual commands

The following were executed from the scratch parent or with the shown absolute
paths. Configuration internally verifies the clean pinned SDK. The source copy
and CMake hook were prepared before configuring; the final source copy was
updated only with this worker's own test change.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a39-native-source \
  -B /workspace/scratch/f364bc93d920/a39-native-build \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/vst3sdk
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/a39-native-build \
  --target test_native_realtime --parallel 2
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/a39-native-build \
  -R '^test_native_realtime$' -V
nm -D /workspace/scratch/f364bc93d920/a39-native-build/bin/Release/test_native_realtime
LD_DEBUG=bindings \
  LD_DEBUG_OUTPUT=/workspace/scratch/f364bc93d920/a39-final-loader-bindings \
  /workspace/scratch/f364bc93d920/a39-native-build/bin/Release/test_native_realtime \
  /workspace/scratch/f364bc93d920/a39-native-build/VST3/Release/HammondB3.vst3 \
  /workspace/scratch/f364bc93d920/a39-native-build/nominal.b3p
```

The negative-control command was generated from the final target's `link.txt`
using Python `shlex.split`, retaining every object/library and adding
`-Wl,--export-dynamic`; `-o` was changed to
`/workspace/scratch/f364bc93d920/a39-final-broad-negative-control`. The module
and all source objects remained untouched. Executing that program with the
same bundle/profile arguments produced the expected rejection above.

Environment: Linux 6.18.57 x86-64, glibc 2.41, GCC 14.2.0, CMake 3.31.6,
Python 3.12.14. Project flags include `-O3 -DNDEBUG -std=c++20 -Wall -Wextra
-Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`. The SDK root is
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`; its four module commits and licenses
are unchanged from the repository lock. This assignment did not rerun the
SDK validator or claim new DAW/device/hosted results.

## Final observed result

The final selected CTest passed **1/1**, zero failures, **0.91 seconds**. Its
133 measured regions comprise 82 accepted/30 rejected native process calls and
15 accepted/six rejected `setProcessing` calls. Every region observed **zero
allocations and zero deallocations**. The extra region compared with the
intermediate run admits a fresh full 1,024-point budget after consuming full
carry, proving that stale duplicate carry does not remain.

```text
path accepted rejected frames fresh_raw carried_raw queued_restores new delete total_us max_us
enabled 37 0 13022 9 0 28 0 0 28823.925 6450.623
dense 5 0 224 4608 0 4 0 0 1285.581 600.910
maximum 3 0 196608 6 0 0 0 0 401692.676 138342.908
carry 13 0 32 2054 1027 0 0 0 385.551 114.154
output-shape 24 0 1152 0 0 0 0 0 2610.977 230.364
rejected 0 30 0 0 0 0 0 0 17.391 2.266
setProcessing 15 6 0 0 0 0 0 0 1.351 0.189
regions=133 overload_calibration=12/12 exact_channel_samples=421308
audible_samples=417960 reference_frames=211038 state_reads=132
rollback_cases=27 future_channel_samples=16572 moving_contact_checks=4
owner_capacity_checks=2 assertions=5206536 checksum=34119173a07f00c7
```

Coverage includes enabled manual/pedal/percussion processing with moving contacts
at all three supported rates, 65,536-frame callbacks, 1,024 native raw records,
1,024 carry records, 256 owners in each namespace, four queued restores, normal/
zero/disconnected/inactive/exact-alias outputs, native accessor/payload failures,
late transactional rejection, state preservation and meaningful future audio.
The reference contains all 122 manual physical notes and 25 pedals for the
full-owner fixture. The report explains precisely what each count means.

## Frozen identities and retained evidence

| Input/output | SHA-256 |
| --- | --- |
| `test_native_realtime.cpp` | `28bea0fa3cbc30f0796e61486a66fe499b84406498969a8d1a4a75a2a9adf23c` |
| `NativeAllocationProbe.h` | `e61fbceddf7fa3df138b534117daf9cdb49a10098ef6864bdadac65335ab57d4` |
| `NativeHarness.h` | `0067515c5259288f1f711e4ce8c0921721682209863ca62ccbee4f50dbb2752a` |
| `NativeHarness.cpp` | `899d504d842e2e1b83d7f629e0bb4335b0c4f4191d7568df90980f27c09828b7` |
| `Processor.h` | `e85cdc6f7aaf70c05eda61630a5e3acee7c7f2fef2796a2c5f557ce034a54e72` |
| `Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `Controller.cpp` | `24b71a4a49d6234def8f9336e22de927577bf75bb859769b9af4a7ff840d41d6` |
| Final executable, 341,568 bytes | `855cdc7333042bec99a3d68ddf848d145aebdda89230265832e6ac3aa1ef228d` |
| Actual module, 434,168 bytes | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| Compiled profile, 4,545 bytes | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Final CTest log | `2c23279ad35b44259682ad423c52290867ae73d44eeb88fd381922936cad2aff` |
| Final loader binding trace | `8723a542276fb635498a5f467d771ab0f4c502fae220a663ea995c5135be3584` |
| Final negative-export control log | `9f081deafc0d1071481a5c4da984b2d3c805742fa37e1cce8c58d0f51674fbda` |
| Final executable dynamic-symbol listing | `42ec220d830b9a2e27a1b5cf3bd9ee9d8df9f12fedc51f00efe15572ba4ffd06` |

Local evidence lives under `/workspace/scratch/f364bc93d920/`:
`a39-configure.log`, `a39-configure-02.log`, `a39-build-01.log` through
`a39-build-04-final.log`, `a39-ctest-01.log` (excluded broad-export result),
`a39-ctest-02-selective.log` (intermediate isolation-corrected result),
`a39-ctest-03-final.log`, `a39-final-loader-bindings.6`,
`a39-final-loader-run.log`, `a39-final-loader-binding-summary.txt`,
`a39-final-negative-export.log`, and
`a39-final-executable-dynamic-symbols.txt`. The preceding sections reproduce the
critical results and failed measurement method so the handoff does not depend
on those temporary paths surviving. No compile or native callback defect was
observed; the broad-export methodology failure and intended negative-control
failure are explicitly retained.

## Integration and next action

Root should integrate these four owned files together with its Linux-only
`test_native_realtime` target, selective operator-export flags, actual bundle/
profile arguments and native test-input aggregate membership. Rebuild the
coherent combined tree, run the affected native gate, update shared current
status/next steps/development log and mark the actual assignment complete.
The standing owner authorization then permits the integrator to commit and
push the completed checkpoint, verifying remote head and exact-source CI.
This worker has not claimed that publication happened.

Next evidence: concurrent actual-module UI state/processing stress, native CI
for the combined revision, and independently proved allocation interception on
macOS/Windows. There is no synthetic passing/skipped test for those platforms.
Only the Linux calling thread's global C++ calls are observed here; direct C
allocation, locks, system calls, other threads and device deadlines remain
outside this test. Timing values are observations, never hard thresholds.
Continue actual DAW/device and release qualification without promoting nominal
models or this bounded engineering test into a hardware-fidelity claim.

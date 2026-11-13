# Assignment 50 — native protocol review

Owner: `/root/w09_a50_native_protocol_audit`.

Assignment **50/60**, wave **9**, current 2026-11-13 pedal session. This is one
newly dispatched worker. The spawning interface displayed an aborted label,
but the worker actually ran, notified root, performed the review and executed
the focused tests recorded below. No subagent was created.

## Scope and outcome

Owned only `docs/reviews/PEDAL_NATIVE_PROTOCOL_FINAL.md` and this note. Reviewed
the processor/controller boundary, bounded native state streams, sample-linear
host timeline and SPSC control publication. **No actionable production defect
was found; no production or test code was changed.** The
[full review](../../reviews/PEDAL_NATIVE_PROTOCOL_FINAL.md) records each concrete
risk, the implementation reason and the executed coverage.

The focus was whole-callback rejection, malformed SDK admission, the shared raw
record budget, all 45 automation identities, offset-N carry, zero-frame
behavior, pending state and acknowledgement, control-vs-transient persistence,
rounding policy, bounded concurrent publication and valid lifecycle ownership.
The exact reviewed code preserves its existing contract. No speculative code
change was made merely to increase the change count.

Read [AGENTS.md](../../../AGENTS.md), current operating handoff, project plan,
status/next-step context, atlas review and native/timeline/state contracts.
Used the cloud runtime skill; no package, network or credential change was
needed. Freshly reread complete atlas text pages **389–394 and 400–401** for
state/curve/lifecycle requirements. Those eight pages do not constitute a new
entire-PDF review or fresh external SDK-source verification.

## Coherent source and dependency identity

The executable inputs came from root's frozen wave-7 archive:

- Source tree: `7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73`.
- Published comparison commit: `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`.
- Published comparison tree: `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`.
- Root's archive: `/workspace/scratch/f364bc93d920/checkpoint-w07/source`.
- SDK root commit: `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`, with submodules
  and notices governed by the unchanged dependency lock.
- Existing build toolchain: GCC 14.2.0, CMake 3.31.6; this execution orchestrator
  ran Python 3.12.14.

Before execution, all **495 archive files** were rehashed as actual Git blobs
and matched the selected source tree. The inventory also retains every file's
size, mode, Git blob ID and SHA-256. Fifty-three compiled-input paths under
`src`, `include` and `plugins/vst3` matched both the published comparison commit
and the live checkout. After execution, those 53 paths plus
`tests/test_host_timeline.cpp` and `tests/test_state_exchange.cpp` still matched
the archive, comparison commit and live checkout exactly. The root's changing
wave-8 Markdown/Python/install files were not mixed into compiled tests.

| Reviewed implementation | SHA-256 |
| --- | --- |
| `plugins/vst3/Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `plugins/vst3/Controller.cpp` | `24b71a4a49d6234def8f9336e22de927577bf75bb859769b9af4a7ff840d41d6` |
| `plugins/vst3/StateStream.cpp` | `c83fbf22ea26c0b7a89974d4c0aa590c1e46f44f4a6c457d6fee512740d02117` |
| `src/HostTimeline.cpp` | `37941dc9d833cabc1ed7ca22327ad23240ea8c04e6de9fc3f447222d2ebb41dd` |
| `src/StateExchange.cpp` | `10a85957cad8e87e00f8ada543f697b9db4d59590b306baaae05fc0120a2a2bf` |
| `src/ParameterBridge.cpp` | `14d7dcfd24f5e7d6d59de8b31999ee52b33c64f73df453bff82b9eaa4f89dce0` |
| `include/hammond/detail/Decimal.h` | `ae2c63ec61e823fda198a4951e029df11184980c9bc8394142a2d46951338c42` |

## Execution selection and setup error retained

The first discovery script selected all seven names from the native build's
CTest JSON. That build's `hammond_vst3_test_inputs` aggregate intentionally
builds native test inputs, not the core-only executables. CTest therefore listed
the two registered but unbuilt core tests without a `command` field; the Python
orchestrator stopped with `KeyError: 'command'` **before executing any test**.
This was a selection/setup error, not a product failure or skipped acceptance.
No source or CMake change was made to hide it.

The corrected discovery selected the two core tests from
`checkpoint-w07/build-default` and the five native tests from
`checkpoint-w07/build-native`. Both builds use the same coherent archived source.
It required every selected definition to contain an actual command, retained
CTest's configured working directory and any environment properties, and then
invoked those exact argument arrays directly. Core tests ran with working
directory `checkpoint-w07/build-default`; native tests used
`checkpoint-w07/build-native/plugins/vst3`. None of these seven definitions
needed additional environment properties. Each subprocess had a 240-second
harness timeout. The full command arrays are retained in `selected-tests.json`
and `focused-results.json` in the task's scratch evidence directory.

The actual command lines, with absolute paths, were:

```sh
/workspace/scratch/f364bc93d920/checkpoint-w07/build-default/test_host_timeline
/workspace/scratch/f364bc93d920/checkpoint-w07/build-default/test_state_exchange
/workspace/scratch/f364bc93d920/checkpoint-w07/build-native/bin/Release/test_native_controller
/workspace/scratch/f364bc93d920/checkpoint-w07/build-native/bin/Release/test_native_abi /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/VST3/Release/HammondB3.vst3 /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/nominal.b3p
/workspace/scratch/f364bc93d920/checkpoint-w07/build-native/bin/Release/test_native_behavior /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/VST3/Release/HammondB3.vst3 /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/nominal.b3p
/workspace/scratch/f364bc93d920/checkpoint-w07/build-native/bin/Release/test_native_automation /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/VST3/Release/HammondB3.vst3 /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/nominal.b3p
/workspace/scratch/f364bc93d920/checkpoint-w07/build-native/bin/Release/test_native_concurrency /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/VST3/Release/HammondB3.vst3 /workspace/scratch/f364bc93d920/checkpoint-w07/build-native/nominal.b3p
```

No source archive or build configuration was changed to run them. Output was
captured into the assignment's separate evidence directory, so the existing
wave-7 CTest result records were not overwritten. This is a selected direct
execution pass; it is not a new full CTest, SDK validator or sanitizer run.

## Actual focused results

All **seven executables exited zero**. Combined elapsed time was **4.353 seconds**.
Every selected executable ran; there were no skipped selections or failed test
assertions. Per-executable timings include process launch and output capture.

| Executable | Seconds | Observed checks |
| --- | ---: | --- |
| `test_host_timeline` | 0.385 | 4,759 accepted calls, 43 rejections, 39 later probes, 933 thresholds and 21 partitions; zero curve/audio error |
| `test_state_exchange` | 0.026 | Queue, publication, migration and Engine-history assertions passed; 6,211 concurrent callbacks, 4,468 producer reads and 12,210 observer reads |
| `test_native_controller` | 0.007 | 41,795 checks, 3,720 four-rounding-mode threshold cases, 387 string round trips and 306 rejected stream/load cases |
| `test_native_abi` | 0.872 | 691,878 assertions; 229,725 compared frames, 217,972 audible frames; zero error |
| `test_native_behavior` | 2.157 | 1,030 accepted/72 rejected callbacks; 59 rollback cases, 233,792 direct-reference frames and 81,302 later-audio samples |
| `test_native_automation` | 0.530 | 231 callbacks/18 zero-frame calls, 89,979 reference frames, 179,958 exact channel samples, 39,948 future channel samples; zero error |
| `test_native_concurrency` | 0.364 | Three rates, 24 controlled rounds, 3,072 accepted stress loads, 3,072 publication-only saves, 64,625 exact audible frames and 6,168 future frames; zero error |

The core concurrent publication test reported 123,056 bounded read failures,
and the actual native stress reported 13,332 busy saves. These are exercised
explicit admission outcomes; the tests require destination preservation and
whole values for accepted reads. They are not assertion failures or evidence
of an audio-thread wait. Variable stress counts depend on the scheduler and
are not used as immutable golden values.

The actual loaded module retains SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`
for 434,168 bytes. The 4,545-byte compiled profile retains SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The four loaded-module tests use the bundle factory/SDK interfaces and plain
Engine oracles. The separate controller test compiles actual controller/stream
sources against the pinned SDK.

## Retained runtime and output hashes

Local execution evidence is under
`/workspace/scratch/f364bc93d920/a50-native-protocol-audit/`. It is reproducible
scratch evidence; this note and the review retain the essential results and
identities in the repository. These hashes identify observed local bytes,
not an authenticated build attestation or downloadable release.

| Runtime file | Bytes | SHA-256 |
| --- | ---: | --- |
| `test_host_timeline` | 174,472 | `889cdeb7cbf899e29c3cbdc1a47d4c9377b3c69536eab5fdd136aada559d8059` |
| `test_state_exchange` | 163,112 | `6778bc056aa66dd5581774729135c575110af2fe4bd4674ed0a6d55f173dabec` |
| `test_native_controller` | 436,448 | `c5a0a1f6e558ff1ef04016f24b04b59cbf9394785f44cd5dc2c16d266847db9e` |
| `test_native_abi` | 324,744 | `de4f307def0afeb410e704983d4f0e31628894fa2e175e5afe7daa2a8db11651` |
| `test_native_behavior` | 450,448 | `cb3f0ba106e69fee2274644523d33f8cbb4fead97678b25b9e4eabfeb0efcf68` |
| `test_native_automation` | 342,840 | `4324256048874560af9fc31d63a1ec10f7f06dc5069ffe311dfbcde2fd36a9e3` |
| `test_native_concurrency` | 309,792 | `03d81590342a014f81a67ae4708873057d994985c98ea97df251a35283f0aac7` |
| `module` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| `profile` | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

| Output record | SHA-256 |
| --- | --- |
| `source-inventory.json` | `450975d2907cc9e47f828dbc6f19d7d25768c4da98f4cbe9d14e245b51241b13` |
| `selected-tests.json` | `bd4a6dfc91f07356237456e167b6c3ba953a19c7c6d3385c74f5c32dc7a42d6a` |
| `focused-results.json` | `21f0e96e95763a5fbb0db7f05e6695bd3fa2dcc97f19481626727dfe02bd841b` |
| `focused.xml` | `f222aac48c3c1f4a775129a77dfbd49a32ea8dacdc2d96bdcdcd9c2409a07340` |
| `runtime-identities.json` | `30f32e1b85806c29ac6b7e4ca0b738abcd7a04a415b13599c4a1c15e9042d3aa` |
| `test_host_timeline.log` | `06dcfb024ce5b4f3513eeabb86eb1047a5ea09efbcc25816d20c6769be6f20ec` |
| `test_state_exchange.log` | `e43fc3f375f52aa859e08db3a78714aaa239591140ab3412103a7d37f1d63977` |
| `test_native_controller.log` | `5ab897bf0d076c194903afa2f7f77501747e63aec902820d4703706c833e0116` |
| `test_native_abi.log` | `688e792adb4e371e528bcacfc5c76eedc42f5028a922a9a9b3e4c1294d241fc5` |
| `test_native_behavior.log` | `eff32bb8973eab73db03b0b9b7af9ca500c8005a4249195179d5c75a928e9e0d` |
| `test_native_automation.log` | `65c096f8d0f7a0e19bd78b9c78152e6b869140629b6cd8281f0a473d59e3083c` |
| `test_native_concurrency.log` | `4ef79831d4d342e0b4e1fd4a879f194f2676355ddaeac1373fdce6216f130650` |

## Findings, limits and next action

The review specifically proved why a successful state preflight remains valid
through candidate rendering: there is one audio consumer, no intervening commit,
UI appends cannot retire the copied range, finite publication lifetime is already
checked, and the successful Engine supplies a valid snapshot. A future change
to any of those conditions must redesign the transaction; a late error after
mutating live Engine state would not provide rollback.

Queue slots and atomic published cells have separate ownership proofs. The
source retains release/acquire handoff for ordinary slots, sequentially
consistent revision/cell publication, a fixed eight-attempt reader, finite
nonwrapping sequences and no live reset API. Serialized UI state methods do not
read mutable Engine state. Lifecycles require actual quiescence rather than
assuming a Boolean stop flag is synchronization. Current nominal control
snapshots still omit transient source, contact, percussion, ownership and clock
state; they do not promise exact-render resume.

One current documentation gap was sent to root for assignment 55:
`docs/VST3_PROCESSOR.md` ends with completed bundle/ABI/validator/allocation work
still phrased as the next task. Preserve its original assignment-31 syntax
result as historical evidence, then add links to current independently executed
native gates and platform status. That contract is outside this assignment's
edit ownership; the review records the follow-up instead of competing for it.

Root should integrate these two frozen records with wave 9, run the final
coherent-source gates, observe the exact published platform results and update
the shared status/next-step/handoff under standing authorization. Actual DAW
save/reopen, device scheduling/deadlines, custom accessible UI, signing/rights
and measured organ/cabinet fidelity remain separate work. This assignment did
not rerun ThreadSanitizer, SDK validation, Windows/macOS builds or physical
measurements. It did not edit the manifest, stage, commit or push.


## Final record checks

Both owned Markdown files have valid UTF-8/LF text, final newlines and no trailing
whitespace. All **21 relative Markdown links** resolve. The final read-only SDK
`git rev-parse HEAD` returned the locked root commit above, and the existing
native build's `CMakeCXXCompiler.cmake` identifies `/usr/bin/c++`, GNU 14.2.0.
The scoped `git diff --check` completed successfully. No code, build input,
shared document, manifest or historical evidence file was changed.

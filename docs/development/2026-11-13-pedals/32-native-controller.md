# Assignment 32 — native controller, factory and bounded state streams

Owner: /root/w06_a32_native_controller

Wave: 06. Session: 2026-11-13 pedal development. This is one newly dispatched
worker assignment; earlier sessions and follow-up messages are not recounted.

## Scope and starting point

Read the standing instructions, current status/next steps, project plan,
operational handoff and development-log context, the full
[native contract](../../VST3_SPIKE_CONTRACT.md), the product atlas review, actual
parameter/state source, and the pinned SDK controller, factory, parameter and
stream headers/implementations. The native source basis is atlas pp. 379–402
and 450 as retained by assignments 05, 06 and 15; this assignment does not claim
a new full-atlas reading or hardware evidence.

Owned `plugins/vst3/Controller.h/.cpp`, `PluginIds.h`, `Factory.cpp`,
`StateStream.h/.cpp`, [controller documentation](../../VST3_CONTROLLER.md),
this note, and—under the integrator's explicit scope extension—
`plugins/vst3/tests/test_native_controller.cpp`. Shared CMake, processor,
operational status and publication remained with their assigned owners. No
subagent, commit, push or shared-document edit was performed.

The coherent focused source snapshot was a `git archive` of published
`88c36b4a72a07f6498f73279f25023278accd350`, with only these owned native files
overlaid under `/workspace/scratch/f364bc93d920/a32-source`. The core was rebuilt
from that archive. The SDK checkout is the already pinned root
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`, with the four locked submodules.
No older library was combined with later live core headers.

## Implemented behavior

The actual SDK `EditController` exports all 45 immutable descriptor identities,
units, bounds, defaults and step counts through its native interface. Fixed
value storage and direct bridge conversions avoid an incompatible SDK range
rounding rule. Exactly the contract's original processor/controller FUIDs are
registered; no sample UUID or fictional contact address was substituted.

There is no custom editor or observer graph. Host-directed parameter changes
and component-state reflection emit no automation or restart gestures. State
1/2/3 parsing and all 45 normalized conversions finish before one fixed-array
commit. Cancelled manual route bits stay in processor state; the controller
reflects retained bank/drawbar values without reconnecting a route. The generic
controller has no separate UI persistence format.

State helpers are `noexcept`, operate only on the serialized control thread,
never retain/seek the host stream, and preserve the destination on read failure.
They bound reads to 16 KiB plus one overflow byte, admit successful partial I/O,
reject invalid counts/status/no-progress writes, and translate allocation/other
exceptions into SDK results. A zero-byte Ok/False read is the explicit EOF
convention; other errors reject. An opaque external write can retain a prefix
after its own failure, which is documented rather than called atomic.

## Executed checks and actual results

GCC 14.2.0 compiled all three production translation units against the actual
SDK with C++20, `-DNDEBUG`, and the project warning set:
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
SDK headers were system includes. Factory syntax compilation used assignment
31's agreed processor header; it did not substitute a fake processor class.

The maintained focused executable then compiled and linked the actual
controller/state code, freshly rebuilt core and pinned SDK static libraries.
Its executed result was:

```text
native-controller: checks=41795 threshold_cases=3720 string_roundtrips=387 rejected_streams=306
```

The process exited **0**. The counts mean:

| Scope | Actual coverage |
| --- | --- |
| Descriptor export | All 45 records against independent JSON-derived literals: IDs, title/path, short title, exact units, steps, flags, root unit and defaults |
| Discrete conversion | 3,720 threshold/adjacent-binary64 cases across FE_TONEAREST, FE_DOWNWARD, FE_UPWARD and FE_TOWARDZERO |
| Native strings | 387 round trips, including every discrete position and expression signed zero/subnormal/adjacent values; caller rounding modes remain unchanged |
| Invalid native values | Nonfinite/out-of-range normalized values, registry holes, invalid plain fractions, null/overlength/non-ASCII strings and malformed numeric grammar preserve destinations |
| State migration | Actual 1/2/3 streams install all 45 expected values; older states explicitly mute pedals; version 1 resets percussion; cancelled routes produce no host gesture |
| Bounded streams | One-, seven-, 512- and 32,768-byte requested transfer caps; both documented EOF results; current-position reads with no seek; exact 16 KiB and one-over limit |
| Failed loads/writes | 306 rejected cases: every prefix before complete final `end`, trailing/unsupported/BOM/invalid-position states, malformed byte counts, failed reads/writes, zero write progress, and injected exceptions |
| Lifecycle/interface | Repeated-init rejection, terminate/reinitialize defaults, no editor, actual `IEditController` query/reference lifecycle and zero component-handler echo calls |

The independent expected registry source remains unchanged, SHA-256
`a80b0f391a37dd9264dc6962131e61c6ba8a0b8ce570d15e89042abe13d148c4`.
This is an actual direct SDK-interface/controller test. The dynamically loaded
module/processor ABI, validator, concurrency and cross-platform gates are
separately assigned; this focused test is not presented as those results.

### Commands used

Task-local CMake is 3.31.6. The actual core/SDK build commands were:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/vst3-foundation-build --target sdk -j 2
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a32-source \
  -B /workspace/scratch/f364bc93d920/a32-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/a32-build --target hammond_core -j 2
```

The direct compile/link used these exact paths; the variables below abbreviate
the literal command arguments:

```sh
A32_SOURCE=/workspace/scratch/f364bc93d920/a32-source
A32_SDK=/workspace/scratch/f364bc93d920/vst3sdk
A32_SDK_LIB=/workspace/scratch/f364bc93d920/vst3-foundation-build/lib/Release
g++ -std=c++20 -O3 -DNDEBUG \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -isystem "$A32_SDK" -I "$A32_SOURCE/include" -I "$A32_SOURCE/plugins/vst3" \
  "$A32_SOURCE/plugins/vst3/tests/test_native_controller.cpp" \
  "$A32_SOURCE/plugins/vst3/Controller.cpp" \
  "$A32_SOURCE/plugins/vst3/StateStream.cpp" \
  /workspace/scratch/f364bc93d920/a32-build/libhammond_core.a \
  "$A32_SDK_LIB/libsdk.a" "$A32_SDK_LIB/libsdk_common.a" \
  "$A32_SDK_LIB/libbase.a" "$A32_SDK_LIB/libpluginterfaces.a" \
  -pthread -ldl -o /workspace/scratch/f364bc93d920/a32-test-native-controller
/workspace/scratch/f364bc93d920/a32-test-native-controller
```

Assignment 33 owns the maintained optional CMake `test_native_controller`
target and CTest hook. The contract documentation gives ordinary reproduction
commands through that integration; it does not require task-local paths.

## Development corrections retained

Before runtime qualification, code inspection found that native expression
formatting should use the same nearest-rounding guard as state serialization.
Added `detail::DecimalRounding` around formatting. The focused test proves the
UI caller's original rounding mode is restored in all four modes. Formatting
is never called on the audio path and holds no Engine reference; this change
adds no audio-thread rounding operation. Assignment 33 received the updated
source hash before qualifying its bundle.

The first test compilation exposed a fixture `iid` argument shadowing the SDK
interface's static `iid`; renamed it `requested_iid`. The first direct link then
showed that SDK `MemoryStream` is not included in the four chosen libraries.
Replaced that test-only dependency with an explicit local `IBStream` fixture,
so the maintained test requires only the declared SDK/core libraries. An
attempt to execute the missing binary after that failed link returned 127 and
is not counted as a runtime test. The corrected executable passed all checks.

Final source hygiene expresses the full-width-digit and supplementary Unicode
test values with equivalent ASCII universal character escapes, avoiding a
dependence on MSVC's source code page. The same test was rebuilt and rerun after
that representation-only change. Production controller/state code did not
change during this final hygiene pass.

## Frozen identities and handoff

| Owned code/test file | SHA-256 |
| --- | --- |
| `plugins/vst3/Controller.h` | `d3a29e6d061779f82e1541af2951e5cf80031a997dedcb50a7d6d1f341057dac` |
| `plugins/vst3/Controller.cpp` | `24b71a4a49d6234def8f9336e22de927577bf75bb859769b9af4a7ff840d41d6` |
| `plugins/vst3/StateStream.h` | `6493aa859427ad55cf81c84df29b4669f038828eb4d2c53f04e442aefadeea8e` |
| `plugins/vst3/StateStream.cpp` | `c83fbf22ea26c0b7a89974d4c0aa590c1e46f44f4a6c457d6fee512740d02117` |
| `plugins/vst3/PluginIds.h` | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |
| `plugins/vst3/Factory.cpp` | `880d4d24d4d6fbf104e441400ebf571a77c15019ae5bc43571a4524c242250d1` |
| `plugins/vst3/tests/test_native_controller.cpp` | `fefb8c2e6bbd2fe0096a4856fb2c466e4ae23198da5830eb4dc043a31527c31a` |

The focused executable SHA-256 is
`8a08e05e1ac5420437b4872332715118b542825b06df36299eef80b6abb29d6c`;
it is a test executable, not the distributable Hammond module.

Next, root combines the frozen native sources with assignment 33's optional
build, assignment 34's actual module ABI harness and assignment 35's behavior
gate. Preserve the exact IDs, quiet restore semantics and state-stream bound.
Qualify the actual bundle and supported platform matrix before making those
claims. Actual DAW/device scheduling, custom UI, signed distribution and
measured B-3/AO-28/Leslie fidelity remain open. Root owns shared handoff updates,
the assignment manifest, coherent full regression and authorized commit/push.

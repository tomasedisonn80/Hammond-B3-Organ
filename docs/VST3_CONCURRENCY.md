# Native concurrent state qualification

`plugins/vst3/tests/test_native_concurrency.cpp` loads the actual VST3 bundle
through the SDK factory and exercises `IComponent::setState/getState` concurrently
with `IAudioProcessor::process`. It does not construct `Processor` directly,
inspect its diagnostics, call its `StateExchange`, or read its live Engine.
The [native harness](VST3_ABI_ACCEPTANCE.md) owns the module and SDK interfaces
until both threads have joined and processing has stopped.

The source basis is atlas pp. 389–390, 393–394 and 400–401: musical snapshots are
separate from transient audio history; active host state calls need a verified
transfer; queue exhaustion and delayed readers require actual concurrency tests.
The implementation contract is [StateExchange](STATE_EXCHANGE.md), integrated
by the [native processor](VST3_PROCESSOR.md). This gate extends the earlier
SDK-free stress test to the actual loaded module.

## Ownership and executed cases

The host initializes, configures, activates and starts an instance before launching
its audio thread. One serialized UI thread owns every state stream and state call;
one audio thread owns every process call, audio buffer and reference Engine.
Activation, bus configuration, setup, shutdown and module unloading never overlap
those operations. All interface lifetimes remain valid until joining finishes.

The test runs both cases below at 44.1, 48 and 96 kHz. Test-host coordination,
deadlines, allocations and stream formatting remain outside the processor call;
none is installed as an audio-side hook.

| Case | Required behavior |
| --- | --- |
| Controlled four-slot rounds | Accept four partial-read state streams, copy their values before the caller destroys its bytes, and save the fourth complete snapshot while audio is paused. |
| Queue-full and malformed loads | A fifth valid state and a state with invalid trailing data reject without replacing the pending save. |
| Rejected audio with pending states | An invalid late automation offset preserves every sample and silence flag, does not consume queue capacity, and leaves the fourth snapshot pending. |
| Successful acknowledgement | Apply the four known restores before sample-zero expression automation; a later save returns the resulting audio controls rather than the older accepted UI value. |
| Held-note history | Hold Upper, Lower and Pedal notes throughout the rounds and compare both native channels and subsequent audio against a plain Engine. Controls restore without reseeding sources or replacing contact/percussion history. |
| Publication-only reading | Before concurrent loading, require 1,024 successful complete audio-family snapshots at each rate, so a pending private UI copy cannot hide publication defects. |
| Stalled reader | Perform no UI state calls while the audio thread completes at least another 32 callbacks per rate. A reader owns no queue slot and cannot stop publication. |
| Concurrent load/save stress | Accept 1,024 new complete UI states per rate, retry explicit queue-full responses off audio, and interleave malformed loads and saves while audio runs. |
| Bounded busy saves | `kResultFalse` is permitted when publication cannot be read within its bound; the actual caller stream must retain its sentinel and receive zero writes. |
| Final drain and future output | After the UI's final release, execute two more boundary publications and 512 held-note samples, then require the final complete audio snapshot. |

There are 24 controlled rounds across three rates, 3,072 accepted stress loads,
3,072 required publication-only saves, at least 96 callbacks while the UI is not
reading, and 6,168 explicitly compared future frames. Including initialization
and the controlled rounds, the fixed accepted-load count is 3,174. The test
rejects 24 invalid process calls and 462 malformed UI loads. Queue-full counts,
busy-read counts and total callback counts depend on thread scheduling.

## Independent state and audio oracles

Independent literal parameter IDs populate all 45 sample-zero queues. Every audio
callback changes a coded complete control pattern: all four nine-drawbar banks,
both selectors, expression, all four percussion controls and both pedal controls.
Both explicit selector points reconnect their routes, so published audio patterns
have both route bits enabled. Pending UI patterns deliberately vary those route
bits as well as all musical controls.

Expression carries an exactly representable generation code in disjoint UI and
audio ranges. A successful pending save must equal the UI thread's latest
accepted complete snapshot. A successful published save must match every field
of the independently reconstructed audio generation. The expression bits are
also compared directly. This checks all 45 musical values and both routing bits;
it does not decode or trust the production atomic-cell layout.

In controlled rounds, a separate Engine receives the known four control restores
and one direct expression event. In the unsynchronized stress case, the audio
thread restores its own known complete audio pattern to that reference Engine
and processes the same number of frames. It never consults which UI states the
native queue consumed. Since every native audio callback explicitly supplies
all 45 controls at frame zero, the audio reference is independent of the
producer/consumer interleaving. Both instances retain the same continuously held
physical notes. Bitwise float comparisons cover both channels, not a tolerance
or a separately rerun `HostTimeline` as an oracle.

No complete-snapshot comparison can distinguish swapping equal field values,
and this finite workload does not exhaust every possible scheduler interleaving.
It does expose incoherent combinations that disagree with either legal complete
pattern and audio-history changes that differ from the independent Engine.

## Observed local results

The [assignment record](development/2026-11-13-pedals/41-native-concurrency.md)
retains exact source, binary, command and log identities.

| Observation | Release | GCC ThreadSanitizer |
| --- | ---: | ---: |
| Focused CTest result | 1/1 passed, 0.36 s | 1/1 passed, 2.76 s |
| Accepted native callbacks | 1,458 | 1,397 |
| Zero-frame callbacks | 288 | 276 |
| Bit-exact reference frames | 66,797 | 64,225 |
| Audible reference frames | 66,797 | 64,225 |
| Accepted state loads | 3,174 | 3,174 |
| Explicit queue-full loads | 10,274 | 8,560 |
| Successful native saves | 16,821 | 15,116 |
| Explicit busy saves with untouched streams | 367 | 110 |
| Pending-family saves | 13,670 | 11,956 |
| Published-family saves | 3,103 | 3,112 |
| Maximum observed audio error | 0 | 0 |

Both runs had zero failed or skipped CTest cases. The sanitizer run used
`TSAN_OPTIONS=halt_on_error=1` and emitted no detector report. The C++ core,
processor/controller, SDK code, loader, harness and test were freshly built
with `-fsanitize=thread`; all 78 actually produced object files had the flag.
Both the test executable and loaded module link `libtsan.so.2`, and the module
has actual detector references. Neither executable exports Hammond core symbols
for substituting its reference Engine into the loaded module.

## Reproduction and limits

With the explicitly acquired locked SDK, the ordinary native gate includes this
test through the build-only aggregate:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-native --target test_native_concurrency --parallel 2
ctest --test-dir build-native -C Release -R '^test_native_concurrency$' --verbose --no-tests=error
```

For a separate GCC ThreadSanitizer build on a compatible Linux host:

```sh
cmake -S . -B build-native-tsan -DCMAKE_BUILD_TYPE=RelWithDebInfo -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk '-DCMAKE_CXX_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' '-DCMAKE_C_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread -DCMAKE_MODULE_LINKER_FLAGS=-fsanitize=thread -DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=thread
cmake --build build-native-tsan --target test_native_concurrency --parallel 2
TSAN_OPTIONS=halt_on_error=1 ctest --test-dir build-native-tsan -C RelWithDebInfo -R '^test_native_concurrency$' --verbose --no-tests=error
```

First establish that the sanitizer runtime can execute on the selected host.
An instrumented build that cannot run is not a passed concurrency gate. Keep
its module identity separate from the ordinary Release module, and do not mix
current headers with older object files.

This result covers a finite actual native workload under the documented SPSC
ownership and stable lifecycle. It does not authorize concurrent state producers,
setup/activation/destruction during processing, or direct UI reads of Engine
state. It is not a proof for every interleaving, a callback allocation audit,
audio-device deadline measurement, commercial-DAW session, cross-platform
sanitizer qualification, or instrument-fidelity claim. The integrator's coherent
combined source and exact hosted platform gates remain separate observations.

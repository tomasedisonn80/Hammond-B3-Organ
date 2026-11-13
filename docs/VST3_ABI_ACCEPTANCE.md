# Native VST3 ABI acceptance

The 2026-11-13 Linux Release gate loaded the actual `HammondB3.vst3` bundle
through the pinned SDK's platform module loader. The maintained ABI test passed
**1/1 in 0.89 seconds**, exercising the exported factory, component, audio
processor and controller interfaces. It compared **229,725 rendered frames**
against a separately driven plain Engine with bit-identical output and zero
observed absolute error. This is an early native integration result for the
declared nominal instrument, not a DAW/device or physical-fidelity result.

The SDK validator independently exited zero and reported **47 passed, zero
failed** against the same module. Its log also contains **16 teardown
diagnostics and nine unsupported-rate error messages**. Those observations are
retained below; the result is not described as warning-free or as support for
every format visited by the validator.

The implementation contracts remain [VST3_SPIKE_CONTRACT.md](VST3_SPIKE_CONTRACT.md),
[VST3_PROCESSOR.md](VST3_PROCESSOR.md), [HOST_TIMELINE.md](HOST_TIMELINE.md)
and [STATE_EXCHANGE.md](STATE_EXCHANGE.md). The source basis is atlas
pp. 385–396, particularly the distinct engine/adapter responsibility, stable
IDs, headless execution, active state calls and separate qualification reports.
Those twelve pages were read directly for this assignment.

## What the harness actually loads

[NativeHarness.h](../plugins/vst3/tests/NativeHarness.h) and
[NativeHarness.cpp](../plugins/vst3/tests/NativeHarness.cpp) provide test-host
fixtures. They use `VST3::Hosting::Module::create`, the module's exported factory,
`IComponent`, `IAudioProcessor` and `IEditController`. They do not include
`Processor.h`, instantiate the production C++ processor class directly, or
substitute its core for the loaded plugin.

Expected processor/controller FUID words are separately written in the harness;
they are not imported from the production `PluginIds.h`. SDK FUID conversion
retains the platform-specific native representation. The actual module must
export exactly the original two class identities and the expected instrument
category. Unknown class and interface requests must fail.

The helper owns module, host context and interfaces with explicit lifetimes.
Initialized interfaces are stopped/terminated and released before the module
unloads; the host remains alive through instance cleanup. Construction failure
also releases partial native objects in that order. Tests use real factory
instances, including separately created processors with explicit checked
termination and same-instance reinitialization.

`MemoryStream`, `EventList`, `ParameterQueue` and `ParameterChanges` are borrowed
test-host interfaces. Their data, optional signed-count overrides and accessor
failure knobs allow later native admission tests without altering the plugin.
Their callback getters copy already-owned values and allocate nothing.
Construction, vector/string mutation, stream serialization and assertions are
test setup outside a callback measurement. These fixtures are not a general
host application or an allocation audit. Their nondeleting reference methods
reflect the fixture owner's explicit lifetime.

## Executed cases

The maintained entry point is
[test_native_abi.cpp](../plugins/vst3/tests/test_native_abi.cpp).

| Surface | Actual checks |
| --- | --- |
| Factory and interfaces | Recognized bundle structure; exactly two frozen UUIDs; original class names/version/category; component's controller UUID; unknown factory/interface rejection; no custom editor view required |
| Parameter exports | All 45 ordered IDs, titles, units, default normalized values, step counts, root unit and automation flags agree with compiled descriptors |
| Conversion laws | Every discrete position and three adjacent binary64 values around each threshold; plain/normalized and display/parse round trips; five continuous expression values; rejected NaN preserves controller value |
| Bus surface | Zero audio inputs, one named stereo output, three named 16-channel event inputs and no event output; Upper main/Lower/Pedals auxiliary roles; channel routing; unsupported mono arrangement rejection |
| Precision and lifecycle | Float32 advertised; float64/unknown precision rejected; unsupported setup leaves no activatable instance; six balanced prepare/activate/process/stop/deactivate/terminate sequences across 44.1/48/96 kHz; deliberate invalid repetitions reject; repeated `setProcessing(true)` does not reset |
| State | Independently written version-1/2/3 documents; partial native stream reads/writes; version-3 save before and after zero-frame acknowledgement; explicit older-state pedal/percussion migration; both route bits; controller pedal reflection; invalid/null input preservation; four pending loads and fifth-load rejection |
| Audible integration | Explicit A-bank registrations with different upper/lower harmonics, both pedal mixtures, nominal manual contacts, seed zero and expression 0.625; literal native bus/pitch endpoints mapped to separately specified physical events |
| Ownership through native input | All 16 channels on each of the three native event buses; first-owner onset, nonfinal releases and final-owner release compared with one physical-note reference |
| Time and output | Zero, one, irregular, 1,024 and 65,536 frames; exact dry stereo equality; finite output; untouched output tails; silence flags derived from actual samples; disconnected processing followed by an audible pedal probe |

The reference uses the same immutable compiled profile and the existing plain
Engine with `make_nominal_console_model()`. Its physical notes are hand-scheduled;
it does not call the native translator, owner adapters or HostTimeline to obtain
expected events. This checks adapter agreement with the declared engine. It is
not a second implementation of the organ model or physical validation of that
model.

Both manual banks default to B. The final audible fixture explicitly selects A
before using its edited bars, gives Upper and Lower different harmonics, and
requires an audible interval from each isolated Upper/Lower/Pedal division.
This prevents a muted manual or a combined pedal-only response from making a
manual routing check pass without exercising sound. A resumed pedal after
disconnected output makes the subsequent phase comparison audible as well.

## Observed result

Linux x86-64, GCC 14.2.0, CMake 3.31.6, Python 3.12.14, Release C++20 and the
project's warnings-as-errors configuration were used. The module and reference
library were rebuilt from one frozen source snapshot; no live-header/older-library
combination was used.

| Measurement | Observed value |
| --- | ---: |
| Actual native factory instances | 9 |
| Assertions | 691,878 |
| Parameter descriptors | 45 |
| Conversion cases | 2,002 |
| Accepted native callbacks | 73 |
| Rejected API calls | 86 |
| State round trips | 7 |
| Explicit balanced lifecycle sequences | 6 |
| Native/reference frames compared | 229,725 |
| Nonzero frames among those comparisons | 217,972 |
| Maximum absolute native/reference audio error | 0 |
| Observed float-bit checksum | `af029009868faa04` |

The checksum identifies this run's ordered float output under this toolchain.
It is not a required cross-platform transcendental-result or native binary ABI.
Each platform must independently compare its module and matching reference.

## SDK validator diagnostics and their scope

The pinned validator's final summary was `47 tests passed, 0 tests failed`,
with exit status zero. The separate invocation took 1.47 seconds under CTest.
The exact SDK revision remains in the [dependency lock](../data/dependencies/vst3-sdk-lock.json).

Sixteen `Failed to teardown test!` lines occurred: the two general Valid State
Transition tests and fourteen unsupported double-precision processing cases.
The selected SDK sources contain conflicting cleanup expectations:

- [`RepeatIdenticalStateTransitionTest`](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/state/repeatidenticalstatetransition.cpp)
  requires a second identical inactive transition to fail.
- [`ValidStateTransitionTest`](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/state/validstatetransition.cpp)
  ends its successful loop after reinitialization, without activation.
- [`ProcessTest::teardown`](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/processing/process.cpp)
  unconditionally requires `setActive(false)` to succeed, including an already
  inactive component and unsupported-format paths that never activated it.

The plugin retains the declared changed-state activation policy. Neither SDK
source nor production behavior was changed to erase these messages. The ABI
suite separately verifies balanced supported transitions, explicit termination,
same-object reinitialization and recovery after rejected float64 setup.

Nine `ERROR` lines report rejected sample-rate setups at 22,050, 32,000, 88,200,
192,000 and 384,000 Hz, plus 1,234.5678, 12,345.678, 123,456.78 and 1,234,567.8
Hz. These are outside the instrument's declared three rates. The SDK's
[`ProcessFormatTest`](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/processing/processformat.cpp)
logs unsuccessful positive-rate setup without turning that branch into a failed
test. Its same run explicitly processes 44,100, 48,000 and 96,000 Hz successfully.
Thus the summary cannot be used as an unsupported-rate or float64 qualification.

## Reproduction and identities

After the optional dependency checks and configuration in
[VST3_BUILD.md](VST3_BUILD.md):

```sh
cmake --build build-vst3 --config Release --target test_native_abi validator
ctest --test-dir build-vst3 -C Release --output-on-failure \
  -R '^(test_native_abi|hammond_vst3_validator)$'
```

The executable receives the actual generated bundle path and matching compiled
profile as its two arguments. CMake supplies both. No system plugin installation
or graphical editor is required.

The tested core comes from fifth-wave tree
`06786b70f1cffcc6371600fd6e14306f16e8c985`, with the exact frozen native build,
processor, controller/state helper and test-host overlays identified in the
[assignment 34 record](development/2026-11-13-pedals/34-native-abi.md).
Published `88c36b4` has identical core/test/data bytes to that base tree; its
differences are result Markdown and assignment metadata.

| Artifact in the observed Linux build | Bytes | SHA-256 |
| --- | ---: | --- |
| `HammondB3.so` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| SDK `validator` | 935,200 | `bea796a46605330c6952b492c48ddea4c0d6ab892b255ca6c36378dddc3532f9` |
| `test_native_abi` | 324,744 | `de4f307def0afeb410e704983d4f0e31628894fa2e175e5afe7daa2a8db11651` |
| Compiled profile | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| `moduleinfo.json` | 1,090 | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |

## Next gates and future-agent rule

The next native acceptance covers full input/automation/carry rejection and
active-state preservation against an independent timeline, followed by actual
native callback allocation instrumentation, concurrency stress and hosted
platform runs. The reusable fixtures support these separately owned tests.
Do not inherit this ABI result for changed module, core, SDK or test bytes.

No actual DAW project, audio device, underrun/deadline, custom interface,
accessibility interaction, signed installer or measured Hammond/Leslie response
was exercised here. The SDK's own skipped unsupported paths do not close those
gates. Future agents must preserve the diagnostic record, identify the exact
source/artifacts they test, update the current handoff and follow
[AGENTS.md](../AGENTS.md) for verified commit/push publication.

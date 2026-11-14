# A17 — Host selection and raw-mode publication

## Assignment and owned scope

Actual assignment **A17**, wave **3**, worker
`/root/w03_a17_host_publication`. The session production baseline is
`b79086f6bb0c42b97130c721c5c73c7c97a13887`; the inspected checkout HEAD was
`70b3354` while dependency owners supplied their reviewed implementation.
The test qualification below identifies copied source bytes rather than
attributing this uncommitted implementation to either earlier commit.

Read `AGENTS.md`, the project plan and current README/status/next-step/log
context, plus `PRESET_SELECTION_CONTRACT.md`,
`PRESET_STATE_PARAMETER_CONTRACT.md`, `PRESET_ADAPTER_AUDIT.md` and
`PRESET_CORE_API.md`. This implements the frozen exclusive-selection contract,
using A13's admitted immutable data, A14's core selection API, A16's appended
47-descriptor bridge and A15's state4 reader/writer.

Owned paths are the StateExchange, PerformanceInput and HostTimeline header/
source pairs; their three existing C++ tests; `docs/STATE_EXCHANGE.md`,
`docs/HOST_TIMELINE.md`, `docs/PERFORMANCE_INPUT.md`; and this note. No Session,
UiModel, VST3, registry, catalog, PDF, shared status, Git ref or publication path
was edited. No commit, push or subagent was requested or performed by A17.
The existing `build-baseline` executables were not reconfigured or rebuilt.

## Production changes

- StateExchange now asserts 47 descriptors and 50 publication cells. Original
  cells 0–44 retain their layout; cells 45/46 carry raw fixed modes, 47/48 carry
  route bits and 49 carries the acknowledged sequence. Decode checks each full
  uint64 value against 0–9 before converting to the byte-backed enum. Effective
  Cancel/fixed/bank parameter values never replace raw retained fields.
- PerformanceInput admits `SelectPreset` as an ordinary control alternative.
  Complete payload validation remains Engine's responsibility, and existing
  owner simulation, stable mixed-input order and whole-call rollback remain
  unchanged.
- HostTimeline extracts each new selector anchor through the checked
  `control_preset_selection` helper during successful preparation and explicit
  whole-state restore. Old bank anchors still use remembered banks. No callback
  completion reconstructs or quantizes raw anchors from Engine state.
- The existing curve cursor and dispatch rules were deliberately preserved:
  numeric descriptor order before notes; new higher-ID selectors after old bank
  commands; explicit repeated commands even when values are unchanged; absent
  and empty queues emit nothing; unchanged discrete plateaus emit nothing;
  same-ID fresh points override carried points and duplicate ties are last-wins.
  Header and contract documentation now describe these interacting controls.

## Executed focused qualification

All **three directly compiled C++ test executables passed**, against one frozen
52-file source/header/test/generated-data/profile snapshot. These are direct
compiler and executable runs, not three CTests or a complete native product
build. GCC **14.2.0** compiled all 20 core translation units with C++20,
`-O3 -DNDEBUG` and the repository's complete strict warning set including
`-Werror`; the successful compile emitted no diagnostics. A fresh archive from
those objects supplied all three executables. No old core library was linked
against the enlarged live headers.

| Executable | Observed result | New and retained evidence |
| --- | --- | --- |
| `test_state_exchange` | Pass | All 1,600 fixed-mode/bank/route combinations through pending save, batch, atomic read and acknowledged save; invalid hidden modes; complete legacy migration; existing queue/lifetime/concurrency checks with fixed fields varied. |
| `test_host_timeline` | Pass | 7,486 accepted calls; 999 threshold cases; 63 callback partitions; 51 rejections with 47 future probes; 9,216 independent oracle frames; 27,937 bitwise sample checks; maximum observed audio and curve errors both zero. |
| `test_performance_input` | Pass, including final added same-time direction checks | 3,891 accepted calls; 67 atomic rejection/future checks; 26,986 bitwise samples; 12,922 bitwise source-phase comparisons; all 42 retained partition cases. |

StateExchange's exhaustive matrix is 100 raw fixed-mode pairs times all 16
remembered-bank/route-bit combinations. It checks every other control and both
signs of expression zero. Each case distinguishes the UI's intact pending copy
from the decoded atomic publication after acknowledgement. Every invalid
byte-valued fixed mode 10–255 rejects at each of the two manual positions while
its route is disabled: 492 invalid snapshots, each tested at both enqueue and
commit boundaries. Pattern generation now varies both fixed modes in existing
queue saturation, stale/foreign token, append-after-preflight, finite lifetime,
24,000-publication delayed-reader and three-thread tests. The observed
12,000-load concurrent run reported:

```text
concurrent callbacks=6074 producer_reads=6111 observer_reads=36483 bounded_read_failures=273405
StateExchange: queue, publication, migration and engine history checks passed
```

Busy reads retain caller sentinels; these scheduling-dependent counts are not
a callback timing result. Independent literal state1/2/3 inputs are preserved,
including migration into a destination that already contains nonzero modes.
Their current serialization oracle is an independently spelled canonical state4
document. Unsupported-version rejection now uses version 5.

HostTimeline retains the named `test_legacy45_ids_and_thresholds` oracle and adds
a separate literal nearest-binary64 selector oracle. The former unbounded
`id >= 0x4000` pedal classification is now explicitly limited to 0x4000–0x4001.
Both new IDs exercise all eleven thresholds, adjacent representable values and
all twelve canonical values. A separately enumerated current47 reverse-queue
case compares all control commands followed by notes against a direct Engine;
its higher-ID fixed selectors act last. Every restored fixed/bank/route
combination checks old remembered-bank anchors and new effective anchors
independently of the production extraction helper.

Alias cases preserve raw old-bank 0.6/0.61 anchors across fixed selection,
absent/empty queues and changed-normalized-but-unchanged-plain interpolation.
Both old-bank and new-selector plateau directions are exercised before their
endpoint carries apply. Repeated unchanged old B exits fixed mode, including a
cancelled route; Cancel retains fixed memory and raw negative zero. Additional
cases combine four restores, duplicate carried endpoints, carried release,
fresh same-ID points, fresh note-on and old/new parameter conflicts. Invalid
new queues and invalid cancelled fixed restores preserve output, owners, all
anchors, carry and Engine history, then match the untouched copy's next audio.
The 42 additional selector-curve partition cases cover both console models,
44.1/48/96 kHz, and seven callback sizes. Their source curves place old-bank
commands at matching explicit/threshold events so added subdivision endpoints
describe the same applied command timeline.

PerformanceInput compares an explicit mixed note/pedal/control stream with
hand-authored direct Engine events. Both zero-frame same-time control orders
are asserted with interleaved identified note duplicates: old-bank last selects
B; fixed last selects C#. All twelve commands run on both manuals while owners,
source phases, clock and readiness remain unchanged by zero elapsed time.
Eleven invalid manual/index/value payloads each reject a zero-frame and a
positive callback after otherwise valid new owner and selector inputs; all
22 new rejection cases compare future audio with the untouched runtime.

Final observed output from the two deterministic counter suites:

```text
host timeline: accepted=7486, oracle_frames=9216, phase_values=17199, exact_samples=27937, rejections=51, future_probes=47, threshold_cases=999, partitions=63, max_audio_error=0, max_curve_error=0, sizeof(HostTimeline)=416664
performance input: 3891 accepted calls, 67 atomic rejection/future checks, 26986 bitwise audio samples, 12922 bitwise source phase comparisons, 42 partition cases
```

The initial snapshot command accidentally copied only top-level public headers,
so compilation of `ControlStateIO.cpp` and `Profile.cpp` failed to find
`hammond/detail/Decimal.h`. This was a test-setup failure before linking or
running tests. The snapshot was corrected to include recursive headers, all
20 objects were rebuilt, and the three suites passed. The first diagnostic log
remains at `/tmp/hammond-preset-a17/compile-attempt1-missing-private-header.log`.
After the first successful run, the performance test gained the two explicit
same-time order assertions; that test alone was recopied, rebuilt and rerun
successfully. All other compiled inputs remained unchanged. No runtime failure
was suppressed or changed to a pass.

## Build commands, inputs and ABI observations

Working directory:
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
The copied source is `/tmp/hammond-preset-a17/source`. Its recursive public/
private headers, all 20 `src/*.cpp` files, three test files and `TestSupport.h`
were captured as bytes and checked unchanged during copying. Generated pedal
and scanner headers and `nominal.b3p` came from the preserved `build-baseline`;
the admitted fixed header came from `/tmp/hammond-preset-a13/generated`.

For every copied source stem `NAME`, the exact command shape was:

```sh
/usr/bin/c++ -O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -I/tmp/hammond-preset-a17/source/include -I/tmp/hammond-preset-a17/source/generated \
  -c /tmp/hammond-preset-a17/source/src/NAME.cpp -o /tmp/hammond-preset-a17/objects/NAME.o
ar rcs /tmp/hammond-preset-a17/libhammond_core.a /tmp/hammond-preset-a17/objects/*.o
```

Each test stem in the result table was compiled and linked with the same flags
and include directories, adding the following arguments:

```sh
-I/tmp/hammond-preset-a17/source/tests
'-DHAMMOND_SOURCE_DIR="/tmp/hammond-preset-a17/source"'
'-DHAMMOND_TEST_PROFILE="/tmp/hammond-preset-a17/source/nominal.b3p"'
/tmp/hammond-preset-a17/source/tests/NAME.cpp
/tmp/hammond-preset-a17/libhammond_core.a
-pthread -o /tmp/hammond-preset-a17/NAME
```

The three resulting executables were invoked directly with no arguments.
A strict C++20 `sizeof` probe against the same frozen headers observed:

| Object | Bytes |
| --- | ---: |
| Engine | 38,664 |
| Manual ownership | 3,328 |
| Pedal ownership | 2,112 |
| Event / host carry / control snapshot | 16 / 24 / 56 |
| HostTimeline | 416,664 |
| StateExchange | 752 |

These are this Linux/GCC build's ABI observations, not a portable serialization
format or permission to mix old objects with changed headers. All copied
repository compilation inputs still matched their recorded hashes after the
last test. The final manifest SHA-256 is
`2f3201c392105652baf3ab741f0c591e727d28fe4753837ccddebd7d5c2b4c26`.
The complete frozen input manifest follows; paths are relative to the copied
source, with repository sources retaining their repository-relative paths.

```json
{
  "generated/hammond/generated/FixedRegistrationData.h": "66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6",
  "generated/hammond/generated/PedalRoutingData.h": "efddce2ea3619a7dd9e153382e307928f7aed60bdb8a0318ca6c0e71ee5f6034",
  "generated/hammond/generated/ScannerLineData.h": "d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082",
  "include/hammond/ConsoleModel.h": "e6ef911961c1aca1ce72bca8d2cfba9c765665d7cef30446adfe53b9ba59db51",
  "include/hammond/ContactBank.h": "a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d",
  "include/hammond/ControlState.h": "aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856",
  "include/hammond/ControlStateIO.h": "7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081",
  "include/hammond/Engine.h": "da1adc2e635e5acfa3f214447b722122c3a162eb9ec602ba14fa744eb9d39ba6",
  "include/hammond/FixedRegistration.h": "4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0",
  "include/hammond/HostTimeline.h": "9af4c94ce22425bd6be878c976dce4950c4bbf52219fc8555a682ce2ef9d2316",
  "include/hammond/InputProcessor.h": "2a454e05652d166602120f5ed912ba85575738d65b5fa9563ce20dc92fc1c8df",
  "include/hammond/NoteOwnership.h": "03baaa46de8c24d346c86a64a09e0503e85b78854d143a1cd616aeda38e4b1dc",
  "include/hammond/ParameterBridge.h": "cd313711737f94e5f7f7b0dd73851347b9c4e53b3962d5d40d7e7c37883293d3",
  "include/hammond/PedalNoteOwnership.h": "3df590c6747f01a19651b2220b3c002422c8934ff06710bc97be8f47c4747d33",
  "include/hammond/PedalRouting.h": "e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8",
  "include/hammond/PedalVoice.h": "694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf",
  "include/hammond/Percussion.h": "5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722",
  "include/hammond/PerformanceInput.h": "0229bc8a88c43c57f390a7342908eb22537f037642040ada7e1455d45ac3ad77",
  "include/hammond/Profile.h": "b1180b3dc04030e0555ef3eb44a21617fc06e93150a9ecb48ebb05955b3e5fd0",
  "include/hammond/RotaryMotion.h": "7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36",
  "include/hammond/RotaryTypes.h": "b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4",
  "include/hammond/ScannerLine.h": "c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7",
  "include/hammond/ScannerRotor.h": "3ca846fc72224114194d73272f410fa2cbe3c0cae94c4fb23105536c7afb4d5a",
  "include/hammond/StateExchange.h": "106dec7df367a4dd3351d243cacd26a6c8041c7ac8e874bba99a6fa26a4ac1d0",
  "include/hammond/TonewheelBank.h": "694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b",
  "include/hammond/Types.h": "0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8",
  "include/hammond/detail/Decimal.h": "ae2c63ec61e823fda198a4951e029df11184980c9bc8394142a2d46951338c42",
  "nominal.b3p": "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f",
  "src/ContactBank.cpp": "91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1",
  "src/ControlState.cpp": "9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d",
  "src/ControlStateIO.cpp": "3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb",
  "src/Engine.cpp": "ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a",
  "src/FixedRegistration.cpp": "690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d",
  "src/HostTimeline.cpp": "f0a3f88396f0f9b743f91277ca31b85a32deda98abae53d022dbf601d2226149",
  "src/InputProcessor.cpp": "d5543a2e4fbd34114da30ac28430130e4b5b5d00110c8c29cae80c85986a76fc",
  "src/NoteOwnership.cpp": "f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751",
  "src/ParameterBridge.cpp": "296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220",
  "src/PedalNoteOwnership.cpp": "a938f9d03a1a05d20cdf5d41567bd9c44bd3f5581ec446897ef79386d148acde",
  "src/PedalRouting.cpp": "8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af",
  "src/PedalVoice.cpp": "88fb5afa936784be351b2940ee6f81216975112f860b007d40f3b6a3d9f7c6ba",
  "src/Percussion.cpp": "823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a",
  "src/PerformanceInput.cpp": "80b9b77bca9e17f8b9a866daca32468d649ae4d6b975f1f0c66ceebba646b189",
  "src/Profile.cpp": "80f5c7456311c77a83df23c548c02cabbf9c1cf1621cff89867d0d0c688ebe54",
  "src/RotaryMotion.cpp": "9c8c98dc66a66088d39b43a52d025289d4dd241ebba583bd4200aba3b539ac4d",
  "src/ScannerLine.cpp": "4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336",
  "src/ScannerRotor.cpp": "f1dbd65a92036fef9957d280d2aafe9bd8579414ef632a6e2c525e370907b2a0",
  "src/StateExchange.cpp": "3f661eab16cd164e5d1299ee59ea7c27e9e1cfd2f7d8d2d25218e24734884837",
  "src/TonewheelBank.cpp": "ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b",
  "tests/TestSupport.h": "8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5",
  "tests/test_host_timeline.cpp": "2fafe978bed7563503e99008e012d0345b859300f7688175cf5d49415ef5e577",
  "tests/test_performance_input.cpp": "538a02d8680fb4e1b0915e2a69e8b4f61526b7d3a0f676994c0899495211e44e",
  "tests/test_state_exchange.cpp": "f13d57e268e12c3b6166afd8049c27d4599e9e31f6b3157ffa5ffc06db6e0ba4"
}
```

## Remaining gates and handoff

Production and assigned tests are ready for the integrator's coherent complete
build. Root owns source freeze, full CMake/CTest discovery and execution,
shared status/next steps/development log, independent acceptance and publication.
Standalone and VST3 owners still need their separately assigned raw publication,
controller-cache, native export/state and UI integration checks. A17 did not
run sanitizers, new callback allocation instrumentation, native SDK/UI checks,
platform builds, hosted CI, a DAW or a physical audio device.

The documentation describes bounded allocation-free production operations, but
source inspection and the three ordinary suites do not substitute for measured
allocation/lifetime or deadline evidence. Those enabled-path checks remain
separate continuation gates. The data remain documentary tap positions with
the existing nominal gain law; no physical latching, loading, measured gain,
factory Table IV acquisition or organ/Leslie fidelity claim is added.

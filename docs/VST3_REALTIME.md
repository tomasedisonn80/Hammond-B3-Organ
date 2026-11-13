# Actual native VST3 callback allocation audit

The Linux Release audit measures the **loaded `HammondB3.vst3` module through
`IAudioProcessor::process` and `setProcessing`**. The qualified 2026-11-13 run
passed **133 measured native regions**, with **zero observed global C++
allocations and zero observed global C++ deallocations in every region**.
There were 112 process calls, including 82 accepted and 30 rejected callbacks,
and 21 lifecycle calls, including 15 accepted and six rejected `setProcessing`
requests. The independent reference checked 421,308 channel samples exactly.

This closes the tested Linux calling-thread C++ allocation observation. It does
not establish a device deadline, absence of every allocator/lock/system call,
concurrent native UI safety, another platform's module interposition, DAW
qualification or instrument fidelity. The models remain nominal. The
[core audit](PEDAL_REALTIME.md), [native behavior gate](VST3_BEHAVIOR_ACCEPTANCE.md),
[processor contract](VST3_PROCESSOR.md) and
[assignment record](development/2026-11-13-pedals/39-native-realtime.md) retain
complementary evidence and the exact source/module identities.

## Proving that the probe reaches the module

The executable's private
[`NativeAllocationProbe.h`](../plugins/vst3/tests/NativeAllocationProbe.h)
replaces scalar/array global `new` and `delete`, including nothrow allocation,
aligned allocation, sized deletion and matching placement-failure deletion
forms. Twelve explicit allocation/free pairs cover all eight allocation
and twelve deletion overloads. Volatile function pointers prevent allocation
elision. Calibration requires exactly **12 allocations and 12 deallocations**,
including zero-size and 64-byte-aligned storage.

Executable calibration alone does not prove coverage of a dynamically loaded
plugin. Before observing callbacks, the test loads the actual bundle through
[`NativeHarness`](../plugins/vst3/tests/NativeHarness.h), obtains its raw
`IPluginFactory`, and measures two separate existing module lifetimes:

| Actual module class | Raw factory create | Raw interface release |
| --- | --- | --- |
| Processor, requested as `IComponent` | 1 allocation, 0 deallocations | 0 allocations, 1 deallocation, reference count 0 |
| Controller, requested as `IEditController` | 1 allocation, 0 deallocations | 0 allocations, 1 deallocation, reference count 0 |

Loader setup, host construction, IDs and assertions are outside these probes.
The newly created objects are released before initialization; no host fixture
allocation is inside the raw factory/release regions. The test requires a
positive balanced module lifetime count and fails if interception is absent.
The production module receives no instrumentation code or allocator changes.

### Export only allocation operators

The Linux test target uses these four selective linker exports:

```cmake
target_link_options(test_native_realtime PRIVATE
    "LINKER:--export-dynamic-symbol=_Znw*"
    "LINKER:--export-dynamic-symbol=_Zna*"
    "LINKER:--export-dynamic-symbol=_Zdl*"
    "LINKER:--export-dynamic-symbol=_Zda*")
```

These names are the ELF/Itanium ABI scalar/array allocation and deletion
families. A broad `--export-dynamic` is unsuitable: this executable also links
a plain Engine reference, and exporting its core symbols can replace the
module's own DSP through ELF symbol resolution. The preliminary broad-export
run passed its counts but is **excluded from qualification** for this reason.
A startup `dlsym` guard rejects an exported reference-Engine entry point. A
separately relinked broad-export negative control failed that guard as intended.

Inspection of the qualified executable found all **20 replacement overloads**
and **no exported `hammond` symbols**. A separate `LD_DEBUG=bindings` run of the
same final executable observed **59 module `hammond` bindings, all resolving to
the module itself**, including Engine processing, HostTimeline processing and
state peek/preflight/commit. Its two exercised native allocation bindings,
scalar `new` and sized scalar `delete`, resolved to the test executable.
The remaining replacement families have explicit overload calibration and
export evidence; the trace does not claim all 20 were called by this module.
Trace-run timings are not used in the results below.

The production Linux module remained **434,168 bytes**, SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`,
identical to the preceding ABI/behavior-qualified build.

## What lies inside each measured region

Only the virtual native API call lies between probe begin/end. For `process`
that includes native output admission, every native event/parameter getter and
validation, translation, state queue peek/preflight, HostTimeline processing,
control publication, silence detection and final host-buffer copying. It
includes rejection paths and empty/disconnected callbacks. `setProcessing`
observations include repeated accepted values, invalid Boolean input, and
unprepared/inactive failure paths.

The fixtures preallocate their event vectors, parameter queues and audio
storage. Their native interface getters read existing storage without
allocation. Parsing the profile, creating/destroying plugin objects, changing
fixture vectors, loading/saving controls, constructing assertions, reference
rendering, hashing and printing happen outside the callback probes. UI
`setState`/`getState` calls are deliberately outside the measured regions;
the audio-side exchange work they cause is inside `process`.

Only this thread's replaceable global C++ allocation/deallocation calls are
counted. Direct `malloc`/`free`, custom allocators that bypass those symbols,
other threads, kernel allocation, locks and system calls are outside coverage.
Module creation proof and source review do not enlarge that scope. Timing uses
`steady_clock` immediately outside the allocation probe and requires finite,
nonnegative observations. No wall-time threshold is a test condition.

## Enabled workloads and semantic checks

| Workload | Actual native work and evidence |
| --- | --- |
| Three supported rates | At 44.1, 48 and 96 kHz, upper/lower bank B registrations, pedals and percussion are enabled. Each initial callback moves manual contacts, holds a pedal and matches a separately prepared plain Engine. Later audio has routed percussion with changing reference readiness. |
| State exchange | Four parsed snapshots are queued before processing. A fifth load rejects. A successful callback permits another full four-entry enqueue, proving drainage. An owner-capacity rejection preserves all four pending snapshots; the next accepted callback applies them and publishes the expected controls. |
| Maximum input work | 1,024 native parameter points in one callback; a separate callback combines 512 note-owner onsets with 512 parameter points. Exact output and saved controls match the direct reference. |
| Full owner tables | 256 distinct manual identities cover all 122 manual keys; 256 pedal identities cover all 25 pedals. A 257th owner rejects independently in each namespace. Releasing all 512 identities emits the known 147 final physical releases; contact release motion and eventual silence are checked. |
| Maximum output work | A 65,536-frame expression ramp runs at every supported rate. A plain Engine receives an independently computed value for every sample. The offset-N endpoint is then consumed by a zero-frame callback. |
| Full carry | 1,024 boundary points are retained. An additional fresh record rejects; zero frames consume the carry. A new full 1,024-point raw budget then fits, detecting stale duplicate carry that equal-value audio alone could miss. |
| Native output shapes | Connected stereo, exact L/R alias, zero outputs, inactive output with null sample pointers, zero channels/zero frames and stereo/zero frames are exercised. Unwritten memory and flags remain unchanged where required; future connected audio verifies elapsed private time. |
| Invalid inputs and outputs | Late NaN velocity, late `getEvent` failure, late NaN parameter value, late `getPoint` failure, channel-count mismatch, partial channel overlap, missing output bus, float64, owner overflow, carry overflow and stopped processing reject without host writes. Saved controls and subsequent exact audio check transactional behavior. |
| Lifecycle | Accepted/rejected `setProcessing` calls preserve the musical timeline. Future reference audio detects a reset or an extra render during a rejected/stopped call. |

The maximum ramp is explicitly `e[n] = 1/4 + (n/65536)*(1/2)` for
`0 <= n < 65536`. The full-carry ramp interpolates from the previous sample at
`-1` to `7/8` at offset 32. The reference computes each sample's expression
without using HostTimeline or ParameterBridge. It uses the same nominal DSP
implementation, so it is an independent adapter/timeline oracle, not an
independent physical organ model.

All successful connected samples must be finite and bit-identical, with correct
silence flags and untouched output tails. There are **417,960 nonzero channel
sample observations**, **211,038 reference frames**, **132 state reads**,
**27 input/output/capacity rollback cases**, and **16,572 future channel
comparisons** after rejection, output reconnection or lifecycle changes. The
three stopped-process rejections are tracked separately from those 27 cases.
The deterministic audio checksum is `34119173a07f00c7`. Alias comparisons read
both declared channels even when those channels designate the same storage.

## Fixed work boundaries

The existing native processor owns 1,024 parameter-point slots, 45 parameter
queue views, 1,024 translated musical slots and a 65,536-float private output
buffer. HostTimeline separately owns its fixed candidate/live state, carry,
work arrays and private output. There are 256 manual and 256 pedal owner slots,
and the state exchange has four snapshots. The ABI test does not infer a
portable processor object size or resident-memory budget from these counts.

Native fresh event records plus parameter points plus prior carry must fit
1,024. Filtered native records still count; restores use their separate bound.
Frames are bounded by the configured maximum, at most 65,536. Timeline curve
reconstruction can produce more physical controls across internal slices than
the raw record count. The [timeline](HOST_TIMELINE.md) and
[core allocation report](PEDAL_REALTIME.md) describe those work bounds.
Zero allocations do not imply constant work independent of frames, owners or
records, and they do not eliminate candidate copies or bounded scans.

## Qualified Release observation

Environment: Linux 6.18.57 x86-64, glibc 2.41, GCC 14.2.0, CMake 3.31.6,
Release `-O3 -DNDEBUG -std=c++20` with strict project warnings. The SDK is the
[locked](../data/dependencies/vst3-sdk-lock.json) `v3.8.1_build_84` checkout.
The complete core, native wrapper, harness and test were built together from
one frozen source snapshot. The selected CTest passed **1/1 in 0.91 seconds**.

| Native region | Accepted / rejected | Elapsed frames | Fresh raw records | Consumed carry | Queued restores | Observed total µs | Observed max µs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Enabled callbacks | 37 / 0 | 13,022 | 9 | 0 | 28 | 28,823.925 | 6,450.623 |
| Dense callbacks | 5 / 0 | 224 | 4,608 | 0 | 4 | 1,285.581 | 600.910 |
| Maximum-frame ramps | 3 / 0 | 196,608 | 6 | 0 | 0 | 401,692.676 | 138,342.908 |
| Carry/zero-frame work | 13 / 0 | 32 | 2,054 | 1,027 | 0 | 385.551 | 114.154 |
| Output shapes | 24 / 0 | 1,152 | 0 | 0 | 0 | 2,610.977 | 230.364 |
| Rejected processing | 0 / 30 | 0 | 0 | 0 | 0 | 17.391 | 2.266 |
| `setProcessing` | 15 / 6 | 0 | 0 | 0 | 0 | 1.351 | 0.189 |

**Every row has zero observed allocations and zero observed deallocations.**
Record/restore totals describe the supplied accepted fixtures, with retention
and consumption checked through capacity, state and audio behavior. They are
not native diagnostic counters exposed through the public ABI. Rejected rows
report zero elapsed/consumed work. Factory and overload calibration counts are
separate from these 133 observed API regions.

Durations are observations on a shared container, include measurement overhead,
and vary between runs. They are not worst-case execution times, device buffers,
underflow measurements, supported CPU minima or performance guarantees.

## Reproduction and next gate

On Linux, using an already acquired and verified SDK:

```sh
cmake -S . -B build-vst3 -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-vst3 --target test_native_realtime --parallel 2
ctest --test-dir build-vst3 -R '^test_native_realtime$' -V
```

The target is part of the native test-input aggregate and uses the actual
bundle/profile paths. It is registered only on Linux. There is no synthetic
passing/skipped test on macOS or Windows: those platforms need a separately
proved module allocation mechanism, including their actual allocator/CRT and
loader boundaries. A new Linux toolchain must also pass both calibrations and
the isolation guard; this one run does not qualify every Linux build.

Next, retain the exact-source native CI result, stress actual module UI state
calls concurrently with processing, and qualify each additional native
allocation mechanism. Actual DAW save/reopen, device scheduling/underflow
capture, accessible UI and signed distribution remain distinct product gates.
Future agents must preserve the selective-export isolation, rebuild coherent
source, retain failed probes as evidence, and update the handoff under
[AGENTS.md](../AGENTS.md) before the integrator's authorized commit and push.

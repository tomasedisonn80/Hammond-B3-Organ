# Product continuation: native code and portability review

Actual reviewer: `/root/w05_a30_portability_review`, A30, wave 5, 15 November
2026 UTC. This is an independent source review, one focused numerical
regression execution and one corrected-metadata runtime check. It is not a
replacement for platform execution.

## Conclusion and source boundary

No production correctness, state-preservation, allocator-pairing, or supported-
platform portability defect was confirmed in the reviewed changes. One small
reporting defect was found in the new manual paint benchmark: its ordinary
current-only build declared alternating painter order even though it runs one
painter. The focused correction is described below. Paired A27 measurements
are unaffected.

The reviewed production delta is from baseline
`af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d` to published feature source
`ff41d412d03f2c5767aa4057b29fa8ec1627449b`, tree
`6462343bb34a7d70d59de75ab349f8530196988c`. Local HEAD and the fetched
`origin/main` both named that source when inspected. The
[implementation receipt](../development/2026-11-15-product-continuation/reports/implementation-publication.json)
and [coherent-build receipt](../development/2026-11-15-product-continuation/reports/wave4-coherent-build.json)
retain publication and executed-test identities separately.

A30 rehashed every changed source in the coherent-build receipt. All matched
except `apps/standalone/CMakeLists.txt`, whose deliberate, uncommitted additions
wire A26's native calibration fixture and A27's manual target. Supplemental
inputs inspected in the working tree were:

| Input | SHA-256 at review |
| --- | --- |
| `tools/standalone_paint_benchmark.cpp` before the reporting correction | `88b7fb146dfd0b4ffdac6be8bf1fd72fa207725d75f782d220878d7251bec4cb` |
| `apps/standalone/native_tests/calibration_lifecycle_driver.cpp` | `9c9f32a83320671f6617c28da640e5b0837d09d5db58c4fb874896a5c5ed255e` |
| `apps/standalone/native_tests/fake_calibration/RtMidi.h` | `0cdd03fdca2bf65bad6ff1b0d5043a85950fe841b5bc76cb5bb8e2df8402710f` |
| `apps/standalone/native_tests/test_standalone_native_calibration.py` | `e4d2d86501582d9ee612b7c110144b595b0bbe85427c86000403a7a955f98e85` |
| Supplemental `apps/standalone/CMakeLists.txt` | `396d67a24a5a5955e11bdb1342e695bbecfd3a55da542dbbd34e48f779c06a22` |

Those supplemental hashes do not belong to the published feature commit or
inherit its 176-test result. Root subsequently archived A27's exact measured
benchmark source/report in local commit
`1080d15749f3a96d8259c0befcc0307aab7ea9a5`, tree
`77c65ce06378a5a25a05591226d05b2445d91b1e`, before authorizing A30's focused
metadata correction. Root then reported verified publication of that same
archive tree as `99b363438b3c4f217e0acb5361c0aea52ad7d0e3`, preserving the
local predecessor. The reviewer changed no production painter, CMake,
shared build, index, or publication state.

## Concrete finding

**A30-1 — Low severity, manual benchmark metadata.** In
[`standalone_paint_benchmark.cpp`](../../tools/standalone_paint_benchmark.cpp),
the JSON writer emits `"alternating_order":true` unconditionally. Without
`HAMMOND_PAINT_BASELINE`, `paired` is false, `before` is null, and both warmup
and measurement loops execute only `current`. The newly wired ordinary target
uses that configuration. Its timing observations are valid current-only
observations, but the order field is factually incorrect.

After root archived the measured source and assigned this correction to A30,
the writer was changed to emit `(paired ? "true" : "false")` for
`alternating_order`, retaining the field and schema. Corrected source SHA-256:
`d81eb9412d6d885807e57b4657c58519309a3e2b830c904ff1b36d6b40569338`.
The paired branch retains its existing true value. This is metadata only;
it does not require repeating A27's paired timing experiment.

After root's coordinated rebuild, A30 ran the ordinary executable once:

```sh
../build-native/apps/standalone/hammond_standalone_paint_benchmark 960 700 flat zero
```

The process exited 0 with empty stderr; parsed JSON had `paired:false`,
`alternating_order:false`, `before:null`, a null baseline-pixel fingerprint,
30 warmups, 300 measured samples and heap instrumentation false. The metadata
check completed in 4.988 seconds. It is not new timing qualification.
Executable SHA-256:
`10d7592d2e6d9e75f4cc45171d5a4e82855839733fd545f9f01e4ce4a43bcfb6`.
Stdout SHA-256:
`8ab886aa3176e28634575aa9d46384fb2ba3b40bb2f4ba4851a41db8eabbfa73`.

## Reviewed production boundaries

### MIDI, native settings and exception boundaries

The [channel-mode](../MIDI_CHANNEL_MODE_CONTRACT.md) and
[expression-calibration](../MIDI_EXPRESSION_CALIBRATION.md) contracts were
checked against `MidiInput.h/.cpp`, `Session.h/.cpp`, and the changed native
`main.cpp` paths.

- Endpoint validation precedes arithmetic. Integer promotion makes the
  subtraction and clamp safe; the valid extent is 1–127. Defaults compute the
  original binary64 division, invalid input preserves the destination, and
  inversion follows saturation. Epoch validation happens before route,
  calibration, timestamp history or diagnostic mutation.
- `ScopedSoundOff` appends to the existing variant. Invalid domain, bus or
  channel rejects before sequence/queue reservation. The application boundary
  checks ideal contacts before constructing a canonical scoped release. The
  new payload owns no dynamic resource and does not introduce a generic core
  note action, source reset, controller reset or new callback exception path.
- CC121 requests normalized expression 1.0 directly. Native controls continue
  through the shared desired-control and acknowledgment path. Calibration is
  copied in each pending request; active diagnostics require an active decoder.
  Invalid Apply preserves the old configuration, healthy identical Apply
  avoids retirement, and changed settings use the existing close/join/release-
  acknowledgment barrier. A failed open consumes its request and retires the
  decoder rather than displaying retained settings as active.
- CLI endpoints are parsed into `int` with complete `from_chars` consumption
  and range checks before narrowing. Duplicate flags and combined endpoint
  ordering reject before SDL initialization or output writes. New string and
  optional-request copies remain on the application thread under the existing
  guarded application/RAII boundary. No such copy was inserted in Session's
  callback processing.

### Crossover numerical and transactional behavior

The [frozen electrical contract](../LESLIE_CROSSOVER_CONTRACT.md) was checked
against `LeslieCrossover.h/.cpp`, the probe, the Python reference and their
relevant acceptance cases.

The four physical coordinates, floating treble port and current signs agree
with the contract. Preparation stages the transition/forcing matrices and
commits them only after finite/residual admission. The fixed LU scales each
original equation and applies the recorded row pivots to the scaled right-hand
side before substitution; swapping complete LU rows is consistent with that
sequence. Rate changes preserve the physical checkpoint and previous input.

Processing validates counts, capacity, frame overflow and byte overlap before
reading a trajectory. The byte-range check guards integer address overflow and
does not form out-of-allocation end pointers. The bounded two-pass transaction
uses the same recurrence evaluation order, writes nothing during validation,
and commits only after the full block succeeds. Its guarantee depends on the
documented externally serialized object and immutable input spans. State and
port arithmetic stay finite under the declared admission bounds; this is not
a claim of arbitrary-rate, arbitrary-load or arbitrary-magnitude support.

`response` solves the prepared recurrence, preserves history, and handles DC
with the stated equilibrium and its actual recurrence residual. The admitted
rates and load ranges avoid reliance on extended-precision `long double` in
the model. The probe uses `long double` for accumulation and phase reduction,
but its conditioning threshold is expressed using binary64 epsilon; it does
not assert a larger mantissa or serialize platform-dependent object bytes.
MSVC's numerical output still requires its actual platform gate.

The probe bounds option count, number length, frequency count, report size and
total sine frames. Checked unsigned parsing and subtraction before the frame-
budget sum avoid wraparound. Real parsing reuses the existing locale-independent
decimal helper; it does not require floating-point `from_chars` support.
Classic-locale JSON is constructed before publication and its numeric outputs
are checked. Invalid inputs are caught at the CLI boundary; offline allocations
are not presented as callback work.

### Near-DC independent-reference correction

The corrected Python nodal oracle retains independently stamped physical edges.
Its source current is the sum of currents returning to B: capacitor current
from H and capacitor/resistor currents from W, with edge orientation accounted
for. KCL makes that sum equal to source current while avoiding subtraction of
nearly equal A/H/W potentials followed by division by a small inductor
impedance. It does not copy native transition matrices or replace the oracle
with the native response function.

A30 executed only this focused regression, from the repository root with
Python 3.12.14:

```sh
python3 tests/test_crossover_reference.py \
  CrossoverReferenceTests.test_near_dc_reactive_current_survives_equipotential_inductor_nodes
```

**Passed: one test in 0.002 seconds, 144 comparisons, maximum normalized error
`2.2204502844110104e-16`.** The case also checks the small reactive-current
component relative to an independent polynomial, so a large real DC conductance
cannot conceal its cancellation. Reference SHA-256 remained
`33eaa88da2534e52f88c044b5fbabf19828655bacb357dc55bbeb6510b580ec5`;
test SHA-256 remained
`e6c8469e345f634606624b2f3eb063cd9091b91d1b2cf1023aadd95598eac4aa`.
A19's [original cancellation and repaired evidence](../development/2026-11-15-product-continuation/notes/A19-crossover-response.md)
remain unchanged.

## Resource and portability review

The allocation observer in `test_leslie_crossover_allocation.cpp` and A27's
optional heap build uses ordinary `malloc/free`, POSIX `posix_memalign/free`
on Unix/Apple, and `_aligned_malloc/_aligned_free` on MSVC. It preserves native
requested payload size on those targets; only the fallback `aligned_alloc`
path rounds size, with checked addition. Zero-size requests and scalar/array,
sized, aligned and nothrow delete combinations are covered by explicit
positive controls through volatile function pointers. Assertions and reporting
occur after observation. The crossover's larger test buffers have static
storage rather than consuming a Windows-sized test stack.

These checks observe current-thread global C++ allocation/free calls. They do
not measure all C/system allocations, leaks, other threads, locks or deadlines.
A25's [retained Release result](../development/2026-11-15-product-continuation/notes/A25-crossover-allocation.md)
and its original local sanitizer failure retain those distinctions. The
leak-enabled sanitizer and empty-main control both stopped at the environment's
ptrace restriction; neither is a sanitizer pass.

A27's manual benchmark shares one renderer, Drawing instance, current model,
headers, fonts and assets across the two painter translation units. The
field-wise geometry hash covers the `UiLayout` fields and active control/key
geometry without hashing padding. Timing uses a steady clock, separate warmup,
alternating order only when paired, and excludes reporting, capture and
fingerprinting. The heap variant does not publish timing qualification. Fixed
dimensions bound pixel indexing and storage; Drawing, renderer and surface
destruct before `SDL_Quit` on normal return and standard-exception unwinding.
No new texture construction was found in the changed paint primitives.

The supplemental A26 facade protects shared mutable discovery/transport log
state with one mutex. Installed shared ownership is set before startup and
retired after the real application destroys/joins its clients. Its callback
offers are synchronous at dependency API boundaries, which is explicit in the
trace. It therefore exercises native lifecycle/acknowledgment ordering but does
not simulate OS callback concurrency or qualify real hardware behavior.

## Evidence already retained and remaining gates

| Evidence | What this review established |
| --- | --- |
| Root's coherent GCC 14.2 Release build and 176/176 CTest, 177.92 seconds | Read the retained receipt/log and rechecked its changed-source hashes; A30 did not rerun the suite. |
| A19 independent response and sine acceptance | Read source and retained result; executed the single repaired near-DC regression separately. |
| A25 calibrated allocation result | Inspected overload pairing, calibration and bounded fixtures; retained source matches the executed receipt. |
| A26's 9 tests / 10 native subprocesses | Read the [worker evidence](../development/2026-11-15-product-continuation/notes/A26-native-calibration-lifecycle.md); inspected supplemental facade/driver source and integration wiring. Integrated CMake execution is a separate gate. |
| A27 paired paint/heap observations | Read the [exact-input report](../development/2026-11-15-product-continuation/reports/A27-paint-performance.json) and [worker note](../development/2026-11-15-product-continuation/notes/A27-paint-performance.md); corrected the current-only metadata issue and executed one ordinary metadata check. No paired timing experiment was repeated. |
| AppleClang/macOS, MSVC/Windows and hosted sanitizers | Source portability reviewed; current primary job logs were not independently audited by A30. Do not infer those passes from the local GCC run or earlier commits. |

Next, the integrator should retain A30-1's correction with its source identity,
build the newly wired ordinary benchmark and calibration fixture coherently, and run
`ctest --test-dir ../build-native --no-tests=error -R '^test_standalone_native_calibration$'`
after building its required executable. Retain the actual core/native hosted
results at their exact published source, including leak-enabled sanitizer
policy and any failures. At handoff, root reported success for all thirteen
jobs at `ff41d412d03f2c5767aa4057b29fa8ec1627449b`; the source-specific
primary-log audit was still planned. This review did not independently audit
those logs. That result cannot qualify supplemental native targets or the
later manual-tool correction absent from that source.

Same-Hz audible acceptance, real drivers/controllers/displays, physical cabinet
measurements, Engine integration, audio deadlines, accessibility and literal
whole-interface 1:1 equality remain outside this review.

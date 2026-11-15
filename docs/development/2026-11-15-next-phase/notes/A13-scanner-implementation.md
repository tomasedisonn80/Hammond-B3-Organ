# A13 — Additive native scanner FOH implementation

**Assignment:** `/root/w03_a13`, wave 3, 15 November 2026.  
**Checkout:** `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.  
**Owned paths:** `include/hammond/ScannerLineFoh.h`, `src/ScannerLineFoh.cpp`,
`tests/test_scanner_line_foh.cpp` and this note.  
**Implementation contract:** `scanner-foh-line-contract-v1`, reviewed SHA-256
`90b3564497ebd669baaaf0badf1a954953f1e1322c45f3e64e37e23cb826866e`.

## Scope and source basis

The additive class is implemented. Root's coordinated GCC 14.2 Release build
and required focused CTest passed; A13 inspected the resulting native log.
This producer result does not qualify the full independent stationary,
transient, process, lifecycle or resource gates in the reviewed contract.

I read the complete `AGENTS.md`, M0–M9 plan, current session entry/checkpoint
and assignment, complete reviewed FOH contract and A10 review, existing line
header/implementation and generated documentary component data. I recovered
the current shared navigation and relevant line/primary-source and A03 source
assessment. The implementation uses the existing retained atlas and primary
review; this assignment claims no new atlas reading or instrument measurement.
Root retains checkout/build/publication authority. No git, child-agent,
configure, compilation or shared-navigation mutation was performed by A13.

The physical model remains `atlas-late-b3-nominal-line-v1`. The new realization
is `scaled-physical-exponential-foh-scanner-line-v1`, with preparation method
`scanner-augmented38-pade13-scaling-squaring-v1`. Public mode/state/frame/response
types, dimensions, computational bounds and the eleven-rate predicate are reused
unchanged from `ScannerLine.h`. The header was published to root before the
source/test completion so A16 can use the stable public surface.

## Implemented behavior

Preparation stamps the reviewed scaled physical equations directly from the
unchanged generated values. The six divider attachments, termination, source
current orientation and chorus return remain those of the admitted graph.
Only the eighteen capacitor differences and eighteen inductor currents are
retained physical histories. The auxiliary input coordinates exist only during
stopped preparation.

For each mode, preparation forms the 38-dimensional normalized-time augmented
generator, retains its one-norm and scales by the smallest permitted power of
two that brings the norm to at most 0.5. The two Padé polynomials use the
contract's degree-13 coefficients **normalized by their common positive c0**,
preserving the specified six-product evaluation order. There is no trace shift,
coordinate balancing, threshold truncation, eigenanalysis or fallback.

One independently row-scaled partial-pivot LU solves all 38 numerator columns
and 38 inverse columns for the condition diagnostic. Every pivot must exceed
eight binary64 epsilons; nonfinite arithmetic and zero row scales reject.
Residuals use the same scaled system as the condition, with the specified
zero-denominator rule, `1e-9` residual ceiling and `condition*2^-52<=1e-4`
preparation admission. Bounded squaring then produces the transition and
separate previous/current endpoint vectors. Both operators and diagnostics
are completed in temporary fixed storage before publication.

Processing maps physical current to the existing Zref scaling, performs one
36-by-36 matrix/vector product and 72 endpoint-forcing products, maps back to
amperes, validates the complete candidate, reconstructs with the **current**
input endpoint, and commits checkpoint and destination together. The first
cold call advances one interval and returns frame 1. The supplied mode applies
to the complete upcoming interval; no hidden previous mode is retained.
`observe` uses the stored input and advances no history.

The stopped response helper solves the prepared recurrence
`(I-d*T)Z=b_current+d*b_previous` and reconstructs outputs at unit current
input. It admits only finite results with normalized residual at most `1e-9`,
retains finite conditioning diagnostics and never substitutes a continuous
analog solve. Reconfiguration preserves the full physical checkpoint; an
equal valid rate is an exact no-op. Rejected operations preserve logical
metadata, physical state and destinations in the specified precedence order.

## Authored behavioral coverage

The separate producer test exercises:

- Cold defaults and endpoint timing; all eleven rates and both preparation
  diagnostics; exact authoring/realization/preparation identities.
- Twenty-two exact-rational DC comparisons, nineteen signed taps plus return
  and dimensionless input current; finite positive-frequency responses at
  100, 997, 5000 and 7000 Hz, preserving nonzero history.
- Thirty public same-polygon flow-composition paths: three base rates, two
  return modes and subdivisions 1, 2, 4, 8, 16, each over 48 original knots.
  This checks FOH endpoint/time scaling without using private coefficients.
- Separate `(previous,current)=(1,0)` and `(0,1)` forcing behavior, sign
  reversal, independent algebraic KCL/output reconstruction and four charged
  fixtures for 64 zero-drive frames at every rate/mode.
- All 121 ordered rate changes, both endpoint observations, exact same-rate
  diagnostics and continuation against independently prepared replay clones.
- Invalid inputs, rates, frequencies and modes; all 37 caller-supplied numeric
  state/history fields with NaN, infinities and both just-outside limits;
  joint-energy rejection; inclusive 1-J/current and input-history boundaries;
  combined-error precedence and saturated counters.
- A finite late candidate-energy rejection in both signs and modes. An
  admitted half-amplitude public process independently reconstructs the
  excessive-energy full candidate, followed by exact rollback continuation.
- Exact partition equivalence for 1, 64, 127 and repeating
  `[1,17,64,3,127,2,31]` batches at all eleven rates, including mode switches.
- Two actual 997-Hz process/response consistency smokes at 48 kHz, with two
  seconds of startup and a one-second integer-cycle complex projection.
  These are producer consistency checks, not the 88-case independent process
  protocol or its successive-settling admission.

The full independent graph-derived coefficient/basis oracle, frozen frequency
grid and same-Hz grading, nine-fixture transient convergence, 250-ms energy
runs, allocation instrumentation, compiler stack accounting, Release timing,
sanitizers and platform execution remain with later acceptance owners. A
producer test pass cannot substitute for those gates.

## Bounds and source audit

Persistent operators contain exactly `2*(36*36+2*36)=2736` binary64 scalars,
or 21,888 bytes, plus the checkpoint, diagnostics and scalar metadata. A public
class-size assertion enforces the reviewed 24-KiB ceiling. Preparation is at
most two 38-dimensional factorizations, 76 solves per mode and 44 dense matrix
products overall. The nominal supported rates require only one to three
squarings; the code retains the full sixteen-squaring cap.

All owned runtime source uses fixed `std::array` storage. Source inspection
finds no heap, logging, locks, parsing, I/O, matrix factorization or exponential
evaluation in processing. Source-level live-object accounting places stopped
reconfiguration/preparation below 192 KiB, response below 48 KiB and processing
below 2 KiB on a conventional 64-bit ABI, including nested helper storage.
These are conservative source counts, **not compiler-observed stack or
allocation-instrumentation results**; the later resource owner must retain
those actual measurements.

Observation bounds are still checked in code even where a public rejection is
unreachable from admitted energy coordinates. The energy limit implies
`abs(x_k)<=sqrt(2/C_k)`, hence at most 44,721.36 V, and `abs(i1)<=2 A`.
With `abs(u)<=64 V`, the independent chorus return bound is below 35,738.54 V.
Every tap is consequently below 80,459.90 V using a conservative triangle
bound, below 131,072 V. Vibrato input current is at most
`2+64/95000<2.001 A`; chorus satisfies `Iin=r/22000<1.625 A`, both below 4 A.
The tests do not falsely claim to have reached these public output-limit
rejection branches. Isolated validator/helper adversarial tests may be added
without a runtime mutation API.

## Verification record and handoff

Executed by A13: read-only source inspection, SHA-256 preservation checks,
file/line inventory, and inspection of root's actual native test log at
`/workspace/scratch/116ca0948095/build-native/Testing/Temporary/LastTest.log`.
Root built `test_scanner_line_foh` coherently in the coordinated Release tree
with GCC 14.2 and the strict project flags
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
Its required CTest selection `^test_scanner_line_foh$`, with
`--no-tests=error`, passed **1/1**, **0.84 s test / 0.87 s total**.
No implementation repair was required after this build. A13 performed no
configure or compilation. No dependency, CMake, old scanner, Engine,
parameter or saved-state change was made by this assignment.

Retained actual test stdout:

```text
scanner FOH producer behavior checks passed
sizeof_scanner_line_foh=22280 dc_cases=22 maximum_dc_complex_error=4.2454928461665986e-13
rate_pairs=121 subdivision_paths=30 rejected_calls=223
process_response_smoke_cases=2 maximum_complex_error=1.1998629721882189e-14
independent_full_grid_transients_resources_acceptance=not_run_by_this_test
```

The 22,280-byte class size is compiler-observed by this test. The test duration
is not a line-only processing benchmark or callback deadline. The following
hashes were observed after execution; the three owned code files are unchanged
from the built inputs. No full-tree or published-commit claim is inferred.

| Tested input/output | Observed SHA-256 |
| --- | --- |
| New public header | `c7cf443b9fe85f0fe544605b2a15fbc2539661f735ca62760dbb510f7111b887` |
| New implementation | `9f5ff3f25f3564774ecaace292eb9299b3d75e897ce7fe6b30a59575addc24df` |
| Producer test | `f6b9bd26a2fa5460ef39f42e524d83f7cc4071c02db76596e24874f6497a0b21` |
| Generated scanner header | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |
| Focused native executable | `9effcd61e18752db7070cff44206053831733f9af8afbae21921210e79e744af` |

| Preserved input | Observed SHA-256 |
| --- | --- |
| Old ScannerLine header | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| Old ScannerLine implementation | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| Old native probe | `4a283205949a837df8835f2b86874ee66624631d05fbdf8a6ccce7ff54e16fdb` |
| Authoring graph | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |

Next: A16 can implement the separate native probe against the stable public
header. Later owners execute the independent acceptance in the reviewed
contract before any stationary-line claim, and retain all lower-rate failures.
Host reconstruction/decimation, the rotating pipeline, G5 completion, G6/Engine
integration and physical M4 remain separate and unqualified.

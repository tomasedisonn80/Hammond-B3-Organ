# A14 — Independent cubic and owned-history acceptance

## Assignment and boundary

Actual worker: `/root/w03_a14_history_acceptance`, wave 3, 14 November 2026.
Owned repository paths are this note and
`tests/test_rotary_history_acceptance.cpp`. No public header, production source,
contract, CMake, shared status, manifest, commit or publication changes were made.
Observed HEAD before and after the qualified run:
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`. The tested implementation was A13's
uncommitted `src/RotaryHistory.cpp`, identified below; HEAD alone does not
identify these tested bytes.

Read the standing instructions, current continuation scope/checkpoint/assignment
manifest, complete project plan, atlas review and A04's relevant source reading,
frozen numerical/renderer/waveform contracts and public motion/history types.
This assignment verifies native cubic interpolation and owned-history behavior.
It does not qualify the complete renderer, R5 reconstruction, R6 allocation or
device deadlines, Engine integration, or measured physical M7.

## Independent expected values and coverage

The test derives four-node weights directly from the defining product on
`{-1,0,1,2}`, using standard-library `long double`; it imports no production
coefficients or interpolation/motion helper into its expected-value calculation.
All 1,028 degree-zero-through-three polynomial points compare separately with
both this product and the analytic polynomial `(x/2)^degree`. Seventy-nine
additional tuples cover signed mixtures, alternating values, positive/negative
impulses at every node, signed zero and 64 deterministic bounded tuples from
seed `0xa14c0b1c5eed1234`, at all 257 fractions.

The complete 65 × 512 static grid calls the native primitive separately on
the cosine and sine support samples. It retains the positive-exponential sign
convention, independent ideal complex values, complex error, and the `mu=1`
row. Every grid result also meets the independent same-cubic product budget.
The high band is characterized without imposing the low-band budget on it.

Behavioral coverage includes 158 exact endpoint cases; 15,420 successful alias
cases; invalid fractions, nonfinite/out-of-range support at all four locations
including zero-weight endpoints; rejection preserving destination/sample bits;
and exact ±1.25 overshoot without clipping. Four supported rates and capacities
`1,2,3,4,5,7,16,16384` exercise waveform startup, every retained sample after
multiple wraps, eviction, negative indices, missing/future supports, fractions
adjacent to integer boundaries, signed overflow, copies and clearing reset.
All successful/rejected reads are checked for immutability. Rejected mutations
compare every physical slot and metadata field by representation, including
signed zero, using the already-declared test friend.

Independent unwrapped analytical motion checks cover both directions, all rates,
capacities `1,2,4,9`, old command anchors after their slots retire, ordered ties,
unchanged commands, strict final endpoints, negative constant-speed history and
owner profile/rate/seed/frame/continuity admission. Twelve accelerated epoch
fixtures cover four waveform and eight motion final-day boundaries. They alter
only the private history clock after public operations establish valid retained
slots; these are boundary fixtures, **not continuous one-day stress tests**.
All histories and complete snapshots are heap allocated.

## Executed result

The source-stable run passed **774,721 checks**, including **23,963 rejected
calls**, **131,728 ordinary waveform pushes**, **65,816 waveform reads**,
**32,140 waveform interpolation queries**, **1,536 ordinary motion appends** and
**20,032 independent motion comparisons**. No failure was recorded. Counts of
ordinary pushes/appends exclude the small explicit lifecycle/end-epoch setup
operations rather than pretending to count all calls.

| Numerical group | Complete count | Maximum error | RMS error |
| --- | ---: | ---: | ---: |
| Polynomial / defining product | 1,028 | `6.776263578034403e-21` | `1.230363736112919e-21` |
| Polynomial / analytic polynomial | 1,028 | `0` | `0` |
| Additional support / product | 20,303 | `6.776263578034403e-21` | `4.524617980509106e-22` |
| Native complex / product | 33,280 | `2.371367685799666e-16` | `6.487150010916883e-17` |
| Native complex / ideal, low band | 6,695 | `0.003480564142224874` | `0.0008464023833509164` |
| Native complex / ideal, full band | 33,280 | `0.9953980792939058` | `0.2789346813611962` |
| Available waveform / product | 12,800 | `1.220269545132435e-16` | `2.329282412050688e-17` |
| Historical motion angle | 20,032 | `5.684341886080801e-14 rad` | `1.116246397994315e-14 rad` |
| Historical motion speed | 20,032 | `3.156329364539801e-15 rad/s` | `8.552003668033088e-16 rad/s` |

The low-band maximum occurs at fraction index 32 / frequency index 102 and
passes the frozen `0.005` limit. The full-band maximum is at `(32,511)`;
23,874 full-grid rows exceed `0.005`. Those values are preserved, not described
as broadband success. Cubic/product groups meet `2e-12`; each motion query uses
the frozen angle/speed absolute-plus-relative budgets.

The qualified executable ran in **0.130716627 seconds**, with Python
`resource.getrusage(RUSAGE_CHILDREN)` reporting **11,008 KiB maximum RSS** for
that executable invocation. GCC 14.2.0, Linux x86_64; binary64 has 53 precision
bits and `long double` has 64 (16-byte storage), rounding mode 0. There is no
80-digit precision claim. The initial `/usr/bin/time` wrapper failed with exit
127 because that program is absent; Python measured the successful rerun.
The normal no-argument invocation also passed at a **512 KiB stack limit**:
774,719 checks and all 33,280 grid evaluations, with no artifact-output checks.
No shared build was used.

## Reproduction and retained artifacts

Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.

```sh
g++ -std=c++20 -O2 -fno-fast-math -ffp-contract=off \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -Iinclude tests/test_rotary_history_acceptance.cpp \
  src/RotaryHistory.cpp src/RotaryMotion.cpp \
  -o ../a14-history-acceptance/test_rotary_history_acceptance
../a14-history-acceptance/test_rotary_history_acceptance \
  --static-grid ../a14-history-acceptance/static-grid.csv \
  --report ../a14-history-acceptance/report.json
```

The existing `tests/test_*.cpp` CMake glob discovers the test once the integrator
links `RotaryHistory.cpp` into `hammond_core`. Default execution always evaluates
the complete grids; `--static-grid` additionally writes them. `--report` writes
the same machine-readable JSON as stdout. There is no external test dependency.

Completed artifacts are under sibling `../a14-history-acceptance/` for the
integrator, who owns report retention: `qualification.json` contains exact
native JSON text, source hashes before/after, compiler/options, invocation,
precision, metrics, resource observations, executable identity and limits;
`static-grid.csv.gz` contains every native/ideal/error row. All 33,280 ordered
coordinates and the gzip lossless round trip were independently checked.

| Artifact | Bytes / dimensions | SHA-256 |
| --- | --- | --- |
| Native executable | Executed strict Release-style binary | `5a57bb4140e7b4813f098aab29953da21118cbcd13817d239598f78a8442affb` |
| Complete raw CSV | 4,890,892 bytes; 33,280 rows × 7 columns, plus header | `34434383696384062b622de40ac08a29ab52f33a583b85d5764fadda12db367c` |
| Deterministic gzip CSV | 2,056,124 bytes | `03a56786a5d929d9a942048091b91fb5e791926019a0e0f3f0dc8aeceb0a2e77` |

Every relevant source was hashed before compilation and after execution; all
matched:

| Source | SHA-256 |
| --- | --- |
| `tests/test_rotary_history_acceptance.cpp` | `839f85847e381c536549829395fb436964bb03e80092802ba5f700a495b59c03` |
| `src/RotaryHistory.cpp` | `4f3c4fbd957f7cc9131b1f4e7c6e77f69df1b7e85c9ba4073de59fe52322a0f5` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `docs/ROTARY_RENDERER_CONTRACT.md` | `52eaaeda293376abd47af3f788e3bd5967452b176cba021f23ab7bc3b1e141a9` |
| `docs/ROTARY_WAVEFORM_ACCEPTANCE.md` | `fa4288d586a2a40d803740408177f9c0a085bd4deb9ae0bdfc832e6d58b0c1aa` |

## Next integration and limits

Integrator: retain the compressed grid and qualification JSON, build/run the
automatically discovered target with the current native library, and carry
these primitive results into the separately owned full renderer qualification.
A18 can supply broader motion/event lifetime and allocation stress; this worker
does not claim those larger fixtures. Only GCC/Linux was executed here. Whole
renderer rollback, stream/block parity, stopped-rate pairs, actual allocation
instrumentation, host/platform jobs and physical measurements remain separate.

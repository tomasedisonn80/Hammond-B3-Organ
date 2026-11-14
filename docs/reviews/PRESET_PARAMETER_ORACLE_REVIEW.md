# Independent preset parameter numerical review

Reviewer: `/root/w04_a21_parameter_oracle`, 2026-11-14, logical wave 4.
Normative inputs: the frozen
[`fixed-registration-state-parameters-v1`](../PRESET_STATE_PARAMETER_CONTRACT.md)
and [`exclusive-fixed-registration-v1`](../PRESET_SELECTION_CONTRACT.md).
Implementation under review: A16's append-only registry and C++/Python scalar
converters, identified by the hashes in the [A21 execution record](../development/2026-11-14-preset-continuation/21-parameter-oracle.md).

## Finding

**The two new selectors pass independent exact numerical acceptance.** The
actual native bridge and actual Python API agree bit for bit for all eleven
thresholds and both adjacent binary64 values, all twelve canonical values,
signed zero, positive subnormal/normal minima and the predecessor of one under
all four standard rounding modes. Invalid domains and unknown native identities
preserve their destinations and caller modes. No new selector numeric defect
was found, and no production converter was changed by this review.

The complete previous 45 registry records retain the frozen digest
`13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`.
All 45 old event mappings also match an independent rational oracle through the
current 47-record diagnostic executable. The earlier 39-/43-record guards remain
unchanged and passed in the existing parameter suites.

There is one **retained legacy signed-zero asymmetry**, described below. It
predates the new selectors; this review does not claim universal bit equality
between every old Python and native plain conversion under every rounding mode.

## Independent construction of binary64 values

The new tests do not read `PRESET_THRESHOLDS`, `PRESET_CANONICAL`, native literal
arrays or another test's expected tables. They construct each required value
from the exact integers in `k/11` and `(2k+1)/22`.

For a positive rational `n/d`, shift `n` left until `n/d` lies in `[1,2)`, keeping
the corresponding binary exponent. Integer division of `n * 2^52` by `d` gives
the candidate 53-bit significand and an exact remainder. A remainder above half
the divisor rounds upward; a tie rounds to an even significand. Carry out of the
significand increments the exponent. Zero is encoded directly as positive zero.
The native oracle's largest scaled numerator is below 44, so its shifted
integer fits `uint64_t`; Python uses arbitrary-precision integers.

Python independently decodes each resulting bit pattern into an exact
`Fraction`. It verifies that the original rational falls between the exact
midpoints to both adjacent representable values, with the correct parity for a
tie. Separate oracle cases exercise a downward tie, an upward tie and a carry
to one. The eleven adjacent-bit pairs are also checked against actual
`math.nextafter`. Neither nearest-value construction nor its certificate depends
on the active floating-point rounding mode.

The derived results are:

| k | Canonical nearest k/11 | Nearest threshold (2k+1)/22 | Threshold versus exact rational |
| ---: | --- | --- | --- |
| 0 | `0x0.0p+0` | `0x1.745d1745d1746p-5` | above |
| 1 | `0x1.745d1745d1746p-4` | `0x1.1745d1745d174p-3` | below |
| 2 | `0x1.745d1745d1746p-3` | `0x1.d1745d1745d17p-3` | below |
| 3 | `0x1.1745d1745d174p-2` | `0x1.45d1745d1745dp-2` | below |
| 4 | `0x1.745d1745d1746p-2` | `0x1.a2e8ba2e8ba2fp-2` | above |
| 5 | `0x1.d1745d1745d17p-2` | `0x1.0000000000000p-1` | exact |
| 6 | `0x1.1745d1745d174p-1` | `0x1.2e8ba2e8ba2e9p-1` | above |
| 7 | `0x1.45d1745d1745dp-1` | `0x1.5d1745d1745d1p-1` | below |
| 8 | `0x1.745d1745d1746p-1` | `0x1.8ba2e8ba2e8bap-1` | below |
| 9 | `0x1.a2e8ba2e8ba2fp-1` | `0x1.ba2e8ba2e8ba3p-1` | above |
| 10 | `0x1.d1745d1745d17p-1` | `0x1.e8ba2e8ba2e8cp-1` | above |
| 11 | `0x1.0000000000000p+0` | — | — |

The five thresholds below the mathematical midpoint are precisely 3/22, 5/22,
7/22, 15/22 and 17/22. At those stored values, equality must select the higher
key even though the exact rational half-up expression would still select the
lower key. The live comparison includes every one of these equality cases.

## Actual conversion paths and rounding modes

`tests/test_preset_parameter_boundaries.cpp` calls the public native
`normalized_to_event`, `plain_to_normalized` and `parameter_descriptor` functions.
Its expected values come from integer construction. It selects the platform's
own `FE_TONEAREST`, `FE_DOWNWARD`, `FE_UPWARD` and `FE_TOWARDZERO`, checks the
caller mode after every API call, and restores the original mode before exit.
The optional `--vectors` output contains exact input/output bits plus those
native mode codes; it does not export production tables.

`tests/test_preset_parameter_oracle.py` consumes those actual native conversion
results and calls `tools/validate_parameters.py` directly. It sets the Python
process's floating-point environment using the native-reported codes, so no
architecture-specific numeric `FE_*` constants are assumed. It checks exact
coverage as well as output values. Missing executables, unsupported modes or
missing `fegetround`/`fesetround` are hard failures; none is converted to a skip.

| Executed scope | Result |
| --- | --- |
| New selectors: 49 normalized and 13 plain inputs × two IDs × four modes | 496 native/Python bit-identical results |
| One representative per old kind under all four modes | 192 native vectors, with the documented old Python zero exception checked explicitly |
| New native invalid-domain conversions and 21 representative unknown IDs | 296 rejected conversions; event destination bytes and scalar NaN payloads unchanged |
| Unknown native descriptor lookup, 21 IDs × four modes | 84 rejections; complete destination bytes unchanged |
| Python invalid domains and unknown IDs | Exceptions, unchanged registry and unchanged caller mode |
| Actual 47-record diagnostic CLI across 49 boundary/canonical/edge inputs | 49 successful invocations; 2,303 event records checked against independent expected values |
| New Python oracle methods | 6/6 passed |
| Fresh Release CTest gate, including both existing Python parameter suites | 4/4 passed |

The new normalized input set includes negative zero, smallest positive
subnormal, smallest positive normal, and the predecessor of one. Plain negative
zero canonicalizes to positive zero for the new selectors in all modes.
Native event checks include both permanent manuals, `SelectPreset`, index zero,
and exact propagation of the maximum `uint32_t` offset.

Native invalid inputs include signed NaN payloads, both infinities, the negative
minimum subnormal, the first value above one, the first value above eleven,
twelve, positive subnormal plain values and fractional plain values. Unknown-ID
probes cover holes between retained ranges, both new-range neighbors, zero,
the signed-boundary area and maximum `uint32_t`. A16 already checks the much
larger exhaustive hole range; A21 intentionally adds an independent narrow
probe rather than duplicating that sweep.

## Retained old zero behavior

Before the migration, Python's plain converter used
`(plain - minimum) / (maximum - minimum)`. Under downward rounding, exact
`+0 - +0` produces `-0`, so an old record's positive plain zero returns negative
normalized zero. Native expression passes its value through and old discrete
conversion divides directly by the positive maximum, retaining positive zero.

| Plain input | Mode | Old native result | Old Python result | Both new-selector paths |
| --- | --- | --- | --- | --- |
| `+0` | nearest/upward/toward zero | `+0` | `+0` | `+0` |
| `+0` | downward | `+0` | `-0` | `+0` |
| `-0` | all four modes | `-0` | `-0` | `+0` |

This was reproduced using the actual Python source and registry loaded from
`b79086f`, with **180 checks** covering all 45 records in all four modes. The
new suite checks the same retained old sign rules and all old normalized
maximums. The integrator explicitly accepted preserving this compatibility
behavior. No old conversion arithmetic, table, fixture or identity was changed.

## Integration and limits

Both new tests use the existing CMake `tests/test_*` discovery. A test-specific
environment stanza supplies generator-expression target paths for the actual
parameter-info and boundary executables, and both are included in the `check`
target prerequisites. This supports multi-configuration output paths without
guessing executable names or neighboring directories. The actual generated
CTest configuration and a fresh build were inspected and executed.

Observed execution is Linux x86-64, GCC 14.2.0 and Python 3.12.14. The tests use
native mode constants and explicit executable paths for portability; this review
does not claim macOS or Windows execution. No existing baseline build was
reconfigured or linked against newer headers.

This closes the independent scalar conversion gate for the identified source.
The next gate is coherent current-source native adapter qualification: actual
47-parameter exports, state4/legacy restore, host same-sample alias order,
carry/plateau behavior and callback rejection rollback. Those tests have
separate owners. This review does not qualify a VST3 module, UI gesture, audio
device deadline, physical preset latch, loaded tap gain or specimen fidelity.

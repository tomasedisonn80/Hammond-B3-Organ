# Portable decimal conversion

`include/hammond/detail/Decimal.h` is the shared internal parser used by compiled
profiles, control snapshots, and offline event values. It uses the same C++20
standard-library implementation on Linux, macOS and Windows. Floating-point
`std::from_chars` is not required; unsigned integer parsing still uses its
existing `from_chars` implementation.

## Syntax and publication

The complete token must match this ASCII grammar:

```text
[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?
```

Both leading signs, a leading decimal point, a trailing decimal point after a
digit, padded digits and scientific notation are accepted. Whitespace belongs
to each caller's tokenizer, never to a numeric token. Empty or partial tokens,
multiple signs, decimal commas, digit separators, hexadecimal numbers, nonfinite
spellings, embedded NULs and non-ASCII digits reject before conversion.

`parse_decimal` returns `Ok`, `InvalidSyntax` or `OutOfRange` and assigns the
destination only on success. Exceptions also leave the destination unchanged.
Each caller keeps its existing input-size bounds and semantic value ranges;
for example, expression still must be in `[0,1]` and source frequency positive.

## Numerical behavior

Conversion extracts directly into `double` through a private `istringstream`
imbued with `std::locale::classic()`. It does not change the global C or C++
locale, inherit user facets, or convert through `long double`. The latter would
introduce a second rounding step on platforms with a wider `long double`.
The caller's floating-point rounding mode is temporarily set to nearest for the
conversion and restored on every exit, including exception unwinding. Failure
to select that mode rejects the token without publishing a result.

Lexically exact zero is handled before conversion, preserving its sign even
with an arbitrarily large exponent. A nonzero decimal that rounds to zero is
unrepresentable underflow and rejects. Finite nonzero subnormal results are
accepted, including values rounded up from below the smallest subnormal; a tiny
result that rounds to the smallest normal is also accepted. Overflow rejects,
including a stream implementation's saturated maximum-finite result. Values
slightly beyond the largest finite value that still round to that value remain
accepted, matching the previous conversion contract.

Standard-library implementations differ in their stream error flags at the tiny
end of the range. libc++ can set `failbit` for a nonzero subnormal result, while
libstdc++ can round underflow to zero without `failbit`. After grammar validation,
the parser therefore requires full stream consumption, no `badbit`, and a finite
nonzero value. It accepts `failbit` only when the magnitude is no greater than the
smallest normal `double`; all other conversion failures reject. LLVM's
[num_get implementation change](https://lists.llvm.org/pipermail/cfe-commits/Week-of-Mon-20160613/162458.html)
shows the direct `strtod_l` result and `ERANGE` flag propagation behind this case.

## Execution and verification boundary

The helper may allocate and is for stopped-engine loading, control serialization
boundaries, and offline event parsing. It is never called by audio processing.
There is no platform-specific fallback hidden from the Linux test run.

`test_decimal` covers independent exact binary64 vectors, decimal halfway ties,
both range boundaries, signed zero, long balanced significands and exponents,
malformed tokens, unchanged finite/zero/NaN destinations, custom global locale
facets, all four standard rounding modes, and round trips across every finite
exponent plus a deterministic dispersed bit-pattern sample. Existing profile,
control-state, and renderer tests remain required integration checks.

The original hosted macOS failure occurred at `b9c1cac` with AppleClang 17 and
Xcode 16.4 because its libc++ had no floating `from_chars` overload. Local Linux
verification of this replacement does not establish a hosted macOS or Windows
pass; that requires the subsequent published CI run.

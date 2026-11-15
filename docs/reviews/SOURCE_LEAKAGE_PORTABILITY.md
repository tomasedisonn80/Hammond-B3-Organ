# Source-leakage lifecycle: subnormal portability correction

**A35 decision:** admit the narrow test correction approved by the integrator.
The source-leakage contract, headroom bound, production arithmetic and normal
exact fixtures are unchanged. This corrects an unsupported assumption about
rounding in the existing downstream pedal mixer. It does not relax a leakage
acceptance tolerance or establish a passing repaired Apple build.

## Observed failure and source

At published commit `9f5610b6a7f9648dd7b8b1bcb25c2fd38615b994`, the
[macOS Release job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43715019795/job/132814560364)
built with AppleClang `17.0.0.17000013`, `-O3 -DNDEBUG -arch arm64`, without a
floating-point contraction override. `test_source_leakage_lifecycle` failed its
line-164 assertion that every tiny pedal mixture equals `33 * denorm_min`.
The preceding exact source-bound, configuration and pedal-bus assertions passed.
The original CHECK did not print the mixture value; an actual Apple value of
34 units is an inference, not a captured observation.

The [original hosted log](../development/2026-11-15-audio-continuation/reports/implementation-macos-first.log.gz),
original test SHA-256
`bfe916f1d377b984b518ea8d063dcba83d8a1f63eb83111687ab5ba5cb6ef192`,
and [A21's original note](../development/2026-11-15-audio-continuation/notes/A21.md)
remain unchanged. A21's 33-unit calculation was valid for separate binary64
multiplication and addition; the test inadvertently required that evaluation
policy from every supported compiler.

`src/PedalVoice.cpp` predates this change and evaluates each term with the single
statement `mixture += coefficient * bus`. The
[Clang compiler manual](https://clang.llvm.org/docs/UsersManual.html#cmdoption-ffp-contract)
documents default contraction within a statement, including in its precise
mode. Such contraction is separate from reassociation or enabling fast-math.
The [leakage core contract](../SOURCE_LEAKAGE_CONTRACT.md) explicitly excludes
cross-platform bit-identity claims for coupled arithmetic; the
[audition contract](../SOURCE_LEAKAGE_AUDITION_CONTRACT.md) preserves the existing
pedal path and freezes its source-domain admission, not a new global compiler
contraction setting. No build or production policy is changed here.

## Independent exact derivation

Let `eta = 2^-1074`, the binary64 minimum positive subnormal. The existing maximum
graph fixture supplies `9 * eta` to eight coefficients of `1/16`. Exhaustively
enumerating all 256 independent term-contraction choices for each polarity gives
exactly `±17 * eta` for the contaminated source. The corrected source guard
remains exactly `31 * eta`, and pedal 1 still gives exactly `±34 * eta` on each
of its four buses. These original exact checks are preserved.

The unchanged nominal pedal rows are `[1/2,1/4,1/8,1/8]` and
`[1/8,1/2,1/4,1/8]`. An integer/Fraction calculation expresses all quantities in
units of eta and rounds ties to even after the operation required by each policy:

| Row | Separate product/add accumulator sequence | Fused product/add accumulator sequence |
| --- | --- | --- |
| Mixture 1 | 17, 25, 29, **33** | 17, 26, 30, **34** |
| Mixture 2 | 4, 21, 29, **33** | 4, 21, 30, **34** |

For example, the first row's `1/4` term is `8.5 * eta`. Rounding the product
first yields 8, then adding to 17 gives 25. Fusing the term with the accumulator
rounds 25.5 directly to the even integer 26. Later terms retain the one-unit
difference. Negative inputs give exactly the sign-reversed outcomes.

All 16 per-term choices for each row and sign were enumerated: **64 tiny-row
cases**, with no production call. Their only outcomes are `±33 * eta` and
`±34 * eta`. Choices for the two rows are independent; no contract requires
the compiler to fuse both rows identically. The permitted positive tuples are:

| Mixture 1 / eta | Mixture 2 / eta | Both at position 8: output / eta |
| ---: | ---: | ---: |
| 33 | 33 | 66 |
| 33 | 34 | 67 |
| 34 | 33 | 67 |
| 34 | 34 | 68 |

With only one drawbar at 8, output equals that row's exact value. Negative tuples
are symmetric. Mixed row policies are permitted by the derivation; neither local
compiler probe happened to emit a mixed tuple. Another **128 exact-rational
normal-row cases** show that either contraction choice retains the two original
normal fixture literals, `1.5` and `0x1.fffffffffffacp+0`.

## Controlled native reproduction

Two bounded private probes compiled the unchanged `src/PedalVoice.cpp` directly
with GCC 14.2 on Linux x86-64. Both used C++20, `-O3`, strict warnings as errors
and `-mfma`; only `-ffp-contract=off` versus `-ffp-contract=fast` differed.
Neither used fast-math or changed the main build. Both ran with round-to-nearest
and successfully retained nonzero subnormals.

The off build returned mixtures `±33 * eta` and both-enabled output `±66 * eta`.
The contracted build returned `±34 * eta` and `±68 * eta`. Disassembly of the
actual pedal function contained zero versus four FMA instructions, respectively.
Separate volatile-product and explicit `std::fma` arithmetic in the probe agreed
with the independent rational results. This reproduces the platform-sensitive
assumption with identical production source; it is not an Apple execution.

The [complete receipt](../development/2026-11-15-audio-continuation/reports/A35-portability.json)
retains all 704 rational source/row cases, eight signed row tuples, original
failure identity, source hashes, commands, compiler output, native values,
relevant disassembly, helper sources, syntax result and exact test diff.

## Exact correction and unchanged acceptance

The corrected test enumerates the two independently derived mixture literals
only for the tiny fixture. It requires one complete expected tuple to match
**both mixture diagnostics, their selected voice output and final float output**.
Expected tuples are computed entirely from independent fixture literals and
known positions; observed samples never generate the expected values. The two
normal fixtures retain a single distinct expected value each.

All exact graph/gain/bound/bus checks, adjacent unsafe-gain rejection, rates,
polarities, control selections, source histories and lifecycle tests remain.
There is no epsilon interval, test skip, output clipping, changed coefficient,
production/flag edit or relaxed source-domain limit. The correction acknowledges
the pre-existing supported expression semantics rather than changing them to
satisfy the initial fixture.

Strict GCC optimized syntax checking passed. Root must coherently build and run
`test_source_leakage_lifecycle`, then retain a fresh actual AppleClang hosted
result for the repaired source. That linked/hosted execution is separate from
these bounded probes. No physical fidelity, callback timing, whole-interface
equality or cross-compiler bitwise product guarantee follows from this review.

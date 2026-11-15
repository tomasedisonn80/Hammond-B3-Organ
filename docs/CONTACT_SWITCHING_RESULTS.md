# Fractional-contact reference v1: executed results

**The admitted offline v1 experiment passes for its identified source and frozen
synthetic inputs.** On 15 November 2026, the repaired study runner completed all
**36 fixtures and 144 renders** from a moved `ContactReferenceTools` installation,
with **21.728087337 seconds external wall time** and **36,974,592 bytes
(35.262 MiB) exact-child peak resident memory**. The
[qualified report](development/2026-11-15-execution-continuation/reports/contact-study-v1-qualified.json)
contains the complete arrays and row decisions; the
[external process receipt](development/2026-11-15-execution-continuation/reports/contact-study-v1-qualified-process.json)
records exit 0 and resource observations through process completion.

This qualifies the numerical implementation of a declared finite, acausal,
fixed-load switched-sine reference. It establishes no causal streaming filter,
native Engine comparison, full-window atlas `1e-4` grade, measured contact
physics or audio fidelity. The playable Engine, its 91 shared source identities,
47 sound parameters, `B3CONTROLS4` and readers 1–3 retain their existing meanings.

[Operating guide](CONTACT_SWITCHING_GUIDE.md) ·
[Install and relocate the tools](CONTACT_REFERENCE_INSTALL.md) ·
[Current execution checkpoint](development/2026-11-15-execution-continuation/CHECKPOINT.md).

## Frozen experiment and acceptance boundary

The [model contract](FRACTIONAL_CONTACT_REFERENCE.md) and
[independent validation protocol](CONTACT_SWITCHING_VALIDATION.md) were frozen
before implementation under the
[admission receipt](development/2026-11-15-execution-continuation/reports/implementation-admission.json).
Their original proposal/status wording remains unchanged; this document records
the subsequent execution. No tolerance, fixture, probe, filter or resource ceiling
was widened to obtain this result.

Twelve recipes run at **44.1, 48 and 96 kHz**, each with **256 observation frames**
and factors **32, 64, 128 and 256**. Every render returns **289 samples**, from
absolute frame **−16 through 272**, including complete pre-ringing and terminal
tails. Continuous key travel and independent hysteretic contacts are evaluated
before source integration and bandwidth reduction. The centered finite kernel
has support ±16 host frames and cutoff parameter 0.45 cycles per host frame;
it is not strictly bandlimited.

The distinction between the two comparison sets is essential:

| Comparison | Set actually graded |
| --- | --- |
| L128 → L256 numerical convergence | **All 289 output samples** of each of the 36 fixtures. |
| Continuous quadrature refinement | **64 frozen probes per fixture**, independently reconstructed with panel widths 1, 1/2 and 1/4 host frame. |
| L256 against the continuous reference | The same **64 frozen probes**, using the converged 1/4-frame quadrature values; both previous gates are prerequisites. |
| Output ranges and tails | Concatenated ranges from each complete immutable render; this checks exported data, not streaming filter state. |

Each row/rate must pass individually. Peak error is divided by the outward raw
bound **B**; RMS calculations scale by B before squaring. NRMSE is eligible only
above the protocol's normalized reference-RMS floor `1e-8`. The three F00 rows
have exact-zero bound and exact silence; the other 33 rows are eligible.
No fitted gain/delay, tail trimming or pooled error replaces a row's decision.

## Numerical outcomes

The qualified report contains **zero failed cells** and no incomplete reason.
The largest observed values below are rounded for readability; the report keeps
their full binary64 values and fixture identities.

| Gate | Maximum peak/B | Frozen peak/B limit | Maximum eligible NRMSE | Frozen NRMSE limit |
| --- | ---: | ---: | ---: | ---: |
| Oracle 1/2 → 1/4 refinement, 64 probes | `1.965095e-14` | `1e-9` | `8.114475e-15` | `1e-7` |
| L128 → L256, all 289 samples | `1.165897e-5` | `6e-5` | `1.222095e-5` | `3e-5` |
| L256 versus continuous 1/4 reference, 64 probes | `3.871869e-6` | `2e-5` | `3.984481e-6` | `1e-5` |
| Ceil-edge oracle 1/2 → 1/4 refinement | `4.440892e-15` | `1e-9` | `2.163478e-15` | `1e-7` |

The high-frequency F04 family produces these maxima. L32→64 and L64→128
differences and observed orders remain in the report as characterizations;
passing the high-rate criteria does not give every lower factor the same grade.
All four kernels pass the frozen symmetry, support-endpoint, finite-normalizer
and DC checks. The report retains coefficient hashes, full response grids,
complete-output L256-minus-L128 residual DFT bands and tail energy.

The [independent A30 review](development/2026-11-15-execution-continuation/notes/A30.md)
and its [detailed receipt](development/2026-11-15-execution-continuation/reports/A30-study-review.json)
record **30,862 bounded assertions** on the first retained numerical arrays:
288 independently reconstructed metric sets, all 144 complete renders, 180
continuous 64-probe arrays, 657 physical edges, exact histories, fixture/probe
identities and resource accounting. A separate 65-digit sine-integral Fourier
calculation agrees with the 259 continuous response values within `4.45e-16`.
This review did not rerun the full matrix.

Root's [qualified numerical-identity receipt](development/2026-11-15-execution-continuation/reports/qualified-study-numeric-identity.json)
then confirms that all 36 final fixture records match that audited run except
the 144 per-factor elapsed-time observations. Samples, events, metrics, gates,
DFT/response values and coefficient records are unchanged. This connects A30's
independent numerical reconstruction to the repaired runner's fresh execution.

The separately named `ceil-edge-same-kernel-v1` experiment shifts physical edges
to `ceil(u)` while preserving source phase, the observation gate and the same
continuous kernel. Its refinement passes; its difference from fractional timing
is a diagnostic with no fidelity threshold. It is neither current Engine parity
nor an isolated physical alias measurement.

## Whole-process resources and relocated execution

The [48-file package manifest](development/2026-11-15-execution-continuation/reports/contact-package-v2.json)
records the installed bytes, original and moved prefixes, neutral working
directory and successful installed single-fixture command. The qualified study
then ran that moved package without using a source checkout as its runtime root.
Python was **3.12.14**, on **Linux x86-64**, with an **Intel Xeon Platinum 8573C**
reported by the host. These timings are observations of that environment, not
callback deadlines or platform-wide performance guarantees.

| Resource | Qualified observation | Frozen ceiling |
| --- | ---: | ---: |
| External wall, startup through child exit/publication | **21.728087337 s** | 300 s |
| Runner's internal interval | **21.633161134 s** | 300 s; external completion also checked |
| Exact-child terminal peak RSS | **36,974,592 bytes** | 268,435,456 bytes (256 MiB) |
| Conservative FIR product count | **159,847,056** | 180,000,000 |
| Oracle integrand evaluations, including responses/normalizers | **3,385,624** | 10,000,000 |
| Largest declared per-render work | **3,555,780** | 20,000,000 |
| Retained qualified report | **2,254,328 bytes** | 33,554,432 bytes (32 MiB) |

The internal timer excludes Python startup, final metadata encoding and atomic
publication. The external receipt includes them and uses
`os.wait4(exact_child_pid)` terminal `ru_maxrss`, converting Linux KiB to bytes.
It does not difference cumulative maxima from unrelated children. FIR work is
the conservative full-support count, not an instrumented CPU multiplication
count. Missing resident-memory evidence or any resource overrun would leave the
experiment incomplete.

The installed snapshot includes the guide/install documentation as it existed
at installation. Later explanatory documentation edits do not retroactively
change that 48-file snapshot. The numerical runtime scripts, frozen contracts,
fixture manifest and probes retain the exact identities below; the package
manifest remains the authority for its original documentation bytes. Results
and session reports are repository evidence outside the installed payload.

## Source and protocol bindings

The qualified report records every implementation file and fixture hash. The
relocated package has no Git checkout, so its report truthfully records Git
identity as unavailable. Its installation receipt names repository base
`33fa95d51e44234eef47ee21c03d29b2b311a5ee`; that base commit alone does not
identify the new uncommitted implementation. Explicit byte identities govern:

| Input or result | SHA-256 |
| --- | --- |
| Model contract | `3c05da4c3f35fcdc53fac05f1592ddc97e444f5038d9c147afae71f46e8deecd` |
| Validation protocol | `5ccbba4d08a2272bef4f7d553446a7ca9582e289fba80f9bcfa223a2d6efb2b5` |
| Numerical kernel | `fc269514eca98c05ee8fb14ff362248d140862cff942a250a01714bb06788e23` |
| Strict I/O | `e3219265f1496a36b4f5d8a13941672b46ddc4116f331b7a1b99115a2dac9dc6` |
| Single-fixture CLI | `46e1967af569e4a9ee35921439351e2ce5fe50c731a2619116cc9e424f4e97f5` |
| Independent continuous oracle | `17f6d93fb5d8fbb5eb1b0d36c609449f9c8b9b94e44ab10a80450f04bb2cf9d4` |
| Admitted study runner | `eb4d374cc46ed1c16448ab3b1c2f03c5714a27c20bfdd0c3dba6e005d8f8066e` |
| Fixture generator | `7e818b414342dfabfdcf23831fbb11ae4ccf51d093a4fd4cc97d046c6c73a387` |
| Fixture manifest | `b80db78bb8477b683bfd2cc1013a0b600c45e8f20b7fc08f75c5efe6e10a22ec` |
| Frozen probe file | `fdcdf6430c008cd28367d3c02f125af2a37ac55ebbe875361fba2549295e7026` |
| Qualified report | `87d7a5ba4dbc12d5d42754386c695ecbd046a61560dc75b5c86b17cc51121dba` |

## Retained first result and publication repair

The immutable [first report](development/2026-11-15-execution-continuation/reports/contact-study-v1.json)
and [first process receipt](development/2026-11-15-execution-continuation/reports/contact-study-v1-process.json)
belong to runner `223b56f9…`. They record **19.034880060 s** external wall,
36,806,656 bytes internal peak RSS and a 2,267,230-byte report. This is historical
evidence, not the repaired runner's final result.

During A30 review, an intermediate `a7b4d409…` runner still used `os.replace`
after a final freshness check. A deterministic interleaving demonstrated that
another experiment created at the destination could be overwritten between
that check and publication. The repair publishes a completely fsynced temporary
with atomic, non-overwriting `os.link`; unsupported filesystems fail explicitly.
The same race then raises `FileExistsError`, preserves the competing bytes and
cleans the owned temporary. Ordinary fresh publication also succeeds. A30
observed **14/14 focused tests in 0.499 s**, including late conflict and final
serialization-deadline cases, before admitting runner `eb4d374c…` for the fresh
full experiment above. All original reports and the defect remain recorded.

## Concrete next boundary

Design the causal streaming candidate separately. Freeze its latency and phase
convention, independent contact histories, complete filter state, bounded
work/allocation, block partitions, empty flushes, resets, rate changes and tail
semantics before grading it. The v1 study supplies a bounded reference at its
frozen probes; a later all-sample atlas `1e-4` claim first needs an independently
admitted full-window reference and complete response/resource evidence.

Keep physical acquisition separate: identify the specimen and obtain synchronized
gesture, contact, source and dry-output captures, with held-out evaluation and
uncertainty. Contact bounce/resistance, transformer loading, measured timing,
harmonics/leakage interactions, percussion and expression circuitry are outside
this fixed-load reference. Native/Engine integration and each platform's device,
callback and audio-fidelity claims retain their own acceptance gates.

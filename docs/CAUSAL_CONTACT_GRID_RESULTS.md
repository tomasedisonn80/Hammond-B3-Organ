# Causal contact grid v1: observed results

**16 November 2026 — the isolated integer-grid trajectory has source-bound
Linux numerical, lifecycle, transport and resource evidence.** Root's retained
[coherent gate](development/2026-11-15-streaming-continuation/reports/coherent-qualification.json)
passed **210/210 CTests in 191.89 seconds** after a 131-step all-target rebuild.
Its 505 code/test/tool/data inputs stayed unchanged during that run. This is
the original prepublication overlay above base
`4aac394cde4da40906b615573a8779aee2d9a37a`, before the A36 and EOF changes
listed below: GCC 14.2.0, Ninja Release, standalone/testing on,
MIDI/VST3/sanitizers off and SDL 2.32.10 dummy audio/video.

The [A36 integration finding](reviews/STREAMING_BUILD_INTEGRATION_REVIEW.md)
was repaired: missing or empty probe setup now fails both Python suites, and
the Upper-rack fixture is native sanitizer gate 22 with previous gates and
limits preserved. The [post-review full suite](development/2026-11-15-streaming-continuation/reports/final-coherent-qualification.json)
passes **210/210 in 191.90 seconds**, while
[eight negative setup cases and both configured suites](development/2026-11-15-streaming-continuation/reports/post-review-setup-qualification.json)
pass separately. The [publication-source receipt](development/2026-11-15-streaming-continuation/reports/publication-source-qualification.json)
records the sole source-byte change between that full run and implementation publication: one empty line removed at a resource
test's EOF, with an identical rebuilt binary and a passing affected CTest.
Original observations and inventories remain intact. Implementation `af2b747`
then the [Windows I/O repair](reviews/CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md)
`2f57723` are published. [All 13 repaired-source hosted jobs pass](development/2026-11-15-streaming-continuation/reports/hosted-2f57723-complete.json),
including Windows core 185/185. The I/O repair changes no trajectory code;
its two changed source/test files have a separate 3/3 affected local receipt.
The [checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md)
records completed worker closure and source-qualified publication history.

[Runnable guide](CAUSAL_CONTACT_GRID_GUIDE.md) ·
[Frozen contract](CAUSAL_CONTACT_GRID_CONTRACT.md) ·
[Independent contract admission](reviews/CAUSAL_CONTACT_GRID_ADMISSION.md).

## Exactness and admitted domain

`causal-contact-grid-v1` accepts integer values directly. Its nine independent
hysteretic contacts per key produce reduced rational crossing times, retain
command anchors across blocks, resolve incoming equality before commands and
preserve caller order for tied targets. Exactness covers this finite domain:

| Quantity | Limit |
| --- | --- |
| Rate and time | 44,100 / 48,000 / 96,000 Hz; 65,536 ticks per frame |
| Keys and thresholds | 1–4 keys, nine contacts each; integer `0 <= off < on <= 2^48` |
| Travel | Integer positions 0 through `2^48`; separate press/release speeds 1 through `2^32−1` position units per tick |
| Epoch | At most 4,096 frames and 512 supplied commands, including ties, no-ops and closure targets |
| Edges | At most 4,608 per call and per epoch, with fixed staging |

The earlier [binary64-input offline reference](FRACTIONAL_CONTACT_REFERENCE.md)
interprets admitted binary64 values as exact rationals for trajectory preparation,
then integrates switched sources and applies a centered, acausal finite filter.
The new grid supplies neither that audio path nor an implicit converter. Rounding
can change contact equality, order and bits, so exact grid replay does not prove
binary64-reference equivalence. The earlier
[36-fixture/four-factor result](CONTACT_SWITCHING_RESULTS.md) retains its own
source and limits: convergence over all 289 output samples, continuous admission
at 64 frozen probes per fixture, and no full-window atlas `1e-4` audio grade.

## What the evidence establishes

| Evidence | Observed result and scope |
| --- | --- |
| [A19 implementation review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md) | No blocking discrepancy in the unsigned arithmetic, reachable hysteresis states, endpoint ordering, persistent anchors, validation precedence, transactions or bounded traversal. Strict GCC syntax passed. This review itself ran no native behavior suite. |
| [A15 independent oracle](development/2026-11-15-streaming-continuation/notes/A15.md) and [A16 native known answers](development/2026-11-15-streaming-continuation/notes/A16.md) | Oracle: 18 methods. Native: ten groups of explicit edges and complete semantic snapshots, including extreme products, future roots, equality, partitions and full capacity. Both registered CTests passed in the coherent gate. The oracle constructs affine paths with `Fraction` without candidate crossing helpers. |
| [A21 differential](development/2026-11-15-streaming-continuation/notes/A21.md) | **11 methods / 199 native probes**, exact comparison of every edge and complete four-key padded snapshot across three rates, whole/single/irregular partitions, close distinct roots, future-prefix causality, limits and 24 seeded mixed cases. Registered CTest passed in 1.43 s. |
| [A22 lifecycle/rollback](development/2026-11-15-streaming-continuation/notes/A22.md) | Nine public-API groups cover phases, canonical fields, validation precedence, late invalid inputs, short-output retry, output-byte preservation, closure, reset and budgets. The later coherent native CTest supplies runtime acceptance beyond A22's original syntax-only handoff. |
| [A24 strict CLI](development/2026-11-15-streaming-continuation/notes/A24.md) | **17 methods / 150 processes: 19 successes and 131 exact rejections**, zero failures/errors/skips in its configured Linux run. Input limit 131,072 raw bytes; JSON ceiling 2 MiB. The corrected probe's coherent CLI CTest passed in 0.45 s. |
| [A27 Windows transport review](reviews/CAUSAL_CONTACT_GRID_PORTABILITY.md) | Guarded binary stdin setup prevents documented CRLF/Ctrl-Z translation from weakening byte admission. Linux regression passed in the coherent gate. [Initial hosted admission](reviews/STREAMING_INITIAL_HOSTED_ADMISSION.md) later observes all six causal suites passing on all four core jobs, including Windows; repaired `2f57723` passes Windows 185/185. Forced mode-failure execution remains unrun. The stdin issue was source-identified, distinct from the observed contact-reference install failure. Stdout may use CRLF. |
| [A23 resources](development/2026-11-15-streaming-continuation/reports/A23-resources.json) and [A28 independent admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md) | Independent reconstruction of instrumentation and 19 identities; normal/instrumented binaries reproduced original receipts byte for byte. See the storage/work limits below. |
| [A35 guide replay](development/2026-11-15-streaming-continuation/reports/A35-guide-smoke.json) | Existing and revised examples each exit 0 with empty stderr; all nine contacts close at tick 32,768 and the final key/block state matches. Raw Linux output is unchanged. This small positive control does not replace the other gates. |

The original [203/203 baseline, 192.21 s](development/2026-11-15-streaming-continuation/reports/baseline-qualification.json)
remains unchanged. A21's initial no-tests selection (exit 8), A21/A24's earlier
unset-environment skips and A28's corrected audit-helper newline assertion stay
in their original records. Successful configured runs do not erase those setup
observations. The subsequent fail-closed helper correction has the separate post-review
receipt above and is not attributed to the older inventory. Earlier reference-study
publication failures and repairs likewise remain in their
[original results](CONTACT_SWITCHING_RESULTS.md#retained-first-result-and-publication-repair).

## Storage, measured work and proof boundaries

On the measured Linux x86-64 ABI, `CausalContactGrid` is **113,056 bytes**:
800 bytes live state plus **112,256 bytes embedded scratch** (800-byte staged
snapshot, 4,608 × 24-byte staged edges and 36 × 24-byte interval edges).
Caller buffers, fixture backing, allocator overhead and compiler stack frames
are separate. Other ABIs may differ.

Each normal/instrumented resource run observes **192 API scopes**, zero hooked
allocations/frees, six successful 12-allocation/12-free calibrations,
14,040 edge assertions and 36 semantic snapshot assertions. The hook covers
the current thread's global C++ new/delete forms; it does not measure all
C/system allocation, other threads, locks, I/O or deadlines. Source inspection
supports absence of allocation, locking and I/O in the trajectory methods. Full semantic
arrays are not retained in the resource JSON; assertions and field-wise digest
`653c948373cd8d8d` bind its finite observations.

| Counted operation | Observed per-call maximum | Proved per-call ceiling |
| --- | ---: | ---: |
| Target validations / applications, each | 512 | 512 |
| Key position evaluations | 2,052 | 2,052 |
| Contact candidates | 18,378 | 18,468 |
| Reached roots / committed copies, each | 4,608 | 4,608 |
| Gcd normalizations | 36 | 4,608 |
| Euclidean remainders | 1,620 | 294,912 |
| Edge-order comparisons | 80,640 | 80,640 |

These are maxima across calls, not one aggregate trace or an observation of
every theoretical maximum. Incoming movements consumed earlier commands, so
`A+M <= 512` and at most nine edges per movement give the 4,608-edge limit.
At most 4,096 successful advancing calls and 512 commands give the separate
source-derived **165,888 contact-examination epoch ceiling**. Arbitrary retries,
rejections and empty calls have per-call bounds only. Counted operations and
fixed storage establish no callback deadline or indefinite-performance bound.

## Compatibility and source bindings

[A30's compatibility review](reviews/STREAMING_CONTINUATION_COMPATIBILITY.md)
preserves the original ContactBank/default dry Engine, 91 shared advancing
sources, 47 parameters, `B3CONTROLS4`/readers 1–3, plugin UUIDs and note/phase
ownership. It finds no Engine/adapter route to the research class. Original
PDF/art/data/fixtures and all 48 frozen `ContactReferenceTools` payload files
match base; the new probe is outside that installation component.

One matched 8,192-frame, 48-kHz dry render (block 64, seed 0, drawbars
888000000, note 60) has zero clipping and zero difference across 16,384 decoded
samples. The [A30 receipt](development/2026-11-15-streaming-continuation/reports/A30-compatibility.json)
retains commands, renderer/profile identities and both byte domains:

| Equal before/candidate bytes | SHA-256 |
| --- | --- |
| Complete WAV, 32,812 bytes | `35a460e99da4c9354e23ec13bb53a70c99f5cd5b70ecf337ec3926c422c7025d` |
| Decoded PCM, 32,768 bytes | `5ce533bce565ede2bd3e2744a1f3cd97aead5c8cd456f762d7dfb0e511e95f9c` |

The historical field `baseline_pcm_sha256` actually hashes the **whole WAV**.
Its original report remains intact; the separate decoded-PCM identity above
corrects the interpretation. One fixture is not universal audio equivalence.

| Stable grid input/result | SHA-256 |
| --- | --- |
| Frozen contract | `ba851e6af0601b52aef73d4b9effb64dffac3ef5e230eff7015e10e58a4ecb4e` |
| Public header | `69c655897b24688873472c559c952d9932f76b0cbed5c3eabd9a9da5b3a5d89f` |
| Production implementation | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |
| Corrected probe source | `265b3c3fd82d8fe5f2a2d09ea235ab54071686a66535f352352a0403d9a0f576` |
| Independent oracle | `3b16fbdb299a93806b3a626bd259f1f4649e042fd8f55b314c8eedb10c2b5a27` |
| Qualified Linux probe executable | `191c1179cf5fb6b2059498445651a6a81cc63161aececa8c248a981b0afb306d` |

The [coherent receipt](development/2026-11-15-streaming-continuation/reports/coherent-qualification.json)
binds the full compressed inventory and original configure/build/CTest logs.
A35 rechecked those raw hashes, the six grid CTest pass entries and the native
probe identity; its receipt records the audit-time input hashes. Later test-helper
edits require fresh qualification even when native executable bytes are unchanged.

## Next runnable checks and remaining work

Run the [guide's Python positive control](CAUSAL_CONTACT_GRID_GUIDE.md#build-and-run-the-native-probe)
against the existing executable. After a relevant source/test change, root can
build the selected native inputs and run the six grid CTests from the repository:

```sh
cmake --build ../build-native --config Release --parallel 3 --target hammond_causal_contact_grid_probe test_causal_contact_grid test_causal_contact_grid_lifecycle test_causal_contact_grid_resources
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error -R "^(python_)?test_causal_contact_grid"
```

The guide also gives clean-checkout presets and explicit direct Python probe-path
setup. Root retains the setup-correction receipts and completed coherent
qualification before publication; no broad suite was rerun for this documentation.

Next M3 work needs independently frozen conversion/rounding/collision and
contact-topology error policy, absolute source phase, partial-cell integration,
the proposed D=16 causal schedule, reconstruction filter/latency, 33-sample
nonempty drain and full-window continuous-reference audio grading. Full-organ
and indefinite capacity, Engine/standalone/VST3 lifecycle integration, host
callback resources/deadlines and synchronized physical contact/source/dry
acquisition remain separate gates. Bounce, resistance and tap loading are not
supplied by synthetic exactness. The implemented grid has published platform
qualification, while these next contracts remain unadmitted; see the
[reviewed next design](CONTACT_STREAMING_NEXT_DESIGN.md) and
[current next steps](NEXT_STEPS.md).

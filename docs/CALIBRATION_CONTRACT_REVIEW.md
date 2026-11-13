# Independent capture contract integration review

**Outcome:** the audio, corpus and comparison foundations are ready for their
separately assigned producers. Two narrow integration clarifications were raised,
applied by the root integrator and verified below. No remaining implementation
blocker was found in this bounded review. This is contract review and independent
literal arithmetic, not acceptance of implementations that have not yet run.

Review identity: `/root/cal_w2_a12`, calibration wave 2, assignment 12,
2026-11-13. The [assignment record](development/2026-11-13-calibration/12-contract-review.md)
retains the exact methods and ownership. The governing scope remains
[offline M0/M8 engineering](CALIBRATION_SCOPE.md), with capture metadata v1 and
the concurrent scanner, rotary and standalone scopes unchanged.

## Reviewed source identity

The checkout and locally recorded `origin/main` were both
`08fa8de8f718584c4ee4ab3b392c779f3290289c`, tree
`f5cff4b89d19f36a73f9d2a8ddb966db487f832c`, at initial inspection. The new
contracts were uncommitted working files; the commit alone does not identify
their reviewed contents. These are SHA-256 values of complete file bytes,
including Markdown whitespace and final newline, observed after the root edits:

| Reviewed file | Final reviewed SHA-256 |
| --- | --- |
| [Audio contract](CAPTURE_AUDIO_CONTRACT.md) | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| [Corpus contract](CAPTURE_CORPUS_CONTRACT.md) | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| [Comparison contract](CAPTURE_COMPARISON_CONTRACT.md) | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| [Shared JSON contract](CAPTURE_COMMON.md) | `5ae7a7fffb05829c8758d82ac74460ca14834acbe1fa4f2b6e4b1648623bb805` |
| `tools/capture_common.py`, used only for the numeric-limit probe | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| [Unchanged capture v1 contract](CAPTURE_FORMAT.md) | `618c20e4c6d2b204c69cdad006d69bfd93638de7c6d711b230452fea78b88177` |

The original authors' corpus hash
`b8f290b326be37fcf828bb1a80652379032e764553bd05c18d7c8640abdbd96d`
and comparison hash
`9be191da6491324d77ff88cd3d098671dd3765bd33b595b4cfae5940ff920e06`
remain correct identities for their earlier observations. They are not the
post-review identities above. This review did not fetch, commit or publish.

## Findings and verified resolutions

### C12-01: comparison reports need their own generic JSON numeric bound

**Integration defect, resolved.** The shared JSON helper defaults to a maximum
numeric magnitude of `1e12`. Comparison reports explicitly admit values through
`2e18`; a legitimate normalized error can exceed the helper default. For the
one-frame reference `math.nextafter(1e-12, math.inf)` and candidate `1e6`, with
the default floor, the normalized error is `9.999999999999999e17` on the reviewed
Python environment. Both input samples are admitted, and the reference exceeds
the floor.

An executed probe confirmed that `capture_common.validate_json_value` rejects
that metric under its default and accepts it with `max_number=2e18`. A producer
that reused the default report guard would therefore reject a valid result.

The minimal correction is now explicit in comparison section 7: callers using
the shared guard must pass `max_number=2e18`. Policy numbers retain their tighter
bound; the metadata helper's default remains unchanged. This does not authorize
relaxing exact schema types, node/depth limits, units or metric semantics.

### C12-02: corpus final purpose and comparison final role need an exact mapping

**Integration ambiguity, resolved.** Corpus purpose uses `final`; policy
`evaluation_role` uses `final_test`. Neither token should be renamed inside its
own schema, and v1 `held_out` alone cannot decide between development validation
and final assessment.

The root added the same explicit boundary mapping to corpus section 2 and
comparison section 10:

| Corpus purpose | Comparison evaluation role |
| --- | --- |
| `fit` | `fit` |
| `validation` | `validation` |
| `final` | `final_test` |
| `unassigned` | `unassigned` |

The later wrapper validates both declarations against this table. The auditor
and v1 validator do not rewrite them. Source inspection after the edit confirmed
the same mapping and preserved the separate chronology/independence gates.

## Cross-contract checks

| Area | Reviewed result and implementation consequence |
| --- | --- |
| Raw and derived metadata | Capture v1 digital geometry applies to raw acquisition only. Every raw file is selected for corpus audio mode. Derived audio uses its own descriptor, including explicit geometry for headerless float. Missing derived descriptors produce retained inconclusive coverage rather than borrowing raw metadata. |
| Admitted formats | Six audio representations are explicit. Legal v1 FLAC declarations remain valid metadata but fail a requested unsupported decode. Extensible WAV is explicitly rejected. Suffixes, ancillary chunks and calibration text do not select or override a decoder. |
| Canonical sample identity | Both companion contracts use the same version, 27-byte domain prefix, little-endian `<IIQ` geometry, frame-major `<d` samples and positive-zero canonicalization. Container/width differences may share a digest only when the normalized samples and geometry are exactly equal. |
| Byte versus decoded identity | File SHA-256 covers every original byte, including headers and padding. Decoded SHA-256 intentionally omits wrapper metadata. Expected manifest/artifact hashes remain distinct from observed hashes, and a structural audit cannot populate observed artifact hashes. |
| Graph and leakage | Sessions, v1 groups, declared gesture/family relations, ancestry, byte equality and selected decoded equality feed one transitive graph. Deterministic stars preserve connectivity without quadratic expansion. All raw/derived equality pairings count. Support-only equality is excluded, with its correlated uncertainty and potential change of scientific role retained as review obligations. |
| Independence limits | Missing labels, different hashes and different paths do not prove independent acquisition. A clean requested-mode graph retains `independence` and `final_holdout_history` as `not_established`. Unassigned or planned members remain inconclusive and cannot dissolve a known-purpose conflict. |
| Units and phase | Samples and absolute metrics remain dimensionless digital FS. No V/FS, Pa/FS or physical-clock conversion is implicit. Signed complex coefficients and exact supplied frequencies are retained; phase uses local frame zero, the declared window, explicit floor masks and `(-pi, pi]` wrapping. |
| Uncertainty and verdict | A metric-specific decision margin is distinguished from standard uncertainty. Unknown uncertainty and masked/undefined metrics remain inconclusive. Zero synthetic margins do not supply physical uncertainty. Every criterion is retained; a fail dominates undefined neighbors. |
| Hidden corrections | The array API compares supplied samples directly. Gain, lag search, phase fit, resampling and clock correction are absent. A later permitted shared gain/integer-delay wrapper must retain original and corrected comparisons, original intervals and exclusions; wider correction features need their own contract. |
| Bounded work | Audio bytes/chunks/samples, returned windows, corpus aggregates/edges/findings and comparison frame/frequency work have explicit inclusive limits. A future audio wrapper must use the intersection of window bounds: the audio API's 1,048,576 returned scalar samples is tighter than the array API's 4,194,304 per-side samples. No silent crop closes that difference. |
| Physical dependencies | Literal synthetic bytes and arrays suffice to implement and test this slice. No unavailable specimen, atlas companion, calibration, listening result or internal circuit measurement is required to begin the producers. Those inputs remain necessary for their separate physical claims. |

These checks are contract analysis. They do not assert that filesystem races,
maximum resource cases, decoder errors, graph construction or report admission
have already passed independently executed producer acceptance.

## Report identities and serialization boundaries

The contracts deliberately define different report surfaces. Audio CLI output is
compact JSON with ASCII escaping. Corpus CLI output uses sorted keys, two-space
indentation, unescaped Unicode and a final LF, matching the common canonical
encoding. The array comparison API returns a JSON-compatible value and requires
finite serialization; it does not yet define a CLI or a report-byte digest.
Do not route all three through one assumed wire encoding and silently change a
frozen CLI representation.

Policy identity is SHA-256 of exact admitted policy bytes, before any reserialization.
Index and manifest identities likewise bind the exact bytes parsed. Neither a
policy hash nor a later report hash attests chronology. There is no report
self-hash in these foundation schemas, so there is no recursive-hash ambiguity
to solve here. A later retained-report/replay wrapper must define its own exact
serialization, input/code identities and byte-hash scope before asserting replay.
That future work is explicit in the comparison contract; it does not block these
foundation producers.

The common helper supplies generic bounds, not every caller's complete contract.
Corpus and comparison callers still enforce exact key/type/unit rules and their
own tighter container/member limits. The audio window's maximum sample result
also exceeds the helper's generic node default, so a future caller must not assume
default JSON limits admit every successful audio-window value. The current audio
CLI serialization is specified independently and need not use that helper.

## Independent literal calculations executed

Python 3.12.14 standard-library calculations used literal bytes, `struct.pack`,
`hashlib.sha256`, and elementary `math` arithmetic. No audio decoder, comparison
producer or producer digest helper supplied an expected result.

| Executed check | Result |
| --- | --- |
| Audio vector A full WAV byte hash | Exact match: `5b56dc77fda85da22f9346b0d250c56bdf467a0d073bb07663db4f07702ed9ac`. |
| Audio vector A canonical decoded hash | Exact match: `6b650fe3f66cfaec1d3ad75b2a91716b3a1868a7a2d3d1b0cc9ebb1b4f641d55`. |
| A changed rate, swapped channels and mono/eight-frame hashes | All three exactly match the printed distinct hashes. |
| Audio vector C full raw byte hash | Exact match: `a537928ab210bdc28f972326557be866963cf75a254529433785b1c100814f46`. |
| Audio vector C canonical decoded hash | Exact match: `6125d66e14d8eba940491f56e21d047b507f10e75841605658432fc8c08cbb57`. |
| PCM16/24/32 edge-vector DC and RMS | All three printed pairs match the independent integer algebra `dc=-1/(5*q)` and `rms=sqrt((2*q*q-2*q+3)/5)/q`. |
| Sine reference / cosine candidate, rate 4, frequency 1 | Coefficients agree with `-0.5j` and `0.5` within trigonometric rounding; complex error is `1/sqrt(2)`, normalized error `sqrt(2)`, phase error `+pi/2`. |
| Four exact binary interval examples | Outcomes are pass, fail, inconclusive and inconclusive in the printed order; touching the limit at the lower endpoint remains inconclusive. |
| Shared JSON numeric boundary | Default rejection and explicit `2e18` admission reproduced for the valid near-floor ratio above. |

Seven printed hashes were checked exactly. The domain-prefix length was checked
as 27 bytes. These targeted checks verify the contract literals; they are not a
substitute for the independently assigned complete decoder, corpus and comparison
acceptance suites.

## Producer handoff

Proceed using the post-review hashes above. Implement the specified APIs and
errors, retain capture-v1 compatibility, and run independently authored acceptance
against the coherent implementation snapshot. Do not silently strengthen a
verdict because bytes, metadata or a numerical fixture pass. Later CLI/replay and
physical admission work must name its additional contracts and actual evidence.

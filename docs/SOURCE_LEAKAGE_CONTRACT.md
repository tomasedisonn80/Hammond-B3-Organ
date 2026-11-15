# Static source leakage: core and data contract v1

**Status:** admitted for implementation by the
[A10 independent review](reviews/SOURCE_LEAKAGE_CONTRACT_REVIEW.md), with its
recorded numerical/parsing clarifications. This is
the audio-continuation M2 contract; its integration contract owns Engine/headroom
and offline selection. No implementation or physical-fidelity pass follows from
this document. Source basis: unchanged atlas pp. 79–84, 369, 459 and 489; the
[complete reading notes](development/2026-11-15-audio-continuation/README.md)
retain coverage and the original PDF identity.

## 1. Boundary, equation and engineering limits

Model ID is **`static-source-leakage-v1`**. For one simultaneous 91-value frame,
`y[d] = x[d] + sum(gain[d,s] * x[s])`. IDs are one-based tone IDs 1–91;
array indices are zero-based. Positive gain preserves polarity and negative
gain reverses it. Gains are dimensionless normalized amplitude ratios, not dB,
calibrated volts, measured pickup coupling or physical generator adjacency.

Every term reads the original input frame. Bidirectional edges and longer graph
cycles are valid simultaneous matrix terms; there is no recursion, feedback solve
or second pass. The implicit diagonal is exactly one. Self-edges and duplicate
`(destination, source)` pairs are rejected, including opposite-sign duplicates.
The layer owns only explicit pre-contact generator coupling; it owns no source
clock, filter, contact click, hum, downstream idle feedthrough or acoustic leak.
Sources already containing coupling must not receive this layer again.

| Limit | Value and rationale |
| --- | --- |
| Source count | Exactly 91, preserving existing identities |
| Edges per destination / total | At most 8 / 728, bounding storage and work |
| Individual gain | Finite, nonzero, `abs(gain) <= 0.25` |
| Destination absolute-gain sum | Canonical binary64 sum `<= 0.5` |
| Input domain | All 91 values finite and in `[-1,1]`, including unused donors |
| Nominal stored-row bound | `1 + canonical_sum(abs(gain[d,s])) <= 1.5` |

These coefficient/capacity bounds are **chosen numerical support limits**, not
atlas measurements or recommended vintage settings. There is no normalization,
clipping, gain smoothing, rate-dependent coefficient change or omitted-edge noise.
An empty graph is identity; an unspecified physical coefficient remains unknown.
The exact mathematical bound is `abs(y[d]) <= 1 + exact_sum(abs(gain[d,s]))`.
The stored canonical sum can round slightly below that exact coefficient sum;
this admission roundoff and the evaluated products/additions can exceed the
nominal stored-row bound by a few ulps.
Consumers requiring `[-1,1]` need the integration contract's explicit input gain
and numerical headroom reserve; checking the mathematical endpoint alone is unsafe.

## 2. Core API and exact behavior

The intended public file is `include/hammond/SourceLeakage.h`; implementation is
`src/SourceLeakage.cpp`. Reuse `ToneId`, `kToneSourceCount` and `Status`.

```cpp
inline constexpr std::size_t kMaxSourceLeakageEdgesPerDestination = 8;
inline constexpr std::size_t kMaxSourceLeakageEdges = 728;
using SourceLeakageFrame = std::array<double, kToneSourceCount>;
struct SourceLeakageEdge { ToneId source; ToneId destination; double gain; };

class SourceLeakage {
public:
    Status prepare(std::span<const SourceLeakageEdge> edges) noexcept;
    Status process_frame(const SourceLeakageFrame& input,
                         SourceLeakageFrame& output) const noexcept;
    bool prepared() const noexcept;
    std::size_t edge_count() const noexcept;
    bool row_absolute_gain_sum(ToneId destination, double& value) const noexcept;
    double max_row_absolute_gain_sum() const noexcept;
};
```

Public constants name the 8/728 limits. `prepare` accepts input edges in any
order, validates every count/ID/gain/pair, and constructs a fully value-owned
candidate sorted by ascending `(destination, source)`. Within each destination,
its absolute-gain sum starts at positive zero and accumulates `abs(gain)` in
ascending source order using binary64. A failure returns `InvalidProfile` and
preserves every previous field, query and future output. Success installs all
candidate data together. Zero edges is a valid prepared graph. No caller buffer
is retained. Default construction is unprepared, not an undocumented graph.

`process_frame` first returns `NotPrepared` if appropriate, then validates all
input samples. Invalid input returns `InvalidBuffer` without changing output.
For each coupled destination, start `value = input[d]`, then perform
`value += gain * input[s]` in ascending source-ID order. There is no reassociation
into cascaded destinations or reduction ordered by caller input. Work is at most
91 input checks, 728 multiply/add terms and bounded frame copies. Standard
round-to-nearest binary64 with gradual underflow (FTZ/DAZ disabled), without
fast-math reassociation, is the numerical contract; exact cross-platform
bit identity of coupled arithmetic is not claimed.

Read every donor from `input`, build a separate fixed-size output candidate,
and publish only after the entire frame succeeds. Full input/output aliasing is
supported and gives the same result as separate arrays. The fixed-array API has
no partially overlapping-span mode. Uncoupled destinations are copied directly;
the empty graph preserves all valid bits, including signed zeros. Coupled zero
results need not preserve input zero signs. No oscillator or history advances.

Before preparation, `edge_count` and the maximum sum return zero;
`prepared()` distinguishes this from a prepared empty graph. A row query returns
false and leaves its destination unchanged for an invalid tone ID or unprepared
object; otherwise it returns the stored sum, including zero for an empty row.
Copying a prepared object preserves its exact value-owned configuration.

Prepare, process, queries and object copies use no dynamic allocation, locks,
I/O, logging or lazy initialization. Prepared object storage must be at most
32 KiB; per-frame scratch is fixed. Preparation/replacement is stopped-thread
work; concurrent mutation/publication is outside v1. Processing is immutable and
sample-rate independent. It is valid at every existing supported rate without
reseeding, and partitioning calls cannot change its stateless result.

## 3. Authoring JSON and compiler

The new authoring schema is `data/source-leakage.schema.json`; the standard-library
compiler is `tools/compile_source_leakage.py`. Its input is UTF-8 JSON, at most
256 KiB, without BOM, duplicate keys, nonfinite numbers or unknown members.
Reject booleans where integers/numbers are required; IDs are JSON integers.
These are the complete top-level members:

| Member | Exact v1 requirement |
| --- | --- |
| `schema_version` | Integer `1` |
| `profile_id` | 11–64 ASCII characters, prefix `synthetic-`, then `[a-z0-9][a-z0-9-]*` |
| `model` | `static-source-leakage-v1` |
| `evidence_status` / `coefficient_origin` | `synthetic` / `synthetic-fixture` |
| `boundary` / `units` | `normalized-generator-precontact-v1` / `normalized-amplitude-ratio` |
| `source_content` | `excludes-leakage` |
| `source_count` | Integer `91` |
| `algorithm_reference` | Object with exact members `document`, `sha256`, `pdf_pages` described below |
| `description` | Nonempty string, at most 512 characters, identifying the synthetic fixture |
| `edges` | Array of at most 728 exact `{source, destination, gain}` objects |

The reference object names `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`, and exactly
`[79,80,81,82,83,84]`. This cites the algorithm discussion; it does not attribute
the invented fixture gains or chosen limits to the atlas. The source-content
declaration is an explicit input assumption, not inspection of unseen recordings.

Validate the same pair/count/gain/row rules as native preparation after
canonical ordering. Row sums require explicit sequential binary64 additions
starting at positive zero, rounding after every addition, in ascending source
order. Do not substitute Python `sum`, `math.fsum`, decimal/exact accumulation
or a reordered reduction for this admission operation. Decimal-to-binary64
conversion must reject overflow and
nonzero values that underflow to zero, rather than silently dropping an edge.
Nonzero representable subnormal coefficients are allowed; ordinary floating
underflow during arithmetic is not repaired by clipping or fabricated noise.

Invocation is `python3 tools/compile_source_leakage.py --input FILE --output FILE`.
Hash the **exact input bytes** before conversion; use canonical order and
round-trip binary64 decimals in output. An existing output, including a symlink,
is refused. Validate completely before publication; failed validation leaves no
new output and preserves every input/existing file. The successful stdout JSON
receipt identifies input SHA, compiled SHA, model/profile/evidence/boundary,
edge count and maximum row sum. No output path or timestamp enters compiled data.

## 4. Native profile and compiled grammar

`SourceLeakageProfile` owns `profile_id` and `authoring_sha256` as zero-terminated,
zero-padded 65-byte arrays, an array of 728 `SourceLeakageEdge` values, and
`std::size_t edge_count`. Unused edge slots are ignored; loaders zero-initialize
them. Numerical preparation consumes only the declared span. Profile validation
also checks metadata, count and strict canonical ordering. Profile zero
initialization is intentionally invalid because required provenance is absent.

`load_source_leakage_profile(std::istream&, SourceLeakageProfile&, std::string&)`
and `load_source_leakage_profile_file(const std::filesystem::path&, ...)` return
bool, preserve the destination on any failure and explain rejection in the error
string. `validate_source_leakage_profile(const SourceLeakageProfile&) noexcept`
returns `Status::Ok` or `Status::InvalidProfile` without allocation. The loaders
may allocate and perform I/O, and are never called from processing.
An observed stream I/O failure is rejection even if bytes before that failure
contain an otherwise complete `end` record; clean EOF is not an I/O failure.

`kMaxCompiledSourceLeakageBytes` is `128 * 1024`. The bounded native text format
is at most that many bytes. These tokens appear exactly
once, in order; edge rows are strictly increasing by `(destination, source)`:

```text
B3LEAKAGE1
model static-source-leakage-v1
profile_id synthetic-pair-demo-v1
evidence_status synthetic
boundary normalized-generator-precontact-v1
source_content excludes-leakage
authoring_sha256 <64 lowercase hexadecimal characters>
source_count 91
edge_count 2
edge destination 25 source 37 gain 0.0625
edge destination 37 source 25 gain -0.03125
end
```

The example digest placeholder is not a valid file. The declared count must
match exactly. After `end`, only ASCII whitespace is allowed. Token separation
uses the existing six ASCII whitespace characters; CRLF is accepted. Reject
comments, embedded NUL/non-ASCII bytes, unexpected/duplicate/truncated records,
unknown version/identity, malformed digest, oversized input and trailing data.
IDs/count use unsigned decimal digit tokens; gains use the repository's strict
decimal grammar, finite/range handling and at most 128 bytes per numeric token.
Reuse `detail::parse_decimal`; hexadecimal, NaN and infinity forms are invalid.

The loader retains the author digest as **provenance supplied by the file**; it
cannot verify absent JSON or authenticate the file. The compiler receipt or a
later verifier can compare real author bytes. A changed authoring order can have
a different author SHA while compiling identical edge arithmetic. No existing
`B3CONTROLS4`, profile format, 47 sound parameter or plugin identity changes.

## 5. Independent acceptance before delivery

Freeze these criteria before examining final production output. Retain actual
source/data identities, commands and failures; the contract alone passes none.

1. **Algebra:** empty graph/uncoupled rows preserve exact bits; power-of-two
   one-edge cases are exact. Compare arbitrary signed sparse graphs with an
   independently written dense/original-frame reference. Per-sample tolerance is
   `32 * epsilon(double) * max(1, abs(reference))`. Include coherent cancellation,
   bidirectional edges, a three-node chain that must not apply `C*C`, all 91 rows,
   maximum 728 edges and shuffled equivalent author order.
2. **Admission and failure:** cover all boundaries, ninth incoming edge, 729th
   edge, duplicate/self/invalid IDs, gain zero/NaN/Inf/out-of-range, excessive row
   sum and invalid inputs even when unused. For destination 91 and ascending
   sources 1-8, gains `[0.25, six copies of 2^-56, 0.25]` have canonical stored
   sum `0.5` and must be admitted. Gains `[six copies of 2^-56, 0.25, 0.25]`
   have stored sum `nextafter(0.5,+infinity)` and must be rejected. These are
   different donor assignments; shuffling each input list must preserve its
   own canonical outcome. Verify previously prepared behavior
   and sentinel output survive every rejection; cover in-place aliasing.
3. **Data path:** round-trip actual compiler output through the native loader;
   verify coefficients, order, exact input hash and receipt. Mutate each grammar
   field, count/order, truncation/trailing bytes, byte limit, decimal underflow,
   malformed/duplicate JSON, underlying stream I/O failure and output collisions.
   A forged digest must never
   be described as verified author bytes.
4. **Signal behavior:** use 1,024-frame coherent-bin synthetic source sinusoids
   at 44.1, 48 and 96 kHz, with source bins 7, 31 and 97 and finite input
   amplitudes at most 0.5. Use `Z[k] = (2/N) * sum(y[n] * exp(-j*2*pi*k*n/N))`
   for positive non-Nyquist bins, with no window. An independent oracle derives
   the expected complex coefficients from the known input phases/amplitudes and
   signed gains, rather than copying the sparse output. Inspect bins 1-511;
   preserve DC and Nyquist as separately normalized `1/N` checks. Record the
   specific edge graph, recipients and input phases before the production run.
   Measure signed donor amplitude and phase at selected recipients,
   and verify no unprovided frequency component beyond a `1e-12` absolute DFT
   amplitude residual for normalized fixtures. This is static linear coupling,
   not measured leakage. Preserve original phases and frame order through
   silence and partitions in the separately tested Engine integration.
5. **Resources and lifecycle:** observe zero allocations/deallocations in core
   prepare/process/query/copy paths, maximum-capacity state and bounded frame
   work. Report actual timing with workload/compiler/hardware; do not infer a
   callback deadline from arithmetic counts. Ordinary copying/reprepare must
   have no stale pointers. Engine headroom, contacts, default compatibility,
   explicit CLI selection and source manifests require their own integration
   evidence before audible publication.

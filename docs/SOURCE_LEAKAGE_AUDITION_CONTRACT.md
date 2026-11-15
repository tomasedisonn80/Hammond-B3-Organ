# Source leakage: Engine and offline audition contract

**Version:** `source-leakage-audition-v1`, 15 November 2026. Independently
admitted with A12's absolute-underflow and outward-rounding correction in the
[contract review](reviews/SOURCE_LEAKAGE_AUDITION_CONTRACT_REVIEW.md). This
does not claim implementation or production-test completion. The
[core/data contract](SOURCE_LEAKAGE_CONTRACT.md) owns
`SourceLeakage`, its profile grammar and numerical limits. The
[audio-continuation checkpoint](development/2026-11-15-audio-continuation/CHECKPOINT.md)
owns subsequent implementation and acceptance.

## 1. Purpose and unchanged boundaries

Provide an intentional offline organ audition of the static synthetic coupling
described by atlas pp. 79-84, 452, 459 and 489. Apply the layer once to the shared
91-source frame before manual, percussion and pedal routing. It is dimensionless
generator-source coupling, with no new oscillator, filter, noise source or
downstream idle-feedthrough path. A closed destination contact can expose a donor
whose own key is not held; opening all destination routes makes this pre-contact
contribution inaudible. Source phases continue in both cases.

Preserve the default ideal-sine Engine, its nominal profile and authoring digest,
47 musical parameters, `B3CONTROLS4`, readers 1-3, and ordinary event meanings.
Leakage selection and its explicit input gain are stopped preparation settings,
not saved controls, automation or a new host/UI feature. Standalone and VST3
continue using their existing default preparation unless separately assigned.
This phase does not connect the scanner, AO-28 or Leslie, or establish measured
coupling. A future source recording that already contains this coupling cannot
receive the same layer again.

## 2. Exact signal order and headroom

For the one selected source frame `x[n]`, with each sample in `[-1,1]`, define:

```text
u_i[n] = input_gain * x_i[n]
y_i[n] = u_i[n] + sum_j(c_ij * u_j[n])
```

The core contract fixes the second line's canonical order and original-input
semantics. All manual sustain, upper percussion and pedal branches consume the
same `y[n]`. Do not apply the gain again at output, separately to each voice, or
inside the leakage coefficient data. Contact/percussion/source advancement still
occurs once per positive sample, including silent and disconnected rendering.
Zero-frame controls neither evaluate the layer nor advance any clock.

`input_gain` is a caller-selected finite value in `[0,1]`. There is **no automatic
normalization, clipping or gain reduction**. A comparison against an empty graph
uses exactly the same explicit gain; changing gain is a separate audible change.

The existing `PedalBusKernel` rejects even one source outside `[-1,1]`, including
an unused source. Do not widen that domain or ignore a possible failure. Let `R`
be the prepared core's maximum canonical binary64 row absolute-gain sum,
`epsilon = std::numeric_limits<double>::epsilon()`, and
`eta = std::numeric_limits<double>::denorm_min()`. Admission is:

```text
empty graph:       require 0 <= input_gain <= 1
                  guarded_bound = input_gain
nonempty, gain 0:  guarded_bound = 0
nonempty, gain>0:  row_bound = (1.0 + R) + (64.0 * epsilon)
                  product_bound = input_gain * row_bound
                  guarded_bound = nextafter(product_bound + (16.0 * eta), +infinity)
                  require finite(guarded_bound) and guarded_bound <= 1.0
```

Validate the finite `[0,1]` gain before these branches. Use the written grouping,
binary64 round-to-nearest arithmetic with gradual underflow, and no fast-math
reassociation. The relative reserve covers the at-most-eight gain products and
additions and rounded row sums. The absolute `16 * eta` allowance covers
gradual-underflow rounding, and `nextafter` rounds the assembled bound outward.
These are engineering margins, not physical uncertainty. A relative reserve
alone is insufficient: with gain `9 * eta`, eight gains of `1/16`, and all
sources equal to one, it reports `14 * eta` while the canonical output is
`17 * eta`. The corrected bound is `31 * eta`. The independent review retains
this counterexample, a bound argument and normal-boundary neighbor evidence;
implementation tests must still verify the actual core and pedal path.
Do not admit a nonempty graph solely because a rounded mathematical
`input_gain * (1 + R)` equals one. With the core's `R <= 0.5`, an explicit gain
of `0.5` is a conservative valid example for every admitted graph.

An empty graph with gain `1.0` bypasses both multiplication and sparse
accumulation. This preserves legacy samples and signed zeros exactly. An empty
graph at another gain intentionally scales the source field. Gain zero is an
explicit silent experiment; source and console histories still advance.

## 3. Stopped Engine API and lifecycle

Add these independent API names; the core/data owner retains its own types:

```cpp
struct SourceLeakageConfiguration {
    bool configured{false};
    double input_gain{1.0};
    std::size_t edge_count{0};
    double maximum_row_absolute_gain_sum{0.0};
    double guarded_output_bound{1.0};
};

Status Engine::set_source_leakage(const SourceLeakage& prepared_leakage,
                                  double input_gain) noexcept;
Status Engine::clear_source_leakage() noexcept;
SourceLeakageConfiguration Engine::source_leakage_configuration() const noexcept;
```

All three require stopped or same-processing-thread access, without concurrent
processing. Installation/clear are **not audio-callback operations**, have no
crossfade/de-click promise and do not provide live publication/retirement.
Before the first successful preparation, the query returns the struct defaults.

Installation validates everything before copying the prepared numerical module
and scalar into owned fixed storage. It retains no caller pointer or span. Error
precedence is `NotPrepared` for an unprepared Engine; `InvalidSpec` for a
nonfinite/out-of-range gain; `InvalidProfile` for an unprepared leakage module;
then `InvalidSpec` for failed headroom admission. Every rejection preserves the
complete Engine and its future samples, including an earlier leakage selection.

Success changes only this configuration. It preserves the selected source bank,
all phases, controls, held keys, contact trajectories, percussion readiness,
frame clock, coefficient caches and last-rendered pedal diagnostic. That last
diagnostic remains historical; installing a setting cannot relabel it as a newly
rendered frame. `configured` is true even for an explicitly selected empty graph
at gain one, while the actual arithmetic can still use the identity bypass.

Clear returns `NotPrepared` before preparation; otherwise it restores the
unconfigured/gain-one bypass and default configuration facts without advancing
time or changing other state. Repeated clear is an exact no-op. Each successful
ordinary `prepare` clears this optional configuration; a rejected prepare retains
it. Successful selected-source preparation also clears it once that separate
API is integrated. Rate reconfiguration preserves the layer, gain and continuous
source phase; a failed or same-rate transition retains its existing semantics.
Restoring musical controls never installs, removes or serializes leakage.

The processing path uses fixed arrays and the prepared module only, with no
allocation, deallocation, file access, locks, logging or metadata parsing. The
admitted source and headroom invariants must make core/pedal failure unreachable
for valid Engine inputs. Qualification must exercise the actual downstream
pedal result; accepting an ignored `InvalidBuffer` is a defect. Do not introduce
a mid-block rejection after advancing sources as a substitute for admission.

## 4. Harmonic-source integration boundary

Read-only inspection of the concurrent playable owner's local commit
`3622651d248ea13de4bccc32fb2c2043fb3db53d` found
`Engine::prepare_harmonic`, `SourceSelection`, `--harmonics` and render-summary
schema 4. Its `HarmonicTonewheelBank` contract bounds actual emitted samples by
`[-1,1]`; the selected source branch already produces one shared frame.
This observation is not publication or acceptance of that owner's work here.

Integrate a published/accepted harmonic change through the integrator before
modifying its branch. Insert leakage **after** the one sine/harmonic selection
and **before** every consumer. Preserve the owner's selection, term suppression,
phase diagnostics, bound and rate policy. Clear leakage on a successful
`prepare_harmonic` just as on ordinary `prepare`; failed preparation retains it.
No second source bank is evaluated merely to obtain leakage donors.

The named synthetic harmonic model contains no separately modeled leakage and
can share this normalized boundary after combined tests pass. A future measured
source model needs an explicit effect-ownership admission before composition.
If harmonic source has not yet been integrated, complete sine-path acceptance
and retain combined-mode gates as unrun; do not import another owner's dirty
files or claim combined support from source inspection alone.

## 5. Offline interface, input protection and receipts

Add two value-taking `hammond_render` options:

```text
--source-leakage FILE
--leakage-input-gain GAIN
```

Require them together, exactly once each. Missing/duplicate/oversized arguments,
unknown switches and nonfinite or out-of-range gain reject before output
creation. Use the existing strict finite-decimal machinery with a gain-specific
error; do not accept trailing junk or localized decimal syntax. Existing options
and defaults retain their behavior.

Resolve the graph through the existing regular-input/canonical-path policy,
enforce the core contract's compiled-byte limit, and load it through
`load_source_leakage_profile_file`. Prepare its numerical module off processing,
then prepare the selected source Engine and install leakage before initial
zero-frame controls. Every input and headroom failure must precede temporary WAV
creation. Add the graph to the complete output-versus-input collision check,
including canonical aliases. Preserve existing-file, dangling-output-symlink,
hard-link publication and `--fail-on-clip` behavior. No graph, score, profile or
existing output may be modified by a successful or failed audition.

The CLI owns profile metadata outside Engine. It retains the selected profile ID,
declared authoring SHA-256 and core identity from the admitted compiled data.
The supplied author digest is provenance, **not verification of absent JSON**.
The retained acceptance bundle must separately hash the actual JSON, compiled
bytes, executable and score, and bind the compiler result to those bytes.

When neither leakage option is present, preserve the exact old summary shape:
schema 3 for sine and the harmonic owner's schema 4 when applicable. When
leakage is selected, emit `render_schema_version: 5`, preserve every applicable
base/harmonic field, and add:

| Field | Required meaning |
| --- | --- |
| `source_leakage_model` | `static-source-leakage-v1` |
| `source_leakage_integration` | `source-leakage-audition-v1` |
| `source_leakage_profile_id` | Admitted synthetic profile ID |
| `source_leakage_authoring_sha256` | Declared original JSON digest |
| `source_leakage_evidence_status` | `synthetic` |
| `source_leakage_boundary` | `normalized-generator-precontact-v1` |
| `source_leakage_source_content` | `excludes-leakage` input requirement |
| `source_leakage_input_gain` | Actual admitted explicit scalar |
| `source_leakage_edge_count` | Actual prepared edge count |
| `source_leakage_maximum_row_absolute_gain_sum` | Actual prepared `R` |
| `source_leakage_guarded_output_bound` | Admitted guarded bound, or gain for an empty graph |
| `source_leakage_identity_bypass` | True exactly for empty graph plus gain one |

Keep `model` identifying the selected source bank, not replacing it with the
coupling identity. Report finite numbers with `max_digits10`. A version-aware
leakage acceptance reader must check these fields and their consistency;
legacy retained-render verifiers must not be made to silently treat schema 5 as
their older fixture schema. Final PCM clipping remains independently reported:
the per-source bound does not guarantee a polyphonic output below full scale.

## 6. Acceptance fixed before implementation

| Gate | Required evidence |
| --- | --- |
| L-A1: unchanged path | On the same source/toolchain, compare default and empty-graph/gain-one Engine output bitwise, including signed-zero cases, all rates, manuals/pedals/percussion, silence/disconnected periods, zero-frame commands and different block partitions. Preserve legacy CLI WAV bytes and schema-3 summary fields; repeat harmonic schema-4 cases after that owner is integrated. |
| L-A2: real signal boundary | Independently derive a one-edge waveform from the unchanged source bank, explicit gain and dense original-input equation. Close only the contaminated destination route, keep the donor's own key released, then open/cancel that route. Verify the donor contribution, polarity, no unintended feedback and continued source phase. Exercise upper/lower, both pedal mixtures and eligible percussion through actual Engine output/diagnostics. |
| L-A3: numerical admission | Reject nonfinite/out-of-range gains, unprepared modules and unsafe headroom transactionally. Test the representable boundary and adjacent values, every full incoming-row case with aligned signs, maximum-capacity graphs, tiny gains, the retained `9 * eta` underflow case and gain zero. Require every actual contaminated magnitude to be no greater than the admitted `guarded_output_bound`, all samples within `[-1,1]`, and the real pedal kernel to return `Ok`; no tolerance outside these bounds. |
| L-A4: lifecycle | Cover replacement and clear with retained keys/contact motion/percussion readiness, same/new/invalid sample rates, successful/failed ordinary preparation, saved-control restore and original last-pedal history. Compare future samples to an untouched control after each rejected operation. Run corresponding harmonic cases when integrated. |
| L-A5: CLI/data safety | Test paired/duplicate/missing flags, strict decimal failures, malformed/oversized graph, wrong metadata, output collision/alias, existing output, write/publication failure and fail-on-clip. Hash all original inputs before/after and require no published WAV for rejected setup. Check exact schema-5 facts against the admitted graph and gain. |
| L-A6: audible/source evidence | Retain one nonempty synthetic graph and its empty-graph comparison at the same gain, seed, events and rate. Use coherent-bin numerical fixtures for expected donor magnitude/phase and explicit unaffected destinations; label demonstration listening as synthetic and distinguish it from measured audio. Preserve source/data/executable identities and actual commands. |
| L-A7: bounded processing | Instrument the changed Engine path for no callback allocation/free; inspect fixed storage and per-sample bounds. Measure optional-path cost separately from baseline at declared workload/toolchain. A bounded result or local timing is not an actual host audio-deadline pass. |

Use the core contract's numerical tolerance for sparse-versus-dense evaluation.
The independent Engine oracle accounts for known coherent route weights,
existing output gain, shared expression and final float conversion. For that
pre-PCM waveform comparison, require absolute error no greater than
`8 * epsilon(float) * max(0.001, abs(reference))`; this is a selected engineering
tolerance, not a specimen-audio threshold. One-edge dyadic fixtures also require
the expected exact unaffected/zero branches. Coherent-bin Engine spectral
fixtures require complex coefficient error and inspected unexpected-bin magnitude
at most `2e-7` normalized amplitude after float conversion; record the inspected
bins and DFT normalization. Apply no window to these bin-coherent fixtures.
For unclipped PCM16 output versus the independently quantized reference, allow
at most one integer quantization step per channel sample. Identity/default PCM
comparisons remain byte-exact. Do not relax these criteria after observing a
failure; any changed contract needs a retained reason and new independent review.
Record all unrun/blocked combined-mode and physical gates explicitly. This
audition does not complete M2 physical fidelity, M3 contact bandwidth, M5-M8,
whole-interface equality, native accessibility or product release.

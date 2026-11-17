# P1 comparator — independent source and oracle admission

Reviewer **A22**, `/root/w04_a22`, wave 4, 17 November 2026 UTC. This review
covers the frozen A17 comparator, its focused tests, the unchanged native
fixture, the [P1 contract](../design/PERFORMANCE_PLATE_P1_CONTRACT.md), the
[A11 design admission](PERFORMANCE_PLATE_P1_DESIGN_ADMISSION.md), and root's
[original paired v1 report](../development/2026-11-16-console-completion/reports/p1-paired-v1/report.json).
The [review receipt](../development/2026-11-16-console-completion/reports/A22-comparator-review.json)
retains identities, the failure diagnosis, executed Python results and limits.

## Decision and exact scope

**ADMIT the narrowly corrected comparator for root's new paired v2 execution.**
The original v1 result remains **failed**. Its four failures came from one
incorrect expectation about remembered workspace focus, present on both the
genuine baseline and candidate sides. This review does not replace that result
with a pass and does not execute a new native comparison.

Root authorized the precise correction after receiving the source-derived
diagnosis. The only comparator behavior change removes the assignment of a
Workspace tab to an untouched workspace's remembered body-control slot. The
visible tab focus, all three remembered slots, complete copied state, matrix,
pixel support and every numerical criterion are still checked exactly. A
source-semantic comment explains the corrected expectation. Five independent
regression methods were added to the Python tests.

| Source | SHA-256 |
| --- | --- |
| Original A17 comparator | `ca0aea0a4609848ef7927558c22d76bfe0ced9efdd59b554b6126d0a8d92a1fa` |
| Original A17 tests | `8f9fafee6e5a18f7fa5df27133e5add1bfdf60f971b79e132353d49ba6b45024` |
| Corrected comparator | `e7a810e21099e346ec4ab86097cba6552cde497fcfd22be659907efeb2c80344` |
| Corrected tests | `b368e9277b306c807672acfa1b200c4fc4eda358c03b3e4e9b3bfe90b21af526` |
| Unchanged native fixture | `4f1875270af71d08c27372944a4a9c8e4c10b6c31dbeb85b3841b6965915956c` |
| Unchanged P1 contract | `20c8839d38229bf24d983eac0baad7381f601c4e6763bbbe556bcdfa6c75ae45` |
| Genuine-before fixture executable used in v1 | `65d0cc74e53faf2d655cba5f6254d5087715c730f22556ec81940195ad18149e` |
| Candidate fixture executable used in v1 | `846f9c1a239243644194bae40a90b555236c255993722b0717fbc1ba5a80018c` |
| Genuine-before painter | `10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366` |
| Candidate painter used in v1 | `8ca5c05138ed4cd12fe8ef416ea35a3d78a8a3c4915645f53d8c0c0df2fcf927` |

The original untracked source bytes were copied **before editing**, then
retained exactly as
[A17 comparator source](../development/2026-11-16-console-completion/reports/source-history/A17-compare_performance_plate.py.txt)
and [A17 test source](../development/2026-11-16-console-completion/reports/source-history/A17-test_compare_performance_plate.py.txt).
These are original byte snapshots, not later reconstructions. A17's note and
test receipt remain unchanged. The painter, native fixture, model, font,
Drawing, thresholds and original paired artifacts were not edited by A22.

## The workspace-focus defect

The source of truth is the unchanged
[`UiModel::focus_control`](../../apps/standalone/UiModel.cpp), together with
`UiModel::set_workspace` and the frozen fixture's `state_for` sequence.
`UiModel.cpp` has SHA-256
`0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd`;
`UiModel.h` has SHA-256
`6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1`.
Both current files exactly match their bytes at starting HEAD
`9d60dbf462a90fe422fd4e69757fe202264acb7c`.

`focus_control` always assigns `view.focus`. It writes `workspace_focus` only
when the focused control is visible **and is not a Workspace tab**. A fresh
model initializes every remembered slot to `UiControlKind::None`. The fixture
sets the copied session and edited B banks, traverses ordinary Tab focus in
Play to the requested Upper B drawbar, then calls `set_workspace` once. For
Rotary and Service, no body control has been remembered, so `set_workspace`
selects the respective visible Workspace tab. That selection does not populate
the remembered body-control slot.

| Main case | Visible `focus` | Exact `workspace_focus` |
| --- | --- | --- |
| 22, Rotary | `[20,0,0,1]` | `[[4,0,1,4],[0,0,0,0],[0,0,0,0]]` |
| 23, Service | `[20,0,0,2]` | `[[4,0,1,4],[0,0,0,0],[0,0,0,0]]` |

All four retained before/candidate streams show those values both before and
after painting. The genuine-before streams independently supply the regression
inputs; candidate bytes do not supply their expected values. The original
comparator instead assigned `memory[workspace] = focus`, contradicting the
unchanged public model's explicit exclusion of Workspace tabs.

The smallest correction is deletion of that conditional assignment. Replacing
the model, fixture, genuine baseline, visible focus or preservation rule would
be incorrect. No case is removed and no metadata field is ignored.

The new tests pin each genuine-before stream's compressed size/SHA-256 and
raw size/SHA-256, limit decompression to 6,560,395 bytes for a required
6,560,394-byte stream, reject trailers, and read a bounded JSON header. They
assert literal expected focus and all remembered slots before calling the
comparator. Four valid model moments are admitted. Twelve mutations are
rejected: remembered workspace tabs, erased or changed Play memory, fabricated
memory in the other unused workspace, and incorrect visible focus.

Running just those five methods against the preserved original A17 comparator
produces four errors for valid model moments and two failed refusal subtests
because the incorrect remembered-tab states are accepted. Against the corrected
comparator, the entire focused suite passes **30/30 methods in 0.878 seconds**.
This establishes both admission of the real fixed state and refusal of the
specific false state that the original oracle expected.

## Independent support and preservation audit

[`scenarios`](../../tools/compare_performance_plate.py) transcribes the frozen
24 main cases, five uncut companions, two repetition witnesses and three
applied-route witnesses. Both `--list` responses must match the complete literal
34-record inventory. Each exported frame must match its fixed scenario and
output size; final matrix checks require 34 pairs, 68 frames and ten
side-specific companion comparisons. A missing, duplicate or altered scenario
cannot produce a successful complete result.

Support is computed from the comparator's own canonical panel and inset,
binary32 public endpoint operations, center-based device boundaries
`ceil(edge * scale - 0.5)`, viewport translation, physical caller clip and
output intersection. The exported inset and witness spans are checked against
these independent calculations; they never supply the permission mask. No
candidate color, candidate material function or observed difference selects
support. The numerical implementation does not reproduce the production P1
field or grain.

The comparison checks every RGBA byte outside that support. Fallback cases 8
and 9, empty/disjoint cases 14 and 15, and inactive cases 17–23 require complete
frame equality. The maximum-domain 64×64 crop has **zero protected exterior
pixels**; its result is correctly bounded to resource-crop evidence. It cannot
establish full-domain exterior containment.

There are 19 independent opaque probes covering rule segments, all four
percussion caps, expression track/handle, both pedal tracks/caps, divider and
four screws. Each required full-frame probe must be nonempty and opaque. The
paired path additionally compares its complete RGBA against the genuine
baseline. Per-side opacity alone is not described as paired color preservation.

Seventeen literal text runs bind text, face, placement, requested/actual size,
padding, color, destination envelopes and opaque cores. The comparator decodes
the pinned font RLE directly and reconstructs float32 glyph positions. Its
sampling follows the inspected pinned Drawing and SDL 2.32.10 software COPY
path: integer destination extents, clipped-source rounding, output-crossing
intermediate surfaces and seven-bit interpolation coordinates. It selects only
exact alpha-255 cores, then checks their actual literal RGBA and paired RGBA.
The full-frame cyan scan verifies every exact focus position and excludes extra
cyan pixels, rather than checking a count alone.

The scalar SDL filter rounds vertically and then horizontally; some SIMD
interior paths retain additional precision. For the exact-alpha-255 predicate
used here, their nonnegative interpolation weights yield the same criterion:
every contributor with nonzero weight must be 255. This audit does not claim
that the comparator reproduces every antialiased alpha value on all backends.

Only glyph destination envelopes are excluded from cut-versus-uncut quiet
material comparisons. That exclusion does not enlarge the paired exterior
support or exempt opaque glyph cores. All four edge-clip quiet domains are
nonempty; the disjoint domain is explicitly zero. Repeats compare actual RGBA
and complete records, not only exported hashes. The frozen native history
sequence exercises 32 other states/transforms on one renderer before restoring
case 0, and the fresh witness creates a separate renderer.

Complete copied desired controls, applied session, view state, layout, 147 key
records, 68 control records including 24 presets, hit observations, workspace
memory, fixed information and renderer records are compared around paint and
across binaries. The sole paired metadata exclusions are the expected helper
`present` and `invoked` flags. A separate direct helper observation preserves
incoming color and renderer state; the later whole-frame painter cannot hide a
helper leak. The checked painter diff leaves existing child/text operations and
their arguments unchanged. Witness metadata is an independent expectation,
not instrumentation of each production drawing call.

## Numerical equations, transport and identity audit

For each fixed half-open rectangle, `patch_measure` independently accumulates
integer RGB and encoded-luma sufficient sums. Write
`z = 2126R + 7152G + 722B`, `X = 2x-(w-1)` and `Y = 2y-(h-1)`.
The rectangular grid makes `1`, `X` and `Y` mutually orthogonal. The population
residual mean square is therefore exactly

```text
(sum(z*z) - sum(z)^2/N
          - sum(X*z)^2/sum(X*X)
          - sum(Y*z)^2/sum(Y*Y)) / (N * 10000^2).
```

The code evaluates that expression with `Fraction`, rejects a negative result,
converts once to binary64 and applies `math.sqrt`. Mean-Y and RGB decisions are
rational. All twelve patch domains/order and all 62 screens remain frozen.
The equal-patch mean threshold is exactly
`6324946007329 / 2837721600000`; RMS errors use the required fixed-order
`math.fsum(errors) / 12.0` and threshold `0.6968632531987865`. The existing
affine-zero, nonaffine, contradictory-statistic and historical-decision tests
pass. A22 inspected these equations and the admitted reference provenance; A22
did not newly decode the source artwork or replace A11's image-statistics audit.

Transport rejects duplicate JSON keys, NaN/infinities, wrong frame structural
integer types, wrong case/packing/stride/dimensions, truncated RGBA and trailers.
Malformed input cannot be promoted to admission: structural failures leave
failed audit records or a failing execution and incomplete-matrix result.
Tests exercise these parser refusal paths. Required metadata keys and native
assertion flags are validated, and independent pixel/state checks supplement
the fixture's own assertions.

The source bounds every subprocess output, stores both stdout and stderr
exclusively, and retains a clearly identified prefix if an output ceiling is
exceeded. The limits are a header below 2 MiB, at most 3866×2194 RGBA pixels,
64 KiB stderr, 70 commands, 160 files and 2 GiB of stored artifacts. The
per-process deadline defaults to 60 seconds and is capped at 120; the
process-start/remaining-process budget defaults to 1200 and is capped at 1800.
There are no automatic retries. POSIX timeout handling kills the process group
and bounds collector joins. Python validation and final reporting are
additional work, so this is not advertised as a hard whole-program wall-clock
deadline. A22 source-reviewed these transport mechanisms; hostile-process
timeout/flood execution was not performed in this review.

Paired mode requires explicit executable/painter identities and pins the
genuine baseline, unchanged fixture, contract, admitted authoring evidence,
model, Drawing, font, image files and relevant SDL sources. Registered inputs
are rehashed after the run. Candidate-only mode has a deliberately narrower
canonical numerical/fixture claim and cannot establish paired preservation.
Source labels are root's build attestations: file hashes and matching output
metadata alone cannot prove which source, configuration or dependencies built
an executable. Root retains coherent-build qualification responsibility.

## Original observed result and next gate

The untouched v1 report SHA-256 is
`4895fdbb8f79e07cc4ad2b6d672807433a98e5a08689c323547432ca88725ab7`.
A22 verified all **140 compressed stream artifacts** still match its recorded
sizes and hashes. The report records 70 zero-exit native processes with no
transport errors, all 34 pairs and **8,991 audit records**, including the four
focus-oracle failures. That counter measures calls to `Audit.check`, not every
internal assertion. Successful guarded functions do not add a record, whereas
a caught guard failure does. Correcting these four failures should therefore
remove four failure records from the next run's count while allowing the
previously interrupted model validation to finish; it removes no requirement.

| Original v1 observation | Recorded result |
| --- | ---: |
| Compared paired pixels | 74,008,097 |
| Protected exterior pixels | 70,415,764 |
| Changed protected pixels | **0** |
| Required equal whole frames | 11, all exact |
| Quiet companion differences | **0**, both sides |
| Genuine-before numerical screens | 28 pass / 34 fail |
| Candidate numerical screens | **62 pass / 0 fail** |
| Candidate mean-Y error | 0.7233057967880376 |
| Candidate residual-RMS error | 0.29217125412952677 |

These are observations from root's retained v1 execution. A22 did not execute
native code, a build, benchmark, new capture or the corrected paired matrix.
Root next runs the corrected comparator in a **new v2 directory**, retaining
the original failed run and original source history. Only that new completed
result can establish the corrected matrix outcome. The frozen eight-process
timing batch, independent actual full-frame visual admission and affected
existing native/platform suites remain separate gates.

This source admission does not establish whole-interface 1:1, a measured
Hammond/Leslie match, native accessibility, real-device or host behavior,
callback deadlines, release readiness or publication. All M0–M9 exits and the
nominal dry Engine, 91 shared running sources, 47 parameter identities,
state-4/readers-1–3, plugin UUIDs and musical ownership remain unchanged.

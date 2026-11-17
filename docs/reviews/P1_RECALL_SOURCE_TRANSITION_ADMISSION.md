# P1 candidate-only gate — exact recall source transition

Reviewer **A30**, actual worker `/root/w05_a30`, wave 5, 17 November 2026 UTC.

## Decision and scope

**ADMIT the exact A26 UiModel source pair as an additional candidate-only source
input, subject to root applying the patch and executing its affected gates.**
This is a source-level exception for the existing canonical P1 numerical gate,
not final runtime acceptance. Paired mode continues to require the original
UiModel pair. A future paired experiment using the helper needs its own admitted
source identities and protocol; this transition does not qualify such a run.

The [A30 patch](../development/2026-11-16-console-completion/reports/A30-model-source-transition.patch)
changes only `tools/compare_performance_plate.py` and its focused Python test
file. Its SHA-256 is
`3aaeed128850dab45c392c4dc24871c097958025b155fcde98b3b737a7b95e5a`.
The [source receipt](../development/2026-11-16-console-completion/reports/A30-source-transition.json)
records original and prospective identities, exact reversal evidence, source
inspections and every unrun gate. A30 wrote no production, tool or test source.
Root owns application, coherent compilation, execution and integration.

| Mode and source pair | Admitted behavior |
| --- | --- |
| Candidate-only, both original files | Retain original admission, with no helper-patch dependency. |
| Candidate-only, both exact A26 files | Require complete inserted-block reversal, original whole-file identities, exact new whole-file identities and the frozen A26 patch identity. |
| Candidate-only, one old and one new file | Refuse before native launch. |
| Candidate-only, any altered or unknown pair | Refuse; no source normalization or automatic pin refresh. |
| Paired, both original files | Retain original source and genuine-baseline requirements. |
| Paired, A26 or any other changed pair | Refuse before native launch. |

## Exact source identities

Every original `PINNED` entry remains byte-for-byte unchanged, including both
UiModel files, the genuine baseline admission, fixture, font, Drawing, contract,
authoring evidence and retained reference images. The original baseline
executable and painter constants also remain unchanged.

| UiModel source | Original SHA-256 | Exact A26 SHA-256 |
| --- | --- | --- |
| Header | `6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1` | `34337e5db254bfbc4e23ee4fadf76ecc8fe792f003bd13ab5b54d0a302b5bb15` |
| Implementation | `0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd` | `b4889e0b5d1b6eb0b88b140b8af92815df4bf021158a902994db2c15ed798986` |

The separately frozen [A26 helper patch](../development/2026-11-16-console-completion/reports/UiModel-recall-controls.patch)
has SHA-256
`d4fadc8ae85d9f3dd2aedb6cccc63977fe1c4516dcca47b758a0ec18c7792cf8`.
It contains ten added lines and no removed or changed existing lines: five in
the header and five in the implementation, including the separating blank line.
The [helper proposal](../development/2026-11-16-console-completion/reports/A26-recall-controls-proposal.json)
and [A26 explanation](../development/2026-11-16-console-completion/notes/A26.md)
retain that operation's semantic contract and separate runtime obligations.

| A30 target | Required original SHA-256 | Prospective SHA-256 after exact A30 patch |
| --- | --- | --- |
| Comparator | `e7a810e21099e346ec4ab86097cba6552cde497fcfd22be659907efeb2c80344` | `57f1127b93e683aacfc67f3cf9904344c3e570e4798dcaacf18928968b52a923` |
| Focused Python tests | `b368e9277b306c807672acfa1b200c4fc4eda358c03b3e4e9b3bfe90b21af526` | `cba6e56cbcf7dd3fe16924e21ae0f1bec2d76215a7df4abcbede600be327bd8c` |

These prospective tool/test bytes were constructed and parsed in memory. They
have not been installed or executed by this reviewer.

## Complete reversal and pair coherence

The new validator takes exactly two complete byte sources. It first accepts
only the original coherent pair. If that pair is absent, it rejects paired mode
and rejects any pair retaining one original file. It then requires precisely
one occurrence of each complete A26 insertion, including every comment and
newline, and removes that whole block once. The reconstructed complete file
must match its original pinned SHA-256. Finally, both complete new files must
match the independently admitted A26 pair.

That final check is necessary: moving an otherwise exact block can still
reverse to the original bytes. Exact prospective whole-file identities reject
such relocation. A changed guard, publication call, declaration or comment
cannot match the complete block. An unrelated edit can leave the inserted
block intact, but cannot reconstruct the original file. Neither mixed pairs
nor per-file interchangeable allowlists are admitted.

| Inserted block | Bytes / lines | Exact block SHA-256 |
| --- | ---: | --- |
| Header comments and public declaration | 409 / 5 | `435d8af677b4c1e65ea2166ac34f12cb70e036f3e6df9210d01a87b9d182832d` |
| Complete implementation and separation | 235 / 5 | `92819dd1ff71a2394bcff46011a7ce591bc3b5fe9c20b86a83afe3f1800d98cf` |

A30 independently applied both unified diffs in memory, checked every hunk's
context and line counts, and directly compared each reversed A26 file with
root's preserved original bytes. Both complete byte comparisons are equal,
in addition to the hash checks. The resulting original sizes are 18,547 header
bytes and 83,758 implementation bytes; A26 produces 18,956 and 83,993 bytes.
The live root-applied files now equal those exact prospective bytes.

`pin_ui_model_sources` registers both actual input identities, reads no more
than the registered byte count plus one, and verifies that the read content
still has the registered size and digest. Accepted inputs record both their
selected literal `expected_sha256` and unchanged `original_pinned_sha256`.
The transitioned path also registers and pins the frozen A26 patch. All these
inputs remain subject to the unchanged final input-stability check.

Every report now includes `ui_model_source_admission`. An accepted record names
the original or A26 variant, original/observed/accepted complete-file hashes,
candidate-only mode, transition ID `ui-model-recall-controls-a26-v1`, patch path
and hash, whole-block hashes and lengths, reconstructed hashes and the exact
reversal result. A rejected setup retains the observed inputs and failure,
with no accepted source record. This reports a source admission; it does not
prove which files were linked into an executable.

## Why the P1 source boundary is preserved

The header addition is a nonvirtual public member declaration and comments.
It adds no data member, base, virtual method, include, initialization or layout
operation. The entire private declaration suffix is byte-identical. Exact
whole-file reversal establishes that every preexisting declaration, constructor
and method body remains unchanged; no class-data or layout-source change is
hidden by the exception. This is source inspection, not a measured ABI or
`sizeof` observation.

The new method validates the complete snapshot and calls the existing forced
whole-control publisher. It does not replace the saved-file reference. Neither
the pinned P1 fixture nor the unchanged painter contains any `recall_controls`
reference. The fixture constructs its model through the original constructor,
resize/presentation/observe/activate/key/workspace paths, and the painter takes
the existing const model interface. The new member is not invoked by those
source paths. The unchanged fixture SHA-256 is
`4f1875270af71d08c27372944a4a9c8e4c10b6c31dbeb85b3841b6965915956c`;
the painter remains
`8ca5c05138ed4cd12fe8ef416ea35a3d78a8a3c4915645f53d8c0c0df2fcf927`.

All original comparator module-level assignments remain textually identical.
Every original function and class except the narrow input registration in
`execute` remains textually identical. Thus all 62 thresholds, twelve patch
domains/order, 34-case matrix, support derivation, copied-state and workspace
focus rules, glyph/opaque/focus checks, exact pixel comparisons, transport
limits and genuine-baseline logic remain unchanged. No painter, native fixture,
pixel evidence, reference statistic or numerical criterion is modified here.

The [original paired v1 report](../development/2026-11-16-console-completion/reports/p1-paired-v1/report.json)
remains `4895fdbb8f79e07cc4ad2b6d672807433a98e5a08689c323547432ca88725ab7`;
the [corrected paired v2 report](../development/2026-11-16-console-completion/reports/p1-paired-v2/report.json)
remains `f64b634d5455e69e506730acac036e6b3764804d775ff4bdabb4d0a4e0abe1d4`.
Their original source-specific outcomes and streams are not regraded or relabeled
as post-helper results. The genuine baseline admission remains
`fb3c4bc99d1534222d80f7263a82fef2f883bb584e2c646aae43a7c80c4993ea`.

## Proposed refusal coverage and source-only verification

All **30 existing test methods** are retained with identical method source.
The patch adds **15 methods**, making **45 proposed methods**, using independent
A26 literals and whole-file hashes. It reconstructs original and new complete
source fixtures from either exact live variant, refusing unknown live source.

The additions cover both valid variants and both modes; both mixed pairs; the
new pair in paired mode; deleted, inverted and weakened guards; disabled force,
saved-reference rebasing and legacy Load routing; declaration/comment changes;
duplicate, removed and relocated blocks; changed legacy Load, workspace-focus
and publisher bodies; added class data and altered old declarations; unchanged
original admission without any helper patch; new patch identity; and source
drift after registration. Four execute-level refusal cases require a failed
report with zero native commands and verify that `Runner.command` is never
called. These are authored tests, **not executed results**.

Read-only `git apply --check --whitespace=error-all` accepts the final patch.
Both prospective Python files parse with `ast.parse`; source-slice inspection
confirms all original tests and protected comparator logic above are unchanged.
No Python test suite, native process, build, benchmark or capture was run by A30.
No nested agent or other workspace was used.

An initial in-memory helper reconstruction encountered the original-source
precondition after root had ended the timing freeze and applied A26. It stopped
without writing source. The completed inspection uses root's retained original
snapshots and separately verifies that the live files equal the exact new pair.
This was a source-prerequisite change, not a test or native-execution result.

## Root handoff and remaining gates

Root should apply the exact A30 patch against the two required original
tool/test identities, verify the two prospective hashes, and run
`python3 -B tests/test_compare_performance_plate.py`. It should then rebuild the
affected model, header consumers and P1 fixture coherently, execute the new
candidate-only gate into a fresh report directory, and retain the exact source,
binary and result identities. The A27/A28 helper and roundtrip tests retain
their independent runtime gates. A new pair is intentionally inadmissible to
the old paired protocol.

This source transition does not accept timing, a browser, native interaction,
hardware devices, accessibility, audio deadlines, physical fidelity, whole
interface 1:1 or release readiness. It does not change the 47 parameter
identities, state 4/readers 1–3, 91 shared running sources, plugin UUIDs,
nominal dry Engine or any M0–M9 exit. Root's source-specific integration and
runtime results remain separate from this bounded source admission.

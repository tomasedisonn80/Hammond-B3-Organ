# A29 — independent native VST3 acceptance

Worker `/root/w05_a29_vst3_acceptance`, logical wave 5, 2026-11-14.
Checkout context: `35554c068492fe2b20c1f8a602d8354ae762dc42`; the current
implementation remains an overlay, so that commit does not identify it alone.
Read the standing instructions, complete M0–M9 plan, current status/next steps,
frozen selector/state/parameter contracts, current native source and A22's
source-identified integration report.

## Scope and outcome

Independent review found no new production defect. The [review](../../reviews/PRESET_VST3_ACCEPTANCE.md)
classifies every retained validator diagnostic, audits selector/cache/state/alias
boundaries and distinguishes current behavior from historical qualification.
Root additionally authorized narrow updates to `docs/VST3_CONTROLLER.md` and
`docs/VST3_PROCESSOR.md`; those now describe 47 parameters and state4 without
rewriting their earlier 45-parameter execution results.

Owned files are those two existing contracts, the new review, this note and
[reports/a29-vst3-acceptance.json](reports/a29-vst3-acceptance.json). No production,
test, build-system, SDK, shared status or assignment-manifest edit was made.
No commit, push or child agent was performed.

## Executed checks

Working directory: `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
An independent Python 3.12.14 audit at `/tmp/hammond-preset-a29/audit.py` read
retained logs, Git objects, exact SDK source, source manifests and existing
binaries. It performed no compilation or native test invocation. The final
structured result has SHA-256
`29b0e1ff82002918b04205314f3fed4c862bc4ddbf0f1c0d1a89cabfe980fc75`.

- Parsed the CTest-number prefixes out of both native logs, retaining ordered
  test-suite/case names, teardown diagnostics, rate messages and final summary.
  The resulting patterns are exactly equal: 16 teardown messages, nine
  unsupported-rate messages, three successful-rate messages and 47/0 summary.
- Compared all complete original 45 registry records with `git show
  b79086f:data/parameter-registry.json`; verified the frozen canonical digest and
  exactly two appended IDs, 20480/20481.
- Checked all 23 native oracle literals with exact `Fraction` arithmetic,
  adjacent `nextafter` values and even-significand tie handling. No production
  table or converter supplied the expected rational values.
- Compared 72 selected source/data files with A22's final manifest. Every file
  matched. The structured record enumerates them and their raw SHA-256 values.
- Compared Processor, StateStream, Factory and PluginIds source bytes with
  `b79086f`; all six selected files matched. Compared both module metadata files
  by bytes; they matched. Hashed both preserved module binaries without loading,
  changing or rebuilding them.
- Inspected exact pinned SDK runner, process setup/teardown, valid/repeated-state
  and rate-format sources. SDK root and public SDK worktrees were clean.

The initial audit script attempted strict Python JSON parsing of SDK-generated
`moduleinfo.json`, whose trailing commas are accepted by the SDK's dialect.
Python rejected that read at line 12. Changed the audit to the stronger required
raw-byte equality comparison; no metadata, SDK or production file was changed.
This was an audit assumption correction, not a product failure or a native rerun.

## Exact retained identities

| Input | SHA-256 or Git commit |
| --- | --- |
| Baseline native transcript | `0036cd425d4f4d221fa2a73588a0dbcc2134ae0009653ee427fdaa5a043b7dfd` |
| A22 final native transcript | `e525207f53d60127dcc03702615eee78d4b50d91665fe27b4b653bacf4260396` |
| A22 complete source manifest | `a21d573d4d1da73340b1942b1a72bd494b45eb3663ab4531599e87ba5a91541c` |
| Preserved baseline module | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| A22 module | `36d02646e039d0748a2f01aa9e89dda07c5be816a3ab040b40ae694faad9889e` |
| Shared module metadata bytes | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| SDK root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| Public SDK submodule | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |
| Plugin interfaces submodule | `4f547e8e102b47de4a8b8aaf343c73b700786372` |

The baseline module remains under the preserved `build-native` directory;
A22's module remains under `/tmp/hammond-preset-a22/build-make`. No older library
was linked against a later header. The structured audit retains exact SDK
source hashes; the review links the corresponding immutable primary sources.

## Handoff

Current native contracts are ready for the integrator's documentation review.
No added native regression is needed for the classified diagnostics: existing
lifecycle tests deliberately assert the declared rejection, while SDK behavior
explains the messages. Final integrated-source builds and hosted checks still
belong to their later owners. No DAW, physical device, leak, deadline or fidelity
qualification is inferred from this source/retained-execution review.

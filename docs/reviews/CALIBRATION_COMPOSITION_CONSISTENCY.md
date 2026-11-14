# Calibration composition consistency review

## Decision and scope

Assignment 41, logical wave 7, found **no unresolved contract, schema, example or
package dependency defect** in the source snapshot identified below. The final
independent, targeted audit passed **220 of 220 cases** against an actual private
`CaptureTools` installation: **57 files, 687,338 bytes**. No production code,
schema, policy, numerical threshold or package inventory was changed by this
assignment. The integrating agent owns acceptance and publication.

The scope is the new [study composition](../CAPTURE_STUDY.md),
[complete-report replay](../CAPTURE_REPLAY.md), and
[installed capture package](../CAPTURE_TOOLS_INSTALL.md), including their
interfaces to the existing job, corpus, policy and v1 capture inputs. It does not
repeat assignment 30's complete older v1 schema audit. That earlier
[665-case review](../CAPTURE_SCHEMA_REVIEW.md) and its terminal-newline repair remain
separate evidence. The repaired v1 schema was included, unmodified, in this
actual installation.

[The assignment note](../development/2026-11-13-calibration/41-composition-consistency.md)
retains the full source identity table, every actual case outcome, the exact final
audit harness, execution context and the initial harness failure. Counts below
refer to finite audit cases, not new maintained unittest methods. Multiple
observations within one case are not counted as extra cases.

| Audit group | Cases | Result |
|---|---:|---|
| Five schema metaschema and local-reference checks | 5 | All met expectations |
| Study document shape and semantic validation | 131 | All met expectations |
| Study original-byte and loader checks | 9 | All met expectations |
| Installed input documents across all five schemas | 14 | All met expectations |
| Independently recomputed original-byte binding edges | 16 | All matched |
| Cross-file study and cumulative-work composition | 8 | All met expectations |
| Actual replay, envelope admission and mismatch checks | 17 | All met expectations |
| Complete reports checked against input schemas | 4 | All rejected as expected |
| Declared module import closure | 10 | All closed within package/standard library |
| Package inventory, bytes, paths and preservation | 6 | All met expectations |
| **Total** | **220** | **220 passed; zero unexpected outcomes** |

## Study shape and semantic responsibilities

The 131 document cases produced 21 admissions by both JSON Schema and the Python
semantic validator, 105 rejections by both, and five schema admissions rejected
by the semantic validator. No tested semantic admission was rejected by the
schema. The five differences are the responsibilities explicitly documented in
[the study guide](../CAPTURE_STUDY.md):

| Input change to an otherwise valid study | Schema | Semantic validator | Reason |
|---|---|---|---|
| `schema_version: 1.0` | Admit | Reject | JSON Schema's mathematical integer category does not retain the required exact Python integer/token distinction. |
| Same job ID in two otherwise different entries | Admit | Reject | Whole-object uniqueness does not express uniqueness of a selected property. |
| Same job path in two otherwise different entries | Admit | Reject | Path uniqueness is checked across entries by the runtime. |
| Same job digest in two otherwise different entries | Admit | Reject | Digest uniqueness is checked across entries by the runtime. |
| Two paths differing only in ASCII case | Admit | Reject | Runtime uniqueness compares case-folded paths. |

These observations do not call for widening runtime acceptance or adding a JSON
Schema dependency to the tools. A minimal reproduction is to load the installed
`examples/capture-demo/study.json`, change only `schema_version` to the Python
float `1.0`, and compare `Draft202012Validator(schema).is_valid(value)` with
`capture_study.validate_study(value)`. The first admits; the second raises a
validation error. For property uniqueness, change only the second entry's
`job_id` to the first entry's ID, retaining its different path and digest. This
also admits the machine schema and rejects semantic validation. These are
reproducible documented boundaries, not defect counterexamples.

The finite matrix covers exact root and entry keys; version and origin literals;
root and collection types; lower-case IDs; lower-hex digests; ASCII path spelling;
64-character component and ID bounds; eight path components; 240-character total
path length; selected Windows device stems; trailing dots; Unicode, control and
surrogate characters; zero, one, eight and nine jobs; identical entries; and
selected-property uniqueness. Python tuples are exercised as a direct API input,
not represented as a JSON serialization feature.

The new study schema rejects terminal LF in IDs, paths and digests. Its explicit
forbidden-character checks and exact digest length already prevent the pattern
end-anchor problem repaired in the older capture schema. Tested control and
Unicode suffixes also reject. This assignment found no new terminal-newline
schema defect.

The nine separate byte/loader cases admit a canonical study and a valid document
padded to exactly 65,536 bytes. They reject 65,537 bytes, a UTF-8 BOM, invalid
UTF-8, duplicate root keys, a trailing JSON document and a float version token.
A valid study declaring a nonexistent job loads successfully through
`load_study`: this confirms the documented metadata-only loading boundary.
Opening and binding declared jobs belongs to execution.

## Composition binds original bytes before work

The eight composition cases use private copies. Four malformed relationships
still satisfy document shape but reject before the bound job runner: a wrong
expected job SHA-256, a correctly rehashed job with a different job ID, a
correctly rehashed job naming a different corpus digest, and changed original
job whitespace without an updated study binding. The first three distinguish
schema shape from cross-file context; the fourth distinguishes parsed JSON values
from original bytes.

Changing job whitespace and updating its study digest permits an actual full
study execution, which retains its `failed` engineering status and the observed
new original-byte digest. Input jobs need not be canonically serialized. Saved
reports used by replay have a different, explicitly canonical byte contract.

Cumulative work checks use separately constructed valid job headers and a runner
sentinel. They verify preflight ordering and equality boundaries without
executing a maximum audio or spectral workload:

| Composition | Declared total | Observed preflight behavior |
|---|---:|---|
| Two jobs, each four candidates × 262,144 samples × 16 frequencies | 33,554,432 spectral terms | Reaches the trapped bound runner at the inclusive limit |
| Three jobs with those same individual bounds | 50,331,648 spectral terms | Rejects before the runner |
| Eight jobs, each four candidates × 262,144 samples, no frequencies | 8,388,608 window samples | Reaches the trapped bound runner at the inclusive limit |

The total window maximum also follows from eight jobs times the unchanged
per-job window bound. This audit does not invent an otherwise-valid aggregate
window case one unit above that maximum, nor imply that the maximum workload
was processed.

## Replay preserves the complete saved comparison and underlying status

Actual installed demo job executions yield `pass`, `inconclusive` and `failed`.
Each saved canonical report replays with `match`, retaining its original
engineering status. The mixed study also matches while retaining its failed
status, complete neighboring outcomes and all ten physical/provenance claim
fields as `not_established`. A matching replay is not a passing comparison.

Seventeen replay cases distinguish envelope admission from full-byte equality.
The saved nested policy and reference can each be replaced by `{}`, and extra
JSON data can be added to the saved candidate or corpus, without violating the
specified outer admission envelope. Actual recomputation then returns
`mismatch`. The saved source/runtime context equalities remain true in those
cases. This is the documented behavior: admitted nested data is retained for
complete comparison and is not independently recertified by the envelope
validator. No nested field is silently dropped before equality.

A compact reproduction is to run the passing demo job, replace its saved
`policy` with `{}`, write the entire modified report using the required canonical
serialization, then verify it against the unchanged original job. Envelope
admission proceeds, and the actual fresh full report differs. This is evidence
for the declared boundary, not a request to make replay a second independent
comparison implementation.

A saved engineering status forged consistently with its numerical verdict is
also admitted, then differs from the actual fresh passing result. An inconsistent
status, a strengthened physical claim, an invalid study work declaration and a
nested strengthened claim reject before the trapped public runner. Source-only
and runtime-only saved-context mutations each produce a mismatch with the
corresponding equality flag false. Compact/noncanonical saved serialization and
same-value/different-original-byte job input reject before the runner.

The three complete job reports and one complete study report were each rejected
by all five input schemas. These are four cases, not twenty. The capture,
corpus, policy, job and study schemas describe their respective inputs; they do
not advertise validation of complete execution reports.

## Installed examples, schema closure and declared dependencies

All five installed schemas pass `Draft202012Validator.check_schema`; their
references are local `#/...` references. The already available `jsonschema`
4.26.0 package was used only by this authoring audit. No dependency was installed,
added to runtime, added to CI or resolved over the network.

Fourteen actual installed input documents pass both the appropriate schema and
the existing semantic entry point: the planned capture, planned corpus and
synthetic policy examples; three demo capture manifests; one demo corpus; three
demo policies; three demo jobs; and one demo study. Their sixteen binding edges
were recomputed directly from each referenced file's original bytes, resolving
locators relative to their actual owning document:

| Binding kind | Edges |
|---|---:|
| Planned corpus → planned capture manifest | 1 |
| Demo corpus → demo capture manifests | 3 |
| Demo manifests → raw float32 files | 3 |
| Three demo jobs → corpus and policy | 6 |
| Demo study → three original job files | 3 |
| **Total** | **16** |

No parse/reserialize normalization substitutes for hashing the original files.
The unchanged demo is sixteen files and 32,831 bytes. Its numerical outcomes
remain synthetic software examples; none of these bindings establishes an
acquisition, a specimen, a measured physical value or a permitted recording.

The inventory was typed independently from the frozen install guide, then
compared with the actual installed tree. All 57 expected files exist, all copied
bytes equal their frozen source identities, exactly five schemas are present,
and the package is unchanged after the audit. Required imported modules were
observed under the installed `tools` directory rather than the source checkout.
The ten-module static import audit retains 92 import observations. All local
imports resolve to declared package modules, including the existing one-level
relative `capture_common` fallback; all other names belong to the observed
Python 3.12 standard-library set. No test, source-checkout or external runtime
package is needed by that observed closure.

The installed README's command paths exist. A bounded inspection of 95 ordinary
local Markdown link occurrences found 68 locally resolving and 27 absent
references. All 27 are historical agent notes, research/PDF references or project
context explicitly excluded and disclosed by
[the installation guide](../CAPTURE_TOOLS_INSTALL.md). They are not missing
runtime inputs or README command targets. The retained note lists those actual
occurrences. This finite link scanner plus manual classification is not a claim
to parse every possible Markdown construction or ship the complete research
archive. No package expansion is requested.

## Frozen source and execution evidence

The successful run observed HEAD
`16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`, and fetched `origin/main`
`183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`. The parent integrated work while this
assignment ran. The audit therefore uses a private archive plus an explicit
coherent overlay of all package dependencies and installer/CMake files; the
hashes qualify the tested content, rather than an assumption that an earlier
HEAD alone describes it. All observed live dependencies still matched their
frozen identities at completion.

Key source identities are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `tools/capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `tools/verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |
| `tools/capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| `data/capture.schema.json` | 32,414 | `51fbfdbcc92d9cdb3b71d4b55618840a806e2847b49c93e6aa7d926621661a74` |
| `data/capture-corpus.schema.json` | 3,690 | `420037ea76f22dbd559b4005f1514bcf59d21310349800f138ce5b93c43707c9` |
| `data/capture-policy.schema.json` | 12,377 | `2a1b0fd959f5f760d9460c7c960d48d7d4adbbd27918c9b4df6849646c8a9678` |
| `data/capture-job.schema.json` | 3,574 | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |
| `data/capture-study.schema.json` | 2,102 | `1805ad62f357ec7f828591dce0a968391beba42418b9ea4f20adfe4139389e3d` |
| `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |

Actual execution used CPython 3.12.14 on Linux x86_64, CMake 4.4.4 and a configure
context identifying GNU C++ 14.2.0. Configuration and component installation
succeeded; no native target was built. The final harness SHA-256 is
`bd78aac8e34c59666b0f6e0f4b602cbe0a3c8b89005242315462acca5dee830b`.
Its 76,060-byte result JSON has SHA-256
`a38e1e5582c721ac60f900b708c8f63eba71fab55a4089be360263d287cc264f`.
The exact harness and compact complete outcome ledger are retained in the
assignment note so this review does not depend solely on temporary files.

The first audit reported one unexpected result caused by its own null-root
fixture dispatcher: `None` meant “mutated in place” to the helper, so the
attempted replacement null document instead selected the unchanged valid study.
An attempted ledger cleanup left that stale record in the unexpected accumulator.
The corrected harness tests null directly and removes the stale bookkeeping.
The expected null rejection never changed; the full corrected 220-case scope
passed. Initial harness/result identities remain in the assignment note. This
was a harness dispatch/bookkeeping error, with no producer or contract change.

## Limits and next action

This is finite, source-bound Linux composition evidence. It does not establish
maximum-work throughput, hard real-time safety, native Windows/macOS execution,
host integration, audio fidelity, acquisition quality, physical calibration,
recording rights, report authorship or historical authenticity. Byte identities
and replay cannot establish that a policy was fixed before someone observed an
outcome. No source threshold or physical value was generated or adjusted.

The governing research basis remains atlas pages 355, 364, 484 and 486: original
records/provenance and claims, disclosed corrections and uncertainty, declared
tolerances with retained inconclusive results, and exact source/setup/change
control. Those pages were freshly inspected for this assignment; the complete
PDF reading is retained separately by this session's six assigned readers. This
assignment does not claim another complete-PDF reading or primary-source
measurement review.

The next action is for the integrator to inspect these two owned notes, accept
this bounded review, and include them in the next coherent documentation
checkpoint. No production repair is requested. If the study/replay code, shared
job dependencies, five schemas, installer helper or packaged examples change,
compare the retained identities and rerun affected composition/byte checks
against an independently installed coherent tree. Preserve documented schema
versus runtime responsibilities and the package's disclosed archive limits.

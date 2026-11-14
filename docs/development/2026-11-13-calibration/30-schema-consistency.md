# Assignment 30 — independent schema and semantic consistency

Actual assignment identity: **`/root/cal_w5_a30`**, logical wave 5 of the
2026-11-13 calibration session. This is one actual newly assigned worker. It
does not recount an earlier author, reviewer or atlas reader.

## Ownership and result

Only these two repository files were written by this worker:

- `docs/CAPTURE_SCHEMA_REVIEW.md`
- `docs/development/2026-11-13-calibration/30-schema-consistency.md`

The complete [independent review](../../CAPTURE_SCHEMA_REVIEW.md) is the
operational result. One terminal-LF schema defect was reproduced and reported;
root repaired it. The accepted schema preserves all v1 fields and the unchanged
semantic validator. The final audit has **665 cases**, consisting of 600
document comparisons, 24 actual byte/parser cases, 36 actual compositions and
five old/new regressions, with **zero unexpected final results**.

No production module, schema, existing test, CMake file, shared progress file,
assignment manifest or Git ref was modified by this worker. Root owns repair,
integration, accepted-state accounting, commits and publication. A scratch audit
script and scratch result logs are development intermediates, not installed
tools, default-test dependencies or a new maintained acceptance suite.

## Source basis and checkout observations

Working directory for all commands:

`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`

Read standing `AGENTS.md`, calibration scope, current README/status/next-step/log
context, plan, the relevant capture contracts, all four full schema values,
their actual validator paths and the new declaration-readiness contract.
Read the consolidated fresh atlas review and independently reread extracted
atlas text pages **355, 364, 372 and 484** for boundary, correction, evidence and
decision requirements. No additional full-PDF reading or original-page visual
inspection is claimed; assignments 1–6 retain the full 500-page coverage.

Initial checkout observation: commit
`3c41bf6f2530497518c487f96bd2cd97e21d9cbb`, tree
`f9baccbb54f51063b01a0859d2c10cdadfbd238b`. Wave-5 implementation and test
files were already live and uncommitted. During this audit root published the
equivalent wave-4 tree as `779fb6e13b8f60236cad4aedb9999ba16198f920` and
continued the separate integration. The final observed local `HEAD` was
`d68058d01272aadeea698a9cf788d261ba822285`, tree
`87ce5e7edefdb4267d947b65569e42b5c2197517`, while locally recorded
`origin/main` was `779fb6e13b8f60236cad4aedb9999ba16198f920`.

Those are surrounding checkout observations, not evidence that a dirty tree or
the whole repository was qualified by this audit. This worker did not fetch or
verify a remote publication. The exact schema/data/source hashes below were
checked before and after the completed audit and remained unchanged throughout
that execution. The original defective schema was obtained from the exact
initial committed source; its byte hash is retained independently of later root
commits and is also available in the published wave-4 commit.

## Exact reviewed identities

| Artifact | SHA-256 |
| --- | --- |
| Original `data/capture.schema.json` | `2e33ff19c23b2c82d593073f6d24bd29889531c62acd2d8fcf08ec48c0ae7860` |
| Repaired `data/capture.schema.json` | `51fbfdbcc92d9cdb3b71d4b55618840a806e2847b49c93e6aa7d926621661a74` |
| `data/capture-corpus.schema.json` | `420037ea76f22dbd559b4005f1514bcf59d21310349800f138ce5b93c43707c9` |
| `data/capture-policy.schema.json` | `2a1b0fd959f5f760d9460c7c960d48d7d4adbbd27918c9b4df6849646c8a9678` |
| `data/capture-job.schema.json` | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |
| Supplied capture plan | `35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac` |
| Supplied corpus plan | `9c23a5faf002472d50e9c4e5e923bdb46e95091ee026288d98a91b785a7c4e2e` |
| Supplied synthetic policy | `e091dca3b3fdf3c3675383096007c5f95b848fa6294dedd3906705d061884316` |
| `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/capture_corpus.py` | `adb44d8838bf112e97bd884587dd74fe2dbf8167197622b4ba40453c004d33c7` |
| `tools/compare_capture.py` | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/capture_job.py` | `3ffe39f5723a6a3af779ba33b799e72bdeed9d60365c5df9a8146b8467aec230` |
| `tools/capture_readiness.py` | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| Capture-v1 contract | `618c20e4c6d2b204c69cdad006d69bfd93638de7c6d711b230452fea78b88177` |
| Corpus contract | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| Comparison/policy contract | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| Cleared file-job contract | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| Declaration-readiness contract | `e3eb647244c62d600e58d37a83f99db165256e4a69cf89e210f354fc12b55b0b` |

The corpus/job hashes include assignment 25's approved private audit-core sharing.
The audit does not attribute those uncommitted bytes to an earlier source tree.
No source or data input changed during either completed matrix execution.

## Method and executed checks

Runtime: Python **3.12.14**, Linux x86_64, reported platform
`Linux-6.18.57-x86_64-with-glibc2.41`. Optional audit tool:
**jsonschema 4.26.0**, already installed. The ordinary production tools continue
to use the standard library only. No package was installed, no remote reference
was resolved and no artifact/evidence was uploaded.

The author used independent literal dictionaries, exact mutations of the
supplied examples, independently packed float32 streams and SHA-256 over the
actual generated bytes. No production validator, graph or decoder was used to
derive an expected outcome. Schema and semantic results were captured
separately, including error text. Temporary archives were cleaned through
`TemporaryDirectory`; no repository fixture or source was rewritten for a test.

The main executed development command was:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a30-schema-audit.py
```

The scratch harness first checks all four schema definitions, then compares
documents, runs real bounded loaders at their exact byte maxima, creates
actual small role/derivative archives and checks source identities before and
after. The maintained review contains the full classification, representative
counterexamples, the five repaired families and a compact durable reproduction
of the original two full-document failures.

| Final executed category | Cases | Observed result |
| --- | ---: | --- |
| Capture-v1 documents | 253 | 30 both admit, 202 both reject, 21 documented semantic-only rejections |
| Corpus documents | 87 | 24 both admit, 53 both reject, 10 documented semantic-only rejections |
| Policy documents | 152 | 28 both admit, 110 both reject, 14 documented semantic-only rejections |
| File-job documents | 108 | 16 both admit, 81 both reject, 11 documented semantic-only rejections |
| Actual original-byte/parser admission | 24 | Exact maxima admit; adjacent excess, duplicate keys, BOM, invalid UTF-8 and trailing documents reject |
| Actual corpus/v1 role mapping | 12 | All four mappings admit, eight mismatches reject |
| Actual corpus/policy job mapping | 16 | All four mappings admit, twelve mismatches reject; valid unassigned remains inconclusive |
| Actual derivative/FLAC composition | 8 | Own geometry and ancestor context retained; missing coverage remains inconclusive; invalid selection/unsupported decode reject |
| Original-versus-repaired terminal LF | 5 | Original schema admits, repaired schema and unchanged runtime reject |
| **Total** | **665** | **No unexpected final outcome** |

The 600 document cases include actual direct admission of a 512-entry index and
rejection of 513 entries, plus actual original-byte admission of 256 compact
policy criteria and rejection of 257. The criterion fixtures remain under the
64 KiB policy limit, so the count rejection is not hidden behind an oversized
document. All positive examples are checked by both the schema and the runtime.
The 256-criterion policy is an audit fixture, not an acquired uncertainty budget.

The byte probes really construct and parse 65,536-byte capture/policy/job inputs
and a 1,048,576-byte corpus index, plus their one-byte excesses. The aggregate
artifact and spectral/window-work excesses are declarations; no 768 MiB fixture,
maximum spectral loop or maximum report was executed. Role and derivative
composition uses tiny original synthetic files. Claims about large-workload
capacity, physical data or native-platform behavior do not follow.

## Retained defect and audit expectation history

The first minimal probe changed `capture_id` or `status_reason` in the supplied
plan to the value `plan` followed by LF. Both complete documents were admitted
by the original schema and rejected by the runtime with a control-character
error. This was reported to root before any repair. The old `$`-terminated
patterns could match before a terminal LF. The expanded old/new regression
also reproduces the same issue for UTC, artifact path and SHA-256 fields.

Root repaired only `data/capture.schema.json`, adding explicit character
exclusions and applicable length constraints. This worker did not author that
repair. All five original failures reject against the final schema while the
original archived schema continues to reproduce them. The runtime validator,
positive values and v1 semantic contract remained unchanged.

The first larger audit then ran **566 document, 24 byte, 28 composition and five
regression cases**. It returned exit **1** because four audit expectations
incorrectly assumed that the installed `FormatChecker()` supplies `date-time`
validation. The four exact invalid dates were non-leap February 29, April 31,
hour 24 and second 60. The production validator rejected all four correctly.

The audit explicitly queried the package: `"date-time" in
FormatChecker().checkers` was false, and no `rfc3339_validator` module was
available. A `conforms` query for the invalid February date returned true for
that unregistered format. The original expectation failure is retained; it is
not called a production pass or a production defect. The calendar fixtures and
required semantic rejection did not change. Their schema outcome was reclassified
as the existing documented calendar gate, without installing anything.

The final expanded audit then ran the 665 cases above and returned exit **0**.
No other unexpected result or production repair was required. The final report
explicitly retains `date_time_format_checker_registered: false`. Initial and
final runs are successive development executions, not extra unique cases to be
added to 665.

| Scratch evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| Final author audit harness | 37,201 | `6ac97a98aa01430c35e781d79ad1fd5a83985fcb8fc6e43bd83b6c4159d178e2` |
| Initial result retaining four expectation mismatches | 238,659 | `595981f75641bc1f5038ad7bdb2a1302c90f77f259113cfc23c9eee182315f5a` |
| Final result with zero unexpected outcomes | 451,462 | `e0c7e42ed3fda0465f6b28783a2a8e9b80fea9a03103adc9661f0b0fecd5a3fd` |

These hashes identify local audit intermediates; they are not claims that a new
test component, public data corpus or preserved instrument recording was added.
The two owned Markdown files carry the durable findings, identities, reproducer
and limits. The optional package is not imported by any newly modified runtime
or default test in this assignment.

Final delivery checks confirmed valid UTF-8, final newlines, no trailing
whitespace, balanced fenced blocks and existing local Markdown link targets.
The compact old/new reproduction was extracted from the maintained review and
executed successfully. All reviewed source/data hashes still matched the final
audit when those delivery checks finished.

## Handoff and unqualified scopes

Root should accept the repaired schema with this review and note, retain the
original counterexamples, include affected existing suites in the final coherent
gate, update current status/accounting and commit/push under the standing
authorization. No additional source change is requested by the final audit.
Future study/replay and installed workflows must run the semantic validators
even after a schema pass and must preserve original policy bytes, complete
role/lineage checks and raw-versus-derived context.

This worker did not run CMake, hosted CI, native Windows/macOS filesystems,
maximum report/audio/graph workloads, hostile filesystem races, source-memory
attestation or a different schema implementation. It did not newly qualify
readiness execution; assignment 28 owns that separate acceptance. This is
bounded synthetic software evidence only. Actual specimen identity, clock/channel
calibration, permissions, acquisition chronology, final holdout history,
listening and physical fidelity remain unestablished.

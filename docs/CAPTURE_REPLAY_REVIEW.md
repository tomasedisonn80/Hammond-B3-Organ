# Capture report replay: independent review and acceptance

**Verdict:** the frozen replay contract is cleared and its implementation passes
the independent Linux acceptance below. A matching replay preserves the saved
engineering outcome, including failure or inconclusive results. It establishes
current complete-report reproducibility within the declared source/runtime and
quiescent-file scope; it establishes no historical authenticity or physical claim.

Reviewer: actual calibration assignment **36**, `/root/cal_w6_a36`, logical
wave 6 of the `2026-11-13-calibration` session. Qualification completed on
2026-11-14 UTC as that session continued across midnight. Assignment 35 owns
the producer. This reviewer owns only this review, the
[independent suite](../tests/test_capture_replay.py) and the
[assignment note](development/2026-11-13-calibration/36-replay-acceptance.md).

| Qualified artifact | SHA-256 |
| --- | --- |
| [Frozen replay contract](CAPTURE_REPLAY.md) | `1d855c9c734f0f8e9c3d73e4a735c9ef5d86066b734d1a74b95426545f3d3d88` |
| `tools/verify_capture_report.py` | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |
| Final `tests/test_capture_replay.py` | `ad4e364794e8fffda5e2959f90c046def0a0d6471b3ff049e2b9a93ea03e9d55` |

The evidence note supplies the eight observed runtime-source identities and the
earlier independent fixture writers. These hashes identify the actual tested
bytes; a concurrent checkout commit alone does not identify uncommitted code.

## Contract review and its scope

The complete replay guide was read and cleared before grading the API. Its
admission, comparison, snapshot and publication rules are compatible with the
complete job/study contracts. No blocking contract ambiguity was found and no
contract change was requested. The implementation was read in full after the
main public-behavior expectations were authored. It remained at its announced
API-ready hash through qualification.

The guide deliberately separates three decisions:

1. **Envelope admission** rejects malformed or inconsistent report headers,
   identities, types, claims, source/runtime records and study composition.
2. **Original-input binding** matches the supplied job/study bytes and parsed
   value to the admitted saved report before invoking the public runner.
3. **Complete-byte reproduction** executes that original input and compares
   every canonical byte of the saved and fresh reports.

The first decision does not recertify every nested policy, manifest or metric.
Those remaining bounded values are retained unprojected for the third decision.
Tests deliberately alter or omit nested comparison content and verify a complete
`mismatch`, even when source/runtime and high-level status remain the same.
A saved status or digest cannot independently produce replay success.

Canonical saved-byte admission is explicit. Compact, differently ordered,
CRLF, extra-whitespace or missing-final-LF copies reject before execution even
when their parsed values equal the original. The tool does not normalize the
saved artifact in place or pretend that a newly formatted copy is the original.

The public-runner composition boundary is equally explicit. Replay preflights
the original input and retains its first snapshot. The existing public runner
then reads it independently and owns its own complete archive snapshots through
its return. Replay checks the returned consumed identity and retains its own
report/input/source snapshots through its later return. A changed input between
preflight and the public read may cause bounded artifact work before rejection;
the tool does not promise an atomic preflight or a hostile-filesystem sandbox.

## Independent expected results

Earlier independent `JobArchive` and `StudyArchive` authors construct the input
files. Their `TestCase` classes are not imported or recounted. Public job/study
executions create the actual saved report artifacts under test. No replay helper
or replay result defines the expected summary or the numerical/status oracle.

The suite fixes the literal reference `[1,-1,1,-1]` and quarter-offset
`[1.25,-0.75,1.25,-0.75]`, their original-byte and decoded SHA-256 identities,
and the exact `0.25 FS` RMS error from the cleared job contract. Margin
`0.125 FS` and bounds `0.375`, `0.25`, `0.0625 FS` independently produce pass,
inconclusive and failed comparisons. Replays of all three return `match` while
retaining the corresponding engineering status.

A mixed study retains pass, inconclusive and failed reports in declared order,
with one count of each outcome and validation role count three. Its replay
matches while its engineering status remains failed. An all-fit study likewise
matches without inventing final-test coverage or changing any of the ten
`not_established` physical/provenance fields.

Expected summaries are assembled independently from literal contract keys,
standard-library serialization and hashing of the actual original bytes, current
runtime observations and source-file bytes. The full context fields, original
input/report identities, fresh-report identity and verifier identity are checked.
Relocation and repeated calls preserve identical summaries in the same
source/runtime environment; returned mutable records do not contaminate later
calls or the original files.

A decisive controlled-return test places `1.0` in saved nested data and `1` in
the fresh nested data. Python dictionary equality considers the two reports
equal, but their canonical byte sequences differ. Replay returns `mismatch`,
proving that value equality or a selected status is not its decision rule. The
controlled extra field is an envelope-comparison probe, not a claim about an
ordinary producer's metric schema.

Changed source hashes and runtime strings remain visible as contextual
differences. An empty saved machine string is admitted as specified. Neither
context flag overrides a full mismatch or identifies its historical cause.

## Admission, resource and mutation acceptance

Executed admission cases cover all required job/study root fields, unknown
fields, exact numeric and Boolean types, literals, IDs, input/source identity
shapes, digest grammar, original byte sizes, matching corpus/policy bindings,
declared outcome precedence, work sums, ordered study jobs, nested source/runtime
agreement, role counts and every physical/provenance claim. Duplicate keys,
BOM, invalid UTF-8, nonfinite/overlong numeric tokens, trailing JSON, malformed
Unicode and forbidden controls reject before the trapped public runner.

| Boundary | Actual independent exercise |
| --- | --- |
| Saved report bytes | A real **16,777,216-byte** canonical admitted envelope reaches an explicit execution sentinel; one extra byte rejects before the runner. This is admission evidence, not a matching maximum-size replay. |
| Report nodes/depth | Independent traversal derives a real report's value-node count and root-zero container depth. Reduced limits accept equality and reject one below. A nested job at depth 33 rejects even when its enclosing study remains within depth 40. |
| Numeric magnitude | Exact integers `±4e18` admit; integers one unit beyond reject, without relying on float rounding. |
| Original input bytes | An actual valid 65,536-byte whitespace-padded job replays; 65,537 bytes reject before public execution. |
| Source bytes | A temporary associated source observation at 1,048,576 bytes is admitted and reported as changed context; one extra byte rejects. The already loaded module is not claimed to be authenticated by that observation. |
| Replay snapshots | Ordinary job/study paths complete with nine/ten replay-owned observations. Reduced caps accept those counts and reject one fewer; source inspection confirms the defensive cap is checked before appending. |
| Summary bounds | Independent byte/node/depth measurements around a complete real summary accept equality and reject one less. No summary truncation or partial success is admitted. |

A 192-criterion policy is originally compact and admissible below 64 KiB, while
its formatted equivalent exceeds 64 KiB. Actual job creation and replay preserve
the compact original bytes and identity. Replay does not pass a pretty-printed
policy copy into the policy parser or discard criteria to make it fit.

Controlled observations verify one saved-report read, two ordinary original-input
reads and exactly one public runner call. A changed original input rejects before
public execution. A deliberately changed input between preflight and the public
read performs actual bounded work, then rejects the newly consumed identity;
this exercises the guide's documented race boundary directly.

Saved report and original input changes after public return reject. Same-byte
leaf replacement rejects, while harmless sibling creation remains valid.
Returned input, source, runtime and claim inconsistencies reject. Runtime is
checked again after the runner returns. Every fault hook asserts that its
intended boundary was reached; temporary roots are resolved before targeted
path comparisons, following the retained Windows/macOS fixture findings.

Nine subprocesses use temporary copied source trees:

- Each of the six job sources and the verifier source is changed after the job
  runner returns: seven rejecting probes.
- The additional study source is changed after the study returns: one rejecting
  probe.
- A source is changed after replay inventory but before the public job read:
  one rejecting probe.

The repository's actual source files are never mutated by these tests. All
copied-source probes require the mutation to have occurred before accepting the
rejection. These are controlled observable changes, not exhaustive live race
schedules or proof against intentionally restored filesystem metadata.

## CLI, filesystem and publication

Six actual replay CLI processes cover matching pass/failed/inconclusive jobs,
a matching failed study, a complete mismatch, and a foreign working directory
with Unicode paths, an ASCII-configured terminal and explicit new-file output.
Matched failed/inconclusive engineering results exit **0** for replay. A complete
mismatch exits **1** with empty stderr. Input/publication rejection also exits 1
but produces no summary; usage errors exit 2. There is no replay exit 3.

In-process cases additionally cover exact argv types, missing/duplicate/empty/
abbreviated/unknown options, help, `main(None)`, text-only streams, actual
ASCII/CRLF-translating wrappers, short or failed stdout, unavailable diagnostics
and cancellation. Successful output bytes are canonical UTF-8/LF, independently
of terminal text encoding or newline translation.

Native Linux symlink, hardlink and FIFO cases all executed. Selected report leaf
or parent links reject; ordinary aliases above a selected root remain usable.
Directories and missing paths reject. Capability tests explicitly skip if a
future platform cannot create the required filesystem object; the final local
run had zero skips.

Existing files, directories, original inputs/reports, hardlink aliases, dangling
links and raced destinations remain unchanged. Missing output parents are not
created. An actual complete publication followed by injected temporary-cleanup
failure remains complete and is disclosed. Later stdout failure also retains
the published file. Short delivery reports failure despite already emitted
bytes. Cancellation propagates without a fabricated summary or publication.

## Executed result, retained failure and next gate

From `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`, using CPython 3.12.14 on
Linux x86_64:

```sh
python3 -B tests/test_capture_replay.py -v
python3 -B tests/test_capture_replay.py
```

The first run completed 69 methods in **7.584 seconds**, with 68 passes and one
reviewer-fixture assertion failure. That assertion compared the contracted RMS
metric record directly to `0.25`, rather than reading its `value` field. It
failed before invoking replay in that method. The numeric expectation remained
`0.25`; only that field lookup was corrected. No producer, contract, threshold
or other test expectation changed.

The corrected suite passed **69/69 methods in 8.070 seconds**. Final text QA
then found one redundant blank line at the test file's end. After that formatting
cleanup, the exact final file at the hash above passed **69/69 in 8.946 seconds**.
Both corrected runs had zero failures, errors or skips. The suite comprises 13 result methods, 17 admission,
eight resource, 15 identity and 16 CLI methods. Subcases and reruns are not
additional methods or distinct assignments. No production defect was found.

Root should include the accepted replay files in a coherent configured source,
qualify the installation/relocation workflow, update shared status/next steps/
log/ledger, and commit/push under the standing authorization. Every installed
runtime dependency and original archive byte must be retained together. Fresh
hosted outcomes remain separately observed gates.

This review claims no native Windows/macOS run, installed-prefix acceptance,
hosted CI, maximum audio/spectral workload, complete maximum-size report
generation, adversarial-filesystem proof, historical timestamp authenticity,
physical acquisition, rights clearance, calibration, listening or fidelity.

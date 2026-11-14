# Capture CLI pipeline and real-pipe acceptance

## Final decision

The final source passes **9/9 independent maintained methods and 71 actual child
processes in 8.223 seconds, with zero failures, errors or skips**. All eight CLI
entrypoints now preserve process exit 1 for the tested real-pipe delivery failures.
Complete published reports and generated files survive failed delivery; ordinary
statuses, canonical bytes, Unicode content, exact replay and no-clobber behavior
remain intact. The standalone generator and legacy validator also run without
sibling capture modules. Root still owns integration and publication.

The [assignment note](../development/2026-11-13-calibration/46-cli-pipeline.md)
retains the complete original 24-case process observation, precise commands,
source identities, failed candidate, expanded acceptance and final case ledger.

## Frozen independent stream criteria

<!-- BEGIN A46 FROZEN STREAM CRITERIA -->
Assignment 46 (`/root/cal_w8_a46`, logical wave 8) froze this protocol before
assignment 47's implementation. This is a process-level qualification of
standard-stream delivery, separate from existing in-process replacement-stream
tests. Only private copied sources, generated fixtures and outputs are used.

1. Create a real OS pipe, close its read descriptor **before** launching the
   child, pass only its writable descriptor as the selected standard stream,
   and close the parent's writer after the child finishes. No timing race or
   downstream consumer is used. Run a fresh interpreter with `-B -S` and
   `PYTHONIOENCODING=ascii:strict`.
2. A detected standard-stream delivery failure returns process exit **1**.
   For a data rejection whose error stream is closed, the existing rejection
   exit **1** must survive interpreter finalization. Do not accept 120, success,
   or any-nonzero as equivalent to the documented 1. When stderr is writable,
   retain a contextual diagnostic without an uncaught traceback or CPython
   finalizer warning. No diagnostic can be required from a closed error pipe.
3. Cover help/small stdout and ordinary report/inventory stdout. Retain exact
   full published report bytes or all completed demo files when delivery fails
   afterward. No deletion or alteration may disguise completed publication.
   Output-file creation and stdout delivery are separate effects, not one atomic
   transaction. Closed output alone does not authorize rewriting original input.
4. Preserve ordinary CLI argument, status, report-byte and no-clobber behavior.
   Run the fresh synthetic pass/inconclusive/failed jobs and mixed failed study;
   all four exact replays match while retaining their underlying outcomes.
   Retain original-byte bindings and every input, source and output identity.
5. Inventory and copied-source coherence must be explicit. The comparison and
   common modules have no CLI. Legacy `validate_capture` is characterized too,
   but any repair or maintained acceptance beyond the seven new CLIs requires
   the integrator to include its entrypoint and preserve its existing packaging
   dependency closure and ordinary v1 semantics.
6. Maintain failures and original stderr/exit evidence. Repair the production
   cause or accurately report the remaining gap; do not relax the expected
   return code or change the numerical policy. This Linux evidence does not
   establish native Windows/macOS behavior, crash durability or hardware fidelity.
<!-- END A46 FROZEN STREAM CRITERIA -->

## Original process-level observation

The ten copied modules were unchanged across the first 24 process invocations.
The producer-independent launcher and complete original observations remain at
`/workspace/scratch/c9f3ead4c910/a46-baseline-pipes.py` and
`/workspace/scratch/c9f3ead4c910/a46-cli-pipeline/baseline-pipes.json`.
The result is 26,452 bytes, SHA-256
`7053ec36d52898ec8fff131517fc6fbe53764b3d916f40c26957cb167cca8058`.
The assignment note will retain the exact launcher and outcome details; scratch
paths are reproducibility context, not repository download links.

| CLI | Closed stdout: help | Closed stdout: ordinary report | Closed stderr: data rejection |
| --- | ---: | --- | ---: |
| Audio | 120 | 120, traceback and finalizer warning | 120 |
| Corpus | 120 | 1, uncaught traceback | 120 |
| Job | 120 | 1, contextual diagnostic; full file retained | 120 |
| Readiness | 120 | 1, contextual diagnostic; full file retained | 120 |
| Study | 120 | 1, contextual diagnostic; full file retained | 120 |
| Replay | 120 | 1, contextual diagnostic; full summary retained | 120 |
| Demo generator | 120 | 120; all 16 completed files retained | 120 |
| Legacy v1 validator | 120 | 120, finalizer warning | 120 |

The first hypothesis was a buffered-finalization boundary, not a new numerical
or file corruption defect. The official [Python 3.12 `sys.exit` documentation](https://docs.python.org/3.12/library/sys.html#sys.exit), inspected for this review,
explains that a cleanup error after `SystemExit`, including a standard-stream
flush error, changes the interpreter result to 120. That documented mechanism
matches the observed finalizer warnings and the difference between small and
large writes. Small writes remain buffered when flush fails; CPython
attempts another flush at shutdown and changes the process result. A large
report may fail during write and retain the intended exit 1. The full reports
and generated demo were complete and preserved in every observed publication
case. Corpus did not publish a file and emitted an uncaught traceback on its
otherwise nonzero failure. All original archive and copied tool bytes remained
unchanged. Assignment 47 owns the bounded production repair; assignment 46 owns
independent acceptance and this record.

## What the independent pipeline checks

A fresh demo is generated in a private Unicode/space path. Only private policy
rationale and planning prose receive `Ω — 東京`; their original policy/job/study
hash edges are updated independently. Literal audio arrays, decision margins and
bounds remain unchanged. The expected RMS errors .25 and .5, with margin .125,
produce the separately predicted pass/inconclusive/failed outcomes. The mixed
study remains failed, and all four saved canonical reports replay exactly while
retaining their respective engineering outcomes.

Thirteen ordinary child invocations establish those controls. The failure matrix
then runs eight help cases, eight valid-output cases, eight data-rejection cases
with closed stderr and four complete-publication cases with both streams closed.
Twenty actual output-collision cases cover exact input, tool source, saved report,
hardlink and dangling-link destinations. Ten further invocations run single-file
generator and validator copies with an empty `PYTHONPATH`, no sibling tools and a
foreign working directory: help, ordinary execution and the three closed-stream
conditions. This is 71 invocations across nine maintained methods, not 71 new
methods or 71 independent agents.

The seven new CLIs retain their specified UTF-8/LF forms. The legacy validator
retains its existing native text-newline convention. The initial test was refined
before repaired acceptance to use `os.linesep` for that legacy control; Linux
expectations and every exact exit-1 criterion stayed unchanged. The original
18,891-byte test and its initial failures remain retained. No numerical tolerance
or pipe outcome was relaxed.

## Candidate dependency finding and correction

The first producer candidate passed the original seven methods / 61 processes
in 6.638 seconds. Root's subsequent source review found that importing the common
CLI helper violated the generator's frozen promise to import no capture-tool
module. The independently running existing demo suite also observed that defect:
42/43 methods passed, and `test_generation_uses_only_standard_library_imports`
failed against generator SHA-256
`0ae33518681f0c627f165daf287de8a25afad24e6ddee74bbb731c2599a80dd3`.

The extended real single-file test then reproduced all five candidate failures
against an immutable copy. Normal help and generation could not import
`capture_common`; closed stdout still exposed that traceback or absent output,
and closed stderr produced 120. These were actual executions, separately dated
from the source-review finding. The 18-process reproduction includes thirteen
ordinary setup controls and five independent-generator cases; it is not a new
full-suite run. Its result is 24,660 bytes, SHA-256
`2d9cd744eab84e415ce600b389de638d319224ce82dd7c63f5aef2c537fccd6c`.

Assignment 47 moved the same guard into the generator as a local stdlib-only
function, as already done for the legacy validator. It changed no generator
payload or v1 meaning. The final expanded nine-method / 71-process result passes,
and the final existing demo suite passes all 43 methods in 1.346 seconds.
The earlier candidate results and failures remain evidence; they were not
rewritten as final success. The legacy validator was never a member of the old
23-file OfflineTools component; its independent script dependency closure is the
separate requirement preserved here.

## Final source and existing regression qualification

The final ten-module closure was copied coherently and matched the producer's
frozen inventory before execution and the live sources afterward. Only generator
source changed between the first candidate and the final candidate. An independent
AST comparison also finds all **228 existing top-level function/class definitions
unchanged** from the original ten-module baseline. Three new executable-boundary
guards and the entrypoint/import additions account for the repair. This finite
source comparison does not replace execution, nor claim whole-program equivalence.

The helper explicitly flushes at the executable boundary, catches the expected
OS delivery failure, and retires only the failing original standard text stream.
The actual tests establish quiet process finalization and preserved files; they
do not claim that closing a text wrapper closes every underlying OS descriptor.
Imported API `main` behavior and numerical functions stay unchanged. Cancellation
and unrelated programming errors are not translated into success.

| Final source | Bytes | SHA-256 |
| --- | ---: | --- |
| `capture_audio.py` | 30,313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `capture_common.py` | 12,774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `capture_corpus.py` | 39,476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `capture_job.py` | 24,433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `capture_readiness.py` | 11,630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `capture_study.py` | 16,849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `make_capture_demo.py` | 25,734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `validate_capture.py` | 28,237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `verify_capture_report.py` | 23,489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

The affected existing suites were executed against an immutable archive of
`c352d684e636b370edcdbbf0249a884623cbbfb1`, tree
`1ce57555f10fc533b5d303e9e53c5631ca1d2090`, with an explicit coherent ready-source
overlay. Ten suites pass on dependencies byte-identical to the final source.
The generator-only change was then qualified in a separate final overlay by its
43-method suite and the expanded process suite. No fresh all-619-method single
final-tree run is claimed.

| Existing suite | Methods | Final applicable result |
| --- | ---: | --- |
| `test_capture.py` | 41 | 41 passed |
| `test_capture_common.py` | 49 | 49 passed |
| `test_capture_audio.py` | 41 | 41 passed |
| `test_capture_audio_admission.py` | 63 | 61 passed; two capability skips |
| `test_capture_corpus.py` | 47 | 47 passed |
| `test_capture_corpus_admission.py` | 59 | 59 passed |
| `test_capture_job.py` | 81 | 81 passed |
| `test_capture_readiness.py` | 65 | 65 passed |
| `test_capture_study.py` | 61 | 61 passed |
| `test_capture_replay.py` | 69 | 69 passed |
| `test_capture_demo.py` | 43 | 43 passed on the final generator overlay |

The eleven existing suites cover 619 methods: 617 pass and two audio capability
cases are skipped. The skips are native Windows reparse behavior and Unix-domain
socket creation/bind denied by this environment (`Errno 1`). A separate two-case
verbose check identified those exact reasons; it is not counted as extra
acceptance. Three independent test processes were allowed concurrently in the
first regression audit; their durations are test observations, not performance
or real-time guarantees.

The final maintained test is 22,054 bytes, SHA-256
`bfff3005af05ede0b48258de9be1b1560384f6fec618fa6b29aad6dc75d41cb6`.
The final process result is 59,263 bytes, SHA-256
`c65213f8baf1a0e23d11acc945607ce232aa719beb4bde94c503f4b16e4fa3e4`.
The final demo result is 4,518 bytes, SHA-256
`4ae3233e2d70825a5f912b2582fb1f9cbacdf4ad286f063167e716162c2cf14e`.
The note retains the full source/log identities and compact complete final case
ledger, so these conclusions do not rely solely on scratch files.

## Operational meaning and next step

A nonzero delivery result does not imply that no file was written. Preserve a
complete `--output` report if it exists; do not remove it to force a repeat with
the same path. Job/study reports can be checked using the explicit original input
and `verify_capture_report.py` with a fresh summary path. A replay match still
retains a failed or inconclusive engineering outcome. A generated demo retained
after an inventory delivery failure remains an input archive; creating it did
not run analysis. Readiness reports are metadata reports, not job/study replay
inputs.

Root should accept the final owned test and records with assignment 47's exact
source, include the new suite in the coherent integration, retain both original
failure families, and observe native hosted outcomes. This finite Linux test
matrix does not establish crash recovery, an atomic file-plus-stream transaction,
all possible concurrent stream races, native Windows/macOS execution, physical
acquisition, metrology, permissions, holdout chronology or instrument fidelity.
No further production repair is requested by this review.

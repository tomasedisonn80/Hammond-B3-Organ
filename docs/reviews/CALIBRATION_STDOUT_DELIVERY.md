# Capture CLI stream-delivery repair

## Result and scope

Assignment **47**, `/root/cal_w8_a47`, repairs the process-level standard-stream
failure found independently by assignment 46. The final source passes its
independent **9-method, 71-process** pipeline matrix, with no failures, errors or
skips. A detected closed-pipe delivery failure now produces process exit **1**
without an uncaught traceback or interpreter-finalization warning on writable
stderr. Completed report files and generated demo files remain intact.

This is a CLI-boundary change. Existing input validation, numerical computation,
public API function bodies, `main` function bodies, report serialization and
publication order are unchanged. Root owns coherent integration, test discovery,
shared status and publication. This report does not claim a final committed
source gate or a new native platform result.

The exact independent criteria were frozen before production edits in
[CALIBRATION_CLI_PIPELINE.md](CALIBRATION_CLI_PIPELINE.md), between its A46 marker
lines: **2,578 bytes**, SHA-256
`02cc59e2b50151e06dcfbd7b68c99be1635a4a6c5de3a2fb6c63db4316814b43`.
That review and its [assignment note](../development/2026-11-13-calibration/46-cli-pipeline.md)
own the independently executed process and regression evidence. The
[producer note](../development/2026-11-13-calibration/47-stdout-delivery.md)
retains this assignment's exact source identities, author probes, initial
findings and reproducible guard-check harness.

## Original failure and cause

Worker 46 used a real OS pipe whose reader was closed before the child started.
It ran fresh `python -B -S` processes with `PYTHONIOENCODING=ascii:strict` and
retained all original files and outputs. Its baseline is the ten-module closure
at the accepted metadata-allocation checkpoint, before this CLI repair.

| CLI | Help with closed stdout | Ordinary output with closed stdout | Data rejection with closed stderr |
| --- | ---: | --- | ---: |
| Audio | 120 | 120, traceback/finalizer noise | 120 |
| Corpus | 120 | 1, uncaught traceback | 120 |
| Job | 120 | 1, contextual diagnostic; completed file retained | 120 |
| Readiness | 120 | 1, contextual diagnostic; completed file retained | 120 |
| Study | 120 | 1, contextual diagnostic; completed file retained | 120 |
| Replay | 120 | 1, contextual diagnostic; completed file retained | 120 |
| Demo generator | 120 | 120; all sixteen created files retained | 120 |
| Legacy v1 validator | 120 | 120 | 120 |

The first independent maintained matrix executed seven methods and 61 child
processes, with 24 failing subcases and no harness errors or skips. Ordinary
controls and twenty collision cases passed. The failure was therefore the
observable process boundary, not changed comparison results or lost reports.

Assignment 47 independently reproduced all sixteen help/rejection failures from
another private before-source copy: every process returned 120. Python's
[documented `sys.exit` behavior](https://docs.python.org/3.12/library/sys.html#sys.exit)
explains this status: a cleanup error after `SystemExit`, including a buffered
standard-stream flush error, can change the exit code to 120. Catching a write
inside `main` and returning 1 is insufficient if its stream still holds buffered
bytes that the interpreter retries at shutdown.

## Executable-boundary implementation

`capture_common._cli_exit` runs only at the executable boundary. It observes the
entrypoint's ordinary result or integer `SystemExit`, handles an otherwise
escaping `OSError` with the module's contextual diagnostic, and explicitly
flushes both standard streams before deciding the process result. Any observed
delivery failure produces 1. Existing input-error and numerical-outcome handling
inside each `main` remains unchanged.

If a flush fails, the helper retires a stream only when all of these hold:

- It is the same object selected at the boundary's start and is still the current
  `sys.stdout` or `sys.stderr` object.
- It is also the corresponding unchanged original `sys.__stdout__` or
  `sys.__stderr__` object.
- Its exact type is `io.TextIOWrapper`, and its descriptor is respectively 1 or 2.

It then closes that failed wrapper. The observed CPython wrapper becomes closed
even when closing repeats the same pipe error during its own flush. The helper
retains a distinct close error or a stream that remains open as additional
cleanup evidence, without substituting it for the original delivery error.
Healthy streams and caller-supplied replacements remain open. No stream is
retired merely because the command returns a failed engineering outcome.

The helper does not change standard-stream objects, reset signals, redirect file
descriptors, open a null device, allocate a temporary descriptor or call
`os._exit`. The observed original standard descriptor remains process-owned
after its wrapper closes; the process releases its descriptors on exit. This is
stream-buffer retirement, not a claim that the helper closed OS descriptor 1/2.
Its normal cleanup path does not bypass Python cleanup.

Already handled contextual errors are not duplicated just because final flushing
observes the same failure. A writable error stream receives the appropriate
module diagnostic: the audio/readiness JSON envelope or existing textual
`corpus error`, `job error`, `study error`, `replay error`, `demo error` or
`capture error` prefix. If stderr itself cannot deliver data, no secondary
diagnostic is promised. Partial stdout bytes cannot be withdrawn, and completed
files are preserved. The generator's existing message still discloses that a
created archive was retained when its inventory delivery fails.

Cancellation and unrelated `ValueError`, `TypeError`, `RuntimeError`, and
noninteger caller `SystemExit` are not suppressed by the guard. Imported API and
direct `main(argv)` calls retain their existing behavior; the finalization guard
is invoked only under `if __name__ == "__main__"`.

### Standalone generator and validator preserved

The frozen [demo contract](../CAPTURE_DEMO.md) requires that its generator import
no capture-tool module. Root caught the first candidate's new executable-only
`capture_common` import before acceptance. The existing independent demo test
also rejected it, and actual no-sibling executions exposed the missing import.
The repaired generator now has an identical local stdlib-only guard. The legacy
validator also keeps a local guard so it remains an independent stdlib script.
Neither requires a sibling module for help, validation, generation or failure
handling.

The three guard function ASTs are exactly equal. This intentional small local
duplication preserves the two standalone contracts; a future guard change must
review all three copies and rerun their actual standalone behavior. The other
six newer CLI entrypoints use the common helper. All ten modules remain in the
existing CaptureTools inventory. The separate 23-file OfflineTools component
does not contain the validator, and its inventory was not changed here.

## Verification and retained failures

### Independent acceptance owned by worker 46

The final [maintained pipeline suite](../../tests/test_capture_cli_pipeline.py)
passes **9/9 methods and 71 actual child processes in 8.223 seconds**, without
failures, errors or skips. It covers all eight CLI help/report/rejection pipe
paths, four both-streams-closed publication cases, ordinary UTF-8/LF behavior
under an ASCII terminal encoding, the literal pass/inconclusive/failed demo
outcomes, four fresh exact replays, twenty output/input/source/link collision
cases, and isolated generator/validator invocation without sibling modules.
The legacy validator keeps its original native text newline convention.

Its final result is 59,263 bytes, SHA-256
`c65213f8baf1a0e23d11acc945607ce232aa719beb4bde94c503f4b16e4fa3e4`.
Its final demo regression passes **43/43 methods in 1.346 seconds**; that result
is 4,518 bytes, SHA-256
`4ae3233e2d70825a5f912b2582fb1f9cbacdf4ad286f063167e716162c2cf14e`.

Ten existing suites passed against the earlier candidate; every source they
consume is identical to the final source. The later generator-only repair is
outside their dependencies. Their counts are v1 capture 41, common 49, audio 41,
audio admission 63, corpus 47, corpus admission
59, job 81, readiness 65, study 61 and replay 69. Those suites contain **576
methods including two explicitly skipped audio capability cases**. With the
repaired 43-method demo suite, the existing regression scope contains 619
methods: 617 passed and two skipped. These are worker 46's executions, not new
producer executions, CTest-suite counts, or a claimed final full-source gate.

The initial candidate's seven-method, 61-process pipe matrix passed, but its
existing demo suite passed only 42/43 and the extended standalone probe failed
five process cases because the generator imported a sibling. These failures
remain retained. Only the generator dependency arrangement changed for the
final source. No expectation, comparison tolerance or standalone contract was
weakened.

### Additional author boundary probes

Assignment 47's finite guard harness passes **18/18 cases** on the final source:
all 228 pre-existing top-level function/class ASTs across the ten-module closure
are unchanged; all three new guards have equal ASTs; custom `StringIO` streams
retain statuses 0/1/2/3 and ownership; failing fake streams are not closed even
if they claim descriptor 1; a replacement real `TextIOWrapper` remains owned by
its caller; five primary exception objects propagate unchanged; actual failed
original wrappers retire while the healthy opposite wrapper stays open; healthy
real streams remain open; and an injected distinct close error retains both
primary and cleanup reasons.

The close-error probe deliberately restores ordinary closing afterward so the
probe process can finish. It demonstrates retained error context, not a guarantee
of exit 1 when an operating system or custom runtime prevents retirement of the
actual original stream. That cleanup boundary is explicitly unresolved beyond
the observed successful retirement cases.

The first version of this author harness incorrectly expected the wrapper close
to close OS descriptor 1. It observed `stream.closed == true`, the opposite
stream still open, and the standard descriptor still valid. Only that harness
assertion was corrected to the intended ownership boundary; no producer change
was needed. The original 7,960-byte harness and failure are retained in the
assignment note. The final 8,028-byte harness has SHA-256
`74b248ceff2e4eeb7173d4f7f84d5e1eafb5f25e9957dde480209e9986670fe4`.

Eight additional actual `-B -S` invocations copied only one script into each
standalone source directory. Generator and validator help, successful work,
closed stdout and closed error output all met expectations. The generator
recreated all sixteen original files byte for byte, totaling 32,831 bytes. Their
static imports resolve only to the observed standard library. Python AST and
owned-source whitespace/diff checks pass.

## Source identity and continuation

The before-source checkpoint is local commit
`459bfacbda90005d618f12c4513b9c71cb11193d`, tree
`3325af558b040759c1b432ec0806a80785af9713`. It already contains the independently
accepted observed-size metadata read. The final candidate changes nine module
files; comparison metrics are unchanged. The producer note retains the complete
ten-module final identity table. Key identities are:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `capture_common.py` | 12,774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `capture_corpus.py` | 39,476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `make_capture_demo.py` | 25,734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `validate_capture.py` | 28,237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |

These are uncommitted candidate identities at the experiment handoff. Changing
observed source files necessarily changes newly produced job/study source
records. Earlier reports and the older allocation experiment remain unchanged;
they must not be rewritten to manufacture a replay match. The metadata reader's
size-plus-one implementation and all numerical rules are preserved.

Actual execution here used CPython 3.12.14 on Linux x86_64. Native Windows/macOS
and other interpreter finalization behavior require their own executed gates.
Custom stream retirement, hostile concurrent source mutation, atomic stdout/file
transactions, physical acquisition, permissions, calibration, holdout chronology,
native real-time behavior and instrument fidelity are not established.

Next: root reviews the independently accepted final closure, retains both
original failures, integrates its separate installation-test repair, qualifies
the resulting coherent source, updates the handoff and publishes under the
standing guarded non-force workflow. No further production repair is requested
by this assignment's final observed results.

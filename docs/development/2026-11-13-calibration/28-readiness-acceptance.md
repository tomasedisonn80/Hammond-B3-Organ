# Assignment 28: independent metadata-readiness acceptance

Actual identity: `/root/cal_w5_a28`, assignment 28 of logical wave 5 in the
2026-11-13 calibration session. This worker owns only
`tests/test_capture_readiness.py` and this note. The parent owns shared status,
the actual assignment manifest, integration, commits and publication. No
production, contract, schema, CMake, shared-document or Git-ref changes were
made by this worker.

**Result:** the final independent suite passed **65 of 65 test methods**, with
zero failures, errors or skips, in **0.554 seconds**. No production defect was
found in the executed scope. Tests retain fictional declaration fixtures and
explicit injected failures; they establish no physical acquisition or fidelity.

## Source and reading

Working directory for all commands was
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. The worker read the standing
instructions, calibration scope/current handoff, plan/current status and next
steps, the entire frozen [readiness contract](../../CAPTURE_READINESS.md),
[unchanged capture-v1 format](../../CAPTURE_FORMAT.md), and relevant producer
and shared-admission code. The fresh complete atlas reading remains the work
of assignments 1–6. This worker additionally read extracted atlas pages 355,
356 and 359 for declaration, boundary, clock and permission context; that is
not another full-PDF reading or external-source verification.

Initial observed checkout was commit
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`; local `origin/main` was
`649b12c7d1faa7601fde1019e913347c65a6634a`. The parent advanced the shared
checkout during this assignment. Final observed local `HEAD` and `origin/main`
were `779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
`f9baccbb54f51063b01a0859d2c10cdadfbd238b`. Those refs identify the surrounding
checkout; the readiness implementation and this test were then uncommitted.
This worker did not fetch or independently verify a remote publication.

The accepted producer and dependency bytes were observed unchanged from
initial reading through the final test. These identities, rather than a
concurrent checkout ref, identify the executed subject:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/capture_readiness.py` | 11,247 | 215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76 |
| `docs/CAPTURE_READINESS.md` | 14,203 | e3eb647244c62d600e58d37a83f99db165256e4a69cf89e210f354fc12b55b0b |
| `tools/capture_common.py` | 9,625 | e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2 |
| `tools/validate_capture.py` | 24,827 | a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af |
| `docs/CAPTURE_FORMAT.md` | 13,696 | 618c20e4c6d2b204c69cdad006d69bfd93638de7c6d711b230452fea78b88177 |
| `tests/test_capture_readiness.py` | 59,830 | 3297b34eeacea16e4a74c5fe79b1fb0fa6b029052ea7cfb43ba78b6c80e8b393 |

## Independent method and results

All fixtures are authored within the test from the public contracts. Neither a
producer private table nor a producer helper computes expected check paths,
categories, missing actions, states, reasons or summaries. The test has its own
literal 21-check and three-channel-check tables, fictional planned/hardware/
synthetic declarations, canonical JSON encoder and independent byte-hash,
value-node and container-depth calculations.

The fictional hardware fixture deliberately claims declarations whose artifact
and evidence locators do not exist. A readiness result may still say
`declarations_complete`; every physical/rights/integrity claim must remain
`not_established`. This tests the stated declaration-only boundary, not the
accuracy or legitimacy of those fictional claims. No acquired recording or
permission is invented as project evidence.

| Independent class | Methods | Executed coverage |
| --- | ---: | --- |
| `DeclarationSemantics` | 16 | Exact report keys; ordered literal check/action table; all unknown reasons including surrounding spaces and Unicode; supplied plan; complete and incomplete hardware/synthetic declarations; exactly scoped synthetic exemptions; uncalibrated clock/channels; independent channel gaps; split-role mapping without holdout claims; planned precedence; actual 16-channel ordering; derivative/raw context; original-byte identities; independent returned objects; one manifest read; Unicode relocation. |
| `InputAdmission` | 19 | Exact path API types; actual 65,536-byte input and excess pre-open rejection; strict UTF-8/BOM/duplicate/nonfinite/trailing/Unicode admission; numeric token and magnitude limits; actual 4,096-node and depth-16 generic JSON boundaries; v1 types, required keys, unknowns, calendar/status, calibration/units, channel order/count/IDs, portable paths and ancestry; missing/special/linked leaves; allowed parent aliases/hardlinks; controlled reparse flag; actual descriptor cleanup and observed in-place mutation. |
| `ReportAdmission` | 5 | Independently counted reduced byte/node/depth output limits, inclusive boundary and adjacent rejection without truncation; actual v1 maximum calibration number retention; no publication or stdout on report-limit rejection. |
| `CommandLineAndPublication` | 25 | All statuses and canonical text; five actual CLI processes with relative/absolute Unicode paths, foreign working directories and an ASCII terminal encoding; binary stdout/stderr; `argv=None`; exact argv types; missing/unknown/abbreviated/duplicate/empty options; help; failure preservation; publication before stdout; exact file/stdout bytes; existing file/input/hardlink/directory/dangling-link preservation; absent-parent handling; destination race; publication and cleanup failures; short writes/flush/stderr/help failures; cancellation. |

Actual native symlink, hardlink, FIFO, file mutation and descriptor checks
executed on this Linux runner; no capability test skipped. On a runner lacking
one of these operations, its explicit capability skip must remain visible.
The controlled reparse fixture confirms that its metadata hook is actually
reached; it is not a native Windows-junction execution result.

The one-read observation wraps the actual `os.open`, allows only the manifest
path, and records exactly one open. The artifact-check API is separately made
an assertion failure if invoked. Evidence, rights and artifact locators remain
unopened. The no-clobber cases inspect existing bytes and the resulting file
set, including absence of stray `.capture-json-*` files after completed cleanup.

## Resource and fault boundaries

- A real valid v1 manifest padded to exactly **65,536 bytes** succeeds with the
  independent original-byte hash. One additional whitespace byte rejects before
  an input descriptor opens.
- Both hardware and synthetic **16-channel** manifests execute the real
  **69-check** result. The 17-channel case rejects under unchanged v1 semantics.
- Exact **4,096 value nodes** and **container depth 16** are exercised as real
  strict JSON values that subsequently fail v1 shape admission. Their adjacent
  excesses reject during generic input admission. They are not reported as valid
  maximum-sized v1 manifests.
- The output's byte/node/depth guards are exercised at independently calculated
  **reduced** bounds around a real report. The production ceilings of 1 MiB,
  16,384 nodes and depth 24 are not claimed as generated full-size valid reports.
  No arbitrary malformed output is used as an expected readiness report.
- The metadata-only calibration-number boundary **1e12** is actually retained,
  unchanged and unconverted, in a fictional declaration. It qualifies numeric
  representation, not any physical scale or metrology.
- Descriptor-wrap failures are injected after a real descriptor opens. Actual
  `fstat` after each hook is removed confirms closure; cancellation retains its
  original `KeyboardInterrupt` type. The mutation test appends actual bytes
  during the bounded read and requires contextual input rejection.
- Cleanup-error hooks perform the real temporary unlink before raising. This
  tests disclosure and preservation when a cleanup operation reports failure;
  it does not prove arbitrary OS close/unlink states or crash recovery.
- A raced destination is actually created between temporary preparation and
  the non-replacing link. Its bytes survive. A completed published report also
  survives a later cleanup or stdout failure. Short writes intentionally retain
  partial stdout delivery, with a nonzero stream error; stdout is not an atomic
  transaction with file publication.

## Executed command and history

```sh
python3 -B tests/test_capture_readiness.py
```

Runtime: CPython **3.12.14**,
`Linux-6.18.57-x86_64-with-glibc2.41`. The first complete run passed all
65 methods in **0.552 seconds**, with no failures, errors or skips. A subsequent
harness inspection made the rejected generic path-like object's `__fspath__`
return a valid selected filename, strengthening that type-rejection fixture.
It did not change any expected value, producer source or contract, and was not
a correction for a failing production result. The final run passed all
**65 methods in 0.554 seconds**, again with zero failures, errors or skips.

No optional dependency, audio device, network access or actual hardware was
needed. Temporary fixtures and output files are scoped to test-owned temporary
directories. No shared CMake, native, renderer or hosted-CI gate was run by this
worker, and no such result follows from this command.

## Handoff

The parent can accept the two owned files, include this suite in the coherent
calibration integration gate, update actual session accounting and publish under
the standing guarded workflow. Future changes to readiness semantics or shared
JSON/v1 admission should rerun the affected acceptance against exact final
source bytes. Preserve explicit skips on platforms where a native operation is
unavailable; controlled hooks cannot close a missing platform gate.

Readiness remains a deterministic report of declarations and unknowns. Actual
artifact/audio verification, specimen identity, reviewed calibrations, permissions,
whole-corpus independence, acquisition suitability, physical fitting and musical
fidelity require their own retained observations. A complete declaration report
does not authorize or qualify any of those later actions.

## Integrator formatting observation

After acceptance, root removed one extra blank line at the test file end to
pass `git diff --check`. No assertion or executable statement changed. The
formatted integration test SHA-256 is `844ee714b2e0bf0392620e9731b6e0adf0c1a0e09d841a1877a51b7ea5e3d67e`;
the table above retains the exact independently delivered version. The next
frozen integration gate will execute the formatted file.

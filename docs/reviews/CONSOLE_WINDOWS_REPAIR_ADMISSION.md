# Console Windows repair admission

**A59, `/root/w10_a59`, wave 10, 17 November 2026 UTC: ADMIT the five
frozen source/test changes and their separately reviewed source-only and
affected local native qualification.** No source blocker was found within
this scope. Windows qualification and a new publication are not claimed.
The [machine-readable review][receipt] records
the exact inspected bytes, retained failures and remaining gates.

## Reviewed source and authority

I read the entire AGENTS and M0–M9 PLAN, console README/checkpoint, actual
ledger, current [publication receipt][publication], P1 frozen contract and the
relevant original evidence. Root owns integration, build, acceptance and
publication. A59 used read-only source, AST, byte, hash and retained-log
inspection, including immutable `git show`/`git diff`; A59 executed no build,
test, native process, CI retry or Git/index/ref mutation.

The original observed source is commit
`cf87a587d0002d106e5210b57a39fd1967245a8f`, tree
`2565ac86f9d31b7ab9d24d0d5353289c2359bf12`. The initial two-line Python
repair scope was explicitly expanded by root after A56 identified a latent
native-newline expectation mismatch. This admission covers that reviewed
expansion in the same two test files; it does not describe the final patch as
only two changed lines.

| Frozen reviewed file | SHA-256 |
| --- | --- |
| `apps/standalone/native_tests/test_standalone_performance_plate.cpp` | `a446f44bf67768aa9d9885084c1809c99102cb24413c7e640485ad17d5b3888d` |
| `tools/compare_performance_plate.py` | `46ce7721d2cb884b08f231249ffc0fc7f80a3d9a33657c0519216d68087671b2` |
| `tests/test_compare_performance_plate.py` | `97bf84741a1954fbd16ba5992862cdfef0393e50e8c5d3ba3b15b9ceda344bdd` |
| `tests/test_capture_standalone_interface.py` | `2ee08931dbef930c91d6b1f591592c65dec359c3de089c6bcf3841b686ab9ccc` |
| `tests/test_compare_header_material.py` | `6105d8a0da993b0e33700226d69165cedfc17d9ab9ac7e7fb5add0906e341c8d` |

Against the 587 input identities qualified for the published source,
**582 remain unchanged and exactly these five change**. Main, painter,
UiModel, Session, LibraryModel, core, parameter/state sources, CMake, workflows,
timeouts and instrumentation remain unchanged. The capture producer and real
header comparator also remain exact. This preserves the existing application
and gallery source boundary. A59 verified the current application's recorded
binary identity but did not make a new capture or execute the application.

## Original Windows failures remain failed

The retained [Core Windows log][core-log] belongs to run `44030833273`, job
`133862108675`, attempt 1, at the original commit above. It records **207/209**
passing CTests and two failed Python suites. Capture ran all **45 methods** and
reported three errors in the selected-scale/hash method, at scales 1, 3 and 10:
`KeyError: 'inputs/play-dimensional.b3uireplay'`. Header comparison ran all
**24 methods** and reported seven errors when its mock fell through to real
filesystem lookup of retained historical POSIX paths. The later Unicode
generator step was skipped. A56's [repair record][path-repair] retains the full
failure and source-only correction separately.

The retained [native Windows log][native-log] and [job review][native-review]
belong to run `44030833294`, job `133862108913`, attempt 1. MSVC reports
**C4702 at P1 fixture line 50**, promoted to C2220 under unchanged `/W4 /WX`.
The build fails before the acceptance step: **zero CTests execute**. Backend
verification, acceptance, post-acceptance source verification and successful
installed-package stages remain unrun. The failure-only title/header readers
do not run there, so the predecessor's copied-state mismatches still have no
new differing-leaf evidence or established cause.

Independent decompression reproduces raw log SHA-256 values
`c47eee99796358d5a7f0cba50883c62d63df69994e701b96d5758f68d1de3d95`
for Core and
`580ad243484bb9cc5d8759ce5392abfdb31735255256ba83f6212b50c9b22fcc`
for native. Later local passes do not replace these original results.

## Exact P1 helper and comparator boundary

The fixture changes only the false return from fallthrough into the explicit
`else` of the existing dependent `if constexpr`. The complete file grows from
75,570 to 75,587 bytes. Reversing its sole complete helper block reconstructs
every byte of original fixture
`4f1875270af71d08c27372944a4a9c8e4c10b6c31dbeb85b3841b6965915956c`.

For the helper-present specialization, the same predicate selects the same
call and arguments, once, followed by `true`. For the helper-absent
specialization, the dependent call remains discarded and the same `false`
result comes from the explicit else. The detector, call site and all fixture
case/workload/assertion code are otherwise identical. This is a source
argument; **no new helper-absent runtime execution is claimed**.

The comparator preserves all **40 original top-level assignments**, including
every original input pin, geometry and resource bound. **70 of 71 original
top-level function/class definitions are verbatim unchanged**. Only `execute`
changes to register the added admission metadata and call the two new source
admission helpers. The old UiModel admission still runs before the new fixture
check, and both complete before any native launch.

The new fixture route requires a Boolean mode and complete byte source. The
original complete fixture remains accepted in both modes. Any different file
first requires candidate-only mode, exactly one complete corrected helper
block and no original block, whole-file reversal to the unchanged original
pin, and the exact corrected complete-file digest. It verifies size/hash
against the registered input read and preserves final input-stability checks.
Changing only a new pin cannot admit malformed, relocated or unrelated bytes.
There is no fallback or source normalization.

Paired comparison retains the original fixture, original coherent UiModel
pair, genuine before executable/painter/admission, all 34 exports, 70-process
bound, clips, companions, repeated frames and strict transport limits. The
corrected fixture is explicitly refused in paired mode. Candidate-only
acceptance continues to claim only the canonical numerical/fixture gate.

All **62 numerical criteria** remain exact: twelve patches each require Y′
mean error ≤3, each RGB mean error ≤4 and residual-RMS error ≤1.2; aggregate
mean error remains the exact ratio `6324946007329/2837721600000`, and aggregate
RMS error remains `0.6968632531987865`. Patch coordinates/order, sufficient-sum
arithmetic, reference inputs and retained **28-pass/34-fail** baseline decisions
are unchanged. Source comparison covers the complete `numerical_screens`,
`frozen_references`, geometry, metadata and paired-check implementations.

All **45 old P1 test methods and their containing classes remain verbatim
unchanged**. Nine added methods cover original/candidate mode boundaries,
complete-byte/Boolean inputs, missing/duplicate/changed predicate/call/return
blocks, unrelated or relocated bytes despite repinning, complete-file pin
enforcement, read and later drift, and refusal before native launch. They do
not alter any existing oracle or skip an old method.

## Two Python test files preserve strict expectations

The capture test now constructs its expected key with
`str(Path("inputs") / filename)`, matching the unchanged inventory producer's
`str(path.relative_to(root))`. It still addresses exactly one required entry;
it does not accept an alternate key or bypass the missing-entry failure.

The unchanged producer writes with
`Path.write_text(script, encoding="ascii")`, whose default text newline mode
translates output LF to the native separator. The test's new
`script.replace("\n", os.linesep).encode("ascii")` therefore computes the
expected disk bytes before the same SHA-256 equality assertion. The actual
recorded bytes are not normalized, no alternate digest is accepted, and all
frozen returned-replay hashes remain unchanged. This additional mismatch is
**source-derived and latent**: the original Windows KeyError occurred before
the hash comparison. Neither that log nor the Linux pass observes a Windows
hash failure or proves new Windows byte output.

All 45 capture methods remain, with only this expected path/disk-byte method
changed and `import os` added. All scales, independent deadlines, replay
delivery, typed semantic assertions and refusal methods retain their source.

The header test changes only mock dictionary insertion keys from the raw
retained string to `str(Path(row["path"]))`. Its existing lookup wrapper
already constructs `Path(source)`, so both sides now use the same native
representation. Each `deepcopy(row)` retains the original path, bytes and hash
fields. Unknown paths still take the unchanged `real_identity` fallback.
All **24 test method bodies**, all original pins and the real comparator's
baseline/refusal predicates remain identical. The prior **78 refusal cases**
are retained by unchanged bodies; this review does not claim a newly
instrumented count. Neither file adds a skip or broad exception handler.

## Reviewed source-only and affected native executions

The [root source-only P1 receipt][p1-unit] and complete log show **54/54 methods**
passing, with no failures, errors or skips, in 0.906 seconds internally
(1.250853054 seconds external wall). All three frozen P1 source identities
are unchanged through that execution.

The [A56 source-only receipt][path-unit] and both complete logs show one
invocation each: **45/45 capture methods** and **24/24 header methods**, with
no failures, errors or skips. Their internal times are 1.813 and 0.629 seconds;
external walls are 2.148579487 and 0.975426857 seconds. Log hashes, method lines
and source identities agree with the receipts. Native/image CLI boundaries
remain mocked, and no historical binary revalidation is inferred.

Root's terminal [affected qualification][local-qualification] rebuilds the P1
fixture in **13.283043498 seconds**, then passes **3/3 CTests** in
**28.239448376 seconds**, with no failures, errors or skips:

| Affected CTest | Observed result |
| --- | --- |
| `python_test_repository_integrity` | 41 Python methods pass |
| `test_standalone_performance_plate` | 34 cases, 53,648 checks, 111 paintings and 61 helper probes pass |
| `test_standalone_performance_plate_numerical` | Candidate-only 191 checks and all 62 numerical screens pass |

I verified the build/CTest log digests, JUnit, full detail output and all **587
current source pins**. The [retained numerical report][p1-runtime] identifies the exact
corrected fixture, its original whole-file reversal and the unchanged UiModel
transition. Its helper is present; it contains no new helper-absent execution.
Independent byte comparison confirms identical retained pre-repair and rebuilt
Linux fixtures, both with digest
`60e951c907bf177b190e1a8abee9246a472b5e1d8ddc957b5ba5e2ce5179ecd5`;
the retained pre-repair source is also byte-identical to the original published
fixture. This pre-repair combined-source binary is separate from the older
genuine pre-P1 paired baseline. The application independently
matches unchanged digest
`3bb46f2ff0a830935b5f1122116b7ff457f5e8532ed1f7860843c237d09a89e9`.
All inputs remained stable during root's run. The three source-only suites
above were not rerun as CTests and are not included in this three-test count.
The retained numerical directory contains the original report and four zlib
streams, 1,152,721 bytes in total. I verified the exact copy against its
original temporary report and all compressed/raw stream digests; root's
[retention receipt][p1-retention] records the lossless copy without another run.

These Linux observations establish neither MSVC compilation, new Windows
execution, helper-absent runtime behavior nor a repaired whole platform
matrix. They do not become a full-suite or new paired-comparison result.
The documentary pass precedes final A59 additions; root still owes final
documentation integrity after all worker records are complete.

## Actual ledger prefix and next gates

At this inspection, the actual ledger has **59 distinct records**, **56
accepted**, and A56/A57/A59 running; A60 has no record. Waves 1–9 each contain
six accepted deliveries. Wave 10 has A55 and A58 accepted plus those three
running records. All 56 accepted notes match their recorded SHA-256, meet the
documented text floor, use ordinary distinct paths and have nonblank root
review. The checker source counts only actual records and requires all sixty
accepted notes across ten complete waves for strict closure. A59 did not run
the checker or prove external dispatch/concurrency from those records.

A concrete navigation inconsistency was reported: CHECKPOINT and ROOT_NEXT_QUEUE
initially said 58 dispatched/55 accepted with A59 undispatched. Root corrected
both current records to the observed 59/56 prefix. The dated publication
receipt correctly retains its historical 58/55 snapshot and stays immutable.
**Strict sixty-worker closure remains open**; planned A60 work and follow-ups
supply no credit.

Root must wait for all original exact-source jobs before the next same-ref
push, preserve all failures, publish accepted
source with a fresh expected remote head and no force, and independently
verify commit/tree/parent/contents. Fresh Windows Core/native execution must
reach the formerly failed gates and the previously unrun diagnostic readers;
all new-source platform families need their own observed results. A60 actual
dispatch, all root acceptances, strict closure and final documentary integrity
remain required. Native browser/main wiring, physical/device/accessibility and
release gates remain separate. **Literal whole-interface 1:1 remains unmet and
unwaived.**

[receipt]: ../development/2026-11-16-console-completion/reports/A59-windows-repair.json
[publication]: ../development/2026-11-16-console-completion/reports/implementation-publication.json
[core-log]: ../development/2026-11-16-console-completion/reports/A56-core-hosted/core-cf87a587-job-133862108675.log.gz
[native-log]: ../development/2026-11-16-console-completion/reports/A57-native-hosted/job-133862108913.log.gz
[native-review]: ../development/2026-11-16-console-completion/reports/A57-native-hosted/job-133862108913-review.json
[path-repair]: ../development/2026-11-16-console-completion/reports/A56-core-hosted/windows-portability-repair.json
[path-unit]: ../development/2026-11-16-console-completion/reports/A56-core-hosted/windows-portability-python-qualification.json
[p1-unit]: ../development/2026-11-16-console-completion/reports/p1-helper-source-tests.json
[local-qualification]: ../development/2026-11-16-console-completion/reports/windows-repair-local-qualification.json
[p1-runtime]: ../development/2026-11-16-console-completion/reports/windows-repair-p1-candidate/report.json
[p1-retention]: ../development/2026-11-16-console-completion/reports/windows-repair-p1-retention.json

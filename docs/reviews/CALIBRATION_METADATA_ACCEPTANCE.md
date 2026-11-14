# Independent confined metadata-read acceptance

## Decision and scope

Assignment **44**, `/root/cal_w8_a44`, logical wave **8**, independently clears
assignment 43's minimal descriptor-sized read for integration. The new focused
suite passes **24/24 methods**. The six unchanged dependent suites pass another
**333 methods**: corpus admission 59, corpus 47, job 81, study 61, replay 69 and
installation 16. All **357 methods** pass without skips on the observed Linux
runtime. No production defect was found. Root owns final coherent integration,
test discovery, shared status, commit and push.

The change is confined to the comment and request size in
`capture_corpus._read_confined_bytes`: after the existing path/descriptor binding
and inclusive size admission, request `before_fd.st_size + 1` instead of
`max_bytes + 1`. The consumed bytes, admission ceilings, exact-length comparison,
descriptor checks, final leaf/parent verification and cleanup ownership remain
unchanged. The unrelated common reader remains unchanged.

This is offline M0/M8 engineering under [CALIBRATION_SCOPE.md](../CALIBRATION_SCOPE.md).
It changes no model, sound, public control, saved state, acquisition protocol or
physical evidence claim. The [project plan](../PLAN.md) and extracted atlas
pp. 355, 364 and 484–486 provide the original-identity, retained-outcome and
change-control basis. This assignment consulted those relevant text pages; it
does not count another complete PDF reading.

## Frozen argument reviewed before acceptance

The exact marker block in the
[allocation protocol](CALIBRATION_METADATA_ALLOCATION.md) is **5,645 UTF-8 bytes**,
SHA-256 `f045d9ef6a5abaa7217d440ea32ca84d734b0af46efb83061da1fec563a5a277`.
Assignment 44 verified that identity and sent initial clearance before running
its acceptance. Later producer result prose is outside that frozen marker block.

Let the already observed, admitted descriptor size be `n`. Admission guarantees
`0 <= n <= max_bytes`. Reading at most `n + 1` preserves one extra byte as a
witness: growth visible during consumption cannot silently return the original
`n`-byte prefix. An observed result must still have exactly `n` bytes and remain
within the caller's cap. Truncation and short reads therefore still reject.
The descriptor stamp after consumption, final pathname stamp and every admitted
parent identity remain necessary: returned length alone does not establish an
unchanged file. The job/study/replay snapshot layers retain their first
observations through their separately documented final boundaries.

The baseline is commit `16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`. Its corpus is **39,220 bytes**,
SHA-256 `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba`.
The candidate corpus is **39,312 bytes**,
SHA-256 `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded`.
An independent byte diff against the frozen source shows only the intended
comment and single read argument. All nine other runtime modules match the
baseline byte for byte. The baseline commit alone does not identify this changed
working source; the exact candidate inventory below does.

The full [corpus read contract](../CAPTURE_CORPUS_CONTRACT.md),
[job snapshot contract](../CAPTURE_JOB_CONTRACT.md),
[shared study snapshot contract](../CAPTURE_STUDY.md) and
[replay boundary](../CAPTURE_REPLAY.md) continue to apply. In particular, archives
and installed sources must remain quiescent. These observed-change checks do
not provide an atomic multi-file transaction or detection of deliberately
restored changes between observations.

## Independently authored cases

The maintained suite is
[`tests/test_capture_metadata_read.py`](../../tests/test_capture_metadata_read.py).
It has 21 reader/snapshot/failure methods and three pipeline methods. Expected
bytes and hashes come from literal private inputs, not from a previous producer
result. Fixtures resolve temporary roots before constructing hook paths.
Every injected operation records an event that must be reached. Successful and
rejected stream paths verify actual descriptor closure. Repository sources are
never edited; the source-difference fixture uses a complete private module copy
and fresh interpreter processes.

| Concern | Independent observation |
| --- | --- |
| Original bytes and hashes | Empty bytes, one byte, a noncanonical UTF-8/CRLF payload and an 8 KiB byte pattern return exactly their original bytes under equality, moderately larger and 16 MiB ceilings. The job observation hashes those actual bytes. Twelve reached stream witnesses each request original size plus one. |
| Inclusive admission | An empty file is admitted at zero; equality is admitted. A one-byte file at zero and a larger file one byte over cap reject before any confined open. Actual growth between path and descriptor admission exceeding the cap rejects before read. |
| Descriptor-derived request | Actual growth after pathname observation but before descriptor admission changes the witnessed request to the descriptor's newly observed size plus one. Final pathname verification still rejects the changed file. |
| Extra growth byte | Actual append after descriptor admission produces exactly the original prefix plus one extra byte under both tight and loose caps; both reject. Append after consumption rejects even when the returned length still matches. |
| Truncation and short result | Actual truncation after admission and a deliberately shortened stream result both reject. The short-result case leaves original file bytes unchanged. |
| Same-size changes | Actual same-size content mutation with an asserted observable timestamp change rejects at descriptor recheck. A metadata-only change after close rejects at final pathname verification. |
| Replacement | A same-byte leaf replacement between pathname observation and open rejects before read. A same-byte replacement after close also rejects. Separate root and descendant-parent swaps retain the same precreated hardlinked leaf and its complete stamp, isolating rejection of the changed directory identity. |
| Final snapshots | A retained job snapshot rejects an observable metadata change after the confined read has returned. Unrelated sibling creation preserves the admitted original bytes and passes. |
| Failure and cleanup | Actual stream closure accompanies ordinary read failure, `KeyboardInterrupt` and `SystemExit`. Close failure never becomes successful return. Failed stream construction releases its owned leaf; a simultaneous cleanup error retains both reasons; cancellation retains its original exception object and exposes the cleanup cause. |
| Fresh public composition | Three real job CLI executions retain pass/inconclusive/failed statuses and literal RMS errors 0.25/0.25/0.5 FS. Each saved report replays as a match without changing its engineering outcome. The three-job study remains failed and retains all three complete nested outcomes. |
| Changed source context | A saved study from a private coherent source copy remains byte-for-byte unchanged after a harmless comment changes only that copy's corpus source. Fresh replay explicitly returns mismatch, `same_runtime: true`, `same_tool_sources: false`, and failed underlying statuses. |

The source-only changed-comment regression tests the continuing provenance
contract without hardcoding a historical repository location into the maintained
suite. The separate exact before/after-source experiment below qualifies the
actual optimization against its original saved report.

Existing corpus admission supplies the broader malformed JSON, byte/count limits,
regular-file, symlink/reparse, identity, directory traversal and error-context
matrix. Existing job, study and replay suites retain the complete publication,
canonical encoding, original-policy-byte, all-input snapshot and status-precedence
coverage. They were executed against the changed common dependency, not credited
from historical results. Installation exercises the complete 57-file package,
including relocation after private source/build deletion.

## Executed commands and results

Working directory was `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Runtime was CPython **3.12.14**, Linux x86_64,
`Linux-6.18.57-x86_64-with-glibc2.41`. The compiler/toolchain identity embedded in
Python was `[Clang 22.1.3]`. Direct installation tests used the exact available
CMake executable; they did not build a native target.

```sh
python3 -B tests/test_capture_metadata_read.py
python3 -B tests/test_capture_corpus_admission.py
python3 -B tests/test_capture_corpus.py
python3 -B tests/test_capture_job.py
python3 -B tests/test_capture_study.py
python3 -B tests/test_capture_replay.py
HAMMOND_TEST_CMAKE=/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake python3 -B tests/test_capture_install.py
```

These independent commands ran concurrently in their private fixtures. The
per-suite elapsed values below are unittest diagnostics, not latency evidence.

| Suite | Methods | Result | Reported elapsed |
| --- | ---: | --- | ---: |
| Metadata read | 24 | Pass, no skips | 1.651 s |
| Corpus admission | 59 | Pass, no skips | 1.804 s |
| Corpus | 47 | Pass, no skips | 1.242 s |
| Job | 81 | Pass, no skips | 5.277 s |
| Study | 61 | Pass, no skips | 6.584 s |
| Replay | 69 | Pass, no skips | 8.911 s |
| Installation | 16 | Pass, no skips | 7.819 s |

### Initial harness failure retained

The first new-suite version was **25,771 bytes**, SHA-256
`f8995ae63f6a2eccc1f38405ae239c467cd44daf1eba62666b573e97d1ac385b`.
Its first run executed 24 methods in 0.992 s and exited 1. The three status
subcases of `test_fresh_jobs_and_replays_preserve_all_three_engineering_outcomes`
raised `KeyError: 'comparison'`: the test looked at the report root instead of
the contract's `evaluation.comparison`. All other methods completed without
failure. The only correction was that nested lookup. No producer code,
expectation, threshold or fixture outcome changed. The corrected suite identity
is recorded below. This test-harness failure is not a producer regression and
is not omitted from the acceptance history.

## Independent review of the allocation evidence

Assignment 40's [original resource profile](CALIBRATION_RESOURCE_PROFILE.md)
correctly presents the old replay peak as a candidate for investigation, without
asserting component attribution. Assignment 43 subsequently froze the controlled
protocol and retained the complete before/after reports and every sample.

Assignment 44 independently checked the final
[`allocation_comparison.json`](../../examples/benchmarks/capture-toolchain-v1/allocation_comparison.json):
**304,390 bytes**, SHA-256
`791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc`.
Its collector is **18,785 bytes**, SHA-256
`4cef019bece4e2625fd3934202c7258a4c5d34afc735c06221c47cbe08f43543`.
The checks compared both ten-module inventories with actual baseline/candidate
bytes, the frozen protocol and collector identities, all 16 original fixture
files totaling 32,831 bytes, all twelve traced samples, both complete canonical
reports, their replay summaries and the predeclared decision arithmetic.

| Operation | Before peaks, bytes, in original order | After peaks, bytes, in original order | Paired reductions, bytes |
| --- | --- | --- | --- |
| Isolated original-report read | 16,785,861; 16,785,861; 16,785,861 | 128,603; 128,603; 128,603 | 16,657,258; 16,657,258; 16,657,258 |
| Complete fresh-study replay | 16,789,839; 16,789,831; 16,789,823 | 1,304,735; 1,304,386; 1,304,888 | 15,485,104; 15,485,445; 15,484,935 |

Every after peak is below every before peak for its operation, satisfying the
frozen local resource rule. The untraced request witnesses are **16,777,217**
before and **119,424** after, each consuming the same original **119,423 bytes**.
The collector's one-frame tracing begins after imports/setup/warmup and retains
the returned object when measuring current and peak traced bytes. Neither the
witness instrumentation nor separate serialization is inside its measured call.
This reviewer inspected and recalculated those retained observations; it did
not rerun the tracing experiment or relabel producer measurements as its own.

The producer's first successful comparison was followed by collection-only
output-path/explicit-protocol handling refinements and a second successful
comparison. The [producer review](CALIBRATION_METADATA_ALLOCATION.md) retains
both sets and their collector identities. Production source, frozen criterion
and report content did not change between those runs. The final artifact above
is the one independently audited here.

### Exact old-report and current-source reproduction

An additional independent standard-library harness copied all ten modules from
the frozen baseline and candidate into separate private directories. It copied
the retained 16-file demo once, then invoked **five fresh `python3 -B -S`
processes** from a foreign working directory:

| Source copy | Public command | Expected and observed exit/outcome |
| --- | --- | --- |
| Before | `capture_study.py --input demo/study.json` | 1, complete failed study |
| Before | `verify_capture_report.py --kind study --input demo/study.json --report before.json` | 0, exact match with failed engineering result |
| After | `capture_study.py --input demo/study.json` | 1, complete failed study |
| After | `verify_capture_report.py --kind study --input demo/study.json --report after.json` | 0, exact match with failed engineering result |
| After | `verify_capture_report.py --kind study --input demo/study.json --report before.json` | 1, explicit mismatch with changed-source context |

The actual harness passed absolute private paths to those options. Both freshly
emitted reports and all three summaries exactly reproduced the producer's
retained canonical bytes/values. Every original source, copied source, archive
file and saved report remained unchanged. The temporary copies were removed;
the identical complete reports remain in the versioned comparison artifact.

| Complete report | Bytes | SHA-256 |
| --- | ---: | --- |
| Original baseline study | 119,423 | `6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727` |
| Fresh candidate study | 119,423 | `71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736` |

The old-report replay remains `mismatch`, with `same_runtime: true` and
`same_tool_sources: false`; both engineering statuses remain `failed`.
Changing a source hash is an expected visible report difference even when all
analysis results agree. No old report is rewritten to obtain a match.

For the experimental content comparison only, independently removing exactly
`/tool_sources` and `/jobs/0/report/tool_sources`,
`/jobs/1/report/tool_sources`, `/jobs/2/report/tool_sources` produces identical
114,760-byte canonical projections, SHA-256
`760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479`.
No other value is removed or normalized. Public replay still compares the whole
original report, including every source observation. The projection is never
passed to public replay or described as a replay match.

## Exact qualified source and test identities

The coherent source set was checked against the baseline and again after
acceptance. Only the corpus module differs from the baseline.

| Runtime module | Bytes | SHA-256 |
| --- | ---: | --- |
| `capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `capture_corpus.py` | 39,312 | `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded` |
| `capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| `capture_readiness.py` | 11,247 | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| `capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `make_capture_demo.py` | 22,329 | `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` |
| `validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |

| Test file under `tests/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `test_capture_metadata_read.py` | 25,785 | `afc907049aba369aa477bd459dbdd7a29b8a1eed7dfd933472c723c3ec2caf3a` |
| `test_capture_corpus_admission.py` | 54,290 | `6fdbc511bfd96e9767c3dd78366c7abb75b061b263295c4fae62f0f051ac36f6` |
| `test_capture_corpus.py` | 52,143 | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |
| `test_capture_job.py` | 78,683 | `0d74f5bff69bb094165992891d3da0c61b73c0543e21e311b36e792ec90e4f12` |
| `test_capture_study.py` | 70,397 | `19f3c58d91026292d353434b6c0ac0348361c7a4f645b7d62f71c470c45dd8c6` |
| `test_capture_replay.py` | 62,858 | `ad4e364794e8fffda5e2959f90c046def0a0d6471b3ff049e2b9a93ea03e9d55` |
| `test_capture_install.py` | 34,023 | `a797443fe7d208bbdaebedae836edca988524d8371938dd95e9368738f26bb74` |

## Integration handoff and limits

Root should include the new maintained suite in normal discovery, integrate the
minimal producer change with these acceptance files and the producer's retained
experiment, and qualify one coherent SDK-free Release source snapshot before
publication. Record the resulting commit/tree and observed remote result in the
shared handoff. Preserve assignment 40's original old-source resource artifact.

This acceptance establishes the specified local software behavior and the narrow
retained allocation observation. It does not establish RSS, all native allocation,
latency, callback deadlines, a hostile-filesystem guarantee, maximum-scale scans,
native Windows/macOS behavior or a cross-platform performance guarantee. Native
platform rechecks remain distinct gates. Synthetic pass/fail/inconclusive fixtures
establish no specimen, permission, calibrated physical scale, untouched holdout
history, listening result or physical fidelity. All ten physical/evidence claim
fields in the exercised job/study/replay outputs remain `not_established`.

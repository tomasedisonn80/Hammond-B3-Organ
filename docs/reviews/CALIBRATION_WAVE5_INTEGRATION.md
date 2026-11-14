# Calibration wave 5 combined integration

## Frozen source and observed result

The first five logical waves contain **30 accepted distinct assignments**. Root
committed their completed tools, independent numerical/schema work and observed
Windows/macOS portability repairs, then inspected and merged remote main
`0085e338388f2c7516a7d455f11692b94e9451f4`. That concurrent standalone checkpoint
contains the reviewed reader-progress repair, installation configuration guard,
retained bundled notices and its actual benchmark matrix. Its ownership and
historical evidence remain intact.

The combined frozen source is local commit
`fd0fb58d2f882aa76c7e40e510f44766f762727c`, tree
`3329cf68bb9ea84479e254934778935bb5c44773`. Root extracted it with `git archive`
into a separate source directory before configuring. Active study, demo, replay
and installation worker files are excluded. No live changed headers were mixed
with this build's objects.

Configure and the complete default Release build succeeded. The unfiltered
CTest gate passed **99/99 suites in 180.68 seconds**, with zero failed suites.
The standalone concurrency suite passed in 0.25 seconds. This result includes
the three new job/readiness/numerical suites and all earlier capture, core,
legacy tool and SDK-free standalone support suites. Suite counts are not
individual method counts or an assertion that every native capability ran.

The toolchain was GCC 14.2.0, CMake/CTest 4.4.4 and Python 3.12.14 on Linux
x86_64. The source was frozen on 2026-11-13 UTC and the observed gate completed
across the 2026-11-14 UTC boundary. The session identity remains its original
`2026-11-13-calibration`; no worker is recounted because the date changed.

## Reproduction

From the repository's parent workspace, using the available CMake/CTest:

```sh
cmake -S /workspace/scratch/c9f3ead4c910/w5-combined-source -B /workspace/scratch/c9f3ead4c910/w5-combined-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /workspace/scratch/c9f3ead4c910/w5-combined-build --parallel 2
ctest --test-dir /workspace/scratch/c9f3ead4c910/w5-combined-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w5-combined-ctest.xml
```

The actual CMake binary was
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`;
CTest is its sibling. Configure selected the primary runtime Python 3.12.
The full build created renderer inputs before the legacy analyzer checks.
Native VST3 and the SDL device executable were disabled; their separate hosted
results must not be attributed to this SDK-free gate.

## Scope, retained failures and continuation

The accepted public job source in this snapshot is SHA-256
`3ffe39f5723a6a3af779ba33b799e72bdeed9d60365c5df9a8146b8467aec230`.
It includes the admitted corpus-core seam and original-policy-byte preservation,
whole-corpus auditing, selected-window comparisons and final input/source checks.
The later study's private job extension is excluded from these 99 suites and
requires its separate coherent focused gate.

The independent readiness suite retains 65 methods; numerical acceptance adds
19 methods with high-precision independently calculated expectations. The schema
review retains 665 actually executed cases and the repaired v1 string-pattern
boundary. Generic shape validation remains distinct from byte and semantic
admission. No runtime dependency was added for the optional schema audit.

The [hosted portability follow-up](CALIBRATION_HOSTED_PORTABILITY.md) preserves
the failed general Release jobs at public `779fb6e`, their actual decoded logs,
original reproductions, root's UTF-8/LF writer fixes and canonical-path fault
fixtures. The repaired final audio/corpus suites execute here. Audio admission
has 63 methods with two explicit capability skips; corpus admission has 58.
The integrated standalone repair resolves the local scheduling assertion in this
frozen run. Fresh hosted Windows/macOS/Linux results are still required before
clearing the corresponding hosted failures.

The frozen retained-accounting check with `--expected-complete 30` reports 30
complete, four running, 26 planned, 34 distinct actual identities and no errors.
Later live acceptance may have advanced beyond this checkpoint; its ledger
must not be substituted for the exact frozen snapshot. External dispatch
attestation remains false in the checker: root's actual orchestration, not a
JSON row or successful consistency check, supplies the dispatch evidence.

No physical recording, specimen identity, permission clearance, calibrated
uncertainty, model fitting, untouched holdout chronology or fidelity verdict
is established here. Continue the independently accepted study/demo through a
new focused source gate, then replay, installation and operational qualification.
Preserve all earlier failed/inconclusive outcomes and exact tested identities.

## Retained local observation identities

| Observation | Bytes | SHA-256 |
| --- | ---: | --- |
| w5-combined-configure.log | 706 | c8b234eb3705815563d093ad7c6afb68e4e924fbc51865c2c925d87f324935d2 |
| w5-combined-build.log | 12141 | fc7e1c8b0321cbe66f8d2b315fd5a830c48c22d3c8c53618f09c6f156592bd82 |
| w5-combined-ctest.log | 12267 | 58903355c59628bcff8fca45733ff2422bd52d92a5ca920f9f7dd68604e16f76 |
| w5-combined-ctest.xml | 50151 | 8aee4fdbaa35c0486d5bb3e9652557f017700284f6a90b052d30357207fcb87d |

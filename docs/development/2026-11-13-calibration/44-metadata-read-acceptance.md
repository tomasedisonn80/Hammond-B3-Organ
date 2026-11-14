# Assignment 44 — independent metadata-read acceptance

Actual agent: **`/root/cal_w8_a44`**. Logical wave: **8**. Work performed on
**2026-11-14 UTC** in the independently counted 2026-11-13 calibration session.
This is one new assignment, separate from producer 43 and resource reviewer 40.

## Owned deliverable and result

Owned and edited only:

- `tests/test_capture_metadata_read.py`
- `docs/reviews/CALIBRATION_METADATA_ACCEPTANCE.md`
- `docs/development/2026-11-13-calibration/44-metadata-read-acceptance.md`

The [complete review](../../reviews/CALIBRATION_METADATA_ACCEPTANCE.md) clears
the minimal reader change for root integration. The independently authored
focused suite passes **24/24 methods**. Six unchanged dependent suites pass
**333/333** additional methods, totaling **357**, with **no skips**. No production
defect was found. Root owns shared documents, assignment accounting, CMake/test
discovery, integration, commit and push. This agent performed no Git mutation,
production edit, protocol edit or benchmark-artifact edit.

## Scope, source and initial review

Read the standing instructions, calibration scope/handoff, current session
manifest, project plan and relevant original-byte/read/snapshot/replay contracts.
Inspected the complete confined reader, descriptor ownership helpers and retained
snapshot composition, existing corpus admission cases and the dependent suites.
Consulted extracted atlas pp. 355, 364 and 484–486 for identity, uncertainty,
retained failure and change-control requirements. This is not another complete
PDF reading. Scanner, rotary, standalone and physical acquisition stay outside
this assignment.

Initial HEAD was `16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`. That frozen baseline contains corpus
**39,220 bytes**, SHA-256
`1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba`.
The qualified changed corpus is **39,312 bytes**, SHA-256
`751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded`.
An exact independent diff found only the intended comment and
`source.read(before_fd.st_size + 1)` argument after existing inclusive admission.
The other nine runtime modules remained identical; their complete inventory and
all seven test identities are in the review.

Verified the frozen allocation-protocol marker block before acceptance:
**5,645 bytes**, SHA-256
`f045d9ef6a5abaa7217d440ea32ca84d734b0af46efb83061da1fec563a5a277`.
Sent clearance of the bounded descriptor-size-plus-extra-byte argument to root
and producer 43. The extra byte, exact consumed length, descriptor stamp,
pathname/parent checks and continuing snapshot boundaries were all required;
allocation reduction alone was never the acceptance criterion.

## Independent work and verification

The new suite uses actual private files, canonical temporary roots and reached
fault hooks. It checks original bytes/hash under twelve payload/cap combinations;
empty/equality/over-cap behavior; observed descriptor-size requests; growth before
and after admission/consumption; truncation and short read; same-size content and
metadata changes; leaf/root/parent replacement; unchanged siblings; retained
snapshots; descriptor release; simultaneous primary/cleanup errors; and preserved
`KeyboardInterrupt`/`SystemExit` cancellation. Root/parent swap cases keep an
already linked leaf's complete stamp unchanged, isolating the directory guard.

Public CLI checks retain all three literal job outcomes and errors, the complete
failed mixed study, matching fresh replay and all ten `not_established` claims.
A private copied-source comment change produces an explicit source mismatch
without changing the original saved report. No live repository source is mutated.

Commands were executed from
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`:

```sh
python3 -B tests/test_capture_metadata_read.py
python3 -B tests/test_capture_corpus_admission.py
python3 -B tests/test_capture_corpus.py
python3 -B tests/test_capture_job.py
python3 -B tests/test_capture_study.py
python3 -B tests/test_capture_replay.py
HAMMOND_TEST_CMAKE=/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake python3 -B tests/test_capture_install.py
```

Results, respectively: **24, 59, 47, 81, 61, 69, 16 methods passed**, each exit 0,
no skips. The corrected focused run took 1.651 s; dependent-suite diagnostics
were 1.804, 1.242, 5.277, 6.584, 8.911 and 7.819 s. Commands ran concurrently
with private fixtures; elapsed values are not performance measurements.
Runtime was CPython 3.12.14, Linux x86_64,
`Linux-6.18.57-x86_64-with-glibc2.41`. Installation tested the real 57-file source
package without a native build, including relocation after private source/build
removal. This is local execution, not native Windows/macOS evidence.

### First harness failure retained

Initial test file: **25,771 bytes**, SHA-256
`f8995ae63f6a2eccc1f38405ae239c467cd44daf1eba62666b573e97d1ac385b`.
Its first run executed 24 methods in 0.992 s and exited 1 with three subcase
errors in one method: `KeyError: 'comparison'`. The test incorrectly looked for
comparison at the job report root. The frozen contract places it under
`evaluation.comparison`; changing only that lookup fixed the harness. No other
method failed, and no producer code, threshold or expected outcome changed.

Final suite: **25,785 bytes**, SHA-256
`afc907049aba369aa477bd459dbdd7a29b8a1eed7dfd933472c723c3ec2caf3a`.
The successful 24-method run and all dependent-suite results qualify this version.

## Independent experiment audit and exact-source reproduction

Audited producer 43's final canonical comparison artifact against actual files:
**304,390 bytes**, SHA-256
`791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc`.
Its final collector is **18,785 bytes**, SHA-256
`4cef019bece4e2625fd3934202c7258a4c5d34afc735c06221c47cbe08f43543`.
Checked both source inventories, all 16 fixture files/32,831 bytes, protocol,
collector, twelve samples, paired reductions, every retained complete report,
fresh/old replay summary and the exact four source-field projection paths.
The producer review separately preserves its initial successful collection and
the later collection-only output/protocol-path guard refinements. The runtime
source and predeclared criterion did not change between those collections.

Retained final isolated peaks are old `[16785861, 16785861, 16785861]`, new
`[128603, 128603, 128603]`; complete replay peaks are old
`[16789839, 16789831, 16789823]`, new `[1304735, 1304386, 1304888]` bytes.
Every after peak is below every before peak for that operation. This agent
recalculated the retained decision but did not repeat the allocation trace or
claim those producer samples as independent measurements.

A separate inline standard-library harness made coherent private before/after
module copies and executed five fresh `python3 -B -S` CLI processes: old study,
old fresh replay, new study, new fresh replay, and new replay of the unchanged
old report. All expected exits and complete reports/summaries reproduced exactly.
Original/copied modules, every archive byte and both saved reports were checked
unchanged after execution. The original study is 119,423 bytes, SHA-256
`6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727`;
the candidate study is 119,423 bytes, SHA-256
`71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736`.
Both own-source replays match and preserve failed engineering status. The
unchanged old report under the new source explicitly mismatches with equal
runtime and unequal tool sources. It is never rewritten.

Independently removing only the four declared `tool_sources` arrays gives equal
114,760-byte experimental projections, SHA-256
`760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479`.
Public replay continues to compare all original canonical bytes, including
source identities. The projections are not replay inputs or replacements for
the complete reports retained in the artifact.

## Next step and limits

Root should accept the substantive result, include the new suite in ordinary
test discovery, qualify a coherent integration snapshot and publish under the
standing no-force workflow. Retain the precise tested tree and actual remote
result in shared status/handoff. Keep assignment 40's old-source resource report
and all producer/acceptance failure history unchanged.

No RSS, latency, callback deadline, maximal-workload scan, hostile-filesystem
guarantee or native Windows/macOS result is claimed. No hardware acquisition,
calibrated scale, rights, independent holdout chronology, listening or fidelity
gate is closed. This is an independently qualified local reader optimization
with unchanged public engineering and evidence semantics.

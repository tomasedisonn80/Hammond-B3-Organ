# Assignment 43 — confined metadata-read allocation

Actual worker: **`/root/cal_w8_a43`**, assignment **43**, logical wave **8**,
session `2026-11-13-calibration`. This is one actual newly dispatched worker.
Execution occurred on 2026-11-14 UTC. No additional agent was spawned or counted.

## Owned paths and scope

Owned exactly:

- The minimal read-size expression/comment in
  `tools/capture_corpus.py::_read_confined_bytes`.
- `docs/reviews/CALIBRATION_METADATA_ALLOCATION.md`.
- `examples/benchmarks/capture-toolchain-v1/check_allocation.py`.
- `examples/benchmarks/capture-toolchain-v1/allocation_comparison.json`.
- This assignment note.

No common/job/study/replay/audio implementation, frozen public contract, test,
worker-40 artifact, shared status, ledger, CMake file or Git ref was changed.
Root owns acceptance, shared handoff integration, commit and push. Assignment 44
owns independently written semantic acceptance and relevant regression execution.

Read standing `AGENTS.md`, calibration scope, README/current status/next steps,
operational handoff, M0–M9 plan and recent development context. Read the corpus,
job and replay confined-reader/snapshot requirements and actual descriptor
ownership, binding, final leaf/parent and complete snapshot implementations.
Read assignment 40's retained resource review, collector and results. Freshly
read the extracted atlas pp. 449 and 484–486: retain original evidence, freeze
criteria and keep code/data identities and physical/product gates separate.
This worker does not claim another complete PDF reading; six earlier actual
assignments own that session-wide work.

## Coherent source and exploratory baseline

At start, the repository HEAD was
`16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`; fetched `origin/main` was
`183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`.
The integrator had frozen the complete before source in
`/workspace/scratch/c9f3ead4c910/w7-installed-source` for a separate full gate.
This assignment never modified that snapshot or claimed its pending result.

Copied its ten capture tools to the private
`a43-baseline-20261114/tools` directory. Original/copied sources were compared
before/after the baseline subprocess. The old corpus source was 39,220 bytes,
SHA-256 `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba`.
The unchanged demo generated 16 files and its complete failed study produced
119,423 canonical bytes, SHA-256
`6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727`.

An untraced wrapper asserted that the actual stream read was reached once and
observed a request for 16,777,217 bytes. With that wrapper removed, the isolated
reader peaked at 16,785,945 traced bytes and retained 121,304; real public replay
peaked at 16,790,342 and retained 83,802. Replay returned `match` while preserving
both underlying engineering statuses as `failed`. This isolated probe established
the concrete mechanism independently of worker 40's aggregate profile.

Sent the evidence and exact proposal to root **before editing production**.
Root approved the single size-aware request, preserving all checks and ownership.
The frozen protocol block in the review is 5,645 bytes, SHA-256
`f045d9ef6a5abaa7217d440ea32ca84d734b0af46efb83061da1fec563a5a277`.
Its exact bytes were saved before the production edit; the block remains unchanged.

## Production change and limits

After the existing descriptor/path identity binding and inclusive
`0 <= before_fd.st_size <= max_bytes` admission, request
`source.read(before_fd.st_size + 1)` instead of `source.read(max_bytes + 1)`.
One comment explains the validated size and extra byte. The existing exact-length,
cap, descriptor stamp, final path/parent stamp and stream cleanup paths are
unchanged. No unrelated common-reader change was made.

The resulting corpus source is 39,312 bytes, SHA-256
`751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded`.
Copied all ten current modules coherently to
`a43-after-source-20261114/tools`; only this corpus module differs from before.
This hash identifies the uncommitted tested implementation at measurement time;
the integrator records its eventual committed tree separately.

The retained reasoning covers empty files and inclusive cap equality, initial
and descriptor oversize rejection before payload reads, growth caught by the
extra byte/exact length, truncation/short reads, descriptor or later leaf/parent
replacement, cancellation/cleanup, and original-byte return semantics. These
are explanations of preserved checks, not a substitute for worker 44's reached
fault-injection tests. Quiescent-input requirements remain. No hostile-filesystem
sandbox, source authenticity or loaded-memory attestation is introduced.

## Frozen comparison and actual results

The stdlib-only collector copies both complete tool sets before executing two
fresh isolated interpreter subprocesses, disables bytecode writes, generates one
shared immutable synthetic archive, and retains complete original/fresh reports.
It traces the exact original report read and real complete fresh replay after
imports/setup/warm-up, using one traceback frame and three separate calls per
operation/source set. All six samples per source are retained, including current
and peak bytes; tracing is stopped before result serialization. An untraced
reached witness separately records each requested read amount.

The predeclared decision requires every after peak to be smaller than every
before peak for both operations. This is a fixed-workload observation, not a new
public bound. There is no ordinary timing, RSS, native-memory or callback claim.

| Operation | Before peak bytes, samples 1/2/3 | After peak bytes, samples 1/2/3 |
| --- | --- | --- |
| Isolated original-report read | 16785861 / 16785861 / 16785861 | 128603 / 128603 / 128603 |
| Complete fresh study replay | 16789839 / 16789831 / 16789823 | 1304735 / 1304386 / 1304888 |

The fixed decision passes. Request witnesses were 16,777,217 before and 119,424
after, both consuming exactly the same 119,423 bytes. Runtime was CPython 3.12.14,
Linux 6.18.57 x86_64, garbage collection enabled. All source/fixture identities
remained stable and the 16-file archive remained 32,831 bytes.

Both source sets replay their own fresh reports exactly. The after report is
119,423 bytes, SHA-256
`71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736`.
The new source replaying the untouched old report returns `mismatch`,
`same_runtime: true`, `same_tool_sources: false`; all engineering outcomes remain
unchanged. Removing only the explicit root and three embedded-job `tool_sources`
fields in a separate analysis gives identical 114,760 canonical bytes, SHA-256
`760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479`.
The public verifier still compares complete original reports; it never uses the
projection. Both complete reports are retained in the JSON and reconstruct their
exact original canonical byte identities.

### Collector refinement and preserved earlier evidence

The first full run passed. Subsequent source review added two collector-only
path guards: refuse new output inside either original source directory, and
defer the repository-relative protocol default when an explicit `--protocol`
is supplied. The latter supports a shallow external collector path. No runtime
source, protocol, fixture, report or resource criterion changed. The collector's
new identity required a final complete rerun, which also passed; no measurement
failed and no outlier or unfavorable sample was removed.

The exact first collector/result are preserved in
`a43-baseline-20261114/first-comparison/`, with hashes and all original current/peak
samples recorded durably in the review. Its isolated peaks were identical to the
final run; its complete replay before peaks were 16789839 / 16789831 / 16789823
and after peaks were 1305009 / 1305360 / 1304925. Both runs support the same frozen
decision. Worker 40's broader profile and artifacts were preserved unchanged.

## Commands and retained identities

Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Python 3.10+ standard library suffices; the observed run used 3.12.14.

```sh
python3 examples/benchmarks/capture-toolchain-v1/check_allocation.py --before-tools /workspace/scratch/c9f3ead4c910/a43-baseline-20261114/tools --after-tools /workspace/scratch/c9f3ead4c910/a43-after-source-20261114/tools --output examples/benchmarks/capture-toolchain-v1/allocation_comparison.json
```

The final collector is 18,785 bytes, SHA-256
`4cef019bece4e2625fd3934202c7258a4c5d34afc735c06221c47cbe08f43543`.
The final comparison is 304,390 bytes, SHA-256
`791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc`.
Each run requires a new output name in an existing parent. The collector uses
exclusive temporary creation and hard-link publication and never overwrites a
destination. No external archive is an input to this fixed benchmark.

Four final manual path/rejection checks passed: existing regular output retained;
dangling output symlink and absent target retained; new output in the before
tools directory rejected without creating it; shallow copied collector with
explicit protocol reached the expected no-clobber rejection without traceback.
Each deliberate rejection returned exit 1 and empty stdout. The published
artifact remained byte identical. Both retained reports passed exact canonical
byte/hash reconstruction. The initial collector also passed the two ordinary
and symlink output probes. These expected negatives are not hidden measurement
failures.

## Handoff and next step

Assignment 43's minimal implementation and controlled experiment are complete.
The corpus, protocol, final collector and final comparison identities were sent
to root and worker 44 and remain frozen. Worker 44 reports 357 methods across
seven suites, all passing with no skips: focused metadata read 24, admission 59,
corpus 47, job 81, study 61, replay 69 and installation 16. It independently
validated all twelve samples/paired reductions and actual source/fixture/
protocol/collector identities and reproduced both complete study reports plus
three replay summaries in five fresh subprocesses. Its initial focused-suite
run had three subcase errors in one method from a wrong nested comparison-key
lookup; the corrected harness required no producer change. Its
[acceptance review](../../reviews/CALIBRATION_METADATA_ACCEPTANCE.md) and
[assignment note](44-metadata-read-acceptance.md) are being prepared at this
handoff. Those are worker 44's reported executions, not tests rerun by 43.
Root owns reading that evidence, integration/full-gate acceptance and publication.
No root acceptance, commit, push, CI result or physical calibration is claimed.

Next let root review the unchanged reader semantics and measured narrow reduction
against those exact hashes, then let the integrator record the tested source tree,
shared handoff and actual publication result. Later agents should preserve the
old reports/source identities, requalify dependent gates after new source changes,
and use a new evidence artifact for any broader performance claim. The public
caps and all physical, native, clock, specimen, permission and fidelity limits
remain unchanged.

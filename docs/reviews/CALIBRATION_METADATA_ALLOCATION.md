# Confined metadata-read allocation experiment

Assignment 43 (`/root/cal_w8_a43`, logical wave 8) follows the retained
[resource profile](CALIBRATION_RESOURCE_PROFILE.md). This is an offline M0/M8
engineering experiment. It changes no capture, job, study or replay contract,
resource-admission cap, physical evidence or acceptance policy.

<!-- BEGIN FROZEN PROTOCOL -->
## Protocol frozen before the implementation change

Frozen at 2026-11-14 00:27:44 UTC, after an exploratory baseline and before
editing the production reader. The integrator approved the minimal proposal.
The exact UTF-8 bytes from this begin marker through the end marker, including
one following LF, are the protocol identity retained with the comparison.

**Question.** Does `_read_confined_bytes` unnecessarily reserve space for its
caller-supplied byte cap when the already admitted descriptor size is smaller?
The only production change may request `before_fd.st_size + 1` bytes instead
of `max_bytes + 1`. It must follow the existing descriptor binding and inclusive
size admission. Preserve all exact-length, descriptor stamp, final path/parent
checks, original-byte returns and stream/descriptor ownership. The extra byte
must remain: growth cannot silently return the original-size prefix.

**Baseline.** Use a coherent copy of all ten tool modules archived from commit
`16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`. Its corpus module is 39,220 bytes,
SHA-256 `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba`.
Retain every module's exact before/after size and SHA-256; reject source drift.
Only `capture_corpus.py` may differ between the two module sets. Copy both sets
before execution and use separate fresh interpreter subprocesses. Do not mutate
the original source directories, any actual archive or saved reports.

**Workload.** The unchanged ten-module closure includes `make_capture_demo`.
Generate its fixed 16-file, 32,831-byte synthetic archive once using the before
copy. The archive is shared unchanged by both subprocesses. Execute the ordinary
study outside measurement and retain its canonical original report bytes.
The exploratory baseline report is 119,423 bytes. The isolated reader in both
subprocesses reads those same original bytes with a 16 MiB cap. Public replay
in each subprocess reads that source set's own freshly emitted report against
the same unchanged study/archive. Preserve the before report when generating
the after report. Record all input and output byte identities.

**Instrumentation.** In each subprocess, witness the isolated stream's actual
single read request in a separate untraced call; assert that the witness was
reached and that returned bytes equal the original report. Restore the helper
before measurement. Perform one untraced warm-up per operation, then three
separate traced calls to (1) the isolated reader and (2) complete public study
replay. Before each traced call, collect garbage. Start `tracemalloc` with one
traceback frame after imports, copying, fixture generation, saved-report creation
and warm-up; retain the returned value while recording current and peak traced
bytes, then stop tracing. Retain all three samples in original order. No timing
or RSS samples are required. Tracing adds overhead and does not cover all native
allocations; these values are not total process RAM or callback deadlines.

**Predeclared resource decision.** The old witnessed request must be
16,777,217; the new request must be original report length plus one. On this
fixed local interpreter/workload, every after peak must be smaller than every
before peak for both the isolated read and complete replay. Report all actual
values, differences and source identities; do not choose a favorable sample or
generalize this observation into a cross-platform allocation guarantee. If the
measurements do not support the narrow claim, retain the evidence and do not
force an optimization acceptance.

**Unchanged semantics.** Both source sets must exactly reproduce their own fresh
study report and retain the underlying failed engineering result. With the after
source, replay of the unchanged old report must return `mismatch`,
`same_runtime: true` and `same_tool_sources: false`. The complete old and fresh
reports must be retained and hashed before any analysis. A separately labeled
comparison may remove only `tool_sources` at the study root and its three
embedded job report roots; these source-independent canonical projections must
be byte identical. That projection is experimental evidence only: public replay
still compares the entire original canonical report, with all source identities.
Every unaffected source module and every fixture byte must remain identical.

Independent acceptance must examine empty files, inclusive cap equality,
oversize admission before read, growth, truncation, short reads, replacement
around descriptor/path observation, parent identity changes and cancellation or
cleanup failures. The original checks are not a hostile-filesystem sandbox;
inputs and installed sources must remain quiescent. Existing relevant suites and
separately written reached fault hooks qualify semantics. A measurement alone
does not qualify them. Do not change the unrelated common reader for symmetry.

**Reproducer and evidence.** `check_allocation.py` uses only the standard library,
bounded inputs and a new output destination. It works in private temporary
copies, rejects changed source/fixture bytes and refuses to overwrite an output.
The final `allocation_comparison.json` retains before/after inventories, original
and fresh output hashes, all samples, witness requests, exact equality/context
checks, collector/protocol identities and the observed runtime. Its contents are
actual observations, not estimated memory use. Assignment 44 owns independent
acceptance; the integrator owns shared status, commit, push and publication gates.
<!-- END FROZEN PROTOCOL -->

## Exploratory observation before the proposal

A fresh subprocess imported a private copy of the ten archived modules. The
16-file demo and failed study produced a 119,423-byte report, SHA-256
`6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727`.
An asserted untraced witness observed one `read(16777217)` request. Without the
witness, one traced isolated read peaked at 16,785,945 bytes (121,304 current);
one complete replay peaked at 16,790,342 bytes (83,802 current). Replay returned
`match`, preserving both engineering statuses as `failed`. The original and
copied source bytes were equal before and after the probe. These exploratory
values motivated the frozen comparison; they are not substituted for its three
samples per operation/source set.

The original reader was bounded and enforced its contract. This work addresses
a specific temporary allocation under a loose cap, not an observed admission,
correctness or fidelity failure. The atlas source basis for retaining changed
code/data identities and separate engineering claims is pp. 449 and 484–486;
assignment 43 read those extracted pages, not another complete PDF pass.

## Results and handoff

The frozen comparison completed on CPython 3.12.14, Linux 6.18.57 x86_64, with
garbage collection enabled. Both workers used the same interpreter build
(`Clang 22.1.3`, Python build dated August 25, 2026). Both the first full collector
run and the final rerun completed without a setup or assertion failure. The
collector-only refinement and all earlier samples are retained below. Independent semantics acceptance
belongs to assignment 44; the measurements below do not substitute for it.

At this handoff, assignment 44 reports **357 methods across seven suites, all
passing with no skips**: 24 focused metadata-read methods plus admission 59,
corpus 47, job 81, study 61, replay 69 and installation 16. It also reports an
independent five-process before/after study/replay reproduction and verification
of all twelve retained traced samples, source/fixture/protocol/collector identities,
complete reports and exact source-only projection. Its first focused-suite run
had three subcase errors in one method from an incorrect nested comparison-key
lookup; the harness was corrected without changing production. Its durable
[independent acceptance review](CALIBRATION_METADATA_ACCEPTANCE.md) is being
prepared at this handoff. These are worker 44's reported executions, not repeated
executions by assignment 43 or an integrator acceptance/publication claim.

| Operation | Sample | Before current bytes | After current bytes | Before peak bytes | After peak bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Isolated original-report read | 1 | 121,304 | 121,304 | 16,785,861 | 128,603 |
| Isolated original-report read | 2 | 121,304 | 121,304 | 16,785,861 | 128,603 |
| Isolated original-report read | 3 | 121,304 | 121,304 | 16,785,861 | 128,603 |
| Complete fresh study replay | 1 | 83,680 | 83,582 | 16,789,839 | 1,304,735 |
| Complete fresh study replay | 2 | 83,565 | 83,249 | 16,789,831 | 1,304,386 |
| Complete fresh study replay | 3 | 83,235 | 83,767 | 16,789,823 | 1,304,888 |

Every after peak is below every before peak for both declared operations, so the
predeclared resource decision is satisfied. The isolated peak reduction is
16,657,258 bytes in each sample. The three complete-replay reductions are
15,485,104, 15,485,445 and 15,484,935 bytes. End-of-call retained allocation is
similar; the changed observation concerns the temporary peak.

The separately asserted untraced read witnesses observed 16,777,217 requested
bytes before and 119,424 after. Both consumed exactly the same 119,423 original
bytes. The isolated operation demonstrates the allocation mechanism directly;
the full replay observations establish its practical effect on this one fixed
workload. No ordinary timing, RSS, native-memory or audio-callback claim follows.

### Sources and retained outputs

The comparison copies all ten tools before either subprocess starts, imports
only from each private copy, disables bytecode writes and checks original/copied
source bytes before and after. Only the corpus module differs. All 16 fixture
files, totaling 32,831 bytes, remain identical. The complete ten-module and
fixture inventories are retained in the comparison artifact.

| Identity | Bytes | SHA-256 |
| --- | ---: | --- |
| Frozen protocol block | 5,645 | `f045d9ef6a5abaa7217d440ea32ca84d734b0af46efb83061da1fec563a5a277` |
| Before `capture_corpus.py` | 39,220 | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| After `capture_corpus.py` | 39,312 | `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded` |
| `check_allocation.py` | 18,785 | `4cef019bece4e2625fd3934202c7258a4c5d34afc735c06221c47cbe08f43543` |
| `allocation_comparison.json` | 304,390 | `791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc` |
| Original canonical study report | 119,423 | `6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727` |
| Fresh canonical study report after the edit | 119,423 | `71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736` |
| Both separately projected study contents | 114,760 | `760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479` |

The after module is an uncommitted change relative to the identified before
commit at measurement time; its content hash identifies the tested bytes. The
integrator records the eventual committed tree and publication separately.
The old coherent source remains recoverable from the before commit; its private
baseline copy was also preserved during this assignment. The original broad
profile, collector and results were not edited and retain their old identities.

After the first successful comparison, source review added two collector-only
guards: reject a new output inside either original tools directory, and compute
the repository-relative default protocol path only when `--protocol` is absent.
The latter permits an explicitly supplied protocol with a collector copied to a
shallow external path. These are outside the measured operations; neither
production source, the protocol, fixture, original/fresh report, nor the resource
criterion changed. A final run was required because the collector identity
changed. No sample was discarded as an outlier and no failed measurement was
reclassified.

The first collector was 18,381 bytes, SHA-256
`016db46a7870a3d8bafa040c338bbdf1c4222255811d6cedc422746362a5e4c6`;
its successful result was 304,390 bytes, SHA-256
`45a144ac756310496cd5e05c725109f6609e4b715b2d8f23b7ad3926847bb6a7`.
Both exact files are preserved in the assignment's scratch checkpoint
`a43-baseline-20261114/first-comparison/`; all its measurements are retained here
so this review does not depend on that temporary checkpoint:

| First run operation/source | Current bytes, samples 1/2/3 | Peak bytes, samples 1/2/3 |
| --- | --- | --- |
| Isolated read, before | 121304 / 121304 / 121304 | 16785861 / 16785861 / 16785861 |
| Isolated read, after | 121304 / 121304 / 121304 | 128603 / 128603 / 128603 |
| Complete replay, before | 83896 / 83457 / 83905 | 16789839 / 16789831 / 16789823 |
| Complete replay, after | 83856 / 84223 / 83804 | 1305009 / 1305360 / 1304925 |

Both complete study reports are stored as JSON values in `retained_reports`,
with their original canonical-byte identities and serialization rule. A separate
reconstruction check reserialized each retained value and recovered exactly its
original byte count and SHA-256. The actual saved report files were never
rewritten during execution. The only analysis projection removes these four
paths: `/tool_sources` and `/jobs/0/report/tool_sources`,
`/jobs/1/report/tool_sources`, `/jobs/2/report/tool_sources`. The resulting entire
canonical byte sequences are identical. Public replay never uses that projection.

Both same-source fresh replays return `match`, retaining all three job outcomes
(`pass`, `inconclusive`, `failed`) and the study's `failed` outcome. The new
source replaying the original old report returns `mismatch`, with
`same_runtime: true` and `same_tool_sources: false`, while retaining both
engineering statuses as `failed`. A source hash records observed file identity;
it does not authenticate loaded memory, historical reports or physical claims.

### Why the existing checks remain necessary

This is source reasoning for the narrow edit. The independent acceptance record
owns the observed fault-injection results.

| Case | Preserved defense and effect of the edit |
| --- | --- |
| Empty file, including a zero cap | An admitted descriptor size of zero requests one byte; unchanged exact-length and stamp checks still require an empty stable result. |
| File exactly at its cap | The requested size remains `max_bytes + 1`, exactly as before. |
| Initial or opened descriptor exceeds its cap | The same two inclusive size guards reject before the payload read; opened-stream ownership remains unchanged. |
| Growth visible while reading | The extra byte exposes a larger-than-admitted prefix and the exact-length check rejects; descriptor and final path stamps remain additional checks. |
| Truncation or a short read | Returned length differs from the admitted descriptor size and rejects. A size change between path and descriptor admission remains visible to final path stamps. |
| Replacement before descriptor binding | The unchanged descriptor/path identity binding rejects a different usable identity. |
| Replacement after reading or parent substitution | The unchanged final leaf stamp and parent type/identity checks remain required. |
| Read failure, cancellation or cleanup failure | The same `_stream`, context manager and descriptor ownership paths execute; only the positive read request count differs. |
| Original-byte hashing and parsing | The same complete admitted payload is returned; no buffer normalization, encoding change or report rewrite is introduced. |

Portable observations still require quiescent inputs. They cannot prove that an
adversary did not modify and restore bytes between observations, or turn absent
usable identities into stronger proof. No new concurrent-filesystem promise is
made.

### Reproduction and continuation

From the repository root, with Python 3.10+ and the exact two source sets, run:

```sh
python3 examples/benchmarks/capture-toolchain-v1/check_allocation.py --before-tools /existing/before/tools --after-tools /existing/after/tools --output /existing/new-allocation-comparison.json
```

Both tools directories need the ten named modules in the artifact inventory.
The before set can be extracted from commit
`16d72e1b351e5cdf1730e90645a6ea37144d1be7`; the after set must match the retained
hashes, with only the corpus source different. `--protocol` optionally supplies
the review document when the collector is run outside its repository layout.
The output parent must already exist and the output name must be new. Source
copies and generated fixtures are private temporary data; no real archive input
is accepted. Later source changes require a separately identified experiment,
not silently updating this result.

The actual command used for the retained run was:

```sh
python3 examples/benchmarks/capture-toolchain-v1/check_allocation.py --before-tools /workspace/scratch/c9f3ead4c910/a43-baseline-20261114/tools --after-tools /workspace/scratch/c9f3ead4c910/a43-after-source-20261114/tools --output examples/benchmarks/capture-toolchain-v1/allocation_comparison.json
```

Four expected rejection/path checks completed against the final collector. An
existing regular output and a dangling output symlink each returned exit 1 with
no stdout and preserved the destination; the dangling link's target remained
absent. A new output inside the before tools directory rejected before creating
any file. A collector copied to a shallow external path, with explicit protocol,
reached the expected existing-output rejection without a traceback. The published
artifact remained byte identical. These intentional rejections are separate from
an unexpected setup or measurement failure. The original collector also passed
the two regular/symlink no-clobber probes before its refinement.

Next: the integrator reads assignment 44's retained acceptance against the frozen
source/protocol, performs the coherent integration gates and records the resulting
committed tree. Worker 44's reported pass does not by itself claim root acceptance.
Do not infer a full benchmark refresh, a physical calibration gate or native
qualification from this experiment. The allocation request improvement alone
does not establish a new universal process-memory limit.

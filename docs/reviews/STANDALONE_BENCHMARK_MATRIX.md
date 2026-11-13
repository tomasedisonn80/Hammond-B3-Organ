# Complete standalone Session benchmark matrix audit

Assignment **52**, wave **9**, actual agent `/root/w09_a52_benchmark_matrix`,
session `2026-11-13-next-phases`.

**Result:** all **60/60** fixed workload/rate/buffer cases executed once and
passed independent functional, state, source-identity and timing-arithmetic
checks. The complete parsed data, all 6,000 raw measured intervals and a
standalone verifier are retained in the
[matrix artifact](../../examples/benchmarks/standalone-session-matrix-v1/README.md).
There is no elapsed-time pass threshold or device-performance conclusion.

## Source, build and actual execution

| Item | Verified identity |
| --- | --- |
| Published source | `649b12c7d1faa7601fde1019e913347c65a6634a` |
| Exact source tree | `cf63327d857b02029e8c5c6f406cab3d3c6890d1` |
| Executable | 154,568 bytes, SHA-256 `0c97a79e8c49dbad961090727fe3ae1668a283bdc4d87f4d334fc9c604981f19` |
| Compiled nominal profile | 4,545 bytes, SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Profile byte FNV-1a64 | Independently recomputed `bf38a44e8d31695a`; matches all 60 reports. |
| Source fingerprint | `5fd7837b44dbe8fd09bfbd9931c20065e29acfffee10f3adca1a622cb18b9bb8`, 57 sorted inputs. |
| Compilation | GCC/G++ 14.2.0, C++20, GNU Release `-O3 -DNDEBUG`; all 23 relevant recorded commands lack sanitizer flags. |
| Build tools from originating audit | CMake 4.4.4, GNU Make 4.4.1; this assignment did not rebuild. |
| Observation host | Linux 6.18.57 x86-64, glibc 2.41, Python 3.12.14; allowed CPUs 0–8. |
| First/last collection timestamps | 2026-11-13 23:39:14.499292 UTC to 23:39:26.786989 UTC. |

The executable and profile came from assignment 49's frozen SDK-free build
under `a49-clean-setup/unavailable originals é 音/build sdk free é 音/`.
They were used read-only; neither assignment 49's source nor either of its
builds was moved, rebuilt or modified. The collector independently recomputed
Git blob identities and executable modes for all **842 tracked source files**
against the published commit, before and after all executions. Their inventory
SHA-256 is
`bd1a198a7331e4c69e9579a48e46828368fbc87f3a2d0c0634257a84f8087680`.
It checked every one of the 57 manifest files against its actual SHA-256 and
recomputed the sorted `path:sha256\n` fingerprint.

The exact binary and compiled profile also retained their byte identities
before/after. The profile's ID and retained authoring digest match its actual
compiled header; this is a byte/metadata check, not authentication of a physical
instrument or endorsement of nominal coefficients. All reports identify
`nominal-unmeasured-v1` and `ideal-shared-sine-v1`.

The CMake cache confirms both native adapters OFF. The recorded compilation
commands identify 19 core units, three standalone-support units and the
benchmark. Their flags were inspected directly, supplementing the executable's
project-option metadata. This is inspection of the originating fresh build,
not a new compilation or sanitizer gate by this assignment.

## Executed command and collector preflight correction

The actual command ran from the shared repository root; aliases below shorten
the argument values preserved in the artifact and raw process records:

```sh
A52_INPUT='/workspace/scratch/5ba97739b54c/a49-clean-setup/unavailable originals é 音'
A52_OUTPUT='/workspace/scratch/5ba97739b54c/a52-benchmark-matrix'
python3 examples/benchmarks/standalone-session-matrix-v1/collect_matrix.py \
  --repo . --commit 649b12c7d1faa7601fde1019e913347c65a6634a \
  --source-root "$A52_INPUT/source é 音" \
  --binary "$A52_INPUT/build sdk free é 音/apps/standalone/hammond_standalone_benchmark" \
  --profile "$A52_INPUT/build sdk free é 音/nominal.b3p" \
  --source-manifest "$A52_INPUT/build sdk free é 音/apps/standalone/standalone-benchmark-source-manifest.json" \
  --origin 'read-only reuse of assignment49 fresh SDK-free Release build' \
  --output examples/benchmarks/standalone-session-matrix-v1/matrix.json \
  --raw-dir "$A52_OUTPUT/raw"
python3 examples/benchmarks/standalone-session-matrix-v1/verify_matrix.py
```

The first collector preflight selected the guessed target spelling
`hammond_standalone_core.dir`, so its 23-command identity assertion failed.
Inspection of actual `compile_commands.json` showed
`hammond_standalone_support.dir`. The selector was corrected while retaining
the exact 23-command requirement. This occurred **before any benchmark
invocation**; the initial raw directory was empty and was retained separately.
No benchmark/source/profile, functional expectation, iteration count or
timeout was changed. The subsequent collection executed all 60 cases once;
there were zero benchmark retries and zero case verification failures.
The preflight correction is retained in `verification.json` and the private
`preflight-correction.json`.

Each child received explicit `LC_ALL=C.UTF-8`,
`SDL_AUDIODRIVER=hammond_matrix_missing_driver` and
`SDL_VIDEODRIVER=hammond_matrix_missing_driver`, with the other environment
inherited. The cwd was the private raw-record directory. The collector stores
each exact argv, UTC start, wall duration, exit code, stdout/stderr byte counts
and hashes. All stderr streams are empty. The 30-second subprocess watchdog
was never reached and is not used as an audio deadline. No CPU affinity,
power/thermal policy or scheduler-load control was applied.

## Independent workload and state reconciliation

The Cartesian product is exactly four workloads × rates **44,100 / 48,000 /
96,000 Hz** × buffer sizes **128 / 256 / 512 / 1,024 / 2,048 frames**. Each
process performs 16 warmup and 100 measured positive render calls. Workload
order is silence, performance, dense, recovery, with ascending rates/buffers;
there is no randomization, speed-based selection or dropped sample.

| Measured phase, summed over 15 settings | Positive calls | Frames | Accepted / applied / discarded commands | QueueFull / RecoveryPending / recovery |
| --- | ---: | ---: | --- | --- |
| Silence | 1,500 | 1,190,400 | 0 / 0 / 0 | 0 / 0 / 0 |
| Performance | 1,500 | 1,190,400 | 0 / 0 / 0 | 0 / 0 / 0 |
| Dense controls | 1,500 | 1,190,400 | 384,000 / 384,000 / 0 | 0 / 0 / 0 |
| Recovery | 1,500 | 1,190,400 | 393,000 / 9,000 / 384,000 | 1,500 / 1,500 / 1,500 |
| **Total** | **6,000** | **4,761,600** | **777,000 / 393,000 / 384,000** | **1,500 / 1,500 / 1,500** |

Setup independently reconciles 225 accepted/applied commands and 60 zero-frame
flushes. Warmup adds 960 positive calls / 761,856 frames, 124,320 accepted,
62,880 applied and 61,440 discarded commands, with 240 intentional recoveries.
Recovery rearming contributes 1,740 additional zero-frame calls across warmup
and measurement. Together the phases cover 5,523,456 positive-render frames;
the measured phase checks 9,523,200 stereo samples.

The verifier imports neither the benchmark implementation nor its maintained
test oracle. It uses literal documented registration/note sets and arithmetic
counts to check every setup, warmup and measured stage, including the exact
admitted/applied/discarded reconciliation and sequence/frame boundaries. Every
one of the **240 complete snapshots** must have the expected controls,
manual/pedal ownership, resolved/applied sequences, recovery/overflow/discard
counters, sticky flags, positive even increasing publication revision and
frame clock. Stops retain controls/time while clearing all holds and peak.

For performance and dense work, the retained notes are upper 60/64/67, lower
48/55 and pedal 1. The controls are upper B `888000000`, lower B `008800000`,
both A banks zero, pedal mixtures 8/5, expression 0.75 and Third/Soft/Fast
percussion enabled. Silence uses literal muted defaults; recovery must actually
rearm six holds, then discard exactly 256 pending controls and publish silence.
These are declared nominal workloads, not factory preset or gain claims.

All measured reports assert finite, bit-identical stereo. Every silent/recovery
hash independently matches the closed-form FNV result for the exact all-zero
float byte count. At each of the 15 settings, dense controls and ordinary
performance have identical complete measured audio hashes and peaks. This
cross-workload check establishes that the 256 within-boundary expression edits
do not change the final rendered signal for these retained workloads. Raw float
audio is not emitted or retained; the hash comparison is not an acoustic or
physical-fidelity assessment.

## Retained timing observations and limits

All **6,000** chronological intervals remain in `matrix.json`. The verifier
recomputes min/max, the median using Python's independent statistics library,
nearest-rank p95/p99, a full-precision sum, the formula `frames × 1e9 / rate`,
all distribution/period ratios and the count strictly above that period. The
enclosing measured loop must contain the complete sum. No clock overhead is
subtracted; warmup stays outside the measured distribution. The separate
1,000-pair clock calibration exposes summaries only, so its ordering/total
bounds are checked without claiming unavailable raw-calibration recomputation.

| Workload | Intervals above arithmetic period | Largest observed period ratio and case |
| --- | ---: | --- |
| Silence | 2 | 9.01273725 at 96,000 Hz / 512 frames; 48,067,932 ns. |
| Performance | 2 | 1.322970703125 at 96,000 Hz / 2,048 frames; 28,223,375 ns. |
| Dense controls | 21 | 3.75702975 at 96,000 Hz / 128 frames; 5,009,373 ns. |
| Recovery | 1 | 3.9123571875 at 48,000 Hz / 512 frames; 41,731,810 ns. |
| **Total** | **26** | All retained; no failed timing threshold or removed outlier. |

The sum of measured render intervals is 9.592160234 seconds. The sum of the
60 complete process wall durations is 11.884067492 seconds; parsing, setup,
warmup, outside-timer workload checks, clock calibration and output add work.
These are descriptions of this collection, not performance targets. The source
of individual long intervals was not diagnosed. Shared-host contention and
uncontrolled affinity/power/thermal conditions prevent a controlled workload
speed comparison. No result is converted to a physical device deadline,
underrun count, latency or hard-real-time pass; those fields remain false/null.

## Retention and next work

The 398,206-byte matrix has SHA-256
`92e1da3c49fc763ace80740d731bc85471b0ea557b9b126903d1ec79a425505d`.
Common build/profile/model/claim fields are stored once; merging them with each
case's disjoint report map reconstructs every parsed JSON value and matches its
retained semantic digest. All original stdout/stderr/process files remain in
`/workspace/scratch/5ba97739b54c/a52-benchmark-matrix/raw/`; their redundant raw
formatting is not required to recompute the committed statistics or counters.

The [assignment note](../development/2026-11-13-next-phases/52-benchmark-matrix.md)
lists the seven owned paths. No production source, CMake, maintained acceptance,
shared status or ledger was changed, and the worker did not commit or publish.
Root owns review/publication and the later combined-source/platform gates.

A future performance qualification needs an identified target machine and
audio backend/device, recorded scheduling and power conditions, actual
callback/UI load, duration, underrun/latency measurements and predeclared
acceptance. Repeat this exact functional matrix on that identified source
first, preserving all samples and source/profile identities. The current
matrix supplies reproducible workloads and arithmetic evidence for that work;
it does not close the native-device or physical-model gates.

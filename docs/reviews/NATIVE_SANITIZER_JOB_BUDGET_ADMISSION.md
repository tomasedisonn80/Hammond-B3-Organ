# Native sanitizer job budget admission — A54 follow-up

## Decision and scope

**Admit one orchestration change: increase only the `native-sanitizers`
job's overall budget from 20 to 35 minutes.** The actual workflow is
[`.github/workflows/standalone.yml`](../../.github/workflows/standalone.yml),
not `native-standalone.yml`. At the reviewed source, line 640 changes from
`    timeout-minutes: 20` to `    timeout-minutes: 35` beneath
`jobs.native-sanitizers`. This review does not apply the change. Root owns
the edit, exact-source publication and any subsequent hosted execution.

The admission concerns the original Linux GCC ASan + UBSan + leaks job
[133814024877, run 44016021554, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021554/job/133814024877),
at source `fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`, tree
`b62f212300d75633346ab8fc5ffdd722255fe00a`. Its result remains **cancelled:
30 passed, one unfinished and three not started**. It is not a successful
34-gate sanitizer qualification.

The job budget is inconsistent with the observed prefix and the existing
limits for the remaining gates. The available evidence does **not** identify
what initiated cancellation. The only terminal error is “The operation was
canceled.” Neither its wording nor the proximity to 20 minutes proves a
timeout trigger or a particular CPU/scheduler cause.

## Independent evidence

A54 fetched the complete original job API metadata and decoded log,
retrieved the workflow at the exact source, and downloaded and inspected
[original diagnostic artifact 14300270335](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021554/artifacts/14300270335).
The 163,235-byte ZIP matches its original GitHub SHA-256. Its provenance
binds the exact source/tree, attempt, sanitizer environment, 34 selected
tests and 31 build inputs. Its generated CTest discovery confirms all 34
commands are enabled, the four remaining timeout properties are present,
and no per-test sanitizer environment override appears. Its instrumentation
receipt contains all 31 selected executable records.

The [new A54 receipt](../development/2026-11-16-heading-title-continuation/reports/a54-native-sanitizer-job-budget.json)
retains the complete original cancellation block, every original passing
result and start line, API step outcomes, exact arithmetic, relevant source
hashes and the proposal. It also retains losslessly compressed copies of
the complete original 135,882-byte CTest stream and 29,345-byte generated
discovery. These copies avoid depending on artifact retention for the
original partial test evidence. The full decoded job log was independently
hashed and agrees with A53's frozen original receipt and
[complete deterministic gzip archive](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814024877-complete.log.gz).
The archive is 114,252 bytes, SHA-256
`f9034e35bdcedebf66b20b2db280746542a290a02ac5a01a4c2bbb6291dbeba3`,
and expands to the exact 1,317,735-byte original log. A54 verified the
complete decoded hash and cancellation-block membership. A53's additive
archive inventory does not modify its original 15,568-byte job receipt,
whose SHA-256 remains
`7a0e5305cbdd199b2bb4347803bd4e8d4b2d2ad736e9cc1d1c6179dc991f6cdc`.
Existing A53 cancellation files and
all accepted A54 reviews, receipts and note remain unchanged.

## Numerical budget analysis

| Original event or interval | Observed value |
| --- | ---: |
| Job start, API | 04:16:26 UTC |
| Build step alone | 329 seconds |
| Job start to first CTest start | 424.5943070 seconds |
| Thirty passing CTests, sum of displayed durations | 739.08 seconds |
| Preset raster start | 04:35:49.6666788 UTC |
| Job start to preset raster start | 1,163.6666788 seconds |
| Remaining from the 1,200-second job budget | **36.3333212 seconds** |
| Preset start to cancellation message | **49.6356720 seconds** |
| Job start to cancellation message | 1,213.3023508 seconds |
| API job completion, including cancellation cleanup | 1,219 seconds |

The passing-test sum uses rounded CTest durations; the directly timestamped
first-test-to-preset interval is 739.0723718 seconds. These are consistent
at their respective precision. The API reports acquisition, configuration,
all 31 builds and instrumentation checks as successful. The gate-running
step is cancelled, final source/SDL reverification is skipped, and the
diagnostic upload succeeds. No failed CTest result row or actual sanitizer
diagnostic appears in the completed stream. Unexecuted coverage remains
unknown; absence of a diagnostic is not completion evidence.

The generated CTest metadata from the original artifact gives this tail:

| Gate | Original observed state | Existing CTest limit |
| --- | --- | ---: |
| `test_standalone_preset_raster` | Started, no result | 300 seconds |
| `test_standalone_native_calibration` | Not started | 180 seconds |
| `test_standalone_replay_paint_boundary` | Not started | 90 seconds |
| `test_standalone_semantic_paint_boundary` | Not started | 90 seconds |
| **Total remaining allowed test envelope** | | **660 seconds** |

These limits were already configured at the cancelled source. In
particular, the original verbose log explicitly reports preset raster's
computed limit as 300 seconds. Cancellation occurs about 49.64 seconds into
that test, so this is not evidence of its own 300-second CTest timeout.

Holding the observed prefix fixed and allowing each remaining gate its
existing limit gives **1,163.6666788 + 660 = 1,823.6666788 seconds**, or
**30 minutes 23.667 seconds**, before the remaining receipt checks, source
reverification and artifact cleanup. A 35-minute job provides **276.3333212
seconds**, about **4 minutes 36 seconds**, beyond that envelope. A 31-minute
job would leave only about 36 seconds for those operations and variation.
The proposed 35 minutes is a finite operational allowance with a narrow
one-scalar edit; it is not asserted to be the mathematically smallest
integer setting.

This calculation is an observed-prefix plus permitted-tail model. It is
not a measured completion time, not a sum of every gate's worst-case limit,
and not a guarantee that another runner will finish. It supports allowing
the unchanged remaining work to reach its own assertions and guards.

## Workload and policy protections

The admission preserves every selected test, fixture, assertion and bound.
In particular:

- Keep all 34 required CTests, all 31 build inputs, exact-name discovery,
  command checks, enabled-gate assertions and fail-on-error behavior.
- Keep CTest `--parallel 1`, its default `--timeout 180`, every generated
  individual timeout, and build `--parallel 2`. Keep the ordinary native
  job's 40-minute budget and the sanitizer dependency step's 8-minute limit.
- Keep `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
  `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and
  `LSAN_OPTIONS=exitcode=23`. Keep the prohibition on per-test overrides.
- Keep project C++ and SDL C address/undefined instrumentation, frame
  pointers, object/archive/runtime audits and the instrumented native
  probe. No disabling, filtering away a gate, `continue-on-error`, or
  suppression is admitted.
- Keep calibration's ten native subprocesses, seven lifecycle scenarios,
  two deliberately failed replays, individual 15-second child limits and
  post-CTest stderr/receipt validation. Keep both replay/semantic initial
  states and their existing 30-second sanitizer child limits.
- Keep preset raster's finite 256 full paints and 272 readbacks, its
  300-second sanitizer guard and separate 30-second ordinary guard. The
  raster fixture measures correctness and has no internal real-time
  performance assertion; this review does not change its workload.
- Keep exact-source/locked-SDL reverification and diagnostic retention.
  Their original unexecuted validation cannot be inferred from upload
  success.

The current workflow, standalone CMake file, four tail fixtures, painter
and application entry were compared byte-for-byte to the exact original
commit while preparing the receipt. The separate Windows explicit-cast
repair is outside this admission. No native executable, build, test or
rerun was launched by A54 for this follow-up, and no remote mutation was
performed.

## Exact hashes and next acceptance

| Evidence or proposed identity | SHA-256 |
| --- | --- |
| Original/current workflow at review | `4fe89694b7b85fe83b27f4bd2b3dc60e2b45ce88e30e1209e94a30a5469bf48c` |
| Candidate workflow if only the admitted scalar changes | `af5cf9421c5cdbae37b5f0d26e1bf3d96c8a5b26491f89b6518db0ca0e1cc319` |
| Original standalone CMake | `642655110b803592e0943d6bb1aa367cd74c81d72b6ebef0b3f1058916157a96` |
| Complete decoded original job log | `0efeef4e151d896864c51597ab697210a2217574387a1818e554fdac41e6c90d` |
| Preserved 991-byte cancellation block | `9e9c8f542e4bd4aad81df2140152cc67c18a7febf0374b1c61d00278c9bf617b` |
| Original downloaded diagnostic ZIP | `a2a39510d66d9157a0659c9f3b7e18a4d67380b0437d218ae4bba7cfc49ca23f` |
| Complete original CTest stream | `fc2ea261b09265f14cd0dc14a885f09b6a0c842700abc7538f1e9ca8711d94bb` |
| Original generated CTest discovery | `2ddcb4759a2f4db7e76360f21b44e7aaff6428317211a24db1b18e120a3a769a` |

After root applies and publishes the reviewed change, acceptance must bind
the new exact source to a complete 34/34 result, actual sanitizer/leak
diagnostics, full native-calibration receipt, unchanged instrumentation
requirements and completed final source/SDL checks. A new terminal failure
must retain its own evidence and receive a specific diagnosis. This
admission authorizes neither retry-until-green nor relabeling the original
cancelled job. The accepted original VST3 results and A54 note remain
unchanged.

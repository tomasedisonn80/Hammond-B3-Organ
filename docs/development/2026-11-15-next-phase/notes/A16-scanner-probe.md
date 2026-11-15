# A16 — additive scanner FOH native probe

**Actual worker:** `/root/w03_a16`, Wave 3, 15 November 2026.
**Checkout:** `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.
**Owned paths:** `tools/scanner_line_foh_probe.cpp`,
`tests/test_scanner_foh_probe.py` and this note.

## Scope and recovery

The separate producer probe and its focused regression suite are implemented.
Root's coordinated GCC 14.2 Release build passed, and the focused CTest passed
1/1 with all fifteen underlying unittest cases successful. A16 inspected the
actual resulting log and rehashed the tested inputs.
This is not independent full-grid, transient, process-settling or physical
qualification. It introduces no Engine route, rotor or host resampler.

Read the complete AGENTS.md, M0–M9 PLAN.md, current next-phase checkpoint,
reviewed FOH contract, old probe contract, A10 review and A13 implementation
note. Inspected the complete old probe, shared Unicode argument adapter,
existing native AC tests, the stable new public header and documentary resistor
values. The retained atlas readings and graph are the source basis; A16 makes
no new whole-atlas reading or acquisition claim. Root owns build, CMake,
publication and shared navigation. No child, configure, compilation, git,
dependency or shared-document mutation is performed by this worker.

The implementation input is `scanner-foh-line-contract-v1`, SHA-256
`90b3564497ebd669baaaf0badf1a954953f1e1322c45f3e64e37e23cb826866e`.
The new target is `hammond_scanner_line_foh_probe`; the test requires
`HAMMOND_SCANNER_LINE_FOH_PROBE_EXECUTABLE` and fails visibly if no actual
executable is supplied. Root registers both in CMake, including the existing
MinGW `-municode` convention.

## Stable CLI and JSON handoff

The tool retains separate `response`, `sine` and `trace` operations. Mandatory
`--operation`, `--sample-rate` and `--mode` options occur once; `--help` is
standalone. Existing strict decimal parsing, unsigned conversion, classic
locale, `max_digits10`, nearest-rounding scope, Windows strict UTF-16-to-UTF-8
entry and complete-report-before-stdout behavior are preserved in the new
file. No old probe or core file is changed. All exceptions produce stderr and
exit 1; success produces one JSON document and exit 0. Output-stream failure
can follow a partial OS write, so atomic destination publication remains the
caller's responsibility.

The bound is thirteen named options, 32,768 bytes per argument, 1–1024 ordered
response frequencies, 16,777,216 total sine frames, 1–16,384 trace knots of
at most 128 bytes each, 262,144 internal trace intervals and 64 MiB of JSON.
Parsing and serialization allocate only in this offline executable. All
bounded trace input and total counter increments are checked before processing.

Common metadata identifies:

- Probe `scanner-line-foh-probe-v1`.
- Model `atlas-late-b3-nominal-line-v1`.
- Realization `scaled-physical-exponential-foh-scanner-line-v1`.
- Preparation `scanner-augmented38-pade13-scaling-squaring-v1`.
- The linked core's compiled authoring SHA-256 and
  `synthetic_nominal_engineering` evidence scope.
- `input_reconstruction:piecewise_linear_between_internal_endpoints`.
- Two `preparation_diagnostics` objects, ordered Vibrato then Chorus, each
  containing exactly `augmented_norm_one`, `squarings`, `normalized_residual`
  and `condition_inf`. The common `preparation_residual` is their maximum.

The response operation retains the original response-array shape, frequency
order and repetitions, nineteen signed complex taps, signed return and A/V
input admittance, residual and condition. It evaluates the actual prepared
FOH recurrence, without advancing state. The sine path calls only actual
`process_frame` for each input; it retains whole and independent half-window
cosine/sine/constant fits, physical residual RMS, startup lengths and final
physical checkpoint. No result is labelled accepted or settled by this tool.

### Original-knot fixture adapter

`trace --subdivisions m` accepts only `1,2,4,8,16`, default 1. It is invalid
on response/sine. `--sample-rate` always names the **internal line rate**.
For each original input knot, the adapter supplies exactly `m` linear
subendpoints from the previous supplied knot, calls the line once per
subendpoint, and emits only the final endpoint. It never processes `j=0` or
repeats the previous endpoint. The last subendpoint is assigned directly from
the supplied knot, avoiding cancellation that could otherwise change tiny
input values. The mode applies to each actual internal interval.

| Trace field | Exact meaning |
| --- | --- |
| `input_knot_adapter` | `offline_piecewise_linear_knot_subdivision` |
| `subdivisions` | Actual `m`, never a host quality-policy selection |
| `internal_steps` | Validated `input_knots*m` |
| `input_knot_rate_hz` | `sample_rate_hz/m` |
| `initial_endpoint_seconds` | `-m/sample_rate_hz` |
| `initial_observation.time_seconds` | Same earlier fixture endpoint |
| `frames[k].time_seconds` | `k/input_knot_rate_hz` |
| `frames[k].frame` | `initial_frame+(k+1)*m` |

The trace clock is exactly
`previous_endpoint_at_minus_one_input_knot;first_emitted_knot_at_zero;frame_counts_completed_internal_intervals`,
including `m=1`. Response/sine retain the original exact clock:
`previous_endpoint_at_minus_one_sample;first_processed_knot_at_zero;frame_counts_completed_intervals`.
Every emitted frame includes the actual input, nineteen taps, return, source
current, energy, full eighteen-voltage/eighteen-current checkpoint and count.
Initial checkpoint and observation are serialized separately.

This adapter preserves the same original input polygon across subdivisions;
it does not generate higher-rate sinusoidal endpoints, interpolate outputs,
filter aliases, rotate a scanner or establish a complete host pipeline.

## Authored focused coverage

The fifteen test cases cover:

- Every supported internal rate and both modes, all common identities and
  diagnostics, rational DC from literal documentary resistors and independent
  source/return KCL signs. Six frequency samples per group are producer checks,
  not the complete 282-bin independent stationary grid.
- Frequency order/repetition, exactly 1024 responses and one-over-limit rejection.
- Actual 997-Hz sine processing in both modes, odd half-window lengths,
  retained checkpoint and response consistency; a separate short startup
  explicitly differs from stationary response and retains nonzero fit residuals.
- Signed initial physical coordinates, energy and clock; all five subdivisions
  in both modes; equal original-polygon flow and exact ordinary expanded-input
  endpoint replays; exact tiny last input despite cancellation in a naive formula.
- Exact uint64 saturation after internal-step counting, overflow before output,
  16,384 knots/262,144 steps and one-over-limit rejection.
- Missing/duplicate/unknown/irrelevant options, strict numbers, modes/rates,
  sine bounds, state/energy rejection, LF/CRLF and exact line-byte boundaries.
- Overlong UTF-8 options constructed below Windows's command-line UTF-16 limit,
  so the actual probe adapter, rather than CreateProcess, performs the rejection.
- Complete stdout preservation on argument/input/process failures and actual
  `/dev/full` output-stream failure on POSIX. That one OS-specific test is
  explicitly skipped where the failing stream is unavailable.

No expected result comes from the old trapezoidal output. Same-rate process
consistency and subdivision composition are named producer checks, not an
independent continuous-flow oracle. Full FOH reference and original analog
same-Hz grading remain with the subsequent owners.

## Verification and next action

Executed by A16: source/contract reads, Python AST parsing, owned-file whitespace
checks, SHA-256 calculation, compile-command inspection and read-back of root's
actual `Testing/Temporary/LastTest.log`. A16 invoked no probe or build. Root
built `hammond_scanner_line_foh_probe` in the coordinated native Release tree
with GCC 14.2, then ran
`ctest -R '^python_test_scanner_foh_probe$' --output-on-failure --no-tests=error`.
The required selection passed **1/1 in 1.83 s** (**1.84 s total**). Python 3.12
reported **15 tests in 1.753 s, OK**, including the POSIX failing-output test;
no case was skipped in this Linux run. No source repair was needed after the
first coherent build. Root retains `a16-build.log` and `a16-ctest.log` and owns
their durable report placement.

The test duration includes subprocess startup, preparation, parsing and
serialization. It is not a line-only timing or callback-deadline measurement.
Other OS/ABI runs, sanitizers, full independent qualification and complete
source publication were not executed by A16.

| Tested input/output | SHA-256 |
| --- | --- |
| New probe source | `470597a58ba352f737119a8a75de1c2f1c50df3fe4e7dfb400e7641c14c46b2a` |
| New Python test | `124d2a137cfb4fc3200d61e4d5d2de104863f875592a2c84da759dab4bdc2b40` |
| New core header | `c7cf443b9fe85f0fe544605b2a15fbc2539661f735ca62760dbb510f7111b887` |
| New core implementation | `9f5ff3f25f3564774ecaace292eb9299b3d75e897ce7fe6b30a59575addc24df` |
| Generated scanner header | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |
| Native probe executable | `4cd01de590f66c266e5fa00d769136188161eadbc17c98d0e543a2fbccaf3ac2` |

| Preserved input | SHA-256 |
| --- | --- |
| Old ScannerLine header | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| Old ScannerLine implementation | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| Old native probe | `4a283205949a837df8835f2b86874ee66624631d05fbdf8a6ccce7ff54e16fdb` |
| Authoring graph | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |

Next independent owners can consume this stable CLI/JSON to build graph-derived
FOH references, complete stationary/process/transient reports, report admission,
lifecycle and resource evidence. G5 complete, G6/Engine and physical M4 remain
separate and unqualified by this producer suite.

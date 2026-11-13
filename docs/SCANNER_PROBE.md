# Native scanner line probe

`hammond_scanner_line_probe` exposes three distinct offline experiments for
[`ScannerLine`](SCANNER_LINE.md): the prepared recurrence response, an actual
frame-processing sinusoid measurement, and an actual endpoint/state trace.
It is a nominal unloaded line diagnostic, not an Engine route, rotor, audio
renderer, quality-policy selector or measured specimen. The
[numerical contract](SCANNER_NUMERICAL_CONTRACT.md) owns grading; the probe
reports data and never labels a numerical gate passed.

The implementation is [`scanner_line_probe.cpp`](../tools/scanner_line_probe.cpp).
It links the same `hammond_core` as other consumers and embeds the generated
scanner authoring fixture identity. It does not read a replacement circuit
file or mutate the admitted nominal graph.

## Build and output contract

From the repository root, with a C++20 compiler, CMake and Python 3:

```sh
cmake -S . -B build-scanner -DCMAKE_BUILD_TYPE=Release
cmake --build build-scanner --config Release --target hammond_scanner_line_probe
build-scanner/hammond_scanner_line_probe --help
```

For a multi-configuration generator, use the executable in the selected
configuration directory, for example `build-scanner/Release/`. Windows builds
use the repository's strict Unicode `wmain` argument adapter; MinGW needs the
target's `-municode` startup option. Hosted platform execution must be qualified
separately from a local compile.

Successful experiments write one JSON document to stdout and exit 0. Argument,
input, preparation, process and measurement failures exit 1 with a diagnostic
on stderr. The entire document is prepared before writing stdout, so these
failures emit no partial JSON. A downstream output-stream failure can occur
after some bytes have already been written; that also reports failure. The
program opens no output files. A caller capturing stdout owns publication,
atomic replacement and overwrite prevention; ordinary shell `>` redirection
can truncate an existing file before this program starts.

All numbers use the classic locale and `max_digits10`. Floating decimal input
uses the repository's [portable parser](DECIMAL_PARSING.md), and probe
arithmetic/serialization selects nearest rounding while preserving the previous
mode on exit. Integer counters use exact unsigned decimal conversion. Numeric
tokens reject whitespace, trailing text, nonfinite spellings and unrepresentable
overflow/underflow. Both decimal signs, scientific notation and signed zero
follow the shared parser contract.

Every invocation requires `--operation`, `--sample-rate` and `--mode` exactly
once. `--help` is accepted only alone. Unknown, duplicate, missing, irrelevant
or oversized options reject. The supported research rates are the numeric
products of `{44100,48000,96000}` and `{1,2,4,8,16}`: fifteen experimental pairs,
eleven distinct numeric rates. A caller must retain its host/multiplier label
when rates coincide. These rates do not extend the Engine/native host API.

### Common JSON fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `probe_id` | `scanner-line-probe-v1`. |
| `evidence_scope` | `synthetic_nominal_engineering`. |
| `operation` | `response`, `sine` or `trace`. |
| `model_id` | `atlas-late-b3-nominal-line-v1`. |
| `realization_id` | `scaled-physical-trapezoidal-scanner-line-v1`. |
| `authoring_sha256` | SHA-256 of the fixture bytes compiled into the linked core. |
| `sample_rate_hz`, `mode` | Actual internal solver rate and `vibrato` or `chorus`. |
| `clock_convention` | Previous endpoint at minus one sample, first supplied knot at zero, frame counter counts completed intervals. |
| `preparation_residual` | Largest normalized solve residual from both prepared return topologies. |

Complex numbers are always `[real, imaginary]`. Tap order is `v1..v19`,
ground-referenced with signed voltage preserved. Input admittance is amperes
per volt, positive from the ideal source into the line. No gain, polarity,
per-tap phase or fitted delay correction is applied.

## Prepared recurrence response

```sh
build-scanner/hammond_scanner_line_probe --operation response \
  --sample-rate 48000 --mode chorus --frequencies 0,100,997,5000,7000,20000
```

`--frequencies` is a comma-separated list of 1–1024 finite values, each in
`0 <= f < sample_rate/2`. Order and repeated frequencies are retained. DC is
an exact zero-frequency recurrence solve; it is not the independent rational
DC oracle. This operation calls `ScannerLine::response` and does not advance
any frame.

`measurement_method` is `prepared_discrete_recurrence_solve`. Each entry in
`responses` contains:

```json
{
  "frequency_hz": 997,
  "taps": [[0.1, -0.2]],
  "return_gain": [0.1, -0.2],
  "input_admittance": [0.00001, -0.00002],
  "normalized_residual": 0,
  "condition_inf": 1
}
```

The numbers above illustrate structure only; actual `taps` always contains
nineteen complex entries. Residual and condition refer to the current-scaled,
row-scaled discrete recurrence matrix documented in `SCANNER_LINE.md`.
Independent comparisons must keep both warp-matched and same-hertz results.
Agreement with this helper alone does not qualify `process_frame`.

## Actual sinusoid processing

```sh
build-scanner/hammond_scanner_line_probe --operation sine \
  --sample-rate 48000 --mode chorus --frequency 997 \
  --warmup-frames 65536 --measurement-frames 65536 --amplitude 1
```

This operation starts from the cold physical checkpoint with previous input
zero. At knot `n` it supplies `amplitude*cos(2*pi*frequency*n/sample_rate)` to
`process_frame` and measures the returned endpoint. It never calls
`ScannerLine::response`. Frequency must be strictly between DC and Nyquist;
amplitude must be in `(0,64]` volts. Default amplitude is 1 V and default
warmup/measurement lengths are 65,536 frames each. Zero warmup is allowed as
an explicit startup experiment. The measured window needs at least eight
frames and four cycles; warmup plus measurement is bounded by 16,777,216 frames.

The estimator fits the actual measured output to cosine, sine and a constant
using a three-column least-squares system. It accepts non-bin-centered
frequencies and uses the declared input clock directly. If fitted coefficients
are `a*cos + b*sin + c`, the reported transfer is `(a - j*b)/amplitude`.
The constant is a nuisance offset in the estimator, not a modification to the
signal. Ill-conditioned fits reject; no phase alignment is fitted. Accumulation
uses `long double`, whose precision is platform-dependent.

`measurement_method` is
`actual_process_frame_cos_sin_constant_least_squares`. The JSON retains
`frequency_hz`, `amplitude_volts`, `warmup_frames`, `measurement_frames`,
`first_half_frames`, `second_half_frames` and:

| Field | Meaning |
| --- | --- |
| `transfer` | Whole-window object containing `taps` (19 complex gains), `return_gain`, `input_admittance`. |
| `first_half_transfer`, `second_half_transfer` | The same transfer structure fitted independently to the two non-overlapping measurement halves. Odd lengths give the extra frame to the second half. |
| `half_window_max_difference` | Largest absolute half-to-half complex difference over taps, return and `15000*input_admittance`. |
| `half_window_current_scale_ohms` | The explicit value `15000`. |
| `fit_residual_rms` | Residual signal RMS with `taps_volts` (19 entries), `return_volts`, `input_current_amps`. |
| `final_state` | Physical checkpoint after all warmup and measured intervals. |

The residual RMS is computed from the least-squares sum of squares. A slightly
negative value caused by subtraction roundoff is clamped to zero before the
square root. It is a diagnostic, not an acceptance test or a claim of exact
zero residual. The two half-window estimates are also diagnostics; they do not
replace repeating the experiment with a longer startup removal. Accordingly,
`startup_convergence_status` always says `caller_must_compare_longer_warmup`.
The frozen four required sine frequencies and bounds remain the caller's job.

## Actual endpoint and physical-state trace

Supply one finite input voltage per stdin line. LF and CRLF are accepted;
whitespace-only lines, blank lines and comments are not. A final newline is
optional. There must be 1–16,384 knots, each at most 128 input bytes and within
`[-64,64]` volts. The entire bounded input is validated before processing.

```sh
printf '1\n0\n-0.5\n0\n' | build-scanner/hammond_scanner_line_probe \
  --operation trace --sample-rate 48000 --mode vibrato
```

Optional `--capacitor-volts` and `--inductor-amps` each take exactly eighteen
comma-separated coordinates. `--previous-input` sets the previous endpoint
drive and `--initial-frame` supplies an unsigned 64-bit completed-interval
counter. Omitted coordinates and counters are zero. The line's joint physical
state/energy admission rules apply; individually bounded entries may still
exceed the total energy bound. A request that would overflow the counter rejects.

The trace uses one fixed mode and rate. Its `measurement_method` is
`actual_process_frame_endpoint_trace`, `input_reconstruction` is
`trapezoidal_endpoint_forcing`, and `time_origin` is
`relative_to_first_supplied_input_knot`. It emits the restored `initial_state`,
an `initial_observation` at `-1/sample_rate` seconds, and a `frames` array.
Each processed row contains:

| Field | Meaning |
| --- | --- |
| `knot_index`, `time_seconds` | Zero-based supplied knot and its relative time `knot_index/sample_rate`. |
| `input_volts` | Supplied input at that knot. |
| `frame` | Restored counter plus the number of completed intervals; the first is initial count plus one. |
| `taps_volts` | Nineteen signed ground-referenced endpoint voltages. |
| `return_volts`, `input_current_amps`, `energy_joules` | Actual line observation and stored physical energy. |
| `state` | `capacitor_volts[18]`, `inductor_amps[18]`, `previous_input_volts`, `frames`. |

A nonzero restored counter does not change this explicitly relative time
origin. A resumed trace's first physical interval starts from its supplied
checkpoint; users reconstruct absolute time from their rate schedule. Mode
and rate switching are exercised through the core API rather than hidden
stdin commands. This format is a research replay checkpoint, separate from
saved musical controls.

## Limits and qualification boundary

The CLI admits at most twelve named options, 32,768 bytes per argument,
1,024 response frequencies, 16,384 trace knots and 16,777,216 sine frames.
Report size is capped at 64 MiB. Fixed dimensional output and bounded row
counts bound memory even though offline parsing and serialization allocate.
No CLI allocation or file/stream operation occurs inside the core processing
method; this tool does not itself establish callback allocation or timing.

Producer checks are recorded in
[assignment 16](development/2026-11-13-scanner/16-scanner-probe.md).
Independent full-grid, process and transient acceptance must identify the
compiled executable, core source, graph fixture and frozen contract. A passing
probe comparison cannot select an audible resampling/filter policy or establish
hardware fidelity, Engine/native integration or DAW qualification.

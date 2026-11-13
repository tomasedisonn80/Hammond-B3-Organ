# Nominal console trace

`hammond_console_trace` exports bounded, deterministic CSV diagnostics from the
actual Engine. It records independent contact travel, shared percussion readiness,
routing and shared source phases alongside each sample they produce. This is an
offline inspection tool for the nominal model, not an acquired instrument
measurement, a callback interface or a restorable DSP checkpoint.

The [console contract](CONSOLE_DYNAMICS.md) owns the unmeasured coefficients and
timing convention. Atlas pp. 115-120 describe independent contact history; pp.
133-135 describe shared percussion; pp. 389 and 401 distinguish controls and
routing from dynamic histories. The trace exposes that scoped implementation
without adding a new DSP algorithm or claiming complete physical preset behavior.

## Build and run

```sh
cmake --build build --target hammond_console_trace
cmake -E make_directory out
./build/hammond_console_trace --profile build/nominal.b3p \
  --scenario partial --sample-rate 48000 --seed 0 --output out/partial.csv
```

Use the configuration subdirectory for executables from a multi-configuration
build. All five options are required exactly once, in any order. `--help` must
appear alone. There are no positional arguments, abbreviated flags or implicit
profile searches. Values are at most 4096 bytes; rate and seed are unsigned
decimal integers of 1-20 digits. The rate must be exactly 44100, 48000 or 96000;
the seed must fit an unsigned 64-bit integer. Unknown, duplicate, missing or
invalid arguments fail with a diagnostic on stderr and a nonzero exit status.

The profile must be an existing regular file accepted by the bounded compiled
profile loader and by Engine preparation at the selected rate. The output's
parent directory must already exist. Existing files, directories and symlinks,
including dangling symlinks, are preserved. The complete trace is generated and
bounded before any temporary output is created. A private sibling directory is
reserved atomically, its file is written/flushed/closed, and a hard link publishes
the complete CSV without replacing a destination created in the meantime. A
filesystem supporting hard links is required. Write, flush, close or publication
failures return nonzero and attempt temporary cleanup. Successful runs emit no
stdout text; the CSV file is the result.

## Versioned scenarios

Every version-1 scenario lasts exactly **120 ms**: 5292, 5760 or 11520 rows at the
three supported rates. A command at integer millisecond `m` is applied at frame
`floor(sample_rate * m / 1000)`. Rows are contiguous frames `0..frames-1`; there is
no extra post-run row. All commands target the upper manual. The primary key is
MIDI 60; the companion key is MIDI 67.

All scenarios explicitly prepare `make_nominal_console_model()` and start with
percussion On / Second / Normal / Fast. Initial retained banks are all zero, bank
B is selected, both routes are enabled, and expression is one. The four percussion
controls are flushed before frame-zero scenario commands. Sustained drawbars stay
zero throughout, so audible output comes only from the eligible second-harmonic
percussion contacts. A positive note-on uses velocity 100; velocity does not
change this model's sustained level or motion.

### `partial`

| Millisecond | Command | Index | Value | Purpose |
| ---: | --- | ---: | ---: | --- |
| 0 | KeyPosition | 60 | 0.5 | Approach a partial hold from below |
| 16 | NoteOn | 60 | 100 | Complete the press after a positive partial target |
| 32 | KeyPosition | 60 | 0.5 | Approach the same hold from above |
| 48 | KeyPosition | 60 | 0.46 | Retain the fifth contact inside its hysteresis band |
| 56 | KeyPosition | 60 | 0.4 | Cross that contact's break threshold |
| 64 | NoteOff | 60 | 0 | Begin normal release |
| 68 | KeyPosition | 60 | 0.55 | Reverse before complete return |
| 84 | NoteOn | 60 | 100 | Complete another press |
| 100 | NoteOff | 60 | 0 | Release the detector |
| 104 | NoteOn | 60 | 100 | Repress with finite recovery |
| 112 | AllNotesOff | 0 | 0 | Immediate upper-manual panic; readiness keeps recovering |

The first 0.5 hold closes contacts 0-3. The return to 0.5 retains contacts 0-4.
Second-harmonic contact 3 can emit audio before physical ninth contact 8 closes;
shared readiness remains one during the initial partial hold. The companion stays
at rest. Exact crossings occur on the selected sample grid.

### `legato`

| Millisecond | Command | Index | Value |
| ---: | --- | ---: | ---: |
| 0 | NoteOn | 60 | 100 |
| 16 | NoteOn | 67 | 100 |
| 32 | NoteOff | 60 | 0 |
| 48 | NoteOff | 67 | 0 |
| 52 | NoteOn | 60 | 100 |
| 72 | NoteOff | 60 | 0 |
| 96 | NoteOn | 60 | 100 |
| 112 | AllNotesOff | 0 | 0 |

The joining key shares existing readiness. Releasing the primary while the
companion detector remains closed does not recharge it. Later releases expose
short and longer recovery intervals without any event resetting readiness.

### `routing`

| Millisecond | Command | Index | Value |
| ---: | --- | ---: | ---: |
| 0 | NoteOn | 60 | 100 |
| 16 | Cancel | 0 | 0 |
| 32 | SelectBank | 0 | 0 (A) |
| 48 | SelectBank | 0 | 1 (B) |
| 64 | Percussion | 0 | 0 (Off) |
| 80 | Percussion | 0 | 1 (On) |
| 96 | NoteOff | 60 | 0 |
| 112 | AllNotesOff | 0 | 0 |

Cancel leaves the physical key closed while disconnecting routing. Bank A
re-enables the route but remains ineligible for percussion. Bank B restores
eligibility; the Off/On interval separately shows retained routing with disabled
percussion. These transitions change neither current source phase nor readiness.
Readiness subsequently recovers whenever the routed detector is false.

## CSV schema 1

The file uses ASCII-compatible UTF-8, LF line endings, classic decimal formatting
and no path, timestamp or locale-dependent fields. Floating values use binary64
`max_digits10` precision (17 significant digits); `audio` is the Engine's binary32
output printed with that precision. Identical inputs on the same build produce
identical bytes. Cross-platform libm output need not be byte-identical.

Exactly 28 initial comment lines have the form `# key=value`, in this order:

| Key | Meaning/value |
| --- | --- |
| `hammond_console_trace_schema` | `1` |
| `evidence_scope` | `synthetic_engineering` |
| `source_model` | `ideal-shared-sine-v1` |
| `contact_model` | `nominal-linear-travel-v1` |
| `percussion_model` | `shared-readiness-v1` |
| `scenario` | Selected scenario |
| `scenario_version` | `1` |
| `profile_id` | Validated compiled profile's declared ID |
| `authoring_sha256` | Compiled profile's declared authoring digest |
| `profile_digest_scope` | `declared_authoring_not_compiled_hash` |
| `sample_rate` | Samples per second |
| `seed` | Selected unsigned seed |
| `frames` | Number of following data rows |
| `timing` | `after_events_before_render_and_advance` |
| `manual` | `upper` |
| `primary_midi` | `60` |
| `companion_midi` | `67` |
| `primary_tone_id` | Source routed by primary contact 3 |
| `companion_tone_id` | Source routed by companion contact 3 |
| `primary_frequency_hz` | Primary tracked source frequency, Hz |
| `companion_frequency_hz` | Companion tracked source frequency, Hz |
| `primary_source_peak` | Primary normalized source amplitude |
| `companion_source_peak` | Companion normalized source amplitude |
| `profile_output_gain` | Owned normalized output gain |
| `initial_percussion` | `on_second_normal_fast` |
| `sustained_drawbars` | `all_zero` |
| `row_count_limit` | `11520` |
| `byte_limit` | `8388608` |

The authoring digest is retained provenance from the supplied compiled profile.
The tool does not hash or authenticate unseen authoring JSON or the compiled file.
Retain the exact input, executable and toolchain identity separately when using a
trace as evidence. Source IDs are one-based tone IDs, not physical terminals or
MIDI numbers. No fixed source number is assumed when looking up the two routes.

The next line is the 36-column CSV header, in this exact order:

```text
frame,time_seconds,position,target,c0,c1,c2,c3,c4,c5,c6,c7,c8,companion_position,companion_target,companion_c0,companion_c1,companion_c2,companion_c3,companion_c4,companion_c5,companion_c6,companion_c7,companion_c8,readiness,physical_detector,eligible,routed_detector,percussion_gain,upper_sustain_gain,route_enabled,selected_bank,percussion_enabled,primary_phase_turns,companion_phase_turns,audio
```

| Columns | Units and interpretation |
| --- | --- |
| `frame`, `time_seconds` | Current render frame; `frame/sample_rate` seconds |
| `position`, `target` and companion equivalents | Normalized key travel in `[0,1]` |
| `c0..c8` and companion equivalents | Physical contact bits, integer 0/1 |
| `readiness` | Shared dimensionless `q` in `[0,1]` |
| `physical_detector` | OR of upper-manual contact 8, integer 0/1 |
| `eligible` | Percussion On, upper route enabled and B selected, integer 0/1 |
| `routed_detector` | Physical detector AND eligibility, integer 0/1 |
| `percussion_gain`, `upper_sustain_gain` | Current dimensionless routed gain diagnostics |
| `route_enabled`, `percussion_enabled` | Current upper routing and control bits, integer 0/1 |
| `selected_bank` | Integer 0=A, 1=B; independent of route enable |
| `primary_phase_turns`, `companion_phase_turns` | Current shared source phases in `[0,1)` turns |
| `audio` | Same-frame normalized floating mono sample; no PCM quantization |

For each frame the tool applies scheduled events with zero-frame flushes, copies
public diagnostics, then renders one sample. It writes the saved state and that
sample into one row. Engine advances its internal state once after producing the
sample, ready for the next row. No extra sample is rendered for diagnostics;
formatting, allocation and file access occur outside Engine processing calls.
The complete file is limited to 8 MiB and at most 11520 data rows. The schedules
are fixed, so this is not an arbitrary score parser or a live tracing facility.

## Verification and next gate

Assignment 40's implementation smoke and source identities are retained in its
[development note](development/2026-11-13-continuation/40-console-trace.md).
Assignment 41 owns permanent independent CLI, schedule, numerical and failure
checks. The continuation ledger owns the combined staged-source, publication and
hosted-platform results. Local installation of this new executable is a separate
packaging gate. This trace establishes no hardware authenticity, complete circuit
behavior, live UI transport, native host support or audio callback deadline.

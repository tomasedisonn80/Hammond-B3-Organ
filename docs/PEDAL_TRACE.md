# Actual Engine pedal trace

`hammond_pedal_trace` exports three bounded CSV scenarios from the actual
Engine's pedal buses, mixtures, contacts and output. It is an offline diagnostic
for the named nominal model. It does not measure a physical pedal network,
instantiate another source bank, provide a live UI transport or save a DSP
checkpoint.

The source basis is [atlas pp. 139–144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139):
shared generator identity, four pedal buses, distinct repeated/null connections,
manual/pedal interactions and separately declared physical unknowns. The
[Engine contract](PEDAL_ENGINE.md) and [fixed voice](PEDAL_VOICE.md) define the
implemented behavior. The matrix and linear gain remain original, unmeasured
engineering fixtures; reactor/loading, physical contact timing and calibrated
footage responses are separate work.

## Build and invoke

```sh
cmake --build build --target hammond_pedal_trace
cmake -E make_directory out
./build/hammond_pedal_trace --profile build/nominal.b3p \
  --scenario routing --sample-rate 96000 --seed 0 --output out/pedals.csv
```

For a multi-configuration generator, use its configuration directory and build
configuration; a typical Windows executable is
`build/Release/hammond_pedal_trace.exe`. Local installation is a later packaging
gate. This change adds the build target and test executable environment only.

All five options are required exactly once, in any order. `--help` must appear
alone. There are no positional arguments, implicit profile searches, abbreviated
flags, arbitrary scores or caller-selected durations. Every value contains
1–4,096 bytes. Rate/seed strings contain 1–20 unsigned decimal digits; leading
zeros are accepted. The rate is exactly 44,100, 48,000 or 96,000 Hz, and seed is
in `0..2^64-1`. Scenario is exactly `unmute`, `overlap` or `routing`.

The profile must resolve to an existing regular file admitted by the bounded
compiled-profile loader and Engine preparation. These fixed scenarios require
manual MIDI 48, zero-based drawbar 2, to route to source 25; a different route
rejects before output creation. This guarantees the declared collision with
pedal 25's first contact and pedal 1's fourth contact. The requirement is a
software scenario anchor, not a physical pedal MIDI-octave assignment. Other
admitted source/profile values are consumed as supplied and reported as declared
provenance.

The output's parent must already exist. Existing files, directories and symlinks,
including dangling symlinks, are preserved. The complete CSV is generated and
bounded before reserving a private sibling directory. Its file is written,
flushed and closed, then published by a hard link without replacing a destination
created in the meantime. The filesystem must support hard links. Failures return
nonzero, report on stderr and attempt to remove owned temporary files/directories;
they never deliberately remove an existing destination. Success emits no stdout
or stderr. This follows the existing [console trace](CONSOLE_TRACE.md) publication
convention.

## Fixed version-1 scenarios

Every scenario lasts exactly **120 ms**: 5,292, 5,760 or 11,520 rows. A command
at integer millisecond `m` applies at frame `floor(rate*m/1000)`, before that
sample. Equal-time commands preserve the table order. There is no extra final
row and no elapsed sample during a control/event flush.

All scenarios prepare the explicit legacy console model: ideal manual contacts,
percussion Off and expression one. Both manual banks select B and both routes
start enabled. Only zero-based manual drawbar 2 is nonzero: Upper position 8,
Lower position 4. All other manual drawbars remain zero. The tracked manual key
is MIDI 48, whose selected drawbar shares source 25. A positive note/pedal On
uses velocity 100; velocity does not scale the sustained model.

| Scenario | Initial pedal positions | Purpose |
| --- | --- | --- |
| `unmute` | `0,0` | Observe nonzero pre-control mixtures while held pedals are inaudible, then change registration without resetting phase |
| `overlap` | `6,2` | Combine two pedals with upper/lower manual branches sharing source 25 |
| `routing` | `4,2` | Keep all 200 physical contacts visible through lower Cancel/reselection and independent division panics |

### `unmute`

| Millisecond | Action |
| ---: | --- |
| 0 | Press pedal 8, then pedal 12 |
| 20 | Set pedal mixture 0 to position 8 |
| 40 | Set pedal mixture 1 to position 4 |
| 60 | Set pedal mixture 0 to position 0 |
| 72 | Set pedal mixture 1 to position 0 |
| 80 | Set pedal mixture 1 to position 8 |
| 96 | Release pedal 8 |
| 104 | Release pedal 12 |
| 112 | Pedal panic |

Both pedals include a documented disconnected contact position. Those contact
bits still close, independently of whether their branches contribute audio.
No manual key is pressed in this scenario.

### `overlap`

| Millisecond | Action |
| ---: | --- |
| 0 | Press pedal 1 |
| 16 | Press Upper MIDI 48 |
| 32 | Press pedal 25 |
| 48 | Press Lower MIDI 48 |
| 64 | Release pedal 1 |
| 80 | Release Upper MIDI 48 |
| 96 | Release pedal 25 |
| 112 | Release Lower MIDI 48 |

### `routing`

| Millisecond | Action |
| ---: | --- |
| 0 | Press pedals 1–25 in ascending order, then Upper MIDI 48, then Lower MIDI 48 |
| 20 | Cancel the Lower manual route |
| 40 | Select Lower bank B, re-enabling its route |
| 60 | Lower manual AllNotesOff |
| 80 | Pedal AllNotesOff |
| 100 | Upper manual AllNotesOff |

All five disconnected contact positions are closed at the beginning. Lower
Cancel and manual panic retain the pedal targets, contacts and registration.
Pedal panic leaves Upper held and audible. The final interval is silent while
the source phase continues.

## CSV schema 1

Files use ASCII-compatible UTF-8, LF endings, classic locale and binary64
`max_digits10` formatting. The audio column contains the Engine's actual
binary32 sample promoted for printing; it is not PCM16. Same-build identical
inputs yield identical bytes. Cross-platform libm identity is not promised.

Exactly **37 initial comment lines** use `# key=value`, in this order:

```text
hammond_pedal_trace_schema,evidence_scope,source_model,manual_contact_model,
pedal_contact_model,pedal_routing_model,pedal_voice_model,pedal_gain_law,
pedal_map_id,pedal_map_raw_sha256,pedal_map_canonical_sha256,
pedal_reference_a_sha256,pedal_reference_b_sha256,mixture_matrix,
pedal_position_gains,pedal_weight_policy,signal_units,scenario,scenario_version,
profile_id,authoring_sha256,profile_digest_scope,sample_rate,seed,frames,timing,
contact_bits_order,pedal_targets_order,manual_midi,manual_drawbar_index,
tracked_tone_id,tracked_frequency_hz,tracked_source_peak,profile_output_gain,
percussion,row_count_limit,byte_limit
```

| Metadata | Interpretation |
| --- | --- |
| Schema/scenario version | Both `1`; evidence scope `synthetic_engineering` |
| Models | `ideal-shared-sine-v1`, `ideal-contacts-v1`, `ideal-eight-contact-pedal-v1`, `linear-pedal-bus-reference-v1`, `nominal-static-pedal-mixture-v1`, `linear-pedal-position-v1` |
| Map and references | Actual compiled map ID, raw/canonical map SHA-256, and both retained CSV SHA-256 values |
| Matrix | Actual compiled rows `0.5,0.25,0.125,0.125;0.125,0.5,0.25,0.125`; bus order Brown, Red, Orange, Yellow |
| Position gains | Actual compiled `0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1` |
| Weight policy | `all-200-unit-positive-v1`, including disconnected physical positions |
| Signal units | `dimensionless_source_normalized`; no voltage calibration |
| Profile | Supplied profile's declared ID/digest, source-25 frequency/peak and actual output multiplier |
| Digest scope | `declared_authoring_not_compiled_hash`; this tool does not hash/authenticate the supplied profile file or unseen authoring JSON |
| Timing | `events_then_pre_render_state_then_one_render_then_historical_record` |
| Contacts/targets | Pedals 1–25; within each pedal, contacts 0–7 |
| Limits | `row_count_limit=11520`, `byte_limit=8388608` |

Retain the exact compiled profile, executable, source and toolchain hashes
separately when using a trace as evidence. A retained authoring digest is not
proof that an independently modified compiled profile matches unseen JSON.

The following line is the exact **27-column header**:

```text
frame,sample_rate,time_seconds,pedal_position_0,pedal_position_1,brown,red,orange,yellow,mixture_0,mixture_1,pedal_output,audio,expression,active_pedals,pedal_targets,contact_bits,upper_down,lower_down,upper_route,lower_route,upper_bank,lower_bank,upper_drawbar,lower_drawbar,source_phase_before,clock_after
```

| Columns | Meaning |
| --- | --- |
| `frame`, `sample_rate` | Actual tags read from `Engine::last_pedal_frame()` after the sample renders |
| `time_seconds` | Actual tagged frame divided by its tagged rate |
| `pedal_position_0/1` | Positions recorded with that rendered sample, each integer 0–8 |
| `brown`, `red`, `orange`, `yellow` | Actual four same-frame bus excitations |
| `mixture_0/1`, `pedal_output` | Actual pre-control mixtures and separate `P`, before common expression/profile gain |
| `audio` | Actual same-frame normalized mono float from Engine |
| `expression`, `active_pedals` | Current pre-render expression and held-pedal count |
| `pedal_targets` | Exactly 25 bits, pedal 1 first; held targets |
| `contact_bits` | Exactly 200 bits; zero-based bit `8*(pedal-1)+contact`, preserving all null positions |
| `upper_down`, `lower_down` | Held targets for the scenario's MIDI 48 key |
| `upper_route`, `lower_route` | Manual routing-enable bits, independent of pedal targets |
| `upper_bank`, `lower_bank` | Selected manual bank, `0=A`, `1=B` |
| `upper_drawbar`, `lower_drawbar` | Retained position of each selected bank's zero-based drawbar 2 |
| `source_phase_before` | Source 25 phase in turns, queried **before** this sample renders |
| `clock_after` | Engine's next-sample frame clock **after** that one render; equals `frame+1` |

The exporter flushes scheduled commands, copies current contact/control/held
state and the pre-render phase, renders exactly one sample, then copies the
actual historical pedal record. It checks record validity, frame/rate/position
tags and the next clock before writing a row. It never recomputes the pedal
mixtures or calls `TonewheelBank` itself. Allocation, formatting and filesystem
operations occur outside Engine processing calls. The entire in-memory file is
bounded before any output is published.

## Independent acceptance and handoff

[test_pedal_trace.py](../tests/test_pedal_trace.py) executes the actual native
CLI. It reads both retained pedal CSVs and both manual CSV source-25 anchors,
independently derives source-byte hashes, and uses separately transcribed
scenario tables. Expected source samples use frozen initial-phase known answers
for seeds zero and `2^64-1`, followed by closed-form elapsed-time phase; the test
contains no production source recurrence or imported production model matrix.
It sums counted CSV branches independently, evaluates integer-numerator mixture
equations and explicit position/8 gain, then applies the actual profile gains
and a separate binary32 rounding operation.

Fixed numerical criteria precede execution: phase error at most `4e-12` turns,
bus/mixture absolute error `2e-9`, pedal `P` error `4e-9`, and mono float error
`4e-7`. These conservative bounds cover the 11,520-step accumulated binary64
phase versus closed-form oracle, the sine slope and 50-branch bus bound, followed
by mixture arithmetic and binary32 rounding. They are software error bounds,
not physical or perceptual tolerances. Tags, targets, contacts, controls and
silent intervals use exact comparisons.

The test also checks supplied nondefault profile peak/output gain, unsigned seed
boundaries, deterministic bytes, strict CLI rejection, invalid profiles and
route anchors, preservation of existing paths, and simultaneous no-clobber
publication. Symbolic-link checks execute when the platform grants creation;
an unavailable Windows privilege is explicitly reported in the test's JSON
summary rather than counted as executed symlink cases.

```sh
cmake --build build --target hammond_pedal_trace
ctest --test-dir build -R '^python_test_pedal_trace$' --output-on-failure
```

[Assignment 25](development/2026-11-13-pedals/25-pedal-trace.md) records the exact
coherent source, commands, initial test-fixture correction and final results.
Root's combined regression/publication, installed packaging, enabled-path
allocation, native hosts/devices and physical calibration remain separate gates.

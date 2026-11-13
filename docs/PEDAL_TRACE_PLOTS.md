# Pedal trace plots

`tools/plot_pedal_trace.py` turns a supported [actual Engine pedal CSV](PEDAL_TRACE.md)
into a deterministic, standalone SVG using only the Python standard library.
It supports the three version-1 scenarios: `unmute`, `overlap` and `routing` at
44,100, 48,000 and 96,000 Hz. Each plot covers the complete 120 ms trace.

The plots describe the **nominal, unmeasured, dimensionless engineering model**.
They do not establish physical contact timing, reactor response, electrical
loading, footage calibration, acoustic behavior or source-phase continuity.
The [atlas, pp. 139–144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139),
[Engine contract](PEDAL_ENGINE.md) and [pedal voice contract](PEDAL_VOICE.md)
remain the basis for those distinctions.

## Run

Generate a new trace and then a new plot; both output parents must exist:

```sh
cmake --build build --target hammond_pedal_trace
cmake -E make_directory out
./build/hammond_pedal_trace --profile build/nominal.b3p \
  --scenario routing --sample-rate 48000 --seed 0 --output out/routing.csv
python3 tools/plot_pedal_trace.py --input out/routing.csv --output out/routing.svg
```

Use the executable's configuration directory with a multi-configuration build,
for example `build/Release/hammond_pedal_trace.exe` on Windows. The Python tool
accepts only `--input TRACE.csv --output PLOT.svg`, once each in either order,
or `--help` alone. Paths may contain Unicode and spaces; each argument is
limited to 4,096 UTF-8 bytes. There are no repository-relative runtime inputs,
third-party Python dependencies, network calls or implicit profile lookups.

Success is silent. An error returns status 1 with a diagnostic on stderr.
The output parent must already exist and support hard links. Existing files,
directories and symlinks, including dangling symlinks, are preserved. The tool
validates and renders the complete plot before writing a private sibling file,
closing it, and publishing with a no-replacement hard link. A competing writer
can win publication; the loser leaves that destination intact. Temporary files
are cleaned up on ordinary exceptions. This is atomic publication, not a promise
of crash durability. Inputs must remain quiescent while they are read.

## Read the five panels

| Panel | Meaning |
| --- | --- |
| Pedal registration | The two integer positions, 0–8, as exact sample-boundary steps. Display labels “Mixture 1” and “Mixture 2” correspond to zero-based CSV suffixes `_0` and `_1`. |
| Four bus excitations | Brown, Red, Orange and Yellow values, before the fixed mixture matrix and pedal position gains. Their scales are dimensionless. |
| Mixtures and pedal output | Both pre-control mixtures and the separate `P` contribution. A zero position can mute `P` while a pre-control mixture continues. |
| Targets, contacts and manual independence | All 25 pedal groups, plus separate Upper/Lower held-key and routing-enable lanes. A dark pedal interval means its target and all eight checked physical contact bits are closed. |
| Final audio | The actual CSV audio column, with a symmetric automatic scale and its observed peak. These are normalized floating-point values, without PCM16 conversion or clipping at ±1. |

Pedals 8–12 have an asterisk. Their documented disconnected contact `c1` remains
part of each physical eight-contact group. The parser checks that bit along with
the other 199 bits; a disconnected branch does not erase its physical contact.
Grouping is admitted only for the declared ideal contact model, where all eight
bits equal their pedal target. Independently timed or bouncing contacts require
a different plot schema; they are rejected instead of hidden by this grouping.

The separate manual lanes make Lower Cancel visible while its key remains held.
They also distinguish manual panic, pedal panic and retained routing state. A
manual route can remain enabled after its held key is released. Source 25 phase
is validated as a finite fraction in `[0,1)` and retained in the original CSV;
it is deliberately omitted from the plot. A wrapped-phase picture would not
prove source continuity or shared-source identity.

## Reduction policy and limits

Every validated row contributes to each of the eight signal envelopes: four
buses, two mixtures, `P` and final audio. For `N` rows and `B=min(N,1000)`, bin
`j` contains frames `[floor(j*N/B), floor((j+1)*N/B))`. Its actual minimum and
maximum are drawn as one vertical stroke at the center of those sample frames.
The first and final samples are included. A one-sample spike survives as the
bin's extremum; there is no interpolation between bins and no first-sample-only
sampling. Timing within a bin is intentionally aggregated. For these scenarios
a bin spans about 0.12 ms, with integer-frame widths differing by at most one.

Each signal contributes at most 1,000 strokes, so signal reduction has at most
8,000 segments and 16,000 extrema endpoints. Pedal position steps and all 29
binary state lanes retain **every transition**, including a last-sample change.
A closed interval is `[first,end)`, ending at the exact next-sample boundary.
The CSV row cap bounds each position to at most 11,519 changes and each binary
lane to at most 5,760 closed intervals. Coordinates round to 0.001 SVG pixel;
there is no claim of retaining full binary64 numeric precision in an image.

| Limit | Behavior |
| --- | --- |
| Input | At most 8 MiB, regular file, ASCII-compatible fields, LF endings with final LF; no CR, BOM or NUL. |
| Rows | Exactly the declared 120 ms: 5,292, 5,760 or 11,520 rows. |
| Line | At most 4,096 bytes. |
| Metadata | Exactly 37 ordered schema-1 declarations, with bounded values. |
| Row | Exactly 27 fields, matching the documented header and canonical numeric forms. |
| Signals | Finite values; buses and pre-control mixtures within ±50, `P` within ±100, audio within ±102. These are conservative admitted model bounds, not measured signal levels. |
| Output | At most 1 MiB, 1200 × 1535 SVG units, no scripts, external images or remote font loads. Excessive exact-transition complexity rejects before publication instead of silently dropping transitions. |

The SVG contains its own title and description for accessibility, plus a visible
source SHA-256 and an XML `<metadata>` JSON object. The JSON retains **every
original metadata declaration**, the exact input-byte SHA-256, the plotting
policy, contact grouping, coordinate precision and validation scope. The same
input bytes produce the same SVG bytes with this tool version. Rasterizers and
font installations can produce different PNG pixels; the SVG is the retained
source artifact.

## What validation establishes

The parser checks the supported model identifiers, exact retained map/reference
SHA declarations, fixed mixture/gain/weight policies, scenario and schema
versions, signal units, timing and field order. It admits the declared
`nominal-unmeasured-v1` profile ID, a syntactically valid lowercase authoring
digest, source increment in `[2^-53,0.5)` turns/sample, and source peak/output
gain in `[0,1]`. Unknown profiles, other maps, other contact/voice/routing models,
other matrices, gain laws, scenario versions and sample rates are unsupported.
A profile with admitted values remains declared provenance, not authentication.

Rows must have contiguous frame numbers from zero, the declared rate, time
consistent with `frame/rate`, and `clock_after=frame+1`. The held count must equal
the number of target bits; all 200 ideal contact bits must agree with those
targets. Integer states, expression and phase must stay in their domains.
Recorded mixture values must agree with the recorded bus values within `2e-12`,
and `P` with recorded mixtures and positions within `4e-12`. These absolute
binary64 allowances cover arithmetic rearrangement for the admitted bounds.

Those checks do **not** rerender the Engine, authenticate an unseen compiled
profile, verify every source frequency/peak, enforce the scenario event schedule,
check final-audio summation or replay the phase recurrence. A fabricated but
structurally consistent CSV can pass. Retain the executable, profile, source and
toolchain identities separately. [The trace producer's independent tests](PEDAL_TRACE.md#independent-acceptance-and-handoff)
cover numerical Engine agreement; the plotter visualizes their recorded fields.

## Retained examples and acceptance

Three exact SVGs from the frozen wave-6 Linux producer, nominal profile, seed 0,
at 48,000 Hz are retained:

- [Unmute](examples/pedal-traces/unmute-48000.svg): positions change while both
  physical pedal groups remain held; pre-control mixtures continue through mute.
- [Overlap](examples/pedal-traces/overlap-48000.svg): the two pedal intervals and
  independent Upper/Lower key intervals overlap at their scheduled boundaries.
- [Routing](examples/pedal-traces/routing-48000.svg): all 25 groups remain closed
  through Lower Cancel; pedal panic releases them at 80 ms while Upper remains held.

The [test suite](../tests/test_plot_pedal_trace.py) combines hand-written schema
fixtures and known answers with actual producer executions for all nine
scenario/rate combinations. It covers malformed declarations/rows/numbers,
all five disconnected positions, single-sample extrema, final-sample state
changes, SVG escaping/accessibility/provenance, output complexity bounds,
no-clobber publication and concurrent writers. Symbolic-link cases report actual
execution or unavailable platform privilege explicitly.

After CMake discovers the new Python test, run:

```sh
ctest --test-dir build -R '^python_test_plot_pedal_trace$' --output-on-failure
```

For a direct run, set `HAMMOND_PEDAL_TRACE_EXECUTABLE` to the actual producer and
`HAMMOND_TEST_PROFILE` to the compiled nominal profile before invoking
`python3 tests/test_plot_pedal_trace.py`. Missing environment is a test failure,
not a skipped actual-producer check. The test needs no SVG renderer. Assignment
[45's evidence note](development/2026-11-13-pedals/45-pedal-plots.md) records exact
identities, commands, nine actual results, visual inspection and remaining gates.

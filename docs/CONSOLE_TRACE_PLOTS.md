# Plotting a nominal console trace

`tools/plot_console_trace.py` turns a validated
[console trace](CONSOLE_TRACE.md) into a standalone SVG. It uses only the Python
standard library. The diagram is an inspection aid for the existing nominal
model; it does not introduce a new contact or percussion model.

## Generate and inspect a plot

```sh
cmake --build build --target hammond_console_trace
cmake -E make_directory out
./build/hammond_console_trace --profile build/nominal.b3p \
  --scenario partial --sample-rate 48000 --seed 0 --output out/partial.csv
python tools/plot_console_trace.py --input out/partial.csv --output out/partial.svg
```

Use the executable's configuration subdirectory for multi-configuration builds.
Open the resulting SVG in an SVG viewer or browser. It contains all geometry,
labels, styles and provenance in one file, with no scripts, external images,
network requests or repository-relative assets. A title and description identify
the drawing for accessibility tools. Installed use invokes the script with a
Python interpreter; the installation contract is maintained separately.

The two required option pairs may appear in either order. `--help` must appear
alone. Unknown, duplicated, missing or abbreviated options, empty paths and path
arguments longer than 4096 characters are rejected. Successful plotting writes
no stdout or stderr text. Failures return nonzero with a diagnostic on stderr.

## What the four views show

All four panels use the same 0–120 ms horizontal scale.

| View | Representation |
| --- | --- |
| Key travel | Actual normalized positions for upper MIDI 60 and 67; dashed targets retain every recorded target transition |
| Shared percussion | Dimensionless readiness `q`, plus separate physical and routed detector bars |
| Contact closures | Both nine-contact banks as sample-grid closed intervals; contact `c8` supplies the physical percussion detector |
| Audio | Normalized floating output, shown as the minimum and maximum observed sample in each time bin |

The trace convention is preserved: each row describes state **after that frame's
events, before rendering and advancing the same sample**. A contact that is closed
at frame `n` is drawn over `[n/rate, (n+1)/rate)`. A transition appears at its actual
frame boundary. The drawing extends the final contact/target state through the
last sample interval, ending at 120 ms; it adds no simulated sample.

Positions and readiness retain the first, minimum, maximum and last observed
sample in each of at most **1010 time bins**, with uniformly spaced display
boundaries rounded down to sample indices. Lines connect those retained
observations as a visual guide. They are not a reconstruction of omitted
sample values. Audio uses one vertical minimum/maximum stroke per bin and no line
between bins, so short extrema are retained without inventing a waveform between
observations. Source phases remain available in the original CSV rather than
being compressed into an additional plot panel.

Contact and target transitions are never decimated. SVG coordinates are rounded
to 0.001 pixel in a 1200-by-1150 view box. This is drawing precision, not new
temporal or numerical precision in the source data. The original CSV remains the
exact record. Excessive transition complexity that would exceed the 1 MiB SVG
limit is rejected instead of silently dropping changes.

The audio scale is derived from the observed peak and may exceed ±1. The core
emits floating samples without a hidden PCM limiter. This trace's two possible
branches each have source peak at most 1, output gain at most 1 and percussion
gain at most 1.5, giving the conservative admitted bound **±3**. Values above PCM
full scale are therefore valid diagnostic input. This plotting bound says
nothing about the safety of converting that signal to a particular PCM format.

## Validation and provenance

The parser independently implements the documented trace schema; it imports no
generator or evidence-producer helpers. It accepts the three version-1 scenarios
(`partial`, `legato`, `routing`) at 44100, 48000 or 96000 Hz. It requires the exact
28 metadata keys in order, the exact 36-column header, the declared 120 ms row
count, contiguous frame indices, finite decimal fields and the supported model
and provenance declarations. It rejects missing or extra rows, duplicate or
unknown declarations, invalid bits, invalid domain values, nonfinite/underflowing
numbers, non-ASCII field bytes, NUL bytes and non-LF or incomplete line endings.

Recorded seconds must agree with `frame/sample_rate` within the larger of
`1e-15` seconds and four binary64 ULPs of that value. The plotter also checks the
simple routing relationships expressed by the trace: physical detector is the OR
of the two tracked ninth contacts; eligibility requires percussion On, an enabled
upper route and bank B; routed detector is physical detector AND eligibility.

The input must be an existing regular file no larger than **8 MiB**, with at most
**11520 rows** and 4096 bytes per data line. The open file's type/size and a bounded
read are checked. Input symlinks may resolve to a regular file; the retained hash
identifies the bytes actually read, not the path spelling. Concurrent hostile file
replacement is not an authenticated acquisition protocol.

Every SVG visibly includes the **SHA-256 of the complete input CSV bytes**. Its
embedded JSON metadata also retains that hash, scenario/version, rate, seed,
frame count, plotting reduction policy and the profile's declared authoring
digest. The latter remains a declaration from the CSV. The plotter does not read
or authenticate the compiled profile, unseen authoring JSON, renderer executable,
toolchain or source instrument.

Structural acceptance does not reenact the event schedule, phase integrator,
contact trajectory, percussion equation or sample mixer. A forged but structurally
consistent CSV can pass. Independent numerical acceptance of the producer belongs
to its dedicated tests, and physical admission/calibration requires separate
evidence. Both the visible figure and its metadata state this boundary.

## Publication and failure behavior

The output parent must already exist. Existing files, directories, symlinks and
dangling symlinks are preserved. The complete input is validated and the complete
SVG is generated within its bound before a temporary output is created.

The writer reserves a private sibling temporary directory, writes, flushes and
closes its file, then creates a hard link at the requested destination. The
hard-link operation does not replace a file another process created after
preflight. A filesystem supporting hard links is required. Failure at writing,
flushing, closing or linking returns an error and attempts temporary cleanup;
it does not publish a partial SVG. The tool provides no durability guarantee
against power failure and performs no in-place update of existing plots.

## Verification and next gate

`tests/test_plot_console_trace.py` uses independently authored structural fixtures
and checks supported rate/scenario declarations, numeric rejection, exact contact
interval placement, audio extrema above full scale, deterministic SVG/provenance,
XML escaping, transition-complexity limits, strict actual CLI behavior and
no-clobber/failure cleanup. These fixtures explicitly are not Engine simulations.

The [assignment 42 note](development/2026-11-13-continuation/42-trace-visualization.md)
records the observed local results, all nine actual scenario/rate plots and visual
inspection. The integrator owns the combined source gate, publication and hosted
platform results. Installed relocation is a separate assignment. No new native
UI, live transport, callback deadline, DSP replay or physical-fidelity result is
claimed by this offline drawing tool.

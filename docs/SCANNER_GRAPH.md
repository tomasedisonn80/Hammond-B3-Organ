# Nominal scanner graph and compiler

## Admitted identity and evidence

[`atlas-late-b3-nominal-v1.json`](../data/scanner/atlas-late-b3-nominal-v1.json)
is a newly authored documentary reconstruction of the atlas's late-B-3 paper
model, identified as `atlas-late-b3-nominal-line-v1`. It is not the missing
original companion graph and is not a measured specimen profile. The source
is the unchanged [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`:
values on p. 157 and connectivity on pp. 158, 175 and 182. The independent fresh
atlas [endpoint review](development/2026-11-13-scanner/02-atlas-scanner-graph.md)
and [physical-coordinate review](development/2026-11-13-scanner/03-atlas-scanner-electronics.md)
retain the source-reading evidence.

Admission verifies the declared source identity and locators. The compiler does
not reopen the 500-page PDF or independently establish the graph's physical
applicability. Repository source-integrity checks, primary-circuit review,
numerical qualification and hardware acquisition remain distinct checks.

## Exact electrical graph

There are 27 named nodes: datum `g`, driven node `p0`, section junctions
`p1..p18`, common return `r`, and divider midpoints `d1..d6`. Each signed branch
is oriented from its `positive` to its `negative` node. Passive-element
orientation establishes the voltage/current convention, not a claim that an
ordinary resistor has a unique physical polarity.

| Elements | Positive endpoint | Negative endpoint | Documentary nominal values |
| --- | --- | --- | --- |
| `L1..L18` | `p(k-1)` | `pk` | 500 mH each, compiled to 0.5 H |
| `C1..C17` | `pk` | `r` | 0.004 microfarad each, compiled to 4e-9 F |
| `C18` | `p18` | `r` | 0.001 microfarad, compiled to 1e-9 F |
| `R1+..R6+` | `p(k-1)` | `dk` | 27, 56, 39, 33, 18, 12 kOhm |
| `R1-..R6-` | `dk` | `r` | 68 kOhm; 0.15, 0.15, 0.18, 0.18, 0.18 MOhm |
| `Rc` | `r` | `g` | 22 kOhm |
| `Rt` | `p18` | `r` | 15 kOhm |

The 50 passives are 18 inductors, 18 capacitors and 14 resistors. The ideal
`Vin` boundary separately imposes `V(p0)-V(g)` in volts. `Sreturn` separately
shorts `r` to `g` for vibrato and opens for chorus. Its closed realization is
node contraction; an infinite conductance is not a numerical component value.

The first six dividers connect **before their inductors**. Outputs `v1..v6`
are `V(d1..d6)-V(g)`; outputs `v7..v19` are `V(p6..p18)-V(g)`. All nineteen
outputs use the same ground reference. In chorus, exporting voltages relative
to `r` would omit part of the intended signal. A DC solve alone cannot expose
an after-inductor divider error because ideal inductors short at DC.

## Authoring contract

The [JSON Schema](../data/scanner-line.schema.json) uses draft 2020-12. Every
structural record has an exact shape. Exact record enumerations, unique items
and exact counts require each admitted component and output once. Node and
component order may vary on input; the compiler emits canonical electrical
order. Explanatory assumption and acquisition prose is bounded and editable,
while status, units, identities and null unknown values remain fixed.

A component's `value` stores decimal `magnitude` as text, an explicit `unit`,
and an ASCII `printed` transcription. For example:

```json
{"magnitude": "0.004", "unit": "uF", "printed": "0.004 uF"}
```

`uF`, `kOhm` and `MOhm` are ASCII transcriptions of the source's unit symbols.
The fixture preserves decimal values and unit prefixes, not the source PDF's
typographic glyphs. The compiler converts through bounded decimal arithmetic
once when producing the SI representation; it retains the printed magnitude,
printed unit and transcription alongside `si_value` and `si_unit`.

Each passive retains its atlas pages, `documentary-nominal` evidence class,
and `not-supplied` uncertainty. The named ideal approximations are ideal coils,
ideal drive and unloaded tap observation. Eight unresolved physical quantities
retain null values, units, a reason and an acquisition task: winding resistance,
mutual inductance, stray capacitance, drive impedance, receiver loading, scanner
coupling capacitance, normalized-signal voltage scale and specimen revision.
No unknown is converted to a measured-looking zero.

The executable admission additionally checks duplicate JSON keys, exact scalar
types, finite positive magnitudes, all endpoints, references, units, provenance,
switch states, counts and identities. It limits input to 256 KiB, strings to
512 characters, nesting to 12 and recursive values to 4,096. It rejects control
characters and unsupported values. Numeric metadata uses integers; component
magnitudes use decimal strings. Booleans and JSON floating-point tokens are
not accepted as integer metadata. JSON Schema's numeric equality permits an
integral floating token in some constant locations; the compiler deliberately
enforces the stricter lexical rule.

A changed component, load, source boundary or topology needs a different model
identity and an explicitly designed contract. Numerical sensitivity experiments
may start from admitted SI data, but must label modified graphs as experiments
and must not republish them under this fixture's identity.

## Compiler APIs and commands

[`tools/compile_scanner_line.py`](../tools/compile_scanner_line.py) uses only
Python's standard library. Its public functions are:

| Function | Result |
| --- | --- |
| `load_profile(path)` | Validated original authoring dictionary |
| `load_profile_with_digest(path)` | Validated dictionary and SHA-256 from one bounded read of the same bytes |
| `validate_profile(profile)` | Original dictionary, unchanged, after complete admission |
| `normalized_profile(profile)` | Independent canonical SI dictionary; the original is untouched |
| `compile_profile(path, output_format="json")` | Deterministic JSON or C++ text from one admitted file snapshot |
| `write_output(path, text, input_path)` | Atomic publication to a separate regular destination |

All admission/publication failures raise `ScannerProfileError`. The SI
representation adds `representation: "scanner-line-si-v1"`; file compilation
also records `authoring_sha256`. The hash identifies raw source bytes, so a
whitespace-only source edit changes it even if the electrical arrays do not.
No timestamp, absolute input path or random identifier enters compiled output.

From the repository root, with an existing output directory:

```sh
python3 tools/compile_scanner_line.py \
  --input data/scanner/atlas-late-b3-nominal-v1.json \
  --output out/scanner-line.json --format json
python3 tools/compile_scanner_line.py \
  --input data/scanner/atlas-late-b3-nominal-v1.json \
  --output out/ScannerLineData.h --format header
```

The header exports `hammond::scanner_generated::kModelId`,
`kAuthoringSha256`, `kInductancesH`, `kCapacitancesF`,
`kDividerUpperOhms`, `kDividerLowerOhms`, `kReturnOhms` and
`kTerminationOhms`. All values are immutable `constexpr` data. Header generation
does not create a scanner runtime or change the organ's controls or signal path.

The CLI succeeds silently with exit 0. Rejection reports its reason to stderr
and exits 2. It validates and constructs the complete output before creating a
temporary file in the destination directory, flushes that file and atomically
replaces the destination. A rejected input or failed publication preserves the
previous output. It rejects output symlinks, nonregular destinations and aliases
of its input. Regular input reads are bounded, reject concurrent byte changes,
and reject FIFOs without waiting on the platforms providing nonblocking open.
Output directories must already exist; the compiler does not create them.

## Acceptance boundary and next step

The implementation assignment's [own checks](development/2026-11-13-scanner/07-scanner-graph-compiler.md)
cover admitted conversion, malformed graph rejection, deterministic output,
preservation of existing files and compilation of the generated C++20 header.
They are producer checks. Independent literal endpoint/schema tests, source
comparison and AC/transient/runtime evidence have separate owners and results.

Next, use this admitted graph for an independently stamped frequency reference,
including both return states, all signed taps, source current, conditioning,
residuals and topology/load sensitivity. Prepare the native physical-state line
only against independently qualified expectations. Neither schema admission nor
an eventual nominal numerical pass closes the missing specimen and loading gates.

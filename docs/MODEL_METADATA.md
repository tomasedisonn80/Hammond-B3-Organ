# Compiled console and pedal factory metadata

`hammond_model_info` exports the actual values returned by the C++ console-model
factories and the compiled nominal pedal routing/voice. It is an offline diagnostic
for reproducible engineering evidence.
It does not render audio, change the running engine, load a source profile or
inspect a physical instrument.

```sh
cmake --build build --target hammond_model_info
./build/hammond_model_info > console-models.json
```

Use `build/Release/hammond_model_info.exe` for a typical Windows Release build.
The only optional argument is `--help`; other arguments fail before JSON output.
The tool reports output-stream failure with a nonzero exit status. A broken pipe
may instead be terminated by the platform's pipe signal, also a nonzero result.
The shell owns the redirected destination; this command does not provide the
renderer’s no-clobber publication guarantee.

## Version 2 contract

The root JSON contains `schema_version: 2`,
`evidence_scope: "synthetic_engineering"`,
`physical_fidelity: "unestablished"`, a separate `source_generator` boundary,
two `console_models` in stable `legacy`, `nominal` order, and one `pedal_model`.
The source-generator record excludes the 91 sources' tuning, amplitudes, phases
and profile routing; those remain independent `RuntimeProfile` inputs and must
be retained with a render. The documentary pedal map is separately identified
in `pedal_model.routing`.

Version 2 preserves all earlier root and console field values and adds the pedal
object. The only changed earlier field is the outer schema version. Existing
version-1 metadata artifacts remain historical console-only descriptions; they
are not rewritten or interpreted as pedal metadata. This tool emits the current
version and does not parse old reports. Its schema is independent of renderer
summary schema 3, parameter diagnostic schema 1 and `B3CONTROLS3`.

Each console entry names the C++ factory actually invoked. Contact metadata
contains its algorithm ID, mode, units, proposed evidence class, atlas locators,
unknown uncertainty and a missing-capture explanation. The two manuals each
contain all 61 MIDI-key rows, and each row includes nine on thresholds, nine off
thresholds and full-travel press/release seconds. No shared template is substituted
for actual per-key values, even while the factories give every key equal defaults.

Percussion metadata contains its algorithm ID, dimensionless readiness coordinate,
declared gain map, all seven actual profile parameters and default controls. Each
parameter includes its value, unit, evidence class and atlas pages. The three RC
products are **derived hypotheses**, not measured audible decay times; the gain
choices are **proposed** normalized values. See [CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md)
for the exact semantics, provenance and replacement path.

### Pedal model and documentary routing

`pedal_model` has `runtime_state_included: false`, `evidence_class: "proposed"`,
atlas page locators 139, 140, 142, 144 and 447, unknown numeric uncertainty, and an
explicit missing-evidence reason. The fixed voice is the original engineering
fixture in [PEDAL_INTEGRATION_CONTRACT.md](PEDAL_INTEGRATION_CONTRACT.md); the atlas
provides its architectural basis and permits nominal progress, not the matrix's
chosen numbers. No measured reactor, source loading, contact motion or calibrated
16-foot/8-foot transfer is implied.

| Record | Exported meaning and source |
| --- | --- |
| `routing` | All eight strings returned by `compiled_pedal_identity()`, plus dimensions and statistics calculated from `compiled_pedal_routes()`. |
| `contacts` | The adopted ideal simultaneous-contact policy, canonical Lower event field, retained state for null positions, velocity-independent loudness, no owned source clock, and the freshly prepared kernel's actual closed-contact count. |
| `weights` | All 200 actual values returned by `nominal_pedal_reference_weights()`, in pedal/contact order, including disconnected positions. These are dimensionless branch weights. |
| `voice` | Compiled voice/gain-law IDs, mixture labels, matrix, position gains, default control positions, units and absolute input/output limits. |

`routing` contains `model_id`, `map_id`, `map_raw_sha256`,
`map_canonical_sha256`, `factory_comparison_id`,
`factory_comparison_raw_sha256`, `review_a_sha256` and `review_b_sha256`.
They identify the actual compiled map, comparison manifest and both independent
CSV inputs. Canonical map hashing follows the project's sorted-key JSON rule,
with compact separators, UTF-8, non-ASCII preservation, no NaN and no final LF;
it is not a claim of RFC 8785 canonicalization. The raw hashes retain file-byte
identity separately. The runtime exporter reads none of those source files.

The computed `pedal_count`, `contacts_per_pedal`, `position_count`, `bus_count`,
`connected_count`, `disconnected_count` and `repeated_source_pairs` describe the
compiled table. `bus_order` is `Brown, Red, Orange, Yellow`, with corresponding
`connected_per_bus` counts. The current factory table has 25 pedals, 200 positions,
195 connections, five disconnections and seven pairs of distinct contacts sharing
a source within one pedal. The bus counts are `[45,50,50,50]`.

Every entry in `disconnections` includes a **one-based** `pedal_id`, **zero-based**
`contact_index`, bus name and an explicit `source_tone_id: null`. Null is never
source zero. Repeated source pairs are counted without deduplicating their branch
weights. The routing record's documented evidence class refers to the retained
[factory comparison](FACTORY_REFERENCE.md); it does not rewrite the original
map's derived authoring provenance or establish specimen continuity.

The descriptive `contacts` policy fields belong to this metadata contract. They
are not an invented callable core contact-ID getter. The renderer separately
names the same adopted policy `ideal-eight-contact-pedal-v1`. The prepared kernel
starts with zero closed contacts. These defaults are not a query of any active
Engine, whose held pedals and null contact states may already differ.

### Exact nominal transfer and units

`voice.matrix` exports the actual compiled rows; its columns follow the reported
bus order. `voice.position_gains` exports the actual nine-entry gain table.
The adopted reference is:

| Mixture | Brown | Red | Orange | Yellow |
| --- | ---: | ---: | ---: | ---: |
| Pedal Mixture 1 | 4/8 | 2/8 | 1/8 | 1/8 |
| Pedal Mixture 2 | 1/8 | 4/8 | 2/8 | 1/8 |

Positions 0–8 use gain `p/8`. `default_positions` comes from a default
`ControlState` and is `[0,0]`. The exporter obtains IDs, labels, numeric matrix,
gains, defaults and limits from the compiled core; it does not restate the table
as an unrelated JSON constant. `weights.values` contains every unit-positive
branch value, including all five null positions. Matrix coefficients, gains and
weights are dimensionless; positions use `drawbar_position`. Bus excitation,
pre-control mixtures and combined pedal output use
`source_normalized_dimensionless`, not volts or PCM full scale.

`voice.absolute_limits` reports admitted absolute bus input 50, absolute mixture
output 50, and absolute combined pedal output 100. These are conservative
mathematical domains for the named voice, before the Engine's common expression
and profile output multiplier. They do not promise unclipped final audio or
measure a physical output. See [PEDAL_VOICE.md](PEDAL_VOICE.md) and
[PEDAL_ENGINE.md](PEDAL_ENGINE.md) for operation and the shared source boundary.

### Validation and serialization

The exporter calls the C++ factories and validates both console models at the three
supported sample rates before emitting JSON. It separately prepares the compiled
pedal table/weights, validates the default pedal controls and requires finite
matrix/gain values and finite nonnegative limits before returning any JSON. It constructs the document using
the classic locale, `max_digits10` precision, stable field order and a final LF.
On Windows, it selects binary stdout to prevent CRT newline conversion.
The complete output must remain strictly below 128 KiB; failure is reported before
publishing any JSON. Repeated invocations of the same build produce identical
bytes. Cross-compiler text identity is not a promised substitute for semantic
comparison or retaining exact executable and metadata hashes.

These records identify the **compiled factory defaults** only. Algorithm IDs
identify a family, not arbitrary custom C++ parameters. A caller that edits a
`ConsoleModel` must retain that actual parameter set independently; this exporter
does not discover it. Likewise, defaults are not the current settings, contacts,
readiness, source phases or clock of an active engine. No authenticity, hardware,
host, callback or deadline qualification follows from a valid metadata document.

## Verification

The focused `python_test_model_info` CTest reads the actual executable via
`HAMMOND_MODEL_INFO_EXECUTABLE`. It checks strict JSON, explicit source separation,
both modes, all 1,098 contact cells per factory, units, independent decimal/RC/gain
expectations, default settings, repeated bytes and locale-environment independence,
argument rejection, and output failure with a temporary file opened read-only
as the actual child process's stdout. The failure check requires a nonzero exit,
the exporter diagnostic, and unchanged destination bytes without a platform skip.
The CMake `check` target builds this executable before running the test.

The pedal checks independently hash the retained map/comparison/CSV bytes,
recompute canonical map bytes, count every cell in both 25-by-8 CSV readings,
and check all null records and repeated-source pairs. Separate rational
expectations verify all 200 weights, both matrix rows, nine gains, default
positions, units and mathematical limits. An actual audible pedal render checks
that its schema-3 identities and rational transfer description agree with the
metadata executable from the same build. Missing executables/profile inputs
are test errors, not skips. The installed/relocated model tool must report schema
2 while the independently versioned parameter tool continues reporting schema 1.

The exporter needs no source-profile file, map/CSV file or external dependency
at runtime. Source files are test or build inputs only. The original console
record remains in
[continuation note 12](development/2026-11-13-continuation/12-model-metadata.md);
this extension's coherent source identities, actual results and limitations are
in [pedal assignment 26](development/2026-11-13-pedals/26-pedal-metadata.md).

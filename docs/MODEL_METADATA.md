# Compiled console factory metadata

`hammond_model_info` exports the actual values returned by the C++ console-model
factories. It is an offline diagnostic for reproducible engineering evidence.
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

## Version 1 contract

The root JSON contains `schema_version: 1`,
`evidence_scope: "synthetic_engineering"`,
`physical_fidelity: "unestablished"`, a separate `source_generator` boundary,
and two `console_models` in stable `legacy`, `nominal` order. The source-generator
record expressly excludes tuning, source amplitudes, phases and wiring; those
remain inputs from a separate `RuntimeProfile` and must be retained with a render.

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

The exporter calls the C++ factories and validates both models at the three
supported sample rates before emitting JSON. It constructs the document using
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
argument rejection, and output failure on platforms with `/dev/full`.
The CMake `check` target builds this executable before running the test.

The exporter currently needs no source-profile file or external dependency.
Its local verification record is in
[continuation note 12](development/2026-11-13-continuation/12-model-metadata.md).

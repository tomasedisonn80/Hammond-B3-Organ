# Capture declaration readiness v1

`tools/capture_readiness.py` reports which declarations in one existing
[capture v1 manifest](CAPTURE_FORMAT.md) are present and which retain explicit
unknowns. It is an original project tool for M0/M8 planning. It does not read
artifact paths or follow evidence/rights locators, inspect audio, apply a
calibration, or decide that a physical acquisition may proceed. A complete
declaration can still be inaccurate, inadequate, unauthorized or unreviewed.

The exact contract below is frozen before the implementation and independent
acceptance. It preserves capture v1 without adding fields to that input format.
The [acquisition protocol](CAPTURE_PROTOCOL.md) supplies the separate physical
review procedure; the [atlas review](research/CALIBRATION_ATLAS_REVIEW.md) retains
the source basis and missing-evidence boundary.

## API and input admission

Python 3.10 or newer and the standard library are sufficient. The public API is:

```python
class ReadinessError(ValueError):
    code: str
    message: str

inspect_readiness(path: str | pathlib.Path) -> dict
main(argv: list[str] | None = None) -> int
```

`path` must be an exact nonempty `str` or a `pathlib.Path` instance. Other types,
including bytes, booleans, generic path-like objects and string subclasses, are
rejected. Relative paths use the current directory. Unicode paths are allowed.
The input leaf must be a regular nonsymlink, non-reparse file; ancestors may
contain ordinary OS aliases. The tool uses `capture_common.read_json` once with
these limits, then calls the unchanged `validate_capture.validate_capture` on
exactly the parsed object:

| Input limit | Inclusive value |
| --- | --- |
| Original UTF-8 bytes, including whitespace | 65,536 |
| JSON value nodes, excluding object keys | 4,096 |
| Nested container depth, root container depth zero | 16 |
| Numeric magnitude | 1e12 |
| Numeric token characters | 64, enforced by the shared parser |

Strict UTF-8, duplicate-key, BOM, nonfinite-number, Unicode and exact-type rules
come from the shared parser and unchanged v1 validator. V1 owns all required
keys, states, dates, units, channel order and local ancestry. An invalid v1
manifest produces an error, never a partial readiness report.

The input identity hashes the exact bytes admitted by that one read, including
whitespace. The manifest is not reopened or rewritten. Shared same-read
identity/size/timestamp checks detect observed changes during reading. Keep the
archive quiescent: this is not a hostile-filesystem sandbox, authentication
scheme or detection of changes restored between observations. Hard links and
allowed parent aliases are not additional acquisition evidence.

## Exact report

Every successful report has exactly these root keys:

| Key | Value |
| --- | --- |
| `schema_version` | Integer `1` |
| `contract_origin` | `project-proposed-capture-readiness-v1` |
| `scope` | `declared-metadata-only` |
| `capture_id` | Input `capture_id` |
| `capture_kind` | Input `capture_kind` |
| `record_status` | Input `status` |
| `status` | One of the three readiness statuses defined below |
| `input` | Exactly `sha256` and `size_bytes` for the admitted original bytes |
| `manifest` | Complete parsed v1 input, with all declarations and reasons unchanged |
| `calibration_context` | `raw_acquisition_only` |
| `checks` | Ordered check objects defined below |
| `summary` | Exactly `total`, `declared`, `missing`, `not_applicable`, all integer counts |
| `claims` | Exactly the seven fixed entries below |

`claims` always maps each of `artifact_integrity`, `audio_content`,
`authenticity`, `calibration`, `permissions`, `corpus_independence` and
`physical_fidelity` to `not_established`. These values never change because a
field has text or a declared calibration number.

V1 digital and calibration context belongs to the raw acquisition stream.
Derived files and their ancestry remain in `manifest.files`; this report does
not extend the raw stream's rate, channel map, calibration or rights scope to
those derivatives. Even an unmodified raw file has not been opened by this tool.

The report contains no tool execution time, hostname, input absolute path or
other environment-dependent field. Repeated reads of the same admitted bytes
produce equal reports. Separate calls return independent mutable objects.
The returned report is bounded to 16,384 value nodes, container depth 24,
numeric magnitude 1e12 and 1,048,576 canonical UTF-8 bytes. Excess output rejects
as `report_limit`; it is never truncated.

## Checks, exact state rules and order

Each check has exactly `path`, `category`, `state`, `reason` and `action`.
`path` is also its unique stable check identifier. A path names a v1 object or
field; bracketed channel indices use ordinary decimal integers without leading
zeros. `state` is `declared`, `missing` or `not_applicable`.

For an ordinary known-or-unknown field, a non-null `value` means `declared`,
with null `reason` and `action`. A null `value` means `missing`; `reason` is the
input `unknown_reason` copied exactly, without trimming or normalization, and
`action` is the literal string in the table. A missing declaration is never
replaced with a nominal or inferred number.

The first 21 checks occur in this exact order. `K` means the ordinary
known-or-unknown rule. The three other rules are defined immediately below.

| Order | `path` / check identifier | `category` | Rule | `action` when missing |
| --- | --- | --- | --- | --- |
| 1 | `specimen.specimen_id` | `specimen` | S | `Record the actual hardware specimen identifier after identity review.` |
| 2 | `specimen.variant` | `specimen` | K | `Record the hardware variant or the synthetic model identity.` |
| 3 | `specimen.revision` | `specimen` | K | `Record the applicable hardware revision or synthetic code/model revision.` |
| 4 | `specimen.identity_evidence` | `specimen` | K | `Locate retained evidence for the declared subject and configuration identity.` |
| 5 | `acquisition.started_at_utc` | `acquisition` | K | `Record the actual acquisition start time only after acquisition occurs.` |
| 6 | `acquisition.operator_id` | `acquisition` | K | `Assign or record a stable operator identifier.` |
| 7 | `acquisition.session_id` | `acquisition` | K | `Assign or record the acquisition session identifier.` |
| 8 | `digital.format` | `digital` | K | `Declare the raw acquisition format and later check the actual stream.` |
| 9 | `digital.sample_rate_hz` | `digital` | K | `Declare the raw digital sample rate without substituting it for physical clock calibration.` |
| 10 | `digital.channel_count` | `digital` | K | `Declare the raw channel count and ordered channel map.` |
| 11 | `physical_clock` | `clock` | C | `Obtain and review physical clock calibration evidence for the actual acquisition setup.` |
| 12 | `stimulus.description` | `stimulus` | K | `Describe the intended or observed stimulus and retain its schedule.` |
| 13 | `stimulus.controls` | `stimulus` | K | `Declare the control settings and complete gesture/state history.` |
| 14 | `stimulus.conditions` | `stimulus` | K | `Declare the relevant operating conditions with units and unresolved quantities.` |
| 15 | `stimulus.synchronization` | `stimulus` | K | `Describe synchronization and its evidence without inferring it from a shared group.` |
| 16 | `signal_path.description` | `signal_path` | K | `Describe the connected path and separately identify its equipment or synthetic stages.` |
| 17 | `signal_path.bypass` | `signal_path` | K | `Declare the bypass states applicable to this signal path.` |
| 18 | `signal_path.loading` | `signal_path` | K | `Declare connected loads or an explicit synthetic context without inferring physical impedance.` |
| 19 | `rights` | `rights` | K | `Locate separate store, analyze, derive-model and redistribute decisions for review.` |
| 20 | `partition.role` | `partition` | P | `Assign the intended analysis role after whole-group and purpose review.` |
| 21 | `partition.group_id` | `partition` | K | `Declare the complete related acquisition group before analysis.` |

- **S:** for hardware, use K. For synthetic, the v1-required null specimen ID is
  `not_applicable`, `reason` is its exact `unknown_reason`, and `action` is null.
  No other specimen field is automatically exempted for synthetic captures.
- **C:** `calibrated` is `declared` with null reason/action; `uncalibrated` is
  `missing` with the exact calibration `unknown_reason` and the table's action;
  `not_applicable` is `not_applicable` with that exact reason and null action.
  V1 permits the last state only for synthetic records. A declared calibration
  is not validated physical evidence.
- **P:** `fit` and `held_out` are `declared` with null reason/action. `unassigned`
  is `missing`, its `reason` is the exact input `partition.rationale`, and its
  action is the table's string. A declared role does not establish independence,
  separate validation versus final-test purpose, or untouched final-test use.

After those 21 checks, append three checks for each input channel in increasing
array index `i`, in the following order. If channel count is unknown, v1 requires
an empty channel array and no channel checks are appended. There are therefore
exactly `21 + 3 * len(manifest.digital.channels)` checks, at most 69.

| `path` / check identifier | `category` | Rule | `action` when missing |
| --- | --- | --- | --- |
| `digital.channels[i].boundary` | `channel` | K | `Identify the channel signal boundary without changing its physical meaning.` |
| `digital.channels[i].port_reference` | `channel` | K | `Declare the channel port, polarity/reference or microphone identity and pose.` |
| `digital.channels[i].calibration` | `channel` | C | `Obtain and review channel scale and uncertainty evidence at the declared boundary.` |

All synthetic channels still need their v1-required known `synthetic` boundary;
their port-reference text may remain missing, and their calibration is
`not_applicable`. Do not create a unity-gain calibration. `summary.total` is the
length of `checks`; the other three counts count exactly their named states and
sum to `total`.

## Status precedence and CLI

Apply these rules in order:

1. If input `status` is `planned`, report `status` is `planned`, irrespective of
   the check counts. Known planning declarations are intentions, not observations.
2. Otherwise, if at least one check is `missing`, use `declarations_incomplete`.
3. Otherwise use `declarations_complete`. This means only that every check has a
   declaration or an explicit v1 synthetic exemption; no physical gate closes.

```sh
python3 tools/capture_readiness.py --input data/capture-planned-example.json
python3 tools/capture_readiness.py --input /path/to/capture.json --output /path/to/new-readiness.json
```

The only options are required `--input`, optional `--output`, and `-h`/`--help`.
Option abbreviations and unrecognized options reject. Each input/output option
may occur at most once; an empty option value rejects as usage. `main` accepts
only `None` or an exact list of exact strings. It returns an integer rather than
raising `SystemExit`; the script entry point uses that return value.

Success emits complete sorted-key, two-space-indented UTF-8 JSON with one final
LF. Real standard streams receive UTF-8 bytes independent of terminal encoding;
in-process text-only redirected streams receive the same Unicode text. With
`--output`, `capture_common.write_json_new` must complete before stdout emits a
report. The file has exactly the same canonical bytes as stdout. The parent
directory must already exist and support hard links. No existing destination
file, directory, or dangling symlink is replaced, and no input artifact is
modified. A destination equal or hardlinked to the input is consequently
preserved and rejected. This is a one-file publication, not a transaction with
stdout or protection against a later stdout failure.

| Exit | Meaning |
| --- | --- |
| 0 | `declarations_complete`, or help requested |
| 1 | Rejected input, manifest, report, output publication or stream write |
| 2 | CLI argument/usage error |
| 3 | Valid `planned` or `declarations_incomplete` report |

Input, admission and publication rejections emit no report on stdout. A failed
stdout write may already have delivered a partial byte sequence and cannot
retract it. When stderr is writable, one canonical
JSON error object has exactly `schema_version: 1`, the same `contract_origin`,
`status: "rejected"`, and `error: {"code": ..., "message": ...}`. Codes are
`invalid_argument` (API path type or CLI syntax), `input_error` (input read or
strict JSON admission), `invalid_manifest` (unchanged v1 semantics),
`report_limit` (bounded report generation), `output_error` (publication), and
`stream_error` (standard-stream I/O). A bad API path raises `ReadinessError`
with `invalid_argument`; a corresponding CLI path rejection exits 2. Other
`inspect_readiness` rejections use their stated code. Platform-specific nested
filesystem messages are descriptive, not stable machine tokens.

If output publication succeeds but its temporary cleanup fails, the complete new
file remains published and the error explicitly retains that fact. If stdout
later fails, any already published complete file also remains; exit 1 and the
`stream_error` message identify that stdout delivery failed. Failure while writing
stderr cannot promise another diagnostic and still returns the intended nonzero
status. Cancellation (`KeyboardInterrupt`, `SystemExit` from external hooks)
is not converted to a successful or ordinary rejection result.

## Following work

Use the missing checks to prepare a human review, retaining every unresolved
reason. Validate actual artifacts separately with the [corpus auditor](CAPTURE_CORPUS.md)
and inspect streams with the [audio tool](CAPTURE_AUDIO.md). A present rights
locator is not permission; a calibrated number is not qualification; a group ID
is not independence. A future physical dataset still needs the protocol's
actual specimen, approved access, observed acquisition, reviewed metrology,
retained raw data and separate held-out evaluation.

# Capture metadata contract v1

This is an **original project proposal reconstructed from the atlas's requirements**,
not a recovered atlas companion. `data/capture.schema.json` describes its structure;
the bounded standard-library checker in `tools/validate_capture.py` owns the stricter
type, state, unit, path and ancestry rules below. Python 3.10 or newer is sufficient.
The atlas's previously reported companion checks are not this tool's results.

The committed `data/capture-planned-example.json` is genuinely **planned**. No actual
specimen, acquisition timestamp, calibration, artifact filename or digest is claimed.
A structurally valid recorded manifest remains a set of declarations: it cannot prove
authentic acquisition, calibration, permission, file format, or instrument fidelity.

## Commands and public API

Run from the repository root (input paths also work from other directories):

```sh
python tools/validate_capture.py --input data/capture-planned-example.json
python tools/validate_capture.py --input /path/to/recorded.json --check-files
python tools/validate_capture.py --input /path/to/recorded.json --check-files --artifact-root /path/to/archive
```

Default validation reads only the manifest, so absent capture files do not prevent
structural validation. `--check-files` is an explicit recorded-only option: it streams
the declared relative regular nonsymlink files, checks sizes and SHA-256, and reports
byte integrity. Its default root is the input manifest's parent. `--artifact-root`
without `--check-files` is a usage error. No command writes files or loads audio.
No WAV/FLAC header, sample content, physical provenance or calibration is inspected.

The public, nonmutating API is:

```python
load_capture(path: str | pathlib.Path) -> dict
validate_capture(value: object) -> None
check_capture_files(value: object, base_dir: str | pathlib.Path) -> dict
main(argv: list[str] | None = None) -> int
```

`load_capture` bounds and parses strict UTF-8 JSON, then calls `validate_capture`.
`check_capture_files` first validates the record and rejects planned records.
Invalid metadata, missing files, unsafe file types, and integrity failures raise
`CaptureError`, a `ValueError` subclass. Neither validation API mutates its input.
CLI success exits 0; a rejected capture exits 1 with `capture error:` on stderr;
argument errors exit 2. Successful stdout is one JSON object with `capture_id`,
`record_status`, `structural_validation: "pass"`, `file_check` (null by default),
`authenticity: "not_established"`, `calibration: "not_established"`, and
`physical_fidelity: "not_established"`.

The successful file-check report, also returned as CLI `file_check`, has exactly:

```json
{"capture_id":"example-id","status":"verified","files_checked":1,"bytes_checked":4,"scope":"declared-byte-integrity-only","authenticity":"not_established","calibration":"not_established","physical_fidelity":"not_established"}
```

Those numbers illustrate a report shape; they are not acquired evidence.

## Exact object contract

Every listed key is required; additional keys are rejected at every object level.
IDs match `[a-z][a-z0-9_-]{0,63}`. Text is nonblank, without control characters or
unpaired Unicode surrogates, at most 2,048 characters. Known-or-unknown fields use
exactly `{"value": ..., "unknown_reason": ...}`: a null value requires a nonblank
reason; a known value requires a null reason. Unknown is never silently zero.

| Root field | Contract |
| --- | --- |
| `schema_version` | Integer `1`; Boolean or floating-point substitutes are rejected. |
| `contract_origin` | Literal `project-proposed-v1`. |
| `capture_id` | A unique catalogue ID chosen by the operator; cross-record uniqueness is a corpus gate. |
| `status` | `planned` or `recorded`. |
| `status_reason` | Nonblank explanation for planned; null for recorded. |
| `capture_kind` | `hardware` or `synthetic`, including for planned work. |
| `specimen` | Known-or-unknown `specimen_id` (ID), `variant`, `revision`, `identity_evidence` (text). |
| `acquisition` | Known-or-unknown `started_at_utc`, `operator_id`, `session_id`. |
| `digital` | Known-or-unknown `format`, `sample_rate_hz`, `channel_count`, plus `channels` array. |
| `physical_clock` | Calibration object describing actual sample-clock frequency, separately from the digital rate. |
| `stimulus` | Known-or-unknown text: `description`, `controls`, `conditions`, `synchronization`. |
| `signal_path` | Known-or-unknown text: `description`, `bypass`, `loading`. |
| `files` | At most 32 artifact records described below. |
| `partition` | `role` (`fit`, `held_out`, `unassigned`), known-or-unknown `group_id` (ID), nonblank `rationale`. |
| `rights` | Known-or-unknown text locating separate store/analyze/derive-model/redistribute declarations. |

`specimen` identifies the primary acquisition subject at the declared boundary.
Describe the organ, AO-28 and connected cabinet identities/revisions individually
in identity evidence and signal-path text; do not collapse a 122 into a 147 variant.
Synthetic records have null `specimen_id` with a reason, and use variant/revision and
identity evidence to name the model/code. Hardware records may explicitly lack
specimen evidence; they cannot consequently support a specimen-specific claim.

Recorded records require known timestamp, operator ID, session ID, digital format,
sample rate, channel count, and group ID. A timestamp is a real calendar date in
`YYYY-MM-DDTHH:MM:SS[.ffffff]Z` form, with 1-6 fractional digits when present.
The operator may use a stable pseudonymous ID. Planned records have a null timestamp,
no files, an explicit status reason, and no calibrated measurement. A known operator
or session ID in a plan is an intended assignment, not acquisition evidence.

## Digital stream and physical calibration

The digital declaration describes the **raw acquisition stream**, not every derived
artifact. Formats are `wav_pcm16`, `wav_pcm24`, `wav_pcm32`, `wav_float32`,
`wav_float64`, `flac_pcm16`, `flac_pcm24`, or `raw_float32_le`. The declared rate is
an integer in 1..768000 Hz; channel count is an integer in 1..16. An unknown count
requires an empty channel list. A known count requires exactly that many ordered
channels, with `index` equal to its zero-based array position and unique channel IDs.

Each channel has exactly `channel_id`, `index`, `boundary`, `port_reference`, and
`calibration`. The latter two are respectively known-or-unknown text and a calibration
object. `boundary` is a known-or-unknown enum from the following table.

| Known boundary | Required calibration unit |
| --- | --- |
| `pickup_unloaded`, `generator_loaded_terminal`, `preamp_GG`, `electrical_voltage` | `V/FS` |
| `electrical_current` | `A/FS` |
| `acoustic_microphone` | `Pa/FS` |
| `synthetic` | null; status `not_applicable` |
| Unknown boundary (null with reason) | null; status `uncalibrated` |

Hardware channels cannot use `synthetic`; synthetic channels must use that boundary.
`port_reference` states polarity, reference terminals or microphone identity/pose.
For example, a G-G differential voltage stays at G-G; it is not a pickup gain.
The text fields deliberately retain human-readable setup declarations in v1 rather
than introducing a second general-purpose control or instrument schema. Include
units, exact controls/state history, stimulus timing, conditions, bypass and connected
loads, or preserve explicit unknowns. Retain detailed schedules/reports as support
artifacts. The checker cannot establish the physical adequacy of those descriptions.

Every calibration object has exactly `status`, `value`, `unit`,
`standard_uncertainty`, `evidence`, and `unknown_reason`:

- `calibrated`: recorded hardware only; positive finite value, finite nonnegative
  standard uncertainty in the **same unit**, nonblank evidence locator, null reason.
  The evidence must describe method, reference, applicable variant, uncertainty
  definition and calibration scope. This is a declared calibration, not verification.
- `uncalibrated`: null value, standard uncertainty and evidence; nonblank reason;
  retain the boundary's unit when known. This permits raw hardware recording.
- `not_applicable`: synthetic only; null value, unit, uncertainty and evidence;
  nonblank reason. Synthetic numbers do not establish physical calibration.

For hardware `physical_clock.unit` is `Hz`; for synthetic it is null with status
`not_applicable`. A calibrated clock value is in `(0, 768000]`, and need not equal
the header/declaration rate. Calibration values and uncertainties are bounded by
1e12 in magnitude; uncertainties cannot be negative. There is no unity-gain or
nominal-clock fallback. Calibration describes one clock shared by this record;
separately clocked streams require separate manifests and explicit synchronization
evidence. A shared group label is not proof of clock synchronization.

The `fit`/`held_out` role expresses intended membership. Even recorded, calibrated,
byte-verified metadata does **not** admit a physical fit. Missing specimen identity,
scale/clock/chain response, loading, synchronization, permissions or uncertainty
must remain a downstream gate until the physical protocol resolves them.

## Artifacts, ancestry and grouping

Each file has exactly `file_id`, `kind` (`raw`, `derived`, `support`), `path`,
`size_bytes`, `sha256`, `parents`, and `derivation`. Recorded records require at
least one raw file. No file placeholders exist in planned records: `files` is empty.
Sizes are integers in 1..268435456 bytes (256 MiB); the sum is at most 536870912 bytes
(512 MiB). SHA-256 is exactly 64 lowercase hexadecimal characters. These are declared
identities until optional byte checking succeeds.

File IDs and case-folded paths must be unique within a manifest. Equal digests are
permitted: equal bytes do not establish independent physical takes. Each path is
relative, at most 240 ASCII characters, and at most eight slash-separated components.
A component is 1..64 characters, starts with an alphanumeric, and otherwise uses
alphanumerics, dots, underscores and hyphens. No dot/dot-dot, trailing dot, empty
component, drive/UNC/absolute path, backslash, colon, or Windows device name is
allowed. The optional byte checker rejects symlink files and directories, nonregular
files, hardlink aliases within the manifest, missing files, and changed size/digest.
File-identity checks use a nonzero descriptor identity, falling back to the path
identity when unavailable. If neither API supplies a usable identity, file checking
rejects the record because it cannot exclude hardlink aliases; structural validation
still works. Equal bytes in independently stored files remain permitted.
The selected root itself must be a nonsymlink directory; ancestors above that root
are canonicalized so operating-system aliases such as macOS `/var` are usable.
Artifact-relative directories remain nonsymlink; Windows reparse points are rejected.
Keep the archive quiescent during verification; the portable path checks are not a
general sandbox against concurrent adversarial filesystem mutation.

Raw and support files have empty `parents` and null `derivation`. Derived files
have 1..16 unique local parent IDs and a derivation object with exactly nonblank
`operation`, `tool`, `tool_version`, and `parameters` strings. All parent IDs must
resolve, no self-reference or cycle is permitted, and every derived file must reach
at least one raw ancestor. Record exact crops/resampling/gains and output-format
changes in these descriptions; v1 neither executes nor validates transformations.
The source bytes remain separate records. External-manifest ancestry is outside v1.

All files inherit the manifest's group and intended split role, so a derivative
cannot locally select its own holdout. Every recorded record, and any plan with an
assigned role, needs a known `group_id`. Group whole takes, synchronized channels,
rotor runs and related crops together. Cross-manifest duplicate identities, shared
parents, incompatible roles, independence, and frozen final-holdout use require a
later corpus audit. `unassigned` does not mean reusable independent evidence.

## Resource limits and unclosed gates

Strict input JSON is at most 65,536 bytes, at most 4,096 value nodes, and at most
16 nested container levels (root level 0). Every list/object has at most 4,096
members before field-specific limits apply. Numeric tokens have at most 64
characters; all numbers must be finite and have magnitude at most 1e12. Boolean
values never substitute for integers or physical numbers. Duplicate JSON object
keys, UTF-8 errors, NaN/Infinity, overflow and unsupported types are rejected.
Hashes stream in 65,536-byte chunks under the artifact and aggregate limits.
The schema records structure; the checker additionally enforces exact Python JSON
types, bounds, date validity, unknown/state consistency, units, identities and DAGs.
It is deliberately not a general JSON Schema implementation.

M0 still needs an actual specimen/revision/condition lock, permissions and equipment
setup. M8 still needs actual retained acquisitions, independently reviewed physical
calibration and synchronization, immutable/restorable raw bytes, a corpus split
audit, upstream-first fitting, frozen tolerances, uncertainty and held-out results.
No metadata pass closes these gates.

Sources: atlas PDF pp. 355-360 (capture contracts, clocks, unknowns, asset identities,
lineage and declared permissions), pp. 361-366 (identifiability, boundaries, fitting
and held-out evaluation), and p. 372 (retained result evidence). See
[the atlas review](research/ATLAS_REVIEW.md) and [M0/M8 plan](PLAN.md).

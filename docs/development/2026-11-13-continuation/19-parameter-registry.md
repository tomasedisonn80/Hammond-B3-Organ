# Assignment 19 — permanent percussion control identities

Agent: `/root/w04_a19_parameter_registry`

Wave: 04, assignment 19 of the 60-agent continuation

Date: 2026-11-13

Baseline inspected: `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`

## Scope and observed result

Extended the internal parameter inventory from 39 to 43 records. The registry
validator accepted the new document and all **24 parameter unittest methods
passed** locally with Python 3.12.14. This is metadata and scalar-conversion
evidence. No native plugin, host automation curve, gesture, DAW recall or physical
instrument qualification was performed by this assignment.

Owned changes:

- [`data/parameter-registry.json`](../../../data/parameter-registry.json)
- [`tools/validate_parameters.py`](../../../tools/validate_parameters.py)
- [`tests/test_parameters.py`](../../../tests/test_parameters.py)
- [`docs/PARAMETERS.md`](../../PARAMETERS.md)
- This assignment note.

The integrating agent owns shared status, CMake, commits and publication. This
assignment did not edit engine, renderer or shared status files, stage changes,
commit, push or spawn additional agents.

## Contract decisions

| ID | Path | Internal event target | Value 0, also default | Value 1 |
| --- | --- | --- | --- | --- |
| 12288 (`0x3000`) | `percussion.enabled` | `percussion`, `upper`, index 0 | Off | On |
| 12289 (`0x3001`) | `percussion.harmonic` | `percussion`, `upper`, index 1 | Second | Third |
| 12290 (`0x3002`) | `percussion.volume` | `percussion`, `upper`, index 2 | Normal | Soft |
| 12291 (`0x3003`) | `percussion.decay` | `percussion`, `upper`, index 3 | Slow | Fast |

These targets correspond to `EventType::Percussion = 8` in the current
[`Types.h`](../../../include/hammond/Types.h) contract. All four records are
dimensionless binary selections, with `step_count = 1`, plain domain `[0,1]`,
normalized domain `[0,1]`, default `0`, normalized default `0.0`, and exact law
`floor(u + 0.5)`. The existing integer-ratio conversion preserves the result for
the binary64 input immediately below the half-step. Reverse conversion is `u=x`;
fractional plain switch values reject. Harmonic codes are not harmonic numbers,
volume is not an amplitude and decay is not a duration.

Schema version is now **2**, with exact model
`exclusive-ab-percussion-console-v2`. The current validator accepts only that
document contract. Historical schema-1 `ideal-exclusive-ab-console-v1` registry
documents fail explicitly, without mutation or inferred missing controls. The
unchanged legacy records still work with the scalar helpers. This choice concerns
the authored registry; it does not change the separate `B3CONTROLS1` saved-control
migration implemented by other assignments.

Stored percussion settings do not depend on current route eligibility. This
metadata maps one retained setting per ID; the engine owns upper-B eligibility,
audio routing, continuous readiness and the sample clock. Creating an event
dictionary does not dispatch it. These IDs are original internal allocations,
not copied atlas allocations or verified VST3 exports.

## Compatibility evidence

Before editing, the complete original file contained 39 records and had SHA-256
`e7a7a9938ff38fbd43cb18aa9a7da482628cb41550d56fd37f9c1d3216547e8e`.
The independent canonical digest of all 39 complete original records is:

```text
61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b
```

Canonicalization sorts records by numeric ID, recursively sorts JSON object keys,
uses compact separators `(',', ':')` with `ensure_ascii=True`, and hashes the
ASCII bytes. The expected digest is frozen directly in the test module; it is
not generated from the new validator's expected metadata. It covers every old
field, including labels, units, defaults, normalized meaning, event mapping and
source/evidence fields. A test confirms that reordering does not change it and
that a changed legacy normalized meaning does.

A separate read-only comparison against
`git show 7a24a30:data/parameter-registry.json` confirmed equality of every original
record by ID. Only IDs 12288–12291 were added. The comparison independently
recomputed the same historical digest. No accepted identity was renumbered or
repurposed.

## Source review and evidence limits

Read the standing instructions, current handoff, console dynamics contract,
existing validator/tests, and relevant continuation reviews. Directly extracted
and read atlas pp. **127–138**, **397–402** and **418** with `pdftotext` for this
assignment. The continuation's six earlier reviewers own the full 500-page
coverage; this assignment does not claim another full review or independent
review of underlying factory source documents.

The atlas supports shared upper percussion, independent tablet controls,
retained state versus eligibility, stable identities, frozen normalized laws and
separate host acceptance. It does not supply these repository-specific numeric
IDs, startup defaults or release-qualified exports. All registry records remain
`proposed`, with `companion_recovered`, `host_exports_verified` and
`native_host_curves_implemented` all false. The missing 62-entry atlas companion
remains missing. No measured hardware values were introduced.

## Verification actually run

```sh
python3 tools/validate_parameters.py data/parameter-registry.json
python3 tests/test_parameters.py -v
git diff --check -- data/parameter-registry.json tools/validate_parameters.py tests/test_parameters.py docs/PARAMETERS.md
```

Observed results:

- Validator exit 0: `Validated 43 proposed internal parameters for exclusive-ab-percussion-console-v2; host mapping remains pending.`
- Unittest exit 0: **24 tests, OK**. Existing parser and scalar checks remain,
  with new whole-record compatibility, historical-document rejection, four
  distinct percussion targets/defaults/laws and non-mutating payload creation.
- Threshold tests now cover every discrete parameter at, immediately below and
  immediately above each half-step. All four percussion controls exercise the
  normalized event helper at both endpoints and all three threshold positions.
- New percussion records participate in malformed metadata, duplicate identity,
  wrong manual/index, changed units/defaults/laws, missing/unknown keys,
  nonfinite/Boolean/overflow values, out-of-range and fractional plain-value
  rejection. Existing bounded UTF-8/JSON, duplicate-key and nonfinite parser
  checks remain; an additional duplicate percussion path is rejected.
- `git diff --check` exit 0. The read-only Git baseline comparison described
  above passed for all 39 records.

## Handoff and next step

The integrator should include these five files in the reviewed checkpoint, update
the shared navigation/status inventory from 39 to 43, and run the current full
integration gates before committing/pushing. The root README's parameter table
still said 39 when inspected; it was deliberately left to the integrator.

Future host work must approve and enumerate actual exported IDs/units, define
native curve and discrete threshold handling, preserve all historical meanings,
test retained settings while percussion is ineligible, balance UI gestures,
handle same-value bank reselect after Cancel, and verify migration/recall in real
hosts. These gates are pending; passing the Python suite does not establish them.

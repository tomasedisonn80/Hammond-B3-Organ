# Pedal render evidence — schema 3

The [offline renderer](RENDER_FORMAT.md), `tools/render_fixture.py` producer and
`tools/verify_render.py` independent consumer now have an explicit pedal-aware
contract. The producer writes **manifest schema 3** only and requires actual
renderer **`render_schema_version: 3`** output. The consumer still verifies
historical schemas 1 and 2 under their original exact contracts. Earlier bundles
are preserved byte for byte; reading them never upgrades or rewrites them.

This extends the common artifact, hashing, process-capture, PCM and failure
rules in [RENDER_EVIDENCE.md](RENDER_EVIDENCE.md) and
[RENDER_VERIFICATION.md](RENDER_VERIFICATION.md). Their schema-1/2 descriptions
remain the historical version contracts. This page specifies the current
schema-3 additions. Evidence remains **`synthetic_engineering`** and the declared
physical status remains **`unmeasured`**.

## Initial controls and score commands

The wrapper adds `--pedal-drawbars NN`; its public `run_fixture()` API adds the
keyword-only `pedal_drawbars="00"`. Accept exactly two ASCII digits in 0–8,
representing Pedal Mixture 1 and Pedal Mixture 2. Wrong types, Unicode digits,
padding, signs, separators, decimal spellings, short or long strings reject
before creating an evidence directory. Default `00` mutes both contributions.
This option does not press a pedal. Scores supply explicit pedal events.

The five-field event grammar remains `frame kind manual index value` with
sorted absolute frames in `[0,total_frames)`, stable ties and all existing
limits. Four new commands are admitted in schema 3:

| Command | Required manual | Index | Value |
| --- | --- | --- | --- |
| `pedal_on` | `lower` | One-based pedal ID 1–25 | Finite integer velocity 0–127; zero releases |
| `pedal_off` | `lower` | One-based pedal ID 1–25 | Exactly zero |
| `pedal_drawbar` | `lower` | Mixture storage index 0 or 1 | Finite integer position 0–8 |
| `pedal_all_notes_off` | `lower` | Exactly zero | Exactly zero |

`lower` is the canonical unused manual field for these commands; it does not
turn a pedal ID into a lower-manual MIDI note. Decimal value spellings that
parse to admitted integers retain the established grammar. Indices and frames
remain unsigned decimal integers. No pedal timing or velocity-loudness model is
inferred from these commands. See the
[pedal integration contract](PEDAL_INTEGRATION_CONTRACT.md) for domain separation,
shared sources, separate panic and the nominal transfer.

Before the score, the renderer flushes nine manual drawbars, four percussion
controls and the two pedal positions at zero elapsed frames. Score frame-zero
commands follow that initialization and may override it. The manifest records
the initial registration and exact score bytes; it does not claim that the
initial registration is the registration at every later sample.

For example, a score containing:

```text
0 pedal_on lower 1 100
12000 pedal_drawbar lower 1 1
24000 pedal_off lower 1 0
24000 pedal_on lower 13 100
36000 pedal_all_notes_off lower 0 0
```

can be rendered using an existing parent directory and a new result directory:

```sh
python3 tools/render_fixture.py \
  --renderer build/hammond_render \
  --output-dir out/pedal-evidence \
  --events path/to/pedal-events.txt \
  --frames 48000 --sample-rate 48000 --block-size 127 --seed 7 \
  --drawbars 000000000 --pedal-drawbars 10
python3 tools/verify_render.py out/pedal-evidence
```

The wrapper always requests failure on clipping. It neither rescales the WAV nor
replaces the renderer's actual float metrics with decoded PCM statistics.

## Exact schema-3 envelope and invocation

The top-level manifest keys and retained artifact names are unchanged. There are
six ordinary files, including `manifest.json`, and a seventh `events.txt` only
for a score. No pedal source map is silently added to the bundle. The map and
reference identities below are frozen documentary identities of the compiled
renderer, with their original source files retained in the repository.

`parameters` has the thirteen schema-2 fields plus required string
**`pedal_drawbars`**, for fourteen fields in total. The argument vector has
exactly **28 strings** in this order:

```text
RENDERER --profile PROFILE_COPY --output WAV --frames FRAMES
  --sample-rate RATE --block-size BLOCK --seed SEED --drawbars DRAWBARS
  --pedal-drawbars PEDAL_DRAWBARS
  --contacts CONTACTS --percussion PERCUSSION
  --percussion-volume VOLUME --percussion-decay DECAY --fail-on-clip
  (--events EVENTS_COPY | --note NOTE)
```

Paths are absolute and the copied filenames remain fixed. The wrapper does not
support a controls-file input or an unrecorded extra renderer argument.
`parameters.event_count` counts only score commands, excluding all fifteen
initialization controls. The default-note mode retains null `event_count` and
the existing manual gesture; both pedal controls still initialize explicitly.

Renderer stdout remains a flat JSON object with exact scalar types and at most
16 KiB of input. Its **31 fields** consist of the eighteen schema-2 names, with
integer `render_schema_version` changed to 3, plus these thirteen required names:

| Field | Required value or derivation |
| --- | --- |
| `pedal_routing_model` | `linear-pedal-bus-reference-v1` |
| `pedal_voice_model` | `nominal-static-pedal-mixture-v1` |
| `pedal_gain_law` | `linear-pedal-position-v1` |
| `pedal_contact_model` | `ideal-eight-contact-pedal-v1` |
| `pedal_map_id` | `atlas-derived-b3-c3-pedal-v1` |
| `pedal_map_raw_sha256` | Exact raw `data/pedal-map.json` SHA-256 below |
| `pedal_map_canonical_sha256` | Canonical map SHA-256 below |
| `pedal_reference_a_sha256` | Raw `data/references/review-a-pedal.csv` SHA-256 below |
| `pedal_reference_b_sha256` | Raw `data/references/review-b-pedal.csv` SHA-256 below |
| `pedal_mixture_matrix` | Exact string `4,2,1,1;1,4,2,1` |
| `pedal_mixture_denominator` | Integer `8` |
| `pedal_gain_denominator` | Integer `8` |
| `pedal_weight_policy` | `all-200-unit-positive-v1` |

The matrix string is a canonical rational representation, versioned by
`nominal-static-pedal-mixture-v1`. The semicolon separates Mixture 1 and Mixture 2;
each row lists Brown, Red, Orange and Yellow bus numerators in that order. Divide
each numerator by eight. The position gain is `p / 8`, independently of the
manual profile's drawbar gain law. Even an equivalent fraction with different
text or denominator is a different serialized representation and rejects under
this version. Integer 8 is required; `8.0`, `true` and a string `"8"` reject.

All 200 reference weights are +1, including the five disconnected positions.
This is an explicitly chosen dimensionless engineering fixture, not a claim
that physical conductances, reactor values, organ volts or 16-foot/8-foot pedal
voicing have been measured. The original numerical choice and replacement path
remain in [PEDAL_VOICE.md](PEDAL_VOICE.md).

## Independently pinned documentary identities

| Input | SHA-256 |
| --- | --- |
| Raw pedal map | `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd` |
| Canonical pedal map | `7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2` |
| Review A pedal CSV | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |
| Review B pedal CSV | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |

Canonical JSON uses sorted keys, separators `(',', ':')`, `ensure_ascii=False`,
`allow_nan=False`, UTF-8, and no appended newline. Raw hashes preserve original
bytes. The two CSV hashes agree because the independent readings retain the same
cells and canonical transcription layout; their documentary provenance is
recorded in [FACTORY_REFERENCE.md](FACTORY_REFERENCE.md).

The C++ renderer takes its identities from the strict compiled routing input.
The producer checks them against the fixed schema-3 contract. The consumer has
its own frozen expectations and does not import the producer, call the renderer,
or derive its accepted map/model identity from either metadata copy. Tests also
compute the four hashes directly from the retained repository sources and compare
them with actual renderer stdout. Changing stdout and manifest together, then
recomputing their artifact hashes, cannot make a different map or mixture pass
this version's consumer.

These comparisons establish consistency with the admitted model identity. They
do not authenticate the process, prove source-to-executable association, replay
audio, or attest to physical fidelity. Verification reports retain all those
limitations explicitly. Documentary runtime route acceptance and numerical
Engine acceptance remain separate tests.

## Historical contracts and rejection behavior

| Manifest version | Parameters | Invocation strings | Renderer metric fields | Pedal grammar |
| --- | ---: | ---: | ---: | --- |
| 1 | 9 | 18 | 15, without `render_schema_version` | Rejected |
| 2 | 13 | 26 | 18, with integer render version 2 | Rejected |
| 3 | 14 | 28 | 31, with integer render version 3 | Admitted under the table above |

Both old versions reject pedal parameters and metadata as unexpected fields.
Schema 1 also retains its existing rejection of later percussion/partial-key
commands. Schema 2 still admits its original console grammar. An old document
does not become current evidence merely by changing a version number. The
consumer rejects missing fields, mixed versions, changed types, unknown model
identities, mismatched argv, invalid score commands and independently inconsistent
PCM or source identities.

All common bounds, file-change detection, fixed inventory, nonsymlink consumer
reads, exclusive result-directory creation, retained failure states, process
timeouts, log limits and integer PCM statistics remain enforced. A malformed
pedal score or initial registration rejects before output-directory creation.
If the renderer executes but reports unsupported metrics, the producer retains
its actual output and a failed manifest; the presence of a WAV is not success.

The new focused suite is `python_test_pedal_render_evidence`. Its exact executed
results and frozen source identifiers belong to
[assignment 21](development/2026-11-13-pedals/21-pedal-evidence.md); whole-repository
and hosted qualification remain the integrator's separate gate.

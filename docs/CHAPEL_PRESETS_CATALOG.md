# Atlas chapel registration catalog

The [authoring catalog](../data/registrations/atlas-chapel-nominal-v1.json) records
the atlas's approved chapel arrangement under `atlas-chapel-nominal-v1`.
Its eighteen ordered registrations contain all **162 documentary tap digits**.
Two independently frozen image transcriptions agree: [A](research/CHAPEL_PRESETS_SOURCE_A.md)
and [B](research/CHAPEL_PRESETS_SOURCE_B.md). This import supplies no runtime
selector, physical latch, loaded transformer gain or percussion interlock.

The atlas table does not publish registration names: authoring/output names are
`null`, and CSV name fields remain empty. Footages are exact strings in feet,
including rational fractions. Tap digits are discrete connection identities,
not linear amplitudes or measured gains. The atlas's underlying factory Table IV,
printed page 4-1, remains independently unverified; specimen wiring is unknown.

## Frozen data contract

[JSON Schema](../data/chapel-presets.schema.json) describes this exact named
authoring model. The [compiler](../tools/compile_chapel_presets.py) additionally
rejects duplicate JSON members, floating-point/nonfinite tokens, oversized or
unstable files, and disagreement with either frozen reading.

| Authoring member | Exact meaning |
| --- | --- |
| `schema_version`, `model_id` | Integer `1`; `atlas-chapel-nominal-v1`. |
| `evidence_class`, `applicable_variant` | `documentary-reconstruction`; `atlas-approved-chapel-arrangement`. |
| `source` | Exact unchanged PDF name/SHA-256/page 122; atlas citation S019-01, Table IV, printed 4-1, `not-independently-verified`. |
| `tap_units` | `discrete-transformer-tap-index`. |
| `drawbars` | Nine ordered objects: one-based `position`, exact `footage_ft`, `lead_color`. |
| `registrations` | Eighteen objects: `manual`, `preset_key`, `preset_name`, `drawbars`, `source_page`. |
| `limitations` | Explicit unpublished names, unverified specimen, unmeasured/unmodeled loaded gains, unmodeled latch and percussion interlock. |

Rows are upper then lower, each in C#, D, D#, E, F, F#, G, G#, A order. Each
drawbar string has exactly nine ASCII digits 0-8; all sixteen leading-zero
registrations retain those zeros. Every row locates page 122. All fields and
types are exact; changed numerical values require a separately reviewed model.

Compilation preserves every authoring member and adds only:

```json
{
  "format": "hammond-chapel-catalog-v1",
  "inputs": {
    "authoring": {"sha256": "<raw bytes>", "canonical_sha256": "<canonical JSON>", "bytes": 4298},
    "review_a": {"sha256": "<raw CSV bytes>", "bytes": 466},
    "review_b": {"sha256": "<raw CSV bytes>", "bytes": 466}
  }
}
```

The example shows added members, not a complete catalog. Canonical authoring
hashes UTF-8 JSON with sorted keys, separators `,`/`:`, no ASCII escaping and no
trailing newline. Authoring key order/whitespace may vary; its actual raw hash
and byte count are retained. Both CSV raw hashes must remain
`dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` after explicit
comparison of all rows and cells. A line-ending change therefore needs review.
No paths, timestamp or Git identity enter the output. The compiler locks the
declared PDF identity; it does not reopen the PDF or establish source independence.

## Build and use

Python 3.10 or newer and its standard library are sufficient. From the repository
root, with an existing build-directory parent:

```sh
cmake -E make_directory build
python3 tools/compile_chapel_presets.py \
  --input data/registrations/atlas-chapel-nominal-v1.json \
  --review-a data/registrations/review-a-chapel.csv \
  --review-b data/registrations/review-b-chapel.csv \
  --output build/chapel-presets.json
```

Success is silent with exit 0. CLI usage errors return 2; admission/publication
errors return 1 with an actionable stderr diagnostic. Options are not abbreviated
or repeated. The import API is `compile_chapel_presets(input, review_a, review_b)
-> str`; `validate_authoring(data)` validates an imported object. The publisher
`write_compiled_catalog(output, text, inputs)` accepts compiler-returned text and
all three input paths. Expected failures raise `ChapelCompileError`.

Inputs must be three distinct nonsymlink regular files: authoring at most 64 KiB,
each CSV at most 16 KiB. Reads are bounded and compare open-file/path identities;
POSIX opens use nonblocking/no-follow flags when available. Output is at most
64 KiB and requires an existing parent. Its leaf must be regular or absent,
cannot alias any input, and cannot be a symbolic link or Windows reparse point.
A same-directory temporary file is fully written/flushed before atomic replace.
Rejected inputs and ordinary publication failures preserve prior output and
inputs; owned temporary files are cleaned up. Hostile concurrent filesystem
mutation and power-loss durability are outside this guarantee.

## Evidence and next implementation

The [assignment record](development/2026-11-13-next-phases/34-chapel-compiler.md)
retains exact source/data/output hashes and executed positive, rejection, file,
CLI and publication probes. Independent maintained acceptance and build
registration are separate integration gates. A schema validation alone does not
enforce all compiler byte/provenance rules or strict integer token syntax.

A following exporter may copy these documentary tap strings into ordinary
retained drawbar banks with explicit manual/bank selection. That must be labeled
as copying a registration, preserve unrelated controls, and use the existing
`B3CONTROLS3` format. It cannot claim the physical fixed-key latch or B-percussion
transition. Actual selector/state/runtime qualification and primary/specimen
acquisition remain under the [M3 contract](M3_REMAINING_AND_SCANNER_GATE.md).

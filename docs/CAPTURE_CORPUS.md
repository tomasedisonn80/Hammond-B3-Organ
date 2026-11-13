# Capture corpus audit tool

`tools/capture_corpus.py` implements the frozen
[capture corpus companion contract](CAPTURE_CORPUS_CONTRACT.md) with Python 3.10+
and standard-library dependencies. It supplements the unchanged
[capture v1 validator](CAPTURE_FORMAT.md) and composes the separate
[audio inspector](CAPTURE_AUDIO_CONTRACT.md). It performs no acquisition,
transformation, network request, input mutation or implicit output-file write.

## Run a corpus audit

From the repository root:

```sh
python3 tools/capture_corpus.py --input data/corpus-planned-example.json
python3 tools/capture_corpus.py --input /path/to/corpus.json --check-files
python3 tools/capture_corpus.py --input /path/to/corpus.json --check-files --check-audio
```

The committed example binds the exact bytes of the existing planned capture.
Its normal result is `inconclusive`, with exit **3**, one `planned_capture`
finding and one `unassigned_capture` finding. No recording or artifact identity
is invented. An exit of 3 is a completed audit with missing eligibility, not an
input parsing failure.

| Mode | Evidence in the report |
| --- | --- |
| Default, `structural_only` | Strict index and every referenced v1 manifest; exact observed index/manifest hashes; declared relationships and artifact identities. Artifacts are not opened. |
| `--check-files`, `files_checked` | All preceding evidence plus streamed observed size/SHA-256 and safe-file checks for every raw, derived and support artifact. |
| `--check-files --check-audio`, `files_and_audio_checked` | All preceding evidence plus actual inspection of every raw file and explicitly described derived audio file. |

`--check-audio` requires `--check-files`. There is no alternate artifact root:
the corpus root is the index's parent, manifests are relative to that root, and
each artifact is relative to its own manifest's parent. Absolute tool and input
paths allow invocation from another working directory.

CLI stdout contains one complete JSON report, sorted by key, indented by two
spaces, with unescaped Unicode and one final LF. It never includes a timestamp
or absolute machine path. Shell redirection can retain the report at a caller's
explicitly chosen destination.

| Exit | Meaning |
| ---: | --- |
| 0 | Complete report: no conflict or eligibility gap found in the requested mode. |
| 1 | Complete `failed` split report, or empty stdout with a contextual `corpus error:` diagnostic for rejected input. |
| 2 | CLI usage error, including audio requested without file checks. |
| 3 | Complete `inconclusive` report preserving missing acquisition, assignment or selected-audio coverage. |

## Public Python interface

Put the repository's `tools` directory on `sys.path`:

```python
from capture_corpus import CorpusError, audit_corpus, load_corpus, validate_corpus

index = load_corpus("data/corpus-planned-example.json")
validate_corpus(index)  # Does not mutate the object or read manifests/artifacts.
report = audit_corpus("data/corpus-planned-example.json")
```

`load_corpus(path)` returns the validated index without added or normalized
fields. `audit_corpus(path, *, check_files=False, check_audio=False)` returns the
complete report even for failed or inconclusive split outcomes. Both flags must
be exact Booleans. Malformed input, unsupported requested audio, unsafe files,
integrity mismatches and exceeded resource limits raise `CorpusError(ValueError)`
without returning a partial audit. Capture/audio/filesystem errors retain the
manifest path, capture ID and file ID when known.

## Index and schema

The root has exactly `schema_version`, `contract_origin`, `corpus_id` and
`captures`. The [planned example](../data/corpus-planned-example.json) shows the
complete required entry shape. Each entry binds an expected SHA-256 to one
portable manifest path and declares a purpose, gesture/family relations,
capture parents, and derived audio descriptors.

| Corpus purpose | Required capture v1 role |
| --- | --- |
| `fit` | `fit` |
| `validation` | `held_out` |
| `final` | `held_out` |
| `unassigned` | `unassigned` |

The mapping applies equally to plans and recorded captures. The auditor does
not rewrite either declaration. A later comparison-policy wrapper maps `final`
to `final_test`; that mapping does not alter the corpus or capture v1 tokens.

[The JSON Schema](../data/capture-corpus.schema.json) is a strict shape schema:
all object keys are required and additional properties are forbidden; it
encodes enums, value ranges, array bounds and the portable path grammar. It is
not a full graph or filesystem validator. JSON Schema's mathematical `integer`
also does not distinguish a JSON token `1.0` from `1`; the Python checker rejects
the floating token. The checker separately enforces byte/node/depth/string
bounds, capture/hash/path and descriptor-ID uniqueness, parent resolution and
acyclicity, manifest byte binding, role agreement, confined reads, aggregate
limits, and the complete relationship graph. No JSON Schema runtime dependency
is needed for the tool.

Every manifest is read into one bounded buffer. Its observed hash is computed
from exactly the bytes parsed and compared with the expected hash before v1
validation. Editing even insignificant manifest whitespace changes that
identity. The index itself is similarly identified from its parsed bytes.
Observed artifact hashes remain null until an actual file check succeeds.

## Whole groups and deterministic witnesses

All captures participate in a single transitive graph. Equal nonnull session
IDs, v1 group IDs, gesture labels and family labels connect captures. Explicit
capture ancestry adds directed child-to-parent witnesses and connects their
effective groups. Equal raw/derived artifact bytes connect captures using
declared hashes in structural mode and verified hashes in file modes. Equal
versioned decoded audio digests add another relationship in audio mode.

Each equality bucket produces a star rooted at its smallest capture ID. For
content equality the smallest participating file ID in each capture is the
witness. Every distinct reason is retained even when another reason already
connects the same endpoints. A disjoint-set structure computes the complete
groups; ancestry validation uses a bounded topological traversal. Neither
operation expands every possible pair of captures.

Shared support bytes, operator IDs, specimen IDs and sample rates do not create
content edges. Missing labels or different byte/decoded hashes do not establish
independence. Crops, resampling and other changed streams need declared ancestry
or a gesture/family relationship because full-stream digests cannot infer them.

A component fails if it mixes any two of `fit`, `validation`, and `final`.
Planned and unassigned captures retain their inconclusive findings even beside
a known-purpose conflict. Every capture belongs to one component, including
singletons. Inventories, edges, groups, findings and all witness choices have
fixed ordering; repeat audits of unchanged quiescent inputs and relocation of
the archive reproduce the same report. Reordering index bytes changes the
index hash while the sorted semantic inventory/graph stays unchanged.

## Audio coverage

Each raw artifact uses its own capture's v1 digital format/rate/channel count.
Every entry in `derived_audio` has exactly `file_id`, `format`, `sample_rate_hz`
and `channel_count`, and must resolve to a derived file. A derivative uses only
its own descriptor; it never borrows raw geometry. The raw-float selector is
explicit, while WAV headers must match the expected rate/count and format.
Legal capture-v1 FLAC declarations remain valid metadata but are unsupported
by the current requested audio inspection.

Support artifacts are byte checked but never decoded. Each derivative omitted
from `derived_audio` is `not_inspected` in audio mode and produces a distinct
`derived_audio_not_declared` finding. The aggregate audio result is `partial`
and its group is inconclusive unless a known-purpose conflict already fails
it. Omission never silently declares an artifact non-audio.

The report retains byte identity separately from observed format, rate,
channel count, frame count and canonical decoded identity. The inspector's
observed size and SHA-256 must match the separately verified bytes. A changed
identity or malformed/nonfinite stream rejects the audit. Canonical decoded
hashes compare exact normalized samples and geometry; they are not perceptual
fingerprints or physical authenticity evidence.

## Bounds and filesystem behavior

The index is at most 1 MiB with 512 captures; individual manifests retain
capture v1's 64 KiB/32-file bounds. The aggregate manifest limit is 16 MiB.
Declared artifacts total at most 2 GiB, and the audio selection totals at most
256 MiB. Every reference counts, even when another manifest names the same
file. Artifact and audio aggregate preflight completes before any artifact is
opened. Artifact reads stream in chunks of at most 65,536 bytes. The auditor
also enforces 8,192 capture-parent edges, 65,536 returned edges and 18,432
findings. All limits are inclusive.

The selected corpus root, indexed directories and input leaves must be
nonsymlink and non-reparse. Ancestors above the chosen root may be canonicalized
for ordinary operating-system aliases. POSIX opens bind parent directory
descriptors where available. Artifact checks reject within-manifest hardlink
aliases and require a usable descriptor or path identity. Shared files across
different captures still participate in raw/derived content grouping. Equal
hashes with conflicting declared sizes, or conflicting identities at one
case-folded corpus-relative locator, are input errors in every mode.

Keep the archive quiescent. The portable before/after observations detect
supported mutation cases but do not provide a hostile concurrent-filesystem
sandbox or a cryptographically immutable snapshot.

## Evidence boundary and verification

Every report preserves `independence`, `final_holdout_history`, `authenticity`,
`specimen_identity`, `calibration`, `permissions` and `physical_fidelity` as
`not_established`. Even a recorded, byte/audio verified clean split establishes
only the requested engineering checks. Synthetic fixtures remain synthetic;
plans remain unacquired. Physical specimen selection, permission, calibrated
scale/clock/chain response, synchronization, study history and held-out
instrument fidelity require separate retained evidence.

[Assignment 14](development/2026-11-13-calibration/14-corpus-implementation.md)
records producer source identities and actual author smoke results. Those
checks are separate from independently authored acceptance and do not close
the physical gates in [the calibration scope](CALIBRATION_SCOPE.md).

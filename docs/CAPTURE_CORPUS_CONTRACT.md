# Capture corpus companion contract v1

This is the frozen project-proposed contract for the offline corpus index and auditor. It supplements [capture metadata v1](CAPTURE_FORMAT.md); it
does not add keys to that format or change the meaning of `planned`, `recorded`, `hardware`, `synthetic`, `fit`, `held_out` or `unassigned`. This
document freezes an implementation target. Its existence is not an implemented-tool or acceptance claim; the session ledger records those
separately.

The index binds exact capture-manifest bytes, declares additional relationships and distinguishes model-selection validation from final assessment.
The auditor constructs a conservative relationship graph before checking split purposes. A clean graph means no conflict was found among the
relationships available in the requested mode. It never proves that unreported relationships are absent, that final material was untouched, or that
physical evidence is admissible.

The source basis is atlas pp. 349-366, 449, 452-455 and 481-486, as freshly reviewed in assignments
[05](development/2026-11-13-calibration/05-atlas-335-417.md) and [06](development/2026-11-13-calibration/06-atlas-418-500.md). This is a new project
reconstruction, not a recovered atlas companion. The scope remains [offline M0/M8 engineering](CALIBRATION_SCOPE.md).

## 1. Public API and execution modes

The implementation target is `tools/capture_corpus.py`, using only Python 3.10+ standard-library dependencies and the project's capture/audio tools:

```python
class CorpusError(ValueError): ...

validate_corpus(value: object) -> None
load_corpus(path: str | pathlib.Path) -> dict
audit_corpus(path: str | pathlib.Path, *,
             check_files: bool = False, check_audio: bool = False) -> dict
main(argv: list[str] | None = None) -> int
```

`validate_corpus` checks the index's exact types, keys, limits, identities, portable paths, parent resolution and acyclic capture-parent graph. It
neither reads manifests/artifacts nor mutates the supplied value. `load_corpus` reads one bounded strict-UTF-8 JSON index, calls `validate_corpus`,
and returns its object without adding fields or normalizing the caller's data.

`audit_corpus` always reads and validates the referenced capture manifests and binds their exact bytes to the index. Its modes are:

| Arguments | Report `mode` | Evidence obtained |
| --- | --- | --- |
| Both false | `structural_only` | Strict index and v1 manifests, observed index/manifest hashes, declared relations and declared raw/derived artifact hashes. No artifact is opened. |
| `check_files=True`, `check_audio=False` | `files_checked` | The preceding evidence plus actual size/SHA-256 and safe-file checks for every declared artifact, including support files. |
| Both true | `files_and_audio_checked` | The preceding evidence plus inspection of every raw file and every explicitly declared derived audio file, under the separate audio contract. |

Both flags require exact Boolean values. `check_audio=True` with `check_files=False` is an error; it does not silently enable a dependency. The
auditor does not resample, normalize, repair, copy, acquire or upload data. It creates no report, cache, decoded-audio or temporary artifact
implicitly and does not modify any input. CLI stdout is the only report destination.

Malformed or inconsistent input, unsafe/missing files, manifest or artifact integrity failure, unsupported requested audio, and exceeded resource
limits raise `CorpusError`. Wrap underlying capture/audio/I/O errors with the relevant relative manifest path, capture ID and file ID where known.
Preserve the actual reason, including expected and observed values for a mismatch. Do not turn a rejected input into a successful partial audit
report.

A structurally valid corpus with split leakage or incomplete eligibility returns the complete structured report with `status: "failed"` or
`"inconclusive"`. Those outcomes are distinct from rejecting the input before an audit can finish.

## 2. Exact index object

Every listed key is required. Additional keys are rejected at every object level. All arrays use exact JSON/Python lists and all objects use exact
dicts; custom objects, tuples and subclasses are rejected. `schema_version` is integer `1`, never `true` or `1.0`. IDs match
`[a-z][a-z0-9_-]{0,63}`. Digests are exactly 64 lowercase hexadecimal characters. No identifier or relation is inferred from a filename or free
text.

The following is a shape example, not a runnable acquired index. Its zero digest is deliberately only illustrative:

```json
{
  "schema_version": 1,
  "contract_origin": "project-proposed-corpus-v1",
  "corpus_id": "example-corpus",
  "captures": [
    {
      "capture_id": "example-capture",
      "manifest_path": "captures/example.json",
      "manifest_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "purpose": "unassigned",
      "relation_labels": [],
      "parent_capture_ids": [],
      "derived_audio": []
    }
  ]
}
```

| Object | Exact required fields and constraints |
| --- | --- |
| Index | `schema_version`, `contract_origin`, `corpus_id`, `captures`; the origin is literal `project-proposed-corpus-v1`; `captures` has 1..512 entries. |
| Capture entry | `capture_id`, `manifest_path`, `manifest_sha256`, `purpose`, `relation_labels`, `parent_capture_ids`, `derived_audio`. |
| Relation label | Exactly `kind` and `label`; `kind` is `gesture` or `family`; `label` is an ID. |
| Derived audio descriptor | Exactly `file_id`, `format`, `sample_rate_hz`, `channel_count`; `file_id` is an ID, `format` is a capture-v1 format token, rate is an exact integer in 1..768000 Hz, count is an exact integer in 1..16. |

`capture_id`, case-folded `manifest_path`, and `manifest_sha256` must each be unique across the index. A byte-identical manifest is one immutable
capture identity, not another independent capture under another path. `manifest_sha256` is the operator's **expected** hash; it is never represented
as an observation until the auditor has read the actual bytes.

`relation_labels` has at most 32 entries and no repeated `(kind, label)` pair. `gesture:x` and `family:x` are distinct namespaces. Labels mean a
declared common acquisition/performance/gesture family and therefore require grouping; they are not arbitrary descriptive tags. Use a family label
when the study must withhold a whole specimen/configuration/stimulus family. The tool cannot infer that scientific choice from a specimen name or
description.

`parent_capture_ids` has at most 16 unique IDs. Every ID must name an entry in this same index, cannot equal the child capture ID, and cannot
participate in a directed cycle. The direction is child to parent. These are explicit cross-manifest capture-level dependencies, supplementing each
v1 file DAG. They do not invent external file parents in v1 or assert a specific transform. Keep actual transform and file-parent detail in the
retained manifests/support evidence. A planned dependency is only an intended relationship and leaves the corpus inconclusive.

`derived_audio` has at most 32 entries, with unique file IDs. During the audit, each must resolve to a `kind: "derived"` file in that entry's v1
manifest. Descriptors for missing, raw or support file IDs are errors. A planned manifest has no files and therefore requires an empty
`derived_audio` list.

### Purpose mapping preserves capture v1

| Corpus `purpose` | Required v1 `partition.role` | Meaning |
| --- | --- | --- |
| `fit` | `fit` | Material intended for parameter fitting. |
| `validation` | `held_out` | Material intended for model selection and development validation. |
| `final` | `held_out` | Material intended for assessment of a previously locked choice. |
| `unassigned` | `unassigned` | No assigned analysis purpose; not independent reusable holdout. |

The mapping is exact for planned and recorded captures. Do not silently map a v1 `held_out` record to final, or change either declaration to make a
component consistent. A final-purpose label does not prove a sealed study or no prior use. Freezing the index hash before fitting and retaining
later usage/review records remain separate policy obligations. Editing any index bytes, including purposes, creates a new index identity and
requires affected-policy/report review.

For a later comparison-policy wrapper, map corpus purposes `fit`, `validation`,
`final`, `unassigned` to policy evaluation roles `fit`, `validation`, `final_test`,
`unassigned` respectively. The wrapper must validate that mapping explicitly;
neither this auditor nor capture v1 silently changes a declared purpose.

## 3. Bounds, portable paths and immutable reads

| Resource | Hard limit |
| --- | ---: |
| Index bytes | 1,048,576 bytes (1 MiB), including whitespace. |
| Index value nodes | 65,536, counting the root and each value; object keys are checked strings but not additional value nodes. |
| Index nesting | 16 container levels with root level 0. |
| Any index container before field limits | 65,536 members. |
| Numeric token length | 64 characters; finite magnitude at most `1e12` before exact field checks. |
| Generic string length | 2,048 characters; narrower ID/path/digest limits still apply. |
| Capture entries | 512. |
| One capture manifest | 65,536 bytes and all unchanged capture-v1 limits. |
| Aggregate referenced manifest bytes | 16,777,216 bytes (16 MiB). |
| Aggregate declared artifact bytes | 2,147,483,648 bytes (2 GiB), counting every manifest reference, including repeated references. |
| Aggregate selected audio bytes in audio mode | 268,435,456 bytes (256 MiB), counting every selected reference before decoding. |
| Cross-manifest parent edges | 8,192. |
| Returned graph edges | 65,536. |
| Returned findings | 18,432. |

All v1 per-file/per-manifest count and byte limits remain enforced, including 32 files, 256 MiB per artifact and 512 MiB per manifest. The audio
inspector's stricter per-file/frame/sample limits also apply when requested. Limits are inclusive; the first excess is rejected. Check
declaration-based aggregate limits before opening artifacts. An implementation must not construct a full pairwise graph and truncate it to fit the
edge bound.

Strict parsing rejects duplicate JSON object keys, invalid UTF-8, a BOM, trailing data, NaN/Infinity, overflowing numbers, unpaired Unicode
surrogates and control characters in strings. Nonblank generic strings may not contain U+0000..U+001F or U+007F..U+009F. Direct API values obey the
same type/depth/node bounds and a cyclic Python value is rejected without unbounded recursion. Booleans never substitute for numeric fields.

`manifest_path` uses the unchanged v1 portable relative-path grammar: at most 240 ASCII characters and eight slash-separated components; each
component is 1..64 characters, starts with an ASCII alphanumeric and otherwise contains ASCII alphanumerics, `.`, `_` or `-`. Reject empty, dot,
dot-dot, trailing-dot, drive, UNC, absolute, backslash and colon forms and Windows device stems such as `CON`, `NUL`, `COM1` or `LPT9`,
case-insensitively, even before an extension.

The selected index is a nonsymlink regular file. Its parent is the corpus root, a nonsymlink directory. Ancestors above that root may be
canonicalized to admit ordinary OS aliases; no indexed descendant directory, manifest or artifact may be a symlink or Windows reparse point.
Manifest paths resolve against this root. An artifact path resolves against its own manifest's parent and inherits v1's safe-file rules, including
within-manifest hardlink-alias rejection. The corpus API has no alternate artifact root and never resolves paths against the current working
directory.

The full corpus-relative artifact locator may be the combination of two valid relative paths; each component path retains its own v1 limit.
Case-folded same-locator references across manifests are allowed only with identical declared size and SHA-256. Equal expected artifact SHA-256 values must also
have equal declared sizes, wherever they occur. Contradictory identities are input errors. A shared regular file or hardlink across captures does
not gain independence: raw/derived content participates in grouping; shared support evidence alone does not.

Read each index/manifest once into its bounded byte buffer; compute its observed SHA-256 from exactly the bytes parsed. Compare manifest bytes to
the expected hash before accepting their contents, validate with `validate_capture`, then require the actual capture ID and v1 role to match the
index. Do not hash a later reread and attribute it to an earlier parse. Enforce the aggregate manifest bound while reading, not after accumulating
unbounded input.

File mode retains capture v1's nonsymlink/regular-file and descriptor-identity checks, streams bounded bytes, and verifies exact declared size and
SHA-256 for all artifacts. Missing usable descriptor and path identities cannot be treated as proof that aliases are absent. Support files are
byte-checked too. In audio mode the inspector's observed size and SHA-256 must also equal the already verified identity; a changed file rejects the
audit. Keep the archive quiescent: these portable checks are not a sandbox against concurrent adversarial mutation.

## 4. Audio selection and canonical content identity

The [audio companion contract](CAPTURE_AUDIO_CONTRACT.md) owns supported formats, literal decoding rules, numeric limits and
`capture_audio.inspect_audio`. Corpus confinement must be checked independently; the direct inspector's acceptance of a filesystem path is not a
confined-root guarantee.

Every raw artifact is selected in audio mode and compared with its own capture's v1 `digital.format.value`, `digital.sample_rate_hz.value` and
`digital.channel_count.value`; recorded v1 metadata requires all three to be known. Every explicitly listed derived audio artifact is selected and
compared with its descriptor. A derived file never borrows raw-stream geometry or format.

For `raw_float32_le`, call `inspect_audio` with that `raw_format` and the selected rate/count. For a WAV declaration, leave `raw_format=None`,
supply rate/count as assertions, and require the returned format token to equal the expected token. Any other declared format is subject to the
audio contract's explicit admission; an unsupported format rejects audio mode without weakening capture v1. Do not select a decoder merely from an
extension. Support files are never decoded.

A derived artifact absent from `derived_audio` remains `audio_status: "not_inspected"`, with reason `derived_audio_not_declared` in audio mode.
Absence is not a declaration that it is non-audio. Every such file produces an inconclusive finding, even when its bytes are verified. This v1
companion deliberately has no bypass that labels a derived file harmless. If some derivatives remain unclassified, the aggregate `audio_check` is
`partial`, never `verified`.

For each successfully inspected stream, retain the inspector's observed `format`, `sample_rate_hz`, `channel_count`, `frame_count`,
`decoded_digest_version` and `decoded_sha256`, separately from its byte hash. The canonical decoded identity is exactly:

```python
decoded_digest_version = "hammond-capture-decoded-v1"
payload = b"HAMMOND-CAPTURE-DECODED-V1\x00"
payload += struct.pack("<IIQ", sample_rate_hz, channel_count, frame_count)
# Append incrementally, in frame-major order and ascending channel index:
payload += struct.pack("<d", canonical_sample)
decoded_sha256 = hashlib.sha256(payload).hexdigest()
```

This notation defines a streamed hash, not allocation of the complete payload. PCM normalization, exact float widening, finite-value admission and
positive-zero canonicalization follow the audio contract. Container headers, paths, bit-depth labels and wrapper metadata are excluded. Identical
decoded samples at the same rate, channel order/count and frame count therefore match despite different WAV headers or compatible encodings. A
changed rate, channel order, sample value or duration is not silently equated. This hash is neither a perceptual fingerprint nor crop/resampling
detection; undeclared transformed relationships remain unknown.

## 5. Deterministic relationship graph

Every capture is a node. Grouping is the transitive closure of these relationships:

| Exact edge `reason` | Equality/dependency used | `basis` |
| --- | --- | --- |
| `session_id` | Equal nonnull v1 `acquisition.session_id.value`, including declared planned assignments. | `manifest_declaration` |
| `v1_group_id` | Equal nonnull v1 `partition.group_id.value`. | `manifest_declaration` |
| `gesture_label` | Equal `label` for index `kind: "gesture"`. | `index_declaration` |
| `family_label` | Equal `label` for index `kind: "family"`. | `index_declaration` |
| `parent_capture` | Every explicit child-to-parent capture edge. | `index_declaration` |
| `artifact_sha256` | Equal SHA-256 among raw or derived artifacts in different captures. | `manifest_declaration` in structural mode; `verified_bytes` after file checking. |
| `decoded_audio_sha256` | Equal versioned canonical digests among selected raw/derived audio in different captures. | `verified_audio` |

Raw-to-raw, raw-to-derived and derived-to-derived equality all count. Support artifacts are excluded from both content-equality grouping rules.
Sharing only support documents, permission records, calibration references, an operator, sample rate or specimen ID does not create an edge. Such
common evidence can still carry correlated uncertainty; this graph is not a covariance model. If a support reference becomes model-fitting material,
its role and grouping need explicit review rather than a free pass based on its old classification.

Different null values do not compare equal as grouping identities. Missing session/group values in planned records, empty relation lists, missing
ancestry or distinct hashes never assert independence. Related crops/resamples with different full-stream digests must retain a parent edge or
relation label.

Each returned edge has exactly:

```json
{
  "left_capture_id": "capture-a",
  "right_capture_id": "capture-b",
  "reason": "session_id",
  "basis": "manifest_declaration",
  "value": "session-one",
  "left_file_id": null,
  "right_file_id": null
}
```

For a parent edge, left is the child, right is the parent, `value` is the parent's capture ID and both file IDs are null. Otherwise left capture ID
is smaller than right capture ID in ASCII lexical order. Session/group/label `value` is the exact common ID. Artifact and decoded `value` is the
common lowercase digest and the two file IDs name the actual witnesses. Both decoded witnesses use the one version frozen above. Do not emit
self-edges.

For each equality bucket, choose the smallest capture ID as an anchor and emit one edge to each other participating capture. For content buckets,
choose the lexically smallest participating file ID within each capture as its witness. This deterministic star records connectivity without a
quadratic expansion. The artifact inventory still exposes every occurrence. Preserve distinct reasons even if their endpoints are already connected.
Deduplicate identical edges, then sort by `(reason, value, left_capture_id, right_capture_id, left_file_id-or-empty, right_file_id-or-empty,
basis)`. Include every declared parent edge separately under this same sort rule.

Connected components are the effective corpus groups. Their `component_id` is the smallest member capture ID. A child and every parent/ancestor
inherit the same effective component even if their original v1 group labels differ. Never rewrite those original labels or purposes to force
agreement. A shared session or ancestry chain cannot place a child in final while its parent is fit.

## 6. Report, findings and verdict

All successful audit API returns, including failed and inconclusive split outcomes, have exactly these root fields:

| Field | Exact type/meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `contract_origin` | `project-proposed-corpus-report-v1`. |
| `corpus_id` | Index ID. |
| `index_sha256` | Observed SHA-256 of the exact parsed index bytes. |
| `mode` | One of the three mode tokens in section 1. |
| `status` | `pass`, `failed` or `inconclusive`, scoped only to the requested audit. |
| `structural_validation` | Literal `pass`; rejected structure produces no report. |
| `file_check` | `not_run` if disabled; otherwise `verified` when files exist, or `not_applicable` if all manifests are planned. |
| `audio_check` | `not_run` if disabled; otherwise `partial` when any derived file is uninspected, `verified` when all recorded audio scope is inspected, or `not_applicable` if all manifests are planned. |
| `captures` | The complete capture inventory defined below, sorted by capture ID. |
| `edges` | The complete deterministic edge list from section 5. |
| `groups` | All connected components, including singleton nodes, sorted by component ID. |
| `findings` | Exact reason objects defined below. |
| `independence` | Literal `not_established`. |
| `final_holdout_history` | Literal `not_established`. |
| `authenticity` | Literal `not_established`. |
| `specimen_identity` | Literal `not_established`. |
| `calibration` | Literal `not_established`. |
| `permissions` | Literal `not_established`. |
| `physical_fidelity` | Literal `not_established`. |

Each capture inventory object has exactly `capture_id`, `manifest_path`, `expected_manifest_sha256`, `observed_manifest_sha256`, `record_status`,
`capture_kind`, `purpose`, `v1_role`, `session_id`, `v1_group_id`, `relation_labels`, `parent_capture_ids`, and `files`. The expected manifest hash
comes from the index; the observed hash comes from the actual parsed bytes. They must match in any returned report. `record_status`, `capture_kind`,
`v1_role` and nullable session/group IDs are the unchanged v1 declarations. Relations are sorted by `(kind, label)` and parent IDs lexically.

Each file inventory object has exactly `file_id`, `kind`, `path`, `expected_size_bytes`, `expected_sha256`, `observed_size_bytes`,
`observed_sha256`, `expected_audio`, `audio_status`, `audio_reason`, and `observed_audio`. Sort files by `file_id`. The path is the unchanged v1
path, relative to that manifest's parent. Observed byte size/hash are null without file checking and otherwise contain the actual matching values.
Hashes in the expected fields must never be copied into an observed field when no read ran.

`expected_audio` is null for support and undeclared derived artifacts; otherwise it has exactly `format`, `sample_rate_hz`, `channel_count` from the
raw digital declaration or the derived descriptor. This expected object is present even without requested audio inspection. `observed_audio` is null
unless inspected; when present it has exactly `format`, `sample_rate_hz`, `channel_count`, `frame_count`, `decoded_digest_version`, and
`decoded_sha256` from the inspector.

| Artifact and requested mode | `audio_status` | `audio_reason` |
| --- | --- | --- |
| Support in every mode | `excluded_support` | `support_not_audio_scope` |
| Raw/derived when audio is disabled | `not_run` | `audio_check_not_requested` |
| Declared raw/derived audio successfully inspected | `verified` | null |
| Derived omitted from `derived_audio`, with audio enabled | `not_inspected` | `derived_audio_not_declared` |

Each component object has exactly `component_id`, `capture_ids`, `purposes`, and `status`. IDs and distinct purposes are sorted lexically. A
component is `failed` if it contains at least two distinct known purposes from `fit`, `validation`, `final`. Otherwise it is `inconclusive` if it
contains a planned capture, an unassigned purpose, or an uninspected derivative in requested audio mode. Otherwise it is `pass`. `unassigned` never
resolves a conflict between known purposes and never supplies an independent fourth split.

Every finding has exactly `code`, `severity`, `component_id`, `capture_ids`, and `file_refs`. `capture_ids` is a sorted unique ID array. Each file
reference has exactly `capture_id` and `file_id`, sorted by that pair. Findings are:

| Exact `code` | `severity` | Emission rule and exact reason |
| --- | --- | --- |
| `cross_purpose_component` | `error` | One per component with two or more known purposes. Include every component capture ID; `file_refs` is empty. Its complete edges show why the purposes are connected. |
| `planned_capture` | `inconclusive` | One per planned capture; its ID only; empty `file_refs`. Intended acquisition is not retained evidence. |
| `unassigned_capture` | `inconclusive` | One per unassigned capture; its ID only; empty `file_refs`. No analysis purpose is frozen. |
| `derived_audio_not_declared` | `inconclusive` | In audio mode, one per omitted derived artifact; its capture ID and one file reference. Actual decoded content was not inspected. |

Sort findings by `(code, component_id, tuple(capture_ids), tuple((capture_id, file_id) for file_refs))`; no timestamps, random IDs, machine-absolute
paths or environment-dependent explanatory text enter reports. The exact reasons are these stable codes plus the graph evidence; stderr may retain
human-readable details for rejected inputs. A failed component dominates the overall status; otherwise any inconclusive component makes the report
inconclusive; otherwise the result is pass. Preserve inconclusive findings even in a failed report.

Repeated audits of unchanged quiescent inputs with the same mode produce the same JSON value and canonical CLI bytes. Serialize stdout with
`json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)` plus one LF. Reordering an index changes its exact index hash;
the sorted graph/inventory otherwise remains order-independent. Relocation of an unchanged confined archive does not change the report.

Always retain all seven `not_established` claim fields above. Even a fully recorded, calibrated-in-metadata, byte/audio-verified, cleanly assigned
corpus does not establish specimen identity, permissions, physical scale/clock/chain calibration, synchronization, untouched final use, listening
results or fidelity. Missing physical evidence remains open; synthetic data stays synthetic.

## 7. CLI exit semantics

The frozen command forms are:

```sh
python3 tools/capture_corpus.py --input /path/to/corpus.json
python3 tools/capture_corpus.py --input /path/to/corpus.json --check-files
python3 tools/capture_corpus.py --input /path/to/corpus.json --check-files --check-audio
```

| Exit | stdout | stderr and meaning |
| ---: | --- | --- |
| 0 | One complete report with `status: "pass"`. | No error; no conflict found within this audit's declared/observed scope. |
| 1 | One complete report with `status: "failed"` for valid leaking input; otherwise empty. | For a `CorpusError`, one contextual `corpus error: ...` diagnostic and no success report. |
| 2 | Empty. | Argument usage error, including `--check-audio` without `--check-files`. |
| 3 | One complete report with `status: "inconclusive"`. | No input-error diagnostic; missing acquisition, assignment or selected-audio coverage remains visible in findings. |

No `--output`, network, archive mutation or inferred-role option belongs to v1. Shell redirection is an explicit caller operation; the auditor never
chooses a destination or overwrites a previous report itself.

## 8. Independent adversarial acceptance requirements

The independent acceptance author must construct inputs and expected graph components separately from the producer. An implementation's own report
is not its oracle. At minimum retain these cases and their observed outcomes:

1. Strict JSON: exact accepted shape; every missing/unknown key at every level; duplicate keys, wrong types, Boolean/float integers, invalid
   UTF-8/surrogates, BOM, trailing bytes, numeric overflow, cycles and just-over byte/node/depth limits. Exercise direct API values as well as
   parsed files; verify no mutation.
2. Identity/confinement: duplicate capture IDs/digests/case-folded paths; valid relocation and foreign working directory; traversal, device names,
   symlink directories/leaves, nonregular files, within-manifest hardlink aliases and missing usable identity. A changed manifest byte must fail
   even if parsed values would match; expected and observed artifact hashes stay distinct.
3. V1 preservation: all four purpose mappings; both held-out purposes remain v1 `held_out`; wrong role/ID fails; a planned-only index returns
   inconclusive without inventing artifacts; hardware unknowns and synthetic status remain visible and no physical claim field changes to pass.
4. Whole groups: separate examples for common session, v1 group, gesture, family, and transitive combinations. Changed paths, IDs and entry order
   cannot hide a fit/validation, fit/final or validation/final conflict. Same specimen/operator or shared support documentation alone must not merge
   independent components.
5. Cross-manifest ancestry: absent parent, self-parent, duplicate parent and two- or longer-node cycle reject before a successful report. A
   chain of child, parent and common ancestor shares one effective component. Different known purposes fail; unassigned and planned members remain
   inconclusive, including beside a failure.
6. Bytes: independently stored byte-identical raw/raw, raw/derived and derived/derived artifacts merge despite distinct session/group labels. Equal
   support-only bytes do not. Conflicting size for one expected digest rejects. Actual byte/size corruption and changed input during inspection
   reject; absence of artifact files is tolerated only in structural mode.
7. Audio: independently assembled WAVs with identical decoded samples but changed harmless headers have different byte hashes and the same literal
   canonical digest. Manually construct the canonical preimage with `struct.pack`, not a producer call. Check negative-zero canonicalization and
   distinct rate, channel layout, frame count and sample cases. Raw uses v1 geometry; derived uses only its descriptor; unlisted derived is uninspected/inconclusive;
   support is never decoded.
8. Evidence levels: structural mode never opens artifacts or fills observed artifact hashes. File mode never decodes or invents decoded hashes.
   Audio mode requires file mode, compares both observed identities, and preserves unsupported or malformed/nonfinite errors. No distinct hash or
   missing label implies independence, and selected-audio gaps cannot yield an audio verification pass.
9. Determinism/resources: shuffled index/manifest arrays produce the prescribed canonical graph while the index hash remains exact; repeated and
   relocated audits replay byte-for-byte; star witnesses and all reason codes match a separately constructed oracle. Exercise many equal
   artifacts/labels without quadratic graph growth and aggregate limits without allocating huge files.
10. CLI/failure preservation: all four exit codes and stdout/stderr distinctions; exact retained failure reason; no success report on integrity
    rejection; mixed failed/inconclusive findings retained; before/after input inventory unchanged; no hidden output artifact. This contract does
    not require physical acquisition to test the tool and cannot close physical gates with fixtures.

Implementation, independently written acceptance, and actual retained run results are subsequent assignments. Any discovered ambiguity must be
resolved in this contract before grading a producer against a silently revised interpretation. The proposed [shared JSON
primitives](CAPTURE_COMMON.md) can supply strict parsed-byte identities and canonical serialization; their independent acceptance is separate, and
this contract still owns corpus-specific limits, semantics and confinement.

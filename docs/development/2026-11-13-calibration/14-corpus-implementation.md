# Assignment 14 — corpus auditor implementation

**Actual assignment:** `/root/cal_w3_a14`, calibration wave 3, assignment 14.
**Outcome:** implemented the frozen corpus API/CLI, strict shape schema, genuinely
planned example and operating guide. Author smoke checks passed, including
actual integration with assignment 13's audio inspector. Independently authored
acceptance remains a subsequent assignment; this note is producer evidence.

## Scope, ownership and source identity

Read repository `AGENTS.md`, the calibration/rotary/standalone ownership scopes,
current status and next steps, the entire corpus contract, shared JSON contract,
capture v1 contract and independent integration review. The corpus contract's
observed SHA-256 is the reviewed frozen identity
`a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2`.
The audio contract's public API, supported formats, identity and composition
rules were also read for the integration boundary.

Owned files only:

- `tools/capture_corpus.py`
- `data/capture-corpus.schema.json`
- `data/corpus-planned-example.json`
- `docs/CAPTURE_CORPUS.md`
- `docs/development/2026-11-13-calibration/14-corpus-implementation.md`

No existing capture v1 code/schema/example, shared contract, core, CMake,
manifest ledger or other worker's implementation was modified. No commit,
fetch or push was performed by this worker; root owns integration/publication.
The initial checkout and locally recorded `origin/main` were both
`08fa8de8f718584c4ee4ab3b392c779f3290289c`, tree
`f5cff4b89d19f36a73f9d2a8ddb966db487f832c`.
During concurrent root integration they advanced to
`5026f671e788eb5e1a77c8ed4046a34afd539200`, tree
`2ed85b986f70895000f086039750f44773508819`, with matching locally recorded
`origin/main`. The new producer files were uncommitted at handoff; their hashes,
not that commit alone, identify the executed implementation.

| File | Complete-file SHA-256 at handoff |
| --- | --- |
| `tools/capture_corpus.py` | `68c710c8afdb2985446ef25b4d0ed7d690970dc8be33535facf0a5ee1747adbe` |
| `data/capture-corpus.schema.json` | `420037ea76f22dbd559b4005f1514bcf59d21310349800f138ce5b93c43707c9` |
| `data/corpus-planned-example.json` | `9c23a5faf002472d50e9c4e5e923bdb46e95091ee026288d98a91b785a7c4e2e` |
| `docs/CAPTURE_CORPUS.md` | `ae3501ce95a6557ff5cdc7a975703ce43708101d20c1ebe18593c80346eb79e6` |
| Existing planned capture bytes bound by the new example | `35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac` |

Actual dependencies used in the final audio integration probe were checked for
identical source hashes immediately before and after execution:

| Dependency | SHA-256 |
| --- | --- |
| `tools/capture_audio.py` | `967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| Unchanged `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

The same before/after probe also checked the corpus producer hash above.

## Implemented decisions

The exact nonmutating public surface is `CorpusError`, `validate_corpus`,
`load_corpus`, `audit_corpus` and `main`. Index loading uses bounded confined
reads, common strict JSON parsing and corpus-specific exact keys, types,
strings, identities, portable paths and limits. Capture manifests are read once
into bounded byte buffers, hashed from exactly the parsed bytes, compared with
their expected identity, and passed to unchanged `validate_capture`. No later
reread is credited as the earlier parse's observation.

Cross-capture ancestry uses Kahn's algorithm with complete parent resolution;
the graph uses disjoint-set union and deterministic equality stars. All seven
reasons are retained, including distinct reasons on already-connected nodes.
Content witnesses use the smallest capture ID as the anchor and the smallest
file ID per capture. Support bytes are excluded from content grouping. Parent
edge direction is preserved. Returned groups and all findings are complete and
sorted, including inconclusive findings inside failed components.

All manifests are admitted before artifact scanning. Locator/hash contradictions
and the 2 GiB artifact / 256 MiB selected-audio aggregates are preflighted from
declarations, counting every reference. The declared graph bound is also checked
before scans. File mode independently streams actual artifacts, retains observed
size/hash, requires usable identity, rejects within-manifest hardlink aliases
and checks root/descendant confinement. POSIX uses directory descriptor traversal
when supported. No input or report file is written by an audit.

Audio import is lazy. Raw files use raw-stream metadata; selected derivatives
use only their own descriptors. Audio identity must equal the separately
verified bytes. Support is never decoded. Each omitted derivative remains
uninspected and emits its own inconclusive finding. The report always keeps
all seven physical/independence claim fields `not_established`.

The aggregate `file_check`/`audio_check` applicability uses whether the admitted
inventory has files. This is equivalent to whether any manifest is recorded:
unchanged v1 requires every recorded capture to contain at least one raw file
and every planned capture to have no files. This equivalence was explicitly
checked in all three planned-only modes.

The JSON Schema is a strict structural schema with portable path constraints,
required fields, forbidden extra properties, enum/range/array bounds and whole
item uniqueness where applicable. Its description and guide explicitly reserve
exact numeric-token types, cross-item ID/path/hash uniqueness, DAG/manifest
semantics, byte/node/depth limits, aggregate limits and filesystem checks for
the Python validator. It does not pretend that JSON Schema proves graph
integrity or distinguishes a mathematical JSON integer `1.0` from token `1`.

## Actual commands and author results

Working directory for every repository-relative command:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Runtime: **Python 3.12.14**, Linux. Standard-library tool execution requires no
installation. The environment already supplied `jsonschema` for the optional
schema-authoring check; it is not imported or required by the corpus tool.

```sh
python3 -m py_compile tools/capture_corpus.py
python3 tools/capture_corpus.py --input data/corpus-planned-example.json
git diff --check
sha256sum tools/capture_corpus.py tools/capture_audio.py tools/capture_common.py tools/validate_capture.py data/capture-corpus.schema.json data/corpus-planned-example.json data/capture-planned-example.json docs/CAPTURE_CORPUS.md docs/CAPTURE_CORPUS_CONTRACT.md
```

Syntax compilation and whitespace checking passed. The planned example returned
exit **3** with `status: inconclusive`, exactly `planned_capture` and
`unassigned_capture`, no files and no invented artifact observations.

A `python3 - <<'PY'` author harness used only standard-library temporary
directories, literal `struct.pack` audio, independently formed SHA preimages,
deep-copied synthetic metadata and subprocess calls. It completed these **ten
grouped author smoke cases** with exit 0; these are not independent test methods:

| Smoke group | Observed result |
| --- | --- |
| Structural mode with all artifact paths absent | Completed failed split report, six declared relationship reasons, every artifact observation null; direct index validation left its object unchanged. |
| Actual file mode | Verified all raw/derived/support bytes; decoded observations remained null and `audio_check` remained `not_run`. |
| Actual audio mode and complete graph | All seven reasons appeared; literal decoded SHA matched; lexically chosen artifact witnesses were correct; split failure and omitted-derivative finding both remained. |
| Repeat/relocation | Repeated and copied confined archives returned equal JSON values. Before/after original-file inventory hashes were unchanged. |
| Cycles | Two-capture ancestry cycle and a cyclic direct Python list each raised `CorpusError`. |
| Aggregate preflight | Lowered-bound probes with an artifact-reader trap rejected artifact and selected-audio aggregates before invoking any artifact scan. These probes did not claim full-size 2 GiB/256 MiB execution. |
| Mode argument shape | Integer substituted for Boolean and audio without file mode both raised `CorpusError`. |
| All CLI exits and serialization | Actual subprocesses exercised pass 0, failed report 1, usage 2 and inconclusive 3; valid reports had empty stderr and exact canonical pretty JSON/LF. A foreign `/tmp` working directory succeeded. |
| Manifest byte mismatch | Added whitespace changed exact manifest SHA; CLI rejected with exit 1, empty stdout and expected/observed identities in the diagnostic. |
| Planned-only corpus in every mode | Each returned inconclusive with both eligibility findings; requested file/audio checks were `not_applicable`. |

The two mono PCM16 raw WAVs encoded `[0, 0.25, -0.5, 0]` at 48,000 Hz.
One included an independently assembled padded `JUNK` chunk. A separately
stored derivative copied the first WAV bytes, a second derivative was deliberately
omitted from `derived_audio`, and the support bytes were deliberately non-audio.
The exact independent decoded preimage was:

```python
b"HAMMOND-CAPTURE-DECODED-V1\0" + struct.pack("<IIQ", 48000, 1, 4) + struct.pack("<4d", 0, 0.25, -0.5, 0)
```

Its SHA-256 was
`4cc959a21407b8f45476ffa9794f7b8e78b7626a3cb7f03408cf2255b7c66ce6`,
which every inspected equal stream returned. The producer was not used to
compute that expected hash.

A second actual `python3 - <<'PY'` integration probe explicitly separated raw
and derived metadata: raw PCM16 WAV at 48,000 Hz / mono / four frames;
derived `raw_float32_le` bytes `[0.25, -0.5]` at 24,000 Hz / stereo / one frame.
The corpus returned `pass` with `audio_check: verified`; the derivative retained
its own format/rate/channel/frame geometry and its literal `<IIQ` + `<2d>`
canonical digest
`9326afae23b16ec1f263f6c21e47616630d6e505798b8037476cc55a7cc4b598`.
All four implementation/dependency source hashes were unchanged before/after.

The schema-authoring probe executed
`jsonschema.Draft202012Validator.check_schema(schema)` and validated the planned
example. Ten unsafe portable paths were rejected by both schema and producer:
traversal, device stems, trailing dot, double separator, backslash, final LF,
colon, absolute path and oversized component cases. Root/entry extra keys also
failed the schema. The probe exited 0.

## Limits, not-run work and next assignment

These fixtures establish software behavior only. They are not acquired organs,
calibrations, permissions, untouched final holdout history or physical fidelity.
Actual decoder integration **was run**; it is not a stubbed decoder claim.

Full independent corpus acceptance, adversarial descriptor/path mutation,
unavailable-identity hooks, real Windows reparse points, platform matrix,
maximum-size data scans and coherent full-repository regression were **not run
by assignment 14**. Independent assignments 17/23/30 and root integration must
qualify their assigned scopes against exact source hashes. The shared helper's
earlier 49-test acceptance is dependency evidence, not this producer's test count.

Next: independently construct graph/byte/audio oracles and adversarial archives
under the frozen contract; retain actual rejected/failed/inconclusive outcomes,
all source identities, and any platform skips. Recheck this producer and its
audio dependency together after fixes. Root then owns shared status, test
integration, coherent qualification and authorized publication.

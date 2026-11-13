# Assignment 17 — independent corpus acceptance

**Actual assignment:** `/root/cal_w3_a17`, calibration wave 3, assignment 17.
**Result:** 47 independently written unittest methods pass against the corpus
producer and actual audio decoder identified below. No production repair was
needed. The suite and this note are the only owned files.

## Ownership and inputs

- `tests/test_capture_corpus.py`
- `docs/development/2026-11-13-calibration/17-corpus-acceptance.md`

Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Read the repository agent instructions, calibration scope, the complete frozen
[corpus contract](../../CAPTURE_CORPUS_CONTRACT.md), and the capture-v1 shape and
state rules in [CAPTURE_FORMAT.md](../../CAPTURE_FORMAT.md). The parent context
provides the current plan, status and other-track ownership. This assignment does
not claim another complete PDF reading or new physical evidence.

The observed checkout and locally recorded `origin/main` at verification were
`5026f671e788eb5e1a77c8ed4046a34afd539200`, tree
`2ed85b986f70895000f086039750f44773508819`. The new producer/test files were
uncommitted at this point, so that commit alone does **not** identify the tested
implementation. The complete-byte identities below were measured immediately
before and after the final test execution and remained equal.

| Executed file or contract | SHA-256 |
| --- | --- |
| `tools/capture_corpus.py` | `68c710c8afdb2985446ef25b4d0ed7d690970dc8be33535facf0a5ee1747adbe` |
| `tools/capture_audio.py` | `967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| Unchanged `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| Frozen `docs/CAPTURE_CORPUS_CONTRACT.md` | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| `tests/test_capture_corpus.py` | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |

No producer, shared documentation, session manifest, CMake, schema, original data,
other-track file or Git ref was changed. Root owns coherent-source integration,
final accounting and publication.

## Independent expected results

The test author builds each small archive from literal dictionaries and
`struct.pack` WAV/raw bytes. It does not use a production manifest generator,
decoder helper, graph routine or producer report as the expected graph/hash
oracle. Synthetic records identify generated test material. Tests with hardware
metadata are also generated fixtures; their declarations are not observations of
an actual specimen or acquisition.

Expected edge dictionaries, directions, bases, witness IDs, component memberships,
purposes and findings are independently specified. Equality buckets are checked
against the contract's deterministic star, including complete inventories and
distinct reasons on nodes that are already connected. The decoded hash oracle
constructs the literal prefix, `<IIQ` geometry and frame-major `<d` samples with
positive-zero canonicalization.

Two retained literal identities give additional anchors:

- Mono 48,000 Hz samples `[0, 0.25, -0.5, 0]`:
  `4cc959a21407b8f45476ffa9794f7b8e78b7626a3cb7f03408cf2255b7c66ce6`.
- Stereo 24,000 Hz one-frame samples `[0.25, -0.5]`:
  `9326afae23b16ec1f263f6c21e47616630d6e505798b8037476cc55a7cc4b598`.

Repeat/relocation and order-change tests use the contract's metamorphic properties
in addition to those literal expectations. Such comparisons check determinism;
they do not substitute for the independently specified graph and identity tests.

## Executed coverage

| Area | Actual acceptance behavior |
| --- | --- |
| Public index interfaces | `validate_corpus` leaves input unchanged and needs no manifests; `load_corpus` preserves the supplied object without normalization. |
| Exact index structure | Missing and unknown keys at every index object level; capture/path/hash identity uniqueness; duplicate relation and derived-file IDs; exact Boolean mode flags and audio's explicit file-check dependency. |
| V1 preservation | All four purpose mappings, including separate validation/final purposes that both retain `held_out`; wrong role or capture ID rejected; planned hardware metadata stays inconclusive in all three modes. |
| Relationship graph | Each session/group/gesture/family reason separately; typed label namespaces; null planned IDs excluded; mixed transitive reasons; every parent edge in chains and a shared-ancestor diamond; unresolved/self/duplicate parents and short/long cycles rejected. |
| Whole splits | Every pair of fit/validation/final fails when related; unassigned members do not resolve a conflict; all seven reasons remain on the same connected nodes; complete groups and findings match exact expected dictionaries. |
| Artifact identity | Independently stored raw/raw, raw/derived and derived/derived duplicates merge; actual shared files across manifests merge; conflicting equal-hash sizes and case-folded locators reject even in structural mode. |
| Support boundary | Common operator/specimen/support alone produces no edge; support equal to another capture's raw file does not become content evidence; actual non-audio support is byte checked and never decoded. |
| Canonical decoded identity | Equal samples with changed ancillary wrapper, PCM/float/raw encodings and signed zeros match the literal digest; changed rate, channel layout/order, duration or sample value has the independently expected distinct digest. |
| Raw/derived audio geometry | Raw format/rate/channel declarations are asserted; a stereo 24 kHz raw-float derivative retains its own geometry beside mono 48 kHz PCM raw; descriptors must resolve to derived files. |
| Missing derived classification | Every omitted derivative remains uninspected; each receives its own sorted inconclusive finding; `audio_check` is partial and failed reports retain all other eligibility findings. |
| Evidence modes | Structural mode succeeds with absent artifacts and leaves observed artifact fields null; file mode verifies deliberately non-audio raw bytes without inventing decoded evidence; requested malformed, nonfinite and unsupported audio rejects with capture/manifest/file context. |
| Immutable input binding | Manifest whitespace changes fail despite identical parsed JSON; actual byte and size corruption fail with expected/observed context; index SHA identifies the exact parsed bytes. |
| Deterministic witnesses | Four captures with three equal files each choose the smallest capture and file witnesses; 32 equal labels yield exactly 31 star edges, not all pairs. |
| Paths and replay | Artifacts resolve against each manifest's own parent; foreign CLI working directory, archive relocation, repeated audits and exact canonical CLI bytes succeed; complete input inventory is unchanged. |
| CLI | Actual subprocesses exercise pass 0, complete split failure 1, usage 2, inconclusive 3 and input-error 1 with empty stdout; unsupported output/alternate-root flags create nothing. |

Every checked report retains the seven physical/independence fields as
`not_established`. A clean split or different digest never becomes proof of
independence, acquisition permission, calibration or instrument fidelity.

## Actual results and corrected test expectation

Runtime: Python **3.12.14**, Linux x86-64, standard library only. Commands from
the working directory above:

```sh
python3 -B tests/test_capture_corpus.py -v
python3 -B tests/test_capture_corpus.py
```

The first version executed **44 methods in 0.731 seconds** and reported two
failing subcases within one method. Those failures came from the test author's
expectation, not the producer. The raw-rate and raw-channel cases reused identical
headerless bytes with different declared geometry. The test initially expected
no graph edge. Contract section 5 independently requires equal raw byte hashes to
retain an `artifact_sha256` relationship, even when the decoded geometry/digest is
different.

The corrected test explicitly requires that byte edge and the resulting failed
fit/final split, while still requiring the two independently computed decoded
digests to differ and no decoded-equality edge to appear. This strengthens the
distinction between byte and sample identities; it changes no contract or
production code. The issue and resolution were sent to root immediately.

After adding the per-manifest-parent, complete diamond and prohibited-output CLI
cases, the verbose suite passed **47/47 methods in 0.873 seconds**. The final
bounded rerun, with all six source/test/contract hashes checked before and after,
reported:

```text
Ran 47 tests in 0.816s

OK
```

Exit was **0**, with **zero failures and zero skips**; all six identities were
unchanged. No unresolved implementation defect was found in this assigned scope.

## Remaining gates and handoff

Assignment 23 owns deeper strict-JSON/resource/filesystem-mutation admission,
including descriptor failure/races, special files, aliases, unavailable identity,
aggregate preflight and maximum-limit behavior. Assignment 30 owns independent
schema parity. Those are separate gates, not implied by the 47 methods here.
This worker did not execute native Windows/macOS behavior, full-size corpus scans,
the coherent CTest build, hosted CI or physical acquisition/acceptance.

Root should retain both the initial test-expectation error and the successful
corrected result, register the new test through the existing test-discovery
workflow, and qualify a coherent source snapshot. Rerun this suite after any
change to corpus admission, the decoder, shared JSON or capture v1. The later
file-comparison/study wrappers must bind these exact observed identities and
preserve all failed/inconclusive findings rather than treating an audit `pass`
as a physical admission decision.

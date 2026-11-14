# Assignment 25 — identity-bound file-job implementation

- Actual agent: `/root/cal_w5_a25`, calibration wave 5, assignment 25.
- Date: 2026-11-13.
- Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
- Owned paths: `tools/capture_job.py`, the minimal private-core refactor in
  `tools/capture_corpus.py`, `docs/CAPTURE_JOB.md`, and this note.
- Root owns shared status/log/ledger, schemas, CMake, acceptance and Git publication.
  This worker did not stage, commit, push, modify the other tracks, or spawn
  additional assignments.

## Source and dependency basis

Initial observed HEAD was `091ad20c632209053c337a06544f82a829644800`, tree
`8679418135946193b2b989a89e60ac6099b00125`, with explicitly concurrent wave-4 work.
Root withheld corpus ownership until its accepted fixes were frozen. This worker
read and authored the new job first, without changing the corpus. Root then
explicitly released the minimal refactor after committing wave 4 as
`1c2ea32f24f978c8ce78aaf04bdb2daa23af359a`, tree
`e90b63736485766bb94636b5afa096cb5eff3b46`.

While the guide was being completed, the observed HEAD advanced to
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`, integrating the separate standalone
checkpoint. The job/corpus bytes below remained the exact executed sources.
These commit observations identify the surrounding checkout, not a committed
job implementation or a complete-tree test pass.

Read `AGENTS.md`, the current calibration session/scope/handoff, project README,
status, next steps, M0–M9 plan, latest development-log entry, retained atlas
review and the independent rotary/standalone scopes. Read the entire cleared
job contract and review, current corpus/common code and the relevant audio,
metric and policy implementations. Fresh source-text reading for this task
covered atlas pp. 355, 364, 367–372, 484 and 486. The session's six separate
readers own the complete 500-page reading; this worker does not claim another
complete reading or new original-page visual inspection.

| Exact input before implementation | SHA-256 |
| --- | --- |
| `docs/CAPTURE_JOB_CONTRACT.md` | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| `docs/CAPTURE_JOB_REVIEW.md` | `9218ca2e0fd72ff07ff1b838cac2dd153ce8e5b1ece18e20cbcc24d3b2c2f271` |
| `data/capture-job.schema.json` | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |
| `tools/capture_audio.py` | `c02c1a5e6023e0278dddca09ad1841541fbb0ece66d7950198f93be7846dc7ac` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/capture_corpus.py`, before shared-core extraction | `ba39a47499df0df837b71d744f773bfbefe14d0eb1a0c471a373900b6c284e7b` |
| `tools/compare_capture.py` | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| Existing corpus acceptance/fixture helper | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |
| Existing corpus admission acceptance | `6d7e0984fb20e0265f53e6ee3df3bb9958ca1440573bac9ed25a7b44bb819a19` |
| Synthetic policy example used for author setup | `e091dca3b3fdf3c3675383096007c5f95b848fa6294dedd3906705d061884316` |

The independently reviewed policy-byte warning directly shaped the implementation:
an admitted 65,437-byte compact policy can expand to 104,893 formatted bytes.
`run_job` therefore retains its original consumed policy buffer through
`evaluate_policy`, instead of hashing or evaluating a reserialization.

## Implemented behavior

The new public API is `JobError`, `validate_job`, `load_job`, `run_job` and
`main`. The validator performs exact shape/type, strict text/path and intrinsic
analysis/window/work admission without I/O. The reader uses bounded strict
UTF-8 JSON and returns the original parsed value. The runner reads without
publishing; valid failed/inconclusive outcomes remain complete reports.

The job rejects more than 64 index captures before loading any manifest. It
loads each manifest once through the existing v1/hash admission, preserves those
exact parsed values, and checks the 256-reference, aggregate-byte, selected-file,
geometry, purpose, evidence-class and policy-analysis conditions before any
artifact stat/open/hash/decode. It uses `_inventory` for declaration-only
preflight. No additional unbound index read or public structural audit occurs.

The corpus change adds one shared private `_audit_loaded` entry point around
the existing audit body. The unchanged public `audit_corpus` performs its normal
index/manifest admission and calls that same core. The job calls it once with
the admitted exact index/manifests and actual observed hashes. The core performs
fresh verification of all artifacts and all declared audio, retains the existing
hardlink/descriptor/root checks, and preserves public report semantics. The
previous descriptor-cleanup repair is untouched.

Each selected audio window is checked against the full corpus observations for
size, raw hash, format, rate, channels, frames, decoded digest version and decoded
hash. All original channels and explicit half-open windows pass unchanged to
the comparison producer. There are at most two additional full audio inspections;
the implementation currently performs both even for exact self-comparison.
No transform, gain/delay search, resampling, normalization or channel remapping
is implemented.

First-admission snapshots cover the job, index, policy, every consumed manifest,
every audited artifact and exactly six associated project source files, together
with confined parent chains. Every retained leaf and directory is checked again
before success. Constituent reads still perform their own descriptor/path checks.
Directory timestamps are not compared; sibling activity does not invalidate a
directory's identity. Cancellation is not caught as successful completion.

The exact report retains the complete job, policy, selected v1 manifests, full
corpus report, evaluator/comparison and selected full-stream inspections minus
only `input_path`. Samples are omitted. Derived selections use
`ancestor_raw_stream_only`; the raw manifest is never promoted into derivative
physical calibration. Runtime/source observations have the prescribed fields
without host names, timestamps or machine paths. All ten provenance/physical
claims stay `not_established`.

The complete report is guarded at 1,048,576 value nodes, depth 32, finite numeric
magnitude 4e18 and 16 MiB canonical UTF-8. Publication occurs only through
`write_json_new`, after complete serialization and before stdout. Existing or
raced destinations are preserved; cleanup-after-publication errors keep their
explicit complete-file disclosure. stdout bytes bypass terminal text encoding.
The documented exit codes distinguish pass, failed, inconclusive, rejected input
and usage. The [guide](../../CAPTURE_JOB.md) includes preparation, APIs, exact
path roots, context limits, publication and continuation instructions.

## Actual executed checks

Environment: Linux, Python **3.12.14**. No package installation or new runtime
dependency was required. All following commands used the working directory
above and `python3 -B` to avoid source-tree bytecode writes.

```sh
python3 -B -c 'import ast,pathlib; ast.parse(pathlib.Path("tools/capture_job.py").read_text()); print("job source parses")'
python3 -B tests/test_capture_corpus.py
python3 -B tests/test_capture_corpus_admission.py
```

The source parse passed. Following the shared-core refactor, the previously
independently authored corpus suites passed **47/47 methods in 0.948 s** and
**57/57 methods in 1.557 s**, zero skips or failures. These are repetitions of
existing independent tests, not new independent job acceptance methods.

An inline `python3 -B` author probe assembled temporary **synthetic** archives
with the existing `_Archive` fixture helper, independently packed the literal
raw float32 samples with `struct.pack`, and used the synthetic example solely
to construct a declared-margin policy. The probe itself was not installed as a
new maintained suite. Its eight executed groups all passed:

1. Reference `[1,-1,1,-1]`, candidate `[1.25,-.75,1.25,-.75]`, rate 4, one
   channel, four frames; RMS error exactly `.25`; margin `.125` and bound `.375`
   pass. Fixed contract raw/decoded identities agree. The nested full corpus
   report equals a separate public full audit. Instrumenting confined byte reads
   observes one consumption each for job/index/policy and both manifests.
2. A repeated run and a complete archive moved to a Unicode `relocated-λ`
   directory produce identical canonical report bytes.
3. The actual CLI, invoked by absolute script path from a foreign working
   directory with `PYTHONIOENCODING=ascii`, exits zero with empty stderr and
   stdout identical to the new output file. Reusing that destination exits one
   with empty stdout and preserves all existing bytes.
4. Lowering the bound to `.25` retains the interval overlap as inconclusive;
   the actual CLI exits three with complete JSON and empty stderr.
5. Half-offset samples `[1.5,-.5,1.5,-.5]` with the same `.25` bound and `.125`
   margin produce failed status; the actual CLI exits one with complete JSON
   and empty stderr.
6. An unselected fit capture duplicating the reference bytes makes the complete
   corpus/job fail while the pair's numerical result passes under a wider bound.
   `cross_purpose_component` remains present in the retained findings.
7. Boolean channel geometry rejects through `validate_job`; abbreviated `--in`
   rejects through the real CLI with exit two and empty stdout.
8. All ten job-level provenance/physical claim fields remain `not_established`.

The probe completed in 0.888 seconds of tool-observed wall time; this is not a
performance threshold or benchmark. It used no acquired instrument recordings
and supplies no physical calibration or fidelity evidence. Exact-byte hashes
were recomputed after execution; the source identities below were unchanged.

| Executed implementation | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/capture_job.py` | 23,438 | `3ffe39f5723a6a3af779ba33b799e72bdeed9d60365c5df9a8146b8467aec230` |
| `tools/capture_corpus.py` | 38,632 | `adb44d8838bf112e97bd884587dd74fe2dbf8167197622b4ba40453c004d33c7` |

There were no observed failing code checks in these initial author/regression
runs. Independent acceptance can expose omissions not covered by this bounded
smoke. No hidden earlier failures are reclassified as these passes.

## Handoff and remaining gates

Root and actual assignment 26 (`/root/cal_w5_a26`) received the API-ready notice,
the exact source hashes and regression results. Assignment 26 owns
`tests/test_capture_job.py` and independently constructed acceptance; it does not
inherit this author's smoke as independent evidence. Its acceptance must cover
the reviewed malformed/resource/geometry/role/evidence cases, complete snapshot
mutations including unselected artifacts and sources, derived context, policy
original-byte bounds, output failure/cancellation and complete CLI semantics.

Root should integrate that evidence and CMake, qualify a coherent source snapshot,
update shared status/next steps/log/ledger and commit/push completed work under
the standing authorization. Preserve the source identities if acceptance changes
the producer. Later study/replay tooling should consume these original-byte
identities and complete outcomes without altering thresholds after inspection.

Native Windows/macOS filesystem behavior, hostile concurrent-filesystem
resistance, a full 16 MiB report workload, hosted CI and clean installed-prefix
acceptance were not executed by this worker. The source snapshots are portable
quiescent-file observations, not code signatures or process-memory attestation.
Acquisition chronology, reference specimen identity, physical measurement scale,
calibration, listening and M8 specimen-specific fidelity remain open.

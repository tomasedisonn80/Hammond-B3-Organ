# Assignment 08: frozen corpus index, graph and audit contract

- Actual assignment identity: `/root/cal_w2_a08`; calibration wave 2, assignment 08.
- Date: 2026-11-13. Owned paths: this note and [CAPTURE_CORPUS_CONTRACT.md](../../CAPTURE_CORPUS_CONTRACT.md) only.
- Observed checkout HEAD: `08fa8de8f718584c4ee4ab3b392c779f3290289c` from `git log -1 --format='%H %s'`.
- Scope: freeze an implementation/independent-acceptance boundary; no production code, JSON schema, shared status, git history or publication mutation.

## Read basis and coordination

Read `AGENTS.md`, calibration scope and capture v1, current README/next steps,
scanner handoff, the current status sections, latest calibration log entry,
implementation plan, active rotary/standalone scopes and session README.
Read the fresh calibration atlas assignments 05 and 06 in full. They establish
the documentary basis at atlas pp. 349-366, 449, 452-455 and 481-486 for immutable
captures, complete groups, cross-record ancestry, frozen final assessment and
separate physical admission. This worker did not claim another full-PDF reading.

Inspected the existing v1 validator's strict types, resource/path limits and
local artifact rules before defining a companion. Read the root-authored
shared JSON primitives contract; its implementation acceptance remains separate.
Sent the index/API/graph shape to root before finalization. Coordinated directly
with A07 on exact `inspect_audio` arguments, decoded-digest bytes, unsupported
formats, derivative geometry and the inspector/corpus confinement distinction.
Root accepted the settled shape and the error-versus-report boundary before
implementation dispatch.

## Frozen decisions

| Area | Contract handed to implementation |
| --- | --- |
| Public API | `validate_corpus(value)`, `load_corpus(path)`, `audit_corpus(path, *, check_files=False, check_audio=False)`, and `CorpusError(ValueError)`. |
| Immutable identity | Expected per-manifest SHA-256 in the index; observed index and manifest SHA-256 from the exact parsed bytes; separate declared and observed artifact hashes. |
| Purpose mapping | `fit` to v1 `fit`; `validation` and `final` to v1 `held_out`; `unassigned` to v1 `unassigned`, with no silent remapping. |
| Grouping | Whole known sessions, v1 group IDs, typed gesture/family labels, raw/derived byte equality, declared capture-parent ancestry, and optionally observed decoded-stream equality. Support-only equality does not union. |
| Cross-manifest lineage | Resolve every parent in this corpus; reject duplicate/absent/self parents and directed cycles; all transitive dependencies inherit one effective group. Original v1 group/purpose declarations stay unchanged. |
| Audio binding | Every raw file uses its capture's v1 digital declaration; derived audio requires its own explicit file/format/rate/channel descriptor; no inheritance. Unlisted derived artifacts remain uninspected/inconclusive. |
| Determinism | Stable star witnesses for each equality bucket, complete reason-labelled graph, lexically sorted captures/files/components/findings, exact canonical stdout JSON, no timestamps or absolute machine paths. |
| Result boundary | Invalid metadata/files/audio raise `CorpusError`; valid leakage returns failed; planned, unassigned or incomplete requested audio returns inconclusive. Physical/independence/history claims remain not established. |
| Exit codes | 0 pass report; 1 leakage report or input rejection with stderr and no success report; 2 usage; 3 inconclusive report. |
| Work bounds | 512 captures; 1 MiB index; 16 MiB aggregate manifests; 2 GiB aggregate declared artifacts counting each reference; 256 MiB selected audio; bounded parents, nodes, depth, graph and findings. |

The canonical decoded digest is the versioned A07 definition: domain prefix,
little-endian rate/channel/frame geometry and normalized finite binary64 samples
in frame/channel order, with positive-zero canonicalization. It catches identical
samples with changed harmless WAV headers but does not infer crop/resampling
lineage or perceptual similarity. The report makes that limit explicit.

The contract includes independent adversarial acceptance for type/key/parser
rejection, bounded resources, immutable parsed-byte identities, confinement and
aliases, every grouping reason and transitive leakage, external-parent cycles,
changed headers, absent derivative geometry, failed/inconclusive preservation,
canonical replay, relocation and absence of hidden output artifacts. These are
requirements for subsequent execution, not results of tests run by this worker.

## Verification and remaining gates

Executed read-only checkout/status inspection and documentation consistency
checks from the repository root:

- `git log -1 --format='%H %s'`, `git branch -vv` and `git status --short`: observed
  the checkout identity above, local `main` tracking `origin/main`, and concurrent
  root/worker changes; preserved those changes without staging or rewriting them.
- A standard-library Python documentation check read both owned files as UTF-8,
  verified final LF, no trailing whitespace and balanced fenced blocks, parsed
  both JSON shape examples, checked their exact index/entry/edge key sets and
  64-character example digest, and resolved every relative Markdown link: passed.
- `git diff --check`: no reported whitespace error. Because the two new owned
  files were still untracked, their whitespace was independently checked by the
  Python check rather than inferred from that git result.
- `rg` cross-check against A07's written audio contract confirmed the actual
  inspector signature, observed size/hash field names and decoded-digest version.

These are documentation checks, not execution of the proposed APIs. No tool
implementation, schema acceptance, audio parser, corpus audit, physical
acquisition, calibration, listening or native/CI gate was executed here.

The root integrator owns acceptance, shared status/log updates, source freeze,
commit and publication. A14 can implement directly against this contract; an
independent worker should construct its graph and literal-byte oracles before
grading the producer. Any contract clarification must be explicit and precede
grading. The absent actual specimen/permission/calibration/synchronization and
untouched final-study evidence remain open even if future synthetic tests pass.

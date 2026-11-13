# Agent 40 — original proposed capture contract

## Scope and source reading

Read `AGENTS.md`, README/status/next steps/latest development log, M0/M8 in
`PLAN.md`, the atlas review and review 05; read original extracted atlas
pp. 355-372. Checked `main`/origin and preserved unrelated working-tree changes.
The atlas companions remain absent. This is an original project-authored v1
reconstruction of requirements, not recovery of their schemas or test results.

Owned changes: `data/capture.schema.json`, `data/capture-planned-example.json`,
`tools/validate_capture.py`, `docs/CAPTURE_FORMAT.md`, and this note. No other
agent's files, shared status, engine, source PDF or dependency list were edited.
No commit, push, hardware capture, or measured dataset was made by this agent.

## Contract decisions

- Planned records have null acquisition timestamps and no artifact records.
  The committed example has no specimen, calibration, acquired filename or hash.
- Recorded records declare hardware/synthetic kind, acquisition time/operator/
  session, digital format/rate/channels and acquisition grouping. Hardware identity
  and physical calibration may remain null with nonblank reasons.
- Digital header/declaration rate is separate from a qualified physical clock.
  Per-channel physical scaling has explicit boundary/unit, status, standard
  uncertainty and evidence locator. Merely recording bytes never marks calibration.
- One shared clock/stream per manifest; exact setup, controls, conditions,
  synchronization, bypass, loading and permissions stay explicit text or unknowns.
  Support files retain fuller identity/chain/rights/calibration material.
- Strict exact keys/types, IDs, true calendar UTC dates, finite bounded numbers,
  null/reason consistency, channel counts/indices, and hardware/synthetic state
  rules are enforced by a dedicated stdlib checker, not a generic schema engine.
- JSON is bounded to 64 KiB, 4096 nodes, depth 16 and 2048-character strings;
  duplicate keys, unsupported types and nonfinite/overlong numbers are rejected.
- At most 32 files, 16 parents, 256 MiB per file and 512 MiB total. IDs and
  portable relative paths are unique. Parent IDs resolve; self/cycles and derived
  files without raw ancestry reject. Every artifact inherits one group/split role.
- Default validation reads no artifacts. Explicit recorded-only `--check-files`
  streams sizes/SHA-256 in 64 KiB chunks; it does not load audio or verify headers.
  Selected roots and artifact components reject symlinks/reparse points; POSIX
  opens bind parent descriptors. Root ancestors canonicalize for macOS OS aliases.
  Hardlink aliases and changes during hashing reject where file IDs are available.
- APIs and CLI were published early to Agent 41; independent tests use their own
  fixtures. Agent 42's acquisition protocol consumes the same stable contract.

## Observed checks

- Planned-example CLI passed with file checking unrequested and authenticity,
  calibration and physical fidelity explicitly `not_established`.
- Narrow manual checks accepted planned and temporary generated synthetic records,
  verified four synthetic bytes, and rejected eight cases: missing file, wrong
  digest, duplicate JSON key, Boolean version, NaN, traversal, impossible date,
  and non-null synthetic physical calibration. Validation did not mutate input.
- The already installed Draft202012Validator accepted the schema meta-check and
  planned/synthetic fixture shapes. This development check added no dependency;
  the published validator requires only Python >=3.10 and the standard library.
- Agent 41's independent 38-method suite passed locally after the path hardening:
  `python3 -m unittest discover -s tests -p test_capture.py -v` (0.699 seconds).
  Agent 41 then reported 39 methods and native CTest 1/1 passing, including the
  in-memory uncalibrated-hardware admission case; see Agent 41's retained report.
- Additional in-memory, explicitly fictional declarations accepted uncalibrated
  hardware metadata and a qualified clock different from the digital rate; seven
  invalid clock value/type/uncertainty/unit cases rejected. Schema/tool consistency
  passed planned, synthetic and fictional calibration shapes. No hardware fixture
  was serialized or byte-checked; these declarations are not measurement evidence.

## Remaining M0/M8 gates

No schema pass proves true acquisition, metadata, calibration, permissions,
format/header agreement or physical fidelity. No calibrated physical fit is admitted
automatically. Real specimen/revision/condition and permission lock, physical chain/
clock/synchronization evidence, restorable immutable acquisitions, global ancestry/
split independence, upstream-first fitting, frozen tolerances, uncertainty and
held-out results remain open. Cross-manifest references and corpus split audits are
outside v1. Keep archives quiescent: portable checks are not a hostile filesystem
sandbox. Windows/macOS runtime qualification remains an integration/hosted-CI gate.

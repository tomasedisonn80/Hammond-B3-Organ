# Assignment 51 — independent core preservation audit

- **Actual worker:** `/root/w09_a51_core_preservation`.
- **Logical wave:** 9; assignment 51 in this session, not an earlier agent reused.
- **Scope:** compare baseline `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1` against
  published standalone checkpoint `649b12c7d1faa7601fde1019e913347c65a6634a`.
- **Owned paths:** this note and
  [`docs/reviews/STANDALONE_CORE_PRESERVATION.md`](../../reviews/STANDALONE_CORE_PRESERVATION.md).
- **Result:** completed audit; no production, test, CMake, shared-status or
  shared-ledger changes. Commit/publication remains the integrator's task.

## Work and executed evidence

Read the standing agent instructions, plan, status, next steps, scanner handoff,
atlas review and independent standalone/rotary/calibration ownership scopes.
Created two new source archives and two fresh SDK-free Release builds using
GCC 14.2.0 and CMake 4.4.4. Verified all 616 baseline and 842 checkpoint tracked
blobs/modes before and after execution. Neither private build used live headers
or the concurrent native timing/concurrency edits.

All **196 pre-existing files** under `src/`, `include/`, `plugins/`, `tools/`,
`data/`, `tests/` and `examples/fixtures/` retain identical bytes and modes.
The independent rotary module adds one core-archive member but is absent from
the renderer's symbols; calibration additions remain offline tooling. Existing
plugin class IDs, parameter registry and B3CONTROLS grammars are preserved.

Both revisions passed **11/11 selected control, migration, console, pedal,
parameter and performance suites**: baseline 2.97 seconds, checkpoint 3.13 seconds.
Both actual parameter tools emitted identical complete 45-record metadata at
default, 0, 0.5 and 1. The nominal compiled profile and generated pedal/scanner
headers are independently regenerated and byte-identical.

The unchanged retained comparator ran eight manual/console scores in three
forms, **24 renders**. A separate audit ran all four pedal scores on both
revisions with 127-frame and 1-frame blocks, **16 renders**. All 40 actual WAV/PCM
outputs and applicable metrics match exactly across their comparison groups;
all report zero clipping. The pedal audit separately checks known silence,
audible content, positive bounded peak and identical dry stereo channels. The
total rendered frame count is **3,241,200**. No retries, failed executions,
weakened assertions or selected-test skips occurred.

The renderer executables themselves are byte-identical: 135,320 bytes, SHA-256
`9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
This is observed for this same toolchain, not a cross-toolchain guarantee.

## Handoff and limitations

The full report retains exact commits/trees, commands, generated-input and
executable identities, source counts, state-test counters, representative WAV
hashes, meaningful boundaries and the next integration gate. Raw source
inventories, 31 recorded outer commands, complete logs and 40 WAVs are at
`/workspace/scratch/5ba97739b54c/a51-core-preservation`.

This audit establishes preservation for its named source pair. It does not
qualify concurrent adapter changes, native host exports, physical devices,
sanitizers or measured Hammond/Leslie fidelity. No root gate was closed merely
because these checks passed. Next: integrate the completed native repairs into
one coherent source, retain their distinct failures and acceptance, and run the
assigned complete-source/hosted qualification before final publication.

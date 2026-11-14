# A23 — Independent pending Session and raster acceptance

Worker `/root/w04_a23_pending_independent`, wave 4. Owned this note and
[`A23-pending-independent.json`](../reports/A23-pending-independent.json) only.
Read AGENTS, the current scope/checkpoint/actual manifest, complete M0–M9 plan,
inspection contracts, A18 source/reports/metadata/inventory, and the actual
Session, UiModel, InspectionModel and native capture paths. No production/test
edit, shared build, CTest invocation, GUI, commit, push or spawn.

## Exact acceptance boundary

Observed HEAD `e4968b2acd37b6f79683704356350070fe2fc329`, committed tree
`1aff4305e347b46c659dcbc27eb524649a4c54c8`; concurrent work remained present.
Rehashed all 102 A18 inventory inputs: **99 match**. Root `CMakeLists.txt`,
`apps/standalone/main.cpp` and `src/RotaryMotion.cpp` have advanced, with old/new
identities retained in the report. The harness, Session, UiModel, inspection,
Drawing, InstrumentView, standalone CMake, assets and profile inputs match.
This review qualifies A18's exact retained executable and captures, not the
whole changing worktree.

| Input | Independently matched SHA-256 |
|---|---|
| Harness source | `d04873c3d4d7d2b76c2c678e592ac8bc8e13f01af64faafce581fbf69b35950d` |
| Native executable, 3,445,104 bytes | `44e059f761aff6c04af62088b7a26d500839f95043e297dcf7769c08e3094b60` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Original/retained native metadata | `daa1531a1f5345da8d68dd260f5a12e458f60f0d9d5d164ca5fafcbdfefefc9a` |

## Independent causal and ownership review

`Session::post` copies a command and allocates its sequence without publishing.
`render` consumes its acquired prefix, applies commands and publishes; a
zero-frame call preserves elapsed frames and the previous peak. `publish`
increments the revision by two. `UiModel::submitted` remembers the control
sequence; `observe` retains desired controls while it remains unresolved.
Keyboard release uses the captured original owner before shortcut/workspace
handling. No fabricated Session observation or callback delay supplies pending.

The retained metadata and fresh replay agree exactly:

| Observation | Frame | Revision | Resolved / applied | Upper target |
|---|---:|---:|---|---|
| Started | 0 | 4 | 0 / 0 | none |
| Note held | 32 | 6 | 1 / 1 | MIDI 60 |
| Preset pending | 32 | 6 | 1 / 1 | MIDI 60 |
| Preset acknowledged | 32 | 8 | 2 / 2 | MIDI 60 |
| Released | 32 | 10 | 3 / 3 | none |
| Stopped | 32 | 12 | 3 / 3 | none |

Sequence 1 is actual A Down, Upper bus 0/channel 0/MIDI 60/owner 1. Sequence 2
is the complete desired Fixed F control copy; the pre-flush publication equals
the held publication and retains applied Bank B. Workspace changes, resizing
and painting neither submit musical commands nor change that publication.
Zero-frame acknowledgement applies F and clears pending. Actual A Up at sequence
3 retains owner 1 and clears the held target; stop preserves applied F. All six
observations have zero faults/recovery/overflow/rejection/discard counts. The
zero peak and held flags do not establish audible output.

## Executed replay and image verification

From the existing Release executable under
`/workspace/scratch/1bb6ee17ad7e/build-native/apps/standalone/`, ran directly in
the isolated `../A23-pending-independent/ordinary` directory:

```sh
/workspace/scratch/1bb6ee17ad7e/build-native/apps/standalone/test_standalone_inspection_raster
/workspace/scratch/1bb6ee17ad7e/build-native/apps/standalone/test_standalone_inspection_raster --capture-dir /workspace/scratch/1bb6ee17ad7e/A23-pending-independent/new-capture
```

Both exited 0; ordinary execution passed 947 assertions and created no files.
Capture passed 965 assertions. Reusing the capture directory and separately
passing an existing empty directory each exited 1 with `refusing overwrite`;
all prior output hashes remained unchanged. CMake source and generated CTest
registration both invoke the ordinary no-argument form. CTest's own shared logs
were left to A22; no new independent CTest result is claimed.

Using Pillow 13.0.0, independently decoded all six original scratch BMPs and
retained PNGs to RGBA. Dimensions, byte counts, file hashes and all six decoded
hashes match the inventory; every decoded pixel matches. The fresh six BMPs
**and metadata reproduce all seven A18 output files byte for byte**. Recomputed
pending/acknowledged differences are **5,317 / 2,918 / 2,698 pixels**.

Visually inspected all six original retained PNGs. Pending Play shows sounding
B, F pending and the held Upper key; acknowledgement shows Fixed F with the key
still held. Both Service sizes visibly show Current, frame 32, revisions 6/8,
the corresponding pending status and applied Upper selection. Upper `1 target`
and Lower/Pedals `0 targets` are legible; no inspected label collision/clipping
was observed. Minimum-size typography remains small and needs physical DPI
review. Stopped audio/no active configuration is truthful for this harness.

**Pass within scope; no blocker found.** These are native rendering harness
captures without an application window or audio device. Desktop input/capture,
physical display/audio, timing, accessibility and literal reference equality
remain separate. Next: integrator accepts these exact evidence identities and
continues the separately scoped complete native desktop journey.

# A29 — independent product compatibility review

Actual worker `/root/w05_a29_compatibility`, wave 5. Read the full standing
instructions, M0–M9 plan, session records, MIDI/crossover contracts and relevant
production/test evidence. Owned only `docs/PRODUCT_COMPATIBILITY.md` and this
note. No production edits, shared-build mutation, commits or publication.

Compared baseline `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d` with published
`ff41d412d03f2c5767aa4057b29fa8ec1627449b`, tree
`6462343bb34a7d70d59de75ab349f8530196988c`. Read-only Git/blob/SHA-256 commands
ran from `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`; the compatibility
document preserves the exact reproduction commands and representative hashes.

All 52 existing core/header files are unchanged; only independent
`LeslieCrossover.h/.cpp` are added. All 20 VST3 files, 39 data/CMake helper
files and four UiModel/StateFiles files are unchanged. All 28 changed-source
hashes in `wave4-coherent-build.json` match the published blobs. Current app
SHA-256 remains `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`;
profile remains `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

Confirmed the 47 exact parameter records, state 4 writer/readers 1–3, dry/shared
source implementation, HostTimeline, plugin UUIDs and 68-control/24-preset/
147-playing-key inventory. Inspected literal state migration oracles, default
CC11 bit equivalence, independent physical-event audio traces, ownership/queue
recovery, pending CC121 edits, calibration state-file invariance and visual
inventory assertions. The retained coherent GCC 14.2 Release log records
176/176 passes in 177.92 s; I did not repeat that suite. It had physical MIDI and
VST3 disabled, so its count supplies no current plugin or device qualification.

No incompatibility defect found. Documented intentional native-only CC120/121,
the eleven-stop calibration modal, expanded diagnostics schema 3, and the need
to rebuild changed internal C++ adapter consumers. Calibration and crossover
checkpoints remain separate from musical saved state; neither adds VST3 MIDI
delivery or live cabinet processing. Crossover 192 kHz does not extend Engine's
three admitted rates.

Next: register A26's real-main fixture and retain its exact-source lifecycle
CTest result; qualify the published VST3 matrix separately. Hardware, DAW,
deadline, display/accessibility and physical/acoustic gates remain open. Local
leak-enabled sanitizer is environment-blocked, not passed. Scoped whitespace
and local Markdown-link checks passed.

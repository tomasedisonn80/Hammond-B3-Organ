# A32 — Native MIDI operating guide

Actual wave-6 worker `/root/w06_a32_midi_operating_guide`. Read standing
instructions, complete plan, session scope/checkpoint, both MIDI contracts,
current main/MidiInput/modal code and A24/A26 acceptance notes. Starting base:
`ff41d412d03f2c5767aa4057b29fa8ec1627449b`, tree
`6462343bb34a7d70d59de75ab349f8530196988c`; concurrent work was preserved.

Added `docs/MIDI_EXPRESSION_GUIDE.md` with locked Linux/macOS/Windows build
recipes, multi-configuration paths, exact CLI options, illustrative endpoint
arithmetic, eleven modal stops, selected/configured/active/pending meanings,
release-barrier reconfiguration, healthy identical-request no-op, failed-open
retry, Disconnect/Panic/audio restart, volatile configuration and reproducible
CLI startup. Native CC120/121/123 scope and global expression are explicit.
Added bounded synthetic examples and links to actual A24/A26 suites/evidence.

Updated only the assigned Interface and Preset runbooks and, after root expanded
ownership, `MIDI_UI_RUNBOOK.md`. Corrected that guide's obsolete eight-stop,
uncalibrated-CC11-only and unsupported-CC120/121 descriptions. Historical
platform/gallery evidence remains historical. No README/shared status,
production, install-module, dependency or build edits were made.

## Executed checks

Used the existing read-only
`/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone`:

- Default and calibrated `--help`: exit 0, all three options present.
- Equal/reversed endpoints, fractional/negative minimum and repeated invert:
  five expected exit-2 refusals before device initialization.
- Three 800 ms guide replays with explicit dummy SDL audio/video: exit 0,
  completion/delivery/acknowledgment/pass true, errors 0. Endpoints 20/100 with
  raw 40 gave 0.25 Normal and 0.75 Inverted; Pedal-channel CC121 reset gave 1.0
  with inversion retained. Native generation/callback messages remained 0;
  pre-shutdown calibration was active and final active was null. Temporary
  scripts/diagnostics were removed after assertions.
- Build recipes were checked against locks, existing guides, CMake and the
  platform workflow; no acquisition, configure, build or CTest was run.
- Scoped `git diff --check` passed. Five owned Markdown files passed trailing
  whitespace/fence checks: 77 local/repository link targets exist and 29 code
  blocks are balanced. This note remains below 400 words.

SHA-256: `main.cpp`
`937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027`;
executable (unchanged before/after checks)
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.

Limits: no physical devices, pedal measurements, OS callback concurrency,
latency, screen-reader, cross-platform execution or new pixel acceptance.
VST3 and the dry Engine remain unchanged. Root owns installation/navigation,
coherent gates and publication; no commits or spawns were made.

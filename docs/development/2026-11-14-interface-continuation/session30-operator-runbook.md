# A30 — independent native operator and runbook audit

Actual assignment: A30, logical wave 5. Owned paths are this note,
`docs/reviews/INTERFACE_OPERATOR_AUDIT.md`, and `reports/a30-*`. No shared guide,
production file, build configuration, index or commit was changed.

## Result

Completed five distinct native operator scenarios and two CLI admission checks.
Four native scenarios passed; one actual native MIDI discovery failure is
retained alongside successful No input recovery assertions. This is scoped
operator acceptance, **not an unqualified MIDI pass**. The full
[operator review](../../reviews/INTERFACE_OPERATOR_AUDIT.md) gives the journey,
two precise findings, source explanation, screenshots, commands and limits.
The [audit record](reports/a30-operator-audit.json) hashes the full retained
payload, and [result.json](reports/a30-operator-evidence/result.json) preserves
all case outcomes and executable checks.

## Executed work

- Read repository rules, current session/checkpoint, full M0–M9 plan, current
  status/next steps/log, operating guide, replay grammar, native workspace and
  workflow machinery, and relevant CLI/modal/renderer source.
- Copied the supplied executable to `/tmp/a30-operator-pinned/` before A28's
  shared rebuild. Every launch and the final copy matched SHA-256
  `005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364`.
- Ran fresh sequences for first launch/read-only Service→Rotary→Play, held
  keyboard navigation, retained-bank versus fixed/sounding selection, exact
  Save/live Load/cold reload, Help/Audio release and restart, and MIDI No input
  Apply/Disconnect/Close. Exact schemas and all meaningful musical/lifecycle
  fields were asserted, then diagnostic transitions and errors were inspected.
- Retained two native PNGs (minimum Service Flat and default Play Dimensional),
  visually reviewed them, and removed only their own reproducible BMPs after
  reopened-PNG decoded-pixel equality. Evidence is 355,563 bytes.

The actual driver command is in the review and audit JSON; per-process commands
and exact replay inputs are under `reports/a30-operator-evidence/`. One initial
exec-server transport failure occurred before process creation. After a simple
workspace check succeeded, the command was retried once; it is not counted as an
application process. No test-suite rerun or build/configure was performed.

## Findings handed to root

**A30-G1:** add the dummy-SDL/native-RtMidi distinction to
`docs/INTERFACE_RUNBOOK.md` under MIDI discovery/recovery. Linux has no
`/dev/snd/seq` here, so explicit discovery failed; No input recovery and fresh
keyboard playing still worked, but the retained error correctly made the replay
exit 1 with `replay.passed=false`. Exact proposed wording and failed stderr are
in the review. Root will apply it after A29 releases its package source-byte gate.

**A30-G2:** A36 owns the stale post-Load status text. At 3166 ms the screenshot
shows CURRENT SNAPSHOT and applied fixed F# while the bottom strip still says
“Loaded controls; waiting for the audio callback.” Load acknowledged at 2186 ms;
`controls_pending=false`. `Application::load_state()` calls `message()` with
that text; `message()` retains it for six seconds independently of acknowledgment.
The finding does not undermine the verified exact control or held-note behavior.

## Identity and remaining work

Base main is `5d81199a9822874b55f3b0a124715cbd6eadf0e5`, which does not contain
this UI overlay. Final observation of the concurrently rebuilt shared executable
was `55b0947985ee562cce3d04eae66cc4d44f805420f475dd578f00373dd2bef6cd`;
this audit qualifies only the pinned earlier bytes. The audited guide hash was
`cee311e98e477aa9e330b3d1060dd04668bafcf6150e1c964570538d9f34e7a5`.

Next: root accepts this scoped audit, adds the guide clarification, assigns A36's
status correction and qualifies the coherent newer executable. A27/A34 retain
the separate minimum-size accidental-label finding. Physical devices, persistent
pointer capture, display/DPI, native screen-reader access, deadlines and physical
model fidelity remain unproved. Dummy capture fails immediately; no persistent
mouse ownership claim is made. Root owns integration, staging, publication and
shared status updates.

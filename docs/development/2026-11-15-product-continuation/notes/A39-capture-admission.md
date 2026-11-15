# A39 — strict MIDI-disabled capture admission

Actual worker `/root/w07_a39_capture_admission`, wave 7. Read AGENTS, the complete
M0–M9 plan, active checkpoint/assignment, capture implementation, retained v3
diagnostics and A22's current strict native schemas. Starting HEAD
`b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree
`b3b8b68e4c1f8312d46962924b5096f4ea10c4d2`; qualification covers the owned overlay.

Changed only the capture utility, its Python regression suite and this note's
evidence. Admission now derives the exact inert MIDI state from strictly typed
compiled-backend facts: available ALSA/CoreMIDI/WinMM requires `closed` before
and after shutdown; unavailable requires backend `unavailable` and that exact
state twice. Contradictory, missing or malformed facts fail. Zero device and
discovery facts now require complete typed members, with no selected/open port,
generation, active transport or MIDI replay. Clean quiescent shutdown remains
mandatory. Existing held-target, pointer, endpoint, acknowledgement, dimensions,
presentation and source/build/executable/tool/input freeze checks remain intact.

Executed from `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`:

- `PYTHONDONTWRITEBYTECODE=1 python3 tests/test_capture_standalone_interface.py -v`:
  **13/13 methods**, **0.244 s**, including all eight actual retained v3 positives
  and original painted-state mutations. New copied-dictionary variants test
  backend/state contradictions, missing/type errors, device/discovery activity
  and shutdown in both modes; they are not new platform captures.
- One root-authorized minimum-size actual replay: native exit **0**, empty
  stdout/stderr, **1.934 s**, MIDI OFF. The old tool rejected it with
  `capture unexpectedly opened/enumerated a native MIDI device`. The repaired
  validator admits the same unchanged bytes. A22's `assert_no_midi_input` and
  `assert_presentation` independently pass those diagnostics without another run.
- Scoped `git diff --check`: passed.

[Result and original failure](../reports/A39-capture-admission.json) retain
commands, configuration, input identities and the checked 108-source integrator
report; [native diagnostics](../reports/A39-midi-off-diagnostics.json) retain raw
bytes. Executable SHA-256:
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.
Tool: `83c214d6f0d6b0fc06910412f41f13a0f3286bebd034280a19d4e5e397875b1f`.
Tests: `2f2f32be77cf2832435d1eb0adf089f779c8d575b437859f33a1c11a7f126d83`.

Native inputs remained unchanged. No production/build mutation, full gallery,
commit or publication was performed. A40 can run its eight-frame gallery and
separate overlay against the frozen tool. Dummy SDL/software evidence does not
qualify physical displays, MIDI hardware, accessibility, deadlines or literal
1:1 equality.

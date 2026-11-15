# A24 — native MIDI/calibration acceptance

Actual wave-4 worker `/root/w04_a24_native_midi_acceptance`. Read the standing
instructions, whole M0–M9 plan, session scope/checkpoint, both frozen MIDI
contracts and A16/A18/A22 handoffs. Starting HEAD `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`;
qualification names the changed executable separately from that documentation
commit. Owned only the two native MIDI test files and this note.

Migrated the original CLI suite to the measured 740×600 dialog and eleven focus
stops. Preserved channel routing, invalid Apply, Cancel, focus wrap, shortcuts,
nonexistent-port, enumeration and original musical-release checks. Added strict
endpoint/invert refusals before SDL/output writes; pointer actions at both sizes in Dimensional/Flat; endpoint clamping, Home/End, direction actions, valid/invalid
selected intervals, correction after refusal and unapplied-setting cancellation.
Calibration configuration and Apply leave musical expression unchanged.

Migrated replay observations with A22's exact typed schemas, preserving member
checking and nullable active/pending semantics. The unsupported packet fixture
now uses CC122/124; valid CC120/121 have their own executed positive coverage.
CC120 and legacy CC123 preserve shared UI owners and other divisions. Six
completed inverted-calibration prefixes verify calibrated CC11, all three
divisions' CC121 reset to 1.0, nonzero mode refusal and retained notes/settings.
Valid synthetic Apply retains script-owned routing/calibration; invalid Apply
reports an error before that no-op while the active epoch continues unchanged.
Existing pending-edit, FIFO, overflow, fault, restart and interruption tests remain.

## Executed verification

From the repository, set `PYTHONDONTWRITEBYTECODE=1` and
`HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone`:

- `python3 apps/standalone/native_tests/test_standalone_midi_cli.py`: **21/21**,
  **155** subprocesses, **18.888 s**; 15 successful and 4 deliberately failed UI replays.
- `python3 apps/standalone/native_tests/test_standalone_midi_replay.py`: **15/15**,
  **33** subprocesses, **40.863 s**; 2 deliberately failed/interrupted replays.
- Scoped `git diff --check`: passed. Both suites explicitly choose dummy SDL.

SHA-256: executable `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`;
CLI test `54af4bd4bc9a203c8af2c9543a8e961f3f8fb13774a99c7ca1edce41e895ef48`;
replay test `4fccad4d06dfd2875b24ba8798477089cc27f78061f7f17dd313c0aef0740fca`.
Compact identities/results and logs remain in sibling `a24-checks/summary.json`,
`cli-first.log` and `replay-first.log`. Earlier integration failures remain in
session `reports/wave3-native-regression.json`.

Next: root runs both registered CTest gates and the full coherent regression.
Native healthy reconnect belongs to A26. These tests establish no physical MIDI,
latency, accessibility, pixel equality or measured-sound result. No production
edits, shared-build mutations, commits or publication were performed.

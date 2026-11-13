# Agent 50: retained nominal audible demo

## Assignment and ownership

Actual agent 50, wave 09. Read repository instructions, README, status/next steps,
latest development entry and both ledgers; reviewed render evidence, verification,
PCM measurement and catalog contracts, plan/review, and atlas pp. 355–360/367–372.
Owned only `examples/rendered/nominal-two-manual-v1/` and this note.

## Deliverable

Added a real four-second `two-manual-changes-v1` WAV and untouched producer bundle.
The package README and eight independent reports sit beside `bundle/`; its exact
seven-file inventory remains valid. Copied score/profile, compiled profile,
manifest and raw renderer stdout/stderr are retained with the WAV.
No executable, build tree, imported recording, or new model was added.

## Executed evidence

Exact commands, measured values and raw-byte hashes are in the package README.
`render_fixture.py` used `/tmp/hammond-wave07-asuv11lz/build/hammond_render`,
current authoring profile, catalog score, 192000 frames, 48000 Hz, block 127,
seed 2601 and drawbars `006400000`; the wrapper enabled `--fail-on-clip`.
The wrapper and renderer returned 0; producer status is `succeeded`.
`verify_render.py` returned 0: `verified_retained_bundle`;
it checked six artifacts plus manifest and matched the external executable.
`analyze_wav.py` returned 0 for the whole file and all six score windows.
All four chord spans contain nonzero PCM; initial 2400 and final 24000 frames
are exactly zero in both channels. No single-frequency assumption was supplied.

WAV: 192000 frames, 48000 Hz, 2 identical PCM16 channels, 768044 bytes.
Renderer float peak/RMS: 0.08130008727312088 / 0.02006219567993473.
Independent PCM peak/RMS: 0.081298828125 / 0.020062170290109253.
Renderer clipping: 0 frames, 0 channel samples. PCM endpoint samples: 0.
WAV SHA-256: `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
Manifest SHA-256: `74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`.
Manifest was read and hashed after creation, never rewritten.
Final audit found exactly 16 demo files, 18 matching README hashes and 35 valid
local links; all text files had no whitespace diagnostics. The initial audit
wrongly required exit 0 from `git diff --no-index --check` for new files; corrected
to accept its normal diff exit 1 only with empty diagnostic streams, then passed.

## Scope and integration handoff

Producer checkout HEAD: `6c3dd8bc923a3c11f6b234425b056e135fbe9f4b`; dirty=true.
`git.binary_association` remains `not_established`; executable/source association,
authentication and physical fidelity remain unestablished. Verification did not
replay the renderer; agent 51 separately owns fresh-build/replay evidence.
This is nominal dry shared-sine audio, with ideal gates that can click; no scanner,
AO-28, Leslie, plugin, device, calibrated capture or realtime claim follows.
PCM endpoints alone cannot infer pre-encoding clipping; measured sample peaks
are not true-peak/physical levels. No broad test suite was rerun for this artifact.
Root owns shared docs/catalog/inventory, staging, publication and remote checks.
`*.wav` and `*.b3p` are intentionally ignored; root must explicitly add only this
bundle's `render.wav` and `profile.b3p`. No staging, commits, pushes or spawning.

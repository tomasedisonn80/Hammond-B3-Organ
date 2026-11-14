# A12 — Independent integration and unchanged-boundary inventory

Actual worker `/root/w02_a12_integration_inventory`, wave 2, assignment 12/60.
Read-only production review on 2026-11-14. Baseline remains
`d493e998e5dd7cf44db46854e87309745063ac54`; the observed checkout had advanced to
`c83fe2336be931385f0d7ab82c55b30bfdfc8fc6` while this review ran. New documentation,
the Windows oracle repair and concurrent A10/root work do not retroactively
change the baseline's tested source identity.

Owned deliverables are this note and
[`reports/a12-boundary-inventory.json`](reports/a12-boundary-inventory.json).
No production files, shared status files, dependencies or build trees were
modified by A12. No tests or builds were rerun and no commit was made by A12.

## Evidence actually checked

- Read `AGENTS.md` and the workspace, geometry and inspection contracts, then
  inspected the affected model, native adapter, renderer, replay, tests,
  CMake/install and workflow sources. Contract digests at review time are retained
  in the report; later editorial corrections may legitimately change them.
- The retained CTest log says **136/136 passed**, with **155.19 seconds** total.
  Its SHA-256 is `6c644a7c15cc4bad5670e561537cd95a90b43eaa3d9d7576105c9daa8ed5c3f5`,
  exactly the value in `baseline.json`. The preserved standalone executable also
  matches that report: `557acb27d16cfc77815c278778335f8418b471b563d1b93a47bf3051eae68c82`.
- Compared **114 protected tracked files byte for byte** with their Git blobs at
  `d493e998`. There were **zero mismatches**: 44 core files, 29 data files, six
  native audio/state files, 20 VST3 files, 11 retained asset files and four atlas
  source/provenance files. The report stores every path, byte count, Git blob and
  SHA-256, plus deterministic group digests for a later comparison.
- The registry still contains **47** records, schema 4. Source inspection confirms
  the `B3CONTROLS4` writer and readers for versions 1–4. The atlas still hashes to
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Baseline qualification remains Linux Release with MIDI/ALSA compiled and SDL
  ALSA audio disabled, using dummy audio/video. This is retained baseline
  evidence, not execution against new interface code, physical-device evidence,
  hosted repair acceptance or a 1:1 visual-fidelity result. A10 owns the observed
  macOS enumeration stall; A11 owns the observed Windows rounding-oracle failure.

## Contract consistency

The three contracts agree on 68 stored controls, ten common header controls,
71 Play focus stops, ten Rotary/Service stops, 147 playing keys, 24 unchanged
rectangular preset keys, transient workspace/presentation state and no sound
parameter/state migration. The geometry contract's shared hit/top/front quads
fit the workspace layout additions without a second presentation enum.

One editorial mismatch was reported immediately: the workspace contract's
inspection paragraph mentions device status in `InspectionRuntimeInfo`; the
inspection contract freezes only `snapshot_available` and
`snapshot_read_succeeded`. Device facts belong to the existing
`InstrumentViewInfo`. The integrator acknowledged ownership of that correction.

Inspection source validation is materially necessary. `Session::prepare()` uses
the default `Engine::prepare(profile, spec)`, which selects
`make_legacy_console_model()` and therefore **ideal-contacts-v1**. The separately
available nominal travel model must not be shown as active. The existing profile
grammar admits the nominal identifier with zero-filled trailing storage and a
lowercase 64-digit digest; actual source-46 frequency and gain must be read from
the supplied profile. Unsupported identity, unavailable snapshots, disconnected
scanner/AO-28/Leslie audio, unacquired physical values and retained stale data
need their contracted visible states.

## Exact implementation and fixture adaptation inventory

Line numbers below refer to the reviewed source and will move during integration.
These are required follow-up checks, not claims of completed acceptance.

| Area | Exact files and current assumptions | Required adaptation and preserved behavior |
|---|---|---|
| Model types/layout | `apps/standalone/UiModel.h`, `UiModel.cpp`: max 64; six header controls; old `UiKeyGeometry`; `valid_layout`, focus order and pointer routing | Append the frozen enums/fields and 68-count inventory; preserve old enum and parameter meanings; implement 71/10 visibility-aware focus and per-workspace memory; use shared quads for visible/manual hit geometry; preserve original note-release ownership through view, Flat and resize transitions. |
| Existing model assertions | `tests/test_standalone_ui.cpp`: 20-element `kinds` and `expected_kinds` around 746/810, `control_count == 64` around 906, 64-control focus loop around 1151 | Both kind arrays need 22 entries before indexing kinds 20/21; append counts 3 and 1. Update control/focus counts and first-focus/wrap expectations. Do not weaken invalid-ID or sound-parameter assertions. |
| Layout and geometry oracle | Same file: `equal_layout` around 541; `check_keyboard` around 575; literal header/key bounds around 928–953 | Equality/invalid-rollback checks must include workspace, presentation, workspace panel and every quad. Replace rectangular manual-edge assumptions with independently calculated projection boundaries; retain panel landmarks, 61/61/25 identities, black-first precedence and rectangular presets. Recompute only deliberately changed header/key geometry literals. Probe AABB corners outside the actual trapezoid. |
| Preset focus compatibility | `tests/test_standalone_preset_ui.cpp`: helper bound `<68`, counts 64 around 179/250, 67-entry order around 260; `native_tests/test_standalone_preset_raster.cpp`: helper `<68` around 44 | Extend the independently specified order to 71: three workspace tabs, the six existing tools, presentation, existing performance controls and three roving key stops. Give bounded traversal enough iterations. Preserve all 24 preset identities and the existing 96-case raster scope. |
| Native hotkeys/replay | `main.cpp` help, SDL mapping, option parsing and event adapter; `ScriptedInput.cpp` 35-entry key table around 38 | Append F4–F7 mappings and make the replay table 39 entries. Keep F1–F3 and computer-key playing global across workspaces; enforce the frozen repeat/modifier/modal rules. Optional startup `--workspace`/`--flat` must reject bad input before device/output side effects. |
| Independent replay grammar | `native_tests/test_standalone_input_replay.cpp`: literal whitelist around 142–144; explicitly invalid `F4` around 252; `docs/STANDALONE_INPUT_REPLAY.md` whitelist | Add F4–F7 independently; replace invalid F4 with unsupported F8. Keep malformed-token and payload rejection coverage and `B3UIREPLAY1` meanings. Update the documented whitelist. |
| Rendering and inspection | `Drawing.h/.cpp`, `InstrumentView.h/.cpp`; new `InspectionModel.h/.cpp` | Render the exact model quads, including inset outlines; keep shape validation/clipping bounded. Add read-only Service/Rotary bodies and common headers. Avoid a non-inline `UiQuad::contains` link dependency in the drawing-only native target. Add owned inspection model data to support; append view arguments carefully where aggregates are initialized. No Session/Engine/backend calls in inspection. |
| Diagnostic schema | `main.cpp::write_diagnostics`; `native_tests/test_standalone_app.py::SCHEMA` around 197 and recursive exact-key check around 129 | The existing oracle rejects extra keys at every nesting level. Add presentation keys to its literal schema alongside the adapter change. Preserve existing schema-3 field meanings and sound-controls shape. Capture/before-shutdown view identity must describe the actually painted view, not final teardown state. |
| Existing native workflows | `native_tests/test_standalone_workflows.py`: Panic click `(1228,66)` around 553; 21-Tab jump around 660; fixed playing-key points around 706; additional relative tab scripts around 526–529/578 | Update the changed header click and the old six-header-based initial focus count. Validate projected key points independently. Relative navigation starting from unchanged preset controls may retain its count; inspect it rather than applying a blind global offset. Preserve exact musical-command, hold/release, state-byte and callback assertions. |
| Other replay users | `native_tests/test_standalone_replay_boundaries.py`, `test_standalone_midi_cli.py`, `test_standalone_chapel.py`, `tools/capture_standalone_reference.py` | Audit literal screen points and before-shutdown fields. MIDI modal Tab counts are internal to the unchanged modal and should not be shifted for the main header. The historical capture tool's modal script uses Ctrl+M and internal Tab traversal; retain historical artifact identities and create explicitly identified new captures. |
| Build/test registration | `apps/standalone/CMakeLists.txt` | Add `InspectionModel.cpp` to support. SDK-free `tests/test_*.cpp` are discovered by the current glob; explicit native tests require targets, CTest registration and inclusion in `hammond_standalone_test_inputs`. Reconfigure before interpreting discovery. Root owns the existing Threads dependency change; A10's discovery helper/test must join the same build graph. |
| Required hosted gates | `.github/workflows/standalone.yml`: required-test set around 381 and build of `hammond_standalone_test_inputs` | The broad `^test_standalone_` filter runs discovered tests, but new workspace/inspection/geometry/native acceptance names should also enter the required set so accidental omission fails. Preserve `--no-tests=error`, existing MIDI gates and native package qualification. |
| Installed documentation | `cmake/InstallStandalone.cmake`: parallel source/name lists around 52; `native_tests/test_standalone_install.py`: `SOURCE_FILES` and `GUIDES`; `.github/workflows/standalone.yml`: package `expected` map around 433 and hardcoded 17/13 count around 456 | Add the current interface runbook in all three inventories and update the payload cardinality. The current preset runbook is absent from those lists and should be an explicit packaging decision. Reconfigure after guide edits, because hashes are configured into install metadata. Preserve exact bytes, movable-prefix/source-unavailable checks and embedded-asset behavior. |
| Current user documentation | `README.md`, `docs/STANDALONE_APP.md`, `docs/MIDI_UI_RUNBOOK.md`, current setup/status/next-step/log and new interface runbook | Document actual hotkeys, transient view state, copied inspection and pending/unavailable meanings; update README with actual Play/Rotary/Service/Flat captures. Keep source concept art separate and retain residual visual differences and all physical acquisition gates. |

## Acceptance that must remain independent

New SDK-free checks should explicitly enumerate 71/10 focus sets, all canonical
new/invalid IDs, idempotent transitions, hidden activation rejection, modal and
modifier gates, drag suppression through original Up, pointer/keyboard ownership,
resize preservation, all projection corners and black-first edge behavior.
Inspection checks need all stable row IDs/sources/evidence/units, bounded copied
text, the complete snapshot precedence, applied-versus-desired disagreement,
invalid identity/enums/nonfinite values, fixed/Cancel bank memory, effective
percussion eligibility and zero command/audio side effects. Native checks must
exercise the actual software renderer and replay/capture identity; core model
tests alone cannot prove those adapters.

Run the relevant changed acceptance first, then the combined selected build gate
once changes are coherent. Discover the final configured test inventory instead
of carrying 136 forward as a current count. Hosted macOS/Windows outcomes,
physical devices and visual matching remain separately qualified.

## Final unchanged-boundary comparison

From the repository root, the final integrator can compare the retained manifest
without rebuilding or producing a copied source tree:

```sh
python - <<'PY'
import hashlib, json
from pathlib import Path
p = Path('docs/development/2026-11-14-interface-continuation/reports/a12-boundary-inventory.json')
report = json.loads(p.read_text())
bad = [row[0] for row in report['files']
       if not Path(row[0]).is_file()
       or hashlib.sha256(Path(row[0]).read_bytes()).hexdigest() != row[4]]
assert not bad, bad
print(f"{report['file_count']} protected files match {report['baseline_commit']}")
PY
```

This manifest deliberately covers the unchanged boundary, not every UI file or
every historical report. The final source/tree, rebuilt binary, test results,
new captures and publication evidence need their own current identities.

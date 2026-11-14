# A21 — independent native workspace acceptance

Actual worker `/root/w04_a21_native_workspace_acceptance`, assignment 21 of
this interface session's 60 distinct workers, wave 4. Owned the new
`apps/standalone/native_tests/test_standalone_workspace_replay.py`, two narrowly
adapted inputs in `test_standalone_workflows.py`, this note and the accompanying
[compact report](reports/a21-native-workspace-acceptance.json) and
[executed output](reports/a21-native-workspace-acceptance.txt). No production
source, CMake, MIDI fixture, shared status, staging, commit or publication was
changed by this worker. Root owns registration and integration.

## Source and observed fixture repairs

Read `AGENTS.md`, the complete project plan, current scope/checkpoint, reviewed
workspace and geometry contracts, and A16–A18's implementation/acceptance
handoffs. The checkout HEAD was
`5d81199a9822874b55f3b0a124715cbd6eadf0e5`, tree
`52b4ec72b77e4442efe2e9e1b089b7b0ea6e638b`. Qualification applies to the concurrent
working-tree overlay and retained source/binary hashes, not that commit alone.

Waited until root's original native gate completed before editing its legacy
fixtures. That [retained first gate](reports/root-first-ui-gate.json) had five
failures in two workflow methods. Both were obsolete input assumptions:

- The first Upper drawbar is now the 25th initial Tab, after ten common controls,
  two Edit controls and twelve presets. Its four extra Tab pairs begin earlier
  at 20 ms; Home, note presses/releases, resize, Right and all existing replay,
  process and acknowledgment deadlines retain their original times.
- The old C2 sample `(202,580)` lies outside the projected left keyboard edge.
  The literal interior sample is now `(222,580)`, retaining the expected MIDI 36
  pointer owner alongside the keyboard's MIDI 60 owner. Counts and permitted
  capture-loss observation paths are unchanged.

No relative Tab sequence, preset/bank assertion, Panic coordinate, MIDI input,
saved-state expectation, musical release or timeout was weakened. The targeted
two-method recheck passed on the preserved A17 executable
`ca095152e8e94b4b1a51fa26f0e1fca346cbb2a7acfd7ec48b0a5839d83151fd`:
**2 methods, 5 subprocesses, 7.474 seconds**. No production defect was observed.

## Added executable coverage

The new suite runs the actual native event loop with explicit dummy SDL audio
and video. It reuses only test fixture literals and strict public-schema/
lifecycle helpers. Production layout, UiModel, Session, decoder and serializer
are not imported as expected-value oracles. Six methods execute 15 processes:

| Native cases | Independent expectations |
|---|---|
| Seven header-pointer cases | 960×700, 1280×900, 1672×941 and all four 1399/1400 by 819/820 combinations; literal Play/Rotary/Service/Flat/Save points, view transition order, keyboard and Space owners, exact canonical state4 bytes from noncanonical input. |
| Four hidden-body cases | Rotary/Service in both presentations; 13 literal Play regions each, hidden Space/arrows, unchanged controls, unchanged keyboard target/octave, and restored Lower C4 audition after return. |
| One focus-memory case | Upper-B drawbar restoration across workspace return, Flat and resize; Rotary remembers Save, Service remembers Load; actual later edits and exact saved/loaded bytes prove the remembered semantic target. |
| Two pointer failure-path cases | Parameter and note Down, immediate dummy capture failure, view/presentation/resize changes, later Move and off-window Up; no transferred parameter edit, glissando or release of the independent keyboard owner. |
| One combined MIDI/UI case | Synthetic MIDI Upper C4, Lower E4 and pedal 25 overlap keyboard Upper C4 and Space Lower C4; pointer workspace/Flat changes and resize preserve all owners; UI C4 release leaves the MIDI C4 owner until its own Note Off. |

Every case compares literal control and held-note paths, exact accepted On/Off
counts, total Session command deltas, acknowledged pre-shutdown state, one audio
device start and final joined cleanup. Navigation cannot silently inject a
control snapshot or release while preserving an otherwise plausible endpoint.
Schema-3 presentation checks cover initial and last-painted identity, bounded
transition observations, copied inspection flags, continuing frame clocks and
successful screenshot identity. Seven temporary BMPs are checked against their
requested dimensions and exact final painted records; their hashes are retained.
This is not a pixel-comparison or visual-fidelity gate.

## Executed gates

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Reused the existing Release native build and dependencies. Python was 3.12.14;
the generated native compiler record identifies GNU 14.2.0; diagnostics identify
SDL 2.32.10, dummy drivers and the software renderer. No new build tree or SDK
was created. A20's released executable was
`005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364`.
The new suite hashes it before/after execution and rejects a changed binary.

```sh
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/601951e27dc3/build-native/apps/standalone/hammond_standalone \
HAMMOND_STANDALONE_WORKSPACE_EVIDENCE=/workspace/scratch/601951e27dc3/a21-workspace-first-evidence \
python3 apps/standalone/native_tests/test_standalone_workspace_replay.py

/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native \
  --output-on-failure --no-tests=error -R '^test_standalone_workflows$'

python3 -m py_compile \
  apps/standalone/native_tests/test_standalone_workspace_replay.py \
  apps/standalone/native_tests/test_standalone_workflows.py
```

- New workspace suite: **6/6 methods passed**, 15 actual subprocesses,
  **39.137 seconds**; 501 UI records and six MIDI packets.
- Complete preserved workflow CTest: **1/1 passed**, **13/13 methods**,
  52 subprocesses, **64.12 seconds** CTest time. Its earlier failed inputs are
  retained in root's original report.
- Python compilation and owned-path `git diff --check`: passed.
- Root registered `test_standalone_workspace_replay` with
  `HAMMOND_STANDALONE_EXECUTABLE`, labels `standalone;native;workspace` and the
  existing 90-second native-suite timeout. Its generated CTest command was
  inspected; the new suite execution above was direct Python, not a separate
  repeated CTest run.

## Limits and next gate

Dummy SDL rejects `SDL_CaptureMouse`; main immediately dispatches CaptureLost.
These native cases therefore qualify capture-failure cleanup, with persistent
keyboard, Space and synthetic MIDI owners. They do not establish a held native
pointer across view changes. A18 separately passed the SDK-free model's held
pointer/parameter continuity contract; a real X11/desktop capture gate remains
required. Neither result substitutes for the other.

The suite does not assert deterministic PCM equivalence, every visual pixel,
all extreme-size rasters, physical MIDI/audio, host or callback deadlines,
native screen-reader behavior, connected AO-28/Leslie models, specimen fidelity
or exact reference-image equality. The next integration step is the registered
workspace CTest in the final coherent-source gate, alongside the independently
owned native gallery/raster evidence and later real-pointer acceptance.

# Reference refinement: native interaction acceptance

This is an acceptance contract, not an execution result. Apply it to the changed
layout under [current scope](REFERENCE_REFINEMENT_SCOPE.md) and the reviewed
[layout](REFERENCE_REFINEMENT_LAYOUT.md). Preserve 47 parameters, state4/readers
1–3, 147 playing keys, 24 presets and original release ownership.

## Three distinct claims

| Execution | What passing establishes | Remaining boundary |
| --- | --- | --- |
| Existing dummy-driver native replay | SDL dispatch, copied/applied state, ownership, rendering and joined cleanup | Dummy capture fails immediately; no OS capture qualification |
| Same scripts on an observed X11 window | Desktop backend and scripted dispatch/rendering | `SDL_PushEvent` does not establish real OS pointer delivery |
| Observed OS press, move, release, resize and close | Only the actual desktop interactions retained below | Synthetic MIDI and dummy audio do not qualify hardware |

[A57](development/2026-11-14-interface-continuation/session57-desktop-recovery.md)
observed focus navigation, an outside-drag released endpoint and supervised
SIGTERM cleanup. It did not observe held navigation, capture return or ordinary
close. Preserve those historical limits; root owns this session's desktop run.

## Executable automated gate

From the repository root, after rebuilding the changed application and tests:

```sh
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -N \
  -R '^test_standalone_(workspace_replay|native_midi_replay|replay_boundaries|input_replay)$'
HAMMOND_STANDALONE_WORKSPACE_EVIDENCE="$PWD/docs/development/2026-11-14-reference-refinement/reports/workspace" \
  ../build-tools/cmake/data/bin/ctest --test-dir ../build-native \
  --output-on-failure --no-tests=error \
  -R '^test_standalone_(workspace_replay|native_midi_replay|replay_boundaries|input_replay)$'
```

Use a fresh evidence destination. The current CTest listing contains four selected
tests. `../build-desktop` is the separate X11/MIDI-enabled build; identifying its
binary does not transfer another binary's qualification.

Adapt `native_tests/test_standalone_workspace_replay.py` under `apps/standalone/`:

1. Preserve its existing synthetic-MIDI/keyboard journey and add two complete
   branch-crossing cases: reference 1672×941 to minimum 960×700, and the reverse.
   At 1280×900 retain current behavior. Geometry/raster checks cover all four
   combinations of width 1399/1400 and height 819/820; add full journeys only for
   distinct ownership risks. Wide allocation requires both thresholds.
2. Keep its original schedule: UI Upper C4 at 180 ms, focused Lower C4 via Space
   at 330; synthetic Upper C4, Lower E4 and pedal 25 at 450/650/850. Navigate
   Rotary, Flat, Service at 1100/1300/1500; resize at 1700. Release Space at 1900
   and A at 2100 with the existing changed modifiers. Release MIDI at
   2350/2550/2750; return Play at 2950; finish at 3200.
3. Require Upper C4 to remain after its UI release because MIDI still owns it.
   Require Lower E4 and pedal 25 until their own Off commands. End with no held
   notes **before shutdown**, exactly five On/five Off commands, unchanged
   controls/canonical Save bytes and one audio-device start. Navigation and
   resize add no musical commands; frame clocks remain monotonic.
4. Keep independent literal click points; update only points that the reviewed
   layout actually moves. Check the relocated pedalboard, both manuals and
   former pedal positions against current visible geometry. Never derive
   expected hit targets from production geometry. Keep the separate dummy
   capture-failure case and tied-resize barrier case.

Use completed, acknowledged script prefixes for essential intermediate holds
when one rendered observation can skip a transition. Retain the complete journey
and exact command/state assertions. Do not enlarge timing windows to hide a miss.
Also retain MIDI-first/UI-last release coverage in the MIDI suite.

## Actual desktop journey

Inspect the current window and logical/drawable sizes before choosing coordinates.
Record a fresh application frame after each meaningful step. Use distinct notes
so pointer and keyboard ownership can be observed independently.

| Step | Required observation |
| --- | --- |
| Hold keyboard Upper C4; press and hold pointer Upper C2 | Both notes visibly held before navigation; successful continued pointer ownership |
| F5, F7, F6, F4 while held; resize across the reviewed branch | Both original owners remain; hidden controls cannot acquire new holds; no control or clock reset |
| Move outside while the original pointer press remains down, then release outside | Suppressed drag retains its original note until Up; afterward only keyboard C4 remains |
| Return without a button; move over another key; then freshly press/release it | Return/motion does not retrigger; a fresh press works and releases normally |
| Repeat branch crossing with a held pedal pointer | Moving the pedalboard preserves the original pedal owner until its release |
| Release keyboard; deliberately lose focus during a fresh UI hold | UI holds clear; returning cannot resurrect the old press |
| Close a separate ordinary launch through the actual window close control | Exit zero, no supervisor timeout/signal, stopped/unheld joined diagnostics |

An atomic drag's released endpoint cannot substitute for the intermediate held
observations. Record a tool limitation or unexecuted step if separate press/move/
release observations cannot be obtained.

For the ordinary-close case, launch from an actual desktop terminal with fresh
output paths; omit replay and smoke options:

```sh
SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=dummy \
  ../build-desktop/apps/standalone/hammond_standalone \
  --state "$PWD/out/desktop-ordinary.b3controls" \
  --diagnostics "$PWD/out/desktop-ordinary.json" --width 1672 --height 941
```

Create `out` first and confirm the state path is absent. Capture intermediate OS
frames separately: ordinary `--screenshot` captures its first eligible frame,
not this journey. Closing during an active replay intentionally fails replay;
test interruption separately from ordinary close. Synthetic MIDI overlap belongs
in the bounded replay cases unless an actual combined OS-input run is retained.

## Bounds and retained evidence

Current parsers admit 250–10000 ms, 64 KiB per script, 256 UI events or 2048 MIDI
events; MIDI lines allow 256 bytes. Times are nondecreasing and below duration.
UI coordinates allow −8192…16384; dimensions allow 960…8192 by 700…8192.
Replay drains for at most 2000 additional ms. Existing subprocess limits are
9 seconds for workspace/MIDI and 8 for boundary tests; CTest limits are
90/90/60/15 seconds for the four gates above. Fit selected fixtures within those
limits; a 10-second script cannot use a 9-second supervisor.

Retain source/tree and executable/dependency hashes, configuration, exact argv,
scripts/state bytes, driver identities, lossless desktop frames, elapsed time,
exit/timeout/signal status and diagnostics. Require final snapshot available,
`running_after_shutdown=false`, `held_after_shutdown=false`, positive callback
counts, finite samples and zero faults/overflows/rejected commands. Check replay
completion/delivery/final acknowledgment and untruncated observations separately.
Keep physical devices, DPI, accessibility and cabinet fidelity unqualified.

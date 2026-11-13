# Native standalone interaction workflows

[`test_standalone_workflows.py`](../apps/standalone/native_tests/test_standalone_workflows.py)
executes the real `hammond_standalone` with bounded `B3UIREPLAY1` files. The app
posts each event through its SDL queue, handles its ordinary keyboard/pointer/
modal paths, then observes the actual Session callback. This supplements the
[app smoke and CLI suite](STANDALONE_APP_ACCEPTANCE.md) and
[independent UI model tests](STANDALONE_UI_ACCEPTANCE.md).

## Maintained acceptance

| Workflow | Independent musical expectation |
| --- | --- |
| Empty replay | No injected smoke note, retained controls, no exit-time file write. |
| Target and octave | Upper MIDI 60 stays held while Lower MIDI 74 and pedal 17 are added; original releases remain correctly addressed; a fresh A uses Upper MIDI 72. |
| Focus loss and repeat | Release clears the note; repeats and duplicate downs remain suppressed until the original up; a fresh press plays once. |
| Audio by keyboard | Tab, Home/End and Return apply 96000 Hz / 128 frames; all four banks, pedal controls and other retained settings survive; notes clear and held-key suppression persists. |
| Help | Open releases notes; Return/Escape close; an unreleased physical key cannot retrigger. |
| Edit versus sounding | Edit A/B and focused drawbar navigation change only the intended stored bank; selecting Sounding B reconnects that route. |
| Cancel versus Panic | Cancel disables only the upper route with all three played parts still held; reselection reconnects; Panic clears all UI parts while retaining controls. |
| Save/Load | Explicit Ctrl+S writes independently declared canonical bytes for every bank and pedal; Ctrl+O restores them; a new process restores no held notes. |
| Resize | Actual 960x700 and 1600x1000 window/drawable sizes, retained drawbar focus and original computer-note ownership. |
| Pointer cleanup | A real pointer note command plus off-window move/up preserves the independent keyboard owner and leaves no held notes. Dummy capture rejection may release immediately. |
| CLI setup rejection | Combining replay with smoke exits 2; missing/malformed replay input exits 1; existing input, state and output sentinel bytes remain untouched. |

Expected pitches, control dictionaries and saved bytes are declared in the
Python suite. It imports neither production UI calculations nor an Engine or
serializer. Button coordinates name the actual default layout; keyboard focus
and resulting musical controls independently establish which control changed.
The three [user-runnable scripts](../examples/standalone-input/README.md) are
also exercised directly by the suite, without a separate generated catalog.

Replay diagnostics retain bounded, coherent musical observations before normal
shutdown cleanup. Held-state transitions must match the stated note identities;
accepted note-command counts establish mouse On/Off even when dummy capture
failure places both in one callback. Final sequence acknowledgment must cover
the submitted prefix. Tests require successful joined shutdown, positive actual
callback/frame counts and zero audio faults, rejected commands or recovery events.
These fixtures allow at most one redundant lifecycle cleanup command to be
discarded per successful device start; Session.stop already clears all owners.
Script acknowledgment and musical state remain strict before final cleanup.
Tests never require an exact callback count or deadline latency.

Resize observations are sampled after event handling and may coalesce a focused
edit and its later key-up. Each observed complete control/held state must match
its acknowledged literal command prefix, with monotonically advancing sequence
numbers. Two ordinary completions at each size separately prove the fully edited
controls with the original Upper MIDI 60 still held, then the same controls after
its release. The held script ends at 1100 ms and the released script retains its
1600 ms endpoint; neither imposes a guarantee of observing every intermediate
UI state. Exact On/Off counts and unchanged saved bytes remain required.

## Execute

After configuring an optional native build with testing enabled:

```sh
cmake --build build-native --target hammond_standalone_test_inputs --parallel 3
ctest --test-dir build-native --output-on-failure --no-tests=error \
  -R '^test_standalone_workflows$'
```

The direct command is useful with any already built native executable:

```sh
HAMMOND_STANDALONE_EXECUTABLE=/absolute/path/to/hammond_standalone \
  python3 apps/standalone/native_tests/test_standalone_workflows.py
```

The environment variable is required; a missing/nonexecutable binary fails
instead of skipping. Every subprocess explicitly sets both SDL drivers to
`dummy`, runs in its own private temporary directory, and names private input,
state and diagnostics paths. Each initial state is a literal valid control
document. Subprocess timeout is 9 seconds; the CTest suite timeout is 90 seconds.
State bytes are compared after every run, and unexpected files fail the suite.

## Evidence and limits

The observed Linux Release run passed **11 methods / 15 real subprocesses**;
the registered CTest gate passed **1/1 in 22.91 seconds**. Exact binary/source
identities and the initial lifecycle-oracle correction are recorded in
[assignment 28](development/2026-11-13-next-phases/28-native-workflows.md).
The later [timing repair](reviews/STANDALONE_TIMING_REPAIR.md) retains the
instrumented counterexample to the old resize assertion. Its clean ASan/UBSan
workflow execution passed **11 methods / 17 real subprocesses** in 28.32 seconds,
as part of a separate 3/3 focused gate. The two added held-endpoint processes
strengthen ownership evidence while permitting valid coalesced observations.
That focused result does not replace a later combined-source full gate.
The [replay input layer](STANDALONE_INPUT_REPLAY.md) has separate parser/SDL-queue acceptance. Queue
delivery and callback acknowledgment are different boundaries; neither one
alone proves the intended musical workflow.

These are SDL dummy-backend software results. The pointer case covers cleanup
when capture fails or an off-window up reaches the app; it does not qualify
OS capture on a real desktop. Physical devices, hotplug, callback deadlines,
high-DPI coordinates, assistive technology and acoustic fidelity remain separate
gates. The test introduces no sound model, parameter, saved-state or plugin
identity change. See [standalone scope](STANDALONE_SCOPE.md).

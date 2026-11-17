# Replay UI history: independent admission

Reviewer A20, `/root/w04_a20`, wave 4 of the heading/title continuation.
Reviewed 16–17 November 2026 against base
`113c29b7b14c8fde0859bc405ef8e4141a131ea6` (base tree
`163e4d7ff687acafa63813c73fdbc303a839a8f6`). This admits the bounded replay
diagnostic correction at the source identities below. No production correction
was required by this review. It does not claim executed coverage of the
512-entry boundary or complete product qualification.

## Retained failure and purpose

The [original baseline run](../development/2026-11-16-heading-title-continuation/reports/baseline-ctest.log)
failed the all-eleven-focus assertion while preserving final MIDI configuration;
the isolated repeat passed on the same executable. A15's
[three immediate-batch observations](../development/2026-11-16-heading-title-continuation/reports/a15-baseline-batched.json)
retain the stronger deterministic input: opening, ten Tabs, and Escape all at
timestamp zero. All three healthy replays lacked MIDI focus values in the
acknowledged musical history. The report preserves its original harness,
executable, input and reproduction command. These failures remain separate from
candidate passes.

`initialize()` may observe preparation before the queued startup restore is
acknowledged. The event loop can then consume several UI actions before its next
Session observation. Retaining overlay/focus transitions before the existing
musical guard addresses this observation loss without admitting an unrestored
musical snapshot. These transitions are main-thread UI facts; they do not
establish painted frames or audio acknowledgment.

## Source admission

| Reviewed property | Finding and boundary |
| --- | --- |
| Reservation and ownership | `initialize()` reserves at least 512 `ReplayUiObservation` slots only when `--input-script` is present. Entries contain an elapsed counter, overlay enum and focus index. Recording and JSON output remain on the application thread. `reserve(512)` does not promise an allocator's exact byte footprint. |
| Normal operation and MIDI-only replay | No UI-history reservation or recording occurs without an input script. The MIDI-only path returns immediately from the new helper and retains its previous JSON shape. The only normal-path additions are empty object members and the false conditional check in pointer handling; sound state and action dispatch are unchanged. |
| Deduplication | The previous `(overlay, modal_focus)` pair is compared before checking capacity. Unchanged observations consume no entry, including repeated observations at capacity. Nonadjacent revisits remain ordered entries. |
| Exact boundary, source-reviewed | With 511 entries, one changed pair is appended as entry 512. At size 512, a new pair produces one capacity error, sets the sticky truncation and fatal flags, stops `running_`, and returns before appending. Later attempts cannot emit the capacity error twice or append entry 513. This branch has not been executed by A20. |
| Failure propagation | The existing success predicate requires zero errors and no fatal failure. Completion also requires `running_`; the new stop therefore cannot become a successful replay. Final exit status is nonzero for fatal failure. The explicit `ui_observations_truncated` field exposes the retained prefix. An additional direct flag check in the success predicate is not required for the current control flow. |
| Pointer opening | The new observation after pointer-down retains a header-opened dialog before another event can move focus. A modal pointer activation may invoke both the old recorder and the new tail call; identical adjacent pairs are deduplicated. |
| Musical observations | The original body beginning with the preparation/restoration guard is byte-identical to the base. Its snapshot availability, running, startup sequence, state/calibration deduplication, capacity and appended fields retain their meanings. `replay_acknowledged()` and final musical acknowledgment remain unchanged. |
| Audio and compatibility | Both `AudioDevice` files, both `Session` files, both `ScriptedInput` files, both `Engine` files, both `ControlStateIO` files and both `StateExchange` files match the base byte-for-byte. No callback code, scheduler, controls format or nominal dry Engine route changes in this patch. This is source preservation, not a fresh callback resource or deadline measurement. |

The three additive UI-replay members retain strict types:
`ui_observation_capacity` is an integer, `ui_observations_truncated` is a
Boolean, and `ui_observations` is an array of exact objects containing integer
`elapsed_ms`, string `overlay`, and integer `modal_focus`. The shared
`ArraySchema` validator uses exact types, so a Boolean cannot satisfy an integer
field. Root's shared `UI_REPLAY_SCHEMA` update requires the exact new fields;
it does not loosen other keys or replace the validator.

## Regression admission and executed coverage

A15 retained the exact eleven-control set and added an ordered `0..10` assertion
for both keyboard and pointer openings. Both inputs put all 24 events at zero;
there are no sleeps or elapsed-time pass thresholds. The same test requires a
final closed modal and checks every musical observation for acknowledged startup
sequences, literal audition manual/pedal drawbars, and empty held-note sets.
Existing delivered/completed/final-acknowledged assertions remain in the common
harness.

A20 adds
`test_modal_maximum_script_preserves_ui_transitions_and_deduplicates` and an
adjacent-pair deduplication assertion for every successful modal case. The new
method uses the full admitted 256-event input budget in two native processes:

| Case | Timestamp-zero source | Exact retained history |
| --- | --- | --- |
| Changing states | Ctrl+M key-down, 254 ordinary Tab key-downs, Escape key-down | 255 MIDI entries with focus `index % 11`, followed by closed overlay at focus 1: exactly 256 entries. Nonadjacent focus revisits are retained. |
| Unchanged states | Ctrl+M key-down, 254 ignored Ctrl+Tab key-downs, Escape key-down | MIDI focus 0, then closed overlay at focus 0: exactly two entries. |

Only navigation keys are used; neither case presses a playing note. The normal
harness still checks actual delivery, final acknowledgment, healthy callback
counters, zero audio faults, shutdown quiescence and absence of saved controls.
Both scripts are 5,661 bytes, have duration 600 ms, and use no event-time
separation. The finite duration is ordinary replay completion, not an inference
about when audio becomes ready.

**Executed A20 result:** one unittest passed in **1.448 s**, two actual native
processes, two successful UI replays, zero enumeration errors and zero expected
failed replays. Python AST parsing passed with **23 test methods**; scoped
`git diff --check` passed.

The script format itself admits at most 256 events. Its unmodified parser rejects
event 257. Therefore this script-only dummy-SDL fixture cannot supply 512 changed
pairs followed by a 513th changed pair. A20 did not weaken the parser, add a
production seam, inject asynchronous live events or infer overflow from timing.
**The 512-accepted/513th-refused runtime boundary remains unexecuted.** A future
separately assigned deterministic native fixture could exercise that private
recorder boundary; the present admission covers its inspected control flow and
the maximum reachable scripted regression.

Root's earlier [focused run](../development/2026-11-16-heading-title-continuation/reports/replay-focused.log)
passed the 22-method application CLI suite, expression diagnostics and native
MIDI replay. That same retained run failed calibration because the separately
built probe still lacked the three new fields. The
[rebuilt-probe run](../development/2026-11-16-heading-title-continuation/reports/t2-fixture-and-calibration-tests-complete.log)
then passed calibration in 20.70 s. The stale-probe failure remains recorded;
neither observation is an A20 full-suite execution or qualification of the
new 23-method file.

## Frozen identities and reproduction

Sole writable checkout/cwd:
`/workspace/scratch/5a28c3564dbf/Hammond-B3-Organ`.
The tested executable is root's existing
`../build-native/apps/standalone/hammond_standalone`. Cache inspection records
Release, standalone/testing ON, MIDI/VST3 OFF, `/usr/bin/c++`, GNU Make, and
read-only SDL source `/workspace/scratch/3edffb787db3/SDL2`. The local compiler is
GCC 14.2.0 and Python is 3.12.14. No build, configure, full CTest, commit or push
was run by A20.

| Input | SHA-256 |
| --- | --- |
| Reviewed `main.cpp` | `89b24fdeae438b77309904d12c32e3e2ae5e964e99968a8656c5b0a710e237c4` |
| A20 `test_standalone_midi_cli.py` | `37ecb6bd48017cee656629e3cac51bc5fa3a1979f1bc2c58d8228113debdf18f` |
| Shared `test_standalone_midi_replay.py` schema | `fa2e957bc49fc104aaba2b9a16cc671549018a133157841ad3f58d7362602fcf` |
| Shared `test_standalone_app.py` validator | `5514d229bb969feeedd1be060d7e64dbd63cff22a08f0a70bd313d6308ae7236` |
| Tested native executable | `e44eefc4fe37c879d2145e085f46f914f1703331aa32c72343f28a53d81eb56a` |
| Changing-state script | `b53ac82d55d887060e948940ab0f9fd3fa00f80cf591981964487172254a2f2c` |
| Unchanged-state script | `eeb496f81bbc68bb0452352533e0785ccc477fadd8edd07eaf25ee3317c5ee1d` |
| `ScriptedInput.h` | `294b11d6a2c9b425d766b019b2ff1e7c460a308c93887c648dd7bce1d955c3d5` |
| `ScriptedInput.cpp` | `a023e8a0a900f1cd7000d532c511d5593d11507eeb997300ff2bd3325c13cc23` |
| Original A15 batched report | `8092ca48c4502c49702fc9c12c380d86e12c0a7153f329454d29b0856994df55` |

Exact scoped native command executed from the cwd above:

```sh
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5a28c3564dbf/build-native/apps/standalone/hammond_standalone PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=apps/standalone/native_tests python3 -B -m unittest -v test_standalone_midi_cli.NativeMidiAcceptance.test_modal_maximum_script_preserves_ui_transitions_and_deduplicates
```

The harness explicitly supplies `SDL_VIDEODRIVER=dummy` and
`SDL_AUDIODRIVER=dummy` to each child. To repeat the syntax check:

```sh
python3 -B - <<'PY'
import ast
from pathlib import Path
p = Path('apps/standalone/native_tests/test_standalone_midi_cli.py')
tree = ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
names = [node.name for node in ast.walk(tree)
         if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
print({'ast_parse': 'passed', 'test_methods': len(names)})
PY
git diff --check -- apps/standalone/native_tests/test_standalone_midi_cli.py docs/reviews/REPLAY_UI_HISTORY_ADMISSION.md docs/development/2026-11-16-heading-title-continuation/notes/A20.md
```

The source-preservation check used `git show <base>:<path>` and compared those
bytes with each of the twelve protected files named above. It also compared the
suffix of `record_replay_observation()` between the unchanged preparation-guard
comment and `static void write_replay_snapshot(`; that exact extracted suffix
hash is `43a0234454ff6204fca949cbabeaf0e92089b156062fb84059252d734ed4b4be`.

## Handoff and limits

Root receives the 23-method harness and runs its complete affected application
suite after handback; coherent full verification, source-specific publication
and hosted results remain root-owned. This review supplies no physical MIDI or
audio-device journey, callback retirement/deadline proof, allocation-instrumented
measurement, painted-frame guarantee, native accessibility result, or
whole-interface 1:1 acceptance. All original plan and release gates remain.

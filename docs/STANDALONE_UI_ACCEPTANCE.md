# Standalone UI acceptance

The maintained SDK-free target
[`test_standalone_ui`](../apps/standalone/tests/test_standalone_ui.cpp) exercises
the actual [`UiModel.cpp`](../apps/standalone/UiModel.cpp) through public input,
action, submission and observation APIs. It qualifies the behavior in
[`STANDALONE_UI.md`](STANDALONE_UI.md), independently of the renderer.

## Retained acceptance scenarios

| Scenario | Evidence and failure boundary |
| --- | --- |
| Permanent controls and bank separation | Explicit literal IDs cover all 45 descriptors, including registry holes and all 36 manual drawbars. Distinct retained changes in Upper A/B and Lower A/B preserve sounding selectors; Cancel and reselect preserve bank positions. Malformed semantic IDs reject without mutation. |
| Physical keyboard capture | An independent literal 17-key table checks each emitted MIDI/pedal value and owner for Upper, Lower and Pedals. Actual Session holds preserve the original manual/pitch after target, octave and focus changes. Repeats, duplicate/orphan Down, modifiers, text entry, unmatched Up and both range endpoints are checked. |
| Pointer, audition and release scope | Actual Session/Engine ownership preserves a keyboard hold after pointer capture loss. Glissando checks exact Off/On ordering across both manuals and both directions across the pedal namespace; outside movement releases, re-entry plays, buttons do not activate during glissando, and outside Up uses the captured note after resize. Space releases its original audition after focus movement. Focus loss releases UI channel 0 while other-channel manual/pedal owners survive; Panic clears them and retains controls. Cancel leaves actual held keys and pedals intact. |
| Parameter gestures and laws | Pointer half-step quantization follows the existing higher-step rule. Changing edit bank and valid resize close the captured drag; rejected resize preserves it. Integer drawbar steps, saturation, expression 0.05/Shift-0.01 steps, endpoints, nonfinite movement rejection, pedals and all four percussion toggles execute. |
| Pending, saved and recovered state | Real accepted sequence acknowledgments retain newer pending edits. Late save completion acknowledges its exact snapshot; valid load preserves edit bank and held notes, invalid load/save/observation preserves state. Actual queue overflow clears held input and rolls back desired controls to the published copy; keys/pointer stay suppressed until release. Actual InvalidCommand requests one scoped cleanup without repeated requests. |
| Layout and hit boundaries | Complete literal natural/accidental pitch inventories cover all 61 Upper + 61 Lower + 25 pedal keys. Every key is bounded and hittable; black-over-white precedence, half-open edges, adjacent white-key seams and outside edges are checked. All 45 visible controls and 18 visible manual drawbars are checked. |
| Focus and app requests | All 45 controls and three roving keyboard groups are reachable by Tab. Reverse traversal retains roving positions; semitone/octave/Home/End navigation clamps without playing. Text entry suppresses navigation. Save, Load, Audio Settings and Help are typed app requests; Escape/window closing emit scoped UI release. |

## Geometry matrix and execution

Valid sizes are **960×700**, **1280×900**, **1920×1080**, **1119×819**,
**1120×820** and **8192×8192**. These include the minimum, reference, large
window, both layout breakpoints and maximum dimensions. Smaller, negative,
zero, too-large and nonfinite dimensions, and an invalid edited bank, preserve
the entire existing layout. Explicit zero/negative-extent rectangles are empty.

From the repository root, using CMake 3.21+ and the ordinary C++20 toolchain:

```sh
cmake -S . -B ../build-ui-tests -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build ../build-ui-tests --target test_standalone_ui --parallel 3
ctest --test-dir ../build-ui-tests -R '^test_standalone_ui$' -C Release --output-on-failure --no-tests=error
```

Assignment 17 executed these steps with GCC 14.2.0 and CMake 4.4.4:
**1/1 CTest suite passed, seven behavioral scenarios, 0.01 seconds**.
The [assignment note](development/2026-11-13-next-phases/17-ui-acceptance.md)
retains the actual tool path and source identities. No production fix was needed.

This is a focused live-tree engineering result. It does not qualify SDL event
translation, actual application dispatch/rendering, native accessibility,
audio-device timing, platform packaging or physical instrument fidelity.
The integrator must rerun the target from its coherent accepted source snapshot.

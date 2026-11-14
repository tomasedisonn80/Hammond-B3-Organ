# Native preset renderer implementation

Assignment **A23**, `/root/w04_a23_reference_renderer`, 2026-11-14. This is an
implementation and author visual review under the frozen
[preset UI contract](../PRESET_UI_DESIGN.md). Independent UI acceptance, the
later visual refinement and the published gallery remain separate assignments.

## References and implemented behavior

Before editing, visually inspected both the exact atlas cover/page-409 JPEG
`docs/design/atlas-cover-reference.jpg` and the historical native capture
`examples/demos/standalone-midi-ui-v1/images/reference-1672x941.png`. Their
SHA-256 identities remain, respectively,
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` and
`239a38c6f47079e442c4ecb0c62c8e38c81d032153be93d892bc854966835fc7`.
Also read the repository instructions, project plan, relevant atlas review,
frozen selection/core/UI contracts and A18's Session/UI-model handoff.

Only `apps/standalone/InstrumentView.cpp` changes executable source in this
assignment. `UiModel`, its palette/header, `Session`, Engine, `main.cpp`, asset
crops and parameter/state identities are unchanged by A23. Help is implemented
in `InstrumentView.cpp`, so no `main.cpp` edit was necessary.

| Area | Actual renderer change |
|---|---|
| Preset geometry | Consume the model's 24 `PresetKey` controls and `preset_key_panels`; paint seven dark naturals before five ivory accidentals for each manual. Both cheeks paint at every admitted height. Remove the old cheek key-count annotation and visible PLAY/CANCEL button assumptions. |
| Applied selection | Derive each manual's effective selection from `view.applied.controls` through `control_preset_selection`. A routed key has a slight face recess and warm top accent. C never receives a latched/depressed treatment. |
| Pending request | Keep the applied key selected; when a different desired effective selection is pending, outline only that desired key in thin amber and show `PRESET UPPER/LOWER … PENDING` in the footer. C may have this request outline. |
| Focus | Paint a separate dark/light outline last, with the contracted inset-2 accidental bounds and exposed lower 0.38 natural region. Preserve labels through the raster-driven refinement below. |
| Captions | Show edited bank independently from applied `SOUNDING FIXED C#`, `SOUNDING A#`, `SOUNDING B` or `CANCELLED`. Use measured fitting and a compact fallback only below the minimum full-caption fit; focused preset status retains the full description. |
| Percussion | Eligibility requires enabled Upper route, fixed mode `None`, and retained bank B. Stored tablet values remain visible while `REQUIRES UPPER B` explains ineligibility. |
| Help | Explain 61 playing keys plus twelve presets per manual, 25 pedals, C Cancel, fixed C#–A, adjustable A#/B, independent EDIT A/B, preset navigation and activation, and retained note ownership. |

The material pass neutralizes the olive cast of the panels and adds restrained
procedural charcoal grain, darker sockets, raised tablet/cap faces, contained
two-unit right/three-unit down tablet shadows and three-to-five-unit tablet
fronts. Drawbar stems are 3.5 units with a narrow metallic highlight; cap fronts
and under-cap shadows are deeper. Playing-key fronts use
`clamp(0.16 * height, 6, 16)`, with stronger fallboard shadows and accidental
side bevels. Existing wood and cabinet crops retain their exact provenance.
No source-art control surface, false rotary/scanner/microphone control, new
playing-key geometry, or new note owner is introduced.

### Raster-driven focus correction

The first actual 960×700 and 1672×941 frames exposed a defect: a full inset-2
two-tone focus stroke erased the C# letter on the narrow accidental. The final
focus pass gives the **original label rectangle and material** foreground
priority, using a temporary SDL clip which preserves the caller's clip. This
creates a small cosmetic opening through the stroke under the label; the
contracted focus bounds, hit region, label bounds and semantic identity stay
unchanged. The final frames and enlarged inspection crops show the restored
pitch text. This does not make the small keys large targets: at the minimum
width, nominal 9-unit two-character labels fit to roughly 6.2–7.1 units with
the existing font. Independent legibility/accessibility acceptance stays open.

## Executed build and captures

The observed committed base was
`35554c068492fe2b20c1f8a602d8354ae762dc42`; it alone does not identify the
uncommitted preset implementation. Copied 1,241 current files into
`/tmp/hammond-preset-a23/source` before building. After the focus correction,
updated only the owned renderer in that copy and rebuilt it against the same
copied headers/libraries. Preserved the first source/captures/executable under
`source-initial`, `captures-initial` and `initial-hammond_standalone`; no earlier
baseline build was reconfigured or rebuilt. A final comparison of 66 native
source/header files found **zero differences** from the live checkout.

Toolchain: GNU C++ 14.2.0, CMake 4.4.4, Release/C++20, with the repository's
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
SDL 2.32.10 is the verified pinned checkout at commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. MIDI was disabled; ALSA was disabled
because this local runner has no ALSA headers. No Clang executable was found on
PATH, so this record makes no local Clang execution claim.

Executed from `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`:

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S /tmp/hammond-preset-a23/source -B /tmp/hammond-preset-a23/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 -DSDL_ALSA=OFF
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a23/build --target hammond_standalone --parallel 3
```

Configure and strict build passed. Five final native processes then ran explicit
600 ms `B3UIREPLAY1` scripts with `SDL_VIDEODRIVER=dummy`,
`SDL_AUDIODRIVER=dummy`, and `SDL_RENDER_DRIVER=software`. Every process exited
0, delivered all events, wrote its requested frame and reported
`replay.passed=true`. The three fixed-focus frames captured independently held
Upper MIDI notes 60 and 64; the Cancel and Help runs create no playing note.
These are actual application pixels, not source art or a mock renderer. BMP to
PNG conversion was checked for identical decoded RGB bytes.

The common `visual-review.b3controls` loads Upper fixed C#, Lower adjustable
A#, stored percussion On and deliberately varied retained banks for inspection.
Those display banks are a visual fixture, not a claimed factory registration.
The exact scripts, state, command argument arrays, logs, diagnostics and images
are retained under `/tmp/hammond-preset-a23/captures`; the manifest below
records the commands. A representative actual command was:

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy SDL_RENDER_DRIVER=software \
  /tmp/hammond-preset-a23/build/apps/standalone/hammond_standalone \
  --width 1672 --height 941 \
  --state /tmp/hammond-preset-a23/captures/visual-review.b3controls \
  --input-script /tmp/hammond-preset-a23/captures/fixed-focus-1672x941.b3uireplay \
  --screenshot /tmp/hammond-preset-a23/captures/fixed-focus-1672x941.bmp \
  --diagnostics /tmp/hammond-preset-a23/captures/fixed-focus-1672x941.json
```

| Final local artifact | SHA-256 |
|---|---|
| `source-manifest.json` | `542bb5016a032791dc629a6b3e1cfd4e25c3531dea8f4a124743149fed8ea419` |
| `source/apps/standalone/InstrumentView.cpp` | `23e8a2421dbec36dd96b0cbc0839612bab236b2b17ee6ead733327eaa9f453cb` |
| `build/apps/standalone/hammond_standalone` | `c06d6f77b07efc9f30ec4644de123d7a9714029b1ce3ffe26091f79710ee2bd0` |
| `capture-manifest.json` | `99d09859240ab1fa367de270fb9f3124052010bd40fced1ecfdc5145def3bb9b` |
| `captures/fixed-focus-1672x941.png` | `e80aecbd0a745cf1774fe5d0507bf4b558e912b52e8a4ccbadbaf8f966fded6f` |
| `captures/fixed-focus-1280x900.png` | `d97bca176513a14b02479883f41677b1f09b0a1a9c77a92f2847850ac8274fcb` |
| `captures/fixed-focus-960x700.png` | `133b85c37338fe3865a79b434b72c5d044b8428575f75afde373335e9a2c87a9` |
| `captures/cancel-1672x941.png` | `a85e0fa81654e5e3a6e67d4d9ac68ba55aa786c5085534f995e1c50049a75ca8` |
| `captures/help-960x700.png` | `400ad52e85e49ed936ff74b9b161f8452525c65901e5666a0ae60c0921404f6a` |

All five sizes/states were visually inspected during the work; the final
minimum/reference frames and four-times nearest-neighbor rail inspection
crops were inspected after the focus repair. The crops are QA derivatives,
not separate native window sizes. `git diff --check` on the owned source passed.

## Comparison and handoff

The walnut surround, exact cabinet decoration and neutral charcoal treatment
are closer to the source. **Literal 1:1 matching has not passed.** The source
still has substantially taller physical keybeds, perspective key fronts,
denser raised caps/tablets, larger readable main labels, and different
rack/header proportions. Rectangular live key geometry, permanent pedals,
the keyboard toolbar, working utility actions, factual device status and the
absence of unimplemented rotary/scanner controls remain visible differences.

A25 receives the final captures for independent model/raster acceptance,
including this focus-label refinement. Responsive boundary captures, pending
and rejected-state raster cases, all-key independent behavior and native
accessibility are not claimed by these five author runs. The copied `main.cpp`
still has the pre-A28 diagnostics schema, so these diagnostics are not presented
as a complete fixed-field/47-parameter report. No old native Python gate was
run against that known incomplete schema. A38 owns further targeted visual
refinement; the integrator and gallery owners retain final capture publication,
README/status/runbook changes and coherent combined-source gates. No commit,
push, physical device test, callback deadline pass or fidelity claim is made by
this assignment.

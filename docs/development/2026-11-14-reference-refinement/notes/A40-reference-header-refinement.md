# A40 — Wide reference header refinement

Actual worker `/root/w07_a40_reference_header_refinement`, wave 7. Owned only
`InstrumentView.cpp::paint_header`, additive material acceptance checks, this
note and `reports/A40-*`. Read AGENTS, current scope/checkpoint, full M0–M9 plan,
layout/material contracts and A36's original-image review. Coordinated directly
with A36/A41; root authorized the narrow typography exception and recorded its
material-contract addendum. No child dispatch, shared documentation, model/audio,
assets, CMake, workflow, `build-native`, commit or publication operation.

## Result

Only `sidebar_pedals && Dimensional` uses Serif 42.75 at `header.y−4.5`, retaining
the existing symmetric title allowance and fit. Exact **NOMINAL DRY ORGAN** uses
the existing Sans atlas/brass color at 17, with bounded spacing toward 374 pixels
of total advance. The allowance is centered and ends at least ten pixels before
Flat; it reduces spacing, then size if required. Seventeen fixed string-view
draws add no allocated text buffer. All other header branches retain their
original calculations. No control/hit/focus geometry, 47 parameters, state,
61+61+25 keys or 24 presets changed.

Actual native captures at 1672×941 and 1400×820 passed the existing 66-event
endpoint validator: four held owners, live retained-drawbar edit, acknowledged
copied state and joined shutdown. PNG encoding preserves every BMP RGBA pixel.
I inspected both full native images; the two lines fit clearly at both sizes.
The original v3 gallery remains unchanged.

At reference size, A36's fixed warm mask gives these half-open bounds:

| Ink | Original reference | Native v3 | Candidate |
|---|---|---|---|
| Title | `[603,20,1067,53]` | `[617,28,1051,59]` | `[602,20,1065,53]` |
| Subtitle/caption | `[650,71,1021,83]` | `[769,93,888,100]` | `[650,71,1020,83]` |

Title width error falls 30→1 pixels and top error 8→0. Caption width error falls
252→1 and top error 22→0. Title ink remains 1.5 pixels left of the reference
center; text shape, subtitle wording and broader interface differences remain.
**Literal 1:1 equality is not claimed.**

## Executed verification and identities

The unchanged baseline passed **901/901** material assertions. The candidate
passes **1,071/1,071**, retaining all 901 and adding 170 checks over 24 complete
headers plus eight cut clips: both sizes, all three workspaces and scales
1/1.25/1.5/2. Tests inspect native ink size/top/center, all fifteen distinct
caption letters, control separation, the Flat margin and caller clip/viewport
preservation. Existing surface/status/overlay results remain identical.

All six drawing, quad, material, scaled-view, workspace and preset raster CTests
passed in **44.66 seconds**, with `--no-tests=error`. No failed build, test or
runtime result preceded this pass. `git diff --check` passes. Only the header
function differs in the production translation unit; UiModel, Drawing and font
bytes remain unchanged. A41 owns independent full-pixel preservation, common
focus and paired timing acceptance; those are not inferred from these tests.

| Source | Before SHA-256 | Candidate SHA-256 |
|---|---|---|
| InstrumentView | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` | `f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a` |
| Material test | `cc00920fa567460999821d9118d3b8c752b9df22be83d63969dd810f5273b252` | `66963058652bd0673a043e03f342c94d71fd3c07e2f37a0d1d94093cc4d4a134` |

Base HEAD advanced separately from `2e161dc` to published `f9c11a4`; root excluded
these candidate source edits. GCC 14.2 Release, pinned SDL 2.32.10, MIDI ON,
VST3 OFF and shared `build-desktop` supplied the app/tests. The candidate app hash
is `01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f`.
The [report](../reports/A40-reference-header-refinement.json) retains commands,
configuration, unchanged sources and raw-result identities; the native-capture
script records its exact invocation and preserves v3. No clean-build, physical
device/display/DPI, accessibility or audio-deadline qualification follows.

Source and desktop operations are frozen/released to A41. Next: accept its
independent differential/timing result, then root publishes this source and
captures the next gallery before updating README.

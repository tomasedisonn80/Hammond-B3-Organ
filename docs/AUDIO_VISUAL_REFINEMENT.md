# Audio-continuation UI evidence and percussion refinement

The wide Dimensional Play interface now groups percussion as **PERC, VOL,
DECAY, HARM**, with live switch values inside ivory tablet bodies and separate
legends below. Actual native application captures verify the eligible Upper B,
fixed-registration and cancelled-route states. The original 1672×941 reference
remains the design target; the user's literal whole-interface **1:1 requirement
is unmet and unwaived**. This is a scoped, hash-bound implementation and capture
record, not complete product-fidelity acceptance.

The source design and invariants are defined by the
[frozen percussion contract](PERCUSSION_REFERENCE_CONTRACT.md), based on atlas
pp. 409–418, 431 and 435 and the unchanged
[cover/page-409 image](design/atlas-cover-reference.jpg). Its reference SHA-256 is
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.

## Body, typography and responsive layout

The refinement is active only in **Play + Dimensional at logical width ≥1400 and
height ≥820**. It reuses the existing tablet material and two-unit cyan focus
outline. The complete outer bezel is also the hit/focus rectangle; the ivory face
is inset by the material painter. Captions and gaps are not larger invisible
targets. Enabled PERC alone receives the selected amber material.

| Visual slot | Stable semantic index | Parameter | Exterior legend | Live value domain |
| --- | ---: | --- | --- | --- |
| 1 | 0 | `0x3000` | PERC | ON / OFF |
| 2 | 2 | `0x3002` | VOL | NORM / SOFT |
| 3 | 3 | `0x3003` | DECAY | SLOW / FAST |
| 4 | 1 | `0x3001` | HARM | 2ND / 3RD |

The visual order `[0,2,3,1]` does not change parameter identities. The reference
image's NORM under DECAY and FAST under HARM are incorrect domains; the live
controls retain the correct musical meanings above. Values use fitted Serif at
requested size 17, with dark opaque ink; exterior legends use fitted Serif at
10.5. The material contains no baked control text. The frozen contract describes
the exact sizing arithmetic and independent anchor tolerances.

| Logical window | Outer body width × height | Left edges, PERC / VOL / DECAY / HARM | Body top |
| --- | --- | --- | ---: |
| 1400×820 | 61.8141 × 47.4 | 137.7182 / 214.5682 / 282.2296 / 349.8910 | 150 |
| 1672×941 | 73.9615 × 48 | 164.6477 / 256.5998 / 337.5577 / 418.5156 | 150 |
| 1920×1080 | 86.0690 × 48 | 179.9352 / 286.9399 / 381.1506 / 475.3612 | 150 |

These are logical geometry anchors, not measurements of physical hardware. The
outer widths scale within the existing percussion subsection, preserving the
larger PERC-to-VOL gap and tighter later gaps. On the shorter active strip, a
combined heading reports route eligibility. At performance height ≥104, a
separate small line reads UPPER B ROUTE ACTIVE or REQUIRES UPPER B. At compact
sizes, in Flat, and in hidden Rotary/Service percussion bodies, the prior layout
and order `[0,1,2,3]` remain. Independent geometry and input evidence is identified
below; the three new app frames themselves cover 1672×941 and 1400×820 at 1×.

The existing 47 parameters, 68 ordinary controls, 147 playing keys, state formats,
drawbar banks, reversed preset controls and note ownership remain contract
invariants. This refinement does not connect scanner, AO-28 or Leslie audio.
The cabinet picture is retained reference art within the actual application,
and its status continues to say that rotary audio is not connected.

## Actual application gallery and state provenance

The [original eight-view gallery](../examples/demos/standalone-audio-preview-v1/README.md)
contains reference/default/minimum Play, reference/minimum Service and Rotary,
and minimum Flat. A28 independently read and hashed every retained manifest
file, re-decoded all eight PNGs and reran their retained diagnostic validator.
All **39 original manifest files**, eight recorded pixel identities and eight
full recorded state validations matched. The original capture inputs and receipt
bytes were preserved. This verifies their retained identities; it does not
independently attest the compiler invocation or make the capture author the
independent judge of full visual fidelity.

The [three added percussion states](../examples/demos/standalone-audio-preview-v1/percussion-states/README.md)
were recorded by running the actual frozen standalone with the real SDL event
pipeline. The input file starts with adjustable Upper B and percussion ON; route
and value changes then occur through keyboard navigation and activation.

| Actual screenshot | Applied route and live values | Visible semantic focus |
| --- | --- | --- |
| [Upper B, 1672×941](../examples/demos/standalone-audio-preview-v1/percussion-states/images/eligible-upper-b.png) | Enabled adjustable B; ON / SOFT / FAST / 3RD; separate UPPER B ROUTE ACTIVE line | HARM; 472 cyan focus pixels in `(418,150)`–`(492,198)` |
| [Fixed D, 1400×820](../examples/demos/standalone-audio-preview-v1/percussion-states/images/fixed-d-off.png) | Fixed D with remembered B; OFF / NORM / SLOW / 2ND; REQUIRES UPPER B | PERC; 420 cyan focus pixels in `(137,150)`–`(199,197)` |
| [Cancel, 1400×820](../examples/demos/standalone-audio-preview-v1/percussion-states/images/cancel-stored-on.png) | Disabled Upper route with remembered B; stored ON / SOFT / FAST / 3RD; REQUIRES UPPER B | DECAY; 420 cyan focus pixels in `(282,150)`–`(344,197)` |

All three original images and the reference JPEG were inspected directly. The
replays represent both values in every changed switch domain. In each case,
desired controls and the copied applied snapshot match completely, with two
Upper notes, one Lower note and one pedal held. The final screenshot is the
recorded current, acknowledged final paint. The application reports no queue,
rejected-command, render, nonfinite or overrange failures, and releases held
owners during joined shutdown. Exact counters and snapshots are retained in
[capture provenance](../examples/demos/standalone-audio-preview-v1/percussion-states/provenance.json)
and [A28's verification report](development/2026-11-15-audio-continuation/reports/A28-gallery.json).

Eligibility is independent of the stored ON/OFF switch. The applied Upper route
must be enabled, adjustable rather than fixed, and using bank B. The Cancel frame
therefore correctly retains amber ON while reporting REQUIRES UPPER B. The
cyan focus evidence combines the actual replay target, observed cap outline and
footer description; normal semantic focus IDs are not present in the native
diagnostic schema. These captures do not claim such an ID was directly logged.

## Source binding and reproducibility

The original and added captures share this frozen executable SHA-256:

`32cea4a90bfc3d742550ad3725c1bf007c2fdc72e111b8b5ab1e95026033daf6`

A28 verified all 115 recorded production inputs, 13 build inputs and 16 source
entries in the [earlier build receipt](development/2026-11-15-audio-continuation/reports/w03-source.json).
The central UI sources are:

| Source | SHA-256 |
| --- | --- |
| `apps/standalone/UiModel.cpp` | `aa4fa2e06c4a8ccb17ba1b1cdfed498372b3626152bb2b8c6c53682b775931c9` |
| `apps/standalone/InstrumentView.cpp` | `97971753c23e7da93d84586cf66ede2a3d9a04f319ddaf4831ba83ea7955f7d6` |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |

At capture, HEAD was `276664ee8570c208bb007cca59f496963ca13ef5` and its committed
tree was `295abfec00bdd874b89eea159f816400f994f7b6`. The implementation existed in
an uncommitted overlay. **The base commit does not identify this implementation.**
The exact file and executable hashes bind this evidence. A later integrator
publication must separately verify that its committed production files match
these hashes, retaining the original receipts and timestamps.

The [capture README](../examples/demos/standalone-audio-preview-v1/percussion-states/README.md)
gives read-only verification and bounded reproduction commands. The capture
script requires a new output path, explicit dummy audio/video and software
rendering, and the recorded coherent source/build identities. It saves a native
BMP then proves a lossless PNG conversion before deleting the BMP intermediate.
The native BMP hash remains recorded; the discarded BMP bytes cannot be
reverified later. Retained PNG bytes, decoded pixels, replay, controls and
diagnostics can be reverified without launching the app.

## Separate acceptance evidence and practical limits

| Evidence | Qualified result | Boundary |
| --- | --- | --- |
| [A18 geometry/input checks](development/2026-11-15-audio-continuation/notes/A18.md) | Fixed anchors, threshold neighbors, target boundaries, all switch domains, 71-stop focus traversal, pending/applied routes and held UI/MIDI ownership | Author note initially records syntax-only execution; root's retained [native CTest log](development/2026-11-15-audio-continuation/reports/w04-native-ctest.log.gz) subsequently records `test_standalone_percussion_reference` passing |
| [A23 paired raster qualification](development/2026-11-15-audio-continuation/reports/w04-a23-paired-final.json) | 66 identical-state old/current pairs, 208,102,766 compared pixels, zero escaped pixels and 28 exact inactive pairs | Uses genuine old/current UI objects with common drawing inputs; expanded masks allow exactly one outward device pixel; covers 1×/1.5×/2× and clips, not physical displays |
| [A23 note and build receipt](development/2026-11-15-audio-continuation/notes/A23.md) | 1,482 literal glyph checks, 52,408 strong-ink pixels and 32 focused active cases; retained first evidence and stricter final comparison | Deterministic painter evidence; separate from time-running standalone screenshots |
| [A28 retained-gallery audit](development/2026-11-15-audio-continuation/reports/A28-gallery.json) | Original eight identities/state records plus three additional real native runs, exact replay/diagnostic/image identities and direct image inspection | Capture author qualification; independent full-reference review remains separately owned |

The original application gallery and three new frames use equal logical and
drawable sizes at 1×. Their callback clocks, elapsed times and footer status may
vary on reproduction. They cannot establish pixel containment between old and
new production versions; the deterministic A23 comparison supplies that separate
evidence. Dummy-driver software captures also do not establish native window
scaling, physical MIDI/audio usability, audio fidelity, deadline margin, semantic
accessibility or a completed browser/plugin journey.

## Remaining design work and next integration step

The reference tablet bodies start near y177; the current frozen strip puts them
at y150. The **approximately 27 logical-pixel vertical difference remains** at
the reference size. A complete reference match also requires a coordinated
review of the wider performance strip, racks/manual allocation, typography and
the reference's concept-only controls. A screenshot of the actual application
must continue to show real capabilities and valid value domains.

The next integrator step is to connect these exact images and qualified limits
from the main README, finish the independent A29 reference review, and bind the
capture hashes to the eventual published source commit. Preserve the original
eight receipts, all three added capture receipts, failed evidence if any future
run fails, and the unresolved 1:1 requirement. A later layout change needs a new
bounded contract and independent geometry/input/raster/application evidence;
it must not silently reuse these screenshots as evidence for changed code.

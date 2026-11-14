# A05 - Complete atlas product reading and reference comparison

Assignment: `/root/w01_a05_atlas_product`, wave 1 of the new fixed-registration
continuation. Ownership is this report only. No production source, source image,
PDF, shared status document or Git history was changed. No application, audio,
host, accessibility or physical-device test was executed by this assignment.

## Source and complete coverage

Read every page **337-420 inclusive**, 84 pages, from
[`Hammond_B3_Leslie_Research_Atlas_500pp.pdf`](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf).
The PDF has 21,248,265 bytes and SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

Extraction used Poppler `pdftotext` 25.03.0 with `-f 337 -l 420 -layout`.
The complete extracted range has 220,199 bytes, 25,535 whitespace-delimited
words, 84 page form feeds and SHA-256
`3028df94f01dd556295a465b479c972c1c8cd147bdabfa8e9fc05604bb8f63be`.
Reading was performed in bounded, complete text chunks: 337-350, 351-364,
365-378, 379-388, 389-398, 399-408 and 409-420. The first display of 365-378
truncated part of page 372; page 372 was then reread completely in a separate
output. This is full page coverage, not a keyword search.

| Pages | Complete chapter read | Consequence for the current phase |
|---|---|---|
| 337-342 | 055: speaker nonlinearities and identification | Driver/cabinet dynamics and physical fitting remain separate from fixed routing. |
| 343-348 | 056: Leslie validation | Synthetic output and attractive UI do not establish cabinet fidelity. |
| 349-354 | 057: physical acquisition | Actual specimen, signal boundary, control history and calibration must accompany future physical claims. |
| 355-360 | 058: schema and provenance | Version and hash actual source/profile assets; compile immutable data off audio. |
| 361-366 | 059: calibration and fitting | Validate upstream routing first; downstream equalization cannot compensate for a mapping mistake. |
| 367-372 | 060: musical regressions | Test source continuity, Cancel, held notes, event ties, callback partitions and first divergent state. |
| 373-378 | 061: listening protocol | No universal identity percentage or listening pass follows from engineering acceptance. |
| 379-384 | 062: runtime budgets | Keep sole audio ownership, fixed bounded communication and no callback allocation. |
| 385-390 | 063: engine architecture | Same core serves all wrappers; controls are distinct from full DSP checkpoints. |
| 391-396 | 064: host integration | Preserve stable IDs, headless operation, event ownership, coherent state restore and explicit host qualification. |
| 397-402 | 065: parameters and migration | Freeze numeric laws as well as IDs; fixed routes, snapshots and physical latch masks have different meanings. |
| 403-408 | 066: packaging | Qualify actual installed artifacts and retained older projects on each claimed platform. |
| 409-414 | 067: art direction | Walnut/charcoal/brass depth, dynamic text, independent editor/sounding routes and real preset-key inventory. |
| 415-420 | 068: player workflows | Show the player's next action and current route clearly; preserve notes across editing, resize and recall. |

Original PDF pages **399, 404, 409 and 415** were rasterized with PyMuPDF
1.26.6 at scale 1.35 and visually inspected. Page 399 shows gesture ownership
and rebinding; page 404 shows the separate build/qualification stages; page
409 contains the art direction; page 415 separately shows a control-layout
study with the reversed preset octaves. These are source figures, not current
application screenshots.

Also read `AGENTS.md`, the full current `README.md` and
[`REFERENCE_UI_DESIGN.md`](../../REFERENCE_UI_DESIGN.md), together with the
parent-provided complete plan/current-next-step context. The README bytes read
have SHA-256 `3265a7821e17164a5ceea7a46ef7abeccf47bc8b712808735c65fb84c08ee8d8`;
the design contract bytes have SHA-256
`888118f131941c2c2c7c923edcfb7d2c06e8494f994b6817f8073ede237cf764`.
These identify the reviewed inputs; later edits require their own qualification.

## Fixed-selection and state contract

The proposed M3 work is supported directly by the player contract. Pages 410,
414 and 415 specify **61 playing keys plus 12 reversed preset keys per manual**,
four retained nine-drawbar banks and 25 separate pedals. Page 410 explicitly
uses ordinary exclusive selection and the documentary chapel matrix. The fuller
multiple-latch physical network remains a different requirement.

1. **Selection changes routing, without copying banks.** Pages 389, 401,
   410 and 416 retain all banks independently of the sounding route. Fixed
   registration must remain unchanged while an adjustable bank is edited.
   Returning to A#/B exposes that bank's retained values.
2. **Cancel is not a note release.** C is a momentary action, not a latched
   sounding registration. It clears the selected manual's route while preserving
   held-key ownership, other divisions, banks and continuous state (369, 389,
   401, 410, 416). A visible cancelled route is legitimate; a permanently
   depressed C key would misrepresent the momentary gesture.
3. **Display eligibility without rewriting controls.** Page 418 requires the
   stored percussion switch positions to remain visible while the route is
   ineligible, with a concise explanation such as `Requires upper B`. Do not
   move the 1-foot drawbar to zero to depict its suppression. Show both applied
   `SOUNDING FIXED C#` and the separate `EDIT B` identity when appropriate.
4. **Do not automate total-state loading as a new vintage key.** Pages 392
   and 401 distinguish physical preset-key intent, host program selection and
   modern total-state recall. A new bounded exclusive routing parameter may
   represent this explicitly limited model; it must not silently become a
   program selector that rewrites every bank. Keep Save/Load as coherent state
   transactions outside the reversed octave.
5. **Preserve old IDs and normalized meaning.** Pages 393 and 397-402 require
   permanent IDs, canonical enum values, precise threshold behavior, unchanged
   old fixtures and visible failure for unsupported future state or missing
   resources. The atlas's proposed discrete conversion on page 398 differs
   from the current repository's midpoint convention. Do not replace existing
   conversion laws while adding the new selector. Explicitly freeze and test
   the new law, including its neighboring binary64 values.
6. **Persist wiring identity.** Pages 389, 394 and 401 require control/profile
   identity, all inactive banks and routing to survive save/load. A new format
   should bind the admitted fixed matrix by a stable model identity and digest,
   rejecting an unsupported or mismatched matrix rather than substituting a
   visually similar registration. Keep profile evidence distinct from mutable
   player controls.
7. **A musical save is not a DSP restart image.** Phases, charge, contact
   trajectories, transient owners, clock, pointer addresses and device handles
   must not enter the new musical format. Parse/migrate off audio, then publish
   one valid copied snapshot. Ordinary restore must not race or reset ongoing
   DSP state (389, 394, 401).

Pages 387, 393 and 400 require ordered events at exact sample boundaries,
zero-frame control commits without elapsed time, and independent reconstruction
of native automation curves. Pages 379-381 and 388 require bounded fixed-size
messages and one serialized owner of mutable audio state. Adding two selector
fields therefore requires reviewing every snapshot encoder/decoder and queue,
not just extending the text writer.

## Original image versus retained native capture

Visually inspected both full 1672 x 941 files:

| Image | File SHA-256 | Observed status |
|---|---|---|
| [Original cover/reference](../../design/atlas-cover-reference.jpg) | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` | Unaltered embedded JPEG, 412,664 bytes; source art direction. |
| [Retained native image](../../../examples/demos/standalone-midi-ui-v1/images/reference-1672x941.png) | `239a38c6f47079e442c4ecb0c62c8e38c81d032153be93d892bc854966835fc7` | 597,319 bytes; earlier application capture with its existing provenance, not a new execution here. |

The current capture carries the composition, wood edges, serif title, paired
racks and exact cabinet decoration. It is visibly different from the source:

| Area | Actual comparison | Feasible next implementation |
|---|---|---|
| Metal and frame | Current deck is flatter and more uniformly green/gray; source uses darker textured panels, deep inner lips and softly lit wood rails. | Add restrained prepared surface texture or deterministic shading, deeper panel recesses and consistent edge highlights; keep decoration outside audio. |
| Tablets | Current tablets have very thin rectangular borders and shallow relief; source caps have rounded bevels, darker sockets and wider soft shadows. | Paint socket, shadow, top face and front face separately, with labels rendered dynamically after the material layers. |
| Drawbars | Current caps are shallower, shafts broad/olive, tracks flat black; source has narrow metallic shafts, projecting caps and stronger occlusion. | Narrow and highlight shafts; add cap-front depth and shadow proportional to the admitted geometry; preserve zero-top/eight-bottom direction and correct footages. |
| Playing manuals | Current keys are orthogonal, visually narrow and flat, with short fronts; source keys show stronger near-edge thickness, fallboard shadow and perspective. | First improve shading, front-face height and raised black-key bevels inside existing paint/hit regions. Any real perspective requires one shared transformed geometry and new hit tests. |
| Vertical composition | Current performance/rack area and manuals are more compressed, while permanent pedals and the computer-key toolbar occupy additional rows absent from the source. | Recover visual space through a deliberate responsive arrangement; an expandable pedal drawer is explicitly supported on pages 410/415/417. Do not silently remove playable pedals or keyboard access. |
| Presets | Current cheek has EDIT/PLAY A/B/Cancel buttons; neither retained image depicts the documented functional reversed octave correctly. | Add the twelve actual preset controls per manual, preserving separate bank editing. Page 415's source layout study is useful for control placement even though the cover remains the material target. |
| Cabinet | Exact source artwork is already retained, but current art is higher/smaller and the lower area is a factual device card instead of mic/speed controls. | Preserve the factual card until those audio features exist. Adjust frame/material proportions without painting enabled controls that do nothing. |

The atlas itself says the cover's generated key counts and legends are not
engineering authority (409). Preserve corrected percussion semantics, proper
footages, live values and actual signal availability. Do not conceal those
necessary differences in a pixel-equality claim. The source proposes decorative
depth, yet page 420 also permits removing perspective when it obscures selection
or blocks operation. A material refinement inside verified geometry is the
least disruptive first step toward the requested appearance.

There is a useful bounded inventory option: the current contract declares 46
ordinary controls, including six PLAY A/B/Cancel route buttons across the two
manuals. Replacing those six with 24 preset keys yields **64 ordinary controls**,
retaining the existing fixed capacity and all EDIT A/B actions. This is a
design recommendation, not a claim that the new layout or focus traversal has
already been implemented or tested. Playing-note geometry stays separate.

## Acceptance evidence to retain

For the new fixed routes, execute every admitted registration and compare it
with an independently initialized equivalent bank while preserving source phase.
Cover held chords, inactive-bank edits, separate lower/pedal ownership,
Cancel/reconnect, upper-B percussion eligibility and history, equal-offset
orders, zero-frame flushes, invalid-call rollback and irregular partitions
(369-372, 387, 389, 393, 400-402).

Enumerate the actual VST3 exports against the new registry and test old saves
with all four banks populated. Compare standalone, headless and plugin output
under the same stimulus and declared precision. Test new selector fields through
coherent publication, pending restore, concurrent save and installed relocation;
a header compile or schema pass alone is insufficient (390, 396, 402, 407).

Capture the changed native app at 1672 x 941, 1280 x 900 and 960 x 700, including
both fixed and adjustable selections, Cancel, pending/applied feedback, focus
and percussion ineligibility. Count 12 preset identities separately from 61
playing identities per manual, then exercise mid-drag bank changes, resizing,
off-window release, save/restore and independent MIDI holds (399, 410-418, 420).
Bind captures to exact source/executable/dependency identities and update the
README only with those actual captures. Retain a direct visual comparison and
remaining differences rather than equating a working UI with physical fidelity.

The wider M0-M9 plan remains intact: M3 fixed-route engineering is dependency
ready; M4/M5/M6/M7 electrical and acoustical completion, M8 physical calibration,
and M9 actual DAW/device/accessibility/signing qualification retain their own
inputs and gates. No physical dataset, listening panel or platform runtime
result was acquired by this source-review assignment.

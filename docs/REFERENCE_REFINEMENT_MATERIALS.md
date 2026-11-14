# Live material and lighting contract

Status: accepted by the integrator after A08 review, subject to independent execution; no rendering pass claimed.
Geometry belongs to [the layout contract](REFERENCE_REFINEMENT_LAYOUT.md).
This contract changes live paint only, preserving the scope's 47 parameters,
state4/readers 1–3, 24 presets, 147 playing keys and original ownership.

## Reference and observed difference

Directly inspected the unchanged [cover/page-409 art](design/atlas-cover-reference.jpg)
and [native v2 Play capture](../examples/demos/standalone-interface-preview-v2/images/play-reference-1672x941.png),
both 1672×941. Their verified SHA-256 identities are respectively
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` and
`27c1a877ac458dc6775e7fb80f3edadf7b0508f923a5ef8d6cfb5095115847cd`.
[A05's complete assigned reading](development/2026-11-14-reference-refinement/notes/A05-atlas-interface.md)
records the atlas constraints, especially pp. 409–420.

The native image has recognizable walnut, ivory and brass, but broad deck faces
look uniformly dark; key beds and front lips have less depth than the concept.
The cropped cabinet is already effective decoration. Strengthen the surrounding
live surfaces rather than processing that image or adding a full-reference overlay.
The concept's inaccurate controls and key counts remain excluded. No literal
1:1, connected rotary, or physical-material claim follows.

## Implementable paint changes

Use one stationary light from above-left. Dimensions below are logical pixels;
colors are proposed sRGB starting values, not measured reflectance. Implement in
`InstrumentView.cpp`; existing `Drawing::gradient`, `quad`, `quad_outline`,
`quad_band` and `inset_quad` provide the required operations.

| Surface | Concrete treatment |
|---|---|
| Charcoal deck (`panel`) | Raise inner gradient from current `(35,34,33)→(18,18,18)` to `(43,41,38)→(21,22,21)`. Keep black recess, narrow metal rim and screws. Give the top/left lip a one-pixel warm highlight; retain a dark bottom/right edge. Do not add broad glowing borders. |
| Deck grain | Retain deterministic local-coordinate grain. Light marks use warm gray with alpha 6–10; dark marks alpha 10–18. Adapt spacing to cap at 2,048 point pairs per panel, with each resulting RGB perturbation ≤8. Paint before labels/controls. Grain must not depend on frame count, time, audio or random allocation. |
| Raised ivory/brass (`button`, `drawbar`) | Retain existing 3–5 px tablet fronts and live bounds. Ivory face starts `(250,237,207)→(225,204,166)`; front `(205,180,139)→(165,135,91)`. Restrict specular band to the upper 12% (maximum 4 px), with one-pixel top/left light and darker right edge. Preserve the existing brown/black/ivory drawbar grouping and selected amber distinction. Brass text remains `kUiBrass`; metal lips use muted brass, not extra text embossing. |
| Walnut (`wood`) | Preserve reference cheek crops and procedural fallback. On exposed live rails use a narrow warm top edge and darker underside, with existing directional grain. Do not stretch a keyboard/control crop over a live region or intensify wood behind small legends. |
| Natural keys (`paint_key`) | Retain current ivory gradient and separate front quad. Increase the existing top recess band from 8% to 12% of top depth, capped at 18 px, fading alpha 90→0. Retain a ≤2 px front-edge highlight. The deeper layout, recess and darker front should supply depth without changing the hit silhouette. |
| Accidentals | Keep the existing inset cap, darker front and narrow bevel. Use upper cap `(61,58,52)` fading to `(20,22,19)`; keep an identifiable top-front edge. Avoid extra rectangular drop shadows across neighboring naturals. Held colors remain visibly distinct from idle. |

All key overlays use bands interpolated from the original `top`/`front` quads;
never use their bounding rectangles. Paint bed, naturals, accidentals, then
held/focus ink for each key. Preserve the existing two-pixel cyan focus and held
marker without dimming them; if the brighter ivory obscures cyan, add a dark
separator inside the same quad. Labels and focus remain above material layers.

## Cabinet and status layering

Use A07's disjoint cabinet and pedal panels and its shared art/status bounds.
Within the cabinet, paint panel, a 2–3 px dark art recess, artwork, narrow warm
upper rim, captions, then status. Any new rim stays outside the artwork but
inside the cabinet; shadows must never enter the pedal panel. Preserve art
aspect ratio, the optional-art fallback, `CABINET REFERENCE` and
`ROTARY AUDIO NOT CONNECTED`. Do not create microphone dials, Stop controls,
animated rotors or implied telemetry.

The compact status card keeps actual audio/MIDI state and explicit disconnected
scanner/rotary facts. Apply `text_line`/`wrapped` only within its allocated rows;
long names/errors must not paint over pedal keys. Footer recovery, pending and
focus messages retain priority. Layout, not paint code, decides available space.
For compact status, use row offsets 31, 49, 67 and 85 with 14 px bounds. The
existing 31/51/71/91 sequence overruns a 101 px card at short/wide legacy sizes;
the corrected final row ends at 99 px without changing geometry or font sizes.
The active sidebar contract reserves at least 116 px for status.

## Acceptance and bounded work

1. Retain lossless actual native before/after captures at 1672×941, 1280×900 and
   960×700; include Flat, held natural/accidental, focused keys and sidebar pedals.
   Compare matched crops with the exact art and document remaining differences.
2. At an unobstructed natural-key center, front-face Rec.709-weighted sRGB level
   (0–255) must be ≥15 below the adjacent top; the rear recess must visibly fade
   rather than forming a hard stripe. Panel grain changes pixels by ≤8 channels.
   Measure samples away from outlines, held marks and antialiased text.
3. Preserve existing text sizes and verify each label/status row remains readable.
   Proposed text/background palette pairs must retain ≥4.5:1 relative-luminance
   contrast for normal labels. This palette check is not native accessibility
   qualification. Flat adds no grain, bevel, new shadow or perspective effect.
4. Use existing drawing, quad, workspace-raster, scaled-view and preset-raster
   suites. At output scales 1, 1.25, 1.5 and 2, newly changed material ink must
   stay inside its intended surface, with no seam leaks or clip/viewport escape.
   Reject nonfinite/empty geometry; bound loops by visible extent or the grain cap.
5. No new textures, dependencies, per-frame heap allocation or audio-thread work.
   Compare reference-size geometry/build/backend before and after materials: warm 30
   frames, time 300 draws excluding capture/I/O, retain median/p95 and renderer.
   Investigate p95 growth exceeding both 15% and 2 ms; this is a UI regression
   budget, not an audio deadline or cross-device performance claim.

Implementation and fresh acceptance remain next work; this document supplies
reviewable targets, not executed results.

## 2026-11-14 measured wide-header typography addendum

The owner requests close reproduction of the original reference. After the
accepted v3 capture, [A36's measured review](reviews/REFERENCE_REFINEMENT_VISUAL.md)
identified title ink 30 pixels too narrow and 8 pixels too low at 1672×941,
plus a much smaller/lower truthful subtitle. Root authorizes a **narrow exception
to the original text-size preservation rule** for `sidebar_pedals` with
`UiPresentation::Dimensional` only. Earlier A08/A14/A26 results retain their
original source identities and requirements.

A40 may refine the title size/baseline and the exact `NOMINAL DRY ORGAN` caption's
size, tracking and baseline, using existing serif/sans faces and existing
`kUiBrass`. Initial measured candidates are title 42.75 at `header.y - 4.5`,
and caption 17 at `header.y + 51.5`, tracked to a 374-pixel advance. These are
candidates; measured native ink, safe fitting and clipping determine acceptance.
The original reference's title ink box is `[603,20,1067,53]` and subtitle box is
`[650,71,1021,83]` under A36's stated threshold/half-open measurement convention.
The caption retains truthful product wording rather than imitating unavailable
sound features.

All control/hit/focus geometry, parameter/state meanings, other palettes,
material/error budgets and allocation boundaries remain unchanged. Complete
Flat and non-sidebar frames must retain identical pixels; changed wide frames
must preserve pixels outside the header. Keep the original title allowance and
fit safely at the wide breakpoint and tested scales. Preserve all existing
material assertions, add scoped authored checks, and require A41's independent
ink/isolation/clip review plus the one changed reference timing cell under A25's
frozen procedure. Retain any first failure and at most one permitted reversed
repeat. Publish accepted source before a fresh source-identified final gallery;
v3 remains immutable historical evidence. This addendum does not claim literal
whole-interface equality or physical display/device qualification.

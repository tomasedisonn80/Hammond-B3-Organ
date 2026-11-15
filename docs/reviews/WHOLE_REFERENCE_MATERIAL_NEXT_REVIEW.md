# Independent review of the next material proposal

**A41, 15 November 2026. Decision: accept the bounded direction for protocol
authoring; production implementation and numerical tolerances are not yet
admitted.** The [A38 proposal](../design/WHOLE_REFERENCE_MATERIAL_NEXT.md) correctly
keeps literal whole-interface **1:1 unmet and unwaived**. It selects a useful
next surface without treating the existing composition pass as material parity.
The conditions below complete the prospective protocol before a painter edit.

## Inspected evidence and reproduced observations

Read the standing instructions, current checkpoint, complete M0–M9 plan,
[composition contract](../WHOLE_REFERENCE_LAYOUT_CONTRACT.md),
[gallery admission](WHOLE_REFERENCE_GALLERY_ADMISSION.md), A27/A29 mask records,
and the relevant current `InstrumentView.cpp`/`Drawing.cpp` implementations.
Directly viewed the original JPEG and both actual 1672×941 and 1400×820 PNGs.
The source hashes match A38's declaration. No image was changed or recaptured.

Independently decoded RGB and recomputed encoded-channel Y′ using A38's weights.
For each half-open patch, a least-squares plane used columns `[1,x,y]`, with
population RMS of its residual. Results, rounded here to six decimals:

| Patch | Reference mean / residual RMS | Current native mean / residual RMS |
| --- | --- | --- |
| `(88,320,18,128)` | 18.291278 / 1.377161 | 31.841181 / 0.486684 |
| `(572,320,14,128)` | 25.323310 / 1.563373 | 31.818605 / 0.622113 |

All four pairs reproduce the proposal. The reference's right-minus-left mean is
7.032031; the native difference is −0.022576. These are image statistics, not
physical luminance or evidence that the two patches represent the entire panel.
The viewed native panel is visibly more uniform and brighter in these areas.
The composition and exact cabinet crop are separately evidenced; differing type,
key/cap shading, wood and truthful control inventory remain visible residuals.

## Conditions before painter implementation

1. **Freeze the actual surface operations and narrow mask.** The canonical Upper
   panel is `(72,269,528,239)`; its four-unit inset is correctly
   `(76,273,520,231)`. Current `reference_panel` paints the inset gradient, then
   grain, border accents and screws; headings and controls are painted later.
   Select only this panel through a private painter argument. “Opt-in” must not
   introduce a control, saved field or parameter. Preserve the other calls and
   insert the changed surface before the existing accents and children.

   Derive coverage from actual binary32 inset arithmetic, each primitive's
   raster rule, viewport, renderer scale and caller clip. `Drawing::gradient`
   uses center-based `PixelRaster`; `Drawing::rect` uses SDL fill rectangles.
   These are not interchangeable endpoint rules. Apply any declared one-pixel
   allowance in device coordinates after deriving intrinsic coverage. The old
   v2 mask covers almost the whole changed composition and cannot qualify this
   smaller edit. Its 6,068 old wood-line corrections concern different source
   operations; neither those regions nor their 675 added pixels carry forward.

2. **Define what preserving children means.** Keep their geometry, text, draw
   operations, order, state and hit/focus identities unchanged. Antialiased glyph
   edges and translucent accents blend with the new background, so their final
   RGB values can legitimately change inside the allowance. Do not demand
   impossible whole-child pixel equality or silently broaden the mask to avoid
   it. Separately compare opaque child interiors, glyph coverage/placement,
   live values and focus edges using declared deterministic fixtures. Outside
   the new allowance, require exact equality; all inactive frames remain exact.

3. **Freeze metric scope and reproducibility.** Apply the proposed mean ±2.0,
   RMS ±0.4 and difference ±1.5 screens to the declared reference-size patches
   using unrounded measured reference values. Retain raw sums/residual results,
   decoder identity and file/decoded-pixel hashes. Declare those screens only
   at 1672×941 unless a separate sampling rule is specified for scaled frames;
   resampling the JPEG introduces a different comparison. The tests should
   record the current baseline's failures before candidate authoring. Full-frame
   examination and retained spatial differences must additionally reject seams,
   banding, repeating grain and worse label/focus contrast. Two patches cannot
   constrain the whole illumination field or prove material identity.

4. **Bound the new rendering work.** Declare deterministic grain coordinates,
   seed and operation/storage limits before implementation. The current helper
   caps grain at 2,048 pairs. A replacement must not accidentally scale an
   unbounded point loop with the admitted 8192×8192 window. Preserve renderer
   scale, viewport, clip and blend state, including an empty intersection.
   Retain the proposed size/scale/offset/crossing-clip and 0/4/8 drawbar matrix,
   with fixed snapshots for exact comparisons and actual replay captures for
   product evidence. The stated affected suites and coherent/platform gates
   remain required; this review did not execute them.

## Admission boundary and next task

Assign independent protocol/mask/test ownership before painter ownership. Freeze
the above definitions, baseline outcomes and source identities together. Root
may then authorize the isolated Upper-rack candidate and obtain new source-bound
captures and independent admission. A pass would qualify only this surface and
preservation matrix. It would not close whole-interface 1:1, native-display
usability, semantic accessibility, connected scanner/rotary audio or physical
fidelity. Existing captures, the original v1 failure and v2 result remain intact.

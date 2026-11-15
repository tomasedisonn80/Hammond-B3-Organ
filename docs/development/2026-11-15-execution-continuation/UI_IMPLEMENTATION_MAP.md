# Wide Play implementation map — frozen worker boundary

A08, 2026-11-15. This maps the admitted design to existing source; it is not a
replacement design or executed acceptance. Root adopts the admission at contract
SHA-256 `55cc841d10dc65004cbfcca83d0fb84dcf54dda779e1d82a376534e2650b730f`.
Read [contract](../../WHOLE_REFERENCE_LAYOUT_CONTRACT.md) and
[review](../../reviews/WHOLE_REFERENCE_LAYOUT_CONTRACT_REVIEW.md) for all literals.

## Exact ownership and shared interface

| Owner | Exclusive writable production files | Boundary |
| --- | --- | --- |
| Layout | `apps/standalone/UiModel.cpp`, `UiModel.h` | Active allocation, canonical construction, mapping, validation; header API below. |
| Painter | `apps/standalone/InstrumentView.cpp` | Active furniture/material/text/order only; consume the header API without editing it. |
| Independent qualification | Explicitly assigned test/capture files | Literal independent expectations; no production helper in expected geometry. |
| Root | CMake, build, shared records, integration/publication | Freeze both source owners before coherent builds and source-bound captures. |

Put this exact SDK-free interface after `UiLayout` in `UiModel.h`; layout owner
implements the small functions inline. Painter can begin against these names.

```cpp
struct ReferenceCompositionScale { float sx, sy, f; };
[[nodiscard]] inline bool reference_composition_active(const UiLayout& layout) noexcept;
[[nodiscard]] inline ReferenceCompositionScale
reference_composition_scale(const UiLayout& layout) noexcept;
[[nodiscard]] inline UiPoint reference_composition_point(
    UiPoint canonical, ReferenceCompositionScale scale) noexcept;
[[nodiscard]] inline UiRect reference_composition_edges(
    float left, float top, float right, float bottom,
    ReferenceCompositionScale scale) noexcept;
[[nodiscard]] inline UiRect reference_composition_rect(
    UiRect canonical, ReferenceCompositionScale scale) noexcept;
[[nodiscard]] inline UiQuad reference_composition_quad(
    const UiQuad& canonical, ReferenceCompositionScale scale) noexcept;
```

Predicate: Play, Dimensional, `1400 <= width <= 8192`, `820 <= height <= 8192`.
Use actual fields, never `sidebar_pedals` alone; these comparisons reject NaN/Inf.
Scale is binary32 `sx=width/1672.0F`, `sy=height/941.0F`, `f=min(sx,sy)`;
its precondition is a valid active layout. Point multiplies x/y by sx/sy.
Edges maps the four endpoints, then subtracts mapped endpoints for extents.
Rect delegates with `(x,y,x+width,y+height)`; Quad maps all four stored vertices.
Preset partitions call **edges** using reused canonical boundary values directly.
Preserve `kUiReferenceWidth=1280`, `kUiReferenceHeight=900`: these mean startup size.
No new sound/state fields, public hit targets, `Drawing` transforms or dependencies.

## Layout writer: concrete change map

1. In `make_ui_layout`, retain the existing argument rejection first. Initialize
   a candidate's size/workspace/presentation, take an early active branch, and
   keep the existing inactive arithmetic intact. Assign destination only after
   both existing validity and the additional active invariants succeed.
2. Construct the contract's parents and all 68 controls in canonical coordinates.
   Retain existing insertion sequence: 10 common controls; per manual Edit A/B,
   12 presets, nine drawbars; percussion `[0,2,3,1]`; expression, two mixtures;
   three keyboard targets, octave down/up. Preserve IDs/bank rebinding exactly.
3. Set active `show_cabinet`, `bank_controls_in_cheeks`, `sidebar_pedals` true.
   Canonical preset panels are Upper `(58,607,164,81)` and Lower `(42,777,172,83)`.
   Edit widths are 80/84; generate canonical inset-4 button labels before mapping.
   Empty unused value/track rectangles remain `{}`. Art uses the mapped
   `(1132,174,466,397)` envelope, aspect-contained at 466:397, top aligned.
4. Add an active-only key constructor beside `make_keys`; preserve old helper.
   Use canonical panel insets 8/20/8 and back factors 0.96/0.95/1. Construct
   hit/top/front first, including each key's projected height and canonical
   `clamp(0.14*height,6,18)` front depth. Transform complete vertices, then derive
   AABBs. Do not map only AABBs or clamp front depth again in window coordinates.
5. Keep `ui_hit_test`, note ownership, parameter mapping and focus/transition
   logic unchanged. No ornamental region gets a record or event action.

## Active validation obligations and traps

- Finite positive parents/control bounds/labels; applicable values for manual
  drawbars, pedal drawbars, expression and percussion; tracks only for drawbars
  and expression. All inapplicable fields are canonical empty, not positive.
- Percussion legends intentionally lie outside cap hits: contain in performance,
  ensure four canonical units below caps, and test they are inert. Other labels
  and all applicable value/track rectangles must fit their declared owners.
- Ordinary controls have disjoint interiors except the deliberate preset
  accidental/natural overlays: exactly 20 intersecting pairs across both manuals.
  Cabinet parent contains toolbar/pedals; the former 10-unit separation assertion
  is inactive-only. Key AABBs can overlap under perspective; validate quads.
- Reuse seven preset partition boundaries; assert 12 adjacent natural joins
  exactly across two manuals. For keys assert identical natural shared vertices,
  top/front joins, exact AABB-from-vertices, horizontal edges and positive area.
- Validate all track endpoint cap envelopes: manual slot y311–461, cap 34×32,
  footage y467–490, digits y491–506; mixture cap 34×22 travels within y182–247.
  These are canonical values, not unscaled window-space padding.
- Keep additional validation active-only unless an independently justified repair
  is assigned; broadening old validation can accidentally reject legacy extrema.

## Painter writer: concrete change map

Prefer an early active branch in `paint_instrument` and active-only local helpers.
Keep inactive `button`, `drawbar`, key/preset paint and header/order literal.
Consume stored controls/quads for every live surface, label, focus and hit relation.

| Existing area | Active replacement |
| --- | --- |
| `paint_instrument` furniture | Canonical rim `(48,510,1074,18)`; parent cabinet before any nested children. Scale active insets/bevels/fronts/slots, with existing colors/materials. |
| `paint_header` | Origins y11.5/y67.5; title 42.75f, caption 17f, tracking budget 374sx; allowances based on mapped Service/Save/Flat. Tabs 18f, tools 11.5f. |
| Performance block | Divider x556,y137–252; both headings; eligibility always its own y248 row. Stored enable and applied Upper-B eligibility retain distinct meaning. |
| `drawbar` | Replace old label-to-value material-strip formula: new footage is below rails. Use track/cap travel envelope; footage 19f with padding 2sx, digits 12f. |
| Rack/cheek block | Full manual rack headings; move EDIT BANK and `sounding_caption` into cheek y+20/y+34. Do not reuse compact shortened captions. |
| `paint_controls` / `button` | Active-only scaled materials and recorded label/value rectangles. Percussion values 20f, legends 13.5f; keep all existing domains/actions. |
| Key/preset material and focus | Use transformed shared quads and scale material insets in x/y; preset stacked accidental labels need scaled pitch/height. Preserve glyph/focus clipping and renderer-state restoration. |
| `paint_cabinet` | Parent/art/title/truth/status before manuals/toolbar/pedals; four truth statements retained. Drop old computed status-card allocation in active branch. |
| Toolbar/pedals | Explicit two-row toolbar and caption `(1340,654,240,14)`; pedal heading `(1150,755,426,16)`. Old caption x+478 would have negative width. |
| `paint_footer` | Preserve recovery/pending/focus/status/dirty/peak priority; scale canonical offsets within `(48,889,1556,36)`. Modals still paint last and remain unchanged. |

Do not scale the whole SDL renderer anisotropically: that stretches glyphs and
risks caller clips/scales. Geometry uses sx/sy; font requests use f and measured
fitting. The active cabinet call must move; changing rectangles alone erases keys.

## Independent test migration, without deleting historical assertions

| Actual test path under `apps/standalone/` | Prospective migration |
| --- | --- |
| `tests/test_standalone_percussion_reference.cpp` | Replace active y150/cap literals and active=Flat neighboring allocations. Assert y177,74×52, exterior y233/height14, value inset 5/6/5/8, scaled canonically; keep inactive literals/domain/input checks. |
| `tests/test_standalone_reference_layout.cpp` | Active parent/key/cabinet/art literals replace old sidebar numbers; nested cabinet containment replaces old 10-unit gap. Retain inactive matrices/fingerprints and 71/10 focus counts. |
| `tests/test_standalone_projection.cpp` | Add independent canonical rational oracles 24/25 and 19/20, 8/20/8 insets and pre-scale front split. Existing 47/50 oracle stays inactive; do not use mapped panel plus fixed 22/30. |
| `tests/test_standalone_ui.cpp`, `test_standalone_preset_ui.cpp` | Active header/cheek/preset literals and scaled label heights migrate; preserve exact edges, complete hits, semantic order, old-location classifications, rollback and original releases. |
| `tests/test_standalone_workspace_acceptance.cpp` and continuity cases | Active Play geometry differs from Flat/non-Play; compare sound/owners/focus semantics separately. Keep identical inactive records and hidden-control rejection. |
| `native_tests/test_standalone_percussion_raster.cpp` | Update active literal glyph/eligibility plans; old percussion-only stream regions cannot bound the whole composition. |
| `native_tests/test_standalone_product_visual.cpp` | New footage/state rows and cap envelope. Its optional old painter currently receives the **new model**; this is not genuine old/new layout evidence. |
| `native_tests/test_standalone_material_acceptance.cpp` | Scale only active Play header expectations/regions; keep Rotary/Service old ink assertions, clipping and modal tests. |
| Scaled/workspace/preset/waveform native cases and replay Python cases | Inspect every literal active coordinate and owner mask; retain renderer-state, exact inactive, focus and pending/applied checks. |

Use independent literal expectations at 1672×941,1400×820,1920×1080,
1400.25×820.25,1672.5×941.25,8192×820,1400×8192,8192×8192 and both `nextafter`
neighbors of both activation thresholds. All four edited-bank pairs, workspaces
and presentations; invalid enums/banks, NaN/±Inf and just-outside dimensions.
Chosen coordinate tolerance stays 0.002; shared edges and inactive records stay
exact. Test rejection preserves complete destination/focus and musical owners.

## Capture and acceptance strategy

Before replacing baseline binaries, root retains genuine old-source layout+paint
frame streams and input/source/executable identities, or builds a separately
assigned read-only baseline. One retained old painter linked to the new model is
insufficient. Use identical state, fonts/art, renderer, offsets and clips for
both sides. Predeclare union of old/new composition/furniture/text bounds;
allow at most one outward device pixel. Every inactive frame is exactly equal.
Cover scales 1/1.5/2, crossing clips, drawbar endpoints, all percussion values,
eligible/fixed/Cancel routes, pending/applied cues and all 71 focused targets.

`tools/capture_standalone_interface.py` already uses keyboard-only stable replay
and qualified source/executable hashes; its eight cases omit minimum-active
1400×820 and wide Flat. Assign additions plus toolbar/pedal focus and percussion
states explicitly; preserve earlier galleries. Its 25th-Tab first-drawbar replay
continues working only if insertion order stays intact. Add separate pointer
journeys for relocated controls and held-pointer threshold/mode changes.
Compare complete new reference frame against original JPEG; report geometry,
materials/type and truthful inventory differences separately. Root updates README
after independent capture admission. No 1:1, native-device or audio claim follows.

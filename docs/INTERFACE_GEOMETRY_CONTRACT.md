# Shared dimensional-key and flat geometry contract

Identity: `standalone-perspective-keys-v1`. This is an M9 presentation contract,
not an instrument geometry measurement or a sound-model identity.

It belongs to the [interface continuation](INTERFACE_CONTINUATION_SCOPE.md) and
works with [the workspace contract](INTERFACE_WORKSPACE_CONTRACT.md). The
inspected starting source is `d493e998e5dd7cf44db46854e87309745063ac54`.
Agent 08 prepared this contract for integrator acceptance before implementation.

## Visual objective and retained inventory

The exact [atlas reference](design/atlas-cover-reference.jpg) is 1672 x 941.
Its useful visual cues are the broad walnut perimeter, shallow recessed charcoal
panels, brass type, illuminated ivory tablets, adjacent drawbar racks, warm cap
highlights, a large cabinet column and two keyboards with sloping sides and
visible front faces. Live controls and their paint remain independent of the
decorative cabinet/wood crops. Do not use the whole source picture as a backing
image with invisible controls over it.

This slice gives the **61 + 61 playing keys real shared trapezoid geometry**,
with an operable flat fallback. The **25 pedals** use the same key geometry API
with rectangular plan geometry and dimensional fronts. All **24 reversed preset
keys** retain their already qualified rectangular layout and separate selection
semantics. Their existing cap shading may improve without changing hit regions.
All four retained drawbar banks, correct footage/color ordering, four percussion
controls and existing expression/pedal controls remain available. The reference
image's shorter keyboard inventory and incorrect legends are not copied.

The first implementation preserves the existing body-panel rows and cabinet
breakpoint. This keeps the new perspective change reviewable independently of
future panel recomposition. Header geometry follows the workspace contract:
three workspace tabs on the left, six existing tools in two rows on the right,
and the presentation toggle below the centered title. Controls do not overlap
the title or each other at the supported minimum.

## Shared data API

Place the SDK-free types with the existing `UiPoint`/`UiRect` declarations in
`apps/standalone/UiModel.h`. Preserve the current prefix of `UiKeyGeometry` so
semantic note and existing envelope consumers remain recognizable:

```cpp
struct UiQuad {
    // Clockwise in screen coordinates: top-left, top-right,
    // bottom-right, bottom-left. Top/bottom edges are horizontal.
    std::array<UiPoint, 4> points{};
    [[nodiscard]] bool contains(UiPoint point) const noexcept;
};

struct UiKeyGeometry {
    UiNote note{};
    UiRect bounds{};       // AABB of hit; never the perspective hit test.
    bool accidental{false};
    UiQuad hit{};          // Complete visible key, including the front face.
    UiQuad top{};          // Lit top surface.
    UiQuad front{};        // Darker front face; empty in Flat presentation.
};
```

All arrays stay fixed-size. These additions are main-thread presentation data;
they must not enter `SessionCommand`, `ControlSnapshot`, `SessionSnapshot`, an
audio callback, the sound parameter registry or serialized control state.
The three extra quads require approximately 14 KiB across 147 playing keys with
ordinary eight-byte `UiPoint`; this is bounded storage, not a new asset cache.
Prefer an inline SDK-free `contains` definition beside the type. The drawing
library and its standalone native test currently link without the complete
Session/UI support library; introducing an out-of-line dependency just for
shape containment must not silently make that target unresolvable.

The workspace contract owns `UiWorkspace`, `UiPresentation`, their fields in
`UiLayout`/`UiViewState`, visibility and the trailing default arguments of
`make_ui_layout`. This geometry uses `UiPresentation::Dimensional` and `Flat`
without introducing another mode enum. Header changes from A13 and the geometry
type additions from A14 must be serialized or integrated as coordinated patches;
no worker may replace another worker's header changes.

## Exact keyboard projection

Each existing playing-key panel supplies the current inset rectangle:

```text
X = panel.x + 8
Y = panel.y + 22
W = panel.width - 16
H = panel.height - 30
C = X + W / 2
```

No physical dimensions are implied. `(u,v)` is normalized unprojected keyboard
space: `u=0..1` spans the naturals and `v=0..1` spans their complete depth.
Let `b` be the ratio of back width to front width:

| Surface | Dimensional `b` | Flat `b` |
|---|---:|---:|
| Upper or lower manual | 0.94 | 1.00 |
| Pedalboard | 1.00 | 1.00 |

Use one homography for every key in a keyboard:

```text
d(u,v) = 1 - (1-b) * v
x(u,v) = C + W * b * (u - 0.5) / d(u,v)
y(u,v) = Y + H * b * v / d(u,v)
```

The denominator is in `[b,1]`, so the admitted mappings have no singularity.
At the back, the manual spans `X + .03W` through `X + .97W`; at the front it
spans exactly `X` through `X+W`. For `b=1` this reduces to the current rectangle.
This is a deliberately mild perspective, not a claimed calibrated camera.

There are 36 naturals in each 61-key manual and 15 in the 25-key pedalboard.
For natural ordinal `n` and natural count `N`, use `u0=n/N`, `u1=(n+1)/N`,
`v0=0`, `v1=1`. Each boundary is calculated from its integer ordinal, never by
repeatedly accumulating widths. For an accidental immediately before natural
ordinal `n`, use `u0=(n-.30)/N`, `u1=(n+.30)/N`, `v0=0`, `v1=.62`.
The existing pitch-class pattern and MIDI/pedal IDs are unchanged.

Build `hit` from `P(u0,v0)`, `P(u1,v0)`, `P(u1,v1)`, `P(u0,v1)` in that order.
Its envelope is the min/max of those four points. Keys adjacent at a natural
boundary must reuse mathematically identical edge expressions so their shared
screen edge has identical floating-point endpoints.

### Top and front faces

In Dimensional mode, let `h` be the screen height of this key's `hit` quad and
choose `front_depth = clamp(.14*h, 6, 18)` logical pixels. The admitted panel
heights make the depth less than `h`; validation still rejects a degenerate
top face rather than emitting malformed geometry. Split `hit` at screen
`ys = bottom_y - front_depth`. Obtain the left and right split points by linear
interpolation along the outer sides at that y. `top` consists of the original
top pair plus the split pair; `front` consists of the split pair plus the
original bottom pair. Their union is exactly `hit`, with no gap or extra area.

In Flat mode, `top = hit`, while `front` is the default empty quad. Geometry
must not simulate a new note/contact position when the key is held. Held-state
color, a bounded inner highlight and surface shading can change; the hit shape
and its ownership remain stable throughout the press.

## Exact hit ownership and focus

`UiQuad::contains` implements the horizontal-edge contract, not a rectangular
approximation. Reject nonfinite points, nonfinite vertices, unequal top/bottom
pair y coordinates, zero/negative height and non-positive top or bottom width.
For an otherwise valid quad with top y `a` and bottom y `z`:

```text
a <= point.y < z
t = (point.y-a)/(z-a)
left  = TL.x + (BL.x-TL.x)*t
right = TR.x + (BR.x-TR.x)*t
left <= point.x < right
```

There is no enlarged tolerance or invisible hit rectangle. The top/left edges
are inclusive; bottom/right are exclusive, matching the existing rectangle
policy. Shared edges have one owner. An outside point in the AABB's sloped
corner must not activate a note. This policy also handles a rectangular Flat
quad without a separate input path.

`ui_hit_test` preserves accidental-before-natural precedence and pitch ordering.
Use `key.hit.contains(point)` for both manual and pedal playing keys. Reversed
preset accidentals retain their existing precedence and rectangle semantics.
Before any musical hit, apply the workspace visibility rule: hidden Play
controls and keys cannot become new pointer targets in Rotary or Service.

Keyboard navigation retains semantic IDs and its roving key focus. Painting
focus on a perspective key uses its actual visible quad, inset enough that the
focus stroke stays inside the key. Do not draw the old AABB outline across a
neighbor or outside the sloped key. Test focus in both modes at the extreme
left, center and right of each manual and on overlapping black/white keys.
Preserve focus meaning and held owners across resize/presentation changes.
Existing key-up and captured pointer-up handling remains independent of the
current hit geometry and must release the original press.

## Drawing primitives and material treatment

Add these main-thread drawing operations, with the geometry types above as their
only shape input:

```cpp
void quad(const UiQuad& shape, UiColor top, UiColor bottom) const noexcept;
void quad_outline(const UiQuad& shape, UiColor color,
                  float thickness = 1.0F) const noexcept;
```

`quad` may use two triangles through the pinned SDL geometry renderer, or a
bounded scanline implementation. It must preserve the quad silhouette and a
top-to-bottom color interpolation under the actual SDL software renderer used
by native acceptance. Unsupported geometry must not silently fall back to the
AABB and thereby paint a different key. Invalid or empty shapes are no-ops.
Clip scanline work to the actual render bounds before iterating; never convert
unvalidated nonfinite geometry to an integer count.

`quad_outline` must keep its stroke inside the supplied shape and be meaningful
at small accidental widths. An implementation may draw the four inside edge
strips, or a bounded outer-minus-inner shape. For a y-inset, first evaluate the
original side edges at the new top/bottom y, then inset each resulting left and
right edge. Shrinking all points around a centroid is not a constant-width
inset and must not be described as one.

Dimensional rendering uses warm ivory top planes, restrained darker key fronts,
black key edge highlights, a dark key bed, and shadows contained within the
shared keyboard panel. Paint naturals before accidentals. The reference's
convincing depth comes principally from distinct top/front planes and shared
perspective, not a glow or a decorative bitmap. Drawbar tracks/caps should
retain the correct brown/brown/ivory/ivory/black/ivory/black/black/ivory order
and literal zero-to-eight direction. Cap faces may gain bevel and gloss while
their actual position/value stays live.

Flat presentation removes perspective, key front faces, decorative grain and
heavy shadows from the playing controls. It preserves labels, selection,
pending/applied distinction, focus, held-state indication, controls and their
semantic actions. The optional cabinet decoration need not be hidden, but its
state must remain honest and it must never receive priority over control text.
No animation or second clock is required by either presentation.

## Responsive and text contract

The supported size interval remains 960 x 700 through 8192 x 8192 logical units.
The default remains 1280 x 900. The reference comparison remains 1672 x 941.
Continue collapsing the Play cabinet below width 1400 and moving bank-edit
controls into the racks below height 820. Do not reduce real key counts to
obtain an attractive reference screenshot.

At the minimum size, every action label needs readable bounded text; use at
least 11 logical pixels for workspace/header action labels, and aim for at
least 10 for compact footage/value labels. A focused preset/key/control needs
a readable full semantic label in the shared status area even where its cap is
small. Avoid silent font shrinking below a declared minimum: shorten a caption,
wrap a secondary status, or use its focus detail. Device names and errors stay
single-line bounded or explicitly wrapped/ellipsized; they never paint over a
neighboring control. This is a visual target to verify, not a native
screen-reader-accessibility claim.

Extreme sizes require geometry validation and bounded rendering checks; retain
representative screenshots, not a gallery of 8192 x 8192 bitmaps. Test the
1399/1400 width and 819/820 height transitions explicitly. The dimensions,
header/control regions and all quads must remain finite, positive where
visible, in their parent panels and within the window.

## Reference comparison and known differences

The following reference landmarks are **approximate visual observations**, not
pixel segmentation or physical measurements. Native values are from the
existing layout's literal 1672 x 941 fixture and key-inset formulas.

| Landmark | Original reference, approximate pixels | Existing application / proposed change |
|---|---|---|
| Walnut/inner left edge | Inner panel starts near x70 | Existing margin x71.896; keep its structural position. |
| Cabinet column | Begins near x1125; photograph top around y174 | Existing cabinet x1141.642 and art y154; retained art aspect remains 466:397. Vertical composition is still different. |
| Drawbar racks | Top near y270, bottom near y510 | Existing racks y230.92 through456.76. The compact actual performance controls and extra playable inventory produce a different row structure. |
| Upper manual sides | Back roughly x270..1095; front roughly x240..1120 | Existing key rectangle x248.858..1123.642. Proposed back becomes x275.101..1097.398, while the front remains x248.858..1123.642. |
| Upper key depth | Bright top/front region roughly y548..692 | Existing playing-key extent y526.76..635.24; new sloping edges and top/front split improve depth but do not erase this row-height difference. |
| Lower manual and pedal area | Lower manual occupies most of y710..870; no live pedal row | Application retains a second 61-key manual plus the separate 25-key pedal row. Their shapes and row heights cannot equal that concept inventory. |

The new reference capture must therefore demonstrate its actual geometry and
materials, not claim literal 1:1 image equality. Remaining structural
differences include the correct full key inventory, live preset octaves, pedal
row, control legends, honest unconnected cabinet state, and tools not present
in the concept. A future panel-composition change needs its own shared layout
and responsive acceptance; it must not be disguised as a material-only edit.

## Required independent acceptance

The geometry author and an independent verifier should retain source identity
and test these feature risks:

1. Known independent projection samples: for a 100 x 100 manual space,
   dimensional back endpoints are x3/x97 and front endpoints x0/x100;
   the centerline remains x50. At `v=.5`, denominator is `.97`, displayed
   y is `48.4536082474`, and width is `96.9072164948`. Flat samples equal the
   unprojected input. Use a documented float tolerance for value comparisons.
2. All 147 playing keys and 24 presets retain unique semantic identities at
   minimum, default, reference and both sides of responsive breakpoints.
   Sample exposed natural centers, accidental centers, front faces, exact
   shared edges, neighboring points and outside-AABB-corner points.
3. AABB-only false positives fail: every dimensional manual has points inside
   its extreme key envelope but outside the visible key that produce no note.
   Accidental overlap always resolves to the accidental first.
4. Both modes preserve control-state bytes, current registrations, held UI and
   MIDI owners and continuous musical history across toggles/resizes. Pointer
   releases after a geometry change still release the original owner; a new
   hidden musical hit is rejected in Rotary/Service.
5. Actual native raster verification checks sloped silhouettes, distinct front
   faces, held state and inset focus under the software renderer at representative
   sizes. A Flat capture retains all live controls with rectangular keys and
   without heavy decorative shading. Key centers and status labels remain
   legible. This is distinct from executing physical devices or accessibility.
6. Existing independent geometry fixtures must be revised only where this
   contract changes them. Preserve original layout dimensions when unchanged;
   do not replace explicit expectations with a call to the production helper.

The A14 primitive/header, A19 layout/hit and A20 renderer assignments implement
successive pieces of this contract. Until they are integrated and their actual
checks pass, this document is a reviewed implementation specification, not
evidence that the new geometry already exists.

# Reference refinement layout contract

Identity: `standalone-sidebar-pedals-v1`; integrator accepted for implementation,
subject to independent tests, over `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`.
This supersedes only the original
[geometry contract's](INTERFACE_GEOMETRY_CONTRACT.md) panel-allocation freeze.
Its projection, shape API, ownership and Flat rules remain authoritative.
This is calculated design acceptance, not an implemented or physical-fidelity pass.

## Allocation and exact arithmetic

Use sidebar pedals **iff `W >= 1400 && H >= 820`**, in both presentations and
with the same common header across workspaces. Otherwise retain the baseline
layout exactly, including short/wide windows. Admission remains finite
`960 <= W <= 8192`, `700 <= H <= 8192`; invalid requests preserve destination.
`show_cabinet` still means width at least 1400; do not confuse it with sidebar mode.

For the active branch, all dimensions below are logical pixels. `clamp` is
inclusive; retain floating-point geometry until rasterization.

```text
d = H - 700
m = clamp(.043W, 48, 72); g = 10
C = W - 2m; K = .311C; P = C - K - g
header = {m,16,C,100}
F = clamp(76 + .12d, 76,110)
R = clamp(168 + .24d,168,236) + 6
performance = {m,126,P,F}
rackY = 126 + F + g; rackW = (P-g)/2
toolbarY = rackY + R + g; toolbarH = 28
Y = toolbarY + 28 + g
U = (H-32-100-F-R-28-36-6g)/2
footer = {m,H-52,C,36}; B = H-52-g
railW = clamp(.15P,156,168)
manual[midiManual] = {m+railW+g,Y+midiManual*(U+g),P-railW-g,U}
Q = clamp(86 + .08d,86,114)
pedals = {m+P+g,B-Q,K,Q}
cabinet = {m+P+g,126,K,B-Q-g-126}
```

`midiManual` is the existing array ordinal 0 or 1, never a MIDI note. Rails
share each manual's y/height; preset panels keep x inset 8, y inset 54,
width `railW-16`, height `U-62`. Existing control placement rules operate in
these parent panels. Both pedal mixture controls stay in the performance panel.

Cabinet art starts at `cabinet.y+48`. Preserve aspect **466:397** and center it
horizontally; its height is
`min((K-16)*397/466, cabinet.height-48-191)`.
The 191-pixel reserve means 61 pixels between art bottom and status top,
at least 116 pixels of status, and 14 pixels below it. Status has x inset 14,
width `K-28`, and ends 14 pixels above cabinet bottom. Existing caption offsets
remain within that reserve. Cabinet and pedal panels are disjoint, separated
by `g`; no cabinet fill, frame, shadow or text may cover pedal ink.

At reference size the recovered 87.28 pixels pay for 10 extra header pixels,
6 extra rack pixels and **35.64 extra pixels per manual**. This favors readable
live controls and deeper keys without reducing the musical inventory.

## Literal acceptance anchors

Key depth means `manual.height-30`, including its front face.

| Window | Sidebar | Manual y / height | Key depth | Pedal y / height |
|---|---:|---:|---:|---:|
| 960×700 | No | 402 / 82 | 52 | 582 / 58 |
| 1280×900 | No | 474 / 138 | 108 | 766 / 74 |
| 1399×819 | No | 444.84 / 115.32 | 85.32 | 691.48 / 67.52 |
| 1400×819 | No | 444.84 / 115.32 | 85.32 | 691.48 / 67.52 |
| 1399×820 | No | 445.2 / 115.6 | 85.6 | 692.4 / 67.6 |
| 1400×820 | Yes | 477.2 / 135.4 | 105.4 | 662.4 / 95.6 |
| 1672×941 | Yes | 520.76 / 174.12 | **144.12** | 773.72 / 105.28 |
| 1920×700 / 8192×700 | No | 402 / 82 | 52 | 582 / 58 |
| 1920×1080 | Yes | 536 / 236 | 206 | 904 / 114 |
| 960×8192 | No | 504 / 3763 | 3733 | 8046 / 86 |
| 8192×8192 | Yes | 536 / 3792 | 3762 | 8016 / 114 |

At 1672×941: cabinet x **1124.831312**, width **475.272688**; racks
y240.92–472.76; toolbar y482.76–510.76; upper keys y542.76–686.88;
lower keys y726.88–871; art y174–565.268792; status height 123.451208;
footer y889–925. The title's painted center is x836 within one raster pixel,
using a symmetric safe interval between tabs/tools and bounded font fitting.
Header controls retain their existing sizes; the Flat toggle moves down 10 pixels.

The [reference](design/atlas-cover-reference.jpg) approximately places cabinet
x1125, upper keys y548–692 and lower keys around y720–867. These are visual
landmarks, not measured hardware. Require native reference depth 144±1 pixels
and cabinet edge 1125±1; retain the remaining rack/vertical-span differences
explicitly. Correct full keyboards, presets, toolbar and honest status prevent
literal image equality.

## Invariants and verification

Preserve 68 ordinary controls including 24 presets, 147 playing keys, 71 Play
focus stops and ten common stops. Retain 47 sound parameters, state4/readers 1–3,
all four banks and release ownership. Sidebar controls are visible in Play;
hidden Play targets reject new input in Rotary/Service. Resize/F7 must preserve
original held owners and produce no musical command by themselves.

Keep the existing `make_keys`, accidental precedence, exact half-open hit
shapes and independent projection oracle. Verify every exposed natural,
accidental and front face, all preset IDs, focus traversal and old-location
hits across both breakpoint axes. Keep minimum/default literals unchanged;
update only authorized wide panel/preset/art expectations, never substitute
production helpers for independent expected values. Inspect native replay's
literal header points after moving Flat.

At 1400×820 the active minima are manual depth 105.4, pedal depth 65.6,
art height 287.4 and status height 116. Both dimensions grow safely thereafter;
exercise 8192 limits and fractional sizes without allocating giant captures.
Native minimum/default/reference/Flat captures must establish visible pedals,
readable labels, focus/held state and truthful audio/MIDI/scanner/rotary status.
Keep detailed device information in its existing interfaces and preserve all
footer focus, pending, error and recovery messages. Compact status line spacing
must also fit the unchanged short/wide 101-pixel card.

# A14 — Live material implementation and native regression repair

Actual worker: `/root/w03_a14_material_impl`, wave 3. Owned files are
`apps/standalone/InstrumentView.cpp` and this note. No commits, publication,
child dispatches, CMake changes, audio changes or shared-document edits were
performed. Inspected HEAD was `d2972a5744c63219f785e118055b7992656cf8b3`;
A13's layout and A15's inspection changes were concurrently present.

Read the standing instructions, complete M0–M9 plan, current session scope,
checkpoint, accepted materials/layout contracts and the relevant atlas review.
Directly opened the original cover/page-409 reference and native v2 Play PNG
with `view_image`. Their SHA-256 identities remain
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` and
`27c1a877ac458dc6775e7fb80f3edadf7b0508f923a5ef8d6cfb5095115847cd`.
The original supplies atmosphere and lighting direction, not correct musical
inventory or a measured physical-material specification.

## Implemented behavior

Charcoal panels now use the accepted warmer gradient and a narrow upper/left
light with dark lower/right edges. Deterministic local-coordinate grain adapts
its spacing and has both a calculated and explicit **2,048-pair maximum per
panel**. Its warm-light alpha is 6–10 and dark alpha 10–18; finite/positive
surface guards precede bounded material work. No texture, dependency, cache or
allocation was added.

Ivory tablets and drawbars have separate pale faces and darker fronts, narrow
specular bands limited to the upper 12%/4 px, and directional edge light.
Selected amber, brown/black/ivory groupings, labels and control bounds remain.
Exposed walnut gains only a three-pixel underside. Natural-key top colors stay
unchanged; their rear recess fades from alpha 90 over 12% of top depth, capped
at 18 px. Front planes are darker and the front highlight is capped at 2 px.
Accidental caps use the specified 61/58/52→20/22/19 gradient. All key layers
still interpolate the original quads; held markers and two-pixel playing-key
focus remain above materials.

The shared `cabinet_art` rectangle remains authoritative. Its three-pixel
recess/rim stays inside the disjoint cabinet panel, above the separate live
pedals. Captions and disconnected facts remain explicit. Compact status rows
now begin at 31/49/67/85, ending at 99 px inside the 101 px legacy minimum.
Sidebar title fitting uses a symmetric safe interval. Flat bypasses new grain,
bevels and shadows; its optional-art fallback also avoids procedural wood.

## Actual verification and observed failure

Builds waited for root's shared-build release. From the repository directory,
used `../build-tools/cmake/data/bin/cmake --build ../build-native --parallel 3
--target hammond_standalone test_standalone_drawing
test_standalone_quad_drawing test_standalone_workspace_raster
test_standalone_scaled_view test_standalone_preset_raster`.
The configured toolchain was GCC Release with SDL 2.32.10 and MIDI disabled.

The initial filtered CTest invocation used `--output-on-failure
--no-tests=error -j 2`: **four of five passed in 21.75 seconds**. Preset raster
reported 14 label-ink failures, exclusively lower-manual naturals at 1400×820
in both presentations. The new fractional row exposed the existing focus
ring's bottom stroke crossing final glyph pixels. The narrow repair opens
that natural-preset frame's bottom while retaining its full-height sides;
accidental clipping and playing-key focus are unchanged. Tests were not edited.

After rebuilding, all three affected suites passed in **21.90 seconds**:

| Suite | Actual observations |
|---|---|
| Preset raster | 192 label/focus, 160 full-size accidental glyph, 752 isolation and 96 state cases; zero failures |
| Scaled view | 168 frames/state checks, 90 clipped frames, 16 focus, 56 Service values/58 lines; zero failures |
| Workspace raster | 150 frames; 108 held, 108 held/focus and 108 front/Flat checks; zero failures |

Workspace raster measured minimum mean top/front contrast of **65.8713 natural
and 15.9033 accidental** sRGB levels. Independent palette arithmetic found
4.9219:1 minimum among the changed normal-label pairs and an eight-level
conservative grain perturbation bound. `git diff --check` passed. Root's
provisional native reference capture was visually inspected, but is not an
accepted gallery or performance result.

Final renderer SHA-256:
`4127c0b2feb9b04f591fa9af82e4a6f3bbc162228205d7d92c8bdcca911ac45f`.
Built app SHA-256:
`ec4387d2d4f7c746ed96bd4b68c8779d86f9e81a709c0dec65f67c168c584b8b`.
Root owns the next same-geometry old/new timing comparison, independent
1.25-scale/material acceptance and source-identified native gallery. No timing,
literal 1:1, physical-device, accessibility or acoustic-fidelity pass is claimed.

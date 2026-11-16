# Reference apron contract — v1

**Status:** proposed for independent admission before implementation. This is a
narrow M9 appearance change, not whole-interface equality or physical fidelity.
Basis: [source record](atlas-reference.json), atlas pp.409–411 and 427–438 as
freshly reviewed in this session's [A05](../development/2026-11-16-preset-library-continuation/notes/A05.md)
and [A06](../development/2026-11-16-preset-library-continuation/notes/A06.md).

## Scope and immutable boundaries

Change only the apron currently painted by
`reference_wood(drawing, mapped({16,887,1640,54}), scale)` in
`paint_reference_composition`. Retain the existing activation predicate:
Dimensional Play, width ≥1400 and height ≥820 within supported layout limits.
Use the existing 1672×941 endpoint mapping without geometry changes.

Define half-open canonical rectangles:

| Identity | x, y, width, height | Meaning |
| --- | --- | --- |
| R | 16, 887, 1640, 54 | Entire apron destination and source crop |
| F | 48, 889, 1556, 36 | Existing live footer, painted later |
| H | 32, 2, 1556, 36 | F in crop-local coordinates |

No other wood call, rim, manual, cap, artwork, geometry, input, control, footer
implementation, overlay order, state, audio or parameter changes are admitted.
Inactive layouts must remain pixel-identical. All live footer text, status,
meter, dirty/pending/recovery cues and subsequent overlays retain their current
paint order and meaning. The historical three-art manifest/compiler and
`ReferenceArt` enum remain unchanged.

## Exact asset and provenance

Create an independent `assets/standalone/reference-apron-v1/` package, compiler
`tools/compile_reference_apron.py`, generated header and private Drawing texture.
Source only `docs/design/atlas-cover-reference.jpg`: 412,664 bytes, 1672×941,
SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
Preserve the JPEG and `atlas-reference.json` byte-for-byte. The source is the
unchanged embedded image object 3 on PDF pages 1/409; its existing generated-art
classification and unresolved upstream rights remain unchanged.

Decode as the existing decoration pipeline: Pillow JPEG defaults, `load()`,
`convert("RGB")`, without EXIF transpose, ICC transformation or resampling.
Require full decoded RGB SHA-256
`07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb`.
The independently reviewed manifest records exact decoder/compressor versions,
source/PDF hashes, rectangles, mask rule, packed/raw byte counts and hashes.

Crop R to **1640×54 RGBA8**, row-major, top-down, pitch **6560**, exactly
**354,240 bytes**. Outside H, copy the original RGB triple and set alpha 255.
Inside H, set **all four bytes to zero**. Thus 32,544 texels retain exact source
RGB and 56,016 texels contain no artwork. H entirely excludes the central
“DESIGN CONCEPT” lettering and its ornament; hidden RGB must not retain it.
No cloning, inpainting, synthetic grain, color adjustment or rearranged pixels.

Store one bounded gzip member with fixed level 9, mtime 0 and empty filename;
freeze its bytes after independent source/mask verification. Ordinary builds
use only Python's standard library to verify the pinned manifest, source bytes,
packed bytes, exact decompressed extent/hash and generated header. Reject bad
hashes, truncation, trailing members/data, oversize streams and input/output
aliasing before replacing output. Source decoding is authoring/verification
only; runtime has no JPEG decoder or asset-file dependency.

## Drawing and fallback

Add `bool Drawing::apron_art(UiRect) const noexcept`, independent of
`reference_art`. Prepare one static `SDL_PIXELFORMAT_RGBA32` texture during
Drawing initialization; release it with that Drawing. Use straight-alpha
`SDL_BLENDMODE_BLEND`, identity RGB/alpha modulation and explicit
`SDL_ScaleModeNearest`. Alpha is binary; nearest sampling prevents interpolation
across the footer hole. Preserve source orientation and aspect mapping dictated
by the existing layout, including unequal-axis stretches. No mipmaps,
premultiplication, tinting, filtering fallback or additional highlights.

One full-source `SDL_RenderCopyF` targets mapped R. Do not derive a new source
rectangle from the caller's clip: SDL owns clipping of the unchanged mapping.
Respect incoming scale, viewport and clip, including enabled empty clips, and
leave their values and renderer blend state unchanged. Reject nonfinite or
nonpositive bounds without drawing. No allocation, texture upload, I/O or model
mutation occurs during painting.

The caller replaces only the named procedural call: if `apron_art` returns
false, execute that original `reference_wood` call with its original arguments.
Texture creation/upload/configuration failure is optional-decoration failure;
controls remain usable. A failed copy also returns false. Verify fallback with
an intentionally unavailable apron texture; its full frame equals baseline.

## Independent raster protocol and genuine baseline

Before changing production painter/Drawing code, independently author and freeze
`reference-apron-v1` fixtures using only existing public UI APIs. Root builds
that exact fixture against the genuine current painter and retains the actual
baseline executable, fixture/source/tree/dependency hashes, command, compiler
and configuration. A reconstructed old branch or candidate fallback is not the
baseline. Build the identical fixture source against the candidate afterward.
If baseline bytes are missing, paired admission is blocked.

Portable transport: `--list` emits the ordered case specification;
`--case N` emits one UTF-8 JSON line followed immediately by width×height×4
uncompressed RGBA8 bytes, top-down with no padding or trailer. Binary stdout
is mandatory on Windows; diagnostics go to stderr. Limit the header to 64 KiB,
each dimension to 4096 and payload to 64 MiB. Header includes protocol/case ID,
logical/output dimensions, actual scale/viewport/clip and enable flag, renderer
identity, deterministic complete UI/info state and byte count. Reject malformed,
short or extra bytes. The independent checker derives masks from this contract;
the producer must not emit its own permitted-change mask.

Freeze **25 paired cases**, not a Cartesian matrix. Unless specified, use
canonical size, scale 1, origin (0,0), full viewport, no clip, fixed stopped
audio and deterministic state. Fix all remaining inputs in the fixture manifest
before the baseline build.

| Cases | Required distinction |
| --- | --- |
| 1–5 | 1672×941 reference; 1400×820 minimum active; 1920×1080; 2200×820; 1400×1100 |
| 6–8 | Canonical layout with renderer scales (1.5,1.5), (2,2), (1.25,1.5) |
| 9 | Canonical, scale 1.5, physical viewport origin (13,17); full companion for 10–15 |
| 10–13 | Case 9 with four-pixel physical clip strips straddling each apron outer edge |
| 14–15 | Case 9 with enabled empty clip; positive-area clip disjoint from apron |
| 16 | Canonical output/viewport cropped to height 880, hiding the complete apron |
| 17 | Running audio, nonzero meter, dirty controls and clipped-sample indication |
| 18 | Pending preset and controls, fixed focus, held notes |
| 19 | Input recovery and explicit status message |
| 20 | Audio settings overlay open |
| 21–22 | Inactive Play at 1399×941 and 1672×819 |
| 23–25 | Canonical Flat Play, Rotary and Service |

For cases 9–15, freeze both output and actual translated viewport extents with
at least two physical pixels below the transformed bottom of R. The four strip
cases must each retain nonempty interior and protected exterior populations
after output/viewport intersection; R ending at the logical layout bottom must
not make bottom-edge containment vacuous.

## Frozen acceptance

At canonical size/scale/origin, candidate case 1 equals decoded source RGB at
**every pixel in R minus F**, with alpha 255; every pixel of F equals baseline.
This is exact equality, not a similarity score. Independently compare the
compiled RGBA bytes against the source/mask rule as a separate gate.

Add a bounded candidate-only direct `Drawing::apron_art` probe before any footer
paint, over two distinct opaque backdrops. At canonical size require every H
pixel to retain its backdrop, every opaque texel to equal original source RGB,
and incoming renderer scale/viewport/clip/blend state to remain unchanged.
The 25 paired UI cases alone cannot test this alpha behavior because their
opaque live footer overwrites H. This direct probe does not replace the genuine
before/candidate fixture or add more paired cases.

For every paired case, all differences must lie within the mapped R physical
envelope: floor of transformed left/top through ceil of transformed right/bottom,
half-open, intersected with output, actual viewport and enabled clip. No extra
halo is allowed. Reproduce existing float endpoint mapping; use queried renderer
transforms, not nominal DPI alone. Pixels whose centers lie inside mapped F
must equal baseline, including every footer state. Cases 14–16 and 21–25 require
whole-frame byte equality. Visible active cases must contain changed apron pixels.

For clips, verify containment and unchanged renderer state; report clipped/full
companion interior differences without claiming cross-clip resampling equality.
Sampling is the frozen SDL nearest-copy behavior, not an untested custom kernel.
Repeat canonical rendering after another state and on a fresh Drawing; require
identical pixels. Independently inspect genuine native captures at reference,
minimum-active and 1920×1080 sizes for seams, grain, footer legibility and absent
baked text. Preserve failures and source/executable/state/pixel identities.
Real display/DPI/input/accessibility and literal whole-interface 1:1 remain
separate gates; dummy-SDL evidence must be labeled accordingly.

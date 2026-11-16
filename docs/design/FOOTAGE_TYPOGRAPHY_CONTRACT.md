# Live manual footage typography — T1 contract candidate

**Root-authored proposal; independent admission and a genuine pre-edit fixture are required before implementation.** This extends the reviewed [material/type proposal](REFERENCE_MATERIAL_TYPE_NEXT.md), using the unchanged reference JPEG and existing ASCII Serif atlas. It does not admit whole-interface 1:1, alter musical labels, or change a control.

## Scope and source inputs

Only the eighteen manual drawbars in wide Dimensional Play use the new private helper. The existing activation, `UiModel`, label/value/hit rectangles, wells/caps, two pedal-mixture labels, all other text, focus, input routes, fonts and assets remain unchanged. Retain the complete strings from `kUiFootageLabels`: `16'`, `5 1/3'`, `8'`, `4'`, `2 2/3'`, `2'`, `1 3/5'`, `1 1/3'`, `1'`. Never copy the concept image's incorrect musical labels.

The prior source uses Serif19 and `centered`; mixed fractions fit down to15 at canonical size and have a higher baseline. Reference observations retain ordinary-label ink at y473–488, versus current y470–483. These are image observations, not a universal readability metric. Preserve original measurements and every observed failure.

`FontData.h` SHA-256 is `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802`; Serif pixel height40/ascent38. Digits advance25 atlas pixels, slash13, apostrophe11. `Drawing::text` remains unchanged, including its transparent-gutter handling. The genuine before painter/binaries must be captured after accepted Lower work and before this edit, with source/tree/fixture/dependency hashes. The initial pre-Lower binaries do not substitute for this transition.

## Exact run geometry

Use existing binary32 composition scales `sx=W/1672`, `sy=H/941`, `f=min(sx,sy)` and binary32 arithmetic in written evaluation order. The unchanged canonical label box is46×23 at y467. All sizes below multiply by f; all baseline offsets from the stored label-box y multiply by sy; the two gaps multiply by sx. Center the measured complete run on the stored label box, not a guessed canonical center.

| Run | Serif size | Baseline offset from label-box y | Advance at f=1 |
| --- | ---: | ---: | ---: |
| Whole numeral |20.5|21.5|12.8125 per digit|
| Fraction numerator |13|15.5|8.125|
| Slash |16|19.5|5.2|
| Fraction denominator |13|21.5|8.125|
| Apostrophe |20.5|21.5|5.6375|

Ordinary complete strings use one20.5-sized text call and baseline21.5. Mixed labels use five consecutive ASCII string-view runs, with a0.5*sx gap after the whole numeral and another before the apostrophe. Measure each run through unchanged `Drawing::text_width`; sum its actual binary32 widths and the two gaps left-to-right. A mixed run is mathematically **39.9*f + sx**, not40.9*sx under unequal composition scales. `16'` is31.2625*f and single-numeral footages18.45*f. Since f≤sx, every recognized run fits the42*sx padded width. These decimal sums explain geometry; actual runtime width uses measured advances.

Set start x=`box.x+(box.width-total_width)/2`. For each run set size=`nominal_size*f`, baseline=`box.y+nominal_offset*sy`, top=`baseline-(38*size)/40` and call unchanged `Drawing::text` in the original ivory color. Advance x by the same measured width, then the explicitly located gap. No independent horizontal stretching, Unicode glyph, font asset, copied image lettering or per-character fitting is allowed. Use string views/fixed local values, no new heap allocation. Recognize only the exact nine current strings; any unknown future label takes the original fitted complete-string fallback. Preserve value text and all subsequent painting.

## Independent support and fixtures

Freeze and build a new native fixture against the genuine current painter before editing it. It must capture both manuals with the same model state and enumerate all nine strings, all eighteen manual focus identities, values0/4/8 and both registration routes. Keep original66 percussion and32 Lower fixtures unchanged. The independent checker derives old centered-text and new run glyph quads from font metrics and actual binary32 layout. It must not import the painter or derive its mask from changed pixels. Include `Drawing::text` subpixel gutter logic, renderer scale, physical viewport/clip, and at most one device pixel of raster envelope around the old/new union. Every other RGBA pixel must be exact; retain failures as lossless images. A whole-label-box or whole-panel permission mask is insufficient.

The frozen new matrix must cover reference1672×941, minimum1400×820,1920×1080, unequal1920×820 and1400×1080, fractional logical dimensions, renderer scales0.75/1.25 and unequal1.5×2, positive/negative viewports, partial glyph clips, enabled-empty/disjoint clips, Flat/Rotary/Service, widths/heights immediately below wide activation, and64×64 output crops at maximum8192 geometry. A reviewer must spell out exact case inventory and metadata before painter editing. Root coordinates its build and preserves the executable/source.

Assert literal complete labels and correct1 3/5', unchanged controls/model/parameters, strong foreground glyph ink, no glyph clipping/collision with values or neighboring labels, all focus outlines, renderer state restoration, deterministic repeats and exact inactive whole frames. Keep fixed transparent-gutter support and retained caption/value geometry. Compare retained Upper/Lower material statistics with the pre-type stage separately; no panel material is modified. Existing fixture expectations must not be weakened to accommodate new typography. If an old fixture hardcodes the old glyph placement, record and independently review a versioned assertion repair retaining the old fixture result.

## Visual and resource acceptance

Inspect actual full frames at reference and minimum active sizes plus an unequal-aspect case; inspect18 live labels at native scale, not only enlarged crops. New ordinary-label ink should occupy the reference-led y473–488 neighborhood at canonical size; report every label's ink bounds and counts instead of concealing different glyphs behind aggregate scores. Legibility, correct full strings and separation from values/focus take precedence over an image silhouette. A numeric containment pass cannot override a clipped or unreadable numerator, denominator, slash or apostrophe. Real display/DPI/accessibility remains a separate observed journey.

The helper performs at most five text calls per mixed label and one per ordinary label: at most90 across eighteen labels (the exact current inventory is50 calls). Work/storage are fixed by the nine recognized strings. No new SDL surface/texture/upload/font allocation, file access, clock, random source or audio/state work occurs. Source bounds do not establish SDL allocation behavior or a frame deadline. Preserve any failing evidence; changes to run metrics/support require a new version and independent review before rerunning. Whole-interface1:1 remains unmet until the full objective passes independently.

## Next step

Independent reviewer must verify the source arithmetic and exact current call count, choose/freeze the native matrix, and admit this contract hash or return corrections. No production typography edit is authorized by this proposal alone.

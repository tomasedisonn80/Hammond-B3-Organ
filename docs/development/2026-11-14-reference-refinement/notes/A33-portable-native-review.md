# A33 — Independent native portability review

## Scope and identity

Read the standing agent rules, current scope/checkpoint/manifest and complete
M0–M9 plan. Independently reviewed the new native R2/R3 implementations, both
batch probes, lifecycle/propagation/allocation tests, native pending/material
rasters, reference-layout test, painted diagnostics and their CMake/CI contracts.
[The review inventory](../reports/A33-portable-native-review.json) identifies all
21 inspected source/configuration files against published `2e161dc`. Eighteen
of nineteen inputs represented in root's coherent build inventory match exactly;
the allocation test differs only by one removed final LF. Independently appending
that byte reproduces its qualified SHA-256. All 21 files match the publication.
This review owns only this note and the A33 reports; product, workflow and shared
builds were untouched.

## Findings

No concrete portability defect requiring a source repair was identified.
Sample positions, turn counts and counters use fixed-width integer types;
bounded admission precedes narrowing or signed arithmetic. Product calculations
use binary64 and explicit `std::fma`, without a reliance on extended `long double`
or a project fast-math option. Signed byte directions pass through ordinary
integers in the text probes, avoiding character extraction. CMake binds each
Python acceptance suite to its built executable through `$<TARGET_FILE:…>`;
there is no hard-coded executable suffix or shell-based launch.

The allocation test uses checked `malloc`/`std::align` storage, matches ordinary,
aligned, sized and nothrow replacement families, and supplies compiler-specific
noinline declarations. Its padding-inclusive snapshots compare the same object
before/after a nonmutating or rejected call, rather than distinct objects whose
padding could differ. Native rasters select `SDL_MAIN_HANDLED`, call
`SDL_SetMainReady`, use software surfaces without hardware initialization and
read byte-order-defined RGBA32 pixels. Ordinary geometry/raster checks do not
freeze a platform-specific floating-point or pixel hash. The legacy binary
snapshot is a separate optional evidence mode.

## Executed precision diagnostic

The independent propagation and material checks use `long double`, so a bounded
scratch-only diagnostic replaced that type and `L` literal suffixes with
`double` in those tests and their local assertion helper. It kept every tolerance
and all built production inputs unchanged. This specifically tests sensitivity
to reduced oracle precision; it is not a compiler or operating-system emulator.

Both variants compiled with GCC 14.2.0, C++20, Release optimization and the
project's complete strict warning set, with no diagnostics. Propagation passed
65,664 history queries, 163 rejections and 369 solved paths; maximum constant-root
error was **1.0404871408908889e-14 seconds**, with at most 41 evaluations.
Material acceptance passed **901 checks / 56 frames**, including all 588 held-key
cases and 6,543,712 outside-clip pixels. Run times were 0.016 and 3.915 seconds.
[Exact argv, variant transformations, library/object identities, exits and raw
outputs](../reports/A33-binary64-diagnostic.json) are retained.

## Required next evidence

The actual workflow uses strict GCC/AppleClang warnings and MSVC
`/W4 /WX /permissive- /Zc:__cplusplus`, all at C++20. Only GCC is available here.
Execute the newly published head's macOS/Windows and Linux gates, retaining any
compiler/libm/runtime failures; this review cannot close those platform gates or
the separately blocked local LSan gate. Root's original 154/155 suite result and
separate repaired capture-install recheck remain distinct observations.

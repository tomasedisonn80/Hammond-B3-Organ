# A15 — wide Dimensional painter implementation

Implemented `standalone-wide-legibility-v1` from `docs/PRODUCT_VISUAL_REFINEMENT.md` in `apps/standalone/InstrumentView.cpp`. Activation is `layout.sidebar_pedals && presentation != Flat`; existing compact/Flat drawing branches remain intact. No layout, hit target, control, font, asset, dependency, parameter, audio, or Drawing API changes.

Manual racks now use complete fitted ASCII footage in the upper 20 px of the original label row (17 px starting size, 2 px horizontal padding), 32 px caps with 8 px fronts, and 14 px numeric ink. The pinned sans digit metrics fit the unchanged 16 px numeric row. Local material must remain between `label.y + 21` and `value.y - 1`; cap shadows are geometrically intersected with that strip. Invalid/nonfinite local geometry is rejected. Endpoint containment uses the strip's genuine margins rather than float-sensitive equivalence between separately calculated cap/slot endpoints. Labels/readouts are painted after materials, with existing focus ink still last.

Rack captions use separate fitted 11.5 px `EDIT BANK` and `SOUNDING` rows. Sounding captions read the copied applied controls, including fixed, A#, B, cancelled, and unavailable routes. Static string views and a stack digit avoid new per-draw heap allocations.

Idle natural keys on the two manuals gain warm left and dark right bands interpolated from their original top-quad side edges. Both bands are 1 px wide and inset 1 px measured normal to the sloping edge, spanning 8–88% of top depth. Rear-recess starting alpha is 70. Held, accidental, pedal, front-face, focus, and compact/Flat paint paths remain unchanged.

Validation: strict C++20 syntax-only compilation passed with `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`; `git diff --check` passed. No shared build was run. Independent raster comparisons, fractional/end-value checks, timing, final screenshots, and visual acceptance remain assigned to later agents/root; this note makes no pixel-identity or reference-equivalence claim.

Baseline painter retained outside the repository at `/workspace/scratch/5b7d983ac078/a15-instrument-view-before.cpp`, SHA-256 `aae710a6e4eb8d7eccfe8fd7e5cf3cb98109ee1bc0143229e5b5b8b63f3c7a4c`. Implemented painter SHA-256: `9e115750bde03f81e396e809a1ad150eefb3c057391372239f6248b3ce9fbf4e`.

Next: A18 may take painter ownership for its separately scoped MIDI overlay; root owns integration, acceptance, documentation, commits, and push.

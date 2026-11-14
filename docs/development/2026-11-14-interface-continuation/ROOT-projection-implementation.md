# Integrator implementation: shared keyboard perspective

After A13 completed the workspace model, the integrator implemented the accepted
manual homography in `UiModel.cpp`: a 0.94 back/front ratio, shared ordinal-derived
edges, actual hit/top/front quads and bounded 6–18 pixel front planes. Flat mode
retains rectangular top planes and empty fronts; the pedalboard keeps rectangular
plan geometry and dimensional fronts. All note identities and control meanings
remain unchanged. Painting will consume these same shapes in the next renderer
assignment; bounding boxes are only envelopes, not invisible playable corners.

Strict GCC14 compilation with all project warning flags passed. The existing
A13 focused workspace target rebuilt against this source and passed1/1 in0.01s.
That recheck covers continued workspace/input behavior; independent numerical,
all-key/boundary and raster qualification belongs to A19 and later acceptance.
No current screenshot is claimed to show this geometry until renderer integration.

This is integrator work and does not count as an additional dispatched worker.

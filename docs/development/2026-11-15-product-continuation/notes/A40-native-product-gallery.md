# A40 — Actual native product gallery

**Scope.** Added only `examples/demos/standalone-product-preview-v1/` and this
note. Preserved every historical gallery. Root's published capture source is
`d556da017ea0a5d4f2d231416782dbc5066e58c2`, tree
`a3150fd2489a50a430b02c01eadd5e0c180bc7f9`; executable SHA-256
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.

**Execution.** From the shared repository, after root's explicit source/build
freeze, ran the unchanged A39-qualified `capture_standalone_interface.py`
(`83c214d6…`) with the qualified executable, build root, supplied report and
`--dummy-sdl`. All eight normal cases passed on first execution. Ran the
overlay script, retained as `midi-overlay/capture.py`, for three separately admitted
modal cases; all passed first execution. Exact commands, environment, cwd,
timings, source/tool/binary/build/input identities and raw diagnostics/stdout/
stderr are retained in each provenance/manifest. Python 3.12.14/Pillow 13.0.0;
Linux Release, SDL 2.32.10 dummy audio/video/software, MIDI backend OFF.

**Checks.** Normal frames retain Upper 60/64, Lower 67 and pedal 3 while editing
Upper B 16-foot 7→8; complete controls, pending flags and final acknowledgment
pass. Modal runs establish the same holds/edit, then Ctrl+M performs scoped
`ReleaseUiNotes`: final owners are empty and acknowledged, individual Note Off
count remains zero. All eleven focus indices were actually painted; replay
path is `0..10,0,10,9,8,7`. Illustrative CLI 20/100/Inverted remains
selected=configured, active null, pending false. Device/discovery/packet/decoder
activity stays zero. All eleven processes exit 0, output no stderr/stdout,
report no audio/Session faults and finish with clean joined shutdown.

Every PNG exactly matches its decoded native BMP pixels; BMP/PNG/pixel hashes
are retained. Only owned BMP intermediates were removed after verification.
Both payloads report every recorded input unchanged (108 production files,
13 build inputs). The older supplied build receipt qualifies matching
production inputs; it does not attest later test-only CMake changes. A40 viewed
all eleven originals plus the atlas reference; 277 historical files remain
byte-identical. README captions distinguish the
39-file normal payload from the independent 18-file overlay payload.

**Limits/handoff.** A41 independently admits these files before README promotion.
No staged/configured divergence, Apply/reconnect, active MIDI, physical devices,
display, accessibility, latency/deadline or measured fidelity claim. Literal
1:1 remains unmet; Engine stays nominal/dry. Root owns shared status/publication.

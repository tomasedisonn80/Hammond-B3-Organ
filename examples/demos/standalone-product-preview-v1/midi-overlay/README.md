# Separate native MIDI-overlay capture

These three PNGs are actual native application output at
`d556da017ea0a5d4f2d231416782dbc5066e58c2`, executable SHA-256
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.
See the [complete gallery and captions](../README.md),
[capture provenance](provenance.json), [18-file manifest](manifest.json) and
[retained authoring script](capture.py).

This payload uses `standalone-product-midi-overlay-capture-v1`. It is separate
from the parent normal gallery's no-overlay/held-note contract. The compiled
MIDI backend is unavailable before and after shutdown, and no native discovery,
device callback, MIDI packet or decoder activity occurred. SDL audio/video are
explicitly dummy and rendering is software.

The CLI supplies illustrative calibration minimum 20, maximum 100 and Inverted.
The UI replay holds Upper 60/64, Lower 67 and pedal 3, changes retained Upper B
16-foot 7 → 8, and opens MIDI with Ctrl+M. The real modal-entry path submits
`ReleaseUiNotes`; final held targets are empty and acknowledged, without
incrementing individual Note Off counters. No Apply, Save or MIDI-script
transport is used.

All eleven modal focus indices are present in actual painted observations.
The complete retained replay path is `0,1,2,3,4,5,6,7,8,9,10,0,10,9,8,7`.
Final focus is expression direction. Selected and configured calibration stay
equal, active calibration is null, and reconnect/release pending stay false.
The run does not demonstrate staged/configured divergence or Apply/reconnect.

The overlay validator checks real audio progress; zero recorded audio and
Session faults; complete musical controls and immutable state-file bytes;
held-state/live-edit observations before modal entry; acknowledged empty owners;
focus traversal; selected/configured/active/pending calibration; exact final
paint/screenshot equality; and unchanged source/build/executable/tool inputs.
Each PNG preserves every decoded native BMP pixel; original BMP, PNG and
decoded-pixel hashes are retained. Only owned BMPs were removed after verification.

The manifest binds this payload's script, inputs, raw diagnostics/stdout/stderr,
images and provenance. It excludes itself and subsequently authored README/review
files. The parent manifest neither includes this directory nor qualifies this
modal contract. Historical galleries remain unchanged.

The settings are not measured pedal endpoints. No hardware, physical display,
latency/deadline, accessibility, literal 1:1 reference or measured instrument
claim follows. The native program remains a nominal dry organ with inactive MIDI.

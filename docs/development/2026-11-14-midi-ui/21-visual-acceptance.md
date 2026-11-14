# A21 — Native visual acceptance review

Actual worker: `/root/w04_a21_visual_acceptance`; MIDI/UI wave 4,
assignment 21. Owned paths are this note and
[`docs/reviews/MIDI_UI_REFERENCE_REVIEW.md`](../../reviews/MIDI_UI_REFERENCE_REVIEW.md).
No production code, original image, other worker's note, shared status or
session ledger was modified. No commit or subagent was created.

## Result

Completed an independent comparison of the exact 1672 × 941 atlas JPEG with
the actual A17 1672 × 941, 1280 × 900, 960 × 700 and minimum MIDI-modal native
captures. Opened every image with the image viewer. The review records measured
composition, actual visible key inventory, material/typographic differences,
all 46 dynamic player controls, the eight-control MIDI modal mapping and
prioritized tasks for A29.

The recognizable composition and corrected musical inventory are present.
The full text-legibility gate and one-to-one appearance goal are **not met**.
The cabinet retains `CABINET REFERENCE` and `ROTARY AUDIO NOT CONNECTED`, and
the UI preserves nominal expression/mixture labels and 61 + 61 + 25 playing
keys. No unsupported scanner/rotary/microphone control or baked interactive
control was found in the inspected renderer.

The main blocking finding is a narrow-glyph raster failure, not only small
font preference: `l`/`i` are three pixels wide in the 32-pixel Sans atlas and
`-` is three pixels high. At 10.5-pixel MIDI help size their destination extent
is 0.984375 pixels; at the 9.5-pixel footer size it is 0.890625. The captured
pixels contain only panel background at the expected `l` in `Close`, and
`--list-midi` loses multiple glyphs/hyphens. Nearest-neighbor enlargement
confirms that the ink is absent in the original raster.

A29 should include the atlas's existing two-pixel transparent padding in the
source/destination rectangles with matching bearing offsets and unchanged
advances. Acceptance calls for a real SDL software-renderer drawing test of
`l`, `i`, `-` separately at 9, 9.5 and 10.5 pixels on a known background, with
nonzero ink for every glyph, followed by inspection of the exact modal/footer
copy and the other required sizes. Linear texture sampling is already enabled.

Other concrete tasks are the contracted explicit MIDI Refresh, inspectable
long port identity, and the wide left wood strip's roughly 3× horizontal
stretch. Material work must preserve control-free art boundaries, dynamic
controls, corrected legends, rectangular hit geometry and factual captions.

## Evidence and verification executed

Base HEAD: `7b36cfac2565397191b3df5e07112611e7f1b0e1`; concurrent uncommitted
MIDI/UI work was present and was preserved. Inspected `AGENTS.md`, current
scope/status/plan pointers, `REFERENCE_UI_DESIGN.md`, `REFERENCE_ART_ASSETS.md`,
A15/A17 notes, the recorded capture commands/diagnostics and the corresponding
`Drawing`, `InstrumentView`, `UiModel`, `main` and font-atlas source.

The input directory is
`/workspace/scratch/cd4bd06ce68f/a17-render-checks/`. Independent Python/Pillow
reads verified each PNG's dimensions, SHA-256 and decoded RGBA SHA-256 against
`capture-record.json`. All four matched. Every recorded current source file,
the original JPEG, art manifest and binary matched its capture-record hash
when checked. Native binary SHA-256:
`072f52ad299592f997af2aaeb2a140a3417e4a77542dd6afbfbae9fd4a60eb4b`.
The review retains all four image hashes and source coordinates.

Read-only pixel scans below the accidentals and through their top planes
counted 36 natural and 25 accidental spans on each manual, and 15 natural and
10 accidental spans on pedals, at all three player sizes. The source key
generator and draw loop independently confirm those counts. The modal source
mapping matches main's pointer/keyboard/focus order exactly; the retained
replay shows selected channels 2/3/4 and focus on Apply without applying them.

Used a Python script to read the 95 Sans glyph records from `FontData.h`,
calculate the actual SDL destination rectangles and inspect the corresponding
PNG pixels. Three nearest-neighbor inspection crops were written only to
`/workspace/scratch/cd4bd06ce68f/a21-visual-review/`; original captures were
unchanged and the crops are not replacement capture evidence.

No extra native capture or broad test rerun was needed to reproduce the named
visual issue. A21 did not rerun or claim A17's smoke results. The recorded
three smoke passes use dummy audio/video and the SDL software renderer. The
MIDI replay returned 1 because `/dev/snd/seq` was unavailable; delivered events
and a visible error modal do not make it a passed MIDI backend gate. The
earlier unsupported replay `M` key remains recorded.

Both new documents passed the local-link existence check (six links total).
`git diff --no-index --check /dev/null <owned-file>` emitted no whitespace
diagnostics for either file; its exit 1 reflects the new-file difference.

## Remaining boundary and handoff

The [full review](../../reviews/MIDI_UI_REFERENCE_REVIEW.md) is the actionable
A29 handoff: first repair thin-glyph raster coverage, then coordinate Refresh/
exact-name affordances and material refinements. A28 owns durable capture
publication. The integrator owns coherent rebuilt-source qualification,
native breakpoint/gesture/mixed-owner/modal recovery evidence and publication.
Static-size images do not qualify live resize transitions, physical devices,
screen readers, measured sound or one-to-one reference fidelity.

# MIDI input and reference-led interface scope

Session: `2026-11-14-midi-ui`; starts at `0f7b90037e51e101d8fa0bfe31af40209d751659`.

Advance the next independent M9 product phase: external MIDI input and native interface refinement. Read [the complete plan](PLAN.md), [next steps](NEXT_STEPS.md), [standalone session](STANDALONE_SESSION.md) and [UI contract](STANDALONE_UI.md). Preserve all 45 public controls, `B3CONTROLS3`, the nominal sound engine, profile, scanner/rotary research modules and every preceding session ledger.

## MIDI boundary to freeze before implementation

- Optional, explicitly enabled, pinned RtMidi 6.0.0 backend, Linux ALSA, Windows WinMM, macOS CoreMIDI. Normal builds remain dependency-free. All connection, enumeration, allocation and close/join work stays outside audio processing.
- One selected physical input port, with three explicitly configured distinct wire channels (defaults 1 upper, 2 lower, 3 pedals; selectable from 1 through 16). Map to reserved internal owner channels 1, 2 and 3, leaving channel 0 exclusively UI-owned. Other wire channels are ignored with visible diagnostics.
- Bounded device inbox, one backend producer and one main-thread consumer; only the main thread calls Session::post. Freeze arrival-order, timestamp/late policy, overflow/disconnect/restart behavior and exact controller mapping before authoring. Existing Session applies events at the next callback boundary; do not promise sample-accurate hardware acquisition.
- Disconnect and device recovery release device-owned notes without touching UI holds. Full Session overflow retains its pre-existing global emergency recovery contract. Quiesce the backend before clearing or destroying its queue.

## Visual boundary

The exact supplied reference is the atlas cover/page 409 generated concept, retained at [atlas-cover-reference.jpg](design/atlas-cover-reference.jpg). Source PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. It defines appearance, while chapter 067 explicitly rejects using its generated legends/key counts as engineering authority.

Develop a native reference-oriented player layout with warm walnut cheeks, charcoal panels, brass legends, layered caps/key fronts, adjacent drawbar banks, two manuals and a right cabinet composition. Keep actual control text and state editable, preserve 61+61 keys and 25 pedals, and make unsupported scanner/rotary behavior explicit. No static reference screenshot may substitute for a working instrument or an observed application capture. If using source artwork for decoration, separate it from interactive controls and retain exact provenance.

Retain keyboard navigation, resize behavior, independent EDIT/SOUNDING banks, focus recovery and honest unmeasured labels. Observe actual screenshots at multiple supported sizes and compare with the source; report residual differences instead of asserting unmeasured pixel equality.

## Work and publication

The new [actual assignment manifest](development/2026-11-14-midi-ui/assignments.json) records sixty newly dispatched workers in ten logical waves, two batches of at most three per wave. Shared files belong to the integrator; subagents own explicit paths and evidence notes. Integrate code and independent review, freeze source for qualification, update README/status/next steps/development log/AGENTS, then commit and push to main with observed remote identity. Do not force-push or replace concurrent work.

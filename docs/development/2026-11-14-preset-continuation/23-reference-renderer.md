# A23 — native preset renderer and reference materials

Assignment `/root/w04_a23_reference_renderer`, logical wave 4, completed
2026-11-14. Owned executable change: `apps/standalone/InstrumentView.cpp`.
Owned evidence: this note and
[PRESET_RENDERER_IMPLEMENTATION.md](../../reviews/PRESET_RENDERER_IMPLEMENTATION.md).
No child workers, commit, push or shared root-document edits were made.

Read repository instructions, project plan, atlas review, frozen preset
selection/core/UI contracts and A18's stable Session/UI-model handoff. Visually
viewed the exact atlas-cover JPEG and historical 1672×941 native capture before
editing. Model, core, state/parameter identity, palette header and `main.cpp`
remain untouched by A23; the Help modal text belongs to `InstrumentView.cpp`.

Implemented both always-visible reversed preset octaves from the shared model
rectangles: naturals before accidentals, actual applied selection through the
checked helper, momentary/unlatched C, separate amber desired-pending outline,
separate two-tone focus, fixed/adjustable/Cancelled captions and full focused
descriptions. Corrected fixed-aware Upper-B percussion eligibility and Help.
Removed the old cheek key count and PLAY/CANCEL paint assumptions. Improved
charcoal texture, tablet/cap depth, deep sockets, 3.5-unit metallic stems and
key fronts while preserving wood/cabinet artwork and all playing-key geometry.

The first actual raster exposed a C# focus-label occlusion. Corrected it by
giving the original label rectangle/material foreground priority within the
final focus treatment, preserving the contracted focus/hit bounds. Initial
sources, pixels and executable remain under `/tmp/hammond-preset-a23/` with
`-initial` names. Tiny fitted sharp labels remain an explicit review limitation.

Built a fresh copied native source with GNU 14.2.0, CMake 4.4.4, strict warning
flags, pinned SDL 2.32.10, standalone On, MIDI Off and local `SDL_ALSA=OFF`.
The observed base was `35554c068492fe2b20c1f8a602d8354ae762dc42`, plus the
copied uncommitted preset dependencies. Final source manifest SHA-256:
`542bb5016a032791dc629a6b3e1cfd4e25c3531dea8f4a124743149fed8ea419`.
Final renderer SHA-256:
`23e8a2421dbec36dd96b0cbc0839612bab236b2b17ee6ead733327eaa9f453cb`.
Final executable SHA-256:
`c06d6f77b07efc9f30ec4644de123d7a9714029b1ce3ffe26091f79710ee2bd0`.
All 66 checked copied native source/header files matched the live source after
the run. No preserved baseline build was rebuilt.

Five final real native processes passed with explicit SDL dummy audio/video
and software rendering. Captures are
`/tmp/hammond-preset-a23/captures/fixed-focus-1672x941.png`,
`fixed-focus-1280x900.png`, `fixed-focus-960x700.png`,
`cancel-1672x941.png` and `help-960x700.png`. All exited 0, delivered their
600 ms input scripts and reported replay success; the fixed-focus frames
captured held Upper notes 60/64. PNG RGB bytes match the original app BMPs.
The review retains exact commands, image hashes and concrete visual findings;
`capture-manifest.json` retains full arguments and runtime identities.

The final native frames and rail crops were inspected and handed to A25.
`git diff --check` passed for the owned source. No old native Python gate was
run before A28's diagnostics update. No local Clang, responsive-boundary,
pending/rejected raster, physical device, native accessibility or literal 1:1
pass is claimed. Source perspective, taller keybeds, denser caps/tablets,
larger labels and header/rack proportions remain concrete visual differences.
Independent A25 acceptance, A38 refinement and the final gallery/README,
coherent qualification and publication remain with their assigned owners.

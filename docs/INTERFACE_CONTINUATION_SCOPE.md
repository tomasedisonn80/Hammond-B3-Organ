# Native interface continuation scope

Session: [2026-11-14-interface-continuation](development/2026-11-14-interface-continuation/README.md).
Starting published source: `d493e998e5dd7cf44db46854e87309745063ac54`.
Status: workspace, geometry and inspection contracts accepted for implementation after wave-2 cross-review. Execution gates remain pending.

## Goal

Continue dependency-ready M9 work from the atlas's interface chapters (PDF
409-444): a live reference-led instrument with Play, Rotary and Service
workspaces, clearer keyboard depth and panel materials, inspectable actual
signal-path/model status, and usable keyboard/pointer navigation at supported
sizes. Preserve the working fixed registrations, all 47 sound parameters,
`B3CONTROLS4` and readers 1-3, all core models and the other tracks.

The source picture is an unchanged concept image. The target is its walnut,
charcoal and brass composition, light tablets, adjacent drawbar racks, dimensional
manuals and cabinet. Actual controls, labels, focus and held states are drawn
from live copied state. The concept's wrong musical labels and shorter playing
inventory cannot replace the real instrument's correct controls. Literal 1:1
equality remains an explicit visual acceptance requirement, not a claim made
because reference pixels have been included.

## Required behavior

1. **Three real workspaces.** Play retains all current playing and control
   functions. Rotary provides an inspectable cabinet/reference view and states
   that rotary audio is not connected. Service exposes actual nominal model,
   registration, audio/MIDI and signal-path information. Read-only facts must
   never masquerade as editable audio parameters or measured hardware values.
2. **One source for input and paint geometry.** Navigation and new dimensional
   keys share their geometry with hit testing. Pointer, keyboard, focus and
   resize behavior remain consistent at minimum, default, reference and extreme
   supported window sizes. Flat presentation, if added, uses identical sound
   controls and independent presentation state.
3. **Sound continuity.** Changing workspaces/presentation emits no sound
   commands, resets no engine history and recalls no control snapshot. Held
   computer keys and pointer releases remain paired across navigation. Hidden
   controls cannot receive new pointer or focus activations. Existing MIDI
   ownership, input failure recovery, Panic, audio settings and Save/Load remain
   operational and explicitly available.
4. **Presentation state stays outside sound state.** New view choices do not
   append sound parameter IDs or change saved-control bytes. Diagnostic additions
   retain existing fields and distinguish presentation observations from sound
   state. No new physical-model claims or fake sensor telemetry.
5. **Reference design remains reviewable.** Retain actual native screenshots
   for all workspaces and supported representative sizes, the exact source
   identity, executable and replay inputs. Compare them with the original
   picture, state residual differences and update the main README to the new
   verified gallery.
6. **Bounded execution and storage.** Reuse a single shared source checkout,
   separately acquired pinned dependencies and a small number of builds. Do
   not clone the repository or SDK per assignment. Keep compact source-identified
   reports and representative captures; retain failures and delete only this
   session's reproducible temporary outputs after review.

## Ownership and acceptance

The integrator owns shared documents, manifests, source freezes, integration,
commits and publication. Workers own expressly assigned files. The new manifest
records only this run's actual 60 distinct worker identities in ten waves of six;
the concurrency limit requires two batches per wave. Earlier session identities
remain separate history.

Wave 1 reads all 500 pages in six disjoint ranges. Wave 2 freezes the presentation,
inspection-data and geometry contracts and reviews the current baseline. Later
waves implement those contracts, independently exercise input/state/raster
behavior, review exact visual differences, qualify package and source boundaries,
and close the durable handoff. Required tests address concrete feature risks;
an unchanged passing gate is not repeatedly run merely to fill a worker slot.

Before publication, build a coherent source, inspect meaningful native/core
regressions, verify no sound-state/model identities changed, retain screenshots
from that source, update setup/status/next steps/development log and publish to
`main` with a fresh expected-head check. Preserve any concurrent remote advances
and verify the fetched published revision. Hosted jobs must be observed before
they are reported as passing.

## Boundaries left open

Physical audio/MIDI devices, DAW use, native screen-reader integration, deadlines,
specimen fidelity, scanner numerical-policy resolution, connected AO-28/Leslie
models, calibration capture, signing and release rights remain their existing
separate gates. Software tests and reference-led rendering do not close them.

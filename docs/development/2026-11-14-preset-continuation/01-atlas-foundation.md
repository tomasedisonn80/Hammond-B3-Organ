# A01 - Atlas foundation, pages 1-84

## Assignment and exact source

Assignment **A01**, wave **01**, actual worker
`/root/w01_a01_atlas_foundation`, reads the complete one-based PDF page range
**1-84 inclusive** for the new preset continuation. This note covers that range;
the other fresh readers cover the remaining pages. It does not count an earlier
session's reading as this assignment.

- Source: [unchanged 500-page atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf).
- Source SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Source size: **21,248,265 bytes**, PDF 1.4, **500 pages** according to `pdfinfo`.
- Starting repository commit:
  `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
- Starting committed tree:
  `b0210756bf704017d9e56ebca97f935cc9c451c9`.
- Tools: Poppler `pdftotext` **25.03.0**, `pdfinfo`, `pdftoppm`, Python 3 hashing,
  and direct visual inspection of the rendered page images.

`AGENTS.md`, the [implementation plan](../../PLAN.md), and the complete current
[next-step contract](../../NEXT_STEPS.md) were read. The parent also supplies the
current repository status and the bounded assignment. No production source,
shared status document, previous session record, Git commit, branch or remote
was modified by this worker.

## Complete reading and visual coverage

The exact extraction command was run from the repository root:

```sh
pdftotext -f 1 -l 84 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
```

Its output contained **208,010 characters**, **24,763 whitespace-delimited
words**, and **84 form feeds**. The UTF-8 extracted-text SHA-256 was
`8fb09946a1817dac8988ab52a98e5090cd930ed1f26d267a66df0b2a0a5dd572`.
The complete text was displayed and read in six successive, untruncated chunks:
1-14, 15-28, 29-42, 43-56, 57-70 and 71-84. This was a complete page-range reading,
not a keyword search or a reading of prior summaries.

| Pages | Material read in full | Main consequence for this continuation |
|---|---|---|
| 1-12 | Cover, evidence classes, reference lock, system responsibilities, M0-M9 order, visual evidence limits, contents and agent contract | Keep research waves, implementation milestones and worker waves distinct; functional, visual and physical evidence have separate gates. |
| 13-18 | Chapter 1: instrument/configuration identity and fidelity contract | Performance controls do not replace immutable specimen identity; unmeasured status must survive persistence. |
| 19-24 | Chapter 2: service source atlas, exact page locators, topology transcription and documentary admission | This reading is evidence from the atlas, not a new inspection of its underlying factory drawings. |
| 25-30 | Chapter 3: patents, generator/scanner/control mechanisms and rotary abstractions | Historical mechanisms do not supply unverified production constants; switching, routing and envelope state remain separate. |
| 31-36 | Chapter 4: cabinet appearance, part hierarchy, materials and visual acceptance | Reference artwork can guide the interface; dimensions, calibrated materials and hidden structure require distinct evidence. |
| 37-42 | Chapter 5: keys, nine-contact model, trajectories, timing and acceptance | Preset changes select onward routes while shared source phase continues; cancellation does not destroy oscillator state. |
| 43-48 | Chapter 6: generator assemblies, shaft relationships, persistent state and acquisition | Registration events cannot create or reset the shared generator; silent intervals and host transport do not imply mechanical restarts. |
| 49-54 | Chapter 7: four drawbar banks, preset routing, controls, continuous contact and acceptance | Direct source basis for an exclusive selector with nine fixed rows, two retained banks and Cancel per manual. |
| 55-60 | Chapter 8: Leslie variants, moving/stationary assemblies, profile identity and acquisition | A visual cabinet or registration selector must not imply unimplemented Leslie electronics/acoustics. |
| 61-66 | Chapter 9: source numbering, pitch references, rational tuning, phase and verification | Keep source IDs, array indexes, physical terminals and MIDI notes separate; preserve existing source/profile identity. |
| 67-72 | Chapter 10: pickup boundary, flux/voltage models, preparation and acceptance | Current nominal source values must not become measured voltages through a new preset label. |
| 73-78 | Chapter 11: filter families, revisions, units, state and measured response | Preset selection must not reinitialize or duplicate source/filter processing; fixed-gain behavior does not establish loaded-network fidelity. |
| 79-84 | Chapter 12: leakage location, topology, source reuse, identification and acceptance | Do not add generic leakage to conceal switching defects or duplicate existing source components. |

Selected pages **1, 4, 40, 49, 50 and 52** were rendered at 100 dpi with
`pdftoppm -f PAGE -l PAGE -r 100 -singlefile -png ...` and inspected as images.
The other pages in this assignment received complete text reading, not a claim
of complete image/diagram inspection.

Observed visual details:

- **Page 1:** the proposed instrument image has walnut cheeks, a charcoal/brass
  panel, centered title, adjacent manual drawbar racks, two manuals and a cabinet
  at right. Its own caption makes engineering specifications authoritative over
  the illustrated controls. The concept's percussion legends do not supply a
  reliable control truth table.
- **Page 4:** the diagram visibly places shared sources before contacts/preset
  routing and separates organ circuitry from Leslie electronics and acoustic
  paths. Its caption calls this a responsibility map, not a factory netlist.
- **Page 40:** the diagram separates position/MIDI trajectory input, contact
  events, source routing, manual output and visual state. Its arrows and caption
  support one audio timeline with a display snapshot, not UI-driven sound timing.
- **Page 49:** the table visually confirms the nine footage/color assignments;
  the photograph is a lighting-dependent context image. The required 36 manual
  and two pedal values are stated separately from the visible compact layout.
- **Page 50:** the selector table visually confirms Cancel, C#-A, A#/Bb and B,
  with percussion eligibility confined to upper B. The photo shows the distinct
  reverse-colored preset-key region, not additional ordinary playing notes.
- **Page 52:** the live-control pseudocode resolves selector, banks and fixed
  rows independently. The adjoining switch photograph does not justify changing
  the verified tablet labels to match the generated cover image.

The temporary rendered pages and extracted text are reproducible scratch
intermediates; the unchanged PDF and this authored reading record are the
retained source and result.

## Source basis for the next phase

### 1. An exclusive fixed-registration selector is a supported engineering slice

Page **50** explicitly proposes one mutually exclusive selection per manual.
That proposal is narrower than the physical latch mechanism, which the same
page says can also latch several registration keys. It also identifies C as a
momentary mechanical cancel without electrical contacts. Therefore an exclusive
software selector is justified as the declared nominal behavior, while a full
physical latch-mask/contact model remains separate work.

| Selector | Registration source | Percussion eligibility |
|---|---|---|
| C / Cancel | No selected manual registration | None |
| C#, D, D#, E, F, F#, G, G#, A | The manual's corresponding fixed nine-value row | None |
| A# / Bb | Left adjustable bank of that manual | None |
| B | Right adjustable bank of that manual | Upper manual only, and only with percussion enabled |

The eighteen fixed chapel rows belong to the previously admitted documentary
catalog and the later preset chapter. This page range establishes selection
semantics, not an independent transcription or verification of those eighteen
rows. It does not independently verify the factory Table IV underlying the
atlas. Preserve the catalog's existing documentary provenance.

Fixed values, retained bank settings and selected route are separate state
objects (pp. **49-50, 52**). Editing an inactive bank must not change the currently
sounding fixed registration. Selecting a bank then exposes that bank's retained
values. A fixed preset must not be implemented by copying its values into an
editable bank: that loses the performance distinction explicitly required here.

Modern total-state snapshots are a separate software facility (p. **50**).
Selecting a wired registration must not silently restore devices, expression,
other manual settings, unrelated tablets or an entire saved project. Page **54**
also warns that modern recalled-preset editing behavior does not establish
vintage wired-preset semantics.

### 2. Registration changes are routing events, not note events

Pages **40, 42, 46, 48, 52, 63-64, 70, 76 and 82** repeatedly require persistent
shared sources. The new selector must keep the following invariants:

- A selector event never creates a tonewheel voice, restarts phase or resets
  source/filter state.
- Cancel disconnects a manual route. It is not global panic and does not clear
  independent held-key ownership.
- A later reselection under held contacts uses the ongoing source field.
- Both manuals use the same cached source value when they request the same
  electrical source at the same sample.
- Silent, cancelled and disconnected intervals advance the generator according
  to the existing engine contract.
- Sample-offset control ordering is independent of block partition and UI frame
  rate. UI animation never delays audio state changes.

Source numbering must remain explicit: tone 1 corresponds to the nominal MIDI
24 anchor; tone 46 to MIDI 69; tone 91 to MIDI 114 (pp. **61, 66**). These are
reference indexing/pitch anchors, not new claims about factory gear tuning.
Nothing about adding fixed registrations authorizes replacing the current source
profile, source map, phase seed or nominal gain model.

### 3. Percussion requires an explicit selector transition policy

Pages **28, 50-52 and 54** distinguish contact state, route state and percussion
envelope behavior. The visible eligibility rule is upper manual plus B/right
bank plus percussion enabled. Moving to any fixed row, A#/left bank or Cancel
must not leave the upper-B-only path enabled by a stale Boolean.

This range does not determine every charge/recovery transition under held keys.
The later percussion chapters and the existing implemented state machine must
settle that policy. The current next-step document correctly requires
B-to-fixed-to-B tests, partly recovered percussion, held notes and preserved
history. Preserve actual trigger/recovery state rather than synthesizing an
unjustified fresh attack whenever the selector changes.

### 4. Continuous-contact hardware remains an explicit limitation

Page **52** describes two contacts linked by a 1-ohm resistor and says the 0-8
markings are not isolated mechanical detents. Its proposed initial implementation
may use discrete nominal gains with a bounded transition, but neither a smooth
amplitude slider nor a nine-value vector proves the actual contact/loading
network. Pages **73-78** likewise distinguish linear fixed-load approximations
from stateful, changing-load networks. Preserve this limitation in the new
selector/profile label and handoff.

## Recommended acceptance evidence

These are source-based acceptance requirements for later assignments, not tests
executed by this reader:

1. Compare all **nine fixed rows on each manual** against an independently
   initialized equivalent registration, at continuing generator phase and with
   percussion disabled for the direct equivalence case.
2. Switch Cancel/fixed/left-bank/right-bank during held chords. Check route,
   held-note owners, source continuity and final PCM, including both manuals
   and an unaffected pedal path.
3. Edit each inactive bank while a fixed preset sounds. Require unchanged fixed
   output; on selecting the edited bank require its retained values.
4. Cover upper-B eligibility and B-to-fixed-to-B transitions with held keys,
   partly recovered percussion, and changes to each percussion tablet. Do not
   infer all history semantics from the eligibility Boolean alone.
5. Check event order at the same sample offset, different block partitions,
   invalid selectors, no-op reselection and complete failed-call rollback under
   the established core contract.
6. Define append-only parameter identities and a versioned saved-control
   migration before changing shared fixed structures. All earlier parameter
   meanings, serialized migrations and plugin UUIDs remain stable. Older saved
   bank/Cancel states must migrate deterministically; fixed selections and all
   four bank vectors must survive new-format round trips.
7. Check UI selection/highlight, fixed registration label and audio state against
   the same canonical selector. The interface remains usable without animation
   and at supported sizes. Visible pressed preset keys are routing controls,
   never additional sounding note keys.
8. Qualify callback allocation/lifetime and native state/automation paths from
   one coherent source. The initial atlas specifically excludes file access,
   allocations, locks, logging and asset work from audio processing (p. **12**).

## Plan and evidence limits

The complete project order is M0 reference, M1 testable skeleton, M2 shared
generator, M3 console, M4 scanner, M5 AO-28, M6 Leslie electronics, M7 rotary
acoustics, M8 calibration and M9 product/release (p. **5**, reconciled with
`docs/PLAN.md`). This session's exclusive preset routing advances **M3** and its
native controls advance **M9**. It does not close all M3 hardware behavior or
advance the unresolved scanner/AO-28/Leslie fidelity gates by implication.

Pages **2-3, 13-18** explicitly state the atlas acquired no physical instrument
measurements. Unknown specimen/revision values stay unknown. A passing selector
test establishes the named nominal behavior; it does not establish loaded
transformer gains, factory latch geometry, calibrated organ sound or a measured
percentage of authenticity.

The cover image is a proposed UI direction, and pages **6, 31-36, 49-54, 58**
separate artwork/photographs from geometry and circuit authority. Match the
reference's composition and materials while keeping verified legends, counts
and live state. A future 1:1 UI claim needs actual application captures and
explicit comparison evidence. This reader has inspected source images only;
no application screenshot, native interaction, hardware test or visual-match
acceptance was performed here.

## Result and handoff

**Completed:** all 84 assigned pages read in full, six selected pages visually
inspected, exact source/text identities recorded, and current plan/next-step
contracts reconciled with the source. The strongest selector sources are
**pp. 49-54**, supported by the continuity requirements on **pp. 40-48 and
61-66**.

**Next:** the integrator should freeze the typed selector, legacy-control
mapping, saved-state migration and percussion transition contract, then assign
implementation and independent acceptance under those explicit rules. Preserve
the other tracks' source ownership and prior evidence. This worker ran no
production build or audio test and makes no completion claim for the resulting
implementation.

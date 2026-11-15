# A01 - complete atlas reading, pages 1-84

## Assignment and observed inputs

- Agent: `/root/w01_a01`, Wave 1, 15 November 2026.
- Owned deliverable: this note only. No source changes, builds, configure runs,
  dependency changes, Git mutations or publication were performed.
- Checkout: `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.
- Observed HEAD: `138fca9af7feca46d10b0e2b65d891f4751a3904`; tree:
  `d26e7ca86197750629b5e6f85fc548e03a815dd8`.
- Initial `git status --short`: modified `AGENTS.md` and untracked current-session
  directory; these are the integrator's session setup. Other work was preserved.
- Read all of `AGENTS.md`, all of `docs/PLAN.md`, and all of the current session
  `README.md` and `CHECKPOINT.md`. Inspected actual dispatched ownership in
  `assignments.json`. Recovered current/next sections of README, STATUS,
  PRODUCT_HANDOFF and the latest development-log entry; read NEXT_STEPS fully.
  Historical product navigation is not a new live remote observation. The new
  AGENTS front matter and this session's entry control present ownership.

### Source identities and personal reading coverage

| Input | Exact identity |
| --- | --- |
| Source PDF | `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 21,248,265 bytes |
| PDF SHA-256 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Full extraction | `/workspace/scratch/116ca0948095/atlas/atlas.txt`, 1,298,588 bytes |
| Extraction SHA-256 | `e6ed8ed76663a8f12c487ae1e4d3ab69facc36971df240a15b1ba36eeb22485d` |
| Pages 1-84 extraction SHA-256 | `8fb09946a1817dac8988ab52a98e5090cd930ed1f26d267a66df0b2a0a5dd572` |

The range hash is UTF-8 bytes of `"\f".join(pages[:84]) + "\f"`, where
`pages = full_text.split("\f")`. The full extraction has 500 nonempty pages
and one terminal empty chunk. `pdfinfo` independently reports 500 pages,
A4, no encryption, PDF 1.4. Every printed footer from page 2 through page 84
matched its one-based extraction position; the cover has no numbered footer.

I personally read the complete text of **every page 1-84**, in bounded slices
1-12, 13-24, 25-36, 37-48, 49-60, 61-72 and 73-84. These were the full page
texts with indentation stripped for display, not searches, earlier notes or
chapter summaries. Coverage comprises the front matter and all of chapters
001-012. I do not claim personal coverage of pages 85-500.

I also rendered and visually inspected pages **1, 4, 62, 63, 68 and 80**, using
`pdftoppm -f N -l N -scale-to 1300 -png -singlefile` into the owned temporary
directory `/workspace/scratch/116ca0948095/atlas/a01-review/`. In particular:

- Page 1 labels the attractive UI as proposed art direction and says engineering
  specifications govern final controls. It does not certify a live application.
- Page 4's diagram is a responsibility map, with internal routing explicitly
  dependent on the selected circuit. It is not a connected electrical netlist.
- Page 62's plot is an equal-tempered explanatory reference; the adjacent ratio
  table is a software-derived comparison. Neither is a measured gear inventory.
- Page 63 illustrates continuous source phase gated by contacts; its chosen
  timing is explicitly synthetic.
- Page 68's pickup drawing labels the changing gap and winding, but its tooth
  count, proportions and field geometry are illustrative.
- Page 80's visible 12-source matrix is hypothetical. Its near-diagonal pattern
  is not evidence that physical neighbors are adjacent tone IDs or that its
  displayed dB values are valid coefficients.

## Whole project objective and evidence boundaries

Pages 2-5, 12-18 specify an identified vintage electromechanical B-3/AO-28 and
Leslie 122, with a separate profile for 147 and other variants. The goal is one
inspectable engine and an eventual reliable instrument product, with separate
behavioral, audio, visual and deployment acceptance. The atlas explicitly says
that it acquired no new physical instrument measurements (p. 2). An engineering
test, an implemented module, a source-derived table, or a compelling screenshot
does not close specimen correspondence.

The implementation milestones remain M0 reference/provenance, M1 testable core,
M2 shared generator, M3 console behavior, M4 scanner, M5 AO-28 electronics,
M6 Leslie electronics, M7 rotary acoustics, M8 calibration and M9 product/release
(p. 5). The ten research waves and this session's ten worker waves are separate
organizations. The already playable nominal dry engine is useful while physical
data is absent; it must retain its unmeasured identity.

The evidence classes are documented, measured, derived, proposed and unknown
(p. 2). Every physical value needs units, source/revision, applicable specimen,
uncertainty or an explicit missing-input reason (pp. 12, 15). Immutable specimen
identity belongs outside mutable musical controls. A revised specimen or
calibration creates a new profile rather than rewriting previous evidence
(pp. 14-15). Final fidelity needs held-out captures and repeatability-informed
tolerances; percentage authenticity is not justified by completeness (p. 18).

### Page-specific findings

| Pages | Findings relevant to continuation |
| --- | --- |
| 1-12 | Preserve shared continuous sources, separately observable routing/electrical/acoustic boundaries, deterministic offline paths and callback isolation. Images, plots and the UI concept have different evidential roles; retouched P005/P020 cannot support dimensions. |
| 13-18 | Freeze instrument/configuration fingerprints; keep nulls explicit. Functional, specimen and visual correspondence are separate. Capture direct organ and cabinet microphone outputs as distinct datasets. |
| 19-24 | Source edition, printed/PDF page and crop matter. The 220-page factory collection and 73-page compilation with 1995 redraws are not interchangeable or independent witnesses. Connectivity precedes component interpretation and numerical export. Atlas p. 23 explicitly leaves an underside-layout pixel inspection uncompleted. |
| 25-30 | Patents explain mechanisms and alternatives; they do not supply verified B-3/122 production values. Keep mechanical and electrical phase distinct, and one owner per acoustic delay/directivity effect. US2828659 is an unresolved source candidate in this research. |
| 31-36 | The 48-3/4 x 49-1/2 x 46 inch dimensions are assembled furniture bounds including bench/pedals, not a bare-console CAD box. Material appearance does not prove substrate. The 319-callout/276-number inventory mentioned on p. 36 is a companion claim, not an acquired file or new count verified here. |
| 37-42 | Each of 122 playing keys has nine contact identities. Partial motion, per-key thresholds/hysteresis and repeated-note return differ from binary note gating. MIDI trajectories are declared surrogates. Published approximately 9 mm travel is one 1967 C-3 observation, not a universal B-3 tolerance. Timing fidelity needs synchronized position/contact traces and held-out keys/gestures. |
| 43-48 | Separate tone, shaft, compartment, pickup and disk identities. Documented structural totals are 91 active wheels, five balancing blanks and 48 rotating assemblies; blanks do not become sources. The 16/192 tooth pair has ratio 12. No complete applicable production gear table, inertias or tolerances is supplied. A complex mechanical model requires held-out improvement over constant speed. |
| 49-54 | Preserve four nine-drawbar manual banks plus two pedal drawbars. Fixed registrations and inactive banks are separate state. C is cancel; C#-A are nine wired registrations; A#/B choose banks. Upper B gates percussion. The exclusive selector is a declared software model; physical simultaneous latching is a separate option. Continuous-contact hardware does not establish a linear travel-to-gain law. Modern total-state snapshots must be a separately named software layer (p. 50). |
| 55-60 | Cabinet family, input/amplifier route, rotor assemblies, geometry and evidence have independent identities. Tall and short cabinets do not share geometry merely by scaling. Driver diaphragms and rotating acoustic channels are different physical parts. Optional reverb and modern servo circuitry are not default vintage-122 behavior. |
| 61-66 | One-based tone IDs, zero-based storage, terminals and MIDI are distinct domains. ET anchors are tone 1/MIDI 24, tone 46/MIDI 69 and tone 91/MIDI 114. Page 62 supplies twelve lowest-frequency rational software comparisons, not complete factory gearing; the upper seven 192-tooth outputs need their own rule. Missing gear entries must not silently become ET. |
| 67-72 | Distinguish pickup geometry, induced emf and loaded terminal voltage. Nominal sine, calibrated voltage coefficients and flux-linkage coefficients have different evidence and equations. Preserve complex phase, mechanical versus tooth basis, units, source/load boundary and anti-alias policy. A terminal recording cannot uniquely identify magnet, gap, coil and filter parameters. |
| 73-78 | Early port groups 1-43, 44-48, 49-54 and 55-91 have different documented networks. Historical mf/mfd means microfarads here. Bulletin 16 changes 37-48 and can be retrofitted; serial alone cannot choose the network. The 318.31 Hz calculation on p. 74 assumes an ideal source and 10-ohm load. Precomputed harmonic/filter multiplication is valid only for stationary linear fixed-load behavior; post-filter captures must not receive the filter twice. The p. 78 0.1 dB/1 degree criterion is a proposed engineering target, not a physical result. |
| 79-84 | Leakage needs a declared injection point and an actual physical/empirical graph; pitch adjacency and arbitrary background noise are inadequate. Gain-only feedforward sparse transfer is an available first numerical abstraction. Off-diagonal scale zero must preserve the diagonal path; there is no automatic normalization. Held-out evidence must resolve pre-contact contamination versus post-contact feedthrough, and correlated sources may make fitting non-identifiable. No complete measured 91-source matrix or universal level is supplied. |

## Current source comparison

These are direct source inspections, not newly executed C++ runtime acceptance:

| Current path | Observed implementation and implication |
| --- | --- |
| `include/hammond/TonewheelBank.h`, `src/TonewheelBank.cpp` | Explicit `ideal-shared-sine-v1`; 91 value-owned states, seeded modeled phase, one sine evaluation and one phase advance per frame. Stopped rate reconfiguration changes increments while preserving phase/sample. No harmonic, flux, shaft/compartment, filter or leakage model. |
| `include/hammond/Profile.h`, `src/Profile.cpp` | `ToneSource` holds frequency, normalized peak and base phase only. Runtime profile holds nominal identity/hash, gains, 91 sources and manual map. Loading is stopped, bounded and transactional. Runtime checks validate numerical domains; the retained digest is not verification of unseen authoring JSON. |
| `tools/compile_profile.py`, `data/profile.schema.json`, `data/profiles/nominal-unmeasured-v1.json` | Authoring validation deliberately accepts one exact nominal model: ET equation, unit amplitudes, zero base phases, proposed gains and named boundaries. Physical pickup voltage/harmonics/loading/leakage are explicitly absent. A richer model needs a new identity/schema path, not relaxed validation under the existing name. |
| `include/hammond/ContactBank.h`, `src/ContactBank.cpp` | Both ideal and normalized linear-travel models already exist. Every key owns nine distinct on/off thresholds, hysteresis, targets and interruption history. Proposed 8/12 ms values are explicitly unmeasured. Threshold resolution is at the frame boundary; there is no recorded bounce or fractional switching model here. Do not recreate the existing contact foundation as new work. |
| `src/Engine.cpp` | One source frame is reused for all manual, percussion and pedal branches. Contact routing sums source coefficients coherently; cancellation disables the onward route. The nominal output multiplies summed dry audio by output gain and expression. No generator-filter/leakage/scanner/AO-28/Leslie route is present in the inspected processing path. |
| `src/FixedRegistration.cpp` and Engine routing | Immutable generated fixed-registration rows and exclusive selection are already used separately from retained banks. This satisfies a useful behavioral layer of pp. 49-54; it does not establish transformer loading or physical latch behavior. |

The authoring profile's original `not-modeled` console fields are provenance for
that frozen initial profile, not a reason to erase later ConsoleModel/pedal/
percussion implementations. Preserve their distinct current identities.

## Feasible next phases, with acceptance and limits

The integrator should choose after all six full readings. The following tasks
have no need to edit Drawing, InstrumentView, UiModel, M6 FOH, native MIDI-close
or R4 paths. They are proposals, not ownership grants or completed work.

### 1. Independent generator spectrum/profile foundation

Pages 61-78 support a separately named, bounded authoring contract and a synthetic
harmonic-voltage evaluator. New proposed paths could be
`data/generator-spectrum.schema.json`, `tools/compile_generator_spectrum.py`,
`include/hammond/GeneratorSpectrum.h`, `src/GeneratorSpectrum.cpp` and dedicated
tests/docs. Existing nominal Profile/TonewheelBank and live Engine can remain
unchanged. Begin with explicit source IDs, coefficient basis/phase convention,
normalized versus calibrated-voltage units, capture/load boundary, bandlimit
policy, per-value provenance and unknown mechanical references.

Required engineering acceptance: scalar analytic Fourier oracle; amplitude,
phase and sign checks; zero/DC policy; finite and capacity validation; alias
comparison against a higher-rate reference; stable source phase through silence
and partitions; bounded storage and allocation checks; stopped transactional
rate/profile lifecycle; no double filtering; reproducible source/data reports.
If flux linkage is later supported, constant linkage must yield zero emf and
sinusoidal linkage must match the analytic derivative (p. 72).

This can test mathematics with explicitly synthetic coefficients now. It cannot
produce measured B-3 pickup tone without captures. Do not invent the missing
upper-source rational rule or derive factory gear factorization from the twelve
p. 62 software comparison ratios. This is useful independent M2 research, but
scanner G5 or a bounded M9 feature may provide a more immediate next product step.

### 2. Independent sparse generator-transfer kernel

Pages 79-84 supply a precise bounded gain-only research task: consume one
91-source frame and apply a separately identified feedforward off-diagonal
graph, with source/destination boundary and provenance. Proposed new paths:
`include/hammond/GeneratorTransfer.h`, `src/GeneratorTransfer.cpp`, dedicated
profile/compiler/reference/tests. No actual leakage edges should be introduced
into the nominal Engine or called calibrated.

Acceptance: independent dense-versus-sparse comparison; alpha-zero preserves
the diagonal path exactly; one edge changes only its destination; signed gain
gives the expected phase reversal; duplicate/invalid IDs and nonfinite or
over-budget coefficients fail before installation; no accidental graph cascade
from reading already-mixed destinations; derived sum bounds; block invariance,
transactional failure and zero callback allocation. A delayed/filter extension
needs its own state and stability contract. Real edges/levels and any audible
post-contact feedthrough remain acquisition-dependent.

### 3. Explicit modern control snapshots as a distinct M9 layer

Pages 15 and 50 justify a modern total-state snapshot/recall feature provided it
is kept separate from specimen calibration and vintage wired-preset selection.
Potential existing boundaries are `apps/standalone/StateFiles.{h,cpp}`,
`apps/standalone/Session.{h,cpp}` and `src/ControlStateIO.cpp`; these paths were
located, not fully audited by A01. Root must inspect and assign them before work.
New library/metadata files could avoid the concurrently owned visual deck.

Acceptance should preserve all 47 sound identities and `B3CONTROLS4` plus readers
1-3, independent retained banks/fixed routes, and continuous source/contact/
percussion histories under the existing control-only restore contract. Recall
must not change audio-device preferences or relabel calibration as a musical
preset. Test malformed/stale records, transactional failure and inactive-bank
behavior. This is an actionable product feature only after its contract and
ownership review; p. 50 does not authorize changing vintage preset semantics.

### Work that still needs acquired inputs

Complete production shaft/gear/compartment/pickup relationships; specimen
frequencies and common-clock phases; loaded pre/post-filter captures; component
losses and impedances; original-versus-retrofit filter applicability; calibrated
contact/bounce traces and drawbar travel/loading; physical cabinet and UI geometry.
These require documentary acquisition or a physical specimen. A schema, synthetic
waveform or perfect numerical oracle does not close them.

## Actual executed checks and retained limitations

1. `git status --short`, `git log -1 --format='%H%n%T%n%s'` and `git remote -v`
   established local source/worktree and configured remote only. No live remote
   query, fetch, commit, reset, push or staged-tree acceptance was performed.
2. Python SHA-256 and form-feed checks produced the exact source/range identities
   above. `pdfinfo` confirmed the 500-page original; six selected pages were
   rendered and visually inspected. I did not inspect every figure or retrieve
   the atlas's cited external primary documents.
3. From repository root:

   ```sh
   python3 -B tools/compile_profile.py --input data/profiles/nominal-unmeasured-v1.json --check
   ```

   Exit 0, no output file written. It reported canonical authoring SHA-256
   `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
4. An independent read-only Python calculation found exactly 91 ordered source
   IDs and zero difference from `440 * 2**((tone_id - 46) / 12)` for all stored
   frequencies. Anchors: tone 1 = 32.70319566257483 Hz, 13 = 65.40639132514966,
   46 = 440, 73 = 2093.004522404789, 91 = 5919.91076338615. This verifies the
   declared nominal equation, not factory pitch or runtime rendering.
5. No C++ compile, runtime test, audio render, physical capture, DAW/device,
   accessibility or real-display test was run. Historical passes remain tied to
   their original sources. No 1:1 visual/audio completion claim is made.

### Inspected source SHA-256 records

| Path | SHA-256 |
| --- | --- |
| `include/hammond/Profile.h` | `b1180b3dc04030e0555ef3eb44a21617fc06e93150a9ecb48ebb05955b3e5fd0` |
| `src/Profile.cpp` | `80f5c7456311c77a83df23c548c02cabbf9c1cf1621cff89867d0d0c688ebe54` |
| `include/hammond/TonewheelBank.h` | `694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b` |
| `src/TonewheelBank.cpp` | `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b` |
| `tools/compile_profile.py` | `2ca649de88a3f267970e4ed00fa6c08b7c234bffcc1b4c24b47a89be608fb2a8` |
| `data/profile.schema.json` | `064beb58d186bb9ace5b2271c00c1b6f7d06c5ef43a403b6319344d92c1057af` |
| `data/profiles/nominal-unmeasured-v1.json` | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| `include/hammond/ContactBank.h` | `a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d` |
| `src/ContactBank.cpp` | `91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |

The new session retains its own actual assignment. This note neither repeats
older worker credit nor grants ownership of the separately active fidelity/R4
tracks. The integrator owns shared navigation, build coordination, scope freeze
and publication.

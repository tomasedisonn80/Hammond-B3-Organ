# A02 - Atlas console boundaries, pages 85-168

## Assignment and source identity

- Session: `2026-11-14-waveform-continuation`; actual worker `/root/w01_a02_atlas_console`; date 2026-11-14 UTC. This is distinct from the in-progress reference-refinement session.
- Owned path: this note only. Result: complete fresh assigned text reading plus selected original-page visual review; no new DSP, physical or product acceptance claim.
- Repository: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
- Observed HEAD: `2e161dc3a60fc3442051799574feed37bffbfc5c`; tree `17f8e4d698f903c37bff09deee196ea73e0da108`. Local `origin/main` matched; this worker did not fetch or verify the live remote.
- PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition 12 November 2026, 500 pages, 21,248,265 bytes; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Text: `/workspace/scratch/e3cacb90cc81/atlas-text/part-2-85-168.txt`, 214,852 bytes, 4,918 lines; SHA-256 `36eb088cd1be8e44a7f9bf226a42e22bd8afd3892c64ad99cb0c93191dab8276`.
- Read complete `AGENTS.md` and `docs/PLAN.md`; consulted current README/status/next-steps/log sections, reference-refinement scope/checkpoint, `ATLAS_REVIEW.md`, `ERRATA.md` and rotary propagation API/continuation documents. Current implementation statements below derive from those documents, not an independent Engine-source audit.

## Actual complete reading

Final coverage used separate consecutive untruncated `sed -n` outputs: `1,400`, `401,800`, `801,1200`, `1201,1600`, `1601,2000`, `2001,2400`, `2401,2800`, `2801,3200`, `3201,3600`, `3601,4000`, `4001,4400`, `4401,4800`, `4801,4918`.
An initial exploratory batched display was not used as coverage; its opening atlas range was reread in the full sequence. No search or prior summary substituted for reading. A subsequent marker check found exactly 84 ordered markers, pages 85 through 168, without gaps or repetitions.

| Complete PDF text coverage | Chapter | Subject |
| --- | --- | --- |
| 85-90 | 013 | Mechanical modulation and motor imperfections |
| 91-96 | 014 | Tonewheel calibration data model |
| 97-102 | 015 | Manual harmonic mapping and foldback |
| 103-108 | 016 | Shared oscillator implementation |
| 109-114 | 017 | Drawbar attenuation and bus mixing |
| 115-120 | 018 | Contact timing and key click |
| 121-126 | 019 | Preset matrix and registration |
| 127-132 | 020 | Percussion trigger and retrigger |
| 133-138 | 021 | Percussion circuit and envelope |
| 139-144 | 022 | Pedal mapping and shaping |
| 145-150 | 023 | Expression mechanism and response |
| 151-156 | 024 | Console state and MIDI semantics |
| 157-162 | 025 | Scanner delay-line circuit |
| 163-168 | 026 | Scanner capacitive rotor |

## Actual visual inspection and limits

Read the PDF skill, rendered original PDF pages with Poppler at 1,400-pixel height and viewed all six images. They are reproducible scratch intermediates under `/workspace/scratch/e3cacb90cc81/tmp/pdfs/a02/`. Full text coverage does not mean every illustration or cited external source was independently reviewed.

| Original PDF page viewed | Observation and evidence limit |
| --- | --- |
| 110 | The 3 dB chart is explicitly a nominal initialization, not a solved transformer/loading model. |
| 122 | All nine upper/lower table strings agree with extracted text, including leading zeros. This checks the atlas, not its underlying factory Table IV independently. |
| 134 | Embedded schematic is captioned a historical patent embodiment; it cannot replace an identified production AO-28 drawing. No component tracing claimed. |
| 147 | Confirmed the expression equations and `v*dC/dt` term with the stated surrogate/loading limitations. |
| 158 | Diagram separates common return, loaded first-six dividers, later sections and termination; 19 outputs are ground-relative, and 18 L + 18 C + 14 R is the idealized graph. |
| 166 | Confirmed the existing E01 mismatch: 15 printed entries but 16-position indexing and modulo-16 access. |

All page references here are one-based atlas PDF pages. The source PDF is unchanged; rereading its claims does not recover absent companion files or create independent primary-source verification.

## Console routing, contacts and gain

**Shared field:** electrical tone IDs, physical terminals, manual keys, MIDI pitches and storage indices remain distinct. Both manuals consume one continuously running 91-source field through independent routes. No note, preset, silence interval or effect bypass restarts source phase; no GUI operation owns its clock (pp. 85-90, 91-108).

**Manual map:** preliminary offsets are `[0,19,12,24,31,36,40,43,48]`; only the 16-foot route adds 12 for keys 1-12. Upper foldback repeatedly subtracts 12 while the source exceeds 91. Manual sources 1-12 remain unreachable. At top key 61, drawbars 2/5/8 share source 80 and 4/6/9 share source 85, while retaining independent contact states and gains (pp. 97-102). The repository's later independent factory comparison remains separate evidence; it was not rerun here.

**Contacts:** each key has nine histories tied to gesture; make and break need separate models. Electrical click depends on actual source value and slope at the edge. Mechanical clatter, electrical contact click and percussion are distinct. MIDI velocity may select a named gesture but must not scale sustained loudness. Folded source collisions cannot merge contacts before their switching/loading states are resolved (pp. 100, 115-120, 152).

**Drawbars:** the nominal reference uses `g(0)=0` and `g(p)=10^(3*(p-8)/20)` for physical positions 1-8. This is a proposed dimensionless voltage law, not measured tap gain. Coherent equal paths add amplitudes, so two same-phase branches double amplitude in the linear fixture. Never normalize by held-note count (pp. 109-114). Loading, transformer saturation and intermediate contact travel require their own model/evidence; the patent winding numbers and approximately 1-ohm contact bridge do not supply a complete production circuit.

**Pedals:** 25 keys, eight contacts each, four collecting buses and two coupled mixtures feed the lower-manual transformer. The 200 map positions contain 195 connections and five nulls. The exceptional third-contact column repeats another source for pedals 1-7, disconnects for 8-12, then uses the higher source. Preserve repeated branches and null-versus-source-zero semantics; never create an independent bass oscillator or reuse the manual mapper (pp. 139-144).

## Preset, percussion and expression boundaries

**Retained banks and Cancel:** C is momentary Cancel, has no electrical contacts and releases the selected manual's registration connectivity while preserving held notes, generator state, the other manual and pedals. C#-A select fixed rows; A#/B connect the existing adjustable banks without copying values. Four bank memories persist; fixed registrations ignore edits until an adjustable bank is selected. The UI must not make C a permanent depressed latch or treat Cancel as Panic (pp. 121-126).

**Fixed matrix:** page 122 supplies one approved chapel profile with 162 tap assignments, not universal surviving-B-3 wiring. Digits designate taps, not amplitude multipliers. The atlas's single visual transcription remains a source claim. Simultaneous physical latching is a separate extension; ordinary program selection is exclusive, and multiple latches cannot become a naive sum of independent presets without loaded-network evidence (pp. 121-126).

**One percussion history:** upper B enables the reference route. Keying is the eighth harmonic, meaning the 1-foot bus/ninth physical drawbar, not the eighth drawbar. A silent audible drawbar does not erase its physical contact. Lower/pedal owners do not enter the upper detector (pp. 124, 127-132).

Joining notes feed current shared harmonic audio through the existing decay rather than receiving independent envelope attacks. Recovery follows elapsed open-contact time; an off/on pair at one sample offset creates no recharge interval. Preset/tablet changes preserve charge history. Exact held-key B exit/re-entry behavior remains dependent on traced topology and captures, so this session must retain the current declared nominal policy (pp. 124-132).

Sustained return, percussion output, upper attenuation and upper-B 1-foot masking have distinct ownership. The selected drawbar changes sustained sound without directly scaling the percussion envelope. Normal/Soft cannot accidentally attenuate lower or percussion paths with upper sustained audio. Percussion bypasses scanner vibrato and reuses shared source phase (pp. 133-138). The derived RC products on p. 135 are electrical hypotheses, not measured audible timing or permission to retune the existing core.

**Expression:** the common preamp path includes upper, lower, pedals and percussion once. Physical expression changes capacitive transfer/loading and drive into later nonlinear stages; final monitoring gain is separate. A scalar gain remains a declared approximation (pp. 145-150). Preserve today's nominal expression behavior; R4 must not reinterpret it as cabinet normalization or apply it again to each rotor.

GUI/MIDI/host expression inputs resolve into one timestamped trajectory. Position, controller calibration and electrical response are separate; movement never resets generator, percussion or scanner history (pp. 148-150). Photoreal pedal motion supplies no capacitance or response calibration.

## State ownership and actionable R4/UI constraints

The audio layer owns applied controls; adapters send ordered commands and the UI consumes copied state. Pending sequence and applied sequence may differ. Persistent settings remain separate from note owners, contact trajectories, phases, charge, reactive states and rotary histories (pp. 151-155).

A held note keeps its original manual destination when input routing changes. Multiple owners hold one physical key; one release cannot release another owner's key or double its source amplitude. Release matching uses saved destination before current mapping. Same-timestamp ordering is a declared product policy (pp. 130, 152-153).

Ordinary patches are not complete runtime checkpoints and must not resurrect saved notes. Vintage preset selection does not recall expression, scanner, Leslie speed or generator profile. A live patch follows the declared ownership/phase-preservation policy (pp. 126, 155). The current concrete repository invariant is **47 parameters, state4 writer and readers 1-3**; those counts are project contracts, not atlas values.

1. Keep R4 an independent nominal renderer/probe boundary. Do not insert it into Engine, change dry latency/audio, retune console models or add cabinet parameters/state. R5 audible policy and R6 runtime/Engine integration remain separate gates (`docs/ROTARY_PROPAGATION.md`).
2. Keep explicit separate horn/drum radiation-boundary inputs. R4 must not invent crossover/driver preparation or duplicate one dry stream as if M5/M6 were complete. Respect what a waveform already contains; source/loaded/filter boundaries prevent double processing (pp. 93, 103, 116, 141).
3. Preserve clocks independent of notes and UI. Rotor speed commands request targets; actual horn/drum state remains separately owned. Transport, virtual power and processed sample time are distinct policies (pp. 105-106, 129-130, 154).
4. Preserve the existing frozen R4 requirements: bounded separate histories, write-at-n/observe-at-n-2, cubic support, zero negative audio, signed Horn-then-Drum addition and whole-call rollback. These are project numerical requirements; the two-frame renderer delay must not become a dry-Engine change.
5. UI refinement preserves all banks, fixed selections, Cancel, note origins, expression, percussion history and parameter/state meanings. Resize, workspace/Flat changes and inspection remain presentation operations. Cabinet artwork or motion does not establish connected audio.
6. Preparation, fitting, allocation/reclamation, file access and UI work remain outside processing. Preserve sample-offset ordering, zero-sample semantics and bounded failure behavior (pp. 94-96, 106, 112, 118, 130, 136, 148, 155). Renderer failure cannot partially mutate the dry instrument.
7. Integrator should qualify coherent-source dry PCM/control isolation and independent R4 partition/rollback/latency acceptance. These are next acceptance inputs, not A02-executed tests. Render success or screenshots cannot clear physical M3, scanner G5, M5/M6, device or accessibility gates.

## Physical uncertainties and scanner boundaries

| Missing/limited evidence | Required disposition |
| --- | --- |
| Generator residuals, phases, pickup waves/levels (pp. 85-96) | Keep nominal identity. Model A motion data and factory forcing rates do not establish B-3 modulation depths. Table V G-G service readings are not oscillator amplitudes. |
| Drawbar loading, winding/impedance and travel (pp. 109-114) | Preserve current gain reference; no invented saturation, chord compression or physical overlap. |
| B-3 contact timing/release/correlation (pp. 115-120) | A single 1967 C-3 study does not identify universal B-3 timing or bare-contact resistance. |
| Preset/interlock transitions and percussion circuit (pp. 121-138) | Preserve explicit current policies; acquire wiring, charge/recharge, return and switch traces before claiming measured behavior. |
| Pedal reactor, contacts, spectra and transfer (pp. 139-144) | Documentary map does not identify bass timbre or coupling. |
| Expression geometry, capacitance, loading, feedback (pp. 145-150) | Nominal gain and animation do not establish measured preamp response. |
| Scanner loss, overlap, loading, speed (pp. 157-168) | Preserve separate M4/G5 gate and nominal-source labels. |

Scanner counts are distinct: 18 LC sections, 19 ground-relative outputs, nine selected terminals and 16 physical positions. Common return is included once; mode changes retain reactive state. Capacitive stator transitions are not clicking metallic switches (pp. 157-166).
The printed p. 166 list omits a final `1`. Existing `ERRATA.md` E01 preserves the mismatch and later primary-paper corroboration; this worker confirmed the PDF mismatch only. The p. 154 caption's chapter-044 motion pointer is also a retained erratum; chapters 047/052 are the documented navigation correction. Neither issue authorizes changing dry behavior or closing scanner G5.

## Execution and next handoff

Executed: sequential reads; PDF/text `sha256sum`; `pdfinfo`; Git status/HEAD/tree/local tracking-reference inspection; six Poppler renders and image views; byte/line/page-marker check. Render command: `pdftoppm -f PAGE -l PAGE -singlefile -scale-to 1400 -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /workspace/scratch/e3cacb90cc81/tmp/pdfs/a02/atlas-page-PAGE`.
The repository was initially clean; later concurrent AGENTS/new-session changes were preserved. Only this note was authored. **No build, DSP test, commit, push, shared-document/product edit or physical measurement was performed.**
Next: integrator carries these constraints into this distinct session's reviewed R4 API and UI assignments, using the frozen numerical contract, accepted R2/R3, explicit two-input boundary and coherent dry/control baseline. Report exact-source independent results while preserving all unresolved physical/product gates.

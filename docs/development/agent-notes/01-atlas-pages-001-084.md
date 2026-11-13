# Agent 01: Atlas pages 001-084

## Review record

- Assignment: first-wave source review; scope, dependency order, data contracts, first-phase acceptance gates, and evidence limits. No implementation or external-source verification was performed.
- Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition 12 November 2026. All citations below are one-based PDF pages, which match the atlas's displayed page numbers in this range.
- Source SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Reading completed: **all 84 assigned pages**, including the cover, preface, contents, and all six pages of chapters 1-12. Sequential text batches were 1-8, 9-16, 17-24, 25-32, 33-40, 41-48, 49-56, 57-64, 65-72, 73-80, and 81-84; 201,844 extracted characters in total. Output was not truncated. This is not a claim to have read pages 85-500.
- Visual review: rendered and inspected pages **4, 15, 26, 39, 43, 49, 50, 62, 63, 68, 74, and 80**. Figures on pages 62, 63, 68, and 80 are explicitly illustrative: they do not supply measured frequencies, contact timing, production dimensions, or leakage coefficients. The responsibility map on page 4 is not a wiring schematic.
- At review time the committed repository contained only this PDF and a one-heading README. The companion chapter JSON, source catalog, image atlas, physical inventory, mission prompt, and acceptance matrix mentioned in the PDF were not committed artifacts. Their existence in the research package must not be assumed to establish repository availability.

## Decision for the first implementation

Build an **evidence-labeled, deterministic dry-engine foundation**. The atlas permits useful nominal development models while measurements are unavailable, but explicitly reports no measured reference specimen, completed engine, or demonstrated fidelity result in its research package (pp. 2, 13-18). The initial development profile should include `unmeasured` in its name and preserve that status through saved state and reports (pp. 16, 18).

The baseline is a vintage electromechanical B-3, an identified AO-28 revision, and a vintage Leslie 122. The 60 Hz configuration is a proposed baseline; 50 Hz, Leslie 147, modern B-3, modern Leslie H-series, and modified instruments need separately identified profiles (pp. 3, 13-14, 55-60). The actual specimen and AO-28 revision remain unknown. Thus a documentary readiness gate can be completed now, while physical reference lock and calibrated correspondence remain open.

### Dependency order

| Milestone | Implementable obligation | Exit evidence / limit |
| --- | --- | --- |
| 0: reference and evidence contracts | Versioned configuration, source/revision records, unknowns with acquisition tasks, explicit baseline and extensions. | Another engineer can reproduce each interpretation; unknown specimen fields remain null. No measured-reference claim (pp. 3, 15, 18-24). |
| 1: testable skeleton | Framework-independent engine; preparation outside processing; sample-offset semantic events; offline renderer; module observation points; status/report output. | Deterministic input reproduces output; profile units/unknowns round-trip; report identifies approximation and unsupported stages (pp. 5, 12, 16). |
| 2: generator core | Canonical 91-source registry; explicit frequency mode; persistent phases; explicit source/contact mapping boundary. | Identity/anchor checks, silent-period phase continuity, shared-source reuse, block partition invariance, frequency provenance, and eventual mapping/foldback tests (pp. 5, 43-48, 61-66). |
| 3: console behavior | Contacts, independent drawbar banks, preset routes, pedals, percussion, expression. | State/routing tests before claims about measured mechanics or circuit response (pp. 5, 37-42, 49-54). |

The remaining order is scanner, organ electronics, Leslie electronics, independent rotary acoustics, calibration, then product/release. Dry-organ discrepancies must be resolved before downstream stages are tuned. The visual product follows stable signal contracts (pp. 4-5, 12). Later-review agents must supply the detailed contracts in chapters 14-24 and 63, 73-79 before the coordinator finalizes the first-phase scope.

## Page coverage and substantive findings

| Covered pages | Findings that affect engineering |
| --- | --- |
| 1-12: framing and navigation | Separate documented, measured, derived, proposed, and unknown evidence. Three different results require separate evaluation: control behavior, specimen audio, and visual correspondence. Keep allocation, I/O, locks, logging, and rendering off the callback. The contents locate the later implementation and acceptance chapters. |
| 13-18: reference contract | Immutable specimen identity must be separate from mutable performance state. Revision changes produce a new profile and invalidate affected calibration. The first executable program loads a profile, renders timestamped events, exposes intermediate outputs, and reports implemented/approximated/disabled/unverified blocks. |
| 19-24: primary-source atlas | The 220-page factory scan and 73-page compilation are different documents; the latter contains three 1995 redraws. Record printed and PDF page numbers independently. Extract topology before component values; preserve ambiguous crossings and conflicting variants. A secondary host is not independent corroboration. |
| 25-30: patents | Patents explain mechanisms and alternatives, not production applicability. The generator is a mechanical/electrical graph; scanner overlap is not automatically abrupt switching; percussion is a routing/state problem; rotating acoustic channels are distinct from speaker diaphragms. |
| 31-36: cabinet appearance | The documented overall footprint includes bench and pedals, so it is not a bare-console bounding box. Scene parts need provenance, units, hierarchy, and measured pivots. Rendering consumes read-only state; hiding a mesh cannot alter audio. Retouched imagery cannot support dimensional assertions. |
| 37-42: keyboard contacts | Two 61-key manuals each have nine contacts per playing key: 549 contacts per manual, 1,098 total. Keep key motion, per-contact state, routing, and animation separate. MIDI can provide a declared synthetic trajectory, not observed finger motion. Partial closure and incomplete-release retriggers are later behavioral obligations. |
| 43-48: generator mechanics | Separate 91 electrical sources from 96 disk positions, five balancing blanks, 48 rotating assemblies, pickup identities, and compartments. Start with constant-speed persistent phases; detailed mechanical dynamics require held-out evidence. A 16/192 tooth pair has frequency ratio 12, not an octave. |
| 49-54: console controls | Preserve all 36 manual plus two pedal drawbar settings independently. Fixed presets, inactive bank settings, and selected routes are distinct. Upper B selection gates percussion eligibility. Great vibrato includes pedals. Global Soft and percussion Soft are separate controls. Drawbar markings do not prove mechanical detents or a linear gain law. |
| 55-60: Leslie families | Baseline 122 and 147 have different electrical interfaces; cabinet height, amplifier, drivers, and motion records must remain independently identified. Horn/drum states are independent; drivers and rotating acoustic parts are distinct. Reverb variants and modern servo-drive behavior are separate targets. |
| 61-66: frequency and phase | Tone ID 1-91, array index 0-90, terminal position, shaft/tooth identity, and MIDI anchor are distinct. Explicit rational, measured, and equal-tempered configurations prevent silent substitutions. Source phase continues through silence and host buffer boundaries. |
| 67-72: pickups | Keep raw induced voltage and loaded terminal voltage distinct. Nominal sinusoids, measured voltage coefficients, and flux-linkage coefficients have different evidence obligations. Full mechanical-turn structure can matter; a one-tooth waveform cannot encode every repeated defect. Never apply a measured terminal filter twice. |
| 73-78: generator filters | Early filter groups and the 1965 retrofit are separate per-port variants. Preserve original `mf/mfd` notation while converting its microfarad meaning into SI. Fixed-load stationary linear filtering may be compiled into harmonic coefficients; changing loads and startup may require state. |
| 79-84: leakage | Physical adjacency is not semitone adjacency. Separate magnetic, filter, harness, and post-contact residual paths; every edge declares its boundary and evidence. No complete measured 91-source leakage matrix is supplied. Begin clean; add identified sparse transfers only when justified. |

## Proposed data boundaries

These are implementation recommendations distilled from the atlas, not a claim that a ready-made companion schema was supplied.

| Record | Minimum useful content and validation |
| --- | --- |
| `EvidenceValue<T>` | Optional SI value, unit, original notation, evidence class, source locator, applicable revision, uncertainty, conditions, derivation/fit parents, and replacement/acquisition task. Missing is not zero. A measured tag requires an acquisition record (pp. 12, 15). |
| `SourceRecord` and applicability | Stable source ID; URL/document identity and hash; edition; printed/PDF page; normalized crop; reading status; reviewer/date; assembly predicate. Document existence does not establish specimen applicability (pp. 19-24). |
| `ReferenceProfile` | Schema/profile version, immutable identity/fingerprint, region, generator/AO-28/scanner/cabinet revisions, modification history, evidence state, and unresolved fields. Controls do not rewrite identity; calibration edits create a new version (pp. 3, 14-16). |
| `GeneratorProfile` | Exactly 91 unique source IDs with explicit array conversion, pickup/terminal links, optional shaft/compartment/disk links, frequency mode, rational factors or measured frequency records, waveform boundary, and deterministic phase initialization. Unknown physical associations remain unknown (pp. 43, 46, 61-64, 70). |
| `GeneratorState` / `SourceFrame` | Persistent double-precision or tested fixed-point phase; optional shared mechanical state; one evaluated source value reused by every routing path per sample. Note count must not multiply oscillator or coupling state (pp. 46, 64, 70, 82). |
| `KeyboardProfile` / contact state | Two manuals, 61 playing keys each, nine stable contact IDs per key, independent source map, thresholds and timing provenance. Permit separate closure/release thresholds and declared MIDI surrogate trajectories (pp. 37-42). |
| `ConsoleState` | Four independent nine-drawbar banks plus two pedal controls; wired preset matrix; separate selection; named switch enums; expression; extension flags. Physical drawbar travel and displayed 0-8 mark can coexist (pp. 49-54). |
| `PickupProfile` / `FilterPort` | Source boundary and amplitude units, coefficient basis/phase origin, observation load, spectral policy, per-port topology/revision, physical or identified response, evidence. A post-filter waveform cannot receive the same filter again (pp. 67-78). |
| `LeakageEdge` | Source/destination IDs and boundaries, phase/gain convention, stable transfer, evidence, valid range, and preallocated state. Distinguish magnetic/filter/harness namespaces and any downstream residual (pp. 79-84). |
| `CabinetProfile` | Independent amplifier/input route, crossover, drivers, geometry, horn/drum dynamics, region, specimen state, and measurement references; compatibility checks prevent accidental hybrid profiles (pp. 55-60). |
| `RenderReport` | Profile/build/event/capture identity, sample rate, block/quality settings, observation points, implementation status per module, test results, and explicit remaining limitations (pp. 12, 16, 18). |

### Frequency initialization that can be used honestly

Page 62 supplies the following rational initialization reference derived from a pinned setBfree 60 Hz implementation. It is software-comparison evidence, **not a verified factory gear inventory**. Retain integer numerator/denominator and the derivation source; reduced speed ratios do not identify the actual gear tooth counts.

| Pitch class | C | C# | D | D# | E | F | F# | G | G# | A | A# | B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ratio | 85/104 | 71/82 | 67/73 | 35/36 | 69/67 | 12/11 | 37/32 | 49/40 | 48/37 | 11/8 | 67/46 | 54/35 |

The listed lowest frequencies are `40 * ratio` Hz. The seven upper 192-tooth outputs require their own rule; ordinary 256-tooth octave extension is specifically rejected (p. 62). This range does not provide the full production map or that complete upper-output rule. A later source review must resolve it before a complete rational mode is accepted. Missing required gear data must fail preparation rather than silently select equal temperament (p. 64).

An explicitly named 12-TET test mode is permitted. Its indexing convention is `MIDI = tone_id + 23` and `f = 440 * 2^((tone_id - 46)/12)`: tone 1 is MIDI 24, tone 46 is MIDI 69, and tone 91 is MIDI 114. This is an indexing/reference calculation, not vintage measured tuning (pp. 61, 66).

## Candidate implementation and acceptance tests

No tests below have been run by this report's author. They are proposed gates for implementation agents, and the distinction between algorithm tests and hardware validation must survive the final report.

| Gate | Falsifiable fixture | Evidence / acceptance meaning |
| --- | --- | --- |
| Profile round-trip | Save/load unknown AO-28 and specimen fields, units, original notation, and `unmeasured` status. | Values/status unchanged; no null-to-zero coercion (pp. 15-18). |
| Invalid evidence rejection | Numeric parameter lacks unit; measured parameter lacks acquisition; source ID duplicates; required frequency missing. | Preparation rejects with actionable diagnostics (pp. 15, 61, 64). |
| Source identities | Count 91 sources; separately represent blanks when physical topology is present; reject duplicate pickups and orphan references. | Structural correctness only (pp. 43, 48, 61). |
| Pitch anchors | Independently calculate tone IDs 1, 13, 46, 73, and 91; compare rational mode against exact-rational arithmetic. | Detect indexing/octave and tuning-mode mistakes (pp. 61, 66). |
| Shared-source reuse | Route the same source to upper/lower contacts and observe both at the declared source boundary. | Both consume the same phase/sample; downstream differences do not imply separate oscillators (pp. 26, 66, 70). |
| Silent phase continuity | Render equal durations with contacts open/closed; reopen at the same absolute sample. | Source phase is identical; note, preset, and silence do not reset it (pp. 46, 63, 66). |
| Event/block invariance | Partition one timestamped timeline into different block sizes, including events at block boundaries and multiple events at an offset. | Defined ordering and identical timing; output agrees within a declared numerical tolerance (pp. 12, 40, 48, 66). |
| Sample-rate policy | Render supported rates and verify frequency, duration, continuity, and spectral limits. | Convergence toward equivalent continuous behavior; bit identity across rates is not required (pp. 48, 64). |
| Keyboard structure | Verify 122 keys each with nine contacts; exercise partial closure and repeated presses before full return. | Structural and synthetic behavioral validation; measured timing remains deferred (pp. 37-42). |
| Registration integrity | Move inactive bank, select fixed preset/A#/B/Cancel, save/reload all controls. | Only intended route changes; 38 settings retained; preset keys do not sound (pp. 49-54). |
| Console interactions | Check upper-B percussion eligibility, distinct Soft controls, and all four manual-enable combinations across six scanner modes. | Routing/state tests can pass even while scanner/percussion audio stages remain unimplemented (pp. 50-54). |
| Source boundary | Supply a post-filter fixture and ensure generator filtering is bypassed; check waveform amplitude units. | Prevent double filtering and false calibrated-voltage claims (pp. 67-70, 75-78). |
| Filter units/revisions | Round-trip 0.255 microfarad as 2.55e-7 F and 0.105 microfarad as 1.05e-7 F; choose early versus retrofit explicitly. | Prevent 1,000-fold unit errors and serial-only variant inference (pp. 73-78). |
| Leakage structure | Zero off-diagonal edges; enable one edge; reverse its sign; compare sparse and dense offline evaluation. | Only declared destinations change; diagonal stays intact; invalid/unstable edges reject (pp. 81-84). |
| Runtime ownership | Verify preparation owns parsing/allocation; audio uses bounded prepared state; UI snapshot cadence cannot affect output. | Real-time architecture evidence, not a CPU budget or production-host certification (pp. 12, 34, 40, 46, 82). |

Prioritize the profile, source, timing, offline rendering, and report fixtures in the first phases. Contact mechanics, filter/flux models, leakage, cabinet physics, and scene assets should not be claimed complete because their interfaces or placeholder states exist.

## Ambiguities, blockers, and source traps

1. **Missing physical reference and companion data.** No serial, acquisition session, exact AO-28 revision, measured wheel levels/phases, complete production gear table, or calibrated leakage matrix is supplied in this range. Preserve each as an owned acquisition task, not invented numeric precision (pp. 2-3, 17, 48, 66, 84).
2. **Preset simplification needs a named scope.** Page 50 acknowledges simultaneous physical registration-key latching and momentary mechanical Cancel, then proposes a mutually exclusive software selector. Treat that enum as a simplified interaction mode; chapter 19 must settle the physical latch-mask contract. Do not claim exclusivity is the complete factory mechanism.
3. **Original sources were not all inspected by the atlas.** The AO-28 underside layout was located but not visually verified; patent US2828659 remained an unretrieved candidate. Those cannot become verified evidence through inheritance (pp. 23, 30). This review also has not independently inspected the underlying primary sources.
4. **Neighboring models have bounded relevance.** Published key-travel examples concern one 1967 C-3; pickup research concerns a 1938 Model A; capacitor-restoration observations concern a 1962 M-111. Modern B-3 manuals describe modern conventions. None supplies universal B-3 calibration (pp. 13, 38-42, 54, 68-72, 77).
5. **Generator filtering depends on revision and load.** The early groups are tones 1-43 shunt only, 44-48 reactor only, 49-54 with 0.255 microfarad, and 55-91 with 0.105 microfarad. Bulletin 16 changes tones 37-48 using 50 microfarad and 10 ohms, permits retrofit, and does not make the illustrative 318.31 Hz ideal-source calculation an assembled-generator measurement (pp. 73-75).
6. **Figures and default tolerances do not create measurements.** Page 80's leakage matrix is a hypothetical 12-source illustration. Page 63's contact gates are illustrative. Page 78's 0.1 dB / 1 degree tolerance is a proposed numerical comparison target, not a factory specification or achieved result. Phase seeds, smoothing, and numerical thresholds need recorded implementation rationale.
7. **Documentary authority and rights are separate.** Keep later redraws, alternate-host copies, patent embodiments, and production evidence distinct. The atlas calls for reuse records; it does not authorize bundling every linked manual/photo. P005/P020 are retouched and excluded from geometry evidence (pp. 6, 19-30, 33-36, 55-60).

## Handoff priorities

The coordinator should carry these findings into persistent project instructions: source-page citations accompany decisions; unknowns and provisional labels survive serialization; no unperformed measurement or test is reported as completed; dry/shared-source architecture precedes downstream fitting; and future agents review the relevant later chapters before expanding fidelity claims. This report is evidence for those rules, not a substitute for the other agents' coverage of pages 85-500.

Recommended immediate outputs are a versioned unmeasured profile/schema, source and uncertainty registers, a framework-independent engine skeleton, deterministic offline render/report tooling, a tested 91-source registry with an explicitly selected frequency mode, and retained results for the first-phase gates above. The final implementation handoff must name the exact completed behavior and the remaining physical calibration tasks (pp. 12, 16, 18, 24, 48, 66, 84).

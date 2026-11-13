# Agent 02: atlas pages 085-168

## Scope, coverage, and evidence boundary

Assignment: read every assigned page, identify implementation requirements and first-phase gates, and edit only this report. This agent made no implementation changes and performed no commits or pushes. The coordinator owns integration and shared status files.

Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition 12 November 2026, 500 pages. SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. Page references below are PDF/printed atlas page numbers, which agree in the assigned range. A source-manual page mentioned inside the atlas is a different numbering system.

I read all 84 pages in ascending, contiguous batches: **085-096, 097-108, 109-120, 121-132, 133-144, 145-156, 157-168**. Each batch printed every page with a character count and an explicit 12/12 completion marker; none of the seven tool results was truncated. I also rendered and visually inspected pages **092, 098, 122, 140, 158, and 166**. The visuals confirmed table content and exposed an actual printed pseudocode error on page 166.

| Pages | Chapter and reviewed content |
| --- | --- |
| 085-090 | 013: mechanical irregularity, shared phase, acquisition, isolation, and acceptance |
| 091-096 | 014: calibration schema, provenance, boundaries, compilation, and integrity tests |
| 097-102 | 015: manual mapping, foldback, shared collisions, and documentary review limits |
| 103-108 | 016: shared generator, scalar oracle, lifecycle, timing, bandwidth, and performance |
| 109-114 | 017: drawbar gains, transformer/loading boundaries, nominal mixing, and calibration |
| 115-120 | 018: nine contact histories, phase-dependent click, event timing, and antialiasing |
| 121-126 | 019: preset cradle, complete chapel matrix, percussion interlock, and persistence |
| 127-132 | 020: shared percussion detector/history, note ownership, and rearming |
| 133-138 | 021: AO-28 percussion identity, nominal RC values, routing, and measurement gates |
| 139-144 | 022: pedal contact map, low-wheel spectra, mixture network, and missing calibration |
| 145-150 | 023: expression mechanism, capacitive transfer, control mapping, and measurement |
| 151-156 | 024: canonical commands, ownership, automation ordering, patches, and checkpoints |
| 157-162 | 025: scanner line graph, nominal values, state accounting, and independent solvers |
| 163-168 | 026: scanner geometry, capacitive overlap, terminal order, and continuous rotation |

**Evidence discipline:** the atlas reports historical sources and research papers; I did not independently retrieve their original scans. Its proposals and calculated examples remain proposals and calculations. No specimen audio, gear-frequency dataset, calibration captures, or referenced companion JSON files were present in the initial checkout. Passing proposed software tests cannot establish measured B-3 fidelity.

## Findings that constrain the first implementation

### 1. Compile data into a shared, continuously running source field

The generator owns 91 persistent sources; manuals, contacts, drawbars, pedals, and percussion consume source identities. Each source is evaluated once per sample instant. Equal identities return the same source value and phase, while their contact and bus branches remain distinct. Notes, registration changes, host transport, and silence must not reset generator phase. A sample-rate change changes integration increments while preserving explicit phase state. A zero-sample processing call accepts allowed controls without advancing time or dereferencing absent audio buffers. These are architectural proposals and invariants in pp. 087-090 and 103-108.

Use a scalar double-precision renderer as the numerical reference before lookup tables or SIMD. Both paths must consume identical waveform coefficients, phase conventions, and bandwidth limits. Frequency is integrated; multiplying changing instantaneous frequency by absolute time is incorrect. Mechanical revolution, electrical tooth cycle, common timing residual, and pickup-gap variation are separate coordinates. Mechanical refinements are not required to make the initial constant-speed field coherent (pp. 085-090, 104-107).

The first generator profile can use explicitly synthetic sine waves and the derived equal-tempered fixture `f(toneId) = 440 * 2^((toneId - 46)/12)`. Page 094 provides the tone-46/440-Hz indexing fixture, and p. 098 explicitly permits simplified 12-TET profiles for software tests. **This does not reconstruct the historical geared-frequency table**, shaft relationships, measured phases, low-wheel harmonic spectra, or real pickup levels. Those remain separate acquisitions or source imports.

### 2. Manual routing is recoverable, but independent full-table verification is not

Pages 097-102 distinguish playing key `1..61`, drawbar `1..9`, tone ID `1..91`, physical terminal, and storage index `toneId - 1`. The suggested MIDI range is 36..96; that is a software adapter convention. Both manuals use the same baseline map.

The PDF supplies a complete constructive rule:

```text
offset = [0, 19, 12, 24, 31, 36, 40, 43, 48]
w = key + offset[drawbar - 1]
if drawbar == 1 and key <= 12: w += 12
while w > 91: w -= 12
```

The result uses sources 13..91. Repeated subtraction is necessary; upper 1-foot assignments can fold twice. Do not clamp, silence, or apply the manual low fold to pedals. Do not synthesize an exact harmonic by multiplying the 8-foot oscillator: the routing returns another shared source identity (pp. 098-101).

Six independently stated PDF boundary rows are available on p. 102:

| Playing key | Tone IDs in physical drawbar order |
| --- | --- |
| 1 | 13, 20, 13, 25, 32, 37, 41, 44, 49 |
| 13 | 13, 32, 25, 37, 44, 49, 53, 56, 61 |
| 43 | 43, 62, 55, 67, 74, 79, 83, 86, 91 |
| 44 | 44, 63, 56, 68, 75, 80, 84, 87, 80 |
| 56 | 56, 75, 68, 80, 87, 80, 84, 87, 80 |
| 61 | 61, 80, 73, 85, 80, 85, 89, 80, 85 |

The claimed complete 61-row transcription is in absent `data/015-manual-map.json`. The p. 098 visual is a plot, not 61 numerical rows. Therefore a generated 549-entry table plus these six fixtures supports **atlas-algorithm consistency**, not independent verification of every factory-table entry. The release gate for full documentary conformity stays open until a separate reviewer obtains the original table or authenticated companion.

### 3. Start with explicitly named nominal mixing and ideal contacts

Physical drawbar direction is 0=mute and 8=full. The initial amplitude law proposed on p. 111 is `g(0)=0`, `g(p)=10^(3*(p-8)/20)` for positions 1..8. It is a nominal 3-dB-per-step approximation, not measured transformer taps. Equal coherent paths algebraically double amplitude, approximately +6.0206 dB; do not sum their powers or divide the result by held-key count. Choose fixed, documented output headroom (pp. 109-114).

Retain each of nine contact histories per key. Ideal simultaneous make/break is an acceptable named first reference. Real attack and release differ; contact timing and bounce are not supplied as universal B-3 data. A contact edge acts on the current shared-source value, so a peak closure differs from a zero-crossing closure; the latter can still create a slope discontinuity. Adding a generic noise burst is not a contact model. MIDI velocity may choose a named gesture surrogate without becoming a sustained loudness multiplier (pp. 115-120).

Abrupt contact switching creates bandwidth beyond the source spectrum. A sine-only generator does not prove that the complete keyed signal is alias-free. Record the initial ideal-contact bandwidth limitation, then compare a high-rate switching reference before choosing oversampling or edge correction. Page 120's normalized RMS error target of `1e-4` is a proposed project gate, not a measured result or factory tolerance.

### 4. Model applied state and input ownership before richer sound

Pages 130 and 151-156 propose one timestamped command stream and audio-owned applied state. Input origin, bus, channel, note identity/fallback serial, original destination, physical key, and stable press order belong to owner records. Two owners of one physical key create one depressed key; one release must leave the other owner intact. Existing releases use saved destinations after routing changes. Unmatched releases are bounded diagnostics, not permission to release a different owner. Unidentified repeated notes use an explicit bounded policy, such as FIFO.

Equal-time ordering is a product policy: continuous curve value, discrete routing controls, stable note-event order, then due contact transitions. Preserve this policy across block partitions. A same-sample off/on pair consumes zero elapsed time and cannot recharge percussion. Raw MIDI zero-velocity NoteOn semantics must be implemented in its adapter; do not automatically impose them on normalized VST3 events (pp. 130, 152-153).

Preserve four independent nine-drawbar manual banks. Cancel empties the selected manual's preset connectivity without clearing held keys, the other manual, pedals, or generator state. A/B bank selection changes connectivity without copying values. Vintage preset selection must not recall Leslie speed, expression, scanner settings, or a different generator profile (pp. 121-126).

Patches save controls/configuration; replay checkpoints additionally save time-dependent state. Ordinary project restore starts without held keys; live patch load follows its separately named ownership policy. Deterministic checkpoints need sample index, phases, owner records, pending edges, random state, and downstream histories plus a compatibility manifest (pp. 126, 155). Default processed-time suspension freezes the model until processing resumes; wall-clock catch-up is a separate optional policy (p. 154).

## Exact proposed interfaces and first-phase exit gates

These are engineering proposals for a host-independent core; names may be adapted without losing the boundaries.

```cpp
struct ToneId { uint8_t oneBased; };       // validated 1..91
struct PlayingKey { uint8_t oneBased; };   // validated 1..61
struct DrawbarId { uint8_t oneBased; };    // validated 1..9
using SourceFrame = std::array<double, 91>;
using ManualMap = std::array<std::array<ToneId, 9>, 61>;

ToneId mapManual(PlayingKey key, DrawbarId drawbar);
double nominalDrawbarGain(uint8_t physicalPosition); // validated 0..8

// Preparation owns validation, I/O, allocation, and rate-dependent compilation.
PreparedBank compileProfile(const ResearchProfile&, double sampleRate,
                            ProvisionalPolicy);
// evaluate() reads current angle; advanceOneSample() is called exactly once.
SourceFrame GeneratorField::evaluate() const noexcept;
void GeneratorField::advanceOneSample() noexcept;
void ContactRouter::apply(const TimedCommand&) noexcept;
ManualBusFrame ContactRouter::consume(const SourceFrame&) noexcept;
double NominalMix::render(const ManualBusFrame&, const Registration&) noexcept;
```

The physical-voltage schema should retain `waveform_boundary`, phase domain, source unit, and evidence class. A dimensionless synthetic profile must say that its amplitude is normalized and that physical volts are uncalibrated. Do not claim a measured voltage merely because a struct uses `double`.

| Milestone | Concrete required behavior | Meaningful evidence to retain |
| --- | --- | --- |
| M0 foundation | Versioned profile/control/event contracts; evidence fields and missing-data reasons; exact distinct index domains | Invalid duplicate IDs, missing IDs/references, wrong units, invalid ranges, nonfinite numbers, and contradictory waveform boundaries are rejected with specific diagnostics |
| M1 offline engine | Same event chronology under varied partitions; bounded ownership/event capacity; stable equal-time order; explicit zero-sample behavior | One-sample reference versus partitions including 1, 32, 64, 127, 512, 1024 at 44.1/48/96 kHz; two-owner release, late-release after remap, malformed event, and overflow traces |
| M2 shared provisional field | 91 free-running synthetic sources; phase survives silence/notes/presets; one shared value per source/time; defined initial phase snapshot | Render an uninterrupted field and the same field through silent/keyed intervals; compare source state and samples. Verify provisional tone46=440 Hz and sample-rate continuity. Do not claim real gearing or pickup calibration |
| Early M3 routing/controls | Immutable 61x9 map, ideal nine-contact paths, nominal drawbar gain, independent manual/bank state | All generated IDs valid; six PDF reference rows exact; focused keys12/13,43/44,48/49,51/52,55/56,60/61; zero/mid/full gain; coherent collision equals sum; inactive bank edits leave active audio unchanged |
| Deferred audio fidelity | Contact antialiasing, measured spectra/loading, percussion, scanner, expression, and Leslie | Explicit pending gates with required source/capture inputs; no sound-impression substitute |

For callback-safety claims, instrument actual processing paths and observe zero allocation, destruction/deallocation, locks, file access, and unbounded work. A prepared pointer swap is insufficient if old-bank reclamation occurs on the audio thread. Invalid profile load must leave the prior valid bank **and playback state** intact (pp. 094-096, 106). A test of equivalent algorithms generated from the same formula is not independent documentary validation.

## Recoverable later data and requirements

### Preset panel

Page 122 contains the complete 162-digit upper/lower chapel matrix, visually confirmed in this review. Its exact profile scope is `factory_chapel_table_iv`, with `single_visual_transcription` status inherited from the atlas; this review confirms the atlas presentation, not the original factory scan. Registrations must remain nine-character strings of digits 0..8, preserving leading zeros. Presets C#..A are fixed routes; A# and B select existing banks. C is a momentary mechanical cancel with no electrical contacts. Simultaneous latching can occur physically, but summing two program outputs is not a verified circuit model (pp. 121-126).

| Preset | Upper | Lower |
| --- | --- | --- |
| C# | `005320000` | `004545440` |
| D | `004432000` | `004423220` |
| D# | `008740000` | `007373430` |
| E | `004544222` | `004544220` |
| F | `005403000` | `006644322` |
| F# | `004675300` | `005642200` |
| G | `005644320` | `006845433` |
| G# | `006876540` | `008030000` |
| A | `327645222` | `427866244` |

### Percussion

The relevant detector is the **eighth harmonic, 1-foot route: drawbar nine**, not drawbar eight. It is independent of whether that drawbar produces audible sound. Percussion belongs to upper B and has one shared history per organ. A joining note enters current selected-harmonic audio under the existing envelope; it does not receive an independent attack. Lower/pedal notes do not hold the upper detector active (pp. 127-132).

The temporary readiness surrogate `qNext = target + (q-target)*exp(-dt/tau)` is bounded for positive tau and nonnegative elapsed time. Its coordinates are dimensionless proposals, not capacitor voltages. Mode/preset switching while keys remain held must preserve history; exact transition behavior remains an acquisition question (pp. 124, 128-132).

AO-28 nominal values printed on p. 133 are C31=3.3e-7 F, R57=1.5e6 ohm, R58=4.7e6 ohm, R55=8.2e4 ohm, R56=2.2e4 ohm. Page 135 calculates isolated slow/fast RC products of 1.551 s and approximately 0.375 s; the 0.03432-s simple recharge product is explicitly only a hypothesis. These are not audible decay times. Gain versus control voltage, fast-mode initial bias, normal/soft gain, upper attenuation, return path, and P-to-D network require separate profiles and evidence. Selected drawbar movement must not multiply percussion volume; percussion bypasses scanner processing (pp. 134-138).

Recommended later order: unity-envelope routing fixtures, shared control state, fitted voltage/gain map, input/output transfer, then supported loading/nonlinearity. Reuse shared sources and avoid double-adding the sustained return (p. 136).

### Pedals

The 25-pedal, eight-contact map can be generated from p. 140 as `[p, third(p), p+12, p+24, p+31, p+36, p+40, p+43]`, with `third=p+12` for p1..7, absent for p8..12, and `p+19` for p13..25. There are 195 connected positions and five nulls; null is disconnected, never tone zero. Keep repeated source branches distinct. Bus pairs are contacts1/2,3/4,5/6,7/8, corresponding to documented brown/red/orange/yellow diagram identifiers.

This reconstructs the atlas rule and printed boundary rows, not an independently checked original 200-position table. The pedal audio is a four-bus electrical mixture feeding two drawbars and the lower-manual path. It is not two independent sine oscillators. Low-wheel spectra, reactor value/loss, actual resistances, and transfer functions are unfilled; a sine-only pedal is a reduced model (pp. 139-144).

### Expression

Expression belongs at the common preamp boundary and changes drive into later nonlinear stages. Keep downstream monitoring gain separate. The reported mechanism is a two-stator capacitive coupling system with a pedal-linked rotor; neither a linear crossfade nor generic gain-plus-EQ is established by that fact. Stationary models and moving-capacitance models differ by the `v*dC/dt` term. Controller CC11 mapping is a proposal, with calibrated endpoints/inversion separate from the instrument transfer. Capacitance curves, linkage, parasitics, and measured response remain unknown (pp. 145-150). Reserve an `ExpressionModel.process(input, position, preparedProfile)` boundary now; label an initial control-only gain as provisional.

### Scanner line and rotor

Pages 157-162 distinguish **18 inductors, 18 capacitors, and 19 observed voltages**; a cited paper's prose saying 19 stages conflicts with its explicit circuit enumeration. Nominal paper-model values are L1..18=0.5 H, C1..17=4e-9 F, C18=1e-9 F, six loaded divider pairs, Rc=22 kohm, and Rt=15 kohm. They are documented model values, not specimen measurements.

The p. 158 visual does provide a reconstructable repeated topology despite the missing 50-component companion graph: each section has series L and shunt C to a shared return; the first six have an input-side R+/R- divider; Rc connects common return to ground and is bypassed for vibrato; Rt terminates p18 to that return. Outputs v1..6 are divider midpoints and v7..19 are p6..p18, all ground-referenced. Any reconstruction needs an explicit diagram/units review and independent nodal versus runtime complex-response comparison. Do not silently claim the absent graph was imported.

There are 16 physical stator groups, nine scanner terminals in the selected research model, and 19 ladder observations. The atlas reports 412 rpm nominal, giving approximately 6.8667 Hz; actual specimen speed remains unmeasured. Rotor overlap is capacitive, not hard metallic tap switching; brush faults belong after combination. Normalized triangular crossfading is a named unloaded approximation; loading/stray capacitance can alter gain (pp. 163-168).

**Confirmed atlas erratum, p. 166:** the printed `order` contains only 15 elements, `[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2]`, although the loop uses 16 positions. The prose and wrap test imply the missing final `1`. The proposed repaired sequence is `[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2,1]`. This is an evidence-backed inference, not a silently imported historical fact. Test length, range, complete forward/return traversal, wrap continuity, equal-input unity, and phase continuation under bypass/silence; seek independent source confirmation before closing documentary review.

## Provenance and risk handoff

- Keep immutable observations, editable profiles, compiled banks, and playback state separate. Store per-quantity units, categorical evidence, source locator, uncertainty or missing reason, and nominal/observed/fitted distinctions (pp. 091-096).
- Strict JSON parsing must reject duplicate object names and nonfinite extensions. Schema structure is followed by exact-ID and graph checks; `uniqueItems` does not ensure unique tone IDs. Unknown values remain null; required runtime unknowns need an explicit provisional policy (pp. 092-096).
- `induced_emf`, `loaded_pickup_port`, and `filtered_generator_terminal` boundaries prevent duplicate filtering. Factory Table V is a preamp G-G service-output measurement under a special setup, not an oscillator gain table; the p. 092 visual explicitly confirms this (pp. 092-093).
- Serial-number inference cannot determine actual filter topology after retrofit. Bulletin16's tones37..48/B-3 serial93990 change must retain observed-versus-inferred conflict records (p. 095).
- Persistent seeds and absolute sample time govern randomness, never callback count or GUI time. Separate additive hum/noise, angular irregularity, pickup-gap effects, scanner, Leslie, and room contributions (pp. 085-090).
- Patent examples and other-model studies motivate mechanisms but do not populate production B-3 parameters. The C-3 contact study, 1938 Model A pickup-motion study, historical winding ratios, and patent circuit plates need explicit applicability limits (pp. 086, 109-110, 115-120, 133-145).

**Recommended next agent action:** implement M0/M1 contracts and M2 shared synthetic sources, then the exact manual algorithm plus six retained PDF fixtures and named nominal mixing. Record the unclosed original-table review, geared-frequency import, contact bandwidth, and all specimen-calibration gates. Future agents should review this note's interfaces against the coordinator's final architecture before adding percussion, pedal networks, or scanner code.

**Verification performed by this agent:** full assigned-page reading; six rendered-page visual inspections; source-file SHA-256; review of repository standing instructions and current initial checkout. No DSP tests, performance measurements, hardware captures, or original-source independent verification were performed, and none is claimed.

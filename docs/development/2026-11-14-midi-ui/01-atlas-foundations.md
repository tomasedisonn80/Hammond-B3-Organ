# A01 — Fresh atlas foundations and UI/MIDI implications

## Assignment and inspected identity

- Actual worker: `/root/w01_a01_atlas_foundations`; assignment A01, logical wave 1
  of the newly requested MIDI/UI session. This is a fresh reading, not a recount
  of an earlier session's worker.
- Repository baseline inspected: `0f7b90037e51e101d8fa0bfe31af40209d751659`.
- Source: [`Hammond_B3_Leslie_Research_Atlas_500pp.pdf`](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  evidence edition 12 November 2026, 21,248,265 bytes, 500 pages.
- PDF SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Complete fresh text coverage: **every word extracted from inclusive PDF pages
  1–84**, read in seven consecutive nontruncated output groups: 1–12, 13–24,
  25–36, 37–48, 49–60, 61–72 and 73–84. These are front matter plus chapters
  001–012. Extracted text is faithful to the existing PDF, not an independent
  verification of the underlying primary documents.
- Actual visual inspection: Poppler renders of **pages 1 and 49**, at 95 dpi.
  The cover's concept interface and the drawbar table/photograph were viewed.
  This does not claim a visual inspection of every page or external source.
- Context inspected: repository `AGENTS.md`, source manifest, plan, existing
  atlas review, current status/next steps, newest log entry, README, standalone
  handoff and `apps/standalone/Session.h`.

## Whole project and next dependency-ready work

The atlas calls for a vintage electromechanical B-3 with an identified AO-28
revision and a separately identified vintage Leslie 122. A 147, modern B-3 or
modern Leslie is a distinct target, even where appearance or abstractions can
be shared (pp. 2–3, 13–14, 55–60). Its ten research waves organize 80 chapters;
its implementation plan is the separate M0–M9 sequence on p. 5. Neither is an
agent completion count.

The implementation order starts with reference/data contracts, a deterministic
framework-independent skeleton and 91 shared continuous sources. Console
behavior precedes a qualified scanner and connected AO-28. Leslie electrical,
rotary and room behavior need their own boundaries; calibration and release
need actual retained evidence. UI/adapter work can proceed against the stable
nominal dry core without asserting that it completes the later physical model.
Pages 5, 12 and 16 require timestamped controls, offline reproducibility,
observable module boundaries and reports of approximated/disabled/unverified
subsystems.

The current repository's next-steps document identifies an external MIDI
adapter as independent M9 work. That is consistent with these pages: new input
should drive the established contact/routing engine, with the UI consuming
copied state. It must not introduce per-note oscillators or make the display's
update rate the musical timebase. Native UI refinement is also dependency-ready
while the scanner's unresolved numerical gate and physical acquisition gates
remain independently visible.

## Evidence rules that constrain implementation

1. **Functional, audio and visual correspondence are separate.** Pages 13 and
   18 explicitly separate these claims. A close-looking image cannot establish
   audio agreement; software routing tests cannot establish cabinet dimensions
   or calibrated sound. No physical instrument was measured for this atlas
   (p. 2), and no authenticity percentage follows from document completeness.
2. **Values carry meaning and provenance.** Units, evidence class, applicable
   revision, source locator, method/conditions, uncertainty and parent/fitting
   records belong with a number (pp. 12, 15, 21). Unknown is not zero. A musical
   control change is separate from immutable specimen identity.
3. **References are not all equivalent.** The 220-page factory compilation,
   73-page mixed compilation and its three 1995 redraws remain separate sources
   (pp. 19–24). Patent embodiments explain mechanisms but cannot silently supply
   production B-3 values (pp. 25–30). The PDF's mentioned original companion
   files are not present merely because the PDF describes them; the existing
   source manifest records their baseline absence.
4. **One physical effect has one owner.** Pickup voltage, loaded terminal
   voltage, generator filtering, contact/drawbar routing and downstream
   electronics remain distinct (pp. 67–78). A post-filter capture cannot be
   filtered again. Leakage requires an injection boundary and cannot duplicate
   components already present in a captured waveform (pp. 79–84).
5. **Observation is independent of processing.** File/image loading, allocation,
   locks, parsing, logging and rendering stay off the audio callback (pp. 12,
   34, 40, 46, 64, 70, 76, 82). Hiding a mesh or losing a render frame cannot
   alter saved audio controls, source phase or sound generation.

## UI reference: what the inspected pixels establish

The cover contains a concrete proposed **TONEWHEEL ATLAS** interface. Its visible
composition has warm walnut side/end rails; charcoal metal panels with brass
rules/lettering; PLAY/ROTARY/SERVICE tabs at the upper left; a centered title;
two adjacent manual drawbar panels; two stacked manuals beneath them; and a
right-side cabinet and microphone area. Cream switches, warm white key faces,
black accidentals, restrained shadows and bright brass text establish the
reference's visual vocabulary. The page itself calls this **proposed interface
art direction** and says engineering specifications govern final controls.

The cover is therefore a useful explicit visual target for the user's request,
with its PDF/page/image identity retained. It is not a photograph of an actual
running product or a dimensional engineering drawing. Pages 6, 34, 36 and 58
require this distinction. A raw screenshot of the reference must never be
presented as a screenshot of implemented controls.

Its decorative labels, available visual buttons and apparent key arrangement
must be reconciled with the verified engineering semantics. The cover depicts
scanner/rotary choices that the current dry application does not implement.
Reproducing their appearance is possible, but they must not imply working sound
paths. Either provide a clear inactive state with an honest explanation or
reserve that region for the separately identified future model. A functional
control cannot inherit an incorrect meaning merely to match a concept pixel.

Page 49 provides the authoritative order of nine manual drawbars for each bank:
`16`, `5 1/3`, `8`, `4`, `2 2/3`, `2`, `1 3/5`, `1 1/3`, `1` feet. Its cap
colors in that order are brown, brown, white, white, black, white, black, black,
white. These are functional color classes, not calibrated material colors.
The associated P003 photograph has colored stage lighting (p. 53). Do not
sample it as neutral wood or cap albedo.

Pages 31–36 require geometry identity, dimensions with endpoints and
uncertainty, calibrated views and landmark residuals for dimensional claims.
The listed 48¾ × 49½ × 46 inch envelope includes bench and pedalboard; it cannot
be used as the bare console dimensions. P005 and P020 are explicitly retouched
and excluded from geometry evidence (pp. 6, 33, 35, 55, 58). Appearance-only
styling may proceed without inventing those missing measurements.

## Control and external MIDI implications

| Atlas finding | Consequence for this session |
| --- | --- |
| 61 playing keys per manual, nine contacts per key (pp. 37–42) | Preserve 122 playing-key identities and their independent routing; decorative preset keys must not become sounding notes. A visible key depression is not a measured contact closure. |
| Ordinary MIDI initiates a declared synthetic trajectory (p. 39) | Document the adapter as a nominal input path. Velocity may inform a separately declared transient policy, but must not silently scale steady organ loudness. |
| Four banks of nine manual values plus two pedal values (p. 49) | All 38 retained values survive UI changes and save/load. One visible bank per manual does not justify overwriting the inactive bank. |
| Stable manual/bank/footage identity independent of pixels (p. 49) | Bind controls through the existing stable parameter registry; scaling and moving controls cannot change identity or automation. |
| C cancel, C♯–A fixed registrations, A♯/B adjust routes (p. 50) | Do not interpret fixed presets as ordinary playing notes or silently implement them as generic whole-state recalls. Cancel changes routing and retains source state. The current physical fixed-selector work remains separate. |
| Upper B percussion eligibility; percussion/global soft separate (pp. 50–51) | Preserve the established eligibility/interlock and explicitly named enum meanings. Do not create a second percussion voice per MIDI note. |
| Great vibrato includes pedals; one shared scanner mode (p. 51) | Any later scanner UI must follow the shared routing contract. Two cosmetic selectors must not create independent rates in the vintage path. |
| Continuous contact hardware, numbered marks do not prove discrete detents (p. 52) | Preserve the current nominal discrete control law and its label; visual smoothness alone does not implement loaded continuous contacts. |
| Timestamped controls; inactive edits and held-chord selector changes (pp. 40, 52, 54) | New MIDI timestamps need an explicit clock/late-event policy. Test held notes, concurrent UI edits, release after focus loss, inactive banks and recovery, using actual Session state and rendered outcomes. |

The existing `Session.h` adds a concrete local constraint: `post()` has **one
main/UI producer**, and its commands have offset zero. An external callback must
not become an uncoordinated second producer. A bounded ingress transport should
serialize device events through the existing owner, retaining original device,
channel and note ownership. UI-scoped release uses reserved channel 0; external
notes must survive ordinary UI focus loss. Any future sample-offset extension
needs a separately specified Session change rather than an undocumented claim
that the current callback-boundary queue is sample accurate.

## Source and mapping invariants to preserve

Electrical sources, physical terminals, shaft/compartment identities, MIDI notes
and storage indices are different domains (pp. 43, 61). The proposed nominal
reference uses `MIDI = tone_id + 23`, with tone 1/MIDI 24, tone 46/MIDI 69 and
tone 91/MIDI 114 as independent anchors (pp. 61, 66). That does not make
physical output terminals sequential.

The 91 active sources share ongoing phase; five balance positions are not
additional audible sources (pp. 43–48). Note attacks/releases, silence,
cancel, screen changes and transport operations must not accidentally reset
them. Equal-tempered, rational-reference and measured profiles have separate
identities. The setBfree-derived candidate ratios on p. 62 are not a verified
factory gear inventory, and the published paper formula criticized on p. 66
must not replace the independently anchored mapping.

Generator pickup/filter/leakage development is outside this MIDI/UI slice.
Pages 67–84 supply model boundaries and future acquisition plans, not new
calibration data. Their useful concrete checks include derivative sign/units,
no repeated filtering, stable bounded prepared transfers, SI capacitance
conversion, early versus 1965 revision separation, phase-sensitive sums,
sparse/dense reference parity and explicit residual injection points. None
justifies changing today's nominal source waveform merely to make a UI demo
sound more vintage.

## Recommended acceptance and next handoff

1. Freeze backend/version/rights, event ingress capacities, device ownership,
   ordering, timestamp and late-event/disconnect policies before integrating
   external MIDI. Keep physical-controller qualification separate from injected
   streams.
2. Exercise overlapping UI/device owners, duplicate presses, zero-velocity
   release, channel separation, out-of-order events, bounded overflow, device
   disconnect/reconnect and shutdown. Compare observable holds and rendered
   behavior without silently modifying existing source, control or state IDs.
3. Identify the actual cover image as the visual target and retain an unaltered
   reference extraction plus provenance. Capture the **running native app** at
   declared dimensions; inspect control labels, hit regions and image alignment
   against that target. Describe remaining mismatch concretely rather than
   declaring an unmeasured one-to-one pass.
4. Recheck all existing controls after layout changes: separate EDIT/SOUNDING
   banks, Cancel/Panic distinction, keyboard focus, pointer release outside the
   window, resize, small-window readability, inactive settings and saved-state
   round trips. Test audio independence from rendering changes.
5. Update README with the actual native image and link the source/reference,
   setup, current limits and next task. Preserve the standing AGENTS rule to
   document, verify, commit and push completed work, with exact source identities.

This assignment is a source review. It does **not** claim new engine tests,
physical measurements, native MIDI operation, accessibility qualification or
pixel-level UI parity. Its only authored repository file is this note; the
integrator owns shared contracts, implementation, acceptance and publication.

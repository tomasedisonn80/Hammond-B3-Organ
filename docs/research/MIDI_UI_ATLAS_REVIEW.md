# Full atlas reading for the MIDI/UI continuation

Source: [unchanged 500-page atlas](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. Six new assignments read the complete text of every page in disjoint ranges and inspected selected figures. This is a fresh reading; older sessions are not recounted. It does not claim independent retrieval of every cited primary document.

| New assignment | Complete text coverage | Retained findings |
|---|---|---|
| A01 | 1–84 | [Foundations](../development/2026-11-14-midi-ui/01-atlas-foundations.md) |
| A02 | 85–168 | [Console and ownership](../development/2026-11-14-midi-ui/02-atlas-console.md) |
| A03 | 169–252 | [Electronics and scanner](../development/2026-11-14-midi-ui/03-atlas-electronics.md) |
| A04 | 253–336 | [Rotary and measurements](../development/2026-11-14-midi-ui/04-atlas-rotary.md) |
| A05 | 337–420 | [Architecture and interface](../development/2026-11-14-midi-ui/05-atlas-architecture.md) |
| A06 | 421–500 | [Product and complete plan](../development/2026-11-14-midi-ui/06-atlas-product.md) |

## Whole project

The [M0–M9 implementation plan](../PLAN.md) remains the governing sequence: identify the reference and evidence; build a bounded independent engine; shared continuous tone sources; console behavior; scanner; connected AO-28 electronics; variant-specific Leslie electronics; rotary acoustics; calibration with held-out physical evidence; and native host/product/release work. The PDF's ten research waves and this session's ten worker waves are different organizations. Neither implies that all ten engineering milestones are finished.

The existing nominal core allows an independent M9 product slice. The [current scope](../MIDI_UI_SCOPE.md) adds external MIDI input and develops the actual standalone visual surface. Scanner numerical-policy failure, incomplete connected AO-28/Leslie models, physical measurements, native accessibility and actual controller/DAW qualification remain explicit gates.

## Requirements carried into implementation

1. Preserve source phase and one shared generator across both manuals and pedals. MIDI velocity must not silently scale sustained organ gain. UI timing cannot own synthesis time.
2. Keep all four drawbar banks and independent EDIT/SOUNDING identity. Cancel changes one route and preserves notes; Panic and scoped device release are different operations. Preserve upper-B percussion eligibility and its shared history.
3. Preserve channel0 for UI. Freeze the external namespace, configured wire channels, original routes, anonymous repeated-note policy and bounded recovery before backend integration. One main thread remains the Session producer.
4. Current Session applies offset-zero messages at callback boundaries. Device timestamps are diagnostic acquisition data until a separately qualified scheduler exists. Define equal-time/late ordering honestly.
5. Reconcile incoming MIDI controls into the same desired control state as native edits. A stale whole-UI snapshot must not silently undo an accepted external edit.
6. Use the [exact atlas cover/page409 reference](../design/atlas-reference.json) for appearance, and engineering text for labels/counts/semantics. Keep dynamic controls separate from source artwork. Drawbar0 is inward/top and8 outward/bottom even though the concept shows inconsistent numbering.
7. Retain actual native screenshots, resize/playing/focus evidence and concrete visual differences. Source concept pixels are not an executed app, and an attractive view is not a measured 1:1 match.
8. Cabinet and microphone art cannot imply connected rotary processing. Baseline historical speed behavior is Slow/Fast; Stop requires a separately identified extension. Native screen-reader operation and physical controller latency require their own observed environments.

The actual assignment manifest and notes record dispatch, output and accepted results. The integrator owns coherent source qualification and publication.

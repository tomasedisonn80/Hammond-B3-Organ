# Continuation identity and compatibility review

**Assignment 53, continuation wave 09 — 2026-11-13.** Result: no mismatch in
the identity and migration contracts examined. This review compares actual Git
blobs and live data, checks the compiled parameter exporter, and runs two existing
control migration suites plus the retained schema-1 bundle verifier. It does not
repeat the platform or enabled-audio qualification reviews.

## Checkpoint and evidence boundary

The original source baseline is
`9c8068c95f6843dce95f7f22d729738eef8074f6`; the audited published continuation is
`2046b9388f6aab1122e37646b2f20199b5c6079f`, tree
`759ddcaf93be2047a5732034663e565f728fb5ad`. The executables used here come from the
coherent `checkpoint-w08-build`, built from tree
`0c722f1ffa2a2f04522438a4cb86cec6b8d3e392`. Direct Git comparison found only three
Markdown differences between those trees: `docs/DEVELOPMENT_LOG.md`,
`docs/STATUS.md`, and the continuation assignment index. All 96 tracked files
under `src`, `include`, `tools`, `tests`, and `data`, together with
`CMakeLists.txt`, matched the published source at audit time. These checks do not
claim that later worktree documentation edits were compiled.

The supplied atlas was independently hashed and inspected with `pdfinfo`: 500
pages, 21,248,265 bytes. This assignment reread its pedal rule on PDF p.140; the
project's full-document reading is recorded separately in the development
history. No physical instrument, calibration measurement, host, or external
factory scan was acquired for this review.

## Protected byte identities

Every file below is byte-identical in the baseline Git blob, published Git blob,
and live checkout. SHA-256 values describe the complete file bytes.

| Protected input | SHA-256 |
| --- | --- |
| [500-page supplied atlas](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| [Nominal authoring JSON](../../data/profiles/nominal-unmeasured-v1.json) | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| [Authoring schema](../../data/profile.schema.json) | `064beb58d186bb9ace5b2271c00c1b6f7d06c5ef43a403b6319344d92c1057af` |
| [Profile compiler](../../tools/compile_profile.py) | `2ca649de88a3f267970e4ed00fa6c08b7c234bffcc1b4c24b47a89be608fb2a8` |
| [Pedal map](../../data/pedal-map.json) | `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd` |
| [Original five-fixture catalog](../../examples/fixtures/catalog-v1.json) | `98ffa2c3bc30f60ceb839e1fc2ab978e45dcf5f2cb4970fe77f91894344c34f8` |
| [Two-manual score](../../examples/fixtures/two-manual-changes-v1.events) | `d86b7fb3e3a62865b218400828aaef7ee176c39da7f08ef29aed5ae5b0627ae8` |
| [A4 fundamental score](../../examples/fixtures/a4-fundamental-v1.events) | `c3295b7a060b7af68c6e3d43198a54cbe33ee26b6bc8e3c2cd1a76b80cfeb59f` |
| [Low-fold score](../../examples/fixtures/low-fold-coherent-v1.events) | `3ae330fbdf6f789dcd0533c521c63dce855e743000ecc283fae565009726ddea` |
| [Held-bank/Cancel score](../../examples/fixtures/held-bank-cancel-v1.events) | `fbd3060bdcae1bb7e4701de92799dca8ae0e4f92c5efedc84b450794c7e5ef5c` |
| [High-fold score](../../examples/fixtures/high-fold-coherent-v1.events) | `0431c06df58e4b66decf385f6fdbb4e89b146dcd80efaa0dc23d2d3155b120c0` |

Each score's actual digest also equals its catalog entry. The nominal profile
has three distinct identifiers that must remain explicit:

| Identity | Verified value and meaning |
| --- | --- |
| Profile ID | `nominal-unmeasured-v1` |
| Canonical authoring SHA-256 | `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83` |
| Compiled `B3PROFILE 1` SHA-256 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`; 4,545 bytes in the coherent build |

The canonical authoring value was independently recomputed with sorted JSON
keys, separators `(',', ':')`, `ensure_ascii=False`, `allow_nan=False`, and UTF-8
encoding, matching the [compiler convention](../../tools/compile_profile.py)
and [format contract](../PROFILE_FORMAT.md). It equals the compiled header and
catalog value. The raw JSON hash above includes its formatting. Retaining a
digest in a [runtime profile](../../include/hammond/Profile.h) records identity;
it does not authenticate an absent authoring document or a physical instrument.

## Identity domains and literal wiring

| Domain | Exact range or invariant | Source |
| --- | --- | --- |
| Tone IDs / source storage | One-based IDs `1..91`; zero-based indices `0..90`; conversion is `id - 1` after validation | [Types.h](../../include/hammond/Types.h) |
| Manual identity | `Upper = 0`, `Lower = 1`; two manuals | [Types.h](../../include/hammond/Types.h) |
| Manual key input / storage | MIDI `36..96`; indices `0..60`; authoring playing-key rows `1..61` | [Types.h](../../include/hammond/Types.h), [authoring profile](../../data/profiles/nominal-unmeasured-v1.json) |
| Manual source routes | `61 × 9`, 549 entries, actual range `13..91`; both manuals use this map | [authoring profile](../../data/profiles/nominal-unmeasured-v1.json) |
| Pedal map / source routes | Pedal IDs `1..25`; eight zero-based columns `0..7`; 200 positions, 195 connected; declared source domain `1..91`, actual connected range `1..68` | [pedal map](../../data/pedal-map.json) |
| Explicit pedal disconnections | Exactly `(pedal ID, column) = (8,1), (9,1), (10,1), (11,1), (12,1)`; JSON `null` means absent connection | [pedal map](../../data/pedal-map.json), atlas p.140 |
| Pedal bus columns | Brown `[0,1]`, red `[2,3]`, orange `[4,5]`, yellow `[6,7]` | [pedal map](../../data/pedal-map.json), [routing contract](../PEDAL_ROUTING.md) |

Every pedal row was compared with the constructive rule
`[p, third(p), p+12, p+24, p+31, p+36, p+40, p+43]`, where `third(p)` is
`p+12` for `1..7`, `null` for `8..12`, and `p+19` for `13..25`. The seven repeated
source pairs in columns 1 and 2 remain separate contact branches on different
buses. Neither deduplication nor substitution of source zero preserves this
contract. There is presently no pedal audio path or pedal `Manual` value.

Both retained independent factory transcriptions were decoded and compared
cell-for-cell with the current maps: 549/549 manual entries and 200/200 pedal
positions agree for each reviewer, including all five absent connections.
The two [manual CSVs](../../data/references/review-a-manual.csv) share SHA-256
`23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6`;
the two [pedal CSVs](../../data/references/review-a-pedal.csv) share SHA-256
`b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1`.
The [second manual](../../data/references/review-b-manual.csv),
[second pedal](../../data/references/review-b-pedal.csv), and
[provenance manifest](../../data/references/factory-table-iii.json) retain the
review trail. This assignment rechecked retained transcription agreement; it
did not perform a third independent reading of the original scan.

That documentary agreement concerns wiring. It does not calibrate the nominal
12-TET pitches, unit source peaks, base phases, drawbar gain law, or output gain;
nor does it establish pickup voltages, contact resistance, pedal shaping, or a
particular specimen's continuity. The original profile's historical
`independent_factory_verification: false` and missing-companion explanation are
preserved authoring provenance. Later [factory-reference evidence](../FACTORY_REFERENCE.md)
is recorded separately, without rewriting those protected bytes.

## Parameters and event values

All 39 baseline [parameter records](../../data/parameter-registry.json) are
field-for-field equal to the corresponding current records, including ranges,
defaults, units, conversion meaning, event targets, and provenance. Sorting
these records by numeric ID, then serializing with recursively sorted keys,
compact separators and ASCII escaping, gives SHA-256
`61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b`.
This is a digest of the original records, not of the entire changed registry.

| Stable parameter allocation | IDs |
| --- | --- |
| Upper A / Upper B drawbars | `4096..4104` / `4112..4120` |
| Lower A / Lower B drawbars | `4128..4136` / `4144..4152` |
| Expression / upper and lower bank selectors | `8192` / `8208`, `8209` |
| Appended percussion enabled, harmonic, volume, decay | `12288`, `12289`, `12290`, `12291` |

The compiled `hammond_parameter_info --normalized 0.5` export matched all 43
registry descriptors for IDs, paths, kinds, units, ranges, defaults, step counts,
and event targets. At that input, every drawbar emits position 4, expression
emits 0.5, and selectors/switches emit 1. This bounded exporter comparison does
not claim a new exhaustive test of every normalized value. The four additions
default to 0 and target upper-manual percussion indices `0..3`. These remain
proposed internal IDs, not verified host exports. Cancel and the two retained
route-enable bits are not additional scalar parameter IDs.

The whole registry intentionally advances from schema 1 /
`ideal-exclusive-ab-console-v1` to schema 2 /
`exclusive-ab-percussion-console-v2`.
[The current validator](../../tools/validate_parameters.py) accepts only the
named schema-2 registry. Preserving the 39 records does not imply that this
validator accepts an old schema-1 document.

The actual enum history is also append-only. The
[baseline Types.h](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/9c8068c95f6843dce95f7f22d729738eef8074f6/include/hammond/Types.h)
defines `NoteOn=0`, `NoteOff=1`, `Drawbar=2`, `Expression=3`, `AllNotesOff=4`,
`BankDrawbar=5`, `SelectBank=6`, `Cancel=7`.
[Console integration](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/4ead76957c763afbbddde1bc96f1128384329e50/include/hammond/Types.h)
adds `Percussion=8`; the [published continuation](../../include/hammond/Types.h)
preserves `0..8` and appends `KeyPosition=9`. Value 8 did not exist in the
original baseline. Enum preservation is not a promise of stable C++ object
layout or raw-memory preset serialization.

## Save-format and render-evidence compatibility

| Contract | Retained behavior | Deliberate extension |
| --- | --- | --- |
| Musical control input | Strict `B3CONTROLS1` is accepted; original expression, both manuals' retained banks, selections, and route bits survive | Missing legacy percussion controls become Off/Second/Normal/Slow, regardless of the destination's previous values |
| Musical control output | No implicit downgrade | Writer always emits complete `B3CONTROLS2`; missing, extra, malformed, or unknown-version input rejects atomically |
| DSP histories | Excluded from the control snapshot and save grammar | Restoring controls retains engine clock, held-key/contact history, source phases, and percussion readiness/history |
| Historical render evidence | Schema 1 retains its exact nine parameter fields, 18-token renderer invocation, 15 metrics fields, and original eight event commands | Schema 2 has 13 parameter fields, 26 invocation tokens, 18 metrics fields; adds console selections and `render_schema_version`, `contact_model`, `percussion_model` |
| New score commands | Schema 1 rejects percussion/key-position commands | Schema 2 accepts validated `percussion` and `key_position`; intermediate key positions require nominal contacts |

These are separate version domains: profile grammar, parameter registry, saved
controls, exporter envelope, and render bundle versions must not be inferred
from one another. See the [control-state parser/writer](../../src/ControlStateIO.cpp),
[ControlSnapshot](../../include/hammond/ControlState.h),
[save-format contract](../CONTROL_STATE_FORMAT.md),
[schema-2 producer](../../tools/render_fixture.py), and
[dual-schema verifier](../../tools/verify_render.py).

The existing `test_control_io` and `test_percussion_controls` suites passed
2/2 in the coherent build. The former checks all 16 percussion combinations,
destination-independent v1 migration, canonical v2 output, and rejection
behavior; the latter includes legacy restore with unchanged dynamic history.
Those histories are absent from the persisted format; the tests do not create
a portable DSP-resume format.

The retained [original render bundle](../../examples/rendered/nominal-two-manual-v1/bundle/manifest.json)
passed the current verifier: schema 1, six artifacts verified, 192,000 frames
at 48 kHz. Its manifest SHA-256 is
`74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`;
WAV SHA-256 is
`9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
The verifier did not replay audio or authenticate the recorded original tools,
source/build association, or physical fidelity. Schema-2 additions here were
checked against source contracts; enabled-audio qualification is a separate
review.

## Constraints for the next pedal or host task

1. Preserve the atlas, original profile, catalog, and scores as identified above.
   Give a changed model an explicit new identity and record why it differs.
2. Declare pedal row IDs, source IDs, storage indices, and any incoming MIDI
   mapping separately. Preserve `Upper=0`, `Lower=1`, manual MIDI `36..96`, and
   checked source-ID conversion. Do not route pedal IDs through manual-key
   conversion by accident.
3. Keep all 200 pedal positions, five explicit absences, seven duplicate-source
   branch pairs, and four physical bus groups. Agreeing with documentary wiring
   leaves gain/loading and physical calibration open.
4. Preserve all 43 existing parameter records and event values `0..9`. Allocate
   future identifiers explicitly; do not recycle values or change existing
   normalization semantics to accommodate pedals or a host API.
5. Specify any new saved-control version and its migration before extending
   state. Keep destination-independent defaults, transactional rejection, and
   dynamic history exclusions. Keep legacy saved-state acceptance separate
   from registry and bundle schema acceptance.
6. Retain the schema-1 evidence reader and exact old bundle contract while
   versioning future evidence changes. A new renderer schema is not permission
   to silently relabel historical bundles.

No implementation change was required by this audit. Commands, scope, and
handoff are recorded in [assignment 53](../development/2026-11-13-continuation/53-identity-compatibility-audit.md).

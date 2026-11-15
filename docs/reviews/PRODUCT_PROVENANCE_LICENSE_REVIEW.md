# Product provenance, dependency and notice review

## Result and inspected source

**A44's scoped provenance and notice checks pass.** No unexpected source,
dependency, pixel or notice hash mismatch was found. One current-facing shared
inventory defect was corrected: `DEPENDENCIES_AND_RIGHTS.md` said no extracted
atlas image was retained, although the retained JPEG and three decorative crops
were already accurately described in `THIRD_PARTY_NOTICES.md`. The updated
inventory also identifies the current 16/20-file Standalone and six-file
CrossoverTools rules; its dated nine-file observation remains explicitly
historical. No notice, license lock, application source, gallery payload or
existing evidence record was changed by this review.

Inspected checkout: `d556da017ea0a5d4f2d231416782dbc5066e58c2`, tree
`a3150fd2489a50a430b02c01eadd5e0c180bc7f9`, with concurrent test/install changes
identified separately. The [bounded audit](../development/2026-11-15-product-continuation/reports/A44-provenance-audit.json)
retains the checked file identities, six crossover source hashes, gallery
checks and exact install-rule hashes. This is source/asset inspection, not a
new build, numerical-suite run, installation or platform qualification.

## Supplied atlas and M6 derivation

The actual PDF remains **500 pages and 21,248,265 bytes**, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Its [source record](../research/source-manifest.json) matches. A44 read the
actual text of pp. 271–276 and compared the
[registry](../../data/crossover/leslie-122-ideal-v1.json),
[contract](../LESLIE_CROSSOVER_CONTRACT.md),
[native constants](../../src/LeslieCrossover.cpp) and
[reference admission](../../tools/crossover_reference.py).

| Checked claim | Actual atlas locator and retained classification |
| --- | --- |
| L2 = 0.0032 H; L3 = 0.0052 H; C16A = 0.0000078 F; C16B = 0.0000125 F | p. 271; documentary nominal values, not specimen measurements |
| L2/treble load A–H, C16A H–B, L3 A–W, C16B/bass load W–B | p. 272; treble voltage remains floating A–H |
| Two 16-ohm resistors, ideal imposed voltage and zero losses | p. 273; explicit illustrative fixture assumptions |
| Leslie 122 divider 052803, 1971; 113860, 1979 as related context | p. 271; related assembly is not an admitted substitute or measured 147 profile |
| Source citations S044-01/S044-02; absent `reference_code/crossover_ac_reference.py` | pp. 271–276; cited manufacturer drawings were not independently acquired or inspected for this model |
| Measured parasitics, drivers, polarity and specimen applicability unavailable | pp. 275–276; unknown physical fields remain null |

The registry correctly separates mathematical zero-loss assumptions from the
unknown winding resistance, capacitor ESR/leakage, actual complex driver
impedances, amplifier source impedance, acoustic polarity, serial applicability
and uncertainty. Its computational bounds and alternative resistor experiments
are labeled as numerical choices. No unidentified measured value or physical
rating was found masquerading as a factory value. The C++ module/probe and
Python algebra are newly implemented project work; they are not the missing
atlas companion, a complete amplifier/cabinet, or an Engine audio route.

The [retained acceptance report](../development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json)
still matches all six recorded source files and the available native probe
(`da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac`).
The [plot](../design/crossover/same-hz-nominal-v1.png), SHA-256
`6084be255054c1f11afdac26b3d8972721f9711598b13b30231ace69326bf39c`,
contains matching report/source/probe/plotter metadata and 24 observations.
Its authoring version is Matplotlib 3.10.8. The
[characterization](../LESLIE_CROSSOVER_CHARACTERIZATION.md) preserves the
difference between warped-reference agreement and same-Hz electrical errors;
the figure supplies neither new hardware data nor an audible acceptance.
Matplotlib is optional plot authoring, outside native code and CrossoverTools.

## Dependencies and required notice scope

The selected dependency locks, retained fonts/reference inputs and combined
notices have no changes from session start `647ae1b2`. A44 rehashed the available
locked local sources; no download was performed.

| Component | Checked identity and scope |
| --- | --- |
| SDL2 2.32.10 | Local commit `5d249570393f7a37e037abf22cd6012a4cc56a71`; 884-byte primary license SHA-256 `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` matches the [lock](../../data/dependencies/sdl2-lock.json). |
| RtMidi 6.0.0 | Local commit `1e5b49925aa60065db52de44c366d446a902547b`; both upstream source hashes and the 1,349-byte [retained notice](../../assets/standalone/midi/LICENSE-RtMidi.txt) match the [lock](../../data/dependencies/rtmidi-lock.json). Notice SHA-256 `7fa091d9c1aa492ebfcafa9f919d27bbce61e4f048ece2dfc3b7f93181e9e364`. |
| RtMidi prepared correction | Applying the two locked replacements in memory to the matching upstream source reproduces the declared 168,216-byte prepared source and SHA-256 `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a`. This did not create a prepared tree or qualify a live backend. |
| DejaVu 2.37 | Both retained TTF hashes, the source-manifest hash and generated `FontData.h` hash match their [records](../../assets/standalone/fonts/source-manifest.json). The complete 2,345-byte notice matches SHA-256 `22308e512b54800ba9fe6f9aecd6bea42b71f68f77dbc83196715aac50e631d6` and is reproduced in the generated header. |

The complete SDL2, yuv2rgb and selected HIDAPI BSD texts in
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) match the corresponding
locked local source texts after the stated trailing-whitespace normalization.
The Sun fallback comment is present in its source and matches its recorded
file hash. The notice accurately distinguishes archive compilation from final
linked math symbols, optional RtMidi from the MIDI-OFF build, and the font
permission text from the separate Debian packaging terms. A44 did not repeat
the earlier executable-symbol or VST3 artifact audits or generalize their
platform-specific observations.

No new runtime library, imported numerical implementation or missing notice
was identified in the scoped M6/probe/calibration sources. The existing
project-wide `LICENSE` remains unselected. The combined notice does not grant
rights to project code, the PDF or its artwork; these facts do not add an
approval step to the authorized development and local staging work.

## Reference pixels and eleven actual captures

The retained [JPEG extraction record](../design/atlas-reference.json) matches
the 412,664-byte source image, SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
The [decoration manifest](../../assets/standalone/reference/manifest.json)
matches its decoded RGB hash and all three compressed/pixel hashes. Each
decompressed crop equals its exact integer rectangle in that JPEG. This checks
the retained ancestry, without re-extracting the PDF stream. The existing
atlas concept remains the supplied design reference; no new AI artwork,
downloaded photograph or font input was added by this product continuation.

A44 rehashed both new gallery manifests: **39 normal payload files and 18
separate overlay payload files**, comprising eight plus three PNGs. All PNG
file/decoded-pixel identities, 108 production inputs against current bytes and
capture-commit blobs, 13 selected build inputs and both capture tools match.
The executable remains
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.
The [normal provenance](../../examples/demos/standalone-product-preview-v1/provenance.json),
[overlay provenance](../../examples/demos/standalone-product-preview-v1/midi-overlay/provenance.json)
and [A41 admission](PRODUCT_GALLERY_ADMISSION.md) identify actual native SDL
dummy audio/video/software-renderer execution at `d556da0`, MIDI backend OFF.
A44 did not repeat A41's visual or interaction admission.

All eleven original BMPs are unavailable after the author's recorded lossless
conversion checks. A44 verified the retained PNGs and decoded hashes, without
claiming a fresh BMP-to-PNG comparison or reconstructing original bytes. The
earlier root build receipt matches production inputs; its historical standalone
CMake hash differs because test-only rules advanced. That disclosed difference
does not turn the receipt into a later build attestation. The screenshots
include existing atlas-derived decoration, so their native-capture provenance
does not settle the source-art permissions in the
[existing rights record](../research/RIGHTS_AND_SOURCES.md).

## Calibration fixture and component payloads

The [calibration driver](../../apps/standalone/native_tests/calibration_lifecycle_driver.cpp)
uses the real application lifecycle with a separate
[test-only compatible dependency](../../apps/standalone/native_tests/fake_calibration/RtMidi.h).
Its API-boundary callback schedule is explicitly synthetic. It is neither an
upstream RtMidi replacement shipped with the application nor evidence from a
physical controller. All 14 source entries in the
[latest retained calibration report](../development/2026-11-15-product-continuation/reports/gcc13-facade-root-native-calibration.json)
match. A26's earlier report differs on the later driver/facade edits; A38's
report differs on the later facade edit. Those are valid historical records,
not hashes to rewrite or promote to current-source qualification.

| Source-inspected component | Payload and notice treatment |
| --- | --- |
| [Standalone](../../cmake/InstallStandalone.cmake), MIDI OFF | 16 files including the executable, combined notice, complete SDL2/DejaVu notices, font/reference provenance, capability metadata and A43's added `MIDI_EXPRESSION_GUIDE.md`. |
| Standalone, MIDI ON | 20 files: the same 16 plus the exact RtMidi notice, dependency lock, prepared-source record and correction patch. MIDI backend capability is distinct from a working physical device. |
| [CrossoverTools](../../cmake/InstallCrossoverTools.cmake) | Six files: native probe, standard-library Python reference, registry, two documents and unchanged combined notice. No atlas, plot, fonts, SDL/RtMidi source, interpreter or calibration fixture is copied. |

Standalone binds configured metadata hashes and preflights the exact required
notice/correction identities before copying. CrossoverTools preflights its
fixed six inputs and copies the combined notice without manufacturing a project
license. Neither component installs the calibration test probe. A44 inspected
the actual rules and matching inventory assertions; execution of A43's updated
installed workflows belongs to the integrator's separate result. During this
review, the [root installed-workflow log](../development/2026-11-15-product-continuation/reports/A43-root-installed-ctest.txt)
recorded 1/1 CTest passing in 5.31 seconds, with eight Python methods and the
16-file MIDI-OFF payload at the same `7ded143b…` executable. A44 read that result;
it did not execute it or infer a MIDI-ON/platform pass from it.

## Exact continuation gates

The documentation discrepancy is repaired in
[the current inventory](../DEPENDENCIES_AND_RIGHTS.md). Following the observed
local MIDI-OFF install result, the remaining integration gate is source-identified
hosted qualification of the repaired test/build source, including MIDI-ON
payload/platform and instrumented calibration paths, while preserving the
earlier failures and source-specific records. A44's hash inspection cannot
replace those execution results or prove the later source was published.

The next M6 numerical task remains a versioned electrical-accuracy protocol
before evaluating a differently identified realization; the
[developer guide](../CROSSOVER_DEVELOPER_GUIDE.md) and
[characterization](../LESLIE_CROSSOVER_CHARACTERIZATION.md) retain its inputs.
Physical promotion separately needs the applicable primary drawing, identified
assembly and calibrated component/load/multiport evidence with uncertainty.
Real controllers/displays, literal 1:1 UI equality, complete circuit/cabinet
fidelity and any broader distribution claim remain outside this audit.

**Executed verification:** bounded local SHA-256/JSON/Pillow/Git-object checks,
`pdfinfo`, `pdftotext -f 271 -l 276 -layout`, direct source/notice comparison and
owned Markdown link/whitespace checks. No build, test suite, native application
process, dependency acquisition, commit or publication was performed by A44.

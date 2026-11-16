# Reference apron interaction preservation admission

**A33 / wave 6 / `/root/w06_a33`, 16 November 2026: admitted for the frozen
software-rendered interaction and inactive-layout preservation scope.** No
concrete apron interaction regression or additional focused test is identified.
The [contract](../design/REFERENCE_APRON_CONTRACT.md) and its original fixture
remain unchanged; this review neither expands their coverage nor closes physical
input, accessibility, display/DPI or literal whole-interface 1:1 acceptance.

## Source and evidence binding

Live HEAD is base `54df95fe343d417dd89bb7a91f85e4f51c08dfe7`. The
`InstrumentView.cpp` diff replaces exactly one apron `reference_wood` call with
`apron_art`, retaining the original call and arguments as fallback. Activation,
endpoint mapping, control/key geometry and the subsequent
`reference_controls → reference_footer → overlay` ordering are unchanged.
Drawing adds an optional initialization-time texture and one full-source copy;
its painter receives no model or input state.

I recomputed all 15 source hashes in the
[paired report](../development/2026-11-16-preset-library-continuation/reports/apron-paired-final.json),
its checker hash and all three executable hashes: every value matches. The
report SHA-256 is
`5305e9d2d339c327c860d00fbb00f7ba0679c03dccc92d95f62c44fe4b65b896`.
The [genuine-before receipt](../development/2026-11-16-preset-library-continuation/reports/apron-genuine-baseline.json)
binds retained before `8391cb06…`; the report binds that binary, candidate
`0a7b2d50…` and unavailable-texture `2577977a…`. The original fixture is still
`59cecf6b…`.

Byte comparisons against `git show 54df95fe:<path>` independently establish
unchanged `UiModel`, `InstrumentView.h`, `main.cpp`, `ScriptedInput`, `MidiInput`,
`InputProcessor`, `PerformanceInput` and `ParameterBridge`, including each paired
header. Selected current SHA-256 identities:

| Source | SHA-256 |
| --- | --- |
| `apps/standalone/UiModel.cpp` | `0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd` |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| `apps/standalone/ScriptedInput.cpp` | `a023e8a0a900f1cd7000d532c511d5593d11507eeb997300ff2bd3325c13cc23` |
| `apps/standalone/MidiInput.cpp` | `4ddd655fb4a21040f2f83228fb23e38f98d0abe21d5bce7f0e28d064b5b7477c` |
| `src/InputProcessor.cpp` | `d5543a2e4fbd34114da30ac28430130e4b5b5d00110c8c29cae80c85986a76fc` |
| `src/PerformanceInput.cpp` | `80b9b77bca9e17f8b9a866daca32468d649ae4d6b975f1f0c66ceebba646b189` |
| `src/ParameterBridge.cpp` | `296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220` |

This is a scoped source-preservation finding; the separate registration-library
changes are not described as unchanged.

## Semantic states and independent footer protection

The fixture serializes complete desired/applied controls, copied session, focus,
pending/dirty/recovery flags and `InstrumentViewInfo`. Its before/after paint
comparison additionally includes every control/key geometry, omitted only from
the bounded stream. The consumer validates frozen expected semantics before
requiring equality of complete before/candidate/unavailable headers.

I invoked only candidate `--case 16`, `17`, `18`, `19` to inspect contract cases
17–20. Each emitted header and payload hash reproduced its existing report
identity; this was not a new 25-case pixel admission.

| Contract case | Observed semantic distinction | Changed apron pixels | Compared footer pixels / changes |
| --- | --- | ---: | ---: |
| 17 | Running in session and info; peak 0.75; dirty drawbar; 17 clipped samples | 32,542 | 56,016 / 0 |
| 18 | Pending and dirty; desired Upper bank A versus applied B; Lower B drawbar index 4 desired 5 versus applied 4; focus `[4,1,1,4]`; held Upper/Lower/pedal indices 24/36/12 | 32,542 | 56,016 / 0 |
| 19 | Recovery true; `RecoveryPending` status 11; recovery/overflow/rejected/discarded counts 2/1/2/3; explicit release-held-keys message | 32,542 | 56,016 / 0 |
| 20 | Audio overlay 2; selected device 1, 96 kHz, 256 frames; current configuration remains 48 kHz/512 | 32,479 | 56,016 / 0 |

Case 18 preserves the existing preset-pending footer priority. Its pending
controls and fixed focus are real metadata/paint inputs, but it does not
separately exercise the controls-only footer wording. Held-note and focus pixels
outside R are protected by the independent exterior comparison.

The consumer derives F from contract coordinates and counts differing RGBA
pixels in its complete output-intersected center box, independently of the R
allowance. It does not subtract F and then declare success from an empty mask.
Each semantic case compares all 56,016 visible F pixels. Across the retained
25 cases, 1,851,123 F centers and 60,026,983 pixels outside allowed R have zero
changes. These are fixed copied-state raster observations, not physical MIDI or
live callback journeys.

## Hidden/inactive frames and direct compositing

Cases 14–16 and 21–25 have zero differences across each entire frame, with
identical before/candidate/unavailable RGBA hashes. They cover enabled-empty
clip, a positive-area 256-pixel disjoint clip, output height 880, inactive
1399-wide/819-high Play, Flat, Rotary and Service. Cases 14–15 still compare
126,036 output footer centers despite none being visible through their clips.
Case 16 and inactive cases have empty F masks; their admission instead requires
explicit whole-frame equality. Thus those empty masks supply no footer claim.

The separate direct native executable still matches `7212b9dc…` in the
[native qualification](../development/2026-11-16-preset-library-continuation/reports/w03-apron-native-qualification.json).
A fresh invocation passes **95 checks, zero failures**: four canonical probes,
five renderer-state probes and sixteen invalid bounds. Before any footer paint,
all 56,016 hole texels retain opaque blue/gold backdrops; all 32,544 opaque texels
match embedded RGBA. Scale, viewport, clip/enabled state, blend and color are
preserved; same/fresh Drawing repetition passes. Independent original-JPEG
identity remains the separate [asset admission](REFERENCE_APRON_ASSET_ADMISSION.md).

Verification used the existing Linux SDL 2.32.10 software renderer without audio
or windows. No build, fixture/production edit, broad rerun or gallery acceptance
was performed. Expanded application-gallery inspection and real device,
accessibility, DPI and literal whole-interface 1:1 gates remain separate.

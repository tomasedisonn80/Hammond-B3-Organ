# Streaming continuation compatibility review

**A30, wave 5; 16 November 2026.** The audited overlay preserves the nominal
dry Engine and musical identities. One matched dry fixture is byte-identical.
Source preservation and observed output are separate findings; neither proves
universal audio equivalence or physical fidelity.

The [audit receipt](../development/2026-11-15-streaming-continuation/reports/A30-compatibility.json)
records the UTC observation, commands, hashes and inventories. Base/HEAD was
`4aac394cde4da40906b615573a8779aee2d9a37a`, tree
`3605c9ce098a052afc10b2969fefe31e15644fe9`, with an uncommitted overlay.

## Source preservation

All **187** entries in the saved baseline source manifest were rehashed:
**185 match**; only `apps/standalone/CMakeLists.txt` and `InstrumentView.cpp`
differ. Comparing every original tracked file against its base Git blob found
**3,742/3,748 identical**. The six differences at audit time were
AGENTS, README, top-level CMake, standalone CMake, InstrumentView and
StandaloneBenchmark.cmake. This **audit-time inventory** may change during later
documentation reconciliation; production findings remain bound to their hashes.

CMake adds the research object/probe, tests and material raster fixture; the
benchmark identity gains the new header. Compiler/audio flags are unchanged.
The painter selects the new material only for the upper registration panel in
the existing active composition. UiModel, Session, input, audio-device and
musical-state code are unchanged.

| Invariant | Source-based finding |
| --- | --- |
| Default dry Engine | All 59 original core/header files match. `prepare` retains the legacy console and clears optional leakage. ContactBank/mixing are unchanged. |
| 91 shared sources | `kToneSourceCount = 91`; the bank advances once per frame, including silence/disconnected output. Notes alter contact targets without resetting phase; velocity does not scale steady loudness. |
| 47 parameters | Registry has 47 unique IDs; its bytes and ParameterBridge are unchanged. |
| Saved controls | Unchanged ControlState/ControlStateIO retain `B3CONTROLS4` and readers 1–3, without migration or newly saved transient history. |
| Plugin identity | All 20 plugin files match. Processor FUID words: `19F9ADC0 533F42B4 B96BD51D 6547E838`; controller: `0DEE76AB 26BC475A BF64F138 C89FB0E0`. |
| Note ownership | Manual/pedal owners, input/timeline and standalone ownership paths are unchanged; the last owner still controls physical release. |

`CausalContactGrid` is a separately named `hammond::research` class. Its
translation unit enters the static archive for its explicit probe/tests.
Inspection/search found no Engine/adapter reference, automatic initialization
hook or audio reconstruction/filter route. Live integration remains separate.

## Original evidence and frozen installation

The original PDF is unchanged: **21,248,265 bytes**, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
All **135 art/font/assets entries**, **71 data files**, **157 test files** and
**585 example files** present at base match their original blobs; these groups
overlap. New gallery/test files are additive and do not replace original evidence.

All **48 ContactReferenceTools payload files** and its CMake installation module
match base, including frozen contracts, 36 fixtures, manifest and probes. Rules
retain `EXCLUDE_FROM_ALL`, copy-only preflight and refusal to merge an existing
package. No causal-grid file enters the component. A30 did not rerun installation.

## One observed dry fixture

From the repository root, using the preserved genuine-before profile and a
fresh owned destination:

```sh
../build-native/hammond_render --profile ../baseline/nominal.b3p \
  --output ../compatibility-work/dry-organ.wav --frames 8192 \
  --sample-rate 48000 --block-size 64 --seed 0 --drawbars 888000000 \
  --note 60 --fail-on-clip
```

Candidate exit was **0**, with empty stderr. Before/candidate renderer bytes and
baseline/current profiles match. The stereo signed-16-bit WAV, PCM and metadata match;
maximum absolute difference is **0 across 16,384 samples**, with zero clipping.
The [original candidate stdout](../development/2026-11-15-streaming-continuation/reports/A30-dry-render.log)
retains peak `0.076829910278320312` and RMS `0.031813211947603344`.

| Equal before/candidate artifact | SHA-256 |
| --- | --- |
| Renderer | `928205dc3b31e57faa7664cb39e691659d1c7f7430b5555ade70b4a9830835bf` |
| Profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Complete WAV, 32,812 bytes | `35a460e99da4c9354e23ec13bb53a70c99f5cd5b70ecf337ec3926c422c7025d` |
| Decoded PCM, 32,768 bytes | `5ce533bce565ede2bd3e2744a1f3cd97aead5c8cd456f762d7dfb0e511e95f9c` |

**Receipt-label correction:** the unchanged baseline qualification field
`baseline_pcm_sha256` actually identifies the complete WAV, not decoded PCM.
Both identities are recorded without changing the original report. Its baseline
application executable field is distinct from the renderer identity above.

## Limits and handoff

Root subsequently completed **210/210 CTests in 191.89 seconds**; its
[coherent receipt](../development/2026-11-15-streaming-continuation/reports/coherent-qualification.json)
binds 505 unchanged code/input files and the same renderer. A30 verified that
inventory and the compressed CTest log hash; A30 ran no build or broad suite.

The dry fixture covers one profile, note, registration, seed, rate and block
size. Native VST3, physical devices, callback deadlines, contact physics,
full-window reconstruction and literal whole-interface 1:1 remain separate
gates. Production changes need affected requalification; later prose edits
alone do not invalidate this fixture.

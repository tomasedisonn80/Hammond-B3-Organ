# Nominal pedal audio fixtures and independent PCM acceptance

The [pedal catalog](../examples/fixtures/pedals/pedal-catalog-v1.json) contains
four original, reproducible scores for the implemented nominal pedal division.
The [acceptance suite](../tests/test_pedal_catalog.py) renders actual stereo
PCM16 WAVs and checks their contents independently of the production routing,
mixture implementation and source phase initializer. The original five manual
and three console scores and their two catalogs remain unchanged.

This is synthetic software evidence. The atlas requires shared generator
identity, literal contact routing, separate control history and declared linear
reference behavior on [pp. 139–144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139).
[Page 447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447) permits explicitly
named nominal console models while electrical models remain incomplete.
The fixed matrix and linear position gain come from the project's
[adopted integration contract](PEDAL_INTEGRATION_CONTRACT.md), not from recovered
reactor values or measured 16-foot/8-foot transfer functions.

## Catalog contract

The catalog has its own **schema 1**, identity
**`nominal-pedal-fixtures-v1`**, and status **`synthetic-unmeasured`**.
This version is distinct from renderer/evidence schema 3 and control-state
`B3CONTROLS3`. The catalog binds:

- The unchanged atlas identity and relevant one-based PDF pages.
- The nominal profile's canonical authoring hash and compiled profile hash.
- The raw and canonical pedal-map hashes, both retained pedal CSVs and both
  retained manual CSVs.
- The 45 current parameter records' canonical hash, registry schema/model and
  the two permanent pedal parameter IDs, `0x4000` and `0x4001`.
- Ordered Brown/Red/Orange/Yellow buses, rational matrix numerators,
  denominator 8, position-gain denominator 8 and the all-200-unit-weight policy.
- Exact score bytes, initial registrations, rates, seeds, block size and
  explicit stationary, silent and audible spans.

Only the parameter **record array** is hashed for this binding. A later change
to registry provenance or qualification metadata does not silently change the
control records being exercised. Any actual control-record or profile/model
change needs deliberate fixture admission under its stated identity.

All four scores use **48,000 frames per second**, ideal manual contacts,
percussion off and a nominal 127-frame block. The test also renders each score
with blocks of 1 and 1,024 frames. This musical catalog's observed gate is at
48 kHz; separate Engine and renderer suites cover the other admitted rates.

| Score | Duration | Initial manual / pedal registration | Explicit expression | Purpose |
| --- | ---: | --- | ---: | --- |
| [pedal-mixtures-v1.events](../examples/fixtures/pedals/pedal-mixtures-v1.events) | 1.0 s | `000000000` / `40` | 0.5 | Hold pedal 1 through `40`, `04` and `44`; distinguish the mixtures and preserve its two separate ToneId 13 paths. |
| [pedal-shared-source-v1.events](../examples/fixtures/pedals/pedal-shared-source-v1.events) | 1.2 s | `000000000` / `40` | 0.5 | Add lower-manual MIDI 36, drawbar index 2, and pedal 13 to pedal 1; release their contributions independently. |
| [pedal-held-routing-v1.events](../examples/fixtures/pedals/pedal-held-routing-v1.events) | 1.2 s | `000000000` / `00` | 0.5 | Press while muted, unmute twice, Cancel/reselect the lower manual and issue a manual panic while retaining the pedal; include pedal 8's disconnected position. |
| [pedal-phrase-v1.events](../examples/fixtures/pedals/pedal-phrase-v1.events) | 3.0 s | `006400000` / `32` | 0.75 | An original C–F–G–C gesture using two manuals and pedal rows 1, 6 and 8, with explicit release and silence. |

The pitch names in the last row describe the **nominal 12-TET software profile**.
Pedal IDs are wiring-row identifiers 1–25; no physical pedal MIDI octave is
inferred. The lower bank is configured by the score. Initial upper registration
applies to bank B, and all score changes retain their literal sample ordering.

The fixture bounds allow four scores, at most 144,000 frames per score, 8 KiB
per score, 64 events and 12 events at one frame. A score has no more than eight
fits; each fit spans 2,400–24,000 frames and at most 24 distinct sources. The
committed scores contain **63 events in total**. Unknown or malformed commands,
changed identities, unexpected fields, path traversal, out-of-domain controls,
unbounded fit specifications and fits crossing a score event reject.

## Independent amplitude and phase checks

Both retained pedal CSV maps are parsed as literal 25-by-8 tables and compared.
All 195 connected positions and five empty cells remain explicit. Both manual
CSV readings are also compared; manual MIDI 36 selects physical key 1, and the
CSV cell selects its source. The test never invokes the production route
compiler, generated header, routing formula or mixture function to construct
expected audio.

For each admitted stationary span, the catalog declares held pedals, the two
positions and any active manual branches. The pedal coefficient for source
`t` is calculated with exact rational arithmetic:

```text
coefficient[t] = sum over matching connected contact positions
                 (p0 * [4,2,1,1][bus] + p1 * [1,4,2,1][bus]) / 64
```

The literal contact-to-bus sequence is Brown, Brown, Red, Red, Orange, Orange,
Yellow, Yellow. Repeated sources remain separate terms. A manual branch adds
the bound source profile's declared manual drawbar gain. The final expected
component peak is the resulting coefficient times the source peak amplitude,
explicit expression and profile output gain. All are normalized software
quantities. No volts, physical winding resistance or acoustic calibration is
implied.

The shared-source fixture makes ToneId 13 particularly observable. Its expected
coefficient before common gain/expression moves through:

| Span state | ToneId 13 coefficient |
| --- | ---: |
| Pedal 1 alone, Mixture 1 position 4 | `3/8` |
| Add lower-manual MIDI 36 / drawbar index 2 at position 8 | `1 + 3/8` |
| Add pedal 13 at the same mixture setting | `1 + 5/8` |
| Panic the lower manual | `5/8` |
| Release pedal 1 | `1/4` |

The two pedal-1 paths contribute `1/4 + 1/8`; deduplicating the repeated source
would therefore produce a detectable amplitude error. The suite verifies that
this wrong model and a separate altered-mixture model both fail its amplitude
gate. These are oracle sensitivity checks, not compiled production mutations.

Initial phase is deliberately **estimated from the actual PCM**, without
copying a generator PRNG. At the bound source frequencies, a small least-squares
fit uses sine/cosine basis functions at each sample's absolute frame position:

```text
x[n] = sum_t (a[t] sin(2π f[t] n / fs) + b[t] cos(2π f[t] n / fs))
```

The component peak is `hypot(a,b)`. The normalized pair `(a,b)/hypot(a,b)` must
remain consistent whenever that same ToneId appears again in the score. This
checks shared phase across mixture changes, overlapping manuals/pedals, muted
intervals, Cancel/reselection and later note returns. It does not authenticate
the unknown initial phase against a physical instrument.

The fit uses every fourth sample to construct its normal equations, with a
checked frequency limit below the resulting 6 kHz Nyquist boundary. A bounded
partial-pivot solve rejects singular fits. **Residuals are then checked on
every sample in each entire fit window**, not just the subsampled fit points.

The held-routing score also has an explicit counterfactual render: start with
pedal registration `40` instead of `00`, keeping the same score, profile, seed
and clock. Its initially audible prefix must be nonzero, while every PCM sample
from frame 4,800 onward must equal the originally muted render. The later
mute/unmute pair additionally participates in the independently fitted phase
checks. No source reset or invented envelope is used to make the comparison.

## Fixed tolerances and observed local result

Tolerances were fixed before the first run and are versioned in the catalog and
independently asserted by the suite. They were not widened after execution.

| Quantity | Acceptance bound | Largest observed error |
| --- | ---: | ---: |
| Component peak, normalized output | `4 × 10^-5` absolute | `1.4432453011507633 × 10^-6` |
| Shared normalized phase-vector component | `0.006` absolute | `0.0008450474547653242` |
| Full-window residual | `2.0` PCM16 LSB | `0.5954989038965657` PCM16 LSB |
| Partitioned WAV and unmute suffix | Exact bytes/samples | Exact match |

Declared audible spans must contain a PCM magnitude of at least 64. Declared
silent spans contain only zero samples, and all dry left/right samples agree.
The renderer must report zero clipped frames and respect each score's explicit
float-peak bound; the suite neither rescales nor limits output.

The first coherent Release run passed **1/1 CTest suite, five Python methods,
zero failures and zero skips, in 3.24 seconds**. It executed 13 native renders
covering 979,200 mono frames; 19 fits covering 184,800 full residual samples;
155 component-amplitude comparisons; and 103 shared-phase comparisons.
All four scores had identical complete WAV files at blocks 1, 127 and 1,024.
The initially muted comparison matched the 52,800-sample suffix exactly.

The tested base was frozen wave-4 tree
`f84cacb4e6eb01189ca29136fc838885fdd858f4`, overlaid only with this catalog, its
four scores and its test. The coherent renderer SHA-256 was
`42e4373f6ea80eb0c87238b009283b729e89d71858fc73085831069e84f79d59`.
This local result belongs to GCC 14.2.0, CMake 3.31.6 and Python 3.12.14.
Whole-repository and hosted qualification are separate integrator gates.

## Reproduce the checks and the musical phrase

From a coherent checkout containing these fixtures:

```sh
cmake -S . -B build-pedal-catalog -DCMAKE_BUILD_TYPE=Release
cmake --build build-pedal-catalog --target hammond_render -j 4
ctest --test-dir build-pedal-catalog -R '^python_test_pedal_catalog$' --output-on-failure
```

The Python suite also accepts explicit `--renderer` and `--profile` paths.
Missing prerequisites fail instead of skipping audio checks. On a typical
Windows multi-configuration build, select `--config Release` and use the
corresponding `Release/hammond_render.exe` path.

For a new WAV filename under an existing output directory:

```sh
cmake -E make_directory out
./build-pedal-catalog/hammond_render \
  --profile build-pedal-catalog/nominal.b3p \
  --output out/nominal-pedal-phrase.wav \
  --events examples/fixtures/pedals/pedal-phrase-v1.events \
  --frames 144000 --sample-rate 48000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 \
  --contacts ideal --percussion off \
  --percussion-volume normal --percussion-decay slow --fail-on-clip
```

To retain a new [schema-3 evidence bundle](PEDAL_RENDER_EVIDENCE.md), select an
unused directory and preserve the same score/controls:

```sh
python3 tools/render_fixture.py \
  --renderer build-pedal-catalog/hammond_render \
  --output-dir out/nominal-pedal-phrase-evidence \
  --events examples/fixtures/pedals/pedal-phrase-v1.events \
  --frames 144000 --sample-rate 48000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 \
  --contacts ideal --percussion off \
  --percussion-volume normal --percussion-decay slow
python3 tools/verify_render.py out/nominal-pedal-phrase-evidence
```

This assignment retains the score/catalog and test, not a generated WAV or
evidence bundle. A later demo assignment must actually run and independently
verify the retained artifact before claiming publication of that audio.

## Remaining gates

These checks qualify selected software gestures and fixed nominal coefficients.
They do not establish physical low-wheel spectra, reactor/load response,
pedal-contact timing, factory gearing, switching bandwidth, AO-28/scanner/Leslie
processing, native host behavior, device deadlines or a measured instrument
match. Ideal switching can click; this catalog does not qualify alias suppression.
No cross-compiler/libm byte-identical audio promise follows from a same-build
partition comparison.

A measured replacement needs new source/model identities, electrical units and
uncertainty, named specimen/load/capture boundaries and independent acceptance.
Preserve these original nominal fixtures as compatibility evidence instead of
renaming their output a calibrated pedal model. Exact assignment commands,
source hashes and handoff are retained in
[assignment 27](development/2026-11-13-pedals/27-pedal-audio-catalog.md).

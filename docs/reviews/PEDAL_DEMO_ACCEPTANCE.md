# Independent acceptance of the retained pedal demo

Assignment **44/60**, wave **8**, 2026-11-13 pedal-development session. The
[retained three-second pedal phrase](../../examples/demos/pedal-phrase-v1/README.md)
passes independent artifact, source-inventory, score, PCM, analysis-window and
current-renderer checks. No production or demo defect was found. This review
qualifies the named **nominal, unmeasured software model** and its retained
evidence; it does not establish measured Hammond response or subjective quality.

The executable regression gate is
[`tests/test_pedal_demo.py`](../../tests/test_pedal_demo.py). Its final focused
run passed **10 methods, zero failures, zero errors and zero skips in 1.936 s**.
It includes five actual renderer calls and ten independently changed copies of
the retained bundle. Root's combined checkout/CTest and publication gate remain
separate from this focused result.

## Evidence inspected

The seven-file schema-3 bundle is unchanged. Its exact files are the manifest,
authoring JSON, compiled profile, ordered score, WAV and raw stdout/stderr.
The complete demo directory contains **18 files**: those seven, eight analysis/
verification reports, the source inventory, README and adjacent provenance.
The final provenance inventories all other **17 files**, explicitly excluding
itself. Every recorded byte count and SHA-256 matched the actual file.

| Retained identity | Observed value |
| --- | --- |
| Published source commit | `d7b886103f8c9d4649ffa1c35930b79808217a3d` |
| Source tree | `018c3897889aaae0070f632981e0c889a35cad30` |
| Source inventory SHA-256 | `4b207c6ad747761442ab326b3fd683ecd48fbbf6b1eedea4a8de600b832b64e8` |
| Final provenance SHA-256 | `da04261fe618b457d3e4162550d905efac5faa02049c2d00485ee0a186ea184b` |
| README SHA-256 | `54433a625801fcf3c1b7bbb9ca35d067118a6eb5eb2af9c46168954f44baf9c8` |
| Manifest SHA-256 | `8cca3be0d5f451e9574590a211db748885062446674e46efb2a5e385027efb87` |
| Complete WAV SHA-256 | `a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1` |
| PCM data SHA-256 | `3107d186bb811b2cf1a2a3497422f5d77169f92ca2c9c7f22a1553482141c77c` |
| Canonical authoring-profile SHA-256 | `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83` |
| Compiled-profile SHA-256 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Score SHA-256 | `47daa264ca9524c98d7a189d28728778c9057852b8fd3d68e7fea9d2e63b9be5` |

The 474 source records were independently compared with `git ls-tree -rz` and
the actual `git cat-file --batch` blob contents. Paths, file modes, Git blob
identifiers, byte counts and SHA-256 values all matched. The commit's actual
tree also matched. The committed test separately reconstructs the Git tree
objects from the retained inventory, including tree ordering and directory
modes. That structural check runs even when CI has only a shallow checkout;
it does not require access to the historical commit's objects.

The adjacent provenance's 17 translation-unit identities agree with that
source inventory. Its original renderer is 135,320 bytes, SHA-256
`a0a33ffad00f01f82e3e25fb59b9225c0d4aa5655ce601fea3b81e2c8af9079e`.
The manifest correctly retains unavailable HEAD/dirty observations for its
plain source archive. The independent consumer reports
`source_build_association: not_established`, and this review preserves that
authentication limit. Local build records and matching source inventories
are useful observed provenance, not a signed source-to-binary attestation.

## Independent PCM and musical checks

The new parser uses only Python's standard library and reads the canonical
44-byte RIFF header directly. It checks integer PCM encoding, two channels,
48,000 Hz, 192,000 bytes/s, four-byte frame alignment, 16 bits per channel,
576,000 data bytes and an exact total file size of 576,044 bytes. Every one of
the **144,000 stereo frames** has equal left/right samples. The PCM payload's
hash is calculated separately from the complete WAV hash.

Integer arithmetic over one channel gives a maximum absolute code of **2,762**,
sum of squares **81,653,430,143** and **115,143 nonzero samples**. There are no
codes at either full-scale endpoint. With the analyzer's declared division by
32,768, peak is **0.08428955078125** and RMS is **0.02298031808643901**. The
retained renderer's distinct float measurements are peak
**0.08429475128650665**, RMS **0.022980303816301697**, zero clipped frames and
zero clipped channel samples. The float/PCM metrics agree within one PCM code;
the test does not confuse quantized endpoint counts with proof of float-domain
clipping.

All seven retained analysis reports were checked against newly calculated
integer sums, squared sums, nonzero counts, peak, RMS, DC and stereo equality.
Both reported channels and all frame/window boundaries agree.

| Window | Half-open frames | Nonzero frames per channel | PCM peak | PCM RMS |
| --- | --- | ---: | ---: | ---: |
| Whole | `[0, 144000)` | 115,143 | 0.08428955078125 | 0.02298031808643901 |
| Leading silence | `[0, 4800)` | 0 | 0 | 0 |
| C opening | `[7200, 30000)` | 22,776 | 0.08428955078125 | 0.024494867757760046 |
| F | `[36000, 58800)` | 22,797 | 0.0673828125 | 0.027184468073167222 |
| G | `[64800, 87600)` | 22,791 | 0.07232666015625 | 0.026511671248796307 |
| C return | `[93600, 116400)` | 22,794 | 0.064666748046875 | 0.024419268855217228 |
| Trailing silence | `[120000, 144000)` | 0 | 0 | 0 |

These are overlapping reports of one three-second render, not additional
independent audio duration. The mixture has no declared monophonic frequency
estimate. All leading 4,800 and trailing 24,000 frames are exactly silent.

The literal 38-event score was compared with an independently written timeline
and the accepted catalog. This includes expression 0.75; the lower B bank's
8-foot setting; upper registration `006400000`; pedal positions `32`; four
chord starts at frames 4,800, 33,600, 62,400 and 91,200; separately ordered
upper, lower and pedal panics; and final release at frame 120,000. The C/F/G
names describe the nominal profile. Pedal values 1, 6 and 8 identify wiring
rows, without inventing a physical MIDI octave. The profile, seed 2704,
48 kHz rate, 144,000 frames, ideal contacts and disabled percussion all match
the manifest and [catalog contract](../PEDAL_AUDIO_ACCEPTANCE.md).

## Actual current replay and component oracle

Replay used the coherent assignment-42 SDK-free Release executable at
`/workspace/scratch/f364bc93d920/a42-build/hammond_render`, 135,320 bytes,
SHA-256 `9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
Its source is the same published base with the frozen assignment-37 CLI changes
and assignment-42 metadata changes. All **476 files** in its existing source
manifest were independently rehashed and matched; that manifest's SHA-256 is
`f252333abfc019e31c85778b34f3eccdcaab3d2bb8f6e242ed6c2414a1a3d508`.
No live header was linked to an older library. The observed environment was
Linux x86_64, glibc 2.41 and Python 3.12.14; the reused coherent build records
GCC 14.2.0 and CMake 3.31.6.

Actual current renders at blocks **64, 127 and 1,024** matched one another and
the historical complete WAV/PCM exactly, including the hashes above. This is
an observed same-platform result. The portable committed test pins historical
bytes, but requires exact current partition agreement only within the current
build. It makes no cross-compiler or cross-libm bit-equality promise and does
not assert fixed historical floating-point metric strings against every future
platform.

Two further renderer calls use independently constructed manual-only and
pedal-only scores. Each retains the same clock, seed, expression, chord times
and final panic. The manual call sets pedal positions to `00`; the pedal call
uses no manual notes or lower-bank setup and sets manual registration to zero.
Both outputs have nonzero energy throughout every declared chord window and
exact leading/trailing silence. Their observed float peaks are
**0.06138529255986214** and **0.024127578362822533**; their float RMS values
are **0.018544125952660015** and **0.007645064451056262**. All clip counters are
zero, and none of the five renders exceeds the phrase's 0.103 peak bound.

Adding the two separately quantized component streams reconstructs the full
phrase to a maximum difference of **one PCM code**, within the predetermined
two-code bound. Of 144,000 frames, 115,107 match the sum exactly and 28,893
differ by one code. The full phrase differs from the manual-only render in
115,074 frames. This establishes that the retained musical example contains a
real pedal contribution and checks linear composition from matching shared
generator state. It is the declared linear-fixture check in
[atlas page 144](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=144),
without treating a nominal sum as an electrical loading model. The independent
catalog amplitude/phase suite remains the more detailed wiring/component
oracle.

## Rejection and relocation checks

Each negative case starts from a fresh private copy of this actual demo. Where
payload bytes change, their manifest hashes/sizes are updated so rejection
exercises semantic validation beyond a stale hash. The test checks the intended
diagnostic for every case and then verifies that the original bundle is still
byte-identical.

| Changed copy | Observed rejection |
| --- | --- |
| One left-channel PCM byte | Stereo channels differ. |
| Last PCM frame removed | Truncated or misaligned samples. |
| Header sample rate changed to 44.1 kHz | Declared rate/byte-rate/alignment mismatch. |
| First pedal ID changed from 1 to 0 | Invalid event payload at score line 10. |
| Pedal-map identity changed in metrics and stdout | Expected retained map identity. |
| Mixture matrix changed in metrics and stdout | Expected `4,2,1,1;1,4,2,1` matrix. |
| Initial pedal positions changed to `99` in parameters and argv | Positions must be two digits in 0–8. |
| Evidence scope promoted to measured instrument | Expected synthetic engineering scope. |
| Schema changed from 3 to 2 with pedal payload retained | Schema-2 parameter fields reject. |
| Clipped-frame count changed to one in metrics and stdout | Expected zero clipped frames. |

A relocated copy with spaces in its path also passed the real consumer CLI
from an unrelated working directory. No file bytes were rewritten. The
consumer explicitly reported replay `not_performed`: verifying recorded
evidence does not execute its historical argument strings. The current
renderer calls described above are separate, explicit test invocations.

## Reproduce and continue

After configuring and building the normal project, CMake's existing Python
test glob discovers this file and supplies the current target through
`HAMMOND_RENDER_EXECUTABLE`. No CMake modification is required.

```sh
ctest --test-dir build -R '^python_test_pedal_demo$' --output-on-failure
```

The directly executed focused gate was:

```sh
HAMMOND_RENDER_EXECUTABLE=/workspace/scratch/f364bc93d920/a42-build/hammond_render \
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_pedal_demo.py
python3 tools/verify_render.py examples/demos/pedal-phrase-v1/bundle
```

For another build directory or Windows configuration, supply that build's
actual `hammond_render` executable through the same environment variable, or
use the configured CTest command. Missing inputs or renderer configuration
fail this gate; they are not silently skipped.

Root should include this suite and the immutable demo in the next coherent
combined checkout gate, explicitly stage the ignored WAV/compiled-profile
evidence, and publish the accepted checkpoint. Future model changes must
preserve this historical example and introduce a new named artifact when its
source identity or intended model changes.

No subjective listening occurred. Physical pedal shaping, complex low-wheel
spectra, measured contact timing, reactor/loading response, calibrated footage,
loaded expression, scanner/AO-28/Leslie behavior, native DAW/device operation
and deadline performance remain outside this focused acceptance. The limits
follow [atlas pages 139–144](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139)
and the explicitly named provisional-model rule on
[page 447](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447).

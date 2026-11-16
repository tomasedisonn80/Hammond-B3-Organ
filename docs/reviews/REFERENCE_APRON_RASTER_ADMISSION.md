# Independent reference apron raster admission

**A23 / wave 4 / `/root/w04_a23`, 16 November 2026: admitted for the frozen
25-case paired raster scope.** Literal whole-interface 1:1 remains unqualified.
Authority: the complete [contract](../design/REFERENCE_APRON_CONTRACT.md),
[frozen inputs](../design/reference-apron-fixtures.json) and retained
[genuine-before receipt](../development/2026-11-16-preset-library-continuation/reports/apron-genuine-baseline.json).

## Independent method and result

The new [consumer](../../tools/check_reference_apron_raster.py) pins the original
fixture, manifest, contract, JPEG and actual genuine-before executable. It
validates each executable's complete `--list`, uses zero-based `--case 0..24`,
and compares complete copied model/session/info, layout and queried renderer
metadata. The frozen serializer's numeric routing booleans are explicitly
accounted for. No producer allowance or generated artwork supplies the masks.

Binary32 endpoint mapping derives R and F from contract coordinates. The R
allowance uses floor/ceil physical edges intersected with output, actual viewport
and enabled physical clip; F protection uses half-open pixel-center membership.
An enabled empty clip permits zero pixels. There is no added halo.

**25/25 pass across 61,780,011 paired pixels.** All 17 visible active cases change;
638,929 pixels differ in total. Outside-allowance changes: **0**. Protected-footer
changes: **0**. Contract cases **14–16 and 21–25** are wholly identical. Every one
of the **25 unavailable-texture frames** equals the genuine before frame in all
RGBA bytes. Canonical case 1 matches original source RGB and alpha 255 at all
**32,544 R-minus-F pixels**; its **56,016 F pixels** equal baseline. Two retained
source pixels coincidentally already matched baseline, so canonical changed count
is 32,542.

| Aggregate population | Pixels |
| --- | ---: |
| Permitted R envelopes after output/viewport/clip intersection | 1,753,028 |
| Visible pixel centers inside mapped R | 1,738,688 |
| Protected output outside permitted R | 60,026,983 |
| Protected F centers in output, including clipped-out centers | 1,851,123 |

The translated strip checks are nonvacuous. “Exterior” below means visible
centers outside R; all output outside the allowance is separately protected.

| Contract case | Allowed | R-center interior | Visible center exterior |
| --- | ---: | ---: | ---: |
| 10, left | 164 | 162 | 182 |
| 11, right | 164 | 162 | 182 |
| 12, top | 4,920 | 4,920 | 4,936 |
| 13, bottom | 4,920 | 2,460 | 7,396 |

Clipped/full-companion visible differences for cases 10–15 are respectively
**165, 170, 308, 4, 0, 0 before**, and **165, 251, 308, 4, 0, 0 candidate**.
Candidate case 11 contains **81 R-center differences** against its full companion;
the others contain zero. These are preserved sampling observations. The frozen
protocol requires containment and preserved transforms; cross-clip resampling
equality is not an admission condition.

## Exact identities

All values below are SHA-256. The final 63,003-byte report
`../a23-apron/paired-final.json` records every frame/header hash, all 25 masks,
complete source identities, executable paths, commands and zero failures. Its
hash is `5305e9d2d339c327c860d00fbb00f7ba0679c03dccc92d95f62c44fe4b65b896`.
The original `../a23-apron/paired-first.json` remains unchanged, SHA-256
`7416174d67cab482f1d1debac468b8a222ecca7d0ce07aebe45e29faf4f2f8c4`.

| Input or result | SHA-256 |
| --- | --- |
| Frozen fixture | `59cecf6ba99bf9361f506954758a500845f2298bf934ceef27ba69d995743f73` |
| Frozen manifest | `6a75548862cd7d313e07b7a21827f5acfd3d97533e02e7fccecf73611d7d832e` |
| Candidate Drawing.cpp | `666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a` |
| Candidate Drawing.h | `36663f449abfbf01c755b8ab718b2a75252709b68ed38df9452d446ea82289f3` |
| Candidate InstrumentView.cpp | `63bede9eb5fccde155d6d6ddfbbcbfa7566ab06dcf2726d92b84bc7ad0e72a77` |
| Genuine before executable | `8391cb06222f7f9eb61381f86631dce364752022dbc4faa14c22fab4ae7f35e6` |
| Candidate executable | `0a7b2d506edbf8bc47ddbda8592d59b721e60e050d487b89cb0da6a2c1117ac3` |
| Unavailable-texture executable | `2577977a4e95049a1f072c03c9210dd4113047eabe99a4176ab886154d1aa83f` |
| Canonical before/unavailable RGBA | `e91d61c60458e161d0dba087a8a681afebde4904884fd6220ee99acdb607bfe1` |
| Canonical candidate RGBA | `54d71ccf1e3dd99021eaff2be89dab7d2e6324e86edca7d432a70de4297cef74` |
| Canonical R-minus-F candidate/source RGBA | `b90cd031507fefe09e506719d10a9f12ffa59068d00edd54e396724ba12b7a2a` |
| Final consumer | `b10581af7de479fcc7f49960780e0d24cdeecc33f5a7e456eb0edfbde336e118` |

## Repeatability and consumer adversaries

From the current repository, using the retained sibling build directories:

```sh
python3 -B -S tests/test_reference_apron_raster_checker.py -v
python3 -B tests/test_reference_apron_raster_checker.py -v
python3 -B tools/check_reference_apron_raster.py --repo . \
  --report ../a23-apron/repeated-admission.json --progress
```

Explicit `--before`, `--candidate`, `--unavailable` and `--receipt` paths support
relocation. `--case` accepts zero-based diagnostic subsets and returns a partial
result unless all 25 were checked. `--keep-streams` optionally retains original
transport bytes. Existing report/stream names are refused to preserve evidence.

The first consumer run passed **14/14 adversarial methods in 0.525 seconds**.
Root's integration review then found that unconditional NumPy/Pillow imports
would break ordinary stdlib-only CTest. Dependencies are now loaded only for
offline pixel work. `--help` runs without them; paired admission explicitly
refuses with a clear dependency error. The final `-S` run passes **12 methods**
and skips only **two NumPy pixel methods**, explicitly, in **0.414 seconds**.
The final equipped run passes **14/14 in 0.637 seconds**. The fresh paired run
has identical source/binary/frame/header/mask/results to the original; no
numerical criterion changed.

Tests independently enumerate boundary pixels and reject malformed UTF-8/JSON,
duplicate members, nonfinite numbers, CRLF/oversized headers, invalid dimensions,
short/extra payloads, producer masks, wrong numbering, incomplete metadata and
stdout/stderr/time-limit violations. Header extent is at most 64 KiB, dimensions
at most 4096, payload at most 64 MiB, and each subprocess has a finite deadline.
The exact first log is `../a23-apron/consumer-tests-first.log`, SHA-256
`38ba90884b54a4038149796cc3dd015bfcadf0c50d7c8e00dd6aa537f7391d6f`.
Final logs under the same scratch directory are `consumer-tests-stdlib.log`,
SHA-256 `47b2570f5b315cd8376484d8c086f1ea4358cf543b40dea711acd1a8ec3be40c`,
and `consumer-tests-with-deps.log`, SHA-256
`710f4956da97f0b2bc791b4fa11c7799488641b5261645042d7882ccddea21d7`.
No original failed raster run was replaced; the integration finding is retained.

This is SDL 2.32.10 software-surface evidence, with Pillow 13.0.0 and NumPy 2.3.5.
Relevant sources and executable bytes stayed unchanged throughout. Independent
asset admission belongs to A22; root owns direct pre-footer alpha/state and
same-Drawing repeat gates. Genuine application visual inspection, real display,
DPI, input and accessibility retain separate acceptance. No native build,
production/fixture/asset edit, commit or publication was performed here.

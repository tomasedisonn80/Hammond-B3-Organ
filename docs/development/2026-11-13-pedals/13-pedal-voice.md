# Assignment 13: fixed nominal pedal voice

Owner: /root/w03_a13_pedal_voice

Wave 03, new pedal session. This assignment implements the adopted fixed voice
after the independently checked routing kernel; it is not a physical calibration.

## Implemented scope

Added only these five assigned files:

- `include/hammond/PedalVoice.h`
- `src/PedalVoice.cpp`
- `tests/test_pedal_voice.cpp`
- [PEDAL_VOICE.md](../../PEDAL_VOICE.md)
- This assignment note.

The stateless `render_nominal_pedal_voice` operation accepts four normalized
buses and two retained positions. Its fixed rows are `[1/2,1/4,1/8,1/8]` and
`[1/8,1/2,1/4,1/8]`; the separate gain law is `p/8`. Immutable metadata retains
`nominal-static-pedal-mixture-v1`, `linear-pedal-position-v1`, the complete
matrix/gain table, Mixture 1/2 labels and numerical bounds. No arbitrary
coefficient input can silently retain the nominal identity.

All four buses must be finite and within [-50,50], including muted calls.
Bus errors return `InvalidBuffer` before invalid positions return `InvalidEvent`.
The function validates before computing a local result and commits destination
only on success. It returns both pre-control mixtures and their combined `P`;
both positions zero give canonical positive-zero `P` while retaining mixtures.
There is no source evaluation, phase/time state, release envelope, limiter or
polyphony normalization. The explicit weight helper returns 200 owned +1 values.

The `PedalDrawbarPositions` alias and validation helper were coordinated with
assignment 14 before implementation. No existing control, Engine, event or
parameter files were edited. The [integration contract](../../PEDAL_INTEGRATION_CONTRACT.md)
remains the authority for their later connection.

## Source review and coherent test snapshot

Read current standing instructions/status/next steps and session records,
the adopted integration contract, routing API and test support. Re-read complete
atlas pages 139-144 and 447 from the retained extraction, preserving their
distinction between documentary routes, a declared linear fixture and the
missing reactor/loading/spectral measurements. Earlier six-reader review records
were not counted as new reading assignments.

The inspected published HEAD was `6a38805ea072627f383d9eb988d735dc259db472`.
Root had frozen wave 2 as tree `81b1c30436a239d8c04ffcd1ec658d356eb81acc`.
To avoid compiling against assignment 14's concurrently changing object layout,
copied that frozen source into ignored `build-a13/source`, then overlaid only
the new voice header, source and native test. The core and consumer were both
compiled from that coherent copy. Actual tested/live source hashes matched:

| File | SHA-256 |
| --- | --- |
| PedalVoice.h | `694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf` |
| PedalVoice.cpp | `88fb5afa936784be351b2940ee6f81216975112f860b007d40f3b6a3d9f7c6ba` |
| test_pedal_voice.cpp | `9b754390dd0b9ffc65b0e79529598bda513dcbd329e0c9d4528047148dfe0372` |

## Actual executed checks

Used GCC 14.2.0, CMake 3.31.6 and the existing Python 3.12.14 build dependency:

```sh
cmake -S build-a13/source -B build-a13/build -DCMAKE_BUILD_TYPE=Release
cmake --build build-a13/build --target test_pedal_voice -j 2
ctest --test-dir build-a13/build -R '^test_pedal_voice$' --output-on-failure
```

The strict-warning Release core and consumer compiled successfully. Focused
CTest: **1/1 passed, zero failures, 0.01 seconds**. The retained CTest output
reports five groups, **3,240 exact frame comparisons**, **83,268 ordinary
floating-point frame comparisons** and **1,073 rejected calls**.

The reference uses independently arranged integer-numerator equations, not the
exported matrix/gain table. Exact cases include every basis, all 16 extreme
corners, mixed dyadic frames and all 81 control pairs; they reach output 100
without limiting. Ordinary cases cover all four standard rounding modes,
adjacent in-range limits, subnormals and signed zero. The observed maximum error
was **3.27515792264421179425e-14**, below the predeclared absolute bound
**7.10542735760100185871e-13**. The caller's rounding mode remained unchanged.

Every bus position rejects nonfinite/out-of-bound values even while muted.
Every rejected uint8 position value 9-255 was exercised in both controls with
nonzero and silent inputs. Rejections preserve destination bit patterns,
including a NaN payload and negative zero. Repeated valid calls around unrelated
and rejected calls return identical results. Direct checks also verified owned
weight copies, metadata identities, UTF-8/LF, whitespace, note identity and local
documentation links.

No implementation defect was found by this focused gate. No full regression,
new enabled-path allocation instrumentation, sanitizer, hosted CI, actual Engine
audio, native host or physical-fidelity result is claimed by this assignment.
The integrator owns those subsequent gates and shared status publication. No
input data/PDF, shared status files, commits or remote branches were changed.

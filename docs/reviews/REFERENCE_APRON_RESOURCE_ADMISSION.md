# Reference apron resource and lifecycle admission

**A34 / wave 6 / `/root/w06_a34`, 16 November 2026: admitted for the scoped
source and retained software-renderer evidence below.** No resource or ownership
blocker was identified in the [frozen contract](../design/REFERENCE_APRON_CONTRACT.md).
This review adds one descriptive measurement pair, without a timing threshold.

## Ownership, preparation and failure

[Drawing.cpp](../../apps/standalone/Drawing.cpp) prepares the optional apron only
after required fonts and renderer blend initialization succeed. `make_apron`
validates positive dimensions at most 8192, pitch `width*4`, nonnull pixels and
exact byte count before creation. Those bounded integer products are safe.
It creates one static RGBA32 texture, uploads once, and sets BLEND, identity
RGB/alpha modulation and explicit Nearest. Any upload/configuration failure
destroys the local texture and returns null; creation failure returns null
directly. Optional failure leaves `initialize()` successful and clears its error.
Required initialization failures retain their existing false/error behavior.

Successful font members reject repeated initialization before any new texture
creation. Failed required initialization never reaches apron preparation.
The private, initially null apron pointer is assigned only the successful result;
the noncopyable Drawing destructor releases it. There is no frame cache or
paint-time retry of preparation. Every initialized Drawing prepares the texture,
including inactive layouts. The existing renderer-reset handler destroys Drawing
and creates a fresh one, so “once” means per initialized Drawing, not per process.
Application member order destroys Drawing before its renderer/window.

The [unavailable-texture seam](../../apps/standalone/native_tests/reference_apron_unavailable_texture.cpp)
intercepts only RGBA32 creation at 1640×54. The retained
[paired report](../development/2026-11-16-preset-library-continuation/reports/apron-paired-final.json)
proves all **25 fallback frames exactly equal genuine baseline**. Upload,
individual configuration and copy failures were not separately injected:
cleanup/false-return conclusions for those branches are source inspection.
Exact equality after arbitrary backend copy failures is not established.

## Paint boundary and finite inputs

`apron_art` checks texture availability, finite x/y/width/height and positive
extents, constructs one stack `SDL_FRect`, and returns the result of one
full-source `SDL_RenderCopyF`. It introduces no C++ dynamic storage, decoding,
upload, file access, logging or model access. The sole caller retains the original
procedural wood call and arguments whenever false is returned. Existing whole-view
text construction still allocates; this is not a whole-painter allocation-free claim.

The new method changes no renderer scale, viewport, clip/enabled flag, draw blend
or draw color; texture modulation remains private and fixed after preparation.
SDL owns clipping of the original mapping. Valid layout dimensions are bounded
to 8192 and use the unchanged endpoint transform, keeping admitted destinations
finite. Extreme finite rectangles or arbitrary backend transforms beyond that
domain are not additionally qualified.

The existing [direct probe](../../apps/standalone/native_tests/test_standalone_reference_apron_art.cpp)
and [interaction admission](REFERENCE_APRON_INTERACTION_ADMISSION.md) record
**95 checks, zero failures**: four canonical probes, five transformed/state probes,
sixteen invalid rectangles, unprepared/null rejection, and same/fresh Drawing
repeatability. They verify both opaque backdrops through every hole texel,
opaque texels, containment and incoming state. I checked matching source/binary
identities and original logs; neither direct nor 25-case suites were rerun.

## Resource quantities and one observation

The admitted asset is **354,240 compiled RGBA bytes**, 1640×54 at pitch 6560;
its repository gzip is **61,162 bytes**. Runtime reads embedded bytes and needs
no asset file or decompressor. Drawing gains one pointer and one optional texture.
354,240 bytes describes the logical pixel payload, not total backend allocation:
SDL conversion/storage, driver metadata and allocator overhead remain additional.

From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, inspected benchmark source
defines these exact commands, each executed once through
`python3 -B ../a34-resources/measure.py`:

```sh
../baseline-native/hammond_standalone_paint_benchmark 1672 941 dimensional mixed-held
../build-native/apps/standalone/hammond_standalone_paint_benchmark 1672 941 dimensional mixed-held
```

Each process uses 30 warmups and 300 samples, no heap instrumentation, SDL 2.32.10
software surface, batching enabled, scale 1, full viewport, no clip/window/audio
device, and a 6,293,408-byte ABGR8888 surface. Geometry fingerprint and all
comparison metadata agree; expected apron pixels differ. Environment: Linux
6.18.57 x86-64/glibc 2.41, Xeon Platinum 8573C, nine available logical CPUs;
GCC 14.2.0/Ninja Release, MIDI/VST3 and X11/Wayland/ALSA/Pulse/JACK disabled.

| Observed quantity | Genuine baseline | Candidate |
| --- | ---: | ---: |
| Paint + flush/present median, ms | 107.662072 | 105.997843 |
| Paint + flush/present p95, ms | 131.320750 | 134.992378 |
| External process wall, s | 36.957074 | 37.085141 |
| User / system CPU, s | 36.756681 / 0.023674 | 36.764905 / 0.087203 |
| Whole-process peak RSS, KiB | 14,296 | 14,296 |
| Executable file bytes | 3,395,520 | 3,752,032 |

Both exit zero with empty stderr. Linux `wait4` supplies exact-child accounting;
wall observation has approximately 10 ms polling granularity. Baseline ran first
in separate processes without randomized repetitions: these values establish no
speed ranking, incremental texture-memory cost, leak bound, callback/deadline,
display presentation or VRAM result. Equal RSS does not imply zero memory cost.
The initial wrapper failed before launching either benchmark because
`/usr/bin/time` was absent; original runner/empty outputs and correction remain.

## Exact identities and remaining evidence

SHA-256 identities, unchanged through measurement:

| Input | SHA-256 |
| --- | --- |
| Drawing.cpp | `666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a` |
| Drawing.h | `36663f449abfbf01c755b8ab718b2a75252709b68ed38df9452d446ea82289f3` |
| InstrumentView.cpp | `63bede9eb5fccde155d6d6ddfbbcbfa7566ab06dcf2726d92b84bc7ad0e72a77` |
| Baseline benchmark | `f80e261f8001df5099d8c824194c621dea42672db33434e4973e19e230cda492` |
| Candidate benchmark | `f5f5bd03a1b98ed9ba3b96856879488377410f7e51299a785337e0addcd5437f` |

Scratch `../a34-resources/measurement.json` retains raw samples, commands,
environment, source/output hashes and process observations; SHA-256
`b6da72a6acf84786dba48b4d18fa8bafa6ec2ce11e0f3f839fc22842bff892ef`.
Its runner is `4be7524c5f3c6fe93b3e76ad724a43d7dbb88393c0ce8c30a80be12861d14ece`.
Existing paired report remains
`5305e9d2d339c327c860d00fbb00f7ba0679c03dccc92d95f62c44fe4b65b896`.
No production/test/build changes were needed. Real display/DPI/accessibility,
physical fidelity and literal whole-interface 1:1 retain separate gates.

# Actual standalone chapel audition demonstration

Assignment **56/60**, wave **10**, actual agent
`/root/w10_a56_chapel_demo`, session `2026-11-13-next-phases`.

**Result:** two actual final-candidate application captures pass the declared
control, note-ownership, callback, image and shutdown checks. The
[retained ten-file bundle](../../examples/demos/standalone-chapel-v1/README.md)
contains the explicit control state, replay, unmodified diagnostics, lossless
images, provenance, file manifest and independent artifact verifier.

This is a Linux software-renderer/dummy-driver demonstration. It does not
establish hardware output, listening quality, acoustic fidelity, device latency,
desktop/DPI behavior or assistive-technology qualification.

## Exact source and build boundary

| Item | Observed identity |
| --- | --- |
| Published source | `0085e338388f2c7516a7d455f11692b94e9451f4` |
| Equivalent local commit | `fa6df9d04916da8e23938cc3e85f524e3707e7d8` |
| Exact common Git tree | `19c763503f67e1f054d2d27b6ec3d8fca2e36474` |
| Frozen source | `/workspace/scratch/5ba97739b54c/a55-full-integration/source` |
| Source comparison | All **894** tracked Git blobs and executable modes match before and after capture. |
| Source inventory SHA-256 | `d78606ec2567e271e37f0aa0b466f794852cb2079668ec0ce5ec0bf9c818140d` |
| App | 2,598,768 bytes; SHA-256 `def97cef70b3eafcd108170a985c61215b878c918debde6ff2fb236a2a9c3416` |
| Compiled nominal profile | 4,545 bytes; SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Compiled chapel catalog | 4,837 bytes; SHA-256 `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91` |
| Runtime | Linux 6.18.57 x86-64, glibc 2.41; SDL 2.32.10, dummy audio/video and software rendering. |
| Build | Assignment 55's fresh GCC 14.2.0 Release build, CMake 4.4.4 / GNU Make 4.4.1. |
| Image authoring | Python 3.12.14, Pillow 13.0.0. |

Assignment 55 reported its full Release build succeeded before these outputs
were used. This agent independently inspected the actual main compile command
(`-O3 -DNDEBUG -std=c++20` and strict warnings), compared all frozen source blobs
to Git, and hashed the finished executable/profile/catalog. It performed no new
build or CTest gate and does not transfer assignment 55's later results into
this review. The build/source trees were read-only; the frozen exporter was
invoked with Python `-B` to avoid creating source bytecode caches.

The coordinator independently fetched the public commit and confirmed the same
tree as the local source. Source-specific records remain authoritative if later
work changes that tree. The earlier
[window demonstration](STANDALONE_WINDOW_DEMO.md) and its files are unchanged.

## Independent musical input and state checks

The source basis is the [reviewed catalog](../CHAPEL_PRESETS_CATALOG.md),
[ordinary-control export](../CHAPEL_CONTROLS.md),
[B3CONTROLS3 contract](../CONTROL_STATE_FORMAT.md) and
[bounded replay contract](../STANDALONE_INPUT_REPLAY.md). This assignment does
not claim another independent full-PDF reading or independent verification of
the atlas's primary Table IV.

The actual exporter selected Upper catalog **C# = 005320000**, Lower catalog
**A = 427866244**, common bank **B** and expression **0.5**. Both routes are
enabled, both A banks are zero, pedals are `00`, and percussion is
Off/Second/Normal/Slow. The entire exported file exactly equals an independently
declared 292-byte literal, SHA-256
`25efc1b8af7eaee11b022059c8607822aab8209221f60c20990dad3cacd352c0`.
The complete controls in every recorded observation and final snapshot equal
an independent literal dictionary covering all fields.

The 349-byte replay, SHA-256
`b203d8b94ed0e32bd7f3b8f6871f85cd36f008cad22153d13161f6bad867b9ff`,
contains eight ordinary SDL keyboard actions over 1400 ms. It explicitly selects
Upper, presses A (MIDI 60), selects Lower, presses D (MIDI 64), then returns the
destination for future presses to Upper. There are no musical key-up actions.
Both actual observation paths are empty → Upper 60 → Upper 60 plus Lower 64;
no pedal note appears. Sequence markers are coherent, monotonic and covered by
the submitted prefix. The final pre-shutdown snapshot acknowledges sequence 3
with the two exact notes and unchanged controls.

Both processes accepted exactly two On commands and zero Off commands. Their
controls and script files remained byte-identical. The ordinary shutdown joins
the callback and clears both notes. One redundant automatic scoped-release
command per run is counted as discarded during stopped cleanup; this is separate
from the fully acknowledged scripted prefix and is within the existing contract.

## Actual process and callback evidence

Each process ran once in its own private cwd under
`/workspace/scratch/5ba97739b54c/a56-chapel-demo/`. The complete child environment
was `PATH=` plus `LANG=C.UTF-8`, `LC_ALL=C.UTF-8`, `SDL_AUDIODRIVER=dummy`,
`SDL_VIDEODRIVER=dummy`, `SDL_RENDER_DRIVER=software`. This demonstrates these
executions did not need a development-tool PATH. Original source/build paths
were present; this assignment makes no new source-removal/relocation claim.

| Capture | UTC start on 2026-11-13 | Process seconds | Callbacks / frames | Images | Maximum observed nominal peak |
| --- | --- | ---: | --- | ---: | ---: |
| Reference 1280 × 900 | 23:52:23.892896 | 1.546843 | 130 / 66,560 | 34 | 0.04554705694317818 |
| Minimum 960 × 700 | 23:52:25.625848 | 1.484244 | 129 / 66,048 | 50 | 0.04757985100150108 |

Both obtained 48,000 Hz, 512 frames, two native-float32 channels and 4,096-byte
buffers. All callback format/render/nonfinite/overrange counters, Session fault,
queue-overflow, rejected-command and recovery counters are zero. Runtime reports
actual requested window/drawable dimensions, positive painting and held capture.
Final Session frame clocks equal actual rendered frames; final running and held
flags are false. Both exit zero with empty stdout/stderr. The measured peaks and
counts describe these wall-clock executions, not a latency or speed comparison.

The original diagnostics remain unmodified:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `reference.json` | 4,667 | `69ba78a6f383b297fca22140ef184c25946362d7a299f6c21f327b4fa430bf5c` |
| `minimum.json` | 4,665 | `b0a60e51ca3af8ed93d7b28e2a8483256be587f882b06b15d7fd793fc1a03960` |

## Actual image and visual verification

Each BMP was decoded as RGBA and saved directly as PNG, with no crop, resize,
retouching or mode conversion. Reopening each PNG confirmed equality of mode,
dimensions and every decoded pixel byte against its original BMP.

| Image | PNG bytes | PNG SHA-256 |
| --- | ---: | --- |
| `reference.png` | 67,777 | `78f6c7a581f2633077765a9bf70a14d3675422340fdca614605160093adbc74e` |
| `minimum.png` | 54,084 | `1f64a62e3aae8280b78cc6ab9627f23477e3a1c6e90ae06892fc809e8f9b6e1d` |

Both images were directly inspected. The selected B banks show their literal
digits; the A banks remain independently zero in diagnostics. The expression
display reads 50%, both pedal mixtures zero, and percussion Off. Upper C4 and
Lower E4 have distinct held fills while surrounding white keys remain unheld.
No panel edges, button labels or footer elements visibly clip or overlap in
these two views. Minimum-size footage labels and status text remain compact;
real-display usability has not been qualified.

Independent literal pixel locations below the accidentals additionally verify
the two highlighted keys at each size. At reference size, Upper C4 `(522,500)`
has RGBA `(180,168,125,255)`, unlike neighboring D4/E4 `(243,237,215,255)`.
Lower E4 `(590,670)` has `(176,165,121,255)`, unlike Lower C4/D4
`(245,239,216,255)`. Minimum-size coordinates and all actual values are retained
in provenance. These points were chosen from the rendered images, without
importing production geometry or painter code.

## Reproduction, verification and next step

The bundle README contains the exact exporter options, environment and two
application invocations, plus lossless conversion and artifact verification.
`verify_demo.py` checks the complete retained manifest, independent literal
state/script, all observations and final endpoints, every pixel hash and held
key comparisons. It needs Python/Pillow only; it launches no app and makes no
device claim. Raw BMPs, invocation records, stdout/stderr, the capture checker
and all source hashes remain in the private `a56-chapel-demo` directory.

The retained verifier was executed successfully on 14 November 2026 UTC:
**10 files, 165,762 bytes**, both capture records and all declared checks passed.
Its first execution exited zero. The manifest SHA-256 is
`deca520a43d6aaf57e5ca3c5878c3e74bb67db6eb9ddb15298a547ca90f65293`.
Final read-only checks confirmed the executable, compiled profile and catalog
hashes still match the pre-capture values. Python syntax, text whitespace and
local Markdown targets passed; the earlier window-v1 files match the captured
public source unchanged.

No exporter or native capture failed, no process was retried, and no production
source, test, CMake or existing demonstration file changed. Root owns the shared
status/ledger, combined-source qualification and commit/push.

The next visual gate is actual desktop scaling, pointer capture, display
readability and assistive-technology operation, with explicit platform identity.
The next musical product gates require real devices/controllers and independently
admitted physical evidence. The documentary tap mapping, nominal dry profile and
wall-clock replay remain explicitly bounded software demonstrations.

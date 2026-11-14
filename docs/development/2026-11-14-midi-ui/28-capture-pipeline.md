# A28 — Bounded native capture pipeline and initial retained gallery

Actual worker: `/root/w05_a28_capture_pipeline`, assignment 28, logical wave 5
of the MIDI/UI session. Owned only the new capture utility,
`examples/demos/standalone-midi-ui-v1/` and this note. No root README, shared
status, CMake, application source, old gallery, commit or subagent was changed
or created by this worker.

## Result

Implemented [capture_standalone_reference.py](../../../tools/capture_standalone_reference.py)
and retained [four actual native captures](../../../examples/demos/standalone-midi-ui-v1/README.md):
1672 × 941, 1280 × 900 and 960 × 700 player views with UI-owned Upper C4 and
Lower E4 held, plus the minimum-size MIDI modal with paired explicit synthetic
MIDI/UI scripts. All four native processes passed. All decoded BMP/PNG pixels
matched, all recorded binary/source/build/dependency identities remained equal,
and all four images plus the exact atlas reference were visually inspected.

This is deliberately **initial pre-A29 evidence**. The narrow-glyph dropout
reported by A21 remains visible in the modal instructions, headings and footer.
The complete legibility and pixel-identical appearance goals are not met.
The actual display says synthetic replay and does not claim a native MIDI
connection. SDL audio/video are explicitly dummy and the renderer is software;
there is no physical hardware, desktop-photo or acoustic-fidelity pass.

## Utility and ownership boundary

The utility requires an explicit executable, matching source/build roots, a
fresh output directory and `--dummy-sdl` acknowledgment. Even an empty existing
output directory is rejected. Each app process has a configurable finite guard
of 4–60 seconds, default 12. Every input/script/state/output path is separate and
newly owned by the capture directory. Explicit B3CONTROLS3 state avoids default
preferences and is compared unchanged afterward. The tool does not build the
app, write app source, download anything or choose a hardware port.

The three 1400 ms players replay eight events each through B3UIREPLAY1. The
modal also runs for 1400 ms, with 14 UI events and an explicit three-record MIDI
script. Its two MIDI-owned notes survive the modal's UI focus release. Ctrl+M
opens the real modal, five Tabs focus Apply, and Return invokes it. Synthetic
mode's actual main-loop branch bypasses native enumeration, including Apply.

Success requires actual diagnostics schema 2, zero application/audio/Session
faults, positive callback and paint progress, exact obtained dimensions and
48 kHz / 512-frame float32 stereo configuration, correct complete controls,
exact delivery/note counts, final sequence acknowledgment, held `[[60],[64]]`,
empty pedals and clear joined shutdown. Native MIDI generation, names and device
callback counters must stay zero. The synthetic source, 512-event and 32-packet
budgets, capacities, delivery/lifecycle disposition and timing qualification
are explicitly checked. The utility records observations, not inferred success
from exit zero or a screenshot alone.

Pillow 13.0.0 is an authoring dependency only. The original BMP is encoded
directly to PNG; mode, size, every decoded byte and decoded RGB bytes must match.
The unchanged original BMP bytes are retained as deterministic gzip archives,
and input/process/diagnostic/image/pixel hashes accompany the exact commands.
The generated capture manifest excludes itself and later authored review
material; the final bundle manifest also covers that review and this edition's
source overlay. Neither manifest is an authenticity signature.

## Freeze and exact identity

Root kept the current binary/source stable until A28 copied them into
`/workspace/scratch/cd4bd06ce68f/a28-initial-freeze/`. Original/copy/original-after
hash comparisons passed for the 3,583,376-byte native executable, 191 selected
source files and 602 initially copied build/configuration/generated files. Root
then released live Drawing source to A29. The four captures execute only the
private frozen executable; they never qualify later concurrent source edits.

Base local HEAD was `e09107414896c2c53dad124a74f60c8043fadfe4`, tree
`1f117a17cf561fae8978adeb612abf9ad29d7b64`. The captured code includes the
uncommitted A23/A24 replay implementation and other selected fixture/build
changes. The base commit alone is not the captured source. The parent supplied
prepared repository-equivalent `e918b332ccc64d0307e60f53bf7c7f53ffd141e9`; this
worker read the checkpoint record but did not fetch or attest its publication.
The local object lookup for that prepared remote identity was unavailable.

| Actual capture input | SHA-256 |
| --- | --- |
| Frozen native executable | `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d` |
| Frozen `main.cpp` | `22719975ed910b0b23db841617446e492890d89f2106cc04279fc9e46824f42e` |
| Initial `Drawing.cpp` | `4d13a5eb312799b341e44a41f52960e44c04da1a7b05ecfdda86bc635e1ecda9` |
| `InstrumentView.cpp` | `82c7171626f16039ac4877a8cafc12928941d51fb295a37d0f23ac6c294c6e8e` |
| `UiModel.cpp` | `ac1a381367cfee7cce61e27ebd0b094c76a730806383e9ead609622687993e28` |
| Capture utility used | `baeb1444e8ca35c6853fcacb5ca061213a8f78c10928ee9df83231cdda7426aa` |

The utility independently hashed all 191 selected source files, 157 relevant
build/configuration/archive/generated files and 1,881 dependency/compiler/library
paths before and after the actual capture. SDL 2.32.10 is commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`; RtMidi 6.0.0 is
`1e5b49925aa60065db52de44c366d446a902547b`. The prepared RtMidi source and patch,
embedded profile/reference-art headers, dependency locks, assets and original
concept JPEG have their own hashes. The build is GNU C++ 14.2.0 / CMake 4.4.4,
Release, `HAMMOND_ENABLE_MIDI=ON`, using the prepared ALSA 1.2.14 dependency.
The existing local `SDL_ALSA=OFF` workaround remains explicit.

The frozen files were also compared to the base git objects. An exact 17-file,
111,561-byte compressed source overlay preserves all selected changed/new
source bytes, including MidiReplay.cpp/.h; each member was decoded and rehashed.
It allows later recovery against the named base without inventing source code.
The complete selected-source inventory still governs equality. System libraries
and toolchain are not a hermetic or signed build attestation.

## Executed command and observations

Working directory: `/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.

```sh
python3 -B tools/capture_standalone_reference.py \
  --exe /workspace/scratch/cd4bd06ce68f/a28-initial-freeze/hammond_standalone \
  --source-root /workspace/scratch/cd4bd06ce68f/a28-initial-freeze/source \
  --build-root /workspace/scratch/cd4bd06ce68f/a28-initial-freeze/build \
  --output /workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ/examples/demos/standalone-midi-ui-v1 \
  --dummy-sdl --timeout-seconds 12 \
  --expected-exe-sha256 e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d \
  --source-context /workspace/scratch/cd4bd06ce68f/a28-initial-freeze/freeze-receipt.json
```

Successful capture interval: **2026-11-14 04:49:34–04:49:42 UTC**. Every app
returned zero with empty stdout/stderr; no app invocation was retried.

| View | Callbacks / audio frames | UI / MIDI records | Final sequence | Painted images |
| --- | --- | --- | ---: | ---: |
| 1672 × 941 | 140 / 71,680 | 8 / none | 3 | 23 |
| 1280 × 900 | 135 / 69,120 | 8 / none | 3 | 29 |
| 960 × 700 | 132 / 67,584 | 8 / none | 3 | 43 |
| Minimum synthetic modal | 133 / 68,096 | 14 / 3 | 4 | 35 |

All four report exactly two On / zero Off commands before joined shutdown;
both holds are then cleared. The modal accepts two of two packets, starts one
synthetic epoch and records no drop, rejection, backend/overflow fault or
native device callback. Observed producer/drain maxima are 2/2; their declared
bounds are 512/32. This is not a stress test of either bound.

Independent post-capture decoding compared every PNG with its archived original
BMP and every original capture-manifest entry. Literal key-interior samples
also prove held-vs-unheld paint in each unobscured player: reference held RGB
`225,201,140` versus idle `246,231,201`; default held `226,201,140` versus the
same idle; minimum held `214,182,124` versus idle `248,233,203`. Each comparison
uses equal-height neighboring naturals below accidentals, with explicit pixel
coordinates retained in `pixel-checks.json`, without importing app geometry.

## Failure retained, inspections and handoff

One earlier capture-tool attempt failed **before launching any app process**:
SDL tracks `android-project-ant/src` as a symlink to a directory. Opening every
tracked path as a regular file raised `IsADirectoryError`. The failed output
was moved intact to `a28-failed-dependency-symlink/` and its provenance retained
inside the gallery. The concrete correction hashes symlink target bytes.
The subsequent complete four-process capture passed. Three separate CLI
admission checks reject an existing output, missing dummy acknowledgment and
NaN timeout, preserving sentinel bytes and creating no output/run directory.

Opened the original reference and all four retained PNGs using the image
viewer. The major composition and exact held keys are visible; default/minimum
layouts intentionally omit the cabinet, and the minimum uses compact bank rows.
No major panel clipping/control collision was observed in these states. The
modal fits, shows explicit synthetic identity, channels 1/2/3 and Apply focus.
Initial small text drops narrow strokes as A21 reported; the generic Apply help,
repeated synthetic prefix, flattened keys and stretched left wood crop remain.
The gallery explicitly preserves those residuals instead of calling them a
legibility or one-to-one fidelity pass.

The tool parsed successfully with Python's AST, its help executed, capture
manifests/source overlay/full pixels were independently verified, local links
were checked, and owned files passed whitespace checks. All tracked files in
the older `examples/demos/` editions remain byte-identical to HEAD. The final
check verified 31 original capture-manifest files, 40 final bundle entries,
all 191 reconstructed selected source files, 40 historical demo files, 30 local
links, four full decoded image comparisons and three owned-text whitespace
checks. No large
test suite was rerun for this isolated authoring tool. A29 owns typography;
A39 can rerun the same utility on a new frozen executable/source into a fresh
edition. The integrator owns acceptance, current screenshot presentation and
publication. Physical MIDI/audio, high-DPI, live resize, native accessibility,
latency/deadlines and acoustic-fidelity gates remain separate.

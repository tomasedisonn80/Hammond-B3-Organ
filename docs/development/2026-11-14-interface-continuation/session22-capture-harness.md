# A22 — Native interface capture harness and provisional gallery

Actual assignment: `/root/w04_a22_capture_harness`, wave 4, worker 22 of this
interface continuation. Owned only the new
[`tools/capture_standalone_interface.py`](../../../tools/capture_standalone_interface.py),
[`standalone-interface-preview-v1`](../../../examples/demos/standalone-interface-preview-v1/README.md)
gallery and this note. Root owns CMake, shared status/README, integration and
publication. No production source, existing gallery, parameter or state format
was modified by this worker.

## Result

The first actual matrix completed **8/8 passed**, 2026-11-14 11:12:42–11:13:02
UTC. Each native process exited 0, delivered and acknowledged its replay,
painted the requested view and dimensions, captured held notes, and cleared
owners on joined shutdown. There were no reported application, audio render,
format, overrange, nonfinite, recovery, queue-overflow or rejected-command
failures. The eight native processes took approximately 1.86–2.07 seconds each.

| Actual native PNG | Dimensions | Replay events | PNG bytes |
| --- | --- | --- | ---: |
| `play-reference-1672x941.png` | 1672 × 941 | 66 | 643,326 |
| `play-default-1280x900.png` | 1280 × 900 | 66 | 172,136 |
| `play-minimum-960x700.png` | 960 × 700 | 66 | 131,056 |
| `service-reference-1672x941.png` | 1672 × 941 | 66 | 410,332 |
| `service-minimum-960x700.png` | 960 × 700 | 66 | 166,394 |
| `rotary-reference-1672x941.png` | 1672 × 941 | 66 | 783,139 |
| `rotary-minimum-960x700.png` | 960 × 700 | 66 | 320,060 |
| `flat-minimum-960x700.png` | 960 × 700 | 68 | 49,272 |

The capture payload plus provenance/manifest occupied **2,847,503 bytes** before
the small README review; the complete gallery is below 2.86 MB. Each original
BMP was hashed, converted losslessly to PNG, reopened, compared byte-for-byte
in its decoded mode, and only then removed. No redundant BMP archives, extreme
bitmaps or generated concept imagery were added.

## Exact source and qualification boundary

The root coordinated a production-source/executable freeze during capture.
HEAD and committed tree remained `5d81199a9822874b55f3b0a124715cbd6eadf0e5` and
`52b4ec72b77e4442efe2e9e1b089b7b0ea6e638b`. The native UI was an unpublished
production overlay: HEAD alone does not identify it. The harness required the
current [A20 build report](reports/a20-material-refinement.json), verified every
reported source digest and its binary digest, and copied that report unchanged
into the gallery. The A17/root-first-ui report was not promoted to the newer
renderer's qualification.

| Identity | SHA-256 |
| --- | --- |
| Executable, before and after | `005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364` |
| A20 author report | `5b2e9b4d7ea16ec4254d6978a25180fdafd2771685eaea307feb81b3b790df87` |
| Renderer `InstrumentView.cpp` | `5f5f209dbe33cb92e3c1d237258ba123d0a86e78c694d50c0634db8549d54407` |
| Capture harness, before and after | `17aafb70e87a2fd557317e04802e62a4d935d2f2b93bf65a2df0d688c5a16545` |
| Observed production inventory | `6eb61ab582aaa01b92f84ded0b49db6896b22eebb4b67bdabc49134acaf6a7bf` |
| Observed generated/library inventory | `a55aa515407a2f9bd631d8183b3c10ffb93c92d48360843ee9fbecf19d7be94a` |
| Gallery provenance | `10219e3a5ab9f3d9c47ea4022fbd4dcb614d8d55866274653631f364c869e745` |
| Gallery manifest | `ca8e0c99a8b5cb5a0aa33c3894a676eea46de1f39645a227932d2ed4dd286375` |

The manifest records 98 production source/resource identities and 13 generated
headers, compiled-profile or selected static-library identities; all remained
unchanged. This inventory extends the ten source identities covered by the A20
author report as **observed files**, not an independent rebuild attestation.
Concurrent test additions, CMake test/install edits and unrelated documentation
are excluded. Selected build configuration values are recorded and compared.
No hermetic dependency, compiler or signed source-to-binary claim is made.

The recorded Release build has native standalone and RtMidi enabled, with pinned
SDL/RtMidi paths and the existing local `SDL_ALSA=OFF` workaround. The actual
runtime reported SDL 2.32.10, software drawing, dummy audio/video, 48 kHz stereo
float and 512-frame buffers. No physical MIDI input was opened or enumerated.
Python 3.12.14 and Pillow 13.0.0 performed capture authoring; Pillow is a lazy,
optional authoring dependency and is not introduced into the application.

## Replay and assertion coverage

The harness writes bounded `B3UIREPLAY1` plans and a shared `B3CONTROLS4` input.
Each run holds Upper notes 60/64, Lower note 67 and pedal ID 3, then edits Upper
B's 16-foot retained drawbar from 7 to 8 through the real Tab/Up keyboard path.
The Upper fixed C# route remains selected, Lower uses adjustable A, all four
retained banks remain distinct, expression is 0.75, and the stored percussion
choice is On but Upper B is ineligible. The initial control file never changes.

F4/F5/F6 or F7 select the final view while those original owners remain held.
The fixed duration is 1,800 ms, with a default 12-second subprocess limit.
Validation checks the complete initial-held and final desired/applied control
states, final note arrays, command acknowledgments, native render/audio progress,
error counters, no MIDI-device use and final shutdown cleanup.

The screenshot's own `presentation.screenshot` record must identify the actual
workspace, presentation, overlay and dimensions. It must be the final painted
replay frame, equal to `last_painted` and `before_shutdown`, with current copied
inspection state and no pending controls. Startup arguments or later shutdown
state cannot substitute for this assertion. Both logical/drawable dimensions
and decoded BMP/PNG dimensions are checked. Executable and production file hashes
are checked before each case; source, executable, generated/library/configuration,
inputs, harness and author-report identities are checked after the full matrix.
A difference marks the entire gallery failed.

## Executed verification

From `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`:

```sh
python3 -B tools/capture_standalone_interface.py \
  --exe /workspace/scratch/601951e27dc3/build-native/apps/standalone/hammond_standalone \
  --source-root . --build-root /workspace/scratch/601951e27dc3/build-native \
  --source-qualification docs/development/2026-11-14-interface-continuation/reports/a20-material-refinement.json \
  --expected-exe-sha256 005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364 \
  --dummy-sdl --output examples/demos/standalone-interface-preview-v1
```

The exact command/environment per process is in the gallery provenance. After
capture, a separate reader recomputed all 39 manifest file sizes/hashes and
all eight decoded PNG hashes/dimensions successfully. The real outputs, rather
than implementation-mirroring unit tests, are this assignment's primary gate.

Three additional admission probes returned exit 2 before writing output:

- Reusing the existing gallery: `output already exists; refusing to overwrite any gallery`.
- Supplying the old root-first-ui report: `qualification needs binary_sha256`.
- Supplying a disposable A20-shaped report with the earlier A17 renderer digest:
  `qualification source digest differs: apps/standalone/InstrumentView.cpp`.

The existing gallery's manifest digest stayed unchanged after those probes.
No production source was deliberately mutated to test drift, and no rebuild or
full acceptance suite was claimed by A22. Initial captured runs had no failures.

## Actual visual inspection

Inspected an eight-view contact sheet and the full-size Play reference,
minimum Play, minimum Service, minimum Rotary and minimum Flat PNGs. Also
inspected the unchanged 1672 × 941 atlas cover/page-409 source image.

- Play retains the full manuals, preset octaves and pedals. Upper 60/64, Lower
  67 and pedal 3 have live held highlighting; the changed Upper B cap reads 8
  and its focus outline is visible. The minimum layout moves bank controls
  into the racks and removes the cabinet without hiding the playing inventory.
- The dimensional keys show sloping sides and bounded front faces. Flat has
  rectangular keys and plain caps/panels while retaining the same musical
  state and focused drawbar.
- Minimum Service displays all six cards and 28 rows without observed card/header
  overlap. The four-bank memory row wraps inside its card. 2/1/1 held targets,
  the fixed/sounding versus edited-bank distinction, unavailable V/rpm values,
  unacquired m geometry and explicit nominal/unconnected model limitations are
  visible. This is a visual observation, not native accessibility qualification.
- Minimum Rotary shows the decorative cabinet, six honest read-only rows and
  explicit cabinet-audio disconnection. No rotor speed is represented as a
  measured or active value.

Literal 1:1 equality is **not established**. Panel composition, material detail,
lighting, row heights and cabinet placement still differ from the reference;
the application also preserves correct full musical inventory and live controls
that differ from the concept. The small reversed-preset labels still merit
continued readability review. No fake waveform, physical capture, image-generated
app mockup or unqualified physical/software claim was introduced.

## Handoff

Root can link the standard `images/` names from the current README after its own
review. A46 should build/qualify the final coherent source, supply a matching
current source/binary report, and use a **new** gallery directory. Preserve this
provisional evidence and the old preset/MIDI galleries. The later report must
retain source-overlay versus published-commit distinctions and invalidate any
affected screenshot claims after renderer changes. Physical devices, native
display/DPI, deadlines, screen-reader access, specimen fidelity and connected
scanner/AO-28/Leslie models remain separate gates under the complete M0–M9 plan.

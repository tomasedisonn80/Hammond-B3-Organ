# Assignment 20 — pedal commands and renderer metadata

Owner: /root/w04_a20_pedal_renderer

Wave: 4. Assignment: 20 of this session's 60 new assignments.

## Scope and source basis

Extended the existing offline renderer to play the accepted nominal pedal core.
Owned files are `tools/render.cpp`, `tests/test_pedal_render_cli.py`,
`docs/RENDER_FORMAT.md` and this note. The actual existing renderer contract is
`RENDER_FORMAT.md`; no unrelated `OFFLINE_RENDERER.md` was created. Root retains
shared status, manifest, CMake, regression migration and publication ownership.

Read the standing instructions, project plan/current handoff, wave-3 pedal/state
contracts and source. Read all six atlas pages 139–144 directly through bounded
`pdftotext -layout`, along with the current full-range console review. These pages
require shared sources, retained branch identity, independent pedal state and an
explicit distinction between a linear reference and measured electrical shaping.
The adopted matrix and gain law remain original, unmeasured engineering fixtures.

Root clarified that this task need not invent saved-control CLI flags. The
renderer previously had none; it still has none. The separate B3CONTROLS3 API and
its v1/v2 migrations remain unchanged and documented by assignment 14. No control
serialization, second output file or live Engine state access was added here.

## Implemented behavior

- Added `--pedal-drawbars NN`, exactly two digits 0–8, default `00`, ordered
  Pedal Mixture 1 then Mixture 2. Initial zero-frame controls now contain the
  previous nine upper drawbars and four percussion settings, followed by the
  two pedal positions. Score events at frame zero then override these controls.
- Added five-field score verbs `pedal_on`, `pedal_off`, `pedal_drawbar` and
  `pedal_all_notes_off`. They require canonical `lower`, checked pedal IDs 1–25
  or mixture indices 0–1, and the already adopted Engine payload rules. No
  third manual, MIDI octave inference or note-ownership protocol is introduced.
- Retained complete-score validation before output creation, stable tied-event
  order, exact dense-block subdivision and all previous byte/count limits.
  The initial 15 controls consume no score-frame event capacity or source time.
- Retained the existing PCM conversion, actual float metrics, clipping policy,
  no-overwrite hard-link publication, temporary cleanup and stdout-failure rules.
  There is no new gain, normalization, limiter, envelope or source evaluation.
- Advanced every current render summary to schema 3 with all previous fields
  preserved and thirteen mandatory pedal identity/transfer fields. The compiled
  routing identity supplies its model/map IDs and raw/canonical/reference hashes.
  The voice/gain identifiers come from their production constants. Matrix
  numerators are formatted from the actual compiled coefficients multiplied by
  the frozen denominator eight, producing `4,2,1,1;1,4,2,1`.

The additional contact policy is named `ideal-eight-contact-pedal-v1`; it remains
independent of manual `--contacts nominal`. Explicit +1 branch weights, including
the disconnected positions, are named `all-200-unit-positive-v1`. These describe
the accepted Engine policies, not measured contacts or electrical conductance.

The exact flag, verb and metadata contract was agreed with root and assignment
21 before their producer/verifier extension. That extension owns strict current
schema-3 evidence and separate historical schema-1/2 admission. Root assigned
the migration of existing current-output tests and legacy PCM comparisons to
assignment 23; those files were not edited here.

## Coherent verification and observed result

The test source was copied from root's complete wave-3 archive, staged tree
`24f80c3e8405fa0a49500a080967279e615a9b97`, into
`/workspace/scratch/f364bc93d920/a20-source`. Only this assignment's renderer and
new Python suite were overlaid. The build did not consume concurrent ownership,
evidence-tool or shared-header changes from the live tree.

Executed commands:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a20-source \
  -B /workspace/scratch/f364bc93d920/build-a20-renderer \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build \
  /workspace/scratch/f364bc93d920/build-a20-renderer \
  --target hammond_render -j 2
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a20-renderer \
  --output-on-failure -R '^python_test_pedal_render_cli$'
git diff --check -- tools/render.cpp docs/RENDER_FORMAT.md tests/test_pedal_render_cli.py
```

Toolchain: GCC 14.2.0, CMake 3.31.6, Python 3.12.14, Release, project warning
flags treated as errors. Configure and build succeeded without a repair or
retry. **1/1 selected CTest suite passed, zero failures, 1.83 seconds.** It ran
**17 Python methods and 358 actual CLI invocations**, with zero skipped cases.
The Python methods themselves took 1.699 seconds. `LastTest.log` records the
matching isolated source and executable. The scoped whitespace check passed.

The executed checks include:

| Coverage | Observed acceptance |
| --- | --- |
| All 25 pedal IDs at all three supported rates | Each becomes audible, then releases exactly at the requested sample; valid stereo PCM16 and unclipped metrics |
| All 81 initial position pairs | Byte-identical WAVs and metrics to equivalent frame-zero scored controls |
| Initial controls and tied events | Score-zero overrides flags; On/Off versus Off/On retains file order |
| Muted or unplayed pedals | Existing manual WAV bytes and metrics preserved; later unmute matches the corresponding continuously running source samples |
| Positive velocity and repeats | Velocities 1/64/127, duplicate presses and zero-velocity release follow the physical-target contract |
| Division independence | Manual Cancel/reselection/panic leaves pedals unchanged; pedal panic preserves manuals and releases all 25 pedals at the exact frame |
| Contact mode | Pedal WAV bytes unchanged between ideal and nominal manual contact modes |
| Dense scheduling | 1,024 same-frame events and 3,425 total events produce identical PCM and non-block metadata at block sizes 1, 17, 64, 127, 512 and 65,536 |
| Rejection | Malformed flags and 34 invalid command forms at early and late frames create no output/temporary files; overflow, unsorted events and zero-length render also reject |
| Clipping/publication | Dense manual-plus-pedal audio reports actual clipping; `--fail-on-clip` returns 2 with matching metrics and no WAV; existing destinations and input collisions remain untouched |
| Provenance | Schema-3 identifiers, exact numerator/denominator types and compiled raw/canonical/reference hashes agree with independently hashed retained inputs |

Source freeze identities:

| File | SHA-256 |
| --- | --- |
| `tools/render.cpp` | `b8c9f631575ffdd6e198f4811e8add1b301534ca709654aaad1078ec235d08b7` |
| `tests/test_pedal_render_cli.py` | `57bce625a3554b4ec0030b7caa135dfc585c9520f9a3ee7a058d8c2a5a045c1f` |

## Remaining gates and next step

The CLI always renders positive connected output; the initial no-time control
flush is observed through equivalent scored output, while disconnected-output
and zero-frame Engine acceptance belong to the existing core integration gates.
This suite is neither an independent full numerical pedal transfer oracle nor
an allocation/deadline audit. The independently frozen CSV/numerical Engine
tests retain their separate evidence; assignment 23 owns legacy executable
comparison and additional actual-output integration.

Next: integrate assignment 21's evidence schema, assignment 23's current-output
regressions and the completed ownership work from one frozen wave-4 source tree.
Run the combined build/CTest gate and publish only after root records the actual
result. No commits, pushes, shared status changes, SDK/host tests or hardware
measurements were performed by this worker. Measured pedal color, electrical
loading, physical contacts, full M3 and native host/device operation remain
separate gates.

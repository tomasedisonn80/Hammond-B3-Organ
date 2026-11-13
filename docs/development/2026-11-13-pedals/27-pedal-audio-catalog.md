# 27 — Nominal pedal musical fixtures and independent PCM acceptance

Owner: /root/w05_a27_pedal_audio_catalog

Assignment **27/60**, wave **5**. Scope: four original pedal event fixtures,
a bound catalog, independent checks of actual serialized audio, and a usable
three-second score for the later retained demo. The integrator approved the
filenames, schema and fitted-phase/coefficient approach before the first run.

## Files and source basis

- `examples/fixtures/pedals/pedal-catalog-v1.json`
- `examples/fixtures/pedals/pedal-mixtures-v1.events`
- `examples/fixtures/pedals/pedal-shared-source-v1.events`
- `examples/fixtures/pedals/pedal-held-routing-v1.events`
- `examples/fixtures/pedals/pedal-phrase-v1.events`
- `tests/test_pedal_catalog.py`
- `docs/PEDAL_AUDIO_ACCEPTANCE.md`
- This note.

Read the standing instructions, current entry points and plan, prior catalog
contracts, pedal integration/evidence contracts, both pedal/manual CSV readings
and the relevant profile/registry records. Reread atlas pages 139, 140, 142,
144 and 447. The complete fresh atlas review remains wave 1's separate scope;
this assignment does not claim another complete 500-page reading.

The new scores use explicit PedalId 1–25, ideal manual contacts, percussion off,
declared expression and fixed nominal gain/matrix identities. Catalog schema 1
is distinct from renderer/evidence schema 3. Source/profile/map/CSV/control
records and score bytes are bound by identity and hashes. Physical pedal MIDI
octave, reactor/loading values and acoustic timbre remain unknown.

## Implementation and independent expectations

The four scores expose both mixtures, duplicate source paths within pedal 1,
manual/pedal and pedal/pedal ToneId 13 collisions, independent panics, held muted
pedals, lower Cancel/reselection and pedal 8's disconnected position. The final
score is an original three-second C–F–G–C gesture under the nominal software
pitch model, ready for a later actual demo render. No WAV was retained here.

Expected component amplitudes use both literal CSV readings, integer contact
numerators `[4,2,1,1]` / `[1,4,2,1]`, exact rational division by 64 for positions,
and the bound profile's source/manual gains. The test imports no production
routing compiler, generated route header, matrix function, evidence producer
or source PRNG. Initial phases are fitted from actual PCM using sine/cosine at
absolute frame positions. Normalized coefficient pairs are compared whenever a
shared source returns. Every sample in each fit window is checked for residual,
even though the small least-squares construction uses a bounded stride of four.

Eight exact full-WAV comparisons cover the four scores at blocks 1/127/1024.
An additional initially audible version of the held-routing score must have
nonzero initial audio and the same 52,800-sample suffix after unmute. Twelve
catalog mutations and six malformed score payloads reject. Deduplicating a
repeated pedal source and altering the mixture matrix each independently fail
the numerical oracle; these are oracle-sensitivity cases, not production edits.

## Coherent build and actual commands

Started with root's immutable wave-4 source tree
`f84cacb4e6eb01189ca29136fc838885fdd858f4` at
`/workspace/scratch/f364bc93d920/checkpoint-w04/source`.
Copied it to `/workspace/scratch/f364bc93d920/a27-source`, then copied only the
new pedal fixture directory and the new Python test from the worktree. Concurrent
trace/metadata/CMake and later native-foundation work was excluded.

Actual configure/build/test commands, run sequentially and logged outside the
repository:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a27-source \
  -B /workspace/scratch/f364bc93d920/build-a27 -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a27 --target hammond_render -j 4
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a27 \
  -R '^python_test_pedal_catalog$' --output-on-failure \
  --output-junit /workspace/scratch/f364bc93d920/a27-ctest.xml
```

Observed toolchain: GCC 14.2.0, CMake 3.31.6, Python 3.12.14. Strict native
compilation succeeded. The first and only execution passed **1/1 selected
CTest suite, five Python methods, zero failures and zero skips, 3.24 seconds**
(Python method runner: 3.110 seconds). No test, production or tolerance repair
was required after execution.

| Executed observation | Result |
| --- | ---: |
| Actual renderer calls | 13 |
| Rendered mono frames | 979,200 |
| Stationary fit windows | 19 |
| Full-window residual samples | 184,800 |
| Independent component amplitudes | 155 |
| Shared normalized phase-vector comparisons | 103 |
| Maximum component peak error / fixed bound | `1.4432453011507633e-6` / `4e-5` |
| Maximum phase-vector component error / fixed bound | `0.0008450474547653242` / `0.006` |
| Maximum residual / fixed bound, PCM16 LSB | `0.5954989038965657` / `2.0` |

All dry channels matched, all declared silence/audibility intervals passed,
each explicit peak bound passed and every native render reported zero clipping.
The test's actual result output is retained in the scoped CTest log and JUnit
file; these are temporary local diagnostics, not a hosted-platform result.

## Frozen identities

| File/artifact | SHA-256 |
| --- | --- |
| `tests/test_pedal_catalog.py` | `31728c18c6d42d29895b2b073db9485fe54ecdb402523c70c9459c62cd261ab4` |
| `pedal-catalog-v1.json` | `f064cdda432791703f1853d9cde52faa3cd5bf9899b999ad5b38ee64bb1ed5b7` |
| `pedal-mixtures-v1.events` | `0adc929a3cde2f834f6d368dbd49e5441b636c2a933880144a8988033b45ba4d` |
| `pedal-shared-source-v1.events` | `b0390f58fed9f91509089d8782a4d22ea5374070a2689fdeab5641a4d582cfb2` |
| `pedal-held-routing-v1.events` | `71acf2756109509c81fa5e48d0ee7ef4d321f53e29d233ad2c60c3451f2ccdfa` |
| `pedal-phrase-v1.events` | `47daa264ca9524c98d7a189d28728778c9057852b8fd3d68e7fea9d2e63b9be5` |
| Coherent `hammond_render` executable | `42e4373f6ea80eb0c87238b009283b729e89d71858fc73085831069e84f79d59` |
| Compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

All six live code/data files match their tested copies byte for byte. Separately
compared the original eight `.events` files and both catalogs with
`git show b4fc61ccfcc59724f14fb0cee947ed7bb7142075:<path>`: **all ten original
inputs are byte-identical**. No existing fixture, production code, CMake,
shared status, commit or remote reference was changed by this assignment.

The acceptance document includes portable check/render/evidence commands and
explicit same-build/48-kHz scope. Owned-file UTF-8/LF/whitespace and local-link
checks complete the handoff; no further optional audio test expansion is needed.

## Next step and limits

Root should include these frozen inputs and the suite in the coherent wave-5
gate and observed hosted qualification. The later demo worker should render
`pedal-phrase-v1.events` with the documented exact settings, retain a new
schema-3 evidence bundle, independently replay/verify it and document its actual
audio hashes and metrics before publishing audio. A proposed command is not a
retained artifact or a completed demo gate.

Physical calibration, complete M3, scanner/AO-28/Leslie, native host/device use,
callback deadlines and cross-toolchain bitwise audio identity remain separate.
The new scores and fitted phases do not establish a measured instrument match.

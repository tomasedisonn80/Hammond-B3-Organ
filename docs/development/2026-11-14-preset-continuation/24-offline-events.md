# A24 — offline selector events and retained evidence

Assignment: `/root/w04_a24_offline_selector_events`, logical wave 4, 2026-11-14.
The integrator assigned the offline renderer, producer/consumer score admission,
focused renderer tests, one new selector score and offline documentation. This
worker spawned no children and made no commit or push. The integrator owns the
shared status, ledger and publication records.

## Implemented scope

`tools/render.cpp`, `tools/render_fixture.py` and `tools/verify_render.py` now
admit `select_preset`: either manual, unsigned index zero, finite parsed integral
value 0–11. Negative zero is admitted Cancel. The C++ adapter emits the already
accepted `EventType::SelectPreset`; no catalog parser or second selection model
was added. Existing full-score preflight and stable equal-frame order remain the
admission and scheduling boundaries. The renderer's help explains the fixed keys,
retained banks and old-bank exit from fixed mode.

The current producer and renderer remain schema 3. The independent consumer
admits the new type only under schema 3 and explicitly retains schema-1/2 rejection.
No metric field, parameter field, argv position, report/container version or
historical bundle was changed. Existing executable, tool, input and score hashes
remain authoritative. The new documentation and score comments pin the fixed
catalog's source identity without adding retroactive claims to archived evidence.

Owned changes:

- `tools/render.cpp`, `tools/render_fixture.py`, `tools/verify_render.py`.
- `tests/test_render.py`, `tests/test_render_fixture.py`, `tests/test_verify_render.py`.
- `docs/PRESET_OFFLINE.md` and minimal current-event changes to `docs/RENDER_FORMAT.md`.
- `examples/fixtures/presets/selector-events-v1.txt` and this worker record.

The source basis is the frozen `exclusive-fixed-registration-v1` contract,
`PRESET_CORE_API.md`, `PRESET_ADAPTER_AUDIT.md`, and the existing render/evidence
contracts, including schema 3 in `PEDAL_RENDER_EVIDENCE.md`. The complete project
plan and current session instructions were read. A10's independent literal
page-122 oracle supplied the test registrations; neither production generation
nor a runtime lookup supplied expected rows.

## Coherent source and toolchain

The build used a copied worktree at `out/a24-preset-offline/source`, including
the integrator's accepted but then-uncommitted core/data changes. The associated
HEAD was `35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`; these identify checkout context,
**not** the modified tested source.

The snapshot contains 1,244 files. Its identity is SHA-256
`35022c886d8f13a9f37eb02f36a91ff31d5c5072928008830cf3cf70bf435d49`, calculated over
compact sorted-key JSON mapping each relative path to its raw SHA-256 and byte
count. The complete local map is `out/a24-preset-offline/source-snapshot.json`.
The snapshot was created before this execution note. Its nine owned code/test/
contract/score files still matched the working tree after acceptance. Ninety-nine
previously tracked fixture/demo/catalog files also matched the copied bytes;
this work changed none of those archived inputs.

| Tested input | Raw SHA-256 |
|---|---|
| `CMakeLists.txt` | `1c569b0dc5d5afbe5b99ff8529d457ca736ad8e82a36105336badbd4e9841e53` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |
| `include/hammond/Types.h` | `0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8` |
| `tools/render.cpp` | `31cad942a4cb2d3afce5d444c56635af3d9ac7ad255d2bb73de15e750b2c5c48` |
| `tools/render_fixture.py` | `5da593836b2ab71c327d34a7840a0b8505904eb9452a06b6532612472d6e3707` |
| `tools/verify_render.py` | `65f32e2d5609290fcffad929ac29ee5f8f99288d5bbe1f69b13b9e482d277a0d` |
| `tests/test_render.py` | `270012ca9fa5094e68e56552adf352e02ce460196a6a40fc31c8a3669bcaf2ef` |
| `tests/test_render_fixture.py` | `ef5eded44513f5910f51c11c73677f51f6c57757a9b7ead4d965e405164d8e3c` |
| `tests/test_verify_render.py` | `ca3be481fdeff40c743da2ac4f40cb25d92a045c2a3defa7ec9ae461a7d7efd2` |

Configuration: GNU C++ 14.2.0 (`/usr/bin/c++`, Debian 14.2.0-19), CMake/CTest
4.4.4, Python 3.12.14, Linux Release, testing enabled; native standalone, VST3 and
physical MIDI disabled. The fixed-data generator admitted both existing chapel
readings as a normal build prerequisite. The compiled renderer SHA-256 is
`ade81c8062b28a862a01c48f86220320558d893f19ab78a073deb1acf754f93b`
(140,456 bytes). `nominal.b3p` SHA-256 is
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`
(4,545 bytes), with canonical authoring SHA-256
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.

## Executed commands and results

Working directory: `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
The CMake tools were supplied at
`/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/`.
The copied tree and build directory were new; the retained root baseline
executable at `/workspace/scratch/a472c29da8b3/build-baseline/hammond_render`
was not built, replaced or modified.

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S out/a24-preset-offline/source -B out/a24-preset-offline/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build out/a24-preset-offline/build --target hammond_render -j 4
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir out/a24-preset-offline/build --output-on-failure --no-tests=error \
  -R '^python_test_(render|render_fixture|verify_render)$'
```

Configure and the strict-warning renderer build succeeded on their first attempt.
The selected CTest gate passed **3/3 suites, 107 unittest methods, 18.11 seconds**:

| Suite | Methods | CTest duration | Result |
|---|---:|---:|---|
| `python_test_render` | 39 | 4.23 seconds | Pass |
| `python_test_render_fixture` | 30 | 8.95 seconds | Pass |
| `python_test_verify_render` | 38 | 4.92 seconds | Pass |

The new acceptance includes:

- All eighteen fixed registrations versus literal bank-A edit/selection events,
  with already-held folded chords, stable sample times and matched WAV/float
  metrics across block sizes 17 and 127 at 48 kHz.
- Independently verified real selector and literal-bank bundles containing all
  eighteen rows in a continuing timeline. All rows are audible, their complete
  WAV bytes agree, and negative-zero Cancel mutes the final held lower route.
- Six same-frame ordering/alias cases per manual, including old B after fixed,
  reversed B/fixed order, fixed/Cancel and Cancel/fixed, plus values 10 and 11.
- Cancel, an explicit retained-bank edit during disconnection, and the old B
  command reconnecting the still-held note without a new note gesture.
- All twelve accepted numeric selector forms on both manuals, retained BOM/CRLF
  bytes and exact event hashes, without creating note gestures.
- Thirty invalid selector cases in each admission layer. A valid note and fixed
  event precede the late invalid command; the CLI creates no output, the producer
  creates no result or process invocation, and the consumer rejects even rehashed
  event/manifest mutations. A preexisting output sentinel is preserved.
- Twenty rehashed schema-1/2 selector cases rejected independently, including
  Cancel, fixed keys and the two adjustable bank aliases.

The existing three suites also passed their historical/default render,
integrity, process, exact-field and no-clobber regressions. This worker did not
duplicate the core's exhaustive note/contact/percussion lifecycle tests.
Python syntax parsing and scoped `git diff --check` passed.

## Executed demonstration

The documented command was run with the frozen producer and renderer, using
`out/a24-preset-offline/demo-evidence` as the new output directory. The independent
frozen verifier was then run against that directory. The result was
`succeeded` / `verified_retained_bundle`, schema 3, 23 score events, 96,000 stereo
frames at 48 kHz, block 127, seed 7 and **zero clipped frames**. Both bank-drawbar
initialization and fixed-selection transitions came from the retained event file.
The source catalog remained `atlas-chapel-nominal-v1` with authoring raw hash
`c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf`.

| Local artifact | Raw SHA-256 |
|---|---|
| New score / retained `events.txt` | `85db503f136f52f43581c35f17ae2e7418be0607dfa472bf9fbe8b99689f994a` |
| Demo `render.wav` | `75ba604050b839507208266ec602d336f1aad6882f70163d75d8f5c191427da5` |
| Demo `manifest.json` | `e46ce5d935787358eda2c66e24391151af26cf64fba15cc56cb9c9eb3332ba96` |
| `demo-verification.json` | `29f5d9ed20eeb4aace49014cac27ee1b53817f84b07f8190842fe326a97ebf6d` |
| `build.log` | `7214887b78de8b4cb2a3dbd0fd2162e3f6b88461c4c1da04abea0c0385ddb888` |
| `ctest.log` | `69ab6d787fe79eb779c1b15e43b9e3d66fbe5445943de015b43cf536f7690e1f` |

The verifier matched the readable executable and checked six retained artifacts.
It reported replay `not_performed`; authentication, source/build association
and physical fidelity remain `not_established`, as required. The build/source
observations above are this worker's separate engineering record, not an added
claim inside the manifest. Generated run outputs remain local acceptance evidence;
the new source score and these reproduction instructions are retained in Git.

## Remaining gates and handoff

The production changes were reported stable to the integrator after the scoped
Linux acceptance. The final integrated tree must receive its own coherent build
and affected-suite gate. The preserved old-executable PCM comparison belongs to
the integrator's later legacy gate and was not performed here. Actual Windows
and macOS renderer/evidence runs, native UI/VST3/device acceptance, and published
source/CI verification remain separately owned. No root CMake, main/Session,
registry or persistence source was edited by this worker.

The new all-row offline comparison used percussion off and 48 kHz. The core's
broader histories, rates, contact/percussion policies and allocation gates must
retain their own accepted results. Documentary rows do not establish physical
preset latching, loaded gain calibration, factory Table IV verification or an
end-to-end measured instrument match.

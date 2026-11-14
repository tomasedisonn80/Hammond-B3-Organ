# A15 — bounded copied-state inspection model

Actual worker: `/root/w03_a15_inspection_model`, wave 3, assignment 15 of this
session's 60 distinct workers. The integrator owns shared handoffs, CMake source
registration, independent acceptance, commits and publication.

## Source and owned changes

Implemented the accepted `standalone-inspection-v1` contract in
`docs/INTERFACE_INSPECTION_CONTRACT.md`. Checkout HEAD during this assignment was
`c83fe2336be931385f0d7ab82c55b30bfdfc8fc6`, tree
`717b3f03dda4a5da409bc9dddd552a913752cdcd`. The implementation is a concurrent
working-tree overlay; that published commit alone does not identify these files.

Owned files:

- `apps/standalone/InspectionModel.h`
- `apps/standalone/InspectionModel.cpp`
- `apps/standalone/tests/test_standalone_inspection_author.cpp`
- This note.

The public API is the frozen six-card, six-row-per-card, six-Rotary-row document
with two observation flags. Actual Service row counts are 4, 6, 3, 4, 5 and 6;
the total is 34 populated Service/Rotary rows. Every row preserves its stable ID,
unit, evidence class, availability and program-lifetime source locator. No
sound parameter, Engine, Session publication, device API, profile format or
saved-control schema changed.

Formatting uses stack/fixed arrays and locale-independent `std::to_chars`.
Dynamic text is owned in 128-byte fields with at most 127 payload bytes and a
terminating NUL. The writer marks overflow with `...` and `truncated`; canonical
accepted identity/digest and current row formats fit without truncation. The
API admits no arbitrary device strings. All output `string_view` metadata refers
to static literals. The builder performs no heap allocation, file access, live
Session/Engine read, device query, lock or resource initialization. It remains
main-thread formatting, not an audio-callback API.

## Model and observation truth

Source inspection of `Session::prepare`, the default `Engine::prepare` path,
`ConsoleModel`, `ContactBank`, `Profile`, `ControlState`, `FixedRegistration`,
`Percussion`, `PedalVoice` and `ScannerLine` establishes the displayed facts:

- The standalone contact family is **`ideal-contacts-v1`**. The separately
  available linear-travel model and its proposed 8/12 ms defaults are not active
  inspection values.
- Generator family is `ideal-shared-sine-v1`, with 91 shared sources. Tone 46
  and output gain are copied from the supplied profile, formatted to six
  significant digits and marked proposed model quantities. The ID must match
  the exact nominal grammar with zero-filled trailing storage; the authoring
  digest must be 64 lowercase hexadecimal characters followed by NUL.
  Unsupported/malformed identity data becomes visible invalid text and cannot
  inject control or non-ASCII bytes.
- Frequency admission checks its intrinsic displayed domain, finite and
  positive. Gain and expression require finite 0..1. This read-only view does
  not replace full profile preparation or claim sample-rate/Nyquist admission.
- Snapshot precedence is unavailable, unprepared, retained after a failed
  latest read, stopped, current. Only an available prepared copy exposes applied
  musical values. A retained copy keeps its exact frame/publication revision;
  no clock magnitude is treated as evidence of freshness. An unavailable copy
  has zero-initialized diagnostic fields and an explicit Unavailable state,
  which the renderer must not present as an observed clock.
- Applied controls and held targets use only `view.applied`. Desired
  `view.controls` never supplies sound values. Pending is copied separately;
  UI edit-bank labels remain explicitly Edit. Effective selections use
  `control_preset_selection` after whole-snapshot validation. Cancel preserves
  all four raw nine-position memories and held targets.
- Upper-B percussion eligibility requires enabled upper routing, no fixed
  registration and selected bank B. Retained On/Off, harmonic, volume and decay
  remain separate from eligibility; no transient charge/readiness is invented.
- Scanner research, complete AO-28, cabinet audio, physical voltages, rotor
  speeds, microphone geometry and brake retain their actual disconnected or
  unacquired boundaries. Unknown physical quantities are words with units,
  never numeric zero. There is no Measured badge.

## Executed validation

Toolchain: GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14. Reused the existing
`build-a13-sdkfree` Release build after the integrator confirmed the shared
`UiModel.h` and projection were stable and registered `InspectionModel.cpp`.
No source/SDK clone or additional build directory was created. The reused build
occupied **7.6 MiB** after this assignment; the workspace volume had **38 GiB
available** at observation.

From `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude -Iapps/standalone -fsyntax-only apps/standalone/InspectionModel.cpp
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude -Iapps/standalone -Itests -DHAMMOND_TEST_PROFILE='"/workspace/scratch/601951e27dc3/build-a13-sdkfree/nominal.b3p"' -DHAMMOND_SOURCE_DIR='"/workspace/scratch/601951e27dc3/Hammond-B3-Organ"' -fsyntax-only apps/standalone/tests/test_standalone_inspection_author.cpp
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake -S . -B /workspace/scratch/601951e27dc3/build-a13-sdkfree -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-a13-sdkfree --target test_standalone_inspection_author --parallel 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/601951e27dc3/build-a13-sdkfree --output-on-failure --no-tests=error -R '^test_standalone_inspection_author$'
```

Both strict syntax checks passed. Configure/build passed. Focused CTest:
**1/1 passed**, 0.01 seconds total. No failing iteration preceded this passing
author build. The test includes:

- All 34 row identities in order, source fragments, units, availability,
  evidence labels, row bounds and visible model/physical-unknown wording.
- All 16 combinations of available/prepared/read-success/running; preserved
  retained frame/revision; missing observations; freshness independent of
  nonzero clocks.
- Modified valid profile frequency, gain and digest; malformed, unsupported,
  unterminated, control-byte and non-ASCII identity arrays; nonfinite and
  out-of-domain displayed values; negative-zero formatting.
- Conflicting and even invalid desired controls versus valid applied values;
  fixed selection, Cancel, four unequal raw banks, independent edit banks,
  pending state and logical held-target counts including manual endpoints.
- 128 percussion combinations covering all three eligibility conditions and
  all four retained choices, 14 malformed applied-control cases and each
  independently invalid edit-bank enum.
- Deterministic documents, value ownership, byte-unchanged input objects, and a
  calibrated ordinary C++ `new`/`delete` interposition check observing zero
  allocations/deallocations for the builder. That probe does not observe C heap,
  OS allocations, other threads, locks or timing; the fixed-storage source audit
  is separate evidence for the builder's bounded implementation.

### Retained source identities

SHA-256 values observed after the passing author gate:

| File | SHA-256 |
|---|---|
| `InspectionModel.h` | `d16fe12811c399fd9edc03286ec00767e086268447e03f40fa9d9cdf9badddb9` |
| `InspectionModel.cpp` | `59df4b36e7b565a6f07f2efee63634953b55112b24927292d2f884ddddda8645` |
| `test_standalone_inspection_author.cpp` | `e1b3518f73794640963394299fa269b4e63ad9cc75ab7c409f92165bc696ba02` |
| Shared `UiModel.h` | `1c51aaa46ee12be91ae8729fa739d7f4d102dc030bae61dbf15fd0cc1692a98d` |
| Shared `UiModel.cpp` | `c536c460c6157197bc98c12c1d9d865584c043c44d1c7d3ca6d3d539f74dc0c3` |
| Integrator-owned `apps/standalone/CMakeLists.txt` | `a9fd96cd28043b207d91d1e909402590cddbbba6412152ab2ba8d1cf49f50071` |
| `docs/INTERFACE_INSPECTION_CONTRACT.md` | `cc506683e10e3c6b1bd8fdd9851c70e20fab0797057d9be929ccfeb8226d4608` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Author test executable | `37512d878941600db15b40159acfe1a94be08470cd2f615e2930b4259fa3f68a` |

## Next integration gates

A23 independently qualifies the model against the accepted contract. A16/native
integration consumes the already copied snapshot observation flags and this
document without a second Session read. Native drawing must visibly distinguish
Retained/Stopped/Unprepared/Unavailable states, show pending controls and loaded
profile provenance, keep existing device status, and make the six cards readable
at supported sizes. Rotary needs an explicit no-specimen-fidelity summary in its
renderer; the intentionally trimmed API has no separate Rotary summary field.

The current author gate is SDK-free software validation, not native raster,
platform, physical-device, audio-deadline, calibration or 1:1 visual acceptance.
No shared handoff, core/model source, state registry, commit or push was changed
by this worker. The integrator publishes the coherent completed slice.

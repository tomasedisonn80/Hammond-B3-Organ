# Assignment 14: retained pedal controls and saved-state migration

Owner: /root/w03_a14_pedal_state

Wave 3, new pedal session. This assignment implements the control-state portion
of [the adopted integration contract](../../PEDAL_INTEGRATION_CONTRACT.md).
It does not count or rewrite the earlier console continuation's assignment 14.

## Implemented contract

`ControlSnapshot` now owns `pedal_drawbars`, an independent two-position array,
initially `[0,0]`. Its shared `PedalDrawbarPositions` type comes from the frozen
`PedalVoice.h` interface coordinated with assignment 13. `ControlState` exposes
`set_pedal_drawbar`, checked `pedal_drawbar_position` and a copied
`pedal_drawbar_positions` result. Index range is 0–1 and position range 0–8.
Invalid setters/getters preserve state/destination. Whole-snapshot validation
checks both positions before any retained control changes. Manual bank selection,
Cancel and percussion edits leave pedal settings intact.

The writer emits canonical **B3CONTROLS3**, inserting exactly
`pedal drawbars <p0> <p1>` after percussion and before the upper manual. The
reader still admits the original B3CONTROLS1 and B3CONTROLS2 grammars. Both load
through a fresh candidate with pedals explicitly muted; version 1 also restores
its existing Off/Second/Normal/Slow percussion defaults. Version 3 must supply
all 73 tokens, including both pedal positions. Missing, duplicated, reordered,
out-of-range or trailing records reject without publishing partially read data.

The 16 KiB bound, locale and rounding behavior, stream/error handling and
controls-only semantics are preserved. No held pedals, owners, contact state,
source phase, readiness, time, model identity or last-rendered diagnostics were
added to the format. The updated
[format specification](../../CONTROL_STATE_FORMAT.md) records exact grammar,
older-format migration and execution boundaries.

## Files and verification

Changed the two ControlState files, two ControlStateIO files,
`tests/test_control_io.cpp`, `tests/test_controls.cpp` and the format specification.
Added `tests/test_pedal_controls.cpp` and this note. The existing
`test_percussion_controls.cpp` needed no modification. Engine, event types,
parameter registry, profile/data, shared status and historical notes were not
edited by this worker.

Built the complete core and focused consumers together in the isolated
`build-a14` directory with GCC 14.2.0, CMake 3.31.6 and the repository's strict
Release warning configuration:

```sh
cmake -S . -B build-a14 -DCMAKE_BUILD_TYPE=Release
cmake --build build-a14 --target test_control_io test_controls \
  test_percussion_controls test_pedal_controls -j 3
ctest --test-dir build-a14 \
  -R '^(test_control_io|test_controls|test_percussion_controls|test_pedal_controls)$' \
  --output-on-failure
```

The commands used the task-local CMake 3.31.6 executable. Result: **4/4 suites
passed, zero failures, 0.18 seconds**. All four native binaries executed; none
was skipped. Retained test output reports:

| Executed coverage | Observation |
| --- | ---: |
| New pedal round trips | 105, including all 81 position pairs plus 24 rounding-mode/expression cases |
| Old-format migrations | 162: both formats into every previous pedal pair |
| Rejected version-3 documents | 133, destination preserved |
| Rejected pedal snapshots | 494: all values 9–255 in each field |
| Existing I/O malformed cases | 590, destination preserved |

The new gate also checks copied ownership, manual-Cancel/selector independence,
all invalid byte-valued setters, invalid getter indices and unchanged output
strings. Current-format transport inherits the existing locale, EOF-exception,
read-failure and exact byte-limit checks. The original 60-token and 69-token
fixture literals were compared directly to HEAD and remain byte-for-byte
unchanged as migration inputs.

The observed parent revision when retaining results was
`6768ef2388819ebbaaf7cc23bdf72265dc72c561`. These checks qualify the coherent
working implementation, not that earlier committed tree. Key tested file
SHA-256 identities are:

| File | SHA-256 |
| --- | --- |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `src/ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |
| `include/hammond/ControlStateIO.h` | `2b42270c1d32bb57f3240ed48db5a45b182aaa5cec0c501d65d9f698b7016127` |
| `src/ControlStateIO.cpp` | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |
| `tests/test_pedal_controls.cpp` | `ad53c94b6604e31634cb2e3848759b6103e6f45a6b1354788bfc1332b127d5fe` |
| Shared `include/hammond/PedalVoice.h` dependency | `694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf` |

`git diff --check` passed for the tracked owned changes. Direct file-content and
local-link checks cover the new test/note as well. No commit or push was performed.

## Handoff and remaining gate

The API and owned implementation are frozen for the Engine and parameter workers.
Use one coherent rebuilt source/header snapshot: `ControlSnapshot` has changed
layout. Root owns combined regression, staged-tree identities and publication.
The old manual/percussion history tests passed with the new state, but live held
pedal/source-history preservation requires the forthcoming Engine integration;
this assignment does not claim that unimplemented path, native host state,
concurrent publication, physical calibration or complete M3 acceptance.

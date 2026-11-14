# A16 — Native workspace and inspection integration

Actual assignment 16 of this interface session. Owned `main.cpp`,
`ScriptedInput.cpp`, the native application/schema and replay-parser tests, and
`STANDALONE_INPUT_REPLAY.md`. The integrating agent owns publication and shared
status. No files were staged or committed by this worker. The staged asynchronous
MIDI discovery repair remains intact; this work adds presentation integration.

## Changes

Startup admits `--workspace play|rotary|service` and `--flat`, with Play and
Dimensional defaults. Invalid, missing and repeated options fail during CLI
admission before SDL/device initialization or output. SDL F4/F5/F6 select the
three workspaces and F7 toggles presentation through the existing UiModel path.
The replay whitelist grows from 35 to 39 names, preserving the format, bounds,
modifiers, marker ordering and event semantics; the former invalid F4 case is
now F8. CLI help and replay documentation describe the new shortcuts.

Every native frame builds an immutable `InspectionDocument` from the loaded
RuntimeProfile, copied UiViewState and two read flags. `snapshot_available_`
still means that a coherent copy has been obtained. The new
`snapshot_read_succeeded_` is assigned from the actual bounded
`Session::read_snapshot` call before its failure return, so failed reads retain
the previous state without falsely labeling it current. The renderer receives
the agreed trailing `const InspectionDocument* inspection{nullptr}` field.
No Engine call, second Session read or new device query was added.

Schema 3 retains its existing musical fields and meanings. A separate
`presentation` object contains initial selections, the exact last flushed frame,
successful screenshot frame, last frame before shutdown, and a 512-record
transition history. Each frame identifies workspace, presentation, overlay,
logical size and inspector freshness/frame/revision. Missing frames are null.
Shutdown's later stopped snapshot does not replace painted/captured records.
History truncation is explicit and does not affect musical processing or alter
shutdown/watchdog deadlines. The schema validator checks every nested frame.

## Actual verification

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Reusable Release native build: `/workspace/scratch/601951e27dc3/build-native`.
CMake/CTest: `/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/`.
The [compact report](reports/a16-native-integration.json) records the current
source HEAD, owned-file hashes and parser executable hash.

- Built `test_standalone_input_replay` with the reused native dependencies.
- Ran `ctest --test-dir /workspace/scratch/601951e27dc3/build-native -R
  '^test_standalone_input_replay$' --output-on-failure --no-tests=error`:
  **1/1 passed**, including literal admission/SDL-event checks for all 39 names.
- Compiled `main.cpp` with `-fsyntax-only` using its actual generated native
  compile command and strict warning flags, including `-Werror`: passed.
- Python compilation and owned-path `git diff --check`: passed.

Three native application methods were added: rejected workspace values; all six
startup workspace/presentation combinations with unchanged saved controls; and
an actual F4–F7 replay covering modifier/modal suppression, held-note ownership,
captured view identity and final shutdown cleanup. Existing duplicate/missing
option and Help checks were extended. The existing no-audio case now exercises
Service/Flat and requires an explicitly unprepared copied inspection state.
These application executions are **pending renderer integration**, not passes.

## Next integrated gate and limits

After A17's renderer is coherent, the integrator/A21 should build
`hammond_standalone`, then run:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native \
  -R '^(test_standalone_app|test_standalone_native_midi_replay)$' \
  --output-on-failure --no-tests=error
```

The MIDI replay suite imports the extended strict schema. Retain its original
transport, shutdown and source assertions. Existing literal held-key pixel
expectations are preserved for the integrated renderer gate; any necessary
geometry update must retain the independent held/unheld checks. Subsequent
native workspace pointer/raster/resize acceptance and actual galleries remain
separate assignments. This worker's executed SDL parser gate uses dummy video;
no physical device, native accessibility, platform, deadline or fidelity pass is
claimed.

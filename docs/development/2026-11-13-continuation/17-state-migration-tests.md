# Assignment 17 — independent control migration and history tests

Date: 2026-11-13. Continuation wave 03, assignment 17 of 60.
Agent: `w03_a17_state_migration_tests`.

## Scope and basis

Read the repository's standing agent instructions, current handoff, project plan,
atlas review, control-format contract and the new control/Engine interfaces. Read
the extracted atlas text for pp. 151–156, 389, 394 and 401. These pages distinguish
retained controls from contact and DSP histories, require immutable migration
inputs, and preserve history during ordinary routing/snapshot changes. This
assignment does not claim another complete 500-page review.

Only these implementation files changed:

- `tests/test_control_io.cpp` — extend independent format/migration verification.
- `tests/test_percussion_controls.cpp` — new control/history integration suite.

The existing CMake test discovery registers the new target without a build-file
change. No core implementation, shared status file, git index, commit or remote was
changed by this assignment; the integrating agent owns publication and handoff.

## What the tests establish

The original version-1 literal fixture remains byte-for-byte unchanged, under the
name `kLegacyCanonical`. Its 60-token mutation positions and malformed legacy-input
cases remain intact. Canonical writer expectations now require `B3CONTROLS2`,
including re-saving successfully migrated version-1 inputs.

A separate literal version-2 fixture has 69 tokens. The new tests cover:

- Each of the 16 percussion setting combinations, with parser expectations and
  canonical writer bytes derived from the documented text names independently of
  the serializer, followed by actual roundtrips.
- Loading version 1 into destinations containing every previous percussion
  combination: Off/Second/Normal/Slow are always installed, while the old banks,
  selected routes and expression preserve their documented meaning.
- Mandatory version-2 fields, each missing percussion token, every truncated token
  prefix, duplicate fields and records, reordered fields, invalid enum names,
  unknown versions and attempted version-1 extensions. A version-2 header cannot
  fall back to version-1 defaults when its percussion record is missing.
- Invalid numeric values, all 36 invalid drawbar positions, trailing records, BOM,
  NUL and non-ASCII whitespace, the exact 16,384-byte limit and rejection one byte
  above it.
- Locale independence, configured clean-EOF exceptions, initial stream failures,
  both injected stream exception types before/during/after a complete payload,
  exception-mask retention and bounded consumption for **both** input versions.
- Invalid enum values 2, 127 and 255 for harmonic, volume and decay. Serialization,
  `ControlState::restore` and `set_percussion_settings` reject atomically despite
  simultaneous valid changes to other candidate fields. Every malformed parse
  starts from a destination with nondefault percussion settings and verifies them.

The new Engine test constructs moving release and press contacts, held keys on
both manuals, a partially discharged shared percussion state, nonzero frame time,
and continuously running tone sources. It checks all 122 per-key contact snapshots,
held-key flags/counts, all 91 source phases, the frame clock and percussion readiness
around ordinary restores. It also verifies:

- All 16 restored percussion combinations preserve those live histories.
- Upper A selection, Cancel on either selected bank, a hidden B-bank edit and
  return to B retain the stored percussion controls and do not replenish readiness.
- Live restoration of a literal version-1 input migrates the controls to explicit
  defaults while preserving the current contact, key, phase and readiness history.
- All nine invalid enum restore candidates preserve controls and histories.
- A parse that fails after consuming otherwise valid changed controls leaves the
  destination usable without altering the engine's subsequent behavior.

Each failed restore, and the rejected-parse/restored-destination path, is followed
by 512 samples of further note/release/panic events. Float output bits, complete
public dynamic histories, control snapshots and percussion diagnostics match an
untouched copied engine after each block. This checks future behavior in addition
to immediate diagnostic equality.

## Observed commands and results

Commands ran from `/workspace/scratch/60e8291da354/Hammond-B3-Organ`:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S /workspace/scratch/60e8291da354/Hammond-B3-Organ -B /workspace/scratch/60e8291da354/a17-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build /workspace/scratch/60e8291da354/a17-build --target test_control_io test_percussion_controls -j 2
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/60e8291da354/a17-build -R '^(test_control_io|test_percussion_controls)$' --output-on-failure -V
git diff --check -- tests/test_control_io.cpp tests/test_percussion_controls.cpp
```

All commands exited 0. Configuration identified GNU C++ 14.2.0 and Python 3.12.14.
The project's strict warning flags, including `-Wconversion`, `-Wsign-conversion`
and `-Werror`, were active in this Release build. Both focused CTest suites passed:

| Target | Observed result |
| --- | --- |
| `test_control_io` | Passed; 558 malformed inputs preserved destination semantics |
| `test_percussion_controls` | Passed; control/history migration and future-audio checks |

The focused CTest run reported 2/2 passing in 0.04 seconds. No core bug was found
in this assigned scope and no implementation repair was required. The first build
and first focused execution both passed.

## Handoff and limits

The integrator should include both targets in the complete integration gate and
record the final committed source and hosted results. These results concern the
working source present during this assignment, not an already published commit.
No full-suite, sanitizer, macOS, Windows or hosted run is claimed here.

The tests establish declared software semantics for a nominal console model.
They do not establish measured contact/percussion accuracy, a complete DSP
checkpoint format, concurrent state publication or VST3/standalone host behavior.
Those remain separate implementation and acquisition gates.

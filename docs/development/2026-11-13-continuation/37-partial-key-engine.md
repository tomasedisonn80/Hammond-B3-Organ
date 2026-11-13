# Assignment 37: explicit Engine partial-key targets

- Agent: `/root/w07_a37_partial_key_engine`; continuation wave 07, assignment 37/60.
- Date: 2026-11-13 UTC.
- Outcome: implemented and locally qualified; integration, independent permanent
  tests, publication and hosted qualification belong to the integrating agent.
- Source basis: preserved atlas pp. 115-120, read from the extracted page files;
  especially p. 117's shared motion, distinct contact histories and partial holds.
  These are proposed architecture and acceptance boundaries, not measured timings.

## Changed files and behavior

Only the following implementation/contract files and this note were edited:

| File | Change |
| --- | --- |
| `include/hammond/Types.h` | Append `EventType::KeyPosition = 9`; preserve values 0-8; document physical target semantics |
| `include/hammond/Engine.h` | Document mode-dependent admission, whole-call rejection and target-based held diagnostics |
| `src/Engine.cpp` | Validate partial targets during complete preflight and dispatch note/position events by actual target |
| `docs/CONSOLE_DYNAMICS.md` | Specify the event, motion/history boundary, note authority and persistence exclusions |

`KeyPosition` accepts Upper or Lower, MIDI 36-96, and a finite normalized target
in `[0,1]`. Linear travel uses the existing contact model without advancing time
on application. Ideal contacts accept exactly 0 or 1; an interior target rejects
the complete request before any earlier event, output sample or state changes.
Stable same-offset ordering and render-before-advance timing remain intact.

The old note dispatch compared only a held Boolean. That would suppress a full
NoteOn after a positive partial target. Dispatch now compares the actual contact
target. Positive-velocity NoteOn commands 1; NoteOff and zero-velocity NoteOn
command 0 through ordinary release travel. Identical targets preserve the motion
segment. `key_down` and active counts mean target greater than zero: they do not
report contact closure. `AllNotesOff` retains its explicit immediate manual panic.

Preparation and `reconfigure_sample_rate()` are unchanged, confirmed by comparing
their complete method text against the frozen wave-06 tree below. No members,
lifecycle APIs, velocity mapping, new model parameters, control serialization or
ownership merge were introduced. Sources, readiness and clock are not reset by
these events. The `InputProcessor` sole-note-authority rule remains in force.

## Coherent verification identity

Wave-06 source/index was frozen by the integrator as Git tree
`4370375d5dfe2161d8eefbf492cd692f2613d9c6`. This worker did not stage, reset, commit,
push or alter another worker's files. All four additions remained unstaged while
wave-06 publication proceeded. The original staged Engine blobs were observed as
`d42f073ec1f8da1ae68dd5c610877e3d99fe88f2` for the header and
`9f9711766d5f0aa494d9613aa776e43c97db7ba0` for the implementation.

Verification extracted that exact tree into a separate scratch directory, then
overlaid only the four frozen files above. It did not compile against changing
live headers. SHA-256 identities of the qualified overlay:

```text
a8f86c3b0910a5e0921b1ff583b4c947573dfecb955bff2c8341613ffdf95fe0  include/hammond/Types.h
efb8f0eb36dccbe5f0416186ef9478091be48e5634cfd6a8f0155b3dfd1c81c0  include/hammond/Engine.h
53c07390447796f4c57e96e58b9d6720df76094e14a0e6240b284f62e4310ccf  src/Engine.cpp
af1f12f4578669dcb058fb2c260629ff986e6688aa1de9c768b8890d60ee8a6c  docs/CONSOLE_DYNAMICS.md
```

The local snapshot root was
`/workspace/scratch/60e8291da354/w07-a37-partial-key`. Its full relative-path/source
SHA-256 manifest, including the scratch harness, had digest
`1eea25622282dcb02a19c251fa38ecbf0481e2f657ec1acc5ae7722c6ab8d225`.
The scratch-only `tests/test_a37_partial_smoke.cpp` had digest
`e0f914cc2bbd07024d247e122244b8a5b952c458deeac7673da31a155e5f9de3`.
This disposable harness is not a retained repository test or publication gate;
assignment 39 owns independent permanent coverage. All four live owned files
were checked byte-for-byte against the frozen overlay after verification.

## Commands and observed results

Toolchain: CMake 4.4.4, GNU C++ 14.2.0, Python 3.12.14, Linux Release.
The repository's strict `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
-Wshadow -Werror` policy remained enabled. With `A37_ROOT` set to the snapshot root
above and `A37_CMAKE` to
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`, the commands were:

```sh
"$A37_CMAKE" -S "$A37_ROOT/source" -B "$A37_ROOT/build" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
"$A37_CMAKE" --build "$A37_ROOT/build" --parallel 3 --target \
  test_a37_partial_smoke test_engine test_console_engine test_core_robustness \
  test_contact_bank test_percussion test_contact_rate test_percussion_rate \
  test_source_rate test_input_processor hammond_parameter_info
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir "$A37_ROOT/build" --output-on-failure \
  -R '^test_(a37_partial_smoke|engine|console_engine|core_robustness|contact_bank|percussion|contact_rate|percussion_rate|source_rate|input_processor)$'
```

Configure and all selected strict builds succeeded. **10/10 CTest suites passed**
in 1.65 seconds. The scratch smoke reported 201 process calls, 33 atomic rejection
cases and 6,656 exact audio comparisons across 44.1, 48 and 96 kHz. It checked:

- Zero-time partial targets, target-based held counts, first-sample-before-motion,
  four closed contacts when approaching 0.5 from below and five from above.
- Duplicate target future equivalence, full NoteOn after a partial hold, ordinary
  and velocity-zero release, manual panic isolation and unchanged zero-time q/phases.
- Interior ideal targets including the closest interior endpoints, malformed
  targets/manuals/notes/types, valid-prefix rejection, untouched output and future
  state/audio after rejection.
- An unchanged instantaneous partial-release state across a supported rate change,
  plus exact audio/state over a mixed 2,048-frame timeline with irregular partitions.

Existing tests also passed: Engine, console integration, core robustness,
ContactBank, percussion, source/contact/percussion rate lifecycle and transactional
input. The console suite reported 1,179 source/audio oracles, 318 closed-form
readiness checks, 42 partition/disconnected comparisons and 16 preservation cases.
The input suite retained its 459,896 exact sample comparisons. Existing invalid
EventType tests use 255, not the newly valid value 9; no tests needed alteration.

`tools/parameter_info.cpp` intentionally handles only registered control-event
types with an existing throwing default. Its strict build succeeded unchanged;
KeyPosition does not become an automatable retained parameter. No other exhaustive
EventType switch required adaptation. The renderer still lacked partial-input
grammar in this snapshot; assignment 38 owns that extension.

No implementation or test failure was observed. One initial source-read command
requested nonexistent `tests/test_console.cpp`; `rg --files` identified the actual
`tests/test_console_engine.cpp`, which was then read, built and run. No fallback
disabled a check or changed compiler warnings. Scoped `git diff --check` passed.

## Limits and next step

These are local software checks on a nominal sample-grid trajectory. No measured
gesture/controller, calibrated thresholds, bounce, fractional edges, switching
bandwidth result, audio-device deadline, native host or new hosted CI result is
claimed. This worker did not execute a complete repository/platform matrix.

Assignment 38 should expose the frozen event contract in the offline parser and
matching evidence grammar, rejecting ideal interior targets during complete CLI
preflight. Assignment 39 should independently retain enum compatibility, all-key
admission, contact-subset/trajectory, note-after-partial, error atomicity and
partition/timing cases. The integrator should qualify one combined staged tree,
update shared status/next steps/log, then publish and observe its remote/CI result.

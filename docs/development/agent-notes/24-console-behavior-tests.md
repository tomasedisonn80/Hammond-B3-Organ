# Agent 24 — independent console behavior tests

Assignment: wave 04, agent 24 of 60; 2026-11-13. Owned only
`tests/test_controls.cpp` and this note. No implementation edits or commits.
Read AGENTS, README/status/next steps/log/plan, atlas review/errata, the console
extension contract, and atlas pp. 121-132, 389, 447. Agent 22 confirmed stable
Engine/Types sources before this suite was built. Persistence belongs to agent 23.

## Permanent evidence

- Nine test groups exercise ControlState directly and the actual Engine.
- Defaults require four zero banks, B selected on both manuals, enabled routes,
  expression one; all 36 retained positions receive all nine legal values
  (324 writes), with complete-state comparison after each write.
- Invalid setters/getters preserve state and checked destinations. Both bool
  destinations and invalid enum/position sentinels are checked; copied snapshots
  and copied bank arrays cannot mutate their owners.
- Direct BankDrawbar indices 0..17 address both manuals independently. Hidden
  bank edits, including mid-block edits, leave audible routes and held keys alone.
  Legacy Drawbar follows each manual's selected bank, including while cancelled.
- Held-key switches change the audio at the assigned sample. Cancel retains all
  bank values, selection, keys and expression; source phase advances through
  silence. Selected/hidden edits stay muted; reselect resumes without note events.
- Upper/lower cancellation and AllNotesOff remain independent. Panic clears
  only the requested manual's keys and preserves its cancellation/control state;
  reconnecting that route does not recreate released notes.
- Successful and stale control restores preserve every key, all 91 source phases
  and the 64-bit frame clock. Later audio verifies rebuilt routing. Unprepared
  restore rejects; 81 malformed snapshots reject atomically in both APIs.
- Thirty-four malformed new event payloads each reject zero-frame and positive
  calls (68 cases), despite valid state-changing prefixes. Output sentinels,
  consumption, controls, keys, phases, clock and subsequent audio stay unchanged.
- The fixed 2,113-frame timeline matches bitwise for block sizes
  1/17/64/127/511/1024 at 44.1/48/96 kHz, including same-frame Cancel/select orders.
  Velocity 1 and 127 renders also match bitwise.

Audio expectations use separate engines driven by independently authored legacy
Drawbar/Expression/note timelines, with the reference rendered in 53-frame blocks.
They never interpret the new console event stream through production ControlState
or restore the tested engine's snapshot. Full-state captures inspect values, not
object padding. The existing independent oscillator suite owns waveform accuracy.

## Executed verification

Tool directory: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin`.
Source directory: `/workspace/scratch/c871510c69b2/Hammond-B3-Organ`.
Commands used that directory's `cmake`/`ctest`, with these arguments:

```text
cmake -S /workspace/scratch/c871510c69b2/Hammond-B3-Organ -B /workspace/scratch/c871510c69b2/agent24-debug -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
cmake --build /workspace/scratch/c871510c69b2/agent24-debug --target test_controls -j 2
ctest --test-dir /workspace/scratch/c871510c69b2/agent24-debug -R '^test_controls$' --output-on-failure
cmake -S /workspace/scratch/c871510c69b2/Hammond-B3-Organ -B /workspace/scratch/c871510c69b2/agent24-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/c871510c69b2/agent24-release --target test_controls -j 2
ctest --test-dir /workspace/scratch/c871510c69b2/agent24-release -R '^test_controls$' --output-on-failure
```

GCC 14.2.0 strict-warning builds and final CTest runs passed: Debug 1/1 (0.20 s),
Release 1/1 (0.11 s). A concurrent Debug rebuild emitted a Make jobserver FIFO
already-exists warning and still exited zero; compilation and tests succeeded.
No test failure or Engine/ControlState implementation defect was found.

## Limits and handoff

No serializer duplication, sanitizer run, full-suite rerun, native-host test,
deadline measurement or hardware capture is claimed here. This verifies the
documented ideal exclusive A/B model, not physical preset latches, contacts,
transformer loading, percussion, pedal audio or loaded expression. Full M3 and
measured fidelity remain open. The integrator owns shared status/log updates.

# Agent 22 — retained console controls in Engine and renderer

## Scope and implementation

- Wave 04; owned `Types.h`, `Engine.h`, `Engine.cpp`, the renderer's new-event
  adapter/help and this note. No tests/shared documents/commits/pushes changed.
- Read AGENTS, current handoff/plan, atlas review/errata, console extension,
  ControlState API/implementation, engine/renderer contracts and atlas pp. 121-126,
  389, 447. Physical loading, preset latches and percussion remain unimplemented.
- Waited for coordinator's wave03 checkpoint before editing. Frozen predecessor:
  `108a92b7c27c7b4c3788b6a880eaf36597448d94`.
- Engine now value-owns ControlState. Preparation resets four muted banks,
  selected B on both manuals, enabled routes and expression one, with no keys.
- Stable event values append BankDrawbar=5, SelectBank=6, Cancel=7. Existing
  Drawbar edits selected bank; flattened bank index 0..17 edits without selecting.
  SelectBank reconnects; Cancel retains banks, selection, keys and expression.
- Full process preflight validates the new payloads before any mutation/output.
  Same-offset order and zero-frame dispatch retain the existing clock contract.
- New copied snapshot/bank/selection/route diagnostics expose no mutable state.
  Restore requires a prepared engine, validates the entire snapshot before
  mutation, and marks coefficients dirty without touching keys/phases/clock.
  Checked control diagnostics preserve their output parameter on rejection.
- Mixing uses the selected retained bank and skips cancelled manual routes.
  Legacy accumulation/multiply order is unchanged. AllNotesOff remains key release.
- Renderer accepts `bank_drawbar`, `select_bank`, `cancel`, strictly checks their
  fields and documents them in help. Legacy parsing/publication behavior is intact.

## Executed engineering evidence

GCC 14.2, CMake 4.4.4; strict C++20 warnings include conversion, sign-conversion,
shadow and `-Werror`. Task-local CMake/CTest directory: `../build-tools/cmake/data/bin`.

```sh
cmake -S . -B ../agent22-debug -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
cmake --build ../agent22-debug --target test_engine hammond_render --parallel 2
ctest --test-dir ../agent22-debug --output-on-failure --no-tests=error -R '^(test_engine|python_test_render)$'
cmake -S . -B ../agent22-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent22-release --target test_engine hammond_render --parallel 2
ctest --test-dir ../agent22-release --output-on-failure --no-tests=error -R '^(test_engine|python_test_render)$'
```

- Both builds passed; existing engine and 20-case renderer suites passed 2/2
  CTest targets in Debug (1.35 s) and Release (1.05 s).
- Temporary strict C++ smoke (`../agent22-console-smoke.cpp`) passed defaults,
  retained/hidden-bank edits, Cancel/reselect, snapshot round trip/rejection,
  unprepared restore rejection, all 91 phase bit patterns, clock/key preservation,
  panic separation, invalid diagnostics and nine atomic late-invalid event calls.
- Temporary Python smoke (`../agent22-render-smoke.py`) compared new Release to
  the frozen wave03 Release renderer: 24 identical WAV-byte/JSON results across
  three rates, two block sizes, two seeds and default/mixed legacy score fixtures.
- Six console-score partitions (1/17/64/127/512/1024) matched an equivalent
  legacy gain-control score exactly in WAV bytes and signal metrics. Sixteen
  malformed new score payloads rejected without publishing output/temp residue.
- Assigned-source `git diff --check` passed. No implementation defect observed;
  coordinator separately updated the legacy invalid-enum fixture from 5 to 255.

## Limits and handoff

Same-thread/stopped control access only; no concurrent UI or host-state protocol.
Core changes use fixed-size values and no I/O. Allocation/deadline instrumentation
belongs to later real-time audit; no new instrumented real-time claim is made.
Agent 24 owns permanent new-control tests. Coordinator owns engine/renderer docs
and shared handoff updates. These are nominal engineering checks, not measured
console fidelity, physical preset loading, complete M3 or product qualification.

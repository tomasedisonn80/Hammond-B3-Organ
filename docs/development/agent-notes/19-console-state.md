# Agent 19: retained early console state

## Assignment and evidence

Owned `include/hammond/ControlState.h`, `src/ControlState.cpp`, and this note.
Read AGENTS, current project handoff, CONSOLE_EXTENSION, ENGINE_API, PLAN,
ATLAS_REVIEW and note02; directly checked atlas pp. 121 and 123-126.
Those pages distinguish retained banks, selector connectivity, Cancel, physical
latches/loading and parameter recall from a time-dependent engine checkpoint.
Initial branch was `main`, tracking `origin/main` at `4b83053`; preserved all
other agents' in-progress changes. No Engine/Types edits, commits or pushes.

## Implemented contract

`ControlState` owns fixed arrays and one scalar; no pointers, allocation,
external lifetime or borrowed mutable state. Defaults are 36 zero positions,
bank B selected on both manuals, both routes enabled, expression 1.
All methods are `noexcept`. Mutations use checked bool: true includes a valid
no-op; false preserves state. Checked getters preserve destinations on failure.

Public value types are `DrawbarBank { A=0, B=1 }`, `DrawbarPositions`,
`ManualDrawbarBanks`, `AllDrawbarBanks` and `ControlSnapshot`. Snapshot fields:
`drawbars[manual][bank][drawbar]`, `selected_banks[manual]`,
`route_enabled[manual]`, and finite normalized `expression` in 0..1.
Snapshot equality is value equality; arrays and snapshots are copied out.

- `set_bank_drawbar(manual, bank, index, uint8_position)` retains bank identity.
- `set_drawbar(manual, index, uint8_position)` edits the selected bank.
- `select_bank(manual, bank)` selects and reconnects only that manual.
- `cancel(manual)` only disables its route; editing does not reconnect it.
- `set_expression(double)`, `snapshot()`, and `restore(snapshot)` complete edits.
- `drawbar_banks()`, `bank_drawbar_position(...)`, `drawbar_position(...)`,
  `active_drawbar_position(...)`, `selected_bank(...)`, `route_enabled(...)`,
  and `expression()` expose copied diagnostics.
- Retained `drawbar_position` ignores cancellation; active position becomes 0.
- `is_valid_drawbar_bank` and `is_valid_control_snapshot` are public helpers.
  Restore checks every position, selected enum and expression before assignment.

Exact declarations are in the header and were sent upstream before implementation.

## Executed checks

Used `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`:
`-S <repo> -B /workspace/scratch/c871510c69b2/agent19-build`
`-DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=OFF`, then
`--build /workspace/scratch/c871510c69b2/agent19-build --target hammond_core -j 2`.
GCC 14.2 strict C++20 compilation passed, including all existing core sources.
Compiled temporary `../agent19-control-check.cpp` against that static library
with `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
Passed default values, all-bank independence, cancelled edits/reselection,
manual isolation, copied getters, copy ownership, round trip, invalid manual/
bank/index/position mutations and unchanged failed-getter destinations.
All 81 invalid snapshot cases preserved the prior populated state: 72 invalid
positions, 4 invalid selected enums, and 5 invalid/nonfinite expression values.
Compile-time checks confirmed trivial copyability and selected noexcept APIs.
No permanent tests added; agent24 owns independent retained coverage.

## Limits and handoff

Exclusive A/B is an intentional engineering model. Physical multi-preset
latches/loading, fixed registrations, contact trajectories, percussion,
pedal audio and loaded expression are unimplemented. Control snapshots contain
no keys, clock, phases or envelope history. Same-thread/stopped access remains
required; no concurrent publication or measured-instrument result is claimed.
Engine integration and serializer wiring remain with agents22/23.

# Assignment 09 - console model and integration contract

- Agent: `/root/w02_a09_console_contract`; continuation wave 02, assignment 09.
- Reviewed repository baseline: `7c2ad2089f795b2147f5fc72cf10a4542d953a8c`.
- Owned outputs: `include/hammond/ConsoleModel.h`, `docs/CONSOLE_DYNAMICS.md`,
  and this note. No changes to Engine, events, controls, CLI, shared status or
  the other module owners' files; no commit, push or subagents.

## Inputs and decisions

Read the standing instructions, current README/status/next steps, latest log,
plan and atlas review. Read continuation reviews 01, 02, 05 and 06, and directly
read atlas pp. 37-42, 127-138, 389, 394, 401 and 447. Other cited architecture
requirements are traced through those full-range reviews. This assignment does
not claim another full 500-page reading, visual inspection or external factory
source verification.

Coordinated the exact public interfaces with contact owner 07 and percussion
owner 08. `ConsoleModel` is a thin value-owned aggregate of their parameter
profiles. Default construction and `make_legacy_console_model()` use ideal
contacts; `make_nominal_console_model()` selects explicit synthetic travel.
Both supply nominal percussion coefficients while the retained percussion-enable
control separately defaults to false. `validate_console_model()` composes the
module validation contracts and rejects unsupported sample rates first.

The canonical [console contract](../../CONSOLE_DYNAMICS.md) freezes:

- Current-position/current-q rendering followed by one advancement per positive
  sample; ideal zero-frame commands remain immediate, while travel and q receive
  no elapsed time. Same-offset release/press cannot manufacture recovery.
- Independent physical index-8 keying, upper-B eligibility, selected-harmonic
  indices 3/4, upper-only 1-foot masking and normal sustain compensation.
  Selected-harmonic audio may precede the detector during partial travel; only
  route eligibility gates it. Stored drawbars and physical contacts survive masks.
- Per-key independent make/break thresholds, proposed 8/12 ms travel, normalized
  units, partial-position support, current-position reversal and strict bounds.
- One shared readiness history; explicit nominal recovery during ineligible
  routing; RC-derived hypotheses distinct from measured decay; proposed gains
  and the replacement path to a qualified circuit/behavioral model.
- Parent-confirmed event extension value 8 (`Percussion`), Upper manual only,
  indices 0/1/2/3 for enable/harmonic/volume/decay and values 0/1.
- Parent-confirmed `B3CONTROLS2` grammar: mandatory percussion tokens after
  expression, before manual blocks. Version 1 migrates to Off/Second/Normal/Slow;
  future/malformed versions reject. Snapshots exclude live contacts, q, ownership,
  phases and clock, and successful control restore preserves those histories.

The contract explicitly labels this as a scoped M3 checkpoint. It makes no claim
that headers/documentation alone implement the Engine overload, event extension,
state migration, host adapter or physical fidelity. Integration and independent
behavioral tests are later assignments; shared status is the integrator's record.

## Executed checks

Compiled a standalone C++20 translation unit including `ConsoleModel.h` using
GCC 14 with `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
-Werror -I include -fsyntax-only`. It instantiated both factories and validation,
and statically checked the returned types, trivial value copying and nothrow
default construction. The compiler reported no errors or warnings. This was a
syntax/type-contract check, not a runtime behavior test.

Executed `python3 tools/check_repository.py`: source identity, chapter index,
Markdown links, prior-session agent-note consistency and data-reference checks
all passed. That checker does not independently verify the new runtime semantics
or this continuation's final agent count. No full build, sanitizer, hardware,
UI, hosted CI or deadline result is claimed by this assignment.

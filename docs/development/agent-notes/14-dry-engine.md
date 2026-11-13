# Agent 14 — dry engine facade and console mix

## Assignment and evidence boundary

- Wave 03; owned `include/hammond/Engine.h`, `src/Engine.cpp`, and this note.
- Read repository instructions, current handoff, frozen engine/profile contracts,
  source-bank implementation, and atlas pp. 61–66, 97–108, 385–390.
- Scope is the nominal M0–M2 engineering model: ideal boolean keys, drawbars,
  global linear expression and shared sine sources. No measured console,
  percussion, scanner, AO-28, Leslie, contact or host behavior is claimed.

## Implemented

- Frozen `prepare`, `process`, `frame_clock`, and `prepared` facade; profile,
  source bank, two 61-key manuals and retained drawbars are value-owned.
- Successful preparation starts muted drawbars/no keys/expression one at the
  requested timeline origin. Validation completes before replacing working state.
- Full request preflight rejects bad enum/payload/order/offset/capacity/output,
  oversized blocks and unsigned timeline overflow. Failure consumes zero events
  and preserves controls, source phases, clock, output and subsequent audio.
- Stable same-offset events precede their sample; zero-frame flushes apply once
  without advancing sources or time. Boolean keys prevent duplicate voices;
  velocity zero releases and every nonzero velocity has the same sustained gain.
- One 91-source frame is generated per processed sample, including silence and
  disconnected output. Each routed branch adds its drawbar gain to its source
  coefficient; profile output gain and expression multiply the algebraic mix.
- Changed keys/drawbars dirty the coefficients. One rebuild follows an entire
  event cluster; expression changes need no routing scan. No clipping, branch
  deduplication, power summation or polyphony normalization is introduced.
- Copied diagnostics expose key counts/state, checked drawbar positions,
  expression and checked source phases. Access is stopped/same-thread only.
- Code uses fixed storage and bounded loops, with no allocation, locks, I/O,
  logging or ownership destruction in prepare/process. Instrumented callback
  allocation/deadline qualification remains a separate test assignment.

## Executed checks

- CMake 4.4.4/GCC 14.2 Debug build in scratch `agent14-build`, with repository
  `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`:
  configure with `BUILD_TESTING=OFF`, build `hammond_core hammond_profile`: PASS.
- Initial outer CMake Python wrapper failed to import its module; using the
  installed native executable `build-tools/cmake/data/bin/cmake` resolved it.
- Scratch `agent14-smoke.cpp` compiled with the same strict C++20 flags and
  linked the built core; execution: PASS, real output peak `0.0299975`.
- Smoke independently checked the first sample from phase/frequency-profile
  data, finite nonzero audio, coherent doubled foldback and velocity independence.
- Checked all 91 phases through silent/disconnected blocks, later audio equality,
  flush/order behavior, profile value ownership and failed-prepare preservation.
- Checked valid-prefix/invalid-tail atomicity, malformed event variants, unsorted
  events, half-open endpoints, bad flush offsets, short buffers, block/capacity
  limits and terminal `uint64_t` clock overflow. Subsequent audio stayed identical.
- A 300-frame event timeline rendered bit-identically as one block and partitions
  1/62/1/63/1/127/45; controls, final clock and all phases also matched.

## Handoff

- Header readiness and diagnostics were sent to the integrator before tests.
- Agent 17 owns durable comprehensive engine tests; this smoke is temporary.
- No commits, pushes, shared-document edits or changes outside assigned source
  ownership were made; scratch build/smoke files are verification intermediates.

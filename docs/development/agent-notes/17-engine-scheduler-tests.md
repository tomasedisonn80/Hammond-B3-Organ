# Agent 17 — permanent dry-engine and scheduler tests

## Scope and evidence

- Wave 03; owned `tests/test_engine.cpp` and this note only.
- Read `AGENTS.md`, current handoff, engine/profile/type/source contracts, note 14,
  `ATLAS_REVIEW.md`, errata, and atlas text pp. 61–66, 97–108, 385–390.
- Tests exercise the real `Engine` and `TestSupport` checks, active under NDEBUG.
  All borrowed spans refer to live, correctly sized C++ storage.
- Engineering fixtures are synthetic and unmeasured; they establish no hardware,
  host, contact, AO-28, scanner, Leslie, or concurrent-UI qualification.

## Permanent coverage

- Independent long-double sine/elapsed-time oracle uses frozen seed-zero phase
  offsets, known profile frequency/amplitude/base phase and explicit output gain.
  It does not instantiate the source bank or derive expectations from engine phases.
  Audio absolute tolerances are 3e-8..5e-7; accumulated phase tolerance is 2e-12 turns.
- Audible source checks at 44100/48000/96000 Hz; a nonzero initial frame is only
  a clock origin. Initial keys/drawbars are muted and expression is one.
- Low folded branches and two distinct keys share tone 13 coherently: amplitude
  doubles, RMS ratio is two and gain is +6.020599913279624 dB; no hidden clipping.
- Every top-key drawbar independently matches the atlas p.102 printed row;
  combined routes retain three copies each of tone 80 and tone 85.
- Two manuals join the same ongoing source phase. Selected-manual AllNotesOff
  preserves the other manual, both registrations, expression, clock and phases.
- Nonzero velocity independence, repeated boolean note ownership, single-release
  clearing, zero-velocity release and held-key drawbar changes through all positions.
- Exact sample onset/release and stable equal-offset note, panic, drawbar and
  expression ordering; positive half-open end events are rejected and can be
  retained by the caller for the next block.
- Zero flushes consume only their supplied events, retain all 91 phases/time and
  touch no output. Caller cursor advancement prevents replay; no events are queued.
- Disconnected and silent processing advances sources; continuation audio matches
  connected processing. Extra output samples remain untouched.
- Full-call rejection checks all public state, all 91 phase bit patterns, output
  bits, zero events consumed and subsequent audio against an untouched engine.
  Cases include late invalid events, unsorted/end/flush offsets, payload bounds,
  every event's NaN/Inf/manual rejection, bad event enums, short output, block
  oversize, 1025 events, an invalid 1024th event, and unprepared calls.
- Exactly 1024 events succeed; uint64 terminal-frame overflow rejects atomically,
  while a legal final block and a zero-frame flush at UINT64_MAX succeed.
- Failed prepare preserves an active graph, including invalid spec/profile and
  source-increment underflow. Valid caller profile mutation and profile destruction
  cannot change the owned graph or its continuation audio.
- One absolute 2053-frame/25-event timeline has an independent hand-written gain
  schedule and source oracle. At all three rates, block sizes 1/17/64/127/512/1024
  are bit-identical on the same build, including partial final blocks and either
  positive dispatch or offset-zero flush dispatch. Final controls/phases match.
- Invalid diagnostic queries preserve destinations and state.

## Executed commands and results

GCC 14.2/CMake 4.4.4; strict C++20 warnings include conversion/sign-conversion/shadow
and `-Werror`. Debug passed in 0.33 s; Release (`-O3 -DNDEBUG`) passed in 0.16 s.

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S /workspace/scratch/c871510c69b2/Hammond-B3-Organ -B /workspace/scratch/c871510c69b2/agent17-debug -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build /workspace/scratch/c871510c69b2/agent17-debug --target test_engine --parallel 2
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/c871510c69b2/agent17-debug --output-on-failure -R '^test_engine$'
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S /workspace/scratch/c871510c69b2/Hammond-B3-Organ -B /workspace/scratch/c871510c69b2/agent17-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build /workspace/scratch/c871510c69b2/agent17-release --target test_engine --parallel 2
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/c871510c69b2/agent17-release --output-on-failure -R '^test_engine$'
```

Both configurations built cleanly and reported 1/1 CTest pass; no engine defects
were observed. No implementation edits, commits, pushes or spawned agents.
Callback-allocation instrumentation is reserved for agent 28; sanitizer/deadline,
other compilers/platforms and cross-build bit identity were not tested here.

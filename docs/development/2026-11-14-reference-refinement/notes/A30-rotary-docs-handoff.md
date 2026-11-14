# A30 — Durable native rotary handoff

Actual worker: `/root/w05_a30_rotary_docs_handoff`, wave 5. Owned
`docs/ROTARY_MOTION.md`, new `docs/ROTARY_PROPAGATION.md`, the current status
section of `docs/ROTARY_SCOPE.md`, and this note. Root owns shared status,
publication and integration. No production, numerical budget, build tree,
retained report, commit or push was changed; no worker was spawned.

## Basis and result

Read AGENTS, the complete M0–M9 plan, atlas/current-scope reviews, checkpoint,
manifest, frozen rotary contracts, complete native headers/implementations and
A16/A17/A19/A24/A27/A28 notes and retained reports. Observed HEAD was
`e4968b2acd37b6f79683704356350070fe2fc329`; additional source was uncommitted.
Motion SHA-256 remains
`a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1`;
propagation remains
`dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e`.
Both frozen contract hashes still match the accepted reports.

Corrected the obsolete `tau*g` evaluation order and open-R2 claim. Documented
borrowed immutable lifetime, canonical history admission, split positions,
inclusive coverage, staged failures/statuses, full-orbit/Mach/iteration bounds,
source-tree API availability, reproducible native/Python commands, measured
numerical results and original failures. A19's separate independent-motion
ratio diagnostic is not relabeled an identical-motion solver test. A27's
instrumented workload completed, but full ASan/UBSan/LSan failed at EPERM thread
attachment; hosted leak-enabled qualification stays pending.

Next work is concrete R4 streaming motion/waveform ownership, cubic delay and
whole-call transactions under the frozen contract, then R5 audible policy and
R6 runtime/integration. Separate horn/drum inputs, nominal/unmeasured values,
dry Engine, 47 parameters/state4 and scanner G5 boundaries remain explicit.

## Literal caller and executed check

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Compiler: Debian GCC 14.2.0-19. With root coordination, extracted this literal
example from `ROTARY_PROPAGATION.md` to `/tmp/a30-rotary-caller.cpp`:

```cpp
#include "hammond/RotaryPropagation.h"
#include <array>

using namespace hammond::rotary;

Status query_example(PathResult& result, SamplePosition& emission) noexcept {
    constexpr double rate = 48000.0;
    const MotionProfile profile{4.0, 40.0, 0.7, 1.1, 1};
    RotaryMotion rotor;
    Status status = rotor.prepare(profile, 0.25, 4.0,
                                  SpeedCommand::Chorale, rate);
    if (status != Status::Ok) return status;
    const MotionState seed = rotor.epoch_initial_state();
    std::array<MotionSegment, 2> segments{rotor.segment(), MotionSegment{}};
    status = rotor.apply_command(24000, SpeedCommand::Tremolo);
    if (status != Status::Ok) return status;
    segments[1] = rotor.segment();

    MotionHistoryView history;
    status = history.prepare(profile, seed, rate, segments, 48000);
    if (status != Status::Ok) return status;
    PreparedRetardedPath path;
    status = path.prepare(history, Vec3{0.0, 0.0, 1.0}, 0.18,
                          MicrophoneProfile{Vec3{2.0, -1.0, 1.2}}, 343.0, 1.0);
    if (status != Status::Ok) return status;
    return path.solve(SamplePosition{36000, 0.5}, result, emission);
}
```

```sh
g++ -std=c++20 -fsyntax-only -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude /tmp/a30-rotary-caller.cpp
```

Exit 0, no diagnostics. Snippet SHA-256:
`8cf1e47fc256dfaef2451cf8bb5956437dfaaa61b326390a2d1bc51977878bb4`.
This checks syntax/signatures, not runtime behavior. No native/Python suite or
shared build ran in this assignment. Local evidence-link/whitespace checks
passed; the syntax example is identical in the runbook and this note. Root
retains coherent CTest and final publication responsibility.

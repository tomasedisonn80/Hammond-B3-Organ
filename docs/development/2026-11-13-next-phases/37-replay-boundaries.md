# Assignment 37 — native replay boundaries and event drain

Actual worker `/root/w07_a37_replay_boundaries`; wave 7, assignment 37 of this
session's sixty. Owned the new native Python suite, its maintained acceptance
document and this note. Root additionally delegated only the bounded event-drain
block in `apps/standalone/main.cpp`. Root owns CMake, shared records and commits.

Read AGENTS, current plan/status/next steps, app/replay/workflow contracts and
the pinned SDL public event headers and relevant implementation. This is M9
adapter acceptance, separate from scanner/rotary and physical model work.
Starting HEAD `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`, had concurrent uncommitted additions.
The hashes below identify the actual executed app beyond that checkpoint.

## Failure, repair and exact identities

Independently reproduced root's report using a 250 ms plan of 256 identical
`0 resize 960 700` records. Old main
`e2fc28db7852c23b46615d6c97d7967d133be810ccdd32e05f244dcda606aecb`, binary
`bfb1b30b0b94fdc69c2fc1be3711b4b6d048a9f4651e9346cd8c5bd003ecb7ca`, exited 1
after 2.336 seconds: 110/256 pushed, not delivered/completed. Root's separate
run reached 133; neither partial count is treated as deterministic.

The changed block pumps native input once per turn and drains queued events with
public `SDL_PeepEvents(SDL_GETEVENT)`, retaining the total 256-event budget,
ordinary handlers and two-second grace. A negative result reports a fatal error;
the drain stops on a handler's shutdown request. No private sentinel value or
SDL hint is used. Reversing exactly this block reconstructs the old main hash,
confirming no other production changes by this worker.

| Executed input | SHA-256 |
| --- | --- |
| Repaired main | `560f3f12cd0b9a081748d601ec8ad42c69b4e73b3d68ab6d583e4d5e9be1ea88` |
| Actual native executable | `7377e8c2c146636ef3b4ca28891d257bbfcc9db8b6f42caa257b6857d97d9925` |
| New boundary suite | `3489b99dc253c1b9678768aef779e17ae3ece194f6f9ce5e684e77fc3f902eeb` |
| Unchanged Session.cpp | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Unchanged UiModel.cpp | `c42aee8edcd3663f5925581cd738997bf83438a2fdcc13072b8a40f5407997c1` |
| Unchanged ScriptedInput.cpp | `ed6987b1b134737842028e611ed5f03ea67e9b232984284d885ca2c29d27809e` |
| Complete final CTest log | `e83f47ac5a16756a79657737f166599556136753e22bd0f26247bf4e729d7842` |

Linux Release; GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14. Actual external
SDL 2.32.10 remains at `5d249570393f7a37e037abf22cd6012a4cc56a71`.
Root's existing native build embeds the unchanged nominal profile and glyphs.

## Actual checks and correction history

The repaired exact 256-resize plan exited 0 in **0.319 seconds**, with all 256
actions delivered and acknowledged. This is local wall time, not a speed gate.
The [maintained contract](../../STANDALONE_REPLAY_BOUNDARIES.md) lists literal
oracles for ties, per-resize pointer geometry, held snapshots/BMP, Quit, 0/256/257
events, 65536/65537 bytes and complete filesystem-preserving admission failures.

The first new-suite run passed 8/9 methods over 29 processes in 4.716 seconds.
Its intended white-key point `(45,500)` actually hit Lower C# at the minimum
size, yielding MIDI 37. Corrected only that fixture to the interior white-key
point `(35,500)`; retained the original MIDI-36 oracle and geometry distinction.
The direct repeated suite passed **9/9, 29 runs, 19 preserved rejections** in
4.734 seconds, zero skips. Production source remained unchanged.

Root then registered the canonical test with its mandatory executable environment
and 60-second timeout. Working directory for the final commands:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

```sh
cmake_bin=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$cmake_bin/cmake" --build ../build-native-app --target hammond_standalone --parallel 4
"$cmake_bin/ctest" --test-dir ../build-native-app \
  -R '^test_standalone_(app|workflows|replay_boundaries)$' \
  --no-tests=error --output-on-failure --parallel 2 -V
```

Strict build succeeded. Complete CTest result: **3/3 passed, zero failures,
22.80 seconds**. App: 18 methods/164 runs, 8.60 seconds; workflows: 11 methods/
15 runs, 22.79 seconds; new boundaries: 9 methods/29 runs, 4.76 seconds.
Total: **38 methods / 208 executable runs**. All used explicit dummy drivers.
No original app/workflow assertion changed for this repair.

One transient exec-server disconnect resolved on normal retry. The orchestration
host expired before final tool retrieval, but the retained log has the complete
100% CTest summary and LastTest.log has `End testing`; all test processes ended.
Those completed checks were recovered, not rerun or relabeled as interrupted.
Raw logs, original/repaired diagnostics and the isolated production patch remain
in scratch `../a37-evidence/`; the durable facts and identities are retained here.

## Handoff and limits

Main and the new suite are frozen at the listed hashes. Root should integrate
observed remote advances, run its coherent source gate and publish under the
existing authorization. No core/Session/UI/helper, warning policy, state format,
public parameter or dependency identity changed. No commits by this worker.

The evidence is finite Linux dummy execution. Windows/macOS, physical pointer
capture/audio, high-DPI behavior, native accessibility and device deadlines are
unqualified here. Some filesystem branches explicitly skip unavailable platform
facilities; all executed on Linux. The queue-read error branch was not injected.

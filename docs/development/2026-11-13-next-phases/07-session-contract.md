# Assignment 07: standalone Session contract

- Actual assignment: `/root/w02_a07_standalone_contract`, wave 2, first batch.
- Starting inspected commit: `2e917509b378d48c85cc1d52c3aa446eef9552c8`;
  tree `ac5f1888569339a9a3fd6c396d4d58fbe71dd503`. The local origin/main
  reference named the same commit. No network freshness claim is made.
- Owned paths: `apps/standalone/Session.h`, `docs/STANDALONE_SESSION.md` and
  this report. Core, parameter/state/UUID files and other workers' paths remain
  untouched. Root owns shared status, manifest acceptance and publication.

Read standing instructions, current scope/status/handoff/plan, wave 1 notes 05
and 06, and the actual Engine, control-state, performance-input, ownership and
state-exchange interfaces/implementations. Coordinated command types, UI channel
0, original owner identity, snapshot fields and recovery behavior with root and
assignment 09. Root explicitly selected whole-session overflow panic because
admitted typed events can also own notes on non-UI channels.

Frozen the SDK-free PIMPL header and precise one-producer/one-consumer contract:
256 copied commands, callback-boundary timing, whole-control restore, scoped UI
release, global panic, out-of-queue recovery, finite counter exhaustion,
coherent atomic snapshots, stopped device lifecycle and exact mono-to-stereo
rendering at 44.1/48/96 kHz. Core nominal defaults remain unchanged; an app
registration must be explicit. The implementation acceptance matrix covers
core parity, actual overflow races, ownership, restore, lifecycle, publication
contention and a calibrated callback allocation probe.

This assignment adds declarations and requirements only. No Session runtime,
native executable, device, performance, concurrency or allocation result is
claimed. Wave 3 implements Session.cpp and the named standalone-local tests;
the integrator wires and qualifies a coherent tree before publication.

## Executed checks

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

- GCC `c++ (Debian 14.2.0-19) 14.2.0`: passed a stdin translation unit with
  `c++ -std=c++20 -Wall -Wextra -Werror -pedantic -Iinclude -I. -x c++
  -fsyntax-only -`. It includes Session.h and asserts command/snapshot trivial
  copying, Session copy/move prohibition, exact capacity/UI channel and noexcept
  post/render/snapshot calls. No linking or runtime result is implied.
- Python owned-file check: **3 files, 4 local Markdown links, zero trailing
  whitespace errors**, all files end with a newline.
- Inspected actual status before/after edits; other workers' current build,
  dependency and standing-instruction changes remain untouched.

No commit or push is performed by this worker. Root approved the API and global
overflow recovery; assignment 09 received the concrete names and snapshot fields.

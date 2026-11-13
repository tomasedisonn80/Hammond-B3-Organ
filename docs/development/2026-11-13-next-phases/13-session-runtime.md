# Assignment 13 — standalone Session runtime

Actual worker: `/root/w03_a13_session_runtime`, wave 3, 13 November 2026.
Owned files: `apps/standalone/Session.cpp` and this note. No public header,
core, CMake, shared status, manifest or other worker file was changed; no commit
or publication was attempted. Integration and independent acceptance belong to root.

## Implemented

- One persistent Engine and the existing manual/pedal ownership processors;
  complete FIFO control restores, original owner identities, channel-zero UI
  release, and coordinated global panic. Nominal core defaults stay unchanged.
- Exactly 256 usable fixed SPSC slots. One atomic word combines the modulo ring
  publication cursor, recovery barrier and epoch. A slot's release CAS and a
  consumer recovery request have one modification order. Closing admission
  captures raced accepted commands for bounded discard; an epoch change prevents
  a producer suspended before recovery from publishing its old slot afterward.
- A suspended sole producer cannot create a second command-induced recovery
  after the first emptied epoch, so the epoch bit cannot undergo ABA during that
  pending CAS. Permanent exhaustion/failure bits and quiescent lifecycle rules
  cover the remaining transitions. No consumer wait or drain-until-empty loop.
- Fixed mono storage and literal unchanged L/R copies; zero-frame flushes retain
  peak and clock. Invalid render admission preserves output, queue and music.
- All snapshot payload cells are always-lock-free atomics. Acquire/release
  payload publication plus an even revision prevents torn accepted observations;
  readers make at most eight attempts and never stall the writer.
- Lifetime command/publication limits, nonwrapping public sequences/revisions,
  saturating diagnostics, out-of-queue global overflow/rejection recovery,
  earlier-control preservation, and publication-exhaustion safety panic.
- Transactional stopped preparation and stopped global release/discard preserve
  the specified controls/phase/readiness/clock semantics. No render/post/read
  allocation, destruction, lock, logging, parsing or I/O occurs in this source.

## Executed checks and identities

Checkout HEAD when inspected: `2e917509b378d48c85cc1d52c3aa446eef9552c8`.
Working source includes other workers' separately owned uncommitted changes.
Compiler: GCC `14.2.0` on Linux, C++20.

From `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`:

```sh
g++ -std=c++20 -Iinclude -Iapps/standalone -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -fsyntax-only apps/standalone/Session.cpp
g++ -std=c++20 -O2 -pthread -Iinclude -Iapps/standalone -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror apps/standalone/Session.cpp ../session-smoke.cpp ../build-baseline/libhammond_core.a -o ../session-smoke
../session-smoke
git diff --check -- apps/standalone/Session.cpp
```

Strict compile and focused smoke passed. Final rerun: 1,338 executed assertions,
8,247 coherent concurrent reader observations, 8,779 accepted producer commands;
counts depend on scheduling. Checks cover bit-identical direct Engine parity at
44.1/48/96 kHz, all copied control fields, scoped/global ownership release, exact
256-slot pressure, suffix accounting, retained controls after consumer rejection,
invalid output preservation, zero-frame peak/clock, lifecycle, command and
publication exhaustion, and simultaneous producer/callback/snapshot activity.
The smoke harness is temporary outside the repository; assignment 16 owns
durable independent acceptance tests. No smoke failure required a contract change.

| Input | SHA-256 |
| --- | --- |
| Final `Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Frozen `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Frozen Session contract | `a1e02204ab660103300cbbc32daf684450358bfdeea239d30fbe81d5825ac3df` |
| Baseline `libhammond_core.a` | `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8` |
| Baseline `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Assignment 15 separately reported actual Session/SDL dummy-device integration
success before the final strengthening of the producer CAS to acquire/release.
Its report owns those measurements; they are not this worker's executions.
Independent durable tests, allocation-hook calibration, race-detector execution,
real devices, native UI, callback deadlines and full M9 qualification remain
separate gates. Root requested this implementation handoff without extending
optional sanitizer or stress work.

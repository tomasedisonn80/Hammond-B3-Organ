# Agent 13 — shared tonewheel bank

- Scope: `TonewheelBank.h/.cpp`; exact frozen `ENGINE_API.md` interface.
- Reviewed standing docs, types/profile validation and atlas notes 01/02; `ATLAS_REVIEW.md` is absent.
- Model: `ideal-shared-sine-v1`, using `nominal-unmeasured-v1` source data.
  Atlas pp. 61-66 and 85-108, through notes 01/02, support this provisional field.
  No new atlas-page review or instrument measurement was performed here.

## Implemented contract

- Exactly 91 value-owned states retain frequency (Hz), normalized peak amplitude,
  phase (turns), prepared increment (turns/sample), and last source sample.
- `prepare` calls complete runtime-profile validation. Supported sample rates
  remain 44100, 48000, 96000 Hz. Every increment must be finite and in `(0,0.5)`;
  division underflow to zero and rounding onto Nyquist are also rejected.
- Prepare builds local candidate state and publishes only after all checks pass.
  A rejected prepare preserves every phase, sample and prepared flag. A successful
  prepare explicitly initializes a new field; it is not live sample-rate migration.
- Each frame emits `amplitude * sin(2*pi*current_phase)` before advancing each
  source once and wrapping into `[0,1)`. Every source runs, including zero-amplitude
  sources. The class has no note, registration, transport or reset-on-note API.
- Unprepared processing writes 91 zeros without advancing. Invalid tone IDs or
  unprepared phase queries return false and leave the destination unchanged.
- Processing uses bounded loops, value storage and standard-library sine; no
  allocation, ownership disposal, locks, logging, I/O or external DSP dependency.
  Call prepare/diagnostics while stopped or on the processing thread.

## Precisely specified proposed seed convention

Initialize unsigned 64-bit state `s = seed`, including seed zero. In ascending
tone-ID order 1..91, draw exactly once using modulo-2^64 arithmetic:

```text
s = s + 0x9e3779b97f4a7c15; z = s
z = (z XOR (z >> 30)) * 0xbf58476d1ce4e5b9
z = (z XOR (z >> 27)) * 0x94d049bb133111eb
z = z XOR (z >> 31)
offset = double(z >> 11) * 2^-53
phase = base_phase + offset; if phase >= 1, subtract 1
```

This is a C++ adaptation of Sebastiano Vigna's 2015 fixed-increment SplitMix64
[primary reference](https://prng.di.unimi.it/splitmix.c), retrieved and verified
2026-11-13 (the `splitmix64.c` URL redirects there). The reference grants a public
domain dedication and permission to use/modify/distribute. No source asset or
library was added. Same inputs and frame count reproduce samples on the same
build/platform/floating-point environment; cross-libm/compiler bit identity is
not promised. This seed supplies proposed electrical phases, not measured shaft
coupling or hardware phases. Frequencies are copied, never silently retuned.

## Executed evidence and handoff

- GCC 14.2.0 Debug build passed with repository strict warnings including
  conversion/sign-conversion/shadow warnings as errors. CMake command used the
  task-local `build-tools/cmake/data/bin/cmake`, external build `agent13-build`,
  and targets `hammond_core hammond_profile` with `BUILD_TESTING=OFF`.
- External `agent13-tonewheel-smoke.cpp` compiled with the same warnings and passed:
  unprepared/invalid-ID behavior; first three known seed-zero integer outputs;
  base-phase addition; emit-before-advance; profile value ownership; equal/different
  seeds; rejected-prepare continuity; all 91 phases including a muted source.
- One-second tone-46 crossing counts were 440 at 44.1/48/96 kHz. Independent
  long-double elapsed-time phase checks had maximum error `2.82802e-12` turns.
- Independent tests belong to agent 16; callback allocator/deadline, sanitizer,
  host and physical-fidelity qualification were not performed here.
- API-ready notice sent to integrator. No commits, pushes or unrelated file edits.

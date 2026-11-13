# Agent 34 — numerical bounds

## Assignment and inputs

- Wave 06; baseline `b9c1cac`; completed numerical scope on 2026-11-13.
- Read AGENTS, current status/plan/log, profile/engine/source contracts and tests,
  atlas review and chapters 009/016 (pp. 61-66, 103-108).
- Own `tests/test_numerics.cpp`, `docs/NUMERICAL_BOUNDS.md` and this note.
- Coordinated with integrator before the narrow source/header fix. No Engine,
  Profile, shared status/log, unrelated file, commit or push changes.

## Decision and implementation

- Agent 31 found `1e-300 Hz` at 48 kHz prepared but its positive increment
  rounded away at seeded phase `0.88331080821364261` for 1024 frames.
- Proposed the full-spacing floor; integrator explicitly approved it.
- Bank/Engine prepare now requires computed `frequency/sample_rate` in
  `[0x1p-53, 0.5)` turns/sample. Failure is `InvalidProfile`, atomic as before.
- `2^-53` is the largest binary64 phase spacing below one. This conservative
  support floor guarantees progress, not relative frequency accuracy near it.
  The tighter RN no-stall condition is `delta > 2^-54`; it was not selected.
- Only the Bank preparation comparison/comment and its header contract changed.
  No nominal source data, PRNG, recurrence, sine or mixing operation changed.
- Documented loader/intrinsic validation versus sample-rate-dependent prepare,
  rounding assumptions, exact bounds, observed tolerances and scope limits.

## Permanent coverage

- At all 3 rates, just-below/at/just-above floor input frequencies produce the
  respective adjacent increments. Rejects tiny positive `1e-300 Hz` too.
- Last-source rejection follows 90 valid candidate preparations; all phases
  and 257 future frames match a continuing control. Fresh failure stays silent.
- At/above-floor progress at 0, 0.25, 0.5, 0.75 and nextafter(1,0), with wrap.
- Engine last-source failure preserves controls, held key, all source phases,
  clock, prior block limit and subsequent output.
- 262144 frames/rate at actual nominal tones 1/91; no large capture or WAV.
  Exact integer modular elapsed-time residue plus bounded long-double oracle;
  no production PRNG, initial phase readback or repeated double recurrence.
- Every-frame finite/range checks; phase/sample oracle checks at first 16 and
  1024-frame checkpoints. Existing all-91 one-second/partition tests retained.
- Synthetic maximum routing enables all 122 keys/18 drawbars and coherently
  mixes 1098 branches; 256 finite samples/rate attain +1098 and -1098.

## Actual commands and results

- Toolchain: GNU 14.2.0; native CMake/CTest `../build-tools/cmake/data/bin/`.
- Configured `../agent34-release`, Release, `BUILD_TESTING=ON`.
- Built `test_numerics`; before fix CTest failed at the new expected rejection:
  `bank.prepare(rejected, rate, 1) == Status::InvalidProfile`.
- Patched source/header, rebuilt and ran verbose `^test_numerics$`: passed.
- Built `test_tonewheel test_engine test_profile` with `-j 2` and ran
  `ctest --test-dir ../agent34-release --output-on-failure
  -R '^test_(numerics|tonewheel|engine|profile)$'`: **4/4 passed**, ~2 s total.
- Max checked phase error: `7.72218156390100385345e-12` turns; final-window
  allowance `3.6379788938278867505e-11` (64-bit long-double significand).
- Max checked sample error: `4.79478160175333912793e-11` normalized units;
  final-window unit-amplitude allowance approximately `2.28582731692127616e-10`.
- Nominal compiled profile SHA-256 unchanged:
  `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
- New suite ~1 s executor run time; no callback deadline inference.
- `docs/NUMERICAL_BOUNDS.md` retains all six per-rate/source maxima, derivations,
  checkpoint scope, synthetic mix bound and reproduction instructions.

## Limits and handoff

- Bounded several-second software evidence, not unbounded drift, measured
  hardware behavior or global bitwise/platform equivalence.
- New tests are written to tolerate long double == double, but no MSVC/macOS
  execution or new sanitizer run claimed; integrated CI remains root-owned.
- Recommend integrator cross-links from central profile/engine contracts to
  NUMERICAL_BOUNDS and updates shared status/log with combined evidence.

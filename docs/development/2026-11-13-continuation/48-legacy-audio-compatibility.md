# Assignment 48 — legacy audio compatibility

Agent: `/root/w08_a48_legacy_audio_compatibility`

Date: 2026-11-13 UTC. Continuation wave 08, assignment 48 of 60.

## Scope and verdict

Added only this note and
[CONTINUATION_LEGACY_AUDIO.md](../../reviews/CONTINUATION_LEGACY_AUDIO.md).
The report independently compares exact WAV and PCM output across a pinned
pre-continuation renderer and the published wave-seven runtime, then verifies
the unchanged historical schema-1 bundle. No production, permanent-test,
shared-status, CMake or index change was made. No commits, pushes or subagents
were used by this assignment.

**All compatibility checks passed.** There were no compilation failures, render
failures, audio mismatches or production defects. A typo in the assignment's
initial reference hash was resolved by hashing the actual executable and reading
the existing retained evidence; it was not a changed binary or product failure.

## Identity and independence

Read `AGENTS.md`, current status/next steps/development log, the project plan,
atlas-review boundaries, render contract, fixture catalog, earlier renderer
acceptance and historical demo replay. Relevant complete atlas chapters were
read at pp. 103-108 and 385-390. The runtime skill was read; its advertised
environment-status tool was not available in this worker. Local paths, compiler
and build configuration were inspected directly; no environment or dependency
change was needed.

The retained reference has SHA-256
`8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4`.
Existing evidence links it to a clean `6c3dd8b` replay, so I built a fresh
`9c8068c95f6843dce95f7f22d729738eef8074f6` reference rather than infer its original
source from a retained filename. The clean archive contained no live overlays.
The new baseline executable has a different hash,
`1253b5bae0ce0c40dd1e30595220810e731e93a9eee9bb3a0fd63eff1ce67229`.
Its source tree is `a8cd06fb906026617c697c514709222c91eb17e3`, and its tar archive
SHA-256 is `c55a8524ce8ce8769ed7ffe42901e8a48ae8e29035f68565f9b9801e9ef9f5a3`.

Current source/executable qualification is pinned to published commit
`9a5c99a862daf26a2bab9b05613c98803727a3e7`, tree
`a85f1bcb43d2815b6f661172f7ab394ad34bee7e`. All 296 tracked archive blobs were
verified against that tree before use. The executable SHA-256 is
`cc0f7a98cdc23694e18c8b53a1241704a876331677688950dea0e7cd6a498efd`.
Its runtime/test sources are unchanged from the integrator's full-gate tree
`1132e9cf242997473b87dd64a8a65086580d594c`; only three Markdown records changed.

The generated baseline and current compiled-profile bytes agree exactly at
SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The legacy catalog, all five score bytes and raw authoring JSON were independently
compared with `git show 9c8068c:<path>` and remain unchanged.

## Executed checks

| Check | Observed result |
| --- | --- |
| Fresh baseline build | Strict GCC 14.2.0 Release, C++20, warnings as errors, sanitizers Off; passed |
| Baseline versus current defaults | 11 complete WAV and decoded PCM pairs exactly equal |
| Current defaults versus explicit ideal/Off/Normal/Slow | 11 complete WAV and decoded PCM pairs exactly equal |
| Held-key bank/Cancel partitions | Blocks 1, 127 and 65536 agree for all three selections; six additional comparisons |
| Legacy report preservation | All 15 old fields exactly equal after removing only the three mandatory schema-2 additions |
| Retained reference cross-check | One four-second render matches the fresh baseline/current WAV and old metric fields |
| Historical bundle | Independent verifier passes schema 1, six artifacts, 192000 frames; seven bundle files unchanged |

There were 34 actual renderer calls plus one independent-verifier CLI call.
The 11 cases per renderer selection contain 880040 frames and 1760080 interleaved
PCM channel samples. All renderer calls together produced 2832120 model frames.
Every output was decoded as stereo PCM16, checked for its requested rate/count
and equal dry channels, and compared as both complete WAV bytes and PCM payload.
All calls returned success, produced no stderr and reported zero clipped frames.
The report retains the parameter table and resulting complete-WAV hashes.

## Actual commands and retained scratch record

A Python `git archive`/`tarfile.extractall(filter="data")` step extracted only the
pinned baseline into the following source directory. The actual build commands
were:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a48-legacy-qualification/baseline-source \
  -B /workspace/scratch/60e8291da354/a48-legacy-qualification/baseline-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_ENABLE_SANITIZERS=OFF
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a48-legacy-qualification/baseline-build \
  --target hammond_render --parallel 2
python /workspace/scratch/60e8291da354/a48-legacy-qualification/compare.py
```

The scratch harness constructed each legacy invocation from the report's table:
`--profile`, `--frames`, `--sample-rate`, `--block-size`, `--seed`, `--drawbars`,
either `--events` or `--note`, `--fail-on-clip`, and a distinct `--output` path.
For the actual-default case it omitted rate/block/seed/registration/note options.
The third selection appended `--contacts ideal --percussion off
--percussion-volume normal --percussion-decay slow`. It parsed JSON independently
and decoded WAV files with Python's standard-library `wave` and `struct` modules;
it imported no producer or renderer validation helpers. The same-thread scratch
run required all comparisons to pass before writing its aggregate record.

The verifier command actually used was:

```sh
python /workspace/scratch/60e8291da354/checkpoint-w07-src/tools/verify_render.py \
  /workspace/scratch/60e8291da354/checkpoint-w07-src/examples/rendered/nominal-two-manual-v1/bundle
```

| Scratch record | SHA-256 |
| --- | --- |
| `a48-legacy-qualification/source-identities.json` | `d7aac0f7c3ed3500c2f7c8ba72fc57852d57953d56825e9ee58811ac57e1e796` |
| `a48-legacy-qualification/compare.py` | `e9fe2be5f999846104293928e6d64570f1d478165e524f25bd5f39c01d9f962b` |
| `a48-legacy-qualification/comparison.json` | `a73239fd122fc10bc11304530e35b9a349d91e6c40d889163b42b24f2584541f` |
| Qualified independent verifier | `332d7cbc694ab457ed607f4473f688ea6d86c8cf2765e706ec463fef18dc20db` |

These temporary paths identify the actual run, not dependencies for future tests.
The permanent report retains the source/artifact identities, complete case table,
comparison rules and common output hashes needed to repeat this scope after
rebuilding the pinned revisions.

## Limits and concrete handoff

No new permanent matrix was added: existing legacy catalog, renderer and verifier
suites already retain their behavioral gates. This assignment resolves the
specific continued-audio-compatibility question after the rate and partial-key
extensions. It covers Linux/GCC in this environment, not universal floating-point
byte identity across compilers or libraries. Schema-2 metadata intentionally
differs; nominal travel and enabled percussion are separate opt-in behavior.
Physical calibration, native hosts/devices and callback deadlines remain outside
this result. Historical verification preserves the original bundle's unresolved
authentication/build-association fields.

The integrator should retain both documents with wave eight, update current shared
status/next steps/log, complete the remaining exact staged-source checks and
observe that publication's hosted results. No production fix is requested.

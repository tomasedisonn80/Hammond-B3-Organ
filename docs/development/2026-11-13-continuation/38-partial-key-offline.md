# Assignment 38 — partial-key offline input

Agent: `/root/w07_a38_partial_key_offline`

Wave: 07, assignment 38 of this continuation's 60 new agents

Date: 2026-11-13 UTC

## Implemented contract

The renderer, evidence producer and independent verifier accept the five-field
score command `frame key_position upper|lower MIDI36..96 target`. The target must
parse as finite binary64 in `[0,1]`, subject to the existing strict decimal-token
and underflow rules. Nominal contacts accept interior targets; ideal contacts
accept only 0 and 1. The command uses assignment 37's `EventType::KeyPosition = 9`
without changing earlier event identities, saved controls or parameter IDs.

The C++ score parser receives the selected contact mode and rejects an invalid
target during `load_score()`, before `TemporaryWave` opens an output. The public
producer helper is `validate_events(raw, frames, contacts="ideal")`, preserving
existing two-argument callers. `run_fixture()` supplies the selected mode before
creating a bundle or launching its renderer. The independent verifier retains its
own parser and receives the declared manifest mode; it imports no producer helper.

`key_position` extends schema 2's score grammar. The 13 manifest parameters,
18 renderer metrics, 26 invocation tokens, source/contact/percussion model IDs,
file bounds and artifact identities remain unchanged. Existing schema-2 bundles
keep their meanings. Schema 1 retains its original eight-event grammar and rejects
the new command even for endpoint targets. No historical fixture was rewritten.

The three format contracts document partial holds, history-preserving reversal,
full NoteOn after a partial hold, mode-dependent preflight, and synthetic-model
limits. The source basis is atlas pp. 115–118, especially p. 117's separate
mechanical trajectory, nine contact histories and partial-depression requirement.
This task exposes the existing nominal model; it adds no measured trajectory,
fractional timing, contact bounce, antialiasing, native controller or saved DSP
checkpoint.

## Coherent source and observed checks

The qualification source was extracted from immutable Git tree
`4370375d5dfe2161d8eefbf492cd692f2613d9c6`, then overlaid with assignment 37's three
frozen Types/Engine files and this assignment's six production/document files.
Every overlay was hashed before the build and compared with the live file after
the checks. No older library was linked against later live headers.

Strict GCC 14.2.0 Release configuration/build succeeded with Python 3.12.14.
Historical `python_test_render`, `python_test_render_fixture` and
`python_test_verify_render` passed **3/3 CTest suites in 4.18 seconds**: respectively
34, 28 and 34 Python methods, **96 total, zero skipped**. No failing compile, test,
runtime assertion or subsequent production correction occurred.

A separate temporary smoke harness exercised these new boundaries:

| Check | Observed result |
| --- | --- |
| Actual C++ preflight | Six rejections: ideal interior target, MIDI 35, target 1.1, target -0.1, NaN and unknown manual; no WAV or temporary output appeared |
| Producer preflight | The same six cases raised `FixtureError`, created no bundle and never called the mocked renderer invocation helper |
| Independent parser | Rejected ideal schema-2 interior target and schema-1 interior/endpoint commands; accepted nominal schema-2 partial target |
| Public helper compatibility | Existing two-argument call accepted an ideal endpoint; explicit nominal mode accepted a partial target |
| Actual evidence | Two schema-2 bundles, nominal partial/full/reverse/release and ideal endpoint input, passed independent verification |
| Format preservation | Both bundles retained exactly 13 parameters, 18 renderer metrics, 26 argv tokens and unchanged supplied score bytes |

The nominal smoke used 4,000 frames, block size 127, upper MIDI 60, target 0.5 at
frame 0, full NoteOn at 1000, target 0.5 at 2000 and NoteOff at 3000. The ideal
smoke used lower MIDI 36 with endpoint targets at frames 0 and 1000. Both used
48 kHz. Assignment 39 owns the broader permanent new-feature acceptance tests.

Commands actually run (the qualification directory contains the frozen source):

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a38-offline-qualification/source \
  -B /workspace/scratch/60e8291da354/a38-offline-qualification/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a38-offline-qualification/build \
  --target hammond_render --parallel 3
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a38-offline-qualification/build \
  --verbose --output-on-failure \
  -R '^python_test_(render|render_fixture|verify_render)$' --parallel 3
python /workspace/scratch/60e8291da354/a38-offline-qualification/smoke.py
```

| Frozen file | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `a8f86c3b0910a5e0921b1ff583b4c947573dfecb955bff2c8341613ffdf95fe0` |
| `include/hammond/Engine.h` | `efb8f0eb36dccbe5f0416186ef9478091be48e5634cfd6a8f0155b3dfd1c81c0` |
| `src/Engine.cpp` | `53c07390447796f4c57e96e58b9d6720df76094e14a0e6240b284f62e4310ccf` |
| `tools/render.cpp` | `6838b1e8b406935cc8f69bd78aedc57b91ae55280c62d73220813f6d01d601bb` |
| `tools/render_fixture.py` | `9e4a63808a7d754a038b503242dfa078c5cfaeaa1bc9ca9b80c3646d7c56fd36` |
| `tools/verify_render.py` | `332d7cbc694ab457ed607f4473f688ea6d86c8cf2765e706ec463fef18dc20db` |
| Qualified renderer | `cc0f7a98cdc23694e18c8b53a1241704a876331677688950dea0e7cd6a498efd` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Snapshot manifest SHA-256:
`9965f61ee572c3b377052d6f6b67d59144a9ab0a153cd2666e2aa14f43353106`.
Temporary smoke harness SHA-256:
`80e5f94aba28521a06f04308c0e4bda327fa82ea1881b7d177bb6557b5595f67`.
These paths/hashes identify an observed run; future qualification must use a fresh
coherent source and permanent repository tests, not require scratch files to survive.

## Files and handoff

Changed only `tools/render.cpp`, `tools/render_fixture.py`, `tools/verify_render.py`,
`docs/RENDER_FORMAT.md`, `docs/RENDER_EVIDENCE.md`, `docs/RENDER_VERIFICATION.md`
and this note. No tests, fixtures, CMake, shared status, Git index or publication
were changed by this assignment. The parser API and exact source hashes were sent
to assignment 39 before its independent acceptance work.

The integrator must combine the frozen Engine/parser changes with assignment 39's
tests, qualify one exact staged tree, update shared status/next steps/log, then
publish and observe that revision's hosted matrix. This local scope does not
establish native platform results, physical calibration or callback deadlines.

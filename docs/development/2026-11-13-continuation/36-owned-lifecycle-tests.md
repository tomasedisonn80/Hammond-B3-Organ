# Assignment 36 — ownership through sample-rate lifecycle changes

Agent: `/root/w06_a36_owned_lifecycle_tests`

Identity normalization: assignment 54 recorded the integrator-confirmed
canonical dispatch name; the original evidence below is unchanged.

Date: 2026-11-13 UTC. Continuation wave 06, assignment 36 of its separately
counted sixty assignments. Scope: independent cross-layer verification using
`NoteOwnership`, `process_owned_notes()` and the wave 06 Engine rate API.

## Files and source boundary

Added `tests/test_owned_lifecycle.cpp` and this note only. No production code,
build definition, shared status file or index was changed. The integrator owns
staging, the combined publication gate, commits and push verification.

The test compiled against an isolated `git archive` of the integrator's immutable
Git **tree**, not a commit, `4370375d5dfe2161d8eefbf492cd692f2613d9c6`, plus only
this new test. The archive is `/workspace/scratch/60e8291da354/a36-frozen-src`;
the out-of-source Release build is `/workspace/scratch/60e8291da354/a36-release`.
No subsequent live Engine/header edits were copied into this archive. The test
uses the wave 06 full-key API and contains no future partial-key event.

| Input or output | SHA-256 |
| --- | --- |
| `tests/test_owned_lifecycle.cpp` | `1d99b9680bb088e169b800b78b843685d0cf8cd6932ed29fefd70c66ca245c0f` |
| Local Release `test_owned_lifecycle` executable | `95f5eb1da9ffea852bde5df4a8a1d2bc3c24f2b66e45df1417718fe24096fba8` |
| Build-generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Read `AGENTS.md`, the current plan/handoff context, and
`SAMPLE_RATE_LIFECYCLE.md`, `INPUT_PROCESSOR.md`, and `NOTE_OWNERSHIP.md`.
Atlas pp. 130, 132 and 151 supply the declared ownership/timing boundaries:
original manual destinations survive remapping, only elapsed samples advance
shared history, and software ownership evidence is separate from physical
contact or percussion qualification.

## Independent mixed-rate evidence

The test hand-writes **32 host commands**, a separate **22-event physical-key
timeline**, and six expected surviving-owner tables. It never generates its
expected physical events by calling the ownership translator. A separate Engine
receives that direct timeline; the owned Engine receives only host notes through
the transactional wrapper. Control-only changes are explicit zero-frame boundary
operations on both engines.

The 3,814-frame sequence runs with both ideal and nominal linear contacts.
For each contact mode, partitions 1, 7, 31, 127 and 257 frames, plus an irregular
3/127/1/257/19 selection, produce identical audio and boundary states. Each run
also compares owned and direct Engine audio/state after every processing block.
All 91 phases, all 122 held targets/contact snapshots, controls, clock, rate and
percussion diagnostics are checked. Readiness, phases, positions and targets
receive additional bitwise double comparisons.

| Segment | Rate, frames | Boundary and ownership actions | Observed exit state |
| --- | --- | --- | --- |
| 1 | 48,000 Hz, 601 | Upper 60 has owners on two channels; Lower 67 and two anonymous Upper 64 owners join; one Upper 60 owner releases | Four owners on three physical keys; readiness below one; nominal Upper 64 is partway down |
| 2 | 96,000 Hz, 379 | Swap bus destinations, Cancel Upper, repeat an identified On, release one anonymous Upper owner, add notes on new destinations | Five owners retain their original manuals; release of old Lower 67 reaches Lower; Cancel permits readiness recovery |
| 3 | 44,100 Hz, 487 | Reselect Upper B; restore changed expression, lower-bank and percussion controls; release original Upper notes after remapping; channel AllNotesOff removes remaining bus 0/channel 0 owners | Two surviving Upper owners on bus 1/channel 3; old Upper anonymous owner releases before newer Lower owner; one channel command emits two final physical releases |
| 4 | 48,000 Hz, 29 | Select Upper A; release Upper 72/76 and add Lower 55 | One Lower owner; readiness recovers while Upper is ineligible; nominal Upper 72 has an upward target and its ninth contact still closed |
| 5 | 96,000 Hz, 1,081 | Reselect Upper B without resetting ownership/readiness; velocity-zero release of remapped Lower 55; play/release Upper 65 | One Lower 69 owner; prior release travel proceeds through the new rate |
| 6 | 44,100 Hz, 1,237 | Restore initial musical controls; add a second Lower 69 owner; channel releases; play/release Upper 62 | Zero owners and held keys; every contact settles open at position/target zero |

Every rate boundary checks exact state/owner preservation and follows the rate
operation with a same-rate no-op. Zero-frame empty input and unchanged control
restoration preserve the full observed state and output sentinels. Changed
settings, Cancel and selection preserve physical state, readiness, phase and
clock while changing the intended route/eligibility controls. Expected ownership
tables explicitly count every manual/pitch and check the corresponding held key.

## Rejection, future behavior and retained limits

- Fourteen rejected-rate cases cover both contact modes: unsupported zero,
  negative, 32 kHz, infinity and NaN requests, plus a deliberately synthetic
  30,000 Hz source valid at 96 kHz but invalid at 44.1/48 kHz. Every failure
  preserves the separately owned adapter and all observed Engine state. Three
  subsequent blocks with actual note input/audio match an untouched control.
- After transitions among all supported rates, the original 17-frame maximum
  still accepts 17 and rejects 18. Short buffers, half-open timestamp violations,
  identified-pitch conflicts after a valid prefix, hard block overflow and 1,025
  host commands reject atomically. Rejected output preserves every float,
  including negative-zero sentinels. Ownership and future output/state match
  untouched controls. Successful maximum-sized calls retain original Upper
  owners after bus remapping while new notes reach Lower, and preserve output
  entries beyond the requested frames.
- At a `UINT64_MAX - 5` origin, processing three frames and changing rate leaves
  exactly two renderable frames. A three-frame transaction rejects without
  installing a tentative channel release. Two frames reach `UINT64_MAX` exactly.
  Another rate change consumes no frame; zero-frame final channel release and
  same-offset press/release remain valid. A positive frame rejects while
  preserving owners/state/output. A too-large block still reports its earlier
  admission error. No positive future probe is claimed after the clock is full.

## Executed checks

GCC 14.2.0, C++20, Linux, Release, with the repository's warnings-as-errors flags.
The first compilation and execution passed; no production correction was needed.
The existing CMake glob discovers this test without a build-file edit.

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S /workspace/scratch/60e8291da354/a36-frozen-src -B /workspace/scratch/60e8291da354/a36-release -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build /workspace/scratch/60e8291da354/a36-release --target test_owned_lifecycle -j4
/workspace/scratch/60e8291da354/a36-release/test_owned_lifecycle
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/60e8291da354/a36-release -R '^test_owned_lifecycle$' --output-on-failure
```

Observed executable output:

```text
owned lifecycle: 12 mixed-rate runs, 156 preserved rate boundaries, 14 rejected rates, 42 rejected input blocks, 50 future probes, 10086 exact state comparisons, 2408812 exact sample comparisons
```

The 156 rate-boundary checks include the separate direct reference, initial
same-rate boundaries and additional limit/rollback fixtures. Each also tests a
repeated same-rate call. The 2,408,812 float comparisons include untouched output
tails and rejection/zero-frame sentinels; they are not 2,408,812 independently
rendered samples. The twelve 3,814-frame owned/direct comparisons cover 45,768
rendered positions; ten partition-to-baseline comparisons cover another 38,140.
The 50 future probes comprise fourteen rejected rates and thirty-six rejected
input blocks; six near-overflow rejection cases use the explicit remaining-clock
checks instead.

Focused CTest result: **1/1 passed**, 0.16 seconds reported. This is elapsed test
execution, not an audio-callback measurement. Scoped `git diff --check` passed,
and explicit line scanning found no trailing whitespace in the new test. Engines
and comparison systems use test-owned heap storage; fixed small event/audio
arrays and the production wrapper's bounded storage keep the test's call stack
bounded. No allocation or portable stack-budget audit is claimed here.

## Handoff and remaining gates

This closes the assignment's scoped ownership/rate transaction verification.
The integrator must qualify the complete staged wave 06 source tree, include
assignment 35's separate analytic Engine rate suite, update shared status and
ledger, then publish and observe the actual hosted results. Do not infer those
results from this focused local pass.

Next host-facing lifecycle work must specify stopped/deactivated processing,
the ordering of pending input/control events, output-buffer renegotiation,
rate-segment time conversion, and ownership continuity before executing an
actual native host/device transition. This assignment establishes no native
plugin ABI, device reactivation, concurrent publication, callback deadline,
Windows/macOS qualification, sanitizer result, or measured contact/percussion
fidelity. Ordinary saved controls still exclude ownership and DSP history.

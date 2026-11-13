# Assignment 16: independent console engine tests

Agent: `/root/w03_a16_engine_console_tests`; continuation wave 03.
Working-tree base at completion: `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`.
The tested integration was still an uncommitted shared working tree; the source
identities below identify the exact files observed after the successful run.

## Scope and result

Added the permanent `tests/test_console_engine.cpp` suite and this note. No core,
existing test, CMake or shared status file was changed by this assignment.
The existing CMake test-source discovery registers the new target automatically.
The integrator owns the full regression run, publication and shared handoff.

The focused Release test passed with strict compiler warnings enabled:

```text
Console engine passed: 1179 source/audio oracles, 318 closed-form readiness checks,
42 partition/disconnected comparisons, 16 failure-preservation cases.
```

No reproducible core defect was found by these checks. An argument-evaluation
ordering hazard in the new test itself was removed before the executed run:
each source frame now advances in a separate statement before reading its oracle
samples. No engine behavior was changed to accommodate the tests.

## Independent expectations and permanent coverage

The expected routing comes from the frozen
[console contract](../../CONSOLE_DYNAMICS.md), particularly its contact/source
separation, sample convention, eligibility and shared-readiness rules. The atlas
evidence is pp. 100, 111, 115-120 and 127-138; pp. 128-129 and 132 specifically
motivate a physical keying contact and elapsed-time shared state. These tests
validate the declared nominal software contract, not measured hardware behavior.

The audio oracle advances a separate `TonewheelBank` with the same profile, seed
and rate, then explicitly adds the required contact/source routes. This is an
independent oracle for **Engine routing and source reuse**, not an independent
implementation of tonewheel synthesis. Expected readiness uses long-double
elapsed-time exponential expressions for complete constant-condition segments,
not a duplicate of the callback's sample recurrence or a recorded golden file.

Custom binary-exact gain settings deliberately differ from the factory values:
slow decay 0.25 s, fast decay 0.0625 s, recovery 0.125 s, Normal gain 0.75, Soft
gain 0.125, Fast gain multiplier 2 and Normal upper-sustain factor 0.25. This
checks that integration actually uses its copied model parameters. Custom travel
thresholds at exact sample boundaries make the selected contact and the keying
contact independently observable.

| Behavior | Executed expectation |
| --- | --- |
| Folded branches remain separate | MIDI 36 contacts 0 and 2 share a source but close at samples 60 and 240; 501 samples independently verify zero, one and two coherent contributions. |
| Physical keying ignores drawbars | Upper contact 8 drives the detector while sustained drawbars are zero; changing the audible 1-foot drawbar does not change the detector, q or masked audio. Lower-only notes do not drive it. |
| Eligibility follows the retained route | Enabled percussion uses upper B only. Held keys remain physical through A and Cancel; route changes retain q and the stored percussion settings. |
| Normal compensation and the 1-foot mask | Only eligible upper sustained audio is attenuated and only its contact 8 is masked. Lower sustained paths remain ordinary. A, disabled percussion and Soft behavior use their declared gains. |
| Harmonic identity and source phase | Second and Third read contact indices 3 and 4 from the same continuously advancing source bank, even with their sustained drawbars at zero. Raising a selected drawbar adds exactly its sustained branch. |
| One shared readiness state | Legato chord additions, repeated physical presses, zero-time release/repress and mode changes retain q. One remaining upper key continues decay; an elapsed all-released interval follows analytic recovery. These segments run at all three supported rates. |
| Selected audio can precede keying | A custom contact 3 closes at sample 120 while contact 8 closes at sample 360. Audio passes with q = 1 before keying, and the first decay occurs after the first keyed sample. |
| Zero elapsed time | Zero-frame calls and same-offset off/on clusters leave q, source phases and clock unchanged; travel targets can change without advancing position. |
| Release, panic and restore | Ordinary release retains the detector until the physical contact opens. `AllNotesOff` immediately clears that manual's contacts while retaining q. Valid control restoration preserves every contact, source phase, q and clock while changing eligibility. |
| Model ownership and diagnostics | Caller-side model mutation after preparation cannot change future output. Invalid contact diagnostic queries leave their output destination untouched. Velocity 1 and 127 produce identical nominal physical-key behavior. |

### Complete timeline and future-state comparisons

One 2,053-sample timeline contains 36 events covering both manuals, retained banks,
folded notes, overlapping and repeated keys, release reversal, Cancel, expression,
all percussion controls and manual panic. It starts at frame 1,000 to exercise
nonzero clock origins. For ideal and linear-travel modes at 44.1, 48 and 96 kHz,
the suite compares one-sample rendering with block sizes 17, 64, 127, 1,024, the
whole timeline and the repeating irregular pattern `3, 29, 1, 211, 7, 64, 509, 5`.
Empty zero-frame calls are interleaved at block boundaries.

All 36 partition comparisons require bit-identical audio and identical controls,
clock, all 122 contact snapshots and all 91 source phases, plus readiness and
routing diagnostics. Six additional disconnected-output runs must arrive at that
same state and produce bit-identical audio and state through a further 1,024
samples with new events. Pending travel at the end of the main timeline makes
that continuation sensitive to hidden trajectory history.

### Atomic failure cases

Nine invalid trailing events follow a valid note event in a request. They cover
the wrong manual, unsupported setting index, fractional/out-of-range values,
NaN, infinity, an offset equal to the block length and an unknown event type.
Every request must report zero consumed events and preserve sentinel output.

Four malformed console models cover a late contact parameter, nonfinite travel,
zero recovery time and nonfinite gain. Three malformed control snapshots cover
each percussion enum while also carrying otherwise valid changed controls.
All 16 cases compare the complete observable state and a 1,024-sample continuation
with an untouched copy, proving rejection does not partially publish valid prefixes
or alter hidden future behavior.

## Reproduction

Run from the repository root. The session used GCC 14.2 and C++20, Release mode,
the existing strict warnings-as-errors configuration and a separate build tree:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake -S . -B ../agent16-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake --build ../agent16-release --target test_console_engine -j2
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest --test-dir ../agent16-release -R '^test_console_engine$' --output-on-failure
```

Observed focused CTest result: **1/1 passed**, 0.28 seconds. The duration describes
this test execution only; it is not a DSP performance result. The test assertions
remain enabled in Release through the repository's `TestSupport.h` checks.

| Tested file | SHA-256 |
| --- | --- |
| `tests/test_console_engine.cpp` | `e83b53b2f34fca27c16b515a846a9b1d9e63dfa995767341e5b5526f11466c76` |
| `src/Engine.cpp` | `3ac33dcb6d22458821c07de854aba46d6a797190325f858c352ea527ca640f5f` |
| `src/ContactBank.cpp` | `2adc9662992805c980488e065647463474f63547e9a6be7fab2a1f3ec05a8bb7` |
| `src/Percussion.cpp` | `873b6e71ebf7e2535884bfe6d5d71a7a36fc101e536ed987f59b7cd87a446564` |
| `src/ControlState.cpp` | `7b49116640c1f466f655e166683f84e1561402976ca92c06d01feef88e66607c` |
| `include/hammond/Engine.h` | `c41c65ab153d2ecb60e9ced49e18f269d483c8643085f732b86b0e09086a7af0` |
| `include/hammond/ContactBank.h` | `6200803eb1032a3ac76d3683a502ea9c68716ab80b0904499224af51cc30c0a4` |
| `include/hammond/Percussion.h` | `725a530a578937b28bbe1fb8fb470852959b6c6b31fad7d5dbe288fc4e591039` |
| `include/hammond/ControlState.h` | `88f22e3c6c6ad4a7cca756ba2e29c2822fa344f78cfb9269c1e5090a7fe7c31a` |
| `include/hammond/Types.h` | `5bf9327c4ef768f7954b160fc6f47c32534cff2c1e60b9c989a6255ddb93fc1f` |

## Next integration step and limits

Include this permanent test in the integrator's full core and wrapper regression
run. Preserve the existing default-ideal legacy tests: this suite adds console
behavior checks without replacing their old contracts. Re-run this target if
the engine, contact, percussion or control integration changes.

This assignment does not claim a full CTest run, sanitizer coverage, callback
allocation proof, benchmark result, cross-platform execution, hosted CI result,
device/host qualification or physical B-3 calibration. The larger qualification
work remains in the project status and next-step documents. No commit or push
was attempted by this delegated agent; the parent integrator publishes the
accepted combined changes.

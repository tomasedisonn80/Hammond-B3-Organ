# A49 — Final coherent Release qualification

Actual assignment **49/60**, logical wave **9**. Worker:
`/root/w09_a49_final_coherent_gate`.

## Result

Completed the requested configure, full incremental build, fresh discovery and
**one complete combined Release gate**. The gate is **146/147**, not accepted as
a complete pass. All 147 tests executed exactly once; no skip, timeout or retry.
CTest returned 8 after 525.60 seconds. The distinct failure is a workspace replay
startup-observation assertion: first copied state at 191 ms, required before the
first 180 ms sound action. All recorded source/output identities were stable.

The full [review](../../reviews/INTERFACE_FINAL_COHERENT_GATE.md),
[machine result](reports/a49-final-result.json),
[original log](reports/a49-release-ctest.log),
[original JUnit](reports/a49-release-junit.xml) and
[concrete failure handoff](reports/a49-workspace-failure.json) preserve the outcome.
The earlier UI run also remains 146/147 with its own different failure identity.
The repaired native MIDI suite passes here: twelve methods, 24 native processes,
30.47 seconds. Native workflows pass thirteen methods and 52 processes in 65.01
seconds. The remaining failure is not hidden by those passes.

## Owned work and source basis

Owned files are `docs/reviews/INTERFACE_FINAL_COHERENT_GATE.md`, this session note,
and `reports/a49-*`. A49 held the exclusive `../build-native` configure/build/test
lease. It changed no production code, fixtures, assertions, time limits, CMake
or workflow; it staged and committed nothing.

Inputs match commit `cdbb2beaa28bf136f9a8db6213819129514e2ae9`, tree
`b4d71c1f574ab17ba1a3f37b24667c1ff3f9c527`. The 327 source/test/build/workflow
inputs, 98 production inputs, 114 protected files and 31 supplemental
source/install inputs are individually hashed before and after qualification.
The production set also matches `8673713`; all protected files independently
match baseline `d493e998`. Concurrent README/gallery/docs/report edits are
identified separately from build inputs.

The 3,707,640-byte native application remains SHA-256
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2` throughout.
The full build refreshed six test executable byte identities. The rebuilt set
of 82 executables and 21 selected generated/archive/configuration outputs was
stable across all tests. No binary was added to the repository.

## Execution

Read AGENTS, current scope/session/checkpoint, the complete project plan and
relevant workspace/geometry/inspection contracts, original coherent gate and
repair closure. Reused Linux GCC 14.2, CMake/CTest 4.4.4, Python 3.12.14, SDL2
2.32.10 and RtMidi 6.0.0. Configuration was Release, standalone/MIDI ON, VST3 and
sanitizers OFF, SDL ALSA OFF and RtMidi ALSA ON. Configure verified pinned local
dependencies without acquisition. The two-worker full build completed in 3.40
seconds after the 2.13-second configure.

Fresh discovery was 147 tests. Serial CTest preserved the established native
CI policy and ordinary 60/60/30 raster and 90-second replay limits. The recorded
commands have no test filter, global timeout override or repeat option. Every
test in fresh discovery appears exactly once in JUnit; all 130 names from A40's
separate SDK-free inventory are present plus seventeen native additions. This
combined native-enabled execution does not replace that separate configuration.

## Failure and next owner

The failing method's first observation has applied/resolved sequence 3 and
submitted sequence 4. The note scheduled at 180 ms was already queued at the
191 ms copied observation. The next assertion also requires submitted==applied,
so simply widening the time bound would not establish the intended baseline.
Final raw replay is acknowledged at sequence 13 with five On/five Off and no
held notes. Later assertions after the failure were not reached and are not
reported as passes.

Retained scripts and diagnostics are extracted from original failure output;
the state copy is explicitly the exact fixture literal, not the cleaned-up
private runtime file. Root assigned A52 the independent diagnosis and fixture
repair. **CPU and build-native were released to A52 after the post-gate snapshot.**
A49 performs no rerun. A52/root must retain this original result and identify
any changed-source affected-suite qualification and incremental closure
separately.

A49 also supplied an independent
[challenge of A52's proposed startup-prefix repair](reports/a49-startup-proposal-review.json).
It found no flaw subject to identical startup inputs, a completed acknowledged
pre-shutdown baseline and all unchanged full-journey command/ownership assertions.
This is a proposal review, not repair execution or acceptance.

Physical devices/hosts, desktop capture, accessibility, deadlines, literal pixel
equality and physical fidelity remain outside this local engineering gate.

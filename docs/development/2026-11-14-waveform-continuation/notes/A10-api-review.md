# A10 — Independent R4 API, history and streaming-path review

Date: 14 November 2026. Actual assignment:
`/root/w02_a10_api_review`, wave 2, A10/60. Reviewed checkout:
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.

## Decision and scope

**ACCEPT the A07 declarations/contract and the integrator's streaming-path
source as the basis for independent implementation. No blocking contract,
ownership, clock, capacity or path-math defect was found.** The history owner
can implement `src/RotaryHistory.cpp` against the unchanged declarations.

This is source/API review plus isolated syntax checking. There was no linked
renderer, executed history behavior, independent path parity, rollback,
allocation or R4 acceptance run in this assignment. The new history and renderer
implementations did not exist when reviewed. No R5, R6 integration or physical
claim follows from this decision.

Read the standing `AGENTS.md`, complete `docs/PLAN.md`, current waveform scope,
checkpoint and actual manifest, frozen numerical contract, A07 renderer contract,
R3 propagation contract, both new public headers and streaming-path source.
Reviewed the existing motion/types/propagation sources to check that the proposed
operations are implementable using their actual semantics. Current status,
next-step/log pointers and consolidated atlas findings were consulted. This
assignment does not claim a new independent reading of all atlas pages.

The checkout HEAD and observed local `origin/main` were both
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. The reviewed new files were
uncommitted; their hashes below qualify this review. Existing concurrent files
were preserved. Only this assigned note was added; no public header, production
source, CMake, shared status, build directory or Git commit was changed.

## Findings with exact references

| Area | Review result and implementation consequence |
| --- | --- |
| Full circular orbit | `src/RotaryStreamingPath.cpp:78–103` validates the motion seed/profile/command and all geometry before publication. Its `hypot(R-a,h)`, `hypot(R+a,h)` and `a*max(original seed,slow,fast)/c` match `docs/ROTARY_NUMERICAL_CONTRACT.md:69–83`. This includes microphones horizontally inside the orbit: `hypot` correctly takes the magnitude of `R-a`; no replacement by a clipped nonnegative radius difference is needed. |
| Signed geometry and solver | `src/RotaryStreamingPath.cpp:142–158` uses the existing circular helper, receiver-minus-source displacement, positive-toward-receiver radial speed, derivative `1-radial/c`, reciprocal frequency ratio and reference-distance pressure gain. `:168–201` keeps the R3 32-ulp bracket, endpoint sign checks, cached selected evaluation, 48 total geometry evaluations, `1e-14` early target and `1e-11` success residual. These agree with `src/RotaryPropagation.cpp:250–310` and the frozen R3 contract. |
| Split clock arithmetic | `src/RotaryStreamingPath.cpp:32–64` subtracts only bounded local delay frames, with checked integer subtraction and fractional borrow/carry. It never forms a large floating sample index. The upper delay guard of 13,000 frames contains the admitted maximum of 12,800 plus roundoff padding. All epoch frames fit signed 64-bit conversion: the largest supported epoch is 16,588,800,000 frames. |
| Path/history compatibility | `src/RotaryStreamingPath.cpp:120–139` requires preparation, exact motion-profile equality and an epoch seed within the original admitted speed envelope, then admits observation and every evaluated emission through the history. A stopped rate epoch or reset does not require weakening the original Mach bound. Both output destinations are published only at `:200–201`. |
| Cubic endpoints | `include/hammond/RotaryHistory.h:19–26,45–51` and `docs/ROTARY_RENDERER_CONTRACT.md:94–109` distinguish the standalone closed fraction interval `[0,1]` from canonical `SamplePosition` fractions `[0,1)`. Exact endpoint selection is permitted only after all four support values are admitted. Zero-weight missing nodes still reject. This preserves the frozen `j/256`, `j=0..256` characterization. |
| Retained trajectory | `include/hammond/RotaryHistory.h:64–93` and `docs/ROTARY_RENDERER_CONTRACT.md:63–89` retain a complete original event segment for each interval. An original command anchor can precede the oldest retained frame; evaluating the retained segment must still use that anchor. This avoids block-dependent reanchoring and removes R3's unrelated finite-fixture event cap without unbounded event storage. |
| Continuity and final endpoint | At append frame `n`, compare the preceding interval's native evaluation at `n` with the owner's current state, then admit the new segment at `n+1` before mutation (`docs/ROTARY_RENDERER_CONTRACT.md:66–72`). Existing `RotaryMotion::advance_to/apply_command` evaluate from their retained original anchor (`src/RotaryMotion.cpp:326–357`), so exact native state equality is implementable. At the final boundary only fraction zero is covered; the previous segment gives the correct continuous physical state even after new commands at that boundary. |
| Negative history and silence | Negative waveform indices inside the signed epoch are declared zero; negative motion always uses the epoch seed and constant seed speed. Empty positive motion history admits only `{0,0}`. Never use a later accelerating segment for negative time and never replace an unavailable nonnegative sample with zero (`docs/ROTARY_RENDERER_CONTRACT.md:53–89`). The cubic can use nonnegative support while its emission coordinate remains negative; that is the frozen finite-support operator, so a test must compare the specified cubic rather than impose a separate step-function output-silence rule. |
| Capacity and explicit tail | The common `H=D+6`, `flush=D+4` rule at `docs/ROTARY_RENDERER_CONTRACT.md:143–159` is sufficient, including bracket padding; the reasoning is below. Primitive capacities as small as one remain useful for isolated retirement tests; the renderer's geometry-derived capacity is larger. |
| Whole-call rollback | The journal contract at `docs/ROTARY_RENDERER_CONTRACT.md:248–278` records every overwritten slot before any of the four writes and replays records in reverse. This handles `N>H`, partial append failure and repeated overwrites of one slot. Restoring all four prior counters separately, and keeping physical owners/diagnostics staged, is sufficient. Inactive scratch is explicitly unobservable; retained slot data are not exempt. |
| Reset and stopped rate change | `include/hammond/RotaryRenderer.h:123–128` and `docs/ROTARY_RENDERER_CONTRACT.md:290–312` agree with the frozen lifecycle. Existing motion copies retain their original reset seed: `src/RotaryMotion.cpp:369–393` resets to that seed at the current rate, while reconfiguration preserves current physical state/turns/command and starts a new epoch. Candidate renderer storage must preserve these owner copies rather than call fresh `prepare` with the current state and accidentally replace the original reset seed. |
| Admission and publication | The preflight order at `docs/ROTARY_RENDERER_CONTRACT.md:194–205` is concrete and preserves the numerical contract. Byte-range arithmetic must be checked before overlap comparison; inputs may overlap, outputs may not. Offset-N commands, following offset-zero commands, unchanged commands and successful zero-frame diagnostics are specified without a partition-dependent counter (`:207–228`). No fallible work may follow publication (`:263–270`). |

## Capacity and tail reasoning

Let `D=ceil(Fs*rmax/c)` and let `B` be the upper padded bracket in frames.
Within the admitted domain, the 32-ulp distance padding contributes less than
`7.3e-11` frames at 192 kHz; the remaining arithmetic roundoff is also far below
one frame. Therefore `B<D+1` even if the unpadded maximum is an exact integer.

After writing input frame `n`, the common ring has `next_frame=n+1` and, after
wrap, `oldest=n+1-(D+6)=n-D-5`. Observation is `n-2`. The earliest bracket
emission has floor at least `n-D-3`, and its oldest cubic node is at least
`n-D-4`, still inside retained storage. Because every admitted delay is strictly
positive, the latest emission floor is at most `n-3`, so the newest cubic node
is at most `n-1`, already written. Negative support uses the declared startup
zeros. Motion queries need no older floor than the waveform support bound.

After the final nonzero-input region ends at frame `N-1`, explicitly processing
`D+4` zero frames leaves the following input frame at `n=N+D+4`. Its earliest
emission is greater than `N+1`; every cubic support then has index at least
`N`. All remaining original audio influence has therefore been covered by the
flush. Motion still advances, and the flush consumes ordinary epoch frames.

## Required implementation checks, without widening the frozen gate

These are acceptance obligations already present in the contracts, highlighted
for the next owner rather than new optional test work:

1. Check fraction validity and signed epoch bounds before coverage. Admit
   `{-max_frame,0}` and `{max_frame,0}` as position endpoints where applicable;
   reject `{max_frame,positive_fraction}` with `TimelineOverflow`. An unavailable
   in-epoch nonnegative sample/query is `InsufficientHistory`. A waveform query
   for the final boundary is not an invented sample. Checked cubic support
   arithmetic and each support's epoch bounds still apply at either extreme.
2. At `next_frame==max_frame`, reject another push/append; admit zero-frame
   renderer commands without advancing histories. At capacity one, evaluate the
   previous interval's boundary before overwriting its only slot. At larger
   capacities, retain original anchors after their original slots retire.
3. Keep complete support admission at exact cubic endpoints. Preserve every
   destination on primitive failure. For transaction tests use field-level
   bit comparisons or actual slot-byte comparisons as prescribed; default
   floating `operator==` alone cannot distinguish signed-zero changes.
4. Reconfigure to the same rate as a real new epoch; preserve current physical
   state and commands, replace negative motion seed, clear audio/diagnostics,
   and retain the original reset seed. Invalid/allocation-failed replacement
   must preserve the working renderer. Then verify reset after reconfiguration.
5. Qualify the streaming solver against the independent reference once history
   exists. Its deliberate similarity to R3 is not an executed numerical result.

No separate review test-spec file was needed: the frozen renderer contract and
independent acceptance assignment already own those tests.

A11 also requested a focused review of signed-zero seeds during an empty
zero-frame call. No issue was found: `evaluate_motion_segment` returns the
initial state verbatim at zero elapsed time (`src/RotaryMotion.cpp:195–197`),
and `evaluate_split` returns that state when the remaining fractional time is
zero (`:137–139`). Re-evaluating an unchanged original anchor at the same frame
reproduces the boundary state; a newly anchored segment at that frame returns
its exact initial state. This is source reasoning, not a separate executed R2
test. The existing requirement to compare double fields by bits remains useful.

## Actual verification and retained source identity

Toolchain: `c++ (Debian 14.2.0-19) 14.2.0`. Working directory for commands:
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.

- Header inclusion syntax check with
  `c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -Iinclude -x c++ -fsyntax-only -`
  passed, exit 0, with both headers included and compile-time assertions that
  the histories are copy-constructible and the renderer is neither copy- nor
  move-constructible.
- `c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -Iinclude -fsyntax-only src/RotaryStreamingPath.cpp`
  passed, exit 0, with no diagnostics.
- An earlier invocation incorrectly supplied the headers themselves as primary
  translation units. It exited 1 solely because GCC warns about `#pragma once`
  in a main file and `-Werror` promoted that warning. The ordinary-include
  invocation above corrected the check setup; no product change was needed.
- No linked runtime test, CMake invocation or shared build ran. No temporary
  build artifacts were created in the repository.

SHA-256 values of the reviewed inputs:

| File | SHA-256 |
| --- | --- |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `docs/ROTARY_PROPAGATION_CONTRACT.md` | `0834909ad8ea4b2b9696f0047d739d03976da3adb4a2eb48f2b7556737bccdcc` |
| `docs/ROTARY_RENDERER_CONTRACT.md` | `a1c8e94c2d76ccad784400a1276a7717d9e4c100e4104db2c4b13d65d33a3caf` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| `src/RotaryPropagation.cpp` | `dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e` |
| `src/RotaryStreamingPath.cpp` | `ed79d6ce3653f52f5f9a7d43d4f5cf9743f18cc3c9458ee7734928e42dcbae50` |

Next concrete action: accept/freeze this API through the integrator, implement
the assigned history and renderer files, then execute the independent frozen
history, propagation and whole-call acceptance cases on their exact source.

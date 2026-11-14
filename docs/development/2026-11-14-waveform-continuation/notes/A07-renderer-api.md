# A07 — R4 streaming API and transaction contract

## Assignment and inspected source

- Actual worker: `/root/w02_a07_renderer_api`; wave 2; 14 November 2026.
- Initial inspected HEAD: `2e161dc3a60fc3442051799574feed37bffbfc5c`.
  The integrator concurrently reconciled the preceding session; final observed
  HEAD during this assignment was `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`.
- Workspace: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
- Read the standing agent rules, current scope/checkpoint/actual manifest,
  complete M0–M9 plan, A04 rotary reading, numerical contract, R3 contract and
  implementation, R4 propagation handoff, renderer review brief, and existing
  `RotaryTypes`, `RotaryMotion` and `RotaryPropagation` declarations/source.
- Owned only `docs/ROTARY_RENDERER_CONTRACT.md`,
  `include/hammond/RotaryHistory.h`, `include/hammond/RotaryRenderer.h` and this
  note. No shared records, existing rotary code, Engine/state/parameters, build
  configuration, commits or nested workers were changed by this assignment.

## Concrete frozen proposal

The two new headers and `rotary-renderer-v1` contract form a stable API proposal
for integrator acceptance and independent review. They preserve the unchanged
`rotary-numerics-v1` domain, budgets and source boundary.

1. `WaveformHistory` owns a bounded double ring and the complete four-node cubic
   read. Its standalone pure kernel admits closed fractions `[0,1]`, so the
   required `j/256` final endpoint selects `x[k+1]` explicitly. Canonical
   `SamplePosition` queries continue to use `[0,1)`.
2. `MotionFrameHistory` owns one **original event-anchored segment** per retained
   integer interval. No block/sample reanchoring occurs. Every later retained
   copy keeps the original anchor even after its old slot retires; lifetime
   event count does not consume a growing queue. Negative motion uses the epoch
   seed, while negative audio is zero.
3. `PreparedStreamingPath` owns admitted rate-independent geometry and borrows
   a compatible streaming history only during `solve`. The immutable R3 API
   and qualified source stay unchanged. Its 48-evaluation budget and all root
   arithmetic conventions remain frozen.
4. `RotaryRenderer` owns a heap-allocated prepared storage object, both motion
   owners/rings, four paths, output scratch and one undo record per written
   frame. Full history arrays and backups must not be stack locals.
5. A bounded reverse journal replaces whole-bank copying: each record captures
   both overwritten samples and both overwritten original segments before any
   write. Reverse replay plus saved ring clocks recovers all physical history
   bytes even when one call wraps a small ring repeatedly. Owners/diagnostics
   remain staged until commit. Only invisible output/journal scratch is excluded
   from persistent-state equality; it cannot affect later accepted output.
6. Copied state/diagnostics, exact buffer/event/status admission, offset-N/next-zero
   ordering, zero-frame commands, reset, same/different stopped rate epochs,
   declared silent replacement history and explicit tail length are specified.
   Dry Engine, all 47 parameters and state4/readers 1–3 stay unchanged.
7. A narrow undefined-in-production `detail::RotaryRendererTestAccess` friend
   permits a dedicated test to corrupt one later-read retained slot, prove an
   actual late failure after earlier samples, verify complete rollback, restore
   the fixture and compare accepted continuation with an untouched control.
   There is no shipping public error-injection control.

## Non-overlapping implementation ownership

| Owner | Files and boundary |
| --- | --- |
| History implementation | `src/RotaryHistory.cpp`: cubic kernel plus both history types |
| Streaming path implementation | `src/RotaryStreamingPath.cpp`: the new path only, with existing motion/geometry helpers |
| Renderer implementation | `src/RotaryRenderer.cpp` and private `src/RotaryRendererInternal.h`: storage, lifecycle, admission, events, journal and publication |
| Independent acceptance | Separately assigned history/cubic, transaction, partition/event, same-cubic oracle, lifecycle/symmetry and allocation fixtures |
| Integrator | Contract acceptance, CMake/shared records, coherent builds and publication |

The integrator reported starting and separately compiling the streaming path
against these stable signatures during this assignment. That source and compile
belong to the integrator, not this worker's implementation or verification claim.

## Actual checks and limits

No configure, compile, build or test was run by A07, as assigned. This is a
source/design deliverable. The earlier **155/155** baseline predates these new
headers and cannot qualify R4. `git diff --check` returned success for the
current tracked diff; a separate Python scan verified every new owned header/
contract has final LF and no trailing whitespace. Read-only `git status` and
`git rev-parse HEAD` confirmed the source identities above.

The direct command for the new-file formatting/identity check was Python 3
`Path.read_bytes()`, `splitlines()`, trailing-whitespace assertions and
`hashlib.sha256`, from the workspace root. Stable proposal identities:

| File | SHA-256 |
| --- | --- |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `docs/ROTARY_RENDERER_CONTRACT.md` | `a1c8e94c2d76ccad784400a1276a7717d9e4c100e4104db2c4b13d65d33a3caf` |

Next: independent API/transaction reviewers and integrator accept or identify a
specific defect before implementation owners complete their files. Then build
coherent source with the session's reused CMake executable
`/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake` and sibling
`../build`, under integrator coordination. Execute every unchanged R4 acceptance
experiment, including all-rate ten-second same-cubic references and prescribed
partitions. R5 audible policy, R6 runtime/device integration and physical M7
remain separate and unpassed by this proposal.

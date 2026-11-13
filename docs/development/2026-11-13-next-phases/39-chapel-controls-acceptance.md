# Assignment 39 — independent chapel control acceptance

Actual agent `/root/w07_a39_chapel_controls_acceptance`, wave 7, assignment 39
of this session's sixty assignments. A resumed worker turn continued this same
assignment; it was not counted as another agent. Owned only the SDK-free test,
native test, [acceptance guide](../../CHAPEL_CONTROLS_ACCEPTANCE.md) and this note.
No producer, Engine, CMake, shared status/ledger or commit edits were made.

Read AGENTS, active scope/status/next steps/plan, B3CONTROLS3, source-B review and
catalog/compiler contracts. This acceptance uses the independently reviewed
atlas p122 import; it did not acquire factory Table IV or inspect a specimen.
Starting published HEAD was `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`, with concurrent worker changes.
Relevant file and executable hashes below identify the tested artifacts; that
starting revision alone does not identify the full changing worktree.

## Implemented checks and actual outcomes

Python **3.12.14**, Linux; native runtime **SDL 2.32.10**, dummy video/audio.
All commands ran from `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Each suite generated its own private 4,837-byte catalog through the compiler,
checked its complete expected hash, and preserved all repository source inputs.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_controls.py -v
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5ba97739b54c/build-native-app/apps/standalone/hammond_standalone \
  PYTHONDONTWRITEBYTECODE=1 python3 apps/standalone/native_tests/test_standalone_chapel.py -v
```

| Maintained suite | Executed result |
| --- | --- |
| SDK-free exporter acceptance | **15/15 methods pass**, 15.461 s, exit 0; 270 exporter CLI calls, 205 matrix/expression exact-state cases, 264 API rejections, six publication fault/race probes; no skips on this Linux host. |
| Final native acceptance | **2/2 methods pass**, 17.613 s, exit 0; 20 exported states and 20 actual SDL application runs; all eighteen registrations plus two pairs; no skips. |

The 205 state counter covers 198 possible manual/off combinations across both
banks plus seven literal expression vectors. Defaults, equals syntax, Unicode
paths, exact input-size boundary and public-writer success have additional checks.
All 162 individual tap mutations reject even after their canonical hash is
recomputed. Wrapper/semantic/type/hash, CLI, malformed-file, alias and publication
failures preserve complete fixture snapshots. The raw authoring hash/count
trust boundary is explicitly tested as metadata shape, not absent-byte proof.

Native checks compare literal controls for every observation, positive/zero
finite audio peak as applicable, exact accepted note counts and target ownership,
release/final acknowledgment, no fault/error/recovery/overflow, and preserved
catalog/script bytes. Save runs while notes are held and emits only controls.
All twenty cases require observed successful Save status and independent output
bytes. The paired expression case also proves C++ rewrites accepted `0.1` input
to canonical `0.10000000000000001`; it cannot pass merely by retaining its input.

The initial native candidate also passed 2/2 in 17.941 s. Inspection then found
that byte equality on already canonical input alone did not prove Save executed;
the status and noncanonical-input assertions strengthened that oracle before the
final run. No exporter/native functional test failed and no producer changes
were needed. An auxiliary missing-executable probe correctly failed in setup
with exit **5** and no skip. Its first probe driver incorrectly expected exit 1;
changing that auxiliary assertion to require nonzero confirmed the contract.
The maintained suite and production code were unchanged by that probe correction.

Logs are retained locally as `../a39-sdk-first.log`, `../a39-native-first.log`,
`../a39-native-final.log`, and `../a39-native-missing-prerequisite-confirmed.log`.
These scratch logs complement the maintained tests; this record is the durable
result summary. No host, physical-device or future-platform pass is inferred.

## Exact qualification identities

| Artifact | SHA-256 |
| --- | --- |
| `tests/test_chapel_controls.py` | `cd9efb682df350ea8abfdb0e3005ee26502632c733708be25f06680ad24ca62f` |
| `apps/standalone/native_tests/test_standalone_chapel.py` | `87c70cab4632558c9d92308820475322f6421ef06b427b2a93590ba85a36cb6d` |
| Exporter | `dc390c74ac9af31322d73a116dfd61cd353c6e2ee309a7871c571bca1c3904a8` |
| Compiler/public authoring validator | `fcfdb3342478d8a4369f1080d234515c59a87a0094db522c1f44a8e7ddd61210` |
| Compiled catalog, 4,837 bytes | `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91` |
| Raw authoring, 4,298 bytes | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| Canonical authoring semantics | `ebed39e9b73a0479b7493ce1d5fce1f3309f4c0663981144263877b8ca74dd1b` |
| Each frozen review CSV, 466 bytes | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |
| Native `main.cpp` | `560f3f12cd0b9a081748d601ec8ad42c69b4e73b3d68ab6d583e4d5e9be1ea88` |
| Actual native executable | `7377e8c2c146636ef3b4ca28891d257bbfcc9db8b6f42caa257b6857d97d9925` |

Worker 38 froze the exporter before qualification. Worker 37 and root froze the
native executable and main source before native execution; the suite rechecked
binary and relevant source bytes afterward. Root concurrently integrated additive
rotary/calibration work into a separate build. This worker's result attaches to
the listed executable and relevant inputs, not untested claims about that merge.

## Integration handoff and remaining gates

The SDK-free suite is discovered as `python_test_chapel_controls`. Root registered
the separate `test_standalone_chapel` native CTest with a 90-second timeout.
Root owns actual assembled CTest results, refreshed integration identities,
shared handoff/ledger updates and commit/push. Those follow-up results must be
recorded separately from this worker's direct commands; no canonical CTest run
is claimed here. Rebuild the configured native test inputs before the root gate.

Keep [CHAPEL_CONTROLS.md](../../CHAPEL_CONTROLS.md)'s exact grammar, metadata trust
boundary and hardlink publication limits when continuing. Acquisition of primary
Table IV/specimen wiring and measured loaded tap gains remains open. A future
physical preset selector needs a separately reviewed latch, percussion-interlock
and state/runtime contract under [M3](../../M3_REMAINING_AND_SCANNER_GATE.md).
These tests qualify copying documentary digits to the nominal dry Engine; they
do not demonstrate factory timbre, physical latching or calibrated fidelity.

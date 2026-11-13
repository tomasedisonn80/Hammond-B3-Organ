# Assignment 36 — independent chapel catalog acceptance

Canonical worker `/root/w06_a36_chapel_acceptance`; wave 6, assignment 36 of the
current sixty-assignment session. Owned only `tests/test_chapel_presets.py`,
`docs/CHAPEL_PRESETS_ACCEPTANCE.md` and this note. No production, CMake,
shared-status, ledger or source-fixture edits; no commits by this worker.

Read AGENTS, active project/status/next-step/scope evidence, the relevant M3
contract and both independent chapel source guides. The literal test rows and
physical position order were taken from reading B and its source guide, not
producer constants. Agent34 froze the public compiler/output contract before
the suite was run. Its raw-byte CSV lock, authoring formatting freedom, writer
precondition and JSON Schema-versus-token semantics were explicitly confirmed.

## Exact inputs

CWD `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`. Starting and final HEAD
was `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`. Concurrent uncommitted work exists;
the following frozen file identities define this narrower qualification.

| Input | SHA-256 |
| --- | --- |
| `tools/compile_chapel_presets.py` | `fcfdb3342478d8a4369f1080d234515c59a87a0094db522c1f44a8e7ddd61210` |
| Authoring JSON | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| Declared schema | `07676c32411b34a4c8b683f251a2f3599a1ef19d294fa2bcc03551a933e2decd` |
| Each independently frozen CSV | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |
| Maintained acceptance suite | `02d548ff5b78066aed8e27d66250232379e986da3d266349c7f4948f9b897536` |
| Default emitted catalog | `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91` |

Authoring is 4,298 bytes; each reading is 466 bytes; default output is 4,837
bytes. Canonical authoring SHA-256 is
`ebed39e9b73a0479b7493ce1d5fce1f3309f4c0663981144263877b8ca74dd1b`.
The declared PDF identity remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
This worker did not repeat the complete PDF review or verify factory Table IV.

## Actual execution

Linux x86_64; Python 3.12.14; CMake/CTest 4.4.4. Commands from the repository
root (CMake is not on this container's default PATH):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_presets.py -v
cmake_bin=/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin
"$cmake_bin/cmake" -S . -B ../build-chapel-acceptance-a36 -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
"$cmake_bin/cmake" --build ../build-chapel-acceptance-a36 \
  --target hammond_profile --parallel 2
"$cmake_bin/ctest" --test-dir ../build-chapel-acceptance-a36 \
  -R '^python_test_chapel_presets$' --no-tests=error --output-on-failure -V
```

The direct run passed **18/18 methods in 6.051 seconds**. Fresh configuration
and profile build exited zero; canonical CTest passed **1/1 in 6.39 seconds**
(6.40 seconds total; Python 6.227 seconds). Each run executed **111 actual CLI
processes, 234 public-API rejection cases and five injected I/O failures**,
with no skipped methods or unexpected failures. No test or producer repair was
needed. Root separately ran its assembled catalog target and canonical gate;
that independent integration result is outside this worker's execution count.

## Independent checks and findings

The [maintained contract](../../CHAPEL_PRESETS_ACCEPTANCE.md) lists the complete
matrix. Literal comparisons cover all eighteen key/manual identities and all
162 tap digits, including all sixteen leading-zero strings and null names.
Every tap position is separately changed to a different legal 0–8 digit and
rejected; range-only validation cannot pass that test. All nine footage/color
positions and source/evidence/limitation values are independently checked.

Malformed JSON/CSV, duplicate members, wrong scalar/container types, relabeled
evidence, incomplete/reordered matrices, ambiguous rows and frozen-byte changes
reject. Valid authoring at exactly 65,536 bytes succeeds with correct raw and
canonical identities; larger authoring and both oversized review inputs reject.
Schema declaration checks cover every required field, closed object and ordered
constant; they do not substitute a custom validator for full JSON Schema.

Real private symlink, dangling-link, hardlink, parent-alias, directory, FIFO and
Unicode/space-path fixtures executed. Each rejected CLI call preserves the whole
fixture's entries, modes, bytes and inodes. Publication probes inject creation,
short-write, flush, fsync and replace failures while using real temporary files
for the surrounding operations; prior output survives and owned temporary files
are removed. Both successful runs rechecked all five repository input bytes.

## Handoff and limits

Root owns coherent publication and shared status. The next useful consumer is a
separately qualified nominal control-state/export or selector boundary; this
catalog does not implement physical preset latches, change 45 parameter IDs,
alter saved formats or select a gain law. Do not promote two atlas readings to
an independent factory Table IV review. Windows/macOS execution, hostile file
races, power-loss durability, specimen continuity, loaded gains and physical
percussion transitions remain unqualified. No native/device/audio pass follows
from this offline catalog gate.

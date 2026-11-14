# Capture replay and installation integration

## Accepted result and exact source

The immutable combined source passes **103/103 unfiltered SDK-free Release
CTest suites in 197.85 seconds**, with successful configuration and compilation.
This qualifies the accepted report replay, 57-file CaptureTools package and
Windows demo preservation-fixture repair together with the existing core and
offline workflows. It preserves the concurrent standalone advance `183fc9e`.

| Identity | Value |
| --- | --- |
| Local frozen commit | `16d72e1b351e5cdf1730e90645a6ea37144d1be7` |
| Exact Git tree | `5619bbb018830e071bc2ce45af84984cdd16bfc1` |
| GitHub equivalent source commit | `7caee9e5a1aadfa36f2a87b6855684cbd730d803` |
| Integrated remote parent | `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e` |
| Frozen archive | `/workspace/scratch/c9f3ead4c910/w7-installed-source` |
| Separate build | `/workspace/scratch/c9f3ead4c910/w7-installed-build` |

The local and GitHub source commit identities differ because publication uses
the authenticated GitHub connection; their complete Git trees are equal. The
source object is retained separately from the later documentation and review
checkpoint. Its manifest records 39 accepted assignments and 42 dispatches;
later acceptance of assignments 40–42 does not retroactively alter that frozen
record or the code tested here.

## Configuration and execution

The observed toolchain is Linux x86_64, GNU C++ 14.2.0, CMake/CTest 4.4.4 and
CPython 3.12.14. The executable used for CMake was
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`, with
the sibling `ctest`. Python was
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`.
The gate used a fresh archive and separate build directory, not old objects
against live edited headers. Its reproducible command form is:

```sh
git archive 16d72e1b351e5cdf1730e90645a6ea37144d1be7 | tar -x -C /existing/empty-source
cmake -S /existing/empty-source -B /existing/new-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /existing/new-build --parallel 2
ctest --test-dir /existing/new-build --output-on-failure --no-tests=error --output-junit /existing/new-ctest.xml
```

The retained actual run used the archive/build paths above. All 103 CTest entries
passed; the JUnit result has zero suite failures, disabled entries or skipped
entries. That does not mean every nested Python capability-dependent subcase
ran: audio admission retains two explicitly disclosed capability skips in this
Linux environment. CTest suites, unittest methods and individual assertions are
different counts. The concurrent corpus Unicode regression makes its admission
suite 59 methods; audio admission is 63 methods including those two skips.

| Retained scratch evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `checks/w7-installed-configure.log` | 707 | `526d8b3485fed34d81004d861189571b6c6b5f444ee9957013f76badb3f61ccb` |
| `checks/w7-installed-build.log` | 12,141 | `09f9410965c772fbaacf6761fddf1fc6229702f7cf98ef840e5f08336e36c64a` |
| `checks/w7-installed-ctest.log` | 13,381 | `8929c148a111ddaf224ab70fcdde81ea5a15476aca550fabe51da7aefea3642c` |
| `checks/w7-installed-ctest.xml` | 51,419 | `a61e95fe21257ce677d38f7d6f0cb3d4d26b7ef3536c5ea507fdbc446ea1fe26` |

Scratch evidence paths are relative to `/workspace/scratch/c9f3ead4c910` and are
not repository download links. This durable report retains their identities,
commands, outcome and scope; the independent component notes retain the detailed
methods, initial failures and relevant source identities.

## Included behavior and independent evidence

- [Replay acceptance](../CAPTURE_REPLAY_REVIEW.md) passes 69 methods. A complete
  canonical report is freshly recomputed and compared byte for byte. A matching
  replay can retain a failed or inconclusive engineering outcome.
- [CaptureTools installation](../CAPTURE_INSTALL_REVIEW.md) passes 16
  methods, including all 57 missing-source preflights, component isolation,
  Unicode relocation, deletion of private source/build directories, installed
  standard-library-only execution and four complete replays. Existing
  OfflineTools remains a separate 23-file component; its two-method suite passes.
- The demo's 43-method suite includes the root fixture repair for Windows native
  symlink-target spelling. It compares the observed target before and after the
  rejected operation, preserving both link-presence and absent-target checks.
  Production generation was unchanged. Its exact test SHA-256 is
  `2ebc86c18997da96b4d70894ca193949d77de7ade68655e4ae4cfcad2ef0904d`.
- The merge retains the separately owned standalone chapel work and the added
  corpus Unicode diagnostic regression from `183fc9e`. The only development-log
  insertion conflict preserved both full histories.

The separately accepted [composition review](CALIBRATION_COMPOSITION_CONSISTENCY.md)
passes 220 finite audit cases against an actual installation with matching
package source identities. The [resource profile](CALIBRATION_RESOURCE_PROFILE.md)
retains twelve cases, all 36 ordinary timing samples and separate traced
allocation observations. The [accounting review](CALIBRATION_ACCOUNTING_AUDIT.md)
retains its two historical counts and twelve focused consistency checks. These
are independent evidence, not extra CTest suites or additional workers.

## Limits and continuation

The [actual hosted review at `955fc4c`](CALIBRATION_HOSTED_RECHECK.md) retains
nine successful jobs and one Windows Release fixture failure. That older source
does not include replay or the new package. The local repair and this Linux gate
do not establish a new Windows or macOS result; observe fresh hosted jobs after
publication and preserve their exact source and outcomes.

The frozen corpus source here is SHA-256
`1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba`.
Assignment 43's later metadata-allocation optimization and assignment 44's new
acceptance are excluded from this gate and await independent qualification.
The profile exposed a concrete allocation mechanism; it did not establish a
latency guarantee, resident-memory ceiling or native real-time safety.

No native VST3 or SDL application target was enabled in this local gate. No
physical instrument, recording permissions, acquisition calibration, holdout
chronology, model fitting or fidelity claim is established. Continue the actual
remaining assignments, integrate inspected concurrent changes, verify affected
coherent sources and publish under the standing non-force workflow.

## Inspected concurrent advance before publication

Main subsequently advanced to `6214032f3565f9e221fcf3988e33a22a73bb4ea8`.
Root inspected its two changed files: native workflow endpoint acceptance and
an independently strengthened version of the same demo symlink fixture. The
merge preserves its actual initial link target and adds unchanged link-stat
checks. The native tests retain their owning track's scope; this calibration
integration does not claim a fresh native executable run.

The merged archive `0f41ccc6e61a97f6646b8612b50b14ea287dc447`, tree
`55816e41c27f03de689e5ace2b8d45ef88b3c8ae`, passed the actual command
`python3 -B /workspace/scratch/c9f3ead4c910/w7-publish-source/tests/test_capture_demo.py`:
**43/43 methods in 1.519 seconds, no skips**. The strengthened test is 39,162
bytes, SHA-256 `a0b5ed53d59ef91e224d477b5996ca1f7f594d8f3d4a7592559e0352bba03112`.
No capture production code changed between the full 103-suite snapshot and this
merge. The later documentation-only publication record is a separate commit;
the full gate remains attributed to its exact earlier source tree.

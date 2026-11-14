# A49 — Coherent final native build and full registered CTest

Actual worker `/root/w09_a49_coherent_final_build`, wave 9. The **single
all-target build passed**, and the **single full registered CTest execution
passed 157/157 in 146.97 seconds**. There was no product/test failure, repair,
filtered recheck or second full run. The build took 11.381 seconds. The
[readable result](../reports/A49-coherent-final-build.json),
[original CTest output](../reports/A49-ctest-original.log),
[complete per-test output](../reports/A49-LastTest.log) and
[artifact manifest](../reports/A49-artifact-manifest.json) retain the exact
commands, raw outcomes, identities and limits.

## Source and actual input closure

Read AGENTS, the complete M0–M9 plan, current checkpoint/concurrent handoff,
previous coherent result and A38–A41 acceptance before running. Root assigned
exclusive ownership of the existing `../build-native` tree. Its product, test,
tool, data and build-source inputs matched published commit
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`. The checkout also contained accepted,
partly uncommitted documentation and v4-gallery work. This is not a clean
worktree claim or a claim that every tested document already belonged to that
published tree.

Inspection found that `python_test_repository_integrity` checks actual live
Markdown and local link targets. `test_standalone_install` installs and checks
six guide files, including A47's updated `INTERFACE_RUNBOOK.md`, and the notices
and atlas provenance. CaptureTools installation checks its twenty-one named
documents and complete fixed payload. Other registered fixtures read scanner,
rotary and capture contracts, factory-reading notes and v3 diagnostic JSON.
The checker regression suite uses private synthetic session records; its pass
does not close the actual sixty-worker ledger.

Root coordinated a whole-repository freeze after A47 finalized its five files;
A50 and A51 kept their concurrent work outside the checkout. All A49 logs and
inventories remained outside the repository until post-run hashes completed.
Before build, after build and after CTest, all **2,625 recorded repository
files**, including **912 Markdown files**, were byte-identical. All **368
recorded product/test/build-source files** matched the published Git blobs.
All **1,758 SDL2 files** were unchanged. Snapshots exclude Git internals and
Python bytecode caches; those exclusions and the already-dirty status are
explicit. The complete snapshots are retained losslessly as three gzip files,
with compressed and original SHA-256 identities in the result. The post-build
executables, generated inputs and install/test configuration were unchanged
through CTest. This evidence does not claim a hermetic operating-system image.

## Configuration, commands and observed coverage

Working directory was
`/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`. Reused GCC 14.2.0 Release
with `-O3 -DNDEBUG`, CMake/CTest 4.4.5, Ninja
`1.13.2.git.kitware.jobserver-pipe-1`, Python 3.12.14 and pinned SDL2 2.32.10
at `5d249570393f7a37e037abf22cd6012a4cc56a71`. Standalone and testing were ON;
MIDI, VST3 and sanitizers were OFF. No dependencies were downloaded and no
additional permanent build tree was created. This was an incremental
all-target build; its normal dependency-triggered regeneration refreshed the
install metadata and rebuilt the changed header consumers.

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --parallel 3
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release --show-only=json-v1 --no-tests=error
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error --parallel 3
```

Discovery actually returned 157 tests. The retained original result contains
157 distinct passing completion rows and 157 passing detailed records. Its
material fixture reports **1,071 checks, zero failures**, retaining 901 legacy
checks plus 170 header assertions. The new checker and capture-validator
fixtures pass twenty and seven Python methods respectively. The repaired
allocation fixture passes all 82,320 observed queries with zero allocations
and frees in its measured intervals. CaptureTools installation passes sixteen
methods; actual repository integrity passes forty-one methods.

The native executable SHA-256 is
`7945754c1551a0c3c143c7b180cb2ef1ab74da9981bb7901c8724f46bbf8eb0b`.
Its MIDI-OFF configuration differs from A46's gallery executable. Cache SHA-256
remained `3d8d1b65a436e297c3f755fd43fe7160c4d71d03f563b3c3c5e00419ca337e2c`.
All three command-output logs are complete within their eight-MiB bounds; the
entire retained A49 run bundle is approximately 1.78 MB before this note and
its small manifest.

## Historical observations, limits and handoff

The earlier full **154/155**, followed by the distinct repaired installation
**1/1**, remains unchanged in `coherent-result.json`. CTest left an inherited
`LastTestsFailed.log` naming capture installation, timestamped 21:06:49 UTC,
before A49 began. Its exact bytes are retained under an explicitly inherited
filename; it is not a failure in the new full run. CTest 4.4's shorter success
wording needed an offline reporting-parser adjustment. Reading one mixed
installation-output line as standalone JSON also failed during report
assembly; restricting extraction to the two named JSON fixtures corrected
that reporting issue. Neither operation changed or reran any test.

The repository freeze and native-build ownership were released to root,
A50 and A51 immediately after the final snapshot at 22:23:12 UTC. Only owned
A49 evidence was then added. Those new artifacts and this note are outside the
earlier Markdown snapshot. No standalone sanitizer, timing campaign, GUI or
gallery-capture run was performed; ordinary registered suite fixtures retain
their existing dummy-driver workflows and benchmark smoke coverage. This
result supplies no new MIDI-enabled, VST3, physical-device, accessibility,
audio-deadline, hosted-sanitizer, visual-equality or physical-fidelity claim.
Scanner G5 and unconnected rotary/Engine boundaries remain as recorded.

Next, root should review and accept this evidence, finish the remaining actual
assignments and their source-specific hosted/gallery qualifications, then check
the final documentation and execute the strict refinement checker against the
completed sixty-record manifest. Publish the accepted coherent records under
the existing authorization. A49 makes no source, configuration, workflow,
manifest, shared-documentation or publication change.

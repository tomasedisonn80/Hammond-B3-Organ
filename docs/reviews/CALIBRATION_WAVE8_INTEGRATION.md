# Combined calibration integration through wave 8

## Result and source identity

The immutable combined source configures, builds and passes **106/106 unfiltered
SDK-free Release CTest suites in 192.51 seconds**. This includes all accepted
capture production changes through the first eight logical waves, the new graph,
metadata-read and real-pipe suites, the root Windows installation-fixture repair,
and explicit binary classification of raw float32 artifacts.

| Identity | Value |
| --- | --- |
| Local frozen commit | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` |
| Exact complete Git tree | `3edea0838b75feb06c19e151ec8539e80646fc03` |
| Equivalent GitHub source commit | `5e19022c8696023bb1aa841ebea2eaeec0d719a3` |
| Prior allocation-only source | Local `459bfacbda90005d618f12c4513b9c71cb11193d`; GitHub `d377fab7a840dc6d7a499fdf576d0dd8bb5dd4c1` |
| Allocation-only common tree | `3325af558b040759c1b432ec0806a80785af9713` |
| Last verified earlier publication | `3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf` |

The local and GitHub source commits have equal complete trees. The published
history retains the allocation-only and full combined source as separate
ancestors; documentation/checkpoint commits do not retroactively alter either
tested tree. The full source's manifest has **48 accepted assignments**, three
running and nine planned, with 51 distinct dispatch identities. Later review
acceptance and dispatch are recorded in the continuing manifest, not attributed
to that historical snapshot.

## Actual coherent gate

The source was freshly extracted with `git archive` into
`/workspace/scratch/c9f3ead4c910/w8-combined-source`. The separate build directory
was `/workspace/scratch/c9f3ead4c910/w8-combined-build`. No older objects were
combined with live headers, and active documentation workers were excluded.

The observed tools were CMake/CTest **4.4.4**, GNU C++ **14.2.0**, and CPython
**3.12.14** on Linux x86_64. The actual CMake/CTest executables were under
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin`; CMake selected
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`.

```sh
cmake -S /workspace/scratch/c9f3ead4c910/w8-combined-source -B /workspace/scratch/c9f3ead4c910/w8-combined-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /workspace/scratch/c9f3ead4c910/w8-combined-build --parallel 2
ctest --test-dir /workspace/scratch/c9f3ead4c910/w8-combined-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w8-combined-ctest.xml
```

Configuration, the full build and unfiltered CTest all returned zero. JUnit has
106 entries, zero failures, zero disabled entries and zero skipped entries.
Nested Python capability skips remain distinct; a successful suite does not
establish every platform capability. The two known local audio-admission skips
remain documented in the independent CLI review. No unexecuted Windows/macOS,
native VST3 or SDL application gate is inferred from this local configuration.

| Retained log under scratch `checks/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `w8-combined-configure.log` | 706 | `2fa7ccb3184ad22f2c5a463390db046c5c6f416ddf7d57d0b29325e5bb564e91` |
| `w8-combined-build.log` | 12,141 | `5f1bcbd0a0f0028e7be3da7e9c2a1aa7361e2158948e0d50dd6de0297bee20bf` |
| `w8-combined-ctest.log` | 13,788 | `62d31c3601da857cc13dc0ef42c21d3bcb20baf8394c5e022fb7627a47a2c96a` |
| `w8-combined-ctest.xml` | 52,305 | `9a12a066e312c62dde559cb372afbd4e9a96183c97a4309d7d8d07b16714b27d` |

These scratch logs are under `/workspace/scratch/c9f3ead4c910`. This durable
record retains their identities, actual commands, outcome and practical limits.

## Accepted changes and retained failures

- [Metadata allocation](CALIBRATION_METADATA_ACCEPTANCE.md) keeps the admitted
  descriptor-size-plus-one read, exact original bytes and all mutation/cleanup
  checks. The earlier [15-suite gate](CALIBRATION_ALLOCATION_INTEGRATION.md)
  and frozen before/after experiment remain separately reproducible.
- [Graph acceptance](CALIBRATION_GRAPH_ACCEPTANCE.md) executes 43 complete
  audits and five intentional rejects in seven maintained methods. Its dense
  case has 512 recorded synthetic captures and 18,276 exact expected edges.
  It retains failed and inconclusive corpus outcomes as expected results.
- [CLI acceptance](CALIBRATION_CLI_PIPELINE.md) passes nine methods and 71
  actual subprocesses. Its original 24 failing pipe cases and first-candidate
  standalone generator regression remain retained. The final boundary guard
  preserves all original numerical/validation definitions and complete files;
  generator and validator remain independent standard-library scripts.
- The [hosted package review](CALIBRATION_HOSTED_PACKAGE_RECHECK.md) retains
  the older `3b0979b` Windows failure and actual resolution of the earlier demo
  defect. Root's installation test now copies literal bytes containing CRLF,
  NUL and LF before its deliberate abort, preserving the complete assertion
  scope without assuming a foreign text writer's newline convention.
- [Raw Git identity](CALIBRATION_RAW_GIT_IDENTITY.md) demonstrates an actual
  supported float32 stream changed by text-auto filtering. `*.f32 binary`
  preserves it; the existing demo and supplied PDF are unchanged.
- [Evidence-boundary review](CALIBRATION_EVIDENCE_BOUNDARIES.md) passes 30
  finite cases. Declared metadata, engineering pass and replay match still
  establish no acquisition, rights, calibrated scale or physical fidelity.

The full gate reruns these integrated maintained suites and the existing engine,
offline tools, schemas, routing, rendering, traces, plots, repository integrity
and SDK-free adapter tests together. Author assertions, independent methods,
audit cases and CTest entries are different units; their totals are not added
together as a new number of independent tests or workers.

## Publication and continuation

The next checkpoint includes this qualified source plus accepted review records
and current pointers. Publish with an inspected expected-head guard, preserve
concurrent changes and verify the fetched commit/tree. Source-object creation
alone does not claim a branch update; the development log records the observed
publication separately.

Observe fresh hosted outcomes for the actual stream guard and exact-byte Windows
fixture. The older 103-suite platform matrix does not qualify these changed
sources. Complete clean setup, compatibility, operating/acquisition guidance,
remaining final reviews and the requested actual sixty-agent accounting. No
physical measurements, parameter fitting, DAW/device acceptance or signed
product release is established by this engineering checkpoint.

## Preserved concurrent completion and affected merge checks

The guarded publication preparation observed a concurrent advance to
`27209a7fec075b082aa911c9ea2159938deaae85` and stopped before updating main.
Root fetched and inspected all 28 changed paths: completed standalone records,
current documentation and an alternative test-only installation sentinel repair.
No production/native source changed. The merge keeps the newer calibration
section and the complete standalone continuation, preserves both development
histories, and retains the literal binary-copy fixture qualified above.

The immutable merged commit is `346d4eaa710c3ab9214a32e5e5a2cb916376ef83`, tree
`9aa7c28e55ba86a4d0b0b53dee135a6e6ceb3520`. All 35 differences from the full
106-suite source are under `docs/`, `AGENTS.md` or `README.md`; all production,
maintained tests, build configuration and model/demo inputs remain identical.
The changed packaged PLAN document and expanded documentation were qualified
from its own fresh archive `w9-merge-source`:

```sh
HAMMOND_TEST_CMAKE=/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake python3 -B /workspace/scratch/c9f3ead4c910/w9-merge-source/tests/test_capture_install.py
python3 -B /workspace/scratch/c9f3ead4c910/w9-merge-source/tests/test_repository_integrity.py
```

The installation suite passed **16/16 in 6.207 seconds**; repository integrity
passed **41/41 in 2.434 seconds**, both without skips. Their retained logs are
115 bytes / SHA-256 `36341c2b286adb0eb13ca213ed805ae340c6e652610dd031810709c1d8cc9411`
and 140 bytes / SHA-256 `4887997e547ba9ec5da6a2ec7aa70bba21efcce3c45ae7d0700273bf20a79e08`,
respectively, under scratch `checks/w9-merge-install.log` and
`checks/w9-merge-integrity.log`. No redundant full native rebuild or new
106-suite run is claimed for documentation-only changes.

Accepted [clean setup](CALIBRATION_CLEAN_SETUP.md) separately completes 51 real
commands and fifteen grouped checks against the original full-gate source,
including co-installation and relocation of all eighty files after private
source/build deletion. The [compatibility audit](CALIBRATION_COMPATIBILITY_AUDIT.md)
checks eighteen cases and preserved baseline identities, including the PDF and
all 45 public parameter records. Those finite audits are not additional CTest
suites or a claim that the concurrent standalone history never changed.

## Preserved standalone hosted closure and operating guide

Before publication, a second expected-head observation found concurrent
`7ec79fb1c80793cf2f1bd6418abc081a547528c5`, the documentation-only follow-up to
27209a7. Root inspected all ten changed paths and preserved its actual hosted
closure evidence and successor contracts. The merged source is local
`a77eb836d21f9df95b008359150372e5bad01d85`, tree
`1b9412923832f4189a06d4fdd77760220cdf5a79`. All differences from the full 106-suite
source are AGENTS/README or documentation/records. Production, tests, build
inputs, models and data remain identical. A fresh git archive of this merged
source passes all **41 repository-integrity methods in 2.459 seconds**. The
preceding affected install gate remains 16/16; this second merge changes no
installed payload input.

The separate standalone closure's ten successful jobs at 272 qualify its own
103-suite source and alternative newline-free marker. They do not qualify the
new allocation/CLI source or literal binary-copy fixture. Assignment 55 will
observe the next published source's actual hosted jobs.

Assignment 52 is accepted after root's source/guide and frozen-byte review:
fifteen actual source commands, four exact replays, all expected outcomes and
unchanged inputs. Its runbook is linked from README and the operational handoff,
and remains outside the frozen 57-file package inventory. The continuing ledger
records 52 accepted workers and 55 actual dispatch identities.

## Verified public code checkpoint

Root published `d7f6100010eb4cdd028ec93000cd9e893ac6d190`, exact tree
`0140c737de4db28288b118744c2beef57976697f`, with first parent
`7ec79fb1c80793cf2f1bd6418abc081a547528c5` and additional parent
`f4815a6372d103e92789a9732642345864543405`. Expected-head and non-force guards
succeeded. Root fetched main, checked its exact commit/tree against local
`2671fa548a0d728281f54a70ecec6e906b34967c`, and verified both qualified
`d377fab7` and `5e19022c` source commits and concurrent `7ec79fb` as ancestors.
Local source history is retained on `calibration-local-wave9-52`.

The public checkpoint contains 52 accepted records and 55 actual dispatch
identities. All changes from the full 48a1907 source are documentation/records;
production, tests, build inputs, models and data remain byte-identical. Its own
fresh hosted jobs are the platform qualification target; root holds further
publication until those jobs finish to avoid cancelling the observed source.
Later assignments 53/54 complete nine accepted waves through documentary
acquisition and exact source/report-identity reviews, without changing code.

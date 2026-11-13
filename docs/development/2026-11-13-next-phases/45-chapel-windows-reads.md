# Assignment 45 — portable chapel input identity

Actual agent `/root/w08_a45_chapel_windows_reads`, assignment 45/60, wave 8.
Owned only `tools/compile_chapel_presets.py`, `tools/chapel_controls.py`, their
two maintained Python tests, [the admission guide](../../CHAPEL_FILE_ADMISSION.md)
and this note. No native/core code, CMake, shared record, state format, data,
commit or publication was changed by this worker.

Read AGENTS, current scope/status/next steps/log and chapel contracts. The task
starts from failures at published `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`. Root advanced its unrelated integration
to local `c5452d10f3d6a9c861d1556ac030ada93b283000`, tree
`c2b1699e1ac5750d5eb9698ded72c5b9b4c2b6a9`, while this task was active.
The repaired files were uncommitted during testing; their hashes below identify
the actual qualification inputs rather than implying a whole-commit pass.

## Original failures and root cause

Core [run 43523378849](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43523378849),
Windows job `132222981820`, built successfully. Catalog acceptance then reported
three failures and one error around rewritten inputs. Exporter acceptance failed
its rewritten-catalog boundary case. Both readers rejected before reading because
they compared complete path and descriptor metadata tuples, including ctime.

I inspected immutable CPython **v3.12.10** primary source, matching the runner's
Python version. `win32_xstat` in
[Modules/posixmodule.c](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c)
preserves legacy creation-time ctime, while `_Py_fstat_noraise` and its helpers
in [Python/fileutils.c](https://github.com/python/cpython/blob/v3.12.10/Python/fileutils.c)
return change time. The [upstream report](https://github.com/python/cpython/issues/157671)
and [Python documentation](https://docs.python.org/3.12/library/os.html#os.stat_result)
provide additional context. No Windows runner was executed by this worker.

Before production edits, two new maintained methods per suite reproduced:

- A simulated Windows path/descriptor ctime difference rejecting a valid input.
- An actual raw descriptor remaining open after injected `fdopen` failure.

Each two-method pre-repair probe reported one error and one failure. Its test
cleanup closed the leaked descriptor after detecting it. The POSIX mismatch
subcase still correctly rejected. Source before repair was compiler SHA-256
`fcfdb3342478d8a4369f1080d234515c59a87a0094db522c1f44a8e7ddd61210` and exporter
`dc390c74ac9af31322d73a116dfd61cd353c6e2ee309a7871c571bca1c3904a8`.

## Narrow repair and test design

The cross-API comparison still requires exact device/inode/size/mtime. POSIX
also retains cross-API ctime equality; only Windows permits that one semantic
difference. Each complete five-field stamp is still checked before/after through
its own API. Initial/final file type and reparse flags must remain admissible.
The raw descriptor is closed if stream wrapping fails. Public limits, JSON/data
admission, canonical output and publication rules remain unchanged.

Each suite adds five maintained methods. The 38 rejection probes cover one
POSIX ctime mismatch, four common fields under each of two platform branches,
seven fields under each descriptor/path domain and platform branch, and the
descriptor-wrap failure. The seven fields include all five identity stamps,
file type and reparse attributes. Both post-read calls must actually occur;
early rejection cannot masquerade as post-read mutation coverage. Every rejected
fixture preserves bytes, inode/type/mode and entry set. A copied OS namespace
isolates platform behavior without globally changing `os.name` or `pathlib`.

Three real rewrites per suite exercise actual filesystem and CLI behavior with
independent catalog/state expectations. The complete existing suites remain in
place, including all 162 individual tap mutations and all 205 exact-state vectors.
No tests were disabled, made Windows-only skips or weakened to hide the failures.

## Actual executed results

Linux x86-64, Python **3.12.14**, working directory
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_presets.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_controls.py -v
```

| Complete maintained gate | Actual result |
| --- | --- |
| Catalog compiler | **23/23 pass**, exit 0, 6.946 s; 114 CLI calls, 272 API rejects including 38 reader probes, five publication failures. |
| Control exporter | **20/20 pass**, exit 0, 18.300 s; 273 CLI calls, 205 exact-state vectors, 302 API rejects including 38 reader probes, six publication fault/race probes. |

No skipped methods. Both suites passed on their first complete repaired run;
no producer or fixture correction followed that result. Source/data stability
checks passed. The canonical catalog remains 4,837 bytes, SHA-256
`f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91`.
These Linux execution and controlled metadata fixtures do not claim an actual
Windows pass. Root must observe the next named hosted execution.

| Repaired artifact | SHA-256 |
| --- | --- |
| Compiler | `ae54bbc196d779b2b1b369aa2c2e7db4268dd175201d6b193fed8256e6420826` |
| Exporter | `9639e83a6a04e40786227ffca69c50db82dd6099e102cc8c727a204fe1a9d436` |
| Catalog test | `7522b0b09f5920669c08a1b7f3726a1fc2d1bf6d16005e8c97a7c694afddc1e8` |
| Exporter test | `0387795670554c755bd737434b8070bdb3da8c46b01bc9be2b5761fd64cc6ec3` |
| Catalog pre-repair log | `e4c4733e209bdcae145a26217791317b8a9facc201cbf44aa4b0a6a490d341dc` |
| Exporter pre-repair log | `fb1f12ce6fafe7fa54863a583515cb0149fab27db88e060a6a6ede28bc6e9881` |
| Catalog complete repaired log | `8b7b2de2ba9008333fa00862c1c5d53739a2b5093a543603b1df244ede804c53` |
| Exporter complete repaired log | `0953c742254e4f9e7c59d5a8eb4c8f3fa0da68fc1c023c109539d97dc6cb066a` |

Logs are `../a45-catalog-before.log`, `../a45-controls-before.log`,
`../a45-catalog-final.log` and `../a45-controls-final.log`. They are scratch
evidence; this maintained note retains the executed result and identities.

## Integration handoff

Root can use the unchanged CTest names `python_test_chapel_presets` and
`python_test_chapel_controls` after rebuilding/discovering the selected inputs.
Publish the six owned files, retain the original failed Windows evidence and
inspect the repaired Windows job before closing that platform gate. Source
hashes were frozen before handing them to root. The raw metadata observation
contract still excludes hostile concurrent replacement and power-loss durability;
it does not authenticate a physical instrument or add preset-selector behavior.

# Python runtime context and command-line preservation

Assignment **58**, logical wave **10**, actual worker `/root/cal_w10_a58`.
This independent finite check uses published source
`d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree
`0140c737de4db28288b118744c2beef57976697f`, on Linux x86_64.

**Result: the maintained nine-method CLI pipeline passes under actual CPython
3.13.5, with all 71 child processes and zero failures, errors or skips.**
A separate twelve-process matrix compares actual CPython 3.12.14 and 3.13.5.
Four own-runtime replays match; four cross-runtime replays mismatch, with
`same_tool_sources: true` and `same_runtime: false`. The inconclusive job and
failed mixed study retain their engineering statuses in every case.
No production defect or required source change was found.

The [assignment record](../development/2026-11-13-calibration/58-runtime-context.md)
retains exact source identities, commands, the executed audit/driver, output
hashes and the corrected audit-only syntax error. This is additional finite
Linux runtime evidence. It is not the integrator's full 106-suite gate,
assignment 55's hosted matrix, or a test of the declared Python 3.10 floor.

## Coherent source and actual environments

A fresh `git archive` of the exact public commit was extracted into a private
Unicode/space path. All ten tool files and the maintained pipeline test were
compared directly with that commit's Git blobs. The complete extracted
file-byte inventory contains **1,023 files / 40,370,269 bytes** and is unchanged
after all executions. Its canonical inventory is 164,836 bytes, SHA-256
`b93f76f1435034f19dfe27c860844f9852616307bd10a91f66d5d6635b0afd07`.
This is the digest of the path/size/hash inventory, not a packed archive digest
or an attestation of loaded interpreter memory.

| Actual interpreter | Observed runtime |
| --- | --- |
| `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12` | CPython 3.12.14, `linux`, `x86_64` |
| `/usr/bin/python3.13` | CPython 3.13.5, `linux`, `x86_64` |

The separate matrix invokes every tool with `-B -S`, empty `PYTHONPATH`,
`PYTHONIOENCODING=ascii:strict`, and `PYTHONDONTWRITEBYTECODE=1`, from a foreign
Unicode working directory. Inputs and outputs use explicit absolute paths.
The pipeline's existing private-source, Unicode and real-pipe mechanisms remain
unchanged. No network access, runtime download, native build or installation
was performed.

## Actual Python 3.13 pipeline

The unchanged
[`test_capture_cli_pipeline.py`](../../tests/test_capture_cli_pipeline.py)
is 22,054 bytes, SHA-256
`bfff3005af05ede0b48258de9be1b1560384f6fec618fa6b29aad6dc75d41cb6`.
A small standard-library driver loads its actual test class, runs the default
nine methods, and records the class's existing subprocess observations. The
driver does not change the test class, producer modules, expectations or
subprocess implementation. All 71 observed child commands select the actual
3.13 executable.

| Executed group | Actual CLI processes | Required behavior retained |
| --- | ---: | --- |
| Synthetic archive setup | 1 | Exact generated fixture inventory |
| Ordinary tools and complete replay | 12 | UTF-8 bytes, literal numerical outcomes and all engineering statuses |
| Both standard streams closed | 4 | Exit 1 and complete published files |
| Closed stdout help/report or closed stderr rejection | 24 | Exit 1; no unexpected finalizer status 120 or tracebacks on writable stderr |
| Existing input/source/report and hardlink/dangling destinations | 20 | Rejection with original bytes and link targets preserved |
| Generator/validator copied without siblings | 10 | Independent-script ordinary/help/failure behavior |
| **Total** | **71** | **All expected outcomes** |

Unittest ran **9 methods in 6.681 seconds**, with no failures, errors or skips.
The child exit distribution is 13 zeros, two threes and 56 ones; those nonzero
values are the declared engineering or failure outcomes, not ignored failures.
Elapsed time is a run observation, not a performance threshold or callback
guarantee. The pipeline retains its deliberate private Unicode fixture edits;
it does not alter the repository's sixteen original demo files.

## Actual cross-runtime report matrix

The separate twelve tool invocations use the **unchanged original demo**.
Four producers execute the inconclusive job and failed study once per runtime.
Eight verifiers cover both saved runtimes under both executing runtimes.

| Saved producer runtime | Executing verifier runtime | Job and study replay | Context flags |
| --- | --- | --- | --- |
| 3.12.14 | 3.12.14 | Two `match`, exit 0 | Runtime true; sources true |
| 3.13.5 | 3.13.5 | Two `match`, exit 0 | Runtime true; sources true |
| 3.12.14 | 3.13.5 | Two `mismatch`, exit 1 | Runtime false; sources true |
| 3.13.5 | 3.12.14 | Two `mismatch`, exit 1 | Runtime false; sources true |

The job producers exit **3**, retaining `inconclusive`. Study producers exit
**1**, retaining `failed` and all three ordered jobs: pass, inconclusive, failed.
Every completed verifier has empty stderr and a full canonical summary. Saved
and replayed report identities equal the corresponding actual producer bytes.
Every `--output` file equals stdout exactly. Source files, original input files
and saved producer files remain unchanged.

| Runtime shorthand | Producer / engineering status | Complete bytes | SHA-256 |
| --- | --- | ---: | --- |
| 312 | job / inconclusive | 32,783 | `c39a060fadf9c3fbf71b1608c3884e62bf25b67fa4168f0948fe021646bb0930` |
| 312 | study / failed | 119,427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` |
| 313 | job / inconclusive | 32,782 | `75e61d1a307b725800687ef9c4c6fefa06ac16ee6b77f23502d63e1862293e81` |
| 313 | study / failed | 119,423 | `20c6454432028f00a0bddb248895d580834ae602984719d02cb6ad0ad69e0e4a` |

The report size changes have a specific explanation here: `3.12.14` has one
more character than `3.13.5`. The job has one runtime envelope and the study has
four, so their actual complete report sizes differ by one and four bytes,
respectively. The other three observed runtime fields are identical.

For diagnostic comparison only, the audit removes exactly `/runtime` from
copies of the two job values, and exactly `/runtime`,
`/jobs/0/report/runtime`, `/jobs/1/report/runtime`,
`/jobs/2/report/runtime` from copies of the two study values. It removes no
source inventory, input binding, numerical value, policy, role, status or claim.
The remaining canonical values are identical:

| Explicit projection | Bytes | SHA-256 |
| --- | ---: | --- |
| Job with its one runtime object removed | 32,637 | `90dd074bf31a29d689964d1f137373a4d2311fd8cfdfc8f39b2839145220c764` |
| Study with its four runtime objects removed | 118,735 | `d2c72d03bdf3be595fbc539a89f140284f40603249ade0a625fde2dace7c07e1` |

**This projection is not a public replay match or an allowed override.**
The public verifier compares every canonical byte and explicitly reports the
cross-runtime mismatches above. The projection only describes the observed
difference in these finite fixtures; it does not establish that another
dataset, operation or runtime has identical numerics.

## Operator consequences

Keep every original report and record the actual interpreter used to create it.
A runtime change warrants a fresh output name and an honest new report. When
replay mismatches, read `context.saved_runtime`, `context.replayed_runtime`,
`same_runtime` and `same_tool_sources`; do not edit either envelope to force a
match. A matching replay reproduces the underlying failed or inconclusive
result without converting it into a passing comparison.

From a coherent checkout, an operator with the two named interpreters available
can run the maintained suite and a compact study example:

```sh
python3.13 -B -S tests/test_capture_cli_pipeline.py
mkdir runtime-results
python3.12 -B -S tools/capture_study.py --input examples/capture-demo/study.json --output runtime-results/study-312.json
python3.13 -B -S tools/verify_capture_report.py --kind study --input examples/capture-demo/study.json --report runtime-results/study-312.json --output runtime-results/cross-runtime.json
python3.13 -B -S tools/capture_study.py --input examples/capture-demo/study.json --output runtime-results/study-313.json
python3.13 -B -S tools/verify_capture_report.py --kind study --input examples/capture-demo/study.json --report runtime-results/study-313.json --output runtime-results/own-runtime.json
```

Use a new directory and run these separately. Expected command exits after
directory creation are **1, 1, 1, 0**; the first command's test runner exits 0.
Select actual interpreter paths when those command names are unavailable.
This portable recipe describes the executed cases; the exact audit below used
the absolute interpreter paths in the environment table.

The [replay contract](../CAPTURE_REPLAY.md) and
[operations guide](../CALIBRATION_RUNBOOK.md) define full semantics. The present
result does not qualify Python 3.10/3.11, arbitrary Python 3.13 builds,
other implementations, Windows/macOS under 3.13, all possible locales or
hostile concurrent mutation. It does not recertify the entire toolchain on
3.13, establish physical calibration, supply authentic acquisition history or
complete M8. The original declared minimum remains a contract; direct execution
of that minimum remains separate evidence.

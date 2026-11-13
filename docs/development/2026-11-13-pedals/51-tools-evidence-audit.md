# Assignment 51 — tools and evidence final audit

Owner: `/root/w09_a51_tools_evidence_audit`

Wave: 9

Session: `2026-11-13-pedals`

Status: local audit and approved repair complete; root owns integration and publication

## Scope and decisions

Read the repository agent rules, active pedal handoff and plan, atlas review,
current status/next steps/development log, CLI Unicode contract, render evidence,
trace plots and session-checker contract. Inspected their relevant tools and
tests. Reread atlas text pages **355–360**, covering evidence and source-identity
boundaries; this assignment did not reread the entire PDF or render new visual
plot previews. The cloud runtime skill was read; no dependencies or network
configuration were changed.

Reviewed the coherent W8 source, rather than mixing live worker edits with older
binaries. Verified all 534 frozen source files and executable modes against Git
tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e`, then rehashed those files after
qualification. The archive remained unchanged.

The review established one concrete Windows reparse admission defect. After
reporting it, root authorized the exact two production/test paths below.
Assignment 51 changed only these four files:

- `tools/native_bundle_inventory.py`
- `tests/test_native_bundle_inventory.py`
- `docs/reviews/PEDAL_TOOLS_EVIDENCE_FINAL.md`
- this assignment note

No DSP/native source, CMake, install manifest, shared documentation, session
ledger or other worker file was edited. No index changes, commits or pushes were
made by this worker. The [review](../../reviews/PEDAL_TOOLS_EVIDENCE_FINAL.md)
contains the contracts, repair rationale and evidence limitations.

## Focused baseline execution

Workspace prefix: `/workspace/scratch/f364bc93d920`. Frozen source:
`checkpoint-w08/source`; matching build: `checkpoint-w08/build-default`.
Private evidence directory: `a51-tools-audit`.

Obtained configured commands and environments with:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/checkpoint-w08/build-default \
  --show-only=json-v1
```

Executed each corresponding test command directly, preserving its configured
`ENVIRONMENT`. All nine commands used this interpreter and test-path pattern:

```text
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
/workspace/scratch/f364bc93d920/checkpoint-w08/source/tests/test_<suite>.py
```

The selected suites were `render_fixture`, `verify_render`,
`pedal_render_evidence`, `cli_unicode`, `pedal_trace`, `plot_pedal_trace`,
`pedal_session`, `pedal_demo` and `native_bundle_inventory`. They executed
**28 + 35 + 17 + 11 + 13 + 16 + 24 + 10 + 19 = 173 methods** with zero failures,
errors or skips. Process orchestration took 36.528 seconds. The review records
individual timings. Actual W8 CLI executables and the compiled `nominal.b3p`
profile were supplied by CTest, so executable-dependent coverage did not
silently skip. Bytecode writing was disabled.

Root's separately reported full W8 gates were 71/71 default and 8/8 native
suites. This note does not claim those as this worker's own execution.

## Concrete repair and regression

Synthetic metadata probes against the original frozen tool tagged each of the
bundle root, a descendant directory and a descendant regular file with Windows
attribute `0x400`, preserving the actual directory/regular mode. All three
were incorrectly accepted. The repaired tool rejects the reparse bit immediately
after fresh `lstat` at root, traversal and regular-file admission, before
resolving, traversing or opening the selected path. Existing identity,
stability, bounds and no-clobber guards remain. Inputs must be quiescent.

New regression guards fail on actual traversal/opening of each tagged path.
The regular-file admission helper is also checked directly. On Windows the
same method creates and removes two real junctions and checks their targets
remain intact. The executed Linux output explicitly said actual Windows
junctions were not applicable; that hosted-platform result remains pending.

Copied final tool/test bytes into `a51-tools-audit/repair-source` and paired the
new regression with the unchanged old tool in
`a51-tools-audit/baseline-regression-source`. Exact qualification commands:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B \
  /workspace/scratch/f364bc93d920/a51-tools-audit/baseline-regression-source/tests/test_native_bundle_inventory.py \
  NativeBundleInventoryTests.test_reparse_roots_directories_and_files_reject_before_access
```

This deliberate negative control returned the expected exit 1: one method,
three failing subtests, 0.004 reported seconds. The guards proved that the old
tool attempted the forbidden access; this was not an unexplained failing gate.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B \
  /workspace/scratch/f364bc93d920/a51-tools-audit/repair-source/tests/test_native_bundle_inventory.py
```

The repaired suite returned 0: **20 methods in 0.444 reported seconds**, zero
failures, errors or skips. A prior exploratory live invocation also passed
20 methods; the privately frozen run is the recorded repair qualification.

| Final repair file | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/native_bundle_inventory.py` | 19121 | `ee46f979cb3070dcf39d976ab657be974d937f89e835a7927b384dcc755ad4a7` |
| `tests/test_native_bundle_inventory.py` | 25633 | `aa11faf0abdbc9e0ec1bc2ad293f66fc95b249301ccda61db94546076e5e0860` |

## Actual bundle check and retained identities

Read the real generated bundle location from
`checkpoint-w08/build-native/hammond-vst3-path-Release.txt`. Ran both inventory
versions with the same arguments; the first exact command was:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B \
  /workspace/scratch/f364bc93d920/checkpoint-w08/source/tools/native_bundle_inventory.py \
  --bundle /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/VST3/Release/HammondB3.vst3 \
  --output /workspace/scratch/f364bc93d920/a51-tools-audit/bundle-before.json \
  --source-manifest /workspace/scratch/f364bc93d920/a51-tools-audit/repair-source-record.json \
  --sdk-lock /workspace/scratch/f364bc93d920/checkpoint-w08/source/data/dependencies/vst3-sdk-lock.json \
  --project-notices /workspace/scratch/f364bc93d920/checkpoint-w08/source/THIRD_PARTY_NOTICES.md
```

The second command replaced only the script with
`/workspace/scratch/f364bc93d920/a51-tools-audit/repair-source/tools/native_bundle_inventory.py`
and output with
`/workspace/scratch/f364bc93d920/a51-tools-audit/bundle-after.json`.
Both exited 0 and recorded four files, 444,239 bytes, Linux x86_64. Their complete
report bytes were identical. The source-overlay record is explicitly a local
observation, not an authenticated association between source and binary. No
module load or new ABI test is claimed here.

The scratch records below retain commands, results and hashes. They are local
session evidence, not distributed attestations; this durable note preserves the
material observations if those scratch files later disappear.

| Evidence under `a51-tools-audit` | SHA-256 |
| --- | --- |
| `source-inventory-before.json` | `0dda1cb7a61a21d05aae4a60a27f2e1ffc1a0c45bcd06ded322fc5038beceb30` |
| `focused-results.json` | `c26555e115f24082d2ef54cc292e7c5ab5f29284123509f4389a1ff55736fa76` |
| `reparse-before.json` | `6f1cbc2abb2429bda104298795a564c5f3a77b07cd33a26ee7e953284522676e` |
| `repair-source-record.json` | `62109a35f7809bd4daee357bc08cca040f6ccd92616a0747016be6fd32f0eadd` |
| `repair-results.json` | `758ffb073c9fa63f0f106c85ee01a447f08073c3ae2c88a01e95ecfbf1975313` |
| `pre-repair-regression.log` | `c8cfb503f5b761ac58a5f9b4d5244df701f647952bd6796938bc8c24e4e6b085` |
| `repair-suite.log` | `a907978e134e7c06ce994328e3e7a6d622386e9d4afac7957795b759d02fc17a` |
| `bundle-before.json` and `bundle-after.json` | `b8e3d87f54c7ec7146032719476dc2cab7317c26a03b079f859cd5ee80fd01ea` |

The actual module `Contents/x86_64-linux/HammondB3.so` was 434,168 bytes, mode
`0755`, SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.

## Handoff and next step

Root should include the four owned files in the W9 source freeze and qualify
the coherent integration before committing/pushing. Inspect the hosted Windows
test output for the explicit two-actual-junction success line, then retain its
run and commit identity. The native CI documentation owner should extend its
admission wording to cover reparse points and junctions. Do not promote local
Linux metadata probes into a completed Windows execution claim.

Continue the remaining current-session assignments using the existing ledger
and handoff rules. A running assignment or a note that merely parses earns no
automatic completion credit. This worker supplies no new physical capture,
DAW/device qualification, signing or publication result.

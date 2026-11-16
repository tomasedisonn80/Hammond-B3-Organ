# Independent admission: Windows contact-reference identity repair

**A47, 16 November 2026 — source and local regression admission.** The reviewed
repair addresses the observed path/descriptor metadata mismatch without dropping
timestamp fields, weakening a numerical criterion, or adding a Windows skip.
No blocking finding remains for this patch. Root still owns the affected CTests,
publication and a fresh hosted Windows result at the repaired source. This review
does not claim that repaired Windows execution has already passed.

The governing [bounded repair scope](../development/2026-11-15-streaming-continuation/WINDOWS_REPAIR_SCOPE.md)
preserves the trajectory, material, numerical and product gates. A47 read the
complete AGENTS and M0–M9 plan, current recovery records, I/O and install contracts,
actual implementation/test diff, original failure, and primary CPython source.
A45 owned the implementation and registered regressions; A47 edited only this
review and its own note/evidence. No native build or broad suite was run by A47.

## Observed failure and reviewed identities

The [original failure receipt](../development/2026-11-15-streaming-continuation/reports/windows-core-af2b747-failure.json)
binds commit `af2b74760ee195c9497b314a1a29172f5238dd44`, workflow run
`43783034126`, job `133024356072`, **Release (Windows MSVC)**, Python **3.12.10
x64**. That job passed **184/185 CTests**; the relocated package's single-fixture
command failed with `input changed after path preflight`. The failure is retained
and is not converted into a pass by this diagnosis. A47 independently decompressed
the complete job log and reproduced its **526,325-byte** decoded SHA-256
`2858f8f90bb79736630bf72b0fdaca93156baf9f8496afe83cb7500adc47ba6d`.

The stable diff was coordinated with A45 before final review. Both files retained
these exact hashes throughout A47's independent execution:

| Reviewed file | SHA-256 |
| --- | --- |
| `tools/contact_switching_io.py` | `1281cd0726a6cf16dcc0ceea8445b4e42900ed995bb82dfea70c6dffdd104cc6` |
| `tests/test_contact_switching_io.py` | `ade725edc0d0b3f99714e10363f98c6454bacd7ed927698393fb2f1ed6410b81` |

The earlier I/O implementation hash was
`e3219265f1496a36b4f5d8a13941672b46ddc4116f331b7a1b99115a2dac9dc6`.
The comparison base has tree `fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4`;
these changed bytes are a reviewed overlay, not an assertion that the original
published commit already contains the repair.

## Primary-source diagnosis

A47 independently read the exact **CPython v3.12.10** sources, not merely a report
about a later interpreter:

- [`Python/fileutils.c`](https://github.com/python/cpython/blob/v3.12.10/Python/fileutils.c),
  `_Py_attribute_data_to_stat` and `_Py_fstat_noraise`: the Windows descriptor
  path obtains `FILE_BASIC_INFO` and assigns its change time to ctime.
- [`Modules/posixmodule.c`](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c),
  `win32_xstat` and `os_fstat_impl`: the path branch replaces ctime with birth
  time for compatibility, while the descriptor branch returns its own result.
  `update_st_mode_from_path` also synthesizes execute bits for selected suffixes.
- [CPython issue 157671](https://github.com/python/cpython/issues/157671)
  independently reports the same API discrepancy on later Windows interpreters.
  It corroborates the mechanism; the version-specific source establishes its
  applicability to 3.12.10.

An unchanged file can therefore have unequal path and descriptor ctime values.
Whole-signature equality across those APIs is not a valid same-file test. These
source facts explain the retained failure and justify separating metadata domains;
they are not a substitute for executing the repaired package on Windows.

## Review of the actual change

`_signature` is byte-for-byte unchanged and still contains **device, inode, mode,
size, mtime_ns and ctime_ns**. `OutputPlan` retains two full input signatures:
`input_signature` now comes from an opened descriptor, while the added
`input_path_signature` retains the complete path result. Neither domain loses a
field, and ctime and mtime remain independently meaningful within their own domain.

The new `_preflight_input_signature` opens the already resolved input read-only,
with the same available nonblocking and binary flags as the loader. It admits
regular type and the existing **256 KiB** size bound from the opened descriptor,
bridges path and descriptor through `os.path.samestat` (device/inode), and checks
the full path signature again while the descriptor is open. Its `finally` closes
the raw descriptor on success and failure. Comparing device/inode at the bridge
permits legitimate ctime/mode differences without treating another file as the
same input.

`load_input` compares its descriptor signature to that descriptor-derived token,
then retains the full before/after descriptor comparison around the bounded
**262,145-byte maximum read**. Its change outside that comparison is explicit
cleanup if `os.fdopen` construction raises, including interruption. A constructed
stream remains context-managed. Parsing still occurs after the stream closes.

The following existing rejection and publication behavior is preserved:

| Boundary | Review finding |
| --- | --- |
| Input/output aliases | Normalized direct paths, same device/inode hardlinks, output leaf symlinks and unsupported special files retain their rejection branches. The added descriptor/path bridge also rejects replacement or substitution between path admission and open. |
| Input path and parent changes | Original argument and resolved-path identities remain in the plan. Full path signatures, output signatures and output-parent identity remain part of dataclass equality in `_recheck_plan`. |
| Late mutation | `atomic_write_report` is unchanged: it rechecks before creating the temporary and again after writing, flushing, fsyncing and closing it. Both rechecks now recapture compatible descriptor and path tokens. |
| Failure outputs | Encoding/admission still precede temporary creation; rejected publication preserves an existing report or an absent destination. The existing `finally` removes the owned temporary and leaves unrelated files alone. |
| Work and storage | The helper adds one metadata-only, short-lived input open per preflight/recheck and one six-integer path tuple. It adds no data-read loop or persistent handle. Input/report/depth/work/time/memory caps are unchanged. |
| Numerical scope | Parser, report construction/encoding, kernel, oracle, study, fixtures, frozen contracts, tolerances and schema definitions are unchanged. No Engine, rendering, audio, parameter, state or UI code changes are part of this repair. |

These are metadata snapshots, as in the existing design. They do not establish a
filesystem lock or eliminate the interval between the final recheck and atomic
replacement. The repair retains that model and its existing failure boundaries.

## Regressions and independent execution

A47 inspected all eight additive A45 methods and verified both retained log
hashes. The [before-repair receipt](../development/2026-11-15-streaming-continuation/reports/A45-before-repair-tests.json)
records those methods against unchanged production source: exit 1 with eight
failed assertions/subcases. This includes stable API divergence, lack of a
descriptor-derived publication token, preflight replacement/substitution and
descriptor cleanup. Existing mutation rejection cases also remain exercised.
The [after-repair receipt](../development/2026-11-15-streaming-continuation/reports/A45-after-repair-tests.json)
records the complete I/O suite: **39 methods, 38 passed and one existing AF_UNIX
facility skip** caused by host `EPERM`, with no failures. Its unittest time is
**0.911 s** and external process time **1.110138046 s**. The skip is neither new
nor a Windows exception. A47 did not rerun that complete suite.

The independently authored [A47 checks](../development/2026-11-15-streaming-continuation/reports/A47-independent-checks.py)
and [complete receipt](../development/2026-11-15-streaming-continuation/reports/A47-independent-checks.json)
record **five methods / 31 cases, zero failures, errors or skips** on Linux
6.18.57 x86_64, glibc 2.41, Python **3.12.14**. The retained run took **0.202 s**
inside unittest and **0.276621019 s** including its source audit. From the recorded
repository cwd:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12 -B \
  docs/development/2026-11-15-streaming-continuation/reports/A47-independent-checks.py
```

The 31 cases are separate from A45's registered test count:

- **24 late-publication cases:** mutate each of the six fields separately in
  each metadata domain, after the temporary's fsync, with both absent and existing
  outputs. A stable descriptor/path ctime discrepancy is present throughout.
  All reject, preserve the expected output state and unrelated file, remove the
  owned temporary, and close recorded descriptors.
- **Four type/size cases:** a descriptor with the same device/inode but a special
  type or size **262,145 bytes** rejects in preflight and load, before parsing or
  output allocation; descriptors close.
- **Two exceptional cleanup cases:** a path-stat `OSError` while the preflight
  handle is open and `KeyboardInterrupt` during load stream construction both
  leave descriptors closed and prior output intact.
- **One complete CLI case:** stable ctime and execute-bit differences succeed,
  preserve the frozen input hash, report the new implementation hash and match
  the unmocked samples of the same **F00-48000-v1 silence fixture**. This bounded
  success is not a fresh numerical study or a nonzero-audio comparison.

The receipt also independently compares ASTs to the published base: only
`OutputPlan`, `load_input` and `preflight_paths` change; only
`_preflight_input_signature` is added. All other existing function/class ASTs and
module constants/imports match. All **31 pre-existing test methods** and their
supporting class methods remain unchanged; eight test methods are additive.

## Package identity and remaining acceptance

A47 rehashed the historical A30 component inventory. The **48 payload names**
and CMake installation module are unchanged. Exactly **one payload file's bytes**
change: `tools/contact_switching_io.py`, with the new hash above. The other
**47 payload files** retain the recorded hashes, including numerical code,
contracts, all 36 fixtures, manifest and probes. Copy-only installation,
`EXCLUDE_FROM_ALL`, and refusal to merge an existing package remain unchanged.

The [earlier 48-file hash-equality statement](STREAMING_CONTINUATION_COMPATIBILITY.md)
belongs to its earlier snapshot. It must not be restated as current after this
repair. Original numerical reports, sample hashes, timings and old source-bound
claims remain historical evidence. The new I/O source identity is explicit in
this admission and is emitted by the checked CLI.

**Admission:** the narrow implementation and its retained rejection semantics are
accepted for root's affected qualification and publication. A47 has no blocking
source or local-regression finding. Root must retain the I/O, installation and
study-admission CTest results for these bytes, then inspect fresh hosted results
at the repaired commit. No repaired Windows runtime, new full numerical grade,
physical contact model, live integration or product-release gate is claimed here.

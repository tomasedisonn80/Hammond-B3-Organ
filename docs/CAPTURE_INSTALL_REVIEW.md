# CaptureTools independent installation acceptance

**Verdict:** the frozen `capture-tools-install-v1` contract is cleared. The
exact implementation below passes the independent Linux installation and
relocation checks. The unchanged OfflineTools component also passes its existing
maintained regression through a private configuration containing the new helper.
No production defect or installation-contract change was required.

Reviewer: actual calibration assignment **38**, `/root/cal_w7_a38`, logical
wave 7. Assignment 37 owns the producer and its guide. This reviewer owns only
[the maintained acceptance suite](../tests/test_capture_install.py), this review,
and [the assignment note](development/2026-11-13-calibration/38-install-acceptance.md).
Root owns shared records, coherent integration and publication.

| Qualified input | Bytes | SHA-256 |
| --- | ---: | --- |
| Frozen [installation guide](CAPTURE_TOOLS_INSTALL.md) | 17,824 | `ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590` |
| `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
| `CMakeLists.txt`, including the released one-line include | 16,412 | `98843ed4e797cc4ce7caac14d995d8962492ed50b8756d3a6d8b19d0c316aed0` |
| Final independent `tests/test_capture_install.py` | 34,023 | `a797443fe7d208bbdaebedae836edca988524d8371938dd95e9368738f26bb74` |

## Contract review and independent expectations

The complete frozen guide and the complete existing OfflineTools module and
test were read before grading. The guide explicitly distinguishes the Python
runtime requirements from the C++ compiler needed by ordinary repository
configuration. Its 57-file inventory, separate explicit component, copied-source
closure, new destination requirement and preflight boundary are coherent.
The guide was cleared before the producer's formal ready notice.

The test's literal inventory was authored from the guide before reading the
implementation's lists: ten Python modules, eight data/schema files, sixteen
unchanged demo files, twenty-one documentation files and two root files.
The producer's file list is not its oracle. Every copied source/data byte is
compared with the independent private source snapshot; the generated README
is checked for its relative commands, guide link, outcome explanations and
absence of required private source/build paths. Its bytes remain deterministic
across repeated configuration and configuration selections.

The installed demo's raw vectors, raw/decoded SHA-256 constants, exact quarter
and half offsets, interval bounds and expected statuses come from the frozen
demo/job contracts. The test independently constructs the float32 and decoded
binary64 preimages. It neither imports another test's fixture factory nor
obtains numerical expectations from an installed producer report.

## Actual package and configuration results

The maintained suite copies the source into private directories, retaining the
ordinary top-level project configuration and the native source inputs it needs.
It omits the PDF, Git database, build products and unrelated tests. No native
target is built. Actual CMake configuration succeeds with both native adapters
disabled, then `--component CaptureTools` installs the exact 57-file set.

The source-only condition is checked against absent renderer/metadata/trace
executables and absent `nominal.b3p`. A prefix containing unrelated user data
is accepted without changing that data. The CMake component manifest names
exactly the same 57 installed paths. The package contains no symlinks, bytecode
caches, test suite, native executable or unexpected file.

The suite executes repeated configuration, a custom `assets/reference` data
directory, and Release, Debug and a deliberately non-native configuration name.
Each copies identical payload bytes because this component has no target output
or configuration filter. Unset, empty and `COPY` install modes succeed. Symlink
and other non-COPY modes reject before writes. Six invalid data-directory forms
reject during configuration, preserving the existing relative-directory rule.

Actual POSIX `DESTDIR` staging installs at the staged destination, leaves the
logical unstaged prefix absent, and rejects a second installation without
changing the staged package. That case is explicitly skipped on Windows, where
this CMake facility is not supported by the contract's platform scope.

An isolated no-language CMake project includes the real helpers and one
independent unrelated-component sentinel. Default and other component selections
never install CaptureTools, while explicit CaptureTools selection never installs
the sentinel. This is component-dispatch evidence, not a substituted native
runtime. The ordinary full project configuration is exercised separately above.

The configured CTest entry supplies the actual selected CMake binary and its
180-second timeout. The workspace had no `cmake` on PATH; the producer already
provided this test environment in its initial ready helper. No source repair
was required to resolve that prerequisite.

## Preflight, preservation and late failure

All **57 individual payload inputs** are removed in separate private-source
subcases. Each actual install rejects with the offending path before changing
the existing prefix. This includes the generated entry point and the late
documentation/notice inputs; the test does not only sample the first module.

Additional actual checks reject empty and directory inputs at both an early
module and a late notice, and reject an observed source symlink. Existing
destination files, directories, complete packages, valid links and dangling
links remain unchanged. Unrelated prefix contents and link targets survive.
The snapshots retain the actual native `os.readlink()` result before and after;
they do not assume that Windows returns the originally requested namespace
spelling. Temporary roots are resolved before constructing fault paths.

A deterministic fault is inserted only into a private generated install script,
after the first real CaptureTools copy. It writes an other-writer marker and
then aborts. The actual partial payload and marker remain; the install log
discloses the partial-copy boundary. The injection asserts its explicit reached
diagnostic, so an earlier unrelated failure cannot satisfy this test.

This last case is a controlled late abort, not an actual disk-full, interruption
or live filesystem-race test. The contract deliberately promises no atomic
multi-file transaction and no nonreplacement guarantee for a hostile writer
after preflight. The tests preserve that distinction instead of claiming stronger
behavior from ordinary CMake copy operations.

## Relocation with source and build removed

A separate private ordinary project is configured and installed, its prefix
moved to a Unicode path, and **its entire original private source and build
directories deleted**. Installed commands run from a foreign Unicode working
directory with no `HAMMOND_*`, `PYTHONPATH` or `PYTHONHOME` assumptions. Python
uses `-B -S`, disabling site-package loading and bytecode writes. An import probe
checks all ten observed module locations under the relocated package.

The AST dependency check admits only standard-library imports or an explicitly
packaged sibling. The installed execution then exercises the actual closure,
including the source-observing job/study/replay modules. Fourteen actual CLI
processes and one import-probe process run after the private source/build removal.

| Installed operation | Observed required result |
| --- | --- |
| Capture-v1 planned declaration | Exit 0. |
| Readiness of the plan | Exit 3; `planned`, 21 checks. |
| Planned corpus | Exit 3; `inconclusive`. |
| Complete demo corpus byte/audio audit | Exit 0; `pass`, exact original index digest. |
| Raw reference inspection | Exit 0; 4 Hz, one channel, four frames, exact raw/decoded identities, DC 0 and RMS 1. |
| Three jobs | Exits 0, 3 and 1; exact 0.25/0.25/0.5 FS metrics and declared closed intervals. |
| Mixed study | Exit 1; all three complete jobs retained, one of each outcome, validation count 3, work 12/12. |
| Three job replays and study replay | All exit 0 with exact complete report matches; original pass/inconclusive/failed statuses remain explicit. |
| New demo generation | Exit 0; 16 files, 32,831 bytes, byte-identical archive, `execution: not_run`. |

Every job's observed source digest/size is independently checked against its
installed module bytes. Explicit report files equal stdout. Canonical reports
remain UTF-8/LF under an ASCII-configured terminal environment; the audio tool
retains its separate compact-output format. Every physical/provenance claim
checked in jobs and replay summaries remains `not_established`.
All 57 package files are unchanged after the full operation sequence.

## Existing OfflineTools compatibility

The existing `tests/test_install.py` was also executed without modification
through a private **current** ordinary configuration that includes the new
CaptureTools helper. This separate probe reused complete executable/profile
artifacts from root's already qualified frozen wave-5 build, not stale objects
linked with changed headers. Ninety-five native, data, fixture, plotter and
legacy-install source files were checked byte-identical to that frozen source
before reuse. The assignment note retains all six copied artifact identities.

Both existing methods passed: actual 23-file installation/relocation/render/
metadata/trace/plot behavior, and complete-prefix preflight preservation.
The new component does not appear in that installed 23-file inventory. The
old module and test themselves remain unchanged. This is compatibility evidence
for those complete artifacts and current installation rules; it is not a newly
compiled native source gate or native device qualification.

## Results, failure history and next gate

Runtime: CPython 3.12.14, CMake/CTest 4.4.4 and GCC 14.2.0 configuration on
Linux x86_64. The final maintained installation suite passed **16/16 methods
in 6.982 seconds**, with zero failures, errors and skips. The separate unchanged
OfflineTools suite passed **2/2 methods in 6.631 seconds**, also without skips.

The first 16-method run had one **test-harness failure** in 9.399 seconds: the
AST check incorrectly required absolute imports. `compare_capture.py` already
supports `from .capture_common import ...` as a package-mode fallback. The test
was corrected to resolve a one-level sibling against the same explicit packaged
module set. It still rejects undeclared local or external dependencies. The
initial source hash and exact failure are retained in the assignment note.
All actual install/relocation cases passed in that first run; no producer,
guide, package inventory, numerical expectation or threshold changed.

Root should integrate this test into the coherent configured gate, preserve the
existing install suite, update shared status/handoff/accounting and publish under
the standing non-force workflow. Later edits to a packaged module or contract
require the affected installed checks again. Native Windows/macOS execution,
hosted CI, minimum-version Python/CMake execution, adversarial races, physical
acquisition, permissions, calibrated metrology, listening and full release remain
separate gates. Packaging and successful replay do not discharge them.

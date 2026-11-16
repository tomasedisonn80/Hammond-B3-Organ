# Contact-grid conversion installation — independent acceptance

A30 independently exercised the real `ContactGridConversionTools` CMake rules
against the admitted [conversion contract](../CONTACT_GRID_CONVERSION_CONTRACT.md)
and [installation contract](../CONTACT_GRID_CONVERSION_INSTALL.md). **The named
installer passes this bounded installation/runtime scope:** 13 test methods,
93 real child processes, zero failures/errors/skips on Linux. The final suite
took 9.780 seconds internally (9.929 seconds in the enclosing process).

This accepts explicit package copying, preflight and relocation behavior at the
identities below. Independent numerical/native correspondence, audio accuracy,
hosted operating systems, physical fidelity and whole-interface parity retain
their separate gates. No production file or original package was changed.

## Independence and exact inputs

The new [test](../../tests/test_contact_grid_conversion_install.py) declares the
five-file inventory from the contract. It does not import the production
converter, the A23 smoke, another installation test, or installer variables to
construct expected outcomes. It uses actual CMake installation, exact byte and
filesystem snapshots, real child interpreters and a separately declared original
48-file inventory. Reading A23 and the original harness informed platform/setup
conventions; it did not substitute their outcomes for this run.

Only a private `TemporaryDirectory` is mutable. Its `LANGUAGES NONE` project
includes unchanged copies of the shared installer, new converter installer and
original reference installer. It contains an unrelated ordinary-install sentinel
and deliberately unlisted Python/document/cache siblings. No native target is
built. Private source inputs total 369,045 bytes; the new installed payload totals
131,200 bytes. Every private project is removed by test cleanup. All 54 watched
checkout files retained their original hashes throughout the suite.

| Input | SHA-256 |
| --- | --- |
| Independent test | `6aab927980c8414ed7fe04a9c3c74e9c2164c8424082af82a2545bcf8bf2bbf7` |
| New install module | `50b9cf6c4a46ec41c74d6a76bc693c8633f8ae7f8229f4ab004051067b6e025c` |
| Numerical converter | `eff387f8457040ea67400dcb378ee1c2049b604d7c862fd6ca683b52c8f93797` |
| CLI | `56b73884ab44fc0694a763e6ffd576590c613926bfbc42f60ad0491c2caa935c` |
| Admitted conversion contract | `e5b4d26e9d74aef41fc5c6abe351597d43097da3faed5af6a26d0e3e557e18c0` |
| Complete passing receipt | `4173021ee8c516468716b2c80c94cc5eb80c9a912e65c5a1870ca2aeba4027c2` |

The [source audit](../development/2026-11-16-conversion-material/reports/A30-source-bindings.json)
compares the complete original 48-file reference payload plus its own and the
shared installer byte-for-byte with base
`a411268fd498f65c083203137831bf5afed83bd8`. All match. It also records CMake
3.31.6, the observed checkout HEAD and test syntax/whitespace checks. Source
hashes establish identity, not correctness or trust in a modified interpreter.

## Executed matrix

| Boundary | Independent observation |
| --- | --- |
| Explicit component | Exactly five ordinary files and their required directories; no unlisted sibling, cache, native target or unrelated default file enters the payload or prefix. Copies have identical bytes and different source identities. Existing unrelated file and empty directory remain. |
| Copy modes and permissions | Unset, empty and `COPY` modes succeed. On POSIX, privately executable 0755 sources become ordinary 0644 copies. |
| Every missing payload | All five files are separately withheld. Both absent and populated unrelated prefixes are unchanged in all ten refusals. |
| Empty/directory payloads | Each of the five inputs is separately empty and directory-valued; all ten refuse before prefix creation. |
| Linked sources | All five linked leaves, a dangling leaf and each internal ancestor (`tools`, `docs`, source root) refuse before copy. |
| Noncopy modes | Nine values, including all six documented link/link-or-copy variants plus lowercase, trailing-space and unknown values, refuse without destination changes. |
| Existing package | File, empty directory, populated directory and a real installed package are all refused and preserved. No merge or overwrite occurs. |
| Destination ancestors | File-valued prefix/data/organ ancestors refuse. Directory, file and dangling links at all four prefix-to-package positions cannot redirect a write; both link tree and external target remain unchanged. |
| Component isolation | With the new converter withheld, ordinary install still copies only its sentinel, unknown component creates nothing, and the actual original component copies exactly its 48 files. With an original-only fixture withheld, the converter still copies exactly its five files. |
| Data directory | Three relative layouts, including normalized backslashes and `.`, install correctly. Ten empty/absolute/drive/parent/list variants fail configuration under the new component's validator. |
| Multiple configurations | A private Ninja Multi-Config project installs both Release and Debug directly, without any build. |
| POSIX staging | `DESTDIR` uses the effective staged prefix. Reinstallation and missing-input refusal preserve the staged destination and do not create the nominal prefix. |
| Runtime relocation | The complete actual installation is renamed, private source/build are deleted, and the installed CLI runs from a foreign directory with poisoned local modules and `PYTHONPATH`. Exact certificate and package results follow below. |

The tests inspect exact destination bytes, modes, empty directories and link
targets without following links during preservation snapshots. They assert both
nonzero refusal and the component-specific diagnostic; successful unrelated
operations cannot satisfy the refusal assertions. The expected inventory is not
a broad recursive copy of the candidate's own manifest.

## Installed execution

The test first executes the source CLI on the unchanged original F02 48 kHz
fixture, then performs the actual CMake install into a custom data layout. It
renames that prefix, deletes its copied source and build, and executes:

```sh
python3 -B -E -s -S <relocated-package>/tools/convert_contact_grid.py \
  --input <external-work>/F02-48000-v1.json \
  --output <external-work>/relocated-certificate.json
```

Both real commands are silent and return 0. The installed certificate is
byte-identical to the source certificate: **33,678 bytes**, SHA-256
`77d084d531e81ce17cbde01a1b3d75d5430f95a4b04b6d5df1200b322cd5ba7e`. It retains
18 edges, two arrivals, 256 frames, original input byte identity, all four actual
module hashes, the actual contract hash, Python version and valid CGGRID1 text
hash. Its `audio_accuracy` stays `unqualified`. The relocated package remains
exactly five unchanged files, with no generated bytecode.

The foreign directory includes failing same-named module files, including a
`json.py`, and is also supplied through `PYTHONPATH`; `-E -s -S` supplies the
documented isolated invocation. This does not prove hostile-runtime security.
`-B` prevents writing caches but does not prohibit reading an existing valid
cache. The new trusted package contains none. Numerical correctness of F02
belongs to the separate independent numerical/native suites; this run verifies
distribution identity and execution.

## Original failure and correction

The [initial receipt](../development/2026-11-16-conversion-material/reports/A30-install-initial.json)
and [complete log](../development/2026-11-16-conversion-material/reports/A30-install-initial.log)
retain the first 12-method, 92-process run: ten subtest failures in one diagnostic
assertion, with no operational failure. CMake correctly rejected every invalid
data directory but wrapped `nonempty relative CMAKE_INSTALL_DATADIR` across a
line because this component's name is longer. The assertion incorrectly
required contiguous spaces. The [exact initial test](../development/2026-11-16-conversion-material/reports/A30-install-initial-test.py)
is retained.

The correction normalizes only diagnostic whitespace. Exit status, component
identity, directory validity and all filesystem assertions remain mandatory.
Before final acceptance, the suite also tightened whole-prefix inventory and
added the meaningful 0755-to-0644 test. The [final full log](../development/2026-11-16-conversion-material/reports/A30-install-verified.log)
and [passing receipt](../development/2026-11-16-conversion-material/reports/A30-install-verified.json)
retain the observed 13-method result. No installer, payload, threshold or source
input was repaired to make it pass.

## Reproduction and remaining gates

From the repository root, with Python 3.10+ and CMake 3.21+ available:

```sh
python3 -B tests/test_contact_grid_conversion_install.py
```

Set `HAMMOND_CONTACT_GRID_CONVERSION_INSTALL_REPORT` to a **fresh** JSON path to
retain per-process argv, cwd, timings, statuses, stream sizes/hashes, bounded
refusal diagnostics and source bindings. Existing receipts are refused. The
normal repository discovery names this test
`python_test_contact_grid_conversion_install`; the existing module supplies
`HAMMOND_TEST_CMAKE`, generator/make-program/configuration and a 180-second
CTest limit. Each child process has a 45-second external timeout. Root owns
reconfiguration and coherent CTest integration.

Linux/Python 3.12.14/CMake 3.31.6 is the observed platform. Symlink creation,
POSIX permissions and `DESTDIR` have explicit platform limitations; unavailable
symlink or multi-configuration facilities are reported as skips, never passes.
Hosted Windows/macOS execution remains root's next source-specific gate.

This is preflight preservation, not a transactional package installer. A later
copy/disk failure can leave a partial new installation; concurrent hostile
directory replacement and power-loss durability were not tested or claimed.
The tiny fixture validates the included real modules, not root's complete native
build. Physical, live audio, callback, accessibility and full-UI targets are
unaffected by this bounded acceptance.

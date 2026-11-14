# Assignment 38 — independent CaptureTools installation acceptance

Actual identity: **`/root/cal_w7_a38`**, assignment **38**, logical wave **7**
of the `2026-11-13-calibration` session. Work completed on 2026-11-14 UTC;
the date change does not create another assignment or session.

Owned files are only `tests/test_capture_install.py`,
`docs/CAPTURE_INSTALL_REVIEW.md` and this note. No producer, CMake module, frozen
guide, schema, fixture, shared document, ledger or Git ref was changed by this
worker. All filesystem mutations and deletions affected private copies.
Root owns acceptance, integration and publication.

## Context and reviewed source

Working directory: `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
The initial checkout was local commit
`1aef68489fc18b860bbab8fd06a65fdde8a4d6cd`, tree
`5ed86b2f0eeee4e00926aebaaf4432ec61760328`, with installation/replay work
uncommitted. Root later published and selected
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`; local `origin/main` matched that
observation. Neither commit alone identifies the then-uncommitted install
helper, replay producer or this acceptance. Their exact byte identities below
are the qualification inputs. This worker performed no push or hosted-CI claim.

Read `AGENTS.md`, README/current status/next steps/log, the calibration scope and
handoff, other active ownership boundaries, the M0–M9 plan and retained atlas
review. Read the complete `CAPTURE_TOOLS_INSTALL.md`, existing
`InstallHammondTools.cmake` and `tests/test_install.py` before grading, plus
relevant job/audio/demo report contracts. Read fresh extracted atlas text on
pp. 484 and 486: declared decision rules, retained outcomes, exact code/setup
identity and bounded release claims. The six earlier actual readers own the
complete 500-page coverage; this assignment does not claim another full reading
or original-image inspection.

The full install guide was cleared at SHA-256
`ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590` before
grading. The literal 57-file inventory, module closure, vectors/digests and
outcome expectations were authored before inspecting the producer's list/code.
Assignment 37 then supplied its formal ready hashes and author evidence. A
possible CMake PATH prerequisite was checked: its initial helper already
supplied the correct guarded CTest environment and timeout, so no source change
was needed. A missing planned implementation was never graded as a failure.

## Exact qualified identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
| `CMakeLists.txt` | 16,412 | `98843ed4e797cc4ce7caac14d995d8962492ed50b8756d3a6d8b19d0c316aed0` |
| `docs/CAPTURE_TOOLS_INSTALL.md` | 17,824 | `ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590` |
| Final `tests/test_capture_install.py` | 34,023 | `a797443fe7d208bbdaebedae836edca988524d8371938dd95e9368738f26bb74` |
| Existing `cmake/InstallHammondTools.cmake` | 10,971 | `97cb6ec2c7073e3c50a1b00106317ddd726a2fb01e580dc96b55be0044140355` |
| Existing `tests/test_install.py` | 36,292 | `66c183f2893f717fe3ba76f264f05bd9c855ccb056672801af1885ea5c9baeac` |
| `tools/validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_corpus.py` | 39,220 | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| `tools/capture_readiness.py` | 11,247 | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| `tools/capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `tools/make_capture_demo.py` | 22,329 | `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` |
| `tools/verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |

All 56 copied source payloads and the two install helper sources are compared
with the live originals at suite teardown; they remained unchanged. The generated
README is separately checked and compared across configurations. The helper,
guide, root include and ten runtime module identities were confirmed again after
qualification. The test has exactly 16 maintained methods; subcases, reruns and
the old two-method suite are not additional new methods or workers.

## Commands and observed results

Runtime: **CPython 3.12.14**, `Linux-6.18.57-x86_64-with-glibc2.41`,
CMake/CTest **4.4.4**, GCC **14.2.0** during ordinary project configuration.
No package, SDK or dependency was installed. No native target was built by this
assignment's new-component suite.

From the working directory above:

```sh
HAMMOND_TEST_CMAKE=/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake python3 -B tests/test_capture_install.py -v
```

| Execution | Result |
| --- | --- |
| First graded source, SHA `2028fed893f7ad8aa5698ea7152f7cc1079e7b595cc28d0b0ffc5edb9102400c` | 16 methods in 9.399 seconds; 15 passed, one AST-oracle failure, zero errors/skips. |
| Final source at `a797443f…` above | **16/16 passed in 6.982 seconds**; zero failures/errors/skips. |
| Unchanged existing OfflineTools suite through private current configuration | **2/2 passed in 6.631 seconds**; zero failures/errors/skips. |

The full final test file passed `ast.parse`, strict UTF-8, LF-only content, one
final newline and no trailing whitespace. These are formatting checks, not new
behavioral acceptance methods.

### Preserved first-run failure

The initial AST dependency check used `assertEqual(node.level, 0)` for every
`ImportFrom` node. It failed with `AssertionError: 1 != 0` at the unchanged
`compare_capture.py` fallback:

```python
from .capture_common import DataError, parse_json_bytes, validate_json_value
```

That import names the already packaged `capture_common` sibling; direct installed
execution had already succeeded. The reviewer corrected the oracle to permit
one-level relative imports only when their sibling belongs to the same explicit
ten-module set. Undeclared siblings, outer-package imports and nonstandard
external dependencies still reject. No producer, contract, inventory, numerical
result or threshold was changed. The original test bytes remain locally at
`/workspace/scratch/c9f3ead4c910/a38-initial-install-test.py`; this note retains
the exact counterexample and original identity independently of scratch lifetime.

Before grading, authoring inspection changed generated-README discovery from
a top-level-only search to recursive basename discovery and removed a redundant
fault-hook parser. Those were fixture-construction corrections before the first
run, not concealed failing producer tests.

## Meaningful installed behavior

The [full review](../../CAPTURE_INSTALL_REVIEW.md) records the detailed reasoning.
Executed new-component checks include:

- Actual ordinary private project configuration with optional native adapters
  disabled, exact CTest CMake environment, no native target output and exact
  57-file installation/manifest. Every copied source/data byte matches its private
  original; the unchanged demo remains 16 files and 32,831 bytes.
- Standard-library or declared-sibling import closure, repeated configuration,
  Release/Debug/arbitrary source-only configuration selections, custom relative
  DATADIR, six invalid directory forms, COPY/unset/empty versus rejected modes,
  explicit component isolation and actual POSIX DESTDIR staging.
- All 57 inputs individually missing before any destination write; empty and
  directory early/late inputs; source symlink; existing destination file,
  directory, complete package, valid/dangling links; unchanged unrelated files
  and link targets. Native link values are captured before/after rather than
  assuming Windows preserves the requested path spelling.
- A reached, deterministic abort after the first real copied file. The partial
  package and injected other-writer marker remain and the log discloses the
  partial-copy boundary. This does not claim an actual disk-full or hostile race.
- Actual relocation to Unicode paths followed by deletion of the entire private
  source/build trees. Fourteen CLI processes and one import probe run from a
  foreign Unicode directory with `-B -S`, no project/Python path assumptions and
  an ASCII-configured terminal. All ten module locations resolve inside the
  moved package, with no source fallback or site-package dependency.
- Planned validator/readiness/corpus exits 0/3/3; complete demo corpus exit 0;
  raw reference inspection and independent raw/decoded preimages; job exits
  0/3/1 with literal 0.25/0.25/0.5 FS metrics; the complete mixed study exits 1
  with work 12/12 and all three results retained. Four replays match exactly,
  including failed and inconclusive engineering outcomes. New demo generation
  remains `execution: not_run` and equals all original bytes.
- Independently checked installed source observations, exact report-file/stdout
  bytes, all physical/provenance fields remaining `not_established`, and all
  57 installed files unchanged after execution.

All native Linux symlink cases and POSIX staging executed; there were no skips.
The maintained suite reports explicit skips for unavailable link capabilities
or unsupported Windows DESTDIR rather than inferring a native pass.

## Existing 23-file component probe

The separate private root was
`/workspace/scratch/c9f3ead4c910/a38-legacy-component-y55syp4f`.
It used the actual current top-level configuration and CaptureTools helper,
then copied the five complete executables and profile from root's frozen
`w5-combined-build`. Their source checkpoint is
`fd0fb58d2f882aa76c7e40e510f44766f762727c`, tree
`3329cf68bb9ea84479e254934778935bb5c44773`, retained publicly as the equivalent
source tree of commit `340903a333ecfa5c684620ae8ac54e2e917a6217`.

Before reuse, 95 existing files under `src`, `include`, `data`, the original
fixture subtree, tool C++ inputs, both plotters, the old install helper and its
test were verified byte-identical between that frozen source and the current
checkout. No object was relinked or mixed with a different header. These are
complete already qualified executable artifacts used to test new installation
composition, not a fresh native source-build qualification.

| Reused complete input | Bytes | SHA-256 |
| --- | ---: | --- |
| `hammond_render` | 135,320 | `9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6` |
| `hammond_model_info` | 46,976 | `3471217c9f35530ea19c10fcff8508fa6a8dd4ae29c920e6ef5e8d1cb6bcc991` |
| `hammond_parameter_info` | 41,176 | `e66ebd2334836874f045d1a92fd456796b1e74bc495804220abfd8f3c7ed0e23` |
| `hammond_console_trace` | 122,704 | `7b968ac5d441031bda2280d84104629066937422953c6434c5350ef7f885d969` |
| `hammond_pedal_trace` | 126,864 | `9bd2ce87bb0f8f4806d8e0c48aa62573e212fd8a6b6690cb34a721431692bf54` |
| `nominal.b3p` | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The unchanged old test was executed as:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a38-legacy-component-y55syp4f/source/tests/test_install.py -v
```

Its ordinary `HAMMOND_TEST_CMAKE`, `HAMMOND_TEST_BUILD_DIR`, configuration,
five executable paths, profile, bindir and datadir variables pointed at that
private configuration and copied complete inputs. Both maintained methods pass
the actual 23-file relocation/render/metadata/trace/plot behavior and preflight
preservation. CaptureTools files do not leak into the old inventory. The
unchanged old module/test hashes are listed above.

| Local observation | Bytes | SHA-256 |
| --- | ---: | --- |
| `a38-capture-install-final.log` | 2,437 | `f5ad3bb0882d0b209b2195cea345a39c7655a985276c3187cb96f9de63644695` |
| `a38-existing-offline-install.log` | 314 | `b3d1b2b1fd81c772bc889c7c094349a2aeba134af749e3b6ae693b0faaba0daa` |
| `a38-existing-offline-install.json` | 1,313 | `e50f026773bb91dc6728f1f165bc5a571cf617aaf1b5e2a45e458e42a3db2f6c` |

## Handoff and limits

The implementation is accepted within the stated Linux source/package scope.
Root and assignment 37 have the exact results and identities. Root should add
the independent suite to its coherent source gate, preserve the existing install
suite, update shared status/next steps/handoff/ledger, and commit/push completed
work under the standing main workflow. The helper already supplies discovery
environment and timeout when the independent test exists. Keep all ten modules,
all original archive bytes and deliberately nonzero engineering outcomes together.

No native Windows/macOS execution, hosted CI, Python 3.10 or CMake 3.21 runtime
test, full hostile-filesystem stress, actual disk-full/cancellation test, native
SDK/device/host qualification, rights clearance, physical acquisition, calibrated
uncertainty, listening or instrument-fidelity acceptance is claimed here.
Installation is local engineering readiness. A successfully reproduced failed
report remains a failed engineering result and supplies no physical evidence.

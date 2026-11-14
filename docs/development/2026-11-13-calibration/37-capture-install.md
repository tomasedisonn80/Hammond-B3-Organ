# Assignment 37 — separate relocatable CaptureTools component

Actual worker: **`/root/cal_w7_a37`**, assignment **37**, logical wave **7** in
the `2026-11-13-calibration` session. Execution continued across UTC midnight;
the completed author observations below were inspected on **2026-11-14**. This
is one actual assignment, separate from the independent installation reviewer.

## Ownership, source basis and contract freeze

Owned changes are exactly:

- `cmake/InstallCaptureTools.cmake`.
- `docs/CAPTURE_TOOLS_INSTALL.md`.
- This assignment note.
- One expressly released `include(cmake/InstallCaptureTools.cmake)` line in
  `CMakeLists.txt`, adjacent to the existing offline-install include.

No existing production Python module, schema, test, other CMake module, shared
status/handoff, assignment ledger or Git ref was changed by this worker. Root
owns integration, acceptance, shared records and publication. Independent
assignment 38 owns maintained installation tests and its own acceptance note.

Read `AGENTS.md`, the active scopes and calibration handoff/session, current
README/status/next steps and latest log, the M0–M9 plan and atlas review, the
entire existing `InstallHammondTools.cmake` and `tests/test_install.py`, the
offline installation guide, installed-module import closure and the complete
frozen replay contract. Fresh extracted atlas pp. 484–486 were also read. Their
separate acceptance, distribution and identity/change-control requirements
support this packaging boundary; they do not prescribe this component or its
57-file layout. The session's six earlier readers own the full 500-page coverage.
This assignment does not claim another complete PDF or primary-source review.

Root approved the proposed exact inventory, explicit-only component, relative
data root, fresh payload leaf, preflight and quiescent-copy limits before code.
The complete install guide was then frozen **before implementation and grading**:
17,824 bytes, SHA-256
`ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590`.
Assignment 38 independently read and cleared that guide before inspecting the
producer. It remains unchanged.

The first checkout observation was `fd0fb58d2f882aa76c7e40e510f44766f762727c`,
tree `3329cf68bb9ea84479e254934778935bb5c44773`. Root continued its separately
owned publication while this work proceeded. The **actual author source copy**
was made from a `git archive` of
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`, followed by an explicit coherent
overlay of the 56 copied package source files, new helper and one-line root
CMake change. Each overlay file was hashed and checked unchanged around copying
and again after execution. This base commit alone does not identify the then
uncommitted installer or replay source; exact file identities below do.

## Implemented package and preservation boundary

`CaptureTools` is a separate, explicit `EXCLUDE_FROM_ALL` CMake component under
`<prefix>/<CMAKE_INSTALL_DATADIR>/hammond-b3-organ/capture-tools`. Its repository-
shaped layout preserves relative paths between tools, data, guides and the demo.
Ten copied Python modules close every actual local import; all other imports
are from Python's standard library. The component uses no native target output,
profile compilation, network, package installation or audio device.

The **57 actual files** comprise ten Python modules, eight data files, sixteen
unchanged demo files, twenty-one guides/contracts/context documents, one fixed
generated README and the unchanged third-party notice. Every source is explicitly
listed; no source-directory glob or recursive directory copy can silently add a
new dependency. Source/data bytes are copied unchanged. The root README contains
only fixed relative instructions and no original checkout/build/prefix value.

The existing `OfflineTools` include remains in place and unchanged. The new
helper follows it and uses its established relative-directory validation. Every
new install rule, including preflight, is scoped to `CaptureTools` and excluded
from ordinary unqualified installation. No old target, destination or component
rule is modified. The existing module and its maintained 23-file test retain
their exact source hashes listed below. Assignment 38 separately executes old-
component preservation; this author note does not borrow that pending result.

Preflight checks all 57 inputs before any component destination write. It rejects
missing, empty, directory and CMake-observed symlink payloads and non-COPY install
modes. The complete destination leaf must be absent, including an existing file,
directory or dangling symlink. Other prefix contents and other components remain
independent. A pre-copy log statement explicitly discloses that later failure can
leave a partial new package and that no automatic cleanup occurs.

This is a quiescent-source/destination operation. Ordinary CMake observations
and copy semantics are not a hostile-filesystem sandbox, native reparse proof or
atomic multi-file transaction. A concurrent creator after preflight is outside
that promise. Later copy failure/cancellation can leave a partial new directory;
the helper does not recursively delete it. These limits were frozen in the guide
before code, rather than added to explain a failing test.

The new helper also supplies exact CMake/build/configuration/data-directory
environment values and a 180-second timeout when independently authored
`python_test_capture_install` is discovered. The CMake executable is not on this
environment's ordinary PATH. Assignment 38 and root requested that integration;
it was already present in the initial helper and required no later source edit.
This is test setup/discovery, not a runtime dependency or a failed package test.

## Actual author execution

Runtime: **Python 3.12.14 / Linux x86_64**, CMake **4.4.4**. The ordinary copied
project configured its existing C++ targets using the available compiler, but
no native target was built for this package. Both `hammond_render` and
`nominal.b3p` were asserted absent after configuration. No package/dependency
was installed and no network operation was needed.

The author harness was run once from
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a37-install-author.py
```

It passed **10 author check groups and 26 actual subprocess commands**, checking
the exact **57-file / 687,338-byte** initial installed payload. These are author
smoke groups and commands, not independent acceptance methods. The first graded
author run passed with no unexpected failure and no producer repair.

The copied source/build/prefix paths contained spaces and `é`. The moved prefix
and report paths also contained `音`. The source copy was coherent and private;
no live repository source or another worker's build was renamed or mutated.
Actual configuration/install commands, with the available CMake binary expanded,
were equivalent to:

```sh
cmake -S "/workspace/scratch/c9f3ead4c910/a37-install-author/source é with spaces" -B "/workspace/scratch/c9f3ead4c910/a37-install-author/build é with spaces" -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --install "/workspace/scratch/c9f3ead4c910/a37-install-author/build é with spaces" --config Release --component CaptureTools --prefix "/workspace/scratch/c9f3ead4c910/a37-install-author/prefix é with spaces"
```

The first configure was repeated successfully. A second private build used
`-DCMAKE_INSTALL_DATADIR=assets/reference -DCMAKE_BUILD_TYPE=Debug`; installing
with `--config Debug` and `CMAKE_INSTALL_MODE=COPY` produced exactly the same
57 file bytes at its custom location. The default configure/install used unset
`CMAKE_INSTALL_MODE` and no `DESTDIR`.

| Actual command group | Observed result |
| --- | --- |
| Ordinary configure and repeated configure | Both exit 0; no native output or compiled profile built. |
| Fresh default CaptureTools installation | Exit 0; exact 57 paths, all 56 copied-source byte identities and fixed README verified; no native/old-component payload. |
| Repeat installation to the completed root | Exit 1 with existing-destination diagnostic; every prior path/content preserved. |
| Late-listed `half.f32` replaced separately by missing, empty, directory and symlink cases | Four expected exit-1 rejections before destination writes; unrelated prefix marker retained; original private bytes restored after each case. |
| `CMAKE_INSTALL_MODE=ABS_SYMLINK` | Expected exit 1 before writes; prefix snapshot unchanged. |
| Destination leaf separately a regular file and dangling link | Two expected exit-1 rejections; leaf and all unrelated prefix contents preserved. |
| Custom data directory / Debug configure and COPY installation | Both exit 0; identical full inventory and bytes beneath `assets/reference`. |
| Installed validation, readiness, planned corpus and full demo corpus audit | Exits 0, 3, 3, 0; expected planned/inconclusive boundaries retained. |
| Installed pass, inconclusive and failed jobs | Exits 0, 3, 1; complete report status/physical limits, stdout and explicit output-file bytes agree. |
| Installed replay of each of those three jobs | All exit 0 with complete `match`; each underlying pass/inconclusive/failed status remains unchanged, sources/runtime agree. |
| Installed mixed study and its replay | Study exit 1 preserves ordered pass/inconclusive/failed reports and exact counts; replay exit 0 retains the underlying failed status and equals its output file. |
| Installed generator | Exit 0, 16 files and `execution: not_run`; each generated file equals the unchanged retained demo. |

For all installed workflow processes, the original private source, build and
prefix paths had first been **renamed away and asserted absent**. The complete
prefix was moved to its Unicode destination, and execution used absolute copied
script/input paths from an unrelated working directory. `HAMMOND_*`,
`PYTHONPATH`, `PYTHONHOME`, `DESTDIR` and install-mode assumptions were removed;
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONNOUSERSITE=1`, `PYTHONIOENCODING=ascii` and
the interpreter's explicit `-B` were used. No new package file or cache appeared.

The study retained exactly three jobs, one of each outcome, validation role 3
and zero other roles. The whole installed package was hashed before and after
execution and remained unchanged. Complete saved report bytes were passed to
the installed verifier; the underlying expected failures were never discarded
or converted into a passing engineering verdict. Actual import AST inspection
confirmed the ten-module closure plus standard-library names.

## Qualified implementation identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| New `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
| Frozen `docs/CAPTURE_TOOLS_INSTALL.md` | 17,824 | `ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590` |
| Root `CMakeLists.txt`, with only the released include | 16,412 | `98843ed4e797cc4ce7caac14d995d8962492ed50b8756d3a6d8b19d0c316aed0` |
| Unchanged `cmake/InstallHammondTools.cmake` | 10,971 | `97cb6ec2c7073e3c50a1b00106317ddd726a2fb01e580dc96b55be0044140355` |
| Unchanged `tests/test_install.py` | 36,292 | `66c183f2893f717fe3ba76f264f05bd9c855ccb056672801af1885ea5c9baeac` |
| Replay producer used for installed execution | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |
| Generated installed root README | 4,448 | `9a7b8bdf85fbd2ed212342f0338a6e2ad8927191f0ea6e875da3497a71fbf715` |

The source/guide identities were checked unchanged at final inspection. Root's
concurrent commit/publish operation changed local Git context, not these tested
bytes. The installed source inventory below records every module and dependency
actually used; no earlier report alone qualifies later source edits.

## Scratch evidence identities

The author harness and raw command logs are local development observations;
the retained contract, exact inventory, source identities and observations in
this note are durable. Assignment 38 supplies independently authored maintained
tests rather than importing this harness as independent acceptance.

| Local observation under `/workspace/scratch/c9f3ead4c910/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `a37-install-author.py` | 15,198 | `46e1d0373679fa3351c34ca68094e5736424b0d9882298cef16c60982d9effa3` |
| `a37-install-author/summary.json` | 42,595 | `27081cb630a1784f549649a02af2df8f999364e9468ad242a2f003b44f3070d5` |
| `a37-install-author/commands.json` | 22,430 | `917c73c0a0025c61b497060082b666adbb326ff81ce8e962d5227c6cd3a884fb` |
| `a37-install-author/source.tar`, base archive before overlay | 39,024,640 | `27b617a5ff1a890f5499e022581b130851de5e60fc677e3311b369be98fbcf4c` |

Each command record retains its actual argv, working directory, expected and
observed exit, complete stdout/stderr byte lengths and SHA-256. Raw streams are
separate files under `a37-install-author/logs/`. There was no failed first test
run or oracle adjustment. One prose-typing error and an initially mismatched
patch context were corrected before the guide hash was frozen; no contract,
source or test expectation changed in response to a graded result.

## Next integration and unrun scope

Root and assignment 38 received the frozen contract, ready helper/include
identities and actual author results. Root should accept the package with the
independent installation result, qualify a coherent configured source including
test discovery and the unchanged old component, update shared status/next steps/
handoff/log/ledger, and commit/push under the standing expected-head workflow.
New source or notice/document bytes change the package inventory and require
an explicit new package identity; the old table remains dated evidence.

This worker did not execute native macOS or Windows installation, a multi-config
generator, `DESTDIR` staging, an actual later I/O/cancellation failure after
copying began, a hostile filesystem race, hosted CI, old OfflineTools execution,
native binaries or real audio devices. The two tested Debug/Release builds are
single-configuration CMake builds. Source review and documented CMake behavior
are not substituted for those unrun cases. Independent acceptance may exercise
additional boundaries and must retain its own results.

The installer neither signs a package nor provides a project-wide license.
No acquisition permission, calibrated scale/time, physical corpus, untouched
holdout, model fitting, listening, specimen fidelity or production distribution
gate is closed by copied files or matching synthetic replay. All demo and
report evidence boundaries remain unchanged.

## Observed complete installed inventory

The following 57 rows identify the actual initial installed package. Paths are
relative to `capture-tools`; total size is **687,338 bytes**. Later source or
documentation changes require a new inventory rather than rewriting this one.

| Installed path | Bytes | SHA-256 |
| --- | ---: | --- |
| `README.md` | 4,448 | `9a7b8bdf85fbd2ed212342f0338a6e2ad8927191f0ea6e875da3497a71fbf715` |
| `THIRD_PARTY_NOTICES.md` | 16,366 | `3d4acfae5c0c83b5184d3806b1ce70040beeaf027da28b541ab220e764ae4faa` |
| `data/capture-corpus.schema.json` | 3,690 | `420037ea76f22dbd559b4005f1514bcf59d21310349800f138ce5b93c43707c9` |
| `data/capture-job.schema.json` | 3,574 | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |
| `data/capture-planned-example.json` | 3,223 | `35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac` |
| `data/capture-policy-synthetic-example.json` | 1,047 | `e091dca3b3fdf3c3675383096007c5f95b848fa6294dedd3906705d061884316` |
| `data/capture-policy.schema.json` | 12,377 | `2a1b0fd959f5f760d9460c7c960d48d7d4adbbd27918c9b4df6849646c8a9678` |
| `data/capture-study.schema.json` | 2,102 | `1805ad62f357ec7f828591dce0a968391beba42418b9ea4f20adfe4139389e3d` |
| `data/capture.schema.json` | 32,414 | `51fbfdbcc92d9cdb3b71d4b55618840a806e2847b49c93e6aa7d926621661a74` |
| `data/corpus-planned-example.json` | 466 | `9c23a5faf002472d50e9c4e5e923bdb46e95091ee026288d98a91b785a7c4e2e` |
| `docs/CALIBRATION_SCOPE.md` | 3,139 | `a6d9f05dd5cf24de297210e65597e15d02cd2197f422b9da2889c0211643bb35` |
| `docs/CAPTURE_AUDIO.md` | 9,078 | `b62ab52596532140845586a66ba0da7781b92da60fa26678afc7ff0c8851eb14` |
| `docs/CAPTURE_AUDIO_CONTRACT.md` | 35,980 | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| `docs/CAPTURE_COMMON.md` | 3,923 | `5ae7a7fffb05829c8758d82ac74460ca14834acbe1fa4f2b6e4b1648623bb805` |
| `docs/CAPTURE_COMPARISON.md` | 8,399 | `ab3b0e89bd94e26246fbff70dcc7982e93f2747ee953c83b428da69015fca6ea` |
| `docs/CAPTURE_COMPARISON_CONTRACT.md` | 28,479 | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| `docs/CAPTURE_CORPUS.md` | 10,802 | `ae3501ce95a6557ff5cdc7a975703ce43708101d20c1ebe18593c80346eb79e6` |
| `docs/CAPTURE_CORPUS_CONTRACT.md` | 31,880 | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| `docs/CAPTURE_DEMO.md` | 13,389 | `c60283e526a7e1f5f11e628536d0295b9a614038b411de6642e227c1c6ae3008` |
| `docs/CAPTURE_FORMAT.md` | 13,696 | `618c20e4c6d2b204c69cdad006d69bfd93638de7c6d711b230452fea78b88177` |
| `docs/CAPTURE_JOB.md` | 11,741 | `8e51706e2f2d10540dde62071cbfa157339cbc8ce162b57cdbd7ab754c3581f6` |
| `docs/CAPTURE_JOB_CONTRACT.md` | 29,508 | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| `docs/CAPTURE_JOB_REVIEW.md` | 13,719 | `9218ca2e0fd72ff07ff1b838cac2dd153ce8e5b1ece18e20cbcc24d3b2c2f271` |
| `docs/CAPTURE_POLICY.md` | 11,526 | `ea762fb1a65c99727fbcdf573ff47e86b004089d37d71ff72067f83e30c72a4c` |
| `docs/CAPTURE_PROTOCOL.md` | 31,020 | `9fbe033601f4685248e480d7114ca82e47fab1d4c7f2768b2551225ae12b97b5` |
| `docs/CAPTURE_READINESS.md` | 14,203 | `e3eb647244c62d600e58d37a83f99db165256e4a69cf89e210f354fc12b55b0b` |
| `docs/CAPTURE_REPLAY.md` | 18,044 | `1d855c9c734f0f8e9c3d73e4a735c9ef5d86066b734d1a74b95426545f3d3d88` |
| `docs/CAPTURE_STUDY.md` | 19,910 | `a60d8c6a92356f2381ea61ba39c0dab50048b0f88ee6dc75bf943c7f5c5198e3` |
| `docs/CAPTURE_TOOLS_INSTALL.md` | 17,824 | `ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590` |
| `docs/CAPTURE_VALIDATION.md` | 5,436 | `4a16cd0e1c09944ad8554db6b17dbdd3265120ce0c02169c2d23359990313b4d` |
| `docs/PLAN.md` | 8,035 | `92fb19e2d8793bca803b3611ae38fa7b5034ff40b30b923fed9981ec7c7d3bde` |
| `examples/capture-demo/EXPECTED.json` | 4,425 | `8b3ade3def7f51119b90f5a65bc9fa3bf7c46ab561929a60acdd973245793396` |
| `examples/capture-demo/README.md` | 6,127 | `867618f49b41d88eaba13a86048190d4f0db30bc34b453adb9d51ce8fd1e4b08` |
| `examples/capture-demo/corpus/audio/half.f32` | 16 | `36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758` |
| `examples/capture-demo/corpus/audio/quarter.f32` | 16 | `bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2` |
| `examples/capture-demo/corpus/audio/reference.f32` | 16 | `fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402` |
| `examples/capture-demo/corpus/corpus.json` | 1,295 | `1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361` |
| `examples/capture-demo/corpus/half.json` | 4,589 | `281945a1b21b473949eb1049c489f21d2e506c96fd859412a97737631d94d0f5` |
| `examples/capture-demo/corpus/quarter.json` | 4,599 | `2727e5b2ef50652d96be9e2b55880eba9390c1b6804addc7af2d39878f8f7e54` |
| `examples/capture-demo/corpus/reference.json` | 4,599 | `e3d5761fa8f6d3351c82fdc72a13df8c8db9458f07fba401cb22f1fe85fef970` |
| `examples/capture-demo/job-fail.json` | 787 | `f2fad01bdafbebd14517cb0d9f6e8b3ce8e1541135358308818671327c27e703` |
| `examples/capture-demo/job-inconclusive.json` | 806 | `d66a0d0f5762ed6f961e9db2a36426e0b308973547d62ee25be9bf44f42568c6` |
| `examples/capture-demo/job-pass.json` | 790 | `63f83d706b412cc4cd7a76957f924cb9c6970436593fdae3e0fd8724dea66e45` |
| `examples/capture-demo/policy-fail.json` | 1,346 | `c1025c652a3b85be75b10420ae87aca2db6bd8bf748e0218e5b2cd260e77ee3c` |
| `examples/capture-demo/policy-inconclusive.json` | 1,362 | `23684a20f7cf263645fc7b4124804d248a114fba79973280818986ee48dd5e43` |
| `examples/capture-demo/policy-pass.json` | 1,348 | `8300754d2088849d6a8fe042f248543e1c9965229b4ad9cc220f45bfa31cccc5` |
| `examples/capture-demo/study.json` | 710 | `725e91cd3264d420018f2a6d269a27ed47f941e0e17b0abd09c81a71dafb717a` |
| `tools/capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/capture_corpus.py` | 39,220 | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `tools/capture_job.py` | 24,302 | `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` |
| `tools/capture_readiness.py` | 11,247 | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| `tools/capture_study.py` | 16,740 | `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/make_capture_demo.py` | 22,329 | `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` |
| `tools/validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `tools/verify_capture_report.py` | 23,380 | `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` |

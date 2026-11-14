# Assignment 41 — composition consistency

## Assignment, authority and outcome

- Actual assignment: **41**; logical wave: **7**; worker: `/root/cal_w7_a41`.
- Owned repository files: this note and
  [CALIBRATION_COMPOSITION_CONSISTENCY.md](../../reviews/CALIBRATION_COMPOSITION_CONSISTENCY.md).
- Outcome: **220/220 targeted audit cases passed; no unresolved production,
  schema, example or dependency defect found; no repair requested**.
- No production source, schema, tests, CMake, shared status, ledger or Git state
  was changed by this worker. The parent owns integration, commit and push.

Read the repository agent rules, calibration and relevant component scope,
earlier [capture schema review](../../CAPTURE_SCHEMA_REVIEW.md), the full
[study](../../CAPTURE_STUDY.md), [replay](../../CAPTURE_REPLAY.md) and
[installation](../../CAPTURE_TOOLS_INSTALL.md) guides, current plan and relevant
handoffs. Inspected atlas pages 355, 364, 484 and 486. The session's six earlier
readers own its complete-PDF reading evidence; this worker does not claim a new
complete reading.

The linked review explains the substantive boundary decisions and limitations.
This note retains the actual execution material. Case counts are finite audit
cases, not new unittest methods. Sentinel work-limit cases check preflight and
never execute maximum audio/spectral workloads. All fixtures and mutations were
private; the installed demo and package were preserved byte for byte.

## Setup and observed source context

The successful run used Python 3.12.14 on Linux x86_64 and already available
`jsonschema` 4.26.0 as authoring-only audit tooling. No dependency was installed
or added to runtime/tests. The actual CMake executable was
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`
(version 4.4.4). CMake identified GNU C++ 14.2.0 and the Python 3.12.14 interpreter.
No native target was built.

| Observation | Value |
|---|---|
| Successful-run HEAD | `16d72e1b351e5cdf1730e90645a6ea37144d1be7` |
| Successful-run tree | `5619bbb018830e071bc2ce45af84984cdd16bfc1` |
| Observed fetched `origin/main` | `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e` |
| Initial-run HEAD | `955fc4c41f74ada094f14fbaf386c943811e9050` |
| Initial-run tree | `70956d0f0e125d57abfbf1aed56460c067f8ef28` |
| Final private workspace | `/tmp/a41-composition-we0pwfl6` |
| Initial private workspace | `/tmp/a41-composition-dc5waq9z` |
| Installed payload | `prefix/share/hammond-b3-organ/capture-tools` under the final workspace |

Parent integration advanced during this assignment. The harness archives its
observed HEAD, overlays all 58 identified package/CMake dependencies coherently,
checks their copied bytes and confirms the live dependencies remain unchanged
through the run. The source hashes below identify the tested snapshot; an older
HEAD alone is insufficient. This worker did not fetch, merge or alter Git.

Actual top-level command, run once with the initial harness and once after its
fixture dispatch correction:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a41-composition-audit.py
```

The successful run invoked:

```sh
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake -S /tmp/a41-composition-we0pwfl6/source -B /tmp/a41-composition-we0pwfl6/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake --install /tmp/a41-composition-we0pwfl6/build --config Release --component CaptureTools --prefix /tmp/a41-composition-we0pwfl6/prefix
```

Both configure and install exited successfully. Actual installed runtime modules
were imported from the new package. The package contained exactly 57 files and
687,338 bytes, including five schemas and the unchanged sixteen-file,
32,831-byte demo. All 56 copied payload files match their corresponding frozen
source bytes; the remaining generated installed README is identified below.

## Initial harness failure retained

The first run reported one unexpected null-root outcome caused by the mutation
helper using callback return `None` to mean “use the original document after an
in-place edit.” The attempted null replacement therefore validated the unchanged
valid study. A subsequent explicit null check correctly rejected, but attempted
ledger cleanup left the original erroneous record in the unexpected accumulator.

The correction dispatches the null document directly, outside that convention,
and removes stale case-removal bookkeeping. This is one harness
fixture-dispatch/bookkeeping failure, not a production defect. The expected
result remained schema rejection plus runtime rejection. The full corrected
220-case matrix passed; no schema, source producer, threshold, work bound or
contract was altered to obtain that result.

The initial harness and initial result were copied before correction. Temporary
artifact locations are historical execution paths, not portable dependencies:

| Artifact under `/workspace/scratch/c9f3ead4c910/` | Bytes | SHA-256 |
|---|---:|---|
| `a41-composition/first-harness.py` | 21,819 | `65be3fc3244ec81e7f00697804833a77dfccc072aed979f459d9f2dab8921a33` |
| `a41-composition/first-result.json` | 76,246 | `adfc3658a635a03253ece6eaf5ca70622cc8fd35fcf9100b173163a4b4c885ef` |
| `a41-composition-audit.py` | 21,744 | `bd78aac8e34c59666b0f6e0f4b602cbe0a3c8b89005242315462acca5dee830b` |
| `a41-composition/result.json` | 76,060 | `a38e1e5582c721ac60f900b708c8f63eba71fab55a4089be360263d287cc264f` |
| `a41-composition/configure.log` | 573 | `ad55f4f6b9a421efd17827be5d1377c790be0f1e79280fba7ba62fd515cd312d` |
| `a41-composition/install.log` | 7,007 | `75cd91ee58ee547f09a941c09822a5c7a1de150bafaf6138112aebc1fc291aae` |

The final executable harness is retained verbatim at the end of this note,
together with the complete compact actual-outcome ledger and source identities.
A future reproduction must first restore/verify the identified source content,
then adapt only local paths and tool locations. Different source identities
require a new review record. Existing maintained acceptance tests remain the
normal regression gates; this ad hoc audit introduces no runtime or CI dependency.

## Complete frozen dependency identities

The following 58 files are the 56 copied payload inputs plus `CMakeLists.txt`
and the installation helper. The generated installed README is additional.
The parent checkout's root README is not a copied payload dependency.

| File | Bytes | SHA-256 |
|---|---:|---|
| `CMakeLists.txt` | 16,412 | `98843ed4e797cc4ce7caac14d995d8962492ed50b8756d3a6d8b19d0c316aed0` |
| `THIRD_PARTY_NOTICES.md` | 16,366 | `3d4acfae5c0c83b5184d3806b1ce70040beeaf027da28b541ab220e764ae4faa` |
| `cmake/InstallCaptureTools.cmake` | 11,069 | `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015` |
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

Generated installed `README.md`: 4,448 bytes; SHA-256
`9a7b8bdf85fbd2ed212342f0338a6e2ad8927191f0ea6e875da3497a71fbf715`.
The copy equality, exact inventory and end-of-run preservation cases below mean
these source identities also identify every corresponding installed file.

## Actual case ledger

Every row below met its stated expectation. Values are the actual recorded
observations; the harness following this ledger retains exact construction and
expected value for each named case. For study document and installed input
pairs, positions are `[schema_admits, semantic_admits]`. For the first four
study-composition triples, positions are `[shape_admits, operation_rejects,
bound_runner_calls]`. Work-bound triples are `[headers_valid, outcome,
bound_runner_calls]`. Replay tuples and rejection pairs are defined by their
explicit `record` calls in the retained harness. Booleans are not global
pass/fail labels: rejection is the intended result for negative cases.

### `schema_meta` — 5 cases

| Actual case | Actual observation = expected |
|---|---|
| `capture` | `true` |
| `capture-corpus` | `true` |
| `capture-policy` | `true` |
| `capture-job` | `true` |
| `capture-study` | `true` |

### `study_document` — 131 cases

| Actual case | Actual observation = expected |
|---|---|
| `missing-root-contract_origin` | `[false,false]` |
| `missing-root-corpus_sha256` | `[false,false]` |
| `missing-root-jobs` | `[false,false]` |
| `missing-root-schema_version` | `[false,false]` |
| `missing-root-study_id` | `[false,false]` |
| `extra-root` | `[false,false]` |
| `missing-entry-job_id` | `[false,false]` |
| `missing-entry-path` | `[false,false]` |
| `missing-entry-sha256` | `[false,false]` |
| `extra-entry` | `[false,false]` |
| `version-1` | `[true,true]` |
| `version-1.0` | `[true,false]` |
| `version-True` | `[false,false]` |
| `version-0` | `[false,false]` |
| `version-2` | `[false,false]` |
| `version--1` | `[false,false]` |
| `version-'1'` | `[false,false]` |
| `version-None` | `[false,false]` |
| `version-[]` | `[false,false]` |
| `version-{}` | `[false,false]` |
| `origin-''` | `[false,false]` |
| `origin-'project-proposed-capture-study-v2'` | `[false,false]` |
| `origin-'project-proposed-capture-study-v1\n'` | `[false,false]` |
| `origin-None` | `[false,false]` |
| `study_id-'a'` | `[true,true]` |
| `study_id-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[true,true]` |
| `study_id-'a0_-'` | `[true,true]` |
| `study_id-''` | `[false,false]` |
| `study_id-'A'` | `[false,false]` |
| `study_id-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[false,false]` |
| `study_id-'0a'` | `[false,false]` |
| `study_id-'a\n'` | `[false,false]` |
| `study_id-'a\r'` | `[false,false]` |
| `study_id-'a\t'` | `[false,false]` |
| `study_id-'a\x00'` | `[false,false]` |
| `study_id-'a\x7f'` | `[false,false]` |
| `study_id-'a\x85'` | `[false,false]` |
| `study_id-'\xe9'` | `[false,false]` |
| `study_id-'\U0001d11e'` | `[false,false]` |
| `study_id-'a\ud800'` | `[false,false]` |
| `study_id-' a'` | `[false,false]` |
| `study_id-'a/b'` | `[false,false]` |
| `study_id-'a.'` | `[false,false]` |
| `study_id-'a:b'` | `[false,false]` |
| `job_id-'a'` | `[true,true]` |
| `job_id-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[true,true]` |
| `job_id-'a0_-'` | `[true,true]` |
| `job_id-''` | `[false,false]` |
| `job_id-'A'` | `[false,false]` |
| `job_id-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[false,false]` |
| `job_id-'0a'` | `[false,false]` |
| `job_id-'a\n'` | `[false,false]` |
| `job_id-'a\r'` | `[false,false]` |
| `job_id-'a\t'` | `[false,false]` |
| `job_id-'a\x00'` | `[false,false]` |
| `job_id-'a\x7f'` | `[false,false]` |
| `job_id-'a\x85'` | `[false,false]` |
| `job_id-'\xe9'` | `[false,false]` |
| `job_id-'\U0001d11e'` | `[false,false]` |
| `job_id-'a\ud800'` | `[false,false]` |
| `job_id-' a'` | `[false,false]` |
| `job_id-'a/b'` | `[false,false]` |
| `job_id-'a.'` | `[false,false]` |
| `job_id-'a:b'` | `[false,false]` |
| `corpus_sha-'0000000000000000000000000000000000000000000000000000000000000000'` | `[true,true]` |
| `corpus_sha-'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'` | `[true,true]` |
| `corpus_sha-'000000000000000000000000000000000000000000000000000000000000000'` | `[false,false]` |
| `corpus_sha-'00000000000000000000000000000000000000000000000000000000000000000'` | `[false,false]` |
| `corpus_sha-'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'` | `[false,false]` |
| `corpus_sha-'gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg'` | `[false,false]` |
| `corpus_sha-'0000000000000000000000000000000000000000000000000000000000000000\n'` | `[false,false]` |
| `corpus_sha-'000000000000000000000000000000000000000000000000000000000000000\x7f'` | `[false,false]` |
| `corpus_sha-'000000000000000000000000000000000000000000000000000000000000000\xe9'` | `[false,false]` |
| `corpus_sha-'000000000000000000000000000000000000000000000000000000000000000\ud800'` | `[false,false]` |
| `corpus_sha-' 000000000000000000000000000000000000000000000000000000000000000'` | `[false,false]` |
| `corpus_sha-''` | `[false,false]` |
| `job_sha-'0000000000000000000000000000000000000000000000000000000000000000'` | `[true,true]` |
| `job_sha-'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'` | `[true,true]` |
| `job_sha-'000000000000000000000000000000000000000000000000000000000000000'` | `[false,false]` |
| `job_sha-'00000000000000000000000000000000000000000000000000000000000000000'` | `[false,false]` |
| `job_sha-'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'` | `[false,false]` |
| `job_sha-'gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg'` | `[false,false]` |
| `job_sha-'0000000000000000000000000000000000000000000000000000000000000000\n'` | `[false,false]` |
| `job_sha-'000000000000000000000000000000000000000000000000000000000000000\x7f'` | `[false,false]` |
| `job_sha-'000000000000000000000000000000000000000000000000000000000000000\xe9'` | `[false,false]` |
| `job_sha-'000000000000000000000000000000000000000000000000000000000000000\ud800'` | `[false,false]` |
| `job_sha-' 000000000000000000000000000000000000000000000000000000000000000'` | `[false,false]` |
| `job_sha-''` | `[false,false]` |
| `path-'a'` | `[true,true]` |
| `path-'A/b-1.json'` | `[true,true]` |
| `path-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[true,true]` |
| `path-'a/a/a/a/a/a/a/a'` | `[true,true]` |
| `path-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[true,true]` |
| `path-'a..b'` | `[true,true]` |
| `path-'COM0.json'` | `[true,true]` |
| `path-'1.json'` | `[true,true]` |
| `path-''` | `[false,false]` |
| `path-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[false,false]` |
| `path-'a/a/a/a/a/a/a/a/a'` | `[false,false]` |
| `path-'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` | `[false,false]` |
| `path-'/abs'` | `[false,false]` |
| `path-'../a'` | `[false,false]` |
| `path-'a/..'` | `[false,false]` |
| `path-'a//b'` | `[false,false]` |
| `path-'a/'` | `[false,false]` |
| `path-'a\\b'` | `[false,false]` |
| `path-'a:b'` | `[false,false]` |
| `path-'CON'` | `[false,false]` |
| `path-'con.wav'` | `[false,false]` |
| `path-'x/Lpt9.ext'` | `[false,false]` |
| `path-'a.'` | `[false,false]` |
| `path-'a./b'` | `[false,false]` |
| `path-'.hidden'` | `[false,false]` |
| `path-'a\n'` | `[false,false]` |
| `path-'a\x85'` | `[false,false]` |
| `path-'\xe9.json'` | `[false,false]` |
| `path-'a\ud800'` | `[false,false]` |
| `job-count-0` | `[false,false]` |
| `job-count-1` | `[true,true]` |
| `job-count-8` | `[true,true]` |
| `job-count-9` | `[false,false]` |
| `identical-entry` | `[false,false]` |
| `duplicate-field-job_id` | `[true,false]` |
| `duplicate-field-path` | `[true,false]` |
| `duplicate-field-sha256` | `[true,false]` |
| `casefold-path` | `[true,false]` |
| `tuple-jobs` | `[false,false]` |
| `root-[]` | `[false,false]` |
| `root-False` | `[false,false]` |
| `root-1` | `[false,false]` |
| `root-None` | `[false,false]` |

### `study_bytes` — 9 cases

| Actual case | Actual observation = expected |
|---|---|
| `canonical` | `true` |
| `exact-64KiB` | `true` |
| `over-64KiB` | `false` |
| `BOM` | `false` |
| `invalid-UTF8` | `false` |
| `duplicate-key` | `false` |
| `trailing-document` | `false` |
| `float-version` | `false` |
| `load-does-not-open-job` | `true` |

### `installed_input` — 14 cases

| Actual case | Actual observation = expected |
|---|---|
| `data/capture-planned-example.json` | `[true,true]` |
| `data/corpus-planned-example.json` | `[true,true]` |
| `data/capture-policy-synthetic-example.json` | `[true,true]` |
| `examples/capture-demo/corpus/reference.json` | `[true,true]` |
| `examples/capture-demo/corpus/quarter.json` | `[true,true]` |
| `examples/capture-demo/corpus/half.json` | `[true,true]` |
| `examples/capture-demo/corpus/corpus.json` | `[true,true]` |
| `examples/capture-demo/policy-pass.json` | `[true,true]` |
| `examples/capture-demo/policy-inconclusive.json` | `[true,true]` |
| `examples/capture-demo/policy-fail.json` | `[true,true]` |
| `examples/capture-demo/job-pass.json` | `[true,true]` |
| `examples/capture-demo/job-inconclusive.json` | `[true,true]` |
| `examples/capture-demo/job-fail.json` | `[true,true]` |
| `examples/capture-demo/study.json` | `[true,true]` |

### `binding` — 16 cases

| Actual case | Actual observation = expected |
|---|---|
| `data/corpus-planned-example.json->planned-dry-gg-acquisition` | `"35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac"` |
| `examples/capture-demo/corpus/corpus.json->reference` | `"e3d5761fa8f6d3351c82fdc72a13df8c8db9458f07fba401cb22f1fe85fef970"` |
| `examples/capture-demo/corpus/reference.json->raw` | `"fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402"` |
| `examples/capture-demo/corpus/corpus.json->quarter` | `"2727e5b2ef50652d96be9e2b55880eba9390c1b6804addc7af2d39878f8f7e54"` |
| `examples/capture-demo/corpus/quarter.json->raw` | `"bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2"` |
| `examples/capture-demo/corpus/corpus.json->half` | `"281945a1b21b473949eb1049c489f21d2e506c96fd859412a97737631d94d0f5"` |
| `examples/capture-demo/corpus/half.json->raw` | `"36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758"` |
| `job-pass:corpus` | `"1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361"` |
| `job-pass:policy` | `"8300754d2088849d6a8fe042f248543e1c9965229b4ad9cc220f45bfa31cccc5"` |
| `job-inconclusive:corpus` | `"1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361"` |
| `job-inconclusive:policy` | `"23684a20f7cf263645fc7b4124804d248a114fba79973280818986ee48dd5e43"` |
| `job-fail:corpus` | `"1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361"` |
| `job-fail:policy` | `"c1025c652a3b85be75b10420ae87aca2db6bd8bf748e0218e5b2cd260e77ee3c"` |
| `study->demo-pass` | `"63f83d706b412cc4cd7a76957f924cb9c6970436593fdae3e0fd8724dea66e45"` |
| `study->demo-inconclusive` | `"d66a0d0f5762ed6f961e9db2a36426e0b308973547d62ee25be9bf44f42568c6"` |
| `study->demo-fail` | `"f2fad01bdafbebd14517cb0d9f6e8b3ce8e1541135358308818671327c27e703"` |

### `study_composition` — 8 cases

| Actual case | Actual observation = expected |
|---|---|
| `wrong-job-hash` | `[true,true,0]` |
| `job-id-mismatch` | `[true,true,0]` |
| `corpus-mismatch` | `[true,true,0]` |
| `unbound-job-whitespace` | `[true,true,0]` |
| `bound-original-whitespace` | `["failed","749bd39da78d0c532e00ce12e25b92034a8e37822ca515fa7b6d100d5f806105"]` |
| `spectral-equality` | `[true,"runner",1]` |
| `spectral-excess` | `[true,"rejected",0]` |
| `window-equality` | `[true,"runner",1]` |

### `replay` — 17 cases

| Actual case | Actual observation = expected |
|---|---|
| `job-pass` | `["pass","match","pass",true]` |
| `job-inconclusive` | `["inconclusive","match","inconclusive",true]` |
| `job-fail` | `["failed","match","failed",true]` |
| `study-mixed` | `["failed","match","failed",true]` |
| `opaque-policy` | `"mismatch"` |
| `opaque-reference` | `"mismatch"` |
| `opaque-candidate-extra` | `"mismatch"` |
| `opaque-corpus-extra` | `"mismatch"` |
| `consistent-forged-status` | `"mismatch"` |
| `inconsistent-status` | `[false,0]` |
| `physical-overclaim` | `[false,0]` |
| `source-context` | `"mismatch"` |
| `runtime-context` | `"mismatch"` |
| `saved-compact-original` | `[false,0]` |
| `same-value-different-input-bytes` | `[false,0]` |
| `wrong-study-work` | `[false,0]` |
| `nested-study-claim` | `[false,0]` |

### `report_is_not_input_schema` — 4 cases

| Actual case | Actual observation = expected |
|---|---|
| `job-pass` | `[false,false,false,false,false]` |
| `job-inconclusive` | `[false,false,false,false,false]` |
| `job-fail` | `[false,false,false,false,false]` |
| `study-mixed` | `[false,false,false,false,false]` |

### `import_closure` — 10 cases

| Actual case | Actual observation = expected |
|---|---|
| `validate_capture` | `[]` |
| `capture_common` | `[]` |
| `capture_audio` | `[]` |
| `capture_corpus` | `[]` |
| `compare_capture` | `[]` |
| `capture_job` | `[]` |
| `capture_readiness` | `[]` |
| `capture_study` | `[]` |
| `make_capture_demo` | `[]` |
| `verify_capture_report` | `[]` |

### `package` — 6 cases

| Actual case | Actual observation = expected |
|---|---|
| `exact-inventory` | `57` |
| `copied-byte-identities` | `true` |
| `schema-count` | `5` |
| `demo-bytes` | `32831` |
| `readme-runtime-paths` | `true` |
| `unchanged-after-audit` | `true` |

Study document totals are 21 admissions by both, 105 rejections by both and five
schema admissions rejected by semantics: floating `1.0`, selected-property
ID/path/SHA duplication and case-folded path duplication. All are documented
semantic responsibilities. Four complete-report cases each test all five input
schemas; their five observations do not increase the case count to twenty.

Work sentinel details: spectral equality declares 2,097,152 window samples and
33,554,432 terms; spectral excess declares 3,145,728 samples and 50,331,648 terms;
window equality declares 8,388,608 samples and zero terms. Each stops before
maximum workload execution. Opaque nested-data and consistent forged-status
replay cases retain matching source/runtime context while returning complete
`mismatch`. Source and runtime mutation cases set only the corresponding context
equality false. Actual normal demo replay preserves pass/inconclusive/failed
engineering statuses and all claim fields at `not_established`.

## Import and document closure observations

The per-module audit covers 92 static import observations across ten declared
modules. The existing one-level `.capture_common` fallback resolves within the
package; all other imported names are declared local modules or the observed
Python 3.12 standard-library set. Imported production module `__file__` paths
were checked under the installed package. This is the observed static closure,
not a claim about arbitrary runtime-generated imports in future code.

The installed README command paths resolve. A finite ordinary-Markdown link
scan, excluding fenced/inline code, found 95 local link occurrences. Sixty-eight
resolve inside the package. The following 27 refer to historical notes,
research/PDF material or project context outside its declared archive scope,
as explicitly disclosed by the installation guide. These are retained as a
package limitation; no runtime dependency or package expansion is requested.

| Installed document | Referenced path absent from this component |
|---|---|
| `docs/CAPTURE_FORMAT.md` | `research/ATLAS_REVIEW.md` |
| `docs/CAPTURE_PROTOCOL.md` | `../Hammond_B3_Leslie_Research_Atlas_500pp.pdf` |
| `docs/CAPTURE_PROTOCOL.md` | `research/ATLAS_REVIEW.md` |
| `docs/CAPTURE_PROTOCOL.md` | `research/ERRATA.md` |
| `docs/CAPTURE_PROTOCOL.md` | `research/ATLAS_REVIEW.md` |
| `docs/CAPTURE_PROTOCOL.md` | `NEXT_STEPS.md` |
| `docs/CAPTURE_VALIDATION.md` | `development/agent-notes/41-capture-tests.md` |
| `docs/CAPTURE_AUDIO_CONTRACT.md` | `development/2026-11-13-calibration/07-audio-contract.md` |
| `docs/CAPTURE_AUDIO.md` | `development/2026-11-13-calibration/13-audio-implementation.md` |
| `docs/CAPTURE_CORPUS_CONTRACT.md` | `development/2026-11-13-calibration/05-atlas-335-417.md` |
| `docs/CAPTURE_CORPUS_CONTRACT.md` | `development/2026-11-13-calibration/06-atlas-418-500.md` |
| `docs/CAPTURE_CORPUS.md` | `development/2026-11-13-calibration/14-corpus-implementation.md` |
| `docs/CAPTURE_COMPARISON_CONTRACT.md` | `development/2026-11-13-calibration/09-comparison-contract.md` |
| `docs/CAPTURE_COMPARISON.md` | `CALIBRATION_CONTRACT_REVIEW.md` |
| `docs/CAPTURE_COMPARISON.md` | `development/2026-11-13-calibration/15-metrics-implementation.md` |
| `docs/CAPTURE_COMPARISON.md` | `development/2026-11-13-calibration/18-metric-acceptance.md` |
| `docs/CAPTURE_COMPARISON.md` | `development/2026-11-13-calibration/21-policy-acceptance.md` |
| `docs/CAPTURE_POLICY.md` | `development/2026-11-13-calibration/20-policy-implementation.md` |
| `docs/CAPTURE_JOB_CONTRACT.md` | `development/2026-11-13-calibration/19-file-job-contract.md` |
| `docs/CAPTURE_JOB.md` | `development/2026-11-13-calibration/25-file-job-implementation.md` |
| `docs/CAPTURE_READINESS.md` | `research/CALIBRATION_ATLAS_REVIEW.md` |
| `docs/PLAN.md` | `IMPLEMENTATION_CONTRACT.md` |
| `docs/PLAN.md` | `FACTORY_REFERENCE.md` |
| `docs/PLAN.md` | `STATUS.md` |
| `docs/PLAN.md` | `NEXT_STEPS.md` |
| `docs/PLAN.md` | `DEVELOPMENT_LOG.md` |
| `docs/CAPTURE_JOB_REVIEW.md` | `development/2026-11-13-calibration/22-job-contract-review.md` |

## Handoff and limits

The integrator should accept/review these two owned files and incorporate them
in its next coherent documentation checkpoint. No production fix is proposed.
Do not add `jsonschema` to runtime or infer physical success from a passing shape,
an engineering comparison or a matching replay. Preserve the failed/inconclusive
outcomes, original-byte inputs and exact policy identities. If a listed source
changes, requalify the affected interface against a newly installed coherent
snapshot before applying this conclusion to it.

This assignment supplies finite Linux composition and package evidence only.
No native Windows/macOS execution, hardware acquisition, calibration, acoustic
measurement, host qualification, maximum-work timing, real-time safety, rights
clearance or historical authenticity was performed. No physical value or
acceptance threshold was generated or edited. Hashes identify bytes, not the
chronology in which a policy or report was authored. Commit/push verification
and session accounting remain with the parent; this worker claims neither.

## Exact final audit harness

The code below is the verbatim 21,744-byte final scratch harness identified
above. It creates private copies, installs the component without a native build,
performs the bounded audit and records results. Paths reflect the actual run.
Its `jsonschema` import belongs only to this authoring audit. Running it against
later live sources generates a new source-qualified observation; it does not
reproduce these historical hashes automatically.

```python
from __future__ import annotations
import ast
import copy
from collections import Counter
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from unittest import mock
from urllib.parse import unquote
from jsonschema import Draft202012Validator

REPO = Path('/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ')
OUT = Path('/workspace/scratch/c9f3ead4c910/a41-composition')
OUT.mkdir(exist_ok=True)
CMAKE = Path('/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake')
MODULES = ['validate_capture','capture_common','capture_audio','capture_corpus','compare_capture','capture_job','capture_readiness','capture_study','make_capture_demo','verify_capture_report']
SCHEMAS = ['capture','capture-corpus','capture-policy','capture-job','capture-study']
DATA = [f'data/{s}.schema.json' for s in SCHEMAS] + ['data/capture-planned-example.json','data/corpus-planned-example.json','data/capture-policy-synthetic-example.json']
DOCS = ['CAPTURE_FORMAT','CAPTURE_PROTOCOL','CAPTURE_VALIDATION','CAPTURE_COMMON','CAPTURE_AUDIO_CONTRACT','CAPTURE_AUDIO','CAPTURE_CORPUS_CONTRACT','CAPTURE_CORPUS','CAPTURE_COMPARISON_CONTRACT','CAPTURE_COMPARISON','CAPTURE_POLICY','CAPTURE_JOB_CONTRACT','CAPTURE_JOB','CAPTURE_READINESS','CAPTURE_STUDY','CAPTURE_DEMO','CAPTURE_REPLAY','CAPTURE_TOOLS_INSTALL','PLAN','CALIBRATION_SCOPE','CAPTURE_JOB_REVIEW']
DEMO = ['README.md','EXPECTED.json','study.json','job-pass.json','job-inconclusive.json','job-fail.json','policy-pass.json','policy-inconclusive.json','policy-fail.json','corpus/corpus.json','corpus/reference.json','corpus/quarter.json','corpus/half.json','corpus/audio/reference.f32','corpus/audio/quarter.f32','corpus/audio/half.f32']
PAYLOAD = [f'tools/{m}.py' for m in MODULES] + DATA + [f'docs/{d}.md' for d in DOCS] + [f'examples/capture-demo/{p}' for p in DEMO] + ['THIRD_PARTY_NOTICES.md']
EXPECTED = set(PAYLOAD + ['README.md'])
assert len(EXPECTED) == 57
TRACKED = PAYLOAD + ['CMakeLists.txt','cmake/InstallCaptureTools.cmake']
def identity(p):
    b=p.read_bytes();return {'size_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def canonical(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def put(p,v):p.write_bytes(canonical(v))
identities={p:identity(REPO/p) for p in TRACKED}
head=subprocess.check_output(['git','rev-parse','HEAD','HEAD^{tree}','origin/main'],cwd=REPO,text=True).splitlines()
workspace=Path(tempfile.mkdtemp(prefix='a41-composition-')).resolve()
source=workspace/'source';source.mkdir()
archive=subprocess.check_output(['git','archive',head[0]],cwd=REPO)
with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(source,filter='data')
for rel in TRACKED:
    target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((REPO/rel).read_bytes());assert identity(target)==identities[rel]
assert all(identity(REPO/p)==identities[p] for p in TRACKED)
build=workspace/'build';prefix=workspace/'prefix'
commands=[['-S',str(source),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=OFF','-DHAMMOND_BUILD_VST3=OFF','-DHAMMOND_BUILD_STANDALONE=OFF'],['--install',str(build),'--config','Release','--component','CaptureTools','--prefix',str(prefix)]]
for label,args in zip(['configure','install'],commands):
    r=subprocess.run([str(CMAKE),*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
    (OUT/(label+'.log')).write_text(r.stdout)
    assert r.returncode==0,(label,r.stdout[-3000:])
package=prefix/'share/hammond-b3-organ/capture-tools'
package_before={p.relative_to(package).as_posix():identity(p) for p in package.rglob('*') if p.is_file()}
assert set(package_before)==EXPECTED
assert all(identity(package/p)==identities[p] for p in PAYLOAD)
sys.path.insert(0,str(package/'tools'))
import validate_capture, capture_common, capture_audio, capture_corpus, compare_capture, capture_job, capture_study, verify_capture_report
assert all(Path(sys.modules[m].__file__).resolve().is_relative_to(package/'tools') for m in ['validate_capture','capture_common','capture_audio','capture_corpus','compare_capture','capture_job','capture_study','verify_capture_report'])
cases=[];unexpected=[]
def record(group,name,actual,expected,detail=None):
    row={'group':group,'case':name,'actual':actual,'expected':expected}
    if detail is not None:row['detail']=detail
    cases.append(row)
    if actual!=expected:unexpected.append(row)
def admitted(fn,*args):
    try:fn(*args);return True
    except (ValueError,TypeError,OverflowError):return False
schema_values={n:json.loads((package/f'data/{n}.schema.json').read_text()) for n in SCHEMAS}
validators={}
for name,value in schema_values.items():
    Draft202012Validator.check_schema(value)
    refs=[]
    def walk(node):
        if isinstance(node,dict):
            for k,v in node.items():
                if k=='$ref':refs.append(v)
                walk(v)
        elif isinstance(node,list):
            for v in node:walk(v)
    walk(value)
    record('schema_meta',name,all(r.startswith('#/') for r in refs),True,{'references':len(refs)})
    validators[name]=Draft202012Validator(value)
base=json.loads((package/'examples/capture-demo/study.json').read_text())
def study_case(name,mutator,shape=True,runtime=True):
    value=copy.deepcopy(base);replacement=mutator(value)
    if replacement is not None:value=replacement
    record('study_document',name,[validators['capture-study'].is_valid(value),admitted(capture_study.validate_study,value)],[shape,runtime])
def set_path(v,path,value):
    obj=v
    for part in path[:-1]:obj=obj[part]
    obj[path[-1]]=value
for key in base:
    study_case('missing-root-'+key,lambda v,k=key:v.pop(k) and None,False,False)
study_case('extra-root',lambda v:v.update(extra=0),False,False)
for key in base['jobs'][0]:
    study_case('missing-entry-'+key,lambda v,k=key:v['jobs'][0].pop(k) and None,False,False)
study_case('extra-entry',lambda v:v['jobs'][0].update(extra=0),False,False)
for number in [1,1.0,True,0,2,-1,'1',None,[],{}]:
    study_case('version-'+repr(number),lambda v,x=number:v.update(schema_version=x),number==1 and not isinstance(number,bool),type(number) is int and number==1)
for origin in ['', 'project-proposed-capture-study-v2', 'project-proposed-capture-study-v1\n', None]:
    study_case('origin-'+repr(origin),lambda v,x=origin:v.update(contract_origin=x),False,False)
ids=[('a',True),('a'*64,True),('a0_-',True),('',False),('A',False),('a'*65,False),('0a',False),('a\n',False),('a\r',False),('a\t',False),('a\0',False),('a\x7f',False),('a\x85',False),('é',False),('𝄞',False),('a\ud800',False),(' a',False),('a/b',False),('a.',False),('a:b',False)]
for label,path in [('study_id',['study_id']),('job_id',['jobs',0,'job_id'])]:
    for value,expected in ids:study_case(label+'-'+ascii(value),lambda v,p=path,x=value:set_path(v,p,x),expected,expected)
hashes=[('0'*64,True),('f'*64,True),('0'*63,False),('0'*65,False),('A'*64,False),('g'*64,False),('0'*64+'\n',False),('0'*63+'\x7f',False),('0'*63+'é',False),('0'*63+'\ud800',False),(' '+'0'*63,False),('',False)]
for label,path in [('corpus_sha',['corpus_sha256']),('job_sha',['jobs',0,'sha256'])]:
    for value,expected in hashes:study_case(label+'-'+ascii(value),lambda v,p=path,x=value:set_path(v,p,x),expected,expected)
paths=[('a',True),('A/b-1.json',True),('a'*64,True),('/'.join(['a']*8),True),('/'.join(['a'*64]*3+['a'*45]),True),('a..b',True),('COM0.json',True),('1.json',True),('',False),('a'*65,False),('/'.join(['a']*9),False),('/'.join(['a'*64]*3+['a'*46]),False),('/abs',False),('../a',False),('a/..',False),('a//b',False),('a/',False),('a\\b',False),('a:b',False),('CON',False),('con.wav',False),('x/Lpt9.ext',False),('a.',False),('a./b',False),('.hidden',False),('a\n',False),('a\x85',False),('é.json',False),('a\ud800',False)]
for value,expected in paths:study_case('path-'+ascii(value),lambda v,x=value:set_path(v,['jobs',0,'path'],x),expected,expected)
for count in [0,1,8,9]:
    def entries(v,n=count):v['jobs']=[{'job_id':f'job-{i}','path':f'job-{i}.json','sha256':f'{i:064x}'} for i in range(n)]
    study_case('job-count-'+str(count),entries,1<=count<=8,1<=count<=8)
study_case('identical-entry',lambda v:v['jobs'].append(copy.deepcopy(v['jobs'][0])),False,False)
for key in ['job_id','path','sha256']:
    study_case('duplicate-field-'+key,lambda v,k=key:v['jobs'][1].update({k:v['jobs'][0][k]}),True,False)
study_case('casefold-path',lambda v:v['jobs'][1].update(path=v['jobs'][0]['path'].upper()),True,False)
study_case('tuple-jobs',lambda v:v.update(jobs=tuple(v['jobs'])),False,False)
for value in [[],False,1]:study_case('root-'+repr(value),lambda v,x=value:x,False,False)
# Null is a document itself, not the mutation callback's no-return convention.
record('study_document','root-None',[validators['capture-study'].is_valid(None),admitted(capture_study.validate_study,None)],[False,False])
# Original byte admission of the new input family.
payload=canonical(base);byte_cases=[('canonical',payload,True),('exact-64KiB',payload+b' '*(65536-len(payload)),True),('over-64KiB',payload+b' '*(65537-len(payload)),False),('BOM',b'\xef\xbb\xbf'+payload,False),('invalid-UTF8',b'\xff'+payload,False),('duplicate-key',b'{"schema_version":1,'+payload[1:],False),('trailing-document',payload+b'{}',False),('float-version',canonical({**base,'schema_version':1.0}),False)]
for name,data,expected in byte_cases:
    path=workspace/'study-bytes.json';path.write_bytes(data);record('study_bytes',name,admitted(capture_study.load_study,path),expected)
path=workspace/'metadata-only.json';value=copy.deepcopy(base);value['jobs']=[{'job_id':'absent','path':'absent.json','sha256':'0'*64}];put(path,value);record('study_bytes','load-does-not-open-job',admitted(capture_study.load_study,path),True)
# Every actual installed declaration across all five schemas.
input_specs=[('data/capture-planned-example.json','capture'),('data/corpus-planned-example.json','capture-corpus'),('data/capture-policy-synthetic-example.json','capture-policy')]
input_specs += [(f'examples/capture-demo/corpus/{n}.json','capture') for n in ['reference','quarter','half']]
input_specs += [('examples/capture-demo/corpus/corpus.json','capture-corpus')]
input_specs += [(f'examples/capture-demo/policy-{n}.json','capture-policy') for n in ['pass','inconclusive','fail']]
input_specs += [(f'examples/capture-demo/job-{n}.json','capture-job') for n in ['pass','inconclusive','fail']]
input_specs += [('examples/capture-demo/study.json','capture-study')]
checks={'capture':validate_capture.validate_capture,'capture-corpus':capture_corpus.validate_corpus,'capture-job':capture_job.validate_job,'capture-study':capture_study.validate_study}
for rel,kind in input_specs:
    b=(package/rel).read_bytes();v=json.loads(b);semantic=admitted(compare_capture.parse_policy,b) if kind=='capture-policy' else admitted(checks[kind],v)
    record('installed_input',rel,[validators[kind].is_valid(v),semantic],[True,True])
# Independently recompute all original-byte edges; locators retain their own parent roots.
for indexrel in ['data/corpus-planned-example.json','examples/capture-demo/corpus/corpus.json']:
    indexpath=package/indexrel;index=json.loads(indexpath.read_text())
    for entry in index['captures']:
        mpath=indexpath.parent/entry['manifest_path'];record('binding',indexrel+'->'+entry['capture_id'],digest(mpath.read_bytes()),entry['manifest_sha256'])
        manifest=json.loads(mpath.read_text())
        for f in manifest['files']:
            if f.get('sha256') is not None:record('binding',str(mpath.relative_to(package))+'->'+f['file_id'],digest((mpath.parent/f['path']).read_bytes()),f['sha256'])
demo=package/'examples/capture-demo'
for name in ['pass','inconclusive','fail']:
    job=json.loads((demo/f'job-{name}.json').read_text())
    for key in ['corpus','policy']:record('binding',f'job-{name}:{key}',digest((demo/job[key]['path']).read_bytes()),job[key]['sha256'])
for entry in base['jobs']:record('binding','study->'+entry['job_id'],digest((demo/entry['path']).read_bytes()),entry['sha256'])
# The semantic gates unavailable to a standalone study shape schema.
class ReachedRunner(Exception):pass
def study_fixture(name):
    target=workspace/name;shutil.copytree(demo,target);return target
for name,mutation in [('wrong-job-hash',None),('job-id-mismatch','job_id'),('corpus-mismatch','corpus'),('unbound-job-whitespace','whitespace')]:
    root=study_fixture(name);study=json.loads((root/'study.json').read_text());last=study['jobs'][-1];jobpath=root/last['path'];job=json.loads(jobpath.read_text())
    if mutation=='job_id':job['job_id']='different-id';put(jobpath,job);last['sha256']=digest(jobpath.read_bytes())
    elif mutation=='corpus':job['corpus']['sha256']='f'*64;put(jobpath,job);last['sha256']=digest(jobpath.read_bytes())
    elif mutation=='whitespace':jobpath.write_bytes(jobpath.read_bytes()+b' ')
    else:last['sha256']='0'*64
    put(root/'study.json',study)
    with mock.patch.object(capture_job,'_run_bound_job',side_effect=ReachedRunner) as hook:
        rejected=not admitted(capture_study.run_study,root/'study.json')
        record('study_composition',name,[validators['capture-study'].is_valid(study),rejected,hook.call_count],[True,True,0])
root=study_fixture('bound-whitespace');study=json.loads((root/'study.json').read_text());last=study['jobs'][-1];jp=root/last['path'];jp.write_bytes(jp.read_bytes()+b' \n');last['sha256']=digest(jp.read_bytes());put(root/'study.json',study);report=capture_study.run_study(root/'study.json');record('study_composition','bound-original-whitespace',[report['status'],report['jobs'][-1]['observed_sha256']],["failed",last['sha256']])
for name,count,k,expected in [('spectral-equality',2,16,'runner'),('spectral-excess',3,16,'rejected'),('window-equality',8,0,'runner')]:
    root=study_fixture(name);study=copy.deepcopy(base);study['jobs']=[]
    for i in range(count):
        job=json.loads((demo/'job-pass.json').read_text());job['job_id']=f'bound-{i}';job['analysis'].update(channel_count=4,frame_count=262144,sample_rate_hz=768000,frequencies_hz=list(range(k)));capture_job.validate_job(job);jp=root/f'bound-{i}.json';put(jp,job);study['jobs'].append({'job_id':job['job_id'],'path':jp.name,'sha256':digest(jp.read_bytes())})
    put(root/'study.json',study)
    with mock.patch.object(capture_job,'_run_bound_job',side_effect=ReachedRunner) as hook:
        try:capture_study.run_study(root/'study.json');actual='unexpected-return'
        except ReachedRunner:actual='runner'
        except capture_study.StudyError:actual='rejected'
    record('study_composition',name,[validators['capture-study'].is_valid(study),actual,hook.call_count],[True,expected,1 if expected=='runner' else 0],{'window_samples':count*4*262144,'spectral_terms':count*4*262144*k,'maximum_audio_work_executed':False})
# Actual original reports and replay: input schemas are not output validators.
reports={};report_paths={}
for kind,name,status in [('job','pass','pass'),('job','inconclusive','inconclusive'),('job','fail','failed'),('study','mixed','failed')]:
    inp=demo/(f'job-{name}.json' if kind=='job' else 'study.json');r=capture_job.run_job(inp) if kind=='job' else capture_study.run_study(inp);rp=workspace/f'{kind}-{name}-report.json';put(rp,r);reports[(kind,name)]=r;report_paths[(kind,name)]=rp
    summary=verify_capture_report.verify_report(kind,inp,rp)
    record('replay',kind+'-'+name,[r['status'],summary['status'],summary['replayed_engineering_status'],all(summary[key]=='not_established' for key in verify_capture_report.CLAIM_FIELDS)],[status,'match',status,True])
    record('report_is_not_input_schema',kind+'-'+name,[validators[s].is_valid(r) for s in SCHEMAS],[False]*5)
job=reports[('job','pass')]
mutations=[('opaque-policy',lambda r:r.update(policy={}),True),('opaque-reference',lambda r:r.update(reference={}),True),('opaque-candidate-extra',lambda r:r['candidate'].update(audit_probe='different'),True),('opaque-corpus-extra',lambda r:r['corpus_report'].update(audit_probe='different'),True),('consistent-forged-status',lambda r:(r.update(status='failed'),r['evaluation'].update(numerical_verdict='fail')),True),('inconsistent-status',lambda r:r.update(status='failed'),False),('physical-overclaim',lambda r:r.update(physical_fidelity='established'),False),('source-context',lambda r:r['tool_sources'][0].update(sha256='f'*64),True),('runtime-context',lambda r:r['runtime'].update(python_version='0.0.0'),True)]
for name,change,admit in mutations:
    v=copy.deepcopy(job);change(v);rp=workspace/(name+'.json');put(rp,v)
    if admit:
        summary=verify_capture_report.verify_report('job',demo/'job-pass.json',rp)
        record('replay',name,summary['status'],'mismatch',{'saved_status':summary['saved_engineering_status'],'fresh_status':summary['replayed_engineering_status'],'same_sources':summary['context']['same_tool_sources'],'same_runtime':summary['context']['same_runtime']})
    else:
        with mock.patch.object(capture_job,'run_job',side_effect=ReachedRunner) as hook:
            result=admitted(verify_capture_report.verify_report,'job',demo/'job-pass.json',rp)
        record('replay',name,[result,hook.call_count],[False,0])
rp=workspace/'compact-report.json';rp.write_bytes(json.dumps(job,separators=(',',':')).encode())
with mock.patch.object(capture_job,'run_job',side_effect=ReachedRunner) as hook:result=admitted(verify_capture_report.verify_report,'job',demo/'job-pass.json',rp)
record('replay','saved-compact-original',[result,hook.call_count],[False,0])
changed_input=workspace/'same-value-job.json';changed_input.write_bytes((demo/'job-pass.json').read_bytes()+b' ')
with mock.patch.object(capture_job,'run_job',side_effect=ReachedRunner) as hook:result=admitted(verify_capture_report.verify_report,'job',changed_input,report_paths[('job','pass')])
record('replay','same-value-different-input-bytes',[result,hook.call_count],[False,0])
for name,change in [('wrong-study-work',lambda r:r['work'].update(window_samples=13)),('nested-study-claim',lambda r:r['jobs'][0]['report'].update(permissions='established'))]:
    v=copy.deepcopy(reports[('study','mixed')]);change(v);rp=workspace/(name+'.json');put(rp,v)
    with mock.patch.object(capture_study,'run_study',side_effect=ReachedRunner) as hook:result=admitted(verify_capture_report.verify_report,'study',demo/'study.json',rp)
    record('replay',name,[result,hook.call_count],[False,0])
# Independent import closure and linked operating paths.
imports=[]
for module in MODULES:
    parsed=ast.parse((package/f'tools/{module}.py').read_text());bad=[];rows=[]
    for node in ast.walk(parsed):
        if isinstance(node,ast.Import):
            for alias in node.names:
                name=alias.name.split('.')[0];rows.append((0,name));
                if name not in MODULES and name not in sys.stdlib_module_names:bad.append(name)
        elif isinstance(node,ast.ImportFrom):
            name=(node.module or '').split('.')[0];rows.append((node.level,name))
            if node.level>1 or (node.level==1 and name not in MODULES) or (node.level==0 and name not in MODULES and name not in sys.stdlib_module_names):bad.append('.'*node.level+name)
    imports.extend({'source':module,'level':level,'module':name} for level,name in rows)
    record('import_closure',module,bad,[])
missing_links=[];local_links=0
for rel in ['README.md']+[f'docs/{d}.md' for d in DOCS]+['examples/capture-demo/README.md']:
    text=(package/rel).read_text();text=re.sub(r'```[\s\S]*?```','',text);text=re.sub(r'`[^`]*`','',text)
    for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
        if link.startswith(('http:','https:','#','mailto:')):continue
        target=unquote(link.split('#')[0]);local_links+=1
        if not (package/rel).parent.joinpath(target).exists():missing_links.append({'source':rel,'target':target})
record('package','exact-inventory',len(package_before),57)
record('package','copied-byte-identities',all(package_before[p]==identities[p] for p in PAYLOAD),True)
record('package','schema-count',sum(p.endswith('.schema.json') for p in EXPECTED),5)
record('package','demo-bytes',sum(package_before['examples/capture-demo/'+p]['size_bytes'] for p in DEMO),32831)
record('package','readme-runtime-paths',all((package/p).is_file() for p in re.findall(r'(?:tools/[A-Za-z0-9_]+\.py|(?:data|examples/capture-demo)/[A-Za-z0-9_./-]+\.json)',(package/'README.md').read_text())),True)
record('package','unchanged-after-audit',package_before=={p.relative_to(package).as_posix():identity(p) for p in package.rglob('*') if p.is_file()},True)
assert all(identity(REPO/p)==identities[p] for p in TRACKED)
result={'status':'passed' if not unexpected else 'failed','runtime':{'python':platform.python_version(),'platform':sys.platform,'machine':platform.machine(),'jsonschema':importlib.metadata.version('jsonschema')},'base_context':head,'workspace':str(workspace),'source_identities':identities,'installed':package_before,'cases':cases,'group_counts':dict(Counter(r['group'] for r in cases)),'study_outcomes':dict(Counter(str(r['actual']) for r in cases if r['group']=='study_document')),'import_records':imports,'local_markdown_links':local_links,'missing_document_links':missing_links,'unexpected':unexpected}
(OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n')
print(json.dumps({k:result[k] for k in ['status','runtime','base_context','workspace','group_counts','study_outcomes','local_markdown_links','missing_document_links','unexpected']},indent=2))
raise SystemExit(bool(unexpected))
```

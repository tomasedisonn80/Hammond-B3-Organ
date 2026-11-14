# Assignment 50 — fresh setup and relocation

Actual worker: **`/root/cal_w9_a50`**, assignment **50**, logical wave **9**, session
`2026-11-13-calibration`. Work executed on 2026-11-14 UTC. This is one actual newly
dispatched worker, not a reuse of an earlier installation review.

## Owned files and decision

Owned only this note and [CALIBRATION_CLEAN_SETUP.md](../../reviews/CALIBRATION_CLEAN_SETUP.md).
The complete review explains the scope and result. **51 recorded setup/runtime
commands and 15 grouped checks passed on the first actual audit run.** No flow
was skipped; all deliberately nonzero outcomes were expected. No production
repair was requested. No production, maintained test, CMake, shared status,
assignment ledger or Git ref was edited, staged or published by this worker.
Root owns acceptance, shared documentation and publication.

## Readings, source freeze and prerequisites

Read AGENTS, README, current STATUS/NEXT_STEPS/development log, the calibration
scope and handoff, project plan, original atlas-review consolidation, BUILD,
OFFLINE_INSTALL and the complete CaptureTools install contract. Read extracted
atlas pages 449, 484 and 486 for upstream-first evidence and source/setup/change
control. The six earlier actual readers own this session's full-PDF coverage;
this assignment does not claim another complete reading.

A preliminary read-only documentation lookup attempted the nonexistent
`docs/OFFLINE_TOOLS_INSTALL.md`; `rg --files` identified the actual
`docs/OFFLINE_INSTALL.md`, which was then read. This was a lookup correction,
not a failed project setup command. No failed audit run was discarded.

Waited for root's explicit source-freeze message before copying or configuring.
The exact input is local commit `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a`, tree
`3edea0838b75feb06c19e151ec8539e80646fc03`. It includes the final CLI guard,
standalone-generator repair, Windows binary-marker fixture and raw-float32 Git
attribute. Its archive contains 1,000 files and 39,738,773 bytes. Root's separate
integration build was not reused. Later root publication owns the corresponding
reachable public commit/tree mapping.

Actual CMake executable:
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`, version 4.4.4.
Compiler: `/usr/bin/c++`, Debian GNU C++ 14.2.0-19. Python:
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`,
3.12.14, build `[Clang 22.1.3]`. System: Linux 6.18.57 x86_64, glibc 2.41.
Configuration uses Release, BUILD_TESTING=OFF, VST3=OFF and STANDALONE=OFF.
No dependency installation or network command was performed. The Python tools
ran with `-B -S`, empty PYTHONPATH, PYTHONNOUSERSITE=1, bytecode disabled and
PYTHONIOENCODING=ascii:strict; inherited HAMMOND variables were removed.

The audit workspace is `/workspace/scratch/c9f3ead4c910/a50-clean-setup`.
Its source/build/prefix paths include spaces and café. Only task-created private
source/build/pre-move-native-data directories were removed, after source identity
verification. The moved prefix and reports remain in scratch for inspection;
the retained note provides reproduction and exact identities without depending
on their continued availability.

Actual top-level execution, from the repository root:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a50-clean-setup.py --commit 48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a
```

No full CTest gate is claimed here. CMake configured and built the five actual
native offline tools from fresh coherent inputs. The 51-command ledger counts
recorded setup/runtime commands, excluding two preliminary Git identity/archive
commands and compiler/linker child processes.

## Actual grouped checks

| Check | Outcome and scope |
| --- | --- |
| capture-before-native-build | Pass. {"bytes": 698919, "copied_source_files": 56, "files": 57} |
| source-capture-pipeline | Pass. 10 real commands; original planned/incomplete/pass/inconclusive/failed outcomes retained |
| coinstalled-inventories | Pass. Exactly80 files:57 capture+23 unchanged offline payload paths/bytes; no symlinks |
| capture-reinstall-preserves-both | Pass. Existing package rejection preserves all80 payload files |
| native-before-native-flows | Pass. All five native tools and both stdlib plotters executed; WAV 72000 frames, 48000Hz, identical PCM16 stereo, no clipping |
| source-unchanged | Pass. {"bytes": 39738773, "files": 1000} |
| relocation-and-removal | Pass. Original prefix, private source, build and pre-move native data absent |
| installed-capture-pipeline | Pass. 10 real commands; original planned/incomplete/pass/inconclusive/failed outcomes retained |
| complete-report-relocation-equality | Pass. All3 jobs and mixedstudy byte-identical between source and installed executions |
| four-cross-location-replays | Pass. Pass/inconclusive/failed jobs and failedstudy replay exact original source reports without oldsource/build |
| runtime-no-clobber | Pass. Existing report and installed demo rejected with unchanged bytes and empty stdout |
| standalone-script-closure | Pass. Each isolated script needs only standardlibrary and its explicit data; generatorrecreates16originalfiles |
| native-after-native-flows | Pass. All five native tools and both stdlib plotters executed; WAV 72000 frames, 48000Hz, identical PCM16 stereo, no clipping |
| native-relocation-equality | Pass. FullWAV,2metadataJSON,2CSV and2SVG outputs are byte-identical after source/build deletion |
| installed-input-preservation | Pass. All80 installedfiles unchanged; no bytecode or source fallback |

## Complete command outcome ledger

Every command's exact argument construction and working directory appear in the
embedded script below. Captured stdout/stderr are in `logs/NN-label.stdout` and
`.stderr` under the scratch workspace. Elapsed diagnostics are execution context,
not benchmark evidence. Expected nonzero results preserve plans, inconclusive
or failed engineering comparisons and no-clobber rejections.

| No. | Command label | Expected exit | Observed exit | Stdout bytes | Stderr bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | `cmake-version` | 0 | 0 | 90 | 0 |
| 2 | `compiler-version` | 0 | 0 | 232 | 0 |
| 3 | `configure` | 0 | 0 | 599 | 0 |
| 4 | `capture-install-before-build` | 0 | 0 | 8863 | 0 |
| 5 | `source-validate-plan` | 0 | 0 | 235 | 0 |
| 6 | `source-readiness-plan` | 3 | 3 | 10488 | 0 |
| 7 | `source-readiness-recorded` | 3 | 3 | 9865 | 0 |
| 8 | `source-planned-corpus` | 3 | 3 | 1954 | 0 |
| 9 | `source-demo-corpus` | 0 | 0 | 7277 | 0 |
| 10 | `source-raw-audio` | 0 | 0 | 1361 | 0 |
| 11 | `source-job-pass` | 0 | 0 | 32695 | 0 |
| 12 | `source-job-inconclusive` | 3 | 3 | 32783 | 0 |
| 13 | `source-job-fail` | 1 | 1 | 32660 | 0 |
| 14 | `source-study` | 1 | 1 | 119427 | 0 |
| 15 | `build-five-native-tools` | 0 | 0 | 3509 | 0 |
| 16 | `offline-coinstall` | 0 | 0 | 3082 | 0 |
| 17 | `capture-reinstall-reject` | 1 | 1 | 0 | 303 |
| 18 | `native-before-render` | 0 | 0 | 1284 | 0 |
| 19 | `native-before-hammond_model_info` | 0 | 0 | 108255 | 0 |
| 20 | `native-before-hammond_parameter_info` | 0 | 0 | 12298 | 0 |
| 21 | `native-before-console-trace` | 0 | 0 | 0 | 0 |
| 22 | `native-before-console-plot` | 0 | 0 | 0 | 0 |
| 23 | `native-before-pedal-trace` | 0 | 0 | 0 | 0 |
| 24 | `native-before-pedal-plot` | 0 | 0 | 0 | 0 |
| 25 | `installed-validate-plan` | 0 | 0 | 235 | 0 |
| 26 | `installed-readiness-plan` | 3 | 3 | 10488 | 0 |
| 27 | `installed-readiness-recorded` | 3 | 3 | 9865 | 0 |
| 28 | `installed-planned-corpus` | 3 | 3 | 1954 | 0 |
| 29 | `installed-demo-corpus` | 0 | 0 | 7277 | 0 |
| 30 | `installed-raw-audio` | 0 | 0 | 1399 | 0 |
| 31 | `installed-job-pass` | 0 | 0 | 32695 | 0 |
| 32 | `installed-job-inconclusive` | 3 | 3 | 32783 | 0 |
| 33 | `installed-job-fail` | 1 | 1 | 32660 | 0 |
| 34 | `installed-study` | 1 | 1 | 119427 | 0 |
| 35 | `replay-original-job-pass` | 0 | 0 | 3916 | 0 |
| 36 | `replay-original-job-inconclusive` | 0 | 0 | 3932 | 0 |
| 37 | `replay-original-job-fail` | 0 | 0 | 3920 | 0 |
| 38 | `replay-original-study` | 0 | 0 | 4262 | 0 |
| 39 | `job-output-no-clobber` | 1 | 1 | 0 | 257 |
| 40 | `generator-existing-reject` | 1 | 1 | 0 | 321 |
| 41 | `single-make_capture_demo-help` | 0 | 0 | 256 | 0 |
| 42 | `single-generator-work` | 0 | 0 | 2814 | 0 |
| 43 | `single-validate_capture-help` | 0 | 0 | 474 | 0 |
| 44 | `single-validator-work` | 0 | 0 | 455 | 0 |
| 45 | `native-after-render` | 0 | 0 | 1284 | 0 |
| 46 | `native-after-hammond_model_info` | 0 | 0 | 108255 | 0 |
| 47 | `native-after-hammond_parameter_info` | 0 | 0 | 12298 | 0 |
| 48 | `native-after-console-trace` | 0 | 0 | 0 | 0 |
| 49 | `native-after-console-plot` | 0 | 0 | 0 | 0 |
| 50 | `native-after-pedal-trace` | 0 | 0 | 0 | 0 |
| 51 | `native-after-pedal-plot` | 0 | 0 | 0 | 0 |

## Exact combined installed inventory

The independently typed payload lists come from the public contracts, not the
producer's install manifest or another test's inventory. All 57 capture paths
and 23 offline paths exist, with no symlinks. Copied source/data/script bytes and
all five native executables/compiled profile match their exact source/build
inputs. The generated CaptureTools README is retained as its own identity.
All 80 files below were unchanged after relocation and every runtime command.

| Path below moved prefix | Bytes | SHA-256 |
| --- | ---: | --- |
| `bin/hammond_console_trace` | 122704 | `7b968ac5d441031bda2280d84104629066937422953c6434c5350ef7f885d969` |
| `bin/hammond_model_info` | 46976 | `3471217c9f35530ea19c10fcff8508fa6a8dd4ae29c920e6ef5e8d1cb6bcc991` |
| `bin/hammond_parameter_info` | 41176 | `e66ebd2334836874f045d1a92fd456796b1e74bc495804220abfd8f3c7ed0e23` |
| `bin/hammond_pedal_trace` | 126864 | `9bd2ce87bb0f8f4806d8e0c48aa62573e212fd8a6b6690cb34a721431692bf54` |
| `bin/hammond_render` | 135320 | `9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6` |
| `bin/plot_console_trace.py` | 22430 | `e7cf4603acbf2707b7752f781314a97293b89567675eb19cae772f4db37d3720` |
| `bin/plot_pedal_trace.py` | 25610 | `45b28978924e88ac09b95bc6e5c9671e2b2f5059f9bd79df47565e8659f10f15` |
| `share/hammond-b3-organ/capture-tools/README.md` | 4448 | `9a7b8bdf85fbd2ed212342f0338a6e2ad8927191f0ea6e875da3497a71fbf715` |
| `share/hammond-b3-organ/capture-tools/THIRD_PARTY_NOTICES.md` | 16366 | `3d4acfae5c0c83b5184d3806b1ce70040beeaf027da28b541ab220e764ae4faa` |
| `share/hammond-b3-organ/capture-tools/data/capture-corpus.schema.json` | 3690 | `420037ea76f22dbd559b4005f1514bcf59d21310349800f138ce5b93c43707c9` |
| `share/hammond-b3-organ/capture-tools/data/capture-job.schema.json` | 3574 | `af1046b9d50d18e6da553805972591a2cf330403b8196ca376a577bfdb7afa2a` |
| `share/hammond-b3-organ/capture-tools/data/capture-planned-example.json` | 3223 | `35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac` |
| `share/hammond-b3-organ/capture-tools/data/capture-policy-synthetic-example.json` | 1047 | `e091dca3b3fdf3c3675383096007c5f95b848fa6294dedd3906705d061884316` |
| `share/hammond-b3-organ/capture-tools/data/capture-policy.schema.json` | 12377 | `2a1b0fd959f5f760d9460c7c960d48d7d4adbbd27918c9b4df6849646c8a9678` |
| `share/hammond-b3-organ/capture-tools/data/capture-study.schema.json` | 2102 | `1805ad62f357ec7f828591dce0a968391beba42418b9ea4f20adfe4139389e3d` |
| `share/hammond-b3-organ/capture-tools/data/capture.schema.json` | 32414 | `51fbfdbcc92d9cdb3b71d4b55618840a806e2847b49c93e6aa7d926621661a74` |
| `share/hammond-b3-organ/capture-tools/data/corpus-planned-example.json` | 466 | `9c23a5faf002472d50e9c4e5e923bdb46e95091ee026288d98a91b785a7c4e2e` |
| `share/hammond-b3-organ/capture-tools/docs/CALIBRATION_SCOPE.md` | 3139 | `a6d9f05dd5cf24de297210e65597e15d02cd2197f422b9da2889c0211643bb35` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_AUDIO.md` | 9078 | `b62ab52596532140845586a66ba0da7781b92da60fa26678afc7ff0c8851eb14` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_AUDIO_CONTRACT.md` | 35980 | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_COMMON.md` | 3923 | `5ae7a7fffb05829c8758d82ac74460ca14834acbe1fa4f2b6e4b1648623bb805` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_COMPARISON.md` | 8399 | `ab3b0e89bd94e26246fbff70dcc7982e93f2747ee953c83b428da69015fca6ea` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_COMPARISON_CONTRACT.md` | 28479 | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_CORPUS.md` | 10802 | `ae3501ce95a6557ff5cdc7a975703ce43708101d20c1ebe18593c80346eb79e6` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_CORPUS_CONTRACT.md` | 31880 | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_DEMO.md` | 13389 | `c60283e526a7e1f5f11e628536d0295b9a614038b411de6642e227c1c6ae3008` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_FORMAT.md` | 13696 | `618c20e4c6d2b204c69cdad006d69bfd93638de7c6d711b230452fea78b88177` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_JOB.md` | 11741 | `8e51706e2f2d10540dde62071cbfa157339cbc8ce162b57cdbd7ab754c3581f6` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_JOB_CONTRACT.md` | 29508 | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_JOB_REVIEW.md` | 13719 | `9218ca2e0fd72ff07ff1b838cac2dd153ce8e5b1ece18e20cbcc24d3b2c2f271` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_POLICY.md` | 11526 | `ea762fb1a65c99727fbcdf573ff47e86b004089d37d71ff72067f83e30c72a4c` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_PROTOCOL.md` | 31287 | `8dbfd09b9c2b5a8cfd10dd7df3adecab3d1b0ad7d48e0472557af9850424751f` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_READINESS.md` | 14203 | `e3eb647244c62d600e58d37a83f99db165256e4a69cf89e210f354fc12b55b0b` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_REPLAY.md` | 18044 | `1d855c9c734f0f8e9c3d73e4a735c9ef5d86066b734d1a74b95426545f3d3d88` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_STUDY.md` | 19910 | `a60d8c6a92356f2381ea61ba39c0dab50048b0f88ee6dc75bf943c7f5c5198e3` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_TOOLS_INSTALL.md` | 17824 | `ccffae418b2f45d5c88f977aa1fa1f6aa0662ba231f142dc7b2b2f264cd1f590` |
| `share/hammond-b3-organ/capture-tools/docs/CAPTURE_VALIDATION.md` | 5436 | `4a16cd0e1c09944ad8554db6b17dbdd3265120ce0c02169c2d23359990313b4d` |
| `share/hammond-b3-organ/capture-tools/docs/PLAN.md` | 8035 | `92fb19e2d8793bca803b3611ae38fa7b5034ff40b30b923fed9981ec7c7d3bde` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/EXPECTED.json` | 4425 | `8b3ade3def7f51119b90f5a65bc9fa3bf7c46ab561929a60acdd973245793396` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/README.md` | 6127 | `867618f49b41d88eaba13a86048190d4f0db30bc34b453adb9d51ce8fd1e4b08` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/audio/half.f32` | 16 | `36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/audio/quarter.f32` | 16 | `bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/audio/reference.f32` | 16 | `fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/corpus.json` | 1295 | `1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/half.json` | 4589 | `281945a1b21b473949eb1049c489f21d2e506c96fd859412a97737631d94d0f5` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/quarter.json` | 4599 | `2727e5b2ef50652d96be9e2b55880eba9390c1b6804addc7af2d39878f8f7e54` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/corpus/reference.json` | 4599 | `e3d5761fa8f6d3351c82fdc72a13df8c8db9458f07fba401cb22f1fe85fef970` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/job-fail.json` | 787 | `f2fad01bdafbebd14517cb0d9f6e8b3ce8e1541135358308818671327c27e703` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/job-inconclusive.json` | 806 | `d66a0d0f5762ed6f961e9db2a36426e0b308973547d62ee25be9bf44f42568c6` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/job-pass.json` | 790 | `63f83d706b412cc4cd7a76957f924cb9c6970436593fdae3e0fd8724dea66e45` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/policy-fail.json` | 1346 | `c1025c652a3b85be75b10420ae87aca2db6bd8bf748e0218e5b2cd260e77ee3c` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/policy-inconclusive.json` | 1362 | `23684a20f7cf263645fc7b4124804d248a114fba79973280818986ee48dd5e43` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/policy-pass.json` | 1348 | `8300754d2088849d6a8fe042f248543e1c9965229b4ad9cc220f45bfa31cccc5` |
| `share/hammond-b3-organ/capture-tools/examples/capture-demo/study.json` | 710 | `725e91cd3264d420018f2a6d269a27ed47f941e0e17b0abd09c81a71dafb717a` |
| `share/hammond-b3-organ/capture-tools/tools/capture_audio.py` | 30313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `share/hammond-b3-organ/capture-tools/tools/capture_common.py` | 12774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `share/hammond-b3-organ/capture-tools/tools/capture_corpus.py` | 39476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `share/hammond-b3-organ/capture-tools/tools/capture_job.py` | 24433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `share/hammond-b3-organ/capture-tools/tools/capture_readiness.py` | 11630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `share/hammond-b3-organ/capture-tools/tools/capture_study.py` | 16849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `share/hammond-b3-organ/capture-tools/tools/compare_capture.py` | 33448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `share/hammond-b3-organ/capture-tools/tools/make_capture_demo.py` | 25734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `share/hammond-b3-organ/capture-tools/tools/validate_capture.py` | 28237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `share/hammond-b3-organ/capture-tools/tools/verify_capture_report.py` | 23489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |
| `share/hammond-b3-organ/fixtures/a4-fundamental-v1.events` | 480 | `c3295b7a060b7af68c6e3d43198a54cbe33ee26b6bc8e3c2cd1a76b80cfeb59f` |
| `share/hammond-b3-organ/fixtures/catalog-v1.json` | 15544 | `98ffa2c3bc30f60ceb839e1fc2ab978e45dcf5f2cb4970fe77f91894344c34f8` |
| `share/hammond-b3-organ/fixtures/console/console-catalog-v1.json` | 12216 | `f66d31d43e67b52fb2044a680c9c6ca6f02608bd94eac1988ed56edc1f28a27b` |
| `share/hammond-b3-organ/fixtures/console/console-percussion-legato-v1.events` | 515 | `48f95b03561e48b13b1899203632a420d45f2283d1c293093c0236afde8e5ac9` |
| `share/hammond-b3-organ/fixtures/console/console-routing-mask-v1.events` | 565 | `3f654665fd74bc26fe2cb42bf597adb2b68f4485c7a47c89c0a4f0a84ae52318` |
| `share/hammond-b3-organ/fixtures/console/console-travel-v1.events` | 396 | `9147e5bb93d701ad0cee516cf28509a685f2791fefb19218a70c12dacd9d9806` |
| `share/hammond-b3-organ/fixtures/held-bank-cancel-v1.events` | 1010 | `fbd3060bdcae1bb7e4701de92799dca8ae0e4f92c5efedc84b450794c7e5ef5c` |
| `share/hammond-b3-organ/fixtures/high-fold-coherent-v1.events` | 537 | `0431c06df58e4b66decf385f6fdbb4e89b146dcd80efaa0dc23d2d3155b120c0` |
| `share/hammond-b3-organ/fixtures/low-fold-coherent-v1.events` | 671 | `3ae330fbdf6f789dcd0533c521c63dce855e743000ecc283fae565009726ddea` |
| `share/hammond-b3-organ/fixtures/pedals/pedal-catalog-v1.json` | 20057 | `f064cdda432791703f1853d9cde52faa3cd5bf9899b999ad5b38ee64bb1ed5b7` |
| `share/hammond-b3-organ/fixtures/pedals/pedal-held-routing-v1.events` | 447 | `71acf2756109509c81fa5e48d0ee7ef4d321f53e29d233ad2c60c3451f2ccdfa` |
| `share/hammond-b3-organ/fixtures/pedals/pedal-mixtures-v1.events` | 238 | `0adc929a3cde2f834f6d368dbd49e5441b636c2a933880144a8988033b45ba4d` |
| `share/hammond-b3-organ/fixtures/pedals/pedal-phrase-v1.events` | 1246 | `47daa264ca9524c98d7a189d28728778c9057852b8fd3d68e7fea9d2e63b9be5` |
| `share/hammond-b3-organ/fixtures/pedals/pedal-shared-source-v1.events` | 356 | `b0390f58fed9f91509089d8782a4d22ea5374070a2689fdeab5641a4d582cfb2` |
| `share/hammond-b3-organ/fixtures/two-manual-changes-v1.events` | 1607 | `d86b7fb3e3a62865b218400828aaef7ee176c39da7f08ef29aed5ae5b0627ae8` |
| `share/hammond-b3-organ/nominal.b3p` | 4545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Exact runtime products

These four full capture reports match their source and installed executions byte
for byte under the same runtime. Four installed replay commands consumed the
original source-run reports and matched with same source/runtime context; both
failed and inconclusive engineering results remain unchanged.

| Complete report | Bytes | SHA-256 |
| --- | ---: | --- |
| `job-fail` | 32660 | `ba1e39fc5f5410491f7826346c7259dfcf8b603dffbc0a260a9886ed66252321` |
| `job-inconclusive` | 32783 | `c39a060fadf9c3fbf71b1608c3884e62bf25b67fa4168f0948fe021646bb0930` |
| `job-pass` | 32695 | `fe4628d7b8fe78f2d15fd86e0acc16494bc552e25caaebd24bb4b09f5b2e9547` |
| `study` | 119427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` |

The following complete native products also match before and after relocation,
using the same newly compiled executables and explicit original data. All five
native tools and both plotters actually executed. The 1.5-second A4 WAV has
72,000 frames at 48,000 Hz, nonzero identical PCM16 stereo channels and no reported
clipping. Metadata retains 91 source slots, 45 parameter mappings and explicit
unqualified physical/host fields. Console partial and pedal overlap SVGs contain
the original CSV hash. These are nominal synthetic software outputs.

| Product | Bytes | SHA-256 |
| --- | ---: | --- |
| `a4.wav` | 288044 | `01f6efe7eb581e702cd59efc19b2df75ab0ddeee945ae7550c8bbfe9ed36e4d3` |
| `console.csv` | 1194816 | `dbaa075fcd7bea24b4a61a5df8f55faab53053244ad1e59126ba3f4d80fd89b2` |
| `console.svg` | 117510 | `76d8583e00977856e54e61fbb1691ff2f7ffb3e2e9f86e0ee5f807e9bdc203a4` |
| `hammond_model_info.json` | 108255 | `11a28002347425e56898115148f5c2ccb53364a0d6c62903da80ebf42126bfd3` |
| `hammond_parameter_info.json` | 12298 | `71d300d5e074b7b00b28ac801739d47834898235ba286bf1efa80c1d2b65182c` |
| `pedal.csv` | 2552204 | `ca674bb297fb97b00465e0627cedaf99e292358257f545d96a954980d795d589` |
| `pedal.svg` | 203164 | `8202ef4a605222a5423009b226bb105fad4f1e9b0643172a7ec97b8489a7b6f7` |

## Audit identity and exact reproduction

The executed script is 21,850 bytes, SHA-256
`3fd0680ab5c6c084db619cd7ca310ef8e919434f8bab73ca28feff5ca1c73417`.
The complete result JSON is 248,270 bytes, SHA-256
`40d7639302df272af393000865123b72fa587df9b697d250faed1d190aa24629`.
It retains all 1,000 source-file hashes, complete command argument arrays,
stdout/stderr identities, all 80 installed-file hashes, products and outcomes.
The script below is copied exactly, including its final LF; its hash is verified
against the actual executed file. It is an audit reproduction, not an additional
runtime dependency or installed utility. Before reusing it, select a new private
WORK path and available tool locations; record those resulting input changes
and their own new output identities. It deliberately refuses an existing WORK.

```python
#!/usr/bin/env python3
"""Assignment 50: actual fresh setup/relocation flows, no production imports."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import traceback
import wave

REPO = Path('/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ')
WORK = Path('/workspace/scratch/c9f3ead4c910/a50-clean-setup')
CMAKE = '/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake'
MODULES = ('validate_capture capture_common capture_audio capture_corpus compare_capture '
           'capture_job capture_readiness capture_study make_capture_demo verify_capture_report').split()
DATA = ('capture.schema.json capture-corpus.schema.json capture-policy.schema.json '
        'capture-job.schema.json capture-study.schema.json capture-planned-example.json '
        'corpus-planned-example.json capture-policy-synthetic-example.json').split()
DEMO = ('README.md EXPECTED.json study.json job-pass.json job-inconclusive.json job-fail.json '
        'policy-pass.json policy-inconclusive.json policy-fail.json corpus/corpus.json '
        'corpus/reference.json corpus/quarter.json corpus/half.json '
        'corpus/audio/reference.f32 corpus/audio/quarter.f32 corpus/audio/half.f32').split()
DOCS = ('CAPTURE_FORMAT CAPTURE_PROTOCOL CAPTURE_VALIDATION CAPTURE_COMMON CAPTURE_AUDIO_CONTRACT '
        'CAPTURE_AUDIO CAPTURE_CORPUS_CONTRACT CAPTURE_CORPUS CAPTURE_COMPARISON_CONTRACT '
        'CAPTURE_COMPARISON CAPTURE_POLICY CAPTURE_JOB_CONTRACT CAPTURE_JOB CAPTURE_READINESS '
        'CAPTURE_STUDY CAPTURE_DEMO CAPTURE_REPLAY CAPTURE_TOOLS_INSTALL PLAN CALIBRATION_SCOPE '
        'CAPTURE_JOB_REVIEW').split()
CAPTURE = ({'README.md', 'THIRD_PARTY_NOTICES.md'}
           | {'tools/' + x + '.py' for x in MODULES}
           | {'data/' + x for x in DATA}
           | {'examples/capture-demo/' + x for x in DEMO}
           | {'docs/' + x + '.md' for x in DOCS})
NATIVE = ('hammond_render hammond_model_info hammond_parameter_info '
          'hammond_console_trace hammond_pedal_trace').split()
OLD_FIXTURES = ('catalog-v1.json a4-fundamental-v1.events two-manual-changes-v1.events '
                'low-fold-coherent-v1.events held-bank-cancel-v1.events high-fold-coherent-v1.events '
                'console/console-catalog-v1.json console/console-travel-v1.events '
                'console/console-percussion-legato-v1.events console/console-routing-mask-v1.events '
                'pedals/pedal-catalog-v1.json pedals/pedal-mixtures-v1.events '
                'pedals/pedal-shared-source-v1.events pedals/pedal-held-routing-v1.events '
                'pedals/pedal-phrase-v1.events').split()
OFFLINE = ({'bin/' + x for x in NATIVE}
           | {'bin/plot_console_trace.py', 'bin/plot_pedal_trace.py'}
           | {'share/hammond-b3-organ/nominal.b3p'}
           | {'share/hammond-b3-organ/fixtures/' + x for x in OLD_FIXTURES})
CLAIMS = ('boundary_equivalence synchronization authenticity specimen_identity calibration '
          'permissions independence preregistration final_holdout_history physical_fidelity').split()
COUNTER = 0
RESULT = {'assignment': 50, 'agent': '/root/cal_w9_a50', 'wave': 9,
          'scope': 'fresh coherent local setup and same-runtime relocation',
          'commands': [], 'checks': [], 'unexpected_failure': None}


def identity(payload):
    return {'size_bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}


def inventory(path):
    result = {}
    for entry in sorted(path.rglob('*')):
        assert not entry.is_symlink(), ('unexpected symlink', str(entry))
        if entry.is_file():
            result[entry.relative_to(path).as_posix()] = identity(entry.read_bytes())
    return result


def save():
    (WORK / 'result.json').write_text(json.dumps(RESULT, sort_keys=True, indent=2) + '\n')


def checked(label, details):
    RESULT['checks'].append({'case': label, 'result': 'passed', 'details': details})
    save()


def execute(label, command, expected=0, cwd=None, env=None):
    global COUNTER
    COUNTER += 1
    started = time.monotonic()
    answer = subprocess.run([str(x) for x in command], cwd=cwd or WORK,
                            env=env or ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=300)
    stem = f'{COUNTER:02d}-{label}'
    for side in ('stdout', 'stderr'):
        (LOGS / (stem + '.' + side)).write_bytes(getattr(answer, side))
    record = {'number': COUNTER, 'label': label, 'argv': [str(x) for x in command],
              'cwd': str(cwd or WORK), 'expected_exit': expected, 'observed_exit': answer.returncode,
              'elapsed_seconds': round(time.monotonic() - started, 6),
              'stdout': identity(answer.stdout), 'stderr': identity(answer.stderr)}
    RESULT['commands'].append(record)
    save()
    assert answer.returncode == expected, (label, answer.returncode, expected,
                                           answer.stderr.decode('utf-8', 'replace')[-4000:])
    return answer


def value(answer, canonical=True):
    parsed = json.loads(answer.stdout)
    if canonical:
        expected = (json.dumps(parsed, ensure_ascii=False, allow_nan=False,
                               sort_keys=True, indent=2) + '\n').encode()
        assert answer.stdout == expected
    return parsed


def unknown(report):
    assert all(report[k] == 'not_established' for k in CLAIMS)


def python_tool(root, tool, *args):
    return [sys.executable, '-B', '-S', root / 'tools' / (tool + '.py'), *args]


def pipeline(root, phase, reports):
    demo = root / 'examples/capture-demo'
    report_dir = OUTPUT / phase
    report_dir.mkdir()
    answer = execute(phase + '-validate-plan', python_tool(root, 'validate_capture',
                     '--input', root / 'data/capture-planned-example.json'), cwd=FOREIGN)
    parsed = value(answer, False)
    assert parsed['structural_validation'] == 'pass' and parsed['record_status'] == 'planned'
    assert parsed['file_check'] is None and parsed['physical_fidelity'] == 'not_established'
    for name, path, status in (
            ('plan', root / 'data/capture-planned-example.json', 'planned'),
            ('recorded', demo / 'corpus/reference.json', 'declarations_incomplete')):
        answer = execute(phase + '-readiness-' + name,
                         python_tool(root, 'capture_readiness', '--input', path), 3, FOREIGN)
        parsed = value(answer)
        assert parsed['status'] == status and set(parsed['claims'].values()) == {'not_established'}
        assert parsed['calibration_context'] == 'raw_acquisition_only'
    answer = execute(phase + '-planned-corpus', python_tool(root, 'capture_corpus',
                     '--input', root / 'data/corpus-planned-example.json'), 3, FOREIGN)
    assert value(answer)['status'] == 'inconclusive'
    answer = execute(phase + '-demo-corpus', python_tool(root, 'capture_corpus',
                     '--input', demo / 'corpus/corpus.json', '--check-files', '--check-audio'), 0, FOREIGN)
    parsed = value(answer)
    assert parsed['status'] == 'pass' and parsed['physical_fidelity'] == 'not_established'
    answer = execute(phase + '-raw-audio', python_tool(root, 'capture_audio', '--input',
                     demo / 'corpus/audio/reference.f32', '--raw-format', 'raw_float32_le',
                     '--sample-rate-hz', '4', '--channel-count', '1'), 0, FOREIGN)
    audio = value(answer, False)
    assert audio['frame_count'] == 4 and audio['channel_count'] == 1 and audio['sample_rate_hz'] == 4
    for suffix, status, exit_code, rms in (
            ('pass', 'pass', 0, .25), ('inconclusive', 'inconclusive', 3, .25),
            ('fail', 'failed', 1, .5)):
        output = report_dir / ('job-' + suffix + '.json')
        answer = execute(phase + '-job-' + suffix, python_tool(root, 'capture_job',
                         '--input', demo / ('job-' + suffix + '.json'), '--output', output),
                         exit_code, FOREIGN)
        parsed = value(answer)
        assert parsed['status'] == status
        assert parsed['evaluation']['comparison']['channels'][0]['metrics']['rms_error_fs']['value'] == rms
        unknown(parsed)
        assert output.read_bytes() == answer.stdout
        reports['job-' + suffix] = (output, answer.stdout)
    output = report_dir / 'study.json'
    answer = execute(phase + '-study', python_tool(root, 'capture_study', '--input',
                     demo / 'study.json', '--output', output), 1, FOREIGN)
    parsed = value(answer)
    assert parsed['status'] == 'failed'
    assert [x['report']['status'] for x in parsed['jobs']] == ['pass', 'inconclusive', 'failed']
    assert parsed['summary'] == {'jobs': 3, 'pass': 1, 'inconclusive': 1, 'failed': 1,
            'roles': {'fit': 0, 'validation': 3, 'final_test': 0, 'unassigned': 0}}
    assert parsed['work'] == {'spectral_terms': 12, 'window_samples': 12}
    unknown(parsed)
    for item in parsed['jobs']:
        unknown(item['report'])
    assert output.read_bytes() == answer.stdout
    reports['study'] = (output, answer.stdout)
    checked(phase + '-capture-pipeline', '10 real commands; original planned/incomplete/pass/inconclusive/failed outcomes retained')


def native_flow(bin_dir, data_dir, plot_dir, phase):
    output = OUTPUT / phase
    output.mkdir()
    answer = execute(phase + '-render', [bin_dir / 'hammond_render', '--profile', data_dir / 'nominal.b3p',
                     '--events', data_dir / 'fixtures/a4-fundamental-v1.events', '--output', output / 'a4.wav',
                     '--sample-rate', '48000', '--frames', '72000', '--block-size', '127', '--seed', '2602',
                     '--drawbars', '008000000', '--fail-on-clip'], 0, FOREIGN)
    rendered = value(answer, False)
    assert rendered['status'] == 'ok' and rendered['clipped_frames'] == 0
    with wave.open(str(output / 'a4.wav'), 'rb') as sound:
        assert (sound.getnchannels(), sound.getsampwidth(), sound.getframerate(), sound.getnframes()) == (2, 2, 48000, 72000)
        pcm = sound.readframes(72000)
    assert any(pcm)
    assert all(pcm[n:n+2] == pcm[n+2:n+4] for n in range(0, len(pcm), 4))
    for tool, extra in [('hammond_model_info', []), ('hammond_parameter_info', ['--normalized', '0.5'])]:
        answer = execute(phase + '-' + tool, [bin_dir / tool, *extra], 0, FOREIGN)
        parsed = value(answer, False)
        (output / (tool + '.json')).write_bytes(answer.stdout)
        if tool == 'hammond_model_info':
            assert parsed['source_generator']['source_count'] == 91
            assert parsed['physical_fidelity'] == 'unestablished'
        else:
            assert len(parsed['parameters']) == 45 and parsed['host_exports_verified'] is False
    for subject, scenario, seed in [('console', 'partial', '0'), ('pedal', 'overlap', '2705')]:
        csv = output / (subject + '.csv')
        execute(phase + '-' + subject + '-trace', [bin_dir / ('hammond_' + subject + '_trace'),
                '--profile', data_dir / 'nominal.b3p', '--scenario', scenario, '--sample-rate', '48000',
                '--seed', seed, '--output', csv], 0, FOREIGN)
        svg = output / (subject + '.svg')
        execute(phase + '-' + subject + '-plot', [sys.executable, '-B', '-S',
                plot_dir / ('plot_' + subject + '_trace.py'), '--input', csv, '--output', svg], 0, FOREIGN)
        assert b'<svg' in svg.read_bytes()
        assert hashlib.sha256(csv.read_bytes()).hexdigest().encode() in svg.read_bytes()
    checked(phase + '-native-flows', 'All five native tools and both stdlib plotters executed; WAV 72000 frames, 48000Hz, identical PCM16 stereo, no clipping')
    return inventory(output)


def main(commit):
    global LOGS, FOREIGN, OUTPUT, ENV
    WORK.mkdir(exist_ok=False)
    LOGS = WORK / 'logs'; LOGS.mkdir()
    FOREIGN = WORK / 'unrelated working café'; FOREIGN.mkdir()
    OUTPUT = WORK / 'outputs café'; OUTPUT.mkdir()
    ENV = {k: v for k, v in os.environ.items()
           if not k.startswith('HAMMOND_') and k not in ('PYTHONPATH', 'PYTHONHOME', 'CMAKE_INSTALL_MODE')}
    ENV.update(PYTHONPATH='', PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', PYTHONIOENCODING='ascii:strict')
    RESULT.update(source_commit=commit,
                  source_tree=subprocess.check_output(['git', 'rev-parse', commit + '^{tree}'], cwd=REPO, text=True).strip(),
                  runtime={'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
                           'machine': platform.machine()}, environment={'PYTHONPATH': '', 'site_import_disabled': True,
                           'PYTHONIOENCODING': 'ascii:strict', 'HAMMOND_variables_removed': True})
    save()
    source = WORK / 'source café path'; source.mkdir()
    build = WORK / 'build café path'
    prefix = WORK / 'initial prefix café'
    moved = WORK / 'moved prefix café'
    archive = subprocess.check_output(['git', 'archive', commit], cwd=REPO)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(source, filter='data')
    assert not (source / '.git').exists()
    source_inventory = inventory(source)
    RESULT['source_inventory'] = source_inventory
    execute('cmake-version', [CMAKE, '--version'])
    execute('compiler-version', ['/usr/bin/c++', '--version'])
    execute('configure', [CMAKE, '-S', source, '-B', build, '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF',
            '-DHAMMOND_BUILD_VST3=OFF', '-DHAMMOND_BUILD_STANDALONE=OFF', '-DPython3_EXECUTABLE=' + sys.executable])
    assert not (build / 'hammond_render').exists()
    execute('capture-install-before-build', [CMAKE, '--install', build, '--config', 'Release',
            '--component', 'CaptureTools', '--prefix', prefix])
    capture = prefix / 'share/hammond-b3-organ/capture-tools'
    capture_inventory = inventory(capture)
    assert len(CAPTURE) == 57 and set(capture_inventory) == CAPTURE
    for relative in CAPTURE - {'README.md'}:
        assert capture_inventory[relative] == source_inventory[relative]
    checked('capture-before-native-build', {'files': len(capture_inventory),
            'bytes': sum(x['size_bytes'] for x in capture_inventory.values()), 'copied_source_files': 56})
    RESULT['capture_inventory'] = capture_inventory
    source_reports = {}
    pipeline(source, 'source', source_reports)
    execute('build-five-native-tools', [CMAKE, '--build', build, '--config', 'Release', '--parallel', '2',
            '--target', *NATIVE])
    execute('offline-coinstall', [CMAKE, '--install', build, '--config', 'Release',
            '--component', 'OfflineTools', '--prefix', prefix])
    combined = inventory(prefix)
    expected = OFFLINE | {'share/hammond-b3-organ/capture-tools/' + x for x in CAPTURE}
    assert len(OFFLINE) == 23 and set(combined) == expected and len(combined) == 80
    assert inventory(capture) == capture_inventory
    for name in NATIVE:
        assert (prefix / 'bin' / name).read_bytes() == (build / name).read_bytes()
    assert (prefix / 'share/hammond-b3-organ/nominal.b3p').read_bytes() == (build / 'nominal.b3p').read_bytes()
    for name in ('plot_console_trace.py', 'plot_pedal_trace.py'):
        assert (prefix / 'bin' / name).read_bytes() == (source / 'tools' / name).read_bytes()
    for name in OLD_FIXTURES:
        assert (prefix / 'share/hammond-b3-organ/fixtures' / name).read_bytes() == (source / 'examples/fixtures' / name).read_bytes()
    checked('coinstalled-inventories', 'Exactly80 files:57 capture+23 unchanged offline payload paths/bytes; no symlinks')
    RESULT['combined_inventory'] = combined
    execute('capture-reinstall-reject', [CMAKE, '--install', build, '--config', 'Release',
            '--component', 'CaptureTools', '--prefix', prefix], 1)
    assert inventory(prefix) == combined
    checked('capture-reinstall-preserves-both', 'Existing package rejection preserves all80 payload files')
    # Exercise same-build original tools before discarding all native build inputs.
    native_data = WORK / 'native explicit data before'
    native_data.mkdir()
    shutil.copyfile(build / 'nominal.b3p', native_data / 'nominal.b3p')
    shutil.copytree(source / 'examples/fixtures', native_data / 'fixtures')
    before_native = native_flow(build, native_data, source / 'tools', 'native-before')
    assert inventory(source) == source_inventory
    checked('source-unchanged', {'files': len(source_inventory), 'bytes': sum(x['size_bytes'] for x in source_inventory.values())})
    prefix.rename(moved)
    assert inventory(moved) == combined
    # Only these task-created private paths are removed; the shared checkout is never changed.
    for path in (source, build, native_data):
        assert path.parent == WORK and path != REPO
        shutil.rmtree(path)
        assert not path.exists()
    assert not prefix.exists()
    checked('relocation-and-removal', 'Original prefix, private source, build and pre-move native data absent')
    capture = moved / 'share/hammond-b3-organ/capture-tools'
    installed_reports = {}
    pipeline(capture, 'installed', installed_reports)
    for key in source_reports:
        assert installed_reports[key][1] == source_reports[key][1]
    checked('complete-report-relocation-equality', 'All3 jobs and mixedstudy byte-identical between source and installed executions')
    for key, (old_path, old_bytes) in source_reports.items():
        kind = 'study' if key == 'study' else 'job'
        input_path = capture / 'examples/capture-demo' / (key + '.json')
        output = OUTPUT / (key + '-replay.json')
        answer = execute('replay-original-' + key, python_tool(capture, 'verify_capture_report',
                         '--kind', kind, '--input', input_path, '--report', old_path, '--output', output), 0, FOREIGN)
        parsed = value(answer)
        assert parsed['status'] == 'match' and parsed['exact_report_match'] is True
        assert parsed['context']['same_runtime'] and parsed['context']['same_tool_sources']
        assert parsed['saved_engineering_status'] == json.loads(old_bytes)['status'] == parsed['replayed_engineering_status']
        unknown(parsed)
        assert old_path.read_bytes() == old_bytes and output.read_bytes() == answer.stdout
    checked('four-cross-location-replays', 'Pass/inconclusive/failed jobs and failedstudy replay exact original source reports without oldsource/build')
    preserve_path, preserve_bytes = installed_reports['job-pass']
    answer = execute('job-output-no-clobber', python_tool(capture, 'capture_job', '--input',
                     capture / 'examples/capture-demo/job-pass.json', '--output', preserve_path), 1, FOREIGN)
    assert answer.stdout == b'' and preserve_path.read_bytes() == preserve_bytes
    answer = execute('generator-existing-reject', python_tool(capture, 'make_capture_demo',
                     '--output', capture / 'examples/capture-demo'), 1, FOREIGN)
    assert answer.stdout == b'' and inventory(moved) == combined
    checked('runtime-no-clobber', 'Existing report and installed demo rejected with unchanged bytes and empty stdout')
    # Copy each promised standalone script by itself, with no sibling tool or site package.
    for name in ('make_capture_demo', 'validate_capture'):
        single = WORK / ('single script ' + name + ' café'); single.mkdir()
        script = single / (name + '.py'); shutil.copyfile(capture / 'tools' / script.name, script)
        execute('single-' + name + '-help', [sys.executable, '-B', '-S', script, '--help'], 0, FOREIGN)
        if name == 'make_capture_demo':
            destination = OUTPUT / 'standalone generated café'
            answer = execute('single-generator-work', [sys.executable, '-B', '-S', script, '--output', destination], 0, FOREIGN)
            assert value(answer)['execution'] == 'not_run'
            assert inventory(destination) == inventory(capture / 'examples/capture-demo')
        else:
            answer = execute('single-validator-work', [sys.executable, '-B', '-S', script, '--input',
                    capture / 'examples/capture-demo/corpus/reference.json', '--check-files'], 0, FOREIGN)
            assert value(answer, False)['file_check']['status'] == 'verified'
        assert set(inventory(single)) == {script.name}
    checked('standalone-script-closure', 'Each isolated script needs only standardlibrary and its explicit data; generatorrecreates16originalfiles')
    after_native = native_flow(moved / 'bin', moved / 'share/hammond-b3-organ', moved / 'bin', 'native-after')
    assert before_native == after_native
    checked('native-relocation-equality', 'FullWAV,2metadataJSON,2CSV and2SVG outputs are byte-identical after source/build deletion')
    RESULT['native_outputs'] = after_native
    RESULT['capture_reports'] = {key: identity(data) for key, (_, data) in installed_reports.items()}
    assert inventory(moved) == combined
    assert not any(moved.rglob('__pycache__'))
    checked('installed-input-preservation', 'All80 installedfiles unchanged; no bytecode or source fallback')
    RESULT['status'] = 'passed'
    RESULT['command_count'] = COUNTER
    RESULT['check_count'] = len(RESULT['checks'])
    save()
    print(json.dumps({'status': RESULT['status'], 'commands': COUNTER, 'checks': len(RESULT['checks']),
                      'source_commit': commit, 'source_tree': RESULT['source_tree']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--commit', required=True)
    arguments = parser.parse_args()
    try:
        main(arguments.commit)
    except BaseException as error:
        RESULT['unexpected_failure'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        if WORK.exists():
            save()
        raise
```

## Handoff and boundaries

No unexpected audit failure, harness runtime failure, skipped flow or producer
repair occurred. The source and installed bytes stayed unchanged through their
stated observation boundaries. No genuine acquisition or private user data was
introduced. Original demo and nominal native fixtures remain explicitly synthetic.

Root should review and accept these two owned records, include the observed
commands in the runbook, preserve the exact local/public source mapping, and
publish with the standing guarded workflow. A changed module, data binding,
payload rule or native input requires the affected source-qualified flow again.
This finite local exercise does not assert all filesystem races, all failure
modes, Windows/macOS, other interpreters, compiler-runtime bundling, a clean OS,
VST3/SDL device behavior, DAW integration, timing deadlines, signed distribution,
rights, measurement calibration, holdout history or instrument fidelity.

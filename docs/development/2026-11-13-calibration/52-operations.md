# Assignment 52 — operational runbook

Actual worker: **`/root/cal_w9_a52`**, assignment **52**, logical wave **9** of
session `2026-11-13-calibration`. This is one newly dispatched worker; no other
worker was spawned or counted by this assignment. Work was performed on
2026-11-14 UTC.

## Owned deliverable and decision

Owned exactly this note and [CALIBRATION_RUNBOOK.md](../../CALIBRATION_RUNBOOK.md).
The runbook gives source and installed command paths, expected exits, original
report handling, replay interpretation, package boundaries and the next-agent
workflow. It changes no production code, contract, maintained test, package
inventory, shared status, assignment ledger or Git ref. Root owns acceptance,
integration, shared pointers, commit and publication.

**All fifteen final public source commands met their independently stated
expected outcomes, with zero unexpected outcomes.** Four exact replays retain
all three engineering statuses. Saved files match their command stdout bytes;
existing output is preserved; the regenerated archive has exactly sixteen files
and 32,831 bytes, identical to the original. All 28 copied source/input files,
282,903 bytes, remain unchanged. This is a finite command verification, not a
new unittest suite or a full project gate.

## Read source and design choices

Read the standing AGENTS instructions, root README, PLAN, calibration scope,
current STATUS/NEXT_STEPS/development log, operational handoff and the installed
CaptureTools contract. Read the relevant readiness, audio, job, policy, study,
demo and replay behavior, and the existing offline/native handoff links. The
session's six original readers and consolidated atlas review own full-PDF
coverage; this assignment does not claim a new complete PDF or external-source
review.

The guide leads with a runnable source workflow, keeps expected exits beside
each command, and avoids success-only chaining across a deliberately failed
study. It separates structural validation, present declarations, inspected
bytes, corpus graph results, numerical outcomes and replay equality. It names
fresh output paths and the distinction between an already published report and
later stream-delivery failure. Saved job/study reports remain original canonical
bytes; EXPECTED.json and generation inventories remain unexecuted oracles.

User setup selects current fetched main or an explicitly published historical
identity. Historical local acceptance SHAs and scratch paths are context in
notes, not public clone prerequisites. The runbook delegates evolving acceptance
and task counts to the current status/handoff/manifest instead of freezing a
stale completion total. It keeps the new runbook outside the frozen 57-file
installation inventory, points installed users to their actual README/copied
guides, and preserves the standalone generator/validator exceptions without
calling every script a standalone package.

The installed prerequisites and command forms were read directly from the
contract and confirmed against assignment 50's independently executed review.
The runbook attributes that installed evidence. This worker did not configure,
build, install, remove or relocate a native package and does not count worker
50's invocations as its own.

## Exact qualified source and environment

| Observation | Value |
| --- | --- |
| Immutable local source commit | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` |
| Exact Git tree | `3edea0838b75feb06c19e151ec8539e80646fc03` |
| Frozen archive used | `/workspace/scratch/c9f3ead4c910/w8-combined-source` |
| Observed start HEAD/tree | Same local commit/tree above |
| Observed fetched remote at start | `3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf` |
| Final private copied source | `/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京` |
| Child working directory | `/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/foreign working directory` |
| Runtime | CPython 3.12.14, Clang 22.1.3, Linux 6.18.57 x86_64, glibc 2.41 |
| Child invocation | Selected interpreter with `-B -S`; explicit absolute script/input/output paths |
| Child environment overrides | `PYTHONDONTWRITEBYTECODE=1`, empty `PYTHONPATH`, `PYTHONIOENCODING=ascii:strict` |

The copied closure contains ten `.py` files, two planning JSON inputs and the
sixteen-file unchanged demo. It contains no test helper, installed site package,
compiled engine or runtime schema dependency. Each copied source/input identity
was compared with its frozen archive counterpart after the completed run; all
match. All copies remained unchanged before/after execution. Only private result
files and a private regenerated demo were created.

| Module | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/capture_audio.py` | 30313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `tools/capture_common.py` | 12774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `tools/capture_corpus.py` | 39476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `tools/capture_job.py` | 24433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `tools/capture_readiness.py` | 11630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `tools/capture_study.py` | 16849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `tools/compare_capture.py` | 33448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/make_capture_demo.py` | 25734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `tools/validate_capture.py` | 28237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `tools/verify_capture_report.py` | 23489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

## Executed verification and outcomes

Top-level final command, executed from the repository root:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a52-verify-operations.py
```

The final process exits 0. The command's final stdout is:

```json
{"inputs_unchanged": true, "processes": 15, "results": "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/result.json", "unexpected_outcomes": 0}
```

No elapsed-time or performance threshold is inferred. Each ordinary operation
emitted empty stderr. The final existing-output rejection deliberately returned
1, emitted no stdout and preserved the prior passing report; its stderr identified
an existing destination. Its temporary filename and escaped private path are
run-specific diagnostic context, not a stable expected error string.

| Command case | Expected / observed exit | Stdout bytes | Stdout SHA-256 |
| --- | ---: | ---: | --- |
| validate-plan | 0 / 0 | 235 | `e37771d2802f6fc49298a2edbaa63e9d323579d319fe2aa114638775b4068d21` |
| readiness-plan | 3 / 3 | 10488 | `0e57b5435517a8a72be25cd3177ba9d15b334021d2ba732d0358f12f482413d4` |
| corpus-plan | 3 / 3 | 1954 | `68176e91ad5f7ee87a14990549809dab8b7734c397123a685af9418e6c49d590` |
| corpus-demo | 0 / 0 | 7277 | `f9d763ef64db724521313a52750e805e2e2df3e3d632ce561fe3135a8401c04a` |
| audio-reference | 0 / 0 | 1386 | `e82dc995c11fffeda0e6ad7a422c39abaea52e35a9385cd1dffcca6da00e598f` |
| job-pass | 0 / 0 | 32695 | `fe4628d7b8fe78f2d15fd86e0acc16494bc552e25caaebd24bb4b09f5b2e9547` |
| job-inconclusive | 3 / 3 | 32783 | `c39a060fadf9c3fbf71b1608c3884e62bf25b67fa4168f0948fe021646bb0930` |
| job-fail | 1 / 1 | 32660 | `ba1e39fc5f5410491f7826346c7259dfcf8b603dffbc0a260a9886ed66252321` |
| study | 1 / 1 | 119427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` |
| replay-pass | 0 / 0 | 3916 | `709f2d4f396c5c44c83165f18b61873f9b84b3a48ae2deb36f94401570c4b3cf` |
| replay-inconclusive | 0 / 0 | 3932 | `aabf8aa7fed0eb055d848f61f9ffa1616d53c32bfbbd332e559a81a85fd7646f` |
| replay-fail | 0 / 0 | 3920 | `765e10522a39c01ecb731c7f5439f1f28108fad6461d2e7fe50a9bac032f5056` |
| replay-study | 0 / 0 | 4262 | `5c6b8ad9c208566c887c92ba00e04978c304c20902d486a8474d47178e5e59db` |
| generate-demo | 0 / 0 | 2814 | `4134299381cbc1964dec8d886aa559863a666ecd36f0a3e61560b4e44ba52e0c` |
| preserve-existing-output | 1 / 1 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The v1 plan remains `planned` with `structural_validation: "pass"`. Readiness
remains planned with twenty missing declarations and seven unknown claims.
The plan corpus is inconclusive; the complete demo corpus passes. The inspected
raw reference has four frames, one channel and the explicit synthetic rate 4.
The three job RMS values are literal 0.25/0.25/0.5 FS, with outcomes
pass/inconclusive/failed. The mixed study retains one of each result and remains
failed. Every job and replay retains the ten independently typed unknown
physical/evidence fields. All four replays match their original canonical reports
and preserve their underlying outcomes and original report bytes.

Nine saved JSON outputs (readiness, three jobs, study, four replay summaries)
match their exact stdout bytes. The sixteen newly generated inputs are unchanged
relative to the original demo; both their inventory and EXPECTED.json retain
`execution: "not_run"`. The output tree therefore contains 25 files and 276,914 bytes.
Audio inspection includes its selected absolute input path; its observed hash is
specific to this run. Source/runtime observations also qualify job/study/report
identities, so these hashes are not universal expected outputs for another tree
or interpreter.

Actual child commands, in order, with every argument JSON-quoted for legibility:

```text
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/validate_capture.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/data/capture-planned-example.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_readiness.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/data/capture-planned-example.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/readiness.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_corpus.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/data/corpus-planned-example.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_corpus.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/corpus/corpus.json" "--check-files" "--check-audio"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_audio.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/corpus/audio/reference.f32" "--raw-format" "raw_float32_le" "--sample-rate-hz" "4" "--channel-count" "1"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_job.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-pass.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-pass.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_job.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-inconclusive.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-inconclusive.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_job.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-fail.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-fail.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_study.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/study.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/study.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/verify_capture_report.py" "--kind" "job" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-pass.json" "--report" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-pass.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/pass-replay.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/verify_capture_report.py" "--kind" "job" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-inconclusive.json" "--report" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-inconclusive.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/inconclusive-replay.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/verify_capture_report.py" "--kind" "job" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-fail.json" "--report" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-fail.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/fail-replay.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/verify_capture_report.py" "--kind" "study" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/study.json" "--report" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/study.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/study-replay.json"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/make_capture_demo.py" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/new-demo"
"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3" "-B" "-S" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/tools/capture_job.py" "--input" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/source café 東京/examples/capture-demo/job-pass.json" "--output" "/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete/reports café 東京/job-pass.json"
```

## Retained harness mistakes

The first harness was 7,028 bytes, SHA-256
`3dab0dc72c9757216ee82fe384f45472d4c8047aebbf061c1de52e225c47b626`.
It stopped after the successful validator invocation with an AssertionError
because the audit expected `structural_validation == "passed"`. The unchanged
source/contract emits `"pass"`; the actual child exited 0. A separate inspection
confirmed that output. The original harness is preserved as
`a52-verify-operations-first.py`. That run did not reach the later commands and
is not counted as a completed fifteen-command gate.

The second harness was 7,032 bytes, SHA-256
`0b9529bc3cd90716fe2b42101fe929c4c6cfb5ff09c036b0042386c4a6606b80`.
It passed the preceding command/metric assertions, then stopped at the first
job's claim check with `KeyError: 'claims'`. Readiness has a nested claims map;
job/replay claims are named top-level fields. The original job source and report
were correct. The second harness and its 237-byte failure log are preserved;
that log SHA-256 is
`09381f8d0033c6b73989f7af9ef23ed1f5e9db7143a7d996f113ee5e8c148091`.

Only audit assertions were corrected: the exact structural-validation token and
access to the ten separately typed top-level claim fields. A new private working
directory was used each time, preserving earlier copies and outputs. No producer,
input, numerical margin, intended status, policy or expected exit changed.
The final harness is 7,262 bytes, SHA-256
`1c9dc1528228782a73ca88409a340876cb137cccb324c972b9b6fca377e629e2`.
Reversing those two precise assertion edits and working-directory names
reconstructed both earlier harness hashes exactly. The full final source is
embedded below so those earlier states remain reconstructible without scratch.

## Independent installed-workflow evidence used in the guide

Worker 50 `/root/cal_w9_a50` qualified its own fresh archive/build from the same
`48a1907` / tree `3edea083` source. I read the complete frozen
[clean-setup review](../../reviews/CALIBRATION_CLEAN_SETUP.md), which is 11,397 bytes,
SHA-256 `0f44c763a0e79fd08cfb2dd72f386ddd1ccedc356d50851c800e5216c77e3461`.
It records 51 setup/runtime commands and 15 grouped checks, all expected outcomes,
with no unexpected failure or skipped flow. It installed 57 CaptureTools files
before native compilation, then built the five offline executables and
co-installed 23 OfflineTools files. The final 80-file prefix survived relocation,
removal of only its private source/build, all capture workflows, exact replay
of original source-run reports, and all five native offline tools/two plotters.
All installed files remained unchanged. This is explicitly worker 50's execution.

The successful command forms in that review match the runbook's CMake flags,
component selection, default `share` path and separate native-build prerequisite.
The observed package byte counts and tool versions belong to that identified
source; the public runbook preserves stable inventory counts without implying
that future edited documentation or binaries retain those same sizes. Native
Windows/macOS, clean-OS, device/DAW, signing and physical gates remain outside
that local setup evidence.

## Retained artifacts and complete input identity

The final result JSON is 22,739 bytes, SHA-256
`43cfc7a5f67480a39963ace33b1e02f7a672ca302d7c53fa5feb0beafe813872`. The 161-byte successful stdout log has SHA-256
`969f94297fd8675323ac50ffa2f85b82bdcfda76f9ccf2917b3b00b9a36075f4`.
They reside in the task's scratch area; this note retains the substantive command
ledger, inputs, outcomes, identities and exact executable audit. No requirement
to fetch an agent's private path is imposed on users.

```json
{
  "data/capture-planned-example.json": {
    "size_bytes": 3223,
    "sha256": "35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac"
  },
  "data/corpus-planned-example.json": {
    "size_bytes": 466,
    "sha256": "9c23a5faf002472d50e9c4e5e923bdb46e95091ee026288d98a91b785a7c4e2e"
  },
  "examples/capture-demo/EXPECTED.json": {
    "size_bytes": 4425,
    "sha256": "8b3ade3def7f51119b90f5a65bc9fa3bf7c46ab561929a60acdd973245793396"
  },
  "examples/capture-demo/README.md": {
    "size_bytes": 6127,
    "sha256": "867618f49b41d88eaba13a86048190d4f0db30bc34b453adb9d51ce8fd1e4b08"
  },
  "examples/capture-demo/corpus/audio/half.f32": {
    "size_bytes": 16,
    "sha256": "36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758"
  },
  "examples/capture-demo/corpus/audio/quarter.f32": {
    "size_bytes": 16,
    "sha256": "bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2"
  },
  "examples/capture-demo/corpus/audio/reference.f32": {
    "size_bytes": 16,
    "sha256": "fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402"
  },
  "examples/capture-demo/corpus/corpus.json": {
    "size_bytes": 1295,
    "sha256": "1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361"
  },
  "examples/capture-demo/corpus/half.json": {
    "size_bytes": 4589,
    "sha256": "281945a1b21b473949eb1049c489f21d2e506c96fd859412a97737631d94d0f5"
  },
  "examples/capture-demo/corpus/quarter.json": {
    "size_bytes": 4599,
    "sha256": "2727e5b2ef50652d96be9e2b55880eba9390c1b6804addc7af2d39878f8f7e54"
  },
  "examples/capture-demo/corpus/reference.json": {
    "size_bytes": 4599,
    "sha256": "e3d5761fa8f6d3351c82fdc72a13df8c8db9458f07fba401cb22f1fe85fef970"
  },
  "examples/capture-demo/job-fail.json": {
    "size_bytes": 787,
    "sha256": "f2fad01bdafbebd14517cb0d9f6e8b3ce8e1541135358308818671327c27e703"
  },
  "examples/capture-demo/job-inconclusive.json": {
    "size_bytes": 806,
    "sha256": "d66a0d0f5762ed6f961e9db2a36426e0b308973547d62ee25be9bf44f42568c6"
  },
  "examples/capture-demo/job-pass.json": {
    "size_bytes": 790,
    "sha256": "63f83d706b412cc4cd7a76957f924cb9c6970436593fdae3e0fd8724dea66e45"
  },
  "examples/capture-demo/policy-fail.json": {
    "size_bytes": 1346,
    "sha256": "c1025c652a3b85be75b10420ae87aca2db6bd8bf748e0218e5b2cd260e77ee3c"
  },
  "examples/capture-demo/policy-inconclusive.json": {
    "size_bytes": 1362,
    "sha256": "23684a20f7cf263645fc7b4124804d248a114fba79973280818986ee48dd5e43"
  },
  "examples/capture-demo/policy-pass.json": {
    "size_bytes": 1348,
    "sha256": "8300754d2088849d6a8fe042f248543e1c9965229b4ad9cc220f45bfa31cccc5"
  },
  "examples/capture-demo/study.json": {
    "size_bytes": 710,
    "sha256": "725e91cd3264d420018f2a6d269a27ed47f941e0e17b0abd09c81a71dafb717a"
  },
  "tools/capture_audio.py": {
    "size_bytes": 30313,
    "sha256": "f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216"
  },
  "tools/capture_common.py": {
    "size_bytes": 12774,
    "sha256": "f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab"
  },
  "tools/capture_corpus.py": {
    "size_bytes": 39476,
    "sha256": "baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8"
  },
  "tools/capture_job.py": {
    "size_bytes": 24433,
    "sha256": "a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b"
  },
  "tools/capture_readiness.py": {
    "size_bytes": 11630,
    "sha256": "816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1"
  },
  "tools/capture_study.py": {
    "size_bytes": 16849,
    "sha256": "5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98"
  },
  "tools/compare_capture.py": {
    "size_bytes": 33448,
    "sha256": "220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a"
  },
  "tools/make_capture_demo.py": {
    "size_bytes": 25734,
    "sha256": "67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535"
  },
  "tools/validate_capture.py": {
    "size_bytes": 28237,
    "sha256": "f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa"
  },
  "tools/verify_capture_report.py": {
    "size_bytes": 23489,
    "sha256": "6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba"
  }
}
```

## Exact final audit source

```python
from pathlib import Path
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys

FROZEN = Path('/workspace/scratch/c9f3ead4c910/w8-combined-source')
WORK = Path('/workspace/scratch/c9f3ead4c910/a52-operations-20261114-complete')
WORK.mkdir(exist_ok=False)
SOURCE = WORK / 'source café 東京'
REPORTS = WORK / 'reports café 東京'
FOREIGN = WORK / 'foreign working directory'
for p in (SOURCE / 'tools', SOURCE / 'data', REPORTS, FOREIGN):
    p.mkdir(parents=True)
MODULES = ('capture_audio', 'capture_common', 'capture_corpus', 'capture_job',
           'capture_readiness', 'capture_study', 'compare_capture',
           'make_capture_demo', 'validate_capture', 'verify_capture_report')
CLAIMS = ('boundary_equivalence', 'synchronization', 'authenticity', 'specimen_identity',
          'calibration', 'permissions', 'independence', 'preregistration',
          'final_holdout_history', 'physical_fidelity')
for name in MODULES:
    shutil.copyfile(FROZEN / 'tools' / (name + '.py'), SOURCE / 'tools' / (name + '.py'))
for name in ('capture-planned-example.json', 'corpus-planned-example.json'):
    shutil.copyfile(FROZEN / 'data' / name, SOURCE / 'data' / name)
shutil.copytree(FROZEN / 'examples/capture-demo', SOURCE / 'examples/capture-demo')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def inventory(root):
    return {p.relative_to(root).as_posix(): {'size_bytes': p.stat().st_size,
             'sha256': sha(p.read_bytes())} for p in sorted(root.rglob('*')) if p.is_file()}

before = inventory(SOURCE)
environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH='',
                   PYTHONIOENCODING='ascii:strict')
observations = []

def run(label, module, args, expected, output=None, reject=False):
    command = [sys.executable, '-B', '-S', str(SOURCE / 'tools' / (module + '.py')),
               *[str(a) for a in args]]
    result = subprocess.run(command, cwd=FOREIGN, env=environment,
                            capture_output=True, timeout=30)
    row = {'label': label, 'command': command, 'expected_exit': expected,
           'observed_exit': result.returncode, 'stdout_size': len(result.stdout),
           'stdout_sha256': sha(result.stdout),
           'stderr': result.stderr.decode('utf-8', errors='strict')}
    observations.append(row)
    assert result.returncode == expected, row
    if reject:
        assert not result.stdout and result.stderr, row
        return None
    assert not result.stderr, row
    value = json.loads(result.stdout)
    row['status'] = value.get('status', value.get('record_status', value.get('execution')))
    if output:
        assert output.read_bytes() == result.stdout, row
        row['saved_output'] = {'size_bytes': len(result.stdout), 'sha256': sha(result.stdout)}
    return value

demo = SOURCE / 'examples/capture-demo'
plan = SOURCE / 'data/capture-planned-example.json'
value = run('validate-plan', 'validate_capture', ['--input', plan], 0)
assert value['record_status'] == 'planned' and value['structural_validation'] == 'pass'
readiness = REPORTS / 'readiness.json'
value = run('readiness-plan', 'capture_readiness', ['--input', plan, '--output', readiness], 3, readiness)
assert value['status'] == 'planned' and value['summary']['missing'] == 20
assert set(value['claims'].values()) == {'not_established'}
value = run('corpus-plan', 'capture_corpus', ['--input', SOURCE / 'data/corpus-planned-example.json'], 3)
assert value['status'] == 'inconclusive'
value = run('corpus-demo', 'capture_corpus', ['--input', demo / 'corpus/corpus.json', '--check-files', '--check-audio'], 0)
assert value['status'] == 'pass'
value = run('audio-reference', 'capture_audio', ['--input', demo / 'corpus/audio/reference.f32',
            '--raw-format', 'raw_float32_le', '--sample-rate-hz', '4', '--channel-count', '1'], 0)
assert (value['status'], value['frame_count'], value['channel_count'], value['sample_rate_hz']) == ('inspected', 4, 1, 4)

saved = []
for stem, expected, status, rms in (('pass', 0, 'pass', .25),
                                  ('inconclusive', 3, 'inconclusive', .25),
                                  ('fail', 1, 'failed', .5)):
    input_path = demo / ('job-' + stem + '.json')
    output = REPORTS / ('job-' + stem + '.json')
    value = run('job-' + stem, 'capture_job', ['--input', input_path, '--output', output], expected, output)
    assert value['status'] == status
    assert value['evaluation']['comparison']['channels'][0]['metrics']['rms_error_fs']['value'] == rms
    assert {value[name] for name in CLAIMS} == {'not_established'}
    saved.append(('job', stem, input_path, output, status))
study = REPORTS / 'study.json'
value = run('study', 'capture_study', ['--input', demo / 'study.json', '--output', study], 1, study)
assert {key: value['summary'][key] for key in ('jobs', 'pass', 'inconclusive', 'failed')} == {
    'jobs': 3, 'pass': 1, 'inconclusive': 1, 'failed': 1}
saved.append(('study', 'study', demo / 'study.json', study, 'failed'))
for kind, stem, input_path, report, status in saved:
    original = report.read_bytes()
    output = REPORTS / (stem + '-replay.json')
    value = run('replay-' + stem, 'verify_capture_report', ['--kind', kind, '--input', input_path,
                '--report', report, '--output', output], 0, output)
    assert (value['status'], value['saved_engineering_status'], value['replayed_engineering_status']) == ('match', status, status)
    assert value['exact_report_match'] and report.read_bytes() == original
    assert {value[name] for name in CLAIMS} == {'not_established'}
new_demo = REPORTS / 'new-demo'
value = run('generate-demo', 'make_capture_demo', ['--output', new_demo], 0)
assert value['execution'] == 'not_run'
assert inventory(new_demo) == inventory(demo)
assert len(inventory(new_demo)) == 16
assert sum(v['size_bytes'] for v in inventory(new_demo).values()) == 32831
assert json.loads((new_demo / 'EXPECTED.json').read_bytes())['execution'] == 'not_run'
original = (REPORTS / 'job-pass.json').read_bytes()
run('preserve-existing-output', 'capture_job', ['--input', demo / 'job-pass.json',
    '--output', REPORTS / 'job-pass.json'], 1, reject=True)
assert (REPORTS / 'job-pass.json').read_bytes() == original
after = inventory(SOURCE)
assert after == before
assert len(observations) == 15
result = {'source_commit': '48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a',
          'source_tree': '3edea0838b75feb06c19e151ec8539e80646fc03',
          'python': sys.version, 'platform': platform.platform(), 'machine': platform.machine(),
          'working_directory': str(FOREIGN), 'environment_overrides': {
              'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': '', 'PYTHONIOENCODING': 'ascii:strict'},
          'source_and_inputs_before': before, 'source_and_inputs_unchanged': after == before,
          'observations': observations, 'processes': len(observations),
          'unexpected_outcomes': 0, 'report_files': inventory(REPORTS)}
(WORK / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'processes': len(observations), 'unexpected_outcomes': 0,
                  'inputs_unchanged': True, 'results': str(WORK / 'result.json')}, sort_keys=True))
```

## Final document checks

Both owned files are UTF-8 with final LF, no CR and no trailing whitespace.
All 30 local Markdown links resolve. The embedded final audit is byte-identical
to the executed 7,262-byte source and parses as Python. All ten copied modules
still match the frozen and current repository sources. Assignment 50's cited
review still has its recorded hash.

One read-only result-inspection command incorrectly called `len()` on the integer
`processes` count and raised TypeError. The corrected inspection checked
`processes == 15` and the separate fifteen-element `observations` list, then
verified every actual exit against its expected exit and all source identities.
This did not execute another producer or alter any report or the completed audit.

## Integration and next step

Root should accept these two owned files and add a clear runbook link near the
setup section of CALIBRATION_HANDOFF.md and the capture paragraph of the root
README. It can also link the guide from current NEXT_STEPS after final integration.
No CaptureTools inventory expansion is requested; its installed README and 21
copied guides remain the contracted package. Preserve the publication/tree map
and exact hosted outcomes in the integration record rather than duplicating a
stale final count in this guide.

The existing code is ready for the guide's software workflow. The next concrete
development task remains under current NEXT_STEPS/scopes, with actual acquisition,
permissions, specimen/configuration records and metrology needed before a physical
calibration gate. Future agents follow the standing ownership, coherent-source,
meaningful-check, documentation and guarded commit/push workflow. This source
verification establishes no physical measurement, fitted model, independent
holdout history, listening equivalence or native device/host result.

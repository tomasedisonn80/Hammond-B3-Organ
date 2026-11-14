# Assignment 54 — report identity through the CLI source repair

- Actual worker: `/root/cal_w9_a54`; logical wave 9; executed 2026-11-14 UTC.
- Owned repository paths: this note and
  [CALIBRATION_REPORT_IDENTITY_AUDIT.md](../../reviews/CALIBRATION_REPORT_IDENTITY_AUDIT.md).
- Scope: independent finite qualification of retained canonical reports, exact
  source/runtime bindings, unchanged analytical/claim content, public replay
  outcomes and original input preservation across the accepted allocation and
  CLI-only repairs.
- No production, test, CMake, shared-status, ledger or Git edits. Root owns
  integration, acceptance and publication. Frozen copies were used while root
  reconciled concurrent remote changes; no changing working-tree producer was run.

## Outcome and exact execution accounting

**20 finite check groups passed; 22 fresh project CLI interpreters executed.**
Eight producer invocations comprise five studies and three standalone jobs.
Thirteen completed replay invocations comprise eight exact matches and five
expected source mismatches. The twenty-second invocation is the deliberately
noncanonical saved-report rejection, which returns no summary. This count
excludes shell/Python audit processes and read-only Git object queries.

The principal audit executed 19 groups / 20 project processes / 12 complete
replay summaries. A separate check added one group / two processes / one
complete summary to verify a genuinely different working directory with relative
public arguments. It did not repeat the full matrix. No existing replay suite,
CMake/CTest suite or allocation measurement is included in these counts.

There was one prior harness attempt that stopped after its first completed
source check and before any project CLI launch. Its artifact-field assumption
was corrected; the original source and outcome are retained below. There were
no project production failures in this assignment. Expected public mismatches,
failed/inconclusive engineering outcomes and canonical rejection remain explicit.

### Frozen sources and runtime

All thirty tool blobs were compared byte-for-byte with their immutable local
Git objects before execution. The public mapping/status qualification is in the
review. The directories below are exact session provenance, not a claim that a
future machine will have the same paths.

Before this record was frozen, root reported publishing and fetching verification
of `d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree
`0140c737de4db28288b118744c2beef57976697f`, with the public `d377fab7...` and
`5e19022c...` source mappings retained as reachable ancestors. That is root's
publication observation, distinct from this worker's independent local audit.

| Label | Source archive | Local commit | Verified tree |
| --- | --- | --- | --- |
| `allocation459` | `/workspace/scratch/c9f3ead4c910/w8-allocation-source` | `459bfacbda90005d618f12c4513b9c71cb11193d` | `3325af558b040759c1b432ec0806a80785af9713` |
| `final48` | `/workspace/scratch/c9f3ead4c910/w8-combined-source` | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` | `3edea0838b75feb06c19e151ec8539e80646fc03` |
| `original16` | `/workspace/scratch/c9f3ead4c910/w7-installed-source` | `16d72e1b351e5cdf1730e90645a6ea37144d1be7` | `5619bbb018830e071bc2ce45af84984cdd16bfc1` |

Interpreter: `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python`,
Python 3.12.14, Clang 22.1.3. Every project invocation uses `-B -S`; the audit
imports no project producer. Report runtime is exactly:

```json
{
  "machine": "x86_64",
  "python_implementation": "cpython",
  "python_version": "3.12.14",
  "sys_platform": "linux"
}
```

### Actual commands

Working directory for these audit entry points:
`/workspace/scratch/c9f3ead4c910`.

```sh
python -B -S /workspace/scratch/c9f3ead4c910/a54-report-identity-audit.py /workspace/scratch/c9f3ead4c910/a54-identity-run1
# First attempt: harness assertion failure before any project CLI.
python -B -S /workspace/scratch/c9f3ead4c910/a54-report-identity-audit.py /workspace/scratch/c9f3ead4c910/a54-identity-run2
# Corrected finite audit: 19 groups, 20 fresh project CLI processes, pass.
python -B -S /workspace/scratch/c9f3ead4c910/a54-cwd-check.py
# Separate actual-cwd variation: 1 group, 2 fresh project CLI processes, pass.
```

The original first-attempt program is reconstructed exactly by replacing the
following two corrected lines in the retained core harness with the single old
line shown afterwards:

```python
assert item['identity'] == artifact[field]['fresh_report']
assert artifact[field]['original_report'] == artifact['retained_reports']['before']['identity']
# Original incorrect line:
assert item['identity'] == artifact[field]['original_report']
```

The failure was `AssertionError` at line 117. Both independently fixed retained
report hashes had already matched. The artifact's `after.original_report`
deliberately retains `6cf434...`, while `after.fresh_report` and its retained
after value identify `71d514...`. The correction verifies this intended
distinction; it changes no expected digest, production source or saved report.

### Actual process outcomes and stdout identities

The principal audit's child commands all have the prefix
`<recorded-python> -B -S <coherent-copy>/tools/<public-script>`.
The source-copy/input/report arguments are retained verbatim in the core code
below. Empty successful diagnostics are checked explicitly. The deliberately
rejected noncanonical input produces the documented diagnostic and empty stdout.

| Fresh process | Exit | Stdout bytes | Stdout SHA-256 |
| --- | ---: | ---: | --- |
| `original16-study` | 1 | 119,423 | `6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727` |
| `allocation459-study` | 1 | 119,423 | `71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736` |
| `final48-study` | 1 | 119,427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` |
| `original16-own-replay` | 0 | 4,260 | `e81593b98384dc94f2d97799aaedca7c20ea84ada939272b8e4605a88936b998` |
| `allocation459-own-replay` | 0 | 4,260 | `f27c6dbfda6276a39d8d71b27915319d6c8e41a657940ce87d1469fc7832a3a0` |
| `final48-own-replay` | 0 | 4,262 | `5c6b8ad9c208566c887c92ba00e04978c304c20902d486a8474d47178e5e59db` |
| `final48-versus-original16` | 1 | 4,266 | `f66a8827ebdb14c94565af37959311231877c9ff45a96021f6528a88684ec069` |
| `final48-versus-allocation459` | 1 | 4,266 | `2a4ed1a96aafd449e5a930070314588fb54246f701f78ff913326845c31c0209` |
| `final48-job-pass` | 0 | 32,695 | `fe4628d7b8fe78f2d15fd86e0acc16494bc552e25caaebd24bb4b09f5b2e9547` |
| `final48-job-inconclusive` | 3 | 32,783 | `c39a060fadf9c3fbf71b1608c3884e62bf25b67fa4168f0948fe021646bb0930` |
| `final48-job-fail` | 1 | 32,660 | `ba1e39fc5f5410491f7826346c7259dfcf8b603dffbc0a260a9886ed66252321` |
| `final48-own-job-replay-pass` | 0 | 3,916 | `709f2d4f396c5c44c83165f18b61873f9b84b3a48ae2deb36f94401570c4b3cf` |
| `final48-own-job-replay-inconclusive` | 0 | 3,932 | `aabf8aa7fed0eb055d848f61f9ffa1616d53c32bfbbd332e559a81a85fd7646f` |
| `final48-own-job-replay-fail` | 0 | 3,920 | `765e10522a39c01ecb731c7f5439f1f28108fad6461d2e7fe50a9bac032f5056` |
| `final48-old-job-replay-pass` | 1 | 3,920 | `b8f78b221bc4747aed7a7aea0b2650533f42eda77dcf642c66ef84af241c6c8d` |
| `final48-old-job-replay-inconclusive` | 1 | 3,936 | `6f9ebef002281fbb55404b4cd51bb513895a1929780144940e22d8548069ada8` |
| `final48-old-job-replay-fail` | 1 | 3,924 | `b589a39de6b11164190c0980044acc22a526b189c6f3b2cc9ad9e313ffe47d72` |
| `relocated-study` | 1 | 119,427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` |
| `relocated-cross-path-replay` | 0 | 4,262 | `5c6b8ad9c208566c887c92ba00e04978c304c20902d486a8474d47178e5e59db` |
| `noncanonical-report-rejected` | 1 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `second-cwd-study` | 1 | 119,427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` |
| `second-cwd-replay` | 0 | 4,262 | `5c6b8ad9c208566c887c92ba00e04978c304c20902d486a8474d47178e5e59db` |

For the five source mismatches the summaries report `same_runtime=true`,
`same_tool_sources=false` and `exact_report_match=false`. The public output and
exit status are not replaced by the audit's source-independent projection.
The noncanonical rejection is exactly:

```text
replay error: saved report: original bytes must be exact canonical JSON
```

### Finite check groups

| Group | Executed check | Result |
| --- | --- | --- |
| 01 | coherent ten-module frozen source copies match all thirty Git blobs | Pass |
| 02 | original canonical report values reconstruct both retained byte identities | Pass |
| 03 | unchanged sixteen-file archive matches both original inventories and all source snapshots | Pass |
| 04 | allocation change affects one module and CLI repair affects nine modules | Pass |
| 05 | three fresh study interpreters reproduce the independently fixed full report identities | Pass |
| 06 | same-source study replays exactly match while retaining engineering failed | Pass |
| 07 | final source replays both original reports as explicit complete-report mismatches | Pass |
| 08 | three public job commands reproduce full embedded study reports with 0,3,1 exits | Pass |
| 09 | all three same-source job replays match without changing their engineering verdicts | Pass |
| 10 | three retained allocation-source job reports mismatch final sources without edits | Pass |
| 11 | source inventories match actual bytes and literal six/seven producer module closures | Pass |
| 12 | every replay summary binds original input, both reports, contexts and own verifier source | Pass |
| 13 | all forty root/embedded claims and three statuses/roles remain explicitly unchanged | Pass |
| 14 | complete analytical/claim projection is byte-identical across all three sources | Pass |
| 15 | four-byte report growth is exactly four 9625-to-12774 source-size digit changes | Pass |
| 16 | study/job/policy/corpus/manifest/audio identities bind the unchanged original bytes | Pass |
| 17 | Unicode relocation, source/data timestamps and selected environment changes; foreign cwd | Pass |
| 18 | noncanonical copy rejects before emitting a summary and is never normalized in place | Pass |
| 19 | original reports, source snapshots, both archives and artifact remain unchanged | Pass |
| 20 | Different Unicode cwd and relative public input/report arguments preserve full study and replay bytes | Pass |

The core group-12 checkpoint had eleven completed replay summaries; its same
helper checked the twelfth at group 17. The supplementary case requires exact
byte equality to that checked summary, supplying the thirteenth. Group 13 checks
forty root/embedded claim positions in each of three study versions.

## Source and input identity ledger

The ten-module source inventory below records actual bytes. Public producer
inventories select the literal six/seven module sets described in the review;
the separate replay source record is checked in every completed summary. Static
project-import closure is inspected independently, without asserting memory or
bytecode attestation. The unchanged `compare_capture.py` hash appears in all
three versions. Only `capture_corpus.py` differs between original and allocation
versions.

| Module | Original bytes / SHA-256 | Allocation bytes / SHA-256 | Final bytes / SHA-256 |
| --- | --- | --- | --- |
| `capture_audio.py` | 29,951 / `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` | 29,951 / `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` | 30,313 / `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `capture_common.py` | 9,625 / `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` | 9,625 / `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` | 12,774 / `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `capture_corpus.py` | 39,220 / `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` | 39,312 / `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded` | 39,476 / `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `capture_job.py` | 24,302 / `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` | 24,302 / `147002ac866a4451e6740eae69da9f914116339f89b657bae7d4c6ef41e3eded` | 24,433 / `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `capture_readiness.py` | 11,247 / `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` | 11,247 / `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` | 11,630 / `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `capture_study.py` | 16,740 / `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` | 16,740 / `4b627a8c213ff43691e8011dca0a4206db8f4184dd32b5ea6edad4471f90e69d` | 16,849 / `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `compare_capture.py` | 33,448 / `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` | 33,448 / `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` | 33,448 / `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `make_capture_demo.py` | 22,329 / `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` | 22,329 / `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` | 25,734 / `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `validate_capture.py` | 24,827 / `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` | 24,827 / `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` | 28,237 / `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `verify_capture_report.py` | 23,380 / `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` | 23,380 / `23dc1c316232c27345ce35beec667a1e604847dc30b31b9b0b8bfc63423dd2d4` | 23,489 / `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

The unchanged fixture inventory is complete; it includes support documents as
well as actual bound study/job/policy/corpus/manifest/audio inputs. Its canonical
serialization is a sorted array of objects with the keys `path`, `sha256` and
`size_bytes`, using the exact independent `canonical()` function below.

| Relative fixture path | Bytes | SHA-256 |
| --- | ---: | --- |
| `EXPECTED.json` | 4,425 | `8b3ade3def7f51119b90f5a65bc9fa3bf7c46ab561929a60acdd973245793396` |
| `README.md` | 6,127 | `867618f49b41d88eaba13a86048190d4f0db30bc34b453adb9d51ce8fd1e4b08` |
| `corpus/audio/half.f32` | 16 | `36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758` |
| `corpus/audio/quarter.f32` | 16 | `bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2` |
| `corpus/audio/reference.f32` | 16 | `fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402` |
| `corpus/corpus.json` | 1,295 | `1d6e840f5c89ec0f021886e07bc0b0db5e0179fb6a3ce6f4a880f388c3b58361` |
| `corpus/half.json` | 4,589 | `281945a1b21b473949eb1049c489f21d2e506c96fd859412a97737631d94d0f5` |
| `corpus/quarter.json` | 4,599 | `2727e5b2ef50652d96be9e2b55880eba9390c1b6804addc7af2d39878f8f7e54` |
| `corpus/reference.json` | 4,599 | `e3d5761fa8f6d3351c82fdc72a13df8c8db9458f07fba401cb22f1fe85fef970` |
| `job-fail.json` | 787 | `f2fad01bdafbebd14517cb0d9f6e8b3ce8e1541135358308818671327c27e703` |
| `job-inconclusive.json` | 806 | `d66a0d0f5762ed6f961e9db2a36426e0b308973547d62ee25be9bf44f42568c6` |
| `job-pass.json` | 790 | `63f83d706b412cc4cd7a76957f924cb9c6970436593fdae3e0fd8724dea66e45` |
| `policy-fail.json` | 1,346 | `c1025c652a3b85be75b10420ae87aca2db6bd8bf748e0218e5b2cd260e77ee3c` |
| `policy-inconclusive.json` | 1,362 | `23684a20f7cf263645fc7b4124804d248a114fba79973280818986ee48dd5e43` |
| `policy-pass.json` | 1,348 | `8300754d2088849d6a8fe042f248543e1c9965229b4ad9cc220f45bfa31cccc5` |
| `study.json` | 710 | `725e91cd3264d420018f2a6d269a27ed47f941e0e17b0abd09c81a71dafb717a` |

The 16 files total 32,831 bytes. Their canonical inventory is 2,353 bytes, SHA-256 `76fea5dfb708444f75d7b8c53ea687f36a831f6921ec405d5d58e08da4f681ee`.

## Retained audit-artifact identities

These identities identify actual scratch execution artifacts. The complete
auditor source and substantive outputs are retained in this committed note;
temporary machine-local JSON/log paths are not promised as repository files.
The original report values and all original fixture bytes already reside in
the repository. No generated final report overwrites either older value.

Documentation-only verification parsed the retained Python blocks and checked
relative Markdown links and LF encoding. It caught one escaped-newline rendering
error in the first draft of the public example, which was corrected before
freezing this record; no project CLI was rerun or test count added for that edit.

| Actual artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `a54-report-identity-audit-v1.py` | 22,204 | `d49f214cfa41c080c6a7f86a184c1ba40e4d6e1a2d18bdf6244bdd2dc34b1c75` |
| `a54-report-identity-audit.py` | 22,301 | `3a8a317e738af808c9db8ddba55216bd37271f1624abe1c3fce60e53f48f36b3` |
| `a54-cwd-check.py` | 2,646 | `ed72767d4ccc35642e9bab4cb8dd6aac951be90655e7d85a30d3d03e4689e6af` |
| `a54-identity-run1/audit.json` | 6,528 | `f6802b9886350e346541bc0ac8c493a035a490113bf418803c0cada4b3ec5f3c` |
| `a54-identity-run1/failure.txt` | 649 | `f009c6385408853bf3b9c0022f274d6414fcebfc011569da2c23772dece0e0b6` |
| `a54-identity-run2/audit.json` | 93,749 | `088f5db9582ac843a313e3116faadaf9a2ac941cd663e8491d9229c245baf1fc` |
| `a54-cwd-check/result.json` | 1,584 | `84c8c0a2729ad2c8e3e7ce32f4cd993e718bea2d3496735c23fad666febc3218` |

The core harness is executable evidence for the recorded local layout and
immutable local objects. It deliberately refuses an existing output directory.
For another checkout, use the review's public operator recipe and its published
commit mappings; do not silently substitute a changing working tree for a
qualified snapshot or alter retained expected hashes until a test passes.

## Exact corrected core audit program

```python
#!/usr/bin/env python3
"""Finite assignment-54 report identity audit; never imports project producers."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path('/workspace/scratch/c9f3ead4c910')
REPO = ROOT / 'Hammond-B3-Organ'
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=False)
VERSIONS = {
    'original16': ('16d72e1b351e5cdf1730e90645a6ea37144d1be7',
                   '5619bbb018830e071bc2ce45af84984cdd16bfc1', 'w7-installed-source'),
    'allocation459': ('459bfacbda90005d618f12c4513b9c71cb11193d',
                      '3325af558b040759c1b432ec0806a80785af9713', 'w8-allocation-source'),
    'final48': ('48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a',
                '3edea0838b75feb06c19e151ec8539e80646fc03', 'w8-combined-source'),
}
MODULES = sorted(('capture_audio.py', 'capture_common.py', 'capture_corpus.py',
                  'capture_job.py', 'capture_readiness.py', 'capture_study.py',
                  'compare_capture.py', 'make_capture_demo.py',
                  'validate_capture.py', 'verify_capture_report.py'))
JOB_MODULES = sorted(('capture_audio.py', 'capture_common.py', 'capture_corpus.py',
                      'capture_job.py', 'compare_capture.py', 'validate_capture.py'))
STUDY_MODULES = sorted(JOB_MODULES + ['capture_study.py'])
CLAIMS = ('boundary_equivalence', 'synchronization', 'authenticity',
          'specimen_identity', 'calibration', 'permissions', 'independence',
          'preregistration', 'final_holdout_history', 'physical_fidelity')
FIXTURE_PATHS = sorted(('EXPECTED.json', 'README.md', 'study.json',
    'job-pass.json', 'job-inconclusive.json', 'job-fail.json',
    'policy-pass.json', 'policy-inconclusive.json', 'policy-fail.json',
    'corpus/corpus.json', 'corpus/reference.json', 'corpus/quarter.json',
    'corpus/half.json', 'corpus/audio/reference.f32',
    'corpus/audio/quarter.f32', 'corpus/audio/half.f32'))
REMOVED = ['/tool_sources', '/jobs/0/report/tool_sources',
           '/jobs/1/report/tool_sources', '/jobs/2/report/tool_sources']
EXPECTED = {
    'original16': (119423, '6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727'),
    'allocation459': (119423, '71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736'),
    'final48': (119427, 'b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa'),
}
RUNTIME = dict(python_implementation=sys.implementation.name,
               python_version=platform.python_version(), sys_platform=sys.platform,
               machine=platform.machine())
RESULT = {'assignment': 54, 'agent': '/root/cal_w9_a54', 'checks': [],
          'commands': [], 'versions': {}, 'runtime': RUNTIME,
          'removed_paths': REMOVED, 'used_by_public_replay': False}

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode('utf-8')

def identity(payload):
    return dict(size_bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())

def inv(directory):
    return [dict(path=p.relative_to(directory).as_posix(), **identity(p.read_bytes()))
            for p in sorted(directory.rglob('*')) if p.is_file()]

def check(name, condition, detail=None):
    RESULT['checks'].append(dict(name=name, pass_=bool(condition), detail=detail))
    (OUT / 'audit.json').write_bytes(canonical(RESULT))
    if not condition:
        raise AssertionError(name)

def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args],
                          check=True, capture_output=True).stdout

def write_new(path, payload):
    with path.open('xb') as stream:
        stream.write(payload)
    return path

TOOLS = {}
SOURCES = {}
ORIGINAL_SOURCE_INVENTORIES = {}
for label, (commit, tree, archived) in VERSIONS.items():
    assert git('rev-parse', commit + '^{tree}').decode().strip() == tree
    directory = OUT / label / 'tools'
    directory.mkdir(parents=True)
    TOOLS[label] = directory
    rows = []
    for name in MODULES:
        raw = (ROOT / archived / 'tools' / name).read_bytes()
        assert raw == git('show', commit + ':tools/' + name), (label, name)
        write_new(directory / name, raw)
        rows.append(dict(module=name, **identity(raw)))
    SOURCES[label] = rows
    ORIGINAL_SOURCE_INVENTORIES[label] = rows
    RESULT['versions'][label] = dict(commit=commit, tree=tree, sources=rows)
check('01 coherent ten-module frozen source copies match all thirty Git blobs', True)

artifact_path = ROOT / 'w8-combined-source/examples/benchmarks/capture-toolchain-v1/allocation_comparison.json'
artifact_raw = artifact_path.read_bytes()
artifact_id = identity(artifact_raw)
artifact = json.loads(artifact_raw)
assert artifact_id == dict(size_bytes=304390, sha256='791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc')
assert artifact_raw == canonical(artifact)
assert artifact_raw == (ROOT / 'w8-allocation-source/examples/benchmarks/capture-toolchain-v1/allocation_comparison.json').read_bytes()
saved_dir = OUT / 'saved-originals'
saved_dir.mkdir()
SAVED = {}
STUDIES = {}
for label, field in (('original16', 'before'), ('allocation459', 'after')):
    item = artifact['retained_reports'][field]
    payload = canonical(item['value'])
    assert identity(payload) == item['identity']
    assert (len(payload), hashlib.sha256(payload).hexdigest()) == EXPECTED[label]
    assert item['identity'] == artifact[field]['fresh_report']
    assert artifact[field]['original_report'] == artifact['retained_reports']['before']['identity']
    SAVED[label] = write_new(saved_dir / (label + '.json'), payload)
    STUDIES[label] = item['value']
RESULT['retained_artifact'] = artifact_id
check('02 original canonical report values reconstruct both retained byte identities', True,
      {label: identity(path.read_bytes()) for label, path in SAVED.items()})

archive = OUT / 'one unchanged archive'
shutil.copytree(ROOT / 'w8-combined-source/examples/capture-demo', archive)
archive_before = inv(archive)
assert [r['path'] for r in archive_before] == FIXTURE_PATHS
assert sum(r['size_bytes'] for r in archive_before) == 32831
assert archive_before == artifact['before']['fixture'] == artifact['after']['fixture']
for label, (commit, _, archived) in VERSIONS.items():
    assert inv(ROOT / archived / 'examples/capture-demo') == archive_before
    for row in archive_before:
        assert (archive / row['path']).read_bytes() == git('show', commit + ':examples/capture-demo/' + row['path'])
RESULT['archive'] = archive_before
check('03 unchanged sixteen-file archive matches both original inventories and all source snapshots', True)

def changed(left, right):
    return [a['module'] for a, b in zip(SOURCES[left], SOURCES[right]) if a != b]
assert changed('original16', 'allocation459') == ['capture_corpus.py']
assert changed('allocation459', 'final48') == [m for m in MODULES if m != 'compare_capture.py']
check('04 allocation change affects one module and CLI repair affects nine modules', True,
      {'allocation': changed('original16', 'allocation459'),
       'cli': changed('allocation459', 'final48')})

foreign_cwd = OUT / 'foreign working directory λ'
foreign_cwd.mkdir()
BASE_ENV = os.environ.copy()
BASE_ENV.update(PYTHONHASHSEED='0', TZ='UTC', LC_ALL='C.UTF-8')
BASE_ENV.pop('PYTHONPATH', None)
RESULT['environment'] = {'base': {k: BASE_ENV[k] for k in ('PYTHONHASHSEED', 'TZ', 'LC_ALL')},
                         'inherited_environment_values_not_collected': True,
                         'PYTHONPATH_removed': True}
REPORTS = OUT / 'reports'
REPORTS.mkdir()

def execute(label, name, script, args, expected_rc, env=None):
    path = REPORTS / (name + '.stdout')
    err = REPORTS / (name + '.stderr')
    argv = [sys.executable, '-B', '-S', str(TOOLS[label] / script), *map(str, args)]
    process = subprocess.run(argv, cwd=foreign_cwd, env=BASE_ENV if env is None else env,
                             capture_output=True, timeout=30)
    write_new(path, process.stdout)
    write_new(err, process.stderr)
    RESULT['commands'].append(dict(name=name, argv=argv, returncode=process.returncode,
                                  expected_returncode=expected_rc,
                                  stdout=identity(process.stdout), stderr=identity(process.stderr)))
    (OUT / 'audit.json').write_bytes(canonical(RESULT))
    assert process.returncode == expected_rc, (name, process.returncode, process.stderr)
    return process, path

for label in VERSIONS:
    proc, report_path = execute(label, label + '-study', 'capture_study.py',
                               ['--input', archive / 'study.json'], 1)
    assert not proc.stderr
    value = json.loads(proc.stdout)
    assert proc.stdout == canonical(value)
    assert (len(proc.stdout), hashlib.sha256(proc.stdout).hexdigest()) == EXPECTED[label]
    if label in SAVED:
        assert proc.stdout == SAVED[label].read_bytes()
    STUDIES[label] = value
    SAVED.setdefault(label, report_path)
check('05 three fresh study interpreters reproduce the independently fixed full report identities', True,
      {label: identity(canonical(value)) for label, value in STUDIES.items()})

SUMMARIES = []
def replay(label, name, input_path, saved, expected_match, saved_value, fresh_value, env=None):
    proc, path = execute(label, name, 'verify_capture_report.py',
        ['--kind', 'study' if 'study_contract' in saved_value else 'job',
         '--input', input_path, '--report', saved], 0 if expected_match else 1, env)
    assert not proc.stderr
    value = json.loads(proc.stdout)
    assert proc.stdout == canonical(value)
    assert value['status'] == ('match' if expected_match else 'mismatch')
    assert value['exact_report_match'] is expected_match
    assert value['saved_report'] == identity(saved.read_bytes())
    assert value['replayed_report'] == identity(canonical(fresh_value))
    assert value['saved_engineering_status'] == saved_value['status']
    assert value['replayed_engineering_status'] == fresh_value['status']
    assert value['input'] == identity(input_path.read_bytes())
    assert value['verification_scope'] == 'complete_canonical_report_bytes'
    assert value['context'] == dict(same_runtime=True,
        same_tool_sources=saved_value['tool_sources'] == fresh_value['tool_sources'],
        saved_runtime=saved_value['runtime'], replayed_runtime=fresh_value['runtime'],
        saved_tool_sources=saved_value['tool_sources'], replayed_tool_sources=fresh_value['tool_sources'])
    assert value['verifier_runtime'] == RUNTIME
    assert value['verifier_source'] == next(r for r in SOURCES[label] if r['module'] == 'verify_capture_report.py')
    assert all(value[k] == 'not_established' for k in CLAIMS)
    SUMMARIES.append(dict(name=name, value=value))
    return value

for label in VERSIONS:
    replay(label, label + '-own-replay', archive / 'study.json', SAVED[label], True,
           STUDIES[label], STUDIES[label])
check('06 same-source study replays exactly match while retaining engineering failed', True)
for label in ('original16', 'allocation459'):
    replay('final48', 'final48-versus-' + label, archive / 'study.json', SAVED[label], False,
           STUDIES[label], STUDIES['final48'])
check('07 final source replays both original reports as explicit complete-report mismatches', True)

JOB_PATHS = []
for index, (suffix, code) in enumerate((('pass', 0), ('inconclusive', 3), ('fail', 1))):
    proc, report_path = execute('final48', 'final48-job-' + suffix, 'capture_job.py',
                               ['--input', archive / ('job-' + suffix + '.json')], code)
    assert not proc.stderr
    assert proc.stdout == canonical(STUDIES['final48']['jobs'][index]['report'])
    JOB_PATHS.append(report_path)
check('08 three public job commands reproduce full embedded study reports with 0,3,1 exits', True)
for index, suffix in enumerate(('pass', 'inconclusive', 'fail')):
    fresh = STUDIES['final48']['jobs'][index]['report']
    replay('final48', 'final48-own-job-replay-' + suffix, archive / ('job-' + suffix + '.json'),
           JOB_PATHS[index], True, fresh, fresh)
check('09 all three same-source job replays match without changing their engineering verdicts', True)
for index, suffix in enumerate(('pass', 'inconclusive', 'fail')):
    old = STUDIES['allocation459']['jobs'][index]['report']
    old_path = write_new(saved_dir / ('allocation459-job-' + suffix + '.json'), canonical(old))
    replay('final48', 'final48-old-job-replay-' + suffix, archive / ('job-' + suffix + '.json'),
           old_path, False, old, STUDIES['final48']['jobs'][index]['report'])
check('10 three retained allocation-source job reports mismatch final sources without edits', True)

for label, study in STUDIES.items():
    expected = {r['module']: r for r in SOURCES[label]}
    assert study['tool_sources'] == [expected[m] for m in STUDY_MODULES]
    assert study['runtime'] == RUNTIME
    for entry in study['jobs']:
        assert entry['report']['tool_sources'] == [expected[m] for m in JOB_MODULES]
        assert entry['report']['runtime'] == RUNTIME
    imports = {}
    for module in MODULES:
        tree = ast.parse((TOOLS[label] / module).read_text(encoding='utf-8'))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(n.name.split('.')[0] + '.py' for n in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split('.')[0] + '.py')
        imports[module] = names.intersection(MODULES)
    def closure(name):
        found = {name}
        todo = [name]
        while todo:
            for item in imports[todo.pop()] - found:
                found.add(item)
                todo.append(item)
        return sorted(found)
    assert closure('capture_job.py') == JOB_MODULES
    assert closure('capture_study.py') == STUDY_MODULES
    RESULT['versions'][label]['static_project_import_closure'] = {
        'job': closure('capture_job.py'), 'study': closure('capture_study.py'),
        'verifier': closure('verify_capture_report.py')}
check('11 source inventories match actual bytes and literal six/seven producer module closures', True)
check('12 every replay summary binds original input, both reports, contexts and own verifier source', True,
      {'summaries_checked_so_far': len(SUMMARIES), 'runtime': RUNTIME})

for study in STUDIES.values():
    assert study['status'] == 'failed'
    assert study['summary'] == {'jobs': 3, 'pass': 1, 'inconclusive': 1, 'failed': 1,
        'roles': {'fit': 0, 'validation': 3, 'final_test': 0, 'unassigned': 0}}
    assert study['work'] == {'window_samples': 12, 'spectral_terms': 12}
    assert all(study[k] == 'not_established' for k in CLAIMS)
    for index, entry in enumerate(study['jobs']):
        report = entry['report']
        assert report['status'] == ('pass', 'inconclusive', 'failed')[index]
        assert report['evaluation']['evaluation_role'] == 'validation'
        assert all(report[k] == 'not_established' for k in CLAIMS)
check('13 all forty root/embedded claims and three statuses/roles remain explicitly unchanged', True)

def project(study):
    result = copy.deepcopy(study)
    del result['tool_sources']
    for index in range(3):
        del result['jobs'][index]['report']['tool_sources']
    return canonical(result)

projected = {label: project(study) for label, study in STUDIES.items()}
assert len(set(projected.values())) == 1
assert identity(projected['final48']) == {
    'size_bytes': 114760, 'sha256': '760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479'}
assert identity(projected['final48']) == artifact['source_independent_content']['before']
assert REMOVED == artifact['source_independent_content']['removed_paths']
check('14 complete analytical/claim projection is byte-identical across all three sources', True,
      {'identity': identity(projected['final48']), 'only_removed_paths': REMOVED,
       'used_by_public_replay': False})

array_sizes = {}
for label, study in STUDIES.items():
    arrays = [study['tool_sources']] + [entry['report']['tool_sources'] for entry in study['jobs']]
    array_sizes[label] = [len(canonical(a)) for a in arrays]
delta = [b - a for a, b in zip(array_sizes['allocation459'], array_sizes['final48'])]
assert delta == [1, 1, 1, 1]
assert len(canonical(STUDIES['final48'])) - len(canonical(STUDIES['allocation459'])) == sum(delta) == 4
for old, new in zip(SOURCES['allocation459'], SOURCES['final48']):
    if old['module'] in STUDY_MODULES:
        assert len(str(new['size_bytes'])) - len(str(old['size_bytes'])) == (1 if old['module'] == 'capture_common.py' else 0)
check('15 four-byte report growth is exactly four 9625-to-12774 source-size digit changes', True,
      {'canonical_array_bytes': array_sizes, 'per_array_byte_deltas': delta,
       'unchanged_projection_bytes': len(projected['final48'])})

for study in STUDIES.values():
    assert study['input'] == identity((archive / 'study.json').read_bytes())
    for entry in study['jobs']:
        report = entry['report']
        job_bytes = (archive / entry['path']).read_bytes()
        assert identity(job_bytes) == report['inputs']['job']
        assert entry['expected_sha256'] == entry['observed_sha256'] == identity(job_bytes)['sha256']
        assert entry['size_bytes'] == len(job_bytes)
        for kind in ('policy', 'corpus'):
            binding = report['inputs'][kind]
            raw = (archive / binding['path']).read_bytes()
            assert binding['size_bytes'] == len(raw)
            assert binding['observed_sha256'] == binding['expected_sha256'] == identity(raw)['sha256']
        assert report['evaluation']['policy_sha256'] == report['inputs']['policy']['observed_sha256']
        corpus = report['corpus_report']
        assert corpus['index_sha256'] == identity((archive / 'corpus/corpus.json').read_bytes())['sha256']
        for capture in corpus['captures']:
            manifest_path = archive / 'corpus' / capture['manifest_path']
            manifest_sha = identity(manifest_path.read_bytes())['sha256']
            assert capture['expected_manifest_sha256'] == capture['observed_manifest_sha256'] == manifest_sha
            for item in capture['files']:
                raw = (manifest_path.parent / item['path']).read_bytes()
                assert item['expected_sha256'] == item['observed_sha256'] == identity(raw)['sha256']
                assert item['expected_size_bytes'] == item['observed_size_bytes'] == len(raw)
check('16 study/job/policy/corpus/manifest/audio identities bind the unchanged original bytes', True)

relocated = OUT / 'relocated Ω tool package'
shutil.copytree(TOOLS['final48'], relocated / 'tools')
shutil.copytree(archive, relocated / 'archive 標本')
TOOLS['relocated48'] = relocated / 'tools'
SOURCES['relocated48'] = SOURCES['final48']
relocated_archive = relocated / 'archive 標本'
for path in relocated.rglob('*'):
    if path.is_file():
        os.utime(path, (1234567890, 1234567890))
assert inv(relocated_archive) == archive_before
OTHER_ENV = BASE_ENV.copy()
OTHER_ENV.update(PYTHONHASHSEED='314159', TZ='Pacific/Honolulu', LC_ALL='C', SOURCE_DATE_EPOCH='1')
RESULT['environment']['relocated'] = {k: OTHER_ENV[k] for k in ('PYTHONHASHSEED', 'TZ', 'LC_ALL', 'SOURCE_DATE_EPOCH')}
proc, path = execute('relocated48', 'relocated-study', 'capture_study.py',
                    ['--input', relocated_archive / 'study.json'], 1, OTHER_ENV)
assert not proc.stderr and proc.stdout == canonical(STUDIES['final48'])
replay('relocated48', 'relocated-cross-path-replay', relocated_archive / 'study.json',
       SAVED['final48'], True, STUDIES['final48'], STUDIES['final48'], OTHER_ENV)
assert str(OUT).encode() not in proc.stdout and str(ROOT).encode() not in proc.stdout
check('17 Unicode relocation, file timestamps, cwd and selected environment changes preserve exact report', True,
      {'fresh_study_identity': identity(proc.stdout), 'fixture_mtime': 1234567890,
       'replay_uses_original_location_saved_report': True,
       'incidental_output_paths_found': False})

noncanonical = write_new(saved_dir / 'noncanonical-final.json',
                         json.dumps(STUDIES['final48'], separators=(',', ':')).encode())
proc, path = execute('final48', 'noncanonical-report-rejected', 'verify_capture_report.py',
    ['--kind', 'study', '--input', archive / 'study.json', '--report', noncanonical], 1)
assert not proc.stdout and b'canonical' in proc.stderr
check('18 noncanonical copy rejects before emitting a summary and is never normalized in place', True,
      {'stderr': proc.stderr.decode(), 'saved_identity': identity(noncanonical.read_bytes())})

assert inv(archive) == archive_before
assert inv(relocated_archive) == archive_before
assert artifact_path.read_bytes() == artifact_raw
for label, (_, _, archived) in VERSIONS.items():
    for row in ORIGINAL_SOURCE_INVENTORIES[label]:
        name = row['module']
        for directory in (ROOT / archived / 'tools', TOOLS[label]):
            assert dict(module=name, **identity((directory / name).read_bytes())) == row
    assert (len(SAVED[label].read_bytes()), hashlib.sha256(SAVED[label].read_bytes()).hexdigest()) == EXPECTED[label]
assert all((relocated / 'tools' / m).read_bytes() == (TOOLS['final48'] / m).read_bytes() for m in MODULES)
assert not list(OUT.rglob('__pycache__'))
check('19 original reports, source snapshots, both archives and artifact remain unchanged', True)

RESULT['replays'] = SUMMARIES
RESULT['fresh_cli_processes'] = len(RESULT['commands'])
assert len(RESULT['commands']) == 20
assert len(SUMMARIES) == 12
assert all(row['pass_'] for row in RESULT['checks'])
RESULT['outcome'] = 'pass'
RESULT['scope'] = 'Finite source/report identity audit; not calibration, code-memory attestation, OS/toolchain qualification, allocation or general replay-suite execution.'
(OUT / 'audit.json').write_bytes(canonical(RESULT))
print(json.dumps({'outcome': 'pass', 'check_groups': len(RESULT['checks']),
    'fresh_cli_processes': len(RESULT['commands']), 'replay_summaries': len(SUMMARIES),
    'audit_identity': identity((OUT / 'audit.json').read_bytes()), 'output': str(OUT)}, sort_keys=True))

```

## Exact supplementary different-cwd program

```python
#!/usr/bin/env python3
"""Check an actually different cwd using relative public input/report arguments."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/workspace/scratch/c9f3ead4c910')
PREVIOUS = ROOT / 'a54-identity-run2'
OUT = ROOT / 'a54-cwd-check'
OUT.mkdir(exist_ok=False)
CWD = OUT / 'second foreign cwd ν'
CWD.mkdir()
TOOLS = PREVIOUS / 'relocated Ω tool package/tools'
ARCHIVE = PREVIOUS / 'relocated Ω tool package/archive 標本'
SAVED = PREVIOUS / 'reports/final48-study.stdout'
env = os.environ.copy()
env.pop('PYTHONPATH', None)
env.update(PYTHONHASHSEED='314159', TZ='Pacific/Honolulu', LC_ALL='C', SOURCE_DATE_EPOCH='1')
cases = [
    ('study', [sys.executable, '-B', '-S', str(TOOLS / 'capture_study.py'),
               '--input', os.path.relpath(ARCHIVE / 'study.json', CWD)], 1,
               PREVIOUS / 'reports/relocated-study.stdout'),
    ('replay', [sys.executable, '-B', '-S', str(TOOLS / 'verify_capture_report.py'),
               '--kind', 'study', '--input', os.path.relpath(ARCHIVE / 'study.json', CWD),
               '--report', os.path.relpath(SAVED, CWD)], 0,
               PREVIOUS / 'reports/relocated-cross-path-replay.stdout'),
]
tracked = sorted([p for base in (TOOLS, ARCHIVE) for p in base.rglob('*') if p.is_file()] + [SAVED])
before = {str(p): p.read_bytes() for p in tracked}
result = {'assignment': 54, 'check_group': 20, 'fresh_cli_processes': 2, 'cases': [],
          'cwd': str(CWD), 'relative_input_and_report_arguments': True}
for name, argv, code, expected in cases:
    process = subprocess.run(argv, cwd=CWD, env=env, capture_output=True, timeout=30)
    (OUT / (name + '.stdout')).write_bytes(process.stdout)
    (OUT / (name + '.stderr')).write_bytes(process.stderr)
    record = dict(name=name, argv=argv, returncode=process.returncode,
                  expected_returncode=code, stdout_size_bytes=len(process.stdout),
                  stdout_sha256=hashlib.sha256(process.stdout).hexdigest())
    result['cases'].append(record)
    (OUT / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    assert process.returncode == code and not process.stderr
    assert process.stdout == expected.read_bytes()
assert all(path.read_bytes() == before[str(path)] for path in tracked)
result.update(outcome='pass', source_archive_and_saved_report_unchanged=True)
(OUT / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({'outcome': 'pass', 'check_groups': 1, 'fresh_cli_processes': 2,
                  'summary': str(OUT / 'result.json')}, sort_keys=True))

```

## Limits and handoff

The original artifact, both retained report identities, all copied/source Git
blobs and the 16 input files remain unchanged. The four-array projection is
114,760 bytes / `760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479`
for all three source versions and is never passed to public replay. The actual
four-byte full-report increase is fully explained by the source context size
field change. All numerical, metadata, role, status, claim, policy and runtime
values remain in the complete projection.

This is finite local identity evidence. It is not a rerun of the independent
69-method replay suite, root's 106/106 Release gate, installation, hosted CI,
allocation profiling, arbitrary environment/host invariance, hostile filesystem
atomicity, historical authenticity or loaded-memory attestation. Synthetic
reports retain all ten unknown claims and cannot close physical M8 acceptance.

No production repair is requested. Root should review and integrate the two
owned records, link the immutable public source mapping to an observed
publication record, and preserve both original reports and the expected source
mismatches. Future agents must repeat affected exact-source checks when source,
runtime, policy or data changes, keep failed/inconclusive outcomes, and create
new reports rather than rewrite historical evidence. The current acquisition
handoff remains the next source of concrete physical-evidence requirements.

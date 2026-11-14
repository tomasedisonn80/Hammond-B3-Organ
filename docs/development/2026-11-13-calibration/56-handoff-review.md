# Assignment 56 — independent operational and acquisition handoff review

Actual worker: `/root/cal_w10_a56`, logical wave **10**, assignment **56** of the
`2026-11-13-calibration` session. This is one newly dispatched worker and no
sub-worker was created or counted. Work was performed on 2026-11-14 UTC.

## Owned result and acceptance

Owned only this note and [CALIBRATION_HANDOFF_REVIEW.md](../../reviews/CALIBRATION_HANDOFF_REVIEW.md).
Reviewed the two new guides without editing them. **Accept both for their stated
scope; no blocking contradiction or production/test change is required.** Root
owns shared status, task counts, staging, commits and publication. I made no Git,
ledger, production, maintained test, package or shared-document mutation.

The final audit executed **19 project CLI processes**, checked **24 documented
command option sets** against eight real help outputs, and resolved **58 relative
links** (28 runbook / 30 acquisition-plan). The complete private source archive
contains **1,023 files / 40,370,269 bytes**, unchanged before/after. These are finite
review observations, not a new full CTest suite or platform qualification.

## Source and environment

The private source was extracted with `git archive` from published
`d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree
`0140c737de4db28288b118744c2beef57976697f`. The tree was checked with Git; every
extracted regular file was hashed before and after. The parent reported its
fetched remote verification; this worker did not independently perform a network
clone or update a remote ref. Guide 52 exists at that source; guide 53 was frozen
separately from its delivered worktree bytes. Both hashes appear in the retained
result below. Root subsequently reported shared-record checkpoint `eb490af`;
earlier observed task counts are superseded, not flagged as an unresolved defect.

Used CPython 3.12.14 on Linux x86_64. All project child invocations used `-B -S`,
empty `PYTHONPATH`, ASCII terminal encoding, a foreign cwd and Unicode/space source
and output paths. `HAMMOND_*` variables were removed from the child environment.
The record below retains the exact interpreter/version/platform and commands.
The scratch paths describe this execution; neither public guide makes them setup
requirements.

Read AGENTS, the two complete guides, the calibration scope and fresh atlas
consolidation, PLAN and the general atlas review; inspected relevant README,
current status/next-step/handoff/log context, protocol sections, companion guides,
actual CLI entrypoints, constants and CMake package declarations. Truncated
combined readouts of the reviewed guides and plan were reread in narrower calls.
The six prior readers own the full-PDF coverage; no new complete PDF or external
source reading is claimed here. Existing source/data schemas and cross-track
numerical/physical limitations are retained, not requalified by this note.

## Independent audit and observed decisions

The audit was written for this assignment. It does not import earlier workers'
acceptance helpers or count their runs as its own. It uses public CLI subprocesses,
source declarations and independent expected outcomes. It checks the risky guide
decisions: a completed failed job, exact replay preserving that failure, regular
and dangling output preservation, missing parents, incorrect option/flag usage,
strict canonical-byte rejection, honest source-context mismatch, and a complete
published file surviving a real closed stdout pipe. Each final outcome matched.

Installation evidence here is declarative inspection, not execution. The actual
57-file CaptureTools lists include ten modules, eight data, 21 docs, sixteen demo,
one notice and one generated README. Both new guides are outside that package.
OfflineTools has five executable targets, two plotters, a compiled profile and
fifteen fixture/catalog inputs. Assignment 50 separately owns its clean install,
co-installation, relocation and native execution evidence. I ran no CMake build
or install and did not borrow its command count. Physical data, fitting, listening,
platforms, devices and final session completion remain outside this finite scope.

### Initial audit expectation and preserved failure

The first audit ran fifteen project CLI processes and then stopped because my
expected exit for `--check-audio` without `--check-files` was 1. Actual argparse
usage exit 2 is correct and agrees with both guides' usage rule. No source or
guide repair was warranted. The exact original script identity and actual stderr
are retained below. The final run uses a separate new private source/output tree;
its later noncanonical probe explicitly appends one LF to guarantee changed bytes.
The initial partial run is not described as passing or merged into the final
19-process result.

| Retained private evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `audit-initial.py` | 10,436 | `bae80b105a5a094917e52f2e1279634cd3116b8391a777f61f3ba7109267d217` |
| `initial-failure.json` | 839 | `b4ca3496adff3b25d0faf3bdad4269ecad61a8949c057e0776b2ba411ae5f4ac` |
| `audit-final.py` | 10,400 | `5e16cb4c721f39c861c1106464df2d73633e5d1f91f9c22b344f8046d3f22be2` |
| `result.json` | 26,178 | `a4846e0b40dfe8e0d9510c6e326df8782ac8ee1b04513b45296ce9ddbaea7cc2` |

```json
{
  "scope": "audit expectation error, not project or guide failure",
  "case": "audio-needs-file-check",
  "initial_expected_exit": 1,
  "observed_exit": 2,
  "project_cli_processes_before_stop": 15,
  "initial_script_bytes": 10436,
  "initial_script_sha256": "bae80b105a5a094917e52f2e1279634cd3116b8391a777f61f3ba7109267d217",
  "actual_stderr_bytes": 139,
  "actual_stderr_sha256": "4020ec634f7d013f8f5e8e51a6579270b0abc9002647ab51fbfc90cd3dc2bdb6",
  "actual_stderr": "usage: capture_corpus.py [-h] --input INPUT [--check-files] [--check-audio]\ncapture_corpus.py: error: --check-audio requires --check-files\n",
  "correction": "This flag dependency is argparse usage and the guides already classify usage as exit 2. Change only the audit expectation. Final noncanonical probe explicitly appends one LF to guarantee changed bytes."
}
```

## Complete final execution record

Executed from the repository root:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a56-handoff-review/audit-final.py
```

The process returned 0 with all expected outcomes. The following is the complete
retained JSON result, including every child command, exact output sizes/digests,
links, command options, limits and inventory observations. Source reports,
diagnostics and the altered-source copy remain private reproduction intermediates;
no generated report is promoted to a physical measurement.

```json
{
  "scope": "independent guide recovery and contract audit; not full-suite or platform qualification",
  "source_commit": "d7f6100010eb4cdd028ec93000cd9e893ac6d190",
  "source_tree": "0140c737de4db28288b118744c2beef57976697f",
  "runtime": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]",
  "platform": "Linux-6.18.57-x86_64-with-glibc2.41",
  "guides": {
    "docs/CALIBRATION_RUNBOOK.md": {
      "bytes": 20527,
      "sha256": "ae7ceda3c211c571b03038d9aa6fe1d3e454faa49d23500e0e0e46407b6846af"
    },
    "docs/CALIBRATION_NEXT_ACQUISITION.md": {
      "bytes": 28837,
      "sha256": "87e4ebb2c8edc86ada894fc1c4b968b4a1c00597d61e1b2633ad3210ccac814b"
    }
  },
  "archive_files": 1023,
  "archive_bytes": 40370269,
  "archive_unchanged": true,
  "local_links": [
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "STATUS.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CALIBRATION_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "PLAN.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_AUDIO.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_JOB.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_POLICY.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_STUDY.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_REPLAY.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_DEMO.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "reviews/CALIBRATION_CLI_PIPELINE.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_TOOLS_INSTALL.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "OFFLINE_INSTALL.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "PEDAL_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "STANDALONE_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "VST3_BUILD.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "reviews/CALIBRATION_CLEAN_SETUP.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "reviews/CALIBRATION_RAW_GIT_IDENTITY.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_JOB_CONTRACT.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_POLICY.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CAPTURE_PROTOCOL.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "../examples/benchmarks/capture-toolchain-v1/README.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "reviews/CALIBRATION_METADATA_ALLOCATION.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "reviews/CALIBRATION_ALLOCATION_INTEGRATION.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "../AGENTS.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "development/2026-11-13-calibration/assignments.json"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "CALIBRATION_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "NEXT_STEPS.md"
    ],
    [
      "docs/CALIBRATION_RUNBOOK.md",
      "development/2026-11-13-calibration/52-operations.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "PLAN.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_PROTOCOL.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CALIBRATION_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "STATUS.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "NEXT_STEPS.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "development/2026-11-13-calibration/53-next-acquisition.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture-planned-example.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/corpus-planned-example.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_FORMAT.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture.schema.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_AUDIO.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture-corpus.schema.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_CORPUS.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture-policy.schema.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture-job.schema.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture-study.schema.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../data/capture-policy-synthetic-example.json"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "SCANNER_AC_PARITY.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "SCANNER_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "ROTARY_SCOPE.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CALIBRATION_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_JOB.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_STUDY.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_REPLAY.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "CAPTURE_DEMO.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "NEXT_STEPS.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "STANDALONE_HANDOFF.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../AGENTS.md"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "../Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
    ],
    [
      "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "research/CALIBRATION_ATLAS_REVIEW.md"
    ]
  ],
  "guide_commands_option_checked": [
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "validate_capture.py",
      "options": [
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_readiness.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_corpus.py",
      "options": [
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_corpus.py",
      "options": [
        "--check-audio",
        "--check-files",
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_audio.py",
      "options": [
        "--channel-count",
        "--input",
        "--raw-format",
        "--sample-rate-hz"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_job.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_job.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_job.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_study.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "verify_capture_report.py",
      "options": [
        "--input",
        "--kind",
        "--output",
        "--report"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "verify_capture_report.py",
      "options": [
        "--input",
        "--kind",
        "--output",
        "--report"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "verify_capture_report.py",
      "options": [
        "--input",
        "--kind",
        "--output",
        "--report"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "verify_capture_report.py",
      "options": [
        "--input",
        "--kind",
        "--output",
        "--report"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "make_capture_demo.py",
      "options": [
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "capture_study.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_RUNBOOK.md",
      "module": "verify_capture_report.py",
      "options": [
        "--input",
        "--kind",
        "--output",
        "--report"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "validate_capture.py",
      "options": [
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "capture_readiness.py",
      "options": [
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "capture_audio.py",
      "options": [
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "capture_corpus.py",
      "options": [
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "capture_corpus.py",
      "options": [
        "--check-audio",
        "--check-files",
        "--input"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "capture_job.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "capture_study.py",
      "options": [
        "--input",
        "--output"
      ]
    },
    {
      "document": "docs/CALIBRATION_NEXT_ACQUISITION.md",
      "module": "verify_capture_report.py",
      "options": [
        "--input",
        "--kind",
        "--output",
        "--report"
      ]
    }
  ],
  "capture_inventory": {
    "modules": 10,
    "data": 8,
    "documents": 21,
    "demo": 16
  },
  "capture_files_total": 57,
  "offline_fixture_counts": {
    "_hammond_fixture_files": 6,
    "_hammond_console_fixture_files": 4,
    "_hammond_pedal_fixture_files": 5
  },
  "offline_files_total": 23,
  "limits": {
    "corpus_captures": 512,
    "job_captures": 64,
    "job_artifacts": 256,
    "study_jobs": 8,
    "channels": 16,
    "manifest_artifacts": 32,
    "artifact_bytes": 268435456,
    "manifest_bytes": 536870912
  },
  "project_cli_processes": 19,
  "commands": [
    {
      "case": "help-validate_capture.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/validate_capture.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 474,
      "stdout_sha256": "5856bc5180173341d03f3795380807d987e2b7730617a24b71ea87757c2816e7",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-capture_audio.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_audio.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 888,
      "stdout_sha256": "3ec485807284e5d2e0657319697f70b3ed95997705a8e9d3d56b329faad87ece",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-capture_corpus.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_corpus.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 386,
      "stdout_sha256": "0f02e1cc5fb9e034534fc216edd1ea92833f48d74ac2d417bd025c4624ee7062",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-capture_job.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_job.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 306,
      "stdout_sha256": "93521c4fa541afebe7e4555776b2ba058523ed5a582b8e2463923ddc77538346",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-capture_readiness.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_readiness.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 297,
      "stdout_sha256": "5440611afda56ede0045a0e30ca0bc5412905e3335f7ea77842386201afcfb71",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-capture_study.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_study.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 303,
      "stdout_sha256": "5981d8971585a8a2f9b19ee9c7f8a624b21f6803596213ede7b2c4ad2ad93c2a",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-make_capture_demo.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/make_capture_demo.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 256,
      "stdout_sha256": "e3a8555a0e978bcded1499a7a7817fb3649f48dc6143b72d93d14d6ec918f44d",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "help-verify_capture_report.py",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/verify_capture_report.py",
        "--help"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 496,
      "stdout_sha256": "61e9e3d08008d40b70f7dd97eae9085a9fd19f21db51046a205fe4ca152ce02d",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "failed-job",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_job.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/failed.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 32660,
      "stdout_sha256": "ba1e39fc5f5410491f7826346c7259dfcf8b603dffbc0a260a9886ed66252321",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "failed-replay",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/verify_capture_report.py",
        "--kind",
        "job",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--report",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/failed.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/failed-replay.json"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 3920,
      "stdout_sha256": "765e10522a39c01ecb731c7f5439f1f28108fad6461d2e7fe50a9bac032f5056",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "existing-report",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_job.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/failed.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 279,
      "stderr_sha256": "ae92c482b5e6b4bff87e3d2e699784d06425eb4f100207b993392b2ad8fb1298",
      "closed_stdout": false
    },
    {
      "case": "dangling-report",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_job.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/dangling.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 281,
      "stderr_sha256": "79274d9242b2bbad688c4647fd73c921391a01e6dc249a7a01acad44fa3d3e20",
      "closed_stdout": false
    },
    {
      "case": "missing-parent",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_job.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/absent-parent/report.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 203,
      "stderr_sha256": "729a6c98d245f34c54d07056818cf79351027207df42fa2b08f4bffbb13845b4",
      "closed_stdout": false
    },
    {
      "case": "corpus-no-output-option",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_corpus.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/corpus/corpus.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/unsupported-output.json"
      ],
      "expected_exit": 2,
      "exit": 2,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 245,
      "stderr_sha256": "1e42f923cb3ed734c2f04fc19151f4d39ff554bf7c438a958408b93042457873",
      "closed_stdout": false
    },
    {
      "case": "audio-needs-file-check",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_corpus.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/corpus/corpus.json",
        "--check-audio"
      ],
      "expected_exit": 2,
      "exit": 2,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 139,
      "stderr_sha256": "4020ec634f7d013f8f5e8e51a6579270b0abc9002647ab51fbfc90cd3dc2bdb6",
      "closed_stdout": false
    },
    {
      "case": "noncanonical-replay",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/verify_capture_report.py",
        "--kind",
        "job",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--report",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/rewritten.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/noncanonical-replay.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 72,
      "stderr_sha256": "d2bbdf7561f72d4e628043f3ab5e8524fd35eb9b42f73d570b25c15092c44fe8",
      "closed_stdout": false
    },
    {
      "case": "source-context-mismatch",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/comment-only source/tools/verify_capture_report.py",
        "--kind",
        "job",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-fail.json",
        "--report",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/failed.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/changed-source.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 3925,
      "stdout_sha256": "6e0f66841cd78d6bd8c6849d57667f15b0ecd98a354a5cdcfa0041845bda34e8",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    },
    {
      "case": "closed-stdout-published-file",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/capture_job.py",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-pass.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/published-before-pipe-error.json"
      ],
      "expected_exit": 1,
      "exit": 1,
      "stdout_bytes": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_bytes": 34,
      "stderr_sha256": "f2e949a6e1d7572f26cbd8eb17b8f3d897b456d1c6b5bc473c25f434137320bc",
      "closed_stdout": true
    },
    {
      "case": "pipe-file-replay",
      "command": [
        "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
        "-B",
        "-S",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/tools/verify_capture_report.py",
        "--kind",
        "job",
        "--input",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/source café 東京/examples/capture-demo/job-pass.json",
        "--report",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/published-before-pipe-error.json",
        "--output",
        "/workspace/scratch/c9f3ead4c910/a56-handoff-review/final/reports café 東京/pipe-file-replay.json"
      ],
      "expected_exit": 0,
      "exit": 0,
      "stdout_bytes": 3916,
      "stdout_sha256": "709f2d4f396c5c44c83165f18b61873f9b84b3a48ae2deb36f94401570c4b3cf",
      "stderr_bytes": 0,
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "closed_stdout": false
    }
  ],
  "expected_outcomes_passed": true,
  "native_build_or_install_executed": false,
  "hardware_or_platform_claims": "not_established"
}
```

## Exact executable audit

This is the final script byte for byte. Its fixed paths identify this run and
should be changed to new scratch destinations when independently reproducing it;
existing evidence directories are deliberately not deleted or reused.

```python
from pathlib import Path
import ast, hashlib, io, json, os, platform, re, shutil, subprocess, sys, tarfile
REPO=Path('/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ')
BASE=Path('/workspace/scratch/c9f3ead4c910/a56-handoff-review/final')
HEAD='d7f6100010eb4cdd028ec93000cd9e893ac6d190'
TREE='0140c737de4db28288b118744c2beef57976697f'
SRC=BASE/'source café 東京'; OUT=BASE/'reports café 東京'; CWD=BASE/'foreign cwd'
assert not SRC.exists(); SRC.mkdir(); OUT.mkdir(); CWD.mkdir()
archive=subprocess.check_output(['git','archive',HEAD],cwd=REPO)
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(SRC,filter='data')
assert subprocess.check_output(['git','rev-parse',HEAD+'^{tree}'],cwd=REPO,text=True).strip()==TREE
sha=lambda b:hashlib.sha256(b).hexdigest()
def inventory(p):return {str(f.relative_to(p)):{'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(p.rglob('*')) if f.is_file()}
before=inventory(SRC)
DOCS=['docs/CALIBRATION_RUNBOOK.md','docs/CALIBRATION_NEXT_ACQUISITION.md']
expected=['ae7ceda3c211c571b03038d9aa6fe1d3e454faa49d23500e0e0e46407b6846af','87e4ebb2c8edc86ada894fc1c4b968b4a1c00597d61e1b2633ad3210ccac814b']
docs={}
for n,h in zip(DOCS,expected):
 b=(REPO/n).read_bytes();assert sha(b)==h;docs[n]={'bytes':len(b),'sha256':h};(BASE/Path(n).name).write_bytes(b)
links=[]
for n in DOCS:
 for dest in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(BASE/Path(n).name).read_text()):
  if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:',dest) or dest.startswith('#'):continue
  dest=dest.split('#')[0];assert (REPO/Path(n).parent/dest).resolve().exists(),(n,dest);links.append([n,dest])
ENV={k:v for k,v in os.environ.items() if not k.startswith('HAMMOND_')}
ENV.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='',PYTHONIOENCODING='ascii:strict')
commands=[]
def run(label,module,args,expected,source=SRC,closed=False):
 cmd=[sys.executable,'-B','-S',str(source/'tools'/module),*map(str,args)]
 if closed:
  r,w=os.pipe();os.close(r)
  try:p=subprocess.Popen(cmd,cwd=CWD,env=ENV,stdout=w,stderr=subprocess.PIPE)
  finally:os.close(w)
  _,err=p.communicate(timeout=30);stdout=b'';rc=p.returncode
 else:
  p=subprocess.run(cmd,cwd=CWD,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);stdout=p.stdout;err=p.stderr;rc=p.returncode
 (OUT/(label+'.stdout')).write_bytes(stdout);(OUT/(label+'.stderr')).write_bytes(err)
 commands.append({'case':label,'command':cmd,'expected_exit':expected,'exit':rc,'stdout_bytes':len(stdout),'stdout_sha256':sha(stdout),'stderr_bytes':len(err),'stderr_sha256':sha(err),'closed_stdout':closed})
 assert rc==expected,(label,rc,expected,err.decode(errors='replace'))
 assert b'Traceback' not in err and b'Exception ignored in:' not in err,label
 return stdout,err
modules=['validate_capture.py','capture_audio.py','capture_corpus.py','capture_job.py','capture_readiness.py','capture_study.py','make_capture_demo.py','verify_capture_report.py']
helps={}
for m in modules:
 out,err=run('help-'+m,m,['--help'],0);assert not err;helps[m]=set(re.findall(rb'--[a-z][a-z-]*',out))
option_checks=[]
for n in DOCS:
 s=(BASE/Path(n).name).read_text()
 for m in re.finditer(r'python3(?: -B)?\s+(?:"\$hammond_capture/)?tools/([a-z_]+\.py)"?([^`\n]*)',s):
  name=m.group(1);opts=set(re.findall(r'--[a-z][a-z-]*',m.group(2)))
  assert name in helps,(n,name)
  assert all(x.encode() in helps[name] for x in opts),(n,name,opts,helps[name])
  option_checks.append({'document':n,'module':name,'options':sorted(opts)})
# Installation inventory is derived from the declarative build input, not a producer's report.
cm=(SRC/'cmake/InstallCaptureTools.cmake').read_text()
components={}
for key in ['modules','data','documents','demo']:
 section=re.search(r'set\(_hammond_capture_'+key+r'\s+(.*?)\)',cm,re.S).group(1)
 entries=section.split();assert all((SRC/p).is_file() for p in entries);components[key]=entries
assert {k:len(v) for k,v in components.items()}=={'modules':10,'data':8,'documents':21,'demo':16}
assert sum(map(len,components.values()))+2==57
assert all(Path(n).name not in '\n'.join(components['documents']) for n in DOCS)
assert 'COMPONENT CaptureTools EXCLUDE_FROM_ALL' in cm
assert 'IS_SYMLINK "${_hammond_capture_leaf}"' in cm and 'no automatic cleanup is performed' in cm
assert 'CMAKE_INSTALL_MODE' in cm and 'STREQUAL "COPY"' in cm
native=(SRC/'cmake/InstallHammondTools.cmake').read_text()
fixtures={k:re.findall(r'"\$\{PROJECT_SOURCE_DIR\}/([^"]+)"',re.search(r'set\('+k+r'\s+(.*?)\)',native,re.S).group(1)) for k in ['_hammond_fixture_files','_hammond_console_fixture_files','_hammond_pedal_fixture_files']}
assert sum(map(len,fixtures.values()))==15 and all((SRC/p).is_file() for ps in fixtures.values() for p in ps)
assert 5+2+1+sum(map(len,fixtures.values()))==23
cml=(SRC/'CMakeLists.txt').read_text();assert 'cmake_minimum_required(VERSION 3.21)' in cml and 'LANGUAGES CXX' in cml and 'cxx_std_20' in cml and 'find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)' in cml
sys.path.insert(0,str(SRC/'tools'))
import capture_corpus,capture_job,capture_study,capture_audio,validate_capture
limits={'corpus_captures':capture_corpus.MAX_CAPTURES,'job_captures':capture_job.MAX_CAPTURES,'job_artifacts':capture_job.MAX_ARTIFACT_REFERENCES,'study_jobs':capture_study.MAX_JOBS,'channels':capture_audio.MAX_CHANNELS,'manifest_artifacts':validate_capture.MAX_FILES,'artifact_bytes':validate_capture.MAX_FILE_BYTES,'manifest_bytes':validate_capture.MAX_TOTAL_FILE_BYTES}
assert limits==dict(corpus_captures=512,job_captures=64,job_artifacts=256,study_jobs=8,channels=16,manifest_artifacts=32,artifact_bytes=256*1024*1024,manifest_bytes=512*1024*1024)
assert capture_corpus.PURPOSE_ROLES=={'fit':'fit','validation':'held_out','final':'held_out','unassigned':'unassigned'}
assert {'flac_pcm16','flac_pcm24'}<=capture_corpus.FORMATS and not ({'flac_pcm16','flac_pcm24'}&capture_corpus.AUDIO_FORMATS)
job=SRC/'examples/capture-demo/job-fail.json'; saved=OUT/'failed.json'
out,err=run('failed-job','capture_job.py',['--input',job,'--output',saved],1)
assert not err and out==saved.read_bytes() and json.loads(out)['status']=='failed'
summary=OUT/'failed-replay.json'
out,err=run('failed-replay','verify_capture_report.py',['--kind','job','--input',job,'--report',saved,'--output',summary],0)
r=json.loads(out);assert not err and out==summary.read_bytes() and r['status']=='match' and r['saved_engineering_status']==r['replayed_engineering_status']=='failed'
assert r['context']['same_runtime'] and r['context']['same_tool_sources']
original=saved.read_bytes()
out,err=run('existing-report','capture_job.py',['--input',job,'--output',saved],1)
assert not out and err and saved.read_bytes()==original
link=OUT/'dangling.json';link.symlink_to('never-created.json');stat_before=link.lstat();target_before=os.readlink(link)
out,err=run('dangling-report','capture_job.py',['--input',job,'--output',link],1)
assert not out and err and link.is_symlink() and link.lstat()==stat_before and os.readlink(link)==target_before and not (OUT/'never-created.json').exists()
missing=OUT/'absent-parent'/'report.json'
out,err=run('missing-parent','capture_job.py',['--input',job,'--output',missing],1)
assert not out and err and not missing.parent.exists()
corpus=SRC/'examples/capture-demo/corpus/corpus.json';unsupported=OUT/'unsupported-output.json'
out,err=run('corpus-no-output-option','capture_corpus.py',['--input',corpus,'--output',unsupported],2)
assert not out and err and not unsupported.exists()
out,err=run('audio-needs-file-check','capture_corpus.py',['--input',corpus,'--check-audio'],2)
assert not out and err
pretty=OUT/'rewritten.json';pretty.write_bytes(original+b'\n');assert pretty.read_bytes()!=original
noncanon=OUT/'noncanonical-replay.json'
out,err=run('noncanonical-replay','verify_capture_report.py',['--kind','job','--input',job,'--report',pretty,'--output',noncanon],1)
assert not out and err and not noncanon.exists() and saved.read_bytes()==original
variant=BASE/'comment-only source';(variant/'tools').mkdir(parents=True)
for p in components['modules']:shutil.copyfile(SRC/p,variant/p)
common=variant/'tools/capture_common.py';common.write_bytes(common.read_bytes()+b'\n# Independent handoff source-context probe.\n')
mismatch=OUT/'changed-source.json'
out,err=run('source-context-mismatch','verify_capture_report.py',['--kind','job','--input',job,'--report',saved,'--output',mismatch],1,source=variant)
r=json.loads(out);assert not err and out==mismatch.read_bytes() and r['status']=='mismatch' and r['context']['same_runtime'] and not r['context']['same_tool_sources'] and r['saved_engineering_status']==r['replayed_engineering_status']=='failed'
passjob=SRC/'examples/capture-demo/job-pass.json'; pipefile=OUT/'published-before-pipe-error.json'
out,err=run('closed-stdout-published-file','capture_job.py',['--input',passjob,'--output',pipefile],1,closed=True)
assert err and pipefile.is_file() and json.loads(pipefile.read_bytes())['status']=='pass'
pipesummary=OUT/'pipe-file-replay.json'
out,err=run('pipe-file-replay','verify_capture_report.py',['--kind','job','--input',passjob,'--report',pipefile,'--output',pipesummary],0)
r=json.loads(out);assert not err and r['status']=='match' and r['saved_engineering_status']==r['replayed_engineering_status']=='pass'
assert before==inventory(SRC)
assert len(commands)==19
result={'scope':'independent guide recovery and contract audit; not full-suite or platform qualification','source_commit':HEAD,'source_tree':TREE,'runtime':sys.version,'platform':platform.platform(),'guides':docs,'archive_files':len(before),'archive_bytes':sum(x['bytes'] for x in before.values()),'archive_unchanged':True,'local_links':links,'guide_commands_option_checked':option_checks,'capture_inventory':{k:len(v) for k,v in components.items()},'capture_files_total':57,'offline_fixture_counts':{k:len(v) for k,v in fixtures.items()},'offline_files_total':23,'limits':limits,'project_cli_processes':len(commands),'commands':commands,'expected_outcomes_passed':True,'native_build_or_install_executed':False,'hardware_or_platform_claims':'not_established'}
(BASE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:result[k] for k in ['source_commit','archive_files','archive_bytes','archive_unchanged','project_cli_processes','expected_outcomes_passed']}))
print('local links',len(links),'documented command option checks',len(option_checks))
```

## Integration handoff

The review requires no guide correction. Root should retain the current runbook
and acquisition links, record this actual acceptance, keep the 103/106 historical
source scopes separate, and incorporate assignment 55's observed hosted outcome
when complete. Continue to the remaining actual final-wave reviews and strict
session accounting; this assignment does not claim those are already complete.
The next physical artifact and its A1–A6 dependencies remain in the acquisition
guide. The user's standing commit/push/documentation rule remains in AGENTS and
the guides, with observed concurrent history preserved and no force publication.

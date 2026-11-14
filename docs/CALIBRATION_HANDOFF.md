# Capture and calibration toolchain handoff

This is the operational entry point for the independent
[M0/M8 calibration-readiness scope](CALIBRATION_SCOPE.md). Follow the
[current session](development/2026-11-13-calibration/README.md), its actual
assignment manifest, [status](STATUS.md) and [next steps](NEXT_STEPS.md).
The complete [M0–M9 plan](PLAN.md) remains the project authority. Scanner,
rotary and native standalone development retain separate ownership.

## Setup and source identity

Use Python 3.10 or newer. These tools use the standard library, require no
package installation, and perform no network requests. Run the following from
the repository root; an absolute tool path also works from another directory.
Keep input archives quiescent while a command reads them.

```sh
python3 --version
git status --short
git rev-parse HEAD
git rev-parse HEAD^{tree}
python3 tools/check_calibration_session.py --repo . --json
```

Inspect the current remote head before publishing. A report about an earlier
commit does not qualify changed code or an uncommitted checkout. The retained
[starting baseline](reviews/CALIBRATION_BASELINE.md) and
[foundation integration](reviews/CALIBRATION_WAVE2_INTEGRATION.md) identify
their own tested source and toolchain. Later independent acceptance records
name their exact implementation bytes; root records coherent checkpoints.

## Available commands

Validate the supplied acquisition plan and its companion corpus:

```sh
python3 tools/validate_capture.py --input data/capture-planned-example.json
python3 tools/capture_corpus.py --input data/corpus-planned-example.json
```

The second command is expected to exit **3** with an inconclusive report. The
record is a plan with no acquired audio and no assigned analysis purpose.
Do not change unknown metadata or exit semantics merely to obtain a zero exit.

Inspect actual audio or a bounded window:

```sh
python3 tools/capture_audio.py --input /path/to/capture.wav
python3 tools/capture_audio.py --input /path/to/capture.wav --start-frame 0 --frame-count 1024
python3 tools/capture_audio.py --input /path/to/capture.f32 --raw-format raw_float32_le --sample-rate-hz 48000 --channel-count 2
```

The last command's rate and channel count are caller declarations for headerless
float32 bytes. They do not measure a physical clock or establish a channel's
signal boundary. WAV metadata must agree with its actual header. A requested
window still validates the complete stream. See [audio usage](CAPTURE_AUDIO.md)
for supported formats, exact hashes, limits and typed errors.

Audit a prepared corpus and its complete artifact set:

```sh
python3 tools/capture_corpus.py --input /path/to/corpus.json --check-files
python3 tools/capture_corpus.py --input /path/to/corpus.json --check-files --check-audio
```

The [corpus guide](CAPTURE_CORPUS.md) explains the fixed relative-path roots,
whole-group split graph, raw/derived metadata and exits. A clean structural
audit alone does not assert that artifact bytes or audio were read. Support
files are byte checked but never decoded. Every omitted derivative remains
visible when audio coverage is requested.

Array comparisons and fixed policy evaluation are available through the Python
APIs described in [comparison usage](CAPTURE_COMPARISON.md) and
[policy usage](CAPTURE_POLICY.md). Policy preflight needs no invented comparison:
`parse_policy` admits the exact policy bytes before audio work. The
[file-job contract](CAPTURE_JOB_CONTRACT.md) is independently reviewed and its
implementation passes 81 independent methods. Prepare an archive using the
[file-job guide](CAPTURE_JOB.md), then run:

```sh
python3 tools/capture_job.py --input /path/to/job.json
python3 tools/capture_job.py --input /path/to/job.json --output /path/to/new-report.json
```

The job binds original metadata and policy bytes, audits the entire corpus,
compares the declared windows without transformation and rechecks every admitted
input and the six observed tool sources. Reports retain pass, failed and
inconclusive results; numerical failure is a completed report with exit 1.
Malformed input is rejected with no report. An existing output is preserved.
No gain, delay, resampling or channel fitting is silently applied.

Inspect declaration gaps in one unchanged v1 manifest:

```sh
python3 tools/capture_readiness.py --input data/capture-planned-example.json
python3 tools/capture_readiness.py --input /path/to/capture.json --output /path/to/new-readiness.json
```

The [readiness guide](CAPTURE_READINESS.md) defines 21 fixed checks plus three
per channel. The supplied plan intentionally returns `planned` and exit 3,
with 20 missing declarations. This command reads metadata only. Even
`declarations_complete` establishes no acquisition, calibrated scale, rights or
physical fidelity. Unknown reasons and raw-only calibration context are retained.

Run the retained synthetic demonstration and its complete study:

```sh
python3 tools/capture_job.py --input examples/capture-demo/job-pass.json
python3 tools/capture_job.py --input examples/capture-demo/job-inconclusive.json
python3 tools/capture_job.py --input examples/capture-demo/job-fail.json
python3 tools/capture_study.py --input examples/capture-demo/study.json
```

The expected exits are **0, 3, 1, 1**. The failed study retains one result of
each kind; failure is deliberate demonstration data. The [demo guide](CAPTURE_DEMO.md)
defines all sixteen original files and literal expectations. To regenerate,
use `python3 tools/make_capture_demo.py --output /existing/parent/new-demo`:
the destination must be new, and its parent must exist. Generation executes no
analysis. `EXPECTED.json` is an oracle, not a saved execution report.

The [study guide](CAPTURE_STUDY.md) binds up to eight original job files to one
corpus identity, preflights cumulative work and retains every complete result.
Its shared snapshot covers earlier inputs and sources through final return.
The study has 61 independent acceptance methods and the demo has 43. Original
archives and freshly executed report bytes are the inputs for subsequent replay.

Retain and reproduce a complete report with fresh output paths:

```sh
python3 tools/capture_study.py --input examples/capture-demo/study.json --output /existing/new-study-report.json
python3 tools/verify_capture_report.py --kind study --input examples/capture-demo/study.json --report /existing/new-study-report.json --output /existing/new-replay-summary.json
```

Run these separately: their expected exits are **1 and 0** under the same coherent
sources/runtime. A matching replay preserves the study's failed engineering
status. The [replay guide](CAPTURE_REPLAY.md) defines strict original canonical
report admission, actual re-execution, complete byte comparison and the explicit
preflight race boundary. Independent acceptance passes 69 methods. A replay
match establishes no historical authenticity or physical result; source/runtime
differences remain visible context and may produce mismatch.

Install the complete source-only package with CMake 3.21 or newer and a C++
compiler available for ordinary repository configuration:

```sh
cmake -S . -B build-capture -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --install build-capture --config Release --component CaptureTools --prefix /existing/new-prefix
```

No native target build is needed for this component. Its 57 files live under
`<prefix>/<CMAKE_INSTALL_DATADIR>/hammond-b3-organ/capture-tools`; the default
data directory is `share`. Run that package's README commands or absolute tool
paths after moving the complete package. Its runtime requires Python and the
standard library. The [install guide](CAPTURE_TOOLS_INSTALL.md) defines the exact
inventory, existing-destination rejection and disclosed partial-copy boundary.
Independent installation acceptance passes 16 methods, including execution after
private source/build deletion; the old 23-file OfflineTools regression also passes.

## Operational guide

The [complete runbook](CALIBRATION_RUNBOOK.md) gives verified source and installed
commands, expected exits, fresh-output handling, complete replay interpretation,
partial failures and continuation rules. Assignment 52 executed fifteen source
commands and four exact replays; assignment 50 separately owns the clean
co-installation/relocation evidence.

## Current integration and next work

The latest verified published code checkpoint is
`d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree
`0140c737de4db28288b118744c2beef57976697f`. Root fetched main and verified exact
tree equality with local `2671fa5`, plus reachable tested-source ancestors
`d377fab7a840dc6d7a499fdf576d0dd8bb5dd4c1` (allocation) and
`5e19022c8696023bb1aa841ebea2eaeec0d719a3` (full 106-suite source). The guarded
non-force publication preserves concurrent `7ec79fb` and its completed standalone
history. It contains 52 accepted records; later documentary acceptance does not
retroactively change that snapshot. Its production, tests, build, models and data
match the full tested source. [All ten hosted jobs](reviews/CALIBRATION_FINAL_HOSTED.md)
now succeed at that exact public commit; their complete method and capability
observations remain separate from the local gate.

The minimal metadata allocation change, independent graph qualification,
process-level stream repair and evidence-boundary review are accepted. Their
[15-suite allocation gate](reviews/CALIBRATION_ALLOCATION_INTEGRATION.md)
is separate from the later [106-suite combined gate](reviews/CALIBRATION_WAVE8_INTEGRATION.md).
The current manifest has all **60 accepted workers in ten complete waves**.
The [strict completion output](development/2026-11-13-calibration/completion-check.json)
and [final integration record](reviews/CALIBRATION_FINAL_INTEGRATION.md) retain
actual closure and the complete record source separately from the qualified code. The [acquisition plan](CALIBRATION_NEXT_ACQUISITION.md)
defines the next actual inputs and A1–A6 deliverables. The
[report-identity review](reviews/CALIBRATION_REPORT_IDENTITY_AUDIT.md) verifies
original/final full reports and preserves explicit old-source mismatch.

Historically, the reviewed first 34 assignments were published at
`955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`, verified after fetching main.
The earlier [wave-4 report](reviews/CALIBRATION_WAVE4_INTEGRATION.md) records 11/11 focused
and 96/96 full SDK-free Release suites from separate frozen snapshots. The
later job implementation shares the corpus audit core without changing its
public API; both existing corpus suites still pass. The
[combined wave-5 source](reviews/CALIBRATION_WAVE5_INTEGRATION.md) passes 99/99
SDK-free Release suites, preserving the standalone advance from `0085e33`.
The later [study/demo source](reviews/CALIBRATION_STUDY_DEMO_INTEGRATION.md)
passes its separate 16/16 focused gate. Both tested trees are retained as
distinct GitHub commits, with the exact mapping in their reports.

Readiness, numerical and schema acceptance are complete. The
[hosted portability follow-up](reviews/CALIBRATION_HOSTED_PORTABILITY.md) records
the observed Release failures, the local CLI/fixture repairs and the outstanding
hosted recheck. The [later completed matrix](reviews/CALIBRATION_HOSTED_RECHECK.md)
resolves those specific earlier failures at `955fc4c`, while retaining a new
Windows demo-fixture spelling failure. Its isolated preservation-test repair
passed locally and then all 43 methods passed on actual Windows at `3b0979b`.
The [subsequent hosted review](reviews/CALIBRATION_HOSTED_PACKAGE_RECHECK.md)
retains a separate installation-fixture newline failure and the later local
byte-copy repair. The final d7 Windows run passes 106/106 suites, including
that exact marker and all nine real-pipe methods. Replay and the 57-file package
are independently accepted. Their [combined source](reviews/CALIBRATION_INSTALL_REPLAY_INTEGRATION.md)
passes 103/103 unfiltered local Release suites; the exact source mapping and logs
are retained separately from later documentation. Resource profiling, the
220-case composition review and the accounting audit complete seven waves and
42 accepted assignments at that publication. All sixty actual assignments are now accepted
in ten complete waves. Hosted, clean-setup, compatibility, operations/acquisition,
report-identity, runtime, accounting and final reviews are retained with their
original source/count scopes; no review silently qualifies a changed source.
Keep the complete original archives and failure outcomes. Later installation
and relocation acceptance must include every imported module and preserve the
existing offline-tools component. The session manifest is the actual accounting
authority; running or planned workers are not accepted results.

The inspected concurrent `27209a7` publication completes the separate standalone
session and retains its [actual platform audit](reviews/STANDALONE_FINAL_PLATFORM_AUDIT.md),
including the earlier demo repair's Windows pass at `6214032f`. Its
[concurrent integration record](reviews/STANDALONE_CONCURRENT_CALIBRATION_INTEGRATION.md)
also records all ten successful hosted jobs at `27209a7f`, including 103/103
core suites and the alternative newline-free marker with 15 Windows installation
passes/one POSIX-only skip. That source predates the new allocation/CLI changes. This merged
calibration source retains the literal binary-copy fixture already
qualified at `c352d68` and in the full 106-suite source, while preserving both
tracks' original evidence and histories. Root reran the affected installation and repository-documentation gates for
these merges; their exact source scopes remain in the integration record.

## Reviewed continuation

The [independent handoff review](reviews/CALIBRATION_HANDOFF_REVIEW.md) verifies
actual setup options, recovery behavior, complete failed-result replay and
package/acquisition boundaries. The [M0–M9 reconciliation](reviews/CALIBRATION_MILESTONE_RECONCILIATION.md)
names the actual Engine scope and each owner's next concrete output; separate
scanner/rotary research modules are not integrated dry-engine stages.

The [runtime-context review](reviews/CALIBRATION_RUNTIME_CONTEXT.md) adds actual
CPython 3.13.5 Linux execution of nine maintained pipeline methods / 71 child
processes and twelve producer/replay processes across 3.12/3.13. Own-runtime
reports match; cross-runtime reports honestly mismatch. This finite check does
not claim full-suite or minimum-interpreter qualification.

## Evidence and continuation

The [fresh atlas review](research/CALIBRATION_ATLAS_REVIEW.md) records all
500 text pages and the selected original page images inspected by six actual
readers. The PDF remains unchanged. The capture contracts are project proposals
derived from the source requirements; missing instrument recordings remain
missing. Synthetic fixtures prove only their stated software properties.

Preserve raw bytes, exact manifest and policy identities, file ancestry, channel
meaning, whole related groups, failures and inconclusive outcomes. Numerical
agreement does not establish specimen identity, permissions, physical scale,
clock calibration, untouched final-test history, listening acceptance or
instrument fidelity. Consult the [capture protocol](CAPTURE_PROTOCOL.md) before
designing actual acquisition.

Every future agent reads `AGENTS.md`, takes explicit owned paths, continues a
dependency-ready task and retains an honest result note. The integrator updates
status, next steps, this handoff and the development log, verifies a coherent
source snapshot, commits completed work and pushes to main under the owner's
standing authorization. Integrate concurrent changes and verify the fetched
remote identity; never force-push. Earlier session workers are not counted as
new assignments.

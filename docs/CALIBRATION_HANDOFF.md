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

## Current integration and next work

The latest verified published checkpoint is
`3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf`, tree
`656c5f117060210b3df656c62318d5a672fc306d`, containing the first 42 accepted
assignments and preserving the concurrent `6214032` native test advance. Its
full tested source is retained as reachable commit `7caee9e5a1aadfa36f2a87b6855684cbd730d803`.
Later assignments 43–48 are accepted locally: the minimal metadata allocation
change, independent graph qualification, process-level stream repair and evidence
boundary review. Their
[15-suite allocation gate](reviews/CALIBRATION_ALLOCATION_INTEGRATION.md)
is separate from the later accepted stdout/stderr repair and its pending combined
source gate/publication.

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
passes locally and needs a fresh Windows run. Replay and the 57-file package
are independently accepted. Their [combined source](reviews/CALIBRATION_INSTALL_REPLAY_INTEGRATION.md)
passes 103/103 unfiltered local Release suites; the exact source mapping and logs
are retained separately from later documentation. Resource profiling, the
220-case composition review and the accounting audit complete seven waves and
42 accepted assignments at that publication. The current manifest records 48
accepted assignments and eight complete waves. The remaining assignments qualify
clean setup, compatibility, operation/acquisition plans and final handoff.
Keep the complete original archives and failure outcomes. Later installation
and relocation acceptance must include every imported module and preserve the
existing offline-tools component. The session manifest is the actual accounting
authority; running or planned workers are not accepted results.

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

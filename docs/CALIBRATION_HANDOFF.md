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

## Commands available at the initial implementation checkpoint

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
[file-job contract](CAPTURE_JOB_CONTRACT.md) is under independent composition
review before implementation. No gain, delay, resampling or channel fitting is
silently applied by the metric producer.

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

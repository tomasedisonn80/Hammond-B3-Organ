# Capture portability at the combined standalone checkpoint

Assignment **58/60**, logical wave **10**, actual worker
`/root/w10_a58_capture_portability`, executed **2026-11-14 UTC**.
This is an independent investigation and acceptance of capture-tool failures
exposed by the combined standalone source. It does not claim another atlas
reading, a physical capture, or native Windows execution in this Linux worker.

## Result and authorship

All four originally failing Python suites pass locally against frozen tree
`bff821cd872eccc7b3699d118bd49ad4214e89c0`: **210 methods, 208 passed, two
existing native-capability skips, zero failures/errors**. This tree is public
`955fc4c41f74ada094f14fbaf386c943811e9050` plus one independently authored corpus
admission method. The original Windows failure remains retained below; a fresh
native Windows job on the published integrated revision is a separate gate.

The **calibration integrator**, in commit
`340903a333ecfa5c684620ae8ac54e2e917a6217`, authored the production UTF-8 writers,
canonical fixture roots, positive fault-interception checks, explicit mutation
stamp and initial portable stream regressions. Those changes were already
preserved at `955fc4c` when the coordinator discovered the concurrent advance.
See [their hosted portability report](CALIBRATION_HOSTED_PORTABILITY.md).
Assignment 58 preserved these changes and independently qualified them. It did
not overwrite or claim authorship of the concurrent repair.

The only additional maintained test is
`CorpusAdmission.test_unicode_inputs_and_rejection_match_stringio_and_legacy_bytes`.
It admits actual Unicode specimen text and a Unicode archive-root path, checks
the unchanged canonical report, and checks a Unicode missing-file diagnostic.
Each outcome runs through both `StringIO` and real `TextIOWrapper` objects with
`encoding="cp1252", newline="\r\n"` over `BytesIO`. The exact bytes/text and the
empty opposite stream are asserted. Direct text-layer counterexamples prove
that report LF translation and diagnostic encoding failure would occur if that
layer were used. The corpus report deliberately retains constrained ASCII
identities/paths rather than the free-text specimen metadata.

No producer, admission policy, schema, parser, graph, core, Session, native main,
installed payload or CMake change was authored by this assignment. The calibration
advance also extracts the existing corpus audit body into `_audit_loaded` for
its separately owned file-job work; that concurrent refactor is preserved.
Shared status, accounting, publication and the real platform rerun belong to
the coordinator.

## Original observed Windows failure

Source: public `0085e338388f2c7516a7d455f11692b94e9451f4`, tree
`19c763503f67e1f054d2d27b6ec3d8fca2e36474`. Actual
[Windows core job 132244338459](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43529788060/job/132244338459)
in run **43529788060** completed **92/96 suites**, four failed, in **148.31 s**.
CTest exited 8. This is not a Windows native-standalone job failure.

The supplied full decoded job log was inspected, including every one of its
**40 assertion-failure records and one error record**. Its SHA-256 is
`78a40143e8844b96ebffdd24136e870640d3a99208955dc84ff3186461ebe864`.
The coordinator's saved analysis copy normalizes log CRLF to LF; this hash does
not identify the original downloaded ZIP. The appendix retains all 41 extracted
failure/error blocks, including their original assertion representations.

| Original suite | Methods | Recorded failures/errors | Diagnosis |
| --- | ---: | --- | --- |
| `python_test_capture_audio` | 41 | Five assertion failures | Four error envelopes and one success ended with CRLF rather than LF. |
| `python_test_capture_audio_admission` | 62 | 24 assertion failures; five capability skips | **23** stream-byte failures plus one canonical-parent hook miss. |
| `python_test_capture_corpus` | 47 | One assertion failure | Canonical pretty JSON had CRLF on every line. |
| `python_test_capture_corpus_admission` | 57 | Ten assertion failures, one error; six capability skips | Nine missed path-target rejects, one mutation-observation assumption, and one one-sided identity injection. |

The complete grouping accounts for every record:

| Failing method/subcases | Records | Mechanism |
| --- | ---: | --- |
| Audio `test_cli_errors_have_stable_envelope_and_empty_stdout` | 4 | CRLF in the canonical typed error envelope. |
| Audio `test_cli_success_is_exact_canonical_json_from_foreign_cwd` | 1 | CRLF in normal JSON stdout. |
| Audio admission `test_cli_admission_errors_are_complete_finite_json_without_stdout` | 5 | CRLF for unsupported, malformed, nonfinite, out-of-range and missing input. |
| Audio admission `test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens` | 12 | Eleven invalid-token cases and one admitted long token's range rejection all had CRLF. |
| Audio admission `test_unknown_abbreviated_output_and_unpaired_options_create_no_file` | 6 | Six usage envelopes had CRLF. |
| Audio admission `test_canonical_parent_identity_is_rechecked_without_timestamp_false_positive`, identity change | 1 | The literal unresolved-parent comparison missed the canonical parent. |
| Corpus `test_repeat_relocation_cli_bytes_and_input_preservation` | 1 | Pretty JSON stdout passed through newline translation. |
| Corpus admission `test_controlled_reparse_metadata_rejects_every_confined_level` | 5 | Index, captures directory, manifest, artifact directory and artifact hook targets missed. The selected root case itself did not fail. |
| Corpus admission `test_missing_both_artifact_identities_rejects_alias_claim` | 1 | The path identity was not zeroed; the descriptor-only zero left a usable path identity. |
| Corpus admission `test_stat_failures_are_contextual_and_release_descriptors`, lstat | 3 | Index, manifest and artifact lstat injections missed. Existing descriptor and close assertions were retained. |
| Corpus admission `test_usable_path_or_descriptor_identity_fallback_and_zero_device`, device zero | 1 error | Only descriptor device changed; the valid producer then rejected a path/descriptor mismatch. |
| Corpus admission `test_file_mutation_during_metadata_or_artifact_read_rejects` | 1 | The fixture had not guaranteed an observable stamp change after its same-size write. |

### Actual alias mechanism

The original fixtures constructed markers directly from `TemporaryDirectory.name`,
which on that runner retained `C:\Users\RUNNER~1\...`. The corpus producer
canonicalizes ancestors and subsequently observes
`C:\Users\runneradmin\...`; the error traceback records that long form. Audio
similarly resolves the input's parent before its independent parent observation.
Path equality tests in the injected hooks compare spellings, not filesystem
object identity. The hooks therefore did not reach the observations they claimed
to alter. Resolving the fixture's existing temporary root before constructing
markers makes both refer to the same spelling. Positive assertions now require
the canonical-parent, confined-reparse, artifact-path and descriptor hooks to run.
Original lstat-failure tests already require exactly one matching call.

This does not relax symlink/reparse confinement or change usable identity rules.
Explicit ancestor-alias admission tests remain. A local native symlink probe,
described below, independently reproduces the literal-target mismatch without
claiming to create Windows 8.3 paths.

### Separate same-size mutation observation

The mutation wrapper selects streams by their actual device/inode, so its failure
is **not explained by the unresolved path spelling**. The original fixture wrote
one byte after the reader obtained its data and assumed the portable before/after
stamp observations would immediately differ. The failed job did not retain those
stamp values; its exact native timestamp/update behavior cannot be reconstructed
from the traceback alone.

The calibration repair retains that real same-size byte write, explicitly calls
`os.utime` with mtime advanced by **2,000,000,000 ns**, asserts the observed mtime
differs, and asserts the mutation hook ran. The same-size write is still required
to be rejected; no existing assertion is weakened. This checks an observable
mutation under the existing quiescent-archive contract. A writer that leaves all
observed stamps identical remains outside the portable immutable-snapshot claim.

## Frozen source and exact local acceptance

The original archive had 894 tracked files. The independently extracted repaired
base is `955fc4c41f74ada094f14fbaf386c943811e9050`, tree
`70956d0f0e125d57abfbf1aed56460c067f8ef28`; its `git archive --format=tar` SHA-256
is `27b617a5ff1a890f5499e022581b130851de5e60fc677e3311b369be98fbcf4c`.
Only the final 45-line corpus-admission method is overlaid for tested tree
`bff821cd872eccc7b3699d118bd49ad4214e89c0`. No live concurrent source was used
while these suites ran. The snapshot's manifest was verified again afterward;
the copied live test equals the qualified bytes.

Runtime: **Python 3.12.14**, built with Clang 22.1.3, on
**Linux 6.18.57 x86-64, glibc 2.41**. The tools use the standard library; no
dependency was installed for this assignment. There was no Windows kernel,
Windows short-path API, macOS runner or physical device in this execution.

| Frozen file | SHA-256 |
| --- | --- |
| `tools/capture_audio.py` | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_corpus.py` | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `tests/test_capture_audio.py` | `9fc75824234b3203f1eb9f63c0fe7562a3d9a931cda34e9a774b4c1402c56ddd` |
| `tests/test_capture_audio_admission.py` | `871d5c71e8aa57d8e6f6daca14bbd2e0a3d09bf913e4468aaa197b4155faabf7` |
| `tests/test_capture_corpus.py` | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |
| `tests/test_capture_corpus_admission.py` | `6fdbc511bfd96e9767c3dd78366c7abb75b061b263295c4fae62f0f051ac36f6` |

Cwd was
`/workspace/scratch/5ba97739b54c/a58-capture-portability/remote-955`.
Each full original suite was invoked separately; the four independent processes
ran concurrently, and their source snapshot did not change:

```sh
python3 -B tests/test_capture_audio.py -v
python3 -B tests/test_capture_audio_admission.py -v
python3 -B tests/test_capture_corpus.py -v
python3 -B tests/test_capture_corpus_admission.py -v
```

| Final complete suite | Result | Unittest elapsed |
| --- | --- | ---: |
| Audio acceptance | 41 passed, no skips | 0.797 s |
| Audio admission | 61 passed, two existing capability skips, 63 methods | 2.833 s |
| Corpus acceptance | 47 passed, no skips | 1.329 s |
| Corpus admission | 59 passed, no skips | 2.999 s |

The two Linux skips are the existing real Windows-reparse fixture and the native
Unix-domain socket fixture whose bind returned `EPERM`. They are **not passes**.
No new skip was introduced. Windows's original five/six capability skips remain
separate observations and cannot be replaced by this Linux result. The audio
and corpus acceptance files were untouched; their exact byte assertions still
reject CRLF. The admission suite counts increased from the original 62/57 to
63/59: one calibration stream method in each, plus this assignment's one corpus
method.

## Independent counterexamples

The retained private harness `run_portability_probes.py` has SHA-256
`1363943eebd758972dc18db5af9aae6a2642a7968bc2459e31595c8ee6f1701a`.
It loads named maintained tests from an explicitly selected frozen source; the
alias mode creates a real native Linux symlink above temporary fixture roots.
It does not monkeypatch the platform name, Windows path parser or filesystem
identity rules. Its source is included below for reproducibility.

| Controlled observation | Original 0085 | Final repair |
| --- | --- | --- |
| Three stream methods using actual ASCII/CP1252 `TextIOWrapper` objects with CRLF translation | Four assertion failures and two `UnicodeEncodeError` records; 0.025 s | 3/3 passed; 0.014 s |
| Five original fault-fixture methods with a real ancestor symlink | Ten assertion failures plus one identity mismatch error; 0.040 s | 5/5 passed; 0.016 s |

For the stream negative control, the original production source receives only
the two final admission-test files. For the alias negative control, the complete
original source and original tests remain unchanged. The original defects are
retained as expected failures, not relabeled as successful acceptance runs.
These probes establish local failure mechanisms and regression sensitivity;
they do **not** qualify Windows or macOS.

Cwd for the four commands below was
`/workspace/scratch/5ba97739b54c/a58-capture-portability`:

```sh
python3 -B run_portability_probes.py --source /workspace/scratch/5ba97739b54c/a58-capture-portability/original-with-new-stream-tests --mode streams
python3 -B run_portability_probes.py --source /workspace/scratch/5ba97739b54c/a58-capture-portability/remote-955 --mode streams
python3 -B run_portability_probes.py --source /workspace/scratch/5ba97739b54c/a58-capture-portability/baseline --mode ancestor-alias
python3 -B run_portability_probes.py --source /workspace/scratch/5ba97739b54c/a58-capture-portability/remote-955 --mode ancestor-alias
```

The baseline was extracted by `git archive --format=tar 0085e338388f2c7516a7d455f11692b94e9451f4`;
archive SHA-256 is
`6cd03188f0db9f70f7c7abe7c5e05131da12a3e10d34a7320140b6e57f0f0da0`.
The negative stream tree copies that archive and replaces only its two admission
tests with the final qualified files. Python `-B` avoids source bytecode writes;
all fixtures are privately generated synthetic data.

## Retained authored-fixture failure

The first additional corpus method incorrectly tried a Unicode `session_id`.
The unchanged validator correctly rejected it because IDs have the frozen ASCII
grammar. The first private tree was
`a94135c9d988d38742806dffffbd293cb68f6d6f`, with corpus-admission SHA-256
`ad9772e2bd3f69d1a465c89e910567e2e2d28c5129242724114501a808d54a8c`.
Its full corpus-admission suite ran 59 methods and produced **one error** in
1.714 s. The other three suites passed at that first tree: 41 in 0.541 s,
63 with two capability skips in 2.501 s, and 47 in 1.089 s.

The exact rejection was
`acquisition.session_id.value: expected ID matching [a-z][a-z0-9_-]{0,63}`.
This was the test author's invalid fixture, not a producer defect. The final
test puts free Unicode text in the admitted specimen variant and uses a Unicode
archive-root path, then retains the normal ASCII identities. No schema or
producer acceptance rule changed. After that concrete correction, all four
suites ran against the final frozen tree; no unchanged failed run was retried
to obtain a pass.

Before discovering the concurrent published repair, this worker also drafted
two admission-test edits against 0085. That unapplied proposal was saved
privately (SHA-256
`48663a5f7e9756f6d69693931bb24d55b481b1cf4f1f8cfe790c28e879ca6392`)
and the two live files restored to their verified baseline before root integrated
955. It is not part of the final source or an additional claimed repair.

## Evidence identities and continuation

The next tables identify local observations; they do not pretend that a scratch
path is a public archive. The durable failure excerpts and probe source below,
the maintained tests, the public job link and the exact source revisions retain
the substantive reproduction evidence.

The final independent test patch has SHA-256
`fde0c2b2bfd1edbc7121bcad950e7053a0f65450e26d69db2378d3f094f74726`.
The coordinator integrated calibration 955 with separate standalone work at
local merge `85f544f0c3a96972e021db21b8b8cf58741e2951`; that is distinct from
this worker's frozen test tree and requires its own combined publication gate.
Assignment 59 independently reviews the final overlay and production scope.

Next, publish the coherent integrated source under the owner's standing
authorization and inspect the actual Windows core job. Require all four named
suites to complete with the strict original assertions, retain capability skips
explicitly, and name the exact published commit/tree/job. Keep queued, canceled
or unacquired macOS jobs separate. Do not infer a native-platform, physical-device,
calibration, acquisition-permission or fidelity pass from these Linux probes.
The calibration scope, capture-v1 identities, quiescent-input limitation and
future-agent standing workflow remain in force.


### Local retained log identities

| Observation file | Bytes | SHA-256 |
| --- | ---: | --- |
| `candidate-windows-core.log` (decoded/normalized copy) | 313955 | `78a40143e8844b96ebffdd24136e870640d3a99208955dc84ff3186461ebe864` |
| `windows-failure-details.txt` | 36709 | `6e135cd2d0364aeeda4de6b5fe4b51a8ba3f26c04a9f4e7b04ddb46f02bf0c2c` |
| `windows-failure-index.json` | 56998 | `c332387652a965e0e23d754972e81387df421d93f92fc1f5dab8e84e3094429c` |
| `run_portability_probes.py` | 2824 | `1363943eebd758972dc18db5af9aae6a2642a7968bc2459e31595c8ee6f1701a` |
| `old-stream-probe.log` | 13716 | `2fbabd3b5e40f69d8c81a0ae5d1b4a557681346117c8109071af207a39739375` |
| `new-stream-probe.log` | 860 | `2599bb2a68a912757828cf55eabb90a708b6d30fd974d1b766756df43d65a630` |
| `old-alias-probe.log` | 15825 | `139056462b48fa30569161b7115be61cb88c7f5c8d35bb4b10b7ce9007a9cebc` |
| `new-alias-probe.log` | 1242 | `435f4403c28622d4431c1fedb7f086640221b791ad3baf95b958367f914538c3` |
| `test_capture_audio.log` | 5995 | `48aaf9f27d82aa96037e4c0a7f626548864a0f78103a68be9a96bd8c09d7f596` |
| `test_capture_audio_admission.log` | 9682 | `696326d70107a92b45c2dfb7f813e575f89c50f4868048b2ff371e7e2fc2811f` |
| `test_capture_corpus.log` | 7266 | `798bdb0cf444f0823af5fdfcdd3382fa5499d5b19047716d83cf1bc1e776213f` |
| `test_capture_corpus_admission.log` | 8723 | `2a278c6612d006f73a26542c3544a8c09c9ba8dfe8c16e02a7cbbb7f7a4483a6` |
| `invalid-fixture-test_capture_corpus_admission.log` | 11165 | `3e9f536fcac28ce45c95a17f326b268ecb59118c1d1a1681e372262451bfa229` |
| `invalid-fixture-frozen-manifest.json` | 1076 | `57142e16b8a27c80f0a6251867d8a3e78df9d832c256449cd0aeeb8697c10d13` |
| `frozen-manifest.json` | 1076 | `7bc1931cf2700e10965d98e525efe5800063482903f8621a7b7d93edb5cd3a6e` |

## Reproducible local probe source

Save the following as `run_portability_probes.py` outside the frozen source,
then use the exact source-selection commands above. This is a local observation
harness, not a new installed tool or platform emulator.

```python
#!/usr/bin/env python3
"""Retained local mechanism probes; this does not emulate a native Windows OS."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--mode", choices=("streams", "ancestor-alias"), required=True)
args = parser.parse_args()
sys.dont_write_bytecode = True
sys.path.insert(0, str(args.source / "tests"))

stream_tests = [
    "test_capture_audio_admission.CommandLineAdmission.test_json_bytes_bypass_text_newline_and_encoding_translation",
    "test_capture_corpus_admission.CorpusAdmission.test_cli_bytes_bypass_text_newline_and_encoding_translation",
    "test_capture_corpus_admission.CorpusAdmission.test_unicode_inputs_and_rejection_match_stringio_and_legacy_bytes",
]
alias_tests = [
    "test_capture_audio_admission.FilesystemAdmission.test_canonical_parent_identity_is_rechecked_without_timestamp_false_positive",
    "test_capture_corpus_admission.CorpusAdmission.test_controlled_reparse_metadata_rejects_every_confined_level",
    "test_capture_corpus_admission.CorpusAdmission.test_usable_path_or_descriptor_identity_fallback_and_zero_device",
    "test_capture_corpus_admission.CorpusAdmission.test_missing_both_artifact_identities_rejects_alias_claim",
    "test_capture_corpus_admission.CorpusAdmission.test_stat_failures_are_contextual_and_release_descriptors",
]
names = stream_tests if args.mode == "streams" else alias_tests
suite = unittest.defaultTestLoader.loadTestsFromNames(names)
start = time.perf_counter()
if args.mode == "ancestor-alias":
    real_temporary = tempfile.TemporaryDirectory
    with real_temporary(prefix="a58-native-alias-") as outer:
        physical = Path(outer) / "physical"
        physical.mkdir()
        alias = Path(outer) / "ancestor-alias"
        alias.symlink_to(physical, target_is_directory=True)
        assert alias != alias.resolve(strict=True)

        def through_alias(*values, **options):
            options["dir"] = str(alias)
            return real_temporary(*values, **options)

        with mock.patch.object(tempfile, "TemporaryDirectory", through_alias):
            result = unittest.TextTestRunner(verbosity=2).run(suite)
else:
    result = unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({"source": str(args.source), "mode": args.mode,
                  "methods": result.testsRun, "failure_records": len(result.failures),
                  "error_records": len(result.errors), "skipped": len(result.skipped),
                  "successful": result.wasSuccessful(),
                  "elapsed_seconds": round(time.perf_counter() - start, 6)}, sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
```

## Appendix: every original Windows failure/error block

All 41 blocks below were extracted from the retained decoded job log. Only the
CI timestamp prefix was removed; traceback text, escaped byte representations,
subcase arguments and the original method names are retained. The extracted
36,709-byte text has SHA-256
`6e135cd2d0364aeeda4de6b5fe4b51a8ba3f26c04a9f4e7b04ddb46f02bf0c2c`.

```text
FAIL: test_cli_errors_have_stable_envelope_and_empty_stdout (__main__.AudioAcceptance.test_cli_errors_have_stable_envelope_and_empty_stdout) (arguments=('--input', WindowsPath('C:/Users/RUNNER~1/AppData/Local/Temp/capture-audio-acceptance-klyhh4t1/capture.wav'), '--start-frame', '1'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio.py", line 653, in test_cli_errors_have_stable_envelope_and_empty_stdout
    self.assertEqual(result.stderr, (json.dumps(error, sort_keys=True, separators=(",", ":"),
AssertionError: b'{"e[113 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[113 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_errors_have_stable_envelope_and_empty_stdout (__main__.AudioAcceptance.test_cli_errors_have_stable_envelope_and_empty_stdout) (arguments=('--input', WindowsPath('C:/Users/RUNNER~1/AppData/Local/Temp/capture-audio-acceptance-klyhh4t1/capture.wav'), '--frame-count', '1e1', '--start-frame', '0'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio.py", line 653, in test_cli_errors_have_stable_envelope_and_empty_stdout
    self.assertEqual(result.stderr, (json.dumps(error, sort_keys=True, separators=(",", ":"),
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_errors_have_stable_envelope_and_empty_stdout (__main__.AudioAcceptance.test_cli_errors_have_stable_envelope_and_empty_stdout) (arguments=('--input', WindowsPath('C:/Users/RUNNER~1/AppData/Local/Temp/capture-audio-acceptance-klyhh4t1/capture.wav'), '--sample-rate-hz', '44100'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio.py", line 653, in test_cli_errors_have_stable_envelope_and_empty_stdout
    self.assertEqual(result.stderr, (json.dumps(error, sort_keys=True, separators=(",", ":"),
AssertionError: b'{"e[169 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[169 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_errors_have_stable_envelope_and_empty_stdout (__main__.AudioAcceptance.test_cli_errors_have_stable_envelope_and_empty_stdout) (arguments=('--input', WindowsPath('C:/Users/RUNNER~1/AppData/Local/Temp/capture-audio-acceptance-klyhh4t1/absent.wav')))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio.py", line 653, in test_cli_errors_have_stable_envelope_and_empty_stdout
    self.assertEqual(result.stderr, (json.dumps(error, sort_keys=True, separators=(",", ":"),
AssertionError: b'{"e[94 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[94 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_success_is_exact_canonical_json_from_foreign_cwd (__main__.AudioAcceptance.test_cli_success_is_exact_canonical_json_from_foreign_cwd)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio.py", line 622, in test_cli_success_is_exact_canonical_json_from_foreign_cwd
    self.assertEqual(first.stdout, expected)
AssertionError: b'{"a[1665 chars]07663db4f07702ed9ac","size_bytes":60,"status":"inspected"}\r\n' != b'{"a[1665 chars]07663db4f07702ed9ac","size_bytes":60,"status":"inspected"}\n'

----------------------------------------------------------------------


FAIL: test_repeat_relocation_cli_bytes_and_input_preservation (__main__.CorpusAcceptance.test_repeat_relocation_cli_bytes_and_input_preservation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus.py", line 871, in test_repeat_relocation_cli_bytes_and_input_preservation
    self.assertEqual(left.stdout, _json_bytes(report))
AssertionError: b'{\r\n  "audio_check": "verified",\r\n  "aut[4819 chars]\r\n' != b'{\n  "audio_check": "verified",\n  "authent[4525 chars]n}\n'

----------------------------------------------------------------------


FAIL: test_cli_admission_errors_are_complete_finite_json_without_stdout (__main__.CommandLineAdmission.test_cli_admission_errors_are_complete_finite_json_without_stdout) (code='unsupported_format')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 845, in test_cli_admission_errors_are_complete_finite_json_without_stdout
    self.cli_error(["--input", str(path)], 1, code)
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[102 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[102 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_admission_errors_are_complete_finite_json_without_stdout (__main__.CommandLineAdmission.test_cli_admission_errors_are_complete_finite_json_without_stdout) (code='malformed_audio')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 845, in test_cli_admission_errors_are_complete_finite_json_without_stdout
    self.cli_error(["--input", str(path)], 1, code)
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[122 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[122 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_admission_errors_are_complete_finite_json_without_stdout (__main__.CommandLineAdmission.test_cli_admission_errors_are_complete_finite_json_without_stdout) (code='nonfinite_sample')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 845, in test_cli_admission_errors_are_complete_finite_json_without_stdout
    self.cli_error(["--input", str(path)], 1, code)
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[144 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[144 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_admission_errors_are_complete_finite_json_without_stdout (__main__.CommandLineAdmission.test_cli_admission_errors_are_complete_finite_json_without_stdout) (code='sample_out_of_range')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 845, in test_cli_admission_errors_are_complete_finite_json_without_stdout
    self.cli_error(["--input", str(path)], 1, code)
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[154 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[154 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_cli_admission_errors_are_complete_finite_json_without_stdout (__main__.CommandLineAdmission.test_cli_admission_errors_are_complete_finite_json_without_stdout)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 847, in test_cli_admission_errors_are_complete_finite_json_without_stdout
    self.cli_error(["--input", str(self.directory / "missing.wav")], 1, "path_not_found")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[94 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[94 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='-1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='+1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token=' 1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='1 ')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='1.0')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='1e1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='1_0')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='\u0661')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='\uff11\uff12')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens) (token='999999999999999999999')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 823, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[135 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens (__main__.CommandLineAdmission.test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 825, in test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens
    self.cli_error(["--input", str(path), "--start-frame", "9" * 20, "--frame-count", "1"],
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[119 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[119 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_unknown_abbreviated_output_and_unpaired_options_create_no_file (__main__.CommandLineAdmission.test_unknown_abbreviated_output_and_unpaired_options_create_no_file) (extra=['--out', 'C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\capture-audio-admission-tlberv_e\\must-not-exist.json'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 835, in test_unknown_abbreviated_output_and_unpaired_options_create_no_file
    self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[201 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[201 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_unknown_abbreviated_output_and_unpaired_options_create_no_file (__main__.CommandLineAdmission.test_unknown_abbreviated_output_and_unpaired_options_create_no_file) (extra=['--output', 'C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\capture-audio-admission-tlberv_e\\must-not-exist.json'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 835, in test_unknown_abbreviated_output_and_unpaired_options_create_no_file
    self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[204 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[204 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_unknown_abbreviated_output_and_unpaired_options_create_no_file (__main__.CommandLineAdmission.test_unknown_abbreviated_output_and_unpaired_options_create_no_file) (extra=['--inp', 'C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\capture-audio-admission-tlberv_e\\capture.wav'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 835, in test_unknown_abbreviated_output_and_unpaired_options_create_no_file
    self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[193 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[193 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_unknown_abbreviated_output_and_unpaired_options_create_no_file (__main__.CommandLineAdmission.test_unknown_abbreviated_output_and_unpaired_options_create_no_file) (extra=['--start-frame', '0'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 835, in test_unknown_abbreviated_output_and_unpaired_options_create_no_file
    self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[113 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[113 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_unknown_abbreviated_output_and_unpaired_options_create_no_file (__main__.CommandLineAdmission.test_unknown_abbreviated_output_and_unpaired_options_create_no_file) (extra=['--frame-count', '1'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 835, in test_unknown_abbreviated_output_and_unpaired_options_create_no_file
    self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[113 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[113 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_unknown_abbreviated_output_and_unpaired_options_create_no_file (__main__.CommandLineAdmission.test_unknown_abbreviated_output_and_unpaired_options_create_no_file) (extra=['--raw-format', 'wav_pcm16'])
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 835, in test_unknown_abbreviated_output_and_unpaired_options_create_no_file
    self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 176, in cli_error
    self.assertEqual(result.stderr, expected)
AssertionError: b'{"e[142 chars]inspector_version":"capture-audio-v1","status":"rejected"}\r\n' != b'{"e[142 chars]inspector_version":"capture-audio-v1","status":"rejected"}\n'



FAIL: test_canonical_parent_identity_is_rechecked_without_timestamp_false_positive (__main__.FilesystemAdmission.test_canonical_parent_identity_is_rechecked_without_timestamp_false_positive) (identity_change=True)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 723, in test_canonical_parent_identity_is_rechecked_without_timestamp_false_positive
    self.reject("file_changed", audio.inspect_audio, path)
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_audio_admission.py", line 114, in reject
    with self.assertRaises(audio.AudioError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: AudioError not raised

----------------------------------------------------------------------


ERROR: test_usable_path_or_descriptor_identity_fallback_and_zero_device (__main__.CorpusAdmission.test_usable_path_or_descriptor_identity_fallback_and_zero_device) (options={'device_zero': True})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tools\capture_corpus.py", line 697, in audit_corpus
    size, digest = _verify_artifact(root, parts, artifact, identities[entry["capture_id"]])
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tools\capture_corpus.py", line 500, in _verify_artifact
    _bind_descriptor(before_path, before_fd, str(target))
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tools\capture_corpus.py", line 340, in _bind_descriptor
    _require(_identity(before_fd) == _identity(before_path), label,
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tools\capture_corpus.py", line 63, in _require
    raise CorpusError(f"{label}: {message}")
capture_corpus.CorpusError: C:\Users\runneradmin\AppData\Local\Temp\corpus-admission-0kvpmebu\archive\captures\a\raw.bin: file replaced while opening (path/descriptor identity mismatch)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 668, in test_usable_path_or_descriptor_identity_fallback_and_zero_device
    self.assertEqual(subject.audit_corpus(self.path, check_files=True)["file_check"], "verified")
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tools\capture_corpus.py", line 700, in audit_corpus
    raise CorpusError(f"{_where(entry, artifact['file_id'])}: {error}") from error
capture_corpus.CorpusError: manifest 'captures/a.json', capture 'a', file 'raw': C:\Users\runneradmin\AppData\Local\Temp\corpus-admission-0kvpmebu\archive\captures\a\raw.bin: file replaced while opening (path/descriptor identity mismatch)



FAIL: test_controlled_reparse_metadata_rejects_every_confined_level (__main__.CorpusAdmission.test_controlled_reparse_metadata_rejects_every_confined_level) (target='C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\corpus-admission-vlgk_639\\archive\\corpus.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 616, in test_controlled_reparse_metadata_rejects_every_confined_level
    self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_controlled_reparse_metadata_rejects_every_confined_level (__main__.CorpusAdmission.test_controlled_reparse_metadata_rejects_every_confined_level) (target='C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\corpus-admission-vlgk_639\\archive\\captures')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 616, in test_controlled_reparse_metadata_rejects_every_confined_level
    self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_controlled_reparse_metadata_rejects_every_confined_level (__main__.CorpusAdmission.test_controlled_reparse_metadata_rejects_every_confined_level) (target='C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\corpus-admission-vlgk_639\\archive\\captures\\a.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 616, in test_controlled_reparse_metadata_rejects_every_confined_level
    self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_controlled_reparse_metadata_rejects_every_confined_level (__main__.CorpusAdmission.test_controlled_reparse_metadata_rejects_every_confined_level) (target='C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\corpus-admission-vlgk_639\\archive\\captures\\a')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 616, in test_controlled_reparse_metadata_rejects_every_confined_level
    self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_controlled_reparse_metadata_rejects_every_confined_level (__main__.CorpusAdmission.test_controlled_reparse_metadata_rejects_every_confined_level) (target='C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\corpus-admission-vlgk_639\\archive\\captures\\a\\raw.bin')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 616, in test_controlled_reparse_metadata_rejects_every_confined_level
    self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_file_mutation_during_metadata_or_artifact_read_rejects (__main__.CorpusAdmission.test_file_mutation_during_metadata_or_artifact_read_rejects)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 855, in test_file_mutation_during_metadata_or_artifact_read_rejects
    self.reject(subject.audit_corpus, self.path, check_files=True)
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_missing_both_artifact_identities_rejects_alias_claim (__main__.CorpusAdmission.test_missing_both_artifact_identities_rejects_alias_claim)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 672, in test_missing_both_artifact_identities_rejects_alias_claim
    self.reject(subject.audit_corpus, self.path, check_files=True, contains="identity unavailable")
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_stat_failures_are_contextual_and_release_descriptors (__main__.CorpusAdmission.test_stat_failures_are_contextual_and_release_descriptors) (target='corpus.json', kind='lstat')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 720, in test_stat_failures_are_contextual_and_release_descriptors
    self.reject(subject.audit_corpus, self.path, check_files=True,
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_stat_failures_are_contextual_and_release_descriptors (__main__.CorpusAdmission.test_stat_failures_are_contextual_and_release_descriptors) (target='a.json', kind='lstat')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 720, in test_stat_failures_are_contextual_and_release_descriptors
    self.reject(subject.audit_corpus, self.path, check_files=True,
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised



FAIL: test_stat_failures_are_contextual_and_release_descriptors (__main__.CorpusAdmission.test_stat_failures_are_contextual_and_release_descriptors) (target='raw.bin', kind='lstat')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 720, in test_stat_failures_are_contextual_and_release_descriptors
    self.reject(subject.audit_corpus, self.path, check_files=True,
  File "D:\a\Hammond-B3-Organ\Hammond-B3-Organ\tests\test_capture_corpus_admission.py", line 150, in reject
    with self.assertRaises(subject.CorpusError) as caught:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: CorpusError not raised

----------------------------------------------------------------------
```

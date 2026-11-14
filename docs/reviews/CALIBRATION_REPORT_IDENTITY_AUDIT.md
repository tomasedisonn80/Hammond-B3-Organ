# Capture report identity after the CLI delivery repair

Assignment **54**, logical wave **9**, actual worker `/root/cal_w9_a54`,
2026-11-14. This finite independent audit qualifies the immutable capture-tool
source at local `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a`, tree
`3edea0838b75feb06c19e151ec8539e80646fc03`. It does not qualify an evolving
working tree. Publication evidence is separately attributed to the integrator.

**Result: 20 check groups passed through 22 fresh project CLI processes.**
Thirteen complete replay summaries comprise eight exact matches and five
expected source-context mismatches. One additional replay invocation rejects a
noncanonical copy without a summary. Both retained older reports remain intact.
The final source produces a new canonical study whose complete analytical and
claim content is identical when only four explicitly named source-inventory
arrays are removed. Public replay still compares every canonical byte and
correctly reports the older reports as mismatches.

The [assignment record](../development/2026-11-13-calibration/54-report-identity.md)
retains the actual commands, independent harness, exact output identities and
one corrected harness mistake. No production code, test, public report,
threshold or fixture was modified for this audit. The existing
[replay contract](../CAPTURE_REPLAY.md),
[job contract](../CAPTURE_JOB_CONTRACT.md) and
[study contract](../CAPTURE_STUDY.md) remain unchanged.

## Source basis and exact revision boundary

Atlas pp. 355, 364, 449, 484 and 486 require preserving original bytes,
declared analysis, uncertainty, failures and the actual code/setup. Those pages
were read for this assignment. Their change-control rule is the reason to keep
an older report and create a separately identified new execution after a source
repair. The audit does not reread or claim independent coverage of all 500 pages.

| Source | Local immutable commit | Verified local tree | Corresponding GitHub commit |
| --- | --- | --- | --- |
| Original bounded-replay tooling | `16d72e1b351e5cdf1730e90645a6ea37144d1be7` | `5619bbb018830e071bc2ce45af84984cdd16bfc1` | `7caee9e5a1aadfa36f2a87b6855684cbd730d803` |
| Accepted allocation repair | `459bfacbda90005d618f12c4513b9c71cb11193d` | `3325af558b040759c1b432ec0806a80785af9713` | `d377fab7a840dc6d7a499fdf576d0dd8bb5dd4c1` |
| Combined allocation and CLI repair | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` | `3edea0838b75feb06c19e151ec8539e80646fc03` | `5e19022c8696023bb1aa841ebea2eaeec0d719a3` |

The public mappings are the integrator's supplied mappings. This worker
independently checked all three local trees and all thirty corresponding tool
blobs. At assignment dispatch the latter two public objects were prepared while
the integrator reconciled concurrent remote `27209a7fec075b082aa911c9ea2159938deaae85`.
Before this record was frozen, the integrator reported publication and fetched
verification of `d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree
`0140c737de4db28288b118744c2beef57976697f`, with `d377fab7...` and `5e19022c...`
retained as reachable ancestors. That publication check is root's execution;
this worker's independent evidence is the local source/tree inspection and
fresh report executions. Different local/public commit IDs do not authorize
attributing a source test to a different tree.

The sources were copied as coherent sets of ten modules from their frozen
archives, checked against `git show <local-commit>:tools/<module>`, then run in
fresh `python -B -S` interpreters from a foreign working directory. No producer
was imported into the audit interpreter. The three reported runtimes were
exactly `python_implementation=cpython`, `python_version=3.12.14`,
`sys_platform=linux`, `machine=x86_64`.

The original-to-allocation change affects only `capture_corpus.py`.
The allocation-to-final change affects nine of the ten tool files;
`compare_capture.py` remains byte-identical. Six of the seven study-observed
modules change, five of the six job-observed modules change, and the verifier's
separate own-source observation changes. Consequently, a changed report hash is
expected even though the analysis and claim content is unchanged.

## Canonical original reports and new output

The input evidence is the actual
[`allocation_comparison.json`](../../examples/benchmarks/capture-toolchain-v1/allocation_comparison.json),
304,390 bytes, SHA-256
`791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc`.
Its two embedded complete report values were serialized with sorted keys,
two-space indentation, UTF-8, `ensure_ascii=False`, `allow_nan=False` and a final
LF. Their resulting identities match the artifact's retained identities and
the independent fixed expectations below. This reconstructs a separate copy of
the originally retained canonical value; it does not normalize or overwrite a
saved report.

| Complete study | Bytes | SHA-256 | Own-source replay |
| --- | ---: | --- | --- |
| Original `16d72e1` report | 119,423 | `6cf434334a9a612e18224a986fbfb1e7636556be8669c44b526b9629b9208727` | Exact match |
| Allocation `459bfac` report | 119,423 | `71d5148953659ca51b0aa21f1881eb75a8e7942a008c3835d0492ea199bfe736` | Exact match |
| Final `48a1907` report | 119,427 | `b1446aa4c2f66d578331c2b784b48791cd03897ac66fe1226ffc3d6e659e3aaa` | Exact match |

All three fresh study commands exit **1**, because the retained engineering
study status is `failed`. Their own-source verifier commands exit **0**, because
the complete failed result reproduces exactly. On the final source, replaying
either older study exits **1** with a complete `mismatch` summary,
`same_runtime: true`, `same_tool_sources: false` and
`exact_report_match: false`. The verifier retains both complete report identities
and the saved/replayed engineering status `failed`.

The three final job CLI outputs also equal the complete embedded study reports,
byte for byte. Their exits are `0`, `3`, `1` for `pass`, `inconclusive`, `failed`.
Each matches under a new final-source replay. Each older allocation-source job
report mismatches under final sources, with the original engineering status
preserved on both sides. The full comparison is not relaxed because a policy
or numerical verdict is unchanged.

## What is identical, and why four bytes changed

The audit deletes **only** these four paths from deep copies of each complete
study value:

```text
/tool_sources
/jobs/0/report/tool_sources
/jobs/1/report/tool_sources
/jobs/2/report/tool_sources
```

The complete remaining canonical bytes are identical across all three sources:
114,760 bytes, SHA-256
`760543356e4bd9a555b4649e432d0ac6d35ee428716a91d83720d1eeb33ef479`.
No runtime, input binding, metadata, policy, numeric result, work count, status,
role, claim or nested finding is removed. This is an explicitly bounded audit
projection. **It is not public replay match**, a supported override, or an
acceptable replacement report. The public verifier was exercised separately
and produced the full-byte mismatches above.

The source arrays' actual canonical lengths explain the complete four-byte
increase:

| Array | Allocation-source bytes | Final-source bytes | Difference |
| --- | ---: | ---: | ---: |
| Study root `tool_sources` | 1,050 | 1,051 | +1 |
| Pass job `tool_sources` | 901 | 902 | +1 |
| Inconclusive job `tool_sources` | 901 | 902 | +1 |
| Failed job `tool_sources` | 901 | 902 | +1 |

`capture_common.py` grows from 9,625 to 12,774 bytes, adding one decimal digit
in each of the four arrays. Every digest remains 64 characters; the other
observed source sizes keep the same decimal width. The complete projected
remainder is identical, so the sum of the four observed array deltas accounts
for the full report-size delta. This explanation is based on actual contexts,
not inferred from an unchanged status.

All ten claims at the study root and at each of its three job roots remain
`not_established`: boundary equivalence, synchronization, authenticity, specimen
identity, calibration, permissions, independence, preregistration, final
holdout history and physical fidelity. The study retains one pass, one
inconclusive and one failed job; all three roles are `validation`, with zero
fit/final-test/unassigned jobs. Work remains 12 window samples and 12 spectral
terms. These forty root/embedded claim values were checked directly as well as
included in the complete-byte projection.

## Original input identities and provenance inventory

The same unchanged 16-file, 32,831-byte synthetic archive was executed under all
three sources. Each file matched both retained archive inventories and each
corresponding Git blob. Original study, job and policy bytes were bound directly;
the corpus, all three manifests and all three raw audio files were also checked
against the reports' expected and observed hashes and sizes. No original input
was reformatted or regenerated.

The canonical sorted inventory of all 16 `{path, sha256, size_bytes}` records is
2,353 bytes, SHA-256
`76fea5dfb708444f75d7b8c53ea687f36a831f6921ec405d5d58e08da4f681ee`.
This identifies the inventory serialization, not a single packed archive file.
The assignment record retains all sixteen entries and the exact serialization
used by the independent audit.

The job inventory contains exactly `capture_audio.py`, `capture_common.py`,
`capture_corpus.py`, `capture_job.py`, `compare_capture.py` and
`validate_capture.py`. The study inventory adds `capture_study.py`.
An independent AST traversal of the declared project imports produces exactly
those six/seven producer closures for each source snapshot. Each recorded source
size/hash was separately compared with its actual copied bytes.

The replay summary separately records `verify_capture_report.py` and its runtime,
and binds original input bytes, saved bytes, freshly reproduced bytes and both
contexts. The verifier's static imported-project closure has eight modules,
including `capture_study.py` even when the selected replay kind is `job`.
The public job replay contract records the six job sources plus the separate
verifier source; it does not claim an inventory of every imported but unused
module. `capture_readiness.py` and `make_capture_demo.py` belong to the coherent
ten-file package but are not executed dependencies of these producers.

Source observations identify associated on-disk files. They are not attestation
of loaded bytecode, Python/native standard-library code, a process memory image,
OS libraries, environment integrity or an historical executable. Fresh isolated
processes and frozen copies make this experiment interpretable; they do not
upgrade the public contract into code-memory authentication.

## Relocation, environment and failure boundaries

Final sources and the unchanged archive were copied again into Unicode paths.
All copied source/data file timestamps were set to epoch 1,234,567,890 before
execution. The repeated run changed `PYTHONHASHSEED` from `0` to `314159`, `TZ`
from `UTC` to `Pacific/Honolulu`, `LC_ALL` from `C.UTF-8` to `C`, and set
`SOURCE_DATE_EPOCH=1`. `PYTHONPATH` was removed for each run. The source paths,
archive paths, file timestamps and selected environment values do not enter the
canonical report: the output remains exactly the same 119,427 bytes.

A separate two-process check then changed the working directory to a second
Unicode location and used relative public input/report arguments. It reproduced
both the complete study and the complete replay summary byte for byte. Replay
read the final report saved at its original location, while re-executing the
archive at the relocated location. Source files, input bytes and saved reports
were rehashed after these checks and remained unchanged.

This checks the specified benign environment/path variations. It does not prove
invariance under arbitrary imports, locale encodings, CPUs, Python versions or
hostile concurrent mutation. The four declared runtime fields remain part of
report identity; a differing runtime is not stripped to force replay success.
The constructed acquisition timestamp `2000-01-01T00:00:00Z` remains original
fixture metadata, not the audit execution time. No current execution path or
clock value was substituted into the report.

An intentionally compact JSON copy of the final report is rejected with exit
1, no stdout summary, and `saved report: original bytes must be exact canonical
JSON`. The original canonical report remains intact. The five source mismatches
and this canonical-admission rejection are expected retained outcomes, not
failures concealed by the passing audit count.

The first audit harness attempt did fail before launching any project CLI: it
mistakenly equated each retained report with its row's `original_report` field.
In the allocation artifact, `after.original_report` intentionally names the
older pre-allocation report; `after.fresh_report` names the newer allocation
report. The harness was corrected to verify those two meanings. No expected
digest or project artifact changed. The first source hash, failed assertion and
minimal harness correction are retained in the assignment record.

## Executable operator examples

Use a coherent checkout or installed package, an unchanged complete archive,
Python 3.10 or newer and a fresh output directory. Record the source/runtime
identity for each new execution. For this exact historical source, the public
mapping is `5e19022c8696023bb1aa841ebea2eaeec0d719a3`; root subsequently verified
its reachable publication as recorded above. Fetch and verify ancestry in the
operator's own checkout before using that historical pin:

```sh
git fetch origin
git merge-base --is-ancestor 5e19022c8696023bb1aa841ebea2eaeec0d719a3 origin/main
git show --no-patch --format='%H %T' 5e19022c8696023bb1aa841ebea2eaeec0d719a3
```

The tree printed for that exact pin must be
`3edea0838b75feb06c19e151ec8539e80646fc03`. A later documentation/integration
commit may have a different whole tree while preserving these tool bytes; name
the source you actually use. The following Python example runs from the
repository root after that reachability check. It verifies the ten current
source files against the pin, creates new output paths, reconstructs the retained
allocation report separately, runs the new study and checks both replay cases.
It handles the expected engineering exit 1 explicitly.

```python
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

repo = Path.cwd()
pin = '5e19022c8696023bb1aa841ebea2eaeec0d719a3'
modules = ('capture_audio.py', 'capture_common.py', 'capture_corpus.py',
           'capture_job.py', 'capture_readiness.py', 'capture_study.py',
           'compare_capture.py', 'make_capture_demo.py',
           'validate_capture.py', 'verify_capture_report.py')
for name in modules:
    exact = subprocess.check_output(['git', 'show', pin + ':tools/' + name])
    assert (repo / 'tools' / name).read_bytes() == exact

out = Path(tempfile.mkdtemp(prefix='hammond-report-identity-'))
artifact_bytes = (repo / 'examples/benchmarks/capture-toolchain-v1/'
                  'allocation_comparison.json').read_bytes()
assert hashlib.sha256(artifact_bytes).hexdigest() == (
    '791c6c7a2433cec83097e8f5f19d66838dd3c9441417fc32c598a902722fadbc')
item = json.loads(artifact_bytes)['retained_reports']['after']
old_bytes = (json.dumps(item['value'], sort_keys=True, indent=2,
                       ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
assert len(old_bytes) == item['identity']['size_bytes']
assert hashlib.sha256(old_bytes).hexdigest() == item['identity']['sha256']
old = out / 'original-allocation-study.json'
with old.open('xb') as stream:
    stream.write(old_bytes)

def run(module, arguments, expected_exit):
    process = subprocess.run([sys.executable, '-B', '-S',
        str(repo / 'tools' / module), *map(str, arguments)], capture_output=True)
    assert process.returncode == expected_exit, process.stderr.decode()
    return json.loads(process.stdout)

input_path = repo / 'examples/capture-demo/study.json'
fresh = out / 'new-study.json'
study = run('capture_study.py', ['--input', input_path, '--output', fresh], 1)
assert study['status'] == 'failed'
own = run('verify_capture_report.py', ['--kind', 'study', '--input', input_path,
          '--report', fresh, '--output', out / 'own-replay.json'], 0)
old_replay = run('verify_capture_report.py', ['--kind', 'study', '--input', input_path,
                '--report', old, '--output', out / 'old-replay.json'], 1)
assert own['status'] == 'match' and own['exact_report_match'] is True
assert old_replay['status'] == 'mismatch'
assert old_replay['context']['same_tool_sources'] is False
assert old.read_bytes() == old_bytes
print(out)
print(json.dumps(old_replay['context'], sort_keys=True, indent=2))
```

Do not assume the historical `b1446...` report digest on another runtime. The
new report's own replay should still match with quiescent identical inputs,
sources and runtime. The older report may differ in both runtime and sources;
read the actual context flags. The public example's GitHub reachability gate was
not executed by this worker; the equivalent producer/replay commands were
executed against the verified local source copies described above.

Preserve every original saved report and create a new report for a changed
source. A canonical replay match confirms this rerun's complete artifact
equality. It does not certify that an old report was historically generated by
its claimed source, prove permissions or calibration, or close an M8 physical
gate. A rejected run has no usable verification summary. A completed mismatch
has a complete summary and remains a mismatch even if this narrow audit
projection is equal.

## Integration handoff and next gate

No production defect was found. The root's separately executed final-source
106/106 Release gate is external evidence for the integrator; it is not this
worker's execution or an additional count in these 20 groups. Likewise, no
allocation benchmark, hosted runner, native build, installed-package suite,
audio device, real recording, calibration or listening experiment was run here.

The integrator should accept these two owned records, preserve the existing
canonical reports, reconcile concurrent documentation changes, and carry the
observed published commit/tree and remote ancestry into the final handoff. Future source changes require
a new exact-source report and a clear comparison with retained old evidence.
If analytical bytes change beyond the four explicitly inspected source arrays,
investigate the difference and rerun the affected acceptance gate; do not expand
the projection until it passes. Acquisition, calibrated boundaries, fixed
physical tolerances and independent held-out evidence remain separate next
inputs described by the current calibration handoff.

# Assignment 59 — completion accounting and provenance

Actual worker: **`/root/cal_w10_a59`**, logical wave **10**, assignment **59** of
`2026-11-13-calibration`, 2026-11-14 UTC. Owned only this note and
[CALIBRATION_COMPLETION_ACCOUNTING.md](../../reviews/CALIBRATION_COMPLETION_ACCOUNTING.md).

## Frozen result

One finite independent audit passed on local commit
`6242c6d46062af8f137c9233dbdad96b71922bc2`, tree
`ad96d544d40687b720752849050a5bd22a6d8f12`. Root supplied it after accepting
56 and 57; I independently resolved both IDs. The manifest contains **56 complete,
three running (55,58,59), one planned (60)**, 59 distinct declared identities and
nine complete waves. Its 27,147 bytes hash to
`19e17f3137ec0fa42c3cfa8c442fee1ae689009b03989d33146b6ca6c0429683`.

Two actual checker invocations returned expected outcomes: expected56 passes;
premature expected60 rejects observed56. There was no new full suite, native build, hosted execution, physical
measurement or historical-dispatch attestation.

Read the standing instructions, current project/session handoffs, accounting
contract, atlas consolidations, six reader coverage records and integration
evidence. Truncated required portions were reread. This is retained-record
review, not a new full PDF reading; other ledgers remain separate.

## Actual commands and independent checks

Commands ran from the repository root with CPython **3.12.14** on Linux. Scratch
`/workspace/scratch/c9f3ead4c910/a59-accounting-20261114/source` is a fresh archive
of the exact local commit above, extracted with `tarfile` and `filter='data'`.
These private paths identify this execution, not future installation prerequisites.
Root has not supplied a public equivalent for this later local documentation
checkpoint; a fresh clone must use a reachable published source and its own
actual counts rather than assume local `6242` is available.

```sh
git rev-parse 6242c6d 6242c6d^{tree}
python3 -B tools/check_calibration_session.py --repo . --expected-complete 56 --json
python3 -B tools/check_calibration_session.py --repo . --expected-complete 60 --json
```

The last two commands were executed inside the private snapshot using absolute
script/repository paths. They returned **0** and **1**, both with empty stderr.
The second reported only `expected 60 completed assignments, observed 56`.
Both retain `external_dispatch_attested: false`; the negative probe was never
represented as a passing final gate.

The separate command was:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a59-accounting-20261114/audit.py
```

It imports no checker API. It independently checks constants, exact IDs/wave
math/states, per-row agent/note identity, completed-file bounds and regular types,
every path component's lack of symlink/traversal, other-ledger intersections,
coverage union/images, PDF identity/page count, Git-tree equality and ancestry,
and exact source-diff scope. Before/after inventories reconstruct all committed
blob IDs from actual extracted bytes and verify the complete path set.

| Actual observation | Result |
| --- | --- |
| Extracted tree | 1,031 files / 40,554,346 bytes, exact and unchanged |
| Complete notes | 56 / 968,658 bytes, correct identity/encoding/length |
| Completed ownership | 164 references / 153 distinct regular paths |
| Sequentially reused source paths | Eight paths / eleven extra references, no extra workers |
| Separate manifests | Five inspected, zero identity intersections |
| Reader coverage | Six contiguous ranges 1–500; 31 distinct declared images within their ranges |
| Actual PDF | `pdfinfo`: 500 pages; 21,248,265 bytes; original hash unchanged |
| Git mappings / ancestry | Four equal-tree pairs / five d7 ancestry checks |
| Diff scopes | 40 document/record paths full→d7; 15 document/record paths d7→6242 |
| CaptureTools / checker | All 21 copied documents and checker/regression source unchanged after d7 |

Sequential repeated paths are audio (13,47), corpus (14,25,43,47), job (25,31,47),
readiness (27,47), study (31,47), comparison (15,20), generator (33,47), verifier (35,47).
Their historical evidence retains original sources; a current path's existence
does not imply every earlier report tested today's bytes.

## Reproduce the core count gate

At a checkout containing the exact historical manifest, these read-only checks
reproduce its count gate. For final closure, use the final actual count instead.
The full independent audit additionally checks all path components, blobs and
coverage/source relationships described above.

```python
import collections
import hashlib
import json
from pathlib import Path

p = Path('docs/development/2026-11-13-calibration/assignments.json')
b = p.read_bytes()
assert hashlib.sha256(b).hexdigest() == (
    '19e17f3137ec0fa42c3cfa8c442fee1ae689009b03989d33146b6ca6c0429683')
a = json.loads(b)['assignments']
assert [r['assignment'] for r in a] == list(range(1, 61))
assert all(r['wave'] == (r['assignment'] - 1) // 6 + 1 for r in a)
assert collections.Counter(r['state'] for r in a) == {
    'complete': 56, 'running': 3, 'planned': 1}
ids = [r['agent'] for r in a if r['state'] != 'planned']
assert len(ids) == len(set(ids)) == 59
```

## Retained identities and limits

| Private artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `audit.py` | 8,313 | `9ed5522899ee58d8025c4487dfb6fa2b3e9f8aa2b14199db7c74e8acfc55ceb8` |
| `result.json` | 7,997 | `c807d9dd201152bc14c4b395fe4a3e95c128e03a65f08206d393ef7084266aef` |
| `checker-56.stdout.json` | 462 | `de78ed086a966e6524fe3f3c96434f98cad198f5cbc24ef2d822f36b306c7bad` |
| `checker-60.stdout.json` | 510 | `b40c1a6acb068ded3c4c05be91d61652868433422b43e7a8897f49daa15562a8` |
| `source-inventory.json` | 201,259 | `15dcf60b10530e479ace38819fb32fe6889b632e2a8d8456232a5e0073d37034` |

I separately read root's existing JUnit: 52,305 bytes, SHA-256
`9a12a066e312c62dde559cb372afbd4e9a96183c97a4309d7d8d07b16714b27d`,
106 cases, no failure/error/skipped elements. This is inspection, not a new run.
The review preserves each historical manifest's distinct accepted/dispatched counts.

No accounting/provenance defect or harness repair was found. I reported two stale
README composition/readiness pointers; root reported correcting both. Known 54
headline counts also await final integrator reconciliation. These observations
remain distinct from the unchanged frozen snapshot.

Root later reported all ten d7 hosted jobs successful and assignment 58's finite runtime
checks passing. Their own retained records and root acceptance own those claims;
this note does not promote pending rows. Root must accept this audit, finish the
actual final worker, retain the sixty-complete gate, reconcile current handoffs,
then publish with an inspected expected-head/non-force guard and verify fetched
commit/tree. Preserve the PDF, historical reports, other ledgers and physical
unknowns. No staging, commit, ref, source/guide/shared-file edit was performed here.

Final document QA removed a trailing space introduced while condensing the draft;
the Python example compiles and all seven relative links across both records resolve.

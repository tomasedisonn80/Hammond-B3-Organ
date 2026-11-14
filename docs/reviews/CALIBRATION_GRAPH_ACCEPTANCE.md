# Independent corpus graph scale and permutation acceptance

Assignment **45**, actual agent `/root/cal_w8_a45`, logical wave **8** of the
`2026-11-13-calibration` session. This review adds independently authored
[graph acceptance](../../tests/test_capture_graph_scale.py) against the unchanged
[corpus contract](../CAPTURE_CORPUS_CONTRACT.md). It changes no producer or contract.

## Result and scope

The final frozen five-file source passes **7/7 unittest methods in 5.168 seconds**
with zero failures, errors or skips under `python3 -B -S`. Its four producer
modules and test file remain byte-identical before and after execution and match
the live owned/dependency files at the final check. The ordinary corrected live
run passed the same seven methods in 4.984 seconds. These elapsed times describe
test execution on a shared Linux runner; they are not performance thresholds.

The methods complete **43 real public audits** with exact independent expected
graphs, findings and original-byte identities, plus **five intentional public
rejections** that must precede manifest work. Completed reports retain their
engineering outcomes: 42 are `failed` and one is `inconclusive`. An expected
leakage result is a passing acceptance assertion, not a passing corpus. The
mixed fixtures also require exact `pass`, `failed` and `inconclusive` component
statuses where applicable. All seven physical/evidence claims remain
`not_established` in every complete report.

The existing independent corpus suite already covers ordinary small graphs,
two-node reason examples and 32-node stars. Admission already covers 512 planned
manifests. This addition qualifies 512 **recorded synthetic captures with actual
tiny artifacts and audio inspections**, dense overlapping reasons, deep ancestry,
the full reason/purpose-pair matrix, disconnected mixed graphs, and distinct
index versus manifest-byte permutations. Existing malformed-input, filesystem
fault and broad audio-format suites remain separate evidence.

## Independent oracle

Fixtures are literal dictionaries and independently packed little-endian float32
or ordinary IEEE-float RIFF bytes. They import no fixture generator, decoder,
producer graph helper or other acceptance helper. Every sample is an exactly
representable binary fraction. Expected decoded identities hash the contract's
literal prefix, `<IIQ` geometry and binary64 sample preimage, with signed zero
canonicalized explicitly.

The oracle examines every pair of capture identities, compares their declared
session/group/label tokens and independently calculated raw/derived content
identities, and builds an equality **clique** adjacency relation. It adds both
connectivity directions for every declared child-to-parent relation, then
computes components through breadth-first reachability. The production graph
uses disjoint sets and equality stars; the oracle does not call those helpers or
derive its expected groups from the producer's output.

Expected returned stars are a separate projection of the full pair witnesses:
retain an equality pair when its left endpoint is the smallest capture carrying
that exact reason/value token, and use the smallest participating file ID within
each capture. Parent direction and every distinct reason are preserved.
Component purposes, failures, planned/unassigned/omitted-audio findings and
sorting are derived from the fixture specifications. Exact equality is required
for the complete returned `edges`, `groups`, `findings` and `status` values.

Each complete audit also compares its exact index-byte SHA-256, expected/observed
manifest identities, every artifact's expected and observed hashes/byte counts,
every selected decoded identity, retained synthetic status, and all physical
claim fields. Before/after hashes of every input file must remain identical.
The only producer-private hook used by the suite is `_load_manifests`, replaced
with a reached-work sentinel during the five intentional admission failures; it
is never used to produce an oracle or a valid result.

## Executed case matrix

| Method | Complete public audits | Expected public rejects | Distinct acceptance obligation |
| --- | ---: | ---: | --- |
| Dense 512-record graph and 513 preflight | 1 | 3 | All actual files/audio, exact dense stars and multi-parent DAG; one extra entry rejects before any manifest work in all three modes. |
| Seeded mixed graphs | 12 | 0 | Four fixed seeds (`0`, `1`, `17`, `65537`) in each of the three modes; each archive has 50 captures, seven components and preserved incomplete evidence. |
| Index permutations | 5 | 0 | One original plus four fixed shuffles of capture, relation, parent and descriptor arrays; five distinct original index hashes with every other report field equal. |
| Manifest file permutation | 2 | 0 | Twelve recorded captures, each with raw, two derived and support files; new original manifest/index identities but otherwise identical complete reports. |
| Deep 512-record ancestry | 1 | 2 | Exact 511-edge chain and transitive purpose leakage; a full 512-node directed cycle rejects before manifest work in original and reversed index order. |
| Seven reasons × three known-purpose pairs | 21 | 0 | Each reason alone connects a three-capture fixture across each pair of `fit`, `validation`, `final`, retaining the middle unassigned finding. |
| Shared support and pending singletons | 1 | 0 | 64 independently recorded tiny streams plus two plans remain 66 singletons despite shared support bytes and author/variant metadata. |
| **Total** | **43** | **5** | Seven unittest methods; no skipped platform subcases. |

The 43 complete audits comprise 20 structural, seven file-checked and 16
file-and-audio-checked runs. Every fixture is created in a fresh private temporary
directory; these are test-authored data, not acquired corpus evidence.

### Dense recorded boundary

All 512 captures have one independently stored raw, derived and support artifact:
**1,536 actual 16-byte files, 24,576 aggregate artifact bytes**. The two selected
streams per capture produce **1,024 actual audio inspections**, with 16,384
selected audio bytes. Support has the same bytes but is never a content witness
or selected stream. Both content reasons must choose derived file `alpha`, not
the later raw ID `zraw`, as the lexical witness.

Each capture shares a session, v1 group, eight gesture labels and eight family
labels. Capture `cNNN` names up to its previous 16 captures as parents, forming
an acyclic overlapping ancestry graph with 8,056 declared edges. Exact returned
edge counts are:

| Reason | Expected and observed count |
| --- | ---: |
| `session_id` | 511 |
| `v1_group_id` | 511 |
| `gesture_label` | 4,088 |
| `family_label` | 4,088 |
| `artifact_sha256` | 511 |
| `decoded_audio_sha256` | 511 |
| `parent_capture` | 8,056 |
| **Total** | **18,276** |

All captures belong to component `c000`. Purposes cycle through all four tokens,
so the report preserves one `cross_purpose_component` finding and 128 separate
`unassigned_capture` findings: **129 findings**, overall `failed`. The equality
witnesses remain linear per bucket even though the independent oracle expands
the underlying pairwise relationships. This checks the prescribed output, not a
general producer time/memory bound or an internal complexity proof.

The following 513th index entry has a unique ID, path and hash and names an
unwritten manifest. The count bound must reject in all three modes before the
manifest loader is reached. No production limit is patched, no artifact count
is truncated, and no success report is returned for an excess.

### Permutations and incomplete evidence

Index-only shuffling changes original index bytes and their retained SHA-256;
the complete remaining report must remain identical. Reversing actual manifest
file arrays changes each manifest's original bytes, its expected and observed
identity, and the binding index identity. The separate manifest-order test
requires those changes first, then compares all remaining fields exactly. It
does not erase those identities in a saved report or claim the archives have
identical original bytes.

Four seeded mixed archives retain all relationship reasons, raw/WAV wrapper
differences, cross-block ancestry, shared support, explicitly described and
omitted derived audio, and two unrelated plans. Each audio-mode result remains
partial, with six omitted-derived findings. File and structural modes do not
invent decoded identities. Mixed-purpose components fail even while other
groups remain pass/inconclusive; unrelated plans cannot resolve a known-purpose
conflict.

The 21 isolated-reason cases prevent dense overlap from concealing a missing
relationship implementation. Raw/derived byte equality is tested in file mode;
decoded-only equality uses deliberately different RIFF wrapper bytes and actual
audio mode. The five declaration reasons have distinct raw bytes. No second
reason silently supplies connectivity for these cases.

## Source and environment identity

The assignment began at local commit
`16d72e1b351e5cdf1730e90645a6ea37144d1be7`, tree
`5619bbb018830e071bc2ce45af84984cdd16bfc1`. That commit does not contain this new
test or assignment 43's metadata allocation change. Acceptance therefore binds
the following **actual copied files**, not an unqualified claim about the whole
starting commit or later integration commit.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `tests/test_capture_graph_scale.py` | 30,384 | `f85b0d233e36d84e7d63c61b682fb649acef77d11c7d0bf7557aa9e8495ad1b6` |
| `tools/capture_corpus.py` | 39,312 | `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded` |
| `tools/capture_audio.py` | 29,951 | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

The frozen corpus contract is 31,880 bytes, SHA-256
`a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2`.
The five-file copy was made at `2026-11-14T00:38:31.236194+00:00` into
`/workspace/scratch/c9f3ead4c910/a45-frozen-source`. The final run used CPython
3.12.14 (`Clang 22.1.3`), Linux `6.18.57`, x86_64, glibc 2.41. No third-party
dependency, installed site package, C++ build, native audio device or network
access is involved in execution.

From a checkout containing the listed files:

```sh
python3 -B -S tests/test_capture_graph_scale.py -v
```

The exact frozen command used that private five-file directory as the working
directory, with stdout/stderr retained at `a45-frozen-run.log`. Its 1,171-byte log
has SHA-256 `43ef8897160e8dcd09de2990a5eb72b013f3b203575aec649f104010b7ff7919`.

## Retained authoring failures

The first run completed seven methods in 1.841 seconds and exited 1 with
**38 unittest errors**: 37 attempted scenarios correctly rejected a nonnull
synthetic specimen ID authored by this test, and the dense scenario correctly
rejected a 1,079,809-byte pretty-printed index above the existing 1,048,576-byte
limit. No graph defect or producer crash was found.

Only fixture authoring changed: synthetic `specimen_id` became an explicit
unknown, as required by unchanged capture v1; index serialization became compact
JSON with exact original-byte hashing retained. The 512 captures, 16 labels,
8,056 parents, audio files, expected graph, limits and assertions were preserved.
The second run passed all seven methods. The
[assignment note](../development/2026-11-13-calibration/45-corpus-graph.md)
retains original source/log identities and the two original blocks needed to
reproduce the initial fixture errors.

## Limits and integration handoff

This is bounded graph correctness evidence on tiny synthetic streams. It does
not qualify the maximum 2 GiB artifact budget, maximum 256 MiB selected audio,
maximum returned graph/finding count, hostile concurrent filesystem behavior,
RSS, runtime deadline, native Windows/macOS execution or physical independence.
The 16-label dense case is within the 32-label declaration limit; the 8,056-parent
case is within the 8,192 total limit. No claim is made that these are maximum
reachable combinations of all resource limits.

No producer repair, new dependency, contract revision or package inventory
change is required. The integrator should review and accept the three owned
files, include the new suite in the next coherent source gate, and retain the
actual integrated tree and hosted outcomes separately. Assignment 44 owns
independent qualification of the metadata allocation change; this graph result
does not replace its byte-read, source-context or failure-cleanup acceptance.
Future physical studies still require declared acquisition ancestry, split
history, calibration, specimen evidence and predeclared policies beyond any
clean software graph.

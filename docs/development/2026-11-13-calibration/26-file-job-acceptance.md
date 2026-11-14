# Assignment 26 — independent file-job acceptance

**Result:** accepted at the exact source identities below. The final direct
execution passed **81 unittest methods, with zero failures, errors or skips**.
No production defect was observed by this assignment. This qualifies the stated
offline engineering behavior on the observed Linux/Python runtime; it does not
qualify hardware fidelity, a native host or an adversarial filesystem.

Actual identity: **`/root/cal_w5_a26`**, calibration session wave 5,
2026-11-13. This is one newly dispatched assignment. It does not recount an
earlier corpus worker or the six atlas readers.

## Ownership and source basis

This assignment wrote only:

- `tests/test_capture_job.py`
- `docs/development/2026-11-13-calibration/26-file-job-acceptance.md`

The entire revised `docs/CAPTURE_JOB_CONTRACT.md` and independent
`docs/CAPTURE_JOB_REVIEW.md` were read before qualification. The cleared contract
is the acceptance authority. Assignment 25 owns implementation and its private
shared corpus core; root owns CMake, shared status, accounting and publication.
No production module, schema, shared progress file or Git state was changed by
this worker. The temporarily absent API was treated as planned work. Tests were
executed only after producer 25 and root explicitly reported API readiness.

The test archive author reuses assignment 17's independent `_Archive` and
literal WAV builder from `tests/test_capture_corpus.py`. It imports that module
as a module, so its TestCase classes are not recounted by this suite. Expected
raw bytes, canonical decoded preimages, hashes, metrics, intervals, roles,
context, status precedence and exact report keys are independently declared in
the new test. Production validators, decoders or metric helpers do not generate
the expected numerical results. Observing a real subordinate return value is
used only to verify that the wrapper preserves it unchanged.

The project source basis remains the already retained fresh 500-page atlas
review and its unchanged PDF. This assignment did not claim another complete
PDF reading or independent verification of the atlas's underlying documents.

## Exact qualified identities

All six implementation source hashes below were observed before the expanded
acceptance run and after the final run, with no change. Hashes identify the
actual bytes tested, including uncommitted implementation files, rather than
claiming that an earlier committed tree contains them.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/capture_job.py` | 23,438 | `3ffe39f5723a6a3af779ba33b799e72bdeed9d60365c5df9a8146b8467aec230` |
| `tools/capture_corpus.py` | 38,632 | `adb44d8838bf112e97bd884587dd74fe2dbf8167197622b4ba40453c004d33c7` |
| `tools/capture_audio.py` | 29,367 | `c02c1a5e6023e0278dddca09ad1841541fbb0ece66d7950198f93be7846dc7ac` |
| `tools/capture_common.py` | 9,625 | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/validate_capture.py` | 24,827 | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `tests/test_capture_job.py` | 78,586 | `ad45f0e3279699072b0448a791bb624494570ac3b2b5be2c6d805d9e4a3e2cf6` |
| Independent archive fixture, `tests/test_capture_corpus.py` | 52,143 | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |
| Cleared job contract | 29,508 | `ed0b34cbd45d737ea35b33d3049d1b8884f8f665d4f42caeb1e1406466217b84` |
| Independent job contract review | 13,719 | `9218ca2e0fd72ff07ff1b838cac2dd153ce8e5b1ece18e20cbcc24d3b2c2f271` |

The observed checkout HEAD after the final test was
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, with committed tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`. That observation is context, not a
claim that this dirty worktree or the full future integration tree was qualified
by its committed identity. Root must retain the eventual coherent integration
and publication identities separately.

## Executed command and results

Working directory:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`

```sh
python3 -B tests/test_capture_job.py
```

Observed runtime: Python **3.12.14**, implementation `cpython`, platform `linux`,
machine `x86_64`; Python build reports Clang 22.1.3. No third-party package,
network service, hardware recording or dependency installation is required.
The test uses temporary, independently authored archives and copied source
files. Production repository sources are never temporarily modified for fault
injection.

| Executed stage | Methods | Failures/errors | Skips | Reported duration |
| --- | ---: | ---: | ---: | ---: |
| Initial independently authored archive/API/CLI suite | 50 | 0 | 0 | 4.091 s |
| Added source/input mutations, core binding and publication faults | 78 | 0 | 0 | 4.375 s |
| Complete suite before isolated duplicate-key fixture refinement | 81 | 0 | 0 | 4.910 s |
| Final complete retained suite | **81** | **0** | **0** | **4.698 s** |

These are successive development executions, not distinct acceptance methods
to be added together. The final file contains and directly executes 81 methods;
many contain explicit subcases. The last refinement makes duplicate-key byte
fixtures otherwise fully valid, so rejection cannot be explained by an
unrelated shape error. No fabricated subcase total is claimed. All tests passed
on their first execution at each stated stage; no failing requirement was
relaxed to obtain a pass.

Producer 25 separately reported preservation of the existing 47-method corpus
suite and 57-method corpus-admission suite after the shared-core refactor. Those
are producer/root evidence, not additional executions or tests counted by this
assignment. Root remains responsible for the coherent combined acceptance gate.

## What the final suite establishes

### Literal windows, complete audio and numerical outcomes

The three contract vectors use explicit 16-byte float32 streams. All six
printed raw/decoded hashes are recomputed from independently assembled
preimages and checked against the contract and actual job observations. The
literal quarter-offset bias, RMS error and maximum error equal `0.25`; the
tests verify pass `[0.125, 0.375]`, inconclusive overlap, half-offset fail
`[0.375, 0.625]` and the inconclusive lower-endpoint equality case.

Different finite prefixes/suffixes and different selected start frames retain
the original bounds and complete-stream identities while preserving the
selected result. NaN and both infinities outside either selected interval
reject. Actual short streams reject oversized windows. Stereo comparison
retains every channel and its original index; captured arguments prove that
the original samples and analysis reach the comparison without transformation.
Each selected inspection preserves every actual field except `input_path`.

### Corpus scope, policy, roles and derivative meaning

Unselected duplicate bytes, decoded duplicates and declared ancestry retain
cross-purpose failures even when the selected numerical criterion passes.
Unrelated planned/unassigned records retain both inconclusive findings.
Nine real archive combinations exercise all corpus pass/failed/inconclusive
and numerical pass/fail/inconclusive combinations, with failure precedence and
both complete subordinate results preserved.

All four purpose/role mappings, mismatches, all hardware/synthetic selected
kind combinations, an unrelated hardware record, exact self-comparison and
different windows of one file are covered. A synthetic policy rejects either
hardware selection before artifact work. A digital policy does not promote any
physical claim. Missing, planned, support and undescribed derivative selections
reject. A selected stereo derivative with changed rate and format retains its
own geometry and `ancestor_raw_stream_only` context; its raw manifest's channel,
clock and calibration declarations remain raw context.

Original policy bytes are observed at evaluation, including deliberate leading
and trailing whitespace. A valid **52,946-byte compact policy** with 192 criteria
is accepted even though its independently formatted representation is
**82,673 bytes**. Its evaluation hash binds the original compact bytes.
Reformatting is never used as the expected oracle or a way around admission.

### Early admission, composition and final identity checks

Tests cover exact input keys/types, strict JSON bytes, the inclusive 65,536-byte
job limit, portable paths, IDs, hashes, numeric and interval bounds, Hann length,
sample and spectral work. Trapped artifact scanners prove rejection of invalid
policy, selected geometry/roles/kinds, work, expected hashes and manifest byte
changes before artifact work. Exactly 64 captures and exactly 256 total file
references are admitted; 65 captures reject before manifest loading and the
257th reference rejects before artifact scans. Support references and aggregate
audio/artifact bounds participate in these checks.

The selected primary composition reads each job, policy, index and manifest
once, passes the same retained parsed metadata to one shared full-audit core,
and performs two selected window reads. A changed index after admission cannot
drive new manifest or artifact work. Complete actual corpus/evaluation results
are retained without projection or truncation. Window inspection size, byte
hash, format, geometry, digest version, decoded hash and returned interval all
bind to the earlier corpus observations.

After evaluation, controlled changes to the job, index, policy, all three
selected/unselected manifest cases, both selected audio files, unselected audio
and unselected support each reject. Identical-content replacement and confined
parent replacement also reject; unrelated sibling creation is allowed. Every
one of the six temporary copied source modules rejects a late mutation.
Actual opened descriptors are released after injected filesystem failure and
cancellation, observed through Linux `/proc/self/fd`. Hardlink exclusion,
job-root/descendant symlink rejection, allowed ordinary aliases above the job
parent, nonregular leaves and nonblocking FIFO rejection remain covered.

### Report, replay and publication

Exact root/selection/inspection/runtime/source keys and byte identities are
checked. Returned copies do not alias each other or future results. Identical
archives produce identical canonical UTF-8 bytes after relocation to a Unicode
root and invocation from a foreign working directory. Runtime string limits
and source regularity/byte limits reject malformed observations. The 4,097th
returned graph edge and full-report byte/node/depth/number excess reject without
truncation, successful stdout or publication.

The CLI exercises all four exits, help, no abbreviation or implicit override,
one contextual error line, and UTF-8 output under an ASCII text wrapper. New
output files equal stdout for pass, failure and inconclusive results. Existing
files/directories/links and raced destinations remain intact. Missing output
parents are not created. Completed publication followed by temporary cleanup
failure preserves the complete report and discloses the actual failure; primary
publication plus cleanup failures retain both contexts. A short stdout write or
stdout I/O failure cannot become success, and a previously completed file
remains available. Cancellation is propagated rather than translated to success.

## Limits and next step

The real archives are synthetic engineering fixtures. Their acquisition dates,
operators, kinds, rights and physical context are declarations generated solely
for tests. Every physical/provenance claim remains `not_established`. Passing
this suite cannot establish specimen identity, independent capture history,
preregistration, calibration, acquisition permission, listening acceptance or
instrument fidelity.

Controlled dependency faults and filesystem changes are reproducible acceptance
injections, not a hostile-filesystem proof. `/proc` descriptor inventory was
executed on Linux. Native Windows reparse behavior, macOS/Windows filesystem
behavior and native host/platform qualification were not executed here. The
suite retains platform-dependent skips where a future runner lacks symlinks,
hardlinks, FIFO creation or `/proc`; there were no such skips on this runner.
Cross-platform floating-point byte identity is not claimed.

No unresolved production defect was found. Root should integrate the completed
job implementation, this suite and their documentation; register the required
CTest entry, run the existing corpus and relevant capture suites from one
coherent source snapshot, then record actual commit/tree and authorized push
results. Subsequent replay/study work should consume the complete bound report
and preserve original job/index/manifests/policy/audio bytes. It must retain the
same admission limits and evidence boundaries, and must not convert parsed
report copies into fabricated original files or physical qualification.

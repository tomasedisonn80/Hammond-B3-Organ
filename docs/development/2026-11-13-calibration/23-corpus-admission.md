# Assignment 23: corpus admission, resources and filesystem failures

## Assignment and ownership

Actual identity: `/root/cal_w4_a23`. This is assignment 23 of wave 4 in the
2026-11-13 calibration session, conducted on 2026-11-13. This worker owns only
`tests/test_capture_corpus_admission.py` and this evidence note. The integrating
agent owns production repairs, shared status, CMake, Git publication and session
accounting. This worker made no production, CMake, shared-document or Git changes.

Working directory for every command below:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.

The acceptance basis is [the frozen corpus contract](../../CAPTURE_CORPUS_CONTRACT.md),
[calibration scope](../../CALIBRATION_SCOPE.md) and the repository's standing
`AGENTS.md` instructions. The corpus contract was read in full. This work extends
assignment 17's independently authored graph/report acceptance with admission,
resource, filesystem, descriptor and failure-preservation checks. It introduces
no acquisition claim or change to the v1 capture contract.

## Source identities

Initial observed checkout: commit
`8864c051d19556e37dffcd7366fd859606958bc3`, tree
`e4f56a7c722dcad4eda9269d907715b8526dd8cd`. The integrator advanced the checkout
during this work. The final verification observation identified commit
`091ad20c632209053c337a06544f82a829644800`, tree
`8679418135946193b2b989a89e60ac6099b00125`.
These commits identify the concurrent checkout, not all uncommitted test inputs;
the exact relevant bytes below identify the accepted implementation. The locally
recorded `origin/main` was `5b8e2419d23fe27c51709d717812060eafd44dcc` at both
observations. This worker did not fetch or verify a remote publication.

| File | Accepted SHA-256 |
| --- | --- |
| `tools/capture_corpus.py` | `ba39a47499df0df837b71d744f773bfbefe14d0eb1a0c471a373900b6c284e7b` |
| `tools/capture_audio.py` | `c02c1a5e6023e0278dddca09ad1841541fbb0ece66d7950198f93be7846dc7ac` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `docs/CAPTURE_CORPUS_CONTRACT.md` | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| `tests/test_capture_corpus.py` | `a6b688b19e4fdd60d744c9f5b32cf03e526b3ae187b8ac0b91624e0a95b8ed9c` |
| `tests/test_capture_corpus_admission.py` | `6d7e0984fb20e0265f53e6ee3df3bb9958ca1440573bac9ed25a7b44bb819a19` |

The originally examined corpus producer was
`68c710c8afdb2985446ef25b4d0ed7d690970dc8be33535facf0a5ee1747adbe`.
The original audio producer was
`967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2`.
The integrator repaired corpus descriptor ownership after this worker's report.
The audio hash also changed through the separate assignment-24 finding concerning
earliest format-byte error precedence. This worker did not author either repair.
The accepted producer, common-code, contract and fixture hashes remained unchanged
through the final admission and existing-corpus suite runs.

## Independent method

The new suite uses Python's standard-library `unittest`, temporary directories,
real small files, native filesystem operations and explicit injected failures.
It reuses only assignment 17's separately authored `_Archive` fixture writer and
`_json_bytes` serializer. It does not call producer validators or private helpers
to calculate expected acceptance, identities, digests or resource totals.
Fixture byte hashes use an independent `hashlib.sha256` calculation, value nodes
use an independent stack traversal, and admission boundaries are literal contract
values in the tests.

Filesystem instrumentation keeps real `os.open`, `os.close`, `os.fdopen`, reads
and identity observations underneath the hooks. The open observer preserves
the POSIX directory-descriptor capability when `os.open` is replaced. Descriptor
assertions use real `fstat` after fault hooks have been removed where necessary;
an injected `fstat` failure cannot masquerade as a correctly closed descriptor.
The harness independently cleans any descriptor left live by a failed regression
so one case cannot contaminate the next.

The suite contains 57 test methods with additional independent subcases. Counts
below refer to methods, not assertions or injected faults.

## Defect found, reported and repaired

The original producer leaked a leaf descriptor when closing the directory
descriptor failed after opening that leaf. Its `_open_confined` returned the
result of the leaf `os.open` inside a `try`, then closed the parent in `finally`.
An exception from that close discarded the pending return value and left the
leaf descriptor without an owner. The same ownership ordering could lose an
opened child directory when closing its predecessor failed before assigning the
child as the current descriptor.

The minimal observed reproduction used an ordinary planned corpus index on POSIX
and replaced `os.close` with a wrapper that performed the real first close, then
raised `OSError("injected directory close failure after actual close")`.
`load_corpus` raised the contextual `CorpusError` but the opened index descriptor
remained live. The probe observed extra descriptor 4 through `/proc/self/fd` and
closed it independently after recording the defect. The failure was sent to the
integrator immediately; this worker did not modify production code.

The integrator's repair transfers child ownership before closing the predecessor,
retains leaf ownership until the final parent close succeeds, and cleans the
still-owned resource on ordinary failure or cancellation. Cleanup failure retains
the primary reason, and cancellation retains its original `KeyboardInterrupt`
type. The retained regressions are:

- `test_parent_close_failure_after_leaf_open_releases_leaf_regression`;
- `test_predecessor_close_failure_releases_new_child_regression`;
- `test_fdopen_primary_and_cleanup_failure_keep_both_reasons`;
- `test_fdopen_cancellation_survives_cleanup_error`.

These and all remaining admission methods pass against the accepted corpus hash.
No additional producer defect was found during this assignment.

The injected close failures deliberately occur **after the real close**. This
establishes ownership of newly opened resources when an older close reports an
error. It does not prove a portable outcome for an OS close error that leaves the
descriptor's release state ambiguous. The producer deliberately does not retry
such an ambiguous close, because the number may already have been reused.

## Coverage and actual boundary execution

| Area | Executed evidence |
| --- | --- |
| Strict JSON | Invalid UTF-8, BOM, duplicate keys at each index object level, trailing documents, `NaN`/infinities, overflow, escaped surrogates and forbidden controls reject. Malformed manifest bytes are hashed exactly as declared before their strict parse is tested. |
| Numeric and direct API guards | More than 64 numeric-token characters reject; a 64-character token reaches later schema rejection. Excess generic magnitude, non-JSON objects and container/scalar subclasses, boolean/float schema versions, unsafe keys, cycles and excess nesting reject. Depth 16 reaches schema validation, while depth 17 rejects at the nesting guard. |
| Index byte limit | A real 1,048,576-byte valid index, padded with JSON whitespace, loads. One additional byte rejects before any index descriptor opens. |
| Value nodes | An independently counted valid direct-API index with exactly 65,536 value nodes is admitted; one added parent reference makes 65,537 and rejects. Object keys are excluded. This direct-API case is not a claim that its serialization fits the index byte limit. |
| Capture and field counts | A real index and audit of 512 planned manifests complete with 512 groups and 512 planned findings. A 513th index entry rejects. Inclusive and excess relation-label, parent-reference and derived-descriptor counts are checked. |
| Individual manifest bytes | A real 65,536-byte valid manifest loads; 65,537 bytes reject before opening the manifest. |
| Aggregate manifest bytes | A real audit reads 256 distinct manifests of 65,536 bytes each, exactly 16,777,216 bytes. A further manifest rejects before its descriptor opens. |
| Declared artifact budget | Eight 268,435,456-byte declarations admit exactly 2,147,483,648 declared bytes in structural mode. A further one-byte declaration rejects before artifact access. Nine references to one repeated locator still exceed the aggregate. These are declaration tests; no 2 GiB artifact scan was run. |
| Selected-audio budget | Tiny real WAV fixtures and a deliberately lowered audio-budget constant exercise inclusive admission and excess rejection. Repeated references count separately, selected derivatives count, support and omitted derivatives do not enter this audio total. Failure occurs before any artifact open or decoder call. The production 256 MiB audio maximum was not fully scanned. |
| All-artifact budget | Tiny real raw, support and omitted-derived files with a lowered aggregate constant prove every declared artifact contributes. An individually oversized declaration and 33-file manifest reject before artifact access. |
| Graph and finding caps | Small real graphs with lowered caps prove inclusive complete output and excess rejection rather than truncation. The full production edge and finding maxima were not generated. |
| Portable paths | Empty, dot/dot-dot, absolute, drive, UNC, backslash, doubled separator, reserved device name, non-ASCII, control, trailing-dot and overlong path forms reject. Inclusive 64-character components, eight components and 240 total characters admit. |
| Links and special files | Native root/index/manifest/artifact symlinks, intermediate-directory aliases, dangling links, directory leaves and FIFO leaves reject. An alias above the selected root is allowed initially; retargeting it during the index read rejects. Synthetic reparse metadata rejects at each confined level and on the opened artifact. |
| Hardlink policy and identities | Native aliases within one manifest reject for raw/derived and raw/support pairs. Cross-capture hardlinks remain valid and group by artifact digest. A usable path or descriptor identity supplies fallback; zero device number with a useful inode works; both absent identities, mismatched identity and reparse metadata reject. |
| I/O and ownership | Missing paths, invalid input path types, unavailable current directory, open, `lstat`, `fstat`, `fdopen`, read and stream-close failures produce contextual rejection and release acquired descriptors. `KeyboardInterrupt` during wrapping or reading retains cancellation and closes resources. |
| Mutation | Short metadata reads, appended bytes, in-place index/manifest/artifact changes, leaf replacement, an intermediate directory replaced by an alias, selected-root replacement and above-root ancestor retargeting reject. Creating an unrelated sibling is admitted. |
| Bounded scan and reinspection | A real 153,600-byte artifact is consumed through requests of at most 65,536 bytes and its full observed digest matches the independent hash. An audio-inspector observation different from the verified bytes rejects. |
| Failure preservation | The CLI rejects a corrupted raw file with exit 1, contextual stderr and no report on stdout. A complete before/after snapshot of all work-directory paths and file bytes, including a pre-existing report sentinel, is identical. |

All native symlink, hardlink, FIFO, descriptor and replacement cases executed on
this Linux runner. Zero tests skipped. On another platform, unavailable native
capabilities produce explicit `unittest` skips with their reason; they must remain
visible in that platform's retained result. Controlled reparse metadata is useful
branch evidence, but it is not execution of Windows junctions or native reparse
points. The suite does not claim native Windows or macOS qualification.

## Verification

Runtime: Python `3.12.14`, built with Clang `22.1.3`; platform reported
`Linux-6.18.57-x86_64-with-glibc2.41`.

```sh
python3 -B tests/test_capture_corpus_admission.py
python3 -B tests/test_capture_corpus.py
```

The final direct admission command ran **57 tests in 1.461 seconds: OK**, with
zero failures, errors or skips. The existing assignment-17 corpus suite ran
**47 tests in 0.985 seconds: OK**, with zero failures, errors or skips. An earlier
57-method verbose admission run also passed in 1.468 seconds; the final run adds
the broader work-directory/sentinel-output preservation assertion without changing
the method count. The initial 55-method suite passed in 1.338 seconds before the
explicit ancestor-retarget and stat-failure methods were added.

The original standalone descriptor probe's failure is retained above; it is not
erased by the passing repair verification. Tests import production directly and
exercise the CLI in a fresh subprocess for the failure-preservation case.
No optional third-party dependency, network service, hardware or audio device is
needed. Temporary fixture files are removed through `TemporaryDirectory` cleanup.

## Next action and limits

The integrator should accept these two owned files, register the admission suite
in the project test entry point, update shared handoff and session accounting,
then publish through the standing guarded Git workflow. Publication is not an
assertion made by this note.

Assignment 25 may subsequently share the internal corpus audit core. Its input is
the exact accepted contract and source behavior above. After any such refactor,
rerun both commands against the final producer/common/audio hashes, retain any
native capability skips, and independently check that descriptor ownership,
aggregate preflight ordering, repeated-reference accounting, byte identity and
failure preservation remain unchanged. Passing this acceptance does not authorize
weakening the contract to make a later implementation pass.

This work qualifies offline corpus engineering behavior for the exercised inputs.
Synthetic data, controlled fault hooks and structural resource admission do not
establish physical measurement quality, independent recording sessions, calibrated
hardware, a fitted model or musical fidelity. Full-maximum artifact/audio scans,
native Windows reparse behavior, hostile racing filesystem stress and operating
system close states beyond the explicit injected cases remain unexecuted.

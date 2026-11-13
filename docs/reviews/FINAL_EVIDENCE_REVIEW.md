# Final Python evidence review

Agent 56 performed this independent review on 2026-11-13 against published
baseline `6c3dd8bc923a3c11f6b234425b056e135fbe9f4b` and the integrating working
tree, including Agent 51's historical-executable repair and retained demo gate.
This is the original session's wave-10 assignment, separate from the
[console continuation](../development/2026-11-13-continuation/README.md).

**Disposition:** two concrete rejection/portability defects were reproduced and
repaired with integrator authorization. The three affected suites passed all
57 methods locally, with zero skips. No additional blocking defect was found
within the inspected scope. This review does not establish a final integrated
commit, hosted qualification, authentic acquisition, build provenance or physical
fidelity. The integrator owns publication and its revision-specific evidence.

## Reproduced findings and repairs

### F56-1 — absent executable below a former directory failed verification

The [verifier](../../tools/verify_render.py), in `_renderer`, already classified
missing or unreadable historical executables as unavailable. Agent 51 had moved
the initial `lstat` ahead of ancestry validation to handle an absent executable
under a symlinked ancestor. A different real filesystem case remained: a former
build directory could now name a regular file. `lstat` of the executable beneath
it raised `NotADirectoryError`, which escaped the availability classification and
failed an otherwise valid retained bundle.

The reproduction copied the seven-file demo into a temporary directory, created
a regular file named `former_build_directory`, and changed only the copied
manifest's `renderer.path` and `invocation.argv[0]` to the path of its former
`hammond_render` child. No original artifact or executable was changed. The public
`verify_bundle` call raised `NotADirectoryError: [Errno 20] Not a directory`.
The new targeted regression reproduced that error before the repair.

The repair adds only `NotADirectoryError` to the existing external-executable
availability exception cases. The report now says `renderer.status: unavailable`
and retains `replay.status: not_performed`. Present executables still undergo
the existing ancestry, regular-file, observed stability, size and SHA-256 checks.
The existing demo test still rejects changed bytes, a directory at the executable
path, and unacceptable ancestry; the existing verifier suite also remains green.
Retained artifact availability, path and integrity rules are unchanged.

The eighth method in [the demo gate](../../tests/test_demo_bundle.py) constructs
this real topology. Its diagnostic assertion permits `NotADirectoryError` or
`FileNotFoundError` because platforms can report that absent child differently.
This assignment observed `NotADirectoryError` on Linux; it performed no native
Windows or macOS run.

### F56-2 — escaped surrogate reached factory canonical hashing

The [factory comparison](../../tools/validate_factory_reference.py) decoded raw
UTF-8 and rejected malformed JSON, duplicate keys and nonfinite numbers, but its
tree check did not require decoded JSON strings to encode as UTF-8. Escaped lone
surrogates therefore passed `load_json`. Placing `\ud800` in a temporary profile's
`frequency_model.reason` reached `_hashes`, where canonical UTF-8 serialization
raised an uncaught `UnicodeEncodeError`. That violated the comparison API's
declared `FactoryReferenceError` failure boundary and the CLI's clean rejection
behavior. It did not produce a successful comparison or alter pinned history.

The repair validates UTF-8 encodability for every string visited by `_json`.
Its existing traversal visits both dictionary names and values, and its existing
exception handler translates encoding errors to `FactoryReferenceError` before
canonical hashing. Bounds, pinned digests, comparison cells and provenance fields
are unchanged.

Two [regression methods](../../tests/test_factory_reference.py) cover lone high
and low surrogate values and keys, acceptance of a valid paired escape, and the
public comparison/CLI path. Before repair, all four malformed parser subcases
failed to reject and the target comparison errored with `UnicodeEncodeError`.
After repair, the CLI returns 1, emits no success stdout, reports the declared
factory error without a traceback, and leaves the mutated temporary input intact.

## Inspected implementation and assertion boundaries

The review read `AGENTS.md`, current status/next steps, the acceptance matrix,
profile/factory/capture/render/analysis contracts, demo and replay records, and
the separate continuation ledger. It then inspected all six production Python
modules below and the relevant test assertions, rather than accepting report
summaries alone.

| Boundary | Inspected implementation and meaningful assertions | Claim supported by that boundary |
| --- | --- | --- |
| [Profile compiler](../../tools/compile_profile.py) | Exact keys and scalar types; bounded authoring tree; duplicate-key/nonfinite rejection; named nominal equations and all routes; canonical versus raw identities; deterministic compiled text; input/output collision checks and atomic replacement. Tests include numeric/provenance relabeling and independent compiled-route checks. | Validated data for the named unmeasured model. The standalone compiled digest does not authenticate an unseen JSON document or a physical instrument. |
| [Factory comparator](../../tools/validate_factory_reference.py) | Frozen source/CSV/target identities, exact metadata and ordered matrices; all 549 manual cells and 200 pedal positions; all five nulls; bounded diagnostics; optional external-source byte check; the repaired Unicode boundary. Mutations cannot rewrite all three inputs into a new accepted history. | Agreement with the retained documentary transcription and identified project bytes. Review independence and source interpretation still rely on the retained human review procedures. |
| [Capture validator](../../tools/validate_capture.py) | Exact planned/recorded states, explicit unknowns, units, finite typed numbers, real UTC dates, portable paths and local parent DAGs. The root's repaired nonzero file-ID fallback and its two regressions were inspected: separate equal-byte copies pass, aliases fail, and unavailable identities reject. | Structural declarations and optional declared-byte integrity. No audio header, physical chain, calibration, permission authority, corpus split or authentic acquisition is verified. |
| [Render producer](../../tools/render_fixture.py) | Exclusive new-directory creation; bounded copied inputs; independently preflighted score; explicit argument list; retained raw logs; process failure/timeout/truncation states; before/after source/tool/executable hashes; actual float metrics and separately decoded PCM. The mutation test requires successful child execution followed by the exact integrity failure. | An observed successful synthetic software run and its retained artifacts, within the documented filesystem/process assumptions. Checkout HEAD and tool hashes do not establish how the executable was built. |
| [WAV analyzer](../../tools/analyze_wav.py) | Complete RIFF/chunk/frame validation, bounded windows and integer accumulation; per-channel/stereo statistics; full-scale endpoint counts separate from clipping history; crossing interpolation and explicit ambiguity flags. Tests independently construct PCM, malformed headers, window boundaries and ambiguous tones. | Statistics of serialized PCM in normalized units. Header rate is not a calibrated physical clock; a declared expected tone is not recognized pitch or a fidelity pass. |
| [Bundle verifier](../../tools/verify_render.py) | Typed complete successful schema; retained inventory and raw hashes; independent event parser; local recompilation; exact argv and raw stdout reconciliation; streamed PCM and quantization checks; ordered run/Git timestamps; observed file/directory stability; explicit external executable availability. | Internal retained-bundle consistency. The report continues to state that replay was not performed and authentication, source/build association and physical fidelity are unestablished. |
| [Retained demo](../../tests/test_demo_bundle.py) | Pins all seven original hashes; reconciles complete profile/score/catalog/settings; independently decodes every PCM frame and all six timeline spans; checks silence, nonzero chord regions, clipping declarations, relocation and historical path handling. | Integrity of this retained four-second example. Its pinned WAV is not an expected output for future compilers, architectures or operating systems. |

### Bounds, chronology and ancestry

The byte limits match their respective contracts: profile JSON 256 KiB and
compiled profile 128 KiB; factory CSV 8 KiB, JSON/review notes 256 KiB and optional
PDF 16 MiB; capture JSON 64 KiB, 32 artifacts, 256 MiB per file and 512 MiB total;
render events 16 MiB, logs 1 MiB per stream, metrics JSON 16 KiB and executable
512 MiB. The analyzer separately accepts at most 256 MiB, 1,024 chunks, eight
channels and 600 seconds. Audio is streamed, while bounded metadata/events may
be retained in memory. None of these bounds is a real-time callback guarantee.

Numeric strictness has a defined domain: exact integer/Boolean distinctions,
finite parsed values and field ranges are enforced. Nominal profile comparisons
operate at binary64 precision under the documented project canonicalization;
they are not arbitrary-precision decimal or token-preservation claims. The two
independent event parsers explicitly reject nonzero decimal underflow to zero.
Raw authoring-byte hashes remain distinct from canonical parsed-JSON hashes.

Render chronology is locally checked: valid calendar timestamps satisfy
start <= sampled Git time <= finish. This checks declared ordering; it does not
authenticate the host clock or Git/build history. Capture parent references are
local, unique, cycle-free, and every derivative reaches a raw ancestor, regardless
of serialization order. Cross-manifest ancestry, independent takes, permissions,
frozen holdout use and physical admission remain explicit later corpus gates.

Filesystem checks are observations, with different scope per tool. Capture byte
verification rejects artifact-relative aliases/reparse points and uses POSIX
directory descriptors where available; ancestors above its selected root may be
canonicalized. Bundle verification requires nonsymlink ancestors and repeats
inventory/path observations. Producer hashing compares path and descriptor
metadata within their own APIs, with POSIX device/inode binding. Factory reads
check descriptor stability; the analyzer checks its open descriptor's size and
timestamps. These checks do not establish immunity to all concurrent
replace-and-restore races, hostile processes or later mutation.

Original producer/compiler paths and source-checkout metadata in a retained
bundle are historical typed records. The verifier uses the supported local
compiler to validate and reconstruct retained authoring data; it does not require
the historical compiler/wrapper files, resample their Git history or execute the
recorded argv. Missing original tools therefore do not become invented recovered
evidence. A currently readable executable is separately hashed, without asserting
its dependencies or ability to execute.

## Executed checks

The three new methods were first run against the unrepaired production code:

```sh
python3 tests/test_demo_bundle.py DemoBundleTests.test_absent_historical_renderer_below_regular_file_is_unavailable -v
python3 tests/test_factory_reference.py FactoryReferenceTests.test_json_rejects_unpaired_surrogate_strings_and_keys FactoryReferenceTests.test_surrogate_target_fails_through_public_api_and_cli -v
```

Observed results were one demo error, then four factory subcase failures and one
factory error across two methods, as described above. The original narrow
scratch reproductions independently produced the same two exception classes.

After the repairs, these exact affected-suite commands ran on local Linux with
Python 3.12.14:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_factory_reference.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_demo_bundle.py -v
PYTHONDONTWRITEBYTECODE=1 HAMMOND_RENDER_EXECUTABLE=/tmp/hammond-wave07-asuv11lz/build/hammond_render HAMMOND_TEST_PROFILE=/tmp/hammond-wave07-asuv11lz/build/nominal.b3p python3 tests/test_verify_render.py -v
```

| Suite | Methods | Observed result |
| --- | ---: | --- |
| Factory comparison | 22 | Passed; zero failures, errors or skips |
| Retained demo | 8 | Passed; zero failures, errors or skips |
| Existing bundle verifier | 27 | Passed; zero failures, errors or skips |

The verifier suite created its small real-render fixtures using the existing
local Release executable; this agent did not rebuild it. The factory suite
rechecked the original profile and compiled identities and every compiled manual
route. The demo gate rechecked all original artifact hashes, including manifest
`74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`
and WAV `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
The historical `dirty: true`, `6c3dd8b` checkout context and unestablished binary
association were preserved. No frozen bundle, source profile, CSV or attestation
was edited.

Scoped `git diff --check` passed. A read-only check of the nine changed files
found no trailing whitespace and resolved all 28 local Markdown links; the
agent note was within its 80-line limit.

## Not executed or newly established

No broad CTest run, complete compiler/capture/producer/analyzer-suite rerun,
fresh build, source-PDF download/review, native Windows/macOS run, sanitizer run,
host/device session, playback/listening test or physical acquisition was performed
by this assignment. The historical full matrix remains the integrator's observed
21-suite result at `6c3dd8b`; the proposed 23-suite integration and the additional
methods require their own published revision and hosted results. Agent 51's
separate clean-build replay is retained evidence attributed to that assignment,
not a build performed during this review.

The repairs affect portability and controlled rejection. They do not establish
specimen identity, calibrated signal/clock/chain response, authentic authorship,
source-to-binary provenance, corpus independence, host qualification or a playable
instrument. M3 and later product/physical gates remain governed by the current
[acceptance matrix](../ACCEPTANCE_MATRIX.md) and continuation ledger.

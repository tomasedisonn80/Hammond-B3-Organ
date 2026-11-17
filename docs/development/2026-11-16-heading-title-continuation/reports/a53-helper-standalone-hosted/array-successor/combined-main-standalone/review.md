# Exact combined-source standalone qualification

A53/60, wave 9, same accepted worker. **All six main-source standalone jobs
succeeded on attempt 1 at `54859886268ce83c36f359c43327f7c72a77ae82`.**
Five normal families each executed and passed 78/78 tests; Linux
ASan/UBSan with leak detection executed and passed 41/41. This review concerns
[run 44038196285](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44038196285),
its six actual runners, and their complete original logs. It creates no
additional worker credit and changes no previous outcome.

The [summary](summary.json), [terminal API observation](final-observation.json),
[source inventory](inventory.json) and individual receipts below retain exact
identities, results, step outcomes and limits. Root separately owns the Core,
VST3 and sixteen-job aggregate reviews.

## Source and actual results

The exact source tree is `f5f8f037af301f8b1ff5b9b4a00ff5581647667a`, with parents
`d2ed03b94114e35d0caa65968d11afe896a5e9f5` and
`ea02c5465b6c6a896cbbc83b55479d6f62bbf8c9`. The API run head and every actual
checkout in the original logs agree. The separately fetched workflow is
SHA-256 `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659`;
standalone CMake is
`927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07`.
The final terminal observation was obtained at 07:48:33 UTC on 17 November 2026.

| Actual family | Job and receipt | Passed CTests | CTest seconds | Verified installed package |
| --- | --- | ---: | ---: | --- |
| Linux GCC, MIDI ON | [133886098388](job-133886098388.json) | 78/78 | 445.96 | 21 files; ALSA |
| Linux GCC, MIDI OFF | [133886098757](job-133886098757.json) | 78/78 | 475.22 | 17 files; MIDI unavailable |
| macOS ARM, AppleClang | [133886098398](job-133886098398.json) | 78/78 | 430.96 | 21 files; CoreMIDI |
| macOS Intel, AppleClang | [133886098331](job-133886098331.json) | 78/78 | 537.55 | 21 files; CoreMIDI |
| Windows x64, MSVC | [133886098445](job-133886098445.json) | 78/78 | 415.80 | 21 files; WinMM |
| Linux GCC, ASan/UBSan/leaks | [133886098061](job-133886098061.json) | 41/41 | 943.85 | No package stage |

These are 431 executed test observations across six configurations. They do
not represent 431 distinct project tests. The normal workflow explicitly
requires 55 names and actually discovers 75 standalone plus three Python
tests. All 78 observed names match the source inventory. The sanitizer job
discovers the exact 41-name selection from 37 built targets. Older 68/34
inventories remain historical.

GNU 13.3.0, AppleClang 17.0.0.17000013 and MSVC 19.44.35230.0 are recorded in
the respective configure logs. Windows actually compiled all three affected
footage/H1/P1 fixture translation units with `/W4 /WX`; the summary records
each original command's line and hash. Its build, complete acceptance selection,
source/dependency re-verification and package tail all succeeded.

## Executed native, numerical and Python evidence

All six jobs report title density 18/18 with the strict 44-case native
inventory; H1 material 48 cases, 10,542 checks, 163 paintings and 95 helper
probes; H1 statistics 103/103 criteria; and four grain cases with 170 checks.
P1 reports 34 native cases, 53,648 checks, 111 paintings and 61 helper probes.
Its candidate numerical report evaluates 191 checks with zero failures and
passes all 62 frozen screens. Five copied-library gates pass in every family.
These counts come from actual native/reader output in the complete logs.

Every H1 statistics report binds the corrected fixture and reader sources and
reports canonical RGBA SHA-256
`56392ccf2d9d3600533d08955879d43c4a916b720463f3c541d1113b4f854fb2`.
This is scoped canonical software output, not whole-interface visual equality.

Each normal configuration also executes 45 capture-tool, 32 H1-comparator and
64 P1-comparator Python methods. Each reports 37 actual workspace subprocesses,
ten calibration subprocesses across seven native lifecycles, including two
deliberately failed replay scenarios, and two children for each of the replay
and semantic real-application paint gates. These are actual child counters,
not inferred from registered test names. The sanitizer selection does not
include the complete 37-child workspace replay suite.

The successful Windows replay-boundary test explicitly skips its unsupported
FIFO-creation subcase. It still reports 28 actual boundary children and 18
preserved setup rejections. No CTest is skipped. This platform-specific
diagnostic remains in the receipt; it is not presented as FIFO execution.

## Sanitizer instrumentation and limits

The actual instrumentation-verification step succeeds. Its committed checks
require nonempty SDL C and selected project C++ objects compiled with
address/undefined sanitizers and frame pointers, sanitizer references in seven
archives, and the required runtimes in all 37 selected executables. They also
verify real application/probe dependencies and P1/library link inputs.

Production support privately uses MIDI=0; the isolated calibration probe uses
MIDI=1 with its fake dependency first. The job retains the 35-minute total
allowance and strict policies:

- `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`
- `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`
- `LSAN_OPTIONS=exitcode=23`

The individual finite CTest and child limits are recorded in the sanitizer
receipt. No per-test sanitizer-environment override is admitted. The postcheck
actually confirms ten calibration subprocesses and all seven lifecycle
scenarios and scans their recorded stderr streams, including both expected
application failures, for sanitizer/runtime diagnostics. Both paint gates each
report two children from application SHA-256
`b7f298ddaaef04cd376020ba488d68777dc4d074cc1ab7029713667de4029de7`.
All 41 gates and the final source/locked-SDL verification complete successfully;
no sanitizer finding appears in the actual failure stream.

## Dependencies, relocation and package scope

All six source/dependency re-verification steps succeed. The logs bind SDL
2.32.10 to commit `5d249570393f7a37e037abf22cd6012a4cc56a71`. Enabled normal
MIDI jobs verify RtMidi 6.0.0 commit
`1e5b49925aa60065db52de44c366d446a902547b`, including the retained prepared
source/patch identities. Disabled MIDI and sanitizer configurations retain
their declared production capability.

Each normal install CTest passes the unchanged eight-method suite. Its exact
source includes the custom `native prefix Ω` and `relocated Ω` directories
and calibration checks; individual install method names are not printed by
these logs. The later package stage actually asserts the exact installed
inventory and bytes, preservation after rename/relocation, relocated help and
600 ms dummy audio/video smoke, MIDI/dependency metadata, and equality of
archive member names, lengths and bytes to the installed payload. All five
stages print their successful file counts above.

The final API metadata lists five package and six diagnostic artifacts.
A53 did not directly download those main-run artifacts. Executed archive
assertions and successful upload receipts are the evidence claimed here;
independent inspection of a downloaded package or signed distribution is
not claimed. The separately downloaded focused artifact has its own
[complete independent review](../combined-focused/review.md).

## Original retention, prior failures and remaining work

All six complete original decoded logs are retained as deterministic gzip,
with empty filename, mtime zero and level-nine compression. Their combined
size is 6,566,664 decoded bytes and 730,885 stored bytes. The
[retention manifest](complete-log-archives.json) binds both representations
and original newline counts. Windows retains all 5,992 CRLF sequences and
its twelve additional LF endings without conversion. Independent standard
library inspection rechecked every stored/decoded size and hash, gzip header,
round trip, receipt binding and all 431 actual CTest result rows.

The [focused same-source Windows review](../combined-focused/review.md) remains
separate: nine tests pass, all 566 source inputs are verified, and the retained
complete P1 canonical stream is byte-identical to Linux. The raw inventory
differs solely by its final Windows CRLF while complete typed inventories are
equal. This scoped equivalence is not silently extended to unretained
full-matrix frame streams.

The [d2ed Windows failures](../concurrent-d2ed/review.md),
[cf87 standalone failure](../concurrent-cf87/review.md), and
[cf87 Core path failures](../concurrent-cf87/core-windows/review.md) remain
frozen, as do the original 628/03c/fba reports. In particular, Intel's original
03c preset timeout at 30.05 seconds under a 30-second guard and its skipped
tail remain failed. Main548 Intel passes that unchanged gate in 18.36 seconds.
This later observation establishes no timing repair, originating cause or
repeated stability. The original sanitizer cancellation also remains intact.

A53 performed no source edit, native/build/project-test execution, remote
mutation or CI retry. The accepted A53 note is unchanged. Root must combine
the independent sixteen-job evidence, update current recovery documents and
README, verify final source equivalence/integrity, and publish accepted
documentation with a fresh expected head and no force. That later publication
is not claimed by this receipt.

Dummy devices, fake MIDI, copied-state inspection and software painting leave
physical MIDI/audio, real display/DPI, native accessibility, callback retirement
and deadlines, measured fidelity and literal whole-UI 1:1 acceptance open.

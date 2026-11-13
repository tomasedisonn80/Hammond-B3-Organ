# Assignment 24 — independent audio admission and failure qualification

**Actual assignment:** `/root/cal_w4_a24`, calibration wave 4, assignment 24,
2026-11-13. The parent's successful dispatch is the counting record. A worker-side
wrapper-status observation does not add a dispatch. This is one new assignment;
it is not a rerun of assignment 16 and does not add another worker to the session
count. The integrator clarified this accounting wording after acceptance.

**Result:** the final suite ran **62 test methods: 60 passed, 2 skipped, no
failures or errors**. It independently reproduced one production error-ordering
defect. Root repaired the producer, and the retained regression passes against
the exact repaired source below. The two skips are explicit native capability
limits. These engineering fixtures do not establish instrument authenticity,
physical calibration, hostile-filesystem security, or maximum-workload fitness.

## Ownership, reading, and source identity

This assignment owns only:

- `tests/test_capture_audio_admission.py`
- `docs/development/2026-11-13-calibration/24-audio-admission.md`

Work was performed in
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. Read `AGENTS.md`,
`docs/CALIBRATION_SCOPE.md`, all 615 lines of the frozen audio contract, the
producer, and the relevant independent acceptance fixtures. The complete atlas
reading belongs to assignments 1–6; this assignment claims no additional full
PDF reading. No production source, contract, shared status, ledger, CMake, other
worker's test, or Git ref was edited by this worker. Root owns integration,
commits, and publication.

At initial inspection, `HEAD` was
`8864c051d19556e37dffcd7366fd859606958bc3`, tree
`e4f56a7c722dcad4eda9269d907715b8526dd8cd`. During final qualification the
shared checkout had advanced to `091ad20c632209053c337a06544f82a829644800`,
tree `8679418135946193b2b989a89e60ac6099b00125`. Locally recorded
`origin/main` was `5b8e2419d23fe27c51709d717812060eafd44dcc`; this is a local
ref observation, not a remote-publication assertion. The source hashes below,
observed unchanged before and after the final verbose run, identify the actual
tested files independently of concurrent root commits.

| Input | SHA-256 |
| --- | --- |
| Repaired `tools/capture_audio.py` | `c02c1a5e6023e0278dddca09ad1841541fbb0ece66d7950198f93be7846dc7ac` |
| Frozen `docs/CAPTURE_AUDIO_CONTRACT.md` | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| Final `tests/test_capture_audio_admission.py` | `6d8f681d4dfe8f98df188070e1fba115a2d9bc7024f6bab243ff4551d7cd398b` |
| Independent fixture module `tests/test_capture_audio.py` | `9fc75824234b3203f1eb9f63c0fe7562a3d9a931cda34e9a774b4c1402c56ddd` |
| Unchanged legacy `tools/analyze_wav.py` | `e39d3b414854066af2510c3dedf26c70ea71066a09efce5a9cdb41114e8b5fb7` |
| Unchanged v1 validator `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

The original producer against which the defect was reproduced had SHA-256
`967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2`.
The frozen contract was not changed to make the regression pass.

## Independent expectations and failure instrumentation

The suite uses Python's standard library and calls the public API/CLI. Literal
RIFF chunks, explicitly packed headers, PCM codes, and raw float bytes supply
the inputs. It reuses assignment 16's independent `chunk`, `fmt`, `riff`, and
`wave` fixture encoders; it does not use a producer parser, normalization helper,
digest helper, or producer report to calculate an expected result. Error codes,
field positions, phase ordering, bounds, and report requirements come from the
frozen contract.

For the bounded-stream probe, an independent byte sequence supplies the expected
original-file hash. The expected decoded hash is constructed from the literal
`HAMMOND-CAPTURE-DECODED-V1` prefix plus its terminating NUL, explicit
little-endian rate/channel/frame integers, and frame-major binary64 values
`0.0`, `0.25`, and `-0.25`. The three-channel PCM24 source crosses the read
boundary and includes a 70,001-byte ancillary payload. The tiny returned window
must still carry both independently calculated full-stream identities.

`StreamProbe` wraps an actual owned file descriptor. It records each requested
read, returned-byte count, seek, and close; it can inject read/seek/close errors,
short reads, premature EOF, cancellation, and mutations during a read. The
cleanup oracle checks that the real stream is closed, close was called once,
and the captured descriptor returns `EBADF` from the saved real `os.fstat`.
The harness cleans a leaked descriptor after recording its assertion failure.
Digest wrappers independently record every actual update size. Stat hooks copy
real observations and change explicitly selected fields; they test branch
behavior and are not presented as native filesystem qualification.

## Executed acceptance and retained initial failure

Environment: Linux x86_64, kernel `6.18.57`, glibc `2.41`, Python **3.12.14**
(`Clang 22.1.3`). From the repository root:

```sh
python3 -B tests/test_capture_audio_admission.py
python3 -B tests/test_capture_audio_admission.py -v
```

The compact final run exited **0**, reporting `Ran 62 tests in 2.225s`,
`OK (skipped=2)`. A final verbose run, bracketed by the source hashes above,
exited **0**, reporting `Ran 62 tests in 2.111s`, `OK (skipped=2)`.
Its stdout was empty. Unittest's method results and summary were on stderr.
Parameterized cases are not counted as separate methods.

The initial verbose run reported **61 methods, 59 passed, 1 error, 1 skip** in
2.154 seconds and exited **1**. The error was in the native socket fixture:
`socket.socket(socket.AF_UNIX)` raised
`PermissionError: [Errno 1] Operation not permitted` before the harness's
capability handler, which originally covered only `bind`. The handler now
covers socket creation and binding. A separate injected special-file-mode test
was added, accounting for the final 62 methods. This correction did not alter
production behavior or weaken the assertion on a native socket when one can be
created.

| Explicit final skip | Observed reason |
| --- | --- |
| `test_real_unix_socket_is_rejected_before_open` | `native Unix-domain socket creation/bind unavailable: [Errno 1] Operation not permitted` |
| `test_native_windows_reparse_fixture` | `real Windows reparse admission requires a native Windows runner` |

Native FIFO creation, character-device rejection using `/dev/null`, symlinks,
hardlinks, parent aliases, timestamp mutation, POSIX same-size replacement, and
POSIX unlink all executed successfully here. Injected socket/block/character/
FIFO modes and reparse flags passed, but do not substitute for the two skipped
native checks. No tests were marked as expected failures.

## Coverage of the 62 methods

| Group | Methods | Independently exercised behavior |
| --- | ---: | --- |
| `RiffAdmission` | 16 | Empty and recognized truncated headers; unrecognized and explicitly unsupported containers; exact RIFF length; chunk payload and pad bounds; final partial headers; missing, duplicate, or disordered format/data chunks; empty and incomplete frames; supported format lengths and zero extension; unsupported tags and widths; byte-rate/alignment contradictions; earliest-field regression; fact order/size/count/duplicates; LIST and alternate audio sequences; complete post-data chunk admission before window/content errors; raw incomplete frames; argument/file/header/assertion/window/content phase ordering. |
| `ResourceAdmission` | 11 | Adjacent rate/channel rejection; actual duration and chunk limits; sparse file-size admission; actual window duration/frame/scalar boundaries; explicitly reduced total-scalar preflight; actual bounded reads/digest updates and one descriptor; complete-stream hashes for a window; legitimate three-byte short reads. |
| `FilesystemAdmission` | 30 | Missing paths, directories, native and injected special files, leaf links/reparse flags, allowed parent aliases and hardlinks; available/unavailable and zero-device identities; path/fd disagreements; same-API stamps and cross-API timestamp differences; fdopen/open/stat/read/seek/close errors; EOF and cancellation cleanup; final-recheck/close error precedence; descriptor and parent changes; real mutation/replacement/removal; parent-alias retargeting despite a shared child inode; independent requested-leaf observation. |
| `CommandLineAdmission` | 5 | Strict ASCII decimal grammar and length; invalid API paths/selectors/argv types; unknown, abbreviated, output, and unpaired options; no output-file side effect; subprocess admission errors with empty stdout, canonical finite JSON stderr, and required exit statuses. |

The separate 41-method sample/format suite from assignment 16 supplies numerical
and encoding coverage, including invalid samples before, inside, and after a
requested window. Its methods are not included in this assignment's 62 count,
and this worker does not claim to have rerun that suite. Here, complete chunk
validation after `data`, failure precedence before window admission, and
independent full-file/decoded identities on a small returned window extend
that existing complete-stream coverage.

### Resource boundary claims and exclusions

| Probe | Actual workload and supported conclusion |
| --- | --- |
| File-size excess | A real sparse file of 268,435,457 bytes rejects before `os.open`; no audio decoding is performed. |
| Inclusive file-size admission | A real sparse file of 268,435,456 bytes gets past the size gate, reads 12 bytes, and rejects as an unrecognized container. This does not scan or decode 256 MiB. Inclusive successful admission is separately exercised with `MAX_FILE_BYTES` temporarily reduced to a small valid fixture's exact size. |
| Duration | A complete 3,600-frame, 1 Hz PCM file is inspected successfully; 3,601 frames reject. This qualifies the duration arithmetic with a small real stream. |
| Chunk count | A real 4,096-chunk file succeeds; 4,097 chunks reject. |
| Window duration | A real 600-second selection at 1 Hz succeeds; 601 seconds reject. |
| Window frames | An actual 262,144-frame returned window succeeds; 262,145 requested frames reject before hashing. |
| Window scalars | An actual 16-channel by 65,536-frame window returns 1,048,576 samples; the adjacent 65,537-frame request rejects before hashing. |
| Total decoding work | `MAX_DECODED_SAMPLES` is explicitly reduced to 6. A six-scalar stream succeeds; a seven-scalar stream rejects before hashing. No 134,217,728-scalar maximum decoding workload was executed or timed. |
| Streaming limits | A 12,000-frame, three-channel PCM24 fixture plus a 70,001-byte ancillary payload proves actual read/update requests no larger than 65,536 bytes, one owned descriptor, and returned bytes within two file passes plus bounded header overhead for that layout. It is not a proof over all possible layouts. |

## Reproduced producer defect and regression

Frozen contract sections 3 and 10 require internal header consistency for
admitted tags and the earliest malformed field within the header. This literal
fixture has PCM tag 1, one channel, 48,000 Hz, a contradictory zero byte rate,
block alignment 1, and unsupported eight-bit storage:

```python
import struct

form = struct.pack("<HHIIHH", 1, 1, 48000, 0, 1, 8)
body = (b"WAVE" + b"fmt " + struct.pack("<I", 16) + form
        + b"data" + struct.pack("<I", 1) + b"\0\0")
payload = b"RIFF" + struct.pack("<I", len(body)) + body
```

The original producer returned `unsupported_format` for the width field at
byte **34**. The contradictory byte-rate field occurs at byte **28**, so the
contract requires `malformed_audio` at byte 28. The original result and minimal
fixture were reported promptly to root. Root moved byte-rate and block-alignment
validation ahead of unsupported-width rejection, retaining the explicit
unsupported-tag priority and later extension handling.

`test_earlier_malformed_fields_precede_unsupported_width` preserves the original
expectation and adds a zero-alignment variant: when both byte rate and alignment
are zero, the rate equals rate-times-declared-alignment, and the alignment
contradiction at byte **32** wins. Both cases now pass. Adjacent tests confirm
that a consistent earlier header with an unsupported width still reports
`unsupported_format` at byte 34, and explicit unsupported tags still win at
byte 20 even with incompatible extension lengths. No expected value was changed
to follow the original producer's behavior. No additional production defect was
found in the executed admission scope.

## Handoff and next steps

Root should retain both owned files and the error-order repair together, add
the admission suite to the appropriate integration gate, and rerun affected
acceptance on the final integrated source before publishing. This worker did
not modify test registration or run shared CMake/CI gates. The source identities
and limits in this note must remain attached to any claim about these results.

A runner that permits Unix-domain socket creation can execute the native socket
method; a native Windows runner can execute the reparse method. Injected metadata
does not close those native qualification gaps. Maximum scalar/file workloads,
memory ceilings, platform-wide filesystem behavior, live instrument recordings,
acquisition provenance, listening evaluation, and calibration claims remain
outside this assignment. Continue following the standing repository instructions
and the frozen audio/corpus contracts for subsequent development.

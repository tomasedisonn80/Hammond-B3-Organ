# Calibration hosted portability follow-up

## Observed checkpoint and outcomes

On 2026-11-13, root inspected completed GitHub jobs for public commit
`779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
`f9baccbb54f51063b01a0859d2c10cdadfbd238b`. The source's local frozen full gate
had passed 96/96 SDK-free Release suites. That local observation remains valid,
but does not replace these separately observed hosted outcomes.

| Hosted workflow | Observed completed results |
| --- | --- |
| [CI 43527805867](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43527805867) | Linux GCC Release failed one suite; macOS AppleClang Release failed two suites; Windows MSVC Release failed four suites. The separate Linux GCC ASan/UBSan/leaks job succeeded. |
| [Native standalone 43527805757](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43527805757) | Linux GCC, macOS AppleClang and Windows MSVC x64 jobs succeeded. |
| [Native VST3 43527805786](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43527805786) | Linux GCC, macOS AppleClang and Windows MSVC x64 jobs succeeded. |

Those successes apply to each workflow's configured checks at that commit.
They do not establish a real audio device, every DAW, physical calibration or
fidelity. Later source changes require fresh relevant evidence.

Root retrieved each failing job's actual decoded log through the authenticated
GitHub workflow-log operation. A generic fetch endpoint rejected the logs URL;
the documented job-log operation provided the retained content. The failure
classification below comes from those logs, not from job status alone.

## Concrete failures

### Windows canonical output

Windows Release job **132237791002** failed `python_test_capture_audio`,
`python_test_capture_audio_admission`, `python_test_capture_corpus` and
`python_test_capture_corpus_admission`.

The audio successes and typed error envelopes ended in CRLF instead of their
required LF. The corpus's pretty JSON also had translated line endings. Both
producers wrote a Unicode string through the platform's standard text stream.
The existing independent expectations required the original canonical bytes;
those expectations were correct and were not changed.

Root added a small UTF-8 writer in each producer. Real standard streams use
`stream.buffer` to preserve exact bytes and LF; text-only redirected streams
still receive the same Unicode text. Both paths detect short writes and flush.
The corpus's contextual stderr also bypasses terminal encoding, so a Unicode
filename does not fail merely because the terminal is configured as ASCII.
The numerical, parser, corpus graph and public report definitions are unchanged.

### Canonical-path fault fixtures

macOS Release job **132237790511** failed the audio parent-identity injection
and multiple corpus path/reparse/identity injections. The corpus's usable-device
case raised an unexpected mismatch. Windows showed corresponding corpus errors.

The fixtures kept unresolved temporary paths (`/var/...` on macOS and the
runner's short `RUNNER~1` TEMP path on Windows), while the producer deliberately
canonicalizes ancestors before observing confined descendants. Hooks comparing
literal `Path` values consequently missed the intended observation. In the
zero-device case, only the descriptor half changed, correctly causing a mismatch.

Root canonicalized the fixture roots before constructing targeted descendants,
and added explicit assertions that the parent/reparse/path/descriptor hooks were
actually reached. The same precaution was applied to the new job/readiness
fixtures before their first hosted publication. Alias-admission cases remain
separate tests; no producer confinement rule was relaxed.

The tiny same-size corpus mutation also lacked a guaranteed observable timestamp
change on Windows. The test still writes the changed byte in place, and now
explicitly advances its mtime by two seconds and verifies that observation.
This tests the required rejection of an observed mutation without assuming a
filesystem timestamp granularity. A same-size change whose observable stamps
are identical is outside the stated quiescent-input observation guarantee;
this change does not claim a hostile-filesystem proof.

### Separate standalone scheduling assumption

Linux Release job **132237790906** failed only
`test_standalone_concurrency`: line 328 required `reader.active_reads > 0`.
The three native standalone jobs succeeded, so a generic native build failure
is not inferred. The separate active standalone checkout already contains a
committed reader-progress repair with explicit initial/final publication
checkpoints and retained overlapping-activity observations. This calibration
track did not edit that concurrently owned C++ test. Integrate its published
checkpoint and observe fresh results before clearing this hosted failure.

## Reproduction and local repair checks

Two added maintained methods wrap actual `BytesIO` with `TextIOWrapper` using
ASCII encoding and explicit CRLF translation, then invoke the real CLI main
functions. Their expectations are independently encoded canonical JSON, plus
UTF-8 contextual error text. On the archived original producer, the two methods
produce three assertion failures for translated bytes and one encoding error;
on the repaired producer, both pass. An initial probe inspected buffered text
before flushing and saw empty strings; the final regression explicitly flushes
the wrappers to isolate the intended line-ending defect.

A separate native Linux ancestor-alias probe points the temporary directory
through a real symlink. Three original fault-fixture methods reproduce seven
failed subcases. The same three repaired methods pass, and their hook-interception
assertions execute. This reproduces the path-targeting mechanism locally; it is
not a claim that native macOS or Windows was rerun on Linux.

| Repeated local command | Observed result |
| --- | --- |
| `python3 -B tests/test_capture_audio.py` | 41/41 methods passed, 0.622 seconds. |
| `python3 -B tests/test_capture_audio_admission.py` | 63 methods: 61 passed and two explicit native-capability skips, 2.532 seconds. |
| `python3 -B tests/test_capture_corpus.py` | 47/47 methods passed, 1.151 seconds. |
| `python3 -B tests/test_capture_corpus_admission.py` | 58/58 methods passed, 1.290 seconds. |
| `python3 -B tests/test_capture_readiness.py` | 65/65 methods passed, 0.699 seconds. |
| Focused old/new portability probe | Original defects reproduced; repaired two CLI methods and three alias methods passed. |

The two admission method counts each increase by one for the canonical-stream
regression. Historical assignment notes retain their original 62/57 counts and
exact tested source identities. The final stream regressions explicitly flush
the wrappers; the coherent integration gate executes those final bytes.
The original native socket and Windows-reparse capability skips remain explicit.

| Repaired production source | SHA-256 |
| --- | --- |
| `tools/capture_audio.py` | b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c |
| `tools/capture_corpus.py` | 1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba |

## Retained observation identities and continuation

| Local observation | Bytes | SHA-256 |
| --- | ---: | --- |
| Hosted Linux log | 212408 | bbcd104682ab87bfb6eeadfb0f9e0695d1009e3845ecb00968c16be072675dd8 |
| Hosted macOS log | 208666 | 1cb377e29c8252d23698e44c020858d4c0b09b2be0a3a4308cd453c8a74d0a90 |
| Hosted Windows log | 316863 | 85c644f19dab972ff22bc8431951cfecea49d6995782cade67695ebaee626cd6 |
| Scratch portability probe | 3532 | ad53e4bea15c473badaa8f4c38a1f162f271df6e71151773323de0128ad5f7f5 |
| Final probe summary | 651 | 7e7d84c3b9f3b25c282dfb35b3a6a4a2f9e8e7fc8e35ca9079e4440dff3200e6 |

The logs/probe are local development observations. The public run links and
this retained diagnosis preserve the actual failures; the maintained tests retain
the regressions. After the frozen integration gate, publish these repairs,
integrate the separate standalone advance, and inspect the new hosted jobs.
A queued or running replacement job does not close these failures. Study and
replay workers must freeze the repaired dependency bytes in their own evidence.

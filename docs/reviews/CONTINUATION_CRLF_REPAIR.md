# Continuation checker CRLF repair

Root integration record, 2026-11-13 UTC. This repair is not an additional
worker assignment. The original sixty and the continuation sixty remain separate.

## Observed hosted failure

Published candidate `6bdce067ecdfa2b918113e254ed0ae706fdc9b43`, tree
`6f7948c1cc83945f2ca872b96e668de3796cf8a5`, passed all 46 local Release suites.
Hosted [run 43380337294](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294)
passed Linux GCC, macOS AppleClang and Linux ASan/UBSan/leak jobs. Windows MSVC
job `131736381912` passed 45 of 46 suites; only
`python_test_continuation_ledger` failed, with three failed methods and three
method errors among its twelve methods. The new renderer stdout regression and
all 35 renderer methods passed on Windows. No renderer or audio failure is
inferred from this independent accounting-tool defect.

Root fetched the complete Windows job log. Assignment 59 independently verified
the failed diagnostic archive: artifact `14016660801`, 33,714 bytes, SHA-256
`e9ac42bfdb7850632ed1a530325d2f680adcb8b4bff9d030903ee58db9a55ad1`.
Its complete LastTest log retains the actual failure. The final platform review
records all jobs separately; a failed run remains part of the evidence.

## Cause and bounded correction

The synthetic notes use `Path.write_text`, which writes CRLF on Windows. The
checker deliberately reads bounded raw bytes before UTF-8 decoding. That path
preserved CRLF; the owner-line regular expression captured a trailing carriage
return, while strict owner-value matching allowed only spaces and tabs after
the canonical identity. Correct logical owner lines were therefore rejected.

The raw per-file byte limit remains 128 KiB. After the bounded read and UTF-8
decode, the checker now normalizes CRLF to LF for logical-line matching. It does
not write the note, change ownership, promote completion, relax duplicate-owner
checks or consume either session's notes as the other's assignments. No native
runtime, header, renderer, profile, retained audio or build configuration changes.

The new permanent method writes explicit CRLF bytes on every platform for both
complete and running notes. It requires the correct two-complete/one-running
fixture counts, then adds a second canonical owner line and requires rejection.
This exercises ordinary Windows files without needing a Windows-only skip.

## Actual local evidence and remaining hosted gate

Before changing the checker:

```sh
python3 -B tests/test_continuation_ledger.py ContinuationLedgerTests.test_crlf_notes_preserve_identity_and_duplicate_owner_checks
```

The new regression exited 1 with an owner-line `LedgerError`, reproducing the
hosted failure on Linux. After the correction:

```sh
python3 -B tests/test_continuation_ledger.py
python3 -B tools/check_continuation.py --expected-complete 58 --json
```

All **13 methods passed**, zero skips, in 0.125 seconds. The actual manifest
reported 58 complete, two running, zero planned, sixty distinct dispatched
identities and 59 notes (the last readiness note was still a draft). A draft
note did not promote its assignment. Scoped whitespace checks passed.
Assignment 59 independently reproduced LF acceptance and CRLF rejection on the
frozen uncorrected checker, confirming the cause without using this regression.

The repaired source archive requires its own focused accounting/source checks
and guarded publication. The new hosted run must be observed before marking the
Windows failure resolved across platforms. Later final records may update the
[status](../STATUS.md), [session ledger](../development/2026-11-13-continuation/README.md)
and final platform review with that actual result.


## Observed hosted repair qualification

Repair commit `7469ebf759ced820cc34fc9012beff6f772e4b89`, exact tree
`096e2cd13c5aa3fc40e996c923ed80be36b0f622`, passed all four jobs in
[run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473).
Root fetched each complete job log and observed all 46 suites pass, including
accounting and renderer suites. Assignment 59 independently verified each
complete diagnostic ZIP against its GitHub byte length and SHA-256 metadata.
Every job executed 372 Python methods, including all 13 accounting and all 35
renderer methods, with zero failed/disabled/skipped tests. Linux/macOS/Windows
Release and Linux ASan/UBSan/leak checks passed; the sanitizer instrumentation and
actual leak-enabled environment were verified. The
[final platform report](FINAL_CONTINUATION_PLATFORM.md) retains exact job and
artifact identities. This resolves the observed Windows CRLF failure without
removing the failed run or extending the software evidence to physical fidelity.

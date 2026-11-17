# Header material portability conformance and local qualification

## Result

**The implementation exactly matches the frozen two-cast/hash-transition
admission, and both affected local CTests pass.** Independent inspection also
finds byte-identical genuine original/rebuilt fixture binaries, identical
48-case descriptions and identical actual numerical results except the two
admitted source-identity fields. Windows compilation remains the next hosted
gate at a newly published source; the original Windows failure is preserved.

The [frozen admission](HEADER_MATERIAL_WINDOWS_PORTABILITY.md) and its
[receipt](../development/2026-11-16-heading-title-continuation/reports/a53-header-material-windows-portability.json)
remain unchanged. This [separate conformance receipt](../development/2026-11-16-heading-title-continuation/reports/a53-header-material-windows-conformance.json)
records direct file comparisons, complete-report comparison and root's
execution receipts. A53 did not edit source, build or execute tests.

## Exact source scope

The C++ fixture now has SHA
`96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809`;
the active statistics test has SHA
`5f876087a4fea18acc46db16d4c1e7dba3a50e83d322ee6d835d16dd01e31e4f`.
These equal the complete proposed-byte identities frozen before root's edit.
The only changes are the two explicit float casts and the one exact active
fixture-hash literal. Both pre/post native-execution identity checks remain.

Independent hashing against the qualified 475-file input inventory finds
exactly those two changed source files; all other **473 code inputs** agree.
The historical comparator retains its original fixture pin and complete
original bytes. Production application SHA remains
`1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a`.
No workflow flag, numerical condition, expected result, workload or bound was
changed.

## Genuine binary, case and output comparisons

Root preserved the original executable before the edit. A53 independently
read that preserved binary and the rebuilt native fixture. Both contain
3,817,680 identical bytes, SHA
`5dca7e7d05ba1143fd740894b62a87056b96c8a471980fac1e792bbb269ca397`.
This is observed local binary equality, not a prediction about another
compiler's output.

The two actually executed `--list` outputs are byte-identical, each describing
all 48 cases, with SHA
`feba3c0358c376de2026a91fb419a9f741f8f31ad93062a907f1116cb1597558`.
The complete 430-byte default fixture result also matches the preserved
original. It still reports 48 cases, **10,542 checks**, **163 paintings**,
95 helper probes and the unchanged protection/repaint workload.

A53 recursively compared the complete original and new canonical statistics
JSON objects. Exactly two values differ:

| Field | Admitted change |
| --- | --- |
| `identities.frozen_fixture_source_sha256` | Original fixture identity → corrected fixture identity |
| `identities.test_source_sha256` | Original Python test identity → single-literal-transition identity |

Every other field and value is identical, including all **103 evaluated and
passing inequalities**, zero failures, exact errors, helper/state assertions,
reference identities and resource bounds. Canonical RGBA hash remains
`20eea493c5b2fe75c467a5964b54a28c832edf7639f034d8eb83daf4036d4557`;
canonical header hash remains
`1a7b0b316dc771428f2241eec9fbd25668ba337a6a2232b5787a2014f86eaaac`.
The comparison uses the complete 58,181-byte original report, not its truncated
JUnit representation.

## Executed local gates and remaining boundary

Root's [build receipt](../development/2026-11-16-heading-title-continuation/reports/windows-header-fixture-build.json)
records a successful rebuild in 20.032244 seconds. Its
[affected-test receipt](../development/2026-11-16-heading-title-continuation/reports/windows-header-affected.json)
and JUnit record both `test_standalone_header_material` and
`test_standalone_header_statistics` passing, **2/2 in 43.593519 seconds**.
The statistics test still performs one actual native invocation with its
20-second child limit and every original criterion.

These results establish the admitted local correction without changing the
production application. They do not change original `fba1911` CI conclusions
or prove MSVC compilation after repair. Root must publish the correction
without discarding concurrent work, then inspect the new exact-source Windows
job through compilation, native tests and packaging. Other original hosted
outcomes remain attached to their original source. Physical devices, displays,
native accessibility and literal whole-interface reference parity remain
separate qualification work.

# Header material Windows portability admission

## Decision and original failure

**Admit only two explicit float conversions in the native header fixture,
plus the corresponding single exact fixture-hash transition in its active
statistics test.** This is a frozen source review before implementation.
Root owns the edit, numerical comparison, builds, tests and later publication.
Warning policy, production code, all fixture workloads and all numerical
acceptance criteria remain unchanged.

At published commit `fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`, standalone
run `44016021554`, attempt 1, Windows job `133814025240` failed in its aggregate
build. MSVC reports C4244 at `test_standalone_header_material.cpp` line 156,
columns 34 and 71: the two conditional integer results are assigned to float
members. `/W4 /WX` converts the warnings into C2220. Native discovery/tests,
compiled MIDI verification and installed-package qualification were not reached.

The original [compile failure](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814025240-compile-failure.log)
and [build summary](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814025240-build-summary.log)
retain exact bounded job-log segments. The [job receipt](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814025240.json)
records metadata and the complete decoded-log identity. No retry occurred.

## Precise proposed correction

Replace the existing pair of assignments, retaining their location and loop:

```cpp
c.width = static_cast<float>(shape == 0 ? 1920 : 1400); c.height = static_cast<float>(shape == 0 ? 820 : 1080);
```

Both conditional expressions still select the same `int` values. The explicit
built-in conversion performs the same integer-to-float conversion already
required by assignment. It changes neither evaluation order nor the selected
values. All four values are exactly representable binary32 integers.

| Shape | Width | Height | Affected cases |
| --- | ---: | ---: | --- |
| 0 | 1920 | 820 | 9 and 10 |
| 1 | 1400 | 1080 | 11 and 12 |

The existing scale loop still supplies 0.75 and 1.25. The other 44 cases,
including fractional and 8192-dimension/resource cases, are byte-for-byte
untouched. The fixture's float-format assertion, rounding helpers, 48-case
matrix, binary protocol, drawing, probes, history checks, oracle assertions
and invocation workload remain unchanged. Exact selected values preserve
downstream mathematical inputs; root must still compare the actual case and
numeric outputs rather than report an unexecuted binary-equivalence claim.

## Exact identity transition

The [portability receipt](../development/2026-11-16-heading-title-continuation/reports/a53-header-material-windows-portability.json)
records the proposed complete-byte identities and narrow diff.

| Source | Original SHA-256 | Proposed SHA-256 |
| --- | --- | --- |
| C++ fixture | `a6b65d06067d8941e44ef8680f309433a3c82ce1d6bd54d6f3f5bf8d4bde82d2` | `96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809` |
| Active Python statistics test | `f3ee5b2fba5f7216be673f0bd551d9206a2e3ffbbb1f673a7015f47d8d5ad509` | `5f876087a4fea18acc46db16d4c1e7dba3a50e83d322ee6d835d16dd01e31e4f` |

After the corrected C++ bytes are frozen, replace only the active statistics
test's `FIXTURE_SHA256` literal with the proposed C++ hash above. Its exact
fixture checks before and after native execution remain present and unchanged.
No old/new allowlist, bypass, optional identity check, threshold change,
expected-result change or new test exemption is admitted. If root chooses
different formatting, recompute and independently bind its exact bytes before
updating that literal; the listed proposed hashes then no longer describe it.

The historical `tools/compare_header_material.py` pin remains the original
`a6b65d…` identity. Preserve that entire comparator and all older comparison,
admission and output records. Historical reproduction uses its admitted old
source view, as it already does for its older `main.cpp` pin. Do not redefine
old evidence as a run of the corrected fixture.

## Acceptance and limits

A53 verified the two replacements in memory against the exact published Git
blobs, their selected binary32 values, reversibility and the single Python
literal change. No source file, executable or workflow was changed or run.
Root must verify all 48 actual case descriptions and numerical output
equivalence, run the native header-material and header-statistics CTests under
their unchanged criteria, and keep production binaries unchanged. A fresh
guarded publication must then demonstrate actual Windows compilation with
the original warnings-as-errors policy and reach the previously blocked gates.

The five other original standalone jobs continue against `fba1911`; their
outcomes remain evidence for that source. This admission neither repairs their
history nor establishes a new hosted pass, physical/display acceptance, or
whole-interface parity.

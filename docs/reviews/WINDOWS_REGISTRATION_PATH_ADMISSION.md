# Windows registration path normalization repair

16 November 2026; root integration following exact-source hosted evidence.
The first published implementation is `20739f6280b95e567e84615d5c5aee443fc3b93d`.
Its Windows MSVC core job, `133294777970`, failed the unchanged required
`ProtectedPath` assertion for ambiguous native spellings in
`test_standalone_registration_library.cpp`. The decoded original provider logs,
including original line endings, are retained in the
[failure receipt](../development/2026-11-16-preset-library-continuation/reports/first-ci-failure-logs.json).
Linux Release and sanitizer failures at that revision concern the separate
copied-audition Markdown links, already repaired without changing those gates.

## Cause and bounded change

Inspection found the ambiguity checks in both `identify_path` and `resolve_root`
occurred only after `absolute`/`weakly_canonical`. Microsoft's
[path-normalization documentation](https://learn.microsoft.com/en-us/dotnet/standard/io/file-path-formats#path-normalization)
describes trimming periods/spaces and resolving exact `.`/`..` navigation.
Its [Win32 canonicalization reference](https://learn.microsoft.com/en-us/windows/win32/api/pathcch/nf-pathcch-pathcchcanonicalizeex)
also documents the trimming behavior. Together with the hosted assertion, this
supports the diagnosis that normalization could erase the spelling the guard
intended to reject; no separate Windows tracing experiment is claimed.

Root moved an additional check of the caller's requested spelling ahead of
normalization at both entry points. Existing resolved-path checks remain.
The helper exempts only exact `.` and `..` navigation components. Other trailing
periods/spaces and colon-containing components remain ambiguous. Root resolution
retains `InvalidRoot`; protected-path admission retains `ProtectedPath`.
The whole-ASCII-component distinction proof, conservative Unicode uncertainty,
native equivalence, ancestor/suffix checks, create-only publication, authorization
and public API are unchanged. This does not broaden supported Unicode aliases.

A43 independently reviewed and admitted the bounded proposal before root's
implementation: [proposal receipt](../development/2026-11-16-preset-library-continuation/reports/a43-windows-path-proposal.json).
The original three Windows refusal cases remain. Additional cases cover `...`,
`. ` and `.. `, raw ambiguous roots, zero authorizations, unchanged recursive
inventory/protected bytes and absent staging. Positive cases send raw `.` and
`..` through both root and protected-path entry points; they must save exactly
the literal expected bytes with one authorization. No test was skipped or
relaxed to accommodate the failure.

## Qualification and limits

The [source/build receipt](../development/2026-11-16-preset-library-continuation/reports/w08-windows-guard-source.json)
binds both changed files, original build/test logs and executable comparisons.
Root rebuilt the complete Linux configuration, then six affected CTests passed
in **11.33 seconds**: native registration storage, both CLI suites, generator,
independent pack oracle and actual native starter Load. All three Linux tool/app
binaries remain byte-identical to their previous qualified versions, including
the frozen gallery executable. This is Linux qualification, not execution of
the conditional Windows test body.

The earlier 235-test run and focused documentation repair retain their actual
outcomes and source identities. Exact published Windows execution must qualify
this repair; hosted status at an earlier or local-only revision cannot do so.
No sound state, renderer algorithm, painting geometry, reference pixels, package
payload or physical/UI acceptance criterion changed in this repair.

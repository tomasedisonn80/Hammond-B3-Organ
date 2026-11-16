# Registration CLI contract admission — A10

16 November 2026. Independent source review of
[the proposed contract](../REGISTRATION_CLI_CONTRACT.md), SHA-256
`60f2069263507aee74c48efe5a322f7747b09963ca090435ae53bf2d5c2458fe`.

**Disposition: implementation-ready after the two narrow amendments below are
recorded.** The proposed operations fit the existing public APIs. No change to
musical state, storage semantics, browser ownership or acceptance scope is needed.
This is contract admission, not an implementation or executed-test result.

## Source findings

Reviewed complete `AGENTS.md` and `docs/PLAN.md`, the current session records,
[`RegistrationLibrary.h`](../../apps/standalone/RegistrationLibrary.h), its
[implementation](../../apps/standalone/RegistrationLibrary.cpp),
[`ControlStateIO.h`](../../include/hammond/ControlStateIO.h), its
[implementation](../../src/ControlStateIO.cpp),
[`ControlSnapshot`](../../include/hammond/ControlState.h) and
[`CliArguments.h`](../../tools/CliArguments.h).

1. **Arguments and scope are feasible.** The longest command, Registration
   materialization with five option/value pairs, uses exactly 12 arguments
   including executable and verb. Scope-dependent `--current` checking necessarily
   follows selected-entry admission, but still precedes any mutation. Exact suffix,
   ASCII name validation and explicit destination scope agree with the library.
   Registration import retains saved expression; Registration materialization
   replaces only expression from the current snapshot. Performance takes the whole
   entry. `merge_registration_controls` supplies exactly those semantics.

2. **Catalog admission is essential and correctly specified.**
   `read_registration_entry` alone does not detect case ambiguity. The scanner
   marks every same-scope case-colliding row `Ambiguous`, even an exact spelling;
   requiring a complete scan and a `Valid` exact key closes that gap. Missing and
   empty directories are complete read-only results; overflow/unavailable scans
   clear partial rows. The 128-candidate and 512-item bounds include the specified
   invalid-name candidates and unrelated directory items.

3. **Shared arbitrary-file input is an appropriate new boundary.** The proposed
   helper can retain the library reader's handle checks, nonblocking POSIX open,
   leaf-link rejection and 16,385-byte growth detection without copying musical
   grammar. Preserve the leaf while resolving its parent. On Windows, reject device
   and pipe namespaces before opening, then inspect the handle. Only the existing
   parser admits state versions, catalog identity, retained fields and migrations.
   Extracting the successful header's version afterward is provenance, not a new
   parser. Transactional destination replacement is implementable.

4. **Native path reports preserve identity.** Hexadecimal native bytes/code units
   avoid lossy narrowing, including non-UTF-8 POSIX ancestors. JSON diagnostic
   repair is separate: the existing library bounds reasons by raw bytes and can
   split UTF-8, so the CLI must sanitize and re-bound every imported reason before
   JSON escaping. This does not require changing the library.

5. **Authorization and publication match the writer.** Default snapshot equality
   includes expression and every retained field; scoped equality deliberately
   ignores Registration expression and is unsuitable for source revalidation.
   Repeat complete source admission and exact-key reread at authorization, retaining
   captured report data on denial. Protect original and resolved-parent input
   identities through the existing conservative alias checks. The writer checks
   root, output and staging paths, stages privately, authorizes immediately before
   no-replace publication, and retains `committed_entry` after a successful commit.
   Never retry or delete a committed output automatically.

## Required amendments before freeze

### R1 — distinguish admission from post-commit refresh

The final sentence, “Incomplete catalogs never qualify as successful,” conflicts
with the documented `SavedWithWarning` policy. The existing writer returns that
status when publication succeeds but its refreshed catalog is incomplete.

Replace the sentence with: **“An incomplete catalog cannot authorize a read
selection or publication. An incomplete post-publication refreshed catalog retains
`SavedWithWarning`, `committed: true`, the committed entry and exit 1.”** Preserve
the actual failed refreshed-catalog status inside `save.refreshed_catalog`.

### R2 — keep Windows argument failures inside the report contract

`hammond::cli::run_windows` catches count/conversion failures, prints plain stderr
and returns 1 before entering the tool. Reusing that wrapper would violate the
one-object stdout envelope and UsageError/2 policy.

Require a **local registration Windows entry adapter** that strictly converts
UTF-16 user arguments and routes invalid encoding, argument-count and byte-limit
failures through the same JSON `UsageError`/exit 2 reporter. Use `command: null`
when no valid command is available. Unexpected adapter exceptions use the existing
`InternalError` policy. Do not alter the shared wrapper or narrow the JSON promise.

## Implementation dispositions within the existing acceptance

Keep status mapping explicit: catalog `InvalidRoot`/`CapacityExceeded` are exit 3;
`DirectoryUnavailable` is exit 4. A selected entry's `Unavailable` and arbitrary
input `InputUnavailable` are exit 4; invalid payload, nonregular, oversize,
ambiguous or missing selection are exit 3. An unrelated unavailable row remains a
catalog warning. Save collision/protection/authorization refusals are exit 3;
staging/write/flush/close/commit failures are exit 4. Define malformed `--key`
syntax consistently at the argument boundary; `UsageError`/2 is recommended,
while a valid absent key remains `NotFound`/3.

POSIX broken-pipe handling must prevent default SIGPIPE termination so the stated
`ReportFailed`/5 path is observable. Pre-reserve report capacity before saving;
retain known publication if reporting subsequently fails. These are consequences
of the proposed contract, not additional gates. Existing subprocess, mutation,
alias, committed-warning and platform requirements are sufficient; none was run
for this review.

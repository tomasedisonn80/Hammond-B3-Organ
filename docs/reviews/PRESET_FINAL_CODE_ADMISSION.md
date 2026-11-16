# Final registration code admission — A56

16 November 2026; actual worker `/root/w10_a56`, wave 10. **The reviewed
implementation is admitted within the source and retained-evidence scope below;
no remaining concrete code defect was identified.** This independently reviews
the actual final implementation, rather than only the earlier Windows proposal.
Exact local HEAD is published `cc6be852d616ec5887485e3fccc39ddb1db22006`, tree
`201e38b05901fa30e3d053b9c245829818a5b52e`. Later documentation is an uncommitted
overlay. The [machine audit](../development/2026-11-16-preset-library-continuation/reports/a56-final-code-audit.json)
records individual input hashes, Git comparisons, binary and retained-output
identities, and the inspection boundary. No build, unit test, full suite,
render, capture or provider-status query was performed by A56.

## Windows repair: actual control flow and regression strength

In [RegistrationLibrary.cpp](../../apps/standalone/RegistrationLibrary.cpp),
`identify_path` now checks `ambiguous_native_path(requested)` before either
`absolute` or `weakly_canonical`. `resolve_root` does the same before normalization
and preserves `InvalidRoot`. Both retain the existing resolved-path check.
The helper excludes only exact `.` and `..` navigation; other trailing periods,
trailing spaces and colon-containing relative components still refuse.
Protected-input failure therefore remains `ProtectedPath`, while an ambiguous
library root remains `InvalidRoot`. The CLI first passes its retained invocation
spelling through the public root resolver and protects both invocation and
resolved-parent input paths; its own preparation does not bypass the new check.

The [final native tests](../../apps/standalone/tests/test_standalone_registration_library.cpp)
retain `ambiguous.`, `ambiguous ` and `ambiguous:stream`, and add `...`, `. ` and
`.. `. Each protected-path case requires refusal without commitment, zero
authorizer calls, no output and no staging directory. Each raw-root case also
checks catalog/save status, unchanged recursive inventory and protected bytes.
The two positive cases pass raw navigation through both entry points, require
one authorization, compare the complete saved bytes to the literal document,
and preserve protected bytes with no staging residue. These assertions strengthen
the old failing gate without skips or reduced expectations.

The whole-ASCII-component proof remains conservative: both corresponding
components must be entirely ASCII before a folded difference can prove
distinction. Otherwise the prior native-unit comparison retains Unicode
uncertainty. Native equivalence, existing-ancestor/suffix comparison and unresolved
link refusal still follow. Tests retain composed/decomposed and case-variant
uncertainty, canonical aliases and unchanged protected data. Distinct Unicode
siblings can still be refused; the documented ASCII `inputs`/`outputs` layout
does not promise universal Unicode equivalence handling.

The [repair receipt and original log](../development/2026-11-16-preset-library-continuation/reports/w08-windows-guard-source.json)
retain six affected Linux passes in 11.33 seconds. Fresh hashes confirm the
CLI, renderer and application still match all three recorded Linux binaries.
That evidence does **not execute or qualify the conditional Windows body**.
Root's separate [provider observation at 12:54:48 UTC](../development/2026-11-16-preset-library-continuation/reports/followup-windows-step-observation.json) records that exact-head
Windows job `133307538161` passed its full Release CTest and actual Unicode
generator steps. A56 did not independently query those results. Job archival,
native Windows and all-platform completion are separate from that step snapshot.

## Shared input, scope and source compatibility

Both tools call the same [ControlFileInput](../../tools/ControlFileInput.cpp)
implementation. It opens the supplied leaf before resolving ancestors, rejects
special Windows namespaces before opening, checks the opened file type, uses
no-follow/nonblocking POSIX admission, reads at most 16,385 bytes and reports
close errors. Only the successful core parser/writer produces a replacement
destination; failures preserve the original destination and versions 1–3 keep
their existing migrations.

The [CLI](../../tools/registration.cpp) requires a complete catalog, an exact
valid key, a fresh selected read and full-snapshot equality. Final authorization
revalidates both input spellings and repeats source catalog/read admission;
Registration expression is included in those comparisons. Materialization uses
the existing merge helper: only current expression survives for Registration;
Performance restores the full entry. The [renderer](../../tools/render.cpp)
restores the complete snapshot at clock zero, skips default setters on that
branch and applies score events afterward. Schema 6 records the initial canonical
snapshot; suffixes do not change generic restoration semantics.

Independent Git comparison finds the entire `include`, `src` and `plugins`
trees identical to session base `54df95f`; the registration public header and
all pre-existing data files also match. Thus the reviewed change preserves
47 parameter identities, `B3CONTROLS4`/readers 1–3, 91 shared free-running sources,
plugin UUIDs and nominal dry Engine ownership. Fresh byte comparison of the two
retained baseline/candidate WAV and stdout pairs confirms their original equality;
this adds no new render or universal audio-equivalence claim.

## Failure reporting, installed provenance and CI

The [audition helper](../../tools/audition_starter_registrations.py) catches
aggregate-report failures separately, identifies the failed filename and retained
directory, and reports both aggregate files' observed presence/completeness.
It returns failure without retry, deletion or rewriting a completed manifest.
The isolated regression class covers absent/partial failures for both reports
and truthful partial-WAV wording. Its retained two-method qualification remains
separate from original 32-clip evidence.

[Registration installation](../../cmake/InstallRegistrationTools.cmake) uses
explicit excluded components: two tool/guide files and exactly 24 literal
payload names plus two metadata files. Preflight refuses existing destinations,
bad inputs and disallowed ancestors before copying. It runs no generator or
renderer; sequential copying can retain partial output. The
[standalone installer](../../cmake/InstallStandalone.cmake) separately includes
the apron manifest and schema-1 `reference_apron` provenance while preserving
historical `reference_art`. Its configured-hash preflight, notices and tests
retain exact inventories of 17 files with MIDI disabled and 21 enabled.

The actual workflows require all twelve registration/apron core suites before
unfiltered Release/sanitizer execution. Native Release explicitly requires the
three apron gates and real starter Load command/binaries. Native sanitizer
discovery remains exactly 28 gates, including instrumented fallback Drawing;
the original six calibration-probe archives remain separately required.
The Windows Unicode step retains actual generator compilation, `/utf-8`, exact
source-root definition, 24-file equality and zero-attempt source protection.
Its ASCII-separated branches accommodate the admitted conservative policy
without bypassing those checks. These are configured requirements, not new
hosted passes.

The [original integrated result](../development/2026-11-16-preset-library-continuation/reports/w07-integrated-qualification.json)
remains **234/235**, followed by the separately passing report-link repair.
Original audition/archive hashes and logs remain intact. Physical fidelity,
literal whole-interface 1:1, devices/hosts, callback deadlines/retirement,
native accessibility, rights and signed distribution remain open. Root must
complete exact-source hosted observation and documentary publication; this
source admission closes none of those independent gates.

# Console integrated qualification admission

A42 · `/root/w07_a42` · 17 November 2026 UTC · independent read-only audit.

**The recorded all-target build and bounded local passes are supported. The first
full CTest run remains FAILED: 246/247, exit 8, 1,005.02 seconds.** There is no
247/247 rerun in this admission. Root retains acceptance, the subsequent affected
documentation gate and publication. The [audit record](../development/2026-11-16-console-completion/reports/A42-integrated-audit.json)
retains input hashes, reconstructed counts, exclusions and source boundaries.
This admission ends at the **pre-reconciliation overlay** recorded in those
receipts. Subsequent remote advances and any combined source require separate
review and affected qualification.

## Executed evidence

| Evidence | Independently checked outcome | Scope |
| --- | --- | --- |
| [All-target build](../development/2026-11-16-console-completion/reports/integrated-build-result.json) | Exit 0; all 127 numbered build steps occur once, in order | Ordinary Release Linux, GCC 14.2, SDL 2.32.10; MIDI/VST3 disabled |
| [First full CTest](../development/2026-11-16-console-completion/reports/integrated-first-ctest-result.json) | 247 discovered, enabled and executed; 246 passes, one failure, zero disabled or skipped registrations | 69 core, 107 Python and 71 standalone registrations; internal exclusions below remain |
| [Five library suites](../development/2026-11-16-console-completion/reports/library-integrated-result.json) | Focused 5/5 in 0.12 seconds; identical complete suite outputs also occur in the full run | Copied-model/public-API fixtures plus real Session and storage harnesses |
| P1 ordinary / numerical gates | Ordinary: 34 cases, 53,648 checks, 111 paintings. Numerical: 191 checks, zero failures, all 62 frozen screens pass | SDL software surface and canonical candidate-only validation |
| [P1 source-transition Python](../development/2026-11-16-console-completion/reports/p1-source-transition-result.json) and [finite-JSON Python](../development/2026-11-16-console-completion/reports/capture-finite-json-result.json) | Each focused log contains 45 passing methods; each full-run CTest independently reports the same 45-method pass | Exact current comparator/capture source and test hashes |
| [Distinct SDK-free admission](CONSOLE_HEADLESS_ADMISSION.md) | First configure and 68-step build pass; first exact selection passes 12/12 in 5.69 seconds | Separate ordinary Linux configuration; not a second full suite |

Every [JUnit testcase](../development/2026-11-16-console-completion/reports/integrated-first-ctest.xml)
was parsed and compared with discovery, the concise log and the
[complete detailed log](../development/2026-11-16-console-completion/reports/integrated-first-ctest-detail.log).
All 247 names are unique, their order agrees, every executed command matches
discovery, and all statuses agree. The suite has one failure node, no error or
skipped nodes, and no disabled discovery property. JUnit's whole-second `1005`
and per-case sum of 1,004.84224617 seconds are consistent with the retained
1,005.02-second external CTest total. Numerical output truncated in JUnit was
read in full from the detailed log, including every one of the 62 screen results.

The library detail preserves the distinction between 32 model groups / 3,250
assertions; 12 real-Session groups / 42,634 assertions; nine real-filesystem
groups / 1,115 checks with synthetic control proof; nine public-API recall groups /
743,728 assertions with synthetic observations; and four real combined journeys /
1,489 checks. The combined journeys report 138 snapshots, 20 renders, 24 posts,
24 reports to each model, and seven storage/authorizer calls. These harnesses
do not implement the native browser or its `main.cpp` wiring.

## Preserved failure and exclusions

The sole failed registration is `python_test_repository_integrity`. Its 41-method
inner suite reports one failure: A33's note linked `A33-native-next.json` before
that report was written during concurrent authoring. The raw failure names only
that missing link. The [report now exists](../development/2026-11-16-console-completion/reports/A33-native-next.json)
and matches retained SHA-256 `7338155b1c2f2c57b945a1e7ab3e505b6348e5f28ebf4365bc2f1da1539892ce`.
The gate's recorded minute is 16 November 21:42 MST, or 17 November 04:42 UTC;
the report's current modification time is 04:43:49 UTC. This corroborates the
sequence without replacing the original failure. Presence of the report does
not constitute a passing rerun. Root should run the affected documentation gate
after documents are complete and record that result separately.

Zero skipped **CTest registrations** does not mean zero skipped Python methods.
The passing `python_test_capture_audio_admission` reports two skips and
`python_test_contact_switching_io` one. Their default unittest order and static
method inventory map the progress markers to the Windows reparse fixture and
two native Unix-socket fixtures. The nonverbose streams omit the exact socket
exceptions, so no particular OS error is asserted. The state-file suite also
explicitly leaves POSIX failed replacement after a complete temporary write
untested because it lacks a deterministic non-racing fixture. The state-file
exclusion also appears in the headless run.

## Source continuity and qualification limits

The base commit is `9d60dbf462a90fe422fd4e69757fe202264acb7c`; the qualified
working additions require their recorded hashes. All 174 native/source identity
references, covering 161 unique files, matched bytes at this audit's readback. This includes the
changed model/helper/painter, five library tests, comparator/capture tools and
tests, build/workflow wiring, and the broader application/core/data inventory.
The audit also passes 160 retained-artifact and headless-source hash checks,
including all 112 headless source inputs and all sixteen command-stream receipts.
No evidence-integrity inconsistency was found. This is recorded build/source
continuity, not an independent rebuild or a hermetic dependency attestation.

The headless evidence independently contains 50 strict C++20 compile commands,
nine support objects with MIDI disabled, 531 dependency paths with no SDK hit,
and twelve links using the support/core archives. ELF readback names only the
normal C++/C, math and GCC runtime libraries. Its initial report-inspector failure
is preserved; the subsequent reader used an already retained CMake hash and
did not alter or rerun the passing build/tests.

The [final capture receipt](../development/2026-11-16-console-completion/reports/integrated-capture-result.json)
records fifteen successful scale-3 views and unchanged recorded inputs. All 69
manifest entries and the provenance/manifest hashes match. The app identity
`7f8996cdd062907a8ad4f47021a32ef28a5f5b9753ac9bf7b16cc4849dc77ba3`
agrees with the integrated application receipt. A42 reviewed metadata only;
independent final image inspection belongs to A46.

The P1 candidate-only gate admits the exact reviewed recall source pair; it
does not rerun historical paired preservation, timing or H1/T3 source-pinned
comparisons. Ordinary Linux software/dummy outcomes do not establish hosted
Windows/macOS, native MIDI/VST3/DAW, ASan/UBSan, real display/audio/controller,
callback-deadline or OS callback-retirement acceptance. Native accessibility,
physical fidelity, signed release and **literal whole-interface 1:1** remain
unqualified. All M0–M9 exits and compatibility identities remain binding.

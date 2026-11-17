# Array writer successor verification

## Current state

Candidate source **ea02c5465b6c6a896cbbc83b55479d6f62bbf8c9** has passed
its focused Windows qualification. Root's guarded read then found concurrent
main commit cf87a587d0002d106e5210b57a39fd1967245a8f, and root did not update
main. Reconciliation is in progress. No final source or full main-source matrix
has been released to A53, so no full-matrix acceptance is claimed.

The [source audit](source-audit.json) independently binds tree
e46c65173517956d6eda69086f4ee428aeae8782 and parent
6287055a111dc4e2747564da3d48edc9b65e2e3e. Exactly four of 475 frozen inputs
change: the two fixture-only array writers and their active reader identity
literals. The other 471 inputs, production code, CMake/workflow, preset
workload and all bounds remain unchanged. Both writers now iterate explicit
bounded indices. The strict Python comparisons, expected fields and numerical
criteria retain their existing semantics.

Root's [affected Linux qualification](../../windows-array-local/qualification.json)
passed all four existing affected tests once in 47.554 seconds. Independent
read-only inspection confirmed equal complete retained before/after headers
and all recorded inventory, stdout and pixel identity fields. This local
evidence remains separate from Windows execution.

## Focused Windows result

[Run 44031603512, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44031603512)
and job 133864634092 succeeded on actual runner GitHub Actions 1000001444.
Workflow commit 894b6246fda3a26b92c5673619eb2e21f743769b explicitly checks
out the candidate source. Its published workflow SHA-256 is
45357216d41025d882b47296d328f0053965f16844807239ab9a2376499efdad.

The [frozen focused receipt](focused-windows.json) records both unchanged
CTest commands passing: title density in 2.56 seconds, header statistics in
0.37, with 2.95 seconds total. All 18 title cases and all 103 numerical header
criteria pass. Both additional bounded captures report successful unchanged
protocol parsing, empty strict differences, no capture errors, zero exit
status and empty stderr.

The complete captured case0 header has 59,719 bytes and SHA-256
ed941d4d8096bfabfc9b56454e9bf98e1c07fce11a97dc1b6542e41e3230704f;
case46 has 231,432 bytes and SHA-256
eefcf5c0fba5fdb77b4fbcc878c4a4cf9fd0d7855e979de24478ae5fb8efc273.
These header identities and both RGBA identities match the retained Linux
candidate records. The final provenance check verifies the exact candidate,
554 unchanged selected source inputs and CTest exit zero. This diagnostic
scan has its own selection, distinct from the 475-input qualification manifest.

The complete original Windows log is retained as deterministic gzip,
preserving CRLF: 323,463 decoded bytes in 57,063 stored bytes. Hashes,
round-trip equality and bounded excerpt membership are verified. Artifact
metadata is retained; root owns direct artifact download and member inspection.

## Preserved boundaries and next step

The [original six-job outcome](../../a53-helper-standalone-hosted.json) and
[original-source diagnostic](../windows-original-diagnostic-run-44029895588.json)
remain frozen. Their failed Windows predicates are not relabeled. The new
candidate's observed complete arrays and successful strict readers qualify
this focused execution; no compiler-mechanism claim is made.

Root must first reconcile and qualify the concurrent source and release the
resulting exact revision. A53 will audit that revision and its required test
inventory before observing the full standalone matrix, packaging, instrumented
lifecycle post-checks and final source/dependency verification. The candidate
workflow currently specifies 68 normal tests and 34 sanitizer gates; their
scope is not transferred to an unreleased successor.
Physical devices, real displays/DPI, native accessibility and literal
whole-interface 1:1 remain unclosed.

This is the same accepted A53 follow-up. No project build/native/test execution,
CI retry, source/workflow edit, remote mutation or new worker credit was
performed by A53.

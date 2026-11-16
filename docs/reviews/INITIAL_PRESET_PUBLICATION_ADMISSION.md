# Initial preset-library publication admission

16 November 2026; A42 (`/root/w07_a42`), wave 7. **First publication admitted;
hosted qualification remains open.** This review concerns the first implementation
tree only. Its final metadata observation is recorded below and in the
[hosted receipt](../development/2026-11-16-preset-library-continuation/reports/a42-first-hosted.json).

## Independently verified publication

| Identity | Value |
| --- | --- |
| Reviewed local commit | `d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93` |
| Published commit | `20739f6280b95e567e84615d5c5aee443fc3b93d` |
| Identical complete tree | `1e59776459a05a9d934d0b519a45cd4c61b13ae9` |
| Sole parent | `54df95fe343d417dd89bb7a91f85e4f51c08dfe7` |

The initial independent ref GET still observed the parent before publication.
After root's publication notification, independent GitHub GETs observed the
published SHA on `main`, the expected immutable commit/tree/sole parent, and an
untruncated tree. All 21 root entries, including mode, type and object identity,
match `git ls-tree` of the reviewed local commit. Their matching subtree hashes
bind the complete reviewed content. Connector author/time metadata explains the
different commit SHA; the source tree is identical.

The [independent receipt](../development/2026-11-16-preset-library-continuation/reports/a42-first-publication.json)
retains these provider responses and checks. Root's separately retained
[publication receipt](../development/2026-11-16-preset-library-continuation/reports/first-publication.json),
SHA-256 `caae45770dd03c0837d1603330cb49d08bff7121a72e7f566cc2ba4d11c1ac05`,
records fresh before/after refs, the expected parent, `force: false`, and successful
update. Those mutation mechanics are attributed to that receipt; A42 made GETs
only. The shell credential failure and two timed-out inline-tree attempts remain
recorded separately. The successful recovery used immutable blobs and the exact
SHA-only tree before the ordinary ref update.

## First-tree workflow coverage

All three workflow blobs are unchanged from the parent. Their hashes, expanded
names, runner labels, triggers and timeouts are in the
[source inventory](../development/2026-11-16-preset-library-continuation/reports/a42-first-source-workflows.json).
Coverage below is established by source inspection, not inferred test results.

| Jobs | Configured coverage |
| --- | --- |
| Three core Release jobs and one Linux core sanitizer job | Build all preset inputs and run unfiltered CTest with `--no-tests=error`; CMake registers the new CLI, reader, renderer-controls, generator, oracle, audition, install and apron-tool suites. |
| Four native Release jobs | Build the standalone aggregate and run `^test_standalone_`; the three new apron executables are included and selected. The old required-name assertion does not explicitly name them. |
| One native Linux sanitizer job | Retains its exact earlier 25 test-to-target pairs. The three targeted apron gates are absent from that selection. Existing instrumented drawing tests do not replace those gates. |
| One full R4 and three native VST3 jobs | Preserve their existing independent waveform, native validator, test and packaging selections. No registration-specific acceptance is inferred from them. |

Thus the expected matrix is **13 jobs**: CI 5, Native standalone 5, Native VST3 3.
All workflows use push-on-main and cancellation by workflow/ref. A successor can
cancel unfinished first-commit work without supplying a first-commit pass.
Optional Pillow source decoding and NumPy pixel comparisons may skip; these
workflows install neither dependency, so a suite result cannot imply execution
of every optional comparison.

## Hosted observation and remaining gates

At the initial job snapshot, **12:24:04 UTC**, all 13 expected jobs matched the
published SHA: ten were running and three macOS jobs were queued without runners.
The [compressed original responses](../development/2026-11-16-preset-library-continuation/reports/a42-first-hosted-initial-raw.json.gz)
retain that observation independently of any later outcome.

The final A42 observation, **12:26:19–12:26:20 UTC**, found **two successful jobs,
eight running and three queued without runners**. Linux and Windows native VST3
are the two successes; the macOS job in each workflow remains queued. CI has four
running jobs and native standalone four. Every expected name and every run/job
head SHA matches. There are no observed failed steps to investigate. The run-list
endpoint still reports all three workflows queued with null conclusions; its
values and the separate job statuses are preserved without reinterpretation in
the [final original responses](../development/2026-11-16-preset-library-continuation/reports/a42-first-hosted-final-raw.json.gz).
These are provider metadata observations. No completed workflow, individual test
count, inspected package artifact or all-platform success is claimed.

A37's explicit discovery, Windows Unicode source-root check and native sanitizer
expansion to 28 gates, together with A36/root starter Load wiring, belong to the
unpublished follow-up overlay at this review. Later audition and installer fixes
also require their own published identity and qualification. A59 owns final-source
CI closure. Re-query every required job at that source and retain any failures,
cancellations or unacquired runners. This audit does not close physical fidelity,
whole-interface 1:1, device/host deadlines, or native accessibility.

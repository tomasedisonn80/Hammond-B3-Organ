# A29 — Hosted gate wiring and bounded Ubuntu setup

## Scope and source

Owned `.github/workflows/standalone.yml`, this note and the two A29 reports.
Reviewed `AGENTS.md`, the current scope/checkpoint/manifest, complete M0–M9
plan, CMake/presets, both workflows, and retained pending/material/sanitizer
evidence. Base HEAD is `e4968b2acd37b6f79683704356350070fe2fc329`; this
review covers the shared changed source identified by SHA-256 in
[the workflow report](../reports/A29-workflow-review.json).
No product/CMake files, musical identities, historical records, commits or
remote jobs were changed by A29.

## Changes

The native sanitizer job explicitly builds and discovers **16** unique gates,
adding `test_standalone_reference_layout`,
`test_standalone_inspection_raster` and
`test_standalone_material_acceptance` to the original thirteen. Ordinary
native acceptance also explicitly requires these names. All instrumented-object,
archive, link-runtime, exact-set, built-command and disabled/environment-override
checks remain. ASan/UBSan halt behavior, leak detection and LSan exit code 23
are unchanged. Existing 180/360/300-second sanitizer raster limits remain;
pending/material retain their actual 60-second CMake limits with new explicit
workflow assertions, agreed with root. A18/A26 report ordinary runtimes of
0.61/4.00 seconds; no unmeasured deadline increase was made.

Both Ubuntu header steps now have an eight-minute step limit, three acquisition
retries, 30-second HTTP/HTTPS timeouts and a 60-second package-lock wait.
Repository-refresh errors are fatal. Package lists, backend requirements,
dependency verification and retained logs remain; effective apt options are
also retained. This bounds a failed setup while allowing the existing
`always()` diagnostic-upload step.

## Observed hosted state

[API evidence](../reports/A29-hosted-observation.json), observed at
21:04–21:05 UTC on 14 November 2026, confirms **11 successful / 12 jobs** for
the existing head. Native run `43637781292`, Linux MIDI ON job
`132578323599`, remained in header installation. The job started at
20:29:51 UTC; the installation step started at **20:30:01 UTC**. Four other
native jobs, four core jobs and three VST3 jobs succeeded. Fetching the running
job log returned 404/BlobNotFound; the underlying mirror/lock/hook cause is
unverified. No successful work was cancelled or rerun.

## Validation and remaining gate

From the repository root: duplicate-key-rejecting PyYAML parsing passed both
workflows; `bash -n` passed all 30 run blocks; Python AST parsing passed all
ten embedded blocks; `git diff --check` passed. Source checks resolve all
sixteen targets and their test registration/build aggregate. The exact
discovery Python admitted valid synthetic metadata and rejected ten malformed
cases: each missing new gate, duplicate/extra/disabled targets, missing command,
sanitizer override/modification and changed material timeout. These are
admission checks, not executed native tests.

Core `ci.yml` needs no edit: C++/Python `test_*` globs register native
R2/R3/allocation and both independent acceptance suites; explicit CMake
environment bindings select the two built probes, and missing probes raise
errors. Release and sanitizer presets build all targets and run unfiltered
CTest with `--no-tests=error`.

Root owns the current coherent build/155-test run. A29 ran no configure, build,
CTest or apt command. The next coherent published checkpoint must execute the
new sixteen-gate native sanitizer set and core/native platform gates. The local
A27 LSan thread-attach/EPERM failure remains an environment blocker with checks
enabled; this review does not close hosted sanitizer, physical or visual gates.

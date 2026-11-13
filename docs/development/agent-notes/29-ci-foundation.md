# Agent 29 — cross-platform CI foundation

Assignment: wave 05, agent 29 of 60; owned `.github/workflows/ci.yml`, `docs/CI.md`,
and this note. Read repository instructions, current handoff/plan/atlas review,
CMake/presets, build documentation, and relevant source/test portability paths.
Baseline was `ee0d83e5dabb1bb146f2a2985ce410b3461e29ac`; concurrent wave 05 files
were preserved. No source/test changes, commits, pushes, or hosted runs by agent 29.

## Delivered behavior

- Release configure/build/CTest on Ubuntu 24.04 GCC x64, macOS 15 AppleClang arm64,
  and Windows 2022 Visual Studio 2022 MSVC x64; separate Linux GCC ASan+UBSan job.
- Python 3.12 explicitly selected; CMake minimum 3.21 retained; presets discover
  all C++/Python tests and build the generated profile/renderer prerequisites.
- Leak checking is explicitly on (`detect_leaks=1`), with fatal sanitizer reports.
  No local ptrace workaround was copied into hosted CI.
- Read-only contents permission; no persisted checkout credential, secrets,
  deployment, cache, repository writes, or trusted PR-code trigger.
- Per-job/per-test timeouts, per-ref cancellation, failure-preserving log pipes,
  matrix fail-fast disabled, and bounded 14-day diagnostic artifacts/JUnit output.

## Verified upstream pins (2026-11-13)

Used the connected GitHub GET API for each official latest release, exact tag
ref, action manifest and LICENSE. All tag objects below resolved directly to
commits; all three manifests use Node 24 and their LICENSE files declare MIT.

| Action | Tag | Commit |
| --- | --- | --- |
| checkout | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| setup-python | v7.1.0 | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| upload-artifact | v7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |

Authoritative tag evidence:
- https://api.github.com/repos/actions/checkout/git/ref/tags/v7.0.1
- https://api.github.com/repos/actions/setup-python/git/ref/tags/v7.1.0
- https://api.github.com/repos/actions/upload-artifact/git/ref/tags/v7.0.2
- https://github.com/actions/runner-images#available-images
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners

`docs/CI.md` links each immutable commit/LICENSE. Current official runner
inventory confirms the selected labels and architectures; macOS 14 has retired.
The OS/compiler/Python patch images remain moving inputs, logged per run.

## Local validation and limits

Passed: installed PyYAML parse and structural/policy assertions; all 9 inline
scripts passed `bash -n`; all 6 action uses match the 3 upstream verified SHAs.
CMake 4.4.4 `--list-presets=all` recognizes all configure/build/test presets.
Owned-file whitespace/diff review passed. `actionlint` is unavailable; no new
validation dependency was added and this is not GitHub's server validation.
No GitHub-hosted success is claimed. Root owns publication and inspection of
the actual four jobs, including first-run portability failures and skip audit.
Existing retained execution evidence covers Linux only; root owns fresh
integrated Release tests, avoiding an overlapping duplicate full-suite build.

Static portability review found no direct POSIX-only includes in core/renderer.
Unqualified concerns: floating `std::from_chars`, exact nominal `pow` identity,
MSVC/AppleClang `long double` oracle precision, and filesystem hard links.
Profile compiler Python tests explicitly skip unsupported symlink/hardlink
permissions; a passing CTest wrapper therefore needs its unittest skip count
inspected. The renderer hard-link behavior is a mandatory integration check.
No test was weakened and no concern is represented as a demonstrated failure.

CI is an offline-core engineering gate. Plugin/device/DAW/native UI, hardware
fidelity, callback deadline, packaging and signed release gates remain open.

# Agent 43 — hosted CI audit and executable-mutation test repair

## Assignment and evidence

Wave 08, Agent 43 of 60. Owned `tests/test_render_fixture.py`,
`docs/CI_QUALIFICATION.md` and this note. Read AGENTS, README, status/next steps,
latest log, plan, atlas review, chapter 079 (pp. 481–486), CI documentation,
and notes 25/29/33/36. No producer, shared status, workflow or checker changes;
no commits, pushes or subagents. Preserved concurrent wave-07 work.

Audited all four full archives for run `43364414017`, attempt 1, exact revision
`7c2ad2089f795b2147f5fc72cf10a4542d953a8c`. Recomputed ZIP SHA-256 identities,
matching the integrator's GitHub-metadata audit. Read revision/toolchain,
configure/build/CTest/JUnit and all `LastTest.log` records.
The [qualification report](../../CI_QUALIFICATION.md) retains artifact links,
hashes, actual tools, suite/method counts, failures and limits.

## Observed hosted results

- Linux/macOS Release: 18/18 suites passed; Windows and sanitizer: 17/18 each.
- Each job executed 9 C++ suites and 9 Python suites / 195 Python methods.
  No unittest/CTest skips or disabled cases; compiler hardlink/symlink methods
  explicitly passed on all four platforms.
- Linux: GCC 13.3.0, CMake/CTest 3.31.6, Python 3.12.16. macOS 15.8.2 arm64:
  AppleClang 17.0.0.17000013, CMake/CTest 4.4.5, Python 3.12.10. Windows Server
  2022 10.0.20348 x64: MSVC 19.44.35229.0, CMake/CTest 3.31.6, Python 3.12.10.
- Hosted sanitizer compilation and job environment retain ASan/UBSan with
  `detect_leaks=1`. Its failing mutation subtest is not a passing sanitizer gate.
- Earlier run `43363048563` at `9c8068c95f6843dce95f7f22d729738eef8074f6`
  remains the separately qualified four-job / 16-suite baseline.

## Repair and diagnosis boundary

The old test appended directly to a just-executed binary. Hosted failure says
`renderer` instead of expected `integrity`, but omitted the actual manifest
exception. No underlying cause or producer defect is established. The patch
creates a unique renderer copy per scenario and prepares a distinct changed
copy, then replaces the checked path after real execution. Real independent
before/after hashes must match the manifest. Exact integrity-stage rejection,
false integrity verification and no accepted WAV remain required.
Added zero-returncode/complete-capture assertions prevent a renderer failure
from being masked by mutation; diagnostics retain error, status and raw output.
No sleeps, retries, skips or broadened allowed stages were added.

## Executed local checks

Native CMake: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`.
Frozen source/Release build: `/tmp/hammond-wave06b-xawzydwm/{source,build}`.
New build: `/workspace/scratch/c871510c69b2/agent43-sanitizers`.
Configured Debug, `BUILD_TESTING=ON`, `HAMMOND_ENABLE_SANITIZERS=ON`, GCC;
built `hammond_render --parallel 2`. GCC 14.2.0, CMake 4.4.4, Python 3.12.14.
Executed current `python3 -B tests/test_render_fixture.py` with explicit renderer
and compiled-profile environment paths. Release: 19/19 methods, 2.042 s.
ASan/UBSan: 19/19 methods, 2.537 s, with
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` and fatal UBSan reports. No skips.
Leak-enabled local `--help` exited 23 with the explicit ptrace/LeakSanitizer
fatal error; the local pass cannot qualify hosted leak detection.

Original mutation method, only its assertion diagnostics changed in memory:
10 ASan/UBSan iterations / 60 scenarios passed in 1.741 s with leaks disabled.
The integrator separately reported 20 Release iterations / 120 scenarios passing.
These bounded probes do not reproduce or establish the hosted cause.
Owned-file whitespace/diff checks and the repository checker smoke passed;
the frozen source was not edited.

## Handoff

Integrating commit and full hosted rerun are pending; do not claim this repair
passed hosted CI before observing that exact revision. Integrator owns the
Windows `as_posix()` repair, shared handoff updates, publication and new audit.
No native host/device, deadline, physical-fidelity or release qualification claim.

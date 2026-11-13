# Agent 33 — Windows render-evidence repair

## Assignment and boundary

Wave 06 Agent 33 owned `.gitattributes`, `tools/render_fixture.py`,
`tests/test_render_fixture.py`, relevant render documentation and this note.
Read AGENTS, README/status/next steps/latest log, plan, atlas review and atlas
chapter 079 (pp. 481–486). Reviewed the first Windows CI failure log and Agent 30's
independent within-API reader design. No imported verifier helper, core/shared
status/CI edits, commits, pushes or delegated agents.

## Findings and changes

First hosted run: `43361632464`, commit `b9c1cac`, Windows Server 2022,
MSVC 19.44.35229.0, CPython 3.12.10. Build passed; 10/12 suites passed.
All five failed catalog digests exactly equal LF-to-CRLF transformed score bytes.
Added LF checkout rules and explicit binary rules for PDF/WAV/B3P; no hash resets.

The producer's hash and WAV readers compared complete path/descriptor stamps.
Official Python docs and CPython change `a01fb672` explain the Windows ctime
creation-time/ChangeTime difference; upstream issue 157671 reproduces it. The
project's initial log does not disclose the exact differing fields. Both readers
now compare full stamps within each API and bind POSIX device/inode identity.
They retain regular nonsymlink/type/size validation, bounded binary reads,
byte-count validation, and raw SHA-256 before/after-run checks.

Timeout child emits explicit LF bytes; separate stdout/stderr capture assertions
preserve deliberate CRLF and Ctrl-Z. Actual captured logs are never rewritten.
See `docs/WINDOWS_EVIDENCE.md` for source links and detailed failure boundaries.

## Executed checks

Native tools directory: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`.

```sh
cmake -S . -B ../agent33-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent33-release --target hammond_render -j 2
ctest --test-dir ../agent33-release \
  -R '^python_test_(render_fixture|fixture_catalog|verify_render)$' \
  --output-on-failure --no-tests=error -V
```

Fresh GCC 14.2.0 Release build passed. All three selected suites passed:
19 producer methods, two catalog methods/five rendered fixtures and 27 independent
verifier methods. Local CPython 3.12.14; Git 2.52.0. No skipped/suppressed tests.
Earlier direct producer run with Agent 30's real renderer also passed 19 methods.

New regressions execute Windows metadata asymmetry on Linux, reject each stamped
field changing within either API, preserve POSIX identities, and retain CRLF
profile/score inputs through a real render. The temporary Git checkout forces
`core.autocrlf=true` per command and checks bytes/hashes for the catalog, profile,
wrapper, all five scores and binary CRLF sentinels. No repository config changes.
Recomputed all five Windows failure hashes from CRLF transformations; exact match.
Source PDF remains 21,248,265 bytes and SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

## Pending handoff

Native Windows rerun remains pending for the integrator; the simulation and Linux
checks do not qualify Windows. Keep the first failure and inspect the actual
rerun before claiming pass, including executable-copy launch behavior if reached.
No host/device, physical fidelity, reproducible-build or authenticity claim.

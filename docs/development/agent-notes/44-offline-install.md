# Agent 44 — isolated offline CLI installation

Actual assignment: wave 08, agent 44 of 60; implement a local install component
and an executed relocation smoke. Read AGENTS, current README/status/queue/build
and render contracts, plan/review, and atlas chapter 066 (PDF pp. 403–408).
Worked from main `7c2ad20` with unrelated shared changes preserved. No commit/push.

## Changes and scope

- Appended GNUInstallDirs-based `OfflineTools` rules to CMakeLists.txt.
- Exact default payload: `bin/hammond_render` (Windows `.exe`), generated
  `share/hammond-b3-organ/nominal.b3p`, and the existing five event scores plus
  catalog under `share/hammond-b3-organ/fixtures/` (eight files total).
- Relative custom bindir/datadir are supported; absolute/parent-traversing paths
  fail configuration. Install preflight requires both selected-config executable
  and generated profile before copying any component file.
- No PDF, external assets, core archive/headers, benchmark, Python tools, SDK,
  third-party dependency or automatic download is included.
- `tests/test_install.py` invokes actual component installation, renames a prefix
  containing spaces, and renders installed A4 data from an unrelated cwd.
- Checks exact layout/content, no symlinks, actual stereo PCM/full WAV equality,
  catalog/profile hashes and JSON identity/metrics against the build renderer.
- Clears HAMMOND variables before execution; a temporary installed-profile
  digest/gain probe must change reported identity and produce silence. Removing
  that profile must fail without output. Restores bytes; never mutates source or
  build inputs. This synthetic probe makes no new provenance claim.
- CTest supplies CMake/build/config/executable/profile and configured install dirs.
  `$<TARGET_FILE:...>` / `$<CONFIG>` avoid guessing multi-config executable paths.
- Added [OFFLINE_INSTALL.md](../../OFFLINE_INSTALL.md) with local prefix commands,
  relocated Linux/macOS and PowerShell invocation, payload and evidence limits.

## Executed evidence

Linux x86_64; GCC 14.2.0; CMake 4.4.4; Python 3.12.14. Native CMake/CTest were
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/{cmake,ctest}`.
Isolated build: `/workspace/scratch/c871510c69b2/agent44-install-build`.

1. `cmake -S <repo> -B <build> -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON` passed.
2. Before building, real `cmake --install <build> --component OfflineTools
   --config Release --prefix <temporary path with spaces>` failed with the
   explicit build-first diagnostic and created no prefix.
3. `cmake --build <build> --config Release --target hammond_render --parallel 2`
   passed with the project's strict warning configuration.
4. `ctest --test-dir <build> -C Release -R '^python_test_install$'
   --output-on-failure`: 1/1 passed (0.43 s).
5. Separately held/restored this isolated build's executable, then its profile;
   each actual install failed before creating a prefix with the same diagnostic.
6. Reconfigured `CMAKE_INSTALL_BINDIR=offline bin` and
   `CMAKE_INSTALL_DATADIR=offline data`. CTest regex
   `^python_test_(install|render)$`: 2/2 passed (1.18 s total).
7. Separate configure-only temporary builds rejected `../outside` and an absolute
   `/tmp/...` data destination. No system destination was installed.
8. `git diff --check` passed. `python tools/check_repository.py --json` passed
   source/data identities, links and actual agent notes (44 present at that run).

## Limits and handoff

No macOS, Windows/MSVC, multi-config generator or sanitizer run was performed by
this agent. Ninja is unavailable locally; no dependency was installed to add it.
The supplied generator expressions/configuration must still pass actual hosted
qualification. This local install does not establish clean-machine compatibility,
compiler-runtime bundling, product licensing, signed packaging, plugin/audio-device
behavior, physical fidelity or M9 completion. It remains the nominal offline CLI.
The integrator owns shared status/queue/log links and full-matrix qualification.

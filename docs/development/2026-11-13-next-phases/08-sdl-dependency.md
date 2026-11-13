# Assignment 08 — pinned SDL2 acquisition and verification

- Session: `2026-11-13-next-phases`, wave 2, assignment 08.
- Actual worker: `/root/w02_a08_sdl_dependency`.
- Baseline: commit `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`, tree
  `51fd7b24d2f373a693ced8dbde0fba762a3cc434`.
- Owned: `data/dependencies/sdl2-lock.json`, `tools/acquire_sdl2.py`,
  `cmake/VerifySdl2.cmake`, `docs/STANDALONE_DEPENDENCY.md`, this report.

## Implemented

Added a strict official-release lock for SDL2 `release-2.32.10`, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. The primary Zlib `LICENSE.txt`
is 884 bytes, SHA-256
`97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127`.
The source was already present and clean at `../SDL2`; this worker did not
acquire or modify it.

The explicit Python tool admits either a new external acquisition destination
or read-only existing-source verification. It validates the exact supported
lock/schema, checkout root, commit, release tag, primary license, source
presence and cleanliness, including ignored extras and hidden/sparse index
entries. It refuses partial/promisor checkouts and never resets/cleans an
existing path. The new-destination reservation is exclusive. CMake's
`hammond_verify_sdl2(root)` only invokes verification and uses its own adjacent
project tool/lock independently of the caller's `PROJECT_SOURCE_DIR`.

The dependency document records upstream's actual `SDL2_DISABLE_INSTALL`,
static/test options and `project(SDL2 C)`. C-language enablement belongs only
in the optional standalone branch. It also retains primary/bundled notice and
actual backend limitations. No top-level CMake, app or shared status file was
edited; no commit was created by this worker.

## Executed evidence

Working directory for commands:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Tools: Python 3.12.14, Git 2.52.0, CMake 4.4.4 at
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake`.

1. `git -C ../SDL2 show --no-patch --format=fuller HEAD`,
   `git -C ../SDL2 describe --tags --exact-match`, `sha256sum ../SDL2/LICENSE.txt`
   and `wc -c ../SDL2/LICENSE.txt` matched the reviewed identity above.
2. `python3 tools/acquire_sdl2.py --verify-existing ../SDL2` passed and reported
   `network_used: false`, the exact version/tag/commit and one primary license.
3. A temporary CMake script included the new module by absolute path and called
   `hammond_verify_sdl2("${SDL2_CHECK_ROOT}")`. Running the named CMake with
   `-DSDL2_CHECK_ROOT=<absolute SDL2 path> -P <script>` passed. An absent root
   failed with the intended existing-external-source diagnostic.
4. A temporary Python-driven CLI smoke passed eight checks total: both CMake
   cases, required mode, existing destination preservation, rejection of an
   SDL2 child directory, in-project acquisition, substituted commit and
   duplicate JSON key. Exit codes matched 0/1/2 as appropriate. The source
   index SHA-256 was identical before/after. `compile()` accepted the tool.
5. `git -C ../SDL2 status --porcelain=v1 --untracked-files=all` and
   `git -C ../SDL2 ls-files --others --directory --no-empty-directory` remained
   empty. No new checkout/build/test result is attributed to these reads.

The temporary smoke inputs lived under ignored `build-sdl2-dependency-a08`
and were removed by their temporary-directory context. No permanent exhaustive
test file was added; the next independent assignment owns adversarial tests.

## Source and scope limits

Inspected the integrating agent's existing static-build configuration at
`../sdl2-build/include-config-release/SDL2/SDL_config.h`: video dummy/offscreen;
audio disk/dummy/OSS. Desktop X11/Wayland and ALSA/PulseAudio/PipeWire drivers
were absent despite requested cache options. An initial guessed header path
`include/SDL_config.h` did not exist; `rg --files` located the actual generated
header. CMake was absent from inherited PATH, then supplied by the integrator.
These are setup observations, not application failures.

The official release/license GitHub pages could not be fetched through web
open in this environment; official indexed results from
[libsdl.org/release](https://www.libsdl.org/release/) and
[libsdl.org/license.php](https://www.libsdl.org/license.php) corroborated the
release and Zlib licensing. Exact commit/tag/bytes came from the local source.

Network acquisition through the new script, adversarial checkout mutations,
the integrated standalone executable, hosted desktop backends, physical audio,
platform packaging and complete bundled-license distribution are not qualified
by this assignment. The integrator owns optional CMake/application integration;
independent tests should exercise malformed locks and dirty/misidentified
checkouts without changing the existing clean source.

Frozen production input SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `data/dependencies/sdl2-lock.json` | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |
| `tools/acquire_sdl2.py` | `a0555aefe37b37621e2602eea9035b4d048c81c1cca0c3d5442c1f638d927ab3` |
| `cmake/VerifySdl2.cmake` | `21e3bb4fd75cbcc2879f321dae3437a609cd08d88ff98120a8aade19126ffc7e` |

# Assignment 25 — exact-source native standalone CI

Canonical agent: `/root/w05_a25_standalone_ci`; actual assignment 25, wave 5 of
the new sixty-assignment/ten-wave standalone session; 13 November 2026.
Owned only `.github/workflows/standalone.yml`, `docs/STANDALONE_CI.md` and this note.
No CMake, application, test, shared-status, history or remote changes were made.
The integrator owns publication and hosted-result observation.

## Source and reviewed inputs

Repository: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Inspected HEAD `738162f0bc36f88f8c76268d04831862a8118d10`, committed tree
`915e55dc7c3ad022042b188498aa41f2a7f40795`. The live tree also contained concurrent
uncommitted standalone test/install changes. This is a source/syntax review,
not a frozen native build qualification at that HEAD. Local `origin/main` was
`96a37a977ef22b7adf38e1a841f57ffcf32519a7`; no network/publication claim follows.

Read AGENTS, current scope/status/handoffs, plan/atlas review and retained M9
product/closure notes; inspected existing core/native workflows, actual CMake
targets, application/audio/allocation/concurrency and install contracts.
Selected Ubuntu headers from the actual locked upstream `docs/README-linux.md`,
SHA-256 `c39149ceda9b253a3cc768d32b68173fe780286171294c75e5c2173abbbb05af`,
at `/workspace/scratch/5ba97739b54c/SDL2`.

| Reviewed input | SHA-256 |
| --- | --- |
| SDL2 lock | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |
| Font source manifest | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |

SDL2 remains 2.32.10, source commit `5d249570393f7a37e037abf22cd6012a4cc56a71`.

## Delivered behavior

The workflow uses the existing pinned checkout/setup-python/upload-artifact
actions, `contents: read`, exact event checkout and clean tracked-source checks.
It records commit/tree/run/attempt/runner/image/dependency/toolchain identities.
Linux GCC, macOS AppleClang and Windows MSVC x64 build Release on the assigned
hosted images. Explicit external SDL acquisition precedes local verification;
configuration never acquires dependencies. Font rasterization is unnecessary.

Runner-only Ubuntu packages enable X11, ALSA and PulseAudio; apt logs and exact
installed versions are retained. Generated SDL macros must confirm those native
backends, Cocoa/CoreAudio on macOS and Windows/WASAPI on Windows. Dummy drivers
are selected only by the test/smoke steps. Build precedes required filtered CTest
through `hammond_standalone_test_inputs`, `^test_standalone_` and `--no-tests=error`.

The explicit nine-file Standalone component is staged into a fresh prefix,
inventoried against actual source bytes, moved and exercised by relocated help
and 600 ms dummy smoke. State/BMP/JSON paths are explicit. Byte/mode inventories
must survive relocation/execution; links/reparse points, special files and extra
payload reject. The tar.gz is reopened to verify its payload bytes/sizes/modes.
Full diagnostics always upload; only successful gates upload package/inventory/hash.

## Actual checks and remaining gates

Local Linux x86-64 validation used Python 3.12.14, PyYAML 6.0.3 and Bash 5.2.37:

- `yaml.load(..., Loader=yaml.BaseLoader)` parsed the workflow and asserted the
  three triggers/runners, least permission, exact action pins, target/test filter
  and driver scope. All **10** run blocks passed `bash -n`; all **4** inline Python
  blocks passed `ast.parse` and `compile`.
- Extracted inventory helper fixtures admitted nine source-matching files and
  rejected missing/extra files, an extra empty directory, symlink, FIFO and
  changed bytes. Mode changes were detected by full-inventory comparison.
  A real directory rename and tar.gz roundtrip preserved file bytes/sizes/modes.
- The actual existing local generated SDL header parsed correctly: dummy was
  enabled; X11/ALSA/PulseAudio were absent. The new admission rule would reject
  that limited local build, rather than treat it as native-backend coverage.
- Inspected every expression, source/installed/executable path and CMake target;
  Windows uses `Release/hammond_standalone.exe` and explicit Release configuration.
  `git diff --check` and per-owned-file `git diff --no-index --check` passed;
  local Markdown links and both 100-line documentation limits passed.
  No remote workflow or native build was executed here.

The integrator must freeze/publish the combined source, observe all three hosted
jobs and retain their actual logs/artifacts, including setup versus project
failures. Hardware playback, hotplug, latency/underruns, native accessibility,
complete binary notices/runtime dependencies, project licensing and signed/public
distribution remain separate. Workflow syntax and local inventory fixtures do
not establish any platform execution or physical-fidelity pass.

## Owned final content identities

| File | SHA-256 |
| --- | --- |
| `.github/workflows/standalone.yml` | `b7f8c70ff9a4ee38d36427999efdbfd39b8c6a06a2e4921c5196e3b8604b5eba` |
| `docs/STANDALONE_CI.md` | `fc3fccc54f3be68c0693916d2790dcf3d4a8c9fd4ea259a95181efd4bd8cffdb` |

This note's own hash is supplied in the agent handoff to avoid a self-hash cycle.

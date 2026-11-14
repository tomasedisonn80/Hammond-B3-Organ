# A44 — Final MIDI-on and MIDI-off packages

Actual worker `/root/w08_a44_final_package`, assignment **44/60**, logical
wave **8**, 14 November 2026. Owned paths: this note,
`docs/reviews/INTERFACE_FINAL_PACKAGE.md`, `reports/a44-*`, the leased sibling
`build-native` and `build-native-midi-off`, and bounded own `a44-*` staging
directories. **Both build leases are released.** No production source, shared
guide, CMake/workflow file, index or publication operation was changed by A44.

## Result and retained identity

**Passed:** the separately compiled final on/off applications, exact 19/15-file
packages, source-absent relocation and bounded installed CLI/smoke/replay/capture
operations. The [full review](../../reviews/INTERFACE_FINAL_PACKAGE.md) explains
the evidence and limits. The [final result](reports/a44-final-package-result.json)
retains the runtime result and later guide-only refresh separately.

The task was assigned while root's HEAD was `aea58bb8`; root published the
reviewed source before A44's recorded build snapshot. Actual qualification HEAD
was `8673713a484c40e26ac7810c7c4cbc22fa874426`, tree
`e11bd68d6051f663631579ef235325a8775f8133`. All 98 recorded production/asset/data
inputs match that commit. Their sorted path/NUL/hash/LF inventory SHA-256 is
`ddf4f7658cfa9ed49ddac87902788c65531697551faab4dadd1dd57709d9e9ad`.
The [input comparison](reports/a44-input-comparison.json) identifies the four
production changes since A29 and zero differences from the recorded commit.
All 114 protected files still match A12's inventory.

| Product | Qualified executable SHA-256 | Final files / bytes |
| --- | --- | --- |
| MIDI on, RtMidi ALSA | `bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2` | 19 / 3,854,706 |
| MIDI off, unavailable backend | `a09c9127b54ad1efae1ba0c332e4fecff5385d27a834a24ad6c3f7b47d474117` | 15 / 3,765,285 |

Both are Unix Makefiles/Release, standalone/testing ON, VST3/sanitizers OFF,
SDL 2.32.10 with `SDL_ALSA=OFF`. Actual support flags distinguish
`HAMMOND_HAS_RTMIDI=1` and `0`. MIDI-on reuses the established RtMidi and ALSA
development inputs; MIDI-off has an empty RtMidi root. The toolchain is retained
in [a44-toolchain.json](reports/a44-toolchain.json): CMake/CTest 4.4.4, GCC 14.2.0,
Python 3.12.14 and bubblewrap 0.12.0.

## Work performed

1. Read the repository rules, session scope/checkpoint, full M0–M9 plan,
   source/evidence boundaries, current operating guide and A24/A29 install
   implementation/results. Checked free disk and acquired both build leases.
2. Captured the actual product, build/install and installed-guide inputs.
   Configured each existing cache and built only `hammond_standalone` once per
   configuration. The enabled target was already current and preserved A36's
   exact binary; disabled rebuilt the changed inputs and linked its own binary.
3. Ran the existing strict installation suite once per mode. **2/2 CTest suites,
   16 unittest methods passed.** Individual suite times were 7.36 and 6.54 s.
   The full core/native matrix was not repeated.
4. Installed the actual Standalone component into new prefixes, verified every
   byte and ordinary-file entry, moved each prefix, then ran **eight final
   native invocations** inside private mount namespaces. Those processes could
   not see the repository, either build, SDL, RtMidi or the development ALSA
   sysroot. Each mode passed Help, usage rejection with no writes, dummy native
   smoke/capture, and a live-Load/held-note replay across six view combinations.
5. Retained exact native diagnostics, two visually inspected PNGs and loader
   logs. MIDI source stayed `none`, no discovery started, no MIDI input was opened,
   callbacks/frames rendered through SDL dummy, and shutdown was joined and
   unheld with zero application/audio errors. State4 bytes remained unchanged;
   live Load reported “Loaded saved controls.”
6. Released the guide freeze so root could apply A45's reviewed current MIDI
   guide correction. Reconfigured both caches and performed a fresh
   **inventory-only install and movement**, with no app rebuild or flow rerun.
   Only the guide changed; every other payload byte remained identical.
7. Checked actual CTest JSON after root's sanitizer-only timeout allowance:
   ordinary Release workspace-raster/scaled-view/preset-raster timeouts remain
   **60/60/30 seconds in both caches**. This was discovery, not test execution.
   Released both build leases to root and retained compact failure evidence.

## Source-absence and runtime-library boundary

The installed executable is read-only at `/app` and the private work directory
is `/run-work`; ordinary system runtime directories are mounted separately.
An executed Python absence probe runs inside each namespace before the app.
Source and dependency directories remain intact outside the private namespace.
The [enabled](reports/a44-midi-on-relocation.json) and
[disabled](reports/a44-midi-off-relocation.json) reports retain exact commands,
capabilities, metadata sources, all payload hashes and the absence proof.

The enabled executable retains the pre-existing RUNPATH to the ALSA development
sysroot. With that path absent, both `ldd` and the actual loader log resolve and
initialize system `libasound.so.2`; it has the same bytes as the development
copy. MIDI-off has no ALSA dependency. Normal system loader/C/C++/math runtime
libraries remain required. No source-tree or SDK runtime dependency was needed
by the observed installed operations, and no library was added to the package.

## Exact guide/configuration drift

The runtime payload used `MIDI_UI_RUNBOOK.md` SHA-256
`bc088e41621a0fa5363b3206e1ca71bbf4518a0492f46d842c415ab116bb779d`.
After root's A45-reviewed edit, the final package contains
`f51b2c32f5f6e6aa062885bd2b1b64fee24faf85712f4bca9a3b8f1a600695a1`.
It grew by 1,030 bytes; the six guides and notices have 30 resolving relative
links. The [refresh record](reports/a44-package-refresh.json) proves that this is
the only changed payload entry in either package. Original snapshots and
runtime-package reports are preserved, not rewritten as if the guide were
always current.

The only intervening build/install input change was root's
`apps/standalone/CMakeLists.txt` timeout block, from SHA-256
`6661ddf975af37b0b8720140afa857b6537c069d07f388ce0e8524befed97ffe`
to `6b75fe8c73e4927b5fbe3c78e3ab7f88c92ba3f49eb2a5d3df269412cca1abc8`.
The [before](reports/a44-source-before-guide-refresh.json) and
[after](reports/a44-source-after-guide-refresh.json) refresh snapshots prove the
98 product inputs and the final metadata were stable during that refresh.

## Reproduction

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Reuse the documented dependency paths and acquire the two builds before writing
them. The [build driver](reports/a44-build-packages.py) retains each exact
configure/build/filtered-CTest command. Its normal invocation configures and
builds each product target once, with the required gate selected by:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native \
  -C Release --verbose --output-on-failure --no-tests=error \
  -R '^test_standalone_install$'
```

Use `build-native-midi-off` for the second actual configuration. The final
successful independent relocation command was:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12 \
  docs/development/2026-11-14-interface-continuation/reports/a44-qualify-relocation.py \
  --source /workspace/scratch/601951e27dc3/Hammond-B3-Organ \
  --build-on /workspace/scratch/601951e27dc3/build-native \
  --build-off /workspace/scratch/601951e27dc3/build-native-midi-off \
  --cmake /workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --sdl /workspace/scratch/7ffc2842608b/SDL2 \
  --work /workspace/scratch/601951e27dc3/a44-final-packages-runtime \
  --reports /workspace/scratch/601951e27dc3/Hammond-B3-Organ/docs/development/2026-11-14-interface-continuation/reports
```

The work directory must be new and absent. A fresh reproduction of current
source naturally records the final guide directly; the historic guide-only
transition is separately encoded in [a44-refresh-package-docs.py](reports/a44-refresh-package-docs.py).
Its assertions intentionally identify the old and new evidence snapshots.
Final package prefixes are the two `relocated final Ω` directories beneath
`/workspace/scratch/601951e27dc3/a44-final-packages-docs/`.

## Retained corrections, storage and next action

Three harness/setup findings are preserved in
[a44-probe-corrections.json](reports/a44-probe-corrections.json): a successful
CTest summary used newer wording; the first CLI harness expected 1 rather than
the actual usage exit 2; and ptrace-based tracing was unavailable. The first
two expectations were corrected without app changes, and source-absent
namespace execution plus ordinary loader diagnostics supplied the intended
runtime proof. The original records retain four extra CLI invocations from
aborted preparations and one blocked tracer attempt with no native result,
separate from the eight final successful native outcomes. No observed product
failure was discarded or converted into a pass.

Only A44's two abandoned reproducible stages were deleted after inventory
comparison and failure retention, releasing 7,707,352 bytes. Approximately
39.46 GB remained free. Two source-identified package pairs remain outside the
repository; no binary, SDK, PDF or cache is staged. Root owns acceptance,
accounting and publication of the owned note/review/reports.

No physical audio/MIDI, persistent desktop/pointer, display/DPI, callback
deadline, accessibility, real host, reference pixel equality, measured-model,
signing or release-rights gate is claimed. A future product change needs the
affected native gates; a later installed-document change needs reconfiguration
and a fresh exact-inventory install. Root can now use both released builds for
the next coherent qualification without inheriting an A44 write lease.

# A26 — independent selector realtime acceptance

Actual worker `/root/w05_a26_realtime_selector`, logical wave 5, 2026-11-14.
Owned files: `tests/test_preset_realtime.cpp`,
`docs/reviews/PRESET_REALTIME_REVIEW.md`, and this note. No production, existing
test, CMake, shared status, manifest or Git ref was edited. No commit, push or
child agent was performed. The existing preserved baseline/native builds were
not reconfigured or rebuilt.

Read the standing instructions, project plan and current operating context,
the frozen selection/core contracts, A14/A17 implementation evidence and A22
native acceptance. Added independent SDK-free measured acceptance for the new
fixed-data, callback, combined-input and prepared host paths. Only the already
calibrated portable global C++ probe plumbing was reused from
`tests/test_realtime.cpp`; musical fixtures and transition expectations are new.
The [review](../../reviews/PRESET_REALTIME_REVIEW.md) gives the scope, counters,
independent expectations and limitations.

## Coherent source and commands

Copied **1,251** present tracked/untracked, nonignored files into a new
`/tmp/hammond-preset-a26/source` before configuration. A sorted path/hash/size
manifest identifies the copied bytes. Checkout context was commit
`35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`; the accepted uncommitted selector work
is part of the copied tree, so those Git identities alone do not identify this
qualification. No live-tree source was consumed after the copy.

Toolchain: GNU C++ **14.2.0**, CMake/CTest **4.4.4**, Python **3.12.14**, Linux
x86-64, Unix Makefiles, Release, strict repository warnings including `-Werror`.
The ordinary native-table/profile generators ran as real build prerequisites.
No native UI, MIDI or VST3 SDK was enabled. Working directory for the commands
was `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S /tmp/hammond-preset-a26/source -B /tmp/hammond-preset-a26/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a26/build --target test_preset_realtime -j4
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a26/build -N --no-tests=error \
  -R '^test_preset_realtime$'
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a26/build --verbose --output-on-failure \
  --no-tests=error -R '^test_preset_realtime$' \
  --output-junit /tmp/hammond-preset-a26/ctest.xml
```

Configure, strict build, discovery and execution succeeded on their first
attempts. Exactly one suite was discovered and **1/1 passed in 0.08 seconds**.
No test failure, retry, disabled assertion or production correction preceded
this result. Owned-path `git diff --check` passed.

```text
preset realtime: calibration=12/12, compared_samples=6968, audible_samples=12800, preserved_histories=152, future_probes=104
lookup calls=57 accepted=51 rejected=6 frames=0 records=0 new=0 delete=0
control calls=156 accepted=150 rejected=6 frames=0 records=0 new=0 delete=0
engine calls=482 accepted=398 rejected=84 frames=17600 records=6348 new=0 delete=0
combined calls=6 accepted=4 rejected=2 frames=128 records=20 new=0 delete=0
timeline calls=60 accepted=48 rejected=12 frames=1920 records=6210 new=0 delete=0
```

`compared_samples` includes 6,656 rendered samples and 312 tail sentinels.
The 761 measured call regions are separate from the 12/12 calibration operations.
This is not a general allocator or physical deadline result.

## Source and artifact identities

All values below are raw SHA-256. Complete copied-source and selected input
manifests, logs, JUnit and `qualification-identities.json` remain in
`/tmp/hammond-preset-a26/` for the integrator's publication evidence. The source
test remained byte-identical after execution; no compiled input was modified.
The selected 139-file core/data/tool/configuration input map has compact-JSON
digest `cf90f91055f06e9a122f6f17b3e8d19ad1b25cb42b2ba68b7ff126a876d81147`.
Its live-tree comparison found only the separately advancing
`apps/standalone/CMakeLists.txt` changed; the frozen copy used standalone OFF.
The core, this test, its independent fixture, generated inputs and tools still
matched. That later standalone configuration is outside this test's claim.

| Identity | SHA-256 |
|---|---|
| Full copied source manifest | `457ef8762bfe596b522690933a521393cae9dcd90e05c653dcbe7a3c690fcfdd` |
| New test source | `4d1b73a498be2bddcc89d3ce1582be880e070dada5e1821a87a7e89319997ef6` |
| Test executable | `0c8626a24675131b0c33e515ce4eadc0e3439dd090343abe7c4455a318b56d8e` |
| Generated fixed table | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Configure log | `7de4126ab1ca6face90f13383c156de1a755988f95de4290da7caa81eebf6e67` |
| Build log | `1d3eb528044b3504005c8dfa316e7d60d2bf2321ab04d23cccf83807926ff3f7` |
| Verbose CTest log | `eb56eba483be7ab991fdd9009c739704bd914517cb90d02cb0f008520b7930c2` |
| JUnit | `172d7aacc44e387d409260997e3858ddba7ec61eb489834459f6f6a44b86d433` |

The next step is the integrator's complete coherent-source/platform acceptance,
including this automatically registered test, followed by shared status and
setup updates and authorized publication. A26 did not run sanitizer, native SDK,
UI, device or hosted-platform checks and does not replace the separately owned
legacy-PCM comparison or physical acquisition gates.

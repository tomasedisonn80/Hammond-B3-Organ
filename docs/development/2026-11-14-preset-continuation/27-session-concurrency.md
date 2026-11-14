# A27 — independent Session preset concurrency

Actual assignment `/root/w05_a27_session_concurrency`, logical wave5,
2026-11-14. Read standing instructions, the complete M0–M9 plan, current status
and next steps, frozen preset contracts, Session contract/source and A17/A18
publication handoffs. Scope is the new independent concurrent publication test.
The integrator requested its final `test_standalone_` prefix so existing hosted
standalone filtering includes it without a CMake change.

## Owned work and result

Owned only:

- `apps/standalone/tests/test_standalone_preset_concurrency.cpp`.
- `docs/reviews/PRESET_SESSION_CONCURRENCY.md`.
- This execution record.

No production, existing test, CMake, shared status/manifest or archived fixture
changed. No commit, push or child agent. The
[independent review](../../reviews/PRESET_SESSION_CONCURRENCY.md) explains the
immutable sequence oracle, three concurrent roles, pending-versus-applied
checks, copied Save, queue recovery and future-audio boundary. No production
defect was found.

The final focused gate passed **1/1**, with no skips, in **0.03 seconds total
wall time** (CTest displayed 0.02 seconds for the individual test). Stable
counters: three rates; 192 controlled pending checks; 3,264 complete restores;
six full-queue recoveries; 1,536 discarded replacements; 24 rejected calls;
1,524 exact future stereo samples and 768 separate exact priming stereo samples.
All compared samples were nonzero.

Final scheduling observations: 297 callbacks, 14,568 accepted reader copies,
252 bounded busy reads, 17 state4 saves from copied snapshots, 194 changed
cancelled-fixed and 19 changed cancelled-None observations. These are observations,
not deterministic expected counts or device deadline evidence.

## Coherent source and commands

Checkout and inspected remote main both named
`35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`. The tested copy includes the accepted
uncommitted preset implementation; that HEAD alone does not identify it.

Before configuring, copied all 1,260 present tracked/untracked nonignored files
to `/tmp/hammond-preset-a27/source`. The JSON manifest records every copied
path's raw SHA-256 and byte count. All 150 relevant core/standalone/configuration/
data/tool/test inputs matched the live source before and after execution. The
later test-only refinement was copied and its manifest updated before rebuilding.
No preserved `build-baseline` or `build-native` directory was reconfigured,
rebuilt, linked against live headers or otherwise modified.

Toolchain: `/usr/bin/c++`, GNU14.2.0, C++20; CMake/CTest4.4.4; Python3.12.14;
Linux, Unix Makefiles, Release. Native standalone, VST3 and MIDI options were
disabled; the SDK-free standalone support library remains part of the ordinary
build. Actual test flags were `-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic
-Wconversion -Wsign-conversion -Wshadow -Werror`.

Working directory was `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
`cmake` and `ctest` below are the binaries in
`/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/`:

```sh
cmake -S /tmp/hammond-preset-a27/source -B /tmp/hammond-preset-a27/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build /tmp/hammond-preset-a27/build \
  --target test_standalone_preset_concurrency -j4
ctest --test-dir /tmp/hammond-preset-a27/build \
  -R '^test_standalone_preset_concurrency$' --no-tests=error --verbose \
  --output-junit /tmp/hammond-preset-a27/ctest.xml
```

Initial configure/build succeeded. The initial test passed1/1 in0.05seconds wall,
but its future counter included priming samples. Separated that counter and
added the concrete immediate-rejection continuation/held-owner assertion, then
rebuilt only the changed test and repeated the same narrow filter. No broader
rerun followed. `first-build.log`, `first-ctest.log` and `first-ctest.xml` preserve
the first successful run. Final owned whitespace and local-link checks passed.

## Exact identities

Hashes are SHA-256. Logs and complete manifests remain in
`/tmp/hammond-preset-a27/` for integrator retention.

| Artifact | SHA-256 |
| --- | --- |
| Initial `source-manifest.json` | `4c45d2f2349e721298639734c157fe78624ae60b747604a5bfea8773aff8c031` |
| Final `source-manifest-final.json` | `bec6df504a3a5baf03c3585a8c5d4538454e6b2feb9360efc0d439406b53d6c9` |
| Final test source | `a8e5ba17a581f631783369a4e37f37eea94002526d9e602afd13c3495d5f0abd` |
| Final test executable | `0d9861402e091fe3149990eccd5d2f5b15f22511082ea09a8c8aaab2161d5089` |
| `configure.log` | `b1bb1b1e89bdcb0e5b99790267e4fab6f313fa8465979b2f98191f9dd0d54bf4` |
| Final `build.log` | `b1a9de369418d295b0e6fe8ae929695fa47e886df78ebf8573f889a5b7480762` |
| Final `ctest.log` | `473691bb84322f8d669da033fb8972d1822621feb0d00d904bd5cdb22e5436bb` |
| Final `ctest.xml` | `0829a0f5c1e55ddb4b872521972e44cee85d714d58b1c933cdc9fd091edc3ba2` |

`qualification-final.json` records these artifacts and the150-input no-difference
check. The integrator owns final integrated/platform/sanitizer execution, shared
handoff, actual accounting and publication. No sanitizer, native device, host,
visual or physical fidelity gate was executed by A27.

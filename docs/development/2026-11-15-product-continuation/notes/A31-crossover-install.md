# A31 — explicit movable CrossoverTools

Actual worker `/root/w06_a31_crossover_install`, wave 6. Recovered AGENTS, the
complete M0–M9 plan, current session records, crossover contract/characterization,
reference/probe and existing installers. Base HEAD
`ff41d412d03f2c5767aa4057b29fa8ec1627449b`, tree
`6462343bb34a7d70d59de75ab349f8530196988c`; this result qualifies the owned overlay.

Owned `cmake/InstallCrossoverTools.cmake`, `tests/test_crossover_install.py`,
`docs/CROSSOVER_INSTALL.md` and this note. Root added the single include after
InstallHammondTools and reconfigured. Existing unconditional probe/check
dependencies suffice; the module supplies CTest environment, labels and timeout.
No production source, old component payload, shared build, commit or publication
was changed by this worker.

The explicit `EXCLUDE_FROM_ALL` component copies six files: selected probe,
unchanged reference/registry, install guide, frozen contract and notices. The
source-like subtree preserves `DEFAULT_REGISTRY`. Shared directory validation,
COPY-only mode, configuration guard, complete input preflight and destination
collision/ancestor checks precede copying. No project LICENSE exists in the
inspected repository; notices grant no project-wide license.

Executed from `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`:

```sh
env PYTHONDONTWRITEBYTECODE=1 HAMMOND_TEST_CMAKE=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake HAMMOND_TEST_CMAKE_GENERATOR=Ninja HAMMOND_TEST_CMAKE_MAKE_PROGRAM=/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja HAMMOND_TEST_CONFIG=Release HAMMOND_CROSSOVER_PROBE_EXECUTABLE=/workspace/scratch/5b7d983ac078/build-native/hammond_crossover_probe python3 tests/test_crossover_install.py -v
```

**14/14 passed, 1.450s, no skips**, Linux x86_64/glibc2.41, Python3.12.14,
CMake4.4.5, Ninja1.13.2 Kitware, root GCC14.2 Release probe. Private fixtures
passed exact bytes/inventory, source-independent relocated execution, custom
directories, all-input faults, output preservation, links, DESTDIR and Ninja
Multi-Config dispatch. The latter selects private copies of the existing Release
artifact; it does not claim a new Debug compilation. Root's
[integrated CTest](../reports/wave6-crossover-install-ctest.txt) passed 1/1 in1.62s.
Owned whitespace/Python syntax/four local Markdown links and git diff check pass.

SHA-256:

- Installer: `bb83e6c2997d508c6a9a2ed463dc5eff062ab0c3d36ced84d90a86bb086bc03e`.
- Suite: `42f1b49149d2b33d569301389d2947da30f8fb96f1b2a29d71ada54caf5821d5`.
- Guide: `95a7b670f84ca3db9e710664f88e89ddaa35269e69696667c416a58e6a521432`.
- Probe: `da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac`.
- Reference: `33eaa88da2534e52f88c044b5fbabf19828655bacb357dc55bbeb6510b580ec5`.
- Registry: `f55fa98c246b4a19dce12ca829a141cff744f71242cccb68db12b404400319cc`.

Limits: no shared-install manifest mutation, new physical/audible claim,
runtime collection, all-platform distribution or atomic multi-file rollback.
Physical unknowns and dry Engine remain unchanged. Next gate: root's coherent
full CTest and source-identified hosted platform install acceptance before
publication; preserve earlier source-specific CI results separately.

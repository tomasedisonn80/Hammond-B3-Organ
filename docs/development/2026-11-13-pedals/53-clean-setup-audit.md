# Assignment 53 — clean setup and relocation audit

Owner: `/root/w09_a53_clean_setup_audit`.

Assignment **53/60**, wave **9**, of the current 2026-11-13 pedal session.
This is one newly dispatched worker. The spawning UI returned an aborted label,
but this worker activated, notified root and performed the recorded work.
No additional worker was dispatched.

## Ownership and source basis

Created only `docs/reviews/PEDAL_CLEAN_SETUP_FINAL.md` and this note. No source,
CMake, test, SDK, shared handoff, manifest or existing documentation file was
edited. No staging, commit or push was performed. Root owns integration and
publication under [AGENTS.md](../../../AGENTS.md).

Read the standing instructions, current README/status/next steps, project plan,
complete-review consolidation, operational handoff, BUILD/OFFLINE_INSTALL/
VST3_BUILD and relevant CMake/preset/install/SDK verification definitions.
Freshly read the complete extracted text of atlas pages **446 and 450**, covering
the testable offline foundation and the evidence boundary for early host/release
work. This is focused source reading, not another claim of complete-PDF coverage.
The PDF was independently included in the 534-file unchanged-source comparison.
Used the cloud runtime skill. Its environment-status tool was not exposed to
this worker; no environment configuration, dependencies, credentials or network
policy was changed, and no network acquisition was needed.

## Actual archive and setup

Fresh `git archive` of tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e` was
extracted to `/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces`.
All 534 files matched independently computed Git blob IDs, SHA-256 values and
executable-mode classification. All bytes and the file set matched afterward.
The reference root wave-8 archive's 534 files were also independently matched
before using its prebuilt ABI executable. Final wave-8 tree
`8af684dfe56f88222c52ff71d85a911ee1192fa1` changes only the six named Markdown
result files; the executable/data inputs are identical.

Actual toolchain: GCC 14.2.0, GNU Make 4.4.1, CMake/CTest 3.31.6 and Python
3.12.14. Private source, build, install, relocated and output paths contain
spaces and non-ASCII characters. Build directories remain outside source and
SDK trees. The SDK was verified read-only before and after native building.

The ordinary configure used default VST3 OFF, explicit testing OFF and an
intentionally absent SDK path. Core-only construction left the compiled profile
absent; selected offline targets then generated it. There is no supported
HAMMOND_BUILD_TOOLS option, so none was invented. Native construction used the
same source with the actual pinned SDK, testing OFF and explicit `lib` layout.
Its empty filtered CTest run correctly rejected rather than reporting a pass.

## Observed results and scope

The setup runner recorded **28 operational commands**: **25 successful commands and three
expected rejections**, with summed process wall time **49.318 seconds**. This
count is commands, not unit tests or CTest suites. No full ordinary/native matrix
was rerun. Two private-driver assertions needed correction, as retained below.

Fresh core construction took 6.679 seconds, subsequent five-tool construction
10.542 seconds, and actual native module construction 27.375 seconds. Offline
installation produced exactly 23 files. Native installation added a four-file
Linux bundle, preserving all native byte hashes and modes. Reinstallation into
that existing bundle rejected. The prefix then moved, and all original private
source/build directories were temporarily renamed; a finally block restored them.

From an unrelated Unicode directory and with HAMMOND_* variables removed, all
five installed tools and both plotters executed successfully. The three-second
phrase's entire 576,044-byte WAV equals the retained demo and has SHA-256
`a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1`.
Both generated SVGs parse as SVG XML and embed their actual CSV byte hash.

The freshly built, staged and relocated native module passed the independent
actual-module ABI executable: 9 instances, 691,878 assertions, 45 descriptors,
2,002 conversions, 73 accepted callbacks, 86 rejections, 7 state round trips,
6 lifecycle sequences, 229,725 reference frames and 217,972 audible frames.
Maximum observed audio error was zero and float checksum `af029009868faa04`.
The module remains 434,168 bytes, SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.
Its ordinary/reference profiles are the unchanged 4,545-byte `b36b0773…` profile.
The root ABI executable's SHA-256 is
`de4f307def0afeb410e704983d4f0e31628894fa2e175e5afe7daa2a8db11651`.
Both reference files were rehashed unchanged after execution.

This is one Linux/toolchain/filesystem result. No Windows/macOS, fresh-OS,
validator-suite, TSAN, device/DAW, physical calibration or subjective listening
pass is inferred. The ABI command is an actual new execution against this moved
module, rather than inherited credit from root's earlier suite.

## Retained setup-only corrections

1. The initial driver expected one of several guessed missing-directory phrases.
   The actual negative configure correctly exited 1 with `requires an existing
   external HAMMOND_VST3_SDK_ROOT`. Only the driver's wording assertion failed.
   After reading `VerifyVst3Sdk.cmake`, the exact observed diagnostic was checked
   and execution resumed after the completed command.
2. The driver assumed `check_vst3` disappeared when testing was OFF. Actual target
   help and `plugins/vst3/CMakeLists.txt` show it remains a wrapper around CTest
   with `--no-tests=error`; registered native tests are conditional. The corrected
   probe observed zero registered tests and directly executed that filtered
   CTest command, which exited 8 with `No tests were found` as required.

No project defect was attributed to either wrong probe assumption. No successful
build was repeated to hide them, and no production behavior or test was weakened.
`run_setup_audit.py`, `resume_setup_audit.py` and `resume_native_setup_audit.py`
retain the original and corrected private-driver paths with all logs.

## Evidence identities

All local intermediate evidence is under
`/workspace/scratch/f364bc93d920/a53-clean-setup/`. The complete receipts include
exact commands, working directories, expected/observed exits, durations, payload
hashes, source inventory, reference identities and both setup corrections.

| Local receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-inventory.json` | 140,154 | `be2f8216416df113e155817936941708edb2dc8e5a0f8dc5c61e013ce7940281` |
| `runtime-reference.json` | 613 | `9e6b01094458371b8059b0126c8997d968001f1aafd8e6420c0fa01bad7491b2` |
| `results.json` | 25,746 | `3cf85413ecb611dda71e84ea5b43301dafce6b53272e3f3752825baa17ed0107` |

| Retained artifact | SHA-256 |
| --- | --- |
| Installed console CSV | `dbaa075fcd7bea24b4a61a5df8f55faab53053244ad1e59126ba3f4d80fd89b2` |
| Installed console SVG | `76d8583e00977856e54e61fbb1691ff2f7ffb3e2e9f86e0ee5f807e9bdc203a4` |
| Installed pedal CSV | `3ff70b36b23e012112b6038cd450b6716d0fa1d32a0f18579e8578cad0b89374` |
| Installed pedal SVG | `c9cff420597e862644bbc8b2f68080757c1c1a1c8c192dc3118341e97764a255` |

## Command results

The three expected negative operations are missing-SDK configure (exit 1),
empty native CTest (exit 8), and reinstalling an existing native bundle (exit 1).
Every other row requires and observed exit 0.

| Recorded command | Exit | Seconds | Combined output log SHA-256 |
| --- | ---: | ---: | --- |
| toolchain-cmake | 0 | 0.086 | `f6e81c2559f3ce00c5fdad01d7b226c301f5d6b07ee04f65db6dbfdc1cc5970b` |
| toolchain-cxx | 0 | 0.003 | `00f7e3c3e6a0308d7b60cc02429720ef6000d84c0add523f7dc030058d19961b` |
| toolchain-python | 0 | 0.003 | `4c3569f5da09975434dd9fd9a91fadbc4367a91d8f3c3fab59e9241ab9ee4bd8` |
| presets | 0 | 0.005 | `ba3cd0b00f3f4a1f981a83a2773d18258c16efc53de9eb47f03c9177989d37bb` |
| offline-configure | 0 | 0.459 | `69907a11029033152ea7d77934aba0adcfb80fe37861d7ec2457948fa63068b8` |
| offline-target-help | 0 | 0.111 | `d7151160c0dae5f10226cca8c3edd4d6a31869aff31076a308c0357ffe36d4b9` |
| offline-test-discovery | 0 | 0.021 | `655b4edf543a99640d87b7cec2509f8071db3e631f77a63bd8b28f1533babfc4` |
| core-only-build | 0 | 6.679 | `2425507989e9398f8c18ce2f713c0122c9b33412e2d1cd31cc563119c845b2bd` |
| offline-five-tools-build | 0 | 10.542 | `7df4952a360b873c05cb85c316fd5786ff54d17dc2128affb42ea2f38d8b0354` |
| sdk-read-only-verification | 0 | 0.172 | `051362e9ff23d39e4a7deca56f743d37c83123398fef36971d14fffc9630cd49` |
| native-missing-sdk-rejection | 1 | 0.371 | `cf5cd410e838a2ecfba5370a8cafa90fbee94bbf9b82e473bc91b7be439780d0` |
| native-configure | 0 | 0.901 | `b93e3c029a0614139e46aaeb83eade73fc6efc8e46630abb33e0c9aa861d06c9` |
| native-target-help | 0 | 0.221 | `dbda2b49d8a746dd4223d870844b6e379940054949cb111f37a5891b6d5c3510` |
| native-test-discovery | 0 | 0.006 | `655b4edf543a99640d87b7cec2509f8071db3e631f77a63bd8b28f1533babfc4` |
| native-empty-suite-rejection | 8 | 0.005 | `7ef16aa36d24742ca40a283c3997f6b0e42393d3a342eade55ef3f66573a426b` |
| native-module-build | 0 | 27.375 | `a810cabe200e7818630267070b9b2b10f084dacf932696e0da9524b9bfe0a11b` |
| offline-install | 0 | 0.013 | `169427962b22a7d023c85321aa69dc9b00106d7b3de65c55c77d4189ccb47221` |
| native-install | 0 | 0.007 | `06ec90eaffefa0bb289ec5242d287cc7383cc7c098b2873375406655653a9a4a` |
| native-existing-destination-rejection | 1 | 0.005 | `46ffb804c784c9e14a71d1341d86c37f72d6efcd9abfde55608cd690f504fcce` |
| relocated-phrase | 0 | 0.301 | `a41b8e19525ae76c891170b3677964c27093ce88fcfb394754375683acf82d05` |
| relocated-hammond_model_info | 0 | 0.007 | `11a28002347425e56898115148f5c2ccb53364a0d6c62903da80ebf42126bfd3` |
| relocated-hammond_parameter_info | 0 | 0.003 | `71d300d5e074b7b00b28ac801739d47834898235ba286bf1efa80c1d2b65182c` |
| relocated-console-trace | 0 | 0.041 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| relocated-console-plot | 0 | 0.464 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| relocated-pedal-trace | 0 | 0.071 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| relocated-pedal-plot | 0 | 0.387 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| relocated-native-abi | 0 | 0.89 | `688e792adb4e371e528bcacfc5c76eedc42f5028a922a9a9b3e4c1294d241fc5` |
| sdk-read-only-verification-after | 0 | 0.169 | `051362e9ff23d39e4a7deca56f743d37c83123398fef36971d14fffc9630cd49` |

## Exact command arrays, rendered for replay

The JSON receipt remains authoritative for argument boundaries. The shell forms
below quote actual Unicode/spaces paths; the original runner used subprocess
argument arrays and never relied on shell splitting. `PYTHONDONTWRITEBYTECODE=1`
was set; `DESTDIR` and `CMAKE_INSTALL_MODE` were removed for local staging.
Installed runtime commands additionally removed all HAMMOND_* variables.

### 1. toolchain-cmake

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --version
```

### 2. toolchain-cxx

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
c++ --version
```

### 3. toolchain-python

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 --version
```

### 4. presets

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --list-presets
```

### 5. offline-configure

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S '/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces' -B '/workspace/scratch/f364bc93d920/a53-clean-setup/build Release vérifié' -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF '-DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/a53-clean-setup/SDK path deliberately absent'
```

### 6. offline-target-help

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build '/workspace/scratch/f364bc93d920/a53-clean-setup/build Release vérifié' --target help
```

### 7. offline-test-discovery

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir '/workspace/scratch/f364bc93d920/a53-clean-setup/build Release vérifié' --show-only=json-v1
```

### 8. core-only-build

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build '/workspace/scratch/f364bc93d920/a53-clean-setup/build Release vérifié' --config Release --parallel 2 --target hammond_core
```

### 9. offline-five-tools-build

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build '/workspace/scratch/f364bc93d920/a53-clean-setup/build Release vérifié' --config Release --parallel 2 --target hammond_render hammond_model_info hammond_parameter_info hammond_console_trace hammond_pedal_trace
```

### 10. sdk-read-only-verification

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces/tools/acquire_vst3_sdk.py' --verify-existing /workspace/scratch/f364bc93d920/vst3sdk
```

### 11. native-missing-sdk-rejection

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S '/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces' -B '/workspace/scratch/f364bc93d920/a53-clean-setup/native absent SDK é' -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=ON '-DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/a53-clean-setup/SDK path deliberately absent'
```

### 12. native-configure

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S '/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces' -B '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/f364bc93d920/vst3sdk -DCMAKE_INSTALL_LIBDIR=lib
```

### 13. native-target-help

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' --target help
```

### 14. native-test-discovery

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' --show-only=json-v1
```

### 15. native-empty-suite-rejection

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' -C Release --output-on-failure --no-tests=error -R '^(hammond_vst3_validator|test_native_)'
```

### 16. native-module-build

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' --config Release --parallel 2 --target HammondB3
```

### 17. offline-install

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --install '/workspace/scratch/f364bc93d920/a53-clean-setup/build Release vérifié' --config Release --component OfflineTools --prefix '/workspace/scratch/f364bc93d920/a53-clean-setup/stage original érable'
```

### 18. native-install

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --install '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' --config Release --component NativeVST3 --prefix '/workspace/scratch/f364bc93d920/a53-clean-setup/stage original érable'
```

### 19. native-existing-destination-rejection

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --install '/workspace/scratch/f364bc93d920/a53-clean-setup/build native érable' --config Release --component NativeVST3 --prefix '/workspace/scratch/f364bc93d920/a53-clean-setup/stage original érable'
```

### 20. relocated-phrase

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
'/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/hammond_render' --profile '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/share/hammond-b3-organ/nominal.b3p' --events '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/share/hammond-b3-organ/fixtures/pedals/pedal-phrase-v1.events' --output '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/pedal phrase été.wav' --sample-rate 48000 --frames 144000 --block-size 127 --seed 2704 --drawbars 006400000 --pedal-drawbars 32 --contacts ideal --percussion off --percussion-volume normal --percussion-decay slow --fail-on-clip
```

### 21. relocated-hammond_model_info

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
'/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/hammond_model_info'
```

### 22. relocated-hammond_parameter_info

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
'/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/hammond_parameter_info' --normalized 0.5
```

### 23. relocated-console-trace

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
'/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/hammond_console_trace' --profile '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/share/hammond-b3-organ/nominal.b3p' --scenario partial --sample-rate 48000 --seed 0 --output '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/console trace été.csv'
```

### 24. relocated-console-plot

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/plot_console_trace.py' --input '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/console trace été.csv' --output '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/console trace été.svg'
```

### 25. relocated-pedal-trace

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
'/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/hammond_pedal_trace' --profile '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/share/hammond-b3-organ/nominal.b3p' --scenario routing --sample-rate 48000 --seed 0 --output '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/pedal trace été.csv'
```

### 26. relocated-pedal-plot

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/bin/plot_pedal_trace.py' --input '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/pedal trace été.csv' --output '/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été/pedal trace été.svg'
```

### 27. relocated-native-abi

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup/unrelated output été`.

```sh
/workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_abi '/workspace/scratch/f364bc93d920/a53-clean-setup/stage déplacé with spaces/lib/vst3/HammondB3.vst3' /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/nominal.b3p
```

### 28. sdk-read-only-verification-after

Working directory: `/workspace/scratch/f364bc93d920/a53-clean-setup`.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/workspace/scratch/f364bc93d920/a53-clean-setup/érable source with spaces/tools/acquire_vst3_sdk.py' --verify-existing /workspace/scratch/f364bc93d920/vst3sdk
```

## Final document checks

The two owned files pass UTF-8/LF, final-newline and trailing-whitespace checks.
All 15 relative Markdown links resolve. The current session checker's complete-
note structural validator accepts the actual assignment title, owner and
narrative sections. That local check did not edit or promote the manifest;
root still owns substantive acceptance and completion state.

## Handoff and next action

The [public setup review](../../reviews/PEDAL_CLEAN_SETUP_FINAL.md) records the
findings, supported option behavior and scope. No production/build repair is
needed from this audit. Root was notified that VST3_BUILD.md's assignment-33
final next-gates paragraph should preserve its dated results while linking to
now-executed native evidence; that is coordinated with assignment 55, outside
this worker's two-file ownership. Current native platform, rights and actual
publication gates remain root's separate observed work.

Root should accept this note, include the two documents in its next review
checkpoint, run its necessary combined checks and publish with an expected-head
guard. Continue the actual final review assignments and use the new session's
explicit sixty-complete gate only after all sixty real workers finish. Preserve
all prior sessions, physical limits and unresolved release/acquisition gates.

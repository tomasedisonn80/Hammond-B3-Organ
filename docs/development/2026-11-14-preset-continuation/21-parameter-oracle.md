# A21 — Independent parameter integer oracle

Worker: `/root/w04_a21_parameter_oracle`, logical wave 4, 2026-11-14.
Session baseline: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
Observed HEAD during implementation and fresh CMake acceptance:
`35554c068492fe2b20c1f8a602d8354ae762dc42`.
The actual uncommitted A16 implementation is identified by the file hashes
below; HEAD alone does not identify this implementation or the new tests.

## Owned work and result

- Added `tests/test_preset_parameter_oracle.py`: integer significand construction,
  exact-rational nearest-even certificates, strict actual native/Python comparison
  under four caller modes, complete old45 digest, new metadata, all 47 actual CLI
  targets, unknown identities, finite-domain rejection and signed-zero checks.
- Added `tests/test_preset_parameter_boundaries.cpp`: narrow direct public-API
  probe with its own integer-derived expected values, actual native `FE_*` modes,
  byte-preserving failure checks and optional exact-bit output for Python.
- With integrator authorization, added one test-specific `CMakeLists.txt` block
  supplying both native target paths and build prerequisites. Generic Python/C++
  discovery remains unchanged; no neighboring-path or configuration-name guess
  is used.
- Added [independent review](../../reviews/PRESET_PARAMETER_ORACLE_REVIEW.md) and
  this execution record. No production source, existing test, historical fixture,
  shared status file, assignment ledger or baseline build was changed by A21.

**Accepted:** all eleven thresholds and their immediate neighbors, all twelve
canonical values, both selector identities, negative-zero canonicalization,
caller-mode preservation and invalid-output atomicity match the frozen law.
No new selector numeric defect was found. The two independent integer oracles
do not import either production table. Python's exact `Fraction` certificates
also establish nearest-even selection and the five downward-rounded midpoints.

**Compatibility finding:** old Python plain `+0` becomes `-0` only in downward
mode, while native retains `+0`. This predates A16 and was reproduced from the
actual `b79086f` Python source and registry for all 45 records under all four
modes. The integrator directed preservation of that existing behavior. The
review states this exception explicitly; new selectors have strict bit equality
and canonical positive zero in both languages.

## Executed commands and outcomes

Working directory for all commands:
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Toolchain: Linux x86-64, GCC 14.2.0 (Debian 14.2.0-19), Python 3.12.14, managed
CMake/CTest at `/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin`.

### Isolated current-source builds

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -frounding-math -Iinclude \
  src/ParameterBridge.cpp tests/test_preset_parameter_boundaries.cpp \
  -o /tmp/hammond-preset-a21-boundaries
/tmp/hammond-preset-a21-boundaries

g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -frounding-math -Iinclude -Itools \
  src/ParameterBridge.cpp tools/parameter_info.cpp \
  -o /tmp/hammond-preset-a21-parameter-info
HAMMOND_PARAMETER_INFO_EXECUTABLE=/tmp/hammond-preset-a21-parameter-info \
HAMMOND_PRESET_PARAMETER_BOUNDARIES_EXECUTABLE=/tmp/hammond-preset-a21-boundaries \
  python3 tests/test_preset_parameter_oracle.py -v
```

Results: native **688 successful conversions**, **296 atomic conversion
rejections**, **84 unchanged unknown-ID descriptor destinations**, all under
four standard modes. Python **6/6 methods passed**, consuming those actual native
vectors and performing **49 actual 47-record CLI calls**. The 496 new-selector
vectors agree bit for bit; 192 old-kind vectors retain the explicitly documented
legacy behavior. No cross-language checks were skipped.

### CMake discovery and ordinary Release build

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S . -B /tmp/hammond-preset-a21-cmake -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a21-cmake \
  --target test_preset_parameter_boundaries hammond_parameter_info -j 4
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a21-cmake \
  -R '^(test_preset_parameter_boundaries|python_test_preset_parameter_oracle|python_test_parameter_bridge|python_test_parameters)$' \
  --output-on-failure --no-tests=error
```

Configuration and fresh target builds succeeded. The core and its generated
pedal/fixed/scanner tables were rebuilt in the private directory; no older
library was paired with live changed headers. **CTest 4/4 passed** in 4.45 seconds:

| Test | Outcome |
| --- | --- |
| `test_preset_parameter_boundaries` | Pass |
| `python_test_parameter_bridge` | Pass; existing independent old39/43/45 guards retained |
| `python_test_parameters` | Pass; existing registry and numerical checks retained |
| `python_test_preset_parameter_oracle` | Pass; new six-method review suite |

`ctest --show-only=json-v1` additionally confirmed both test registrations and
the resolved environment values:

```text
HAMMOND_PARAMETER_INFO_EXECUTABLE=/tmp/hammond-preset-a21-cmake/hammond_parameter_info
HAMMOND_PRESET_PARAMETER_BOUNDARIES_EXECUTABLE=/tmp/hammond-preset-a21-cmake/test_preset_parameter_boundaries
```

The exact new CMake block is:

```cmake
if(TEST python_test_preset_parameter_oracle)
    set_property(TEST python_test_preset_parameter_oracle APPEND PROPERTY ENVIRONMENT
        "HAMMOND_PARAMETER_INFO_EXECUTABLE=$<TARGET_FILE:hammond_parameter_info>"
        "HAMMOND_PRESET_PARAMETER_BOUNDARIES_EXECUTABLE=$<TARGET_FILE:test_preset_parameter_boundaries>")
    list(APPEND HAMMOND_TEST_TARGETS hammond_parameter_info test_preset_parameter_boundaries)
endif()
```

### Additional focused verification

- Loaded `git show b79086f:tools/validate_parameters.py` and its actual old registry
  into a temporary Python module, selected each of the four supported executor
  modes, and checked all 45 old records at positive plain zero. **180/180 checks**
  confirm the sign exception already existed. The original mode was restored in
  `finally`; no archived file was edited.
- `python3 -m py_compile tests/test_preset_parameter_oracle.py` passed.
- Owned-path `git diff --check` passed before final report delivery.

### Original failure retained

The first strict native compile failed because one newly written `std::array`
used class-template argument deduction across both platform `uint64_t`
(`unsigned long` here) values and `ULL` constants. Giving that invalid-input
array the explicit type `std::array<std::uint64_t, 7>` resolved the test-only
portability issue. The subsequent isolated compile and ordinary CMake build
passed. The failed compile is not counted as a test pass; production code was
unchanged.

## Exact checked identities

All entries below are SHA-256. These production bridge inputs match the A16
record and remained unchanged through A21 acceptance.

| Input | SHA-256 |
| --- | --- |
| `src/ParameterBridge.cpp` | `296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220` |
| `include/hammond/ParameterBridge.h` | `cd313711737f94e5f7f7b0dd73851347b9c4e53b3962d5d40d7e7c37883293d3` |
| `include/hammond/Types.h` | `0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8` |
| `tools/validate_parameters.py` | `bd8c451d5d1b648bdd38db2db384c8322abe29ad2a54cfeeff8554340fdb4505` |
| `tools/parameter_info.cpp` | `3ea19f4c6e512161a7c3effe244a878a81a042d9787b48231db4a4fee54233bc` |
| `data/parameter-registry.json` | `aedaa09e47fc2baba4a08484cce84916f2a27edac55d45f03f167f41c84bd6e2` |
| `tests/test_preset_parameter_boundaries.cpp` | `3f431d729946e2ed674d12661416fc2a0976a74457234af97856250a03b77a96` |
| `tests/test_preset_parameter_oracle.py` | `8b7eace88a7bcb8c12b227447b43ae6f7bb8e090eade63542031dbe122eaf85c` |
| Current complete `CMakeLists.txt`, including A13's earlier generator integration | `1c569b0dc5d5afbe5b99ff8529d457ca736ad8e82a36105336badbd4e9841e53` |

| Executed artifact | SHA-256 |
| --- | --- |
| `/tmp/hammond-preset-a21-boundaries` | `58b05dc021dd443bd434bce8553afb72f1b7c0aad447686f4211c6f3fd46ef77` |
| `/tmp/hammond-preset-a21-parameter-info` | `846264d45677f64bf77eee7c53f558e7b3a222de44186a2c3fcd43a8c8962f28` |
| `/tmp/hammond-preset-a21-cmake/test_preset_parameter_boundaries` | `f613ff6ff88986ca0755faca0a6bf7560b0848e24b84a5050c39187a10a5cdad` |
| `/tmp/hammond-preset-a21-cmake/hammond_parameter_info` | `f3f56ede7fcd93a81423ac78ea86cf959e34ef821d812f1396f607808d93992e` |

## Handoff and next gate

The new tests are ready for the integrator's coherent source snapshot. Build
their required targets before filtered CTest and retain `--no-tests=error`.
The private executables are execution artifacts, not required repository inputs;
normal CMake builds produce the correct test paths.

Next acceptance requires the actual current native plugin and host consumers:
47 exported descriptors and exact identities, state4 and old-state restoration,
old-bank/new-selector same-sample ordering, absent/unchanged queues, carried
points and rollback. Run those separate owners' current-source gates and the
whole integration suite after their changes settle. This scalar review does
not close native host, UI, allocation, macOS/Windows, real-device, physical
latching, loaded-gain or specimen-fidelity gates.

A21 made no commits, pushes, child assignments or shared-root-document edits.
The integrator owns acceptance, current status and publication.

# A16 — Append-only parameters and exact selector conversion

Worker: `/root/w03_a16_parameter_bridge`, logical wave 3, 2026-11-14.
Session base: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
Observed checkout at assignment start: `70b335480323329c7f5b207d5f58086c5b854960`.
The integrator's unrelated macOS color repair advanced HEAD to
`352a398e4f004467c2dab081168be3d8b5206ea9` during this work. The hashes below
identify the actual uncommitted source tested; neither commit alone identifies
this implementation. The integrator owns coherent full-tree acceptance and publication.

## Implementation and preserved identities

Appended IDs 20480 and 20481 for upper/lower `preset_selector` controls, each
plain 0–11, default 11, eleven steps, unit `preset-key-index`, and permanent
`SelectPreset` / `select_preset` target with index 0. Registry schema is 4,
count 47, model `exclusive-fixed-percussion-pedal-console-v4`. Root provenance
records the new documentary scope, while the complete old45 records remain
unchanged, including source pages, labels, defaults and normalized metadata.
Both new records match the exact source-page list and metadata strings in
`PRESET_STATE_PARAMETER_CONTRACT.md`.

The compiled C++ bridge has separate literal arrays for eleven nearest-binary64
midpoints and twelve canonical normalized values. Only the new event kind uses
them. Python gives only `preset_selector` a literal-table branch and retains the
old integer-ratio quantizer and existing plain arithmetic for every old kind.
There is no runtime division by 11, rounding-mode change, state, allocation,
JSON parsing or host dependency in native conversion. Equality selects the
higher key at every boundary, including the five downward-rounded fractions
3/22, 5/22, 7/22, 15/22 and 17/22. New-selector plain -0 canonicalizes to +0;
older signed-zero behavior remains unchanged. Invalid values/IDs preserve native
destinations. The public function signatures and descriptor field layout are
unchanged; the new count/model/header was delivered to the integrator during
implementation.

`hammond_parameter_info` now inventories 47 records and spells `select_preset`.
Its diagnostic schema remains 2 and its verification scope remains SDK-free;
this executable does not inspect a native plugin. Current count/schema/model
checks now reflect 47/4 without rewriting prior evidence.

The historical `examples/fixtures/pedals/pedal-catalog-v1.json` is unchanged.
Its schema-3/count45 control identity now compares against the explicit old45
ID subset of the active registry, sorted numerically and hashed as compact
sorted-key ASCII JSON. The install test preserves the historical catalog fields,
checks that full-record digest, and compares all exposed old45 compiled metadata
with the matching source records. Installed current enumeration expects 47.
The original39 and version2/43 full-record compatibility guards remain intact.

## Executed checks

All commands ran in `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Toolchain: GCC 14.2.0 (Debian 14.2.0-19), Python 3.12.14. The build used fresh
source translation units, A13's generated fixed table, the retained generated
pedal table, and the unchanged nominal profile. No full-tree build or stale
library/header combination was used.

1. `python3 tools/validate_parameters.py` — exit 0; exactly 47 parameters for
   the required schema4 model.
2. `python3 tests/test_parameters.py -v` — **32/32 methods passed**. Covers exact
   new metadata, all canonical values and boundaries, finite/domain/integrality
   rejection, unchanged old39/43/45 records, unknown identity examples, and strict
   parser/metadata rejection. Independent `Fraction` arithmetic searches the
   ordered binary64 bit space and chooses the nearest value with ties to even;
   it does not consume the production tables as its sole oracle.
3. Built the diagnostic with strict project warnings and explicit rounding-mode
   semantics, then ran the cross-language suite:

   ```sh
   g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
     -Wshadow -Werror -frounding-math -Iinclude -Itools \
     src/ParameterBridge.cpp tools/parameter_info.cpp \
     -o /tmp/hammond-preset-a16/hammond_parameter_info
   HAMMOND_PARAMETER_INFO_EXECUTABLE=/tmp/hammond-preset-a16/hammond_parameter_info \
     python3 tests/test_parameter_bridge.py -v
   ```

   **13/13 methods passed, 150 actual diagnostic CLI invocations**. Covers current
   metadata/targets, every old and new threshold and adjacent float, all twelve
   new canonical inputs, independent rational selector decisions, explicit five
   downward-rounded equality cases, preserved compatibility digests, decimal
   syntax/domain bounds, signed zero/subnormal input, locale and stdout failure.
4. Built and ran the native Engine integration test from fresh source:

   ```sh
   g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
     -Wshadow -Werror -frounding-math -Iinclude -Itests \
     -I/workspace/scratch/a472c29da8b3/build-baseline/generated \
     -I/tmp/hammond-preset-a13/generated \
     -DHAMMOND_TEST_PROFILE='"/workspace/scratch/a472c29da8b3/build-baseline/nominal.b3p"' \
     -DHAMMOND_SOURCE_DIR='"/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"' \
     tests/test_parameter_bridge.cpp src/ParameterBridge.cpp src/Engine.cpp \
     src/ControlState.cpp src/FixedRegistration.cpp src/ContactBank.cpp \
     src/PedalRouting.cpp src/PedalVoice.cpp src/Percussion.cpp src/Profile.cpp \
     src/TonewheelBank.cpp -o /tmp/hammond-preset-a16/test_parameter_bridge
   /tmp/hammond-preset-a16/test_parameter_bridge
   ```

   Exit 0: **6,327 independent conversions, 42,666 atomic conversion rejections,
   all 47 live Engine targets; all four standard rounding modes passed**.
   Includes all ID holes through 20482, canonical bit equality, every threshold
   and both neighbors, positive-zero selector canonicalization and preserved old
   negative-zero results, unchanged caller mode after successful/rejected calls,
   exact event offsets, and destination sentinel preservation. Live selector
   actions cover all twelve values on both manuals, retained fixed memory behind
   Cancel, old same-value B reassertion, unchanged banks and independent pedals,
   held notes/contacts, source phases, frame clock and percussion readiness.
5. A local Python `ctypes.CDLL(None)` fenv probe selected the four supported
   glibc modes (0, 0x400, 0x800, 0xc00), restored the original mode in `finally`,
   and checked both selector records against the independent rational oracle:
   **360 successful threshold/canonical conversions**, plus negative zero and
   NaN/infinity/range/fraction rejection. Every call retained its caller mode.
   This is supplementary executor evidence; the portable retained native test
   names `FE_TONEAREST`, `FE_DOWNWARD`, `FE_UPWARD` and `FE_TOWARDZERO` directly.
6. Invoked `tests/test_pedal_catalog.py::validate_catalog` with the unchanged
   catalog and `/workspace/scratch/a472c29da8b3/build-baseline/nominal.b3p` —
   exit 0. Invoked the exact reusable install-test
   `OfflineInstallTests.assert_historical_parameter_compatibility` with the
   current compiled CLI JSON and unchanged catalog — exit 0. These execute the
   repaired comparison logic; the full PCM/relocated-install workflows were not
   run here and remain for the coherent integration build.
7. Owned-path `git diff --check` passed. Original old45 digest and historical
   catalog byte hash were checked before and after edits. Fresh text reading of
   atlas pp. 121–126 and 397–402 confirms the source boundary, permanent IDs,
   retained banks, fixed versus adjustable selection, and engineering evidence
   limits. The frozen contracts remain the normative new conversion law.

## Original failures and corrections

The first hand-written diagnostic build incorrectly listed `src/Decimal.cpp`;
Decimal is header-only at `include/hammond/detail/Decimal.h`. That compile failed
and the immediately attempted cross-language suite correctly reported its
missing executable. Removing the nonexistent input produced the successful
build and 13-method run above. No parser implementation was changed.

The first native strict-warning compile rejected an `int` initializer-list
iteration narrowed to `uint8_t` under `-Werror=conversion`. Replacing it with an
explicit `std::array<std::uint8_t, 12>` preserved the exact test sequence and
passed the fresh strict build. Neither failed compile is counted as a test pass.

## Checked source and artifact identities

All hashes are SHA-256. The two docs are the current explanations of the same
implementation; they do not independently qualify native exports.

| Owned file | SHA-256 |
| --- | --- |
| `include/hammond/ParameterBridge.h` | `cd313711737f94e5f7f7b0dd73851347b9c4e53b3962d5d40d7e7c37883293d3` |
| `src/ParameterBridge.cpp` | `296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220` |
| `data/parameter-registry.json` | `aedaa09e47fc2baba4a08484cce84916f2a27edac55d45f03f167f41c84bd6e2` |
| `tools/validate_parameters.py` | `bd8c451d5d1b648bdd38db2db384c8322abe29ad2a54cfeeff8554340fdb4505` |
| `tools/parameter_info.cpp` | `3ea19f4c6e512161a7c3effe244a878a81a042d9787b48231db4a4fee54233bc` |
| `tests/test_parameters.py` | `1f32e26fc1237d64c51751fdd0e0c236bb0270605781059c625463571bfbdf64` |
| `tests/test_parameter_bridge.cpp` | `1997eaf472755eb7fc12cc41f183f53669293669c7a749a0049a3ea45ff02eb2` |
| `tests/test_parameter_bridge.py` | `8f5d82a9640f57c1097951b9441468a85804e0f0df7aae7628c57f38f48a4f09` |
| `tests/test_pedal_catalog.py` | `a52c2c763d243e47b83e5f6f9cd7dda59c97d15a0ca4da5a1d74bf7a73e3c99b` |
| `tests/test_install.py` | `f7ff6bc277924f551ca9f65e803e66bdd75dd18e7b27b11011d49f796c521a4d` |
| `docs/PARAMETERS.md` | `0f564979df9648f5030c12f92c28f0494a243e64b105d1675b9c9ff4b9f77022` |
| `docs/PARAMETER_BRIDGE.md` | `f35d12a2ebe34bc02daca9a72d3bd93ee0912fe684a54ffd8c0b6d102e4718ab` |

Selected concurrent dependency identities actually consumed by the isolated
build (A13/A14 ownership; unchanged by A16):

| Dependency | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `include/hammond/Engine.h` | `da1adc2e635e5acfa3f214447b722122c3a162eb9ec602ba14fa744eb9d39ba6` |
| `include/hammond/FixedRegistration.h` | `4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `src/ControlState.cpp` | `9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |

| Identity | SHA-256 |
| --- | --- |
| All 45 previous complete records, canonical sorted ASCII JSON | `13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad` |
| Historical pedal catalog bytes | `f064cdda432791703f1853d9cde52faa3cd5bf9899b999ad5b38ee64bb1ed5b7` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| A13 generated fixed-registration header | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |
| Isolated parameter-info executable | `846264d45677f64bf77eee7c53f558e7b3a222de44186a2c3fcd43a8c8962f28` |
| Isolated native parameter-bridge test | `e8d9b8532c4d72e95c81254fcab7655a6eaa78e741ebbda68f0b69776962b368` |

## Handoff and remaining gates

The stable header, two descriptors, literal conversion branch, registry and CLI
are ready for the concurrent publication/HostTimeline and native adapters. Build
one coherent source snapshot after those owners finish. Run CMake-discovered
`test_parameter_bridge`, `python_test_parameters`, `python_test_parameter_bridge`,
`python_test_pedal_catalog` and `python_test_install` with their required built
executables and `--output-on-failure --no-tests=error`. The last two full workflows
are explicitly pending this integration; only their repaired comparison logic
was run here.

Actual VST3 47-record exports, state4/controller restoration, host alias/carry/
rollback behavior, StateExchange/standalone raw fixed-mode publication and
callback allocation are separately owned continuation gates. This work does not
claim those gates, physical latching, loaded preset gains, host/device deadlines,
new real-device evidence or a measured instrument match. No historical catalog,
source PDF, historical registry fixture, plugin UUID or other worker's source was
edited. A16 made no commits, pushes, manifest edits or shared status-document
changes.

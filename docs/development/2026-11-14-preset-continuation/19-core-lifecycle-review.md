# A19 — Independent fixed-registration lifecycle review

Assignment: **A19, wave 4**, worker `/root/w04_a19_core_lifecycle_review`.
Date: **2026-11-14 UTC**. This is the first wave-4 core acceptance assignment
after the accepted A13/A14 prerequisites; A17 host and A18 UI work remained
separate concurrent ownership. No child workers were dispatched.

## Result and owned files

**Pass; no production defect found or repaired.** The independent
[review](../../reviews/PRESET_CORE_LIFECYCLE_REVIEW.md) gives the source findings,
test design, coverage and limitations. Owned additions are:

- `tests/test_fixed_registration_lifecycle.cpp`
- `docs/reviews/PRESET_CORE_LIFECYCLE_REVIEW.md`
- This execution note.

The new test covers fixed-active and Cancel-held memory across all supported
ordered rate pairs, successful live state4 restoration during attack/release/
partial contact travel and evolving percussion readiness, cold load, truthful
last-rendered diagnostics, and rejected rates/restores with future continuation.
Its bank reference reads only `tests/PresetTestOracle.h`'s independent literals.
The subject and bank reference are independently prepared and continuously run;
closed-form phase, contact and readiness calculations supply additional oracles.

## Actual source and preparation

Working directory:

```text
/workspace/scratch/a472c29da8b3/Hammond-B3-Organ
```

Observed HEAD: `352a398e4f004467c2dab081168be3d8b5206ea9`.
The production implementation under review is an **uncommitted overlay**, not
the code at that commit alone. The stable core/I/O translation units and their
transitive project headers were copied before compiling into
`/tmp/hammond-preset-a19`. Their hashes below matched the corresponding live
repository files after the final execution. This avoids mixing later live
headers with an older compiled core. Separately changing adapter/UI files were
not copied or linked.

The frozen snapshot contains ten source translation units:

```text
ContactBank ControlState ControlStateIO Engine FixedRegistration
PedalRouting PedalVoice Percussion Profile TonewheelBank
```

The admitted fixed-data header was copied from
`/tmp/hammond-preset-a13/generated/hammond/generated/FixedRegistrationData.h`.
The generated pedal header and `nominal.b3p` were copied from
`/workspace/scratch/a472c29da8b3/build-baseline`. The baseline directory was read
only. No generator, profile, source JSON/CSV or PDF was changed by A19.

Toolchain: `g++ (Debian 14.2.0-19) 14.2.0`, C++20. CMake was not invoked for
this isolated build. Inspection confirmed the existing test source glob will
discover the new regression in a later coherent configuration.

## Executed commands and outcomes

Each source stem `NAME` above was compiled separately with this exact command
shape and the retained source/include paths:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -I/tmp/hammond-preset-a19/include -I/tmp/hammond-preset-a19/generated \
  -I/tmp/hammond-preset-a19/tests \
  -c /tmp/hammond-preset-a19/src/NAME.cpp -o /tmp/hammond-preset-a19/NAME.o
```

The new regression was compiled/linked with the following command, using only
those newly built objects:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -I/tmp/hammond-preset-a19/include -I/tmp/hammond-preset-a19/generated \
  -I/tmp/hammond-preset-a19/tests \
  '-DHAMMOND_TEST_PROFILE="/tmp/hammond-preset-a19/nominal.b3p"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"' \
  /tmp/hammond-preset-a19/tests/test_fixed_registration_lifecycle.cpp \
  /tmp/hammond-preset-a19/ContactBank.o /tmp/hammond-preset-a19/ControlState.o \
  /tmp/hammond-preset-a19/ControlStateIO.o /tmp/hammond-preset-a19/Engine.o \
  /tmp/hammond-preset-a19/FixedRegistration.o /tmp/hammond-preset-a19/PedalRouting.o \
  /tmp/hammond-preset-a19/PedalVoice.o /tmp/hammond-preset-a19/Percussion.o \
  /tmp/hammond-preset-a19/Profile.o /tmp/hammond-preset-a19/TonewheelBank.o \
  -o /tmp/hammond-preset-a19/test_fixed_registration_lifecycle
/tmp/hammond-preset-a19/test_fixed_registration_lifecycle
```

The first complete strict build took **9.971 seconds**, followed by a passing
initial execution. The final test revision added an identical-controls live
round trip against untouched future continuation, explicit physical-detector
preservation at restore, and observed clean-cache preparation for rejected
operations. It rebuilt in **2.102 seconds**, then ran in **0.830 seconds**, exit
**0**, with no compiler diagnostics or runtime stderr. There were no failed
builds or runs in this assignment. The final stdout is:

```text
fixed registration lifecycle: 72 rate/route/contact scenarios, 288 preserved rate boundaries, 740 live restores, 308 state4 round trips, 72 cold loads, 100 rejected rates, 84 rejected restores, 80256 exact audio frames; 32760 phase, 43920 position, 395280 contact-bit and 360 readiness oracles; 5412 full snapshots; passed
```

Temporary replay material is retained in `/tmp/hammond-preset-a19`:
`build-commands.json`, `input-sha256.json`, the first/final stdout and stderr,
and `final-run.json`. The manifest raw-byte SHA-256 is
`3729f3c94bc638a5d8b60a94eb37d49a342a501661dc92b19fada8515ed8e083`.
The final executable SHA-256 is
`f16073d31e3af254c5fdaf83df69296ee982b907d72f97799c2b2714a3726c46`.
The permanent file hashes below and compile command identify the inputs even
if temporary build outputs are later removed.

Final owned-file checks found no trailing whitespace or broken relative Markdown
links. The JSON manifest reproduced below exactly matched the retained manifest;
all 29 frozen inputs still matched their hashes, and each corresponding live
repository input still matched. Owned-path `git diff --check` also returned 0;
the new files were checked directly because they remained untracked.

## Complete frozen input SHA-256 manifest

Repository inputs use repository-relative paths. `generated/` and
`nominal.b3p` are relative to `/tmp/hammond-preset-a19`.

```json
{
  "generated/hammond/generated/FixedRegistrationData.h": "66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6",
  "generated/hammond/generated/PedalRoutingData.h": "efddce2ea3619a7dd9e153382e307928f7aed60bdb8a0318ca6c0e71ee5f6034",
  "include/hammond/ConsoleModel.h": "e6ef911961c1aca1ce72bca8d2cfba9c765665d7cef30446adfe53b9ba59db51",
  "include/hammond/ContactBank.h": "a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d",
  "include/hammond/ControlState.h": "aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856",
  "include/hammond/ControlStateIO.h": "7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081",
  "include/hammond/Engine.h": "da1adc2e635e5acfa3f214447b722122c3a162eb9ec602ba14fa744eb9d39ba6",
  "include/hammond/FixedRegistration.h": "4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0",
  "include/hammond/PedalRouting.h": "e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8",
  "include/hammond/PedalVoice.h": "694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf",
  "include/hammond/Percussion.h": "5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722",
  "include/hammond/Profile.h": "b1180b3dc04030e0555ef3eb44a21617fc06e93150a9ecb48ebb05955b3e5fd0",
  "include/hammond/TonewheelBank.h": "694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b",
  "include/hammond/Types.h": "0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8",
  "include/hammond/detail/Decimal.h": "ae2c63ec61e823fda198a4951e029df11184980c9bc8394142a2d46951338c42",
  "nominal.b3p": "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f",
  "src/ContactBank.cpp": "91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1",
  "src/ControlState.cpp": "9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d",
  "src/ControlStateIO.cpp": "3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb",
  "src/Engine.cpp": "ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a",
  "src/FixedRegistration.cpp": "690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d",
  "src/PedalRouting.cpp": "8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af",
  "src/PedalVoice.cpp": "88fb5afa936784be351b2940ee6f81216975112f860b007d40f3b6a3d9f7c6ba",
  "src/Percussion.cpp": "823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a",
  "src/Profile.cpp": "80f5c7456311c77a83df23c548c02cabbf9c1cf1621cff89867d0d0c688ebe54",
  "src/TonewheelBank.cpp": "ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b",
  "tests/PresetTestOracle.h": "c2361bc68ff297977e246da391872fc69fe380d8bdd6230efb6a77a9aad61274",
  "tests/TestSupport.h": "8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5",
  "tests/test_fixed_registration_lifecycle.cpp": "23e53cd0abf1a96af0c80369c5c0bba7cdef17d68a07383019c2f0e1f743ce4f"
}
```

## Handoff

Root owns integration of the new glob-discovered regression in a coherent
complete build, shared status/next steps/development-log updates, final source
freeze and publication. This result qualifies the named core/I/O lifecycle
inputs, not unfinished host/UI consumers or every test at repository HEAD.
No full CMake/CTest, sanitizer, allocation, native/host/device, packaging or
hosted CI gate was run by A19. The independent review retains exact row-matrix
and detector-edge scope limits and all physical evidence boundaries.

No other worker's file, shared status file, baseline build, source/catalog/PDF,
Git ref or remote was modified. No commit or push was made.

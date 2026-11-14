# A26 — Strict rotary profile compiler and native field audit

Actual worker `/root/w05_a26_profile_compiler`, wave 5, 14 November 2026.
Owned `tools/compile_rotary_profile.py`, `tests/test_compile_rotary_profile.py`,
`docs/reviews/WAVEFORM_PROFILE_COMPILER.md`, this note and the compact
[result](../reports/a26-profile-compiler.json). No nested workers, commits,
ledger/shared-status edits, CMake/CI changes, native implementation/header
changes, shared build mutations or qualification-runner changes.

Read AGENTS, current scope/checkpoint/assignment manifest, complete M0–M9 plan,
atlas synthesis and rotary evidence boundary, renderer contract, build plan,
existing validator and `RotaryTypes.h`. Observed HEAD
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`. The owned new files are an overlay;
the full shared waveform experiment remained frozen and separately owned.

## Result and integration interface

The standard-library-only compiler reuses the existing strict validator and
emits all 28 double fields as exact binary64 hex literals, two directions and
two commands, preserving Horn/Drum and Left/Right order and admitted SI units.
It stamps the source's exact-byte SHA-256 and admitted profile/model/contract IDs.
Unknown authoring quantities and arbitrary evidence prose are not converted into
runtime constants or interpolated into C++ code. The output is deterministic and
published only after complete admission using same-directory temporary output,
flush/fsync/close and `os.replace`; ordinary failures preserve the previous file.

Agreed directly with A25: `RotaryNominalProfile.h`, namespace
`hammond::rotary::generated`, `kProfileId`, `kProfileSha256`, `kModelId`,
`kContractId` and `inline Profile nominal_profile() noexcept`. A25 consumed the
generated nominal header in its private renderer author build. Root was informed
before implementation and retains CMake/native-target and MinGW ownership.

## Exact identities

| Input or result | SHA-256 |
| --- | --- |
| `tools/compile_rotary_profile.py` | `7f17c3a516f678834dcabdb3ef3637d4ee90db03476b4815388d3f78fe733620` |
| `tests/test_compile_rotary_profile.py` | `c8a701a1deca464a7b4ed2bfc1df907f17dc7d9cd9d440167fd2eb39d0fcf74a` |
| `tools/validate_rotary_profile.py` | `260b63aaf3e22e136ce85143565c5df721ad2869b4ed377f1c5e95d454de5279` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| Nominal source JSON | `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443` |
| Generated nominal header | `d51f3e6edf4f44f87ed65f9a80b9932299ee8d5fa52a2fad5b5d011a454a05a5` |

## Actual verification

From `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`:

```sh
mkdir -p ../a26-profile-compiler/generated
python3 tools/compile_rotary_profile.py \
  --input data/rotary/nominal-research-v1.json \
  --output ../a26-profile-compiler/generated/RotaryNominalProfile.h
python3 tests/test_compile_rotary_profile.py \
  --report ../a26-profile-compiler/portable-tests.json
python3 tests/test_compile_rotary_profile.py --cxx /usr/bin/g++ \
  --native-work-dir /workspace/scratch/e3cacb90cc81/a26-profile-compiler/native \
  --report /workspace/scratch/e3cacb90cc81/a26-profile-compiler/compiler-tests.json -v
python3 tests/test_rotary_profile.py
```

Portable suite: **16/16**, zero skips, **0.339 s**. Explicit native mode:
**19/19**, zero skips, **3.672 s**. Existing validator suite: **33/33**, **1.603 s**.
Actual GCC 14.2.0 strict C++20 compilation and execution passed for four
independent full-Profile observers, five escaped string payloads and a
two-translation-unit header-only linkage/independent-value check. All **128
physical field comparisons** and **16 identity comparisons** passed; the compact
report retains the actual field bits and compiler/source/executable hashes.

The portable suite also verifies the complete source field mapping, exact raw
hashes, deterministic path/hash-seed behavior, malicious text admission/escaping,
invalid/duplicate-key/nonfinite/range/unit/schema rejection, alias rejection and
unchanged existing output after both validation and injected publication errors.
No optional package, SDK, network or core archive was required.

## Limits and concrete next action

The [review](../../../reviews/WAVEFORM_PROFILE_COMPILER.md) gives exact semantics,
commands and integration dependencies. Root should add a build-tree custom
command depending on compiler, validator and nominal JSON, then attach the header
to the native research executable outside `BUILD_TESTING`. Its output parent
must be created first. Independent CLI acceptance remains separate and was not
claimed here. MSVC/AppleClang/MinGW were not executed. File publication is atomic
for normal process failure, not a power-loss directory-durability guarantee.
R4 full parity, R5/R6 and physical M7 remain their existing separate gates.

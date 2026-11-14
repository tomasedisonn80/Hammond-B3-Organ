# R4 build-tree rotary profile compiler

A26 implementation and source-to-Profile review, 14 November 2026. The
[compiler](../../tools/compile_rotary_profile.py) projects a strictly admitted
external research profile into the existing C++20 `hammond::rotary::Profile`.
It adds no physical constants, Engine integration, runtime JSON parser, SDK or
optional Python package. Its numerical and physical boundaries remain those of
[rotary-numerics-v1](../ROTARY_NUMERICAL_CONTRACT.md) and the
[renderer contract](../ROTARY_RENDERER_CONTRACT.md).

The [retained result](../development/2026-11-14-waveform-continuation/reports/a26-profile-compiler.json)
identifies the actual source bytes, strict compile commands, observed native
field bits and test outcomes. Committed HEAD during this work was
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`; the new compiler/tests are an
uncommitted overlay at that checkpoint. This record does not qualify the whole
working tree or the simultaneously running full waveform experiment.

## Generated interface and values

A25 and A26 agreed the build-tree filename `RotaryNominalProfile.h` and namespace
`hammond::rotary::generated` before implementation:

| Declaration | Meaning |
| --- | --- |
| `inline constexpr std::string_view kProfileId` | Admitted external `profile_id` |
| `inline constexpr std::string_view kProfileSha256` | SHA-256 of the exact bounded input bytes read by the validator |
| `inline constexpr std::string_view kModelId` | Admitted `model_id`; compile-time checked against the public type contract |
| `inline constexpr std::string_view kContractId` | Admitted numerical `contract_id`; compile-time checked against the public type contract |
| `[[nodiscard]] inline Profile nominal_profile() noexcept` | A fresh value containing all 32 physical fields, with Horn/Drum and Left/Right array order preserved |

The source default remains
[`data/rotary/nominal-research-v1.json`](../../data/rotary/nominal-research-v1.json),
SHA-256 `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443`.
The compiler does not silently substitute that default: both `--input` and
`--output` are required, allowing the build rule to identify its exact input.
Its resulting nominal header is 2,722 bytes, SHA-256
`d51f3e6edf4f44f87ed65f9a80b9932299ee8d5fa52a2fad5b5d011a454a05a5`.
The generated header belongs in the build tree and is not checked into source.

The compiler calls the existing `load_profile_with_digest` once, then uses its
fresh `normalized_profile` projection. All schema, evidence, unit, finite-number,
duplicate-key, bounds, geometry and command admission remains in that validator.
Unknown physical quantities remain authoring unknowns; none becomes a runtime
zero or a new inferred parameter. The only additional admission concerns output
path identity and a regular-file destination.

Every one of the 28 runtime doubles is emitted with Python's exact hexadecimal
binary64 representation. This preserves signed zero, subnormals and the binary64
value admitted from a JSON integer or decimal. No decimal truncation, coordinate
transform, unit conversion, speed derivation or arithmetic rescaling is applied.
The two direction values and two commands retain their admitted meanings.
Compile-time guards require an IEEE-754 binary64 `double` and matching model and
numerical contract identities.

Only admitted identifiers and the raw-source hash enter C++ string literals.
Source prose and filesystem paths are never inserted into generated comments or
code. The string encoder produces ASCII source with fixed three-digit octal
escapes for quotes, backslashes, question marks and non-ASCII UTF-8 bytes, so
adjacent characters cannot extend an escape. There are no timestamps, absolute
paths, key-order dependencies or locale-sensitive numeric spellings in the
header. Reformatting or reordering source JSON changes its raw-byte digest while
preserving the physical field projection.

## Publication and CLI behavior

The output parent must already exist. Validation and complete header formation
precede any temporary output creation. Input/output path aliases and hardlinks
are rejected, as are existing nonregular destinations. An admitted new header
is written to a same-directory temporary file, flushed and `fsync`ed, closed,
then published using `os.replace`. Ordinary validation/write/replace failures
preserve the existing destination bytes and modification time and clean up the
temporary file. This is normal-process atomic publication; directory metadata is
not separately synced for a power-loss durability claim.

Success returns exit 0 and one JSON identity record with `status: compiled`.
Rejections return exit 2 and one JSON error record with `status: rejected`.
`--help` retains ordinary argparse help. Unknown or abbreviated flags reject.
The Python API exposes `compile_header(path)` as `(ASCII bytes, identity)` and
`compile_profile(input_path, output_path)` as atomic publication plus identity.

From the repository root, an actual generation command is:

```sh
mkdir -p ../a26-profile-compiler/generated
python3 tools/compile_rotary_profile.py \
  --input data/rotary/nominal-research-v1.json \
  --output ../a26-profile-compiler/generated/RotaryNominalProfile.h
```

The integrator should declare the profile, this compiler and
`tools/validate_rotary_profile.py` as custom-command dependencies; create the
generated parent; list the generated header as a native executable input; and
add its parent as a private include directory. The executable/generation rule
belongs outside `BUILD_TESTING`, as specified in the existing
[build plan](../WAVEFORM_BUILD_PLAN.md). Keep the research tool outside the fixed
install inventories. A25 successfully used this generated interface in its
private renderer build; that worker's CLI evidence remains separately owned.
A26 did not change CMake, CI, any native implementation/header, the shared build,
or Git HEAD.

## Executed verification

Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Native scratch: `/workspace/scratch/e3cacb90cc81/a26-profile-compiler/`.
The compiler was GCC `14.2.0` (`Debian 14.2.0-19`) on Linux x86-64. The
[test suite](../../tests/test_compile_rotary_profile.py) needs only the standard
library for its ordinary invocation. Native testing is an explicit additional
mode; an unavailable requested compiler fails rather than producing a skip.

| Actual command | Observed outcome |
| --- | --- |
| `python3 tests/test_compile_rotary_profile.py --report ../a26-profile-compiler/portable-tests.json` | 16/16 methods, zero skips, 0.339 seconds |
| `python3 tests/test_compile_rotary_profile.py --cxx /usr/bin/g++ --native-work-dir /workspace/scratch/e3cacb90cc81/a26-profile-compiler/native --report /workspace/scratch/e3cacb90cc81/a26-profile-compiler/compiler-tests.json -v` | 19/19 methods, zero skips, 3.672 seconds |
| `python3 tests/test_rotary_profile.py` | Existing validator regressions: 33/33 methods, 1.603 seconds |

The native mode performed six actual compile/link/run jobs, including a
two-translation-unit linkage check, without linking the core archive or using
the shared build. All jobs used C++20 and `-Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`. Four independent native observers read every
public physical member and its `std::bit_cast<uint64_t>` representation directly
from the resulting `Profile`. Expected values come directly from original JSON
quantity locations through an independently written source-to-member mapping;
the tests do not reuse the compiler's projection/formatting helpers.

Those four cases cover the actual nominal file; independently varied source
quantities, reversed direction/commands, negative zero and the smallest positive
subnormal; admitted numerical endpoints and integer authoring; and valid hostile
prose containing quote/comment/include syntax and Unicode. All 128 physical
field comparisons and 16 identity comparisons passed. Separate native tests
round-trip five escaped UTF-8 payloads, including embedded NUL and digit-adjacent
escapes, and verify repeated inclusion, inline-identity linkage and independent
factory return values.

Portable tests additionally exercise duplicate keys, nonfinite spellings and
overflow, booleans, malformed/oversized UTF-8 JSON, schema/contract/unit/range
errors, malicious identifiers, array/command admission, exact raw-source hashing,
deterministic bytes under distinct paths and Python hash seeds, existing output
preservation, input aliases/hardlinks, absent/nonregular output paths, and
injected `fsync` and `os.replace` failures with temporary-file cleanup.

## Remaining scope

Root still owns build-rule/native-target integration and independent CLI
acceptance after the frozen full waveform run. A26's native audit is a Linux GCC
result; MSVC, AppleClang and MinGW execution were not performed here. The
generated profile is an unmeasured research projection. Successful compilation
and field preservation do not close full R4 waveform parity, R5 audible policy,
R6 integration/deadlines or physical M7 fidelity.

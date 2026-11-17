# Reconciled main: exact-source VST3 review

A54/60, wave 9, same accepted worker. **All four required VST3 jobs succeeded
on their original attempt 1 at source
`523c1979334b0fbb624ce120128a0b8ada078383`.** This review concerns
[run 44043394002](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394002),
the four actual runner executions and their complete original decoded logs.
It adds no worker credit. The [summary](summary.json),
[terminal metadata](terminal-metadata.json), [source API](source-api.json),
[input comparison](input-comparison.json) and
[complete log manifest](complete-log-archives.json) retain the exact evidence.

## Source and actual executions

The GitHub commit API and fetched Git object agree on tree
`893441fe87859b9dbad81a5d81a453f7c96030f8` and parents
`8189a49eacab5d4e6ce6c178862e83b03bdec437` and
`54859886268ce83c36f359c43327f7c72a77ae82`. The run/job head identities,
actual checkout output and completed provenance assertions all identify 523.
Every job has an assigned runner, build, native acceptance, inventory/archive
and both upload steps completed successfully. Platform-inapplicable configure
steps are explicitly skipped; none of the native CTests is skipped.

| Platform | Actual job and full receipt | Native CTests | CTest seconds | Actual module validator |
| --- | --- | ---: | ---: | ---: |
| Linux GCC x86-64 | [133903128269](job-133903128269.json) | 8/8 | 6.68 | 47 passed / 0 failed |
| macOS ARM64 | [133903128533](job-133903128533.json) | 7/7 | 5.10 | 47 passed / 0 failed |
| Windows MSVC x64 | [133903128675](job-133903128675.json) | 7/7 | 7.58 | 47 passed / 0 failed |
| macOS Intel x86-64 | [133903128818](job-133903128818.json) | 7/7 | 12.10 | 47 passed / 0 failed |

These are **29 executed CTest observations across configurations**.
The actual compiler identities are GNU 13.3.0, AppleClang
17.0.0.17000013 on both macOS architectures, and MSVC 19.44.35230.0.
The macOS target/compile output, Windows x64 build selection and Linux
x86-64 bundle path establish the recorded native targets. Native loading
succeeds on every actual host. New binary headers were not downloaded for
independent inspection; the unchanged hosted inventory command itself parses
and validates the native module header.

The [previous 548 review](../combined-main-vst3/review.md) remains immutable.
Its independent inspection of eight downloaded archives belongs to that
previous source. No earlier pass substitutes for the 523 executions above.

## VST3 input and dependency identity

The comparison retains the entire former 292-path broad source inventory.
**291 identities are unchanged**; the sole broad change is the unrelated
standalone P1 comparator `tools/compare_performance_plate.py`. All **209
explicitly scoped VST3 build/test/dependency paths** have identical Git modes
and blobs, with current byte lengths and SHA-256 values retained. This includes
the workflow, root and VST3 CMake, all core/adapter/harness sources and headers,
generated-input data and relevant authoring/acquisition/inventory scripts.

The full repository comparison also preserves all five changed non-document
paths: the title/header standalone readers, the two comparator test modules
and the P1 comparator. They are not invoked by the native VST3 target or its
selected CTests. This classification was checked against the unchanged
workflow, CMake dependency and test commands; it does not claim that all
project inputs are unchanged.

The [source workflow](source-workflow.txt) is 8,367 bytes, SHA-256
`6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734`.
The [SDK lock](sdk-lock.json) is 3,796 bytes, SHA-256
`ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965`.
Both match 548 exactly.

Each new job actually acquires and then verifies **Steinberg VST3 SDK 3.8.1,
tag v3.8.1_build_84**, root commit
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`. Acquisition, verify-existing
and configure each report the exact root plus four locked submodule commits,
five primary licenses and the embedded JSON identity. These are three observed
verification records per platform. The actual module validator prints VST 3.8.1
and both unchanged processor/controller class identities.

## Actual validator, ABI and native gates

The validator CTest command loads the built `HammondB3.vst3` bundle.
Its **47/0 result is separate from the SDK validator's build-time selftest**.
Each full original stream still contains **16 “Failed to teardown test!”**
and **15 unsupported 64-bit audio-processing diagnostics**. No warning-free
or cause claim is made.

Every platform executes controller, ABI, behavior, automation and concurrency
gates. The ABI result independently reports nine instances, 701,642 assertions,
47 descriptors, 2,140 conversions, 1,673 accepted callbacks, 88 rejected calls,
3,207 state round trips and six lifecycle sequences. It compares 229,725 frames,
217,972 audible, with maximum audio error zero. The relocated ABI JSON equals
the direct result in every field.

Controller output reports 138,215 checks. The complete actual behavior,
automation and concurrency summaries, including their differing observed
scheduling counters, are retained in each job receipt. They were read from
this run rather than copied from predecessor results.

Linux alone executes the ELF real-time interception gate. Its actual output
retains **193 regions, 12/12 overload calibration and 8,945,157 assertions**,
positive processor/controller create/release interception probes, and zero
new/delete calls in all eight processing rows. Its claim is strictly
**Linux calling-thread global C++ new/delete**. It does not cover all allocators,
other threads, other operating systems or hardware callback deadlines.

## Installation, package and artifact scope

Each unchanged install invocation actually reports **two tests and OK**.
Independent source inspection identifies its exact two methods:
`test_install_move_and_load` and
`test_preflight_rejects_incomplete_bundle_without_mutating_prefix`.
No method filter is supplied. The tests cover explicit component installation,
refused reinstall without mutation, unchanged unrelated files, rename/relocation,
actual loading from an unrelated working directory, incomplete/empty bundle
rejection and invalid installation-directory preflight.

Actual install output lists four payload files on Linux and six on each other
platform, including module metadata, SDK license and source notices.
The license hash matches the SDK lock; the notices match the current source.
The module digests printed by the actual install run are:

| Platform | Reported module SHA-256 |
| --- | --- |
| Linux | `cb83fb90758ad73f27100d59f0e36a72690a4b925da25d2e30d0cb45ffbf8639` |
| macOS ARM64 | `7b710fd3290ea325c383522a62fe8d9a26869ba48c6b61a20f558c68ffd6cfe4` |
| macOS Intel | `176c76437fcefe8843919d2ad14436d14d9aa4cd94a7acf6c9c5759aecaf42e9` |
| Windows x64 | `74dd10f35191c244dfb429d8ebdb2c184b27a3ec225a2597d217966e1e6c062b` |

Linux and both macOS module digests match the previous 548 reports. Windows
differs. That difference is retained without inferring a cause or deterministic
build guarantee.

The unchanged inventory command validates bounded payloads, native-header/path
consistency, the locked license and current project notices. The actual workflow
runs it on built and staged bundles and asserts exact inventory equality before
creating the archive. Both artifact uploads succeed for every platform.
All **eight artifact IDs, sizes and SHA-256 digests** agree between the API and
original upload output.

**No new artifact ZIP or tar body was downloaded in this bounded review.**
New inner archive member bytes, raw provenance/module-info bodies and package
headers are therefore not independently re-inspected here. The claimed evidence
is the new actual install/inventory assertions, complete logs and matching
provider/upload metadata. Signed distribution and all-host compatibility are
not established.

## Retention and acceptance boundary

All four complete original decoded logs are stored as deterministic gzip with
empty filename and mtime zero: **1,108,876 decoded bytes / 131,530 stored bytes**.
Both stored and decoded hashes, byte lengths and round trips were checked.
Windows retains its **1,954 CRLF sequences and eight additional LF endings**
without normalization. The [retention manifest](retention.json) binds this
folder. All 176 pre-existing A54 report files in the preparation inventory
remain byte-identical.

The first read-only extraction attempt mistook the prose “enabled rate” lines
for numeric real-time table rows. Its [analysis receipt](analysis-parser-retention.json)
preserves that error. The corrected extraction requires a numeric second token,
all eight exact row labels, eleven columns and both allocation counters zero.
No original output, source, test, limit or acceptance criterion was changed.

This review admits these four actual 523 VST3 families at the scope stated.
The complete sixteen-job project aggregate belongs to root and the separate
Core/standalone reviews. A54 performed no native build/run, project test,
CI retry, source/index edit or remote mutation. The original accepted note and
all predecessor reports remain frozen. Physical calibration, DAWs/devices,
real displays/native accessibility, hardware deadlines, signing and literal
whole-interface 1:1 remain separate unmet product gates.

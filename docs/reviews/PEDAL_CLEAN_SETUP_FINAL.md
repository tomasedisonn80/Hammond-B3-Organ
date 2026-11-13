# Independent clean setup and relocation audit

## Outcome and exact scope

Assignment 53 independently created a fresh source archive in a path containing
spaces and non-ASCII characters, built the core, five offline tools and optional
native module, installed both components, then executed them from a moved prefix.
The original source and both original build paths were temporarily unavailable
during the runtime checks. The setup runner recorded **28 operational commands: 25
exited zero and three deliberately invalid operations rejected**. Their
summed process wall time was 49.318 seconds; this is not an audio deadline metric.
Two incorrect assertions in the private audit driver were corrected and retained
below. No production, build, test, data or public setup command needed a repair.

This is a Linux/GCC setup and relocation result. It is not a new execution of
root's complete 71-suite ordinary or eight-suite native matrix, an actual DAW
session, a clean operating-system installation, or a cross-platform claim.

The inspected instructions are [the current handoff](../PEDAL_HANDOFF.md),
[build guidance](../BUILD.md), [OfflineTools](../OFFLINE_INSTALL.md),
[the optional native build](../VST3_BUILD.md) and
[native local staging](../VST3_LOCAL_INSTALL.md). The implementation inspected
is the [root CMake file](../../CMakeLists.txt), [presets](../../CMakePresets.json),
[SDK verifier](../../cmake/VerifyVst3Sdk.cmake),
[install module](../../cmake/InstallHammondTools.cmake), and
[native target definitions](../../plugins/vst3/CMakeLists.txt).

## Source and toolchain identity

The independently archived tree is
`5370890e32045a556cb61a88cdb1f04fb5a18f7e`, the frozen wave-8 source. All **534
files** matched their Git blob IDs, byte sizes, SHA-256 values and executable-mode
classification before execution. All 534 source files and the exact file set
were unchanged afterward. The final wave-8 tree
`8af684dfe56f88222c52ff71d85a911ee1192fa1` differs only in six Markdown result
records; the build/runtime inputs audited here are identical.

The source directory was `a53-clean-setup/érable source with spaces`, with
separate `build Release vérifié` and `build native érable` directories. Actual
local tools were GCC 14.2.0, GNU Make 4.4.1, CMake/CTest 3.31.6 and Python
3.12.14. The generator was Unix Makefiles. No dependency was installed or
acquired for this assignment. The existing external SDK was verified read-only
before and after native construction using the repository's pinned helper.

The independent native ABI executable came from root's coherent wave-8 build,
not from a later live header set. All 534 files in that reference source archive
were independently matched to the same Git inventory. The reference executable
and profile hashes remained unchanged across this check:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `test_native_abi` | 324,744 | `de4f307def0afeb410e704983d4f0e31628894fa2e175e5afe7daa2a8db11651` |
| Compiled nominal profile | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## What the build switches actually do

There is **no `HAMMOND_BUILD_TOOLS` option**. The offline targets exist in the
ordinary build; a selected target build can avoid building unused executables.
Passing an unknown CMake cache variable would not prove that tools were disabled.
The meaningful switches inspected here are `BUILD_TESTING`, `HAMMOND_BUILD_VST3`
and the separately documented sanitizer option.

The fresh ordinary configure left `HAMMOND_BUILD_VST3=OFF` by default, explicitly
set `BUILD_TESTING=OFF`, and deliberately pointed `HAMMOND_VST3_SDK_ROOT` at an
absent directory. It succeeded without creating that SDK directory or a generated
SDK build directory. Its 22-entry generated compilation database contains only
source paths within the fresh project archive; it is a target description, not
a claim that all 22 translation units were compiled. The selected build below
compiled the core and five offline executables. Source inspection confirms the
SDK verification and native subdirectory are entered only when VST3 is enabled;
no CMake path invokes dependency acquisition.

CTest discovered **zero tests** with testing disabled, and the ordinary target
help had no test executables, `check`, or `HammondB3`. Building only
`hammond_core` succeeded and generated its reviewed pedal-routing header while
leaving `nominal.b3p` absent, as the build guide states. Building the five
OfflineTools executable targets then generated the exact nominal profile.

Enabling VST3 against the missing SDK rejected with the actual instruction:
`requires an existing external HAMMOND_VST3_SDK_ROOT`. The absent path remained
absent. Enabling it against the locked external SDK configured successfully.
The cache showed GUI, hosting/plugin examples, iOS and automatic plugin links
disabled. No SDK source or build output was placed in the project archive or in
the SDK worktrees.

With `BUILD_TESTING=OFF`, the native module target and the two aggregate/wrapper
targets still exist, but registered native test executables do not. `check_vst3`
uses CTest with `--no-tests=error`; its corresponding exact filtered CTest command
was executed directly and rejected the empty suite with exit 8. This verifies
that an empty native test set cannot be reported as a pass. The wrapper itself
was inspected, not invoked, and no complete SDK validator pass is claimed for
this module-only build.

## Executed construction and staging

The selected core build succeeded in 6.679 seconds; the subsequent five-tool
build succeeded in 10.542 seconds. A separate native module-only build succeeded
in 27.375 seconds. The native module contains 434,168 bytes and has SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`, matching the
previously qualified local module despite the different source/build paths.
This is one observed toolchain result, not a general reproducible-build claim.

Actual `cmake --install` staged **exactly 23 OfflineTools files** into a fresh
Unicode prefix. All five installed executables and both Python scripts matched
their built/source bytes. The profile and twelve scores plus three catalogs were
present at the declared relative paths. NativeVST3 then added the complete
four-file Linux bundle under `lib/vst3/HammondB3.vst3`. Every native payload hash
and permission mode matched its built counterpart; no staged file was a symlink.
A second native install into that existing bundle rejected with exit 1 and the
existing-destination diagnostic. Subsequent relocated execution and hash checks
confirmed the retained bundle remained intact.

The build/install command forms actually exercised were:

```sh
cmake -S "$hammond_source" -B "$hammond_offline" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DHAMMOND_VST3_SDK_ROOT="$hammond_missing_sdk"
cmake --build "$hammond_offline" --config Release --parallel 2 --target hammond_core
cmake --build "$hammond_offline" --config Release --parallel 2 \
  --target hammond_render hammond_model_info hammond_parameter_info \
  hammond_console_trace hammond_pedal_trace
python3 "$hammond_source/tools/acquire_vst3_sdk.py" --verify-existing "$hammond_sdk"
cmake -S "$hammond_source" -B "$hammond_native" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT="$hammond_sdk" -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$hammond_native" --config Release --parallel 2 --target HammondB3
cmake --install "$hammond_offline" --config Release --component OfflineTools \
  --prefix "$hammond_prefix"
cmake --install "$hammond_native" --config Release --component NativeVST3 \
  --prefix "$hammond_prefix"
```

These variable names stand for the recorded absolute paths; the assignment note
and retained JSON contain the exact executed argument arrays. Tests were disabled
here specifically to audit option behavior and selected-target packaging. Use
`BUILD_TESTING=ON` and the documented aggregates for normal development gates.

## Relocation with the original paths unavailable

After moving the complete prefix to `stage déplacé with spaces`, the private
source and both build directories were renamed temporarily. Installed processes
ran from a separate `unrelated output été` directory with all `HAMMOND_*`
environment variables removed. Their command lines contained only moved-prefix
inputs and new output paths. The audit driver retained separate comparison
access to the renamed source; no installed process received that path. A `finally`
block restored all three directories after execution.

| Actual relocated operation | Observed result |
| --- | --- |
| Three-second pedal phrase | 144,000 stereo PCM16 frames at 48 kHz; zero reported clipping; complete WAV exactly matches the retained demo |
| Model exporter | Successful actual compiled-model JSON from the installed executable |
| Parameter exporter | 45 mappings, diagnostic schema 2, exact SDK-free verification scope |
| Console partial trace and standalone plot | Actual CSV and valid SVG; SVG contains the exact CSV SHA-256 |
| Pedal routing trace and standalone plot | Actual CSV and valid SVG; SVG contains the exact CSV SHA-256 |
| Actual moved native module through the independent ABI host | Nine instances; 229,725 compared frames, 217,972 audible; maximum audio error zero; 691,878 assertions |

The relocated phrase's complete WAV is 576,044 bytes, SHA-256
`a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1`.
Its float report retains peak `0.08429475128650665` and RMS
`0.022980303816301697`; these metrics describe the nominal synthetic output.

The moved native module test also checked 45 descriptors, 2,002 conversions,
73 accepted callbacks, 86 rejected calls, seven state round trips and six
lifecycle sequences. Its float checksum was `af029009868faa04`. The host used
its separately identified profile for the plain-Engine reference; the plugin's
profile remains embedded in its freshly built module.

## Retained corrections and limits

The private probe initially guessed a missing-SDK error phrase and separately
assumed the native test wrapper target would disappear with testing disabled.
Both assertions stopped the driver after the underlying command had returned
its correct result. The observed diagnostic and actual target definition were
then read, the two assertions corrected, and execution resumed after those
points. Earlier successful build commands were not rerun, and no project code
or tests were changed to satisfy the probe. All three driver versions and the
original logs remain in the local evidence directory.

The final paragraph of [VST3_BUILD.md](../VST3_BUILD.md) still presents several
now-executed native gates as next steps within its assignment-33 historical
section. Root was notified for the coordinated handoff audit. Preserve that
historical result and add current gate links; it does not require a runtime fix.

This finite Linux setup check establishes exercised source/configuration
coherence, selected-target builds, no implicit SDK requirement on the ordinary
path, explicit missing-SDK rejection, and successful moved-prefix operation.
It does not prove Windows/macOS runtime behavior, arbitrary filesystem support,
compiler-runtime packaging, signing, licensing clearance, device scheduling,
subjective quality or measured instrument fidelity. No additional full matrix
was run. Current publication/platform results belong in [STATUS.md](../STATUS.md)
and the [wave-8 integration record](PEDAL_WAVE8_INTEGRATION.md).

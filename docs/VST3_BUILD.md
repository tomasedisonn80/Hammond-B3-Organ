# Optional native VST3 build

The repository can build a headless `HammondB3.vst3` instrument from the existing
core and the separately acquired, pinned Steinberg VST 3 SDK. The default build
remains SDK-free. Configuration never clones, fetches or updates dependencies.
This is an early nominal instrument and native ABI development path; physical
calibration, custom UI, audio-device operation and signed distribution remain
separate milestones. See the [native contract](VST3_SPIKE_CONTRACT.md).

## Build boundaries

| Setting or input | Contract |
| --- | --- |
| `HAMMOND_BUILD_VST3` | Defaults to `OFF`. Only `ON` enters the native build directory. |
| `HAMMOND_VST3_SDK_ROOT` | Explicit path to a separately acquired SDK checkout; no automatic fallback or fetch. |
| CMake | Ordinary project floor stays 3.21; this optional SDK requires 3.25 or newer. |
| Dependency identity | [Lock file](../data/dependencies/vst3-sdk-lock.json): root commit, four required module commits, five primary licenses and the embedded module-info parser hash. |
| SDK source cleanliness | Root and all four required worktrees must have no tracked modification, staged change, untracked file or ignored file. Build outside the checkout. Empty directories are harmless. |
| SDK targets | GUI, plugin examples, hosting applications, iOS, AAX and automatic system-plugin links are disabled. The required validator and module-info tooling are built. |
| Project target | `HammondB3`, using `smtg_add_vst3plugin`, `sdk`, and the existing position-independent `hammond_core`. No DSP copy is maintained in the wrapper. |
| Profile | The exact compiled `nominal.b3p` bytes become a private generated `EmbeddedProfile.h`; decoding occurs before processing. |
| Qualification | `hammond_vst3_validator` and the native tests are CTest entries; `check_vst3` builds their inputs before running them. |

The SDK is not vendored, and its headers are not part of the core's public
dependency surface. Native wrapper and project harness sources retain strict
project warnings. Unmodified SDK target and platform-loader sources use the
SDK build policy; their include directory is marked `SYSTEM` for project
consumers.

## Acquire once, explicitly

From this repository, select a **new path outside the source tree**, whose
parent directory already exists:

```sh
python3 tools/acquire_vst3_sdk.py --destination /absolute/path/to/vst3sdk
```

The helper reads the reviewed lock, clones the named official tag and checks
its exact root commit before fetching only `base`, `cmake`, `pluginterfaces`
and `public.sdk`. It uses `core.autocrlf=false` and `core.eol=lf` for the new root
and required module repositories. These settings preserve committed bytes,
including the raw license/parser identities, across Windows configurations.
They do not normalize an already committed CRLF file into another version.

An existing destination, including a broken symlink, rejects before Git is
invoked. The helper never resets an existing checkout, changes its branch, or
cleans someone else's files. A failed new acquisition leaves its partial
directory available for inspection. Use a different new destination after
resolving the cause, or inspect the retained partial result explicitly.

An existing SDK can be checked without any network operation:

```sh
python3 tools/acquire_vst3_sdk.py \
  --verify-existing /absolute/path/to/vst3sdk
```

Verification requires each required module to be its own checkout, checks its
HEAD and the immutable parent gitlink independently, rejects tracked changes,
and checks the selected raw-file sizes and SHA-256 hashes. It also rejects all
untracked and ignored files. This last rule matters because the SDK discovers
utility subdirectories: a new ignored `CMakeLists.txt` could otherwise change
the build despite unchanged commits and a clean ordinary `git status`.
The checker reports the problem and preserves the source; it does not delete
or repair it. Keep build output and scratch notes outside the SDK worktrees.

The helper's `--lock` argument supports an explicitly supplied reviewed lock;
the CMake integration always passes this repository's own checked-in lock.
Changing a dependency version still requires the normal source/rights review,
lock update and fresh native qualification.

## Configure, build and test

Typical single-configuration build:

```sh
cmake -S . -B build-vst3 -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-vst3 --target HammondB3 --parallel 4
cmake --build build-vst3 --target check_vst3 --parallel 4
```

For a multi-configuration generator such as Visual Studio, select Release when
building and testing:

```sh
cmake -S . -B build-vst3 -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build build-vst3 --config Release --target check_vst3 --parallel 4
```

Testing must remain enabled for `check_vst3`. The ordinary project-wide
`check` target also includes native targets and tests when VST3 is enabled.
For CI or a single verbose run with JUnit output, build the maintained input
aggregate first. It includes every registered native test, the bundle and the
validator, but runs no test. Direct CTest invocation does not first build missing
executables:

```sh
cmake --build build-vst3 --config Release --target hammond_vst3_test_inputs --parallel 4
ctest --test-dir build-vst3 -C Release --output-on-failure \
  -R '^(hammond_vst3_validator|test_native_)'
```

The exact generated bundle path is written into
`build-vst3/hammond-vst3-path-Release.txt`. For the recorded Linux build it is
`build-vst3/VST3/Release/HammondB3.vst3`, containing the native module under
`Contents/x86_64-linux/`. The SDK chooses the appropriate desktop platform
bundle layout. Build/test commands do not install or link the result into a
system or user plugin directory. Native installation remains a separately
reviewed, explicit operation.

The SDK's own validator selftest still runs when that tool is built. Its
plugin post-link validation hook is replaced locally with the explicit
`hammond_vst3_validator` CTest entry, so a failing validation can be inspected
by the independent ABI harness without losing the linked module. This does not
turn a failure into success: `check_vst3` and `check` fail on a failing validator
CTest result. A module build alone is not a validation result.

## Generated inputs and payload

[embed_profile.py](../tools/embed_profile.py) reads at most 128 KiB of compiled
ASCII/LF profile text and emits a deterministic numeric character array plus
`hammond::vst3::kEmbeddedProfileText`. It preserves every input byte and records
the input SHA-256. Numeric initializers avoid dependence on a compiler's source
code page or maximum individual string-literal length. The consumer still uses
the existing strict runtime loader; embedding is transport, not a second
semantic profile validator. Invalid inputs preserve an existing output, writes
use an atomic replacement, and an identical result is not rewritten.

`nominal.b3p` remains generated by the existing profile compiler. The recorded
compiled profile contains 4,545 bytes with SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The generated C++ header is private build output, not a new authoring profile,
checked-in source of truth, sample recording or audio-thread parser.

The local bundle carries `VST3_SDK_LICENSE.txt` and the repository's
`THIRD_PARTY_NOTICES.md` under `Contents/Resources`, alongside the SDK-generated
`moduleinfo.json`. The SDK license filename identifies the component whose
terms it contains; it does not assign a license to the entire project. The SDK
module-info tool retains its own output grammar and class metadata. No complete
SDK checkout, validator executable, atlas, profile JSON or compiled-profile
file is copied into this bundle. The profile text is linked into the module.
Review the actual platform payload and runtime dependencies before redistribution.
The [rights inventory](DEPENDENCIES_AND_RIGHTS.md) retains the unresolved project
and research-asset questions separately.

## Recorded local qualification and next gate

Assignment 33 built a coherent source archive based on tree
`06786b70f1cffcc6371600fd6e14306f16e8c985`, overlaid with frozen processor,
controller and build inputs. Linux/GCC 14.2.0/CMake 3.31.6 built the actual
`HammondB3.vst3` module and module-info resources. The actual module validator
reported **47 passed tests, zero failed tests, exit 0**; its separate SDK
selftest reported **51 passed, zero failed**. These are distinct invocations.

The actual module validator also printed **16 nonfatal teardown messages**.
The pinned repeated-state test requires an already inactive `setActive(false)`
to reject, while `ProcessTest::teardown` unconditionally requires that same
call to succeed, including skipped float64 and already-inactive state cases.
The unchanged SDK's summary/exit status does not count those messages as failed
tests. They are retained in the [assignment evidence](development/2026-11-13-pedals/33-native-build.md);
the project does not claim a warning-free validator log, enable unsupported
float64 processing, or patch the SDK to hide this conflict. Independent balanced
module lifecycle checks are assigned to the actual ABI harness.

The same validator log contains nine `ERROR`-labelled setup rejections for
unsupported sample rates. Its format test prints those diagnostics without
counting them as failed tests. Only 44,100, 48,000 and 96,000 Hz are supported
and processed successfully by this prototype; rates such as 22,050, 32,000,
88,200, 192,000 and 384,000 Hz remain outside the declared core contract. The
retained full log and independent actual-module rate checks qualify the scope
more precisely than the validator summary alone.

The relevant pinned SDK implementations are
[repeated-state admission](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/state/repeatidenticalstatetransition.cpp),
[process teardown](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/processing/process.cpp)
and [valid-state transitions](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/state/validstatetransition.cpp).

The SDK-free tool suite separately exercises real local Git checkouts, staged
and unstaged tampering, parent gitlink mismatch, missing modules, raw identity
hashes, ignored/untracked discovered CMake inputs, no-network configuration,
existing-destination preservation and exact profile-byte transport. Its tests
neither download an SDK nor substitute for an actual native build.

The final focused coherent gate passed **3/3 CTest suites in 3.99 seconds**:
the 14 SDK-free Python methods, actual-module SDK validator, and the maintained
native controller/state-stream executable. The latter reported 41,795 checks,
3,720 exact threshold cases across four rounding modes, 387 native string
round trips and 306 rejected stream/migration cases. No Windows/macOS or
actual DAW execution is inferred from this Linux result.

The next gates are the independent loaded-module ABI/behavior harnesses,
actual native callback allocation evidence, hosted Windows/macOS builds,
concurrent native state calls and explicit package/relocation review. DAW
project save/reopen, host scheduling, device underruns/deadlines, custom UI,
signing and physical fidelity require their own observed evidence.

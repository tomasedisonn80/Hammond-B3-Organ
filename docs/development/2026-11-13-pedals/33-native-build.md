# Assignment 33 — optional pinned native build

**Owner:** `/root/w06_a33_native_build`

**Wave:** 6

**Session:** `2026-11-13-pedals`

## Scope and ownership

Owned only the optional hook in root `CMakeLists.txt`,
`plugins/vst3/CMakeLists.txt`, `cmake/VerifyVst3Sdk.cmake`,
`tools/acquire_vst3_sdk.py`, `tools/embed_profile.py`,
`tests/test_vst3_build_tools.py`, [VST3_BUILD.md](../../VST3_BUILD.md) and this
note. The existing fifth-wave trace/Threads CMake content was preserved.
No shared status document, SDK source, profile, parameter registry or DSP was
edited. No commits, pushes or child-agent dispatches were performed. Root owns
integration and publication under the standing user authorization.

Read the standing instructions, current status/next work, full native contract,
SDK lock, rights inventory and selected notices. Inspected actual pinned SDK
CMake/plugin-loader/validator sources before choosing the build hooks. The SDK
checkout and all new build output remain outside the source repository.

## Implemented

`HAMMOND_BUILD_VST3` defaults off. When explicitly enabled, CMake requires 3.25,
checks the selected external SDK before entering its CMake, enables PIC for the
existing core and builds `HammondB3` with the official SDK helper. Ordinary
configuration retains its 3.21 floor and no SDK/network operation.

Verification checks the root and four required module HEADs, each required path
being its own checkout, immutable parent gitlinks, tracked/staged cleanliness,
all untracked/ignored inputs, five raw primary license identities and the
embedded `json.h` identity. Root identified that the SDK's utility directory
discovery can execute untracked CMake files, so the initially permissive policy
was tightened to require all build/scratch files outside SDK checkouts. The
strengthened test includes a new utility `CMakeLists.txt` hidden with Git's local
exclude file: ordinary status and HEAD remain unchanged, but admission rejects.
No check deletes or resets the checkout.

Explicit acquisition accepts only a new external destination. Root/tag pin is
checked before fetching the four selected modules; all new repositories retain
byte-preserving `core.autocrlf=false`/`core.eol=lf` settings. Existing paths reject
before Git execution, and failed acquisitions retain their partial directory.
Configure invokes only read-only verification, never acquisition.

The bounded profile generator emits exact compiled bytes as numeric character
initializers and the agreed private `kEmbeddedProfileText` string view. It
rejects invalid envelopes/bytes/bounds before output changes, uses atomic
replacement, and avoids rewriting an identical result. Existing-destination
comparison is also bounded. Runtime semantic parsing remains off audio in the
processor, using the existing profile loader.

The native bundle includes `VST3_SDK_LICENSE.txt` and the existing component
notices, with generated module-info data. The SDK license filename does not
imply a project-wide license. SDK sample applications, GUI, automatic plugin
links and wrappers are disabled. SDK validator runs in a required CTest entry;
its post-link invocation is locally suppressed so an independent ABI harness
can inspect a module even when validation fails. `check_vst3` and project-wide
`check` propagate validator test failure. The SDK tool's own selftest remains.

Optional target hooks cover assignment 32's direct controller/stream test and
assignments 34/35's actual loaded-module harness/behavior tests. Upstream
platform-loader sources compile in a separate SDK target; project test sources
retain strict warnings. Each loaded-module executable receives the generated
bundle path and compiled profile path. The ABI/behavior suites are owned and
qualified separately by those workers.

## Coherent source and exact commands

The initial isolated source uses root's frozen fifth-wave tree
`06786b70f1cffcc6371600fd6e14306f16e8c985`, copied before this assignment changed
the working CMake. Frozen assignments 31/32 and this assignment's owned build
inputs were overlaid explicitly into `a33-native-source`; no live-header/old-core
mixture was linked. Assignment 32's final formatting guard and ASCII-escaped
test fixtures were included before the final focused gate.

Local tools: Linux x86-64, GCC 14.2.0, CMake 3.31.6, Python 3.12.14. The separately
acquired SDK matches root `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` and all four
locked module commits. Configure reports missing optional JACK and the SDK's
failed stdatomic feature probe/fallback; both are retained environment results,
not suppressed prerequisites or plugin failures.

Commands actually executed (paths abbreviated to the shared scratch parent):

```sh
python3 tools/acquire_vst3_sdk.py --verify-existing ../vst3sdk
cmake -S ../a33-native-source -B ../a33-native-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT=/absolute/path/to/vst3sdk
cmake --build ../a33-native-build \
  --target validator moduleinfotool hammond_core -j 4
cmake --build ../a33-native-build \
  --target HammondB3 test_native_controller -j 4
ctest --test-dir ../a33-native-build --output-on-failure \
  -R '^(hammond_vst3_validator|test_native_controller|python_test_vst3_build_tools)$' \
  --output-log ../a33-final-gate.log --output-junit ../a33-final-gate.xml
```

Actual executable prefixes were
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/`; the actual SDK root was
`/workspace/scratch/f364bc93d920/vst3sdk`. The local overlay identity record is
`/workspace/scratch/f364bc93d920/a33-native-overlay.json`. Its final source
hash table is also reproduced below so the evidence does not depend on scratch
retention. All code/test inputs matched the owned working files at freeze.

## Observed results and retained failures

| Gate | Actual result |
| --- | --- |
| Clean pinned SDK verification | Passed, five checkouts/five licenses plus embedded parser, no network |
| Actual native build | Passed with strict project warnings; module-info generated from the loaded factory |
| SDK validator selftest | 51 passed, zero failed |
| Actual Hammond module validator | 47 passed, zero failed, exit 0; 16 nonfatal teardown messages retained below |
| SDK-free build-tool suite | 14 Python methods passed; default OFF configuration did not execute the supplied unverified SDK sentinel |
| Native controller/state-stream suite | 41,795 checks, 3,720 thresholds/four rounding modes, 387 string round trips and 306 rejected cases passed |
| Final combined selected CTest | **3/3 passed**, zero failures, **3.99 seconds** |

After that gate, assignment 34 froze its harness header/source. Copied those two
files into the same isolated source and built `hammond_vst3_test_host`
successfully, including the separate SDK Linux module-loader target. Header
SHA-256 is `0067515c5259288f1f711e4ce8c0921721682209863ca62ccbee4f50dbb2752a`;
source SHA-256 is
`899d504d842e2e1b83d7f629e0bb4335b0c4f4191d7568df90980f27c09828b7`.
This checks those CMake compilation hooks; assignment 34's actual ABI test and
assignment 35's behavior test were not yet copied or executed by this worker.
The plugin and prior three-test inputs remain unchanged.

The first build-tool run passed 13/14 methods. Its CMake-error assertion assumed
an unwrapped phrase while CMake wrapped a line; the test now normalizes diagnostic
whitespace without changing its required rejection reason. After the untracked
SDK-input hardening, another 13/14 run exposed `git ls-files --directory`
reporting an empty formerly populated directory. Added `--no-empty-directory`:
the contract excludes untracked files, while empty directories contain no
discoverable CMake input. The same test still rejects both ignored and
nonignored CMake files. The final 14-method run passed under the full CTest gate.
No production DSP defect or SDK source modification was needed.

The actual module validator's 16 teardown messages comprise two valid-state
transition cases and fourteen float64 processing cases. Its repeated-state test
requires repeated inactive deactivation to reject; its process teardown instead
unconditionally demands successful deactivation. Root and this assignment
inspected the pinned implementations linked from [VST3_BUILD.md](../../VST3_BUILD.md).
The SDK reports 47/0 despite these messages. This evidence preserves both facts,
does not describe the log as warning-free and does not change correct
float32-only/lifecycle behavior to hide a conflicting harness expectation.
Assignment 34 independently owns balanced native instance cleanup checks.

The first complete validator log was recorded at
`a33-first-native-validator-full.log`, SHA-256
`12e571215d64fdb1684a40de3414bc13f70463cb2304cc447dd4dad10dcc42aa`.
The final three-test full log is `a33-final-gate-full.log`, 20,857 bytes,
SHA-256 `6e76e398206abf3e142b05539b2665565ccf20f75a8254b8c764ab45d0d58ee6`.
These temporary logs support this retained report; hosted publication must
retain its own exact-commit artifacts and observed results.

## Source and bundle identities

| Owned code/test input | SHA-256 |
| --- | --- |
| Root `CMakeLists.txt` including preserved W5 hooks | `52a839335f38ea6ab4fe4c0737f34265499b08046a868a1b32ffd9358b3b3dd7` |
| `plugins/vst3/CMakeLists.txt` | `443bdc8734d462418247dfb22cc680836ee13a157596ce887379ef6038e45e29` |
| `cmake/VerifyVst3Sdk.cmake` | `4feeb4cfabf1560cfd3487859b88d40974b47801753aeccf848517717443e6eb` |
| `tools/acquire_vst3_sdk.py` | `7e25134bde98d5a1886bd3724331495d1a07856526f87da606ae250b57f5bf86` |
| `tools/embed_profile.py` | `f190b1bd45c1f1c8497293d9154d19982429cc07b3b1f45613e9e62c97556da9` |
| `tests/test_vst3_build_tools.py` | `00e7025b69ace75d7b15457a032bd6eff5f39622ff3c3bee0f22bd4bfc287ab7` |

The native sources are the frozen assignment-31 processor pair
(`e85cdc6f...a54e72`, `a61e5677...6f20b`) and assignment-32 six-file set, with
Controller source `24b71a4a49d6234def8f9336e22de927577bf75bb859769b9af4a7ff840d41d6`.
Their full hashes are retained in their notes. The final direct-controller test
is `fefb8c2e6bbd2fe0096a4856fb2c466e4ae23198da5830eb4dc043a31527c31a`.

Actual bundle:
`/workspace/scratch/f364bc93d920/a33-native-build/VST3/Release/HammondB3.vst3`.

| Bundle file | Bytes | SHA-256 |
| --- | ---: | --- |
| `Contents/x86_64-linux/HammondB3.so` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| `Contents/Resources/moduleinfo.json` | 1,090 | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| `Contents/Resources/VST3_SDK_LICENSE.txt` | 1,094 | `e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e` |
| `Contents/Resources/THIRD_PARTY_NOTICES.md` | 7,887 | `a3aa1900ec8b584bfe0879d0d8c7c1af3148dc23729d01a62e26ed428b61c2f6` |

The compiled profile remains 4,545 bytes,
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
No native binary or SDK source is committed by this assignment. This Linux
payload does not describe a later Windows/macOS bundle or compiler-runtime set.

## Handoff

Root can integrate the frozen build files, preserve the staged fifth-wave
checkpoint, and publish with the required full-code/remote checks. Assignments
34/35 own actual loaded-module lifecycle, audio/state/input and automation
qualification; assignment 36 should use the explicit acquisition helper in
hosted desktop jobs and retain bundle, notices, module-info and full validation
logs. No Windows/macOS plugin build, actual DAW, device deadline, signing,
native UI or physical fidelity is established by this local gate.

After these inputs freeze, rebuild the complete wrapper/core/harness from one
source snapshot. Never relabel the first bundle's result as a changed module's
qualification. Native acquisition/install policy and any later SDK change need
their own maintained checks and actual payload inventory.

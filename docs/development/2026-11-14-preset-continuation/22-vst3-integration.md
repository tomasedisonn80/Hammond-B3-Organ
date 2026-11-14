# A22 — Native VST3 selector integration

Actual worker `/root/w04_a22_vst3_integration`, logical wave 4, 2026-11-14.
Session base: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
Checkout HEAD at the coherent copy: `35554c068492fe2b20c1f8a602d8354ae762dc42`.
The implementation below was uncommitted over that HEAD; HEAD alone does not
identify the tested source. Root owns publication and shared documents.

## Owned work

Read the standing agent instructions, project plan and current status context,
`PRESET_SELECTION_CONTRACT.md`, `PRESET_STATE_PARAMETER_CONTRACT.md`,
`PRESET_ADAPTER_AUDIT.md`, and A16/A17 handoffs. Reviewed the relevant native
controller, processor, StateStream, harness and tests against the available
A13–A17 core/parameter/state/publication dependencies.

Changed `plugins/vst3/Controller.cpp`/`.h`; the native ABI, controller, behavior,
automation, concurrency and realtime tests; added test-only
`plugins/vst3/tests/NativePresetOracle.h`; wrote
`docs/reviews/PRESET_VST3_INTEGRATION.md` and this record. No Processor, StateStream,
PluginIds, factory, root/plugin CMake, shared status, Git ref or another worker's
path was edited. No commit, push or child agent was performed.

The production change adds checked effective selection to `snapshot_plain` and
updates controller comments for 47 descriptors. It keeps the raw host-value
cache unchanged. The [integration review](../../reviews/PRESET_VST3_INTEGRATION.md)
describes the complete native behavior and evidence boundaries.

## Coherent source and toolchain

Copied all **1,240** present tracked/untracked, nonignored source files into
`/tmp/hammond-preset-a22/source` before configuring a fresh build. Copied bytes
were hashed; **155** files under the native/core/configuration/tool/data input
roots were checked against the live source immediately after copying. No build
input changed during this copy. The final test-only fixture correction was
copied into this frozen tree before its target rebuilt.

The copied root CMake includes the separately owned integration environment; A22
made no root CMake edit. The final identity check found all core, native, CMake
and data inputs still equal to the live source. Three independently advancing
CLI files differed: `tools/render.cpp`, `tools/render_fixture.py` and
`tools/verify_render.py`. This native result does not qualify their later live
changes. The source copy prevents those concurrent advances from changing the
tested native translation units or headers.

Toolchain: CMake **4.4.4** at
`/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake`, GNU C/C++
**14.2.0**, Python **3.12.14**, Unix Makefiles, Linux `x86_64-linux`, Release.
Fresh build: `/tmp/hammond-preset-a22/build-make`. The SDK lock check completed
without network access, with embedded JSON and all five primary licenses
verified:

| SDK checkout | Exact commit |
|---|---|
| `/workspace/scratch/1742da7072be/vst3sdk` | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| `base` | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| `cmake` | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| `pluginterfaces` | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| `public.sdk` | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

## Commands and results

Commands were launched from
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`. `cmake` and `ctest` below denote
the exact supplied toolchain paths above. The initial failed configure used
`-G Ninja` and `/tmp/hammond-preset-a22/build`; the available Make generator used
a separate fresh directory:

```sh
cmake -S /tmp/hammond-preset-a22/source \
  -B /tmp/hammond-preset-a22/build-make -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=ON \
  -DHAMMOND_VST3_SDK_ROOT=/workspace/scratch/1742da7072be/vst3sdk \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build /tmp/hammond-preset-a22/build-make \
  --target hammond_vst3_test_inputs -j4
ctest --test-dir /tmp/hammond-preset-a22/build-make \
  -N -R '^(test_native_|hammond_vst3_)' --no-tests=error
ctest --test-dir /tmp/hammond-preset-a22/build-make -C Release \
  --output-on-failure --no-tests=error \
  -R '^(test_native_|hammond_vst3_)' -j4 \
  --output-junit /tmp/hammond-preset-a22/native-first.xml
```

The build-only aggregate built the real module, module metadata utility,
validator and all six native C++ executables. Its SDK selftest passed **51/51**.
Discovery found exactly **eight** native CTest suites. The first selected gate
passed **7/8** in **3.03 s**, with the controller expectation failure described
below. After copying the single corrected test source into the frozen tree,
the same aggregate rebuilt only `test_native_controller`; all other targets
were already current. The final executed command was:

```sh
ctest --test-dir /tmp/hammond-preset-a22/build-make -C Release \
  --verbose --output-on-failure --no-tests=error \
  -R '^(test_native_|hammond_vst3_)' -j4 \
  --output-junit /tmp/hammond-preset-a22/native-final.xml
```

**8/8 passed**, no skipped tests, **2.52 s** total wall time. The later integrator
guidance that a controller-only recheck was sufficient arrived after this final
filter had already been launched. No further broad repeat was performed.

| CTest | Final reported duration |
|---|---:|
| `test_native_controller` | 0.03 s |
| `test_native_abi` | 1.41 s |
| `test_native_behavior` | 2.12 s |
| `test_native_automation` | 0.91 s |
| `test_native_concurrency` | 0.34 s |
| `test_native_realtime` | 1.07 s |
| `hammond_vst3_validator` | 1.92 s |
| `test_native_install` | 1.60 s |

Tests ran concurrently; their individual durations do not sum to wall time.
The SDK plugin validator's **47 internal checks** and the plugin's **47 exported
parameters** are distinct counts. The install suite ran two Python methods and
repeated the actual ABI suite against the relocated four-file bundle.

## Actual counters

Controller: **138,215 checks**, **3,984 threshold cases**, **411 string round
trips**, **469 rejected streams**, **1,600 selector restores**. Threshold cases
include all old/new discrete boundaries and both adjacent binary64 values in
all four standard rounding modes. The new selectors also check all twelve
canonical values in those modes.

ABI: **nine instances**, **701,642 assertions**, **47 descriptors**, **2,140
conversions**, **1,673 accepted callbacks**, **88 rejected calls**, **3,207 state
round trips**, **six lifecycle sequences**, **229,725 compared frames**,
**217,972 audible frames**, maximum audio error **0**, float hash
`af029009868faa04`. The relocated ABI run reported the same values.

Behavior: **29,455,970 checks**, **1,066 accepted callbacks**, **75 rejected
callbacks**, **123 zero callbacks**, **234,185 direct reference frames**,
**618,550 exact channel samples**, **64,480 paired setup channel samples**,
**85,436 future audio samples**, **576,696 audible samples**, **560 state reads**,
**71 rejected state loads**, **90 legacy threshold cases**, **62 rollback cases**,
**nine partition cases**, **three rate changes**, **nine isolated-division
cases**. Division peaks were `0.015,0.015,0.0096094`, overall peak `0.0906279`,
checksum `77364d031ab2c10f`.

Automation: **six legacy45 scores**, **three legacy restore cases**, **six raw
anchor gap cases**, **72 new selector commands**, **198 new selector threshold
cases**, **three alias cases**, **three fixed restore/carry cases**, **nine new
selector partition cases**, **879 callbacks**, **309 zero callbacks**,
**954 state reads**, **102,156 direct reference frames**, **204,312 exact channel
samples**, **24,021 partition mono comparisons**, **46,116 future channel
samples**, **181,504 nonzero channel samples**. The original long curves still
require **12,288 expression events across three long callbacks**. The **18**
isolated-division windows reported minimum RMS values
`0.00402141,0.00655038,0.00172213`; reconnect difference was `0.0238609`, maximum
error **0**, peak `0.198746`, checksum `c7f3f16ed488cb03`.

Concurrency: stable scenarios are **three rates**, **24 controlled rounds**,
**3,072 stress accepted loads**, **3,072 publication-only saves**, **96
reader-pause callbacks**, with successful exception-unwind stop/join cleanup.
This run observed **1,453 callbacks**, **24 rejected callbacks**, **287 zero
callbacks**, **66,651 compared/audible frames**, **6,168 future frames**,
**3,174 accepted loads**, **10,605 full-queue rejections**, **462 malformed
loads**, **17,218 successful saves**, **51 busy saves**, **14,069 pending saves**,
**3,101 published saves**, maximum audio error **0**. Scheduling-dependent
counts are observations, not a deterministic expected count.

Realtime: **193** measured native call regions, **12/12** overload calibration,
**423,762** exact channel comparisons, **420,414** audible samples,
**212,265** direct reference frames, **204** state reads, **30** rollback cases,
**18,114** future channel comparisons, **four** moving-contact checks, **two**
owner-capacity checks, **8,945,157** assertions, checksum `fbea92c63d86af53`.
All paths reported **zero allocations and zero deallocations**:

| Measured path | Accepted | Rejected | Frames | Fresh raw | Carried raw | Restores |
|---|---:|---:|---:|---:|---:|---:|
| enabled | 40 | 0 | 13,793 | 9 | 0 | 28 |
| preset | 54 | 0 | 456 | 90 | 3 | 24 |
| dense | 5 | 0 | 224 | 4,608 | 0 | 4 |
| maximum | 3 | 0 | 196,608 | 6 | 0 | 0 |
| carry | 13 | 0 | 32 | 2,054 | 1,027 | 0 |
| output-shape | 24 | 0 | 1,152 | 0 | 0 | 0 |
| rejected | 0 | 33 | 0 | 0 | 0 | 0 |
| setProcessing | 15 | 6 | 0 | 0 | 0 | 0 |

These allocation observations cover calling-thread global C++ operators under
the retained Linux ELF module-isolation proof. They are not a general allocator,
all-thread, platform or device-deadline claim. Timings remain observations in the
verbose log and are not pass criteria for a physical device.

## Original failures and diagnostics

1. Ninja configure failed because Ninja was not installed, followed by CMake's
   compiler-not-set consequence. No translation unit or test ran in that attempt.
   The new Makefiles build configured successfully. Its optional LIBJACK lookup
   was unavailable and an SDK atomic feature probe failed; neither prevented
   the required headless SDK configuration/build.
2. The first controller run failed at `serialize(read) == wanted_text`. The
   expected legacy-to-v4 text spliced 17 bytes for the 18-byte literal
   `pedal drawbars 7 3`, leaving one trailing digit. This was a test-oracle bug.
   Replaced literal lengths with `std::string_view::size()`. Exact state4 rich
   output and native pending/acknowledged migration had already passed their
   other assertions/suites. No production correction or parser change followed.
3. The successful plugin validator retains **16** `Failed to teardown test!`
   messages and **nine** rejected unsupported-rate setup diagnostics. It reports
   support for 44.1/48/96 kHz, unsupported 64-bit processing and final result
   **47 tests passed / 0 failed**. Preserve these qualifications; do not call the
   run diagnostic-free or infer unsupported precision/rate support.

## Exact source and artifact identities

All hashes below are SHA-256. Full copied-source manifests and command logs are
under `/tmp/hammond-preset-a22/` for the integrator to retain with its publication
evidence. The original manifest is `source-manifest.json`; the final manifest
changes only the corrected controller test source. The build-input digest is
computed from UTF-8 lines `path + ' ' + sha256 + '\n'`, sorted by path, for the
155 named input-root files.

| Identity | SHA-256 |
|---|---|
| Original 1,240-file source manifest | `b70c009b8553fd7260701d223eff31001567a43229a0a0b362cf1b8c64185eab` |
| Final 1,240-file source manifest | `a21d573d4d1da73340b1942b1a72bd494b45eb3663ab4531599e87ba5a91541c` |
| Final 155-input manifest digest | `8d90ce6325f66ccc0ed58534573d7b77d35a3fa2abecfeed878b5c15937b3cf8` |
| `HammondB3.so` | `36d02646e039d0748a2f01aa9e89dda07c5be816a3ab040b40ae694faad9889e` |
| `moduleinfo.json` | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| `configure.log` (failed Ninja) | `ac9e48549c9398ebaf6576d2d1bf803c169b3991b447580f24283886c2d2f616` |
| `configure-make.log` | `b5f794a19e4e2fe5b938b816ced4a2fc854057510db41531bdb2175c63e3985e` |
| `build.log` | `bd713f0f4ab2d152ca8007bbee279bbd77a3ca7fcedf50e6e203032f5d985bae` |
| `build-controller-fix.log` | `3cfb0c4de28f46e2efeb7da494c863a0f9f3656e89de6c55784ceb0c6879c927` |
| `native-first.log` | `f00388d75469ccfe2737c66ccaf74f0c5491ff146f02b7950b8b964abc5689a5` |
| `native-first.xml` | `25466af98d65dfd9e00f8996bc53cb752c2c70c82123742ac973dd564aba52f8` |
| `native-final.log` | `e525207f53d60127dcc03702615eee78d4b50d91665fe27b4b653bacf4260396` |
| `native-final.xml` | `666235036398d738259648f78e3183a69ef7d10f3921a4b507248f66b9499f06` |

### Owned native source

| File | SHA-256 |
|---|---|
| `plugins/vst3/Controller.cpp` | `2978813561b9702b560e227a9ff27b62a19c0c4f9a7b05823a2c40e3112d3be7` |
| `plugins/vst3/Controller.h` | `c5377f380ddb1a1c006482e138cdd6f4736a0258803d8ae9dd0f735ff72570bb` |
| `plugins/vst3/tests/NativePresetOracle.h` | `3b620c607814fc9b686ff5e8e56292956649ab35cd42f0cf9df3426d26196dad` |
| `plugins/vst3/tests/test_native_abi.cpp` | `f93a59fc0cdb99b8b016f77ff78baac6f78a083de674fed49ee194cc12d766f7` |
| `plugins/vst3/tests/test_native_automation.cpp` | `51b4ae6fa84d6895c4ddd0b378223aa132fe5ea8b74016bf262f3147736fcdf9` |
| `plugins/vst3/tests/test_native_behavior.cpp` | `8e9dbfa48663fb316e0f2e5d4d1df9492259c1e5efaaaa461cd193263c095f39` |
| `plugins/vst3/tests/test_native_concurrency.cpp` | `c863a9b6ad514163d3ff3645b43aa04171995ddbf7992d9fdf6aeca88af5027f` |
| `plugins/vst3/tests/test_native_controller.cpp` | `fae0af12a9fc272c1ffbb302666db78aca8c176083b07e0f8a818a97353db640` |
| `plugins/vst3/tests/test_native_realtime.cpp` | `56c47d677c838c7543121c9738e191abe3f2e3437b900df607b6606be8fb53d4` |

### Consumed integration and unchanged adapter inputs

| File | SHA-256 |
|---|---|
| `CMakeLists.txt` | `1c569b0dc5d5afbe5b99ff8529d457ca736ad8e82a36105336badbd4e9841e53` |
| `plugins/vst3/CMakeLists.txt` | `25346bdd7edd1c966b3edc7f7b553ef49924bd5f21ddf7125422e76940652545` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `include/hammond/ParameterBridge.h` | `cd313711737f94e5f7f7b0dd73851347b9c4e53b3962d5d40d7e7c37883293d3` |
| `src/ControlState.cpp` | `9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |
| `src/ParameterBridge.cpp` | `296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220` |
| `src/HostTimeline.cpp` | `f0a3f88396f0f9b743f91277ca31b85a32deda98abae53d022dbf601d2226149` |
| `src/StateExchange.cpp` | `3f661eab16cd164e5d1299ee59ea7c27e9e1cfd2f7d8d2d25218e24734884837` |
| `data/parameter-registry.json` | `aedaa09e47fc2baba4a08484cce84916f2a27edac55d45f03f167f41c84bd6e2` |
| `plugins/vst3/Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `plugins/vst3/Processor.h` | `e85cdc6f7aaf70c05eda61630a5e3acee7c7f2fef2796a2c5f557ce034a54e72` |
| `plugins/vst3/StateStream.cpp` | `c83fbf22ea26c0b7a89974d4c0aa590c1e46f44f4a6c457d6fee512740d02117` |
| `plugins/vst3/StateStream.h` | `6493aa859427ad55cf81c84df29b4669f038828eb4d2c53f04e442aefadeea8e` |
| `plugins/vst3/PluginIds.h` | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |

## Handoff

Production/API readiness was reported before native qualification, and the final
8/8 outcome and source identities were reported to root. The assigned native
implementation is ready for later independent acceptance. Root retains the
full copied-source manifest and logs with its publication evidence, incorporates
other workers' changes in a new coherent qualification, and owns shared status,
next steps, development log, setup documentation, commit/push and hosted checks.

No sanitizer, macOS/Windows build, DAW/device test, standalone UI capture or
physical fidelity gate was run by A22. The fixed table is documentary and uses
the existing nominal gains. The preserved older build executables remain
available for independent no-fixed regression comparisons.

## Integrator evidence retention

The final copied-source manifest, original failed gate, corrected final transcript
and JUnit are now retained under [reports](reports/retained-focused-evidence.json).
Their bytes and hashes match the local evidence identified above.

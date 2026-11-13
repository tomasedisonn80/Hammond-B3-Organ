# Assignment 57 — execute the actual hosted Linux module

## Identity, scope and result

- Assignment: **57/60**, **wave 10**, 2026-11-13 pedal session.
- Owner: **`/root/w10_a57_hosted_module_runtime`**.
- Owned files: this note and
  [PEDAL_HOSTED_RUNTIME_FINAL.md](../../reviews/PEDAL_HOSTED_RUNTIME_FINAL.md).
- Result: the actual downloaded wave-8 Linux module passed one finite gate
  consisting of the existing ABI, behavior and dense automation executables;
  all three exited zero with empty standard error.
- Source: published commit `d601eb166ea3206748f8e012b20a463ff365c0b1`, tree
  `8af684dfe56f88222c52ff71d85a911ee1192fa1`; coherent local reference source
  tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e`.

The parent explicitly required actual hosted bytes. No plugin, host, SDK or
production source was rebuilt or modified. No shared status/manifest file was
edited, and no staging, commit or push was performed by this worker. Parent
owns integration and publication under the standing instructions in
[AGENTS.md](../../../AGENTS.md).

Read the current instructions, project plan and native ABI/behavior/automation
contracts. This task adds an M9 native engineering observation to the existing
nominal dry-organ work, not a new acoustic model, measured instrument result or
complete product-release claim. The separate
[wave-8 platform audit](../../reviews/PEDAL_HOSTED_WAVE8_FINAL.md) records the
original hosted jobs and their limitations.

## Inputs and independent provenance checks

Workspace root: `/workspace/scratch/f364bc93d920`.
Repository: `/workspace/scratch/f364bc93d920/Hammond-B3-Organ`.
Private evidence directory:
`/workspace/scratch/f364bc93d920/a57-hosted-module-runtime`.

The reviewer requested fresh connected GitHub workflow-artifact metadata for
repository `tomasedisonn80/Hammond-B3-Organ`, run **43417681882**. Both retained
API records identify source commit `d601eb166ea3206748f8e012b20a463ff365c0b1`;
the diagnostic provenance separately identifies attempt 1. The actual Linux job
is **131859604629**. Assignment 54 supplied existing ZIP
paths, which assignment 57 independently read and hashed:

| Actual input | Bytes | SHA-256 |
| --- | ---: | --- |
| `a54-hosted-platform-audit/14032427484.zip` | 188,166 | `3c412375fc4d2d3708854a9426a26e13c255b5d79d89911cfb7f8e50076a9562` |
| `a54-hosted-platform-audit/14032911399.zip` | 40,252 | `4232e4ba52985c4d0b827bc56bb1a63ac9bd93410ac5360b68c4131c6a97371a` |
| Inner `HammondB3-Release.tar.gz` | 187,729 | `6b43b47b9093be933c1b4f5941ba327c1c015e9856d43ebb4d452655aab342e8` |
| Inner `inventory.json` | 1,776 | `77776908be91d62193863e177b9768a86b66667766c4771673cdd3b7663d0844` |

ZIP sizes and SHA-256 values match the fresh API digests. The diagnostic ZIP's
provenance matches the exact published commit/tree, run, attempt and Release
configuration. Its build-inventory bytes equal the bundle inventory. The bundle
ZIP contains exactly `HammondB3-Release.tar.gz`, `inventory.json` and
`archive.sha256`; the latter matches the inner archive bytes.

The four payload members and their individual hashes/modes are retained in the
companion review. Each member's size, hash and mode were checked before its
explicit private write, covering all 456,767 payload bytes. The audit rejects
absolute/escaping paths, links, device files,
unexpected or duplicate file members, and mismatched size/hash/mode. It writes
each regular member once with exclusive creation and preserves permissions.
The exact extracted bundle is:

```text
/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/hosted payload with spaces/HammondB3.vst3
```

All 534 tracked source files were compared to Git blob IDs and executable-mode
classification from the frozen tree, with SHA-256 inventories retained. The
published source differs in exactly these six Markdown result files:

```text
docs/DEVELOPMENT_LOG.md
docs/NEXT_STEPS.md
docs/PEDAL_HANDOFF.md
docs/STATUS.md
docs/development/2026-11-13-pedals/README.md
docs/reviews/PEDAL_WAVE8_INTEGRATION.md
```

All 115 inspected CMake/C++/header/data inputs in the current repository match
the frozen reference source. The later native-inventory Python repair is outside
the compiled host/module inputs. Source and runtime bytes were rechecked after
the gate, including the complete source file set with the four known caches
below. The current checkout advancing during documentation does not turn this
into qualification of an unidentified later module.

## First setup failure and its bounded correction

The first private audit-driver invocation verified every tracked source file
then stopped at an overly strict file-set assertion. Four generated caches
already existed in the shared frozen source directory. No tracked file was
missing or changed. This happened **before artifact extraction or native
execution**, so there was no failed plugin callback or runtime substitution.

| Extra generated file below `checkpoint-w08/source/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `tests/__pycache__/test_native_bundle_inventory.cpython-312.pyc` | 40,775 | `e0a88671cb20d8b1098318b4716cbe63fd0a2cb5c79fe59aaca918f9e700542c` |
| `tools/__pycache__/native_bundle_inventory.cpython-312.pyc` | 25,350 | `fc20bfd8adee579699aa5b20a06cc288911c62ea15d163b4031a19ecef5d5b63` |
| `tools/__pycache__/validate_factory_reference.cpython-312.pyc` | 28,994 | `26a269e4405c7a5f8d31a1bd6af4d399a7b0ad2d566f76eb9d52a753f9c39353` |
| `tools/__pycache__/validate_pedal_map.cpython-312.pyc` | 9,373 | `671ccb34fe8f6c1be8bb167c7c36a58a94ca22c5b0724fe193c61664e0668bb6` |

Only the private audit driver was corrected: retain these exact regular files
separately, require no missing tracked or other extra files, and preserve their
bytes. Parent confirmed that tracked source and build inputs are the
qualification boundary. No cache or shared file was deleted; product tests,
production code and SDK checkouts were unchanged. The final source/file-set
and runtime rechecks passed. `initial-setup-stop.json` retains this failure
alongside the successful receipt.

## Exact reference, profile, build and dependency identities

Reference build root:
`/workspace/scratch/f364bc93d920/checkpoint-w08/build-native`.
These are the pre-existing coherent wave-8 executables; assignment 57 performed
no compilation.

| Runtime input below the reference build, except the explicitly hosted row | Bytes | SHA-256 |
| --- | ---: | --- |
| `bin/Release/test_native_abi` | 324,744 | `de4f307def0afeb410e704983d4f0e31628894fa2e175e5afe7daa2a8db11651` |
| `bin/Release/test_native_behavior` | 450,448 | `cb3f0ba106e69fee2274644523d33f8cbb4fead97678b25b9e4eabfeb0efcf68` |
| `bin/Release/test_native_automation` | 342,840 | `4324256048874560af9fc31d63a1ec10f7f06dc5069ffe311dfbcde2fd36a9e3` |
| `nominal.b3p` | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Actual hosted `Contents/x86_64-linux/HammondB3.so` | 446,696 | `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca` |
| Comparison-only local `VST3/Release/HammondB3.vst3/Contents/x86_64-linux/HammondB3.so` | 434,168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| `compile_commands.json` | 139,282 | `a63c4cd51551d29ed07aee9a796578e404ff634694e7b25d9918a6036757c3ba` |
| `CMakeCache.txt` | 23,372 | `5e70b382cd7e24fcdebca163c90ee15179db36553635adf9aaca9b65ec07ab5f` |

The profile's exact bytes occur once inside the actual hosted module. The SDK
lock SHA-256 is
`ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965`.
Read-only `--verify-existing` inspection confirmed the following actual pins,
five primary licenses and embedded JSON, with `network_used: false`:

| SDK checkout | Commit |
| --- | --- |
| Root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| `base` | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| `cmake` | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| `pluginterfaces` | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| `public.sdk` | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

The hosted diagnostic identifies GCC 13.3.0
(`Ubuntu 13.3.0-6ubuntu2~24.04.1`), Ubuntu image `20261101.360.1`,
Linux `7.0.0-1017-azure`, glibc 2.39 and Python 3.12.16. The existing local
reference build uses GCC 14.2.0 (`Debian 14.2.0-19`). Actual execution reports
Linux `6.18.57 x86_64 GNU/Linux` and glibc 2.41. These are distinct build/runtime
observations, not a reproducible-binary claim.

The module's `DT_NEEDED` entries are exactly `libstdc++.so.6`, `libm.so.6`,
`libgcc_s.so.1` and `libc.so.6`. The actual ABI loader trace initialized these
local runtime files; hashes identify this execution environment:

| Resolved local file | Bytes | SHA-256 |
| --- | ---: | --- |
| `/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2` | 225,672 | `c8438e4fde1934e61c88311633f00949ff645d5c04cdb8671fa3d78164d2f307` |
| `/usr/lib/x86_64-linux-gnu/libc.so.6` | 1,995,216 | `9792e3cbb541c8f44c7acf5f14f4022ea62998ecc787d326bed4d8b6547dfd92` |
| `/usr/lib/x86_64-linux-gnu/libgcc_s.so.1` | 182,856 | `30c61ab012a4241bed033725a09b61f5fdd3bb7df95ee852d0b096520524c7af` |
| `/usr/lib/x86_64-linux-gnu/libm.so.6` | 977,112 | `6d567d53e895273ca14a1f9dc164fc6c8d39aed2f60aa46a733c2784228915f3` |
| `/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.33` | 2,497,768 | `972bb2a18b71140dab0240f8a1f68ab3fb1d56bcd4c4f824a91b70888faf5a00` |

The highest required symbol versions observed are `GLIBC_2.38`,
`GLIBCXX_3.4.31` and `CXXABI_1.3.9`. All dependencies resolved and all three
executables completed. No older Linux distribution or alternate C++ runtime
is qualified by that observation.

## Actual commands, environment and loader proof

The private driver was invoked from the repository root:

```sh
python3 /workspace/scratch/f364bc93d920/a57-hosted-module-runtime/qualify.py
```

It independently read Git blobs, API metadata and ZIP/tar bytes, performed
member-by-member extraction, captured the following inspection commands, and
then executed the three hosts once. CTest below is discovery only:

```sh
git -C /workspace/scratch/f364bc93d920/Hammond-B3-Organ ls-tree -rz --full-tree 5370890e32045a556cb61a88cdb1f04fb5a18f7e
git -C /workspace/scratch/f364bc93d920/Hammond-B3-Organ diff --name-only 5370890e32045a556cb61a88cdb1f04fb5a18f7e 8af684dfe56f88222c52ff71d85a911ee1192fa1
python3 /workspace/scratch/f364bc93d920/checkpoint-w08/source/tools/acquire_vst3_sdk.py --verify-existing /workspace/scratch/f364bc93d920/vst3sdk
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir /workspace/scratch/f364bc93d920/checkpoint-w08/build-native -C Release --show-only=json-v1
readelf -h -d -V --wide '/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/hosted payload with spaces/HammondB3.vst3/Contents/x86_64-linux/HammondB3.so'
nm -D --defined-only /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_abi
nm -D --defined-only /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_behavior
nm -D --defined-only /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_automation
uname -srmo
getconf GNU_LIBC_VERSION
c++ --version
```

The three selected executables come directly from CTest's discovered commands.
Only the bundle argument is replaced with the independently extracted hosted
bundle. The profile remains the coherent build's actual input. The exact command
arguments, represented with shell quoting, were:

```sh
/workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_abi '/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/hosted payload with spaces/HammondB3.vst3' /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/nominal.b3p
/workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_behavior '/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/hosted payload with spaces/HammondB3.vst3' /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/nominal.b3p
/workspace/scratch/f364bc93d920/checkpoint-w08/build-native/bin/Release/test_native_automation '/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/hosted payload with spaces/HammondB3.vst3' /workspace/scratch/f364bc93d920/checkpoint-w08/build-native/nominal.b3p
```

Each ran with `subprocess.run(..., timeout=180)` from:

```text
/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/unrelated working directory
```

The exact environment transformation in the driver was:

```python
environment = {
    key: value for key, value in os.environ.items()
    if not key.upper().startswith('HAMMOND_')
}
for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT',
            'LD_DEBUG', 'LD_DEBUG_OUTPUT'):
    environment.pop(key, None)
```

The receipt's `loader_variables_removed` array is empty: none of the five
loader overrides had been set. The ABI process alone then set
`LD_DEBUG=libs,bindings` and
`LD_DEBUG_OUTPUT=/workspace/scratch/f364bc93d920/a57-hosted-module-runtime/abi-loader`.
The other hosts used the cleaned environment without tracing.

None of the three hosts exports a Hammond symbol. The actual ABI trace
`abi-loader.37` identifies initialization of the extracted hosted module and
six `GetPluginFactory` bindings to that exact file. All **56 observed bindings
of Hammond symbols from the module target that same module**. The harness's
SDK `Module::create(bundle_path, error)` path has no local-module fallback.
These observations establish artifact loading and exclude substitution through
the selected executables' dynamic exports. They do not instrument allocations,
locks or callback deadlines.

## Observed output and comparisons

| Executable | Exit | Standard error | Wall seconds |
| --- | ---: | --- | ---: |
| `test_native_abi` | 0 | Empty | 0.918935 |
| `test_native_behavior` | 0 | Empty | 2.126869 |
| `test_native_automation` | 0 | Empty | 0.921640 |

Summed process wall time: **3.967444 seconds**. ABI includes loader tracing;
the sum is not a CTest duration or real-time deadline measurement. No further
optional runtime tests were repeated after this gate qualified.

Actual ABI standard output:

```json
{"suite":"native-abi-v1","instances":9,"assertions":691878,"descriptors":45,"conversions":2002,"accepted_callbacks":73,"rejected_calls":86,"state_round_trips":7,"lifecycle_sequences":6,"compared_frames":229725,"audible_frames":217972,"maximum_audio_error":0,"float_hash":"af029009868faa04"}
```

Actual behavior standard output:

```text
native behavior checks=29046845 accepted_callbacks=1030 rejected_callbacks=72 zero_callbacks=123 direct_reference_frames=233792 exact_channel_samples=610510 paired_setup_channel_samples=61360 future_audio_samples=81302 audible_samples=575944 state_reads=542 rejected_state_loads=68 threshold_cases=90 rollback_cases=59 partition_cases=9 rate_changes=3 isolated_division_cases=9 division_peaks=0.015,0.015,0.0096094 peak=0.0906279 checksum=3c4b24caebfdd1b9
```

Actual dense automation standard output:

```text
native automation: score_cases=6 restore_cases=3 gap_cases=6 callbacks=231 zero_callbacks=18 state_reads=261 direct_reference_frames=89979 exact_channel_samples=179958 partition_mono_samples=19407 future_channel_samples=39948 nonzero_channel_samples=157150 long_callbacks=3 guaranteed_expression_events=12288 isolated_windows=18 division_min_rms=0.00402141,0.00655038,0.00172213 reconnect_difference=0.0238609 maximum_error=0 peak=0.198746 checksum=5ea365699a5717c9
```

These are exact comparisons by the existing acceptance suites, not fitted audio
tolerances. The ABI tests public native factories, interfaces and state/lifecycle
behavior. The behavior gate includes admission rejection, rollback, state and
audible continuation; its large check counter is not a count of independent
test scenarios. The automation workload independently schedules all controls,
state/carry composition, gaps and whole/irregular partitions, including audible
division windows and an actual Lower reconnect counterfactual difference.

The reference intentionally shares nominal DSP/profile code while independently
specifying wrapper inputs and scheduling. Its agreement establishes the tested
wrapper contracts for these hosted bytes on this local runtime. It does not
prove physical fidelity, every scheduling history or cross-platform bitwise
output. State operations here are sequential; no new concurrency or TSAN claim
is added. The earlier full native-suite and validator results remain separate.

## Retained receipt identities

The files below remain in `a57-hosted-module-runtime/`. These workspace paths
may be transient; the durable review and this note retain the decisive source,
artifact, command, output and runtime identities. If those paths are absent,
reacquire the named artifact, check its digest and payload, and prepare a
coherent reference build before asserting a new execution result.

| Receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `qualify.py` | 11,463 | `a3a4b032de0d15ef3835a0896cd390b92c19459b00bc61385ed72451ead22aeb` |
| `qualification.json` | 12,175 | `31c472ce6f679405af1d45e3fb984325683cbffa3c5bcba654b7f5a7ae47ecb6` |
| `source-inventory.json` | 140,936 | `e47b731d0120e2bfbf51c86fb476947ab5734f862a6fbb4cd6990a4a489f2305` |
| `initial-setup-stop.json` | 1,126 | `c323d5cf739371cb37351174c9da6437c027186b46cfd8b84b17aff64ee0d73e` |
| `api-artifact-metadata.json` | 1,705 | `5af83fd588354730e70a855a54b3ee758c5756798bdde1afcf8fd689220dcc1c` |
| `hosted-provenance.json` | 425 | `e8ef61a75b52c8f66b843067a704b83ba07af6c770ab10d989d9f119f9b9c631` |
| `hosted-module-readelf.log` | 9,526 | `cefca954d4d63d180f3cab46ac5eaaf52867fd33d4fd8abf09629a2efc1399df` |
| `sdk-verification.json` | 562 | `051362e9ff23d39e4a7deca56f743d37c83123398fef36971d14fffc9630cd49` |
| `ctest-discovery.json` | 69,830 | `b46701833134e72f23f3efc7202735630db7e46046024e6cb534679fd7e8f281` |
| `abi-loader.37` | 425,842 | `79828bc9705c50756cd55d970d772283428fe9938a3e4ecdce89480937570169` |
| `test_native_abi.stdout.log` | 291 | `688e792adb4e371e528bcacfc5c76eedc42f5028a922a9a9b3e4c1294d241fc5` |
| `test_native_behavior.stdout.log` | 456 | `eff32bb8973eab73db03b0b9b7af9ca500c8005a4249195179d5c75a928e9e0d` |
| `test_native_automation.stdout.log` | 466 | `65c096f8d0f7a0e19bd78b9c78152e6b869140629b6cd8281f0a473d59e3083c` |

Each of the three standard-error files is zero bytes, SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Separate retained files contain the exact `nm` exports, local toolchain text,
hosted toolchain diagnostic and published-tree delta. No provenance field or
result was inferred from a similarly named earlier local module.

## Limitations, integration and next step

No actionable production defect or runtime dependency incompatibility was
observed in this finite Linux artifact gate. Its accepted scope is the three
executed host contracts against module SHA-256 `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca`.
It does not claim a new 8-test native CTest run, an ordinary 71-suite run,
allocation audit, concurrent state stress, TSAN, DAW/device/deadline result,
Windows/macOS execution, reproducible binaries, signing/rights clearance or
measured organ fidelity. The prior SDK-validator record still includes 16
teardown diagnostics and nine unsupported-rate error-labelled messages; no
validator was rerun here.

Parent should accept these two documents, update the actual assignment ledger,
retain the scoped runtime result in current status, complete the exact final
source/record gate and publish under the existing expected-head workflow.
The Windows inventory junction/reparse repair needs its own actual Windows
execution. A macOS runner-acquisition outcome is distinct from a project-test
outcome; only an acquired and executed job can close that platform's gate.
Do not inherit either result from this local Linux execution.

Future model development follows
[M3_REMAINING_AND_SCANNER_GATE.md](../../M3_REMAINING_AND_SCANNER_GATE.md):
identify graph inputs and variant/source basis, implement the proposed prepared
graph/compiler and independent numerical comparisons, and retain the acquisition
limits. Native artifact agreement does not supply the absent specimen data.

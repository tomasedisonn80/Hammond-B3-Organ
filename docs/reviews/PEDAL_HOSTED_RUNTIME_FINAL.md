# Actual hosted Linux module runtime audit

## Result and ownership

Assignment **57/60, wave 10**, owner
**`/root/w10_a57_hosted_module_runtime`**, independently verified and loaded the
actual Linux bundle downloaded from wave-8 native run
[43417681882](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681882),
attempt 1, Linux job **131859604629**. The ABI, behavior and dense automation
executables each exited zero against that extracted module. This is a finite
local execution of a hosted artifact; the separate
[hosted platform audit](PEDAL_HOSTED_WAVE8_FINAL.md) records the jobs themselves.

The downloaded module is **446,696 bytes**, SHA-256
`b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca`.
The local wave-8 module is **434,168 bytes**, SHA-256
`d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.
Their inequality was checked before execution. No module or reference host was
rebuilt for this assignment. Loader tracing and dynamic-export inspection below
identify which implementation actually supplied the results.

The [assignment record](../development/2026-11-13-pedals/57-hosted-module-runtime.md)
retains exact argument arrays, raw output, runtime and reference-host hashes,
the setup-only failure, and the next gate. Only these two documentation files
are owned by this assignment; shared status, commits and pushes belong to the
integrating agent.

## Published source, archive and extracted bytes

| Evidence | Exact identity |
| --- | --- |
| Published source commit | `d601eb166ea3206748f8e012b20a463ff365c0b1` |
| Published source tree | `8af684dfe56f88222c52ff71d85a911ee1192fa1` |
| Coherent local reference source tree | `5370890e32045a556cb61a88cdb1f04fb5a18f7e` |
| Bundle artifact | `14032427484`, 188,166-byte ZIP |
| Bundle ZIP SHA-256 | `3c412375fc4d2d3708854a9426a26e13c255b5d79d89911cfb7f8e50076a9562` |
| Inner `HammondB3-Release.tar.gz` SHA-256 | `6b43b47b9093be933c1b4f5941ba327c1c015e9856d43ebb4d452655aab342e8` |
| Bundle `inventory.json` SHA-256 | `77776908be91d62193863e177b9768a86b66667766c4771673cdd3b7663d0844` |
| Diagnostic artifact | `14032911399`, 40,252-byte ZIP |
| Diagnostic ZIP SHA-256 | `4232e4ba52985c4d0b827bc56bb1a63ac9bd93410ac5360b68c4131c6a97371a` |

The reviewer obtained fresh artifact metadata through the connected GitHub API
and independently matched both existing downloaded ZIPs to its exact sizes,
SHA-256 digests, run ID and source commit. The diagnostic provenance identifies
the same commit, published tree, Release configuration and run attempt. Its
build-inventory bytes equal the bundle inventory. Assignment 54's observations
were useful acquisition pointers; the checks above were repeated on the actual
bytes by assignment 57.

The outer bundle ZIP contains exactly the tar archive, `inventory.json` and
`archive.sha256`. The inner archive has four regular payload files totaling
**456,767 bytes**. Each member's path, size, SHA-256 and mode matched the
inventory before writing an explicit private copy. Absolute paths, parent
escapes, links, device files, duplicate files and unexpected members were
rejected by the audit driver. File and directory modes were preserved; the
module remained executable. No general archive extraction was used.

| Path below `HammondB3.vst3/` | Bytes | Mode | SHA-256 |
| --- | ---: | --- | --- |
| `Contents/Resources/THIRD_PARTY_NOTICES.md` | 7,887 | `0644` | `a3aa1900ec8b584bfe0879d0d8c7c1af3148dc23729d01a62e26ed428b61c2f6` |
| `Contents/Resources/VST3_SDK_LICENSE.txt` | 1,094 | `0644` | `e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e` |
| `Contents/Resources/moduleinfo.json` | 1,090 | `0644` | `d621a2149b6c8b8bac9a84d40bed21ed8de9fbeb9a8708ad44cf890050e56184` |
| `Contents/x86_64-linux/HammondB3.so` | 446,696 | `0755` | `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca` |

## Coherent reference and retained setup failure

All **534 tracked files** in `checkpoint-w08/source` were compared with the
frozen tree's Git blob identities, byte sizes, SHA-256 hashes and executable-mode
classification. The published tree differs only in six Markdown result files.
All **115 inspected CMake/C++/header/data inputs** also match the current
repository. The later Windows inventory repair changes Python tooling and its
regression, leaving these compiled inputs unchanged.

The first audit-driver invocation stopped before extraction or native execution:
its exact-file-set assertion found four pre-existing generated Python cache
files. Every tracked file already matched, and none was missing. The private
driver was corrected to identify and hash those four files separately, require
no other extra or missing files, and preserve them. No shared source, product
test or SDK file was repaired or deleted. The assignment note retains the exact
cache names and hashes; this was a setup assumption failure, not a plugin
failure. The successful run rechecked tracked source, the known caches, current
compiled inputs, runtime binaries/profile and every extracted payload afterward.

The compiled nominal profile is **4,545 bytes**, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Those exact bytes occur once inside the hosted module. The actual reference
hosts come from `checkpoint-w08/build-native`; their hashes and build-record
identities are retained in the assignment note. Read-only SDK verification
confirmed all five pinned checkouts, five primary licenses and the embedded
JSON dependency without network use or SDK modification.

## Runtime compatibility and loader identity

The hosted diagnostic records GCC **13.3.0**, Ubuntu image **20261101.360.1**,
x86-64 Linux **7.0.0-1017-azure** and glibc **2.39**. This execution used the
existing Debian GCC **14.2.0** reference hosts on x86-64 Linux **6.18.57** with
glibc **2.41**. The ELF is 64-bit x86-64. Its four `DT_NEEDED` entries are
`libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1` and `libc.so.6`; the actual loader
trace identifies local files for all four and the dynamic loader itself.
The highest observed required symbol-version families are `GLIBC_2.38`,
`GLIBCXX_3.4.31` and `CXXABI_1.3.9`. No missing symbol or loader incompatibility
occurred in this workload. These observations do not qualify an older runtime
or define a complete minimum operating-system support policy.

Each host ran from an unrelated directory against a private bundle path
containing spaces. The execution environment filtered all `HAMMOND_*` overrides
and cleared loader override variables; none of those loader variables was set
in the original environment. Only the ABI process enabled `LD_DEBUG=libs,bindings`
and its private trace output. No product environment overrides selected a local
plugin or profile.

The [native harness](../../plugins/vst3/tests/NativeHarness.cpp) calls the SDK's
`VST3::Hosting::Module::create` with the supplied bundle path. Its selected
executables export **no Hammond symbols**, as checked with
`nm -D --defined-only`. The actual ABI trace records initialization of the exact
downloaded module, six `GetPluginFactory` bindings to that same module, and
**56 observed Hammond-symbol bindings**, all resolved to that same module.
Consequently the tested module's DSP symbols were not satisfied by an exported
copy from the local reference executable.

The trace is 425,842 bytes, SHA-256
`79828bc9705c50756cd55d970d772283428fe9938a3e4ecdce89480937570169`.
This identity evidence is separate from the native allocation/interposition
gate and does not claim callback allocation or lock measurements.

## Finite acceptance result

CTest JSON discovery established the existing registered executable paths.
The reviewer then ran these **three executables directly**, supplying the
hosted bundle and coherent profile. All exited zero with empty standard error.
No aggregate CTest count is inferred from discovery or from these three runs.

| Executed gate | Relevant observed comparisons | Process wall time |
| --- | --- | ---: |
| [ABI](../VST3_ABI_ACCEPTANCE.md) | 9 instances; 45 descriptors; 2,002 conversions; 7 state round trips; 6 lifecycle sequences; 229,725 compared frames, 217,972 audible frames; maximum audio error 0; checksum `af029009868faa04` | 0.918935 s |
| [Behavior](../VST3_BEHAVIOR_ACCEPTANCE.md) | 1,030 accepted / 72 rejected callbacks; 542 state reads; 68 rejected loads; 59 rollback cases; 9 partitions; 610,510 exact channel samples; checksum `3c4b24caebfdd1b9` | 2.126869 s |
| [Dense automation](../VST3_AUTOMATION_REVIEW.md) | 6 score / 3 restore / 6 gap cases; 231 callbacks; 261 state reads; 179,958 exact channel samples; 3 long callbacks requiring at least 12,288 distinct expression events; maximum error 0; checksum `5ea365699a5717c9` | 0.921640 s |

The summed process wall time is **3.967444 seconds**. ABI timing includes loader
tracing; none of these numbers is a callback-deadline benchmark. Assertion and
sample counts are observations of the existing suites, not counts of independent
physical scenarios. The complete raw output remains in the assignment note.

The oracles use the same nominal DSP implementation and profile while specifying
native scheduling, control mapping, ownership, state and automation expectations
independently of the corresponding wrapper logic. Bitwise comparison is useful
evidence that this separately compiled artifact preserves those contracts under
this runtime. It is neither an independent acoustic model nor proof of binary
reproducibility. Sequential state work in these three tests does not add a
concurrent UI/audio or ThreadSanitizer result.

## Limits and next gate

The hosted module passed this one finite Linux runtime gate. No production
defect or dependency incompatibility was found in its executed scope. There
was no need to rebuild, substitute the local module, or repeat optional tests.
The earlier SDK-validator result still includes 16 teardown diagnostics and
nine unsupported-rate error-labelled messages; assignment 57 did not rerun or
erase that validator result.

This record adds no Windows/macOS execution, DAW session, audio-device operation,
deadline guarantee, custom editor, signing, distribution-rights clearance or
measured Hammond fidelity. The nominal source/contact/percussion/pedal models
retain their existing limitations. Native hosting is an M9 engineering subset
in the [project plan](../PLAN.md); it does not complete M3-M8 or product release.

The integrator should retain this exact artifact qualification, finish the
current revision's source/record gate and publication, and observe the final
hosted jobs. Actual Windows execution of the inventory junction/reparse repair
and any macOS job that acquires a runner need their own results. Later source,
SDK, runtime or module changes must identify their affected claims explicitly.
The next model work remains the concrete
[remaining M3/scanner contract](../M3_REMAINING_AND_SCANNER_GATE.md), with its
independent numerical and acquisition evidence still required.

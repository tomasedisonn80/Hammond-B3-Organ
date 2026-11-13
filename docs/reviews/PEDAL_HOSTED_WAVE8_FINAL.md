# Independent hosted wave-8 platform and artifact audit

## Result and exact source

Five executed jobs at **`d601eb166ea3206748f8e012b20a463ff365c0b1`** passed
their executed scopes. Both macOS jobs were cancelled without acquiring a runner,
with empty runner names and zero steps. **This is not a complete
four-job core or three-platform native matrix pass.** No new local product test,
plugin load, hardware test or build was performed by this reviewer.

The source tree is `8af684dfe56f88222c52ff71d85a911ee1192fa1`. Independent Git
object inspection confirms that it differs from root's qualified wave-8 tree
`5370890e32045a556cb61a88cdb1f04fb5a18f7e` in exactly six Markdown result files.
Both workflow APIs identify this source commit and attempt 1. Every downloaded
core diagnostic source-revision file matches it. Both native provenance files
also match the exact tree, native run ID, attempt and Release configuration.
The [local integration record](PEDAL_WAVE8_INTEGRATION.md) is a separate result;
its success was not used as a substitute for these hosted observations.

The audit concerns [core run 43417681825](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681825)
and [native run 43417681882](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681882).
Later source revisions, including assignment 51's Windows junction/reparse
repair, require their own qualification.

## Actual job results

| Job | Job ID | Actual execution | CTest wall time |
| --- | --- | --- | ---: |
| Core Linux GCC Release | 131859605862 | 71/71 passed; 548 Python methods in 33 Python suites | 54.81 s |
| Core Windows MSVC Release | 131859605848 | 71/71 passed; 548 Python methods in 33 Python suites | 94.05 s |
| Core Linux ASan/UBSan/leaks | 131859605423 | 71/71 passed; 548 Python methods in 33 Python suites | 133.77 s |
| Core macOS AppleClang | 131859605945 | Cancelled after runner acquisition failure; no runner and no executed step | Not executed |
| Native Linux GCC Release | 131859604629 | 8/8 passed; inventory, archive and both artifact uploads succeeded | 6.53 s |
| Native Windows MSVC x64 Release | 131859604308 | 7/7 passed; inventory, archive and both artifact uploads succeeded | 7.27 s |
| Native macOS AppleClang | 131859604644 | Cancelled after runner acquisition failure; no runner and no executed step | Not executed |

The final job-metadata responses have HTTP `Date` **2026-11-13 11:46:21 UTC**.
Core macOS completed at `2026-11-13T11:46:03Z`, native macOS at
`2026-11-13T11:46:02Z`, both with status `completed`, conclusion `cancelled`,
an empty runner name and `steps: []`. Their API `started_at` fields reflect the
queued job records and are not evidence that project code executed. The actual
cancellation annotations were retrieved at **2026-11-13 11:48:12 UTC**.

Every executed job's JUnit contains zero failed, disabled or skipped tests.
The complete core `LastTest.log` files each contain all 33 unittest summaries,
548 methods and no unittest skip. CTest's successful-output truncation omits
eight complete unittest summaries from each JUnit `system-out`; counting only
that truncated text would give 357 methods. The complete last-test logs provide
the 548-method count. The phrase “no skipped cases” in the pedal-renderer output
is not a skip. Native install executes two Python methods in each native job;
they are separate from the 548 ordinary methods. Platform-conditional workflow
configuration steps marked skipped are not skipped tests.

The extra native Linux entry is the Linux-only allocation/interposition audit;
it is absent from the Windows registry, not a disabled Windows test. The native
suite also executes actual bundle install/relocation, controller, SDK validator,
loaded-module ABI, behavior, dense automation and concurrent UI/audio gates.

### New ordinary gates actually executed

The same five selected suites below passed in all three completed core jobs.
Their method counts come from complete test output, not source-code counting.

| Gate | Methods per job | Inspected behavior tied to the published test source |
| --- | ---: | --- |
| `python_test_install` | 2 | Exact 23-file payload, real installation and relocation, all three pedal traces and source/installed SVG comparison, preflight preservation |
| `python_test_pedal_demo` | 10 | Retained source/audio identities, independent PCM checks, block partitions, component renders, semantic mutations and relocation |
| `python_test_pedal_session` | 24 | This session's records and independent malformed/partial/complete fixtures; no credit from historical sessions |
| `python_test_plot_pedal_trace` | 16 | Validated trace algebra and metadata, exact transition/min-max reduction, actual CLI paths, output preservation and concurrent publication |
| `python_test_native_bundle_inventory` | 19 | Published pre-reparse-repair inventory contract, including ordinary mutation rejection and Windows metadata representation cases |

The frozen manifest's 48 complete assignments are the actual source inputs to
this run. The session checker does not claim that all sixty were complete at
wave 8. The later junction test is not present here: do not turn these nineteen
inventory methods into a claim that assignment 51's subsequent repair passed.

### Actual tools and sanitizer policy

All five completed jobs record CMake/CTest **3.31.6**. Linux uses GCC **13.3.0**
and Python **3.12.16**. Windows core configuration records MSVC
**19.44.35229.0**; native configuration records **19.44.35230.0**. Both use
Python **3.12.10**. Native provenance reports Ubuntu image `20261101.360.1`
and Windows image `20261112.366.7`, each x64. A stable runner label does not
imply a permanently fixed compiler or Python patch release.

The sanitizer build log contains `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`. Its actual job environment retains
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and
`LSAN_OPTIONS=exitcode=23`. No AddressSanitizer, LeakSanitizer or undefined-behavior
runtime report was found in the retained build, execution and complete test logs.
This qualifies executed instrumented paths; it does not instrument Python or
establish a native-module TSAN run. The Windows native build commands for the
module/controller and inspected automation/concurrency tests use `/fp:strict`.

## Actual native output and retained validator limitations

Both native controller gates report **41,795 checks**, 3,720 threshold cases,
387 string round trips and 306 rejected stream cases. Each ABI gate compares
**229,725 frames** with maximum audio error zero and checksum
`af029009868faa04`. Each relocated bundle's separate ABI result has the same
229,725-frame zero-error result. Dense automation reports 89,979 direct-reference
frames and 179,958 exact channel samples, with maximum error zero.

The concurrent gate retains 3,072 accepted stress loads, 3,072 publication-only
saves and 96 callbacks without UI reads on each platform. Its schedule-dependent
counters differ: Linux compares 64,016 audible frames, Windows 92,131; each reports
zero error and 6,168 future frames. These are actual finite tests, not real-time
device deadlines or a proof covering every scheduling history.

Each actual SDK validator reports **47 passed, zero failed**, while retaining
**16 “Failed to teardown test!” diagnostics**, **nine unsupported-sample-rate
`ERROR` messages** and **15 unsupported-float64 informational messages**.
These messages are present in both complete native logs. The SDK summary does
not count them as failed cases. This audit neither suppresses them nor claims a
warning-free validator. The supported float32/44.1–48–96 kHz contract and
[earlier portability explanation](PEDAL_NATIVE_PORTABILITY.md) remain unchanged.

## Downloaded artifact verification

Seven actual ZIP archives were independently downloaded through the connected
GitHub Actions artifact endpoint. Each exact byte length and SHA-256 matches its
fresh API record, associated workflow run, source commit and attempt. The five
diagnostic ZIPs contain the corresponding source, configure, build, CTest,
JUnit and complete last-test logs. The two bundle ZIPs each contain exactly
`HammondB3-Release.tar.gz`, `inventory.json` and `archive.sha256`.

| Artifact ID | Role and platform | ZIP bytes | API-matched ZIP SHA-256 |
| --- | --- | ---: | --- |
| 14033006479 | Core diagnostics: Linux | 41,163 | `f4848ff3e9e6a8ca3120253db8cdd41fdb3dd72cbee47d99dd1da1490eace031` |
| 14032408092 | Core diagnostics: Windows | 44,440 | `468064e972c9eebee414915f6694278492dabb72c57464afa9ddb92075b93275` |
| 14032032993 | Core diagnostics: Linux sanitizer | 41,851 | `049675c2a82427b26d43fb8ef355bbc60f9e56fd989335a9549f019392e25b79` |
| 14033300281 | Native bundle: Windows | 412,670 | `98492edd8876945dfe6bc082b8850305d4275e0a94290bfa045ff4180371f5c4` |
| 14032911399 | Native diagnostics: Linux | 40,252 | `4232e4ba52985c4d0b827bc56bb1a63ac9bd93410ac5360b68c4131c6a97371a` |
| 14032427484 | Native bundle: Linux | 188,166 | `3c412375fc4d2d3708854a9426a26e13c255b5d79d89911cfb7f8e50076a9562` |
| 14031952990 | Native diagnostics: Windows | 36,625 | `54f37cbf6958cf94c11aff89f2f040b55c3f9264fa424e761f9b004157c31d62` |

For both bundle artifacts, the staged inventory bytes exactly equal the matching
build inventory in the diagnostic ZIP. The inner archive digest matches its
SHA-256 record. Independent tar inspection rejects links, absolute/parent paths,
duplicate regular files and unexpected regular members, then compares every
member's full bytes, size, SHA-256 and permission mode. All **ten regular
payload files** match. The reported total byte count matches their sum.
No bundle is executed by this inspection.

| Platform | Bundle / diagnostic artifact | Actual payload | Module SHA-256 | Inner archive SHA-256 |
| --- | --- | --- | --- | --- |
| Linux | 14032427484 / 14032911399 | 4 files, 456,767 bytes; 446,696-byte ELF64 x86-64 module | `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca` | `6b43b47b9093be933c1b4f5941ba327c1c015e9856d43ebb4d452655aab342e8` |
| Windows | 14033300281 / 14031952990 | 6 files, 658,056 bytes; 393,728-byte PE32+ x86-64 module | `14ff853094023a537f86dd836fe9ed5bc7025d8912a23a82e2fe29d3be552826` | `395b6c3ec41f4990dfd1f949c49141aa30bf04725f3c49f1a374cb412825b0b2` |

The Windows module has a different full-file hash from wave 7's Windows module;
no cause or cross-build byte identity is inferred. The current native provenance
and actual payload supply its identity. Linux's observed module hash happens to
match the prior hosted Linux module; this is not a compiler-independent build
reproducibility promise. Archive bytes are separately identified and differ
across runs.

Each module contains the unchanged 4,545-byte nominal profile exactly once,
SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The artifact lock bytes match the published lock, and each actual SDK verification
record reports all five locked checkouts, five primary licenses and embedded
JSON checks. The bundle notices equal the exact published source notices. Windows
also contains the recorded SDK-default icon and `desktop.ini`; their provenance
and remaining packaging decision are covered by the
[dependency/artifact review](PEDAL_DEPENDENCY_ARTIFACT_FINAL.md).

These checks establish observed workflow/source/package correspondence and
retained byte integrity. The inventory's source field remains caller-declared;
this is not signed binary-to-source attestation, DAW qualification, runtime-library
bundling, signing, rights clearance or measured physical fidelity.

## Remaining macOS and later-source gates

The two wave-8 macOS jobs changed from queued to cancelled before the final
metadata observation, with no runner and no executed step. Each current job's
actual annotations say “The job was not acquired by Runner of type hosted even
after multiple attempts” and contains three notices about macOS ARM64 runner
capacity. There is no macOS wave-8 test count, executed-project log, artifact or
pass. This is an observed infrastructure acquisition failure, not a detected
project test failure. The cancellation evidence was sent to root; no targeted
retry was issued by this reviewer.

The preceding wave-7 macOS jobs did end cancelled without execution. Root's
retained actual annotations identify a higher-priority waiting request in each
workflow/main concurrency group, alongside ARM64-capacity notices. That reason
belongs to those earlier job IDs. The current jobs instead have their own
explicit runner-acquisition failure annotations.

Root and assignment 59 should coordinate the macOS gate against the exact later
publication containing the reparse/junction repair and any other accepted
changes, retaining actual annotations if it cannot acquire a runner. Nothing in
this wave-8 audit qualifies that unexecuted later code. Root has corrected the
previously reported obsolete first-publication wording in `VST3_CI.md`; this
worker did not edit that shared document.

## Durable audit records

Complete downloaded ZIPs, safe extracted files, five job logs, original API
metadata, per-artifact file/hash receipts, parsed per-test/method records and
independent native archive checks are retained in the local
`a54-hosted-platform-audit/` directory. The Actions artifacts have the workflow's
14-day retention policy. The table below keeps stable identities for critical
execution records after temporary hosted artifacts expire.

For assignment 57's independent loading of the actual hosted Linux payload,
the downloaded bundle artifact is **14032427484** and its matching diagnostics
artifact is **14032911399**, both from native run **43417681882**, attempt **1**:

- Original bundle ZIP: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484.zip`.
- Inner bundle archive: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484/HammondB3-Release.tar.gz`.
- Inventory: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484/inventory.json`.
- Inner archive digest: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484/archive.sha256`.
- Original diagnostic ZIP: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032911399.zip`.
- Extracted diagnostic directory: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032911399/native-ci-logs/`.

The module member inside the tar is
`HammondB3.vst3/Contents/x86_64-linux/HammondB3.so`; this reviewer inspected its
bytes but did not extract the inner tar or load that module. The diagnostic
directory contains `provenance.json`, `build-inventory.json`, CTest output and
the actual configure/build/toolchain/SDK verification records. The final raw API
records are `final-api-43417681825.json` and `final-api-43417681882.json`; actual
cancellation evidence is in `annotations-131859605945.json` and
`annotations-131859604644.json`, all under the same audit root.

| Completed job scope | Complete LastTest.log SHA-256 | CTest JUnit SHA-256 |
| --- | --- | --- |
| core-linux | `dec06f2f1a95bce15e45cd8c71f2e04677bc5af1984abf8fea0771e5857c2353` | `21708d76cc7bb765216b4a5a3f01577ba2f860d3402877e66cecfde0e3228469` |
| core-windows | `0cff4b274b330c352229049daa28f8050b1355aba6bf669cdeb47c3dced5611e` | `885227da8d5027a95582f17fc082fd561df9c46a757cc9b496dfad51bc0c1d56` |
| core-sanitizers | `0d30aa65a572a1ad46a563f9b44c8711d5ca8c78cb9faab39f1e208e6d5a19c8` | `4c4290bf829bd02a026151bc14d28c7e935b05f52bef7291394a02d24df06b04` |
| native-linux | `1d70bbf5bdc7bd84a54fe00f0ec7a9ce8b4903ede61418704dc39b9f239228e8` | `6f5c24e01d3d2f6c3ee2c6f53dca48b8f7ea7198403f1f0704181d80681e2b93` |
| native-windows | `7a76dbdeebdbeabc117097c2e4239771c84f3b649609db5a79f3537c0f2f47e2` | `5ea7a5433f8cc1817b7c8f2893ea18f1cab94f2317dc002da186fa5c1cedd2b4` |

The [assignment note](../development/2026-11-13-pedals/54-hosted-platform-audit.md)
records the exact inspection procedure, source-file hashes and scoped handoff.

# Final platform qualification and portability repair

Owner: `/root/w10_a59_final_platform_gate`.

## Result: all seven exact-source jobs passed

The final audited repair revision is **`0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b`**, tree
`41c0b421643d4076c65ecbac8a750b4aae4d5806`. Its
[core run 43424724290](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43424724290)
and [native run 43424724580](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43424724580)
both completed **successfully**, attempt **1**. All four core jobs and all three
native jobs acquired actual runners, executed their gates and uploaded their
artifacts. Final workflow/job and artifact inspection was completed on
**2026-11-13 at 12:27:16 UTC**; the detailed integrity consolidation followed
that observation. No job was retried or cancelled by this reviewer.

Independent Git inspection binds this publication to qualified fixture-repair
input tree `43ac9f5ae25e30f91b45279995ef44ecf01c357e`; its only publication delta
is two Markdown result records. Its only non-Markdown change from the preceding
`feefe83b` publication is the repaired inventory test. The production inventory
tool, native processor, DSP/core inputs, native tests, workflows, profiles and
SDK lock are unchanged across that final publication boundary. The exact earlier
failures and the two scoped repairs are retained below; later success does not
rewrite those results.

### Executed final matrix

| Job | Job ID | Actual executed result | CTest wall time |
| --- | --- | --- | --- |
| Core Linux | 131883228381 | 71/71; 549 Python methods | 57.00 s |
| Core macOS | 131883228283 | 71/71; 549 Python methods | 53.76 s |
| Core Windows | 131883228028 | 71/71; 549 Python methods | 69.71 s |
| Core ASan/UBSan/leaks | 131883228687 | 71/71; 549 Python methods | 133.30 s |
| Native Linux | 131883229118 | 8/8; two install Python methods | 6.55 s |
| Native macOS | 131883229476 | 7/7; two install Python methods | 4.47 s |
| Native Windows | 131883229403 | 7/7; two install Python methods | 4.23 s |

Every JUnit file records **zero failed, disabled or skipped tests**, and every
complete last-test record reports its corresponding case passed. Each core job
has **33 Python suite summaries totaling 549 methods**. Successful JUnit output
is truncated: only 357 Python methods are visible in its retained `system-out`.
The 549-method count therefore comes from complete `LastTest.log` files, not from
source counting or truncated JUnit. The native install's two Python methods per
platform are additional focused-native execution, separate from the ordinary
549 methods. Platform-conditional workflow steps skipped by design are not
skipped tests. Linux's eighth native test is its explicitly Linux-only
allocation/interposition audit; that test is not registered on Windows/macOS.

The source manifest in this audited revision is the frozen intermediate snapshot
of 55 complete, three running and two planned assignments. Passing its consistency
suite does not assert that all sixty assignments were complete at this source.
Root owns the later final ledger and its separate sixty-complete validation.

### Real Windows junction and portable cleanup gates

The downloaded Windows diagnostic artifact **14035532898** contains a successful
**20-method inventory suite**, all **71** passing core suites, and the exact
complete-output marker:

```text
reparse probes: root/directory/file metadata and 2 actual Windows junctions
```

The published test increments its success counter only after each actual root
or descendant junction is created, classified as a nonsymlink reparse point,
rejected by inventory, removed without recursive target deletion, and checked
for preserved external sentinel/module bytes. It asserts the counter is two
before printing that marker. This successful suite plus the actual Windows
output closes the junction gate; neither Linux's metadata simulation nor the
older failing Windows marker is used as a substitute. Both macOS alias-path
subcases also now pass in the actual 20-method suite.

All three native logs contain:

```text
native-concurrency cleanup_probe=exception-unwind stop_observed=1 worker_joined=1
```

Each still executes three rates, 24 controlled rounds, 3,072 accepted stress
loads, 3,072 publication-only saves and 96 reader-pause callbacks. The observed
concurrent comparisons are **63,498** audible frames on Linux, **114,076** on
macOS and **94,012** on Windows; each has **6,168** future frames and maximum
error **zero**. These schedule-dependent counts are finite observations, not
real-time deadlines or exhaustive scheduling proofs.

The native controller reports **41,795 checks**, 3,720 threshold cases,
387 string round trips and 306 rejected streams on each platform. Actual ABI
and separately relocated ABI tests each compare **229,725 frames**, maximum
error zero, checksum `af029009868faa04`. Behavior compares **610,510 exact
channel samples**; dense automation compares **179,958 exact channel samples**
against 89,979 reference frames, maximum error zero. These are actual loaded
module/relocation gates, not a DAW, device or physical-instrument qualification.

### Actual tools and retained diagnostic limits

| Platform | Compiler | CMake/CTest | Python | Native runner image |
| --- | --- | --- | --- | --- |
| Linux | GCC 13.3.0 | 3.31.6 | 3.12.16 | `20261111.370.1` |
| macOS ARM64 | AppleClang 17.0.0.17000013 / Xcode 16.4 | 4.4.5 | 3.12.10 | `20261104.0514.1` |
| Windows x64 | MSVC 19.44.35229.0 | 3.31.6 | 3.12.10 | `20261101.353.1` |

The actual sanitizer build contains `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`. Its job retains
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and
`LSAN_OPTIONS=exitcode=23`. Complete executed logs contain no AddressSanitizer,
LeakSanitizer or undefined-behavior runtime report. This covers the executed
instrumented core paths; it is not Python instrumentation or native-module TSAN.

**Every actual SDK validator reports 47 passed and zero failed while retaining
16 “Failed to teardown test!” diagnostics, nine unsupported-rate ERROR messages
and 15 unsupported-float64 informational messages.** Their SDK success summary
does not convert those diagnostics into a warning-free result. Supported
float32 and 44.1/48/96 kHz boundaries remain unchanged.

### Ten actual uploaded artifacts

All ten exact ZIPs below were downloaded through the GitHub Actions artifact
endpoint. Fresh API records match their source workflow, commit, exact byte
length and SHA-256. ZIP member paths, duplicate names, links and size bounds were
checked before safe extraction. The seven diagnostic archives retain actual
source, toolchain, configure, build, CTest, JUnit and complete last-test records;
the three bundle archives each contain the inner tar, inventory and digest.

| Artifact ID | Role | ZIP bytes | API-matched ZIP SHA-256 |
| --- | --- | --- | --- |
| 14035353739 | Core Linux diagnostics | 41,240 | `ff7fcececba89318a67c884f880573c854ba6b112bb39d8d0b11cdacdf426d94` |
| 14035737013 | Core macOS diagnostics | 46,074 | `34c4e42d626a314b0818ae34321d72aa424abc4bc76a1f0258e48f59c4e3c34e` |
| 14035532898 | Core Windows diagnostics | 44,401 | `96ecd39e21ff0e4441f0bfc135c708301c63dc76d765813f7d170ce4137052ee` |
| 14037131008 | Core ASan/UBSan/leaks diagnostics | 41,884 | `c5c75dee92789bbac594d45665b365ed92194adde5cad02e071ceefca084fbae` |
| 14036415355 | Native Linux diagnostics | 40,424 | `e4569733b3bc3a32981241347aa5c392963cf3ea97b8ec269659a57c0b5d373b` |
| 14035283702 | Native Linux bundle | 188,116 | `e7fc1fe7ca070fa1938ccf5d2a8f2326c95ea975fe9f124c78a61a21123df3ff` |
| 14036700890 | Native macOS diagnostics | 49,457 | `ddd22c6698b0664229df6d61cd70167b7c546e05e4fec20c7c8c502989d65e8a` |
| 14036635906 | Native macOS bundle | 155,103 | `ced27fc7e8d77a581b0480fab0bb3bc943729bb1635709d2f7376cb7b8428296` |
| 14037045624 | Native Windows diagnostics | 36,753 | `50273732cf386812956f916b67874fbce2cc084e3e7ad17e70a462987e213614` |
| 14037135615 | Native Windows bundle | 412,875 | `d974c4050cff958e01271d4e0bf33c76c2e908bb4ebc1e987335d64ef34a446d` |

For each native bundle, the staged inventory bytes equal the matching build
inventory; the inner archive matches `archive.sha256`. Independent tar inspection
rejects unexpected or duplicate regular paths, links and special files, then
compares every member's full bytes, size, SHA-256 and permission mode against the
inventory. **All 16 regular payload files across the three bundles match**.
Install/relocation test-reported file hashes also equal the corresponding actual
archive member hashes. The native provenance binds each source commit/tree,
run, attempt, architecture and Release configuration.

| Platform | Bundle / diagnostic artifact | Bundle payload | Native module | Module SHA-256 | Inner archive SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Linux | 14035283702 / 14036415355 | 4 files; 456,767 bytes | 446,696 bytes; ELF64 x86_64 | `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca` | `186a49bb288dd3609e80047112a18641dd1141602b37108ce018a767a3496842` |
| macOS | 14036635906 / 14036700890 | 6 files; 459,870 bytes | 446,096 bytes; Mach-O64 arm64 | `87c2d8b6df18979a5699d5c998059e3842dbeb50a1b76e31c84fadf8e2d12d4e` | `f3184f095e099172972f394849d3e2491916fce20b9a06c794074c8a29d68150` |
| Windows | 14037135615 / 14037045624 | 6 files; 658,568 bytes | 394,240 bytes; PE32+ x86_64 | `005d9b283d43693b24a4a7e5cac1e1bbdf456d96ffcaa7e42455269d93bb8d5f` | `248618e57e484e98cdb91a775f10b810897922804edfbc6dcb2deb9c7df33dab` |

Every native module contains the unchanged **4,545-byte** nominal profile exactly
once, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Artifact SDK lock bytes match the published lock, and each actual SDK verification
record matches all five locked checkouts, five primary licenses and embedded
JSON verification. Bundled notices equal the published notice bytes. Windows
retains the documented SDK-default icon and desktop metadata. macOS includes
Info.plist and CodeResources; the actual build log uses ad-hoc `codesign --sign -`.
That build accommodation is not distributor signing or notarization.

Linux's module bytes equal the earlier hosted module independently loaded by
[assignment 57](PEDAL_HOSTED_RUNTIME_FINAL.md). macOS's module bytes also happen
to equal the immediately preceding source's module. The new Windows module has
a different full-file hash. These observed identities are not a promise of
compiler-independent or reproducible builds. No module from these downloads was
executed locally by this final archive inspection; the named hosted jobs provide
the current execution evidence.

The inventories' source identity remains caller-declared. These checks establish
observed workflow/source/package correspondence and retained byte integrity,
not signed binary-to-source attestation, runtime-library bundling, rights
clearance, measured fidelity or DAW/device qualification. Actions retention is
14 days; these durable hashes identify the critical complete execution records:

| Executed scope | Complete LastTest.log SHA-256 | JUnit SHA-256 |
| --- | --- | --- |
| Core Linux | `d52de5125b63e36adb58856014453ff974fdb0436b813713b995ef66c1fbf260` | `f1ad2ffd281a60d10154ec54cd13e96c816f4d929e1b1bbc9d0bbbcd79fbb6b5` |
| Core macOS | `54b16bf348e0704e2efcdaeade5482effa4006be4e76a3e82aeb71270f228098` | `c3371c7cb7e3ea2806e18edeb01fa7ece4dd76672209daa41392ca282a84d6cd` |
| Core Windows | `dd6e6c90b21598662dfe224cdbc1af6207e8bcd5c080c2d08f2903f795b7d96c` | `e537723afb2ca9851ebb3a7f45091eb03c0e8077ec3368fb6b680853a7ecc947` |
| Core ASan/UBSan/leaks | `d455b7909e15fc8bd3c83ef6b10b65eebc506a6ca7f6f0bbfe0cb96889f4f86a` | `540a05ea098ab4ed7601627150fe7b78e51edf10773d9e2426d2c2a924c23072` |
| Native Linux | `0afb2cdc42d346f3dcd58a86707b4f7bc310e457e61a9655e7e543d3faf32882` | `d5de4f8bed0096f611e42a608cb0679bb3798f609d3dd5fd4bc104f2cb240122` |
| Native macOS | `75336ca0d6a95f7cad32de7fe3b380deb7a8baeae1ac5b640476d911251fa040` | `9f2b5f8e9fbddb8f08b808d9ad9dfaf5906fe02469a52e7fcfc3d8a094306456` |
| Native Windows | `09160f0e15c907e0f760c810f39e9278bf520c78756fb11b96f6500e89c6a93b` | `d20af7e528d3fdf9e7948e6bcd7eb8e30ea9bfb4f6858019bb06b1188a4228d2` |

## Frozen source and local inventory evidence

Independent comparison of every Git blob and executable bit confirms that all
**549 tracked regular files** in the wave-9 source directory match tree
`a8817841a0a348b6b742dfeb6668249aa9692a54`; the directory had no extra files at
inspection. Its exact non-Markdown delta from qualified wave-8 tree
`5370890e32045a556cb61a88cdb1f04fb5a18f7e` is the current-session manifest plus
`tools/native_bundle_inventory.py` and `tests/test_native_bundle_inventory.py`.
Compiled inputs, CMake configuration, data and runtime fixtures are unchanged
across those two trees.

Root's retained focused verbose log and JUnit execute **two CTest suites and
44 Python methods**: 20 inventory methods and 24 session-checker methods. They
pass in **1.62 s**, with zero failed, disabled or skipped tests. The regex also
named nonexistent repository/continuation CTest aliases; those names do not
create two additional executed suites. Root separately recorded three direct
repository/original-console/current-session CLI checks. This reviewer inspected
the focused files and did not relabel them as newly executed local tests.

The inventory tool SHA-256 is
`ee46f979cb3070dcf39d976ab657be974d937f89e835a7927b384dcc755ad4a7`;
its test SHA-256 is
`aa11faf0abdbc9e0ec1bc2ad293f66fc95b249301ccda61db94546076e5e0860`.
Linux's metadata probes cannot establish actual Windows junction execution.
The final Windows core artifact was required to contain the explicit marker
`reparse probes: root/directory/file metadata and 2 actual Windows junctions`.

## Actual wave-8 macOS retry result

Root requested one retry of each previously unacquired macOS job. Both then
acquired actual macOS ARM64 runners at source
`d601eb166ea3206748f8e012b20a463ff365c0b1`, tree
`8af684dfe56f88222c52ff71d85a911ee1192fa1`. These are attempt **2** observations
on [core run 43417681825](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681825)
and [native run 43417681882](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681882).

- Core macOS job **131867709274** passed **71/71** CTest suites in **57.99 s**.
  Its complete LastTest.log contains 33 Python summaries totaling **548 methods**;
  JUnit records zero failed, disabled or skipped tests.
- Native macOS job **131867718865** failed while building the concurrent test
  host. AppleClang reported that `std::stop_token` and `std::jthread` are absent
  from its standard library. The build step exited **2** before native CTest,
  inventory or bundle upload. This was a project portability failure with a real
  runner, distinct from the earlier runner-acquisition cancellation.

The actual macOS tools were CMake/CTest **4.4.5**, AppleClang
**17.0.0.17000013**, Python **3.12.10**, macOS **15.8.2 arm64** and Xcode **16.4**.
Native provenance records image `20261104.0514.1`. A runner label does not freeze
tool versions.

Both actual uploaded ZIPs were downloaded and checked against fresh API byte
lengths and SHA-256 values:

| Artifact | Bytes | ZIP SHA-256 |
| --- | ---: | --- |
| Core macOS diagnostics **14034700785** | 46,007 | `01534164cb303800c5419d29180bada8443927ef34fa7d38f17659c6a727851c` |
| Native macOS failure diagnostics **14034960204** | 36,913 | `ad398d869dccef4cf895ac57725446d10d4fb6bfeec0fa794876fecb8b24a3a4` |

The native diagnostic archive contains the failed build and exact source/tree/
attempt provenance, but no CTest XML or inventory. The core archive contains
the actual complete last-test log, JUnit, toolchain and source record. Full job
logs were also retained. Attempt-2 job metadata gives copied Linux/Windows jobs
new IDs while retaining their earlier execution timestamps and attempt-1
artifacts; those metadata IDs alone do not establish another execution.

## Coordinated test-host repair

After the actual failure was reported, root explicitly extended this worker's
scope to **one C++ test file**: `plugins/vst3/tests/test_native_concurrency.cpp`.
The repair removes reliance on `<stop_token>` and `std::jthread` in favor of a
test-local `JoiningThread` and value `StopToken`. The owner stores an atomic
stop flag before constructing its thread and cannot be copied or moved. Tokens
therefore retain a stable flag address until the worker has joined. A normal
explicit `join()` keeps normal completion behavior; destruction of a joinable
worker stores the stop request with release semantics and joins before the flag
or captured test state can be destroyed. Token reads use acquire semantics.

A bounded exception-unwind probe starts a real worker, throws through the
thread owner's scope, and requires that the worker observed the stop request
and finished before the catch completed. It emits
`native-concurrency cleanup_probe=exception-unwind stop_observed=1 worker_joined=1`.
All existing workload sizes, independent audio comparisons, state oracles,
deadlines, explicit joins and platform registration remain. Production code,
SDK inputs, compiler flags and CMake gates are unchanged.

The frozen repair overlays exactly this one file on the complete wave-9 tree.
Its SHA-256 is
`d261ad69d0199cd5da4a9b2f050a7416b2c515c7838f8f26d3a036c9c8b8f0cc`
(27,431 bytes), Git blob `a9503d93c30a0f4fc75c2f83e3c0586a0f73417f`.
A fresh native configure and dependency build used matching source headers,
the locked external SDK, CMake **3.31.6** and GCC **14.2.0**. The actual repaired
`test_native_concurrency` passed **1/1** in **0.33 s**, with zero failed, disabled
or skipped tests. The cleanup marker was present. The existing workload reported
three rates, 24 controlled rounds, 3,072 accepted stress loads, 3,072
publication-only saves, 96 reader-pause callbacks, **64,207** audible compared
frames, **6,168** future frames and maximum audio error **zero**. Schedule-dependent
counters are observations, not fixed acceptance constants.

This local run proves the Linux repair behavior. The exact hosted results above
provide the subsequent AppleClang build and Windows junction qualification.

A post-build source recheck again verifies all 549 tracked files and executable
bits against that exact one-file overlay. Configure/build generated two extra
Python caches under `tools/__pycache__`, for `validate_factory_reference` and
`validate_pedal_map`. They are retained and separately hashed in
`repair/post-build-source-proof.json`; they are not claimed as tracked source
changes or deleted to hide the distinction. The overlay's Git blob was computed
without writing a Git object. Root's separate integration proof records its
initial missing-object and strict no-extra-files setup stops before binding the
tracked tree explicitly.

## First repaired publication: native pass and fixture failures

The integrated publication **`feefe83be6df8cda8bcfc7f7292fdee9913aa8a1`**, tree
`c5090f0786eb87019c964f45c254b0e30a859088`, binds the preceding repairs to the
actual source. Independent Git comparison confirms that its difference from
qualified repaired tree `81a1c466efdec3efe5c1d9af1e1663eb101dacde` is exactly
five Markdown result files. The previously prepared remote object `17d3992`
was never used to update main.

All seven jobs acquired runners and completed at attempt 1. The actual
[native run 43423372834](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372834)
succeeded on all three platforms. The actual
[core run 43423372813](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43423372813)
failed because two platform runs exposed defects in the new inventory test
fixture. This publication is not a complete matrix pass.

| Executed job | Job ID | Actual result | CTest time |
| --- | --- | --- | ---: |
| Core Linux | 131878608461 | 71/71 passed; 549 Python methods | 55.53 s |
| Core sanitizer | 131878608120 | 71/71 passed; 549 Python methods | 124.34 s |
| Core macOS | 131878608364 | 70/71; inventory suite has two failed synthetic subcases | 62.86 s |
| Core Windows | 131878608488 | 70/71; inventory suite has four failed subcases and one error | 76.76 s |
| Native Linux | 131878608871 | 8/8 passed; archive and both uploads passed | 6.87 s |
| Native macOS | 131878608877 | 7/7 passed; archive and both uploads passed | 5.86 s |
| Native Windows | 131878608531 | 7/7 passed; archive and both uploads passed | 7.32 s |

Every core full last-test log contains 33 Python summaries and **549 attempted
methods**, including the failing suite where applicable. The core failures are
not infrastructure failures or skipped tests. Native logs on all three platforms
contain the actual exception-unwind cleanup marker. The concurrent gate reports
63,453 audible compared frames on Linux, 356,725 on macOS and 90,668 on Windows,
all with 6,168 future frames and maximum error zero. Each native validator
retains 47 passed/zero failed alongside 16 teardown diagnostics, nine unsupported
rate ERROR messages and 15 unsupported-float64 informational messages.

All ten actual uploaded ZIPs from this publication were downloaded and their
fresh API byte lengths/digests checked. Full logs and parsed artifacts remain
under their actual artifact/job IDs in the audit directory. All three native
inner archives, build/staged inventories, provenance, locked SDK bytes and
embedded profile bytes were independently checked. Their observed module hashes
are `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca`
(Linux), `87c2d8b6df18979a5699d5c998059e3842dbeb50a1b76e31c84fadf8e2d12d4e`
(macOS), and `fa10cb8406f151af2ac1b95990945f89b922ec097612b38fd522269a77a07fce`
(Windows). These identities belong to this publication's artifacts.

### Diagnosed inventory fixture defects and qualified correction

The macOS temporary directory contains a filesystem alias; Windows used the
short `RUNNER~1` path. The inventory tool canonicalizes its bundle root, while
the synthetic test attached its metadata tags using uncanonicalized path
comparisons. Thus the root case was reached, but the directory/module tags were
never applied. A controlled Linux temporary parent symlink reproduced the exact
two descendant failures before the correction. This was a test fixture mismatch,
not evidence that actual reparse points were admitted by the production walker.

Windows exposed two additional fixture problems. Passing an entire quoted
`mklink /J` command as one `subprocess.run` list argument produced a command-line
syntax error for both junction creation attempts. A manually constructed
`os.stat_result` used for synthetic FIFO metadata had
`st_file_attributes=None`, causing a TypeError before the intended file-kind
rejection. The denied-symlink fallback used the same incomplete fixture shape.
Furthermore, unittest subtest failures let the old test print the two-junction
marker even though both creation attempts had failed. The failing Windows
suite is not junction acceptance evidence despite containing that text.

The retained failing macOS diagnostic ZIP is **14035083250**, 48,348 bytes,
SHA-256 `362682f9634008d041aa307e8aca5b6d119cd9c6491c2b05eb1b5907e9a5baee`.
The retained failing Windows diagnostic ZIP is **14034644176**, 47,940 bytes,
SHA-256 `cb6dcbe01cf91e3858c87b213d0f46c90b6581567f7ee309f3dc9de743e6880b`.

Root authorized a fixture-only correction in
`tests/test_native_bundle_inventory.py`; the production inventory tool remains
byte-identical. The fixture root is canonicalized, synthetic special-mode
metadata explicitly carries integer attribute word zero, and `cmd /d /c` now
receives `mklink`, `/J`, alias and target as separate arguments. Both original
real-junction cases retain their independent admission and sentinel-preservation
assertions. A success counter increments only after each complete case and must
reach two before the actual-Windows marker can print.

The frozen test SHA-256 is
`0f5e64922be14d4aa0f6565989c0314798549c4f80551d68dbc450fb7f79fa92`
(26,365 bytes). All **20 methods** passed under normal temporary setup in
**0.410115 s** and again through a real temporary-parent symlink in
**0.360312 s**. Two additional one-method executions explicitly exercised the
synthetic FIFO and denied-symlink fallback branches; both passed. These are
reruns of existing methods, not additional registered methods. The pre-repair
negative control and post-repair focused alias probe are retained.

An AST-based inspection evaluated the actual subprocess argument expression for
Windows paths containing spaces and checked its serialized command line. It has
separate correctly quoted path arguments and no nested escaped quotes. This is
command-construction inspection, not local Windows execution. The subsequent successful Windows
suite reported above supplies the actual junction acceptance.

## Retained records and next gate

Task-local evidence is under
`/workspace/scratch/f364bc93d920/a59-final-platform-audit/`: immutable-source
comparison, raw API responses, two downloaded retry artifacts, member hashes,
full job logs, parsed per-test/method records and the `repair/` overlay/configure/
build/execution receipts. The focused repair CTest log SHA-256 is
`2f79b1776352afd1eed619cb2d43848eb8df101c4f6ac2a2ee2c6b5ca123c9ab`;
JUnit SHA-256 is
`2dccfe00910d959cd6c3488d1cbf2fd7f413791b20e08d0f095a088d41419c9f`.

The final inspection now binds the exact published commit/tree to all seven
executed jobs and ten downloaded artifacts. `0ad7240-final-audit.json` records
all consolidating assertions; the individual API, ZIP, file, JUnit and full-log
receipts retain the underlying observations. This reviewer owns only the two
reports and the two explicitly coordinated test-file repairs. Root owns final
assignment acceptance, final metadata validation and expected-head publication.
Later documentation/ledger changes must retain an explicit source delta and
validate their affected checks; they do not silently inherit an identical Git
revision. Hardware/DAW behavior, signing, rights, callback deadlines and measured
instrument fidelity remain separate gates.

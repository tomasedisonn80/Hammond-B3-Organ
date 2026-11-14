# Hosted replay/package recheck and installation-fixture portability

## Result and exact source

Assignment **49**, `/root/cal_w9_a49`, logical wave **9**, independently reviewed
all ten completed hosted jobs for published commit
`3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf`, tree
`656c5f117060210b3df656c62318d5a672fc306d`. At the dated observation,
**nine jobs succeeded and Windows Release failed one of 103 CTest suites**.
The earlier Windows demo symlink-preservation failure is resolved at this source:
the downloaded diagnostic artifact records all **43 demo methods passing with
no skips**. Complete report replay also passed on every core platform.

The new Windows failure is a test fixture's newline assumption during an
intentional late installation abort. Root's later test-only repair passes its
independent focused local check and root's full installation suite. **A repaired
native Windows result remains pending** in this review. The original failure is
retained; neither local acceptance nor nine successful neighboring jobs changes
that failed hosted result.

All three workflow runs are attempt 1, triggered by the same push at
2026-11-14 00:36:44 UTC. The metadata observation was
**2026-11-14 00:48:20 UTC**, after every job completed. Each run's `head_sha`,
the fetched commit/tree object, every complete decoded job log and the embedded
revision in all four downloaded core diagnostic ZIPs agree on the source above.
The [assignment note](../development/2026-11-13-calibration/49-hosted-package.md)
retains exact log/artifact identities, commands, test selection and the local
fixture evidence.

This source includes replay, the 57-file CaptureTools package, and the stronger
observed-link/stat preservation fixture merged from `6214032`. It excludes the
later metadata allocation edit, new graph/metadata/CLI pipeline suites and
stdout/stderr delivery repair. Those changes require their own coherent gates.

## Completed job matrix

Elapsed values are the actual CTest totals, not end-to-end workflow duration,
performance thresholds or comparisons between runner speeds.

| Workflow / platform | Job ID | Completed result | CTest total |
| --- | ---: | --- | ---: |
| [CI](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351721), Linux GCC Release | 132262885564 | 103/103 passed | 63.44 s |
| CI, macOS AppleClang Release | 132262885892 | 103/103 passed | 98.24 s |
| CI, Windows MSVC Release | 132262885865 | **102/103 passed; capture installation failed** | 192.17 s |
| CI, Linux GCC ASan + UBSan + leaks | 132262886012 | 103/103 passed | 212.61 s |
| [Native standalone](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351733), Linux GCC | 132262885976 | 14/14 passed | 76.41 s |
| Native standalone, macOS AppleClang | 132262886173 | 14/14 passed | 84.55 s |
| Native standalone, Windows MSVC x64 | 132262885949 | 14/14 passed | 93.46 s |
| [Native VST3](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351667), Linux GCC | 132262885570 | 8/8 passed | 4.91 s |
| Native VST3, macOS AppleClang | 132262885153 | 7/7 passed | 5.76 s |
| Native VST3, Windows MSVC x64 | 132262885553 | 7/7 passed | 7.11 s |

The general CI selection is unfiltered and contains 103 registered suites.
Native standalone explicitly selects `^test_standalone_`; native VST3 selects
`^(hammond_vst3_validator|test_native_)`. Their smaller selections are not full
103-suite runs. CTest entries, unittest methods and nested SDK validator cases
are different units and are not added together as independent coverage.
Platform-specific workflow setup steps marked skipped are not skipped tests.

## Actual replay, demo and package execution

The ordinary job logs suppress successful unittest output. To resolve the prior
symlink-method question without guessing from a green suite, this assignment
also downloaded the four real diagnostic artifacts, checked each ZIP against
its GitHub-reported SHA-256 and size, verified its embedded source revision, and
inspected `LastTest.log`. The following are their actual nested unittest results:

| Core configuration | Demo | Complete report replay | CaptureTools installation |
| --- | --- | --- | --- |
| Linux Release | 43 methods, OK, no skips | 69 methods, OK, no skips | 16 methods, OK, no skips |
| macOS Release | 43 methods, OK, no skips | 69 methods, OK, no skips | 16 methods, OK, no skips |
| Windows Release | **43 methods, OK, no skips** | 69 methods, OK, one skip | 16 methods, one failure and one skip |
| Linux sanitizers | 43 methods, OK, no skips | 69 methods, OK, no skips | 16 methods, OK, no skips |

The Windows demo output is `Ran 43 tests in 3.605s` followed by `OK`, with 43
dots and no skip indicator. The exact source contains the repaired
`test_existing_dangling_symlink_is_preserved`; its optional native capability
path did not skip. This is observed Windows execution of the repair, not merely
source inspection or a local simulation. The earlier
[955fc4c hosted failure](CALIBRATION_HOSTED_RECHECK.md) remains historical evidence.

Other capture-related skip counters are also retained. Linux Release and Linux
sanitizers each report one audio-admission skip. macOS reports one
audio-admission skip and one job skip. Windows reports common JSON/publication
two, audio admission five, corpus admission six, job two, replay one, study one
and installation one. These are the counters emitted by unittest, which can
include capability-dependent subcases. They do not justify a claim that every
platform-dependent method body ran. Windows installation's one unconditional
platform skip is the POSIX-only `DESTDIR` case. The complete per-suite table is
in the assignment note. This hosted observation is separate from the local
Linux environment's earlier two audio capability skips.

## Original Windows installation failure

Windows job `132262885865` ran `python_test_capture_install` and failed
`test_late_install_abort_preserves_partial_package` at the original line 513:

```text
AssertionError: b'preserve other writer\r\n' != b'preserve other writer\n'
Ran 16 tests in 37.421s
FAILED (failures=1, skipped=1)
```

The fixture modifies only its private generated install script, inserting a
foreign marker write and deliberate CMake fatal error after the first real
CaptureTools file copy. The original injection used `file(WRITE ... "...\n")`
and then expected LF bytes. The observed Windows CMake write produced CRLF.
Before the failed assertion, the test verified a nonzero install exit, the
reached-abort diagnostic and the disclosed partial-install warning. The later
retained-package inventory assertions were **not reached in that failed method**;
this record does not promote them to Windows passes.

No installer production defect is demonstrated by this difference. A foreign
writer's text newline spelling was being mistaken for the package's preservation
obligation. The source installer is unchanged, SHA-256
`b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015`.
The original test was 34,023 bytes, SHA-256
`a797443fe7d208bbdaebedae836edca988524d8371938dd95e9368738f26bb74`.

The independently fetched completed Windows job log is 267,078 UTF-8 bytes,
SHA-256 `58b41c56153eff93e5c4c031043e249efd9d2d5520a4bb677405dd1797a712f0`.
It includes post-job orphan-process cleanup and is byte-identical to root's earlier
capture. That earlier capture was therefore already complete even though the
then-observed job metadata lagged. The actual Windows diagnostic ZIP is 58,215
bytes, SHA-256 `6f54a4b2842b32b17b7a3eb6378266354d2713f3ad7ef5bee9228bec4ecd5497`.
Its `LastTest.log` is 147,264 bytes, SHA-256
`f84d4ba363e5f68a1dd053b22de4bc64d28ba90697ef7fd19e23a27c18d685b2`.

## Later root repair and independent local focus

Root's test-only commit is `c352d684e636b370edcdbbf0249a884623cbbfb1`, tree
`1ce57555f10fc533b5d303e9e53c5631ca1d2090`. It prepares a literal private byte
payload containing CRLF, NUL and LF, then inserts `file(COPY_FILE ...)` to place
that exact foreign marker after the first real copy. The assertion compares the
retained marker to those literal bytes. Existing reached-error, partial-warning,
retained-file count and copied-byte assertions remain. No production installer,
resource cap, threshold, output newline contract or package inventory changed.
CMake `COPY_FILE` is within the existing 3.21 minimum.

The repaired test is 34,298 bytes, SHA-256
`c7731f8bbcec56ed65243bb483cf59031048d978ebd0b9a7582ea6a429ea3602`.
Assignment 49 checked its diff and ran the single affected test from root's
immutable `c352d68` archive, not the live checkout being edited by other workers:

```sh
HAMMOND_TEST_CMAKE=/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake python3 -B /workspace/scratch/c9f3ead4c910/w8-install-fixture-source/tests/test_capture_install.py CaptureInstallAcceptance.test_late_install_abort_preserves_partial_package -v
```

It passed **1/1 in 0.870 seconds, no skips**, under CPython 3.12.14 and CMake
4.4.4 on Linux x86_64. Thirteen identified inputs—the ten capture modules, test,
installer helper and CMakeLists—matched that commit before execution and remained
unchanged afterward. This independently exercises the actual late abort and
preserved literal binary marker. It is not a simulated or actual Windows pass.

Root separately ran all **16/16 installation methods in 6.133 seconds** from the
same immutable archive. This reviewer verified the retained log's 115 bytes and
SHA-256 `87b2615ab5ffb33a7193d35a2dad101617eb0b271186f10ac60b27c60162f9b9`;
it did not relabel root's execution as its own. The one-case independent log is
240 bytes, SHA-256
`1fb877231483ea0c6e3feb281d7bcffbd3fb77f2f4209dadc32f560867409b5b`.

## Native and toolchain scope

The three standalone logs retain successful actual native build, fourteen-test
selection, nine-file package inventory, relocation, help, SDL dummy/software
smoke and archive checks. Windows explicitly skips its unsupported FIFO
subcase in replay-boundary acceptance. These are native software observations;
the reviewed logs do not establish a physical audio device, hotplug experiment,
all real-time deadlines, manual accessibility, listening equivalence or a
finished product. No native package was downloaded or executed by assignment 49.

VST3's seven common entries are installation, the actual SDK validator,
controller, ABI, behavior, automation and concurrency. Linux additionally runs
`test_native_realtime`; its absence on Windows/macOS is a configuration boundary,
not an executed pass there. Each SDK validator reports 47 internal cases within
its one CTest entry. Successful bundle inventory/archive/upload steps are
observed, without claiming a DAW qualification or a newly inspected download.

| Hosted platform | Observed compiler | CMake | Python |
| --- | --- | --- | --- |
| Ubuntu 24.04 x86_64, Linux 7.0.0-1014-aws | GNU 13.3.0 | 3.31.6 | 3.12.16 |
| Windows Server 2022 AMD64, 10.0.20348 | MSVC 19.44.35230.0 | 3.31.6 | 3.12.10 |
| macOS 15.8.2 arm64 | AppleClang 17.0.0.17000013 | 4.4.5 | 3.12.10 |

The Linux sanitizer job configures ASan and UBSan with leak detection enabled
and leak exit code 23. Its 103-suite run succeeds and its retained log contains
no AddressSanitizer, UndefinedBehaviorSanitizer runtime-error or LeakSanitizer
failure diagnostic. This observation does not assert instrumentation of every
external library or qualify unexecuted workloads.

## Integration handoff

Update current status/handoff to point to this dated completed matrix: the
previous demo failure has actual Windows resolution, while the new installation
fixture failure and later repair remain distinct. Publish the accepted fixture
repair with the next coherent source and inspect its real Windows result. Later
allocation, graph and CLI delivery changes need source-specific qualification;
this older green/failed matrix cannot cover their changed bytes.

Keep the original failures, the fourteen-day hosted artifact identities, and
explicit skip/platform boundaries. This assignment downloaded diagnostic ZIPs
only, performed read-only Git/API inspection, and wrote only its two owned
review/note files. It did not change production, tests, workflows, shared status,
ledger, Git refs, or run/cancel/retry any hosted workflow. Root owns integration,
acceptance, publication and the actual remaining agent accounting.

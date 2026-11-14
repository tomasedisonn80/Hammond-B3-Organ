# Hosted calibration recheck at 955fc4c

## Result and exact source

**Nine of ten hosted jobs succeeded. Windows Release failed one newly added
preservation-test assertion; the other 100 registered suites passed.** All ten
jobs are completed at the final observation, **2026-11-14 00:14:39 UTC**. There
are no queued or running jobs in this retained observation. The overall CI
workflow remains failed; the native standalone and VST3 workflows succeeded.

The checked source is commit
[`955fc4c41f74ada094f14fbaf386c943811e9050`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/955fc4c41f74ada094f14fbaf386c943811e9050),
tree `70956d0f0e125d57abfbf1aed56460c067f8ef28`. This independent assignment
inspected that committed source with `git show`, the actual workflow metadata
and all ten complete decoded job logs. Each log identifies that checkout.
The three workflows were triggered by the push, all on **attempt 1**. This
review did not dispatch or retry any workflow.

This source includes accepted study/demo work and the earlier portability
repairs. It does **not** contain `verify_capture_report.py`,
`InstallCaptureTools.cmake`, or their replay/install acceptance suites. Those
later live files must receive their own source-qualified gates.

## Completed matrix

All completion times below are UTC on 2026-11-14. Durations are the CTest totals
printed by each actual log, not complete job durations. Counts are registered
CTest suites, not individual unittest methods or a claim of zero capability skips.

| Workflow / job | Actual job | Conclusion | Executed CTest result | Seconds | Completed UTC |
| --- | --- | --- | --- | ---: | --- |
| CI / Linux GCC ASan + UBSan + leaks | [132250925481](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758072/job/132250925481) | success | 101/101 | 122.80 | 00:08:19 |
| CI / Release (Windows MSVC) | [132250925824](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758072/job/132250925824) | failure | 100/101; demo suite failed | 163.15 | 00:10:29 |
| CI / Release (Linux GCC) | [132250925862](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758072/job/132250925862) | success | 101/101 | 77.59 | 00:07:32 |
| CI / Release (macOS AppleClang) | [132250925888](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758072/job/132250925888) | success | 101/101 | 87.51 | 00:12:37 |
| Native standalone / Native standalone (macOS AppleClang) | [132250925816](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758095/job/132250925816) | success | 14/14 | 68.27 | 00:12:54 |
| Native standalone / Native standalone (Linux GCC) | [132250926224](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758095/job/132250926224) | success | 14/14 | 62.46 | 00:08:12 |
| Native standalone / Native standalone (Windows MSVC x64) | [132250926292](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758095/job/132250926292) | success | 14/14 | 75.65 | 00:08:42 |
| Native VST3 / Native VST3 (Windows MSVC x64) | [132250926013](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758175/job/132250926013) | success | 7/7 | 8.04 | 00:07:38 |
| Native VST3 / Native VST3 (macOS AppleClang) | [132250926389](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758175/job/132250926389) | success | 7/7 | 4.23 | 00:11:31 |
| Native VST3 / Native VST3 (Linux GCC) | [132250926449](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758175/job/132250926449) | success | 8/8 | 6.68 | 00:06:27 |

Run records:
[CI 43531758072](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758072),
[native standalone 43531758095](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758095),
[native VST3 43531758175](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758175).

The early observation found macOS queued; the next found it running from
00:09:51–52 UTC. Subsequent actual completion and log retrieval, rather than an
assumed runner acquisition or elapsed wait, closed those pending observations.

## What the workflows executed

The exact committed workflow definitions were read in full. The general CI
Release matrix builds the SDK-free configuration and runs every registered test
with `--no-tests=error`; the sanitizer job builds Debug with address/undefined
sanitizers and runs the same full set. Its actual environment retains
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and `LSAN_OPTIONS=exitcode=23`.
The source's 101-suite registration is the earlier 99-suite combination plus
study and demo. This fresh hosted 101-suite execution is distinct from the
[local 99-suite gate](CALIBRATION_WAVE5_INTEGRATION.md) and the subsequent
[16-suite focused gate](CALIBRATION_STUDY_DEMO_INTEGRATION.md).

The native standalone workflow explicitly acquires/verifies locked SDL2, builds
its native acceptance inputs, checks required compiled native and dummy backends,
and runs the 14 `test_standalone_` suites under explicit dummy audio/video drivers.
It then verifies unchanged source/dependency state, stages the nine-file
standalone component, relocates it, executes help and an actual 600 ms dummy
smoke, and verifies the archive against the retained inventory. The completed
logs show that package verification and successful diagnostic/package uploads.
This reviewer did not download those archives or independently replay them.
This is the nine-file **Standalone** package, not the later 57-file CaptureTools.

The native VST3 workflow acquires/verifies the locked SDK, builds the actual
bundle and acceptance inputs, and executes the validator plus native installation,
controller, ABI, behavior, automation and concurrency suites. Linux additionally
executes `test_native_realtime`, explaining its eight suites versus seven on
Windows and macOS. Each validator output reports 47 tests passed and zero failed;
that is a nested validator count, not 47 additional CTest suites. Logs also show
bundle inventory/archive and diagnostic uploads. No arbitrary DAW matrix or
physical-device qualification follows from those configured tests.

| Runner family | Actual C++ identity | CMake | Python |
| --- | --- | --- | --- |
| Ubuntu 24.04 x64 | GNU 13.3.0 | 3.31.6 | 3.12.16 |
| Windows Server 2022 x64 | MSVC 19.44.35230.0 | 3.31.6 | 3.12.10 |
| macOS 15 arm64 | AppleClang 17.0.0.17000013 | 4.4.5 | 3.12.10 |

The core workflow uses nonverbose CTest output for passing suites, so its fetched
job logs do not expose every unittest capability skip. No skip-free method claim
is made. Native workflows use verbose CTest: the Windows standalone replay-boundary
suite explicitly skips its FIFO subcase because that platform cannot create it;
its other retained cases and the suite pass. Compiler detection's ordinary
“working compiler — skipped” message is not a skipped acceptance test.

## Earlier failures: observed resolution at this source

The [original hosted follow-up](CALIBRATION_HOSTED_PORTABILITY.md) remains the
authority for the actual failed `779fb6e` runs, initial counterexamples and root's
repairs. Those failures are not erased by this later result.

| Earlier failure | Source change inspected | New native observation at 955fc4c |
| --- | --- | --- |
| Windows canonical output translated LF to CRLF; corpus Unicode diagnostics depended on terminal encoding | Audio/corpus real streams now emit explicit UTF-8 bytes through their binary buffer, check write length and flush; text-only streams retain equivalent Unicode behavior. Numerical/parser definitions remain unchanged. | Windows audio, corpus and both admission suites pass. Their canonical-byte expectations were not relaxed. |
| macOS `/var` and Windows short-TEMP fixture hooks missed canonical descendant paths; one identity hook changed only one side | Temporary fixture roots are resolved before hook targeting, and reached-hook assertions cover path/descriptor/reparse observations. The same-size mutation explicitly advances and verifies its timestamp. | Both admission suites pass on macOS and Windows. This verifies those repaired native cases within their suite scope, not a hostile-filesystem guarantee. |
| Linux standalone reader was required to catch an incidental activity flag | The separately owned repair requires exact initial/final publication acknowledgments and retains activity observations separately. One controlled after-callback overflow supplements fifteen race rounds. | Linux general Release and sanitizer concurrency suites pass; all three native standalone concurrency suites also pass. |

New job/readiness fixtures use the same canonical-root precaution. At this
source, audio, corpus, admission, job, readiness, numerical, policy and study
suites pass on all three general Release platforms. The remaining Windows
failure is the distinct demo fixture described next.

## New Windows failure and retained repair boundary

[Windows Release job 132250925824](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43531758072/job/132250925824)
ran the demo's 43 methods in 3.336 seconds. One failed:
`DemoAcceptance.test_existing_dangling_symlink_is_preserved`, at source line 471.
The failed assertion was:

```python
self.assertEqual(path.readlink(), missing)
```

The actual returned target is a `WindowsPath` beginning `//?/C:/Users/...`,
whereas the fixture's requested absolute target begins `C:/Users/...`.
The preceding expected `DemoError` and `path.is_symlink()` assertion completed;
the comparison of two target spellings failed. The absence assertion after that
line was not reached in this particular hosted case and is not credited as run.
This log does not demonstrate a generator overwrite or altered target. It exposes
an assumption that native `readlink()` preserves the requested path spelling.

The frozen generator is SHA-256
`d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204`.
The hosted test file is
`c2928c63f8ad11ad550d8aacec84643d82925a6bb8e96085417520ddee3343df`.
The original complete failed log is retained locally as
`/workspace/scratch/c9f3ead4c910/a39-hosted/955-windows-release.log`;
its public job URL and exact counterexample above preserve the durable finding.

After receiving this finding, root changed only the preservation fixture:
capture `original_target = path.readlink()` immediately after native symlink
creation, then require that exact observed target after rejected generation.
The existing `is_symlink()` and absent-target assertions remain. This compares
the operation's effect against an independent before-observation; it neither
normalizes away a target change nor derives the expected value from the producer.
This reviewer inspected the exact three-line diff and verified the repaired file:
**38,714 bytes**, SHA-256
`2ebc86c18997da96b4d70894ca193949d77de7ade68655e4ae4cfcad2ef0904d`.

Root reported its actual 43-method local pass in 1.223 seconds and a focused
native-spelling mechanism probe: the original fixture fails after one readlink;
the repaired fixture passes with two reached readlinks and the same actual
native target, zero errors/skips. Those executions belong to root, not this
reviewer's test count. They are local mechanism evidence, **not a repaired
Windows run**. No production code or synthetic threshold changed. The `955fc4c`
Windows job and overall CI conclusion remain failed in this report.

## Next observation and claim limits

Root should retain the original failing source/log, integrate the isolated
fixture repair with a coherent next checkpoint, publish under the standing
expected-head guard, and observe its actual Windows Release result. The new
replay/installation source also needs its own native and combined-source evidence;
the completed `955fc4c` runs cannot qualify files absent from that tree.

There was no local compiler/build/test execution by this assignment and no
workflow retry, native device use, artifact download or code change. Source
inspection and logs are the evidence here. Full maximum workloads, scheduling
deadlines, every DAW/device, native accessibility, rights clearance, physical
acquisition/calibration, holdout chronology and instrument fidelity remain
separate gates. Atlas pp. 484–486 explicitly require those scopes to stay separate.

## Exact inspected source identities

All identities below are from `git show 955fc4c:<path>`, not concurrent live files.

| File | SHA-256 |
| --- | --- |
| `tools/capture_audio.py` | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_corpus.py` | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `tools/make_capture_demo.py` | `d6006b6856ad484f5936e56786aeb5013c148c91fa49e373913ef1bb5484d204` |
| `tests/test_capture_audio_admission.py` | `871d5c71e8aa57d8e6f6daca14bbd2e0a3d09bf913e4468aaa197b4155faabf7` |
| `tests/test_capture_corpus_admission.py` | `97fbb2a153bef2ed5fe67992f7fe9a0f5cafa238619e7ab99d4e84e87ce8c7a4` |
| `tests/test_capture_demo.py` | `c2928c63f8ad11ad550d8aacec84643d82925a6bb8e96085417520ddee3343df` |
| `apps/standalone/tests/test_standalone_concurrency.cpp` | `a309882bb248add7d2dc1e6bbec679482d66d162c2d1eb54b4c455d5194355e3` |
| `.github/workflows/ci.yml` | `4835cbd72231c81c082c6545bde58e1514843626ffe4c9b88078c380f79dc87e` |
| `.github/workflows/native-vst3.yml` | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `.github/workflows/standalone.yml` | `b7f8c70ff9a4ee38d36427999efdbfd39b8c6a06a2e4921c5196e3b8604b5eba` |

## Retained decoded-log identities

All ten complete job logs were retrieved through the dedicated decoded-log
operation and saved in the scratch observation directory above. The hashes below
identify their UTF-8 encoded decoded text, preserving returned line endings;
they are not artifact-ZIP or native-binary hashes. The permanent review retains
URLs, exact outcomes and the failure even if the local scratch copies expire.

| Job ID | UTF-8 bytes | SHA-256 |
| --- | ---: | --- |
| 132250925481 | 221,134 | `1660718a459e299f95eba2d8e766403d56274126af66a4d895e1dff8fbe0c182` |
| 132250925816 | 534,578 | `6174785c0509f4a83acd3b4bbf18d0368c405d880bcf40a05de4ab4ef5c6b77e` |
| 132250925862 | 213,367 | `da01b4995d56e7dcc342e509dcf85b1738d04b3f528043fb589fc6b22ee62522` |
| 132250925888 | 193,647 | `c1bb45d243764c9a039e49814ff52b97075aace232fb5b156df895c8fb7a8c98` |
| 132250926013 | 194,514 | `3413b314b0bb9d6d9f9f314f3cc329bdc802288e4da90dbffeae5618d8f7afd0` |
| 132250926224 | 546,770 | `52045230586cd95ffbfed56ec9211ad6505b51b7b3e09beb890628ba08e9a73f` |
| 132250926292 | 243,697 | `0d7e84c114ca0ea990f54dc167e838fdbead3cd853c80ecede85c34c95083004` |
| 132250926389 | 288,313 | `28241893cb18e136e95570774680e9da9f17804d34ce185e4d502448a3154ac2` |
| 132250926449 | 283,224 | `5c4b8dee10810d2def9032e11891c2d7dfb1d078e8ccbe593b0719a8a9e17c9e` |
| 132250925824 | 264,378 | `4f8bee84cdc42e003fb6735a0ec1b763544945d640c7253e932c348989e6a190` |

# Windows MSVC hosted product review

## Result and exact scope

**Both requested Windows jobs passed at `d8c39f7986746eacc991747153c7dbb012bb9a32`.**
A50 independently inspected their decoded primary logs, the completed job steps
and the matching source. The reviewed tree is
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`, parent
`d556da017ea0a5d4f2d231416782dbc5066e58c2`; GitHub commit metadata and local Git
objects agree. These are results for this exact source, before the subsequent
A46/A48 changes. Audit snapshot: **15 November 2026, 02:43 UTC**.

| Required job | Primary observed result |
| --- | --- |
| [CI 43668397337 / Windows Release 132672791932](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397337/job/132672791932) | **155/155 CTest passed in 191.07 s**. `python_test_crossover_install` passed in **8.94 s**. Job completed successfully at 02:40:19 UTC. |
| [Standalone 43668397338 / Windows MSVC x64 MIDI ON 132672792088](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/job/132672792088) | **48 discovered / 48 passed in 309.16 s**. Source/dependency rechecks, installed-payload relocation, smoke, archive verification and both artifact uploads succeeded. Job completed at 02:41:43 UTC. |

The [machine-readable audit](../development/2026-11-15-product-continuation/reports/A50-windows-hosted.json)
retains all six current/historical job IDs, URLs, full decoded-log identities,
sixteen exact source-file hashes and parsed primary metrics.
[Bounded primary excerpts](../development/2026-11-15-product-continuation/reports/A50-windows-primary-excerpts.txt)
preserve timestamps and original line numbers. Complete decoded logs were fetched and searched
in memory; these selected excerpts are not complete raw artifact downloads.

## Toolchain and executed configuration

Both jobs used **Windows Server 2022 Datacenter 10.0.20348**, runner image
**20261112.366.7**, **Visual Studio 17 2022 x64**, **MSVC 19.44.35230.0**,
**MSBuild 17.14.60+43b635718**, Windows SDK **10.0.26100.0**,
**CMake/CTest 3.31.6** and **Python 3.12.10**. The logged checkout is the exact
d8 commit in both jobs. Configuration/build logs establish **Release**.

Core used the Release preset with native standalone, VST3 and sanitizers
disabled by their inspected defaults. Its actual command was
`ctest --preset release --parallel 2 --timeout 300 --no-tests=error`,
with a JUnit output path. Native explicitly enabled standalone and MIDI,
disabled VST3, built the application plus every standalone acceptance input,
then discovered the selected tests before
`ctest --test-dir build-standalone -C Release -V --parallel 1 --no-tests=error --timeout 180 -R '^test_standalone_'`.

Native acquired and verified SDL **2.32.10** at
`5d249570393f7a37e037abf22cd6012a4cc56a71` and RtMidi **6.0.0** at
`1e5b49925aa60065db52de44c366d446a902547b`. It compiled the prepared static
**WinMM** backend. The successful compiler/backend verification step required
Windows video and WASAPI macros; source and dependency checks repeated after
acceptance. These establish compiled availability. Automated native acceptance
used **dummy audio/video**; the material fixture used a software surface without
window or audio initialization.

## Windows repair evidence

The source-bound repair is narrow. In
`calibration_lifecycle_driver.cpp`, each `SDL_getenv` result is immediately
copied into a separate `std::string`, before the next environment read or
application startup. The inspected pinned SDL Windows implementation returns
reusable `SDL_envmem`; retaining both old raw pointers could overwrite the
selected scenario and trace path. The repaired file SHA-256 is
`e33b17f3f9642d17e21e5d645f8f3d82a176ca030b78164521af2e530ce57dd6`.

The d8 primary native log records **nine methods passed in 20.396 s**,
**ten subprocesses, seven native lifecycles and two deliberately failed
replays**; its CTest gate passed in **20.51 s**. All nine named methods print
`ok`. The two replay failures are expected assertions within this successful
fixture. Probe SHA-256:
`097d97a1d756e07c2b93d248bb55bff640547ee93c971a8666912608257b2eb7`.

This exercises the real application/adapter and dummy SDL callbacks with a
substituted synchronous MIDI dependency. It covers declared calibration, port
and route changes, unchanged Apply, no-input Apply, failed reopen, fault
retirement, enumeration and setup refusal. It does not execute physical WinMM
callback races. The source's separate `-municode` addition has no executed
MinGW qualification here.

For CrossoverTools, numeric `while(1)` replaces policy-sensitive
`while(TRUE)` while retaining the destination-ancestor checks.
The Windows test normalizes only stdout CRLF pairs before the existing exact
LF-file comparison; no content or output-safety assertions were relaxed.
The repaired installer gate passes under the same hosted **CMake 3.31.6**
that exposed the original defect. Its POSIX DESTDIR method remains explicitly
skipped on Windows; the successful core console log prints the CTest result,
not a new per-method installer total.

## New material and installed-workflow gates

The d8 material JSON reports **1,293 checks, zero failures and 109 frames** in
a **4.08 s** CTest. It preserves **901** legacy and **170** header assertions
and adds **222** modal checks over **21** frames. The modal record includes
four scenes, 44 control observations, 96 literal glyph regions, eight focused
controls, two invalid and two long-text frames. All **212 resampled pixels**
belong to **38 boundary-crossing glyphs**; unexplained pixels and literal
mismatches are both **zero**. This is the expanded A42 fixture, with its
[original failures and final oracle](../development/2026-11-15-product-continuation/notes/A42-calibration-modal-raster.md)
preserved separately. It is software-raster evidence, not display or literal
whole-reference equality.

The installed gate reports **eight Python methods in 10.490 s** and a
**10.67 s** CTest pass. The emitted actual installed smoke identifies
**20 files, MIDI ON / WinMM**, executable SHA-256
`7a0765fccfa81d786df9974ee3d7696f68e4ebe63c11812888cb4e9caf1d3f2f`,
dummy drivers and zero reported errors. The stage log explicitly installs
`MIDI_EXPRESSION_GUIDE.md`; the later workflow verifies **20 files**,
relocated help, a **600 ms dummy smoke** and the archived bytes.

Source inspection of that successful unfiltered eight-method gate confirms
the private custom-directory case deletes its source/build/dependency copies,
runs the installed 20/100/Inverted guide example, asserts raw CC11 40 becomes
**0.75**, and preserves all package bytes plus four OfflineTools/CrossoverTools
namespace sentinels. These values are inspected assertions covered by the
passing method, not a separate numeric console transcript. The sentinels do
not execute those other components.

The same suite covers a **16-file MIDI-OFF imported-target install-rule
fixture**, with no RtMidi input or SDK lookup. **No separate Windows MIDI-OFF
executable configuration was built or smoke-tested by this matrix.** The actual
Windows package/runtime evidence is the 20-file MIDI-ON case.

The logs record successful [diagnostics artifact 14142823076](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/artifacts/14142823076)
and [package artifact 14143167615](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43668397338/artifacts/14143167615)
uploads. A50 did not download or independently re-extract them; byte-inventory
and archive verification are the executed hosted workflow's evidence.

## Original failures and earlier successes remain separate

A50 independently fetched the four earlier Windows primary job logs as well.

| Exact earlier source | Core Windows | Native Windows |
| --- | --- | --- |
| `b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree `b3b8b68e4c1f8312d46962924b5096f4ea10c4d2` | [132659897861 / run 43664212086](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43664212086/job/132659897861): **154/155**, 259.31 s. Four installer assertion failures, including three CMP0012/preflight cases and stdout CRLF; one method skipped. | [132659898014 / run 43664212019](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43664212019/job/132659898014): **47/48**, 344.01 s. Eight calibration methods fail during scenario/trace setup. |
| `d556da017ea0a5d4f2d231416782dbc5066e58c2`, tree `a3150fd2489a50a430b02c01eadd5e0c180bc7f9` | [132664951145 / run 43665863633](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43665863633/job/132664951145): **155/155**, 205.40 s; installer 9.43 s. | [132664950665 / run 43665863538](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43665863538/job/132664950665): **48/48**, 364.64 s; calibration 9 methods / 10 processes / 7 lifecycles / 2 intentional failed replays, 21.33 s CTest. |

The d556 native run has the **older 1,071-check / 88-frame material fixture**
and **19-file MIDI-ON package**. It proves the earlier repairs, not A42/A43's
subsequent additions. Its separate Linux native sanitizer build failure remains
in the existing receipt; it is neither a Windows failure nor a successful
expanded sanitizer execution. Original b9 receipts remain unchanged.

## Limits and next gate

This audit qualifies the named **Windows MSVC x64 Release** core/native jobs.
VST3 belongs to A52; Linux/macOS, leaks and later source are separate evidence.
No MinGW, Windows Debug/sanitizer, physical MIDI/audio/display, asynchronous OS
driver race, deadline, native accessibility, DAW, signing or literal 1:1 claim
follows. The nominal dry Engine and unresolved physical-model gates remain.

After the integrator publishes the frozen A46/A48 and eventual closure source,
discover the actual Windows selections and audit its exact new primary logs;
do not transfer d8's counts or execution to a changed tree. Keep the identified
real-device and WinMM fault/lifetime journey as a separate product gate.
A50 performed source/log inspection and wrote only this review, its short note
and bounded reports: no local build/test, production/workflow/shared-status edit,
commit or push.

## Source-specific follow-up: c448 core failure and native success

The later exact source is `c4486bafccbcfbcd9bcd9492e8949ddd44ea1340`, tree
`2d21135e570c5b328a7f54d17582ffc7ac62a489`, parent d8. The new
[source-specific report](../development/2026-11-15-product-continuation/reports/A50-final-source-hosted.json)
and [bounded primary excerpts](../development/2026-11-15-product-continuation/reports/A50-final-source-primary.txt)
retain both outcomes; **this source is not Windows-qualified**.

| Exact c448 Windows job | Primary result |
| --- | --- |
| [Core 132685867528 / CI43672641490](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43672641490/job/132685867528) | **156/157**, 226.65 s. New plot-admission module passes in 0.73 s; product-session module fails in 1.40 s, reporting 19 methods, 111 failure entries and one skip. |
| [Native 132685867505 / Standalone43672641506](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43672641506/job/132685867505) | **48/48**, 367.52 s. Calibration: 9 methods, 10 processes, 7 lifecycles, 2 intentional failed replays; material: 1,293 checks, zero failures, 109 frames; installer: 8 methods and the actual 20-file WinMM payload, guide, relocated dummy smoke and archived-byte verification. |

Both logs identify MSVC 19.44.35230.0, CMake/CTest 3.31.6 and Python 3.12.10.
Native production inputs are unchanged from d8. A nonfatal CMP0010 warning
about the generated installer's Windows Python path remains; the install and
archive gates pass. It differs from the earlier repaired CMP0012 failure.

The new checker compares incompatible Windows path/descriptor `ctime` values.
Exact CPython 3.12.10 source confirms that path queries substitute birth time
while `fstat` can retain change time. The separately authorized
[portability repair evidence](../development/2026-11-15-product-continuation/reports/final-source-windows-portability-repair.json)
preserves full POSIX and same-API signatures, compares compatible Windows
fields at open, and retains A51's canonical temporary-path test repair.
Four focused methods with 30 synthetic cases and all 23 product-session
methods pass locally on Linux. These later edits do not change c448's failed
result. The next gate is primary Windows execution at the newly published
repair source; hardware, real display, MinGW and OS race claims remain outside
this audit. The accepted A50 note and earlier reports remain unchanged.

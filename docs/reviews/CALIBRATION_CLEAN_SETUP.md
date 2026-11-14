# Fresh capture and offline-tool setup

## Result and exact source

Assignment **50**, `/root/cal_w9_a50`, logical wave **9**, independently passed
the documented fresh setup, component co-installation and relocation workflows
from one immutable source. **All 51 recorded setup/runtime commands met their
expected exits and all 15 grouped checks passed on the first actual audit run.**
No flow was skipped and no production or documentation repair was required.
The intentionally nonzero planned, inconclusive, failed and no-clobber outcomes
remain visible; they are not unexpected test failures.

| Source identity | Value |
| --- | --- |
| Local frozen commit | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` |
| Complete Git tree | `3edea0838b75feb06c19e151ec8539e80646fc03` |
| Private source inventory | 1,000 files, 39,738,773 bytes |
| Runtime | CPython 3.12.14, Linux 6.18.57 x86_64, glibc 2.41 |
| Configuration/build tools | CMake 4.4.4, GNU C++ 14.2.0 |

Root supplied the freeze before this assignment copied or configured anything.
The audit used its own `git archive`, source directory, build directory and
compiled outputs; it did not reuse root's concurrently running integration
build. All 1,000 source-file identities were checked unchanged before deleting
that private source. The shared checkout was not removed or modified.

The [assignment note](../development/2026-11-13-calibration/50-clean-setup.md)
retains the exact executable audit, complete 51-command outcome ledger, all
80 installed-file identities, principal output identities and reproduction
instructions. The source commit is a local freeze; the integrator owns its
eventual published equivalent and tree mapping. This review does not infer a
branch update or a hosted result from source-object identity.

## Setup actually exercised

The [capture installation guide](../CAPTURE_TOOLS_INSTALL.md),
[offline installation guide](../OFFLINE_INSTALL.md),
[build prerequisites](../BUILD.md) and
[capture handoff](../CALIBRATION_HANDOFF.md) supplied the command paths and
expected outcomes. Configuration used Release with `BUILD_TESTING=OFF`,
`HAMMOND_BUILD_VST3=OFF`, `HAMMOND_BUILD_STANDALONE=OFF` and an explicitly
selected Python interpreter. No dependency installation, SDK acquisition or
network command was performed.

The actual source, build and prefix names contained both spaces and `café`:

```text
/workspace/scratch/c9f3ead4c910/a50-clean-setup/source café path
/workspace/scratch/c9f3ead4c910/a50-clean-setup/build café path
/workspace/scratch/c9f3ead4c910/a50-clean-setup/initial prefix café
/workspace/scratch/c9f3ead4c910/a50-clean-setup/moved prefix café
```

The successful command forms were:

```sh
cmake -S "<source>" -B "<build>" -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF -DPython3_EXECUTABLE="<python>"
cmake --install "<build>" --config Release --component CaptureTools --prefix "<prefix>"
cmake --build "<build>" --config Release --parallel 2 --target hammond_render hammond_model_info hammond_parameter_info hammond_console_trace hammond_pedal_trace
cmake --install "<build>" --config Release --component OfflineTools --prefix "<prefix>"
```

The first install occurred **before the native build**; the renderer executable
did not yet exist. CaptureTools therefore exercised its declared source-only
installation boundary. Ordinary repository configuration still needed the
available C++ compiler. The later native build compiled the five offline tools
and generated their explicit profile from the same archive. Neither VST3 nor
the SDL standalone application was enabled.

All Python tool invocations used `-B -S` from an unrelated empty working directory.
`PYTHONPATH` was empty, `PYTHONNOUSERSITE=1`, bytecode writes were disabled,
`PYTHONIOENCODING=ascii:strict`, and inherited `HAMMOND_*` variables were removed.
Only explicit installed inputs were supplied after relocation. This checks the
observed standard-library/package closure; it is not a clean operating-system
image, native runtime redistribution or network-isolation claim.

## Exact payloads and preservation

| Installation observation | Files | Bytes | Verification |
| --- | ---: | ---: | --- |
| CaptureTools before any native target build | 57 | 698,919 | Independently typed inventory matches exactly; 56 copied files match original source bytes; generated README identity retained. |
| Co-installed OfflineTools addition | 23 | 581,510 | All five binaries match the fresh build, the compiled profile matches, and the two plot scripts plus fifteen fixture files match source bytes. |
| Combined relocated prefix | 80 | 1,280,429 | Exact union with no symlinks; every file unchanged after all runtime flows. |

The capture inventory remains ten Python modules, eight schema/declaration
files, sixteen original demo files, twenty-one guides and two root files.
The separate OfflineTools inventory remains its five native executables,
compiled profile, two plotters and fifteen fixture files. No inventory was
expanded to support the CLI repair.

Reinstalling CaptureTools into its existing package leaf was intentionally
rejected with exit 1. The full 80-file combined prefix remained unchanged,
including OfflineTools. The test then moved the whole prefix and removed only
its task-owned source, build and pre-move native-data directories. Those paths
and the original prefix were verified absent before installed execution.
This goes beyond merely changing the current working directory.

After runtime checks, all 80 installed files still matched their pre-move
identities and no bytecode cache existed in the installation. A valid job's
attempt to replace its existing report and the generator's attempt to replace
the installed demo both returned exit 1 with empty stdout and retained all
existing bytes. The installer is still the contract's ordinary multi-file copy;
these successful and intentional-rejection flows do not qualify every I/O
failure, race or hostile-filesystem case.

## Capture flows after source and build removal

Ten source commands were repeated with installed scripts and explicit installed
inputs. Expected results were typed from the contracts and literal demo vectors,
not learned by accepting whatever the source command returned.

| Public flow | Expected and observed result |
| --- | --- |
| Validate the supplied plan | Exit 0; structural pass, planned record, no implicit file check. |
| Planned readiness | Exit 3; `planned`, raw-acquisition-only context, unknown claims retained. |
| Recorded synthetic readiness | Exit 3; `declarations_incomplete`, unknown claims retained. |
| Planned corpus | Exit 3; `inconclusive`. |
| Complete demo corpus with files and audio | Exit 0; `pass`, physical fidelity unestablished. |
| Original raw reference audio | Exit 0; one channel, four frames at declared 4 Hz. |
| Passing job | Exit 0; `pass`, literal RMS error 0.25 FS. |
| Inconclusive job | Exit 3; `inconclusive`, literal RMS error 0.25 FS. |
| Failed job | Exit 1; `failed`, literal RMS error 0.5 FS. |
| Mixed three-job study | Exit 1; `failed`, retaining all three complete outcomes and 12 window samples/12 spectral terms. |

Each job and study stdout exactly matched its saved canonical report bytes.
The three jobs and study were also **byte-identical between source and installed
execution** under the same runtime. The complete study retained one pass, one
inconclusive and one failed job, all three validation roles, and all ten unknown
evidence fields at its root and each nested job.

Four additional installed replay commands consumed the **original source-run
saved reports**, with installed input paths after the original source/build had
been deleted. All returned exit 0 and `match`, with exact-report equality,
`same_runtime: true`, `same_tool_sources: true`, and unchanged original report
bytes. Failed and inconclusive engineering statuses remained failed and
inconclusive. Replay success did not become a physical or numerical pass.

The generator and validator were each copied alone into separate directories,
with no sibling modules. Their help and successful work ran through `python -B
-S` from the foreign working directory. The generator recreated the exact
sixteen-file, 32,831-byte archive; its inventory remained `execution: not_run`.
The standalone validator explicitly verified the selected original raw file's
bytes. These flows confirm the preserved standalone dependency guarantees;
the separate CLI acceptance owns the exhaustive closed-pipe failure matrix.

## Existing native offline tools after relocation

All five installed native tools and both installed Python plotters ran after
the private source/build disappeared. Their explicit inputs were the moved
compiled profile and moved fixtures. No source authoring JSON or implicit
`HAMMOND_*` path was supplied.

The original A4 render used 48,000 Hz, 72,000 frames, block size 127, seed 2602,
drawbars `008000000` and `--fail-on-clip`. Independent WAV inspection found
stereo PCM16, exactly 72,000 frames, nonzero samples and identical channels;
the render reported zero clipped frames. Model metadata retained 91 source
slots and an unestablished physical-fidelity claim. Parameter metadata retained
45 mappings and `host_exports_verified: false`.

Console `partial` and pedal `overlap` traces at 48,000 Hz ran through their
respective installed plotters. Each SVG retained the SHA-256 of its original
CSV. The complete WAV, both metadata JSON files, both CSV files and both SVG
files were byte-identical to the corresponding freshly built/source-script
executions before relocation. Their exact identities are retained in the note.
This is same-build, same-machine equivalence, not cross-compiler audio identity.

## Evidence, limitations and next action

The audit script is 21,850 bytes, SHA-256
`3fd0680ab5c6c084db619cd7ca310ef8e919434f8bab73ca28feff5ca1c73417`.
Its 248,270-byte result JSON is SHA-256
`40d7639302df272af393000865123b72fa587df9b697d250faed1d190aa24629`.
The note embeds the exact script and retains the substantive result tables;
scratch logs are supplemental rather than the only description of the gate.
The 51-command count excludes two preliminary Git identity/archive commands
and child compiler/linker processes. Fifteen grouped checks are not fifteen
new unittest methods or CTest entries.

No new defect was found and no shared file, production code, test, build rule,
ledger or Git ref was edited by this assignment. Root should accept the two
owned records, use the successful command forms in the operational runbook,
and publish their exact source mapping with the complete integration evidence.
Changes to installed sources, payload inventory, command contracts or native
inputs require their affected flows again.

This qualifies local offline installation and the exercised Linux runtime.
It does not establish Windows/macOS behavior, other Python versions, a clean OS,
compiler-runtime bundling, actual audio devices/DAWs, callback deadlines,
signing, permissions, acquisition, calibration, protected holdout history or
instrument fidelity. The atlas's source/setup/change-control requirements
(pp. 449, 484, 486) keep these engineering results separate from those later
gates. The six earlier readers retain the complete-PDF reading; this assignment
does not claim another full reading.

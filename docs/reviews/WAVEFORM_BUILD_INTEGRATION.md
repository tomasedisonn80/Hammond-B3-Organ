# Independent waveform build integration review

**Reviewer:** actual A24, `/root/w04_a24_build_integration_review`, 14 November 2026.
**Result:** the reviewed build integration passes the isolated Linux checks below.
The integrator corrected one missing smoke-artifact upload path in each ordinary
CI job before the source freeze. A24 changed only this review, its
[worker note](../development/2026-11-14-waveform-continuation/notes/A24-build-integration.md)
and the [compact result](../development/2026-11-14-waveform-continuation/reports/a24-build-integration.json).
Full R4 execution remains the integrator's separate, ongoing task.

## Source and executed scope

The confirmed base was `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b` plus the
uncommitted waveform overlay. All **82 qualification-source hashes** remained
stable from before configuration through the actual smoke. The compact result
contains those hashes, exact expanded command arguments, generated target facts,
raw-log and receipt identities, and explicit limits. This result qualifies the
recorded worktree bytes, rather than every future state of that Git revision.

| Executed operation | Actual result |
| --- | --- |
| Fresh Release core configuration, `BUILD_TESTING=ON` | Pass, 0.572 seconds |
| Separate fresh Release configuration, `BUILD_TESTING=OFF` | Pass, 0.477 seconds; configure only |
| Build `hammond_rotary_waveform_probe` and its core/generated dependencies | Pass, 11.279 seconds |
| Registered waveform smoke and report-admission CTests | **2/2 pass in 3.47 seconds** |
| Report-admission methods within the second CTest | **9/9 pass** |

Both isolated builds used Ninja, GCC 14.2.0, CMake 4.4.5 and Python 3.12.14.
Standalone, VST3, MIDI and sanitizers were OFF; all three optional SDK root cache
entries were empty. No dependency was acquired. The integrator's native cache,
read without modification, instead has standalone ON and a pinned SDL2 root.
Only the isolated core/probe target was built. Host-independent standalone
support targets remain declared by existing project policy; no SDL application,
VST3 plugin or MIDI backend target entered this build.

## Generated build graph and test registration

All **18 generated-configuration checks** pass, using CMake File API data,
CTest JSON discovery and Ninja's command inspection.

| Requirement | Observed result |
| --- | --- |
| Core and ordinary tests use existing globs | History, renderer and streaming sources enter `hammond_core`; all five new C++ behavior suites are discovered once. Their discovery is not an A24 execution claim. |
| Private renderer storage stays private | Exactly `test_rotary_renderer` and `test_rotary_renderer_transactions` receive `src/`. The core's include interface excludes it. |
| Independent probe is test-only | `hammond_rotary_waveform_probe` lists the oracle header, privately includes `tests/` and links only `hammond_core`. No other target lists that oracle header. |
| Ordinary smoke uses the selected build | CTest resolves the exact probe path and `rotary-waveform/Release/smoke`, with a 120-second test timeout. |
| Admission is separate | Its registered command ends in `--self-test`, with a 30-second timeout; the actual run executes all nine methods. |
| Full gate builds its input | `check_rotary_waveform_full` depends on the probe and invokes `--mode full`, the selected probe, the Release full-report parent and `--timeout-seconds 1500`. |
| Fast `check` remains bounded | It builds the probe without depending on the full target. |
| Testing can be disabled | The OFF configuration omits the waveform probe, full/check targets and all C++ test targets. |

The runner creates a timestamp/UUID directory for each invocation. The actual
smoke's `latest.json` names its completed receipt and matches that receipt's
SHA-256; raw native stdout and stderr remain separate original files.
`PrivateProject` copies both `tests/probes/` and `tests/reference/`. Its existing
CaptureTools payload and all three install helpers are unchanged. This last
finding is source inspection; A24 did not repeat the install suite.

## CI preservation and retention repair

The dedicated `rotary-waveform` job configures Linux GCC Release with standalone
and VST3 OFF, requires admission self-tests and invokes the full build target.
It has a **35-minute job cap**, **30-minute full-step cap**, failure-propagating
pipeline and a 14-day artifact upload of complete waveform run directories,
logs, cache, compile commands and configure diagnostics. The upload runs on
success and failure unless cancelled and treats absent upload inputs as errors.

The initial ordinary Release/sanitizer uploads omitted smoke receipts. A24
reported that concrete defect; the integrator added
`build-release/rotary-waveform/` and `build-sanitizers/rotary-waveform/` before
freezing CI source. Structured comparison against the confirmed HEAD proves
both previous job definitions otherwise unchanged and every old artifact path
preserved. The added full job is unconditional and has no `continue-on-error`;
repository branch-protection settings and hosted execution were not inspected.

## Source binding and numerical boundary

The fresh build records **25 actual core/probe compile commands**, including all
five required rotary core sources and the probe. They use C++20, `-O3 -DNDEBUG`
and the existing complete warning-as-error policy, with no detected unsafe
floating options. Contraction remains the compiler default. Cache, command-file,
executable and source identities match before/after the smoke. Native precision
reports binary64 double and 64-bit-significand long double; build configuration
and flags come from actual CMake metadata because those strings are not embedded
in the native executable. Metadata observation alone is not compilation proof;
A24 separately observed this fresh build complete.

The bounded smoke passed four rates, 24 partitions, 98,328 native frames,
163,880 exact alternate-partition scalar comparisons and 360 consumed events.
All 64 selected Decimal path checks pass. Maximum normalized waveform error is
`1.20659368074701270776e-9` against `2e-5`. The wrapper took 2.940 seconds, its
native child 2.377 seconds; retained files total 302,538 bytes. The complete
33,280-row static grid is admitted from A14's retained evidence, not rerun here.

This review does not execute the ten-second full workload, new C++ behavior
suites, installers, hosted jobs, other compilers or sanitizers. It cannot settle
the provisional full-run timing limits, R5/R6, device deadlines or physical
fidelity. Continue with the integrator's frozen full result and then inspect
the exact published revision's actual CI outcomes and retained receipts.

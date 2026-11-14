# Closing hosted audit at fd2f6060

**All thirteen hosted jobs pass** for commit
fd2f6060b1f03b6d902ff0547441c07d6e74ba4f, tree
89c0fb214b018ca43ec9c8b413d3030284a54ec2, attempt 1.
Actual A60 performed this follow-up under its existing accepted identity; no
additional worker is counted. The [machine-readable receipt](../development/2026-11-14-reference-refinement/reports/root-final-hosted.json)
and [primary extracts](../development/2026-11-14-reference-refinement/reports/A60-final-hosted-primary-excerpts.log)
retain checkout identities, complete result counts, exact decoded-log hashes,
required gates and evidence limits.

## Executed outcomes

| Job | Primary result | Time (seconds) |
| --- | --- | ---: |
| [Release (Windows MSVC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334888/job/132629447684) | 146/146 CTest | 217.92 |
| [Release (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334888/job/132629447834) | 146/146 CTest | 132.11 |
| [Release (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334888/job/132629447843) | 146/146 CTest | 137.08 |
| [Linux GCC ASan + UBSan + leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334888/job/132629447886) | 146/146 CTest | 287.38 |
| [Complete R4 waveform qualification (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334888/job/132629447890) | Full waveform passed; admission 14/14 | 513.538315848 |
| [Native standalone (macOS AppleClang, MIDI ON)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334873/job/132629447729) | 42/42 CTest | 260.43 |
| [Native standalone (Windows MSVC x64, MIDI ON)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334873/job/132629447924) | 42/42 CTest | 296.44 |
| [Native standalone (Linux GCC, MIDI OFF)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334873/job/132629448001) | 42/42 CTest | 261.60 |
| [Native standalone (Linux GCC, MIDI ON)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334873/job/132629448015) | 42/42 CTest | 262.72 |
| [Native standalone (Linux GCC ASan + UBSan + leaks)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334873/job/132629448067) | 16/16 CTest | 158.32 |
| [Native VST3 (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334846/job/132629447596) | 7/7 CTest; SDK validator 47/47 | 3.52 |
| [Native VST3 (Windows MSVC x64)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334846/job/132629447740) | 7/7 CTest; SDK validator 47/47 | 7.48 |
| [Native VST3 (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43654334846/job/132629447870) | 8/8 CTest; SDK validator 47/47 | 6.13 |

Times are CTest wall times except the full waveform row, which is the
runner-reported experiment wall time. The twelve CTest jobs contain 790 passing
test executions. Their complete ordinal sequences and unique test names/IDs
match their summaries. The four core test-name sets agree; the four native
Release sets agree. These counts do not sum nested fixture checks.

The repaired waveform admission gate passes on macOS in 3.55 seconds and Windows
in 5.47 seconds. Native macOS passes the previously failing build and then
waveform material in 6.23 seconds. All four native Release jobs report 1,917
waveform-material checks, zero failures and 55 cases/frames; their
baseline-comparison flag is false. The existing material fixture passes
1,071 = 901 + 170 checks in all five native jobs.
The adopted two-file repair hashes match the published sources. The
[original 487064 failures](../development/2026-11-14-reference-refinement/reports/root-integration487064-original-hosted.json)
remain unchanged observations.

## Strict records and sanitizer scope

Linux executed the actual strict refinement-completion step. Its parsed primary
JSON equals the committed completion record exactly: 60 accepted records,
distinct agents and verified notes, ten accepted waves, zero errors. This
accounting-consistency result is separate from the checker regression test and
does not establish dispatch, substantive acceptance or physical fidelity.

Core and native sanitizer jobs retain leak-enabled ASan, UBSan halt-on-error and
LSan exit code 23. Primary compile lines show selected R2/R3/R4 instrumentation.
Native guard steps verify instrumented project/SDL objects, archives and linked
runtimes, then discover exactly sixteen built interface gates with policy
overrides rejected. The existing core quarantine test alone retains its explicit
leak-disable exception. The additional waveform-material fixture is outside the
native sixteen-test sanitizer selection and passes in the four native Release
jobs. No new exception was introduced.

No captured warning text is new relative to A56's matching job. Existing
warnings remain: Windows core's unused CMAKE_BUILD_TYPE, SDL compatibility and
macOS deprecations, Linux SDK format diagnostics, and native Windows' install
CMP0010 warning for the Python path's invalid backslash-h escape. The installed
payload guard passes; that does not erase the warning. Full bounded Windows
warning context is included in the primary extracts.

## Full waveform and preservation boundary

The complete waveform job's primary output reports full mode, pass, an empty
failure list and 513.538315848 seconds. Its strict report-admission self-tests
pass 14/14. This audit did not rerun the experiment or download/replay its
qualification payload; the retained primary execution result has its own exact
published source identity. Earlier full-run evidence and its frozen-source
limits remain historical records.

All 21 protected evidence files remain byte-identical, including accepted A60
records, A56's audit, original failures and earlier cancellations. All 383 named
product/test/tool inputs match this tested commit and its integrated parent;
workflows are separately pinned. No job was retried or cancelled by this auditor.

Root owns final acceptance and the subsequent record-only publication. Such a
commit must continue to name fd2f6060 as the executed source. R4 remaining
lifecycle/review work, R5 audible policy and R6 runtime/Engine integration remain
separate. Nominal dry Engine, 47 parameters, writer4/readers1–3 and scanner G5's
same-hertz failure remain explicit. Dummy native surfaces, SDK validation and
package guards do not qualify physical devices, DAWs, deadlines, accessibility,
signing or physical fidelity. Literal **1:1 visual equality remains unmet**.

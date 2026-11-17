# Successor Core qualification — d2ed03b9

**All six required Core families pass at published `d2ed03b94114e35d0caa65968d11afe896a5e9f5`, attempt 1.**
This is A56's follow-up to the accepted first-source review, with **no additional
agent credit**. Root retains final acceptance and publication authority.

The [complete receipt](core-d2ed03b9-admission.json) records every exact-source
job, runner, step, timing, log identity and artifact result. The
[Core run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790) is terminal **success**, updated
**2026-11-17T07:07:14Z**. The independently verified tree is `45f3f2bc1bc844061be7d1303b13b10bfaba9938`, with
sole parent `cf87a587d0002d106e5210b57a39fd1967245a8f`.

## Every required family

| Exact-source job | Result | Inspected execution |
| --- | --- | --- |
| [Release (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790/job/133874509282) | Success | 209/209 CTests; 110.22 s |
| [Release (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790/job/133874509419) | Success | 209/209 CTests; 174.26 s |
| [Release (macOS Intel AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790/job/133874509438) | Success | 209/209 CTests; 354.38 s |
| [Release (Windows MSVC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790/job/133874509296) | Success | 209/209 CTests; 333.10 s |
| [Linux GCC ASan + UBSan + leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790/job/133874508983) | Success | 209/209 CTests; 318.89 s |
| [Complete R4 waveform qualification (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656790/job/133874509351) | Success | Full R4 pass; 535.726700540 s; 14-method admission self-test passes |

All five CTest families contain the same 209 unique names. All twelve required
registration/apron gates and all five library suites pass on each platform.
There are no failed, cancelled or retried jobs; every job has an assigned runner.
The initial ARM macOS queue and all subsequent observations remain retained.

## Actual Windows repair execution

The [Windows artifact review](core-d2ed03b9-artifact-14307775125.review.json)
independently reads JUnit and LastTest.log from the exact-source artifact:

| Python suite | Actual methods | Result | Method elapsed time |
| --- | --- | --- | --- |
| Capture standalone interface | 45 | OK, no skips | 4.676 s |
| Header material comparison | 24 | OK, no skips | 1.042 s |
| P1 performance-plate comparison | 54 | OK, no skips | 0.952 s |

These are observed hosted method results. The 54-method Python suite remains
separate from native P1/SDL fixture qualification. The same 45/24/54 methods
also pass in the separately downloaded Linux Release artifact.

The formerly skipped Windows Unicode-checkout generator step now succeeds.
Its retained qualification names this exact commit and tree, records 24 saved
payloads, unchanged source-pack bytes, LF-only generator output, and a
ProtectedPath refusal with zero attempted or committed files. The source root
actually contains non-ASCII characters. This qualifies the scoped MSVC generator
exercise; native UI, SDL, VST3 and devices remain separate.

## Source and numerical boundaries

All five repaired inputs match their frozen, locally qualified Git blobs.
The capture producer, real header comparator, Core workflow, protected
include/src/plugins trees, data, root CMake and presets are unchanged from the
failed predecessor. The 81 protected source files retain the reviewed parameter,
state, shared-source, plugin UUID and dry-Engine boundaries.

Sanitizer logs show actual Engine/library-model/test instrumentation and the
unchanged ASan, UBSan and leak policies. The R4 artifact independently reports
all 16 admission groups passing, exact clean before/after source identity, and
38,010,000 equal samples out of 38,010,000 partition comparisons. Original native
stdout/stderr digests and the latest receipt pointer are verified. Its waveform
scope does not establish transaction lifecycle, device deadlines or physical
instrument fidelity.

The Linux standard-library apron checks pass with their explicit six and two
optional-method skips retained. A passing registered CTest does not imply every
optional method or internal branch ran. No timeout, acceptance threshold or
source was changed during this review.

## Original failure and retained evidence

The original cf87a587 Core run remains **failed: five successes, one Windows
failure, 207/209 Windows CTests and exit 8**. Its skipped generator step remains
skipped in that record. The accepted A56 note, reports and complete original logs
are unchanged; this follow-up does not promote an earlier pass to changed source.
The original console 246/247 local full failure also remains preserved.

Six complete new decoded primary logs are retained losslessly in
**279,709 gzip bytes**, representing
**2,724,737 raw bytes**. Three original artifact ZIPs
(Linux Release, Windows Release and R4) total
**447,060 bytes**; all match their API
SHA-256 digests. Other artifact metadata and successful upload records remain
retained without claiming body review. Full final run/jobs metadata and all
seven bounded polling observations are included.

A56 performed read-only remote collection and local evidence parsing in this
follow-up. No local test/build/native execution, Git/ref/index change, CI retry,
source edit or accepted-note rewrite occurred. All new writes are confined to
this evidence directory. Final session closure and product acceptance belong
to root. **Literal whole-interface 1:1 remains unmet and unwaived.**

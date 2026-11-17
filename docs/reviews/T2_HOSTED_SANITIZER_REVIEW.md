# T2 hosted core sanitizer investigation

A08 follow-up, the same `/root/w02_a08` worker; no new staffing credit. Inspected
published source `6047723b595259de355c74342e48a8ae2ee1e228` through read-only
GitHub job steps, the complete decoded log, run/jobs and exact local Git objects.
No rerun, build, production edit or publication was performed. The original
A08 note and earlier CI observation remain unchanged.

## Exact failure

[Core sanitizer job 133715652514](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43986430633/job/133715652514)
configured and built successfully, then passed the required-test inventory gate.
The failing step was **Run every registered test with leak checking**. CTest
passed **201/202 in 408.26 seconds**, exiting 8. Its only failing registered test
was `python_test_render_controls_admission` (test 149).

Within that five-method Python suite,
`RenderControlsAdmissionTests.test_destination_appearing_after_preflight_is_never_replaced`
raised `subprocess.TimeoutExpired` at `tests/test_render_controls_admission.py:366`:

```python
stdout, stderr = process.communicate(timeout=15)
```

The child command used 1,200,000 frames, 48 kHz, block size 1, seed 191,
ideal contacts, saved controls and the nominal compiled profile. The Python
suite reported one error in 16.900 seconds. The complete decoded job log contains
no `ERROR: AddressSanitizer`, `ERROR: LeakSanitizer`, `runtime error:` or
`AddressSanitizer:DEADLYSIGNAL` matches. This is an observed harness timeout,
not a reported sanitizer violation or a memory-safety acceptance result.

The [retained investigation receipt](../development/2026-11-16-heading-title-continuation/reports/t2-core-sanitizer-investigation.json)
includes exact steps, six core-run job outcomes, failure/summary excerpts and the
complete original decoded UTF-8 log compressed with gzip/base64. Its 465,655
decoded bytes have SHA-256
`058cd0f6dc6bbb94ececb420f825cb4dad0cac6807d0e50639deb7573107c320`.
This preserves the tool-returned text, not the provider's original HTTP archive.

## Source relevance and what remains unobserved

Exact-byte comparisons show the failing test, `tools/render.cpp`, core
`CMakeLists.txt`, `CMakePresets.json` and `.github/workflows/ci.yml` are identical
at pre-T2 `113c29b`, published T2 and the inspected worktree. The receipt retains
their hashes. The core job uses Debug GCC 13.3.0 with ASan, UBSan and leak checks;
its preset leaves the native SDL application disabled. Neither the T2
`InstrumentView.cpp` paint path nor the separately admitted native `main.cpp`
replay repair is executed by this headless renderer test.

The race first observes staging with Linux inotify, confirms the renderer is
stopped by SIGSTOP, proves the destination absent, creates a sentinel file and
resumes the renderer. Only then does the 15-second wait begin. The renderer's
source finishes the render and flush before its create-only hard-link publication.
The subsequent assertions for exit 1, expected refusal message, unchanged
sentinel bytes/device/inode, unchanged inputs and staging cleanup were **not
reached**. The `finally` block kills an unfinished child, so this log does not
establish its eventual result or why it exceeded 15 seconds. Scheduling contention,
deadlock and machine speed are not diagnosed.

The core run's five other jobs succeeded, including the macOS-labelled Release
jobs. Other workflow results and later source qualification remain separate.

## Recommended next action

Root can make **one unchanged targeted rerun of job 133715652514** as a bounded
diagnostic, preserving this original 201/202 failure and recording the actual
new attempt. A later success would qualify that attempt without rewriting this one.

If the timeout repeats, the narrow repair candidate is a separately reviewed,
bounded completion budget for this long post-resume race. Keep its 1,200,000
frames/block-1 workload, observed staging, confirmed stopped child, sentinel
injection and every refusal/byte/inode/cleanup assertion. Retain the ordinary
small-render 15-second guard and the existing 90-second registered-test bound.
Choose the revised completion budget from observed instrumented execution and
document it as a changed harness protocol; this inspection supplies no measured
replacement value. Do not skip the test, disable instrumentation, broaden
success conditions or retroactively relabel the original run.

Root owns any diagnosis run, independent admission, corrective change and final
source-specific platform decision.

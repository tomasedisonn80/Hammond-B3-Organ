# Repaired-source hosted admission

**A58, Wave 10, 16 November 2026 — all thirteen hosted jobs pass at the repaired
source.** This admits the exact observations below. The earlier Windows failure
remains failed historical evidence, and the remaining product and physical exits
remain open.

The observed commit is
[`2f57723d9ec806fe8f721c317ef8c1a38d63b532`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/2f57723d9ec806fe8f721c317ef8c1a38d63b532),
tree `cee5fdc4b07d95185ebd9e4d1c5f236f88a787f9`, parent
`af2b74760ee195c9497b314a1a29172f5238dd44`. A58 independently fetched the
commit, all three run records, their job and step records, and all thirteen
decoded logs through the owner's read-only GitHub connector. Every run is a
completed successful **push on main, attempt 1**, at this exact source. Every
job's actual revision output also matches. Separate job-list GETs with
`per_page=100` confirm complete totals **5 + 5 + 3**, avoiding reliance on an
unexamined first-page count.

| Workflow | Run | Observed outcome |
| --- | --- | --- |
| CI | [43785480005](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43785480005) | 5/5 jobs successful |
| Native standalone | [43785480050](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43785480050) | 5/5 jobs successful |
| Native VST3 | [43785480026](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43785480026) | 3/3 jobs successful |

The [audit receipt](../development/2026-11-15-streaming-continuation/reports/A58-hosted-audit.json)
retains exact job IDs, source hashes, steps, numbered test-result lines, toolchain
records and cross-checks. Its
[read-only reproducer](../development/2026-11-15-streaming-continuation/reports/A58-audit-repaired-hosted.py)
checks the retained responses and local Git blobs; it does not run tests or
query the provider. The full fetched records and decoded logs survive in one
[provider bundle](../development/2026-11-15-streaming-continuation/reports/A58-provider-evidence.json.gz):
**7,068,870 decoded JSON bytes, 731,516 gzip bytes**, with exact hashes in the
receipt. These are decoded responses, not original HTTP or artifact-archive bytes.

## Executed selections at this source

Times are each logged CTest wall time, except the separate full R4 experiment.
They are new observations and do not replace the initial publication's timings
or the local 210-test qualification.

| Job | Configuration | Executed result | Wall seconds |
| --- | --- | --- | ---: |
| Core Linux GCC | Release | **185/185** | 96.23 |
| Core macOS AppleClang | Release | **185/185** | 140.33 |
| Core Windows MSVC | Release | **185/185** | 291.43 |
| Core Linux ASan/UBSan/leaks | **Debug** | **185/185** | 333.94 |
| Complete R4 waveform | Release, full experiment | `status: pass`, `mode: full`, `failures: []` | 615.394267795 |
| VST3 Linux GCC | Release | **8/8** | 5.49 |
| VST3 macOS AppleClang | Release | **7/7** | 5.37 |
| VST3 Windows MSVC x64 | Release | **7/7** | 7.57 |
| Standalone Linux, MIDI ON | Release | **53/53** | 323.53 |
| Standalone Linux, MIDI OFF | Release | **53/53** | 315.79 |
| Standalone macOS, MIDI ON | Release | **53/53** | 335.88 |
| Standalone Windows x64, MIDI ON | Release | **53/53** | 404.47 |
| Native standalone ASan/UBSan/leaks | **Release**, MIDI OFF | **22/22** | 489.62 |

All four core jobs execute and pass the six causal suites: grid, lifecycle,
resources, strict CLI, differential replay and Python reference. This includes
actual Windows compile/runtime and transport evidence. It does not demonstrate
the deliberately failing Windows mode-setup branch, a converter or causal audio.

Every VST3 job runs the actual module validator and reports **47 passed, zero
failed**, in addition to its CTest selection. The four standalone Release jobs
execute the same 53 names and contain all 32 required native gates. Their
relocated package checks report 20 installed files and ALSA/CoreMIDI/WinMM for
the three MIDI ON variants; Linux MIDI OFF reports 16 files and MIDI unavailable.
These observations include help, dummy smoke and archive-byte checks.

Observed versions remain explicit: Linux GNU **13.3.0**, CMake/CTest **3.31.6**,
Python **3.12.16**; macOS AppleClang **17.0.0.17000013**, CMake/CTest **4.4.5**,
Python **3.12.10**; Windows MSVC **19.44.35230.0**, CMake/CTest **3.31.6**,
Python **3.12.10**. The complete R4 job reports its own compiler/CMake/Python
lines and is not another CTest selection.

## Windows repair: failure retained, repaired package passes

The [initial admission](STREAMING_INITIAL_HOSTED_ADMISSION.md) remains **12/13
successful jobs** at `af2b747`; Windows core passed 184/185 and failed the
relocated contact-reference installation with `input changed after path
preflight`. A58 rechecked the original full decoded log's SHA-256
`2858f8f90bb79736630bf72b0fdaca93156baf9f8496afe83cb7500adc47ba6d` and diagnostic.
No prior failure, source identity or result was rewritten.

At repaired `2f57723`, Windows job
[133032022089](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43785480005/job/133032022089)
passes all 185 tests, including:

| Affected CTest | Observed Windows result |
| --- | --- |
| `python_test_contact_switching_io` | Passed, 2.24 s |
| `python_test_contact_reference_install` | Passed, 19.38 s |
| `python_test_contact_switching_study` | Passed, 1.84 s |

The independently fetched Windows log exactly equals root's
[retained success log](../development/2026-11-15-streaming-continuation/reports/windows-core-2f57723.log.gz):
**524,438 decoded UTF-8 bytes**, SHA-256
`3a4873732a6909ca09beaa6bb2bfc8ef71303ccb92533927ce230e52b1a73530`.
The [source and regression admission](CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md)
and [affected local qualification](../development/2026-11-15-streaming-continuation/reports/windows-repair-qualification.json)
remain distinct earlier evidence. This fresh hosted pass supplies the Windows
runtime observation they correctly left pending.

## Source identity and sanitizer coverage

A58 independently rehashed all **505** inputs in the repaired-source inventory
and read the corresponding immutable Git blobs. All current file hashes and
published bytes match that inventory. Compared with `af2b747`, exactly two
recorded files change: `tools/contact_switching_io.py` and its existing I/O test
file. The other **503 recorded inputs** remain identical. The three workflow
files also match the repaired commit, parent and working tree. This is a
bounded input-set observation, not a claim that every document is unchanged.

All six selection sources previously audited by A48 retain their exact bytes:
the three workflows, root CMake, standalone CMake and presets. That identity
preserves A48's independently checked additive Upper gate, all old mappings
and timeouts. A58 additionally parses the current 22 sanitizer name-to-target
mappings and 32 required Release names, and compares them with the actual
repaired-source executed names. The sanitizer job executes exactly those
**22 mapped gates**, including the distinct calibration probe target.

The native sanitizer job's source/object/archive/runtime verification step
succeeds. Its complete log contains instrumented compile commands for the
Upper fixture and `InstrumentView.cpp`; its observed policy retains
`detect_leaks=1:halt_on_error=1`, UBSan stack traces with halt-on-error and
LSan exit code 23. The exact-source verification requires the selected project
objects, pinned SDL C, six instrumented archives and ASan/UBSan linked runtimes.
A58 does not infer an unprinted object count or claim that system libraries
were rebuilt. The real application entry runs through a substituted MIDI
dependency; the log reports ten subprocesses and seven lifecycle scenarios.

The Upper fixture passes in all four native Release jobs and the sanitizer job.
Each reports **30 cases, 58,876,889 checks, 49 state restorations, 15 clip
companions, 216 opaque-child probes and 12 focus cases**, under
`upper-rack-material-v1.1`. The sanitizer fixture takes **51.81 s**. Its backend
is explicitly **SDL software surface; fixed copied state; no audio/window**.
This does not rerun or regrade the separate 96-pair comparison or twelve-frame
application gallery.

## Admission and remaining work

A58 read complete AGENTS and PLAN, the active scope/checkpoint and repair scope,
current recovery sections, A48/A47 reviews, source qualification/publication
records and relevant workflow implementation. Work used
`/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`. No production file, shared
document, ledger, index or ref was edited; no build, broad suite, workflow retry,
artifact download, commit or push was performed by A58. A small auditor-authoring
field mismatch was corrected and retained in the
[authoring observation](../development/2026-11-15-streaming-continuation/reports/A58-authoring-observation.json);
it was not a project or hosted test failure.

**No blocking hosted or source-identity finding remains for `2f57723`.** Root
can reconcile current documents with these observed results, complete actual
worker acceptance and publish the final documentation. A later commit still
needs its own remote verification and observed hosted outcomes. This review
does not close another owner's unfinished work or the sixty-worker ledger.

The nominal dry Engine remains unchanged. No converter, causal audio filter,
full-window audio grade, continuing full-organ contact route or physical
Hammond/Leslie match is admitted. Dummy fixtures, validators and compiled native
backends establish neither actual display/audio/MIDI/DAW journeys nor callback
deadlines or OS callback retirement. Semantic accessibility, literal
whole-interface **1:1**, calibration, rights and signed distribution keep their
separate M0–M9 exits.

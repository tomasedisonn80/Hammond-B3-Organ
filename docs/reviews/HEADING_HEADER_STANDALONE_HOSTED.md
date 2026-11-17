# Heading, title and header standalone hosted verification

## Original published outcome

**The original standalone workflow failed overall.** Exact source
fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2 ran in
[Native standalone run 44016021554, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021554).
All six jobs are terminal: four normal families passed, Windows failed during
compilation, and the sanitizer job was cancelled with only 30 of its 34
selected tests completed. This record preserves those outcomes permanently;
a subsequent repaired-source run must have a separate identity.

The [machine-readable receipt](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted.json)
contains every required name and sanitizer target mapping, all actual normal
test names, per-job summaries, header metrics, original failure references and
the earlier combined-workspace diagnosis without alteration. The
[run record](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/run-44016021554.json)
binds actual runners, timestamps and all ten artifact records.

| Actual family | Job ID | Actual runner | Outcome and CTest time | Installed package |
| --- | --- | --- | --- | --- |
| Linux GCC, MIDI ON | 133814025319 | GitHub Actions 1000001383, ubuntu-24.04/X64 | Success; 68/68, 360.44 s | 21 files, ALSA |
| Linux GCC, MIDI OFF | 133814025192 | GitHub Actions 1000001382, ubuntu-24.04/X64 | Success; 68/68, 452.39 s | 17 files, unavailable MIDI |
| macOS Intel AppleClang, MIDI ON | 133814025354 | GitHub Actions 1000001391, macos-15-intel/X64 | Success; 68/68, 602.50 s | 21 files, CoreMIDI |
| macOS AppleClang, MIDI ON | 133814025770 | GitHub Actions 1000001394, macos-15/ARM64 | Success; 68/68, 409.24 s | 21 files, CoreMIDI |
| Windows MSVC x64, MIDI ON | 133814025240 | GitHub Actions 1000001388, windows-2022/X64 | Build failure; tests unreached | Unreached |
| Linux GCC ASan + UBSan + leaks | 133814024877 | GitHub Actions 1000001379, ubuntu-24.04/X64 | Cancelled; 30 passed, one started without result, three unstarted | This job has no package gate |

## Exact source and inventory

Independent GitHub commit metadata identifies tree
b62f212300d75633346ab8fc5ffdd722255fe00a and parents
9d60dbf462a90fe422fd4e69757fe202264acb7c and
835755a9069c25ce55bc2c231547458b4b3ffce4. The remotely fetched workflow matches
the immutable Git source: 71,269 bytes, SHA-256
4fe89694b7b85fe83b27f4bd2b3dc60e2b45ce88e30e1209e94a30a5469bf48c.
Every job's metadata and checkout log refer to the published source and attempt 1.
Root's [publication receipt](../development/2026-11-16-heading-title-continuation/reports/source-publication.json)
retains the guarded publication and independent Git checks.

The published workflow requires **45 normal test names** and discovers all
enabled standalone-prefix tests. Each successful normal job actually discovered
and passed the same 68 names. Its sanitizer inventory is **34 gates mapped to
31 build targets**. Earlier preparation described 44/33/31; that historical
inventory remains archived under the session's inputs/hosted-preparation directory
and cannot describe this executed source.

The receipt also pins the standalone CMake source to 642655110b803592…,
workspace fixture to 38808674e491c222…, and semantic paint fixture to
8a6ecd4ac9747c359…. Full digests and immutable Git blob IDs are retained.
The two prospective Windows portability changes currently in the working tree
are explicitly excluded from the original fba1911 source identity.

## Completed normal native acceptance

Each successful job built the aggregate inputs, checked actual compiler and
native SDL backend identities, verified its compiled MIDI configuration, ran all
68 tests serially, and reverified source and locked dependencies afterward.
MIDI OFF's successful path verifies that RtMidi is not acquired or built.
These assertions are in the exact workflow, and their executed steps passed.

The new title, header, statistics, grain, replay-paint and semantic-paint gates
all passed on all four successful normal jobs. Header material reports 48
cases, 10,542 checks and 163 paintings; grain bounds reports four cases and
170 checks. Statistics passes all 103 numerical criteria on those four jobs
and on the completed sanitizer statistics gate. Its canonical image SHA-256 is
20eea493c5b2fe75c467a5964b54a28c832edf7639f034d8eb83daf4036d4557;
the header digest is
1a7b0b316dc771428f2241eec9fbd25668ba337a6a2232b5787a2014f86eaaac.
These are the original fixture/source identities, before the portability casts.

Every successful normal log reports these actual child counts: application
184; MIDI CLI/modal 159; expression diagnostics 3; calibration 10 across seven
lifecycles with two deliberate replay failures; native MIDI replay 33 with two
expected interruptions; native workflows 52; workspace 37; replay paint 2;
semantic paint 2; replay boundaries 29 with 19 setup rejections. These are
suite-local counts and are not summed into an invented total.

Linux MIDI ON reports 26 enumeration errors, zero successful UI replays and
23 expected failed UI replays in its MIDI CLI/modal suite. The other three
successful normal families report zero enumeration errors, 19 successful
replays and four expected failed replays. All corresponding suites passed
their explicit expectations; neither branch proves attachment of a physical
MIDI device.

The 37-child workspace count includes the seven independently executed
250 ms empty startup prefixes admitted in the frozen
[startup review](WORKSPACE_STARTUP_OBSERVATION_ADMISSION.md).
The existing [conformance](WORKSPACE_STARTUP_OBSERVATION_CONFORMANCE.md) and
[actual local qualification](WORKSPACE_STARTUP_ACTUAL_QUALIFICATION.md) remain
separate, unchanged evidence. Successful hosted workspace tests establish
their complete control, hold, view and saved-byte tails on those four jobs;
they do not erase the original local failed attempts.

## Install, Unicode paths, relocation and archive checks

All four successful families pass the complete, unfiltered installer CTest:
eight Python methods and OK. The exact installer source is SHA-256
0dffa82863f4ddd80e48cc8afc05329af60ae9ec028e5951638b57db16f84fb6.
Individual method names are not printed by that unittest invocation; their
coverage follows from the complete executed command, eight-method success and
the bound source.

The source includes real installed-component movement through Unicode and
space-containing prefixes, help from an unrelated working directory, exact
21-file or 17-file payload checks, and unchanged installed bytes. Its custom
directory case uses program files Ω/bin, readable data Ω/share and operator
session Ω. It removes the private source/build copy before exercising the
copied installation, then runs the fixed 800 ms synthetic inverted-CC11
calibration replay. It requires expression 0.75, empty held notes, exact
20..100 inverted calibration, zero errors, no state save and an unchanged
payload. Disabled-component negative cases remain covered.

The separate workflow staging step verifies the precise payload, hashes and
modes, moves its prefix, runs relocated help and the fixed 600 ms dummy smoke
outside the repository, requires closed or unavailable and quiescent MIDI,
and compares tar members, bytes and modes with the installed files.
All four steps and package uploads succeeded. There are six diagnostic
artifacts and four package artifacts, retained for 14 days. A53 inspected the
actual log assertions and artifact metadata; A53 did not independently
download and compare archive member bytes.

## Sanitizer execution and exact cancellation boundary

The job successfully built all 31 selected inputs and passed its instrumentation
verification step. The published assertions require address/undefined
sanitizers and frame pointers on SDL C and project C++ objects, matching
archive symbols and linked runtimes on all targets. The real application's
main and painter are instrumented; the grain fixture includes the real painter
once. The private MIDI-disabled definition belongs to the support library.
The calibration probe instead retains MIDI-enabled fake-header substitution.
Both application entry paths link the required instrumented archives.
The instrumentation JSON is retained by the CI artifact; A53 relies on the
executed assertions and successful step, without claiming to have downloaded it.

The actual policy remains ASAN_OPTIONS=detect_leaks=1:halt_on_error=1,
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1, and
LSAN_OPTIONS=exitcode=23. Discovery passed exactly 34 enabled commands from 31
targets, with the specified child/CTest bounds and no per-test sanitizer
override. The actual execution is serial.

Thirty tests completed and all 30 passed. In particular, title density took
16.40 s, header material 145.59 s, statistics 2.02 s, grain bounds 0.08 s,
and scaled view 108.89 s. Completed test durations sum to 739.08 s.
This is a partial result, not a 34-test pass.

The [original cancellation block](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814024877-cancellation.log)
preserves the completed scaled-view result, preset-raster launch, actual
command, 300 s CTest bound and cancellation line. Preset raster started at
04:35:49.6666788 UTC. At 04:36:39.3023508, about 49.64 s later, the runner
reported “The operation was canceled.” There is no preset-raster terminal
result or CTest timeout report.

The job began at 04:16:26 and has a 20-minute workflow budget. The cancellation
is near that ceiling, but the available output does not independently identify
the originating cancellation reason. The connector rejects the check-runs
annotation endpoint; no annotation-based cause is asserted. No actual ASan,
UBSan or LSan finding appears in the executed output.

Native calibration, replay paint boundary and semantic paint boundary never
started in this job. Consequently, the instrumented ten-child/seven-lifecycle
calibration post-check, both instrumented real-application paint executions,
the complete CTest summary and source/SDL post-acceptance verification are
unreached. Diagnostic upload succeeded after cancellation and supplies no
substitute for those missing outcomes. Root will assess any prospective
job-budget correction separately while preserving every original result.

## Windows failure and separately reviewed repair

The [original Windows compiler block](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814025240-compile-failure-original-crlf.log.gz)
retains C4244 int-to-float warnings at the two dimension assignments on fixture
line 156, promoted by /WX to C2220. Build failed before compiled-MIDI
verification, test discovery or packaging. The original warning policy remains
unchanged.

The frozen [portability admission](HEADER_MATERIAL_WINDOWS_PORTABILITY.md)
authorizes exactly two explicit float casts and the corresponding active
statistics fixture hash transition. The historical comparator and its old
fixture pin stay unchanged. The separate
[implementation and local-result supplement](HEADER_MATERIAL_WINDOWS_PORTABILITY_CONFORMANCE.md)
confirms exactly those source changes, 473 other code inputs unchanged, and
root's two affected CTests passing in 43.593519385 s. Original and rebuilt
native fixture binaries are byte-identical; all 48 list cases and default
output match. Complete statistics differ only in the two admitted source
identities; all 103 criteria and numerical/image results remain identical.

That local result is not MSVC qualification. The next source publication must
independently pass actual Windows compilation and subsequent gates. Its result
must not replace this original Windows failure.

## Log-retention correction

Final static receipt verification detected that the initial writing tool normalized
the two Windows compiler-log excerpts from CRLF to LF. Their existing files,
original job record and frozen portability reviews remain unchanged. Separate
deterministic gzip members now decode to the original CRLF stream blocks byte
for byte. Gzip avoids the repository's text=auto/eol=lf normalization without
changing Git attributes.
The [retention supplement](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/job-133814025240-log-retention.json)
binds both representations, their sizes and hashes, source line/byte offsets,
and exact newline-normalization equality. This corrects retention provenance;
the compiler text and observed outcome are unchanged.

## Evidence boundaries and continuation

A53 made no source/workflow edits, native executions, reruns, Git mutations or
remote changes. Each complete returned log has a UTF-8 byte count and SHA-256;
bounded selected original lines are identified as noncontiguous excerpts, and
the failure/cancellation blocks retain their exact original contiguous bytes.
All six complete returned decoded logs are also stored as deterministic gzip
members in the [complete-log manifest](../development/2026-11-16-heading-title-continuation/reports/a53-standalone-hosted/complete-log-archives.json).
They retain 5,861,649 original UTF-8 bytes in 628,841 stored bytes, including
Windows CRLF. Every compressed and decoded hash and every round trip is
verified. These are the connector's complete decoded log streams, rather than
the provider's original archive. Root owns repair decisions, guarded
publication and future execution.

The next gates are actual successor-source Windows acceptance and complete
strict sanitizer acceptance, followed by all successor-source family outcomes.
Dummy/software rendering and fake or synthetic MIDI do not establish physical
device acceptance, real-display presentation, native accessibility or literal
whole-interface 1:1 reference parity. Those exits remain open.

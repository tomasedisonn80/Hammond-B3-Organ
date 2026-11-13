# Assignment 48 — hosted platform and actual package review

Actual agent `/root/w08_a48_hosted_platform_review`, wave 8, assignment 48/60;
completed in the 2026-11-13 development session. Owned only this note and
[the hosted platform review](../../reviews/STANDALONE_HOSTED_PLATFORM_REVIEW.md).
No production code, workflow, dependency, shared ledger or status file changed.
Root owns integration, commit and publication.

## Goal and result

Audit observed hosted outcomes and actual Linux/Windows standalone package
bytes for commit `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`. Result: package/source/inventory/
recorded acceptance checks pass for both platforms; an independently relocated
**downloaded Linux executable** also passes integrated keyboard replay.
No local build was substituted, and Windows execution is reported only from
its actual hosted job. This result does not qualify newer source or turn the
checkpoint's failed macOS standalone/core jobs green.

## Work performed and evidence

1. Read root agent instructions, standalone CI/install contracts, continuation
   handoff and platform follow-up. Preserved source and workflow boundaries.
2. Queried authenticated GitHub jobs/artifacts. Native standalone run
   `43523378962`: Linux `132222980756` and Windows `132222981043` succeeded;
   macOS `132222981098` failed compilation and did not run acceptance/package.
   Independently observed all three successful native VST3 jobs in run
   `43523378803`; did not download VST3 payloads or claim independent counts.
3. Downloaded actual package/diagnostics ZIPs and matched API byte lengths and
   SHA-256 values. Artifacts: Linux package `14083099657`, diagnostics
   `14084546622`; Windows package `14083632691`, diagnostics `14083592793`.
   The detailed review retains all four full digests and inner archive hashes.
4. Validated archive paths/types/duplicates/encryption/expansion bounds before
   manual extraction. Both packages contain three ZIP members and exactly nine
   payload files/five directories. Matched every inventory file mode/size/hash,
   directory mode, inner checksum, installed/staged inventory, provenance,
   smoke JSON and BMP identity.
5. Compared seven metadata/notice files with exact source objects, SDL license
   with locked SDL commit, both source font byte identities, compiler records,
   all archived backend macros/config hashes and canonical nominal-profile
   authoring identity. Source `main.cpp` matches native chapel log identity.
6. Parsed actual JUnit and detailed test records. Linux and Windows each ran
   13 selected CTest suites with zero outer failures/disabled/skips. Retained
   Linux's explicit untested POSIX replacement-failure case and Windows's one
   unsupported FIFO Python subcase skip. Recorded actual app/workflow/chapel/
   boundary process counts and calibrated callback allocation scope.
7. Relocated the actual Linux payload; ran `--help` and the exact source's
   711-byte `keyboard-notes.b3ui` with dummy audio/video, software rendering,
   fresh state/output paths and a 30-second subprocess timeout. Checked final
   command acknowledgement, note ownership and all diagnostic counters.
8. Inspected actual ELF/PE formats and runtime imports/symbol requirements;
   checked payload bytes/file modes after execution. Preserved failure counts
   from separate core CI run `43523378849` and the coordinator's detailed log
   diagnosis rather than treating standalone success as an override.

Actual Linux executable SHA-256:
`dbae7012e63f5e7ba5caf22df20b04c523cb5c2545923ac4e16f1fa52fb4db44`.
Actual Windows executable SHA-256:
`980688b720dc79ec0085378c50a9fd2805a72ed795e7da1fdd265b41328208cc`.
Toolchains are GNU 13.3.0/Ubuntu 24.04 x86-64 and MSVC
19.44.35230.0/Windows Server 2022 x64. Required native backend macros are
present, but every audited execution used dummy drivers.

Independent Linux replay: exit zero; 18/18 events, four accepted note-ons and
four accepted note-offs, final sequence 9 acknowledged, one device start,
nontruncated observations, Upper 60/Lower 74/pedal 17 ownership followed by
Upper 72, empty final holds before shutdown. The callback recorded 247 calls
and 126,464 frames with peak `0.14220303297042847`; audio failure counters,
application errors and session fault/recovery/overflow/rejection counters were
zero. One shutdown cleanup command was discarded. Automatic smoke was not
requested. Missing state remained missing. Replay JSON SHA-256:
`fda7aa50f2c4b10304c059909120bd211da6cb176961c743cb672b1bb96fcae9`.

The Linux ELF needs runtime symbols through GLIBC 2.38 and GLIBCXX 3.4.32,
plus native-driver libraries when those backends are selected. Windows PE
imports MSVCP140/VCRUNTIME140/VCRUNTIME140_1 and UCRT; its PE certificate
directory is empty. These are observed package prerequisites, not universal
platform compatibility or signing approval.

## Audit limits and correction

One preliminary audit assertion incorrectly compared the profile's declared
canonical authoring hash with its formatted JSON file-byte hash. The verifier
was corrected to use the exact source canonical JSON convention, and both
platform checks passed. This was an audit assumption error, not a product
failure. No failed product execution was concealed or retried to obtain a pass.

Core Release remains 89/90 Linux, 87/90 Windows and 89/90 macOS at `5b8e241`;
the sanitizer job succeeded. Native macOS remains a build failure at that
source. Scope excludes physical devices/hotplug, callback deadlines, C/system
allocation/locks, accessibility, MIDI, fidelity, release rights and permanent
distribution. No current-source claim follows from these old artifacts.

## Reproduction, handoff and next action

Scratch evidence lives at
`/workspace/scratch/5ba97739b54c/a48-hosted-platform/`, with four ZIPs,
authenticated metadata without temporary URLs, verifier/output JSON,
extracted diagnostics, relocated Linux payload, PE/ELF inspection and retained
replay input/command/results. The detailed review records source mappings,
all installed hashes, process counts, command/environment and artifact IDs.
Reacquire artifacts before 2026-11-27 expiry, verify digests and safe membership
before extracting, then repeat from fresh private directories. A new build or
new source requires distinct evidence.

Root published repaired `649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`, while this audit ran. Its native
`43526206689`, core `43526206646` and VST3 `43526206643` runs were not accepted
as completed evidence here. Assignment 60 should qualify the latest candidate
and its own packages, including macOS standalone execution and repaired
Windows/macOS/core tests. Root should integrate and publish these two reports
with that distinction intact.

Future agents must follow root `AGENTS.md`, read the current handoff, preserve
parallel work and exact source/run/artifact identities, report actual failures
and internal exclusions, document commands/results and the next gate, and let
the coordinator integrate shared changes. A resumed audit does not create
another agent assignment; inspection alone does not establish execution.

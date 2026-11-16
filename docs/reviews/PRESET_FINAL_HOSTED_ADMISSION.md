# Exact-source hosted admission — A59

16 November 2026; actual worker `/root/w10_a59`, wave 10. **Observed completion:
all ten non-macOS jobs succeeded; all three macOS jobs were cancelled without
execution.** The final executing job was independently observed complete at
13:05:07 UTC; aggregate run states were refreshed separately. All three workflows
report aggregate `failure`. No executed job or step in the observed follow-up
has failed.
These provider distinctions prevent an all-thirteen or all-platform pass claim.

The [machine receipt](../development/2026-11-16-preset-library-continuation/reports/a59-final-hosted-observation.json)
preserves exact selected provider fields, observation times, source revisions,
runner assignments and every step outcome. The [initial snapshot](../development/2026-11-16-preset-library-continuation/reports/a59-initial-hosted-observation.json)
separately preserves the earlier queued macOS state. This review uses independent
read-only provider queries; it does not substitute a prior worker's status summary.

## Published source and documentary boundary

Independent branch, Git commit and complete root-tree GETs verify main at
`cc6be852d616ec5887485e3fccc39ddb1db22006`, tree
`201e38b05901fa30e3d053b9c245829818a5b52e`, with the sole parent
`20739f6280b95e567e84615d5c5aee443fc3b93d`. The
[publication identity](../development/2026-11-16-preset-library-continuation/reports/a59-publication-identity.json)
retains those provider responses. All 21 root entries match the local committed
Git objects, including production, build, workflow, assets and data trees.

The [working-source comparison](../development/2026-11-16-preset-library-continuation/reports/a59-local-source-overlay.json)
finds local HEAD/tree equal to those published identities, an empty index at its
observation, and no tracked or untracked production/build/workflow/data changes.
Documentation, reviews, notes and receipts remain an unpublished overlay.
This is neither a clean-final-checkout assertion nor verification of root's later
documentary closing commit. That future publication requires its own fresh
commit/tree/parent/contents verification. Hosted evidence here belongs to
`cc6be852`; identical production inputs would not make a later documentation
commit the same observed revision.

## Observed required matrix

All thirteen jobs identify the exact published head. The three run URLs are
[CI](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43869771157),
[native standalone](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43869771215)
and [native VST3](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43869771192).

| Matrix scope | Jobs | Observed result |
| --- | ---: | --- |
| Core Release, Linux and Windows | 2 | Success |
| Core Linux ASan/UBSan/leaks | 1 | Success |
| Complete Linux R4 waveform qualification | 1 | Success |
| Native Linux Release, MIDI ON and OFF | 2 | Success |
| Native Windows Release, MIDI ON | 1 | Success |
| Native Linux ASan/UBSan/leaks | 1 | Success; 28/28 selected gates |
| Native VST3, Linux and Windows | 2 | Success |
| Core, native standalone and VST3 macOS | 3 | Cancelled; runner 0, no steps |

Each macOS job was first observed queued with `runner_id: null` and `steps: []`,
then completed/cancelled with `runner_id: 0`, an empty runner name and no steps.
No macOS build, test, validator or package executed in this evidence. The
responses establish no reason for the missing runner or cancellation. Aggregate
workflow failures remain recorded even though no executed failing step is present.

Native Linux sanitizer job `133307538255` completes its instrumentation checks,
28-gate leak-check execution, source/dependency reverification and archival.
Its decoded original independently reports **28/28 passing in 662.55 seconds**,
including all three apron gates. This closes that executing job's pending state,
without supplying the absent macOS execution.

## Windows repair and actual Unicode generator

The complete decoded log for core job `133307538161` records the correct checkout
revision, a passing `test_standalone_registration_library` in 0.95 seconds, and
**202/202 tests passing in 206.72 seconds**. This directly executes the Windows
conditional regression that the earlier six Linux passes could not qualify.
The Windows core inventory differs from the local native 235-test configuration;
these are distinct source/configuration observations.

The same successful job compiles the actual generator beneath
`D:/a/_temp/hammond generator é 漢字/source`. Its compiler command contains
`/utf-8` and that exact `HAMMOND_STARTER_SOURCE_DIR`. Actual timestamped JSON
contains 24 successful file records and `Complete` with 24 attempts/commits.
A second invocation returns `ProtectedPath`, zero attempts and zero commits.
The inspected passing workflow step also enforces tracked-HEAD archival,
event-revision equality, codemodel flags, all 24 filenames/bytes/hashes,
an absent protected child and unchanged authored-pack inventory. The retained
log supplies actual compiler/output evidence; it does not claim a separately
downloaded inspection of the external diagnostic artifact's qualification file.

Native Windows job `133307538750` independently passes registration storage in
0.82 seconds, actual starter Load in 11.56 seconds, and **61/61 selected tests
in 462.22 seconds**. Its source/dependency recheck, installed relocation/smoke,
diagnostics and package archival steps all succeed. The log records both successful
artifact uploads. These hosted software checks do not establish physical audio,
MIDI-device or real-display acceptance.

## Retained originals and remaining admission

The [log index and exact excerpts](../development/2026-11-16-preset-library-continuation/reports/a59-hosted-log-excerpts.json)
bind complete decoded core/native Windows and native Linux sanitizer logs to
their jobs and SHA-256 values. Their deterministic gzip files total 241,272 bytes;
decompressed UTF-8 preserves the tool-returned BOM and original line endings.
This retains original decoded log text, not an
original HTTP transfer/archive. Excerpts are explicitly derived readers.

The [first-head history](../development/2026-11-16-preset-library-continuation/reports/first-ci-final-observation.json)
remains six successes, four known failures and three unexecuted macOS cancellations.
The original local 234/235 result also remains unchanged. Later success does not
erase either failure history. A59 changed no code/workflow, dispatched no job,
reran no tests, and cancelled nothing. macOS execution remains unqualified;
all-platform admission is incomplete. Physical fidelity,
literal whole-interface 1:1, native accessibility, callback deadlines/retirement,
DAW/device journeys, rights and signed distribution retain separate exits.

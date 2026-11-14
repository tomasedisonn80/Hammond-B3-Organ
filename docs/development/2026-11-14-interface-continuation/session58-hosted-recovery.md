# Session 58 — hosted recovery evidence

Actual agent: `/root/w10_a58_hosted_closure`, A58, wave ten. This is the same dispatched worker resumed after the workspace interruption; no new worker was spawned.

## Completed audit and observed result

A58's primary-source and hosted-status audit is complete; assignment acceptance is not an all-platform pass. Recovered source `6f69c68ed5bf51d77dba1ae4f75d4bc75d144747`, tree `daa6195fd3cfc4e56dd0d99b46972c68ae3c7e81`, has nine successful jobs and three cancelled macOS jobs in attempt one. The macOS jobs never acquired runners and contain no steps. They do not qualify the repaired fixture. See the [hosted recovery review](../../reviews/INTERFACE_HOSTED_RECOVERY.md) and [exact-source primary audit](reports/a58-recovery-hosted-6f69c68.json).

The primary Linux MIDI OFF, Linux MIDI ON and Windows standalone logs each prove 38/38 CTest, twelve MIDI methods, six workspace methods and thirty actual workspace subprocesses. The native sanitizer log proves thirteen selected suites passed, five native-labelled, with ASan/UBSan instrumentation and leak checking enabled. The full Release native-label count is fourteen, including top-level `test_standalone_install`; the earlier thirteen-name source lists omitted that registration.

## Work actually performed

- Read the published recovery instructions and retrieved the exact recovered fixture, relevant workflow and CMake registrations through GitHub. Independently matched fixture SHA-256 `0488bc549bbe4475fac8daa4f5d69c76a58db5ca7a94f1ff7e146f7ac11c0692`.
- Observed all twelve exact-source job records and decoded the four completed standalone primary logs. Checked distinct CTest names, method identities, checkout SHA, thirty-process declarations, package assertions and sanitizer enforcement/options.
- Preserved the original b1 eleven-success/one-failure matrix and macOS 37/38 failure. Freshly retrieved its failed primary log and verified the original raw hash. Wrote a newly authored [historical recovery summary](reports/a58-recovery-checkpoint6-primary.json), without recreating unavailable original files.
- Re-extracted the historical cdb native 13/13 result, exact flags/options and five-native label distinction from its retained primary GitHub response. Kept pre-outage independent artifact inspection explicitly historical.
- Preserved all three recovery attempt-one macOS cancellations at 2026-11-14T14:34:10Z. The connector rejected their advertised check-run endpoints; cancellation cause remains unverified.
- Kept raw primary log text in cloud memory and authored bounded durable reports with exact identities, hashes, excerpts and scope. No local build/test, workflow rerun, tree/commit mutation or branch update was performed by A58.

## Owned new recovery paths

- `reports/a58-recovery-checkpoint6-primary.json`
- `reports/a58-recovery-hosted-6f69c68.json`
- `../../reviews/INTERFACE_HOSTED_RECOVERY.md`
- `session58-hosted-recovery.md`

These files are new recovery documents. The original local report/review/session-note bytes, raw artifacts and staged 137-file candidate remain unavailable. Before interruption, A58 completed the reported cdb/b1 artifact inspections; this cloud recovery does not claim to recover or rehash those ZIPs.

## Remaining acceptance

Root will publish the final recovery documents and a strict Linux completion-checker step while preserving the exact fixture. That final head supplies the bounded fresh macOS opportunity; its standalone log must show 38/38, six workspace methods and thirty actual native subprocesses. The final head needs its own observed twelve-job matrix and strict sixty-row checker. A58 will not retry or cancel the recovered first-attempt workflows. Their nine successes and three unexecuted macOS cancellations remain preserved. I remain the same A58 for final-head observation.

The review distinguishes engineering CI from real devices, DAW qualification, native accessibility, timing, physical fidelity and literal visual equality. Root owns shared documentation integration, actual worker acceptance and publication.

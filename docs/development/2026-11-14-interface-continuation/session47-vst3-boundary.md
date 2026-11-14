# A47 — Native VST3 boundary

Actual worker `/root/w08_a47_vst3_boundary`, assignment **47/60**, logical wave
**8**, 14 November 2026. Owned paths are this note,
`docs/reviews/INTERFACE_VST3_BOUNDARY.md` and `reports/a47-*`. This is a read-only
product review; no source, build, index, publication or shared-status mutation.

## Result

**Accepted:** this standalone interface slice preserves the native VST3
contract. All 114 A12-protected files match the original baseline, published
`8673713a484c40e26ac7810c7c4cbc22fa874426`, observed current HEAD
`cdbb2beaa28bf136f9a8db6213819129514e2ae9` and current working bytes. This
includes all 20 VST3 and 44 core sources. No native/core paths were added or
removed. The registry, compiled metadata and independent native controller
oracle agree on all 47 IDs/defaults/ranges/steps; state4 and readers 1–3 remain
unchanged. Native sources and hosted build logs have zero SDL/standalone-source
references. The full [review](../../reviews/INTERFACE_VST3_BOUNDARY.md) records
factory/bus/generic-control scope and qualification limits.

## Actual inspection and commands

Read `AGENTS.md`, the whole `docs/PLAN.md`, current scope/checkpoint and relevant
workspace/inspection contracts; inspected root/native/standalone CMake, native
workflow, parameter/state/core boundaries, factory IDs, controller/processor
implementation, native ABI/controller expectations and pinned SDK validator
cleanup/format sources. Used `rg`, bounded `sed`/`cat`, `git status`,
`git rev-parse`, `git show` and `git diff`; no configure/build/CTest invocation.

From `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`:

```sh
python3 docs/development/2026-11-14-interface-continuation/reports/a47-audit.py \
  --repo . --logs ../a47-vst3-hosted-logs \
  --sdk /workspace/scratch/1742da7072be/vst3sdk
```

The audit reads retained primary logs and Git objects, checks bytes and source
metadata, and writes only A47 evidence. It passed: **114 checked / zero
mismatches / 47 parameters / three successful native jobs**. Source hashes,
compiled/oracle comparisons and exact run/test identities are retained in
`a47-source-boundary.json`, `a47-hosted-vst3.json` and `a47-hosted-excerpts.txt`.

Discovered `github_fetch` and `github_fetch_workflow_job_logs` through
`ALL_TOOLS`; used the specified `tomasedisonn80` account and
`repo_full_name=tomasedisonn80/Hammond-B3-Organ`. Fetched run 43596362881's jobs,
Git commit 8673713's tree metadata and full logs for Linux 132451604200,
Windows 132451604376 and macOS 132451604377. Unmodified decoded logs live outside
the repository at `../a47-vst3-hosted-logs/`; compact records include their hashes.
Results: Linux **8/8, 6.05 s**; Windows **7/7, 6.25 s**; macOS **7/7, 4.19 s**.
Each actual module validator reports **47/0**, retaining **16/9/15** teardown,
unsupported-rate and float64 diagnostics. No CTest-level skip occurred; Linux's
additional allocation gate is not registered on Windows/macOS. Conditional
alternate-platform configure steps are recorded as workflow skips.

## Limits and handoff

No native suites were rerun because those exact successful hosted jobs suffice
for the unchanged VST3 bytes. Their results remain tied to 8673713; later
standalone sanitizer/guide metadata does not inherit a hosted result. No custom
VST3 editor, DAW project/device session, physical audio, device deadline,
accessibility, signing, clean-machine or hardware-fidelity acceptance is claimed.
Root should integrate this review and repeat the compact boundary comparison
at the final source freeze. A48/A58 own observing the new standalone sanitizer
job; the next VST3 product gate remains a source/bundle-identified actual DAW
save/reopen and automation session. No commit or push was performed.

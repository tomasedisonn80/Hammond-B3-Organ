# Assignment 52 — dependency and actual native artifact audit

Owner: `/root/w09_a52_dependency_artifact_audit`.

Assignment **52/60**, wave **9**, current pedal session. This is one actual newly
dispatched worker. The spawning UI reported aborted, but the worker ran, notified
root, completed the checks below and produced these records. No child agent was
created or counted.

## Scope, source reading and coordinated change

Initially owned only the new
[dependency/artifact review](../../reviews/PEDAL_DEPENDENCY_ARTIFACT_FINAL.md)
and this note. After identifying outdated current statements, root explicitly
approved updating [DEPENDENCIES_AND_RIGHTS.md](../../DEPENDENCIES_AND_RIGHTS.md)
as a third owned file for wave 9. The correction replaces the old eight-file
OfflineTools, diagnostic-only CI and future-module descriptions with the actual
current boundaries. It preserves the earlier SDK-foundation results as dated
history. No SDK source, lock, notices, native/production/tool/test/CMake code,
shared status or manifest was edited. Root separately assigned the Windows
reparse-point repair to assignment 51; this worker did not touch those files.

Read standing instructions, current handoff/plan/status/next steps, the dependency
and source-rights records, original notices, exact SDK lock, optional build,
acquisition and inventory paths. Freshly read the full extracted text of atlas
pages **475–480**, retaining its distinctions among permission, engineering
applicability, included bytes and final release inspection. This is focused
reading, not another claim of a complete 500-page review. The PDF was rehashed
unchanged against the inspected commit.

Used the cloud runtime skill and its networking guidance. This thread exposed
no `environment_status` tool and had no `/etc/codex/network-policy.json` startup
snapshot. Read-only connected GitHub calls worked; no network configuration,
credential, package, UI, permission flow or dependency installation was needed.
No messages were sent outside the agent team.

## Exact inspected identities and executed commands

Published source: `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`.
Git tree: `19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`.
Native workflow: **43415692247**. Fresh API reads identified the source revision
and successful Linux/Windows jobs independently of the inventory's
caller-declared commit. macOS was still queued at this observation; no completed
three-platform result is claimed here.

Commands executed from the repository or identified scratch directory:

```sh
python3 tools/acquire_vst3_sdk.py --verify-existing /workspace/scratch/f364bc93d920/vst3sdk
python3 tools/acquire_vst3_sdk.py --verify-existing /workspace/scratch/f364bc93d920/a36-sdk-checkout
python3 /workspace/scratch/f364bc93d920/a52-dependency-artifact-audit/audit.py
readelf -d /workspace/scratch/f364bc93d920/a52-dependency-artifact-audit/linux-module.so
objdump -p /workspace/scratch/f364bc93d920/a52-dependency-artifact-audit/windows-module.vst3
```

The two verifier commands each exited zero and reported five primary licenses,
all five checkout identities and the embedded JSON header verified, with no
network used. The independent script separately checked HEAD/top-level identity,
parent gitlinks, tracked/untracked/ignored state, primary license Git blobs,
actual file sizes/hashes and the embedded notice in both external checkouts.
All ten primary-license checks passed. Freshly fetched pinned root LICENSE and
README bytes match their actual checked-out files.

The independent finite artifact script exited zero in **0.715 seconds**. It uses
standard-library ZIP/tar/header/hash inspection and invokes Binutils only to
read import tables. It does not call the production inventory tool or root's
verification script as its oracle. No actual module was loaded. Tool versions:
Python **3.12.14**, Git **2.52.0**, GNU readelf/objdump **2.44**.

## Actual artifact results

Linux artifact **14032125757**, Windows artifact **14032090890** were read from
the actual downloaded ZIP files, not fabricated bundle fixtures. Their bytes,
sizes and hashes match fresh Actions API metadata. Each ZIP has the exact three
expected files. Both inner tar hashes match their included checksum records.
All **ten actual regular payload files** across both bundles have exact
inventory sizes, bytes, SHA-256 and modes, with no duplicate/unexpected/traversing
file paths, links or special members. Linux has four files totaling **456,767
bytes**; Windows has six totaling **658,056 bytes**.

Both modules have the expected 64-bit x86 architecture/header and the same two
locked class IDs in generated metadata. Metadata differs only by Windows CRLF;
the SDK's trailing commas were handled explicitly in a derived in-memory copy,
without changing any retained resource. Each actual module contains the complete
**4,545-byte nominal profile exactly once**, with SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Both include the exact source notices and the locked 1,094-byte SDK license.
The registry source has 45 records. The actual hosted logs separately confirm
45 exported descriptors and 2,002 conversions; static metadata alone was not
represented as a complete parameter-export test.

Direct import-table inspection identifies four Linux runtime libraries and
Windows APIs/MSVC/UCRT imports; none is separately bundled in these payloads.
The full names are retained in the review and local tool outputs. This is not a
transitive runtime-license review or clean-OS execution. No PDF, capture, SDK
source tree, SDK utility, test program or Python interpreter is among the actual
bundle members.

Windows also contains the exact SDK `VST_Logo_Steinberg.ico` as `PlugIn.ico`:
254,170 bytes, SHA-256
`1dda09aceb9fa930a3894cce4ad57edd8fa48ce58157c97ba5f971d2d4e79821`.
The 44-byte `desktop.ini` matches its selected SDK template. The pinned helper
supports an existing original `SMTG_PACKAGE_ICON_PATH` before plugin creation;
empty/missing paths fall back to the SDK logo. Root requested that this be
retained as a concrete future asset/branding/package decision. No SDK/build or
icon mutation was made, and no branding clearance is inferred from the MIT text.

## Observed executions versus new audit work

Downloaded Linux job **131852884056** logs report **8/8 native suites in 5.70
seconds**. Windows job **131852884109** reports **7/7 in 5.80 seconds**. Both
completed inventory and actual artifact upload. The log checks include 229,725
ABI reference frames, zero maximum audio error, 45 descriptors, 41,795 controller
checks and the SDK validator's 47-passed/zero-failed summary. Those are observed
previous hosted executions, not new test runs by this worker. Their documented
teardown/unsupported-rate diagnostics and DAW/device limitations remain.

The pinned inventory source reviewed here is the W7 version, SHA-256
`9f72e3c70b4b25008c40319b96e389b79cbcb6ab18821622c0f771b2c4071ad3`.
Its test SHA-256 is
`c99f64ea9761e57ddf44a46981f728d310ff202e89a39d237adbcfff07a3f8af`.
Assignment 51's later Windows reparse repair requires its own tests and exact
platform result. This audit did not inherit that repair or claim universal
live-filesystem link/race admission from a finite downloaded-archive check.

## Local receipts and handoff

Scratch evidence is under `a52-dependency-artifact-audit` beside the repository:

| Receipt | SHA-256 |
| --- | --- |
| Independent `audit.py` | `c12eef8d53880bb6ae7c92c188619f2a6133f784ddbcb2e0175baed68e7abe98` |
| Structured `results.json` | `aa14c6afb7de2a32464a008e5bb1566fd8e769f611b1cb5bb1af39ce4dd0eb01` |
| Fresh `remote-observation.json` | `dc7eceb56548df3a4770b93ba608fad7133c7b43de4bf87956667a30d3145f2d` |
| Pinned SDK README | `83165df5693e3e77e58fad66b784a3e1b0c7eb8faedffd74fd5c4c453441f3b1` |
| Pinned root SDK license | `e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e` |
| Linux dependency inspection | `9bffb82f5e06b5fe7a40e0cf174ff5a3455220881098b322806b75fe5a76a1b7` |
| Windows dependency inspection | `84ace5ff56ccf5d1a7d1385a0c971af921cf90d048ac9921ee36005ad69e51da` |

Final documentation checks found **47 resolving local Markdown links**, valid
UTF-8/LF text, final newlines and no trailing whitespace. Scoped `git diff --check`
passed. All fourteen inspected source identities and both five-checkout SDK
trees were rechecked unchanged after the documentation edits.

Root owns acceptance, staged-source integration, full checks and commit/push.
Integrate only these three completed documentation files into the next review
checkpoint. Preserve exact lock/notices bytes and all prior artifact histories.
Reinspect actual final platform payloads after any source, notice, icon or runtime
packaging change; qualify the reparse repair separately. Project license,
supplied research-asset permissions, future captures, intended branding,
clean-system runtime support, DAW/device use and signing remain concrete
unclosed release decisions. No staging, commit, push or subagent was performed.

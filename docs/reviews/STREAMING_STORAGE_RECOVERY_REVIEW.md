# Streaming storage and recovery review

A57, actual worker `/root/w10_a57`, wave 10; 16 November 2026. Read the entire
`AGENTS.md` and complete `docs/PLAN.md` before this bounded audit.

## Finding and scope

**Storage is ample; no cleanup is needed or proposed.** At
**2026-11-16 01:43:02 UTC**, `df -B1` and `statvfs` agreed on
**51,162,886,144 available bytes (47.649 GiB)**. The explicitly owned areas below
occupied **400,916,480 allocated bytes**, including the checkout's Git objects.
The source, compact original reports/logs, selected captures and recovery
instructions are recoverable through Git. Original executable bytes remain
scratch-only; their hashes and rebuild recipes do not make those bytes durable.

The reproducible [audit script](../development/2026-11-15-streaming-continuation/reports/A57-storage-recovery.py)
and [machine-readable receipt](../development/2026-11-15-streaming-continuation/reports/A57-storage-recovery.json)
record commands, identities, sizes and checks. Receipt SHA-256:
`a3c06fa74aaedde28f50389bd10b8b71d69f3843b16bd6643cf5f45fdada3799`.

Scope was the owned checkout, `../build-native`, `../baseline`,
`../resource-work`, `../compatibility-work`, and 50 explicitly named root
scratch files. No other workspace, dependency or session checkout was scanned,
changed or deleted. No configure/build, CTest, broad suite, cleanup, production
source edit, index/ref write, fetch or commit was performed. Only A57's assigned
review/note/report paths were written.

HEAD was `2f57723d9ec806fe8f721c317ef8c1a38d63b532`, tree
`cee5fdc4b07d95185ebd9e4d1c5f236f88a787f9`, parent
`af2b74760ee195c9497b314a1a29172f5238dd44`. The local `origin/main` agreed.
HEAD and index bytes remained unchanged during the recorded audit. This is a
local observation plus examination of retained publication receipts, not a new
remote or hosted-CI observation.

## Exact bounded footprint

`du -x -B1 -s` reports allocated bytes; the named root files use `stat` blocks.
These are point-in-time values before the final receipt/review/note writes, not
an estimate of all other sessions' disk use.

| Owned area | Allocated bytes | Retention treatment |
| --- | ---: | --- |
| `Hammond-B3-Organ` checkout, including Git | 249,315,328 | Preserve source, evidence, index and working overlay |
| `../build-native` | 111,607,808 | Coordinated build; includes currently qualified original executable bytes |
| `../baseline` | 17,973,248 | Preserve genuine before binaries, painter, profile and dry WAV |
| `../resource-work` | 143,360 | Optional generated instrumentation and its local executable |
| `../compatibility-work` | 45,056 | Regenerable candidate dry fixture and process output |
| 50 named root files | 21,831,680 | Extracts, raw logs, inventories and transport payloads |
| **Total named owned footprint** | **400,916,480** | **No deletion warranted** |

The filesystem reports capacity **67,586,535,424 bytes**, used
**12,970,901,504 bytes**, and **21%** utilization. `statvfs` total free space is
**54,615,633,920 bytes**; its ordinary available-space value is the smaller
**51,162,886,144 bytes** used above. These meanings must not be interchanged.
The checkpoint's approximate “51 GiB free” is older/coarser wording and should
be refreshed with a dated measurement; current availability is approximately
47.65 GiB, with no pressure implied.

The largest named root intermediates are `publication-payload.json`
(9,905,554 logical bytes), `staged-binary-transfer.json` (6,966,832) and
`repair-publication-payload.json` (1,283,390). Together they are 18,155,776
logical bytes. They are publication transport material, not substitutes for
the published source/evidence. Their presence does not justify cleanup now.

## New Git objects and compiled artifacts

The two-commit continuation range
`4aac394cde4da40906b615573a8779aee2d9a37a..2f57723d9ec806fe8f721c317ef8c1a38d63b532`
introduced **258 distinct blob objects / 8,149,245 logical bytes**. This is the
uncompressed size of newly reachable blobs, not incremental packed disk use.
The five largest are genuine gallery PNGs:

| File under `examples/demos/upper-rack-material-v1/images/` | Blob bytes |
| --- | ---: |
| `play-pedal-focus-1672x941.png` | 710,885 |
| `play-reference-1672x941.png` | 710,745 |
| `play-toolbar-focus-1672x941.png` | 710,305 |
| `play-minimum-active-1400x820.png` | 541,838 |
| `service-reference-1672x941.png` | 412,302 |

Other relatively large new blobs include the retained development log
(274,284 bytes), A30's compatibility receipt (212,947), and A20's physical mask
(206,442). No new blob exceeds 710,885 bytes.

The audit inspected **268 distinct new or changed-path blob versions** across
both commits, including reused objects placed at changed paths. ELF, PE/DOS,
Mach-O and native archive magic checks found **zero compiled binary objects**;
changed-path checks found **zero executable/object/library/cache/build-output
paths**. Intentional binary evidence remains present: PNG and gzip bytes are
not executable build outputs. This result is scoped to the continuation range,
not every commit predating its base.

## What survives a scratch loss

| Evidence or resource | Observed retention and recovery limit |
| --- | --- |
| Original qualification/failure logs | Eleven selected gzip archives reproduce **3,752,598 original raw bytes** with every recorded SHA-256 matching. Their archive bytes also equal HEAD. This includes baseline, coherent/final qualification, repair execution, failed Windows execution and the A20 report. |
| A20 comparison report | The committed 71,353-byte gzip decompresses to the exact **3,045,042-byte** original report, SHA-256 `20651ce04553a3cfd1d56c9c8e997765072d3d0223b1b5cc28aff0816cb0bbf9`. The report and mask preserve original results and per-frame identities. |
| Passing paired raster buffers | The comparison tool writes image artifacts on failed comparisons. The passing 96-pair run does **not** provide an immutable archive of every original raw raster buffer. Re-execution is new evidence and cannot recover otherwise unretained original bytes. |
| Actual application gallery | **Twelve PNGs** are tracked, and all working PNG bytes equal HEAD. These selected lossless captures retain their own source/state/provenance; they are distinct from the 96 paired fixture buffers. |
| Original before binaries | The named baseline application and both comparison binaries are present and match their receipts. They remain outside Git. After scratch loss, source/configuration can support a rebuild, but it is not the original executable. |
| Candidate and diagnostic binaries | The current application, renderer, trajectory probe, paired fixtures and optional instrumentation binary match their named receipts. Their original bytes also remain local-only. Preserve them while current review or reproduction requires genuine before/after inputs. |
| Dry fixture/profile | Baseline renderer, profile and original WAV match A30's identities; the candidate WAV matches the same whole-WAV hash. The original bytes are local-only. A30's decoded-PCM identity remains distinct from the older report's mislabeled whole-WAV field. |
| Atlas reading context | All six existing root extracts match the six recorded reading-receipt hashes. The committed coverage record and substantive reader notes retain the already completed 500-page coverage; this audit does not claim another reading or another worker. |
| Build and transport intermediates | Build caches/objects/generated headers, generated instrumentation, duplicate extract/log copies and publication transport payloads are potentially regenerable. Regeneration must retain original results and distinguish newly produced bytes from an original observation. No deletion is proposed. |

The baseline and candidate application hashes are respectively
`eb9a501ec60d5a90a398ffbf14e21a21967712589c155b54c8be164a71bd823c` and
`c29495e98148767c0d55cab4adc18a245659cea891deb0f37fa160ea976c3cc1`.
Preserving these hashes is useful provenance; it is not a durable binary archive.

## Recovery routes and current refresh

All **25 named recovery files** exist. The bounded file-link check found no
missing targets among **1,283 relative links** in those documents; this checks
file existence, not anchors, external sites or substantive correctness.

| Recovery need | Verified route and boundary |
| --- | --- |
| Permanent rules and complete plan | [AGENTS](../../AGENTS.md), [complete M0–M9 plan](../PLAN.md), and [project guide](../PROJECT_GUIDE.md) retain ownership, separate gates, all milestones and historical source/reading routes. |
| Live context and staffing | [Session entry](../development/2026-11-15-streaming-continuation/README.md), scope, checkpoint, actual ledger and its matching checker are present. Snapshot: **56 records / 53 accepted**; A57 was not yet inserted. Root's active refresh owns subsequent facts. This audit makes no strict-closure claim. |
| Qualified current source | [Repair qualification](../development/2026-11-15-streaming-continuation/reports/windows-repair-qualification.json) and its compressed inventory bind **505 files**; every current file hash matches, the compressed inventory raw hash matches, and none differs from HEAD. The inherited publication/final-coherent receipts remain separate original observations. No tests were rerun. |
| Publication identities | The implementation receipt/manifests match `af2b747` commit/tree/parent and all **243 entries**. The repair receipt/manifests match `2f57723` and all **64 entries**. Both manifest raw hashes match. A57 verifies local identities and retained prior API/fetch statements, not fresh remote state. |
| Normal setup | [README](../../README.md), [MIDI/platform setup](../MIDI_EXPRESSION_GUIDE.md) and [installation](../STANDALONE_INSTALL.md) give clean-checkout prerequisites and locked dependency acquisition. Existing external dependency paths confer no ownership. |
| Recovery build | [Status](../STATUS.md) and [handoff](../PRODUCT_HANDOFF.md) distinguish the coordinated dummy-SDL Release build from a normal native desktop configuration. The absolute scratch path is a current location, not a durable dependency. |
| Concrete continuation | [Next steps](../NEXT_STEPS.md), the causal-grid guide, full plan and latest log preserve next converter/audio/capacity contracts, material/display/accessibility work, owners and unresolved physical/product gates. |

**Known final-refresh work remains with root.** At this snapshot the live
checkpoint/ledger differed from HEAD, and `repair-publication.json`, its late
supporting records and later worker reviews were not yet committed. Current
README/status/plan/handoff/log prose still contains earlier publication/hosted
pending statements. Root reports all thirteen repaired-source jobs successful;
A57 did not retrieve hosted results and does not turn that report into
independent CI evidence. The final exact-source hosted receipt, actual worker
closure, fresh current-document claims and this A57 handoff require root's
remaining integration/publication. These are anticipated closure actions, not
an invented storage or product gate.

Before ending the session, root should finish the actual ledger and current
checkpoint, retain the matching strict result only after all sixty actual
workers are accepted, integrate the exact-source hosted/publication receipts,
and publish the accepted documentation/evidence using the established guarded
nonforced process. Preserve the present scratch-only original binaries and
state that their original bytes will be unavailable if scratch is lost. There
is no reason to delete them to free space now.

## Reproduce this bounded audit

From the owned checkout, the following reads only the allowlisted storage and
Git/source records, then replaces A57's own JSON receipt:

```sh
python3 -B docs/development/2026-11-15-streaming-continuation/reports/A57-storage-recovery.py
```

A later invocation is a new timestamped snapshot and changes the receipt hash.
It does not qualify a new build, publish work, prove external worker dispatch,
close physical/product gates, or make scratch binaries durable.

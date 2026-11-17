# Console resource and preservation admission

Reviewer **A39**, wave 7, 17 November 2026 UTC. This is a read-only source,
identity and storage audit of the owned checkout and six authorized sibling
directories. The [dated report](../development/2026-11-16-console-completion/reports/A39-resources.json)
was written before this review. No build, test, native process, deletion,
archive, Git object write or unrelated-workspace traversal was performed.

## Storage decision

**The observed storage margin supports continuing the authorized work without
cleanup.** At **04:58:25 UTC**, the filesystem had **48,286,797,824 bytes
(44.97 GiB) available** and **4,040,789 free inodes**. The seven owned scopes
used 766,840,832 allocated bytes in total. Measurements use `statvfs` and
`du -s -B1`/`du -sb`; allocation and apparent file length are distinct.
Root's final gallery was active during this snapshot, so these are dated
sizes, not final capture sizes or future capacity guarantees.

| Owned scope | Allocated MiB | Apparent MiB |
| --- | ---: | ---: |
| Repository, including Git and retained evidence | 507.05 | 493.40 |
| `../build-native` | 161.97 | 159.10 |
| `../a32-headless` | 10.01 | 8.80 |
| `../baseline-native` | 14.96 | 14.95 |
| `../qualified-p1-before-recall` | 11.18 | 11.17 |
| `../p1-timing-qualification` | 23.16 | 23.12 |
| `../atlas-text` | 2.98 | 2.96 |

Within the repository, the session reports occupied 142.09 apparent MiB;
paired-v1 and paired-v2 each occupied 62.18 MiB. The largest new file was a
3,273,075-byte compressed frame stream. These nested figures must not be added
to the repository total.

All **140 same-named v1/v2 stream pairs are byte-identical**. Their 280 paths
contain 130,045,026 bytes but only **70 distinct Git blob contents**, totaling
65,019,549 payload bytes. Normal content-addressed Git storage can retain both
run paths while sharing identical objects; working-tree copies still occupy
space. This is a deduplication opportunity, not a prediction of packed size or
evidence of publication. Keep both reports and their original stream paths.

## Source bounds and measurement limits

The [frozen P1 contract](../design/PERFORMANCE_PLATE_P1_CONTRACT.md) and
[independent arithmetic admission](PERFORMANCE_PLATE_P1_DESIGN_ADMISSION.md)
agree with the current painter insertion: 98 integer boundaries, 1,455 cached
doubles, 120 field doubles and 13 knot doubles give **13,096 bytes of named
array payload** on the specified ABI. There are 8,192 grain marks and 16,384
mixer calls. Drawing work is at most **97R + 8,192** primitives: 20,899 at
canonical R=131, or 231,292 at the conservative full-domain R=2300 ceiling.
The 64-row resource crop bounds 14,400 primitives and proves no whole-frame
containment.

P1 introduces no application-owned heap, texture, image-sized storage,
persistent cache or I/O. These are source bounds; fixed scalars, compiler
layout and SDL internals are outside that payload. This audit establishes no
measured stack/RSS ceiling, observed zero-allocation scope or callback deadline.
The separate timing batch remains a descriptive shared-host observation.

[LibraryModel](../../apps/standalone/LibraryModel.h) admits at most **128 catalog
entries**, **512 directory items**, **48-byte names** and **256-byte diagnostics**;
the existing storage layer permits 32 temporary-name attempts. Bounds precede
catalog count additions and copying. Four `uint64_t` mutation counters check
their configured ceilings before increment, reject exhaustion and never wrap;
the 2,000 ms acknowledgment deadline checks addition overflow. State retains
one operation, receipt basis, reference and pending catalog request rather than
an accumulating history. The model contains no filesystem operation, Session
post/read, clock or audio callback work. Its pimpl, strings, vectors and copied
`view()` values can allocate on the main thread: it is not an allocation-free
audio object. Native browser integration remains separate.

| Evidence transport | Enforced source limits |
| --- | --- |
| P1 comparator | At most 70 commands; 120 seconds each and 1,800-second launch/run budget; 36,025,169-byte frame stdout, 64 KiB stderr, 16 MiB report, 160 artifacts and 2 GiB retained-artifact ceiling; bounded decompression and trailer refusal. |
| Frozen timing runner | Eight sequential processes, 30 warmups/300 samples each; 180 seconds each, 1,500-second batch; 128 KiB stdout and 64 KiB stderr each, 1,572,864 total raw-stream bytes; 4,096 identity files and 512 MiB total identity bytes. |
| Supplemental Flat capture | Two processes, 180 seconds each/370-second batch; 6,358,945-byte stdout and 64 KiB stderr each; exact 6,293,408-byte RGBA payload; zero timing samples. |

These transport limits do not bound all Python allocations or hashing/report
wall time. The **existing interface-gallery driver has a narrower guarantee**:
13 or 15 cases, integer replay scale 1–10 and finite 4–60-second child timeout.
Root selected scale 3/30 seconds for the SHA-pinned, source-qualified app.
Its `subprocess.run(capture_output=True)` has **no explicit stdout/stderr byte
ceiling**; unexpected output is rejected after collection. Preserve actual
stream extents for the final run. The large observed disk margin and finite
trusted-app workload do not turn this into an arbitrary-child memory bound.
No transport rewrite or duplicate experiment is part of this audit.

## Dependencies, originals and optional later cleanup

The unchanged lock pins **SDL 2.32.10**, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. Own native/headless caches record
reuse of the existing CMake 4.0.3/Ninja paths and GNU 14.2.0 toolchain. MIDI and
VST3 remain disabled here; the headless configuration also disables standalone
SDL. CMake adds project source/tests to existing targets, with no new third-party
runtime dependency or runtime art. Existing optional Pillow remains an authoring
dependency. Borrowed dependency directories were not traversed or rehashed.

Direct hashes and base-byte comparisons confirm the unchanged atlas PDF
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`,
reference JPEG
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`,
reference provenance, SDL lock and verifier. No asset/dependency directory
changes were observed.

All four entries in the baseline preservation receipt and all eleven retained
binary/source entries in the pre-integration receipt still match. Keep original
failures, binaries, raw receipts, source snapshots and recovery manifests.
The **original before painter object was not retained**. The newly compiled
object and reconstructed benchmark are supplemental ancestry: the reconstructed
binary currently equals all 3,756,168 bytes of the genuine retained benchmark,
but does not restore the missing historical object or compiler observation.

After independently verified publication and completion of active readers,
root could remove only the **nine named atlas extraction files** and **ten
named library-test object files** enumerated exactly in the report, while
preserving source, manifests, binaries and raw evidence. Together they account
for just 5,262,497 apparent bytes. This is optional and presently unnecessary.
No whole-build, baseline, timing, source-history or other-workspace cleanup is
admitted here. Recheck available space before any later substantial capture or
build; this audit accepts neither the final full-suite outcome nor the active
gallery's eventual result.

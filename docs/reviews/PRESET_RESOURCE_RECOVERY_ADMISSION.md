# Preset resource and recovery admission

**A47, wave 8; 16 November 2026.** Admit bounded storage use and preservation of
this session's original evidence. This is an inspection of retained files and
records, not a new build, capture, audio render, benchmark or hosted run. Exact
sizes, hashes, commands and limitations are in the
[audit receipt](../development/2026-11-16-preset-library-continuation/reports/a47-resource-recovery.json).

## Resource boundary

The 12:39 UTC sample found **43,169,308,672 bytes available**, about 40.2 GiB, on
the shared filesystem. This session's visible files occupied 538,275,453 apparent
bytes, approximately 513 MiB. Size inspection stayed within this session;
other sessions' contents and disk use were not inspected.

| Retained item | Apparent file bytes | Finding |
| --- | ---: | --- |
| Coordinated `../build-native` | 150,030,166 | Only native configuration |
| Distinct `../a38-headless` | 5,716,878 | 7,049,216 allocated bytes including directories; justified SDK-free configuration |
| Genuine `../baseline-native` | 10,837,737 | Seven original binary/fixture/list files retained |
| Thirteen-view gallery | 6,635,660 | 63 files; all 61 manifested payloads match |
| Original audition archive | 1,698,038 | All 101 original files preserved |
| First publication scratch | 10,204,728 | 41 base64 encodings and three recovery records |

Only two directories contain both a build cache and Ninja graph. A38's separate
configuration has standalone/MIDI/VST3 disabled and empty SDK roots; this property
cannot be established by the native configuration. Its
[admission](HEADLESS_REGISTRATION_BUILD_ADMISSION.md) records the bounded eight
targets and twelve selected CTests. Archived gallery cache snapshots are evidence,
not additional builds. Scratch probes, installation fixtures and ignored auditions
remain small and separately owned. No cleanup is required to relieve immediate
storage pressure.

## Tracked files, ownership and originals

The session delta against `54df95f` contains no compiled executable/archive magic
or accidentally tracked build outputs, temporary encodings, object files or Python
caches. Canonical registrations, the masked asset, lossless gallery PNGs and
compressed evidence are intentional deliverables. Builds and generated headers
remain outside the checkout; `/out/` auditions remain ignored.

All **31 core headers, 30 core sources, 20 plugin files and 72 pre-existing data
files** match the base byte for byte. `main.cpp` and both UiModel files also match.
The shared registration path repair is explicitly root-owned. All **45 accepted
notes** match the ledger; A46–A48 remain running in the observed 48-worker record.

All seven genuine baseline files match their original receipts, including the
pre-edit raster executable and frozen fixture. Eight preserved baseline/integrated
log checks pass. Original setup, observer, audition and hosted failures remain
present. Root's source-bound **234/235** run, its later documentation-only repair,
and the Windows guard's separate **6/6 Linux** qualification retain distinct
identities; this review does not promote them into a fresh all-platform pass.

The archive SHA-256 is
`e61f5ff3b95966504f4261914339bc0eee759db1837993bbf9d29742b81f9858`.
Every member matches both its recorded hash and ignored original. All 32 WAVs,
16 exact whole-file pairs and 32 relative report links survive; no unsafe archive
paths or links occur. The
[reader](../development/2026-11-16-preset-library-continuation/reports/starter-auditions.md)
explains extraction. All 148 gallery source hashes resolve in the first published
tree. Its captured executable still matches; subsequent source differences are
explicitly recorded. Converted BMPs were deliberately removed after lossless PNG
verification and are not claimed present.

## Publication and context recovery

The first publication's local `d281d4e` and provider `20739f6` retain the same
`1e597764…` tree and sole base parent. All 251 scratch tree entries match committed
objects. The local preservation branch exists. No fresh remote query was made by
A47. During inspection root committed the follow-up as `503ed724`, tree
`201e38b0…`, parent `20739f6`; the final observed index is empty while active
reviews remain untracked. This is not a clean-final-checkout claim.

Resume through AGENTS, the session README, checkpoint, ledger and
[publication receipt](../development/2026-11-16-preset-library-continuation/reports/first-publication.json),
then inspect live local/provider state. Wave 9 must update global navigation that
still leads with older runtime/conversion sessions. Genuine baseline binaries are
local preservation files, not clone contents; retain their directory through
handoff. Rebuilding does not recreate original execution artifacts.

After independently verified final publication, root may optionally remove only
the **41 enumerated `.b64` files: 7,513,888 bytes**. Every encoding regenerates
exactly from its committed blob. Retain manifests, tree payload, verification and
failure records, source, baselines, original auditions, galleries and notes.
Nothing was deleted. Use verified immutable blobs, a SHA-only tree and a fresh
expected parent without force for subsequent publication. Exact Windows hosted
results, all sixty accepted workers and strict closure remain separate next steps.

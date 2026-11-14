# A52 recovery session note: bounded input and macOS workspace fixture

**Newly authored recovery documentation, 14 November 2026.** This note records
work already completed by the same actual assignment **52/60**, logical wave
**9**, worker `/root/w09_a52_bounded_native_burst`. It adds no worker or dispatch.
It was authored through GitHub while the shared workspace was unavailable.
Its text is new; it is not a recovery of the unpublished local note, review,
qualification helper, or raw diagnostic files.

## Outcome and evidence boundary

Before the outage, the approved macOS header-matrix fixture repair passed the
complete affected workspace suite once: **6/6 methods and 30/30 native
processes**, with **14 deliberately corrupted cases rejected**. Root and A60
accepted the source and completed local result. No additional native execution
was performed for this recovery note.

The exact qualified fixture is published in
[recovery commit 6f69c68](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/6f69c68ed5bf51d77dba1ae4f75d4bc75d144747).
Its SHA-256 is
`0488bc549bbe4475fac8daa4f5d69c76a58db5ca7a94f1ff7e146f7ac11c0692`.
During this recovery task, I fetched the
[published fixture at that exact commit](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/6f69c68ed5bf51d77dba1ae4f75d4bc75d144747/apps/standalone/native_tests/test_standalone_workspace_replay.py)
through GitHub and independently reproduced that hash over its 31,885 UTF-8
bytes. This verifies recovered source identity; it does not repeat execution.

The new hosted result was **pending at this note's authoring cut**. The original
macOS failure remains a failure. The raw local 30-process evidence cannot
currently be retrieved from the unavailable workspace and is not included in
the smaller source-recovery commit. The
[root workspace recovery record](reports/root-workspace-recovery.json)
separately identifies the observed qualification, source recovery, unavailable
artifacts, and remaining hosted work.

## Preserve the original A52 work

The [original published session52 note](session52-bounded-input.md),
[bounded-input review](../../reviews/INTERFACE_BOUNDED_INPUT.md), and
[original A52 final result](reports/a52-final-result.json) retain their original
scope and claims. They cover the earlier A49 startup-baseline repair, the
zero-packet MIDI timestamp assertion, the corrected 16-process suite, and the
separate 256-action native burst. They are not reports of the later 30-process
header-matrix qualification.

I verified through GitHub that the original session52 note at recovery commit
6f69c68 is byte-identical to its text at parent
`b1efcdfc34cde92e07f2f6bcb563fc12701dfc01`. The original review and final-result
links also resolve at the recovery commit. This new note does not edit any of
them. Before the outage, the later qualification helper additionally verified
all **180 original A49/A52 report files** against the published originals.

## Observed macOS failure and narrow repair

The published parent b1efcdf hosted checkpoint completed 12 jobs with 11
successes and one failure. The
[original macOS job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43601574718/job/132467248056)
finished **37/38 CTest tests**, failing
`test_pointer_header_matrix_preserves_keyboard_space_and_exact_save` at
1399 x 820. The previously repaired synthetic MIDI/UI method passed.

The original header script pressed Upper A at 180 ms and Space at 320 ms.
A58 retained these relevant observations before the outage:

| Elapsed ms | Applied / resolved | Submitted | Held notes |
|---:|---:|---:|---|
| 53 | 5 | 5 | Empty |
| 356 | 5 | 7 | Empty |
| 440 | 7 | 7 | Upper 60 and Lower 60 |
| 1675 | 8 | 8 | Upper 60 |
| 1896 | 9 | 9 | Empty |

The observation stream did not include applied sequence 6, the first
Upper-only state. The 356 ms row legitimately reports the still-applied empty
state while two note commands have been submitted. The trace does not
demonstrate a lost note. It does fail the original required chronological
hold-state list, and later assertions in that failed method were not reached.

Root approved, and A60 independently reviewed, two bounded prefixes for each
of the original seven sizes. Both use the same executable, size, dummy
environment, and exact original `NONCANONICAL_STATE` as the full journey:

1. Run only original events before 180 ms for 250 ms. Require unchanged
   controls, empty holds, zero On/Off commands, and a fully acknowledged
   pre-shutdown startup sequence. Require the input state bytes to remain
   exactly noncanonical.
2. Run only original events before 320 ms for 250 ms. Require exactly one On,
   no Off, exactly one additional command, and acknowledged Upper 60 ownership
   before shutdown. Require unchanged controls and the same exact noncanonical
   bytes. This prefix need not incidentally sample an initial empty row.
3. Run the original full 2250 ms journey without changing any action or action
   time. Require the original control, view, canonical Save, and screenshot
   assertions, two On/two Off commands, and exactly four post-startup commands.

Every full-run observation is checked against this independent literal map,
using the copied **applied** sequence rather than the independently sampled
submission counter:

| Applied offset from startup | Required held state | Earliest original action time |
|---:|---|---:|
| 0 | Empty | 0 ms |
| 1 | Upper 60 | 180 ms |
| 2 | Upper 60 and Lower 60 | 320 ms |
| 3 | Upper 60 | 1600 ms |
| 4 | Empty | 1800 ms |

Full-run stages **0, 2, 3, and 4 remain mandatory**. Only stage 1 may be absent,
because its acknowledged owner is separately demonstrated by the second
prefix. Each sampled state must match its literal stage. Applied and submitted
sequences must be monotonic and bounded; resolved must equal applied; applied
must not exceed submitted; and elapsed time must be monotonic and no earlier
than the applied stage's original action. The final pre-shutdown state must
acknowledge the exact final command and be empty. Joined shutdown cannot
substitute for the original key releases.

Only the workspace test fixture changed for this follow-up. The production
application, MIDI helper, original scripts, seven sizes, 9-second child limit,
and 90-second suite limit remained unchanged. No build or configure operation,
full 147-test run, deadline increase, or retry was used.

## Complete local qualification actually executed

The approved command ran once before the outage:

```sh
python3 -B docs/development/2026-11-14-interface-continuation/reports/a52-macos-qualify.py \
  --executable ../a36-status-bin/hammond_standalone \
  --output docs/development/2026-11-14-interface-continuation/reports/a52-macos-local-suite
```

That helper and output directory existed locally when the command completed.
They are now inaccessible; the command above records the actual invocation,
not an assertion that its unpublished helper can currently be downloaded.

The pinned executable SHA-256 was
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
All **98 product inventory entries** remained unchanged; the applicable 96
A36 source entries matched the existing build. Source/executable snapshots
before and after the suite matched.

All 30 native applications exited zero. The six methods passed in 44.869
seconds of unittest time; the launcher observed 45.05869714799337 seconds.
These are observations from one run, with no performance, deadline, or leak
claim. CPU was released immediately afterward.

For the seven original sizes, the local evidence demonstrated:

- Fourteen prefix state files retained the exact original noncanonical bytes.
- Seven full-run saved files matched the canonical state bytes exactly.
- Seven original full scripts remained byte-identical to their previously
  published construction. The 1399 x 820 full script matched the retained
  historical macOS script.
- Each local startup prefix acknowledged sequence 3, each Upper-only prefix
  sequence 4, and each full journey sequence 7, with the required owner states.
- The existing harness exercised actual temporary BMP header/dimension checks
  and final-painted-record checks. BMP payloads were removed with the native
  temporary directories; their hash metadata was retained locally.

Explicit dummy SDL audio and video were used. The suite's synthetic MIDI path
did not select or enumerate physical MIDI hardware. These results do not
qualify persistent OS pointer capture, real display behavior, audible sound,
accessibility, or physical hardware.

## Negative checks and historical replay limits

The retained macOS diagnostics reproduced the old hold-list failure. The
repaired diagnostic oracle accepted the actual observations using their
observed startup sequence **5**, without fabricating any intermediate sample.

Ten independent corruptions of that historical diagnostic input were rejected:
missing initial stage 0, missing both-held stage 2, missing post-Space-release
stage 3, missing final-empty stage 4, a wrong original owner, an extra command,
a missing Off, incoherent resolved sequence, an applied Space stage before its
original time, and a submitted-sequence reversal.

Four corruptions of actual fresh local prefix evidence were also rejected:
an unacknowledged startup, a wrong Upper-only owner, a missing Upper On, and
a prefix that had implicitly saved or canonicalized its noncanonical input.
Those checks replayed the retained local method evidence and launched no
additional native application.

Historical macOS Save bytes and BMP bytes were unavailable. The new prefixes
were not executed as part of that historical run. Its diagnostic replay
therefore does not claim a complete historical method pass, a verified Save
file, a verified screenshot payload, or retroactive prefix execution. The
fresh local suite supplies those distinct prefix and file assertions; new
published macOS execution is a separate gate.

## Recorded identities and outage status

The following SHA-256 identities were recorded before the outage. The local
artifacts themselves remain unavailable; these identities are metadata, not
substitutes for their bytes.

| Local artifact | Recorded SHA-256 |
|---|---|
| `a52-macos-qualify.py` | `a10c41eb5230f7f3e876d7393c6bfee28b5158a370ac134c683db88a0e08d6d3` |
| `a52-macos-local-suite/result.json` | `4c5199f063d7acc0918e27ee60326a406e257106788fa3bc26fa76d81cc92385` |
| `a52-macos-local-suite/retained-macos-oracle.json` | `864486b84579a0272d9942b135b8a20ecae096d9ed2deb7ebeed34a22ee5654a` |
| Both source-before and source-after snapshots | `977ba10ff28bfd74321a37ad676d05a984d2bb836d330ec52aef9fb8afa8c7f9` |
| Each new startup-prefix script | `6554ab6b44d5a1e3c236b839ce06444edf5dbed62fab7660cc71ee540eaeac40` |
| Each new Upper-only-prefix script | `244a785caf7d7507a46988b472ad39666e034c58353380da65bf549a59a0de5f` |
| Original 1399 x 820 full script, also retained from macOS | `6255efef1b37d69d37b5ba7a1519c6478b12ae0bc1749b4d25e00109652e49db` |

A new local review and dated session52 append were written before the outage,
but their last packaging command failed before process creation. In particular,
`reports/a52-macos-final-result.json` and
`reports/a52-macos-fixture.patch` were never created. No final local link audit
or filesystem reconciliation is claimed.

Root's recovery record explains that the unpublished staged candidate and raw
local evidence were not uploaded. Root recovered the fixture from exact parent
bytes and the fully recorded approved diff, matching the qualified source
hash before publishing 6f69c68. This smaller recovery commit is distinct from
the inaccessible original staged tree.

This worker's only recovery mutation is creation of a new GitHub blob for
this note. Root owns tree/commit/ref publication and final accounting. A58 owns
the new hosted primary evidence. If workspace access returns, preserve its
worktree and index and reconcile in an isolated checkout as described in the
root recovery record; do not replace original report bytes with reconstructed
text.

## Acceptance and remaining work

A52's actual local repair qualification and corruption checks are complete and
were accepted by root and A60 before the outage. Source identity has now been
independently confirmed against GitHub's published recovery commit. This note
provides a separately labelled, attributable account while preserving the
original published session52 work.

The new hosted gate on the recovered source, retrieval of the original local
artifacts, and final session-wide publication/accounting remain distinct next
actions. This note does not relabel the original 37/38 macOS gate or the earlier
146/147 local gate, and it does not claim a new hosted pass.

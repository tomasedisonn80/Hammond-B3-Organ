# Final operator and UX review — A55

**Outcome: the documented musical journey is supported; two small navigation/copy
corrections and two clarity improvements are proposed. No new product defect is
established.** This read-only review used current source at `cdbb2be`, the working
[runbook](../INTERFACE_RUNBOOK.md) and [handoff](../INTERFACE_HANDOFF.md), and accepted
[A37 operator](INTERFACE_FINAL_OPERATOR_FLOW.md),
[A45 documentation](INTERFACE_DOCUMENTATION_FRESHNESS.md) and
[A51 visual](INTERFACE_FINAL_VISUAL_ACCEPTANCE.md) evidence. The
[compact record](../development/2026-11-14-interface-continuation/reports/a55-final-ux.json)
pins inspected inputs; this is no new native execution or image/hash acceptance.

## Operator journey

The README puts **Build and operate** before the gallery. The runbook distinguishes
installed launch from source builds, links the exact preset build procedure,
requires a writable state path and explains the absent-file audition baseline.
The handoff supplies native/MIDI configurations and relocation commands. This is
a discoverable route into the application; it also identifies the current local
SDL display-backend limitation instead of implying that dummy rendering opens a
desktop window.

Play retains both 61-key manuals and 25 pedals. Computer target/octave selection
and the three roving key groups provide keyboard access beyond the seventeen
computer-piano positions. Fixed C#–A, adjustable A#/B, Edit A/B and Cancel have
distinct meanings. `UiModel::activate` changes the editing bank without publishing
sound controls; `ControlState` reconnects only through an explicit routing change.
A37 exercised a retained-bank edit while Fixed F# continued, followed by Save and
live Load with the original held owner preserved. Focus on D# did not select it.

The persistence signals are separate. `UNSAVED` compares current controls with
the clean reference; pending describes acknowledgment. A clean audition baseline
can exist before a file is created. Save writes an acknowledged copy and marks
that exact copy clean; changes/recovery cancel a waiting Save, and its wait has a
two-second limit. **Loaded saved controls.** reports the load event; pending and
applied indicators still govern application status. A37 observed the corrected
notice after acknowledgment. The runbook explains pending accurately but would
benefit from the short dirty/status paragraph supplied below.

F4–F7 preserve musical state, focus memory and original release ownership; hidden
Play targets reject new activation. A37 covers navigation and minimum Flat focus,
while source confirms release handling precedes shortcut suppression. Opening
Help/Audio/MIDI deliberately releases UI holds and is documented separately.
Flat and keyboard access remain presentation capabilities, not a native semantic
accessibility bridge.

Rotary and Service advertise read-only information. Source rows explicitly retain
unconnected cabinet/scanner/AO-28 paths, unavailable rpm/V, unacquired geometry and
decorative artwork. Their labels do not promise working rotary controls. Audio
failure leaves settings available; the guide gives No input/Apply/Disconnect/Close
recovery after native MIDI discovery failure and explicit reconnection after
fault/Panic/audio restart. These instructions preserve recorded failures and do
not turn synthetic input into a physical-device claim.

## Exact bounded proposals

The [replacement blocks](../development/2026-11-14-interface-continuation/reports/a55-proposed-copy.json)
are proposals for root; A55 changed no shared guide.

| Priority | Finding and minimal action |
|---|---|
| Current navigation | The runbook's unqualified eight-image link still selects **v1**, and its closing paragraph calls that gallery a source overlay. Point current reproduction to **v2**, retain v1 as explicitly historical, and describe published product source with exact executable identity. |
| Copy ambiguity | README says C “momentarily” cancels. Source leaves routing disconnected after release. Remove “momentarily”; this avoids suggesting hold-to-mute behavior. |
| Operator clarity | Explain `UNSAVED`, the clean audition baseline, Load notice and acknowledgment separately. This documents existing behavior. |
| Reader-facing caption | Shorten the leading README provenance paragraph while keeping both evidence links, exact capture source and qualification limits. Full 98/13 inventories, tree/hash details and unchanged executable evidence remain in the linked gallery. |

## Next meaningful UX gate

A57's actual desktop flow remains pending: identify the compiled backend, observe
held ownership through navigation/resize and off-window release, and retain joined
cleanup. Then assess compact legends, focus, `UNSAVED` and genuinely pending/applied
states on an actual display at minimum/default sizes. Native accessibility still
needs an explicit platform bridge and assistive-technology acceptance.

A49 remains **146/147**; A52's fixture-only closure is separate. Twelve hosted jobs
at `cdbb2be` succeeded, without closing those UX gates. A51's known “1 targets”
copy issue stays low priority; literal reference equality remains explicitly
unmet. No physical sound, device, timing or complete M9 claim follows.

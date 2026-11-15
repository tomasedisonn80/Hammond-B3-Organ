# A49 — primary Linux hosted audit

Actual worker `/root/w09_a49_linux_hosted`, wave 9. Read complete AGENTS/PLAN,
current recovery/ownership records and A37/A38/A42/A45 evidence. Own only this
note, `PRODUCT_LINUX_HOSTED_REVIEW.md` and bounded A49 reports.

**Qualified source:** `d8c39f7986746eacc991747153c7dbb012bb9a32`, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`, parent
`d556da017ea0a5d4f2d231416782dbc5066e58c2`. Independently fetched GitHub commit
identity and all six completed primary job logs. CI run **43668397337**;
native run **43668397338**, both push attempt 1. Logs confirm GCC 13.3.0,
CMake/CTest 3.31.6 and Python 3.12.16.

| Job | Executed result |
| --- | --- |
| 132672791917, core Release | 155/155, 80.57 s |
| 132672792034, core ASan/UBSan/leaks | 155/155, 234.39 s |
| 132672792114, native MIDI ON | 48/48, 328.42 s |
| 132672792135, native MIDI OFF | 48/48, 327.47 s |
| 132672791944, native sanitizers | 21/21, 342.06 s |
| 132672791770, full R4 | Full pass, 722.029333257 s; 14 admission checks |

Native sanitizer proof includes **260 distinct instrumented compile commands**,
**21 instrumented executable links**, all six archive symbol assertions and
both runtimes for every executable. Exact discovery/execution matches all 21
required names. Real-entry calibration passes nine methods, ten subprocesses,
seven scenarios and two intentional failed replays; its instrumented probe hash
matches the inventory. The successful final check follows all scenario and
stderr assertions. No sanitizer diagnostic was observed.

All three native jobs report 1293 material assertions, zero failures, 109 frames,
212 explained clipped pixels and zero unexplained/literal mismatches. Release
jobs verify relocated 20-file ON / 16-file OFF packages and archived bytes.

Re-fetched original d556 GCC13 vector-assignment BUILD failure: all 33 retained
excerpt lines match; its tests never ran. d8 clear/push-back execution now passes.
b9 failures and local ptrace blockers remain; only the existing named core
quarantine leak exception is retained. No new suppression.

[Review](../../../reviews/PRODUCT_LINUX_HOSTED_REVIEW.md) and
[receipt](../reports/A49-linux-hosted.json) retain exact links, hashes, excerpts,
selections and limitations. Artifact payloads were not independently downloaded;
their checks were audited in executed logs/source. No local build/test/application,
source/workflow/shared-status edit or publication. Next: qualify A46/A48 and final
published source; dummy/synchronous fixtures do not establish hardware, driver
races, fidelity, accessibility or R5/R6 integration.

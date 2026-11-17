# Concurrent d2ed standalone record

Run [44034656779](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44034656779), attempt 1, tested exact source `d2ed03b94114e35d0caa65968d11afe896a5e9f5`. All six jobs are terminal: **five success and one Windows failure**. [Final metadata](final-metadata.json) binds all actual job IDs, runners, source identities, timestamps and step outcomes. No job remains live in this standalone run.

A53's bounded follow-up inspected the complete failing Windows log; the other root owns the complete non-Windows suite logs. Non-Windows per-test counts are not reconstructed from API conclusions.

Windows job **133874509242** compiled successfully and executed all **78 tests**. **75 passed; three failed**, in 550.83 seconds, exit 8:

| Failed gate | Seconds | Actual boundary |
| --- | ---: | --- |
| Title density | 0.29 | `view.controls.drawbars[0][1]` has length 0 instead of 9; no title cases completed |
| P1 numerical | 0.97 | One failed check out of 192; all 62 current-candidate screen criteria passed |
| H1 statistics | 0.55 | `session.controls.drawbars[0][1]` has length 0 instead of 9; zero of 103 numerical criteria evaluated |

The P1 native fixture itself passed 34 cases, 53,648 checks and 111 paintings. H1 native passed 48 cases, 10,542 checks and 163 paintings. The actual Python capture/H1/P1 source suites passed 45/24/54 methods. Calibration executed ten children and seven lifecycle scenarios; workspace replay executed 37 children; both real-application paint gates executed two children each.

The P1 stdout summary does not identify its failed check. A53 did not download its separately named temporary report and does not infer that check's cause from similar code. Post-acceptance source/dependency verification and final package/relocation steps were skipped after the failing CTest stage.

[The Windows receipt](windows-original-failure.json) and [original-block manifest](windows-failure-blocks.json) preserve the exact outcomes. The complete 659,407-byte original log is losslessly retained in 92,002 compressed bytes. Decoded SHA-256 is `d4c08f3bde380b7f69fdf8e26fde70b6a326125e4624f4713062036a341351fc`. Four exact CRLF excerpts preserve title, P1 native/numerical, H1 statistics and final CTest failure output; separate readable views are verified as newline-only transformations.

The later [combined focused run](../combined-focused/review.md) is a distinct nine-test result at source 5485988. It does not change this original failed result. No native execution, source edit, retry or remote mutation was performed by A53.

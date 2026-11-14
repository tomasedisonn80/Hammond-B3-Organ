# Concurrent calibration integration and Windows package fixture

## Source boundary and preserved work

After all sixty standalone assignments were accepted, root fetched and integrated
calibration publication `3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf`, tree
`656c5f117060210b3df656c62318d5a672fc306d`. Its replay, separate 57-file
CaptureTools component, resource profile, composition review and accounting
remain attributed to the independent calibration session. Its own
[103-suite local gate](CALIBRATION_INSTALL_REPLAY_INTEGRATION.md) retains its
original source identity; the [standalone platform audit](STANDALONE_FINAL_PLATFORM_AUDIT.md)
continues to qualify exact `6214032f`, not every later change.

The merged root source is local commit
`3e1a6cdec048d2b3926457cb2e20a6c4e7dedaa5`, tree
`4c2f1f6c9e31e364029cbc13ebb53165fc1be062`, with **993 tracked files**.
All standalone, core and plugin implementation inputs remain unchanged from
621. The concurrent top-level CMake delta includes the separate
`cmake/InstallCaptureTools.cmake`; its component is excluded from default
installation. The standalone nine-file component retains its own unchanged
contract. Shared status/log conflicts were reconciled by preserving both
tracks' complete results and current ownership. No agent was added or recounted.

## Focused frozen integration checks

Root archived that exact merged source into the private
`../final-remote-integration/source` and used Python 3.12.14, CMake 4.4.4,
`PYTHONDONTWRITEBYTECODE=1` and `LC_ALL=C.UTF-8` on Linux x86-64. Working
directory for both commands was that frozen source. The configured CMake was
provided through `HAMMOND_TEST_CMAKE`; no other checkout was modified.

```sh
python3 -B tests/test_capture_replay.py -v
python3 -B tests/test_capture_install.py -v
```

| Suite | Result | Unittest / process seconds | Complete log SHA-256 |
| --- | --- | --- | --- |
| Replay | 69/69 methods, exit 0 | 7.689 / 8.042 | `eb3b09227b887a52e8b37acde7a3463e09ea47a3b576e7dd997dac068d5ec83a` |
| Installation | 16/16 methods, exit 0 | 6.412 / 6.522 | `88b62a81a3295888f91c71b7a3388696a94d5f7ff215dd553c6b543a4dd1a56f` |

Every one of the 993 source files remained unchanged. These two focused suites
do not constitute a new unfiltered 112-suite native-enabled gate.

## Actual later Windows failure

At public 3b, actual Windows core
[job 132262885865](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43535351721/job/132262885865)
passes **102/103 suites** in 192.17 seconds. Its sole failing suite is
`python_test_capture_install`: 16 methods in 37.421 seconds, one failure and
one platform-capability skip. `test_late_install_abort_preserves_partial_package`
expected the sentinel `b"preserve other writer\n"`, but CMake's Windows
`file(WRITE)` produced `b"preserve other writer\r\n"`.

The expected install rejection, injected late-abort diagnostic and partial
package diagnostic passed before this comparison. The later retained-payload
count and exact copied-file checks had not run. This observed failure is
separate from the earlier Windows demo symlink-spelling fixture, which passed
at 621. The complete decoded Windows log is retained privately as
`../final-remote-integration/windows-before.log`, SHA-256
`d78273743d8a06f0fa3de6ede1420ea2e06fddaf1efbc3949457ea0f50180bf9`.

## Minimal correction and its local acceptance

Root changes only this test method's injected sentinel and matching expected
bytes: both now contain `preserve other writer` without a newline. The purpose
is exact preservation after the intentional late abort. The producer, install
script, package inventory, failure injection, required diagnostics, partial
payload bounds, copied-byte comparisons and existing capability policy remain
unchanged. No retry of the unchanged failing source is counted as a repair.

The private `fixed-source` contains the exact 993-file source above with only
`tests/test_capture_install.py` overlaid. Its corrected SHA-256 is
`7c6ee26c5721bd91c700769076d8615879ccaa85c9e523ca83addb0f45e0d89e`.
The same full installation command passes **16/16 methods**, zero skips,
failures or errors, in **6.262 seconds** unittest / **6.405 seconds** recorded
process time. All source bytes remain unchanged. Complete corrected log:
`../final-remote-integration/fixed-install.log`, SHA-256
`9bbf9b85f8c665e8216f06dd14806b4d11a5caee7049d802e9c12ed2885d82d0`.

## Published closure and completed hosted qualification

Root published the complete sixty-agent records and this correction at
[`27209a7fec075b082aa911c9ea2159938deaae85`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/27209a7fec075b082aa911c9ea2159938deaae85),
tree **`087d81ba1ea83834e866ab47cdd44a53fd9251ec`**, with guarded parent 3b.
The exact local equivalent is `9b68f77628d5c289ab878a811672ad7871eb57fc`.
Root fetched the public commit, verified exact tree equality and a clean worktree,
and preserved local history on `standalone-local-completed-session`.

All three workflows and all ten jobs are observed **completed/success** on that
exact source. Complete decoded job logs were retrieved. The retained
[machine-readable results](STANDALONE_CLOSURE_HOSTED_RESULTS.json) include public
run/job identities, source/tree, all ten test summaries and normalized log hashes.

| Hosted job | CTest result | Seconds | Actual job |
| --- | --- | ---: | --- |
| Core Linux Release | 103/103 | 84.62 | [132268583811](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087807/job/132268583811) |
| Core Windows Release | 103/103 | 181.38 | [132268583576](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087807/job/132268583576) |
| Core macOS Release | 103/103 | 103.58 | [132268583578](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087807/job/132268583578) |
| Core Linux ASan/UBSan/leaks | 103/103 | 128.30 | [132268583371](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087807/job/132268583371) |
| Standalone Linux | 14/14 | 79.78 | [132268583572](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087781/job/132268583572) |
| Standalone Windows | 14/14 | 95.03 | [132268583590](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087781/job/132268583590) |
| Standalone macOS | 14/14 | 80.72 | [132268583294](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087781/job/132268583294) |
| VST3 Linux | 8/8 | 4.26 | [132268583088](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087764/job/132268583088) |
| VST3 Windows | 7/7 | 6.80 | [132268583475](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087764/job/132268583475) |
| VST3 macOS | 7/7 | 6.40 | [132268583549](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43537087764/job/132268583549) |

Root downloaded the actual Windows core diagnostics, artifact **14090826655**,
**57,055 bytes**, SHA-256
`815a7cf38a935dcd1ac8843b86f022a936e83f946faa48508130eee71d70308f`.
All ZIP checks pass and its source-revision file matches 272. Its CTest XML
records 103 tests with zero failures, disabled or skipped outer cases. The
installation case is explicitly `status="run"`, 39.6261 seconds. Its internal
unittest output reports **16 methods in 39.501 seconds: 15 passes and one skip**.
The single skip is the existing POSIX-only DESTDIR method; the corrected
late-abort method passes. The JSON retains the original compact result markers
and their mapping to the exact source's default alphabetical unittest order.
The critical preservation case is not a skip or an inferred unchanged retry.

This completes the new Windows fixture gate. The original 3b **102/103** failure
remains intact above. Internal Python capability skips are distinct from outer
CTest counts. This follow-up does not repeat or extend the 621 standalone
package-byte/relocated-runtime audit, the 183 local 110-suite gate, or the separate
local native sanitizer scope. Later documentation records these outcomes without
changing the tested code. No sixty-first assignment, physical calibration,
device, accessibility, DAW or signed-release qualification is claimed.

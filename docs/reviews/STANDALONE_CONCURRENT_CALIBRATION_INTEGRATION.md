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

Fresh hosted Windows execution of this corrected fixture is the remaining
publication check. Its result must be recorded at the actual new public commit,
without relabeling the earlier 102/103 failure or extending the standalone
621 artifact audit. This root integration repair does not create a sixty-first
assignment or establish physical calibration, device or release qualification.

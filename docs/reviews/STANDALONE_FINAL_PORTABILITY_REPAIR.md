# Final Windows demo-fixture preservation repair

## Observed failure and cause

Assignment 60 inspected the complete actual Windows core log at public
[`183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e).
[Job 132254226441](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43532749364/job/132254226441)
passed **100/101** suites in 151.14 seconds. All four formerly failing audio/
corpus suites passed. The sole remaining failure was the independently added
capture-demo suite: 43 methods, one assertion failure in
`test_existing_dangling_symlink_is_preserved`.

The actual `Path.readlink()` result used Windows' extended-length target
spelling, `//?/C:/Users/runneradmin/.../absent-target`. The test compared it with
the creation argument `C:/Users/runneradmin/.../absent-target`. At the failed
assertion, `build_demo()` had already raised the required `DemoError`, and
`is_symlink()` had passed. The later absent-target assertion had not run.
The log therefore demonstrates a target-spelling oracle failure, not an observed
overwritten symlink. The raw decoded log is retained privately at
`../a60-final-platform/183/core-windows.log`, SHA-256
`7579875c99f672d280fb87ad28da1125d6f3270140ac640a8284c5b6851497f0`.

## Narrow correction and independent review

Root changed only this test method in `tests/test_capture_demo.py`. It records
the actually created link's `readlink()` result before calling the producer,
then requires that exact value afterward. It retains the expected rejection,
symlink type and absent target. It additionally compares the same `lstat()`
API's device, inode, mode, size and nanosecond mtime before and after the call.
No lexical path normalization is substituted for preserving the actual link.
No producer, schema, public policy, capability skip or CMake input changed.

The corrected file's SHA-256 is
`a0b5ed53d59ef91e224d477b5996ca1f7f594d8f3d4a7592559e0352bba03112`.
Assignment 59 independently reviewed the original assertion boundary and new
diff, then executed the exact corrected method: **1/1 passed** in 0.008 seconds.
Its separate [repair review](STANDALONE_REPAIR_HANDOFF_REVIEW.md) retains that
scope. This root integration repair is not another dispatched agent or a new
claim of authorship for the earlier calibration producer fixes.

## Actual frozen local acceptance

The private `../final-demo-portability/source` is the **957-file** exact 183
archive plus this single changed test file. The other **956 files** remained
byte-identical before and after verification. Python 3.12.14 ran on Linux
x86-64 with `PYTHONDONTWRITEBYTECODE=1`:

```sh
python3 -B tests/test_capture_demo.py -v
```

All **43 methods passed**, no skips, failures or errors, in **1.663 seconds**
of unittest time / 1.922 seconds recorded process time. The original strict
canonical-byte, complete synthetic-archive, failure-preservation and bounded
job/study assertions remain intact. The complete log has SHA-256
`0c93bef6aae3970543e97c078a1d54802f5281536a73a232b179bdc26d58e19a`.

An independent local negative control uses a real relative dangling symlink to
the same intended absent target. It changes only fixture creation spelling,
without mocking `readlink()` or the producer: the fixture's ordinary
`make_symlink(destination, target)` call receives
`Path(os.path.relpath(target, destination.parent))`. The original method fails
its absolute-target comparison; the corrected method passes and retains the
exact relative link plus metadata. Both executions run one method with no
skips or errors. This demonstrates sensitivity to the spelling assumption;
it does not emulate Windows namespace handling.

The private probe's SHA-256 is
`d6bba82c97c63e3748411516e5a260ae0f7624bef3243ffcdd03afc5b601404f`.
Original failing probe log:
`314bb99f6c53bf62bf837d85382e7bbbac22222ab4e690645a8a559a111a6dd3`.
Corrected passing probe log:
`f898a8ae52515a472a6400b372b5fde8e5e9adf979ad3452d7969ddd5712a9da`.
The first full corrected local suite passed; no unchanged failing retry was
used to claim repair.

## Publication and remaining platform evidence

The fix and independently reviewed final native workflow oracle were published
together as
[`6214032f3565f9e221fcf3988e33a22a73bb4ea8`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/6214032f3565f9e221fcf3988e33a22a73bb4ea8),
tree **`10f070c54d176571f1919d8141d24dd82db0e41c`**. Its exact local equivalent
is `fcc22346d0ea71d368d570aebbec9ffd1ebbf974`. The guarded parent is 183; root
fetched the new commit, verified identical trees and preserved local history on
`standalone-local-final-oracle-code`. This public delta contains exactly two
test files; production, CMake and installed payload inputs are unchanged.

Actual repaired Windows execution belongs to the
[final platform audit](STANDALONE_FINAL_PLATFORM_AUDIT.md). The earlier
[110/110 combined Release result](STANDALONE_COMBINED_FINAL_GATE.md) is scoped
to 183 and must not silently absorb these later test changes. Keep its original
Windows 100/101 failure and the separate native instrumented failures visible.
This fixture work makes no physical audio, acquisition, timing, accessibility,
DAW or Hammond/Leslie fidelity claim.

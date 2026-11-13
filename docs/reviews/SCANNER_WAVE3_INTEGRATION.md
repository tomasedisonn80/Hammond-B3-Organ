# Coherent scanner line and rotor integration

## Qualified source and result

The integrator qualified local commit `babb8975d6881db6629e570e10ee619c70ba8be3`, tree
`14572ab24e67489997cee20ae452c0635178dca0`, from the separate detached worktree
`/workspace/scratch/1742da7072be/scanner-w3-source`. The new build directory was
`/workspace/scratch/1742da7072be/scanner-w3-build`. Unfinished combined-stage and
allocation files in the working checkout were excluded. The GitHub code object
`772e3b3682c2026414e0a7b50eb726e8bddd7fed` has the identical tree; branch publication is independently verified
by the integrator's handoff receipt. This later report is documentation only.

**All 77 Release CTest suites passed**, zero failures, in **50.64 seconds**.
The build used GCC 14.2.0, CMake 4.4.4, Ninja 1.13.2, Python 3.12.14 and Linux x86_64.
All tests ran from the same committed source and used that build's executables.

```sh
git worktree add --detach /workspace/scratch/1742da7072be/scanner-w3-source babb8975d6881db6629e570e10ee619c70ba8be3
cmake -S /workspace/scratch/1742da7072be/scanner-w3-source -B /workspace/scratch/1742da7072be/scanner-w3-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/1742da7072be/scanner-w3-build --parallel 4
ctest --test-dir /workspace/scratch/1742da7072be/scanner-w3-build -C Release --parallel 3 --output-on-failure --no-tests=error
```

## Meaningful evidence and limits

The new suites supplement the 73-suite graph/reference foundation with native
line state/energy/lifecycle acceptance, independent full-circuit transient
regression, independent native AC/process regression and independent rotor
acceptance. The repeated-default CMake configuration regression also passes,
including changed automatic data roots, preserved custom paths and continued
explicit-empty/traversal/absolute rejection. The portable decimal parser is
used by the new native probe, preserving the existing libc++ compatibility fix.

[Assignment 17](../development/2026-11-13-scanner/17-native-ac-parity.md) ran the
full frozen frequency study from an independently built coherent line/probe:
160,740 logical positive tap comparisons, exact DC and 88 actual process carriers
passed their G3 frequency bounds. Five earlier unsettled process attempts remain
recorded. The full same-hertz G5 grid **failed at every investigated rate**,
including 1,536,000 Hz; all 40,786 failed tap comparisons are retained in the exact
report. No multiplier or output-filter policy was qualified.

[The rotor acceptance](../SCANNER_ROTOR_ACCEPTANCE.md) independently checks the
six modes, three maps, 16-position signed weighting, continuing clock and failure
rollback. Full native matched-step basis/trajectory comparison, combined-stage
routing/allocation, converged transient/rotating references and G5 policy remain
separately assigned. Native Engine processing, 45 public controls, saved-state
formats and physical source assets are unchanged. This checkpoint is neither a
scanner-enabled plugin nor a measured instrument claim.

## Exact qualified inputs

| Input | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `46d0dbcb0439dda780d25579a608996e83063cbceceb9e9f400ff134ee8d60a3` |
| `cmake/InstallHammondTools.cmake` | `97cb6ec2c7073e3c50a1b00106317ddd726a2fb01e580dc96b55be0044140355` |
| `include/hammond/ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| `src/ScannerLine.cpp` | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| `include/hammond/ScannerRotor.h` | `3ca846fc72224114194d73272f410fa2cbe3c0cae94c4fb23105536c7afb4d5a` |
| `src/ScannerRotor.cpp` | `f1dbd65a92036fef9957d280d2aafe9bd8579414ef632a6e2c525e370907b2a0` |
| `tools/scanner_line_probe.cpp` | `4a283205949a837df8835f2b86874ee66624631d05fbdf8a6ccce7ff54e16fdb` |
| `tools/scanner_transient_reference.py` | `5d63941b4b85c28ebf4dce7427e87b87779c3538ae00ff2510014a1df1c45cda` |
| `tools/qualify_scanner_ac.py` | `33e32ca06d60a93be87fa7497f31b41be682bf2f1386d75697b29e4031a42548` |
| `tests/test_scanner_line.cpp` | `7f5fb41717258e131b3649449d131a93510546ee8024643ab9e527133231efa0` |
| `tests/test_scanner_rotor.cpp` | `b7c04d4c91c09f27bc8701831cf889fed5e1e29d4cf59150ba58100505db5926` |
| `tests/test_scanner_transient_reference.py` | `b484f175854f2d461e334ac102e23a8df186b62bc466a85f142479c08e1842d0` |
| `tests/test_scanner_native_ac.py` | `0ee15e83ad52ee0436b41d70538741ff426d44ee6587678afa9840350a907ec1` |

The canonical graph and frozen numerical contract retain the identities in
[the wave 2 report](SCANNER_WAVE2_INTEGRATION.md). The complete 500-page source PDF
is unchanged. Twenty distinct current-session assignments are complete in this
checkpoint; assignments 21–23 are honestly recorded running. Later manifest
updates describe later accepted work and do not rewrite this historical result.

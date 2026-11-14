# Hosted baseline new-output path repair

The native macOS job at `352a398e4f004467c2dab081168be3d8b5206ea9`
compiled successfully after the unused-color repair, then exposed a distinct
startup failure. [Actual job 132383504234](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43573780886/job/132383504234)
passed 17/24 standalone CTests and failed seven native launch/installation suites.
They reported `Cannot compare selected file identities: Operation not supported`
for otherwise valid new screenshot/diagnostic leaves. This is an observed baseline
platform failure, before the new preset implementation was published.

## Correction

The integrator retained each already inspected path's existence and calls
`std::filesystem::equivalent` only when both leaves exist. Resolved path equality
still detects aliases for existing and future files. Existing hard-link checks,
symlink rejection, inspection failures and genuine identity-comparison errors
retain their behavior. The fix does not indiscriminately ignore an unsupported
identity operation on existing files.

## Observed checks

A coherent published-baseline copy supplied headers and native source. Only the
changed `main.cpp` and already repaired renderer object were freshly compiled;
unchanged baseline static archives and pinned dependencies were linked without
rebuilding or modifying the preserved baseline. The initial copied-source build
omitted `tools/CliArguments.h`; adding that unchanged published header resolved
the setup error. Final strict GCC 14.2 compilation and link passed.

The actual native app acceptance then passed **18/18 methods**, executing
**164 child processes** in 8.942 seconds. It covers new output paths, missing parents,
Unicode paths, existing identities/aliases, hardlinks, symlinks, startup/load and
shutdown/failure behavior. [Build commands and results](reports/baseline-path-repair-build.json)
and [native output](reports/baseline-path-repair-native-tests.txt) are retained.
The local run uses explicit SDL dummy drivers and is not a macOS execution claim.
The next guarded published revision supplies the hosted macOS acceptance gate.

## Retained hosted failure excerpt

```text
2026-11-14T08:03:10.1256030Z 102: Traceback (most recent call last):
2026-11-14T08:03:10.1256760Z 102:   File "/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/apps/standalone/native_tests/test_standalone_install.py", line 315, in test_actual_component_relocates_and_runs
2026-11-14T08:03:10.1257500Z 102:     self.assert_success(result)
2026-11-14T08:03:10.1258040Z 102:   File "/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/apps/standalone/native_tests/test_standalone_install.py", line 173, in assert_success
2026-11-14T08:03:10.1258780Z 102:     self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
2026-11-14T08:03:10.1259400Z 102: AssertionError: 1 != 0 : hammond_standalone: Cannot compare selected file identities: Operation not supported
2026-11-14T08:03:10.1259870Z 102: 
2026-11-14T08:03:10.1260010Z 102: 
2026-11-14T08:03:10.1260230Z 102: ----------------------------------------------------------------------
2026-11-14T08:03:10.1260570Z 102: Ran 8 tests in 6.951s
```


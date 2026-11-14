# A11 — Windows rounding-oracle setup repair

Actual worker: `/root/w02_a11_windows_oracle_repair`, wave 2.
Inspected baseline: `d493e998e5dd7cf44db46854e87309745063ac54`.
Owned code: `tests/test_preset_parameter_oracle.py` only. The integrator owns
shared status, publication and hosted qualification; no commit or push was made
by this assignment.

## Observed failure and cause

The published Windows MSVC Release job
[132404740670](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43580730409/job/132404740670)
failed `python_test_preset_parameter_oracle` during class setup. Its Python
3.12.10 loader raised `TypeError: argument of type 'NoneType' is not iterable`
at `ctypes.CDLL(None)`. None of the oracle's six existing test methods ran.
The original timestamped failure is retained in
[the hosted excerpt](reports/a11-hosted-windows-failure.txt); its header and
[result record](reports/a11-result.json) retain the complete downloaded-log hash.

The helper tried the POSIX current-process lookup before `ucrtbase.dll` on
Windows. That invalid first candidate raised `TypeError`, outside the expected
missing-library/missing-symbol handlers, so the valid Windows candidate was
never attempted. This was test-runtime setup failure, not observed incorrect
parameter conversion.

## Repair and preserved gates

Windows now opens `ucrtbase.dll` directly through the existing cdecl `CDLL`
loader. POSIX still uses the current-process lookup. The explicit `fegetround`
and `fesetround` argument/result declarations are unchanged. Missing runtime or
symbols, an unreadable mode, an unavailable native-reported mode, and failure to
restore the caller's mode all remain hard failures. No skip, fallback result or
weaker threshold was introduced.

Added two setup regressions to the existing registered test file. The first
injects the observed Windows loader behavior, including its `None` rejection,
and exercises all four modeled mode switches/restorations and the native-call
signatures. The second requires missing UCRT to fail the gate. These are loader
regressions, not native Windows floating-point execution. The actual oracle
still obtains its platform mode codes and complete vectors from the compiled
native probe and checks them against independent integer/rational expectations.

Production C++, Python conversion logic, all 47 parameter records, the old
45-record digest, state formats and existing conversion/rejection assertions
were not changed. No CMake change is needed: the existing CTest registration
runs the six original methods and the two added setup regressions together.

## Executed verification

Working directory for both commands:
`/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.

Before the one-line candidate repair, the new regression reproduced the exact
observed exception:

```sh
python3 tests/test_preset_parameter_oracle.py RoundingEnvironmentLoadingTests -v
```

Result: two methods, one passed and one `TypeError`, exit 1. The unchanged
failure output is [retained here](reports/a11-regression-before.txt).

After repair, ran the actual required oracle using the already-built, unchanged
baseline native executables:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native \
  -R '^python_test_preset_parameter_oracle$' --no-tests=error -V
```

Result: **1/1 selected suite passed, all 8 methods passed**, exit 0. The actual
native/Python acceptance retained **688 native vectors, 296 atomic conversion
rejections, 84 descriptor rejections, 49 real 47-record CLI invocations and all
four Python rounding modes**. See [complete output](reports/a11-oracle-after.txt)
and [source/executable hashes](reports/a11-result.json). `git diff --check` passed
for the changed test file. No redundant full-suite or new build was needed for
this test-only repair.

## Remaining qualification and handoff

This worker executed Linux/Python 3.12.14, not Windows. The injected regression
demonstrates that the previous setup bug is prevented; it cannot establish a
native Windows UCRT or full Windows CI pass. Publish the integrated revision and
observe the Windows Release job's actual oracle result, including the four
native-reported modes and existing exact conversion assertions. Preserve any
new failure independently instead of declaring Windows green from this local
result. The macOS MIDI replay defect belongs to A10 and was not modified here.

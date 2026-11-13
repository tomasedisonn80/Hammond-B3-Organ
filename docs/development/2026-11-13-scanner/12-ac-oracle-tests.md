# Assignment 12 - independent scanner AC regression

## Identity and ownership

- Actual worker: `/root/w02_a12_ac_oracle_tests`, assignment 12 of 60, wave 2.
- Owned files: `tests/test_scanner_ac_reference.py` and this note only.
- Inspected local and remote main: `6dc0702d5473912268e8af8f852b9b9984198ef3`;
  its committed tree is `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.
- The scanner additions were uncommitted concurrent work. The committed baseline
  alone does not identify these tested additions; their actual hashes are below.
- Execution used Python 3.12.14 and its standard library. No dependency was added.

Read the standing agent contract, current scanner handoff/status/plan context,
[AC reference](../../SCANNER_AC_REFERENCE.md),
[numerical contract](../../SCANNER_NUMERICAL_CONTRACT.md), relevant producer code,
and atlas pp. 157-159. The earlier fresh source reviews and independently assigned
primary-paper review own visual/primary-source verification. This assignment does
not claim another complete PDF reading or physical measurements.

## Independent checks

The test's second finite-frequency calculation uses **backward loaded impedance
recursion followed by forward voltage-divider propagation**. It reads no nodal
stamping routine, LU factors, producer expected graph or producer DC expectation.
It starts from literal documented 0.5 H inductors, 4 nF capacitors with the final
1 nF exception, the six resistor-divider pairs, 15 kOhm termination and 22 kOhm
return. The early divider loading is attached before each inductor. The same
independent method checks the declared changed-termination and after-inductor
experiments, rather than only asserting that their outputs differ.

Literal exact rational DC answers include
`Rparallel = 92438660160000/9455738267` ohms and chorus return ratio
`9455738267/13657495547`, plus all six early-tap fractions, thirteen unity taps
and both input currents. These expectations do not call `dc_reference` to
calculate their own expected result.

The 16 test methods cover:

- The frozen 282-frequency grid, both return states, all 19 signed outputs,
  common return, positive input current, finite solve evidence and conditioning.
- **564 independent AC comparisons and 10,716 tap comparisons** against the
  separately formulated loaded-ladder calculation.
- Positive real input power and equality with explicitly calculated resistor
  dissipation at every grid point; both sides use the same peak-phasor convention.
- Low-frequency approach to the independently retained DC answers.
- Wrong divider attachment: identical exact DC but different finite-frequency
  response, independently reproduced at 1, 5 and 7 kHz.
- Both 7,500 and 30,000 ohm termination experiments at those frequencies;
  upstream response/current changes and the correctly invariant vibrato tap 1.
- Single-output sign reversal for v1, v7 and v19: the selected output negates,
  the other eighteen and the physical node/current solution remain unchanged.
- Return-referenced observation loses exactly one common-return term in chorus
  and correctly agrees with ground reference in vibrato.
- Immutable authoring inputs and distinct, reproducible experiment identity.
- Invalid frequencies, modes, condition flags, grids, experiments and nominal
  graph changes; explicit phase exclusions and conditioning opt-out.
- Real CLI execution with paths containing spaces, reproducible report bytes,
  source hash binding, invalid-argument/input-alias/duplicate-key preservation.
- Nonfinite, nonserializable and oversized reports, plus injected atomic replace
  failure: prior output survives and temporary files are removed.

## Executed result

From `/workspace/scratch/1742da7072be/Hammond-B3-Organ`:

```sh
python3 tests/test_scanner_ac_reference.py -v
git diff --check
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git ls-remote origin refs/heads/main
sha256sum tools/scanner_ac_reference.py tools/compile_scanner_line.py data/scanner/atlas-late-b3-nominal-v1.json docs/SCANNER_NUMERICAL_CONTRACT.md tests/test_scanner_ac_reference.py
python3 --version
```

**All 16 methods passed in 3.537 seconds**, exit 0. The largest complex tap
difference between nodal and loaded-ladder calculations was
`5.6647284161045834e-14`, under the independently declared test comparison bound
`1e-10 + 1e-9*abs(expected)`. All 564 power and solve checks passed. There were no
failed or skipped tests and no producer repair was needed. Repository whitespace
checking passed; the owned files were also checked directly because untracked
files are not covered by ordinary `git diff --check`.

| Tested input | SHA-256 |
| --- | --- |
| AC reference tool | `5472dbe96839a64e864e3d6275ea326b6a497fe5c06997f0a23a3d230763bd1e` |
| Graph compiler | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| Nominal authoring graph | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Numerical contract v1 | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| This test implementation | `cbdea600b273cbf21d8d4d2d116c9f04ca0eac2f7f1e4787972baa5da84bfa1b` |

## Limits and next dependency

These checks support mathematical consistency of the stated ideal circuit.
They are not an external SPICE comparison, continuous-time transient convergence,
C++ processing qualification, rotor/sideband qualification, host test or measured
scanner fidelity result. The next numerical dependency is independent comparison
of the prepared native recurrence and physical-state transients, with warp-matched
and same-hertz results retained separately under the frozen contract.

The integrator owns CMake discovery/execution, full coherent-source qualification,
shared status and publication. This worker changed no producer, shared status,
historical ledger or remote reference, and made no commit or push.

# Assignment 14: independent full-circuit transient reference

**Wave:** 3 of 10. **Assignment:** 14 of 60. **Date:** 13 November 2026.
**Agent:** `w03_a14_transient_oracle`. **Role:** implement the independent
offline transient reference and report actual producer checks.

## Scope and source boundary

Owned files:

- `tools/scanner_transient_reference.py`
- `docs/SCANNER_TRANSIENT_REFERENCE.md`
- This assignment note.

No native implementation, build configuration, shared status, graph fixture or
Git history was changed by this worker. Publication belongs to the coordinator.
The native worker and independent tester received the API and completed-frame
convention while implementation proceeded.

Read `AGENTS.md`, the frozen numerical contract, admitted scanner graph and
compiler, relevant project handoff/review material, and freshly extracted atlas
pp. 182-186. The full-atlas review belongs to earlier recorded assignments;
this note does not claim this worker personally reread all 500 pages.

| Evidence | Identity |
| --- | --- |
| Atlas SHA-256 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Authoring graph SHA-256 | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Frozen contract SHA-256 | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| Reference source SHA-256 at producer verification | `5d63941b4b85c28ebf4dce7427e87b87779c3538ae00ff2510014a1df1c45cda` |
| Integration base observed before implementation | Commit `74473facf8efc3332497ab969017c718458d6921`, tree `6c76bba650c033d9e8ade7ba3b2347ce569a10b6` |
| Coordinator HEAD at final producer smoke | Commit `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`, tree `d98d9baf666f048629f5c817ed0f040b215df0e4` |

The source hash identifies this worker's code independently of the concurrent
coordinator commits. Subsequent fixes must record a new source hash instead
of attributing these observations to an untested source revision.

## Implemented result

The reference stamps every resistor and trapezoidal capacitor/inductor
companion from the admitted full graph. It observes signed graph outputs and
retains return voltage, source current, all 36 physical coordinates and energy.
Its own diagonally scaled Cholesky factor solves the companion nodal circuit.
A separate scaled initial-state MNA imposes capacitor voltages and inductor
currents, solves algebraic nodes and capacitor currents, and reconstructs
compatible histories after state restore, return switching or rate changes.
It never imports the C++ reduction, native matrices or AC LU solver.

The API supports both return states, nonzero physical initialization,
transactional frame/state/mode/rate rejection, stopped observation and
preparation condition estimates. The bounded CLI writes finite JSON
transactionally and identifies the source/contract hashes and endpoint origin.
`render_trace` interpolates the same fixed input polygon for every subdivision.
Refinement proceeds through `8,16,32[,64,128]`, requiring two consecutive
passing comparisons and explicitly returning `inconclusive` otherwise.

`frame` counts completed internal intervals: first processing returns 1.
`render_trace` independently labels first knot 0 at time 0, following the
previous endpoint at `-1/48000` for the frozen grid. There is no one-frame fit.

## Actual producer verification

All checks below ran against this worker's implementation. None is presented
as an independent native-runtime comparison or a complete frozen-suite result.

### CLI and numerical smoke

Commands completed with status 0:

```sh
python3 -m py_compile tools/scanner_transient_reference.py
python3 tools/scanner_transient_reference.py \
  --output /workspace/scratch/1742da7072be/transient-a14-vibrato.json \
  --frames 64 --fixture step-positive --mode vibrato
python3 tools/scanner_transient_reference.py \
  --output /workspace/scratch/1742da7072be/transient-a14-chorus.json \
  --frames 64 --fixture charged-c18 --mode chorus
git diff --check
```

The CLI results explicitly said `matched-step-only; convergence-not-tested`.

| 64-frame case, 48 kHz | Maximum normalized residual | Maximum KCL residual, A | Final energy, J |
| --- | ---: | ---: | ---: |
| Vibrato positive step | `2.6594198672354736e-16` | `2.956144985917508e-19` | `7.496088052852122e-08` |
| Chorus charged C18 | `1.5695661673755776e-16` | `1.7353587506872478e-19` | `1.1256981475266927e-11` |

A separate inline Python producer harness performed 24,000 positive-step
frames at 48 kHz in each mode. It formed the DC parallel resistance with exact
`fractions.Fraction` arithmetic from `Rt` and the six divider resistor sums,
then compared all 19 settled tap voltages and source current. Maximum tap
error was `3.3306690738754696e-15 V` in vibrato and
`9.7699626167013776e-15 V` in chorus; source-current differences were below
`1e-12 A`. This is an analytical DC check, not a frequency-grid comparison.

For the four frozen charged-state families, each mode then ran 3,000 zero-drive
frames at 48 kHz, or 62.5 ms. Every per-step energy increase stayed within
`1e-12*Einitial + 1e-24 J`. Maximum normalized residual across these cases was
`2.6874677984253855e-16`.

| Initial state | Vibrato final/initial energy | Chorus final/initial energy |
| --- | ---: | ---: |
| C1 = +1 V | `3.5145158209737804e-07` | `2.8601266073570467e-07` |
| C18 = -1 V | `4.9930843368885428e-08` | `9.1403405332880323e-08` |
| L1 = +1e-4 A | `8.8745944581560276e-08` | `4.3941843177773115e-08` |
| L18 = -1e-4 A | `1.5989164588731002e-07` | `2.9287844130560861e-07` |

These shorter producer checks do not claim the contract's 250 ms tests at
every supported rate.

### Reconstruction, signs and failure behavior

After 180 sine-input precharge frames in each mode, switching return topology
and changing 48 to 96 kHz preserved the entire `PhysicalState` exactly. NaN
input, invalid mode, zero rate and a Boolean frame counter were rejected.
After each rejection, state/observation and three subsequent valid frames
matched an untouched deep copy exactly.

Both modes passed exact sign reversal across 64-knot positive/negative pulse
traces for every tap, capacitor voltage, inductor current, return voltage and
input current. The first trace record was explicitly `knot=0`, time 0,
completed frame 1. Nonfinite comparison values and changed endpoint times
were rejected. Huge integer input, Boolean input and infinity were rejected.

Output tests retained an existing sentinel file after NaN/Inf serialization,
injected `os.replace` failure, and source-alias rejection. The injected write
failure left no temporary file. A valid finite report replaced the sentinel;
a symlink output was subsequently rejected without modifying its target.

### Refinement behavior and conditioning

A zero-input/zero-state four-knot check returned two passing comparisons at
8, 16 and 32 subdivisions in each mode. This checks convergence-control
plumbing only. It does not establish nonzero transient accuracy.

A separate 64-knot positive-step investigation followed the same fixed linear
input polygon in both modes. It reached the deliberately limited factor-32
cap and correctly reported `inconclusive`:

| Mode | Refinement pair | Worst required normalized RMS | Worst required normalized maximum |
| --- | --- | ---: | ---: |
| Vibrato | 8 to 16 | `7.195428878255054e-4` | `1.8457480235496426e-3` |
| Vibrato | 16 to 32 | `1.8025702460157557e-4` | `4.624503266137392e-4` |
| Chorus | 8 to 16 | `2.634448627037259e-4` | `6.56713260050369e-4` |
| Chorus | 16 to 32 | `6.602215120343626e-5` | `1.6407101679947008e-4` |

The fixed reference bounds remain RMS `2e-6` and maximum `1e-5`. The finer
trace is not called truth. These 64-knot values are not a substitute for the
frozen 2,400-knot experiment.

At 48 kHz, computed infinity-norm condition estimates were:

| Mode | Physical companion matrix | Scaled companion matrix | Scaled initial-state MNA |
| --- | ---: | ---: | ---: |
| Vibrato | `27.808219001043735` | `2.639978706385666` | `12.063106796116504` |
| Chorus | `4773.88262724227` | `2651.3804646749004` | `712.8019722507328` |

Neither mode raised the declared conditioning flag. These are binary64
computed estimates, not certified condition-number bounds.

## Limits and next step

The producer checks establish a functioning independent implementation and
specific algebraic/transactional properties. They do not establish native G3,
all-basis parity, all ordered-rate transitions, complete zero-source energy
coverage, reference convergence for all frozen fixtures, G5 audible-rate
policy, Engine integration, rotary behavior or physical M4 accuracy.

The next independent assignment should compare native processing against this
full-graph matched-step oracle for all 36 basis states, both signs and modes,
supported rates and migration events. Run all frozen 2,400-knot refinement
experiments separately. Retain failures and inconclusive cases; improve the
independent reference before grading continuous-time native accuracy where
the prescribed refinement cap fails. Keep matched-step parity and converged
reference claims distinct. The coordinator's scanner handoff owns promotion
decisions and later result identities.

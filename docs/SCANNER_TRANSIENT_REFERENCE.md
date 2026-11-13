# Independent nominal scanner transient reference

`tools/scanner_transient_reference.py` is an offline, standard-library Python
reference for the admitted ideal scanner circuit. It stamps the full resistor,
capacitor and inductor graph and observes the signed graph outputs. It shares
only the graph admission/compiler with other implementations. It does not
import the native physical-state reduction, native transition matrices, native
factorization, tap formulas or the AC reference's numerical solver.

**Reference identity:** `scanner-full-graph-trapezoidal-reference-v1`.
**Model identity:** `atlas-late-b3-nominal-line-v1`.
The [frozen numerical contract](SCANNER_NUMERICAL_CONTRACT.md) defines the
acceptance experiments. This implementation supplies an independent
matched-step reference and a bounded refinement runner; its presence alone
does not pass G3 or G5. Neither comparison establishes physical M4 fidelity.

## Circuit and numerical method

The admitted graph has 18 inductors, 18 capacitors, 14 resistors, 19 signed
ground-referenced taps, the ideal drive and both return topologies. Ground and
the ideal drive are fixed nodes. The vibrato return is additionally fixed at
ground; the chorus return remains an independently solved node. Every passive
branch stamps its actual graph endpoints, including all six divider junctions
and the shared return. Divider-first ordering reduces fill in the nodal
factor; it does not replace the circuit with a cascade.

For a branch directed from its positive to negative endpoint, let voltage be
the positive-node voltage minus negative-node voltage, and let current flow
in that direction. At step size `h`, a capacitor and inductor each have a
conductance plus a signed history current:

```text
capacitor: Gc = 2*C/h
           Ic(new) = Gc*Vc(new) + Hc
           Hc = -Ic(old) - Gc*Vc(old)

inductor:  Gl = h/(2*L)
           IL(new) = Gl*VL(new) + Hl
           Hl = IL(old) + Gl*VL(old)
```

A resistor contributes `1/R`. Each conductance stamps its two positive
diagonals and two negative off-diagonals. Known drive voltages move to the
right-hand side. A history current subtracts from the positive-node right-hand
side and adds to the negative-node right-hand side. This yields the full
companion nodal system `G*v=b`, with 24 free nodes in vibrato and 25 in chorus.
Both topologies are prepared before processing. The symmetric scaling
`D^-1*G*D^-1`, with `Dii=sqrt(Gii)`, is factored by an independently implemented
Cholesky method. Solves retain every nonzero factor entry; there is no
threshold that discards small entries.

This is the trapezoidal rule. At equal step size it is a discrete circuit
reference. When subdivisions are used, it follows the same linear input
polygon between the original input knots. Agreement with a coarse native
trapezoidal implementation is not, by itself, continuous-time convergence.

### Consistent nonzero initial states and topology changes

A checkpoint contains all 18 capacitor differences `V(pk)-V(r)`, all 18
inductor currents directed `p(k-1)->pk`, the previous input endpoint and a
completed-interval frame counter. Capacitor currents and inductor voltages
are reconstructed independently from those physical coordinates.

The reconstruction uses a separate modified nodal system containing only
resistor conductances, the prescribed inductor currents as current sources,
and 18 ideal voltage constraints imposing the prescribed capacitor voltages.
The additional unknowns are capacitor currents. KCL rows and capacitor-current
unknowns are scaled by 15,000 ohms, leaving voltage constraints in volts. The
nonsingular 42- or 43-dimensional algebraic system is prepared with a separate
Gauss-Jordan inverse. The singular descriptor energy matrix is never inverted.

State restore, return switching and stopped-rate changes solve this algebraic
system again. They preserve the physical state, previous input and frame
counter exactly as supplied; they do not reuse incompatible companion
histories from the previous topology or step size. Ground-referenced nodes
may change when the return changes. Energy is the physical sum
`0.5*sum(C*Vc^2)+0.5*sum(L*IL^2)`, in joules. This tool does not assert that
switch work or a first zero sample after a nonzero input is zero source work.

### Residuals and conditioning

Every frame reports the largest free-node KCL imbalance in amperes. For an
advanced frame, `normalized_residual` uses that imbalance as the numerator of

```text
||G*v-b||inf / (||G||inf*||v||inf + ||b||inf).
```

Here `G` is the unscaled physical nodal conductance matrix. The branch-current
KCL calculation equals `G*v-b` in exact arithmetic and independently retains
the physical current directions. For a stopped observation after initial-state
reconstruction, the normalized residual is instead evaluated directly on the
scaled initial MNA matrix and right-hand side. A zero denominator is accepted
only with a zero numerator. Nonfinite values or residuals above `1e-9` reject
the operation before replacing any existing state.

`preparation_diagnostics()` gives dimensions, scaling conventions and
infinity-norm condition estimates for the physical companion matrix, its
diagonally scaled matrix and the scaled initial MNA matrix. Estimates use
binary64 computed inverses, so they are not rigorous forward-error bounds.
`conditioning_limited` flags any estimate times `2^-52` above `1e-4`.
Investigators must preserve such a flag and obtain stronger evidence before
qualifying that experiment. A small residual alone does not prove accuracy.

## Python API

The tool directory must be on Python's import path, as in existing scanner
tools. The admitted profile is the authoring JSON loaded by the graph compiler.

```python
import sys
sys.path.insert(0, "tools")
from compile_scanner_line import load_profile
from scanner_transient_reference import PhysicalState, TransientLine

profile = load_profile("data/scanner/atlas-late-b3-nominal-v1.json")
initial = PhysicalState(capacitor_volts=(1.0,) + (0.0,) * 17)
line = TransientLine(profile, 48000.0, "chorus", initial)
before = line.observe()              # Current endpoint, no time advance.
first = line.process_frame(0.0)       # Advance one interval.
checkpoint = line.state()             # Immutable physical checkpoint.
line.set_mode("vibrato")              # Reconstruct algebraic history.
line.reconfigure_sample_rate(96000.0)  # Prepare both topologies off line.
line.restore_state(checkpoint)        # Explicit PhysicalState required.
```

| API | Result or convention |
| --- | --- |
| `PhysicalState(capacitor_volts, inductor_amps, previous_input_volts=0, frames=0)` | Eighteen voltage and current coordinates; omitted vectors are zero. |
| `TransientLine(profile, sample_rate, mode, state=None)` | Owned line with both topologies prepared; mode is `vibrato` or `chorus`. |
| `process_frame(input_volts, mode=None)` | Advance to the supplied endpoint; optionally switch before the interval. |
| `observe()` | Current endpoint with `advanced=False`; no state or clock change. |
| `state()` / `restore_state(state)` | Snapshot or replace physical state after successful algebraic reconstruction. |
| `set_mode(mode)` | Preserve physical coordinates and reconstruct the selected return topology. |
| `reconfigure_sample_rate(rate)` | Preserve state and replace both prepared topologies transactionally. |
| `preparation_diagnostics()` | Matrix dimensions, scaling and computed condition estimates for both modes. |
| `fixture(name, sample_rate=48000, frames=2400)` | Input-knot tuple and initial state for one frozen fixture family. |
| `render_trace(profile, inputs, sample_rate, mode, initial_state=None, subdivisions=1)` | Frames sampled only at the original input knots. |
| `compare_traces(first, second)` | Every-channel fixed-scale RMS and maximum difference, with strict knot/time/mode/input matching. |
| `refinement_study(..., refinements=(8,16,32,64,128))` | Stop at two consecutive passing refinements or return `inconclusive`. |
| `write_report(path, report, input_path=None)` | Finite, bounded JSON through an adjacent temporary file and atomic replacement. |

Every frame includes signed `taps_volts` in `v1..v19` order, `return_volts`,
`input_current_amps` positive from the ideal source into the line,
`capacitor_volts` in `C1..C18` order, `inductor_amps` in `L1..L18` order,
`energy_joules`, residuals, mode, rate, input and completed-interval `frame`.
The first processed frame from a cold checkpoint has `frame=1`.
`render_trace` adds separate `knot` and `time_seconds` fields: first knot 0 is
at time 0, following the interval beginning at `-1/sample_rate`. With
subdivisions, the frame counter counts internal intervals, not input knots.
There is no fitted sample shift, sign correction or output gain correction.

### Bounds and failure behavior

The reference accepts rates from 8,000 to 12,288,000 Hz, allowing the frozen
refinements without enlarging native host-rate support. Input and previous
input magnitudes are bounded by 64 V; capacitor-state magnitudes by `1e6 V`;
inductor-state magnitudes by `100 A`; solved node magnitudes by `1e9 V`.
These are defensive numerical limits, not physical operating claims. A frame
counter is an integer in `0..2^64-1`. Booleans, nonfinite values and malformed
state vectors are rejected. States that fail the full algebraic solve or a
subsequent bound are also rejected.

Traces contain 1 through 10,000 knots, subdivision factors are powers of two
from 1 through 128, and a trace has at most 1,280,000 internal steps. Refinement
lists must be an exact prefix of `8,16,32,64,128` containing at least three
factors. Core matrices and state vectors have fixed dimensions. Trace/report
storage is bounded; JSON is limited to 64 MiB. This is an offline tool and
does allocate Python objects per frame.

An invalid frame, restore, mode or rate change preserves the complete previous
line and its later continuation. A report is serialized and checked before
the destination is touched. Existing source-profile aliases, nonregular
destinations and symlink destinations are rejected. An output parent directory
must already exist. On a write failure the prior destination remains intact
and temporary output is removed. The CLI returns status 2 for rejected work.

## Frozen fixtures and refinement interpretation

The frozen suite has nine fixture names: `step-positive`, `step-negative`,
`pulse-positive`, `pulse-negative`, `multisine`, `charged-c1`, `charged-c18`,
`energized-l1` and `energized-l18`. Their exact definitions are in contract
section 5 and implemented by `fixture()`. In particular, the one-knot pulse
is a finite triangular input under linear reconstruction, not a Dirac impulse.

Reference comparisons require normalized RMS at most `2e-6` and maximum at
most `1e-5` for every one of the 19 taps and all 36 physical coordinates.
Voltage normalization is 1 V; current normalization is `1e-4 A`. Return
voltage and input current remain reported diagnostics. Both consecutive
comparison pairs must pass. Hitting factor 128 without that result is
`inconclusive`; `finest_trace` identifies the retained data and does not confer
truth status. Conditioning flags remain relevant even when refinement
differences are small.

The CLI records the graph-file hash, executing tool hash, frozen contract
hash, method, input reconstruction, endpoint origin, initial physical state,
matrix diagnostics and actual performed factors. A shortened trace or changed
knot rate is visibly outside the full frozen fixture grid. Runtime comparison
and physical fidelity flags remain false because this tool does not perform
either experiment itself.

```sh
# Bounded matched-step smoke, explicitly not a convergence result.
python3 tools/scanner_transient_reference.py \
  --mode chorus --fixture charged-c18 --frames 64 \
  --output /tmp/scanner-transient-smoke.json

# One complete frozen fixture with independent refinements.
python3 tools/scanner_transient_reference.py \
  --mode vibrato --fixture step-positive --study \
  --output /tmp/scanner-step-refinement.json
```

## Development evidence and next work

[Assignment 14](development/2026-11-13-scanner/14-transient-oracle.md) records
the actual producer smoke checks. It includes full-graph DC limits, nonzero
physical-state decay, mode/rate reconstruction, failure continuation, polarity,
atomic output and a deliberately short refinement investigation. These checks
do not replace the independent 36-coordinate/native parity suite, all frozen
2,400-knot reference refinements or native G5 comparisons. The
[current handoff](SCANNER_HANDOFF.md) owns subsequent acceptance results.

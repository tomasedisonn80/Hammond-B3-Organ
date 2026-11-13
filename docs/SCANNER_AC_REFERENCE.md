# Independent nominal scanner AC reference

`tools/scanner_ac_reference.py` solves the admitted documentary scanner graph by
stamping every passive edge into a complex nodal admittance system. It does not
import the native runtime's reduced physical-state equations, operators,
factorization or output reconstruction. Its only shared preparation is strict
[graph admission](SCANNER_GRAPH.md) and printed-to-SI unit conversion.

The source basis is the unchanged atlas, pp. 157-159 and 181-186. The graph and
returned results are an ideal nominal reconstruction, not a specimen measurement
or recovery of the atlas's absent companion implementation. The broader
[numerical acceptance contract](M3_REMAINING_AND_SCANNER_GATE.md#4-independent-numerical-oracle-before-the-real-time-solver)
continues to require independent runtime and transient comparisons.

## Electrical and numerical contract

The drive is exactly `V(p0,g)=1 V`. Vibrato imposes `r=g` by elimination;
chorus keeps `r` as an unknown and retains the 22 kOhm return resistance.
The resulting systems have 24 and 25 unknown node voltages respectively.
Each edge stamps both endpoint current equations using `1/R`, `j*omega*C`,
or `1/(j*omega*L)`. No artificial large conductance approximates a short.
The output map reconstructs all nineteen signed voltages from named endpoints.
Input current is positive **from the ideal source into the passive line**, in
amperes for the one-volt excitation, equivalently A/V. The report also retains
`15000 ohms * Iin/Vin` for dimensionless comparison under the numerical contract.

Rows are divided by their largest absolute entry before partial-pivot complex LU.
Pivots at or below `1e-15` in that scaled system are rejected, as are nonfinite
solutions. The solver reports both original-equation and row-scaled normalized
infinity residuals:

`||A*z-b||inf / (||A||inf*||z||inf + ||b||inf)`.

A zero denominator yields zero only for an exactly zero residual. The declared
software residual budget is `1e-9`. The reported condition estimate is
`||A_scaled||inf * ||inverse(A_scaled)||inf`, computed using every inverse column
through the existing LU factors. It describes the scaled nodal equations; it is
not a hardware uncertainty, an eigenvalue estimate or an unscaled descriptor
condition. Bins with `kappa_inf(A_scaled)*2^-52 > 1e-4` are explicitly marked
conditioning-limited and retained for separate evidence; a small residual does
not silently clear them. `--skip-condition` explicitly records that conditioning was not
computed.

DC is separate exact-rational arithmetic: inductors short, capacitors open,
all section nodes equal the imposed input, and the six series-divider branches
are in parallel with the termination. This path does not call complex stamping
or LU. Its resistor values are exact decimal SI values admitted by the compiler.
It retains numerators and denominators as well as decimal renderings.

## Frozen frequency and phase conventions

The default positive-frequency grid is the sorted union of:

- `20 * 1000**(j/120)` Hz, `j=0..120`, rounded to twelve decimal places;
- 5,000 through 9,000 Hz in 25 Hz increments.

The endpoints are explicitly 20 and 20,000 Hz. There are 282 distinct positive
frequencies, both return states, 564 nodal solutions and 10,716 complex tap
transfers. Exact DC results accompany the grid. This is an analog physical-Hz
reference; any runtime bilinear warp must be applied explicitly by its comparison
tool. Agreement at warped frequencies does not establish agreement at the same
physical Hz.

Complex values and magnitude are always retained. Phase is eligible only at
magnitude at least `1e-4` under the one-volt excitation. Ineligible bins have an
explicit exclusion reason. Phase unwrap proceeds only across consecutive
eligible bins, restarts at the principal phase after a gap, and never shifts a
tap to match another tap. Group delay is a negative phase-versus-physical-omega
secant: centered across adjacent bins internally and one-sided at segment edges.
A one-bin eligible segment is explicitly excluded. This sampled estimate can
miss structure narrower than the frozen grid; it is not an independently
converged group-delay claim.

## API

Place `tools` on the Python import path and use:

```python
from compile_scanner_line import load_profile
from scanner_ac_reference import prepare_network, solve_ac, dc_reference

profile = load_profile("data/scanner/atlas-late-b3-nominal-v1.json")
network = prepare_network(profile)
response = solve_ac(network, "chorus", 1000.0)
exact_dc = dc_reference(network, "chorus")
```

`prepare_network` returns an immutable internal numerical record after complete
nominal admission. `solve_ac` and `dc_reference` also accept the original admitted
profile dictionary. The AC result contains complex `taps`, `tap_ids`, named
`node_voltages`, `return_voltage`, `input_current`, system dimension, both
residuals, condition estimate and evidence identity. Frequencies must be finite
real numbers in `[1e-6,1e9]` Hz; zero belongs to `dc_reference`. Booleans are not
accepted as numerical inputs.

Controlled experiments are applied **after** nominal admission:

```python
experiment = prepare_network(profile, experiment={"termination_ohms": 7500.0})
wrong_edges = prepare_network(profile, experiment={"divider_attachment": "after-inductor"})
wrong_reference = prepare_network(profile, experiment={"output_reference": "return"})
reversed_ports = prepare_network(profile, experiment={"output_sign": "reversed"})
one_reversed_port = prepare_network(profile, experiment={"reverse_output": "v7"})
```

Only these five named changes are supported. Experiments receive their own
content-derived `scanner-experiment-v1-...` identity, retain `base_model_id`, and
set `nominal=false`; they are never accepted as alternate nominal source data.
`reverse_output` accepts exactly one ID `v1` through `v19` and leaves all
other observation pairs unchanged. It is mutually exclusive with reversing all
outputs. Moving the early dividers after their inductors produces the same DC response,
but changes finite-frequency transfer. Termination sensitivity must be measured
at a node that can vary: in vibrato, the first divider is held between the ideal
source and ground, so its output correctly stays unchanged when Rt changes.
Later taps change. Chorus also permits the first tap to change through the shared
return. Referencing outputs to `r` exposes the missing common-return term in
chorus; it is numerically identical to ground reference in vibrato.

## Reproducible report

From the repository root:

```sh
python3 tools/scanner_ac_reference.py --output /absolute/new-or-existing/report.json
python3 tools/scanner_ac_reference.py --frequencies 20,1000,6000,20000 \
  --termination-ohms 7500 --output /absolute/new-or-existing/sensitivity.json
```

The report contains source-file and canonical-authoring SHA-256 identities,
physical units, complete grid, signed complex transfers, DC fractions, residuals,
conditioning coverage, phase exclusions and scope. No timestamp or machine path
makes repeat execution differ. Reports are bounded to 16 MiB, custom grids to
1,024 increasing finite points and both declared return states.

The CLI reads one bounded, validated input snapshot for its source digest. It
rejects an output alias of that source, a symlink or nonregular destination,
invalid inputs, failed numerical residuals and serialization failures. A complete
report is written to a sibling temporary file and atomically replaces the target
only on success. Failed calls preserve a previous destination. It downloads
nothing and needs only Python's standard library.

See [assignment 08](development/2026-11-13-scanner/08-scanner-ac-oracle.md)
for the actual executed result and limits. A reference report alone does not
qualify the C++ runtime, physical scanner, organ integration or a native host.

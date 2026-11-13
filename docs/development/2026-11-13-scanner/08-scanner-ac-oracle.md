# Assignment 08 - independent scanner AC oracle

## Identity and ownership

- Actual worker: `/root/w02_a08_scanner_ac_oracle`; wave 2, assignment 08/60.
- Starting commit: `6dc0702d5473912268e8af8f852b9b9984198ef3`.
- Owned files: `tools/scanner_ac_reference.py`, `docs/SCANNER_AC_REFERENCE.md`, and this note.
- Source basis: unchanged atlas pp. 157-159 and 181-186; current scanner gate sections 3/4; fresh source-review notes 02/03. This assignment implements new numerical code, not the atlas's missing companion oracle and not a fresh primary-circuit or full-PDF review.
- Admitted authoring input SHA-256: `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604`.
- Tested oracle SHA-256: `5472dbe96839a64e864e3d6275ea326b6a497fe5c06997f0a23a3d230763bd1e`.

The graph/compiler work belongs to assignment 07. I coordinated its raw/normalized
API and requested a single-snapshot `load_profile_with_digest` method so report
identity cannot accidentally describe a second read. The oracle shares admission
and unit conversion only. All numerical edge stamping, node elimination, complex
LU, residual/conditioning work and tap reconstruction are independently authored
here, without importing the future runtime's reduced-state equations.

## Implemented behavior

The finite-frequency solver stamps all fifty passive edges into ground-referenced
node equations. It eliminates the exact ideal drive and vibrato return constraint,
leaving 24 vibrato or 25 chorus unknown voltages. It reports all nineteen signed
taps, named nodes, common return and positive-into-line input current. The source
current is retained in A/V and as `15000 ohms * Iin/Vin` for dimensionless comparison.

Complex Gaussian elimination uses row-max scaling and partial pivots. Both original
and scaled normalized infinity residuals are reported. Every requested condition
estimate uses all inverse-column solves; conditioning-limited bins are explicitly
flagged by the frozen `kappa_inf(A_scaled)*2^-52 > 1e-4` criterion. Exact-rational
DC comes from resistor branches after ideal L-short/C-open reduction, with no call
to the complex solver.

The frozen default grid has 282 positive frequencies: 121 geometric points from
20 to 20,000 Hz, rounded to twelve decimal places, plus 5,000-9,000 Hz at 25 Hz
intervals. Both return modes are evaluated. Phase below magnitude `1e-4` is
explicitly excluded; eligible contiguous segments are unwrapped without per-tap
alignment. Group delay uses declared physical-frequency secants. Its sampled
values are not asserted to be an independently converged continuous derivative.

Five bounded sensitivity experiments are supported only after exact nominal
admission: changed termination resistance, deliberately after-inductor divider
attachment, return-relative outputs, all reversed output signs and a single selected output
reversal. Each receives a
separate content-derived experimental identity and keeps its nominal base identity;
none is re-admitted as the nominal circuit. JSON serialization and output
publication are bounded and atomic. Invalid input, nonfinite report, input alias,
nonregular destination or numerical-residual failure preserves an existing output.

## Executed verification

Working directory was `/workspace/scratch/1742da7072be/Hammond-B3-Organ`, using
Python 3.12.14. Commands actually executed included:

```sh
python3 -m py_compile tools/scanner_ac_reference.py
python3 tools/scanner_ac_reference.py \
  --output /workspace/scratch/1742da7072be/scanner-ac-reference-a08.json
python3 tools/scanner_ac_reference.py --frequencies 1000,5000,7000 \
  --reverse-output-sign \
  --output /workspace/scratch/1742da7072be/scanner-ac-reversed-a08.json
python3 tools/scanner_ac_reference.py --frequencies 1000,5000,7000 \
  --reverse-output v7 \
  --output /workspace/scratch/1742da7072be/scanner-ac-one-reversed-a08.json
git diff --check
```

Final full-grid execution took approximately 1.91 seconds locally. This is an
offline observation, not an audio callback deadline or benchmark promise.

| Check | Observed result |
| --- | --- |
| Complete nominal positive-frequency grid | 564 successful solves; 10,716 signed complex tap transfers |
| Maximum original/scaled normalized residual | `3.2486101684985267e-16`, below the predeclared `1e-9` budget |
| Conditioning coverage | All 564 estimates computed; minimum `3.9517564871420405`, maximum `1171.5379395201726`; zero conditioning-limited bins |
| Phase exclusions | 848 tap/frequency bins below the declared magnitude floor, retained with reasons |
| Exact DC | Parallel resistance `9775.932618884532` ohms; chorus return ratio `0.6923478931008726`; all output fractions retained |
| Divider mutation | Identical exact DC in both states; maximum tap error at 6 kHz approximately `1.262770543` in vibrato and `0.495403279` in chorus |
| Rt sensitivity | At 1 kHz, halving Rt changes v7 by approximately `0.5104148664` in vibrato and `0.1290968892` in chorus |
| Single-output mutation | Reversed v7 and preserved the other eighteen taps exactly at 1/5/7 kHz in both modes; 114 observations checked |
| Signed outputs | Reversed observation equals the exact negative of every nominal complex tap at 1/5/7 kHz in both modes |
| Both load mutations | Rt=7,500 and 30,000 ohms each measurably changes v7 at 1/5/7 kHz in both modes |
| Low-frequency limit and passivity sign | 0.01 Hz first-tap response approaches exact DC within `1e-5`; real input admittance at 1 kHz is positive in both modes |
| Failure preservation | Four CLI cases (`nan`, decreasing grid, zero frequency, zero Rt) returned 2 and left a sentinel output unchanged |
| Serialization and repeatability | A nonfinite report was rejected without replacement; writing the same finite small report twice produced identical bytes |

The final full report's SHA-256 is
`507838d47c52898839cfd6bbe23d09a5665f8661e4e7565669ecf5599818e054`.
That reproducible execution artifact is outside the repository; the tool and its
commands are the retained deliverable. Supplemental checks above were executed
through short Python API probes using `prepare_network`, `solve_ac`,
`dc_reference`, `build_report`, `write_report` and temporary sentinel files.
Independent committed regression coverage belongs to the separately assigned
review/test worker, not to a fabricated test-suite claim here.

A meaningful loading caveat emerged: v1 in vibrato is a resistor divider directly
between the ideal source and ground. Changing Rt therefore correctly leaves v1
unchanged. Later upstream taps change; chorus v1 also changes because its return
moves. A sensitivity test that demands vibrato v1 movement would reject the
correct graph. The oracle detects the relevant mutations through the appropriate
ports, including the chorus common-return error.

## Limits and handoff

No runtime comparison, transient convergence, rotor/sideband acceptance, Engine
integration, native host test or hardware acquisition was performed by this
assignment. The nominal line lacks measured winding losses, loading, coupling,
absolute signal calibration and specimen applicability. A small linear residual
cannot establish any of those gates. Next use the independently committed tests
and prepared-runtime comparison against this oracle, including explicit bilinear
frequency conversion and separate same-Hz grading. No production control/state
records were modified. The integrator owns shared status and commit/push publication.

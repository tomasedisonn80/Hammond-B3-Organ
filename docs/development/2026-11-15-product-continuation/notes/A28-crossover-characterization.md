# A28 — same-Hz crossover characterization

Actual worker `/root/w05_a28_crossover_characterization`, wave 5. Read standing
instructions, full M0–M9 plan, session records, the complete crossover contract,
A13/A17/A19/A20 notes, coherent acceptance and original oracle-failure records.
Starting HEAD `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`; the retained report's
source/binary identities describe the qualified overlay separately from HEAD.

Delivered `docs/LESLIE_CROSSOVER_CHARACTERIZATION.md`,
`tools/plot_crossover_characterization.py`, and
`docs/design/crossover/same-hz-nominal-v1.png`. The document separates warped
recurrence verification, same-Hz electrical characterization and unacquired
physical/audible acceptance. It gives signed magnitude/phase and absolute port
error, preserves the near-DC oracle repair, and proposes a versioned electrical
protocol before alternative numerical or physical models. The 48→192 kHz
observations do not qualify a resampling pipeline; 176.4 kHz is not a v1 rate.

The plot reuses 24 retained nominal checkpoints; no new native sweep or process
was run. At 20 kHz the analog bass gain is −60.225079 dB. Its 44.1 kHz relative
error of −27.149142 dB corresponds to `9.316571e-4 V/V` absolute complex error.
Treble's −2.892074° phase difference produces `5.048634e-2 V/V` despite a small
magnitude change. No audibility conclusion follows from either scale.

## Executed authoring and checks

After A27 released its quiet timing window, from the repository directory:

```sh
python3 tools/plot_crossover_characterization.py --output docs/design/crossover/same-hz-nominal-v1.png
```

Python 3.12.14 / Matplotlib 3.10.8 generated the **1800×1230, 278,470-byte** PNG.
Visual inspection found readable axes, legend, units and evidence boundary.
Fresh-path reproduction from another working directory was byte-identical.
Existing-output, failed-report and stale-source cases rejected without output
mutation. All 72 port conversions agreed with independent series/parallel
reconstruction; maximum difference `1.0213184464813452e-16`. Embedded source,
report and plotter hashes matched. Syntax and whitespace checks passed.
Commands/results remain in sibling `a28-checks/authoring.log` and `verification.log`.

SHA-256:

- Report: `2773a6fa1b7b81292296d9c29e4677cd5dfe56921ce9e34ee6d126c3ce3269d8`.
- Document: `1d67a2602b042f84368c5c47a2b4395a04ba3ef47e57fdb79b921020a53dd0fa`.
- Plotter: `fecd825b3736de148926544ebd74cf7adc6994d366666d0910929d62c592822c`.
- PNG: `6084be255054c1f11afdac26b3d8972721f9711598b13b30231ace69326bf39c`.

Next: root links this characterization from the M6 guide/status and publishes
the accepted files. Changed acceptance source identities require reviewed new
evidence and figure regeneration. Production, CMake, shared builds, other
checkouts and publication were untouched; v1 and Engine remain unchanged.

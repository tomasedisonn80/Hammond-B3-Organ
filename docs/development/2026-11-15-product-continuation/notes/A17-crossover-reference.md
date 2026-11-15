# A17 — independent crossover reference

Actual agent `/root/w03_a17_crossover_reference`, wave 3. Owns
`tools/crossover_reference.py`, `tests/test_crossover_reference.py` and this note.
Starting HEAD `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`; concurrent native files
were preserved and are outside this qualification.

## Delivered

The standard-library tool admits the fixed v1 registry field by field, including
ordered floating-treble topology, values, units, assembly/source identity,
explicit ideal assumptions and null physical measurements. Duplicate JSON keys,
nonfinite/oversized/malformed inputs and false measurement claims reject.
Alternative 1–1024-ohm loads are named resistor experiments outside the default
16-ohm fixture. No native implementation or state matrices are imported.

`load_network`/`prepare_network`, `analog_response`, `nodal_response` and
`default_frequency_grid` provide reusable APIs. Separate series/parallel algebra
and physical-edge KCL produce both complex load gains and input admittance.
Reports retain raw/canonical registry and code hashes, 124 requested/unique
frequencies, separate exact DC, residuals, evidence limits and null unknowns.
Output is deterministic JSON; an explicit destination is replaced atomically
only after admission/calculation, and registry/source overwrite rejects.

## Executed

Working directory `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`, Python 3.12:

```sh
python3 tests/test_crossover_reference.py
python3 tools/crossover_reference.py --output /workspace/scratch/5b7d983ac078/a17-checks/reference.json
git diff --check -- tools/crossover_reference.py tests/test_crossover_reference.py
```

All **16 tests passed** in 0.546 seconds. Independently reduced literal transfer
polynomials supplied **4,464** comparisons across six load cases: maximum
normalized error `4.5915676671878673e-15`. Maximum resistor power-balance error
was `3.3306690738754696e-16`. The default 136,909-byte report passed its `2e-10`
budget; maximum analog-method error `8.5206426709147675e-16` and nodal residual
`1.0796647739533479e-16`. CLI failure preservation and deterministic output passed.
Compact execution log: sibling scratch `a17-checks/verification.log`.

Source SHA-256 identities:

- Reference: `b91eb34465c4ffed8587ac7839ad68c4a1debf23a397eac5328007f47a1fef38`.
- Tests: `48c3ce6f861eea65ba48d6533bafb89d5588bb2a58ebaeb03cb5f6cc95b3629f`.
- Registry bytes: `f55fa98c246b4a19dce12ca829a141cff744f71242cccb68db12b404400319cc`.

## Next gate and limits

Root wires the Python test into CTest. Wave 4 compares native recurrence and
settled sine output against this independent reference at warped frequencies,
retaining same-Hz errors separately. This assignment qualifies analog algebra
and registry/CLI admission only; it does not independently inspect manufacturer
drawings, verify PDF bytes, measure hardware, test native processing or connect
the divider to Engine. No shared build, commit or other-session modification.

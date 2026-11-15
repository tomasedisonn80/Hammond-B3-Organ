# A09 — passive crossover contract and authoring registry

Actual agent `/root/w02_a09_crossover_contract`, wave 2. Starting source:
`647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb`. Owned only the new
[contract](../../../LESLIE_CROSSOVER_CONTRACT.md),
[registry](../../../../data/crossover/leslie-122-ideal-v1.json) and this note.

Read the complete agent instructions, M0–M9 plan, current session scope and all
atlas pages **271–276**; reread p. 274 separately after aggregate output
truncation. Inspected existing ScannerLine/Status conventions. This is contract
work, not an implementation or execution of the atlas's absent companion.

The contract freezes a four-state C++20 `LeslieCrossover` API with differential
treble/bass voltages, resistor currents, input current, stored energy, physical
checkpoints and completed-frame count. Fixed documentary L/C values retain the
floating A–H treble port. Default loads are explicitly ideal 16-ohm resistors;
alternative bounded resistor experiments do not become driver measurements.
Registry evidence is the inspected atlas, not an independently verified factory
schematic. Physical losses, impedance, polarity and specimen fields remain null.

The chosen realization is prepared trapezoidal endpoint integration at four
rates. Preparation resets an experiment; rate reconfiguration preserves physical
state, previous input and frame count. Empty processing advances nothing. Failed
operations preserve state/configuration and destinations, including a late block
failure. Processing is bounded to 4096 frames, uses fixed storage and performs no
allocation or fitting. Computational limits are explicitly not device ratings.

Required acceptance covers independent analytic/nodal algebra, actual digital
processing and warped-reference parity, separately retained same-Hz errors,
state/rate/transaction cases, midpoint discrete energy balance and calibrated
allocation observations. It does not close M6 hardware or live integration gates.

Verification performed: standard-library JSON parsing; exact PDF SHA-256 match;
four component IDs, ordered node pairs, SI values/units; explicit null physical
fields; terminal newlines and no trailing whitespace. All passed. No build,
numerical runtime test, hardware acquisition or commit was performed.

Contract SHA-256: `b127d393d9addba0c0a9854acaa9a2ad2b797cd06cbd12d5b9be7714693bc44a`.
Registry SHA-256: `f55fa98c246b4a19dce12ca829a141cff744f71242cccb68db12b404400319cc`.
Next: independent topology/numerical review, then native implementation and an
independent reference under the frozen acceptance criteria. Engine/R4 unchanged.

# A13 — native ideal Leslie crossover

Actual wave-3 implementation agent. Baseline documentation commit:
`da48180390a9fd473643d1759c153cb9d37ecfb6`.

Implemented the frozen `LESLIE_CROSSOVER_CONTRACT.md` API in
`include/hammond/LeslieCrossover.h` and `src/LeslieCrossover.cpp`, with author
checks in `tests/test_leslie_crossover.cpp`. The independent four-coordinate
research model uses the documentary L2/L3/C16 values and explicitly declared
resistive loads. Preparation performs checked, row-scaled four-state LU solves;
processing applies the prepared trapezoidal recurrence. Response solves that
actual recurrence, including its DC equilibrium and normalized residual.

Rate changes preserve capacitor voltages, inductor currents, prior input and
frame count exactly. Fixed-storage block processing validates the complete
trajectory before a second identical pass commits any output. It rejects byte
overlap, late invalid inputs, late numerical-bound failures and clock overflow
transactionally. No Engine, musical-state or R4 connection was added.

## Actual verification

GCC C++20 standalone production and test builds passed with `-O2 -DNDEBUG`,
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
The isolated executable `/workspace/scratch/5b7d983ac078/a13-test-leslie-crossover`
passed: 2,480 independently calculated series/parallel response comparisons
(four rates, five load pairs), four processed-sine fits, exact scalar/block
partition equality, all 16 rate pairs, failure preservation/status precedence,
20,000 midpoint energy checks and ten-second decay at each admitted rate.

Measured maxima: normalized complex response error `2.090955353578198e-13`,
recurrence residual `1.7554167342883506e-16`, processed-sine error
`5.4219364318596328e-15`, normalized midpoint energy residual
`1.5034834813763831e-20`. Repository whitespace check passed. Shared build was
not run by this agent; root owns CMake wiring and integration qualification.

## Source hashes and next step

SHA-256:

- Header: `54efff218f873045bd07a2eb3270d07637e3f3fc5d2d51bac032b7efca53559c`
- Implementation: `1a1bdde72af95709143afc4f62991c138ff3458cc78765fbe49a229d82693525`
- Author test: `69a78b1abc9fc79c9404065d060a1a96144fb9e60179a2dd34dfbd8cd4eb7866`

Next: root wires the source into the library; independent agents qualify
electrical response, state transitions, allocation behavior and acceptance
evidence. These author checks establish numerical behavior only. They do not
establish real-driver loading, component losses, acoustic polarity, rotary
behavior, same-Hz analog accuracy or physical Leslie fidelity.

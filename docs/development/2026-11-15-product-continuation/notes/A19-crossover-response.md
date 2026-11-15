# A19 — independent native electrical response

Actual worker `/root/w04_a19_crossover_response`, wave 4, starting HEAD
`af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`. Read standing instructions,
M0–M9 plan, current session and complete crossover contract. Owned
`tools/crossover_probe.cpp`, `tests/test_crossover_acceptance.py` and this note.
Root explicitly expanded ownership for the focused nodal-current correction in
`tools/crossover_reference.py` and its reference test.

The bounded, SDK-free public-API probe supplies strict response/sine commands and
finite JSON. It refuses malformed, duplicate, inapplicable and excessive arguments
without partial JSON. Sine fits observe real processed right endpoints; the probe
does not claim its own startup convergence. Python independently stamps nodal KCL,
derives branch-polynomial modal decay bounds, and compares full/half-window fits.
DC, near-DC, near-Nyquist, four rates and six unequal/extreme resistor pairs are
covered. Same-Hz errors remain separate from warped recurrence acceptance.

## Executed evidence and repair

Working directory: this repository. GCC 14.2 C++20 isolated probe build passed
`-O2 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
-Werror -Iinclude`, linked against root's read-only Release `libhammond_core.a`.
The core archive SHA-256 is
`d110f7523afcc3ae1ab6053da7dfc86dfcddc66d4bfe19aabf1f0458fb1bd13f`.

Initial acceptance found eight near-DC oracle failures: at 1e-8 Hz/RW 1,
source-edge subtraction lost `3.25450149356e-10` imaginary A/V. Native and
series/parallel already agreed within `5.77e-15`. Generic edge-stamped ground
return now avoids cancellation; 144 new polynomial/series/KCL comparisons have
maximum error `2.2204502844110104e-16`.

Python 3.12.14 commands `python3 tests/test_crossover_reference.py` and
`HAMMOND_CROSSOVER_PROBE_EXECUTABLE=../a19-checks/hammond_crossover_probe
python3 tests/test_crossover_acceptance.py` passed 17/17 and 3/3 in 0.507s/1.412s.
Native acceptance executed 153 processes, 9,360 response-port comparisons and 864
processed-sine/half-window comparisons in 96 experiments. Max errors:
response `2.0923475127225402e-13`; sine `3.429777428091277e-13`;
independent fitted transient bound `4.014564579287608e-11`.

Sibling `a19-checks/` retains `initial-oracle-cancellation.log/.json`, final
`verification.log`, `reference-verification.log`, and 83,786-byte `acceptance.json`.
The final report pins sources/binary and records same-Hz tables. Nominal bass
gain differs at 20 kHz by −27.149/−18.202/−2.763/−0.636 dB at
44.1/48/96/192 kHz; no audible threshold or physical fidelity is claimed.

Final isolated probe SHA-256:
`25c958c4d157af5a758a08fb852915c45a5655564d454977007166d61bdef107`.
Probe source: `e9525de45f6df95c05785f50430a049e71fcd5299a00a6b95db11337b65dc475`;
acceptance source: `cf9d8e94e4b57a623fa7fcfaa91d50e81ad19818d151f7dc7f5a1ead69070f95`.
Corrected reference: `33eaa88da2534e52f88c044b5fbabf19828655bacb357dc55bbeb6510b580ec5`;
reference test: `e6c8469e345f634606624b2f3eb063cd9091b91d1b2cf1023aadd95598eac4aa`.

## Next integration gate

Root wires `hammond_crossover_probe`, sets
`HAMMOND_CROSSOVER_PROBE_EXECUTABLE` for `python_test_crossover_acceptance`,
retains original/final reports, and reruns coherent CTest/platform qualification.
Optional `HAMMOND_CROSSOVER_ACCEPTANCE_REPORT` writes compact exact-input evidence.
Shared build, Engine, state formats, commits and publication were untouched.

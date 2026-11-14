# A08 — Independent same-cubic reference and R4 acceptance design

## Assignment and ownership

Actual worker: `/root/w02_a08_reference_design`, wave 2, 14 November 2026.
Assigned by the integrator as a distinct worker in this session. No nested
workers were spawned. Owned files:

- `tests/reference/rotary_waveform_reference.h`
- `docs/ROTARY_WAVEFORM_ACCEPTANCE.md`
- this note

Read `AGENTS.md`, the current waveform scope/checkpoint/manifest, complete
`docs/PLAN.md`, atlas-review guidance, relevant current status/next steps,
`ROTARY_SCOPE`, the full numerical and renderer-plan contracts, the existing
Python oracle, and the R2/R3 acceptance architecture. The session's A04 full
rotary atlas reading supplies the retained source review; this assignment does
not claim another complete atlas reading. Inspected starting source was
`2e161dc3a60fc3442051799574feed37bffbfc5c`; during the assignment the integrator
advanced HEAD to `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`. Relevant uncommitted
file identities below define this work, rather than either HEAD alone.

Did not edit product code, CMake, shared status/log/checkpoint/manifest, other
workers' files or any shared build directory. Did not commit or publish.

## Implemented independent reference

The header is standalone C++20 standard-library offline code, with no production
include or call. It independently implements immutable event-anchored motion,
constant-speed negative motion, Cartesian geometry, split emission positions,
full-orbit delay brackets, a contractive root route with bounded bisection
fallback, a pure-bisection comparison route, four-node product-form cubic,
two-input/two-output rendering and streamed error summaries.

The root target is `5e-15 s`, below the frozen independent `1e-14 s` limit. The
fast route evaluates at most two endpoints plus 24 contractive candidates and
96 fallback bisections. Expected audio uses exactly `t=(n-2)/Fs`, negative input
zero, all four support nodes, one reference-distance/path-distance gain and
Horn-then-Drum addition. There is no alignment, rescaling, clipping, pitch
remapping, shared native trajectory or shared native ring read.

The header's scalar is the platform's `long double`; this Linux run has 64
significand bits and 18 decimal digits. That is not an 80-digit oracle. The
separate existing Decimal motion reference and 100-digit Cartesian checks
qualify selected query values, while the C++ reference makes the complete
millions-of-samples comparison practical. Binary64-only `long double` platforms
must report and qualify their actual arithmetic; they have not been run here.

## Frozen executable workload and integration agreement

The integrator agreed to **one complete ten-second mixed scenario per rate**,
containing isolated signed Horn/Drum impulses, separate bounded deterministic
signals, 35 ordered commands, nonzero histories and explicit silence/tails.
It requires 3,801,000 frames across all four rates, 7,602,000 output scalar
comparisons and 15,204,000 reference paths. Three ten-second runs per rate are
not required. All complete native blocks 1, 7, 64, 257, 4096 and the retained
irregular sequence remain mandatory. Only the expected-reference calculation
is reused across these identical native streams.

The specification fixes the 1,028 bounded polynomial points, all 33,280 static
complex points and all 6,695 low-band points, retaining high-band error as
characterization. It specifies direct bitwise partition comparisons, complete
failure recording, nonzero-history rollback, event boundaries, symmetries,
reset/rate epochs, source identities and precision/runtime metadata. A single
longest-rate canonical binary64 audio stream is 30,720,000 bytes; it can be
replayed and discarded after retaining compact evidence. No million-row JSON
transport or permanent audio corpus is needed.

A07's frozen primitive admits `mu=1` explicitly, matching the final grid row.
Its native diagnostic paths are rotor-major; this reference is channel-major.
The specification explicitly maps native `2*rotor+channel` to reference
`2*channel+rotor`. A19/A28 should preserve this mapping when qualifying native
path diagnostics.

## Actual standalone checks

Ran independently compiled temporary probes outside the shared build, using
GCC `c++ (Debian 14.2.0-19) 14.2.0`, Linux `6.18.57 x86_64 GNU/Linux`, flags
`-std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror -ffp-contract=off`.
Both probes link no native product source. Final probes were rebuilt and rerun
after the header's full-epoch position guard was tightened; both exited zero.

| Actual reference-only check | Observed result |
| --- | --- |
| Degree 0–3, 257 fractions each | 1,028 points; max error `6.7762635780344027e-21` |
| Complete static cubic grid | 33,280 points; full-band max complex error `0.9953980792939058` |
| Complete low-band subset | 6,695 points; max complex error `0.003480564142224863`, below 0.005 |
| Complete input generation at four rates | 7,602,000 scalar samples; max magnitude 1, finite and bounded |
| Fast/pure-bisection comparison | 288 path pairs; max delay difference `4.837720258025688e-15 s` |
| Selected fast-root residual/work | Max residual `4.885460728998835e-15 s`; max 10 evaluations |
| Complete ten-second reference at 48 kHz | 480,000 frames; final run 9.876212027 s, summed stereo checksum `-73.0234837056910409681` |

The earlier exploratory ten-second run took 12.262955657 s and produced the
same checksum. These are observed offline timings, not an optimization result
or a device-deadline claim. No complete all-rate native parity or partition
workload was run by this design assignment.

Selected C++ queries were also checked at 176 all-rate path positions using
`tools/rotary_reference.py` at its private 80-digit motion precision, the R3
acceptance module's 100-digit Cartesian geometry, and its separately bisected
Python root with binary64 geometry and target `1e-16 s`:

| Independent cross-check | Maximum absolute difference | Worst `(rate,frame,rotor,channel)` |
| --- | ---: | --- |
| Unwrapped motion angle | `2.244417994016155e-17 rad` | `(192000,1728000,0,1)` |
| Speed | `1.780654344114074e-18 rad/s` | `(192000,384000,0,0)` |
| Cartesian distance | `4.002030158120896e-18 m` | `(192000,1728000,0,1)` |
| Frequency ratio | `3.125115371771728e-19` | `(192000,1919999,0,1)` |
| Retarded delay | `4.817691316846397e-15 s` | `(192000,1919999,0,1)` |

All selected checks passed their predeclared R2/R3 and root-difference budgets.
The Python root is explicitly not described as an 80-digit geometry solve.

## Exact identities and reproduction handoff

Final retained-source SHA-256:

| Input | SHA-256 |
| --- | --- |
| Reference header | `3c24792f80f86f903926622f4bf016984caf44d727ad3913e4570738ac9c8f21` |
| Acceptance specification | `fa4288d586a2a40d803740408177f9c0a085bd4deb9ae0bdfc832e6d58b0c1aa` |
| Frozen numerical contract | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| Existing Python reference | `4c8bbcdf279f87aaad5b730d60a82958321ba3c1a92e5318eb5e37b1e83c8b0d` |
| Existing R3 acceptance/geometry source | `032c410e4176e8f00a4e70a8446784f12bca89257e1f647faae7ee49e13e6c9a` |

Temporary, assignment-owned checks remain under
`/workspace/scratch/e3cacb90cc81/a08-reference-check/` for immediate integration:

| Temporary input/result | SHA-256 |
| --- | --- |
| `check.cpp` | `689501c56298afeb5840269f8ba3d96672db5e846282cd08fca4267872ff07af` |
| `crosscheck.cpp` | `a34b1a1b0731783a226f9eaa3a276cfa31581f90ca111a8019b83e629e05eac3` |
| `crosscheck.py` | `cf1f1440275f68e288974d5696aaf0706f18f708954837465dd347b0c2103fc6` |
| `check` executable | `5d581d9046e93745c5028462832447bc27608cd882419e1d496bd5a7a8bc4d50` |
| `crosscheck` executable | `c274f5ba8223bdfba78d373f93339fffb901a5cdac38a71669005acb046859be` |
| Final `check.json` | `b6555267b31f93a373c7fdc33905e8640ab5006ed29c70d0a323ce05f438facd` |
| `crosscheck-summary.json` | `9aca43a857c02f39323dd60bf7427032505245239ae03c954db402dedf2f750d` |

Exact working directory:
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`. Compile either probe with:

```sh
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror -ffp-contract=off \
  -I/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ \
  /workspace/scratch/e3cacb90cc81/a08-reference-check/check.cpp \
  -o /workspace/scratch/e3cacb90cc81/a08-reference-check/check
/workspace/scratch/e3cacb90cc81/a08-reference-check/check
```

For the selected Decimal cross-check, compile `crosscheck.cpp` with the same
flags to `crosscheck`, redirect its output to `crosscheck.jsonl` in the same
directory, then run `python3 .../a08-reference-check/crosscheck.py`. The
versioned acceptance specification retains the complete query sets, budgets,
input definitions and algorithms; these exploratory scratch probes are not
the final native acceptance runner.

## Next concrete assignment and limits

Implement the versioned native adapter/runner against A07's headers, preserving
the independent header unchanged unless review finds a concrete reference
defect. Run the complete static grid and one ten-second reference/native stream
at all four rates, then all complete native partitions and required behavioral
fixtures. Retain the compact native report and complete static-grid evidence,
with exact stable worktree/executable identities and every failure. A19/A28
own subsequent integration/qualification; root owns CMake and shared records.

This assignment closes reference/experiment **design readiness** and the named
standalone oracle checks. Native R4 parity, native history/transaction behavior,
complete partition parity, all-rate lifecycle, R5, R6 and physical cabinet
fidelity remain distinct acceptance work. No threshold was changed after
observing a native result, and no native waveform result is claimed here.

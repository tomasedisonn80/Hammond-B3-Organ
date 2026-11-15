# A10 — Independent scanner FOH contract review

**Assignment:** `/root/w02_a10`, wave 2, 15 November 2026.  
**Checkout:** `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.  
**Owned files:** this note and `docs/SCANNER_FOH_CONTRACT.md`, released by A07.  
**Decision:** **accepted for integrator freeze and implementation**, with the
corrections below incorporated. No unresolved contract blocker remains. This
is independent specification review, not native implementation qualification.

## Reviewed identities

| Contract snapshot | Bytes | SHA-256 |
| --- | ---: | --- |
| Original A07 handoff | 36,830 | `b90dff5638abaadc9acd3ff8ff8870b3f1f2f606911c27e1bbe6974fa45bb11e` |
| Final A10-reviewed contract | 39,566 | `90b3564497ebd669baaaf0badf1a954953f1e1322c45f3e64e37e23cb826866e` |

I read the complete `AGENTS.md`, M0–M9 plan and current session README,
checkpoint and actual ownership records; A03's complete atlas/feasibility
note; the complete proposed and frozen scanner numerical contracts; the
existing ScannerLine header/implementation, graph, line and probe contracts;
and relevant native probe, process qualifier, basis tests and independent
full-graph transient reconstruction. The session's observed starting source
is `138fca9af7feca46d10b0e2b65d891f4751a3904`, as retained by its owner.
I did not run git or make a new live remote/source-commit observation.
This review uses the retained atlas/primary-source review; it does not claim a
new atlas reading or physical acquisition.

## Mathematical and behavioral findings

The physical equations preserve all eighteen capacitor differences and
eighteen oriented inductor currents. Divider loads attach to the first five
internal nodes through `D2..D6`; `D1` belongs to the source/return boundary.
The final capacitor is 1 nF, with its 15-kOhm termination. Ground-referenced
outputs are `d1..d6,p6..p18`, and chorus adds the algebraic return exactly
once. The return reduction and positive source-current orientation match
the admitted graph and existing module.

For normalized interval time, the unit auxiliary superdiagonal gives
`du/dtau=u_current-u_previous`. Thus the two added coordinates are temporary
input preparation coordinates, with 36 retained physical states. Extraction
of `b_current=E[:36,37]` and `b_previous=E[:36,36]-b_current` is correct; no
additional factor of the interval belongs in those vectors. The phasor
equation `(I-d*T)Z=b_current+d*b_previous`, with negative-exponent delay `d`,
has the correct current-endpoint time origin and forcing orientation.

I independently checked the Padé coefficient list and U/V evaluation against
Higham's [primary paper](https://doi.org/10.1137/04061101X), Algorithm 2.3,
pp. 1185–1186, using its
[author-hosted text](https://eprints.maths.manchester.ac.uk/634/1/covered/MIMS_ep2006_394.pdf).
The six polynomial matrix products, 38-column denominator solve, sixteen
squaring cap and two-topology work accounting are consistent. The contract
correctly identifies its fixed conservative variant rather than claiming
the paper's adaptive/preprocessed algorithm. Residual and condition apply
to the same row-scaled denominator, and neither is promoted to exponential
forward accuracy.

The accepted rate set is the existing eleven distinct rates/fifteen labels.
Cold processing advances one interval; observe advances nothing. Mode changes
apply to the upcoming interval and preserve physical coordinates, while
algebraic nodes can jump. All status precedence, state/energy limits,
counter-overflow behavior, candidate commit and stopped-rate preservation
match the intended additive API. A new response residual rejection is
explicitly required by this contract without changing old implementation
bytes. Both topology operators are prepared before publication, and the
class remains externally serialized.

## Corrections incorporated

1. **Trace clock:** added an exact trace-specific common clock label. With
   `--subdivisions m`, the previous fixture endpoint is `-m/fs`, and the
   first emitted count is `initial_frame+m`. Retaining the old literal
   minus-one-internal-sample label would contradict `m>1` metadata.
2. **Independent reference coordinates:** specified all coefficient entries,
   the 80-digit comparison direction, the 64-term Taylor indexing and the
   diagonal conversion between native scaled currents and the independent
   `1e-4 A` normalization. The independent graph derivation and different
   exponential evaluator remain mandatory.
3. **Basis and forcing fixtures:** specified `1 V`/`1e-4 A` signed basis
   amplitudes, consistent with existing physical-state tests, and added the
   two public one-frame endpoint-forcing checks. Private coefficient access
   and a runtime fault API are unnecessary to admit all prepared columns.
4. **Reachable boundary tests:** restored the frozen contract's distinction
   between caller-supplied input/state limits and observation limits. An
   output rejection unreachable inside the energy-admitted state region
   needs an algebraic explanation and, where useful, an isolated validator
   check; it cannot be claimed as an executed public-input rejection.
   Every original admission bound remains unchanged.
5. **Report admission:** requires diagnostics for each numerical solve,
   rather than an ambiguous pair of solves when native, independent FOH
   and analog references all appear. Exact-rational DC is identified as
   exact instead of given a fabricated numerical residual. The required
   selected 8x same-Hz gate is now explicitly separated from other rates'
   retained characterization failures and from all-rate discrete parity.

The original numerical contract, tolerances, grid, refinement requirements,
same-Hz failures, transient origin and selected 8x line-only candidates are
unchanged. Complete host conversion, rotating G5, G6/Engine and physical M4
remain separate and `not_run` in this line qualifier.

## Executed small independent calculation

I ran one in-memory, non-native calculation with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B -` from the checkout.
Python was **3.12.14**, NumPy **2.3.5**, SciPy **1.17.0**. It created no file
or runtime dependency. It derived a continuous operator from the existing
independent graph's algebraic capacitor-current/inductor-voltage constraints,
compared it with the proposed equations, evaluated the displayed Padé
polynomials for every admitted rate/mode, and compared with SciPy `expm`.
This screen is not the independently admitted high-precision FOH oracle.

| Check | Observed result |
| --- | --- |
| Independent graph versus proposed scaled derivative, maximum absolute entry difference | `1.4895204919483638e-11` |
| Preparation cases examined | 22 |
| Augmented matrix one-norm range | `1.0` to `2.535224464285476` |
| Required conservative squarings | 1 to 3 |
| Maximum row-scaled Padé denominator infinity condition | `1.5625` |
| Padé versus SciPy exponential, maximum absolute entry difference | `1.7763568394002505e-15` |
| Nilpotent single-integrator limit, `h=0.25`, `B=3` | Both endpoint weights exactly `0.375` |

These results support feasibility of the declared fixed cap and endpoint
extraction. They do not establish native recurrence, state, transient, process,
allocation, timing or full-grid qualification. Native source/build/CTest,
hardware, hosted CI and publication were **not run** by this assignment.
No child agents, shared navigation edits or git operations were performed.

## Preservation and handoff

The following inspected inputs were rehashed after review and remain unchanged:

| Input | SHA-256 |
| --- | --- |
| Frozen numerical contract | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| Authoring graph | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Old ScannerLine header | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| Old ScannerLine implementation | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| Old native probe | `4a283205949a837df8835f2b86874ee66624631d05fbdf8a6ccce7ff54e16fdb` |
| Independent AC reference | `5472dbe96839a64e864e3d6275ea326b6a497fe5c06997f0a23a3d230763bd1e` |
| Independent transient reference | `5d63941b4b85c28ebf4dce7427e87b87779c3538ae00ff2510014a1df1c45cda` |
| A03 atlas/feasibility note | `3161cb6954b0a8f85ea2025983696135fd97ad7125dcfb98691f30cf5b8defb5` |

The document check verifies balanced fenced blocks, resolved local Markdown
targets and no unintended trailing whitespace in the two owned files. Root
may freeze the reviewed contract and dispatch A13's separate native line
implementation now. Subsequent reference and acceptance owners must identify
this reviewed hash and execute the required evidence before declaring the
bounded phase accepted; this review supplies no inherited numerical pass.

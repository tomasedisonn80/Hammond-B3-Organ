# A04 — atlas pages 253–336 and causal representation review

Worker: `/root/w01_a04`; wave 1, assignment 4. This note records source reading
and mathematical design review only. No production code, build, test, capture or
publication was performed by this worker.

## Complete reading coverage

Read the entire `AGENTS.md` and `docs/PLAN.md`, followed by every line of the
assigned atlas extract in six contiguous, nontruncated batches: lines 1–830,
831–1660, 1661–2490, 2491–3320, 3321–4150 and 4151–4960. Coverage is PDF
pages **253–336 inclusive**, all 84 pages, chapters 041–054. This is textual
coverage; embedded figures were read through their extracted captions and
surrounding explanations, not independently transcribed from image pixels.

Extract: `/workspace/scratch/177e78b1ac09/atlas-253-336.txt`, 219,518 bytes.
SHA-256: `029093b45f46062a4e77a8e961ca94e48d280521935e0a24b73863b1f84bb5f1`.
The unchanged source atlas identity remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

Also read the complete [streaming proposal](../../../CONTACT_STREAMING_NEXT_DESIGN.md)
and its [independent design review](../../../reviews/CONTACT_STREAMING_DESIGN_REVIEW.md).
Their acceptance is permission to freeze a representation/trajectory contract;
it is not acceptance of an implemented audio filter.

## Chapter-by-chapter findings

| Chapter / PDF pages | Requirements relevant to continuation |
| --- | --- |
| 041 / 253–258 | The 1971 036616 Leslie 122 identity separates audio, control detection and mechanical rotation. Full differential volts and per-leg voltage conventions must round-trip; control changes cannot reset rotor phase. A reduced detector requires its own identity and measured timing remains absent. |
| 042 / 259–264 | The 147 is a separate connected electrical profile with a single-ended port, console loading and winding feedback. Shared component inventory does not establish the same transfer function. Prepare state off-thread, bound nonlinear work and preserve profile identity. |
| 043 / 265–270 | Solve a connected power stage with explicit driver, transformer, bias, supply and load ports. Offline DC/linear/transient convergence precedes optimization. Retain numerical, electrical and perceptual evidence separately; no newly measured 6550/transformer parameters are supplied. |
| 044 / 271–276 | Four documentary crossover values and the floating treble return must survive implementation. Compare both signed outputs and input admittance to an independent circuit reference. Bilinear frequency warping, state continuity, passivity and rate changes need explicit tests; nominal 800 Hz does not specify an acoustic split. |
| 045 / 277–282 | One stationary driver feeds one rotating active horn; the opposite horn is not another driven audio source. Share one rotor trajectory, preserve phase/time in angular responses and distinguish removed propagation from retained filtering. A zero-speed renderer must reduce to its static response. |
| 046 / 283–288 | The woofer basket remains fixed while the deflector rotates. Keep directionality, propagation and cabinet interference separately owned. Persistent FIR histories, periodic weights, complete angle wrap and a high-rate sideband comparison are required; horn evidence cannot calibrate the bass branch. |
| 047 / 289–294 | Horn and drum have independent mechanical states and direction-specific dynamics. Split intervals at timestamped commands, retain phase/speed at reversals, use stable exponential arithmetic and test partition equivalence. A service 5–8-second criterion is not a universal time constant or a horn measurement. |
| 048 / 295–300 | Appearance, acoustic geometry and specimen identity have different evidence status. Each air/panel/room path has one owner. Fixed-angle response, signed branch summation and preserved delay/phase precede added reflections. CAD appearance cannot supply missing internal dimensions. |
| 049 / 301–306 | Retarded emission time owns propagation geometry; current geometry is a named approximation. The chapter independently corrects the cited distance-sign and interpolation-endpoint errors. Bound root iterations and history, declare added algorithmic latency, retain complete tails, and compare variable blocks to the continuous reference. |
| 050 / 307–312 | Complex directivity, signed coherent summation and shared emission-time geometry are required. Angular FIR basis interpolation retains histories and phase; angle-dependent normalization would remove the modeled modulation. Synthetic Fourier reconstruction does not qualify a physical cabinet. |
| 051 / 313–318 | Microphone positions, axes, channel polarity, clock and boundaries belong in a scene identity. Reception uses source-to-receiver direction consistently, all channels share source/rotor history, and a mix matrix follows reception. Physical Doppler and convenience scene crossfades are distinct policies. |
| 052 / 319–324 | Event-anchored state avoids host-block dependence. Repeated unchanged commands must not rebase motion; evaluate old state at a command before applying the next segment. Retain bounded historical segments, explicit overflow and clock-epoch policy; UI snapshots never advance the audio clock. |
| 053 / 325–330 | Input-time and observation-time angular weighting are different operators even when frozen responses match. Keep persistent histories and explicit bank replacement. Direct/partitioned comparisons include all output samples and tails; operation counts alone are not measured deadlines. |
| 054 / 331–336 | Cabinet, direct path, microphone, room and optional RV spring branches have distinct ownership. MIMO kernels preserve off-diagonal paths and common time zero. Complementary early/late windows reconstruct one response; duplicate coherent paths create a 6.0206 dB error. Physical and runtime gates remain separate. |

These chapters strongly support the contact spike's engineering rules even
though they do not supply new contact constants: event-anchored continuity
(pp. 292, 319–324), bounded preparation/history/work (pp. 304, 310, 328),
explicit algorithmic latency and full tails (pp. 304, 328, 330, 333), and
unchanged operator/ownership while optimizing (pp. 326–330).

## Review of the next M3 representation

The existing proposal explicitly permits a **separately identified quantized
input model** if literal bounded binary64 rational arithmetic is impractical.
That is a defensible implementation direction, with the following boundaries.

1. Freeze a new model identifier, input units, integer domains and conversion
   policy before coding. Exact arithmetic may establish exact trajectory
   behavior **for admitted grid inputs**. It cannot establish equality to every
   original binary64 input, including subnormals. Preserve the existing
   fractional-contact v1 files and results without changing their meanings.
2. Prefer an initial API that accepts explicit integer times, thresholds,
   targets and velocities. This avoids an implicit float-to-grid transformation
   being mistaken for v1 admission. If a converter is delivered, retain original
   and converted identities, rounding direction, per-field error and explicit
   collision/rejection rules. Never clamp silently.
3. Quantization can collapse distinct command times, destroy `off < on`, turn a
   real target change into a no-op, or change whether a trajectory reaches a
   threshold exactly. Those are event-topology changes, not merely smaller
   displayed timing precision. A universal audio `1e-4` result does not follow
   from choosing a fine clock grid. Near a threshold/equality boundary, a tiny
   input perturbation can change the edge ledger discontinuously.
4. Define fractional crossing times as exact rationals in the new grid's clock
   units. Retain exact ordering even when their floating display values agree.
   A mixed whole-tick plus normalized proper-fraction representation can keep
   comparison products smaller than a full absolute numerator cross-product,
   but its actual ranges, products, subtraction and normalization still require
   an independent overflow proof.
5. Keep nine contact histories independently for each key. Evaluate incoming
   motion through each command time, including equality, then apply tied commands
   in caller order. Repeated targets retain their motion anchor. Reversal,
   arrival, holding inside hysteresis and multiple contacts sharing one source
   all need independent fixtures; source identity never merges histories.
6. Declare ownership of edges exactly on a process endpoint so partitioning
   cannot duplicate or lose them. Define empty-process identity, closing
   endpoint commands, reset/closed states and the admitted epoch limit. Reject
   malformed ordering/capacity/domain inputs before mutating outputs or state.
   Test successful continuation after every rejected call.
7. Derive finite maximum work as well as finite storage. If commands are bounded
   across an epoch, distinguish that bound from per-call capacity and emitted
   edge capacity. Prove all multiplication bounds and use portable checked
   arithmetic rather than assuming `__int128` exists on every platform.

The initial acceptance should compare the C++ edge sequence and final snapshots
to an independently written exact-rational oracle for the **same new model**.
Require integer boundary, distinct fractional-root, tie, reversal, no-op,
arrival, empty epoch, capacity, maximum-domain and rollback cases. Compare
single-frame, irregular and maximal partitions, including commands on either
side of a partition. A causality test must show that future commands cannot
alter already emitted events. Allocation hooks should cover ordinary processing,
failure and close paths; size reports and operation bounds remain separate
from any platform deadline claim.

For representative original v1 fixtures, a separate quantified conversion study
can report changed coordinates, root timing, edge-order/contact-state changes
and rejected collisions. Keep this as approximation evidence with its own
protocol, never as proof of universal binary64 equivalence. If conversions are
not implemented in the first spike, name that missing study as the next input.

## Scope recommendation and remaining gates

Proceed with the isolated C++ causal **trajectory** module and independent
rational oracle under a new reviewed contract. Preserve the default Engine,
91 source identities, 47 parameter meanings and `B3CONTROLS4`/readers 1–3.
Do not add the audio filter until the representation, equality/order,
transactional rejection and resource gates have been independently accepted.

The retained D=16 audio schedule is mathematically coherent because the endpoint
coefficient is zero and the last contributing cell finishes before emission.
However, a trajectory-only module has no audio latency or waveform-accuracy
result. The ring/partial-cell schedule, 33 drain samples for nonempty epochs,
full-window continuous oracle, deterministic accumulation and complete filter
tails remain later filter gates. The earlier 64-probe physical-independent
admission cannot supply those results. Physical acquisition, full-organ/indefinite
processing and live Engine/host integration remain distinct steps.

Source review and the six complete textual reads are the only executed work
supporting this note. Its recommendations are proposed acceptance conditions,
not passed implementation tests.

# Causal contact audio: independent contract admission

**16 November 2026 — A10, `/root/w02_a10`, wave 2.** The isolated
`causal-contact-audio-grid-v1` design is **implementable and admitted for
implementation**, subject to its frozen implementation and validation gates.
No remaining arithmetic, staging, lifecycle, ring or fixture blocker was found.
This admits a design and its input protocol, not an implemented renderer,
numerical result, continuous-reference result or production audio route.

The initial contract had three executable ambiguities. Root corrected them
before implementation: one numerical resource authority and counter scope;
replacement of a ready configuration before any input; and preservation of the
floating environment during its probe, with nontrapping exceptions required.
The reviewed final bindings below supersede the initial draft for this decision.
The initial draft identity and findings remain recorded here.

## Inputs, ownership and observations

Read the complete `AGENTS.md` and M0–M9 `PLAN.md`, this session's scope, root
decisions and checkpoint, the current navigation entries, the full
[audio contract](../CAUSAL_CONTACT_AUDIO_CONTRACT.md),
[validation protocol](../CAUSAL_CONTACT_AUDIO_VALIDATION.md),
[fixture module](../../tests/reference/contact_audio_cases.py), the actual
[grid header](../../include/hammond/research/CausalContactGrid.h) and
[implementation](../../src/research/CausalContactGrid.cpp), and all six
[A50 findings](CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md) and the A50 note.
Work stayed in `/workspace/scratch/edcadc57554d/Hammond-B3-Organ`; only this
review and the [A10 note](../development/2026-11-16-runtime-continuation/notes/A10.md)
were written. No production edit, build, native execution, audio render,
quadrature, commit, push or other checkout operation was performed.

| Reviewed input | SHA-256 |
| --- | --- |
| Initial audio contract, before the three amendments | `c190f452c14a1609004e3fc6873ecef67d5929d57e2791c3b47c5038d5b5e0ce` |
| Final amended audio contract | `4c98b46c49d40b895c4856d185318af3ee80b0e40b50665e78fec8ab2fa67b8f` |
| Final validation protocol | `24638c88cd186935fe5611429b17f937ce1c5e901ce01c8a679e64f5c5416b76` |
| Fixture recipe module | `36096d4f207109c3a7526c3e196a346ce5be439fe5e4e6e44dfe2054a7e8527c` |
| Canonical complete fixture manifest | `29cc67159b1c8fe2bb50991d732445c7722e05741fe2ce539e8b77a4667920cf` |
| A12 final fixture-freeze receipt | `852cbbfb38d04dd8825dfff543866dd42b9b02288dda9ff8a92e99a29bc61562` |
| Grid header | `69c655897b24688873472c559c952d9932f76b0cbed5c3eabd9a9da5b3a5d89f` |
| Grid implementation | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |
| A50 review | `feb0a9f4495a7b242a9d85f34dbe927a28681265d501f4485f53a63f635e26b9` |

HEAD during inspection was `79bf34091dda5dc0528cf584891cff3e09657c66`, tree
`b4e5526d3b08ca90fce4c3c152db8459ddd6c4e6`. The new contract/validation inputs
were untracked working files; the hashes, not that historical tree alone,
identify the reviewed design. Python arithmetic checks used CPython 3.12.14.
The final ready-rate wording, continuous underflow tiers, numerical budget table
and all final input/receipt hashes were reread after the authors' last changes.

## Exact interval arithmetic and bound: A50-C1

The two-limb domain is sufficient. A mixed root has `T<=2^24`, a proper
32-bit fraction and `p=T*b+a<2^56`; the endpoint cross-products are below
`2^88`, their sum below `2^89`, and their difference is formed only after exact
ordering. The frame-width and midpoint denominators remain below `2^80` and
`2^81`. Signed cell-boundary computation followed by gate clipping prevents
the initial negative half-cell boundary from entering unsigned time arithmetic.
No rounded endpoint subtraction is necessary.

The conversion domain is also coherent: a positive admitted ratio is at least
`2^-81`, so conversion to binary64 cannot underflow. Restoring division can
keep a remainder below the denominator and double it below `2^82`, without the
incorrect 134-bit numerator shift identified by the contract. The stated
224-step bound covers integer, leading fractional and significand/guard steps.
Correct rounding still needs implementation tests for ties, sticky bits and
renormalizing carry; this review proves capacity, not future code correctness.

The outward raw bound must be exact before its one directed rounding. Scaling
binary64 products by `2^2148` makes every nonnegative product an integer.
The maximum sum, 36, requires 2,154 bits, within the 2,176-bit fixed accumulator.
At most 36 products times 34 limb visits fits the stated 1,224 visits. This
cannot confuse cancellation or an underflowed product with exact-zero routing.
The minimum positive subnormal squared is exactly `2^-2148`: rounded nearest
binary64 is zero, while the smallest enclosing binary64 is `denorm_min`.

The independent Fraction calculation reproduced both A50 realizations:

| Case | Exact reduced width bits, numerator/denominator | Exact reduced midpoint bits | Rounded width | Rounded midpoint |
| --- | --- | --- | --- | --- |
| S10 | 33 / 80 | 89 / 81 | `0x1.0000000180000p-47` | `0x1.fe00000000000p+7` |
| S11 | 72 / 80 | 89 / 81 | `0x1.fe00000000000p-9` | `0x1.fffdff0000000p+7` |

Both S10 endpoint displays are exactly 255.0 while their exact width is
positive. The canonical independent route sums, two-term compensation retained
through calls, common full/partial-cell formula and special S07/S10/S11 criteria
address the remaining A50 loss-of-small-contribution examples. Same-build
partition identity and Python/libm numerical agreement remain separate gates.

## Staging, lifecycle and origin: A50-C2/C3/C4

The real grid is noncopyable and commits in `process` and `close_observation`.
Calling either on the committed grid before fallible audio work would violate
rollback. The proposed friend seam instead copies only private committed
`state_` into a separately embedded trial grid. Its positive process and close
operations initialize their own staging before using it. The wrapper can retain
all grid/audio state and caller output until the final fixed copies succeed;
there is no public restoration API or caller-controlled imported snapshot.

Closure is explicitly part of the same transaction. Incoming endpoint edges
are consumed by processing, but terminal diagnostics retain the preceding bits.
Thus an endpoint break can leave open final bits and a nonzero left limit;
an endpoint make can leave closed final bits and no audible duration. Endpoint
targets themselves add neither travel nor physical edges. A late failure in
terminal diagnostics must preserve the still-active committed epoch, its pending
cell and every output byte. Process and closure fault injection remain mandatory;
ordinary invalid-input tests cannot substitute for those paths.

The result/status precedence, zero-length identities, output-prefix lengths,
suffix preservation and strict drain/reset state machine are implementable.
The source phase belongs to the exact epoch label and uses local input time;
the potentially large signed origin never enters waveform arithmetic. Stopped
reset starts an independent replay. The reviewed amendment permits replacement
of a ready configuration before input while requiring full old-rate drain after
positive input. This reconciles the rate sentence with the prepare phase table.

Implementation review must still check the private seam diff, rerun the old
grid suites, verify complete private state after rejection, and show that ready
replacement and drained reset produce their specified canonical snapshots.

## Partial cells, support and ring: A50-C5

Connected pieces end at their own physical break, a true cell boundary or the
terminal gate. The host/call boundary is deliberately not a summation boundary.
Cell-before-edge tie ordering and ascending key/contact finalization give the
same addition sequence for all admissible call partitions. A muted route still
retains its physical history. The 4,608-edge / 2,304-piece cell-zero burst needs
only the fixed edge array, 36 pending starts and one compensated accumulator;
it needs no pending-piece vector or repeated per-cell scan of the edge list.

For output m, the nonzero support is bounded by
`max(0,(m-32)*256+1)` and `min(256*N,m*256-1)`. The newest supported cell ends
at `m-1/512`, so emitting before ingesting `[m,m+1)` is causal. Eviction only
after emission and against the *next* lower bound retains every required cell.
It would be incorrect to ingest an entire callback before emitting its early
samples; the contract expressly prohibits that sequence.

An independent index-only sweep covered **41,344 output positions for every
N=1..256**, including complete drain. It found at most **8,191** retained
completed cells before processing emission and **8,192** after terminal-cell
closure, within the 8,194-slot ring. All required support indices remained
retained, and complete drain emptied retention. N=0 has no finalized cell and
no manufactured tail. For every positive N the correct length is N+33, not a
forced sixteen-zero prefix or a shortened tail.

The finite work counts and 739,368-byte illustrative envelope fit the declared
1 MiB object/16 KiB additional-stack ceilings. They include two full grid
objects, trial/committed rings, edges, coefficients and staging. They are source
design bounds, not measured ABI or stack results. Preparation must stage its
coefficient result without destroying previously committed coefficients on
failure; available trial storage can support that without a large stack copy.
Named compiler builds still owe the actual object/stack measurements, allocation
and free hooks, late rejection costs and separately reported native run costs.

## Floating environment

The initial phrase "without changing" the environment did not specify probe
exception flags or the effect of caller-enabled synchronous floating traps.
The amendment now requires saving/restoring control state and flags around the
probe and makes nontrapping exceptions a caller/environment precondition.
Successful signal evaluation may raise ordinary inexact flags. This is an
implementable boundary without inventing a portable C++ trap-mask query.

Nearest-even, gradual-underflow probes, IEC binary64, strict evaluation and no
FMA contraction remain requirements. Compiler options and actual underflow/mode
tests must qualify each named build. No mathematical proof here establishes a
universal transcendental-library bound or cross-platform identical samples.

## Frozen fixtures, authority and resource correction: A50-C6

The A12 protocol and fixture module are the **single recipe/resource authority**.
The module constructs new integer-grid fixtures, contains no oracle/candidate
implementation, and imports no numerical renderer. Its binary64 hex-tagged
canonical encoding distinguishes exact input bytes from decimal display values.
The review independently checked all 75 fixture domains, source uniqueness and
lookup, nine-entry route shapes, command ordering, finite source/gain bounds and
the maximum origin/time/position capacities. The complete manifest hash agrees
with A12. Direct construction confirms S02/S03's endpoint semantics and S12's
512-command / 4,608-edge / 2,304-piece witness.

Independent input-only counts give 15,075 nonempty output samples,
**123,509,475** conservative L256 FIR terms and **38,127,456** cell/route visits.
The 180-million ceilings cover independent numerical reconstruction, not the
nine Cartesian native process/drain repetitions. Those native repetitions retain
their own observed costs and per-epoch bounds; they cannot be silently charged
as just one run or treated as a callback deadline result.

The initial audio draft separately named 1,800 seconds for discrete work and
40-million integrands / 1,200 seconds for the new original full-window job.
A12 froze 600 seconds and 64-million integrands, with an input-only planning
bound above 46 million when retained original diagnostics are included. Leaving
both authorities would make the admission criterion ambiguous. Root aligned
the contract to A12 before candidate code/errors. The old 64-probe protocol and
its 10-million ceiling remain unchanged; no historical result is rebound.

The protocol correctly separates discrete grid parity, new grid continuous
grading, expansion of the original F rows and conversion/native comparison.
S07 has an explicit DC residual witness; S10/S11 have noncollapse criteria;
S08/S09 retain an underflow tier without a nominal relative-error claim.
Their continuous comparisons use the relevant gate's own peak threshold in
the absolute allowance; discrete parity retains its separate `1e-10` threshold.
All original rows and refusals remain visible. An unimplemented oracle and its
expected facts must be frozen before examining candidate errors. Numerical,
continuous, resource and oracle-independence grades all remain unrun here.

## Reproduction and next step

Read-only commands used include `git status --short`, `git rev-parse HEAD
HEAD^{tree}`, `sha256sum` on the bound inputs, `cat`/`sed` for the sources, and
the following bounded standard-library arithmetic/index reproduction. The
fixture-domain inspection additionally asserted every source, route, threshold,
speed, target and ordering condition against the contracts; it ran no renderer.

```sh
python3 -B - <<'PY'
import hashlib, importlib.util, math
from fractions import Fraction as F
p=(1<<32)-1; r=p-1; T=1<<16
for name,a,b in [
    ('S10',F(255*T-1)+F(p-1,p),F(255*T)+F(1,r)),
    ('S11',F(256*65535-128)+F(1,p),F(256*65535-128+255)+F(1,r))]:
    d=(b-a)/T; q=(a+b)/(2*T)
    print(name, float(a/T)==float(b/T),
          (d.numerator.bit_length(),d.denominator.bit_length()),
          (q.numerator.bit_length(),q.denominator.bit_length()),
          float(d).hex(),float(q).hex())
maximum=closed_maximum=positions=0
for N in range(1,257):
    first=completed=0
    for m in range(N):
        assert completed-first<=8191
        lo=max(0,(m-32)*256+1); hi=min(256*N,m*256-1)
        if lo<=hi: assert first<=lo<=hi<completed
        first=min(completed,max(first,max(0,(m+1-32)*256+1)))
        completed+=256; maximum=max(maximum,completed-first)
    completed+=1; closed_maximum=max(closed_maximum,completed-first)
    assert completed-first<=8192
    for m in range(N,N+33):
        lo=max(0,(m-32)*256+1); hi=min(256*N,m*256-1)
        if lo<=hi: assert first<=lo<=hi<completed
        first=min(completed,max(first,max(0,(m+1-32)*256+1)))
        positions+=1
    assert first==completed
    positions+=N
print('ring/output positions',maximum,closed_maximum,positions)
s=math.ulp(0.0); product=F(s)*F(s)
assert product>0 and float(product)==0.0 and F(s)>=product
print('minimum product',product==F(1,1<<2148),s.hex())
spec=importlib.util.spec_from_file_location('cases','tests/reference/contact_audio_cases.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
cases=mod.all_cases()
print('fixtures',len(cases),hashlib.sha256(mod.canonical_bytes(mod.manifest())).hexdigest())
print('outputs/FIR/visits',
      sum(c['frames']+33 for c in cases if c['frames']),
      sum((c['frames']+33)*8193 for c in cases if c['frames']),
      sum((256*c['frames']+1)*9*len(c['keys']) for c in cases if c['frames']))
PY
```

The next step is isolated implementation and independently frozen oracle
construction under these bindings, then source review and actual required
gates. No production audio readiness is implied. Physical contact/loading
evidence, Engine/host integration, full-organ or indefinite processing, device
deadlines and platform retirement remain separate. **Literal whole-interface
1:1 remains open, unmet and unwaived.**

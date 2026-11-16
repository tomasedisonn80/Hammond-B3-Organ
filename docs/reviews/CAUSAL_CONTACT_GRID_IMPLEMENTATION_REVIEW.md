# Causal contact grid: independent implementation review

**A19 (`/root/w04_a19`), 16 November 2026. No blocking discrepancy found.**
Source/arithmetic admission is conditional on separate native differential,
lifecycle/rollback and resource gates. This is not final runtime acceptance.

## Source identity

Reviewed the active working overlay and admitted contract. SHA-256 bindings:

| Input | SHA-256 |
| --- | --- |
| `docs/CAUSAL_CONTACT_GRID_CONTRACT.md` | `ba851e6af0601b52aef73d4b9effb64dffac3ef5e230eff7015e10e58a4ecb4e` |
| `include/hammond/research/CausalContactGrid.h` | `69c655897b24688873472c559c952d9932f76b0cbed5c3eabd9a9da5b3a5d89f` |
| `src/research/CausalContactGrid.cpp` | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |

Line references below are to that C++ implementation unless prefixed otherwise.

## Correctness and proof edges

- **Configuration/lifecycle (16–29, 138–153, 289–320):** phase precedes validation;
  only active configurations are inspected/copied into zeroed storage. Unsigned
  `off < on <= 2^48` also bounds `off`. Construction, ready reprepare, closed
  reset/reprepare and N=0 closure preserve canonical histories. Closure changes
  targets/anchors and count/phase without travel or edges.
- **Anchors/hysteresis (32–70, 224–268):** every changed target anchors the already
  evaluated integer position; equal targets preserve anchors even after arrival.
  Tied changes are not coalesced. Reachable states maintain
  `open => position < on` and `closed => position > off`: incoming equality
  switches the bit, while holds/commands preserve position and bits. Thus a
  outgoing edge cannot sit at an excluded interval start. After arrival, the
  bits or target/position eligibility prevent repeats. Unsorted/repeated
  contacts remain independent.
- **Arithmetic (56–69, 75–131):** elapsed ticks are at most `2^28`; widening
  before multiplication gives displacement below `2^60`, clamped before either
  position operation. Distance is at most `2^48`; whole roots stay in 64 bits
  until interval admission. For speed 1, `on=target=2^32+1`, command tick zero,
  the one-frame position is 65536 and the future root is rejected, never wrapped
  into tick 1. Proper fractions have positive denominators; the 64-step Euclid
  guard exceeds the 32-bit bound. Unsigned widened fraction products remain
  below `2^64`, including values above `INT64_MAX`. No floating-point comparison
  can merge close roots. Defensive overflow returns are unreachable by induction
  from prepared state under the admitted domains.
- **Ordering/partitions (189–204, 256–284):** each positive interval resolves
  all keys before applying any command at its end. Its at-most-36 edges sort by
  exact time/key/contact, then append in chronological interval order. Targets
  exclude the call endpoint; edges include it. The next call excludes that
  resolved endpoint, preventing duplicates. Persistent anchors make position and
  roots independent of partition boundaries; future commands cannot revise
  already committed incoming equality.
- **Transactions/precedence (156–221, 289–316):** phase, remaining frames,
  remaining command count, every target domain, then ordering match the contract.
  Subtraction checks precede addition, iteration and narrowing. State/edge staging
  and actual output-capacity checks precede any caller write. Failure retains
  live state/output bytes; retry copies live state afresh. Invalid prepare/close/
  reset cannot commit. This assumes valid disjoint memory and serialized access.

## Bounded work and portability

Header lines 111–115 embed two snapshots, 4608 staged edges and 36 interval edges.
No dynamic storage, I/O, locking, recursion or per-tick stepping is present.
The traversal has at most M+1 intervals.
Each active incoming movement consumed a prior command, so `A+M<=512`; each
monotone movement changes each contact at most once, giving at most 4608 epoch
edges. Batch insertion sort uses at most `sum n(n-1)/2 <= 35E/2` comparisons,
not a full-output sort. Other traversal ceilings follow. Object/scratch bytes and
hook/operation receipts remain the resource gate.

GCC 14.2.0 strict C++20 syntax passed from the repository root:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -fsyntax-only -Iinclude src/research/CausalContactGrid.cpp
```

The implementation uses standard unsigned fixed-width arithmetic without
`__int128`; this compile does not establish MSVC/AppleClang execution or deadlines.

## Independent evidence and remaining acceptance

Inspected all native known answers and oracle/self-tests. Native cases cover
arrivals, holds, ties/anchors, endpoints, three-rate partitions, full travel,
unsigned products and 4608 edges. The oracle reconstructs per-key affine pieces
and interpolates contacts with `Fraction` independently of native crossing
helpers; it does not model native failure/lifecycle transactions. Tests do not
replace the reachability/arithmetic arguments above.

A21 differential, A22 rollback and A23 allocation/operation receipts remain
required. No native test pass is claimed here. Platform/callback deadlines,
Engine/host/filter integration, indefinite/full-organ capacity, binary64
equivalence and physical calibration remain separate gates.

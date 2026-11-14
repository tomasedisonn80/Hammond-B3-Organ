# A20 — Actual late transaction rejection and recovery

## Assignment and outcome

Actual worker `/root/w04_a20_transaction_acceptance`, wave 4, 14 November 2026.
Owned only:

- `tests/test_rotary_renderer_transactions.cpp`
- this note
- `reports/a20-transactions.json`

**Both A11 whole-process late-failure experiments pass on the shipping renderer.**
The ordinary optimized run and a separate run with a 1 MiB stack limit pass with
identical output. No production defect was observed; no product, public/private
header, contract, CMake, shared build, status or assignment-manifest file changed.
No nested worker, commit or publication was created.

Read the standing agent rules, complete M0–M9 plan, current session scope and
checkpoint, current status/next-step/log pointers, atlas review and A04's rotary
reading, the frozen renderer contract, A11's complete transaction review and note,
and the shipping renderer/history/path/motion declarations and implementations.
A16's admission/event tests were inspected to keep this test focused on actual
late rollback instead of duplicating ordinary argument-admission coverage.

The [compact report](../reports/a20-transactions.json) retains exact commands,
compiler, fixture/profile identity, source hashes, executable hash, results and
compiler stack records. The prior checkpoint HEAD was
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. That HEAD is context; the per-file
hashes identify the actual tested uncommitted source. They were unchanged
between the precompile check and the check after both executed runs.

## Exact synthetic fixture and independent expectation

Both fresh fixture pairs use 48,000 Hz, maximum block size 64, sound speed
300 m/s, zero rotor radii/origins and coincident microphones at
`{3/128, 0, 0}` metres. Reference distance is also `3/128` metres. Selected
geometric zero fields retain negative-zero bits, so field comparison is not
ordinary floating equality. The source positions are stationary, while motion
owners have nonzero speed, turns and real command transitions:

| Rotor | Slow / fast rad/s | Up / down tau s | Direction | Initial phase rad | Initial speed rad/s | Original command |
| --- | --- | --- | --- | --- | --- | --- |
| Horn | 3 / 90 | 0.007 / 0.013 | +1 | 6.25 | 47 | Chorale |
| Drum | 4 / 75 | 0.011 / 0.019 | −1 | 0.035 | 61 | Chorale |

The explicit profile projection, serialized as canonical JSON with the rule in
the report, hashes to
`a25d0811eba736068166c4a400dfd117fa4520fedd3104dacb498defcafb6b81`.
These are engineering fixture values, not specimen measurements.

The independent arithmetic is `48000 * (3/128) / 300 = 3.75` frames of travel,
`D=4`, `H=10`, flush=8, and unit pressure gain. With two frames of observation
lag, input frame `n` queries emission `(n-6)+0.25`; its four waveform supports
are `n-7, n-6, n-5, n-4`. Their closed-form weights are
`{-7,105,35,-5}/128`. The scratch-output oracle evaluates these weights directly
in long double against the original logical input sequence; it calls no native
path solve, history query or interpolation kernel.

Each subject/control pair first accepts 40 distinct bounded horn/drum samples,
with seven real commands including one at preload offset 40. The signal is
`(((frame * multiplier + shift) % 257) - 128) / 256`, with multipliers/shifts
`37/9` and `71/23` and explicit signed zero when applicable. Both motion owners
have nonzero turns and committed diagnostics end at frame 39 before injection.

Each rejected request contains 37 valid frames and 16 ordered events. The
stream includes interleaved horn/drum changes, alternating same-offset commands,
one repeated unchanged command, changes at the failing boundaries and three
offset-37 events. The second experiment's inputs overlap by 36 samples in one
38-double allocation: horn starts at element zero, drum at element one. Its
accepted control uses disjoint copies with identical logical values. This
qualifies permitted input overlap specifically through a late failed transaction
and its subsequent accepted replay.

The independent segment expectation uses two small public `RotaryMotion` owners
and the original absolute ordered command stream. It records original segments
for logical intervals, without any ring or undo implementation. Journal record
`n` must contain the values of logical interval `n-H`; this is a direct timeline
calculation. There is no handwritten copy of the production rollback loop.

## Executed late failures

| Experiment | Only injected persistent field | Actual status | First failing input frame | Completed scratch samples per channel | Written journal records | Slot visit counts |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Later support read | Horn frame 39, slot 9, changed to finite `2.0` | `InvalidBuffer` | 43 | 3 | 4 | `1,1,1,1,0,0,0,0,0,0` |
| Partial second motion append | `motion_history[1].max_frame_`, changed from 4,147,200,000 to 63 | `TimelineOverflow` | 63 | 23 | 24 | `3,3,3,3,2,2,2,2,2,2` |

For the first failure, frames 40–42 query supports `33..36`, `34..37` and
`35..38`. Frame 43 first reads poisoned support 39; its current write slot is
3, so the poison at slot 9 has not retired. The request's ordinary input spans
contain only admitted finite values. This is an actual late history/kernel
failure, not invalid-input preflight.

For the second failure, frames 40–62 complete, crossing two full ten-slot rings.
The 24th journal record identifies frame 63 and slot 3. The shipping process
order is record-live, horn waveform push, drum waveform push, first motion
append, then second motion append. Only the last ring has the shortened limit;
both owners and the other three rings keep their original limits. Thus this
reaches the partial-write path before the second motion append returns its
specific `TimelineOverflow` status. Four slots have three separate overwrite
records and six have two; a first-write-only journal, forward restoration or
failure to recover that partial frame would fail the physical-slot assertions.

All 4,096 journal entries and both 4,096-element output scratch arrays are
seeded with distinctive markers before the rejected call. Afterward the test
checks every live record's slot, both old sample bit patterns and both original
segment field patterns against the logical timeline. Every following journal
record remains the seeded marker. Both scratch channels contain exactly the
expected three or 23 independently checked samples; all following scratch
elements remain marked. This is direct evidence of late progress in the current
implementation. **Scratch and journal work bytes are deliberately excluded from
the rollback equality guarantee**; this observation does not turn their current
contents into a public persistence promise. A future deliberate scratch-clearing
implementation would need an equivalent progress observation.

The largest observed scratch-vs-closed-form errors were
`8.163469900068776e-13` and `8.2511775190141634e-13`, below the explicit
fixture tolerance `1e-11`. The small differences reflect the bounded solver's
padded delay endpoints. Both failure results report a maximum of two geometry
evaluations per completed solve and maximum residual
`2.3689817468808272e-17` seconds. Their nonzero work and scratch progress are
independent evidence that processing reached the interior of the block.

Nine and thirteen supplied events respectively lie at boundaries reached before
rejection; those counts come from the reached boundary and original event
stream, not an invented public event counter. Both results return **zero events
consumed**, preserve the original physical owners/diagnostics, and leave the
offset-37 commands unpublished. Accepted replay later verifies the final
original segments against the independent motion-owner timeline.

## Exact preservation and future continuation

The snapshots are heap-owned vectors of canonical 64-bit field words. Doubles
use `std::bit_cast<uint64_t>`; scalar fields and enums preserve their values.
No padded object representation is compared. Every snapshot includes:

- All public copied state, profile, spec, capacity, flush, latency, path bounds
  and diagnostics, plus corresponding private stored configuration/diagnostics
  and each path's prepared flag. Prepared path solving is const.
- Every private waveform and motion-ring metadata field, with all 32,768
  waveform backing slots and all 32,768 motion-segment backing slots. This
  includes the inactive backing slots beyond active `H=10`; every segment's
  anchor, state, target, tau and direction is compared by fields.
- Both owners' complete current getter projections. Resetting small owner
  copies exposes and compares their otherwise private original reset seed and
  command without mutating the subject or requiring another shipping friend.

The snapshot after each injection differs from the pristine snapshot in exactly
one canonical field. This independently checks that only the intended sample or
limit changed. The post-rejection snapshot must match that **injected** pre-state
exactly, retaining the poison or shortened limit. The full caller-output
allocation has 95 doubles, including seven guards before, between and after the
two 37-frame outputs: all **760 bytes of double values** remain bit identical
for each failure, with no struct padding involved.

Only after those checks does the test restore the single injected field. The
complete snapshot then matches pristine subject and untouched control. Each
pair accepts the original 37-frame request followed by 31 further frames in
partitions `1,9,11,10`, with fresh offset-zero ties after the earlier offset-37
events. Short calls overwrite only their required scratch prefixes. Outputs,
all physical backing slots, metadata, configuration, owners and diagnostics
remain bit identical to the unmodified control after every accepted call.

Per executable run, the two experiments perform 18 full snapshot comparisons,
each containing **262,504 canonical field words**, for **4,725,072 field-word
comparisons**. They compare 874 output values including guards across preload,
rejection and continuation. Each pair verifies 68 accepted continuation frames
after fault removal, including a 31-frame suffix longer than two complete
histories. The report retains the exact counts; these are bounded experiments,
not a long-duration waveform-parity or real-time result.

## Reproduction and stack evidence

Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Compiler: `c++ (Debian 14.2.0-19) 14.2.0`. The direct optimized strict build used
the current production `.cpp` files, avoiding stale-library/header mixing:

```sh
mkdir -p ../a20-transactions
c++ -std=c++20 -O2 -DNDEBUG \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -fstack-usage -Iinclude -Isrc -Itests \
  '-DHAMMOND_TEST_PROFILE="/workspace/scratch/e3cacb90cc81/build/nominal.b3p"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ"' \
  tests/test_rotary_renderer_transactions.cpp \
  src/RotaryMotion.cpp src/RotaryPropagation.cpp src/RotaryHistory.cpp \
  src/RotaryStreamingPath.cpp src/RotaryRenderer.cpp \
  -o ../a20-transactions/test_rotary_renderer_transactions
../a20-transactions/test_rotary_renderer_transactions
bash -c 'ulimit -s 1024 && exec ../a20-transactions/test_rotary_renderer_transactions'
```

All three compiler/executable commands exited zero. The profile macro satisfies
the shared test header; this executable uses its explicit inline rotary profile
and does not load `nominal.b3p`. `CHECK` assertions remain active under `NDEBUG`.
No shared CMake configure/build or CTest, sanitizer, leak checker or allocation
interposition was run by A20.

The ABI reports storage size **2,721,712 bytes** and `MotionSegment` size
**56 bytes**. The storage and full snapshots are heap owned. GCC
`-fstack-usage` reports **1,296 bytes** for `RotaryRenderer::process`
(`dynamic,bounded`), **1,088 bytes** for the largest test function frame, and
2,208 bytes for the largest compiled function frame (`prepare`). These are
compiler per-function figures, not measured complete call-chain peaks; the
separate actual 1 MiB stack execution also passes. Raw `.su` hashes are retained
in the report; reproducible executable/stack intermediates stay in the owned
sibling `a20-transactions` directory.

| Input/artifact | SHA-256 |
| --- | --- |
| New transaction test | `fd42656661ed4ea8a75bd207fd971c9ff90e92efec3c16a30c60e33cb092bced` |
| Shipping `RotaryRenderer.cpp` | `b48d82deae98d087493a25976f767c995d4e1db0ae79acb8c699a62dc21c7d04` |
| Private storage header | `56a2fb6e0c3af5b7f686e2d2dc2fad07fd7858920657812ba6d4e28153637796` |
| Shipping `RotaryHistory.cpp` | `4f3c4fbd957f7cc9131b1f4e7c6e77f69df1b7e85c9ba4073de59fe52322a0f5` |
| Shipping `RotaryStreamingPath.cpp` | `ed79d6ce3653f52f5f9a7d43d4f5cf9743f18cc3c9458ee7734928e42dcbae50` |
| Executed optimized binary | `53e08e30fc2ae846e0f06f4754cf6f1eeb2bdabc5f804c080ce69a309bac43ee` |
| Compact report | `db196a62bdaf254a7269cdb8d7e340853d4017529ffdb571ef1d75498ef704e3` |

## Next concrete gate and limits

The integrator can discover/build `test_rotary_renderer_transactions` through
the existing test glob and private `src` include rule, then run its CTest on a
coherent integrated tree. A29 should place these same two actual late calls
inside calibrated allocation/deallocation intervals with fixtures/snapshots
prepared outside measurement. A43 owns the full coherent sanitizer/leak gate;
platform qualification remains separately observed work.

These results qualify the two specified transaction paths, complete restoration
and their accepted future continuation. They do not close full R4 numerical
parity, R5 reconstruction/alias policy, R6 host/device integration or deadlines,
the physical cabinet gate, or any dry Engine/state/UI behavior outside this
independent renderer. No such product path was changed.

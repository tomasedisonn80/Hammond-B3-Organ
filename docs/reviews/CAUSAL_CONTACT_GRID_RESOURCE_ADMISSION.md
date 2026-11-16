# Causal contact grid: resource admission

**A28 (`/root/w05_a28`), 16 November 2026: no blocker.** Admit the fixed-storage/
work claims in frozen [contract](../CAUSAL_CONTACT_GRID_CONTRACT.md) sections 5–6
and A23's Linux observations, within the limits below. This supplies the resource
gate in the [implementation review](CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md).

## Inputs and replay

Overlay of `4aac394cde4da40906b615573a8779aee2d9a37a`:

| Input | SHA-256 |
| --- | --- |
| Production implementation | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |
| Resource fixture | `fcb153c854d788f6b97859364088655ed7a81399818246c754e6c9409ab2515c` |
| Receipt generator/verifier | `80a7b8dfc9ab923037c52e3b199806e762984bb6b34b458675a38f9f0be00881` |
| A23 resource report | `03a585b1f28313dccd5a99240b2a35b912464b51d56eb0a56da6504cf366d10a` |
| Normal executable | `79a426f9f2855925f982d8130d52accd139c37b252a16420746bcadda49cdacf` |
| Instrumented executable | `1c206472e554eb1fe2bd6881de668898646d5a1eb484eaa992446814d6022a15` |

[Independent audit](../development/2026-11-15-streaming-continuation/reports/A28-resource-audit.json)
binds 19 source/generated/raw/build/compiler/object files. Its SHA-256 is
`1b10c8f4eb127114c741448fde97c142c394a9688e45350daa02620381cd0b34`.
Reran from the repository root, with 20-second limits:

```sh
../build-native/test_causal_contact_grid_resources
../resource-work/test_causal_contact_grid_resources_instrumented
```

Both exited 0 with empty stderr and reproduced retained JSON **byte for byte**.
I independently recomputed all bounds, maxima, totals and six predictions.
No rebuilds or subject edits.

Compiler and binary comments agree on GCC Debian 14.2.0-19, `x86_64-linux-gnu`.
Both commands use C++20, `-O3 -DNDEBUG`, strict warnings and `-Werror`. Normal
links the production archive; diagnostic uses the unchanged fixture/generated
TU without that archive; its build exited 0. The core object matches its archive
member and has only undefined `memset`. These checks corroborate root's build/
CTest evidence; the receipt verifier itself does not rebuild.

## Instrumentation and observation

Ten unique anchors match source lines: validations 177/296, application 33,
position 44, contacts 243, root 99, gcd 106, remainder 111, comparator 121, caller
copy 218. Independent replay exactly reconstructs the diagnostic; stripping its
three-line prologue and ten increments recovers production bytes. The 656-byte
header contains nine `uint64_t` thread-local counters and reset/read helpers.
Integer roots bypass gcd; false comparisons count; committed-copy counts exclude
sort shifts/staging copies.

Each build observes **192 scopes**: prepare 36, process 63, snapshot 36, close 33,
reset 18, construction/destruction three each; 64 at each of 44100/48000/96000 Hz.
All report zero allocations/frees. Six calibrations use volatile function pointers
to check 12 allocations/12 frees, nonnull storage and 64-byte alignment. Hooks
cover scalar/array, nothrow, aligned and sized-delete forms. Backing allocation,
setup, checks, hashing, formatting and final release stay outside armed calls.

Release-active checks assert 14,040 edges and 36 semantic snapshots per build.
Receipts agree except instrumentation fields, including statuses and field-wise
FNV `653c948373cd8d8d`; full edge/snapshot arrays are not retained in these JSONs.
Statuses 0–7 occur; overflow is not injected. Byte canaries check
whole-output preservation for grouped rejections/empty calls and short capacity;
the maximum successful retry preserves its extra edge slot. Separate lifecycle/
oracle and memory-safety qualification remain necessary.

## Storage and finite work

Observed ABI: object **113,056 B**, snapshot **800 B**, edge **24 B**. Scratch
**112,256 B** = staged snapshot 800 + staged edges 110,592 + interval edges 864;
Live state is 800 B; fixture backing 342,496 B excludes summary/allocator overhead.
Production arrays are fixed; the fixture uses heap backing. Caller stack use and
compiler stack frames are unmeasured.

| Operation | Observed per-call maximum | Frozen ceiling |
| --- | ---: | ---: |
| Target validations / applications, each | 512 | 512 |
| Position evaluations | 2,052 | 2,052 |
| Contact examinations | 18,378 | 18,468 |
| Reached roots / committed copies, each | 4,608 | 4,608 |
| Gcd normalizations | 36 | 4,608 |
| Euclidean remainders | 1,620 | 294,912 |
| Edge comparisons | 80,640 | 80,640 |

Incoming movements consumed prior commands, so `A+M<=512`; each monotone movement
crosses each contact at most once: `E<=9*(A+M)<=4608`. At most `M+1` intervals
visit K positions and 9K candidates each. Euclid's larger 32-bit starting operand
gives the conservative 64-step bound. Insertion sorting satisfies
`sum(n*(n-1)/2)<=floor((9K-1)*E/2)` for `n<=9K`. Other methods/rejections also
have fixed storage/traversals. Counters describe operations, not all instructions.

Capacity uses 128 batches of 36 reverse-order roots: 4608 edges and
`128*630=80640` comparisons, including short output with zero committed copies
and successful retry. Distinct ticks attain `4*513=2052` evaluations; initial
holds save 90 candidate visits. Independent Euclid replay takes 45 remainders
per Fibonacci root, three per maximum-speed root. N=0 closure validates/applies
512 commands without motion. All six predictions hold at three rates.
**165,888** epoch examinations is source-derived for successful advancing calls;
arbitrary retries/rejections/empty calls have per-call bounds only.

Hooks observe current-thread global C++ new/delete, not all C/system allocation,
other threads, locks or I/O; source inspection supports their absence here.
Other ABI/compiler runs and the MSVC aligned branch remain unexecuted. Source
bounds/whole-test wall times establish no callback deadline. Stack budgets,
hosts/devices, audio filtering, Engine integration, indefinite/full-organ capacity
and physical calibration remain separate gates.

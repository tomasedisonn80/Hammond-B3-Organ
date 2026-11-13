# Prepared pedal routing contract

The `linear-pedal-bus-reference-v1` kernel converts one shared source frame
into four dimensionless bus excitations. It retains all 200 pedal/contact
positions independently. It owns no oscillator, clock, physical reactor,
drawbar mixture or electrical calibration. The separate
[integration contract](PEDAL_INTEGRATION_CONTRACT.md) defines the following
nominal playable division. Actual implemented and executed gates belong in
[STATUS.md](STATUS.md) and the [pedal-session record](development/2026-11-13-pedals/README.md);
this contract is not itself an acceptance result.

The documentary basis is [atlas pp. 139-144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139),
especially the independent linear fixture allowed on p. 144. The preserved
[map and provenance](PEDAL_ROUTING.md) and later
[factory comparison](FACTORY_REFERENCE.md) establish routing identities. They
do not establish contact timing, branch conductance, pedal loudness, reactor
response or a controller MIDI octave.

## Identity and fixed storage

The public declarations are in
[`PedalRouting.h`](../include/hammond/PedalRouting.h), with the scalar
implementation in [`PedalRouting.cpp`](../src/PedalRouting.cpp).

| Type or constant | Exact meaning |
| --- | --- |
| `PedalId` | A distinct wrapper around a one-based pedal value, admitted only in 1-25. Its default value zero is invalid. |
| `kPedalCount`, `kPedalContactCount` | 25 pedals and eight contact positions per pedal. |
| `kPedalContactPositionCount` | 200 positions, in pedal-major/contact-minor order. |
| `PedalBus` | Brown=0, Red=1, Orange=2, Yellow=3; `kPedalBusCount` is four. |
| `PedalRoute` | Pedal ID, contact index 0-7, bus, and `optional<ToneId>` connection. |
| `PedalRouteDefinition` | Exactly 200 route records. |
| `PedalWeights` | Exactly 200 independently supplied, dimensionless `double` weights. |
| `PedalSourceFrame` | Exactly 91 source-normalized `double` samples, indexed by tone ID minus one. |
| `PedalBusFrame` | Exactly four dimensionless `double` bus sums in the bus order above. |
| `PedalContactStates` | Exactly 200 independent Boolean closure states, including disconnected positions. |
| `PedalContactEdit` | Pedal ID, contact index and requested closed/open state. |
| `kPedalDrawbarCount` | Two controls reserved for the separate integration contract; the routing kernel does not apply them. |

`make_pedal_id(uint32_t, PedalId&)`, `pedal_id_to_index(PedalId, size_t&)`
and `pedal_contact_to_index(PedalId, uint32_t, size_t&)` validate before
conversion. Failure returns false and preserves the destination. A pedal ID,
contact column, source ID, physical terminal and MIDI note remain different
domains. Passing a number through an unchecked narrowing cast does not validate
its original domain; use the checked constructor when admitting wider input.

Route position `j` must identify pedal `j / 8 + 1`, contact `j % 8` and bus
`(j % 8) / 2`. An absent `tone` is an electrically unconnected branch. An
engaged tone of zero, or a tone above 91, is invalid. Repeated source numbers
retain independent branch identity and state before their contributions sum.

## Two separate admission boundaries

**Kernel preparation is structural admission.** It accepts any complete
canonical 200-position definition satisfying the IDs, bus memberships, source
bounds and normalization below. It does not require a particular number of
disconnections or certify that an arbitrary caller-supplied definition is the
factory map. This permits independent basis and boundary fixtures.

**The offline compiler admits the specific documentary map.** It checks the
unchanged `atlas-derived-b3-c3-pedal-v1` input, its later factory attestation
and both retained CSV transcriptions. The resulting table has 195 connected
positions and five explicit disconnections. Brown column 1 is disconnected on
pedals 8-12; pedals 1-7 repeat the same source through distinct Brown column 1
and Red column 2 branches. No formula-only comparison substitutes for the CSV
cell checks. These are documentary/software identities, not specimen continuity.

## Kernel operations and failure semantics

All kernel operations are `noexcept`, use value-owned fixed storage, and require
stopped or same-processing-thread access. There is no concurrent publication or
UI-reader protocol. No operation allocates, accesses a file, parses text, locks,
logs, sleeps, advances a source or increments elapsed time.

| Operation | Admission and result |
| --- | --- |
| `prepare(span<const PedalRoute>, const PedalWeights&)` | Requires exactly 200 canonical routes and all 200 finite weights in [-1,1]. Invalid input returns `InvalidProfile`, preserving the entire prior kernel. Success copies all routes and weights, opens every contact and marks the kernel prepared. There are no implicit default weights. |
| `apply_contacts(span<const PedalContactEdit>)` | Error order is `NotPrepared`, then `TooManyEvents` for more than 200 edits, then `InvalidEvent` for a bad pedal/contact. Preflights the whole batch before changing any contact. Success applies supplied order; the last repeated edit wins. An empty batch is `Ok` only after preparation. |
| `render_frame(const PedalSourceFrame&, PedalBusFrame&) const` | Error order is `NotPrepared`, then `InvalidBuffer` if any of all 91 samples is nonfinite or outside [-1,1], including unused samples. Failure preserves destination and kernel. Success writes all four sums and changes no kernel state. |
| `contact_closed(PedalId, uint32_t, bool&) const` | Unprepared or invalid queries return false and preserve destination. Successful queries include disconnected positions. |
| `prepared()` | Whether a successful preparation has occurred. |
| `closed_contact_count()` | Counts all 200 states, including inaudible positions; zero before preparation. |
| `contacts_snapshot()` | Returns a value copy of all 200 states; all false before preparation. It is diagnostic state, not a concurrent snapshot or musical preset. |

Preparation checks every weight, including weights on disconnected branches.
Successful re-preparation intentionally opens contacts; it is not a live
history-preserving model swap. Failed preparation preserves routes, weights,
contacts and prepared status. A caller may retire or modify its input buffers
after successful preparation because the kernel retains no borrowed routes or
weights.

For one frame, start four sums at zero and visit positions 0 through 199. For
each closed, connected position, add `weight[j] * sources[tone_id - 1]` to that
position's bus. There are at most 50 terms per bus and each term's absolute value
is at most one, giving an absolute bus bound of 50. Null positions still retain
contact state and contribute nothing. There is no polyphony normalization,
limiter, deduplication, note priority, attack/release envelope or drawbar law.

The caller supplies the already computed shared source frame. The same array
must feed manual, percussion and pedal consumers; neither calling this kernel
nor editing contacts may generate another source sample. A source-only harness
can demonstrate this boundary before Engine integration. Such a harness result
does not establish that a later Engine integration obeys it.

## Offline compilation and retained identity

The compiler is a Python standard-library authoring tool. The complete explicit
invocation is:

```sh
python3 tools/compile_pedal_routing.py \
  --input data/pedal-map.json \
  --reference data/references/factory-table-iii.json \
  --review-a data/references/review-a-pedal.csv \
  --review-b data/references/review-b-pedal.csv \
  --output build/generated/hammond/generated/PedalRoutingData.h
```

Input byte bounds are 32 KiB for the map, 256 KiB for the comparison manifest,
and 8 KiB for each CSV. The compiler reads regular files, rejects unreadable,
oversized or changing inputs, applies strict UTF-8/JSON and duplicate-field
rules, and reuses the existing map and comparison validators. It compares all
200 cells against each CSV, including blanks, and verifies their retained raw
byte counts/hashes plus the map's raw and canonical hashes. Reformatting an
attested map or CSV without a new attestation fails the exact-byte gate. The
manifest's accepted semantic identity is separate from its actual raw-byte
digest; its generated digest changes if its accepted formatting changes.

Only after successful admission is a deterministic LF C++ header of at most
64 KiB formed. `hammond::generated::kPedalRoutes` contains all 200 explicit routes,
with `std::nullopt` for disconnections. CMake generates it in the build tree,
adds its private include root and makes the core depend on the generator and
all source inputs/validators. The generated header is not an edited source
profile and does not change `B3PROFILE1`.

Output publication uses a temporary file in the destination directory and an
atomic replacement after validation. Input/admission rejection and failed
replacement preserve an existing output. Input/output path aliases are rejected;
source input bytes are never written. A later stdout/reporting failure can return
failure after the new header has already been published; callers must not infer
that every nonzero CLI result means the destination is unchanged. These are
file-publication guarantees, not a transaction with concurrent external editors
or a promise to roll back newly created directories. CLI status is zero on
success, one for validation/publication/reporting errors and two for usage errors.

`compiled_pedal_routes()` returns a const reference to the immutable generated
definition. `compiled_pedal_identity()` returns program-lifetime string views:

| Field | Meaning |
| --- | --- |
| `model_id` | `linear-pedal-bus-reference-v1` |
| `map_id` | `atlas-derived-b3-c3-pedal-v1` |
| `map_raw_sha256` | Digest of the admitted map bytes. |
| `map_canonical_sha256` | Digest under the retained project's JSON canonicalization convention. |
| `factory_comparison_id` | Separate `factory-table-iii-comparison-v1` attestation. |
| `factory_comparison_raw_sha256` | Digest of the actual accepted comparison-manifest bytes. |
| `review_a_sha256`, `review_b_sha256` | Digests of the two admitted CSV byte sequences. |

This metadata describes the compiled documentary input. It does not attach
factory provenance to arbitrary routes or weights passed to `prepare`. An
evidence producer must identify its actual selected routes and weight fixture.
The original map's historical provenance fields remain unchanged; a later
attestation is preserved alongside them rather than rewriting their history.

## Independent acceptance requirements

| Gate | Required observable evidence |
| --- | --- |
| Native identity | Every generated native cell equals both retained CSV cells. Include pedals 1, 7, 8, 12, 13 and 25, all five nulls and the seven repeated-source pairs. |
| Branch independence | Toggle every position separately. Distinct binary-rational weights reveal wrong buses, accidental deduplication and source-index errors. Closing a null branch changes its diagnostic state but none of the four outputs. |
| Numerical reference | Compare source-basis and mixed frames to an independently indexed scalar oracle. Exact rational fixtures agree exactly; non-exact fixtures use a declared rounding bound based on at most 50 contributions, fixed before execution. |
| Admission and atomicity | Reject missing/extra/reordered/duplicate route positions, wrong buses, source 0/92, nonfinite/out-of-domain weights and samples, invalid edits and batches over 200. Compare semantic state and prefilled output before/after rejection. |
| Lifecycle and source history | Verify source-only versus shared-source histories through silence, edits, unused outputs, zero-frame control applications, supported rate changes and irregular event partitions. Contacts survive source-rate changes because this kernel has no rate state. |
| Bounded runtime | Exercise all 25 pedals/200 contacts, success/rejection/diagnostic paths, and calibrated allocation/deallocation instrumentation. Record actual workload/timing without declaring an audio-device deadline from an offline run. |

The compiled factory map, generic kernel, compiler, source harness and integrated
Engine each require their own observed evidence. Passing these gates does not
establish calibrated pedal spectra, physical contact motion, a loaded reactor,
complete M3, VST3/device operation or a measured instrument match.

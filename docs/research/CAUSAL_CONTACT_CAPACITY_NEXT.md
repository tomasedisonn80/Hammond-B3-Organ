# Contact capacity and continuing-runtime proposal

**A40, 16 November 2026 — prospective, unadmitted.** This is a source-derived
planning input, not accepted architecture, an implementation, an Engine route or
a physical contact claim. Preserve `causal-contact-grid-v1`, the nominal dry
Engine, 91 shared sources, 47 parameters and `B3CONTROLS4`/readers 1–3.

## Current boundary and source identity

The [contract](../CAUSAL_CONTACT_GRID_CONTRACT.md),
[header](../../include/hammond/research/CausalContactGrid.h) and
[implementation](../../src/research/CausalContactGrid.cpp) admit 1–4 keys,
nine contacts each, 4,096 frames and **512 supplied commands per epoch**, counting
ties, no-ops and closure targets. Rates are 44,100/48,000/96,000 Hz;
`T=65,536` ticks/frame, `Q=2^48` position units and speeds `1..UINT32_MAX`.
Edges number at most 4,608. No converter, audio, drain or continuation/import API
exists. The class is noncopyable; `snapshot()` exposes state but cannot restore it.

The [resource admission](../reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md)
observed 113,056 bytes on its Linux ABI:
`2*800 + 4608*24 + 36*24 = 113056`. Its 192 allocation-hook scopes and finite
work ceilings do not establish indefinite operation, full-organ storage or a
callback deadline. `prepare()` starts zero/open; `reset()` is closed-only and
also clears positions, targets, anchors, bits and epoch counters.
`close_observation()` seals the epoch without simulating release.

Read-only bindings above base `4aac394cde4da40906b615573a8779aee2d9a37a`
(base tree `3605c9ce098a052afc10b2969fefe31e15644fe9`):

| Input | SHA-256 |
| --- | --- |
| Grid header | `69c655897b24688873472c559c952d9932f76b0cbed5c3eabd9a9da5b3a5d89f` |
| Grid implementation | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |
| Grid contract | `ba851e6af0601b52aef73d4b9effb64dffac3ef5e230eff7015e10e58a4ecb4e` |
| Resource admission | `78d59ba1b8224687eaa6127989ed6fd691c3a878b4e61bde21d9527817aba777` |
| `src/Engine.cpp` | `e1f890234bd09edfb0f0aec4f74cb778a950bbc92a48e3e79a99d2ea771029f3` |

The [author-only arithmetic/source receipt](../development/2026-11-15-streaming-continuation/reports/A40-capacity-audit.json)
binds the remaining cited source files and the exact peer drafts read. No build,
native test, new measurement or independent admission is reported here.

## Scale the owned domains

| Existing domain | Required capacity distinction |
| --- | --- |
| Two manuals | `Types.h` defines `2*61=122` keys, MIDI 36–96 per manual, and nine contacts: **1,098 manual contact histories**. Keep `(Manual, MIDI note)` separate from array index and source ID. |
| Pedals | `PedalRouting.h` defines 25 one-based `PedalId`s, **eight** positions each: **200 states**, four buses and two mixtures. `Engine::apply_pedal()` changes all eight ideal contacts together; five disconnected positions still retain bits. A pedal travel/hysteresis model needs its own contract and evidence. |
| Console inventory | 147 playing keys means `122+25`, not 147 nine-contact trajectories. Current contact-state inventory is `1098+200=1298`, not `147*9=1323`. Four drawbar banks and 24 preset controls do not multiply key trajectories. |
| Shared signal field | `Engine::process()` obtains one frame of 91 sources for all branches, including pedals; source phase advances during silence/disconnected output. Do not create one oscillator bank per key, contact or grid shard. |

Sources: [types](../../include/hammond/Types.h),
[pedal routing](../../include/hammond/PedalRouting.h),
[Engine interface](../../include/hammond/Engine.h) and `Engine.cpp` functions
`apply_event`, `apply_pedal`, `rebuild_coefficients`, `process`.
Velocity does not scale steady amplitude. Cancel disconnects routing while
retaining keys; manual `AllNotesOff` immediately opens contacts, including release
travel. Replacing panic with an ordinary target-zero command would change behavior.

[Manual ownership](../../include/hammond/NoteOwnership.h) and
[pedal ownership](../../include/hammond/PedalNoteOwnership.h) separately allow
256 external owners, not 256 physical keys. Preserve first-owner On/final-owner
Off, anonymous FIFO release, identified duplicates, original manual after bus
remapping and scoped panic. Their implementations commit candidate copies only
after complete translation. [PerformanceInput](../../src/PerformanceInput.cpp)
coordinates both adapters with Engine and rejects physical/partial-key bypasses.
Any future direct key-position input needs the same single note authority.

Thirty-one stock four-key objects would occupy
`ceil(122/4)*113056 = 3,504,736` bytes before caller buffers. This does not add
continuation, global ordering, common quotas or an atomic cross-object commit.
A hot key still exhausts its shard's 512-command epoch. Sharding therefore needs
an admitted scheduler; it is not a solution supplied by the current API.

## Continuing history, time and coupled transactions

Propose a separately versioned streaming contract with **bounded transaction
windows and retained history**, rather than repeated observation closure/reset.
At every ordinary boundary preserve targets, positions, original motion segments,
all contact bits, note owners, controls/percussion, all shared source phases,
audio edge-replay bits, unfinished cell pieces, filter/delay rings and cursors.
No ordinary rollover gates the input, drains the filter or reseeds a source.
Reclaim only history proved irrelevant to future output; retain no unbounded
command/edge log in the callback.

Current grid endpoints are `4096*T=2^28` ticks. Merely extending its `uint32_t`
tick domain admits at most `floor((2^32-1)/T)=65535` complete frames; Engine's
legal 65,536-frame block would require endpoint `2^32`. Widening absolute ticks
to `uint64_t` still limits whole frames to `2^48-1` and breaks the current
displacement proof: at maximum speed, `elapsed*speed` fits only while
`elapsed<=2^32+1`. An old completed anchor can eventually violate that check.

Candidate representation: checked `uint64_t` absolute host-frame identity plus
subframe tick/fraction, with bounded local ticks for each processing window.
Never multiply the entire lifetime frame number by T. Compare multi-part times
exactly; establish arrival/clamping before multiplying a large anchor age.
Preserve original command-anchor identity across no-ops. A computational rebase
at an integer boundary requires a separate exact-equivalence proof and cannot
silently alter v1's observable anchors. Local roots can remain reduced
`uint32_t` fractions; widen-before-multiply fraction comparisons remain essential.
Extend A38's source-origin arithmetic without casting an ever-growing absolute
frame directly to binary64. A bounded phase/origin representation needs its own
drift, subframe and sample-rate-segment proof while preserving all 91 histories.

“Continuing” means storage/work independent of elapsed duration within an
explicit finite clock horizon. `Engine::preflight()` already rejects
`frames > UINT64_MAX-frame_clock` with `TimelineOverflow`; preserve that policy,
checked drain/output offsets and nonwrapping command/publication sequences.
Reset per-window accounting independently of musical state. Lifetime diagnostics
need checked counters or documented saturation with a sticky flag, never wrap
used as an ordering decision. Test near limits by injected clocks, not long waits.

The [A37 converter](CONTACT_GRID_CONVERSION_NEXT.md) and
[A38 audio stage](CAUSAL_CONTACT_AUDIO_NEXT.md) are **unadmitted proposals read
for coordination**. A37 certifies a whole finite epoch off-thread; it does not
yet define bounded online conversion or cross-window collision certification.
A38 proposes one staged transaction for trajectory, replay bits, exact cell
pieces, rings, source origin and input/output/drain cursors. It first limits
audio to four keys and N/block ≤256; this document does not enlarge its admission.
Its proposed D=16 and 33-sample nonempty drain belong to a final observation
closure, not each continuing window.

Review a private stage/commit seam before implementing either combined path:
stage conversion, ownership, trajectory and audio; validate all numeric/capacity
results; then perform one nonfailing commit/output copy. Calling the existing
grid first and discovering an audio error later cannot roll it back. Copying its
object bytes or treating a snapshot as an import API is not a substitute.
HostTimeline's existing candidate Engine value copies also cannot simply contain
the noncopyable grid; define ownership of both prepared state copies explicitly.

Two concrete host incompatibilities also need contracts:

- [HostTimeline](../../include/hammond/HostTimeline.h) stages an entire callback,
  including candidate Engine slices, boundary carry and caller output. Its
  [implementation](../../src/HostTimeline.cpp) can flush dense same-sample events
  through zero-frame Engine calls. Grid `process(0, targets, ...)` rejects
  nonempty targets; closure cannot serve as a zero-time update because it seals
  the epoch. Define an atomic boundary update without advancing any clock.
- Engine's stopped/same-thread rate change preserves keys, contact history,
  readiness, phases and frame clock. A38 currently proposes drain/prepare with
  explicit origin. A future route must reconcile those policies, including
  silence, cancellation, panic and stop/tails, before preserving an Engine API
  is claimed. Saved controls remain separate from DSP history.

## Independently checkable capacity example

For a continuing window let K be manual keys, A≤K moving at entry and M the
supplied manual targets **after ownership expansion**, counting ties/no-ops.
Each monotone movement crosses each contact at most once:
`E<=9*(A+M)<=9*(K+M)`. A command-free window can still emit `9K` edges.
The finite v1 bound `9*512` used previous epoch command counts to charge incoming
motion; resetting only that counter does not preserve the proof.

Engine and PerformanceInput cap each call at 1,024 events. HostTimeline instead
caps **raw fresh records plus retained carry** at 1,024 and can emit multiple
candidate slices. It cannot be assigned a 1,024-target callback bound by name
alone. A conservative proposed manual bound is `M<=2R+122`: each emitted first-On
requires a raw record; each final-Off consumes an initial down key or a prior
emitted On. Scoped panic may emit many final-Offs. Thus R=1,024 gives M=2,170.
Independent admission must cover all legal owner transitions and zero-time
flushes; parameter automation and pedal work need separate bounds.

Illustrate K=122, B≤256 frames, M≤2,170 and E≤20,628. Assume the current measured
layout rules: 152-byte key configuration, 40-byte key snapshot, 24-byte local-time
edge and 16-byte target. Then generalized snapshot `S(K)=32+192K=23,456` bytes.
These are **declared layout projections**, not measured sizes of a new class.

| Fixed storage item | Calculation | Bytes |
| --- | --- | ---: |
| Live/staged trajectory snapshots | `2*(32+192*122)` | 46,912 |
| Transaction edge staging | `20628*24` | 495,072 |
| Interval edge staging | `9*122*24` | 26,352 |
| Additional absolute frame fields, one/key plus cursor, live/staged | `2*(122+1)*8` | 1,968 |
| Caller edge destination | `20628*24` | 495,072 |
| Converted target staging | `2170*16` | 34,720 |
| A38 proposed live/staged 8,194-cell double rings | `2*8194*8` | 131,104 |
| One 8,193-double coefficient table | `8193*8` | 65,544 |
| One 256-float output staging buffer | `256*4` | 1,024 |
| **Known planning subtotal** | Sum above | **1,297,768** |

A hypothetical 2 MiB arena leaves `2097152-1297768=799384` bytes **unassigned**.
That is not a fit claim: exact per-route piece/endpoints and summation storage,
source phases, playback bits, controls/percussion/pedal state, owners, host
carry/queues, full-callback output staging, metadata/alignment and compiler stack
remain to be counted. Avoid allocating these large objects on the audio stack.
Prepare storage off-thread; measure actual ABI sizes and peak stack on every
target. Existing Engine/HostTimeline objects must not be silently counted twice
or omitted from a total application budget.

## Work, fairness, overflow and gates

Extrapolating the current interval scanner/insertion sort to this example gives
at most 264,862 key evaluations, 2,383,758 contact examinations, 20,628 roots,
1,320,192 Euclidean remainder steps and
`floor((1098-1)*20628/2)=11,314,458` edge comparisons per window. One interval
alone can require `1098*1097/2=602253` comparisons. These conservative source
bounds exclude audio integration/filtering, ownership scans, automation and
transaction copies. They are not measured CPU times.

Consider per-key event cursors and a bounded merge/heap only under a new exact
ordering/work proof. Preserve time/key/contact order and all incoming-equality
edges before tied commands. Fairness means one captured global input prefix,
bounded service and no starvation of a manual/pedal or release; it does not mean
reordering due events or spreading a chord across callbacks. Per-producer/per-key
quotas require an explicit admission policy. No unbounded catch-up/retry or
drain-until-empty loop belongs on the audio thread.

Keep synchronous core overflow transactional: reject the whole request before
any state/output publication; never truncate, overwrite unread events, drop
releases or coalesce supplied commands to hide capacity exhaustion. Native queue
recovery is separately owned: [Session.h](../../apps/standalone/Session.h) and
`Session.cpp` use a 256-command captured prefix, out-of-queue global recovery on
QueueFull, and permanent sequence exhaustion. Its scoped sound-off explicitly
requires a new tail policy for a non-ideal Session. Preserve those distinctions;
device-buffer silencing after failure is adapter policy, not a successful render.

At 96 kHz a 256-frame callback has `256/96000=1/375` seconds; a one-frame callback
has only `1/96000` seconds. A burst fitting the event count still needs a deadline
contract at the smallest supported buffer. Predeclare hardware/compiler/rates,
callback sizes, simultaneous crossings, dense panics/automation, queue contention,
maximum and tail latency/headroom criteria. Measure the complete callback,
including copies and publication; source bounds and allocation hooks alone do
not qualify its deadline. Allocate/replace/retire profiles and buffers stopped,
with actual callback/reader quiescence; no callback locks, files, logging or frees.

Required sequence, with each result independently source-bound:

1. Freeze converter/finite audio contracts and their independent numerical,
   clipping, partition, rollback, drain and resource gates first.
2. Admit manual/pedal identity, post-expansion quotas, exact time horizon,
   boundary update, continuing history and coupled commit contracts. Prove edge,
   storage, work and overflow bounds; freeze failure precedence and recovery.
3. Implement isolated continuation only after review. Test repeated ring/window
   wraps, slow unfinished travel, arrival/reversal/equality at rollover, incoming
   motion with M=0, no-ops, coincident bursts, near-limit clocks/counters, late
   rejection/retry and bit-identical partition output/state. Use an independent
   oracle with different window boundaries; retained saturation is not evidence
   of preserved motion.
4. Qualify all 122 manuals plus the distinct pedal path, ownership/panic/restore,
   sample-rate/phase, host latency, maximum host callback slicing and publication/
   retirement. Preserve unchanged-default PCM and existing musical contracts.
   Actual device/host deadlines and physical acquisition remain separate exits.

This proposal changes no public API, source, limits, accepted tolerances or
physical claims. Root retains architecture/integration acceptance.

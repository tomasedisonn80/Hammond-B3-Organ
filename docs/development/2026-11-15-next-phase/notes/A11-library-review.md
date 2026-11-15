# A11 — independent named-library contract review

Assignment `/root/w02_a11`, Wave 2, 15 November 2026. Writable checkout:
`/workspace/scratch/116ca0948095/Hammond-B3-Organ`. Owned files are
`docs/REGISTRATION_LIBRARY_CONTRACT.md` and this note. Root supplied baseline
`138fca9af7feca46d10b0e2b65d891f4751a3904`; this worker performed no Git operation
or independent remote observation.

## Decision and identities

**Accepted as amended for root freeze and implementation. No unresolved library
contract blocker remains.** Acceptance concerns the specification, not executed
filesystem, audio, input, platform or visual behavior. Root owns admission and
implementation dispatch. Required implementation evidence remains in contract
section 9.

| Contract input/result | SHA-256 |
| --- | --- |
| A08 authored library contract, before this review | `d8147c50674af1a49a56cc8dd58a85de28acae2fe817b3f76c47a9534efac1ca` |
| Final independently reviewed library contract | `4760d65b27aa154fd86ee09c2cda87bd30f532874cc1a35c62a5b359889703fa` |
| A09 authored browser contract crossread | `23746a7a0630a29cfa7fbcc9da3ec16577a85104b3c936cea07be7c46e9ac765` |

Read all AGENTS.md and PLAN.md, the active session README/checkpoint/assignments,
current shared recovery headings, complete A05/A06/A08 notes, the full library
contract and subsequently the complete A09 browser contract. Reviewed actual
StateFiles, Session command/publication/recovery paths, UiModel control publication,
baseline/input ownership, and main's state-path aliases, save/load, MIDI dispatch,
observation and event/modal paths. Atlas interpretation is supported by A05/A06's
retained full readings; this review claims no new full-PDF reading or capture.

## Findings resolved in the contract

1. **Save acknowledgement needed its original proof.** The latest applied
   sequence can belong to a note, and counters captured only at Save time cannot
   prove that an earlier controls command survived. Retain expected controls,
   desired revision, sequence and submission-time counters until a matching proof
   exists. Reuse only that proved basis. Explicit equal-control Recall still
   publishes exactly one fresh snapshot. A failed snapshot read cannot certify a
   new completion from the displayed cache.
2. **Synchronous failures have a second path.** `post_midi_command` bypasses
   `UiModel::submitted`; waiting for callback counters alone can miss a recent
   failure. A monotonic submission-failure revision covers every post/gate and
   recovery submission. Receipt IDs/revisions fail on exhaustion, and saturated
   Session counters cannot serve as unchanged-failure proof.
3. **Save needs an observable linearization point.** Stage the acknowledged
   bytes, perform final path/name/capacity checks, then obtain the caller's fresh
   coherent receipt authorization immediately before no-replace commit. No main
   event pump intervenes. Audio can publish later; its later edit/recovery does
   not invalidate the valid past copy or undo a committed file. Root explicitly
   agreed this avoids an impossible transaction spanning audio and filesystem.
4. **Protected paths include creations before the destination.** An absent
   `--state` or diagnostic path must not become the library root or a staging
   directory. Existing parent identities plus conservative ASCII leaf comparison
   cover absent case aliases; unsupported `equivalent` on absent leaves is not
   distinctness proof. Unresolvable ambiguity fails safely. Final actual platform
   tests remain required.
5. **A path status check is insufficient for the stated leaf guarantee.**
   Current `load_control_file` checks `symlink_status` before opening an ifstream.
   The library instead requires a no-follow/nonblocking opened leaf, regular-file
   verification on that same object and the existing bounded parser. Replacing a
   candidate with a symlink/FIFO cannot follow it or wait for a writer. This does
   not claim hostile ancestor-namespace isolation. Root accepted the focused
   requirement; native primitives belong to the implementation owner.
6. **Finite admission must include stale and temporary state.** Every
   recognized-suffix item counts toward 128 candidates; all directory items
   count toward 512. Save preflights a fresh complete scan and reserves room for
   the final entry. Its owned staging item counts normally during final scanning.
   No arbitrary prefix is published. Exact-path no-replace preserves a concurrent
   winner, while distinct case variants on a case-sensitive volume remain an
   explicitly observed ambiguity rather than a claimed directory-wide atomic
   transaction. Conversion errors and locale-dependent character admission are
   excluded.
7. **Draft text and saved names need different admission.** A draft may temporarily
   be empty, end with a space, or equal `CON` while typing `CONtemporary`; final
   Save still applies the exact unchanged name rule. Invalid bytes and oversize
   edits reject atomically. A12 confirmed the companion browser correction.

## Cross-contract coordination and preservation

Crossread A09's authored contract and sent the draft-edit finding to independent
browser reviewer `/root/w02_a12`, who accepted responsibility for its companion
amendment. Scope, selected/current/operation identities, create-only Save new,
No Audio refusal, retained warnings and original-Up semantics agree. A12 owns
the independent browser freeze; no browser file was edited by A11.

Clarified separate RegistrationLibrary storage/scopes, LibraryModel catalog and
receipt authority, RegistrationBrowser presentation, and main-thread orchestration.
The browser owns no second mutable catalog. Gesture closure keeps held pointer
notes/capture, and a closed parameter drag remains suppressed until real Up.

The accepted whole Registration excludes only expression; Performance includes
all current controls. No new parameter, Session variant, state version, envelope,
DSP owner, Engine route, overwrite/delete feature or background worker is added.
Legacy saved baseline, 47 identities, state4/readers1–3, original input ownership,
free-running sources and transient musical histories remain intact requirements.

## Executed checks, source identities and next evidence

Executed source/document reads, targeted `rg`, SHA-256 inspection and a focused
document integrity check. These are static review checks. No configure/build,
runtime test, native capture, benchmark, Git operation, shared-navigation edit,
publication or child dispatch occurred. Initial combined read output was
truncated; affected required documents were reread with bounded output.

| Source reviewed | SHA-256 |
| --- | --- |
| `apps/standalone/StateFiles.cpp` | `6cd0d2f26bb2f938781561d278f15f9230e5d84b6052e8554761dc8e96dfd3b6` |
| `apps/standalone/Session.h` | `dc729465578ed02a8cb0640d07de679be33d731cdece947a09bce736bc84c929` |
| `apps/standalone/Session.cpp` | `256c0ef82e5a6639b3437d01754a0b27673a9d4096fe099a8b66351818ef2ae3` |
| `apps/standalone/UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `apps/standalone/UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |

Next: root admits the contract and assigns native storage/scopes, model/receipt,
browser and app integration by their separate paths. Independent implementation
checks must retain all section-9 cases, especially same-target concurrent create,
symlink/FIFO races, absent protected aliases, true acknowledgement basis,
staging-time cancellation, committed-warning truth and held-input SDL journeys.
Scoped contract acceptance closes no whole-interface 1:1, real-device,
accessibility, callback-deadline or physical-fidelity gate.

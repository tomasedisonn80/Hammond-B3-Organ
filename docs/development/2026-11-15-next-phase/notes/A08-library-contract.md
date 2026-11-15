# A08 — native named registration library contract

Assignment `/root/w02_a08`, Wave 2, 15 November 2026. Owned files are
`docs/REGISTRATION_LIBRARY_CONTRACT.md` and this note. Repository:
`/workspace/scratch/116ca0948095/Hammond-B3-Organ`. Assigned session baseline is
`138fca9af7feca46d10b0e2b65d891f4751a3904`; no independent Git observation is
claimed. The root integrator owns shared navigation, build and publication.

## Source assessment and decisions

Read the complete AGENTS.md and M0–M9 PLAN, active session entry/checkpoint and
assignment ledger, current shared recovery headings, A05/A06 atlas notes, current
ControlSnapshot/state-format definitions, StateFiles, UiModel and relevant main
Session submission/observation/save/load/modal logic. The atlas basis here is
the A05/A06 retained reading, especially pp. 409/416/418; this assignment does not
claim another complete PDF reading or new original-PDF capture.

The contract chooses a full Registration snapshot excluding expression at recall;
Performance/current controls restores all present fields. This resolves A05's
full-registration proposal versus A06's narrower inactive-bank alternative
explicitly. Root accepted that direction. Existing generic controls, parameter
identities, readers, musical transient ownership and legacy `--state` behavior
remain separate authorities.

The compact persistence decision is one unchanged control document per file.
`.b3registration` or `.b3performance` records scope; a portable literal filename
stem records name. No envelope, sidecar, index, new state version or duplicated DSP
owner is needed. New saves are create-only, with POSIX atomic link/Windows
no-replace move requirements, exact resource bounds, protected output/input path
collision checks and failure/cleanup evidence. Named Recall with No Audio is
unavailable and never silently staged; old Load staging remains intact.

Three inspected source hazards drive explicit semantic additions:

- `UiModel::load_controls` changes `saved_controls_`; library recall needs a
  separate operation preserving the legacy clean-file reference.
- `main.cpp::open_overlay` invokes `lose_input`, releasing UI owners. Browser
  opening needs gesture-only closure and retention of held note owners/capture.
- `UiModel::key` handles Escape before its text-entry gate. Browser Escape Down
  must be consumed without release while every actual Up still follows its
  original owner identity and suppressed-key bookkeeping remains correct.

The contract therefore separates selected preview, current-entry provenance,
legacy dirty state and operation receipt. Sequence resolution alone cannot
prove application; exact controls, desired revision and recovery/rejection/discard
counters are required. Timeout is Unconfirmed rather than invented rejection,
and a newer control intent supersedes the old receipt without a false rollback.

## A09 coordination and review status

Coordinated the copied model and semantic API requirements directly with
`/root/w02_a09`, owner of the browser UI contract. Agreed: filename-derived scope,
no import/delete/replace UI, explicit Recall and Save new, Registration default
save scope, bounded literal text entry, independent selected/current entry, one
pending operation, No Audio behavior, full preview and original-Up continuity.
The contract supplies 48-byte names, 128 rows, 512-item scan bound and the
16 KiB existing parser limit for A09's layout and editor specification.

Independent review is pending at this initial handoff. The contract is proposed
implementation input, not an executed product gate. Root will assign implementation
after its review; this assignment does not own native code or shared navigation.

## Executed checks and limitations

Executed read-only source/contract recovery, document line-count/SHA-256
inspection and authoring of these two assigned documents. One attempted read of
`include/hammond/Session.h` failed
because Session belongs to `apps/standalone/`; the actual header and relevant
implementation were subsequently read. This is a source-location correction,
not a build failure. No builds, runtime tests, Git operations, native captures,
publication, other checkout edits or child-agent dispatch occurred.

| Inspected source | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| `apps/standalone/UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `apps/standalone/UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| `apps/standalone/StateFiles.cpp` | `6cd0d2f26bb2f938781561d278f15f9230e5d84b6052e8554761dc8e96dfd3b6` |
| `apps/standalone/Session.h` | `dc729465578ed02a8cb0640d07de679be33d731cdece947a09bce736bc84c929` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `include/hammond/ControlStateIO.h` | `7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081` |

Required next evidence is the contract's acceptance table: independent scope and
legacy baseline fixtures; bounded filesystem/admission and concurrent atomic
creation failures; receipt recovery/timeout truth; SDL held-owner continuity;
main-thread I/O audit and actual changed browser captures. Numerical/physical
model gates and other sessions' ownership remain unchanged.

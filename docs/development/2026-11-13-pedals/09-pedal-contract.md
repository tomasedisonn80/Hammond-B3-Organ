# Assignment 09: pedal runtime and integration contracts

Owner: /root/w02_a09_pedal_contract

Wave: 02. Scope: define and review the current kernel contract and the next
nominal playable-pedal contract. This is one new assignment in this session.

## Owned changes

Added [PEDAL_RUNTIME_CONTRACT.md](../../PEDAL_RUNTIME_CONTRACT.md) and
[PEDAL_INTEGRATION_CONTRACT.md](../../PEDAL_INTEGRATION_CONTRACT.md), plus this
note. No shared status/ledger, code, test, profile, historical record or source
PDF was edited. Root owns integration, completed-assignment accounting and
publication. No commit or push was performed by this worker.

Read `AGENTS.md`, the current plan/status/next-step/handoff context, existing
control-state and parameter contracts, `M3_NEXT_GATE.md`, and all six new
wave-1 atlas review notes. This worker did not claim another independent
500-page PDF reading. The compatibility baseline is `b4fc61c`; agents 07/08
were concurrently implementing their separately owned kernel/compiler files.

## Decisions and API review

Coordinated directly with agents 07 and 08, then inspected the actual new
`PedalRouting.h`, `PedalRouting.cpp` and compiler implementation. The runtime
document matches their frozen types, metadata fields, compiler invocation and
error precedence. No actionable mismatch was found in the reviewed structural
preparation, bounded contact preflight, all-91-source validation or scalar
branch summation.

The contract deliberately distinguishes **generic structural kernel admission**
from the compiler's **exact factory-map admission**. Preparing any valid
200-position table is not a factory attestation. All 200 weights, including null
branches, and all 91 source samples, including unused samples, must be checked.
Disconnected contacts remain diagnostic state; repeated sources remain branches.

Root explicitly approved the following integration decisions during this
assignment:

- `nominal-static-pedal-mixture-v1` uses rows `[1/2,1/4,1/8,1/8]` and
  `[1/8,1/2,1/4,1/8]` over Brown/Red/Orange/Yellow, with all unit branch weights.
- `linear-pedal-position-v1` uses integer positions 0-8 and gain `p/8`;
  both controls default muted. Labels are Pedal Mixture 1/2, without a calibrated
  footage claim.
- Append pedal event values 10-13, keeping Manual values 0/1. New pedal events
  require the canonical Lower field but carry separate pedal IDs, not manual
  MIDI notes. All eight ideal contact states remain observable.
- Preserve the old no-pedal summation order and manual-only `active_key_count`.
  Pedal diagnostics/counts remain separate. Lower Cancel, manual panic and
  upper percussion state cannot silently control pedals.
- Any last-rendered pedal diagnostic retains its actual absolute frame and
  rate, separate from current controls. Zero-frame edits and rate changes cannot
  masquerade as a new sample; fresh successful preparation invalidates the record.
- `B3CONTROLS3` adds `pedal drawbars <p0> <p1>` after percussion; v1/v2 migration
  explicitly mutes pedals and preserves the old controls. Ordinary snapshots
  still exclude held/contact/source/readiness/clock history.
- Registry schema 3, model `exclusive-ab-percussion-pedal-console-v3`, appends
  `0x4000`/`0x4001` and paths `pedal.drawbar.mixture1`/`.mixture2`, preserving all
  43 earlier records and exact normalized laws.

Agent 08 identified an output-contract qualification: stdout reporting can fail
after the generated header has been published. The runtime document therefore
limits preservation guarantees to input/admission and publication failures; it
does not assert that every nonzero CLI result preserves destination bytes.

## Actual checks and remaining gates

A Python consistency check observed all of the following:

- The adopted complete version-3 grammar has **73 tokens**.
- Both rational mixture rows sum exactly to one.
- All **81** admitted position pairs satisfy the declared combined bound of
  100 for bus inputs bounded by 50.
- The inspected registry has 43 records and neither new ID is occupied.
- All **18** local links in the two contracts resolve.

Read-only command families were `cat`, bounded `sed`, `git status/rev-parse`,
Python JSON/regex/Fraction checks, and a focused diff check. A direct file-content
check additionally verifies UTF-8/LF, no trailing whitespace, final newline and
the required note owner because newly added untracked files are not covered by
ordinary `git diff --check` until staged.

No native DSP suite, physical capture, host/device test or full repository
qualification was run by this documentation worker. Agents 07/08 own their
focused implementation results; independent CSV/native, allocation, source
history and later integrated audio gates remain separate assignments. The
contracts require those results and preserve all physical-model and product
limitations rather than treating the specifications as completed behavior.

# Fixed-registration persistence integration review

Reviewer: **A20**, `/root/w04_a20_persistence_acceptance`, 2026-11-14 UTC.
The [worker record](../development/2026-11-14-preset-continuation/20-persistence-acceptance.md)
retains the actual source identities, build commands, output and platform limits.

## Finding

The inspected shared reader/writer and standalone file adapter satisfy the frozen
[state contract](../PRESET_STATE_PARAMETER_CONTRACT.md) in the exercised paths.
The two focused integration targets passed from one copied source tree. No
production IO change was needed. This qualifies Linux file transactions and
live Engine restore behavior; it does not qualify a native window, a VST3 host,
Windows replacement, or every persistence failure the operating system can emit.

Two stale test assumptions needed repair:

1. `test_standalone_state_files.cpp` expected every new save and old-file upgrade
   to write version 3. It now compares real saved files to independently written
   canonical version-4 literals, including the exact catalog identity and raw
   fixed modes. The former default version-3 literal and former varied version-3
   constructor remain intact as legacy inputs.
2. `test_pedal_integration.cpp::old_control_text` constructed old formats by
   removing records from the current serializer output and asserted a current
   version-3 header. Its replacement constructs versions 1, 2 and 3 from explicit
   legacy grammar literals. A separate complete state4 literal qualifies the new
   writer, and fixed/cancelled controls are restored during the existing live
   contact, phase, pedal and percussion-history scenario.

These were identified in source before the edits. A20 did not run an unchanged
stale-test baseline and does not report those old assertions as an executed
runtime failure. All executed strict builds and targeted runtime runs passed.
Final review retained the original upper-B re-enable continuation separately
from the new fixed-state continuation, then reran the affected pedal target.

## Independent source audit

| Boundary | Inspected behavior and consequence |
| --- | --- |
| Version admission | `parse_text` admits exactly versions 1 through 4. Only version 4 reads catalog/fixed fields; it does not attempt a legacy fallback after a failed new record. |
| Catalog binding | Version 4 checks the exact ID, `sha256` token and frozen digest before parsing controls. The check does not depend on either retained mode or either route bit. |
| Raw selection memory | The writer emits each remembered bank, raw fixed mode and route bit separately. A cancelled C# does not become a saved `none`, and fixed A does not become adjustable bank A. |
| Complete validation | The serializer validates the snapshot before indexing label arrays. Parsing builds a fresh candidate, validates the complete document and snapshot, then performs its single destination assignment. Invalid hidden modes cannot bypass validation through Cancel. |
| Legacy defaults | The fresh candidate gives all old readers fixed modes `None`; version 1 also defaults percussion, and versions 1/2 default pedals. The explicit pedal condition admits both versions 3 and 4. |
| Decimal and stream policy | The existing classic locale, nearest-rounding guard, signed-zero path, 16 KiB bound, complete-stream checks and final assignment remain in place. The file adapter delegates parsing to this same implementation. |
| Load boundary | `load_control_file` admits an existing regular file through `symlink_status`, opens in binary mode, and delegates directly to the transactional parser. It contains no format-specific migration or write-back. |
| Save boundary | `save_control_file` serializes before filesystem mutation, checks the destination and existing parent, creates a bounded-attempt sibling temporary directory, writes/flushes/closes the complete temporary file, then replaces the destination. Its RAII object removes pending temporary entries on the tested failures. |

The audited `ControlStateIO.cpp` and its header have the same byte identities as
the accepted [A15 implementation](../development/2026-11-14-preset-continuation/15-state-migration.md).
This review adds integration evidence without rerunning A15's exhaustive mode,
grammar, rounding, stream-fault and invalid-enum enumeration simply to repeat
its counts. The [core contract](../PRESET_CORE_API.md) and
[adapter audit](../PRESET_ADAPTER_AUDIT.md) determine the separate retained/effective
selection meanings used here.

## Actual file transactions

`test_standalone_state_files` calls the production `save_control_file` and
`load_control_file` functions against a private filesystem tree. Expected bytes
come from literals, never from the production serializer or catalog-label API.

- A native Unicode path receives four distinct remembered drawbar banks, upper
  remembered bank A with cancelled C#, lower remembered bank B with active fixed
  A, nondefault percussion and nonzero pedals. Load must recover every field.
- A second overwrite cancels both retained fixed rows and stores expression
  negative zero. Both exact `expression -0` bytes and the loaded sign bit are
  checked. A final overwrite writes the full default state4 literal with two
  `none` modes.
- Literal versions 1, 2 and 3 load into a destination already containing different
  nonzero fixed modes, banks, routes, pedals and negative zero. Every supplied
  old field and each version's migration defaults are checked. Load must leave
  the old file bytes unchanged; explicit Save then upgrades it to independent
  state4 bytes. The complete previous default version-3 literal is also retained
  and upgraded separately.
- Malformed documents preserve the entire destination and original file bytes.
  Focused additions include an unknown catalog, a valid-length different
  lowercase hexadecimal digest, a short digest and a missing catalog **with both
  fixed modes `none`**. A case-invalid fixed token, missing state4 fields, a
  genuinely unsupported version 5, truncation, trailing data and existing
  malformed-bank cases also reject.
- The exact 16,384-byte file loads; a 16,385-byte file rejects without publication.
  Invalid upper and lower retained enum values reject while their affected routes
  are cancelled, preserving arbitrary existing target bytes and not creating
  an absent target.
- Existing missing-parent, directory, parent-is-file, empty-name, regular-symlink
  and dangling-symlink policies remain tested. The Linux run could create the
  symlinks and exercised both load and save rejection.
- The existing `RLIMIT_FSIZE` protocol forces temporary-write failure after
  temporary creation. The existing target remains unchanged, an absent target
  remains absent, and no `.b3-save-` entry survives either complete API call.
  A subsequent normal save succeeds after restoring the process limit.

The three independent complete state4 literals used by the two targets were
also checked as 81-token, 12-line documents ending in `end\n`. The original
version-1/2 literal components, varied version-3 constructor and complete default
version-3 literal were compared byte-for-byte with the pre-edit source.

## Live musical-history integration

`test_pedal_integration` keeps the original independent pedal CSV/source oracle,
all three supported sample rates, rate-change preservation, disconnected-output
partition comparisons, manual/pedal routing checks and rejected-batch future
audio comparisons.

During its live migration scenario, a pedal remains held, manual contacts are
moving and percussion readiness has already decayed. State4 retains cancelled
upper C# with remembered A and active lower G# with remembered B. Each independent
legacy reader must instead recover the original B/B route controls, clear fixed
memory, and apply its own percussion/pedal defaults. For every successful parse
and restore, the test compares clock, all 91 source-phase bit patterns, all manual
contact snapshots and held flags, pedal contacts and held flags, readiness bits,
active counts and the historical last-pedal frame. Effective selection queries
also distinguish the cancelled/fixed state from the migrated bank routes.

The original version-1 to upper-B percussion re-enable restore remains tested,
including immediate eligibility and a zero-frame/future-audio comparison.
Restoring the fixed state again checks ineligibility without changing histories;
its empty zero-frame call and subsequent audio also match a copied continuation
bit-for-bit. The test does not serialize or restore those histories as ordinary
controls.

The final run retained 2,203 independent oracle frames, 32,600 contact checks,
200,837 bitwise phase checks, 17,676 bitwise partition samples and ten late-invalid
transactions. These are the existing test's reported musical checks, not new
counts invented for the persistence change.

## Remaining qualification

The Windows sharing-lock replacement branch is preserved but was not run here.
The Linux test explicitly reports that failed POSIX replacement **after a complete
temporary write** lacks a deterministic non-racing fixture. A20 qualified the
existing bounded write-failure protocol rather than adding sleeps, races or
production fault-injection hooks. The macOS branch was not executed.

These results concern API completion and observed file contents; they do not
establish crash/power-loss durability or behavior under adversarial concurrent
filesystem mutation. There was no sanitizer, allocation, host, device, native
Save/Load UI, Session queue/publication, or full-suite run by this worker. Those
separate owners must consume the same fixed-state and legacy semantics at their
boundaries. No physical latching, measured loading/gain, calibration or fidelity
claim follows from this persistence review.

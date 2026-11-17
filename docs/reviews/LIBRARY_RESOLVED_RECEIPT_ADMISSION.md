# Resolved control receipt interpretation

Root review with independent A19 Session-source review, 16 November 2026.

The first independent model test build succeeded. Its first run reported 32
groups, 3,225 assertions and one failed group: the test expected Awaiting after a
new coherent publication had resolved the original control sequence without
applying it. The [original failure](../development/2026-11-16-console-completion/reports/library-model-first-test-receipt.json)
and original test identity remain retained. No production code changed for this finding.

`SessionSnapshot::resolved_sequence` denotes consumed commands, including rejected
and discarded commands; `last_applied_sequence` denotes the latest actually applied
command. The [Session implementation](../../apps/standalone/Session.cpp) advances
resolved when consuming a command and advances applied only on successful application.
Rejected application and recovery also publish the corresponding rejection, recovery
and discard counters coherently. Once the original sequence has been resolved
without application, it cannot later be applied. A subsequent larger applied
sequence cannot certify that original command. A19 independently confirmed this
from the real Session source while authoring its independent boundary tests.

Root admitted a correction to the test oracle after A16 released ownership:

- A newer publication with neither sequence covering the queued control remains
  Awaiting; a later publication covering both establishes Applied.
- A newer publication resolving the original control without applying it becomes
  terminal Unconfirmed, clears optimistic Pending and establishes no reference.
  A later larger applied sequence with equal control values cannot revive it.

This preserves the frozen design's original receipt guard, its rule that invalid
bases cannot be revived by unrelated sequences, and the existing implementation.
It adds the missing adverse outcome instead of relaxing acknowledgment requirements.
The synthetic isolated pair intentionally omits real Session failure counters to
exercise the independent resolved/applied guard; real Session tests separately
exercise genuine rejection/discard/recovery publications. Root owns the amended
test and coordinated execution. A16's original note and source identity continue
to describe its original delivered version, not this later amendment.

The [original A16 source contents](../development/2026-11-16-console-completion/reports/source-history/test_standalone_library_model-A16.cpp.txt)
were subsequently reconstructed by reversing only the known amendment and
verified against the SHA-256 recorded before that amendment. The
[restoration receipt](../development/2026-11-16-console-completion/reports/source-history/A16-source-restoration.json)
and exact diff distinguish that verified content restoration from an untouched
original file. The corrected run passes all 32 groups and 3,250 assertions; see
the [source-specific result](../development/2026-11-16-console-completion/reports/library-model-resolution-result.json).

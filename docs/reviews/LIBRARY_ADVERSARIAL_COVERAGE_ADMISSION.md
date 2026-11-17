# Library adversarial coverage admission

**A41, 17 November 2026: ADMIT the reviewed copied-state and named-recall
foundation coverage. No new blocking source defect was found.** Root retains
acceptance and publication; native browser/main integration remains unfinished.
This review does not transfer any other owner's scope.
The verdict is pinned before remote reconciliation; it does not qualify later
combined main/H1/CI changes.

## Evidence and boundaries

I read the full AGENTS/M0–M9 plan, current session records, frozen API/design and
prior admissions, all 1,060 implementation lines, the new helper and all five
test sources. The [coverage report][report] records nine adversarial areas,
source-only cases, hashes and remaining gates. All thirteen implementation/test
identities match both the integrated receipt and A32's retained headless inputs.
LibraryModel remains `ae5348c731b0559a6816b75cc190622918ca89d1fe938dd56445d51591904b98`;
UiModel header/source remain `34337e5d…` / `b4889e0b…`. Working-tree hashes,
not base HEAD alone, identify these additions.

I executed no build, product test, native process or storage experiment. Root/A32
performed the [five-suite executions][five]; I inspected their sources, complete
detail log, hashes and retained JUnit results independently.

| Suite | Observed result | Actual boundary |
| --- | --- | --- |
| Model | 32 groups / 3,250 assertions | Copied catalogs and synthetic observations/results |
| Session | 12 groups / 42,634 assertions | Real Session reads, posts and manual renders; fixture catalogs |
| Storage | 9 groups / 1,115 checks | Real create-only files; synthetic control publications |
| Recall helper | 9 groups / 743,728 assertions | Real UiModel; synthetic events, observations and post results |
| Roundtrip | 4 groups / 1,489 checks | Real UiModel/Session/storage; 24 posts, seven storage calls |

The [first full run][full] is **246/247**, including all five library passes.
Its sole A33 report-link failure remains retained; the report now exists, and
root owns the affected integrity rerun. The [distinct SDK-free run][headless]
passes 12/12, including these same five suites. Neither result is a device run.

## Adversarial findings

- **Intent and receipt identity:** equal-value Recall still emits one complete
  command with a new revision/sequence. A newer equal intent supersedes the old
  receipt, including an issued Save; even real subsequent proof cannot revive it.
  Selection, form edits and current reference cannot retarget an operation.
- **Application truth:** a newer unresolved publication remains Awaiting;
  resolved-but-unapplied becomes terminal Unconfirmed. Real rejection/discard,
  256-slot overflow and synchronous tokenless failure prevent larger unrelated
  sequences from supplying proof. Failed/stale/malformed copies and eighteen
  conflicting same-publication variants cannot certify success. The original
  failed A16 oracle and [independently reviewed correction][resolution] remain
  separate; implementation bytes did not change.
- **Time, lifecycle and limits:** 1999/2000-ms ordering, failed-read expiry,
  deadline overflow, rapid Stop/Start and Prepare invalidation are exercised.
  All four issuance counters test zero, last usable token and attempted
  exhaustion; catalog tests additionally reserve the final Save-refresh generation.
  Small injected limits exercise issuance branches; literal `UINT64_MAX`
  issuance is a source-arithmetic argument. A28 proves that a pre-Start restore
  can really apply while remaining ineligible for Save until a new post-Start
  intention is proved.
- **Catalog and disk authority:** malformed bounds/order/counts fail admission;
  leaf revalidation cannot clear directory ambiguity. Newer explicit refresh wins
  over a generation-zero compound scan, and precommit scans cannot falsely mark
  the new reference Missing. Actual storage checks preserve late exact-path
  winners, refuse five final-authorization changes and retain a genuinely
  committed capacity-warning file. Foreign/duplicate results and synthetic
  inconsistent metadata cannot invent a current reference or automatic retry.
- **Musical ownership:** named and legacy clean references remain independent;
  Registration preserves explicit desired expression and Performance restores
  saved expression. Real overlapping owners retain their original releases.
  A19's paired audio/phase/percussion checks are bounded software evidence;
  phase inspection is on its oracle Engine, not hidden Session internals.

Additional **source-only** review covers stale successful tokens preserving newer
pending intent, decreasing counter/fault rejection, bit-distinct same-publication
zero and authorized completion surviving later exhaustion. Forged metadata and
reported syscall failures are synthetic; deterministic collision seams are not
concurrent-device or platform qualification. No redundant tests are proposed.

## Remaining concrete gates

Follow the [native integration plan][next]. Admit model-owned Save availability:
`controls_pending == false` cannot identify a proved basis. Wire real lifecycle,
startup and every ordinary/direct-MIDI/recovery/disabled post exactly once, using
fresh reads and one synchronous final authorization. Current `open_audio` queues
restore before Start; the tested post-Start rule still needs actual app routing.

Dedicated browser entry must preserve original keyboard/Space/pointer/MIDI Ups,
close only parameter gestures and suppress modal Downs. Existing `open_overlay`
releases input, so reusing it would violate that contract. Actual native routing,
storage delay/queued releases, display/DPI/devices, source-specific platform and
sanitizer qualification, native accessibility, callback deadlines/retirement,
physical fidelity, publication/release and literal whole-interface 1:1 remain
separate gates.

[report]: ../development/2026-11-16-console-completion/reports/A41-coverage.json
[five]: ../development/2026-11-16-console-completion/reports/library-integrated-result.json
[full]: ../development/2026-11-16-console-completion/reports/integrated-first-ctest-result.json
[headless]: ../development/2026-11-16-console-completion/reports/A32-headless/qualification.json
[resolution]: LIBRARY_RESOLVED_RECEIPT_ADMISSION.md
[next]: ../design/LIBRARY_NATIVE_INTEGRATION_NEXT.md

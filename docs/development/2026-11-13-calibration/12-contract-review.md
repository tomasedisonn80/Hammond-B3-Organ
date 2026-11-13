# Assignment 12: independent contract integration review

## Identity, ownership and conclusion

- Canonical assignment: `/root/cal_w2_a12`; calibration wave 2, assignment 12.
- Date: 2026-11-13. Runtime for executed probes: Python 3.12.14.
- Owned paths: this note and [CALIBRATION_CONTRACT_REVIEW.md](../../CALIBRATION_CONTRACT_REVIEW.md).
- Initial checkout and local `origin/main`: `08fa8de8f718584c4ee4ab3b392c779f3290289c`;
  tree `f5cff4b89d19f36a73f9d2a8ddb966db487f832c`.
- Outcome: no remaining implementation-blocking inconsistency found after two
  root-authored clarifications. Audio/corpus/comparison producers may proceed.
- No production, test-suite, shared-status, manifest, git-history or publication
  edit was made by this assignment. Other workers' uncommitted files were preserved.

## Sources and review method

Read `AGENTS.md`, the active calibration/rotary/standalone scopes, current README,
status/next steps, scanner handoff, plan, current calibration log entry and session
record. Reviewed the complete audio, corpus, comparison and common contracts,
capture metadata v1, the acquisition/split protocol, the consolidated calibration
atlas review and relevant current-session atlas notes, especially assignments 05
and 06. The review uses those retained source readings; it does not claim another
fresh full-PDF read, new original-page image inspection, or independent verification
of every external source.

The substantive review covered raw/derived declarations, exact byte and sample
hash scopes, format mapping, graph closure and false independence, final-role
mapping, metric units/phase masks, uncertainty decisions, hidden corrections,
serialization and output/resource bounds. It intentionally did not expand the
foundation into physical fitting, resampling, clock correction or a replay schema.

Read-only commands ran from
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`:

```sh
git status --short
git log -1 --format='%H %T %s'
git show-ref refs/remotes/origin/main
python3 --version
```

Bounded `cat`, `sed` and `rg` reads inspected the contracts and relevant context.
Some combined tool outputs truncated; the central contracts and decision-critical
sections were reread in smaller complete outputs before conclusions were recorded.
No fresh remote fetch was performed; the remote identity above means the locally
recorded reference observed by the command, not a new remote-server observation.

An in-memory `python3 - <<'PY'` probe independently assembled the canonical
preimage from literal samples, the 27-byte prefix, `struct.pack('<IIQ', ...)` and
`struct.pack('<d', ...)`. It hashed the literal WAV/raw byte vectors separately.
It checked seven printed hashes, three PCM-edge DC/RMS pairs, the sine/cosine
phase example and all four interval-decision examples. Expected values were not
obtained from a producer or digest helper. The main review records the actual
results and hash scope.

The same probe imported only `capture_common` for one concrete integration check:
`reference=math.nextafter(1e-12, math.inf)`, `candidate=1e6` gives a valid normalized
error of `9.999999999999999e17`. Its default generic JSON numeric guard rejected
the value; the explicit `max_number=2e18` guard admitted it. This is not a full
acceptance claim for the common module; its independent suite belongs to another
assignment.

## Findings sent to the integrator and final verification

1. `C12-01`: valid comparison ratios can exceed the common helper's `1e12`
   default. Requested the exact caller override `max_number=2e18`, preserving
   metadata and policy limits. Root added it to comparison section 7.
2. `C12-02`: requested an explicit table mapping corpus `final` to policy
   `final_test`, with the other three purposes unchanged. Root added matching
   wording to corpus section 2 and comparison section 10.

Reread both edited sections and recomputed complete-file SHA-256 values. Final
reviewed identities are:

| File | SHA-256 after the verified root edits |
| --- | --- |
| Audio contract | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| Corpus contract | `a524a38eedf8b18decd39845df844cc86ad98f8409216523e9917bb372bfb8b2` |
| Comparison contract | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |
| Common contract | `5ae7a7fffb05829c8758d82ac74460ca14834acbe1fa4f2b6e4b1648623bb805` |
| Common source used by the probe | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |

The main review preserves both original author hashes and the post-review hashes;
earlier authors' observations were not rewritten. Its file hashes identify the
reviewed working-file bytes, not a committed source tree or tested producer.

## Remaining evidence and next work

Assignments 13-15 can begin their bounded production work against these clarified
contracts. Independent implementation acceptance remains separate and must retain
actual runtime/source identities, rejection behavior and compatibility results.
No producer code, physical acquisition, corpus independence, calibration, listening
test, host/device qualification or fidelity gate passed in this assignment.

The two owned Markdown files passed the local-target check for all eight links,
contained no trailing whitespace, and ended with a newline. The four final
contract file hashes were rechecked against the table and remained unchanged.

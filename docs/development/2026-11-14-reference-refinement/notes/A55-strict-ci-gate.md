# A55 — Strict Linux CI completion gate

Actual assignment: `/root/w10_a55_strict_ci_gate`, wave 10. I own only the
additive change in `.github/workflows/ci.yml`, this note and the A55 reports.
Root retains the actual manifest, substantive acceptance, shared documentation,
Git operations and final publication. I read the standing instructions, complete
M0–M9 plan, current checkpoint and manifest, concurrent ownership records,
A39's checker note/source/tests and A53's completion-gate review. The observed
published source is `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`. Local HEAD and the local remote-tracking
reference identify that source; I did not perform a fresh remote query.

## Change and preserved requirements

The workflow adds one Linux-only Release step immediately after the preserved
historical interface-session checker and immediately before the existing
artifact upload. Its exact command is:

```sh
set -o pipefail
python tools/check_refinement_session.py --repo . --json | tee ci-logs/refinement-session-completion.json
```

This uses the checker's default strict completion mode. There is no progress
fallback, ignored failure or `continue-on-error` setting. Explicit `pipefail`
keeps a checker failure observable even when `tee` successfully writes its
stdout. The existing earlier step creates `ci-logs`, and the existing upload
already retains that entire directory for fourteen days under
`always() && !cancelled()`. A failed completion step therefore retains its JSON
through the unchanged failure-upload policy. The condition still excludes
cancelled runs. A previously failed prerequisite can skip the checker, and an
artifact's presence alone does not prove that this step executed successfully.

The six inserted lines are the entire workflow change. Removing those exact
bytes restores the published file byte for byte. Matrix entries, timeouts,
dependency action pins, budgets, Release commands and sanitizer policies retain
their prior values. The historical interface command and its records remain
unchanged. This work does not alter the existing core quarantine leak exception
or imply that all individual sanitizer gates are exception-free. Product,
checker and test source retain their published identities; the concurrent
waveform session continues to own R4.

## Executed focused verification

From `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`, I ran the retained
focused audit with Python 3.12.14, the installed PyYAML parser and Bash. The
[audit source](../reports/A55-verify-strict-ci-gate.py) and
[exact results](../reports/A55-strict-ci-gate.json) retain environment details,
file hashes, the complete small diff and every assertion. Its reproduction
command is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/development/2026-11-14-reference-refinement/reports/A55-verify-strict-ci-gate.py
```

The audit parsed both workflow versions, checked exact placement, Linux
selection, strict arguments, Bash availability, prior log-directory creation
and unchanged failure retention. It compared the complete parsed workflow with
the added step removed and separately compared original bytes. `bash -n`
accepted the extracted run block. Two disposable shell-transport probes then
replaced `python` with a local synthetic shell function and executed that exact
block: producer exits zero and thirty-one propagated unchanged, while `tee`
retained each exact synthetic JSON stdout and kept stderr separate. Neither
probe contained checker source or actual ledger data. The real checker was
never invoked. The workflow whitespace check passed, and checker/test plus
historical-checker/manifest bytes matched the named published source.

A53 found no blocking defect within the checker's record-consistency scope.
Its dated snapshot remains 54 recorded identities, 51 accepted notes and
completion false; that historical observation is not this session's final
state. A49 already executed all twenty synthetic checker methods in its full
157/157 run. I inspected the relevant source and review without repeating that
suite, running a product build, CTest or any native GUI action.

## Root's final sequence and limitations

This workflow edit remains unpublished until root has accepted all sixty actual
results and successfully checked the final stable records in strict mode.
After all notes and shared documentation are final, and after coordinating
ownership of `../build-native`, root's exact affected commands from the
repository root are:

```sh
set -o pipefail
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release \
  --output-on-failure --no-tests=error -R '^python_test_repository_integrity$' \
  2>&1 | tee docs/development/2026-11-14-reference-refinement/reports/root-final-repository-integrity.log
python3 tools/check_refinement_session.py --repo . --json \
  | tee docs/development/2026-11-14-reference-refinement/completion-check.json
```

Root must retain each real exit status, require strict completion with zero
errors and sixty accepted/verified identities in ten complete waves, and bind
the result to the final manifest and note bytes. Then inspect the accepted
diff, reconcile any remote advance, publish under the existing expected-head
workflow and observe the new step's actual hosted result and retained JSON at
that exact commit. These are future operations, not A55 execution evidence.
No actual strict or progress check, workflow dispatch, commit or publication
was performed here. Local structure and transport verification does not prove
hosted execution, dispatch authenticity, product readiness, physical fidelity
or literal one-to-one visual equality. The full plan's independent gates remain
governed by their own retained evidence.

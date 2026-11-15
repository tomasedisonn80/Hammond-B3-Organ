# A46 — Product-session record validator

## Basis and ownership

Read the full AGENTS and M0–M9 plan, current entry/checkpoint/assignments,
recovery handoff and relevant existing checker/CI/CMake source. Observed HEAD
and remote main were `d556da017ea0a5d4f2d231416782dbc5066e58c2`, tree
`a3150fd2489a50a430b02c01eadd5e0c180bc7f9`, with concurrent working changes.
This task owns the new checker, focused tests, the added CI record step and
A46 evidence only. No production, CMake, manifest, build or publication mutation
was performed. Python was 3.12.14.

## Delivered contract

Strict mode requires this exact v1 session and requested counts, A01–A60,
distinct canonical agent paths, ten correctly mapped six-worker waves, accepted
states, task/acceptance text, usable ownership and SHA-256-matching notes.
Narrative checks require 100 words and 40 distinct words, excluding comments
and code; historical long notes retain their validity. The 128 KiB note bound
is not a retroactive 400-word limit.

Progress mode accepts actual running rows with unwritten notes and reviewed
candidates, but checks every declared hash and all accepted/reviewed evidence.
Normalized local references reject traversal, globs, symbolic links, Windows
reparse points and special files; bounded reads reject changed inputs.
Ownership handles existing parenthesized scope suffixes and directories.

The report explicitly cannot attest dispatch, substantive review, execution,
publication, product readiness or visual/physical fidelity. Its narrative floor
does not replace the integrator's acceptance.

## Observed verification

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_product_session.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_product_session.py --repo . --allow-incomplete --json
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_product_session.py --repo . --json
```

The 19 focused methods passed in 1.191 seconds, including synthetic complete
fixtures and negative identity/schema/hash/path/status/file cases. Actual progress
returned zero errors: 48 distinct records, 45 accepted and three running.
Strict mode correctly exited 1 with count/status/wave incompleteness; it did
not certify closure. Both retained JSON reports identify manifest
`f49886bc59295e091a413d3c847d12e874408b7cbc5a5a8bac45dbc7546057f7`.
The verification receipt preserves commands, outcomes and artifact hashes.

## Next gate

Root reviews these files and reruns progress after updating actual acceptance.
CMake already discovers `python_test_product_session`; no CMake edit is needed.
CI's sole added Linux Release step initially uses `--allow-incomplete` and
retains its JSON. After all sixty actual acceptances, root removes that flag,
runs and retains the strict result, then observes the hosted gate. No hosted
execution is claimed here.

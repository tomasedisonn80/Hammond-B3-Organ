# Rotary session accounting

The current rotary session has its own [manifest](development/2026-11-13-rotary/assignments.json)
and sixty ordered assignment slots in ten waves. Earlier sixty-assignment
histories remain separate. `tools/check_rotary_session.py` checks this session's
retained accounting without Git or network access:

```sh
python3 tools/check_rotary_session.py --repo . --json
```

The checker reports planned/running/complete counts, distinct recorded worker
identities and complete waves. It rejects duplicate identities/notes, invalid
ordering, missing completed files, absent substantive notes and inconsistent
ownership. Planned rows cannot claim a dispatched identity. A completed note
must identify its actual worker. Paths stay inside the repository and inputs
are bounded. These are consistency checks; the integrator still has to observe
dispatch, review the substantive result and execute the applicable acceptance.

Use an explicit expected count only for the actual accepted scope:

```sh
python3 tools/check_rotary_session.py --repo . --expected-complete 60 --json
```

That final command must fail while any of the sixty assignments is unfinished.
A manifest pass does not establish software correctness, physical fidelity,
host qualification or publication. At introduction the observed state was six
accepted readers, three running wave-2 assignments and 51 planned slots; the
six-complete check passed. Independent adversarial checker tests are a later
session gate, not claimed by that first consistency run.

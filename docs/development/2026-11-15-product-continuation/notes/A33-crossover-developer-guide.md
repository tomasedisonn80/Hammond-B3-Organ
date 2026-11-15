# A33 — independent crossover developer workflow

Actual worker `/root/w06_a33_crossover_developer_guide`, wave 6. Recovered
AGENTS, full M0–M9 plan, active checkpoint/assignments, public header,
implementation, probe, reference, native/lifecycle/allocation/reference/acceptance
tests, registry contract, characterization and install guide. Base HEAD
`99b363438b3c4f217e0acb5361c0aea52ad7d0e3`, tree
`77c65ce06378a5a25a05591226d05b2445d91b1e`; concurrent root/worker changes preserved.

Owned only `docs/CROSSOVER_DEVELOPER_GUIDE.md` and this note. The guide supplies
normal clean-checkout target builds, precise CTest/direct-acceptance commands,
native/reference CLI bounds, SI state/ports, stopped lifecycle and transactional
processing, report/source identity and ordered M6 numerical/acquisition/model
gates. It links contract, characterization and CrossoverTools installation.
Documented the managed CMake/CTest fallback separately from user prerequisites.
No Engine route, physical/audible pass or parameter/state migration is introduced.

## Executed checks

From `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`, with Python 3.12.14 and
the integrator's existing GCC 14.2 Release probe:

```sh
/workspace/scratch/5b7d983ac078/build-native/hammond_crossover_probe --help
python3 -B tools/crossover_reference.py --help
/workspace/scratch/5b7d983ac078/build-native/hammond_crossover_probe --operation response --sample-rate 48000 --frequencies 0,800,20000
python3 -B tools/crossover_reference.py
```

All exited 0. Python captured reports in memory. Native response retained
default 16-ohm loads, three frequencies and exact DC gains 0/1 with 0.0625 A/V;
preparation residual `2.851688292336762e-17`. The analog report passed its
124-point comparison; maximum normalized error `3.4513332058942577e-16`.
All six retained acceptance source hashes matched the worktree. Existing probe
SHA-256 `da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac`
also matched that report; this is not a new source-to-binary attestation.

Checked 21 guide links including both heading anchors, parsed all four shell
blocks with `bash -n`, and verified the first CTest regex selects exactly the
three native crossover tests plus Python reference in the generated test list;
native acceptance is separately registered. Owned whitespace/UTF-8 checks pass.

No configure, build, install, full acceptance, shared CTest, platform/physical
test, commit or publication was run. Root owns coherent acceptance/publication
and shared navigation updates. Next model work freezes same-Hz electrical
criteria before a separately identified numerical candidate, physical acquisition
and coupled M6 qualification; warped agreement remains separate from audible
acceptance. All 47 sound identities and state4/readers 1–3 remain untouched.

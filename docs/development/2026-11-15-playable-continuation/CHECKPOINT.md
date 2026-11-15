# Current checkpoint

## Wave 1 accepted; Wave 2 contracts in progress

Start commit: `3767b645e010066d63ca0b7fc1af8310a6f7e5ad`.
All six actual Wave 1 readers accepted: every PDF page 1–500 has been read.
A07–A09 are drafting harmonic, offline-integration and reference-rack contracts;
A10–A12 will review them independently. No previous session is counted.
The selected scope is in [SCOPE.md](SCOPE.md).

Writable checkout: `/workspace/scratch/3d3981dcf371/Hammond-B3-Organ`.
Coordinated build: `/workspace/scratch/3d3981dcf371/build-native`.
Shared pinned tools and SDL under `/workspace/scratch/1bb6ee17ad7e/` are read-only.
Other source/checkouts/indexes/builds remain untouched.

Initial resource observation: 52 GiB available; clean source clone about 182 MiB.
Use one build, no duplicate dependency downloads, compact logs and selected PNGs.
Keep original PDF and existing evidence unchanged.

## Next operations

1. Accept the six complete range readings and select independent next phases.
2. Build current source coherently; retain original setup/test failures if any.
3. Freeze contracts, implement, independently verify and capture the actual UI.
4. Update README, plan/status/next steps and recovery with exact commands/results.
5. Complete all ten waves and publish verified chunks to main; verify remote.

The reference-match goal is not waived. Source art is not an application capture;
unchanged dry sound is not measured hardware fidelity.

## Observed baseline

Coherent GCC 14.2 Release build succeeded; native ON, MIDI OFF, VST3 OFF.
All **183/183 CTests passed in 179.06 s**. Original configure/build/test logs and
371-input source identities are in reports/. Current interface capture utility
passed eight actual native views under explicit dummy SDL. An initial invocation
of the older reference capture utility rejected diagnostics schema 3 after one
capture; original failure/log/output remain retained, and no pass is attributed
to that attempt. The correct interface utility then passed.
Build is approximately 96 MiB and available storage remains approximately 51 GiB.

# Capture and calibration-readiness scope

This independent M0/M8 engineering session starts from `38c1fac949368fa54bd86c6c00a5997a73480f5e`.
It implements the next evidence-tooling work identified in the existing capture
contract and atlas pp. 349-378, 449 and 481-486. The scanner, rotary and standalone
tracks retain their ownership. This session does not change the Engine, public
parameters, control-state formats, native plugin identities or their model inputs.

## Intended deliverable

Build a dependency-free, offline Python toolchain for actual audio-file inspection,
cross-capture corpus integrity and split auditing, declared comparison metrics,
frozen acceptance policies and reproducible evidence reports. Extend the existing
v1 capture contract through explicit companion contracts, preserving its meaning
and its planned/recorded and synthetic/hardware distinctions.

The toolchain must make a future physical dataset useful without silently filling
missing measurements. Recorded synthetic examples demonstrate software behavior.
They never establish a specimen, acquisition permission, calibrated measurement,
physical fit, listening result or instrument fidelity.

## Acceptance principles

- Inspect actual bytes and audio headers/content under explicit bounds; keep
  unsupported formats, malformed data, nonfinite samples and missing files visible.
- Preserve original files, precise paths/digests, raw/derived ancestry, channel
  identity, signal boundary, units and physical-clock uncertainty.
- Audit complete groups and related records across fit, validation and final-test
  roles. A duplicate byte stream, crop or declared common session cannot become
  independent evidence through a renamed path or manifest.
- Freeze analysis windows, feature definitions, nuisance transforms and tolerances
  before judging a candidate. Preserve failed and inconclusive results. Missing
  evidence cannot produce a passing physical verdict.
- Use independent mathematical examples and separately written acceptance tests.
  Check report replay, corruption, resource limits, failure preservation and clean
  setup. Do not use the producer's output as its only reference.
- Keep all processing offline. No new acquisition or remote upload occurs merely
  because a manifest declares a record. No new runtime or network dependency is
  needed for this scope.

## Ownership and continuation

New tools, companion schemas, tests and documentation use capture/corpus/calibration
names. The root integrator owns shared status, next steps, log, CMake integration
and publication. Each of the sixty newly dispatched workers has a distinct
assignment and substantive retained note in the session ledger. No earlier worker
is counted again. The whole unchanged PDF is freshly read in six disjoint ranges.

Future sessions inspect current status and source, continue dependency-ready work,
retain failed/unrun gates, verify a coherent source tree, update the handoff and
commit/push authorized changes to main without force. Acquisition and fitted model
qualification remain distinct later steps requiring actual reviewed observations.

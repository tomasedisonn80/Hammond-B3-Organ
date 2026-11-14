# A23 — Independent probe and smoke-evidence audit

Actual worker `/root/w04_a23_probe_audit`, wave 4, 14 November 2026.
Owned this note and `docs/reviews/WAVEFORM_PROBE_AUDIT.md`. No nested workers,
native/core/API/CMake edits, shared build, full native run, ledger changes,
commit or publication. Read repository instructions, current scope/checkpoint,
assignment records, complete project plan, atlas synthesis and frozen waveform
acceptance. Observed HEAD `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`; audited files are the current overlay.

## Audited identities

SHA-256 values were checked before and after the audit and remained unchanged.
The smoke artifact belongs to A19; A23 read it without modifying it.

| File | SHA-256 |
| --- | --- |
| `tests/probes/rotary_waveform_probe.cpp` | `922c92ab81d2fcc8a5a0948c7c85ee496cf6816bdc57b20dddba7474899ef577` |
| `tests/reference/rotary_waveform_reference.h` | `3c24792f80f86f903926622f4bf016984caf44d727ad3913e4570738ac9c8f21` |
| `tests/test_rotary_waveform_acceptance.py` | `8f04debc59982303b986c3200bc2b11df5070ce68f4989d8640b1514bb3516c2` |
| `docs/ROTARY_WAVEFORM_ACCEPTANCE.md` | `fa4288d586a2a40d803740408177f9c0a085bd4deb9ae0bdfc832e6d58b0c1aa` |
| `../a19-waveform-probe/smoke.json` | `0aed61e1c0044529a914d9abd61d89c04f0c6d649b2c37ec2db55be177dcdcf7` |
| `../a19-waveform-probe/check_smoke.py` | `39a10388093f7bd8294112fb2809d0c5b8629532fb600bd04bc0ea71a0081e4b` |
| `../a19-waveform-probe/smoke-check.json` | `2f28eecb57f3b0102395cf4d482434420bfd8324c89d79827bfe18a5e2c9a9f0` |

## Findings

No source-level blocker was found. Full mode really traverses every frame of
ten seconds at 44,100/48,000/96,000/192,000 Hz and all six partitions. The
one-frame canonical stream independently computes all 3,801,000 reference
frames; five replays compare 38,010,000 output scalar bit patterns directly.
The 22,806,000 native frames correspond to 91,224,000 native path solutions;
the native renderer's loop performs four path solves per accepted frame.
All 35 ordered commands per rate, including both final-boundary commands,
are supplied without moving timestamps, yielding 840 full-run consumptions.
These totals are source-derived expectations, not an A23 full-run result.

The reference imports no native code or calculated state. It has separate
analytical timelines, Cartesian geometry, bounded contraction/bisection and
product-form cubic support. Horn/Drum input sequences are distinct; negative
indices are zero. Both implementations use `n-2` observation, and selected
native diagnostics are captured at the actual canonical sample. The explicit
reference/native path permutation `[0,2,1,3]` matches both interfaces.
No gain/delay fitting or frequency remapping occurs.

Replay enumerates all 32 state and 46 persistent diagnostic fields, with
binary64 comparisons for floating values and exact commands/integers. It
avoids struct padding and call-local maxima. Budget and bit failures retain
every affected frame in bounded bitmaps; exceptions fail with stage/partial
counts. The largest canonical buffer is 30,720,000 bytes, one rate at a time;
reference output is streamed and the current four-span block is 131,072 bytes.
Reports retain compact metrics instead of successful per-frame JSON records.

The SHA-256 implementation correctly forms big-endian compression words and
length padding while explicitly hashing little-endian binary64 samples. Its
empty, `abc` and 56-byte vectors match Python `hashlib`. A19's checker genuinely
regenerates both inputs independently and compares all partition input hashes;
A23 separately recomputed all 32,776 smoke input scalars and obtained the same
24 matches. No native rendering was needed for this check.

## Actual checks and results

Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Source inspection used `sed`/`rg`, followed by `sha256sum` on the table above.
`python3 tests/test_rotary_waveform_acceptance.py --self-test` passed **9/9**
in 0.352 seconds. Imported-runner checks against the actual existing report
can be repeated without invoking native execution:

```python
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    "audit", "tests/test_rotary_waveform_acceptance.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
report = runner.parse_probe_json(Path("../a19-waveform-probe/smoke.json").read_bytes())
assert runner.validate_report(report, "smoke")["status"] == "pass"
assert runner.selected_decimal_checks(report)["status"] == "pass"
```

Actual smoke admission passed: 16,388 reference frames, 98,328 native frames,
24 partitions, 360 commands and 163,880 equal direct bit comparisons.
Maximum normalized error was `1.20659368074701270776e-9` against unchanged
`2e-5`. All 20 alternate final state/diagnostic comparisons passed. The
64 selected Decimal checks passed; maximum root difference was
`4.0290092979656412e-15 s`, maximum bisection residual
`9.854306506557944e-17 s`, and maximum bisection count 43.

## Limits and next action

This qualifies the audit and retained smoke only. Smoke's named 4,097-frame
shifted input does not cover the full impulse/silence schedule or complete
irregular cycle. Explicit zero-frame/cross-call boundary, symmetry, lifecycle,
transaction and allocation tests retain their separate evidence; the native
probe declares those groups unrun. A14 owns static-grid execution. Source and
binary hashes plus observed compile commands do not independently prove build
freshness; root owns coherent rebuilding. Next run the frozen full wrapper once,
retain all 24 partitions, 176 selected Decimal checks and 288 convergence
pairs, and inspect complete failures before any R4 closure. R5/R6 and physical
fidelity are not established by this audit.

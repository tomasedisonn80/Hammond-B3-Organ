# A21 — Native waveform runner and report admission

Actual assignment /root/w04_a21_waveform_runner, wave 4. Owned only
tests/test_rotary_waveform_acceptance.py and this note. A19 owns the native
probe; root owns CMake/CTest/CI and the eventual full run. No product/API,
shared build, manifest, status, commit or publication changes were made.

## Implemented contract

The standard-library runner accepts --mode smoke|full, --probe PATH,
--report-dir DIR and --timeout-seconds N. Ordinary invocation is the explicit
rotary-r4-shifted-input-smoke-v1 fixture: 4,097 frames at each rate, six
partitions, 16,388 reference and 98,328 native frames. Full is opt-in:
rotary-r4-full-stream-v1, exactly ten seconds at 44,100/48,000/96,000/192,000 Hz,
3,801,000 reference and 22,806,000 native frames. Defaults are the named
HAMMOND_ROTARY_WAVEFORM_PROBE_EXECUTABLE and HAMMOND_ROTARY_WAVEFORM_REPORT_DIR
environment variables, with 90/1,500-second native limits for smoke/full.
A missing executable fails.

Admission uses A19's actual schema-v1 serialization. It rejects missing,
repeated or altered rates/channels/partitions/frames, moved or reordered events,
lost final commands, incomplete direct bit comparisons, changed final physical
states or epoch diagnostics, inconsistent normalization/maxima, nonfinite or
overflow JSON values, duplicate JSON keys, weakened budgets, incomplete
selected/convergence coordinates, fast-math and false precision claims.
Counts are independent of caller-supplied totals. Nonzero native exit and
timeout remain failures even if other metadata looks successful.

Actual selected paths are cross-checked with the separately authored 80-digit
motion and 100-digit Cartesian routines. Motion uses the returned split
emission positions; independent Decimal bisection uses original n-2 observation
positions, target 1e-16 s and frozen 1e-14 s root-difference limit. Full requires
176 selected paths/288 native convergence pairs; smoke requires 64/96.
The A14 complete grid is admitted from its existing report/artifact: hashes,
all 33,280 coordinates, finite values, low-band budget and current tested native
source identities. Its native numerical workload is not rerun.

--self-test runs nine admission-test methods separately from native execution.
Its deliberately artificial schema fixtures are parser inputs only and never
qualify native audio. Root registers that switch as a separate CTest; ordinary
CTest invokes the smoke once.

## Evidence and source-binding limits

Every invocation creates a fresh mode/timestamp/random-suffix directory below
the chosen report parent. Existing runs, including failures, remain intact.
Only latest.json is replaced; it identifies the receipt, mode, status and
SHA-256. Native stdout/stderr are exact byte files with hashes, command,
working directory, exit and timing. Qualification Decimal values are exact
decimal strings; native.stdout.json retains original native numeric tokens.

Before/after inventories hash all src/, include/, CMake, probe/reference and
named contract/oracle/runner/static-gate inputs, including untracked overlays.
Git HEAD/tree, relevant porcelain status and tracked dirty-diff digest are
recorded. Relevant source/HEAD, executable or generated build-input drift
fails. Actual exported core/probe compile commands are retained; full requires
the probe and all five rotary core entries.

These observations bind source and executable bytes; they do not independently
prove an arbitrary old executable was freshly compiled from those bytes.
The build-before-run CMake target owns freshness. Smoke without generated
CMake metadata retains that limitation; full cannot pass without those
commands. The retained A14 native result keeps its own compiler/options and
source identity. Transaction/lifecycle, R5, device deadlines and physical
fidelity remain separate named gates.

Native streams are monitored at 24 MiB each, the owned run directory at 64 MiB,
and retained evidence at 32 MiB. A violation fails and retains available bytes;
no required evidence is silently truncated. These caps accommodate the probe's
complete inline failure bitmaps.

## Actual commands and results

Working directory: /workspace/scratch/e3cacb90cc81/Hammond-B3-Organ.
Scratch evidence: sibling ../a21-waveform-runner/.

    python3 tests/test_rotary_waveform_acceptance.py --self-test
    python3 tests/test_rotary_waveform_acceptance.py --mode smoke \
      --probe /workspace/scratch/e3cacb90cc81/build/hammond_rotary_waveform_probe \
      --report-dir /workspace/scratch/e3cacb90cc81/a21-waveform-runner/smoke \
      --timeout-seconds 90
    python3 tests/test_rotary_waveform_acceptance.py \
      --probe /workspace/scratch/e3cacb90cc81/a21-waveform-runner/does-not-exist \
      --report-dir /workspace/scratch/e3cacb90cc81/a21-waveform-runner/negative
    python3 tests/test_rotary_waveform_acceptance.py --mode smoke \
      --probe /workspace/scratch/e3cacb90cc81/build/hammond_rotary_waveform_probe \
      --report-dir /workspace/scratch/e3cacb90cc81/a21-waveform-runner/negative \
      --timeout-seconds 0.001

- Final self-test: **9/9 pass**, 0.319 s, including 35 report mutations plus
  malformed JSON, source drift, process-status and build-options checks.
  The first run exposed one omission: a syntactically finite Decimal exponent
  bomb was not rejected at JSON admission. Values outside the fixture's finite
  binary64 range are now rejected while long-double decimal digits remain
  preserved. That initial failure was a parser defect, not a native renderer
  failure.
- Actual CMake-built smoke: **pass**, runner 3.109353867 s, native 2.504095771 s;
  82 relevant source hashes stable. All 24 partitions completed, 163,880 direct
  scalar comparisons were bit-equal, 360 events consumed, 64 selected paths
  and 96 convergence pairs passed. Maximum normalized waveform error:
  1.20659368074701270776e-9.
- Selected Decimal maxima: angle 2.6850627461e-19 rad; speed
  4.8071332818e-19 rad/s; distance 1.2541307864e-19 m; ratio
  6.6371685936e-20; root difference 4.0290092980e-15 s. Maximum independent
  bisection residual 9.8543065066e-17 s, 43 steps.
- Missing executable: expected runner exit **1**, failed receipt retained.
  Forced 0.001-second native timeout: expected runner exit **1**, actual native
  exit **-9**, 0.001688716 s; empty stdout/incomplete result explicitly fails.
- Retained A14 admission: pass, all 33,280 rows and current tested native
  inputs match; compressed SHA-256
  03a56786a5d929d9a942048091b91fb5e791926019a0e0f3f0dc8aeceb0a2e77.

Successful receipt:
../a21-waveform-runner/smoke/smoke-20261114T223533.362072Z-b95e175b/qualification.json.
Receipt SHA-256:
820214e0435d68887ad3e897c8bde334868ce739aa65b4c10f9bc4888fcf702a.
It retains 224,712 stdout bytes and 2,320 stderr bytes; total run about 299 KiB.
Original negative runs remain under negative/smoke-20261114T223659.645534Z-e046d1c1/
and negative/smoke-20261114T223659.786616Z-65fd383d/.
runner-checks.json retains exact commands/exits/log paths; final self-test
stdout/stderr are beside it.

Observed HEAD: 26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8 plus recorded overlay.
Runner SHA-256 at smoke/freeze:
8f04debc59982303b986c3200bc2b11df5070ce68f4989d8640b1514bb3516c2.
Executable SHA-256:
3c057118d714f5131d1d8c01278d441830fc218acde3044c9a0e55f0cbe037a3.
Actual build: GCC 14.2.0/libstdc++ 20250315, C++20 Release -O3 -DNDEBUG,
all project warning-as-error flags; no explicit contraction option and no
fast-math option observed. Rounding was to nearest; double has 53 significant
bits/8 bytes, long double 64 bits/16 bytes. Twenty-five actual core/probe
compile command entries are retained.

## Next gate

Root may execute the frozen full target once. A28 independently reviews its
complete counts, metrics, source/binary identities and evidence; A21 did not
launch a duplicate full render. Full Linux runtime, full MSVC/AppleClang and the
combined R4 result are not claimed here. Any later runner/source/build-input
change requires a new qualification identity.

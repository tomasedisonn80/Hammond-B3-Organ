# Assignment 33 — percussion sample-rate lifecycle

Agent: `/root/w06_a33_percussion_rate_lifecycle`

Wave: 06, assignment 33 of this continuation's 60 new agents

Date: 2026-11-13 UTC

Qualified base revision: `093d985150a5d7e18b9c210126af0f08504024ce`.
The core and every tested consumer were rebuilt from one frozen archive of this
revision plus only the three owned source/test overlays listed below. Concurrent
source, contact and Engine lifecycle edits were excluded from this qualification.

## Implemented contract

Added `PercussionState::reconfigure_sample_rate(double) -> Status`. This stopped
or same-processing-thread lifecycle operation advances no time. It preserves the
one shared readiness value `q` exactly, the installed profile and every resulting
current gain. The existing diagnostic reports the newly installed sample rate.
No state fields or object layout changes were introduced.

Its validation and commit order is:

1. An unprepared state returns `NotPrepared`, even for a malformed rate.
2. Any rate other than exactly 44100, 48000 or 96000 samples per second returns
   `InvalidSpec`.
3. The currently installed rate returns `Ok` without writing state or evaluating
   coefficients.
4. A changed rate prepares a local candidate from the value-owned profile using
   the existing `prepare()` validation and coefficient calculation. Every
   fallible step completes before the live object is changed.
5. The candidate receives the original readiness value exactly and is installed
   as one value. Its temporary fresh-preparation `q = 1` is never installed.

The original preparation formulas remain unchanged:

```text
slow_factor   = exp(-1 / (sample_rate * slow_decay_seconds))
fast_factor   = exp(-1 / (sample_rate * fast_decay_seconds))
recovery_step = -expm1(-1 / (sample_rate * recovery_seconds))
```

Every coefficient must remain finite and strictly between zero and one. Existing
profile bounds still require finite time constants in `[0.0001, 60]` seconds,
normal/soft gains and the fast multiplier in `[0, 4]`, and the normal upper-sustain
factor in `[0, 1]`. A future coefficient-validation failure returns its preparation
status without changing the old profile, rate, readiness or subsequent behavior.

Ordinary `prepare()` retains its historical reset to `q = 1`. Rate migration
leaves zero unchanged and preserves a very small normal readiness value instead
of flushing it early. Only a later positive decay sample can invoke the existing
below-smallest-normal flush-to-zero policy. Disabled or disconnected routing
continues to recover on elapsed samples; migration itself supplies no elapsed
sample, detector change, musical control change, phase reset or new oscillator.

This method reuses preparation-time exponentials in a fixed-size local object.
The per-sample recurrence and all nominal factory parameters are unchanged. It
adds no allocation, I/O, logging, locks or publication mechanism. These are code
properties; this assignment did not instrument callback deadlines or allocations.

## Source basis and physical boundary

The supplied [research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
pp. 135 and 151, was read for this task. Page 135 requires finite continuous
envelope state through sample-rate changes and distinguishes nominal electrical
RC time constants from observed audible decay. Page 151 distinguishes portable
controls from evolving electrical/DSP histories and assigns state to its owning
module. The source PDF remains identified by SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

This is a lifecycle addition to the existing dimensionless `shared-readiness-v1`
surrogate described in [CONSOLE_DYNAMICS.md](../../CONSOLE_DYNAMICS.md). It does not
change `q` into capacitor voltage, identify a measured decay curve, validate AO-28
loading or establish B-3 switch-transient fidelity. Nominal gains, component
hypotheses and their replacement/acquisition gates retain their existing status.

## Independent tests and results

The new `test_percussion_rate` uses a continuous-time, whole-segment oracle:

```text
elapsed = frame_count / rate
decay:    q_end = q_start * exp(-elapsed / tau)
recovery: q_end = q_start + (1 - q_start) * -expm1(-elapsed / tau)
```

This oracle uses `long double` and does not copy the implementation's per-sample
coefficient or recurrence. Mixed-rate sequences propagate the theoretical state,
not the implementation's observed state. They explicitly apply the declared
subnormal-flush policy before the next segment when a decay tail reaches zero.
The longest such sequence spans 12,275 positive samples and twelve rate/control
segments. The absolute readiness allowance is `1e-11`: roughly four binary64
machine epsilons per sample across that bounded sequence, leaving room for
coefficient and recurrence rounding, including platforms where `long double`
has binary64 precision. This is an engineering tolerance, not a formal bound on
every platform's `libm` or a physical measurement tolerance.

Instantaneous readiness and gain preservation, same-rate behavior, and rejected
call futures require exact comparisons within the same build. These checks do
not demand bit-identical exponentials across independent numerical algorithms or
platforms. The normal-tail fixture separately predicts the first flush from
elapsed seconds and accepts at most one sample around its independently computed
threshold; all intervening states must be normal or zero.

| Check | Observed scope/result |
| --- | --- |
| Supported pairs | All nine old/new rate pairs under slow decay, fast decay, enabled recovery and disabled recovery |
| Profile coverage | Nominal and varied profiles, both time-constant endpoints, zero and maximum gains/multipliers, zero and unity sustain factors |
| Caller ownership | Overwriting the caller's profile after preparation does not change installed parameters during later migrations |
| Tracked migrations | 234 accepted boundaries, including same-rate entries in the pair matrix and zero-time sequence segments |
| Immediate gain preservation | 7,488 exact checks across all sixteen valid enabled/harmonic/volume/decay settings |
| Closed-form comparisons | 1,305; maximum absolute readiness error `6.3501070721172503e-14` |
| Rejections | 250, including 22 unprepared-precedence cases and 228 prepared invalid-rate cases |
| Invalid rate coverage | NaN, both infinities, both zero signs, negative, unsupported, subnormal and extreme values, immediate floating-point neighbors of all three supported rates, fractional input |
| Exact same-rate calls | 20,736 while alternating decay/recovery and routing policies |
| Exact future comparisons | 152,544 paired positive samples, starting at the currently installed rate before trying later changes |
| Tail behavior | Small normal values survive migration exactly; subsequent decay flushes at the expected time; zero survives migration and disabled recovery resumes from zero |
| Historical preparation | Re-preparation still resets readiness to one at the requested rate |

GNU C++ 14.2.0 Release compilation passed with the repository's strict warning
flags treated as errors. The new lifecycle suite and unchanged `test_percussion`,
`test_percussion_controls`, and `test_console_engine` passed **4/4 CTest suites in
0.29 seconds**, with no skipped tests. The standalone test invocation reported
the counts and maximum above. No build or test failures occurred in this scoped
qualification.

The public preparation API validates and owns the installed profile; supported
rates and accepted time constants produce valid coefficients. Thus the defensive
candidate `InvalidProfile` path cannot be induced through a valid public setup.
The tests do not corrupt private memory to manufacture that branch. They exercise
all public rate rejection paths and confirm subsequent behavior against untouched
copies, including fully ready, partially decayed, recovering and zero histories.

## Exact qualification procedure

The snapshot was created from the repository root with the following commands.
The observed `HEAD` was the full revision recorded above. The manifest retained
the archive hash and exact overlay hashes before compilation; live headers were
never substituted into an older compiled library.

```sh
python - <<'PY'
from pathlib import Path
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
repo = Path('/workspace/scratch/60e8291da354/Hammond-B3-Organ')
frozen = repo.parent / 'a33-frozen-src'
assert not frozen.exists(), frozen
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
archive = subprocess.check_output(['git', 'archive', '--format=tar', base], cwd=repo)
frozen.mkdir()
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as source:
    source.extractall(frozen, filter='data')
overlays = ('include/hammond/Percussion.h', 'src/Percussion.cpp', 'tests/test_percussion_rate.cpp')
manifest = {'base_commit': base, 'archive_sha256': hashlib.sha256(archive).hexdigest(), 'source': str(frozen), 'overlays': {}}
for relative in overlays:
    source = repo / relative
    target = frozen / relative
    shutil.copyfile(source, target)
    manifest['overlays'][relative] = hashlib.sha256(target.read_bytes()).hexdigest()
(repo.parent / 'a33-frozen-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
PY
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a33-frozen-src \
  -B /workspace/scratch/60e8291da354/a33-frozen-build -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a33-frozen-build --parallel 4 \
  --target test_percussion_rate test_percussion test_percussion_controls test_console_engine
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a33-frozen-build \
  --output-on-failure --no-tests=error \
  -R '^(test_percussion_rate|test_percussion|test_percussion_controls|test_console_engine)$'
/workspace/scratch/60e8291da354/a33-frozen-build/test_percussion_rate
git diff --check -- include/hammond/Percussion.h src/Percussion.cpp
```

Future runs should select a fresh snapshot/build directory, explicitly pin the
intended revision, and retain their own hashes and results. The repository tests
use CMake-provided paths and do not depend on this session's scratch directories.

| Qualified content | SHA-256 |
| --- | --- |
| Base git archive | `57c17a47ba9215ac4cfb3d143167f29661a53f8cfaf97de7cc6d725ea8a412d8` |
| `include/hammond/Percussion.h` | `5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722` |
| `src/Percussion.cpp` | `823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a` |
| `tests/test_percussion_rate.cpp` | `3af4ddd24445000f94baebbe942c4f91952c97553a374fe1283fe02a25b787dd` |

## Files and next integration gates

Changed only [Percussion.h](../../../include/hammond/Percussion.h),
[Percussion.cpp](../../../src/Percussion.cpp),
[test_percussion_rate.cpp](../../../tests/test_percussion_rate.cpp), and this note.
No Engine, ContactBank, TonewheelBank, CMake, shared handoff or existing test files
were edited. No staging, commit, push or subagent dispatch occurred in this
assignment. The integrating agent owns shared handoff updates and publication.

Assignment 34 should include the stable method in Engine's local candidate with
the source and contact rate candidates. The old Engine must remain unchanged if
any module rejects the requested rate. A successful Engine change must preserve
musical controls, render clock, all phases, contact trajectories and readiness at
the boundary, while later samples use the new duration. Test both a successful
whole-engine change and a source-profile rejection after other candidates could
have succeeded, then compare the full future against an unchanged copy.

The next acceptance gates are combined-source Engine lifecycle qualification,
independent integration review, the integrating agent's full publication suite,
and CI on its exact committed revision. Native host/device negotiation, timeline
ownership across host callbacks, concurrent calls, callback deadline guarantees,
cross-platform execution and measured physical fidelity remain separate gates.

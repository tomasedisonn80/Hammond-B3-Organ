# Nominal console acceptance

This matrix concerns the named software models `ideal-contacts-v1`,
`nominal-linear-travel-v1` and `shared-readiness-v1`. Their coefficients, units,
source-page basis and limitations are defined in
[CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md). They do not constitute a calibrated
B-3 contact mechanism or a complete AO-28 percussion circuit.

The source architecture is the preserved atlas, particularly pp. 127-128
(shared upper-B detector and physical ninth contact), pp. 134-135 (harmonic route,
coupled controls and isolated RC hypotheses), and p. 447 (M3 integration).
The evidence below tests this repository's declared nominal implementation,
not missing companion results or an acquired reference instrument.

## Acceptance layers

| Contract | Permanent evidence | Boundary of the result |
| --- | --- | --- |
| 1,098 independent contact identities; hysteresis, reversal, partial targets and invalid-profile atomicity | [Contact unit tests](../tests/test_contact_bank.cpp) | Proposed normalized positions and timing; no measured bounce or switching-bandwidth claim |
| One continuous readiness state; closed-form decay/recovery, supported bounds and settings changes | [Percussion unit tests](../tests/test_percussion.cpp) | Dimensionless readiness surrogate and proposed gain map; no capacitor-voltage or complete circuit claim |
| Shared source audio, upper-B eligibility, ninth-contact detector, one-foot masking, compensation and current-sample timing | [Console engine tests](../tests/test_console_engine.cpp) | Direct software audio/state oracles; physical routing transients still need captures |
| Retained settings and strict old-state migration without resetting dynamic histories | [Control I/O tests](../tests/test_control_io.cpp), [percussion control tests](../tests/test_percussion_controls.cpp) | Musical controls only; neither a DSP checkpoint nor a native host-state qualification |
| Original 39 identities retained exactly; four appended percussion IDs and normalization | [Parameter tests](../tests/test_parameters.py) | Proposed internal registry; actual native parameter exports require separate verification |
| Actual CLI model selection, ordered scores, source compatibility and bounded failure behavior | [Renderer tests](../tests/test_render.py) | Offline PCM software evidence; no audio-device deadline or plugin-host claim |
| Explicit schema-2 parameters, exact invocation, raw bytes/logs and failed-evidence retention | [Producer tests](../tests/test_render_fixture.py) | Reproducible evidence construction, not source/build authentication |
| Independent retained-bundle checking, historical schema 1 and strict schema 2 | [Verifier tests](../tests/test_verify_render.py) | Artifact/claim consistency; verifier never replays a recorded command |
| Actual render through producer and independent verifier, then a separate closed-form PCM oracle | [End-to-end console tests](../tests/test_console_evidence.py) | All three supported rates and both contact modes; exact bytes are required only within one build |

The matrix names test ownership. The current integrated commit's executed suite
and hosted matrix results belong in [STATUS.md](STATUS.md) and the
[continuation ledger](development/2026-11-13-continuation/README.md); the existence
of a test file is not itself a pass. Assignment 24's local run and exact tested
binary/profile hashes are retained in its
[evidence note](development/2026-11-13-continuation/24-console-evidence-acceptance.md).

## Independent PCM experiment

`tests/test_console_evidence.py` creates 18 real schema-2 bundles and submits every
one to `verify_bundle()`. It independently reads PCM through Python's `wave`
module, checks equal stereo channels, finite bounded nonzero signal, exact score
retention, compiled-profile identity and WAV SHA-256. It does not use producer or
verifier amplitude calculations as the musical oracle.

The isolated percussion path has all sustained drawbars at zero, Second/Normal/
Fast settings, normalized source amplitude 1 and the nominal profile output gain
0.03. The expected amplitude before readiness is therefore `0.03 × 1.5 = 0.045`.
Normal sustain compensation must not attenuate this path. The model's time
constants are:

```text
tau_fast = (1.5e6 * 4.7e6 / (1.5e6 + 4.7e6)) * 3.3e-7 seconds
tau_recovery = 0.03432 seconds
```

Ideal-contact events press A4 at 0 ms, add E5 at 120 ms, release A4 at 250 ms and
release E5 at 350 ms. Represses at 370 and 600 ms follow distinct 20 and 50 ms
recovery gaps. A duplicate at 700 ms and release/press at the same 750 ms offset
must continue the existing state. Six single-tone windows per sample rate cover
the initial attack, the joining note after the first key releases, both recovery
gaps and both zero-recovery operations. Silence windows must contain exact zeros.

Readiness is evaluated by piecewise closed-form exponentials from these known
detector intervals, not by copying the C++ sample recurrence. The two unknown
coefficients in `q[n] × (a sin(ωn) + b cos(ωn))` account for the source's unknown
seeded phase. A full two-variable least-squares system retains finite-window
cross terms. Its measured amplitude is `hypot(a,b)`; no source PRNG is reproduced.

A separate 150 ms nominal-contact experiment checks selected-harmonic sound
before the ninth-contact detector closes, subsequent decay, and recovery while
the releasing harmonic contact remains closed. Make/break times follow the
declared normalized thresholds and full-travel durations. Three windows at each
sample rate add nine PCM comparisons, for **27 analytic amplitude windows**.

Every fit propagates a per-sample error allowance of `1/32768 + 1e-8` through the
actual inverse normal matrix using coefficient-row L1 norms. One PCM step covers
serialization rounding/scaling; the small additional allowance covers the float
conversion and short supported-build phase/trigonometric calculation. The
combined coefficient bound bounds amplitude error without assuming random
quantization noise, a known phase or an integer number of waveform periods. A
second assertion requires each bound below 0.0002 so a poorly conditioned or
nearly silent window cannot pass with an uninformative allowance. These PCM
checks complement the tighter module/engine timing tests; they cannot distinguish
every sub-LSB or single-sample readiness discrepancy.

Six additional comparisons use the same score at block sizes 1 and 1024, across
44.1, 48 and 96 kHz and both contact modes. Each pair must have identical complete
WAV bytes and decoded PCM. The manifest's block size and directory-dependent
invocation naturally differ. Compiler/library changes may change floating-point
audio bytes; no cross-build bitwise assertion is made.

## Run and remaining gates

After a normal CMake build:

```sh
ctest --test-dir build -R python_test_console_evidence --output-on-failure
```

Direct execution requires both `HAMMOND_RENDER_EXECUTABLE` and
`HAMMOND_TEST_PROFILE`. Missing prerequisites are failures, never skipped tests.
Only the Python standard library and the existing built renderer are used; test
bundles live in bounded temporary directories and are removed afterward.

Hardware contact timing/bounce, preset latching/loading, pedal shaping, continuous
drawbars, loaded expression, AO-28 transfers, scanner and Leslie models retain
separate gates. Native host/device behavior, concurrent publication, callback
deadline evidence and calibrated instrument comparisons are also separate from
these offline experiments. Bundle hashes establish internal integrity; they do
not authenticate a performer, specimen, acquisition or claimed build origin.

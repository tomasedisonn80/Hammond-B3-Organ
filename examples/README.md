# Synthetic nominal-engine fixtures

These five short event scores exercise the existing offline renderer. They are
original synthetic gestures for `nominal-unmeasured-v1` / `ideal-shared-sine-v1`,
using normalized sine sources, proposed 12-TET tuning, ideal key gates, retained
drawbar banks and a linear expression control. They contain no recorded samples.
They make no measured-instrument, hardware-fidelity or performance claim.

The versioned [catalog](fixtures/catalog-v1.json) binds each score by SHA-256 and
records its purpose, sample rate, total frames, seed, initial registration,
profile identity, amplitude ceiling and engineering expectations. Event paths
are relative to the catalog; its authoring-profile path is relative to the
repository root. Spans are half-open absolute frame intervals `[start, end)`.
All fixtures use 48,000 Hz, explicitly request 127-frame renderer blocks, and
last at most four seconds. A fixture's score comment repeats its render settings.

| Fixture ID | Length | Initial upper B drawbars | What to hear/check |
|---|---:|---|---|
| `two-manual-changes-v1` | 4.0 s | `006400000` | C–F–G–C chords on both manuals; the upper registration brightens at 1.75 s; the final half-second is silent |
| `a4-fundamental-v1` | 1.5 s | `008000000` | One second of upper A4 through its 8-foot contact: nominal tone 46 at 440 Hz |
| `low-fold-coherent-v1` | 2.0 s | `800000000` | Tone 13 through one, two, three, then one coherent branches, including a lower-manual contact |
| `held-bank-cancel-v1` | 3.0 s | `008000000` | One held A4 key follows B/A selection, an inactive-bank edit, Cancel, an edit while cancelled, reselect, then panic |
| `high-fold-coherent-v1` | 1.5 s | `000800000` | Top-key 4-foot, 2-foot and twice-folded 1-foot contacts all add coherently at tone 85 |

`--drawbars` initializes upper bank B only. Lower B and both A banks start muted;
the scores explicitly make any other controls they need. Physical drawbar order
is 16′, 5⅓′, 8′, 4′, 2⅔′, 2′, 1⅗′, 1⅓′, 1′. The 8-foot fundamental is therefore
the **third** digit, and `888000000` would not isolate a fundamental. Nonzero note
velocity holds a key; it does not scale the sustained signal in this engine.

## Render from a fresh output directory

Run these commands from the repository root after building the renderer. The
commands below use the normal Linux/macOS single-configuration executable path;
on other generators use the path to the built `hammond_render` executable.

```sh
cmake --preset debug
cmake --build --preset debug
cmake -E make_directory out/fixtures-v1

./build/hammond_render --profile build/nominal.b3p \
  --output out/fixtures-v1/two-manual-changes-v1.wav \
  --events examples/fixtures/two-manual-changes-v1.events \
  --sample-rate 48000 --frames 192000 --block-size 127 --seed 2601 \
  --drawbars 006400000 --fail-on-clip

./build/hammond_render --profile build/nominal.b3p \
  --output out/fixtures-v1/a4-fundamental-v1.wav \
  --events examples/fixtures/a4-fundamental-v1.events \
  --sample-rate 48000 --frames 72000 --block-size 127 --seed 2602 \
  --drawbars 008000000 --fail-on-clip

./build/hammond_render --profile build/nominal.b3p \
  --output out/fixtures-v1/low-fold-coherent-v1.wav \
  --events examples/fixtures/low-fold-coherent-v1.events \
  --sample-rate 48000 --frames 96000 --block-size 127 --seed 2603 \
  --drawbars 800000000 --fail-on-clip

./build/hammond_render --profile build/nominal.b3p \
  --output out/fixtures-v1/held-bank-cancel-v1.wav \
  --events examples/fixtures/held-bank-cancel-v1.events \
  --sample-rate 48000 --frames 144000 --block-size 127 --seed 2604 \
  --drawbars 008000000 --fail-on-clip

./build/hammond_render --profile build/nominal.b3p \
  --output out/fixtures-v1/high-fold-coherent-v1.wav \
  --events examples/fixtures/high-fold-coherent-v1.events \
  --sample-rate 48000 --frames 72000 --block-size 127 --seed 2605 \
  --drawbars 000800000 --fail-on-clip
```

The renderer creates each WAV and prints a JSON report containing float peak,
RMS and clipped-frame count. `--fail-on-clip` requires zero clipping before WAV
publication. Use a new output directory or unused filenames for a subsequent
run: the renderer preserves existing destinations. The output filesystem must
support hard links; see the [rendering contract](../docs/RENDER_FORMAT.md).

For a retained evidence bundle, the optional wrapper compiles the authoring
profile, always enables clipping rejection, and saves copied inputs, hashes,
`render.wav` and `manifest.json`. Its output directory must not already exist:

```sh
cmake -E make_directory out
python3 tools/render_fixture.py --renderer build/hammond_render \
  --output-dir out/two-manual-evidence-v1 \
  --profile-json data/profiles/nominal-unmeasured-v1.json \
  --events examples/fixtures/two-manual-changes-v1.events \
  --sample-rate 48000 --frames 192000 --block-size 127 --seed 2601 \
  --drawbars 006400000
```

The wrapper records one render run. The catalog remains the reviewed source of
these fixture settings and expectations; the wrapper does not select them by ID.

## What the waveforms establish

Each WAV has two identical dry PCM16 channels. The musical example's conservative
sum-of-absolute-branch-gains ceiling is below 0.112 normalized peak; the other
fixtures remain below 0.0451. These are digital headroom bounds for this bound
profile, not measured organ voltages or universal safe registration limits.

Abrupt ideal contact gates, registration changes and Cancel can click at their
event frames. Sine-only source generation does not make these switching edges
band-limited. No contact bounce, measured click spectrum, transformer loading,
percussion, pedal audio, scanner, AO-28 circuit, Leslie or room is represented.
The exclusive A/B selector is the current engineering console model; see the
[console extension](../docs/CONSOLE_EXTENSION.md).

The low-fold fixture has upper MIDI 36's 16-foot and 8-foot contacts and lower
MIDI 48's 16-foot contact all using tone 13. The high-fold fixture has upper
MIDI 96's 4-foot, 2-foot and 1-foot contacts all using tone 85. Their expected
peaks are 0.015, 0.030 and 0.045 when one, two and three branches are active.
They sum the same source coherently; no polyphony normalization is applied.
These routing facts concern the declared nominal map and its atlas-derived
boundaries, not a separately measured complete factory wiring inventory.

In the bank fixture, the single note-on occurs at frame 4807. Cancel silences
`[48023, 72031)` while retaining that key; changing the selected bank during this
interval leaves it silent. Reselecting B restores its edited 8-foot level,
selecting A restores its edited 4-foot level, and panic at frame 120047 removes
the key even when B is selected again. The uneven transition frames make an
accidental phase restart observable.

## Check the catalog and the rendered audio

```sh
python3 tests/test_fixture_catalog.py \
  --renderer build/hammond_render --profile build/nominal.b3p

# CMake discovers the test when the project is configured/built.
ctest --test-dir build -R '^python_test_fixture_catalog$' --output-on-failure
```

CTest injects `HAMMOND_RENDER_EXECUTABLE` and `HAMMOND_TEST_PROFILE`; direct CLI
overrides above select the same inputs. An explicitly configured missing path
fails clearly instead of falling back to another build or skipping audio.

The test validates catalog/profile/score hashes, confined paths, event grammar,
ordered bounded timelines and routing anchors, then renders every score into a
temporary directory. It checks WAV structure, identical channels, reported
metrics, zero clipping, exact silent spans and audible spans. Single-tone spans
are fitted against their declared frequency with PCM quantization tolerance;
their levels and absolute-time phases establish coherent addition and phase
continuity. Mixed chord spans check the declared frequency components and
registration levels with a finite-window leakage allowance. Source phase is
inferred from audio, without duplicating the engine's phase PRNG.

No generated WAV is checked into this catalog. The fixtures total 12 seconds of
audio per test run and each subprocess has a 30-second timeout. They qualify
these short engineering behaviors, not callback deadlines, native hosts, broad
physical fidelity or bitwise identity across compilers and math libraries.

## Nominal console continuation fixtures

The separate [console catalog](fixtures/console/console-catalog-v1.json) adds three
original synthetic scores for `nominal-linear-travel-v1` contacts and
`shared-readiness-v1` percussion. The five fixtures above remain unchanged and
continue to exercise their original ideal-contact/percussion-off defaults.
These new scores use the same bound source profile, explicitly set expression
0.5, and contain **no acquired instrument audio**. Their contact thresholds,
8 ms full press, 12 ms full release and normalized percussion gains are proposed;
RC-derived time constants remain hypotheses, not measured audible decay lengths.

| Fixture ID | Length | Initial upper B drawbars | Initial percussion | What to hear/check |
| --- | ---: | --- | --- | --- |
| `console-travel-v1` | 0.300 s | `008000000` | Off / Normal / Slow | Upper then lower A4, with separate contact travel but shared continuous source phase; velocities 127 and 1 have the same held level |
| `console-percussion-legato-v1` | 0.875 s | `000000000` | Second / Normal / Fast | A4 decays, a joining C5 inherits shared readiness, and a short release gap permits finite recovery before A4 returns |
| `console-routing-mask-v1` | 0.800 s | `000000008` | Second / Soft / Slow | Held upper/lower A4 through A/B, Cancel, hidden edit and percussion-off changes; the lower one-foot branch stays audible when eligible upper B is masked |

All use 48 kHz, 127-frame reference blocks and the exact seed/score hashes in the
catalog. Half-open acceptance windows identify sample boundaries rather than
block boundaries. The travel example's upper 8-foot contact makes at frame 160
and breaks at 6438; its lower counterpart makes at 7126 and breaks at 13447.
The percussion detector is the ninth physical contact (index 8 / 1-foot), not
the selected audible harmonic or a nonzero drawbar setting.

Render after building, using unused output names:

```sh
cmake -E make_directory out/console-v1

./build/hammond_render --profile build/nominal.b3p \
  --output out/console-v1/console-travel-v1.wav \
  --events examples/fixtures/console/console-travel-v1.events \
  --sample-rate 48000 --frames 14400 --block-size 127 --seed 2623 \
  --drawbars 008000000 --contacts nominal --percussion off \
  --percussion-volume normal --percussion-decay slow --fail-on-clip

./build/hammond_render --profile build/nominal.b3p \
  --output out/console-v1/console-percussion-legato-v1.wav \
  --events examples/fixtures/console/console-percussion-legato-v1.events \
  --sample-rate 48000 --frames 42000 --block-size 127 --seed 2624 \
  --drawbars 000000000 --contacts nominal --percussion second \
  --percussion-volume normal --percussion-decay fast --fail-on-clip

./build/hammond_render --profile build/nominal.b3p \
  --output out/console-v1/console-routing-mask-v1.wav \
  --events examples/fixtures/console/console-routing-mask-v1.events \
  --sample-rate 48000 --frames 38400 --block-size 127 --seed 2625 \
  --drawbars 000000008 --contacts nominal --percussion second \
  --percussion-volume soft --percussion-decay slow --fail-on-clip
```

For a retained schema-2 bundle, pass the same flags and score to
`tools/render_fixture.py`, replacing `--profile`/`--output` with
`--profile-json data/profiles/nominal-unmeasured-v1.json` and a fresh
`--output-dir`. Verify the resulting directory independently with
`tools/verify_render.py`; see the [evidence contract](../docs/RENDER_EVIDENCE.md).

Run the dedicated actual-audio checks:

```sh
python3 tests/test_console_catalog.py \
  --renderer build/hammond_render --profile build/nominal.b3p -v
ctest --test-dir build -R '^python_test_console_catalog$' --output-on-failure
```

The test requires actual build inputs, validates bounded source/score identities,
then renders every score at block sizes 1, 127 and 1024. It checks exact same-build
WAV equality, PCM structure, identical channels, no clipping, silent/audible spans
and the declared contact edges. Independent sine/cosine regression uses absolute
frame positions and closed-form elapsed-time exponentials to check component
levels, shared decay/recovery and phase continuity. It never copies the source
phase PRNG or imports production evidence validation. Each declared fit has a
maximum residual of two PCM16 units, a component-amplitude tolerance of 0.00004,
and a normalized phase-vector tolerance of 0.006. These are reviewed software
acceptance tolerances, not instrument uncertainty estimates.

No generated WAV is checked into this catalog. The scores total 1.975 seconds
per partition; each renderer subprocess has a 30-second timeout. The contact
model still uses sample-grid binary switches without bounce or antialiasing.
Percussion is one nominal readiness/gain model, not a complete AO-28 circuit.
Pedal audio, physical preset loading, loaded expression, scanner, Leslie, native
hosts and physical-fidelity qualification remain separate work.

# Fixed nominal pedal voice

`render_nominal_pedal_voice` implements the original, explicitly unmeasured
mixture adopted in [the pedal integration contract](PEDAL_INTEGRATION_CONTRACT.md).
Its inputs are the four excitations from [PedalBusKernel](PEDAL_RUNTIME_CONTRACT.md)
and two retained integer control positions. It returns both mixtures and a
separate pedal contribution `P`, before common Engine expression and output gain.

The source basis is [atlas pp. 139-144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139)
for the shared-source, four-bus architecture and independent linear-reference
acceptance, plus [p. 447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447)
for a replaceable nominal console model. The chosen coefficients originated in
[assignment 02](development/2026-11-13-pedals/02-atlas-console.md) and were adopted
by the integrator. They are not recovered factory or atlas companion values.

## Fixed identities and arithmetic

| Item | Value and evidence scope |
| --- | --- |
| Voice identity | `nominal-static-pedal-mixture-v1`; proposed engineering fixture |
| Audio gain-law identity | `linear-pedal-position-v1`; proposed engineering fixture |
| Bus order | Brown, Red, Orange, Yellow; documentary routing convention |
| Control labels | Pedal Mixture 1 and Pedal Mixture 2 |
| Branch weights | Explicit +1 for each of 200 independent positions, including disconnected positions; dimensionless reference weights |
| Gain law | `g(p) = p/8`, for integer positions 0-8; separate from the manual profile's gain table |
| Units | Dimensionless source-normalized values throughout; no voltage calibration |
| Applicable scope | The nominal B-3/C-3 routing fixture, with ideal branch weights and two independent software controls |
| Physical uncertainty | Reactor/loading, low-wheel spectra, true control coupling and transfer error remain unmeasured; no calibrated footage response is claimed |

The complete immutable matrix is:

| Output | Brown | Red | Orange | Yellow |
| --- | ---: | ---: | ---: | ---: |
| Mixture 1, `z0` | 1/2 | 1/4 | 1/8 | 1/8 |
| Mixture 2, `z1` | 1/8 | 1/2 | 1/4 | 1/8 |

Both rows sum to one. The final contribution is
`P = g(p0) * z0 + g(p1) * z1`. Each row accumulates in the listed bus order;
the two scaled mixtures are then added. With both positions zero, `P` is
canonical positive zero while both pre-control mixture diagnostics remain
available. The module neither evaluates sources nor advances any clock.

Each bus input must be finite and in [-50,50], matching the reference kernel's
maximum of 50 bounded contributions per bus. The fixed nonnegative matrix
therefore bounds each mixture by 50 and `P` by 100. These mathematical bounds
do not establish an unclipped WAV after other divisions and output gain are
included. The implementation adds no limiter, saturation, held-pedal
normalization, attack/release envelope or monophonic policy.

## Public interface and failure behavior

The definitions are in [PedalVoice.h](../include/hammond/PedalVoice.h), with the
operation implemented in [PedalVoice.cpp](../src/PedalVoice.cpp):

```cpp
using PedalDrawbarPositions = std::array<std::uint8_t, kPedalDrawbarCount>;

struct PedalVoiceFrame {
    std::array<double, kPedalDrawbarCount> mixtures{};
    double output{0.0};
};

Status render_nominal_pedal_voice(
    const PedalBusFrame& buses,
    const PedalDrawbarPositions& positions,
    PedalVoiceFrame& destination) noexcept;
```

There is no preparation state or caller-supplied matrix. The function validates
every bus, including when both positions are zero. Any nonfinite or out-of-range
bus returns `Status::InvalidBuffer`. Only after all buses pass does it validate
both positions; a value outside 0-8 returns `Status::InvalidEvent`. These are the
explicit error-precedence rules. Both failures preserve every destination value,
including signed-zero and NaN payload bits already present there. Success
computes a local result and commits it once.

`is_valid_pedal_drawbar_positions` provides the same bounded control validation.
`nominal_pedal_reference_weights()` returns an owned 200-element array of +1
weights for explicit use with `PedalBusKernel::prepare`. It does not change the
kernel's requirement that callers supply weights. Editing a returned array does
not alter later calls or model metadata.

Program-lifetime, immutable metadata includes:

- `kNominalPedalVoiceModelId` and `kNominalPedalGainLawId`.
- `kNominalPedalMixtureMatrix`, `kNominalPedalPositionGains` and
  `kNominalPedalMixtureLabels`.
- `kNominalPedalBusInputLimit`, `kNominalPedalMixtureOutputLimit` and
  `kNominalPedalOutputLimit`.

These values can support the later native model-info export without copying
another set of model constants. A different matrix, gain law or loaded physical
model needs a different identity and its own validation. The current function
accepts no custom coefficients that could be mislabeled with the nominal ID.

## Independent software acceptance

[test_pedal_voice.cpp](../tests/test_pedal_voice.cpp) uses separate
integer-numerator equations for its reference, rather than reading the
production matrix or gain table. It exercises every bus basis, all 16 extreme
input corners, representative exact rational mixed inputs and all 81 control
pairs. Those cases require exact arithmetic agreement and explicitly reach
`P=100`, detecting a hidden limiter or normalization.

For ordinary floating-point inputs, it uses a fixed absolute bound of
`32 * binary64 epsilon * 100`, approximately `7.105427357601002e-13`.
The factor conservatively covers rounded arithmetic in both the production and
independently arranged reference paths, including directed rounding modes.
This bound was chosen before execution; it is a numerical software criterion,
not a physical or perceptual tolerance. The same gate covers all four standard
rounding modes, adjacent in-range limits, subnormal values and signed zero,
while verifying that the function preserves the caller's rounding mode.

Failure tests put invalid values in every bus and every control position,
including muted inputs and every rejected `uint8_t` position value. They check
destination bit preservation and error precedence. Repeated valid calls around
an unrelated frame and a rejected call establish stateless repeatability.

Run the focused registered test after building a coherent source snapshot:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target test_pedal_voice
ctest --test-dir build -R '^test_pedal_voice$' --output-on-failure
```

The [assignment 13 record](development/2026-11-13-pedals/13-pedal-voice.md)
retains actual commands, source identities and observed results. Engine
integration, enabled-path allocation instrumentation, legacy audio, host,
physical-fidelity and full-product gates remain separate. A future loaded
replacement must preserve source identity, four-bus/control boundaries and
observable control semantics while adding the explicitly identified reactive
state, loading and physical evidence required by its model.

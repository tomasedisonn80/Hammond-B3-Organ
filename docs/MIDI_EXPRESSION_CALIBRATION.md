# MIDI expression endpoint calibration

Contract identity: **`midi-expression-endpoints-v1`**. Frozen behavior contract
from product continuation wave 2. The current native implementation and its
independent acceptance are recorded in [current status](STATUS.md), the
[operating guide](MIDI_EXPRESSION_GUIDE.md) and the
[source-specific Linux platform review](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md).
This is adapter configuration for the native standalone's single MIDI input,
not an AO-28 electrical model, factory measurement or sound-state migration.

The source basis is atlas pp. 145–150 (controller calibration before instrument
response), 151–156 (ownership, acknowledgment and separate controller defaults),
and 421–444 (consistent input and readable settings). The existing
[interface guide](INTERFACE_RUNBOOK.md), [MIDI guide](MIDI_UI_RUNBOOK.md) and
[whole plan](PLAN.md) retain their broader contracts.

## Exact mapping and public API

Add these SDK-independent declarations to `apps/standalone/MidiInput.h` in
`hammond::standalone`:

```cpp
inline constexpr std::string_view kMidiExpressionCalibrationModelId =
    "midi-expression-endpoints-v1";

struct MidiExpressionCalibration {
    std::uint8_t minimum{0};
    std::uint8_t maximum{127};
    bool inverted{false};
    [[nodiscard]] bool operator==(const MidiExpressionCalibration&) const noexcept = default;
};

[[nodiscard]] bool valid_midi_expression_calibration(
    const MidiExpressionCalibration& calibration) noexcept;
[[nodiscard]] bool map_midi_expression(
    const MidiExpressionCalibration& calibration, std::uint8_t raw,
    double& destination) noexcept;
```

A configuration is valid exactly when `minimum < maximum <= 127`. Validate
before subtraction or narrowing. `map_midi_expression` also requires `raw <= 127`;
invalid input returns false and preserves the destination. Valid input computes

```text
u = double(clamp(int(raw) - int(minimum), 0, int(maximum) - int(minimum)))
    / double(int(maximum) - int(minimum))
result = inverted ? 1.0 - u : u
```

Every result is finite and in [0,1]. The lower and upper input endpoints map
exactly to 0 and 1 respectively before inversion. Values outside the calibrated
interval saturate. Inversion changes direction after saturation. There is no
curve, smoothing, dead zone, automatic learning or additional gain. Defaults
must produce exactly the existing `double(raw) / 127.0` for all 128 raw values.

Only mapped **CC11** messages use this function. They continue to produce one
`MidiParameterEdit{8192, result}` through `UiModel::external_parameter`, followed
by the existing whole-snapshot submission/acknowledgment path. All mapped wire
channels share the existing single global expression parameter; this feature
does not introduce independent expression per manual. Other controller mappings,
notes, timestamps, diagnostics counters and packet admission retain their meaning.

**CC121's declared expression default is normalized 1.0 and bypasses this
mapping.** Resetting controllers does not reset the calibration. Its other
behavior belongs to the separate channel-mode contract.

Extend `MidiInput` with:

```cpp
[[nodiscard]] bool begin_epoch(
    const MidiRouting& routing = {},
    const MidiExpressionCalibration& calibration = {}) noexcept;
[[nodiscard]] const MidiExpressionCalibration& expression_calibration() const noexcept;
```

The second default argument preserves existing callers. An active epoch,
invalid route or invalid calibration rejects without changing any member or
counter. Success copies route and calibration together, then begins the epoch.
The accessor returns the last accepted epoch's settings; callers must check
`active()` before describing them as active. `end_epoch()` retains those values
and only performs its existing retirement of decoder activity/timestamp history.
No setter changes calibration while an epoch is active. All functions use fixed
storage and have no allocation, locks, I/O or audio-thread access.

## CLI and native settings

Add these options to the ordinary pre-initialization parser:

| Option | Meaning and validation |
| --- | --- |
| `--expression-min N` | Raw lower endpoint, decimal integer 0–127, default 0. |
| `--expression-max N` | Raw upper endpoint, decimal integer 0–127, default 127. |
| `--expression-invert` | Flag selecting inverted direction; absent means normal. |

Existing duplicate-option rejection applies, including the flag. Missing,
negative, overflowing, fractional or trailing-text numbers reject. Validate the
combined endpoint ordering before SDL/device initialization or any output write,
including when no input port is selected. Parse into a wider integer before
conversion to `uint8_t`. Options are legal with synthetic MIDI replay; every
script connect uses the configured calibration. Replay format and script-owned
connect/disconnect behavior remain unchanged.

The MIDI modal adds **EXPRESSION MIN**, **EXPRESSION MAX** and
**EXPRESSION DIRECTION**. Minimum/maximum are distinct from physical heel/toe;
the normal/inverted label makes direction explicit. Keep selected values
separate from configured and active values. Opening the modal copies the latest
configured settings. Editing or closing does not apply them. The existing
modal-opening UI-note release policy remains unchanged.

Use eleven modal focus stops: previous port, next port, Upper channel, Lower
channel, Pedal channel, minimum, maximum, direction, Apply, Disconnect, Close.
Both paint and pointer input use one `MidiOverlayLayout`; update its rectangle
array and bounds consistently. Arrow keys adjust endpoints by one, clamped to
0–127; click/Enter/Space increments. Home/End sets endpoints to 0/127. Direction
activation or an arrow toggles it; Home selects normal and End inverted.
Tab/Shift+Tab wraps all eleven stops. Endpoint edits may temporarily produce an
invalid pair so either order can be entered; show a readable error, and invalid
Apply preserves the old route, epoch and configured values. No silent swapping.

The expanded dialog must fit the 960×700 minimum window and both presentations.
Identify **selected settings**, **active calibration**, and inactive/pending
connection states clearly; selected values are not proof of decoder application.
Keep the actual connection result visible after Apply. Synthetic replay Apply
continues to leave its script-owned route and calibration unchanged; use CLI
settings for replay. Disconnect remains operational.

Apply validates the selected route/calibration first, including during synthetic
replay. An invalid selection reports its error without any mutation. A valid
Apply during replay then retains the script-owned configuration and reports that
the script controls connection changes; it does not update configured settings.

## Epoch transition and persistence

Extend the main-thread `MidiRequest` value to include calibration. Startup,
script connects and native Apply carry it through `start_pending_midi()` into
`begin_epoch`. Validate before retiring an old epoch. The identical
port + routing + calibration request is a no-op when already healthy/active.
Changing any of those three deliberately uses the existing lifecycle:

1. Stop old admission, join the backend, and discard its retired inbox.
2. Submit the existing three scoped MIDI-owner releases and wait for their
   applied acknowledgment/recovery barrier.
3. Start the new decoder/device epoch with the copied configuration.

Thus reconfiguration releases MIDI-owned notes by explicit policy; it never
reinterprets queued bytes under a different mapping. It does not reset the dry
Engine, generator phase, non-MIDI ownership, musical controls or percussion
history. A failed open stays inactive and requires another explicit request.
No automatic reconnect or replay of held notes is added.

Selecting No input may retain a valid configured calibration for a later
connection. Applying calibration itself sends **no expression update**: the
previous musical expression remains until a later admitted CC11, CC121 or
ordinary existing control action changes it. Calibration survives ordinary
MIDI reconnect and audio restart within this process through configured state.
It is not saved in `B3CONTROLS4`, earlier state readers or a new preference file;
CLI arguments provide reproducible startup settings. All 47 parameter IDs and
nominal expression/Engine arithmetic remain unchanged.

Diagnostics must identify the calibration model, configured settings, selected
settings and active settings separately. Active settings are `null` when no
epoch is active; a pending reconnect names its copied request and pending state.
Record pre-shutdown active settings separately from post-shutdown inactivity.
Do not call last-accepted settings active after a failed open or retirement.

## Required acceptance

- Exhaust all 128 values for default exact equivalence, both directions,
  representative narrow/full intervals, saturation, endpoints and monotonicity.
  Reject every invalid interval category and raw values 128–255 without mutation.
- Reject active/invalid `begin_epoch` calls without changing route, calibration,
  timestamp history or counters; reconnect uses the new settings only after the
  old scoped release acknowledgment and inbox retirement.
- Trace CC11 through the real decoder/UI/Session acknowledgment, interleaved with
  drawbar edits and notes. Applied expression agrees with the mapping; all other
  controls, owner scopes and continuous source histories remain preserved.
- Verify CC121 produces 1.0 with inverted/non-default calibration and retains
  the calibration. No other controller is recalibrated.
- Test CLI refusals before output writes, synthetic replay connects, modal
  keyboard/pointer traversal, invalid Apply, cancellation, identical Apply,
  changed Apply, failed reopen and truthful selected/pending/active diagnostics.
- Capture the real native dialog in minimum/reference sizes and Flat mode;
  check labels, focus, hit/paint alignment and original key-up handling. This
  does not establish physical pedal calibration, devices or screen-reader access.

Implementation ownership should separate `MidiInput.h/.cpp` and its SDK-free
tests from `main.cpp` lifecycle/CLI/diagnostics and `InstrumentView.h/.cpp`
modal geometry/paint. Coordinate those shared files with channel-mode and visual
workers before editing; the integrator owns CMake, shared guides and publication.

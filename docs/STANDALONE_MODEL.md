# What the standalone instrument models

The standalone is an early playable window for the repository's **nominal dry
organ**. It uses the same C++ engine and compiled `nominal-unmeasured-v1` profile
as the offline renderer and headless VST3. Its implementation does not establish
a match to a measured Hammond specimen or a complete B-3/AO-28/Leslie system.

## Available musical behavior

Two 61-key manuals and 25 independently held pedals share 91 continuously running
tone sources. Playing a new note does not restart a source. The sources are
proposed ideal sine waves with nominal tuning, levels and initial phases; they
are not captured pickup waveforms. This preserves coherent shared-source sums
and gives timing/routing tests a repeatable model.

Each manual retains nine drawbar positions in both A and B banks. **EDIT A/B**
chooses which retained bank the screen edits. **PLAY A/B** selects the sounding
bank and reconnects that manual. **CANCEL** disconnects its route while retaining
its held keys and stored values. **PANIC** releases notes globally. These actions
have different musical meanings and should not be interchanged.

Drawbars use the implemented integer positions 0–8. Expression is a normalized
linear gain surrogate. The two pedal controls are the existing **Mix 1** and
**Mix 2** nominal mixtures, not independently measured historical footage laws.
The upper-B percussion route retains its four switch settings even when another
bank is selected. Percussion and ideal key contacts remain identified behavioral
models; the standalone does not imply that their physical circuits were fitted.

The application may explicitly load a proposed audition registration so its
initial window can be played immediately: upper B `888000000`, lower B
`008000000`, pedals `80`. That is an application startup choice, not a factory
preset, a new core default or a new state version. A valid selected saved-control
file supplies its own values instead.

## Audio and saved controls

The Session sends identical left/right dry float32 samples to the device adapter.
There is no added stereo room, scanner or rotary cabinet. The device adapter
passes in-range finite samples unchanged, clamps finite outliers to [-1, 1] with
counted clips, and silences a callback containing a nonfinite sample. There is no
hidden loudness normalization. A clip counter identifies output saturation; it
does not identify an amplifier model.

Musical control files use the existing `B3CONTROLS3` grammar and retain the
existing migrations from versions 1 and 2. They contain bank values, route
selection, expression, percussion and pedal controls. They do not contain held
notes, source phases, contact travel, envelope readiness, the sample clock,
audio-device preferences or window geometry. Loading a control file is not
restoring an exact audio checkpoint.

UI events apply at an admitted callback boundary. Computer-key input and pointer
input are supported by this adapter; a hardware MIDI input transport and its
latency/timestamp policy require separate implementation and evidence. The
existing VST3 event buses belong to the plugin adapter.

## Continuing toward the complete instrument

The [M0–M9 plan](PLAN.md) retains the complete project sequence and evidence.
The [scanner track](SCANNER_HANDOFF.md) is still qualifying a separate nominal
circuit/rotor realization. Connected AO-28 electronics, identified Leslie 122/147
circuits, independent horn/drum acoustics, measured calibration and held-out
listening evidence remain later dependencies. The fixed chapel registrations on
atlas p122 now have two agreeing image transcriptions and a strict
[documentary catalog](CHAPEL_PRESETS_CATALOG.md), covering all 18 rows and 162
connection digits. The underlying factory Table IV, loaded gains, physical
selector and latch behavior remain separate M3 gates. The standalone currently
exposes the implemented A/B/Cancel controls; importing registration values into
those controls does not implement the physical fixed-key mechanism.

Actual dummy-backend callbacks, synthetic renders and software screenshots
verify their stated engineering paths. Physical devices, deadline/underrun and
latency measurements, native screen readers, musician workflows, signed
installers and specimen-specific fidelity each require their own retained
results. The [current status](STATUS.md) and [handoff](STANDALONE_HANDOFF.md)
identify which gates have actually run for a named revision.

Source basis: atlas pp. 379–408, 409–444 and 445–456; existing
[implementation contract](IMPLEMENTATION_CONTRACT.md),
[pedal engine](PEDAL_ENGINE.md), [control state](CONTROL_STATE_FORMAT.md) and
[standalone scope](STANDALONE_SCOPE.md). The new full-atlas reading notes are in
[the current session](development/2026-11-13-next-phases/README.md).

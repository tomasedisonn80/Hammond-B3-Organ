# What the standalone instrument models

The standalone is a playable native window for the repository's **nominal dry
organ**, with keyboard/pointer playing and optional native MIDI input. It uses
the same C++ engine and compiled `nominal-unmeasured-v1` profile
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

The reference-oriented interface retains all 45 public parameter identities and
the same musical state. Its additional MIDI settings action is an application
control, not a new sound parameter. Source-art walnut and cabinet decoration
comes from the atlas cover/page 409 generated concept; the cabinet is visible
when the window is wide enough. It does not implement a rotating speaker,
speed switch, scanner, microphone or room. Correct dynamic keys, drawbar labels
and control behavior take precedence over the concept's inaccurate legends.
The [reference review](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/reviews/MIDI_UI_REFERENCE_REVIEW.md) records actual
captures, remaining appearance differences and the minimum-size text-legibility
gate. It does not establish a one-to-one visual match.

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

UI and admitted MIDI events apply at callback boundaries. Optional pinned RtMidi
6.0.0 provides one explicitly selected native input, using ALSA on Linux, WinMM
on Windows or CoreMIDI on macOS. Three distinct one-based wire channels map to
upper/lower/pedals (defaults 1/2/3). Manuals accept notes 36–96; pedals accept
36–60. Other wire channels and pitches outside those ranges are counted and
ignored. Incoming positive note velocities retain the existing gesture meaning;
they do not introduce piano-like sustained gain. MIDI receipt timestamps remain
diagnostic metadata, without sample-accurate scheduling or a measured hardware
latency promise. Synthetic `B3MIDIREPLAY1` replay exercises the same application
routing without opening a physical port. The existing VST3 event buses remain
part of the separate plugin adapter.

Manual CC16–24 edit fixed **B** banks, independently of the screen's EDIT and
SOUNDING selections. Pedal CC16/17 edit Mix 1/Mix 2; CC11 edits shared nominal
expression. CC123 releases the mapped division's MIDI owners. Sustain,
CC120/121, pitch bend, pressure, Program Change and SysEx have no implemented
musical effect. MIDI edits join the same desired controls as local edits and
can be saved, but port/channel choices are machine setup and are not saved in
`B3CONTROLS3`. The [MIDI/UI runbook](MIDI_UI_RUNBOOK.md) gives the complete map,
connection steps and supported-message limits.

Normal MIDI disconnect releases MIDI owners while preserving UI holds. Panic,
audio Restart and faults retire incoming MIDI; connecting again requires an
explicit Apply after recovery. Old notes are never resurrected on reconnect.
The adapter's bounded queue, callback-boundary policy and synthetic tests are
implemented engineering behavior. Physical controllers, hotplug, end-to-end
latency and native-platform operation require their own retained evidence.

## Continuing toward the complete instrument

The [M0–M9 plan](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PLAN.md) retains the complete project sequence and evidence.
The [scanner track](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/SCANNER_HANDOFF.md) is still qualifying a separate nominal
circuit/rotor realization. Connected AO-28 electronics, identified Leslie 122/147
circuits, independent horn/drum acoustics, measured calibration and held-out
listening evidence remain later dependencies. The fixed chapel registrations on
atlas p122 now have two agreeing image transcriptions and a strict
[documentary catalog](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/CHAPEL_PRESETS_CATALOG.md), covering all 18 rows and 162
connection digits. The underlying factory Table IV, loaded gains, physical
selector and latch behavior remain separate M3 gates. The standalone currently
exposes the implemented A/B/Cancel controls; importing registration values into
those controls does not implement the physical fixed-key mechanism.

Actual dummy-backend callbacks, synthetic renders and software screenshots
verify their stated engineering paths. Physical devices, deadline/underrun and
latency measurements, native screen readers, musician workflows, signed
installers and specimen-specific fidelity each require their own retained
results. The [current status](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STATUS.md) and [handoff](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_HANDOFF.md)
identify which gates have actually run for a named revision.

Source basis: atlas pp. 379–408, 409–444 and 445–456; existing
[implementation contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/IMPLEMENTATION_CONTRACT.md),
[pedal engine](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PEDAL_ENGINE.md), [control state](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/CONTROL_STATE_FORMAT.md) and
[standalone scope](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_SCOPE.md). The latest full-atlas reading and engineering boundaries are retained in the
[MIDI/UI atlas review](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/research/MIDI_UI_ATLAS_REVIEW.md).

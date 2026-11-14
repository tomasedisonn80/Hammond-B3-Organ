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
chooses which retained bank the screen edits. The reversed preset octave selects
the sounding route: **C#–A** chooses one of nine fixed registrations, **A#** selects
adjustable bank A, **B** selects adjustable bank B, and **C** cancels the route.
Fixed selection and Cancel retain all adjustable banks and held-note histories.
**PANIC** releases notes globally. The [preset guide](PRESET_RUNBOOK.md) gives
the complete eighteen-row selection behavior and source limits.

The current interface preserves all **47 public parameter identities** and the
same musical state. Play, Rotary, Service and Flat are presentation choices,
outside those sound parameters. Play keeps the live controls; Service shows
read-only copied model/control facts and Rotary shows a cabinet reference with
explicit unavailable audio/physical values. Source-art walnut and cabinet
decoration comes from the atlas cover/page 409 generated concept. It does not
implement a rotating speaker, speed switch, scanner, microphone or room.
Correct dynamic keys, drawbar labels and control behavior take precedence over
the concept's inaccurate legends. The [current native gallery](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/examples/demos/standalone-interface-preview-v1/README.md)
records actual source-identified captures and remaining appearance differences.
It does not establish a one-to-one visual match. The
[interface guide](INTERFACE_RUNBOOK.md) explains current/retained/stopped and
unavailable inspection states; unknown physical values are not numeric zeros.

Drawbars use the implemented integer positions 0–8. Expression is a normalized
linear gain surrogate. The two pedal controls are the existing **Mix 1** and
**Mix 2** nominal mixtures, not independently measured historical footage laws.
The upper-B percussion route retains its four switch settings even when another
bank or a fixed registration is selected. Eligibility requires the enabled
Upper B route with no fixed choice. Percussion and `ideal-contacts-v1` remain
identified behavioral models; the standalone does not imply that their physical
circuits were fitted. Inspection does not expose transient percussion readiness.

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

Musical control files use **`B3CONTROLS4`** and retain readers for versions 1,
2 and 3. They contain all four bank memories, remembered sounding banks, raw fixed
choices, route bits, expression, percussion and pedal controls, with the pinned
fixed-registration catalog identity. Older versions migrate fixed modes to None;
the next explicit Save writes version 4. They do not contain held notes, source
phases, contact travel, envelope readiness, the sample clock, device preferences,
window geometry, workspace, Flat presentation or focus. Loading controls is not
restoring an exact audio checkpoint or a saved UI view.

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

Manual CC16–24 edit the retained **B** drawbar banks, independently of the screen's
EDIT bank and sounding fixed/adjustable/Cancel selection. They do not leave fixed
mode or reconnect Cancel; select preset B explicitly to hear that bank.
Pedal CC16/17 edit Mix 1/Mix 2; CC11 edits shared nominal
expression. CC123 releases the mapped division's MIDI owners. Sustain,
CC120/121, pitch bend, pressure, Program Change and SysEx have no implemented
musical effect. MIDI edits join the same desired controls as local edits and
can be saved, but port/channel choices are machine setup and are not saved in
`B3CONTROLS4`. The [MIDI/UI runbook](MIDI_UI_RUNBOOK.md) gives the complete map
and supported-message limits. The [interface guide](INTERFACE_RUNBOOK.md#midi-discovery-and-recovery)
describes nonblocking modal discovery and explicit refresh/connection.

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
selector and latch behavior remain separate M3 gates. The standalone implements
exclusive fixed selection through its 24 reversed preset keys and preserves
adjustable-bank memory; this nominal routing behavior does not model a measured
physical latch mechanism or calibrated transformer loading.

Actual dummy-backend callbacks, synthetic renders and software screenshots
verify their stated engineering paths. Physical devices, deadline/underrun and
latency measurements, native screen readers, musician workflows, signed
installers and specimen-specific fidelity each require their own retained
results. The [current status](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STATUS.md) and [interface session](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-14-interface-continuation/README.md)
identify which gates have actually run for a named revision.

Source basis: atlas pp. 379–408, 409–444 and 445–456; existing
[implementation contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/IMPLEMENTATION_CONTRACT.md),
[pedal engine](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/PEDAL_ENGINE.md), [control state](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/CONTROL_STATE_FORMAT.md) and
[interface scope](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/INTERFACE_CONTINUATION_SCOPE.md). The latest full-atlas reading and engineering boundaries are retained in the
[interface atlas review](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/research/INTERFACE_ATLAS_REVIEW.md).

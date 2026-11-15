# A07 — native MIDI channel-mode contract

Actual agent `/root/w02_a07_channel_contract`, wave 2. Inspected starting source
`647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb`; this assignment owns this note and
`docs/MIDI_CHANNEL_MODE_CONTRACT.md` only.

Read complete AGENTS/plan, the current session scope, atlas pp.151–156, current
navigation/status/log excerpts, ownership headers/implementations, PerformanceInput,
InputProcessor, HostTimeline, Session, MIDI decoder, Engine contact/rendering paths
and existing MIDI/ownership tests. Independently reopened both cited MIDI.org
primary overview pages. No build, test or product-code modification was performed.

The contract distinguishes CC120 from CC123 through a new fixed-size
`ScopedSoundOff` SessionCommand alternative, preserving existing alternatives.
It restricts immediate-silence reduction to ideal contacts. `Engine::contact_mode()`
directly exposes the owned ContactBank mode; standalone Session currently selects
ideal preparation. Finite release travel cannot safely use ordinary scoped release
as immediate silence. Following root's review, the final narrower design keeps
all generic core note enums/consumers unchanged and performs the explicit,
ideal-guarded reduction inside Session. Invalid typed scopes reject before queue
publication; future non-ideal Session preparation requires a new tail policy.

CC120 retires addressed owners only, preserving same-key UI/other origins, other
divisions, source phase and shared percussion history. Current percussion output
is contact-borrowed, so ideal final-owner release removes its contribution without
clearing another owner's envelope. Future shared tails remain an explicit gate.

CC121 resets only declared global expression, parameter8192, through UiModel's
shared desired-state path. It requests normalized1.0 directly, bypasses pedal
calibration and preserves calibration/settings, notes, registrations and all other
controls. A08 confirmed this interface boundary. CC120/121 reject nonzero values;
CC123 deliberately retains its existing all-value compatibility extension.

Acceptance names decoder, ownership/audio isolation, typed admission,
acknowledgment, queue recovery, partition and allocation checks. This is a
reviewable implementation target, not an acceptance or conformance claim.

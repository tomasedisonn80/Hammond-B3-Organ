# Assignment 06: atlas closure, product gates and standalone handoff

## Scope and actual reading

- Assignment identity: `/root/w01_a06_atlas_closure`; wave 1, second batch of this
  new session. This does not count an earlier session's reader again.
- Checkout inspected: `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`; only this note
  is owned by this assignment. Other workers' files are left unchanged.
- Read the entire extracted text of **PDF pages 421-500 inclusive: 80 pages**,
  chapters 069-080 and the complete eight-page source directory. The successive
  `sed` ranges were 1-550, 551-1150, 1151-1750, 1751-2350, 2351-2950,
  2951-3550, 3551-4150 and 4151-4810 in the session's `atlas/part6.txt`.
- Rendered and visually inspected original PDF pages **434 and 450** with
  `pdftoppm -singlefile -scale-to 1600 -png`. Page 434 contains the keyboard
  ownership table and an explicitly labeled original control-placement study;
  it is not an executed application screenshot. Page 450 contains the M9
  implementation and exit table.
- Verified the unchanged [source PDF](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf)
  SHA-256 as `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
  Page locators below are one-based PDF pages, also printed atlas page numbers.
- Read the standing agent instructions, current session scope, repository
  introduction and scanner handoff/status context. The selected new scope is an
  optional SDL2 standalone adapter around the existing nominal dry core. No
  production code, dependency, build, physical capture or remote write was
  produced or qualified by this reading assignment.

## The complete implementation sequence remains M0-M9

The atlas separates its research organization from implementation milestones
and from measured fidelity. Its final roadmap is on pp. 445-456, with explicit
acceptance and handoff on pp. 481-492.

| Milestone | Retained dependency and exit |
| --- | --- |
| M0 | Lock reference identities, variants, provenance, units and unknowns; a nominal fixture has its own identity (p. 445). |
| M1 | Prepare storage and a common offline clock; verify event ordering, zero-frame flushes, partitions, overflow and lifetime (p. 446). |
| M2 | Share 91 continuously running sources and reviewed maps; never restart source phase on a note event (p. 446). |
| M3 | Preserve contact trajectories, all retained banks, routing-only Cancel and shared percussion recharge; a behavioral surrogate remains replaceable (p. 447). |
| M4 | Qualify the nominal scanner topology and all signed outputs independently, retaining return ownership and transition/state checks (pp. 447, 465). |
| M5 | Select and independently trace a complete AO-28 graph, then loaded linear/nonlinear behavior and the dry G-G boundary (pp. 448, 458, 488). |
| M6 | Preserve separate 122/147 identities, amplifier/loading and floating A-H treble versus W-B bass ports (pp. 448, 460, 466). |
| M7 | Give horn/drum independent trajectories but common state across microphones; assign each delay/filter one owner (pp. 449, 467). |
| M8 | Acquire identified captures, fit upstream first, hold out entire conditions and predeclare uncertainty-aware criteria (pp. 449, 455, 484, 490). |
| M9 | Qualify actual adapters, state, UI, native devices/hosts, dependencies and distribution separately (pp. 450, 456, 485, 492). |

Page 450 explicitly permits early adapter smoke work after M1/M2 and requires
one shared engine across offline, VST3 and standalone surfaces. Page 454 says a
missing acquisition blocks its associated claim, not unrelated reversible work.
This supports the selected independent standalone session while scanner work
continues elsewhere. It does **not** mean that an early standalone closes M9 or
that dry output now includes the scanner, AO-28 or Leslie.

## Concrete standalone implementation requirements

| Area | Requirement for this session | Atlas basis |
| --- | --- | --- |
| Engine ownership | One audio owner mutates the Engine. UI and accessibility code consume bounded copied snapshots. No view enters live DSP objects. | 425, 437, 453, 489 |
| Musical transport | Give commands bounded publication and acknowledgment. Telemetry may report dropped packets; musical note releases must not disappear silently. Specify overflow recovery before implementation. | 425, 442, 453 |
| Callback scope | Allocate, load files, parse state, format text and destroy resources off callback. Qualify actual processing, including error paths; a smooth meter or average CPU reading is not a deadline test. | 425, 453, 461, 485 |
| Keyboard ownership | Capture the original note/manual on key-down, ignore repeat and release that original record on key-up. A manual or octave change while held must not redirect the release. | 434 |
| Focus and close | Internal focus movement and resize preserve owners. Window deactivation/close releases UI-owned audition/playing notes; an eventual independent MIDI owner must remain intact. Panic and historical Cancel stay distinct. | 433-434, 436, 438, 442 |
| Drawbar identity | Bind by permanent manual/bank/footage identity. Editing an inactive bank must not route it. End the captured gesture before rebinding a bank. | 428, 433-434, 440-442 |
| Drawbar resolution | The atlas's 0.1/0.01 increments are proposed input behavior. The current core accepts discrete 0-8 positions; expose that implemented resolution honestly until a separate continuous model exists. | 434; current control contract |
| Parameter compatibility | The book's proposed 62-entry registry is not the current implementation's public registry. Preserve the current 45 IDs and state formats; no renumbering from screen order. | 442, 450, 452, 468 |
| Persistence | Serialize copied musical controls through the existing format. A preset is not a DSP checkpoint: it must not resurrect notes or reset continuous source state by accident. Parse/validate completely before activation. | 424, 450, 453 |
| Lifecycle | Stop or otherwise prove serialized ownership before rate/device/graph changes. For this scope an explicit stopped rebuild is preferable to an unqualified live graph-swap path. | 424, 453, 485, 489 |
| Output claims | Display the active nominal profile and actual device/backend state. Unimplemented scanner/cabinet controls must not imply active sound processing. UI illustrations and generated styling carry no physical-fidelity claim. | 421-426, 429, 437, 451 |
| Reproducible build | Pin the selected SDL source/version and notices; verify actual artifact contents and supported configurations. Existing VST3 permission does not automatically license another dependency, font or image. | 456, 478-480 |

The production callback should not depend on a future inspector or graphics
renderer. If a profile editor is added later, pp. 424/426 require active immutable
identity, separately versioned drafts, obsolete-result rejection and activation
acknowledgment. A selected component or camera view is UI state, not automation.

## UI design and scope

Use charcoal surfaces, restrained brass accents and warm wood styling as original
product appearance. Put operational labels on opaque plates so grain, reflections
and lighting cannot obscure them (pp. 429, 431, 435). The actual page-434 study
shows the distinction between all four retained banks, a routed bank, the two
manuals, playing keys and the separately grouped pedals. That relationship is
useful even if the standalone displays one bank editor per manual.

All visible controls need readable labels, ranges, selected/focused cues and
keyboard equivalents. Keep edited bank, sounding route and keyboard focus
distinct. Pointer geometry and hit testing must use the same scaling transform;
resize must not select a bank or cancel notes (pp. 433-436). Do not copy the
book's continuous drawbar controls, preset options or cabinet controls as if
their full DSP already exists.

The atlas calls for a complete flat operating path and reduced nonessential
motion, not a fallback error screen (pp. 431, 437). A static SDL instrument is a
valid starting surface; decorative rotor motion would be misleading while no
rotary audio state is connected. Device failures and command rejection need
persistent readable status, without moving focus or announcing every meter
update (pp. 425-426, 437).

**Native accessibility remains a separate gate.** Pages 433/438 explicitly say
that web ARIA-like names or keyboard operation do not establish native platform
accessibility. A custom SDL canvas needs a semantic platform bridge and actual
assistive workflows before claiming screen-reader qualification. This session
can verify keyboard access, readable focus and layout while retaining that
limit. Atlas contrast and scale targets are design requirements, not evidence
that the eventual colors or each OS scaling combination have passed (pp. 435-438).

## Acceptance to freeze before implementation

1. Run the same canonical musical fixture through the standalone callback
   adapter and core/offline path, documenting any explicit output conversion.
   Keep exact source/profile/tool identities and partition schedules (p. 450).
2. Exercise key repeat, manual/octave changes while held, pointer/keyboard
   overlap, Cancel/reselection, deactivation and close. Verify original-owner
   release and absence of stuck notes (pp. 434, 438, 441-442).
3. Drive the real bounded command transport to capacity, including a pending
   release. Show its declared recovery and counters; UI stalls and telemetry
   saturation must not become audio waits (pp. 425, 442, 461).
4. Compare save/load of all retained banks and pedals; reject malformed or
   obsolete state without partial activation. Distinguish controls from
   transient notes, contacts, phase and percussion history (pp. 424, 450, 485).
5. Inspect actual native screenshots at declared window sizes and scale factors,
   then exercise real pointer/keyboard dispatch. A software-rendered frame or
   test-double event is useful but has a narrower scope (pp. 436, 438, 443, 485).
6. Exercise actual open/start/stop/close and supported rate/buffer changes with
   the selected backend. Dummy audio verifies only that backend's callback
   behavior; it does not establish a physical device, acoustic output, xrun-free
   performance or round-trip latency (pp. 450, 461, 485).
7. Retain callback allocation/concurrency evidence and named workload timing,
   including setup and unsupported paths. Keep unresolved native accessibility,
   hardware/device, signing and release requirements visible (pp. 456, 485-486).

These are proposed acceptance tasks for later assignments, not results of this
reader. The baseline's retained 77-suite scanner checkpoint belongs to its named
revision and cannot certify newly written standalone code.

## What the next agent should do

Freeze the standalone command/acknowledgment/lifecycle interface before writing
the SDL renderer. Reuse `Engine`, canonical performance-input ownership,
`ControlSnapshot`, parameter descriptors and existing control serialization.
Define original-key ownership, device shutdown and queue overflow explicitly.
Then implement the adapter, independently verify its callback behavior, add the
instrument window and persistence, and run the scoped acceptance above.

Keep source-model progress separately actionable: complete scanner numerical
policy before routing it into the active instrument; independently trace AO-28
connectivity and qualify the dry boundary before integrated cabinet fitting
(pp. 448, 458, 488, 492). Physical acquisition, actual device/host evidence,
semantic accessibility, asset/dependency rights and signed distribution remain
their own tasks. Every completed task retains exact inputs, changed paths,
executed commands, outcomes, failures and the next dependency (pp. 450, 486, 492).

## Checks and limits of this note

Executed: full text reading, selected original-page rendering/inspection, source
SHA-256 check, checkout/status inspection and owned-note whitespace/link checks.
No cited external primary source was independently reverified in this assignment;
the eight-page source directory was read as navigation, not as retrieved content.
No code test, native device, screen reader, UI interaction, dependency-license
qualification, physical measurement, commit or push is claimed here. Root owns
shared status, assignment acceptance and publication.

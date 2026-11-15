# Contact measurement requirements: independent review

**Disposition: suitable for the specimen-lock and pilot-planning step, with the
pre-pilot conditions below.** This is a review of requirements, not admission of
acquired data, a contact fit or hardware fidelity. No specimen is identified and
no measurements were supplied. A42 reviewed
[the proposal](../CONTACT_MEASUREMENT_REQUIREMENTS.md) at SHA-256
`3d0e73d69bb21df5e615e14def22b34a6724293eda98c5235af3b46811a53190`,
against the current capture contracts and implementation on 15 November 2026.

## 1. Documentary route and scope

Both retained independent [factory readings](../FACTORY_REFERENCE.md) and the
nominal profile agree on the two proposed routes:

| Route | Factory cells and profile lookup | Result |
| --- | --- | --- |
| Upper playing key 25, d3/8-foot | CSV row 25, `d3`; profile `[24][2]` | Source 37 |
| Lower playing key 37, d1/16-foot | CSV row 37, `d1`; profile `[36][0]` | Source 37 |

The project's manual MIDI base is 36, so Upper index 24 is MIDI 60. These
identities corroborate documentary routing; neither transcription identifies a
particular instrument's terminal or proves its present wiring. The proposal
correctly requires technician verification, maintains separate manual networks
and treats A+B residuals as potentially involving loading or downstream
nonlinearity. The same-source control is useful only after those actual routes
and recording conditions are locked.

The acquisition order follows [M0–M3](../PLAN.md) and the
[A02 atlas reading](../development/2026-11-15-execution-continuation/notes/A02.md):
identify the instrument and boundary, observe independent contacts and free-running
source phase, then assess electrical prediction. The existing synthetic study
cannot supply bounce, resistance, mechanical timing or specimen variability.
The proposal states this boundary correctly and does not change the nominal
Engine, numerical thresholds or capture schema.

## 2. What capture v1 can represent

Twelve simultaneous signals fit the sixteen-channel bound. A raw common-clock
voltage stream can contain nine contact observations, travel-sensor voltage,
source reference and dry audio. Under [capture v1](../CAPTURE_FORMAT.md), sensor
channels use their actual electrical boundary and `V/FS` calibration. Millimetres,
contact state and normalized travel are calibrated derivatives; they are not new
raw-channel units. The proposal's support records can carry the sensor conversion,
mechanical influence, polarity and uncertainty evidence without changing v1.

`derived/contact-events.csv` can be a derived artifact with local raw parents and
the required operation, tool, version and parameters. The corpus's audio audit
does not parse this event table: a derived artifact without a `derived_audio`
descriptor is reported as not inspected for audio. Byte integrity and valid
ancestry therefore do not validate event detection. CSV/video originals on their
own clocks remain external reviewed evidence. Cross-manifest relationships need
the corpus records; v1's local parent IDs cannot express them alone.

## 3. Conditions before the pilot is admitted

1. **Verify an actual recorder file before acquiring the main schedule.**
   `capture_audio.py` accepts RIFF WAV tags 1 and 3 with the declared PCM/float
   widths and a 16- or 18-byte `fmt` payload. It rejects WAVE_FORMAT_EXTENSIBLE
   and unsupported containers. A generic WAV declaration or twelve available
   channels does not establish decoder compatibility. Retain the untouched pilot
   file and its inspection result. If unsupported, preserve the original and
   resolve the decoder/contract gate; an analysis conversion does not qualify
   raw-file inspection. Preflight actual rate, channel count, width and duration
   against the 256 MiB artifact and 512 MiB manifest bounds. Do not lose contact
   history at recorder-native chunk boundaries.
2. **Freeze event interval meaning before analysis.** Add an event-table data
   dictionary naming raw artifact/channel IDs, source frame interval, common time
   origin, clock/sensor correction references, detector thresholds/hysteresis and
   parameters. Define whether each interval is a deterministic detection bracket
   or a stated-coverage uncertainty interval. Keep phase wrapping, interval
   overlap with bin boundaries, unresolved/repeated transitions and exclusions
   explicit. These details complete the proposal's interval-valued approach;
   they are not an already implemented event schema.
3. **Freeze whole-group assignments before fitting.** `capture_corpus.py` joins
   equal session/group IDs, declared gesture/family labels, ancestry and relevant
   artifact identities. Shared specimen IDs or support files alone do not join
   records. Related chunks, synchronized recorders and derivatives must remain
   together; a changed session label cannot establish independence. The existing
   [acquisition sequence](../CALIBRATION_NEXT_ACQUISITION.md) supplies this rule.

The proposal already requires chain response, noise/overload, DC preservation,
sensor latency/skew, mechanical influence and correlated phase/timing uncertainty.
Its phase-bin and repeat counts remain pilot proposals: unresolvable bins remain
inconclusive. Before admission, the responsible reviewer must confirm that these
quantities were actually measured over the declared bandwidth and validity
interval, with physical boundary and receiving load unchanged or explicitly
versioned. No numerical uncertainty values are available to approve now.

## 4. Next artifact and verification boundary

The next useful output is an actual specimen/configuration lock and a planned
channel/clock/file inventory, followed by the qualified external pilot. The
contact pilot proceeds only where the approved interface permits it. No powered
circuit procedure is supplied by this review.

Verification here was source/document inspection and direct comparison of the
four CSV cells with two profile entries. No acquisition, hardware operation,
runtime experiment, build, broad test suite or publication was performed.
The two CSVs each retain SHA-256
`23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6`;
the profile retains
`d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff`.
The reviewed audio and corpus implementation hashes are
`f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216`
and `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8`.

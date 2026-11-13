# Assignment 01: atlas foundations, pages 1-84

## Identity, ownership, and actual coverage

- Worker: `/root/w01_a01_atlas_foundations`.
- Session: the new `2026-11-13-next-phases` session; no earlier worker is counted.
- Inspected repository HEAD: `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`.
- Inspected tree: `51fd7b24d2f373a693ced8dbde0fba762a3cc434`.
- Owned output: this note only. No production code, shared status, or historical
  ledger was edited. No commit or push was performed by this worker.
- Complete text coverage: inclusive PDF pages **1-84**, including front matter,
  all contents pages, and chapters 1-12. Actual page images **4 and 49** were
  rendered and inspected. This does not assert independent review of every
  photograph, external source, or component diagram.
- Preserved PDF SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

The atlas supplies an evidence contract and an implementation program. It does
not supply measurements of a newly acquired reference instrument. Page 2 states
that limitation expressly. Historical claims about companion JSON, code, or
research results remain source claims until their actual files and evidence are
present and independently admitted.

## What this portion of the book requires

| Pages | Requirement and consequence |
| --- | --- |
| 2-5, 12-18 | Identify a vintage B-3, its AO-28 revision, and a vintage Leslie 122. Keep 147 and modern organs distinct. M0-M9 is the implementation order; ten research waves and a session's agent waves are different counts. Behavioral, specimen/audio, visual, and deployment claims each need their own evidence. |
| 14-16, 21-24 | A physical value carries units, evidence class, revision/applicability, source location, uncertainty, and replacement/acquisition task. Unknown is not zero. Compile documented connectivity before fitting sound. A new model is a reconstruction, not recovery of absent companions. |
| 4, 26-29, 43-48, 61-66 | Tone sources belong to the persistent instrument. Electrical source ID, terminal, storage index, shaft, tooth count, and musical pitch are distinct. Shared routes reuse the same source sample and phase. A note does not restart rotation. |
| 31-36 | A cabinet model requires a geometry ledger. The documented furniture-inclusive footprint is not a bare-console bounding box. The read-only scene cannot own audio timing; hiding a panel or stalling rendering cannot change sound or saved musical state. |
| 37-42 | Each of 122 playing keys has nine contact states. MIDI initiates a declared surrogate trajectory unless real continuous position is supplied. A single C-3 specimen's dimensions do not establish universal B-3 travel. |
| 49-54 | Preserve four independent nine-drawbar manual banks and two pedal controls. Selection, bank contents, wired presets, and software snapshots are separate. Global Soft differs from percussion Soft. Great scanner enable includes pedals. Nine marks are an approximation to continuous electrical contact travel. |
| 55-60 | Leslie family, amplifier, driver, geometry, and motion identities remain separate. Horn and drum have independent state. Stationary transducers and rotating acoustic channels must not be conflated. A modern servo cabinet's speed behavior is not vintage 122 evidence. |
| 67-72 | Separate induced pickup voltage, loaded terminal voltage, and magnetic/geometry hypotheses. Nominal sine, terminal Fourier coefficients, and flux-linkage coefficients are distinct source representations. Units and the filtering boundary must travel with the profile. |
| 73-78 | Early generator filters and the 1965 bulletin are separately identified variants. A post-filter capture must not be filtered again. Steady harmonic-domain voicing is valid only for periodic sources, linear fixed networks, and fixed loads. |
| 79-84 | Leakage is a sparse, explicitly located transfer model, not automatically noise or adjacent-semitone coupling. A terminal recording may already contain it. Shared source reuse, signed complex transfer, dry observability, and held-out physical data remain necessary. |

The visually inspected page 4 is expressly a responsibility map, not factory
connectivity. Its organ, cabinet electronics, rotating paths, and microphone/room
boundaries support separate test harnesses. The page 49 control table confirms
semantic drawbar ordering and the 36-plus-2 count; its stage-lit photograph is
appearance/context evidence, not dimensional or calibrated-color evidence.

## Recommended independent next slice

**Recommended from this reading: a prepared pickup-waveform and steady-voicing
research module, followed by its separately reviewed optional generator
integration.** This is a remaining M2 engineering capability on pp. 67-78. It
does not depend on the concurrently developed scanner implementation, a new
graphical framework, or invented AO-28/Leslie component data.

The module should accept a versioned, explicitly synthetic/unmeasured profile
with a declared source boundary and either terminal-voltage Fourier coefficients
or flux-linkage coefficients. Preparation validates identities, units, phase
origin, coefficient count, finite values, frequency limits, and any filter
ownership before producing bounded immutable data. Runtime evaluates it using
the existing shared phase, with no file access, allocation, logging, or extra
oscillator per note. A plain sinusoid remains the unchanged default.

For a flux-linkage representation, page 69 gives the useful independent identity
`E_l = -j*l*omega*Lambda_l`. The derived output has a different physical meaning
from a normalized terminal-voltage table. It requires actual mechanical tooth
counts/phase relationships before being advertised as a specimen representation;
synthetic mechanical fixtures can test the mathematics without inventing that
missing production graph. A first slice can therefore implement terminal Fourier
evaluation and analytical flux fixtures in isolation while keeping real mechanical
integration pending.

If filters are included, page 76 permits multiplying a source harmonic by
`H(j*2*pi*h*f)` only under declared stationary, linear, fixed-load assumptions.
Preparation must reject double filtering of post-filter coefficients. Changing
load, startup, and rate/tuning transients need separate stateful evidence and
must not inherit the steady-state claim.

### Proposed engineering exit evidence

These are recommended acceptance obligations, not tests executed by this note
and not claimed Hammond factory tolerances. Freeze the actual numerical budgets
before grading the implementation.

1. **Compatibility:** existing profile bytes, public controls, saved-state
   migrations, UUIDs, and the default sine arithmetic remain unchanged until a
   separately identified integration. Replay retained legacy renders and compare
   actual PCM, not only reported peak/RMS values.
2. **Analytic amplitude and phase:** independent sine/cosine and complex-coefficient
   oracles check DC, one harmonic, signed phase, several harmonics, and exact zero
   input. Flux fixtures check the derivative sign, zero output from constant flux,
   and speed-dependent amplitude under the stated open-circuit model.
3. **Boundary correctness:** post-filter coefficients bypass any additional
   generator voicing; a raw-source/filter fixture matches a separately warmed
   stateful reference at fixed load. Reject absent units and incompatible
   representation/filter combinations before activation.
4. **Shared persistent history:** both manuals and pedals consume the same source
   field. Silence, contact release, preset changes, and host block partitioning
   never restart source phase. Compare actual samples and diagnostics.
5. **Bandwidth:** declare the internal-rate margin and retained harmonics;
   independently compare high-frequency and multi-harmonic output to a higher-rate
   reference with a declared reconstruction/filter. Report failed bins and
   convergence limits instead of fitting away gain or phase error.
6. **Failure and lifecycle:** reject malformed, oversized, nonfinite, duplicate,
   wrong-unit, and unsupported-rate input atomically. From nonzero history,
   rejected preparation or control changes leave subsequent state/output
   equivalent to an untouched clone. Prepared swaps stay outside processing until
   a bounded publication/retirement design exists.
7. **Runtime:** bound memory and sample work, use a calibrated allocation probe,
   and retain actual scoped evidence. A zero-allocation result is not an audio
   deadline or device qualification.
8. **Evidence and handoff:** every exported test render names the code/profile,
   source boundary, sample rate, reconstruction/filter policy, and synthetic
   status. Physical pickup/filter/leakage calibration remains pending measured
   captures and identified specimen applicability.

## Other parallel options and their boundaries

A standalone adapter is also dependency-ready as a scoped nominal-product
experiment because stable core/parameter/state interfaces already exist. Its
acceptance must exercise an actual device lifecycle and control thread handoff;
a window or an offline WAV command alone does not establish standalone playback.
The wider product chapters are assigned to other readers in this wave.

A rotary-acoustic research module can proceed independently if its two inputs
explicitly represent separate horn and bass radiation excitations, with units
and effect ownership declared. Pages 29 and 55-60 support separate motion,
distance/directivity, cabinet identity, and geometry. It must not quietly add an
arbitrary pitch LFO on top of propagation delay or call a generic split of the
current dry organ a validated 122. Complete dry-organ validation precedes cabinet
fitting; isolated synthetic geometry and motion tests are a narrower claim.

Do not duplicate the active scanner task or turn its retained same-hertz failures
into a pass by changing a status label. At this inspected baseline,
`docs/NEXT_STEPS.md` and `docs/SCANNER_HANDOFF.md` retain that open numerical gate.
This assignment did not run scanner, native, or full-suite tests.

## Actual inspection commands and limits

Working directory for repository commands:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

Read `AGENTS.md`, the plan and operational documentation, current status/next
steps, the atlas review, and the latest development-log material. Commands
included `cat`, `sed`, `git rev-parse HEAD HEAD^{tree}`, `git status --short`, and
`sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf`. The source tree was clean
at the identity check. Later independent workers may add their owned notes.

Read every line of the coordinator's page-labeled extraction at
`/workspace/scratch/5ba97739b54c/atlas/part1.txt` using these complete ranges:
`1-280`, `281-1050`, `1051-1800`, `1801-2550`, `2551-3300`, `3301-4050`,
`4051-4800`, and `4801-5012`. An earlier combined tool result was truncated;
the affected atlas range was reread in a separate bounded result before claiming
coverage. No text page was omitted on the basis of repeated layout or boilerplate.

Rendered pages 4 and 49 with `pdftoppm -f <page> -l <page> -r 90 -png
-singlefile` into task scratch and inspected both PNGs with the image-view tool.
Those renderings remain inspection intermediates; the original PDF is unchanged.
No external paper, scan, patent, photograph license, physical instrument, audio
device, or product build was newly verified in this assignment.

# Assignment 06: fresh atlas plan, acceptance and release review

## Identity and actual coverage

- Session `2026-11-13-scanner`, wave 1, assignment 06 of 60.
- Worker `/root/w01_a06_atlas_closure`; owned change is this note only.
- Starting commit `6dc0702d5473912268e8af8f852b9b9984198ef3`, tree `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.
- Source: [the unchanged atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), 500 pages, 21,248,265 bytes, edition 12 November 2026.
- Freshly observed SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- **Fresh complete text reading: every page 421-500 inclusive, 80 pages.** These cover chapters 069-080 and all eight source-directory pages. An initially truncated combined output was recovered by separately rereading pages 424-425; subsequent complete six-page and four-page batches avoided omissions.
- **Actual visual inspections: pages 428, 447, 465 and 486**, rendered at maximum dimension 1,500 pixels and opened with the image viewer. Other pages were read as text. This does not claim that every figure or referenced external source was independently examined.

I read `AGENTS.md` and the current README/status/next-step/handoff/plan/research-review entry points and latest development-log excerpt. The integrator's new scanner status pointer appeared during this read; concurrent shared-document changes were preserved. No earlier session's reader identity or result is counted as this assignment.

## Whole-project plan and concrete next scope

The atlas specifies an inspectable core serving an offline renderer, VST3 and standalone product, ultimately calibrated to an identified vintage B-3/AO-28/Leslie 122 reference. Milestones M0-M9 govern implementation, whereas the book's ten research waves organize its chapters. The current sixty-assignment session is a third, independent work organization. Neither page coverage nor assignment count establishes product completion. [pp. 445-456, 481-492]

| Milestone | Required engineering progress and distinct exit |
| --- | --- |
| M0 | Versioned reference identity, variants, units, provenance, assumptions and acquisition queue; keep proposed and measured profiles separate. |
| M1 | Prepared immutable data, bounded runtime/event ownership and reproducible offline clock/rendering; execute partition, flush, overflow and lifetime checks. |
| M2 | Ninety-one shared continuing sources with distinct source, terminal and MIDI identities; verify routing, null contacts and phase continuity. |
| M3 | Ordered contacts, retained registrations, presets, percussion recharge and expression interfaces; preserve held-note state and routing-only Cancel. Physical timing/loading remains independently qualified. |
| M4 | Reviewed connected scanner line, shared scanner history and six modes; same-load independent numerical comparisons, transitions and stability evidence. |
| M5 | Revision-specific connected AO-28, loaded linear/DC reference before nonlinear stages, and direct G-G validation before cabinet fitting. |
| M6 | Selected Leslie electrical chain, coupled load and signed floating crossover ports; retain 147 separately from 122. |
| M7 | Independent horn/drum motion, causal paths and microphone pressure output, with each propagation/filter/room effect owned once. |
| M8 | Immutable calibrated captures, upstream-first fitting and whole-group holdouts; predeclared uncertainty-aware physical and listening decisions. |
| M9 | Actual native hosts/devices, state and automation, accessible dimensional/flat UI, reproducible packaging, rights and platform release evidence. |

**Nominal scanner numerical work is dependency-ready without pretending physical M3 is complete.** Page 447 explicitly permits M3 behavioral fixtures and M4 numerical work in parallel once M2 routing and port conventions are fixed. Pages 451, 454 and 457 permit named substitutes while physical acquisition proceeds, provided every approximation retains assumptions, omitted interactions and a replacement gate. This supports the integrator's graph -> independent reference -> prepared runtime sequence while preserving the existing dry engine and its 45 stable control identities.

For this session, implement and qualify the nominal scanner at named ports before advertising it as a production-integrated, measured scanner. Runtime integration must declare its source-to-voltage scale and loading boundary. The source supplies no universal physical error threshold; unknown losses, coupling and loading remain unknown. [pp. 452, 459, 483-484, 489-490]

## Scanner acceptance requirements from the closing chapters

1. **Exact circuit and observation identity.** The documented nominal network has 18 LC sections, 50 passive elements and 19 ground-referenced outputs. The first six outputs are divider midpoints; outputs 7-19 are `p6..p18`. Nine selected terminals and sixteen scanner positions are separate domains. A graph-count or array-shape check cannot establish correct connectivity. [pp. 447, 465, 481, 487]
2. **Common return occurs once.** With `v_k = r + z_k`, normalized scanning of ground-referenced taps already contains the common return. An additional arbitrary dry term duplicates it. An unloaded tap crossfade is an explicit approximation; moving coupling capacitance follows `d(Cv)/dt`. [pp. 465, 489]
3. **Independent numerical formulation.** Reproduce the admitted nominal network independently, then compare the production time-domain implementation at comparable ports, loads and frequencies. Declare bilinear frequency warping instead of silently comparing unlike analog/digital frequencies. Test all nineteen signed transfers before amplitude normalization. [pp. 447, 465, 483]
4. **Physical state and tails.** Follow static response with migration, complete tails, demanding valid parameters, block partitions and rate changes. Preserve state when topology changes. Zero-frame control flushes do not advance physical clocks. A successful stationary AC solve does not establish stable integration or moving coupling. [pp. 453, 465, 483, 485]
5. **WDF-specific corrections remain applicable if that formulation is selected.** The visibly inspected page 465 records `M = I - Phi*S11`, the ordering of the root elimination, convention-dependent source/open/short signs, negative previous incident wave for an inductor and positive for a capacitor. Prewarp uses angular frequency `2*pi*f0`; a printed hertz/radians mismatch must not enter an implementation. These are the atlas's independent corrections, not author-issued errata. A physical-state solver still needs its own derivation and checks. [pp. 463, 465]
6. **Criteria precede grading.** Retain each result's implementation, data, profile, setup, metric, bound and reviewer. A threshold selected after observing validation is a revised study, not a retroactive pass. Small numerical residuals support only the declared model. Physical thresholds require calibrated uncertainty and held-out evidence. [pp. 481, 483-486]

The next evidence after numerical admission is stationary tap/return response with identified drive and load, followed by angular coupling and all six modes. Chassis, scanner revision, winding loss, actual loading, scale, timing, calibration and raw/derived ancestry are separate acquisition fields. [pp. 455, 459, 490]

## Complete chapter digest

| Pages / chapter | Findings retained for future implementation |
| --- | --- |
| 421-426 / 069 | SERVICE reports exact assembly/profile/model/evidence status. Compare traces only when ports, units, timing, calibration and analysis agree. Draft edits differ from active immutable profiles; stale worker results cannot activate. UI consumes bounded timestamped snapshots and can lose telemetry without losing musical events. |
| 427-432 / 070 | Geometry and artistic styling retain separate provenance. Stable mesh IDs cannot be array order or host parameter IDs. The inspected coordinate conversion `(x,y,z) -> (x,z,-y)` preserves handedness. GPU resources, cameras, material/LOD choices and decorative motion cannot own audio clocks. Proposed meshes/budgets are unproduced and unmeasured in the atlas. |
| 433-438 / 071 | One semantic model serves dimensional and fully usable flat controls. Native accessibility needs actual platform interfaces and tasks; web labels or screenshots cannot qualify it. Bank visibility differs from host automation visibility. Keyboard ownership, scale, reduced motion and native host shortcuts each require execution evidence. |
| 439-444 / 072 | The book reports 28 JavaScript state checks using limited test doubles, with browser execution blocked in that research session. These absent companion artifacts are not this checkout's tests. Preserve original bank/gesture ownership and distinguish layout illustrations from actual screenshots. |
| 445-450 / 073 | Complete M0-M9 order; M3 and M4 can proceed in parallel under fixed source/port contracts. Independent AC checks precede physical scanner claims. Close the dry organ before compensating through cabinet models. Early adapter smoke tests do not close M9. |
| 451-456 / 074 | Build, prove and disclose. Strict typed compilation includes meaning and cross-file ownership, beyond JSON shape. One mutable audio owner and explicit retirement protect resources. Every milestone hands over exact versions, commands, results, remaining uncertainty and next work. |
| 457-462 / 075 | Unknown physical inputs block the affected claim, not a named synthetic fixture. AO-28 placement lists are not connectivity. Acquire source/console/scanner/dry evidence before cabinet fitting. Do not repeatedly reopen resolved documentary corrections; identify the actual residual question. |
| 463-468 / 076 | Corrected source/terminal maps, scanner count/polarity/WDF algebra, AO-28 variants, floating Leslie treble port and acoustic timing retain distinct source/model scopes. Project-derived corrections are not author errata. Runtime and physical acceptance remain separate from mathematical references. |
| 469-474 / 077 | Eighty-eight acquisition task families do not mean 88 images. Each accepted image has a defined claim: identity, topology, geometry, appearance, condition or timing. Retouched context art cannot resolve hidden geometry. Masters, derivative ancestry, permission and independent interpretation remain distinct records. |
| 475-480 / 078 | Reproduction permission and engineering authority are independent decisions. Asset-specific licenses, alterations and exact bytes matter. Do not include whole source manuals because an individual image is reusable. The atlas's historical packaging checks do not qualify this repository's later builds or release. |
| 481-486 / 079 | Passes belong to one versioned claim and boundary. Keep documentary, numerical, production, physical and release tiers distinct; preserve failed, blocked, inconclusive and not-run outcomes. Grids/bounds/setup must precede grading and changed inputs trigger only affected requalification. |
| 487-492 / 080 | The research handoff contains no measured instrument or finished plugin. A component registry cannot become a graph by sorting designators. The compiler owns variant/unit/port/effect admission before prepared publication. Acquire intermediate boundaries and reserve full conditions before fitting. |
| 493-500 / source directory | Read every source-title/category/ID entry. The directory distinguishes factory manuals, patents, photographs, papers, official APIs and rights/metrology sources. Locators and relevance are navigation evidence; listing a source does not establish fresh access or independent corroboration. The DAFx scanner paper is indexed on p. 495. |

## Standing handoff implications

Keep the original PDF and earlier evidence unchanged. Every later worker should read current status and next steps, own a bounded task, name the required source/algorithm inputs and acceptance evidence, run relevant checks, retain failures and limitations, and provide concrete next dependencies. The integrator updates shared status, next steps, development log and contracts before publishing authorized completed work. A reference change invalidates affected results; it does not erase prior observations. [pp. 450, 454, 456, 481, 486, 492; repository `AGENTS.md`]

A useful end-of-session handoff can therefore report a nominal graph/runtime and independently qualified software behavior, while leaving Engine/native integration, measured coupling, AO-28, Leslie, calibration and product gates precisely scoped. It must not use sixty completed assignments as the meaning of a completed instrument.

## Executed checks and limits

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.

Commands actually run:

```sh
cat AGENTS.md
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
pdftotext -f 421 -l 432 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 424 -l 425 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 433 -l 438 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 439 -l 444 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 445 -l 450 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 451 -l 456 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 457 -l 462 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 463 -l 468 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 469 -l 474 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 475 -l 480 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 481 -l 486 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 487 -l 492 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 493 -l 496 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 497 -l 500 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
git diff --check
```

A Python loop invoked `pdftoppm -f PAGE -l PAGE -scale-to 1500 -singlefile -png Hammond_B3_Leslie_Research_Atlas_500pp.pdf /tmp/hammond-a06/pagePAGE` for pages 428, 447, 465 and 486. All four generated PNGs were opened and inspected. Temporary render files are outside the repository. Python `Path.read_text()` supplied the current context excerpts described above.

Source identity and page count matched; text extraction/rendering succeeded and all assigned pages were read. No external primary source, original missing companion, model implementation, CTest suite, device, DAW, hardware measurement, commit or push was executed by this assignment. The root integrator owns acceptance, publication and shared handoff consolidation.

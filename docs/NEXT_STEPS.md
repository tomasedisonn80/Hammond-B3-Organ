# Next steps

## Current checkpoint and ownership

The original session's first development phases, retained demo and final code
repairs are published in `61c6ecbd87f46a91b4d0d975c823eeae2e2fb3f8`.
All sixty original workers have completed their assignments in ten waves of six.
The final session record retains their reviews and current handoff. Read [STATUS.md](STATUS.md), the
[assignment ledger](development/AGENT_LEDGER.md) and
[operational handoff](SESSION_HANDOFF.md) for the latest completion and verification.

The next product milestone is **M3 console integration**. The separate
[console continuation](development/2026-11-13-continuation/README.md) already owns
engine, persistence and renderer integration. Its preserved `7a24a30` checkpoint
supplies `ContactBank`, `PercussionState`, `ConsoleModel`, independent component
tests and the metadata exporter. Inspect its newest ledger, current remote head
and actual source before claiming a task; select an uncovered acceptance gate
within that work rather than starting another implementation of these modules.

## First dependency-ready engineering task

**Integrate the existing contact and shared-percussion components into the
prepared engine, then verify the complete event-to-audio history.** Read atlas
chapters 17–24, [console dynamics](CONSOLE_DYNAMICS.md),
[the M3 acceptance contract](M3_ACCEPTANCE_CONTRACT.md),
[engine API](ENGINE_API.md) and [control-state format](CONTROL_STATE_FORMAT.md).
The nominal source profile and historical demo remain immutable inputs.

| Step | Affected boundary | Required acceptance evidence |
| --- | --- | --- |
| Reconcile active ownership and revision | Continuation ledger, current `main`, actual Engine/Types/control/renderer code | Identify the exact remaining integration gap and preserve all intervening commits and local work. A contract describing an API is not evidence that the API exists. |
| Connect the prepared console model | `Engine::prepare`, fixed contact storage, source routing | Preserve legacy ideal defaults and the two-argument preparation behavior. Validate/copy the complete model before replacing prepared state; invalid models leave state unchanged. Keep file access, allocation and publication outside processing. |
| Render contact trajectories | Physical-key targets and all nine manual routes | Independent contact identities; render-current-state-then-advance timing; stable same-frame event order; partial holds/reversal; no phase reset or velocity-dependent steady gain. Compare complete audio and state across block partitions and supported sample rates. |
| Connect one shared percussion state | Upper-manual detector, eligibility, harmonic source routes, sustained routing | Shared readiness and finite recovery, held-key and release/repress cases, upper-B selection, Cancel/reselect, disabled controls and lower-manual isolation. Reuse the existing continuously running sources; retain explicit nominal parameter identities and limits. |
| Extend timed controls and saved state | Event preflight, snapshots, registry, proposed `B3CONTROLS2` migration | Preserve prior IDs and source-profile identity; reject whole malformed event spans atomically. Specify and test v1 migration and complete v2 parsing before changing the writer. Keep Agent 55's exact expression round-trip and caller-rounding restoration. Never serialize key trajectories, readiness, source phases or clock as ordinary controls. |
| Extend the offline CLI and retained evidence | Renderer score/CLI, model metadata, fixtures, verifier | Keep existing ideal fixtures compatible. Retain actual selected console coefficients and controls with new renders. Create a new versioned evidence bundle; never rewrite the historical four-second demo or claim it used the new model. |
| Close the integrated acceptance gates | Independent tests, callback/partition checks, hosted matrix | Map every proposed M3 scenario to an actual test or an explicit open reason. Exercise complete event-to-audio interactions and preserved failure semantics. Run the necessary full combined suite and all configured platforms, recording exact revisions, counts and skips. |

The current `hammond_model_info` command exports compiled factory defaults. It
cannot report an arbitrary caller-edited `ConsoleModel` or a running engine's
current controls/history. A future render that uses custom coefficients must
retain that actual parameter set. Algorithm IDs alone do not identify every
possible parameter choice.

Physical preset latch behavior, pedal weighting/shaping and measured expression
remain separate M3 gates. Existing A/B selection, routing-only Cancel, pedal
mapping data and nominal readiness do not close them. Avoid solving later
scanner/cabinet sound by compensating for an unverified upstream organ model.

## Acquisition work that can proceed in parallel

Use [CAPTURE_PROTOCOL.md](CAPTURE_PROTOCOL.md) and its planned metadata example:

1. Identify the organ/generator, AO-28 revision, cabinet model/revision, condition,
   modifications and measurement permissions. Keep missing fields explicitly unknown.
2. Retain the completed [factory routing comparison](FACTORY_REFERENCE.md), then
   acquire calibrated source, contact, percussion and expression evidence at named
   boundaries. Documentary wiring agreement is separate from actual specimen tuning,
   waveform/level/phase and loading measurements.
3. Record units, loading, raw digital rate versus physical clock, calibration,
   uncertainty, rights and raw/derived ancestry. Admit real captures with the stated
   physical checks; a metadata or byte-hash pass cannot perform that admission.
4. Keep whole takes and related channels/derivatives together. Maintain an external
   corpus ledger for fitting, validation and untouched final holdouts; the per-file
   validator does not establish corpus-wide independence.

M4 scanner, M5 AO-28, M6 Leslie electronics and M7 rotary acoustics retain the
specific source/topology/acquisition dependencies in [PLAN.md](PLAN.md). Native
VST3/device audio, accessible UI, platform distribution and rights are separate
M9 gates. The [host proposal](HOST_INTEGRATION.md) supplies unrun adapter criteria,
not an implemented plugin or device application.

## Required handoff for every future agent

Follow [AGENTS.md](../AGENTS.md): inspect current code and both session ledgers,
select dependency-ready work, state its evidence boundary, execute the necessary
checks, update status/next steps/log and affected contracts, then commit and push
completed authorized work. Preserve others' commits, use an expected-head guard,
and observe the actual remote result. Retain failures and unrun gates. Workers
report to the integrator; they do not compete to rewrite shared status documents.

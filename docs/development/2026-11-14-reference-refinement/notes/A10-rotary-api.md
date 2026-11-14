# A10 — Bounded native R2/R3 API

Actual worker `/root/w02_a10_rotary_api`, wave 2. Owns this note and
`docs/ROTARY_PROPAGATION_CONTRACT.md` only; no code, commit, push or extra worker.

Inspected HEAD `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`, tree
`c37da16cedbb91573476a44bd4eafe5a5e30134a`. Read current AGENTS/scope/checkpoint/
manifest, complete PLAN, A04 acoustics review, rotary numerical/motion contracts,
both native headers and the independent reference implementation. Existing
`SamplePosition`, `PathBounds`, `PathResult`, SI profiles and statuses suffice;
the proposal adds only prepared ownership wrappers, a geometry helper and an
explicit segment-count cap.

The contract orders independent native R2 before R3. Its caller-owned immutable
span has exact canonical continuity checks, explicit coverage, startup seed,
bounded binary search and a visible lifetime obligation. Prepared paths bind
full-orbit admission to the actual seed, reuse historical trajectory queries,
return split emission positions and count every solver evaluation within 48.
No new waveform history, Engine connection or physical claim is introduced.

Source SHA-256 identities:

| Input | SHA-256 |
| --- | --- |
| `RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `rotary_reference.py` | `4c8bbcdf279f87aaad5b730d60a82958321ba3c1a92e5318eb5e37b1e83c8b0d` |
| Numerical contract | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |

Executed read-only inventory, `git status --short`, `git rev-parse HEAD
HEAD^{tree}`, source hashes, document word/link checks and whitespace inspection.
No numerical runtime test was run or gate closed. Root retains shared status and
publication ownership. A12 independently reviewed the draft with no blocking
API finding; its requested geometry-domain and negative-epoch clarifications
are incorporated. Next: freeze this API; independently qualify R2;
implement and independently grade R3 against the frozen experiments, retaining
actual error locations and failures. Current callback and R4 remain separate.

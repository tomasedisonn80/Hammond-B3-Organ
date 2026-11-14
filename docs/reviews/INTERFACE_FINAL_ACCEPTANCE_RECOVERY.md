# Final native interface acceptance — recovery review

Reviewer: actual A60, `/root/w10_a60_final_handoff`, on 2026-11-14. This is newly authored recovery prose. The original local A60 review and detailed JSON reports cannot currently be retrieved and are not reproduced here as if their bytes had been recovered.

## Decision and source

The completed native interface work and the exact recovered test-fixture repair are suitable for bounded engineering acceptance, with the remaining gates below explicit. The handoff is actionable for a developer continuing from published source. It does not establish literal 1:1 reference equality, physical Hammond/Leslie fidelity or a complete product release.

The current recovery checkpoint is [6f69c68ed5bf51d77dba1ae4f75d4bc75d144747](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/6f69c68ed5bf51d77dba1ae4f75d4bc75d144747), tree `daa6195fd3cfc4e56dd0d99b46972c68ae3c7e81`, parent `b1efcdfc34cde92e07f2f6bcb563fc12701dfc01`. A60 independently fetched the parent and recovered Python source and calculated these exact identities:

| Source | SHA-256 |
| --- | --- |
| Parent workspace replay fixture | `485de6fd6e3da49bbac1f523d4cb277557ee4b94ee1b7ce098f7188466d2cbf3` |
| Recovered qualified fixture | `0488bc549bbe4475fac8daa4f5d69c76a58db5ca7a94f1ff7e146f7ac11c0692` |

The recovered file is `apps/standalone/native_tests/test_standalone_workspace_replay.py`, Git blob `1575ea9e13584654a8c176e885dabbaf056d1e54`. The exact comparison contains seven changed paths: that fixture, `.gitattributes`, a corrected handoff argument, two navigation entries and the two root recovery records. No runtime product, CMake or workflow source changed. The product implementation remains the one published at `8673713a484c40e26ac7810c7c4cbc22fa874426`.

The [machine recovery record](../development/2026-11-14-interface-continuation/reports/root-workspace-recovery.json) and [human account](../development/2026-11-14-interface-continuation/RECOVERY.md) distinguish this published source from the unuploaded 137-file local candidate. The exact raw artifact archive is still unavailable.

## Implementation and operator contract

I inspected implementation and contracts before the interruption. Play, Rotary and Service are real workspaces over the same controls. F4, F5 and F6 select them; F7 toggles transient Flat presentation. Navigation does not recall sound or add musical commands. Existing key and pointer owners retain their original release destinations. Hidden Play controls reject new activation. Help, Audio and MIDI deliberately release UI holds; external MIDI retains its separate ownership rules.

The layout has 68 ordinary control records, including 24 reversed preset records, and 147 playing keys: 61 Upper, 61 Lower and 25 pedals. Play has 71 Tab stops because each playing-key group contributes one roving stop. Rotary and Service expose the ten common controls. These counts describe different things and should not be added together as a parameter count.

The engine contract remains 47 sound parameters, a `B3CONTROLS4` writer with readers for versions 1–3, 91 continuously running sources, four retained drawbar banks and eighteen documentary fixed registrations. Cancel disconnects a route while preserving memories and held notes. Fixed C#–A selections and adjustable A#/B routes are implemented. Editing a retained bank does not silently select it. UI presentation remains outside musical saved state. Explicit Save and live Load preserve the documented distinction between controls and transient histories.

Service has six cards and 28 read-only rows. It distinguishes copied applied state, desired pending controls, retained snapshots and unavailable observations. Unknown physical voltage, speed or dimension is not reported as zero. Rotary cabinet artwork is decorative; connected rotary audio and measured cabinet behavior remain open. These are useful inspection contracts, not evidence that the future physical models are finished. See the [operator guide](../INTERFACE_RUNBOOK.md) and [complete project plan](../PLAN.md).

## Why the macOS fixture repair is acceptable

The earlier [macOS job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43601574718/job/132467248056) failed one of 38 standalone tests at size 1399×820. Its observations went from applied sequence 5 with no held notes to applied sequence 7 with Upper 60 and Lower 60 held; sequence 6 was not sampled. At 356 ms the copied applied state was still sequence 5 although the separately observed submitted sequence was already 7. Later sequence 8 retained Upper 60 and sequence 9 was empty. This demonstrates a missing intermediate observation in that trace. It does not demonstrate lost note ownership.

The original full script remains unchanged: Upper key-down at 180 ms, Space down at 320 ms, Space up at 1600 ms, Upper key-up at 1800 ms and Save at 1950 ms, within the same 2250 ms replay. Each of the seven sizes now first executes two original prefixes for 250 ms: the nonmusical prefix before 180 ms, and the Upper-only prefix before 320 ms. They use the same exact noncanonical state and size. The first establishes a fully acknowledged origin without note commands; the second must acknowledge exactly one On, zero Off and the Upper-only owner. Neither may save or canonicalize the input.

The full run then checks each copied observation against the literal applied-command prefix: empty, Upper, both manuals, Upper, empty. It requires stages 0, 2, 3 and 4, permits only stage 1 to be absent and independently proves stage 1 in the completed prefix. It checks monotonic applied/submitted/elapsed values, resolved equals applied, bounded command sequences and the earliest possible event times. The final pre-shutdown observation must show the original +4 command delta and released state, so shutdown cleanup cannot conceal a missing release. The original 2 On/2 Off counts, view order, controls, canonical Save bytes and screenshot condition remain.

Before the outage I compared the original event construction, full native call, size matrix, state constant, unaffected assertions and timeout bounds. I also checked the producer: copied held state and applied/resolved sequence belong to one Session snapshot, whereas submitted sequence is read separately. The revised bounds respect that distinction.

A52 ran the complete six-method suite once: 30 native processes passed, 44.869 seconds inside unittest and 45.058697 seconds around the launcher, with the unchanged nine-second child and ninety-second suite bounds. I independently inspected all thirty zero-exit records, seven unchanged full scripts, fourteen exact 469-byte noncanonical prefix states and seven exact 452-byte canonical Save outputs. The application remained SHA-256 `bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`; the source-before/after record preserved 98 product inputs. Ten corrupted historical diagnostic cases and four corrupted fresh local prefix cases were rejected.

The historical macOS excerpt did not contain actual saved-state or BMP bytes, and the new prefixes were never executed on that historical host. Its retrospective review proves only old-oracle failure reproduction and the new full diagnostic-map checks. It does not prove the entire modified method passed on that host. Fresh local execution covered the complete method; new hosted execution on the recovered source is a separate gate.

These observations were completed before the environment failed. The [root recovery record](../development/2026-11-14-interface-continuation/reports/root-workspace-recovery.json) retains attribution and the result identity; the unavailable original 30-process archive has not been recreated.

## Evidence retained with its original limits

| Evidence | Accepted meaning | Remaining limit |
| --- | --- | --- |
| [500-page atlas review](../research/INTERFACE_ATLAS_REVIEW.md) | The current session's complete six-reader review and implementation synthesis are published. | Research chapters and nominal source data are not newly acquired physical measurements. |
| [Eight-image native gallery](../../examples/demos/standalone-interface-preview-v2/README.md) | Published actual native captures with source, application and pixel identities. | Dummy SDL/software rendering and equal logical/drawable size do not qualify physical display DPI or hardware. |
| [Final visual review](INTERFACE_FINAL_VISUAL_ACCEPTANCE.md) | Reference-led workspace and geometry improvements are reviewable. | Key depth, material, lighting and composition still differ; literal 1:1 is unmet. |
| [Relocatable package review](INTERFACE_FINAL_PACKAGE.md) | MIDI-on/off payloads and installed guides were qualified; the later guide refresh preserved executable bytes. | No fresh package can be rebuilt from the unavailable workspace in this recovery review. |
| [Original full gate](INTERFACE_FINAL_COHERENT_GATE.md) | Its 146 passes and one failure out of 147 executed tests remain preserved. | Later focused fixture closure must not turn that historical result into 147/147. |
| [Earlier bounded input closure](INTERFACE_BOUNDED_INPUT.md) | The earlier six-method, sixteen-process closure and 256-action burst have their own published evidence. | They are distinct from this later six-method, thirty-process macOS follow-up. |
| A57 real X11 attempt, summarized in the published recovery record | A source-identical build with a different SDL backend opened a window; click/focus navigation and an off-window-drag released endpoint were observed. | Full held-owner navigation/resize replay, capture-return counters and a retained lossless desktop image were not completed. Alt+F4 was ineffective; the 90-second SIGTERM bound joined with exit 0. |

A60 personally viewed the concept plus the v2 reference Play and minimum Service images. I did not newly inspect all eight captures. The minor Service copy “1 targets” remains deferred. The final gallery's settled controls do not itself show a pending-control state.

On `b1efcdf`, A58 observed all twelve jobs completed: eleven success and the single macOS 37/38 failure. Its focused Linux sanitizer job passed thirteen selected interface suites with ASan, UBSan and leak detection; only five were native-labelled suites. Earlier local attach failures and timeouts remain earlier results. At 14:22:24 UTC on 2026-11-14, A58 reported three successful, six running and three queued jobs for `6f69c68`. The [recovered-source standalone workflow](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228118) therefore remains pending in this dated review.

## Documentation, accounting and safe continuation

The [new recovery handoff](../INTERFACE_RECOVERY_HANDOFF.md) gives precise current counts, source identities, setup, the whole M0–M9 plan and the next dependency gates. It supersedes stale operational prose in the original handoff while retaining its historical evidence. The CLI correction is the exact token `--expected-exe-sha256`; no global prose-spacing rewrite is appropriate for identifiers or arguments.

The raw-state Git attribute is narrowly scoped to `docs/development/**/reports/**/*.b3controls -text`. Before the outage, root caught index normalization of fourteen deliberate CRLF prefix states, leaving the worktree unchanged, corrected the staging treatment and verified thirty state files plus 128 artifact hashes. The attribute is now published. The unavailable raw files are not included in the smaller recovery commit.

Root attests sixty actual dispatches in ten logical waves; the failed initial A59 spawn is excluded. A59's completed audit checked the actual session mapping and 57 accepted note identities at its observation point. Names are unique within this session; some names recur in historical sessions. The completion checker establishes consistency of retained records and hashes. It cannot authenticate dispatch or substitute for substantive acceptance.

After root has accepted every actual assignment and integrated the recovery notes, one additional step in the existing Linux Release job can run `python tools/check_interface_session.py --repo . --json` after the existing product tests and retain its JSON through the existing artifact upload. This proposal does not add product tests or suppress existing gates. At this review's source checkpoint that step has not been added or run; no local strict completion result is claimed.

The remaining acceptance dependencies are the recovered source's completed hosted matrix, accepted final assignment ledger with an observed strict checker result, and honest preservation of the missing raw archive. The full real-desktop replay, literal visual equality, physical devices/DAWs, native semantic accessibility, callback deadlines, specimen calibration and release rights/signing remain separate product work. They do not require reopening unaffected passing engineering gates.

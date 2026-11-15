# Product publication and preserved-work audit — A58

Actual reviewer: `/root/w10_a58_publication_audit`, wave 10, 15 November
2026 UTC. Read-only object, file and metadata inspection supports the recorded
publication and preservation claims. **No additional publication blocker was
found. Final code/ledger publication and its hosted qualification remain
pending.** This review does not accept a future staged tree or complete the
actual-worker ledger.

The [bounded audit receipt](../development/2026-11-15-product-continuation/reports/A58-publication-audit.json)
retains exact objects, file hashes, snapshot times, command scope and limitations.
The final independent GitHub GET at **03:14:39 UTC** still returned
`d8c39f7986746eacc991747153c7dbb012bb9a32` for `refs/heads/main`.
Local inspection was at approximately **03:12:57–03:12:58 UTC**. Later legitimate
owner progress is outside those observations.

## Exact published ancestry

GitHub read-only Git Data GETs independently returned each commit's tree and
single parent below. Local commit objects match every returned identity.
Local HEAD and fetched `origin/main` also resolve to d8; the live GET, rather
than that cached ref alone, establishes the remote observation.

| Published checkpoint | Commit | Tree | Single parent |
| --- | --- | --- | --- |
| Atlas reading and workflow | `da48180390a9fd473643d1759c153cb9d37ecfb6` | `ab4bc2b0036977589aa1088f3241ebc94dda5faa` | `647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb` |
| Reviewed contracts | `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d` | `f80130a6e932840ea027764f220b624e16a45844` | `da48180390a9fd473643d1759c153cb9d37ecfb6` |
| Product implementation | `ff41d412d03f2c5767aa4057b29fa8ec1627449b` | `6462343bb34a7d70d59de75ab349f8530196988c` | `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d` |
| Original paint observations | `99b363438b3c4f217e0acb5361c0aea52ad7d0e3` | `77c65ce06378a5a25a05591226d05b2445d91b1e` | `ff41d412d03f2c5767aa4057b29fa8ec1627449b` |
| Calibration fixture and install | `b9d352a82ac1afdec70c76ec5b1987785a37762e` | `b3b8b68e4c1f8312d46962924b5096f4ea10c4d2` | `99b363438b3c4f217e0acb5361c0aea52ad7d0e3` |
| Portability and guides | `d556da017ea0a5d4f2d231416782dbc5066e58c2` | `a3150fd2489a50a430b02c01eadd5e0c180bc7f9` | `b9d352a82ac1afdec70c76ec5b1987785a37762e` |
| Admitted gallery and repaired fixtures | `d8c39f7986746eacc991747153c7dbb012bb9a32` | `edf67b978f93e8dbea6537ce92d3928c171bc1f3` | `d556da017ea0a5d4f2d231416782dbc5066e58c2` |

The session start `647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb`, tree
`5358e5fe19c87d70a2cbfec8231c50e3f03d712d`, directly follows refinement closure
`fd2f6060b1f03b6d902ff0547441c07d6e74ba4f`. Both remain ancestors of d8.
No session checkpoint replaces that ancestry.

All seven retained local checkpoint refs exist. Each local commit has the
same tree as its corresponding remote commit, while keeping its own identity:

| Ref under `refs/checkpoints/` | Preserved local commit | Same-tree published commit |
| --- | --- | --- |
| `local-atlas-review` | `a3d10bf49ef878a1eb3c08460d244ba68a8143eb` | `da48180390a9fd473643d1759c153cb9d37ecfb6` |
| `local-reviewed-contracts` | `3b4a44e5f9dfd38172779ae0ec11a1d2169b9cd6` | `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d` |
| `local-product-implementation` | `ef2956b85ec1ed001488936b05ea2136d64514f3` | `ff41d412d03f2c5767aa4057b29fa8ec1627449b` |
| `local-paint-observation` | `1080d15749f3a96d8259c0befcc0307aab7ea9a5` | `99b363438b3c4f217e0acb5361c0aea52ad7d0e3` |
| `local-calibration-install` | `f033b68c6137e523fd79957b2e093346978a8dfa` | `b9d352a82ac1afdec70c76ec5b1987785a37762e` |
| `local-portability-guides` | `78b85e7e00143b9622ef74c9efa1254b0ef24ed8` | `d556da017ea0a5d4f2d231416782dbc5066e58c2` |
| `local-product-gallery` | `fd0761b63ff25146a9a4695dd16e7a821f0c5399` | `d8c39f7986746eacc991747153c7dbb012bb9a32` |

The retained [atlas](../development/2026-11-15-product-continuation/reports/atlas-publication.json),
[contract](../development/2026-11-15-product-continuation/reports/contract-publication.json),
[implementation](../development/2026-11-15-product-continuation/reports/implementation-publication.json),
[calibration/install](../development/2026-11-15-product-continuation/reports/calibration-install-publication.json),
[portability](../development/2026-11-15-product-continuation/reports/portability-guides-publication.json)
and [gallery](../development/2026-11-15-product-continuation/reports/gallery-publication.json)
receipts agree with these objects. They record non-force publication and
expected-head or guarded-update checks. The gallery receipt explicitly records
expected-SHA enforcement, eleven verified binary blobs, 97 changed paths and
preservation of later working files. The paint checkpoint has its remote object
and retained local ref, rather than a separate publication JSON receipt.

This independently establishes the resulting ancestry and trees. Immutable Git
objects cannot retrospectively prove the exact arguments of an earlier API
request; A58 does not claim possession of a raw mutation-request log. The
integrator must perform the fresh expected-head/no-force procedure again for
the actual final publication.

## Preserved source, galleries and original results

The following comparisons inspect current bytes and published Git blobs.
No application, test, build, numerical experiment or capture was executed.

| Compared material | Independent observation |
| --- | --- |
| Existing core/header, VST3 and musical UI/state files | All **52**, **20** and **four** respective session-start files are identical at d8 and in the inspected worktree. New crossover files are separate additions. This supports the preserved nominal dry Engine, musical-state and plugin boundary; [A55](PRODUCT_FINAL_CODE_ACCEPTANCE.md) retains the detailed 47-identity/state4/readers 1–3/91-source review. |
| Historical evidence | All **277 historical standalone gallery files** and **1,746 earlier-session development records** tracked at the session start are identical at d8 and in this checkout. The other owner's later unpublished files are outside this comparison. |
| Captured production source | All **108** hashes in the capture-qualified receipt match b9, d556, d8 and current files. The retained application still hashes to `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`. Agreement does not create a new compiler attestation or capture. |
| Current product gallery | All **62 files** equal their d8 blobs; both manifests admit the same **57 payload entries**. All **eleven PNG byte identities and decoded RGBA hashes** match A41. Capture source remains d556, publication source d8. Original BMP intermediates are unavailable; no fresh comparison to their original bytes is claimed. |
| Later coherent local evidence | All **366 frozen code/test/build/data inputs** and all three original configure/build/CTest log hashes match the retained receipt for **180/180 in 507.55 s**. That result belongs to d8 plus the accepted A46/A48 repairs. It does not qualify a future final tree or add a new execution. |
| Refreshed characterization plot | Decoded pixels are exactly equal to d8; only the JSON `plotter_sha256` field within PNG Description metadata changes. Current PNG SHA-256 is `57bc9ff8fb5e6f12d84bf9d2cd726ca2dfdd4dff5d24de05e8b7da9e7569054c`. No numerical rerun occurred. |

The [d8 hosted receipt](../development/2026-11-15-product-continuation/reports/d8-hosted-status.json)
and [Linux](PRODUCT_LINUX_HOSTED_REVIEW.md),
[Windows](PRODUCT_WINDOWS_HOSTED_REVIEW.md),
[macOS](PRODUCT_MACOS_HOSTED_REVIEW.md) and
[VST3](PRODUCT_VST3_HOSTED_REVIEW.md) primary reviews retain the thirteen
successful jobs for d8. A58 did not re-audit their primary logs or transfer
their qualification to the later working overlay. Original b9 and d556 failures
remain preserved alongside the later passing evidence.

## Current uncommitted scope and snapshot limits

At the 03:12:57 snapshot, this checkout had **zero staged entries, sixteen
modified tracked files and 55 untracked entries**, excluding A58's assigned
outputs. Its index hash was unchanged across the inspection. The actual ledger
then held **58 dispatched / 55 accepted** records; subsequent dispatches and
acceptances belong to the [live checkpoint](../development/2026-11-15-product-continuation/CHECKPOINT.md)
and [manifest](../development/2026-11-15-product-continuation/assignments.json).
These counts are a dated observation, not a final closure claim.

Only five paths in the source/test/build/CI groups differ or are newly present:

| Owner's accepted scope | Paths |
| --- | --- |
| A46 actual-record validation | `tools/check_product_session.py`, `tests/test_product_session.py`, `.github/workflows/ci.yml` |
| A48 report admission | `tools/plot_crossover_characterization.py`, `tests/test_plot_crossover_characterization.py` |

The other pending files are documentation, the metadata-only plot update,
worker notes, publication/hosted receipts and original logs. The audit receipt
retains the exact observed path list and five code/CI identities. The CI product
step still uses `--allow-incomplete`; it is deliberately not the final strict
closure gate. Running or newly delivered worker files require root's actual
acceptance before inclusion. A58 has neither staged those files nor certified
their eventual combined tree.

## Separate R4 checkout

With `GIT_OPTIONAL_LOCKS=0`, A58 inspected only necessary metadata in
`/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`. At 03:12:58 UTC it retained
HEAD `fd2f6060b1f03b6d902ff0547441c07d6e74ba4f`, tree
`89c0fb214b018ca43ec9c8b413d3030284a54ec2`, **151 staged entries and four
untracked entries**, with no unstaged tracked entries. Its ledger contains
41 actual dispatched workers: 38 accepted and three running; nineteen of its
sixty rows are still planned. Its index remained SHA-256
`92308eb7babf2685f0438d35c695455f012b9625bd9e64031b0c1153c9daa795`
across the read.

Those observations agree with A56's earlier snapshot. They neither accept the
owner's overlay nor prove it must stay unchanged while that owner continues.
Future differences can be legitimate progress. No file, index, ref, build or
evidence in that checkout was modified. Published d8 R4 success does not close
its separate worker ledger, integration, publication or R5/R6 gates.

## Preserve raw whitespace evidence

The [gallery preflight](../development/2026-11-15-product-continuation/reports/gallery-publication-preflight.json)
deliberately excludes three original artifacts from source whitespace grading:

| Original report basename | Unchanged SHA-256 at d8 and now |
| --- | --- |
| `A42-first-failure.patch` | `97463d5475cd44e0ad47469091a8a94ff7a5f25b4bb120855f80e4eaef2cba5a` |
| `A43-root-installed-ctest.txt` | `dcc210d29118c609d04995a624d571007bc552ffdd4d14e614bc12d4c2a549ba` |
| `wave7-material-facade-ctest.txt` | `174ed3055995dd6095890a30428051353eedc2c738df4cf63199736eedab5dcc` |

Replaying `git diff --check d556da01 d8c39f7` reports exactly ten trailing-space
diagnostics in these files. The same comparison with those exact three path
exclusions returns zero. Their blank patch-context markers and original CTest
prefixes are evidence bytes, with no exemption for production source.

The newly retained `reports/wave8-configure.txt` has **eight** original
trailing-space lines and SHA-256
`abe0a48328fc642b9f3c8c6aefb660dd80c7ea22e61039a9411925f1f5b06d23`.
It matches the coherent-build receipt. Root confirmed that the final preflight
will preserve its bytes and record this fourth exact raw-log exclusion. Do not
normalize an original log or broaden the exception to source or an entire
reports directory.

## Root's final publication checklist

1. Finish actual acceptance of A01–A60 in ten six-worker waves. Review owned
   diffs and note hashes, retain the strict product-checker result, then change
   the CI product-record invocation from progress to strict. An incomplete
   checker result or these publication checks cannot supply missing acceptance.
2. Stage only accepted worker outputs and root-owned reconciliation. Preserve
   original failures, all galleries, earlier ledgers and the separate checkout.
   Bind any raw whitespace exclusions to the exact named artifact hashes.
   Inspect the final staged paths and tree; no final staged tree is attested here.
3. Recheck the frozen code inputs against the 366-input gate and account for
   the final CI/ledger changes. Run the necessary affected integrity gates;
   repeat runtime qualification only for changed relevant inputs or a required
   gate. Preserve the 180-test observation under its original source boundary.
4. Immediately before publishing, read the actual remote main. This audit's
   d8 value is a snapshot, not a reusable lease. If it advanced, inspect and
   preserve compatible work, reconcile actual overlaps and recheck affected
   inputs. Publish with the fresh `expected_sha` and `force:false`; compare
   the candidate's complete tree, including binary blobs, before moving main.
5. Independently fetch/read the resulting main ref and commit. Verify exact
   commit, tree, intended parent(s) and expected file/blob contents. Preserve
   the local same-tree predecessor under a checkpoint ref, then synchronize
   the local branch with a guarded update that preserves active files/index.
   Do not reset another owner's work to obtain a clean status.
6. Observe the final source's required hosted jobs, including both added Python
   modules and the strict actual-60-record step. Retain primary evidence and
   real failures. Afterwards publish the compact evidence/closure handoff with
   its tested source explicit; verify that publication and the actual local
   state again. A later evidence-only commit is not a new runtime execution.

The integrator owns all these mutations and remaining qualification. A58 made
only the assigned review, note and bounded receipt; it performed no commit,
push, local fetch, ref/index mutation, shared-source edit, test, build, capture
or deletion. Literal whole-interface 1:1, real-device/accessibility/DAW and
physical-model gates remain distinct from publication integrity.

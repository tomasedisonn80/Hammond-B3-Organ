# Final documentary publication safety review — A52

**No remaining identified blocker in the corrected helpers**, provided root preserves the explicit final-index, commit-tree and nonforced expected-main guards. This read-only prospective review does not certify final staging or publication as already executed.

## Original findings and observed corrections

The first reviewed `check_combined_stage.py` was 6,004 bytes, SHA-256 `8b226285e8725a9b5ed7dbcf991b0e67caf7c45ac5d12be50fdf0b4bfde86c13`. Its eleven-document exception permitted unintended document mode/type changes, and its unchanged-base count subtracted only the older nine-file source delta. Root added presence/mode/type equality for all eleven documents and changed the count to actual Git-entry equality.

The corrected checker is 6,260 bytes, SHA-256 `c5cdb7d9ec85f5c64435f74b9bb59990672d4dafc5d12c070afbe99bfbec8f1e`. Reversing exactly those two changes reconstructs the original bytes and hash. `prepare_guarded_publication.py` remains 2,582 bytes, SHA-256 `ef0b4bc906355ce29f6c92966901a56c59419c7542b3d313e26da3d50cc02a5a`. Both parse as Python; neither was executed by A52.

## Publication boundaries

Use the combined checker with literal source `54859886268ce83c36f359c43327f7c72a77ae82`. All existing noncurrent entries retain their complete mode/type/blob identity. The checker runs integrity gates on its immutable staged archive. Its four emitted proofs must be staged separately, with a full-entry comparison showing that only those four exact paths differ from the checked tree. Keep the post-proof comparison receipt outside that frozen index; avoid an unaccounted fifth file or another broad add. Require the actual local commit tree to equal the recorded final index tree, with source548 as sole parent.

Preparation reads immutable Git blobs, preserves modes and rejects every deletion. Acknowledged upload states only avoid duplicate blob uploads; the remote Git Data tree must still match the complete expected local tree. Require a fresh main ref equal to source548 immediately before the nonforced update. A competing descendant not contained in the candidate history must cause a stop, without forcing. Independently verify API ref/commit/tree/parents and Git-fetched contents before aligning local HEAD without discarding work. The reviewed helpers themselves do not perform the ref update, so those checks remain explicit root responsibilities.

## Evidence preservation

All 71 acknowledged Core/VST3 blob rows match their preupload manifest, current raw bytes and Git check-in blob identities. The tracked source attributes and local attributes introduce no archive export exclusions or substitutions. All 35 accepted main Core files, their freeze manifest and the earlier 110 frozen A52 files remain unchanged. The terminal source548 receipt remains SHA-256 `d2cf446d4ee22ef415fb46dd019958617de8a30d5124a733ede986225c60af2c`: sixteen successful jobs and 1,505 CTest observations across configurations, with full R4 separate.

The documentary successor receives source equivalence and its own staged integrity checks. Hosted executions retain source548 attribution; old failures, optional skips and open hardware/whole-interface 1:1 gates remain intact. The user already authorized commit and push; this review introduces no new approval step. [publication-safety-review.json](publication-safety-review.json) retains the exact findings, hashes and prospective sequence guards.

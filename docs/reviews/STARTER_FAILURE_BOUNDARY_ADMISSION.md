# Starter audition failure boundary admission — A40

16 November 2026. Reviewed at local HEAD
`d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93`, with root's separately owned
native-load/CI additions. Scope is the audition helper and its original
14-method suite, against the [pack](../STARTER_REGISTRATION_PACK_CONTRACT.md)
and [render](../REGISTRATION_RENDER_CONTRACT.md) contracts. A30's
[CLI/generator/installer review](REGISTRATION_FAILURE_BOUNDARIES.md) and A35's
[installation admission](REGISTRATION_INSTALL_ADMISSION.md) remain separate;
their experiments were not repeated.

**Admit the corrected reporting boundary at the identities below; root's full
integration gate remains required.** This is no new all-recipe rendering,
publication, hosted-platform or physical acceptance.

## Concrete finding and preserved failure

**A40-F1:** aggregate `manifest.json`/`report.md` writes originally occurred
outside the batch failure handler. A late write exception reached the generic
`audition refused` diagnostic after files already existed. That diagnostic
identified neither the failed report nor retained report state. The module also
promised retained reports unconditionally, while generated prose described
“Each WAV” as complete even when its failed job retained `RIFFpartial`.

The [original receipt](../development/2026-11-16-preset-library-continuation/reports/a40-failure-boundaries-original.json)
records three controlled cases: an ordinary first-child failure, then injected
late manifest/report write failures. Each attempted one injected child, returned
1, and retained actual partial WAV/log bytes. The late cases retained a
19-byte report prefix; manifest failure left no Markdown report, while Markdown
failure retained the completed failed-batch manifest. Both late cases emitted
only the generic refusal. All watched inputs remained unchanged.
The [archive](../development/2026-11-16-preset-library-continuation/reports/a40-failure-boundaries-original.tar.gz)
preserves the exact probe, diagnostic bytes and complete residue. ENOSPC and
child exit were injected; no native renderer or actual disk exhaustion occurred.

Root explicitly reassigned the two production/test paths for this correction.
`AuditionReportError` now identifies the failed aggregate filename, retained
output directory, and both reports as absent, present with completed write,
present with unverified completeness, or presence unknown after inspection
failure. The CLI returns 1. No partial report is rewritten, removed or retried.
An already completed manifest retains its batch status even if subsequent
Markdown delivery fails; the process still fails and identifies that boundary.
The success JSON schema, job plan and rendering arguments are unchanged.
Report prose now limits complete-clip claims to successful WAVs and explicitly
distinguishes partial artifacts from validated clips.

## Admitted behavior and limits

| Boundary | Evidence and meaning |
| --- | --- |
| Preflight refusal | Existing tests inspect invalid timeout, existing/aliased destinations, nonregular input, unsafe manifest filenames, extra entries and unequal suffix pairs before creation. Final exclusive `mkdir` refuses a competing directory. |
| Child or evidence failure | Existing controlled nonzero, timeout and canonical-provenance cases preserve actual outputs, stop the batch and leave later jobs unrun. Start failure, malformed successful stdout and WAV rejection also follow inspected failure branches; they were not newly executed here. |
| Report creation failure | New cases cover failure before creation and after partial writes for each aggregate report. Diagnostics, retained bytes, no later report attempt after manifest failure, and unchanged destination reuse refusal are checked. |
| Provenance | Canonical schema-6 controls must equal admitted payload bytes; successful suffix pairs require whole-WAV hashes to match. Input identities are observed before/after hashes, not authenticated runtime identities or immunity to transient changes. |

Regular-file read limits remain renderer 512 MiB, profile 1 MiB, manifest/tool
128 KiB each, payload 16 KiB and score 8 KiB. WAV inspection permits 196,096
bytes; stdout/stderr inspection permits 1 MiB each. These are inspection limits,
not child-output disk quotas. Exactly 32 jobs render 48,000 frames each, with
per-child timeouts of 0.1–30 seconds. Directory enumeration, filesystem latency
and aggregate reporting have no batch deadline. No new caps or frozen contract
changes were introduced.

The preserved original author log records 14/14 methods in 4.496 seconds; its
manifest records 32 completed clips, 16 equal pairs and unchanged inputs. Those
remain original-source evidence, not a rerun or qualification of changed bytes.

## Targeted qualification and identities

Cwd `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`; Python 3.12.14.
The [targeted receipt](../development/2026-11-16-preset-library-continuation/reports/a40-failure-targeted-tests.json)
retains exact argv/environment, input hashes and original compressed logs:

```sh
HAMMOND_SOURCE_DIR=. HAMMOND_RENDER_EXECUTABLE=../build-native/hammond_render \
HAMMOND_TEST_PROFILE=../build-native/nominal.b3p TMPDIR="$PWD/out/a40-targeted-test-tmp" \
python3 -B tests/test_starter_auditions.py \
  StarterAuditionReportFailureTests.test_aggregate_report_failures_identify_retained_and_missing_files \
  StarterAuditionReportFailureTests.test_failed_job_report_distinguishes_partial_wav_from_successful_clips -v
```

**2/2 methods pass in 0.042 seconds:** five injected child calls, zero native
renders. The separate class avoids the original suite's 32-render setup.
`git diff --check -- tools/audition_starter_registrations.py tests/test_starter_auditions.py`
passes. Root reviewed and admitted the source-ready diff before note freeze.

| Input | SHA-256 |
| --- | --- |
| Corrected helper | `1ff78d28e74c7556aa525f5eb779d40ced76b7f913c1ec38085b4c2def216157` |
| Expanded 16-method source | `5fea287ed572de6ca2fd62e34e7113ab5878ea44e16d92849d81c34d4a16431d` |
| Original helper | `60a2e20d0a60a6e6e18ea55913e69fd1bedb81f52ae8ae0558cacf0ac09a173a` |
| Original 14-method source | `b9214a51dafcc0bab4ab8eef8ff52e91ec57eaa69cd92d70f82021ab1cf6c8a4` |
| Original 32-clip manifest | `01ae18231688c215512059850a7784c4451e502b37a640b2ef34934d55e3160d` |
| A40 failure receipt | `5b750507885c2fdfbabd006ab6a6f79550e0c9f2cb441341f8e680da64e6ce37` |

Root should run the complete integrated gate and retain exact-source publication
and hosted results. Whole-interface 1:1, physical calibration, device/host
acceptance and other owners' unfinished work remain open.

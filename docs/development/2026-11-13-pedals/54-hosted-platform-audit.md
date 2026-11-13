# Assignment 54 — independent hosted wave-8 audit

Owner: `/root/w09_a54_hosted_platform_audit`.

Assignment **54/60**, wave **9**, current pedal-development session. This is one
newly dispatched worker. The spawning UI reported aborted, but the worker ran,
notified root, retrieved actual evidence and completed this review. No child
worker was dispatched.

## Scope and ownership

Owned only `docs/reviews/PEDAL_HOSTED_WAVE8_FINAL.md` and this note. Read standing
[AGENTS.md](../../../AGENTS.md), current plan/status/next steps and operational
handoff, both CI contracts, the portability history, wave-8 integration record,
actual published workflow YAML and the relevant test sources. The runtime skill
and networking reference were read before artifact transfer. The runtime-status
tool and local network-policy file were not available in this child environment;
ordinary allowed artifact requests succeeded with inherited settings. No network
policy, credentials or packages were changed.

The reviewed published commit is `d601eb166ea3206748f8e012b20a463ff365c0b1`,
tree `8af684dfe56f88222c52ff71d85a911ee1192fa1`. Its six-file delta from root's
qualified tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e` is Markdown only.
The live assignment-51 inventory repair was deliberately excluded. All source
hashes below come from `git show COMMIT:path`, not the changing worktree.

## Executed audit and retained commands

Read-only connected GitHub calls retrieved:

```text
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681825
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681882
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681825/jobs?per_page=20
GET /repos/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681882/jobs?per_page=20
GET each run's artifacts and each completed job's complete logs
GET the seven identified artifact ZIPs through the artifact-download connector
```

The account was the owner's already-selected GitHub connection. No workflow
rerun, ref update, repository write or message to a third party was issued.
Artifact responses supplied temporary file references; downloads used ordinary
`urllib.request.urlopen(..., timeout=45)` with inherited proxy/CA settings.
Each compressed byte length and SHA-256 was checked against fresh API metadata
before bounded ZIP inspection. Private extraction rejected unsafe names and
link entries. It retained the original ZIP bytes and every extracted member's
size/hash receipt. No downloaded module was loaded.

The final public job and annotation responses additionally retain their HTTP
`Date` headers. The connector did not accept the check-run annotation endpoint;
the corresponding ordinary read-only public GitHub API request supplied the
actual annotations without changing access settings or credentials.

Key source comparisons were:

```sh
git rev-parse 'd601eb166ea3206748f8e012b20a463ff365c0b1^{tree}'
git diff --name-only 5370890e32045a556cb61a88cdb1f04fb5a18f7e d601eb166ea3206748f8e012b20a463ff365c0b1
git show d601eb166ea3206748f8e012b20a463ff365c0b1:.github/workflows/ci.yml
git show d601eb166ea3206748f8e012b20a463ff365c0b1:.github/workflows/native-vst3.yml
```

Local Python inspection used `xml.etree.ElementTree` for JUnit, independently
split all complete last-test records, counted actual unittest summaries/skips,
checked actual source/run/tree/attempt provenance and SDK-lock equality, and
parsed native headers directly. For each native tar it checked exact membership,
links/paths, full bytes, sizes, hashes and modes against the inventory, verified
the outer/inner digests, compared build/staged inventory bytes and located the
unchanged profile exactly once in the module. It checked the sanitizer compile
flags/environment and inspected actual Windows native `/fp:strict` commands.
All inspection assertions completed successfully.

The audit did **not** rerun the software suites, build the project, run TSAN,
load a plugin, test a DAW or audio device, or take physical measurements. Its
execution evidence is the newly retrieved actual hosted logs and artifacts.

## Observed results

Core Linux, Windows and Linux sanitizer jobs each passed **71/71 suites** and
**548 Python methods in 33 Python suites**, with zero failures, disabled tests
or skips. Their CTest wall times were **54.81, 94.05 and 133.77 seconds**.
The new actual install/demo/session/plot gates and the published nineteen-method
inventory gate ran on all three. Native Linux passed **8/8 in 6.53 seconds**;
Windows passed **7/7 in 7.27 seconds**, each including two native-install Python
methods and completed build/copy inventories and artifact uploads.

JUnit success-output truncation initially yielded only 357 visible Python
methods and omitted eight summaries. This was an incomplete extraction, not a
test failure. Reading the retained complete `LastTest.log` files established all
33 summaries and the correct 548 count on every completed core job. The audit
retains both raw records and the complete per-suite method list.

Both SDK validators report 47 passed/zero failed while retaining sixteen
teardown diagnostics, nine unsupported-rate ERROR messages and fifteen
unsupported-float64 info messages. The supported-format/lifecycle restrictions
and independent ABI checks remain explicit. Native ABI and relocated-ABI
results each compare 229,725 frames with zero maximum error. Controller metadata,
thresholds and strict streams report 41,795 checks per platform. Concurrency
counts remain schedule-dependent and are recorded without treating timing as a
device deadline.

All **seven actual ZIPs** match fresh Actions digests and sizes. Both native
inner archives and all **ten payload members** match their exact inventory
bytes, sizes, modes and hashes. Build/staged inventories match byte for byte.
Source/run/tree and the five SDK checkouts/license-verification record agree.
Each actual module contains the unchanged 4,545-byte compiled profile once.
The current Windows module is `14ff853094023a537f86dd836fe9ed5bc7025d8912a23a82e2fe29d3be552826`;
it does not inherit wave 7's different Windows module identity. No cause for
that binary difference or build-reproducibility promise is asserted.

The final job metadata has HTTP `Date` **2026-11-13 11:46:21 UTC**. Both macOS jobs
had changed from queued to `completed`/`cancelled`, retaining empty runner names
and zero steps. Core job **131859605945** completed at `2026-11-13T11:46:03Z`;
native job **131859604644** at `2026-11-13T11:46:02Z`. The `started_at` fields in
their queued job records do not establish execution. Actual current-job
annotations retrieved at **2026-11-13 11:48:12 UTC** state that the hosted runner
was not acquired after multiple attempts and contain three ARM64-capacity
notices for each job. No project code ran. These observations leave both
complete-matrix gates open and differ from wave 7's observed higher-priority
concurrency cancellation. Root received the actual changed outcome and reason;
no retry or runner-label/test-policy change was issued by this reviewer.

## Source identities and evidence location

| Published input | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 5,898 | `4835cbd72231c81c082c6545bde58e1514843626ffe4c9b88078c380f79dc87e` |
| `.github/workflows/native-vst3.yml` | 8,261 | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `data/dependencies/vst3-sdk-lock.json` | 3,796 | `ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965` |
| `tests/test_pedal_demo.py` | 24,755 | `841405bb2d71f54feeb4461e141fbd268adfe6e4a2465106558ed58ca0ab6eb4` |
| `tests/test_plot_pedal_trace.py` | 27,460 | `4a15024dc338eb5bda60c375c538357e2ea17fea23d155e190e1cb0e5447f167` |
| `tests/test_pedal_session.py` | 21,803 | `bd700a1b78108de2decbaa815744a5c0bcc3b51d58950c1e66851d885752b554` |
| `tests/test_install.py` | 34,550 | `eadd0a110b828b4a483235f740d13f0de0e96598a25de007c56aafc6ff2f1c6e` |
| `plugins/vst3/tests/test_native_install.py` | 11,704 | `3f2a2e8b52ca2d647e4da45218ed68c748b7a5d5212b8254fad57e3b6965366e` |

The local `a54-hosted-platform-audit/` directory contains the seven ZIPs, their
safe extracted files and receipts; five full job logs; initial/latest API
observations; `execution-audit.json`; per-job parsed JUnit and complete-method
lists; and `native-artifact-verification.json`. The
[public review](../../reviews/PEDAL_HOSTED_WAVE8_FINAL.md) retains every artifact
ID/digest, job/source association, complete-log/JUnit hashes and actual counts.
Temporary Actions artifacts are subject to the workflow's fourteen-day policy;
these retained report identities make that limitation explicit.

Exact local handoff for assignment 57, all associated with native run
**43417681882**, attempt **1**, published W8 source **d601eb166ea3206748f8e012b20a463ff365c0b1**:

- Bundle artifact **14032427484**: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484.zip`.
- Actual hosted inner archive: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484/HammondB3-Release.tar.gz`.
- Inventory and archive digest: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484/inventory.json` and `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032427484/archive.sha256`.
- Diagnostic artifact **14032911399**: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032911399.zip`.
- Actual diagnostic payload: `/workspace/scratch/f364bc93d920/a54-hosted-platform-audit/14032911399/native-ci-logs/`.

The inner module member is `HammondB3.vst3/Contents/x86_64-linux/HammondB3.so`,
SHA-256 `b8efd0d0e93567f072ef7304734787ff20fdf096145f344dffa502035b9847ca`.
The final API responses and current cancellation annotations are retained in
`final-api-43417681825.json`, `final-api-43417681882.json`,
`annotations-131859605945.json` and `annotations-131859604644.json` under the
same audit root. These are the raw evidence for the final timestamps and status.

## Handoff and boundaries

No project failure was found in the five executed jobs. Root and assignment 59
own the later exact-source platform gate, including macOS runner acquisition
and the real Windows junction regression from assignment 51. Root has corrected
the reported obsolete first-publication paragraph in `docs/VST3_CI.md`; this
worker made no shared-document edit. The wave-8 review is frozen at the recorded
final metadata and annotation observations, without optional further polling.

Scoped document verification checks both reports as UTF-8 with LF endings, a
final newline and no trailing whitespace. All six relative Markdown links
resolve. The owned-file whitespace check passes. No product test was added or
rerun for these documentation changes.

The audit establishes finite software execution and observed artifact/source
association, not signed build attestation, external-host/device qualification,
rights clearance, complete M3, scanner/AO-28/Leslie fidelity or a released product.
Only the two owned Markdown files were written in the repository. No staging,
commit, push, production/test modification or additional worker was performed.

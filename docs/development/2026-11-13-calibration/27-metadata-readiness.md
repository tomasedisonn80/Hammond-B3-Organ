# Assignment 27 — capture declaration readiness

Actual worker identity: `/root/cal_w5_a27`. This is assignment 27 of logical
wave 5 in the 2026-11-13 calibration session. The parent's successful dispatch
is the counting record; a worker-side wrapper observation adds no dispatch.
It is one distinct assignment; no earlier worker or future acceptance worker
is counted here. Root clarified this accounting wording at acceptance.

## Ownership and source basis

This worker owns only:

- `tools/capture_readiness.py`
- `docs/CAPTURE_READINESS.md`
- `docs/development/2026-11-13-calibration/27-metadata-readiness.md`

The working directory was
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. Read the standing `AGENTS.md`,
current calibration scope and handoff, project plan, status/next-step/log context,
complete capture v1 format contract and validator, shared JSON primitives,
relevant schema definitions, acquisition protocol sections and the fresh atlas
review. This assignment does not claim another complete reading of the PDF.
The six actual atlas readers' coverage remains the source-reading record.

At first inspection, local `HEAD` was
`091ad20c632209053c337a06544f82a829644800`, tree
`8679418135946193b2b989a89e60ac6099b00125`; locally recorded `origin/main` was
`5b8e2419d23fe27c51709d717812060eafd44dcc`. During final source freezing the
integrator had advanced the checkout to
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`; locally recorded `origin/main` was
`649b12c7d1faa7601fde1019e913347c65a6634a`. These observations identify concurrent
checkout history, not a claim that this worker's new uncommitted files were in
those commits. No remote publication or hosted qualification was performed or
verified by this worker.

| Exact input/deliverable | SHA-256 at producer freeze |
| --- | --- |
| `tools/capture_readiness.py` | `215b2abd3614195151c5751248f2d40850653d794af1786e95eaedccf13bdc76` |
| `docs/CAPTURE_READINESS.md` | `e3eb647244c62d600e58d37a83f99db165256e4a69cf89e210f354fc12b55b0b` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |
| `data/capture.schema.json` | `2e33ff19c23b2c82d593073f6d24bd29889531c62acd2d8fcf08ec48c0ae7860` |
| `data/capture-planned-example.json` | `35eb831bd8fc4cca3107dca983efadfe8b4edc50a966931bae96dc7946f075ac` |

The shared JSON code, unchanged v1 validator, schema, supplied plan, other
production modules, tests, shared status files, session ledger, CMake and Git
refs were not modified by this worker. The integrator owns acceptance, shared
documentation, coherent-source verification and publication.

## Contract before implementation

The integrator approved a deliberately small metadata-only proposal. The guide
was written before the implementation and its initial hash was sent to root so
assignment 28 could work from an independent contract. Before implementation,
one wording correction made the stream failure boundary precise: admission and
publication rejections emit no report, but a failed stdout write may already
have delivered partial bytes and cannot retract them. That clarification changed
the guide hash from
`47af07c532fd25d085c5f6187843ee3e2dd055cc830b0fdc5ffeaa2339449ab7`
to the final hash above. Check rules, order, report fields and resource bounds
did not change. Root was notified of both hashes and the exact reason.

The final [readiness contract](../../CAPTURE_READINESS.md) defines:

- `ReadinessError` with stable `code` and descriptive `message`,
  `inspect_readiness(path)`, and integer-returning `main(argv)`.
- One bounded regular-file read through shared JSON admission: original bytes
  at most 65,536, 4,096 value nodes, depth 16 and numeric magnitude 1e12, followed
  by unchanged capture v1 semantic validation. The identity belongs to those
  exact parsed bytes, including whitespace; no second read is used for hashing.
- The complete parsed manifest and its original reasons; 21 ordered base checks
  plus three per declared channel, at most 69. The guide lists every stable
  path/check identifier, category, state rule and literal missing-field action.
- Explicit `declared`, `missing` and `not_applicable` states. Only synthetic
  specimen ID and v1 synthetic calibrations receive the documented exemption.
  An unknown synthetic port, model revision or rights field remains missing.
- `planned` status takes precedence for every plan. Recorded records are
  `declarations_incomplete` when any check is missing, otherwise
  `declarations_complete`. None of these statuses admits a physical fit.
- `raw_acquisition_only` calibration context and seven permanent
  `not_established` claim fields. Derived records retain their declared ancestry
  without inheriting raw-stream scale, geometry or rights scope.
- A bounded, deterministic report without input absolute path, hostname or
  execution timestamp. Output is limited to 1 MiB, 16,384 nodes, depth 24 and
  numeric magnitude 1e12, with rejection rather than truncation.
- Strict CLI options, original UTF-8 stdout bytes, optional fresh no-clobber
  publication before stdout, typed JSON failures and explicit exits 0/1/2/3.

No artifact, audio, evidence locator or rights locator is opened. No new input
schema, general workflow language, measurement substitution or runtime dependency
was introduced. Hardware calibration and permission text are declarations for a
reviewer, not facts established by this program.

## Executed producer checks

Runtime: Python **3.12.14**, Linux. All commands below used the working directory
given above. The first direct smoke command imported the new module and called:

```python
capture_readiness.inspect_readiness(Path("data/capture-planned-example.json"))
```

It returned `planned` with exactly **21 checks: 1 declared, 20 missing,
0 not_applicable**. The input identity was the 3,223 original bytes and the
supplied-plan SHA-256 in the table. That plan still contains no acquisition.

A scratch author-check harness then ran:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/readiness-author-check.py
```

Observed result: **104 assertions passed and 15 actual CLI subprocesses passed**,
exit zero, with the command reporting 1.080 seconds. This is producer-authored
development evidence, not assignment 28's independent acceptance. The scratch
harness SHA-256 was
`e5c07a4610def6d2f61eac8a0d56e36cd3d9b7b2aee4951a60e71a18766439b9`.
It creates temporary fixtures and removes them through `TemporaryDirectory`;
it is not an installed tool or a retained project acceptance suite.

| Area | Actual executed evidence |
| --- | --- |
| Exact report and plan | Root/check key sets, supplied-plan counts, status precedence, action/null rules, raw context and all seven permanent claim values. |
| Synthetic declaration states | A recorded two-channel synthetic declaration yields 27 total, 23 declared, zero missing and four not-applicable checks. Missing revision and channel-port text remain gaps; an unassigned role adds its own gap. |
| Original data preservation | Independent `hashlib.sha256` over exact fixture bytes; whitespace changes identity without changing parsed declarations; accented/Unicode reasons and leading/trailing spaces survive exactly; separate returned reports do not share mutable state. |
| Hardware-shaped declarations | A clearly labeled hypothetical one-channel hardware metadata fixture with declared clock/scale produces 24 declared checks while every physical claim stays unestablished. Removing the clock, boundary and scale declarations produces three separate gaps with the exact original reasons. No hardware acquisition or calibration exists for this fixture. |
| Raw/derived/support boundary | Valid raw, derived and support declarations reference absent files. Reporting succeeds without creating or reading those artifacts; the entire local ancestry remains unchanged in the report. |
| Actual inclusive limits | A valid manifest padded to exactly 65,536 bytes is read and identified; byte 65,537 rejects. An actual 16-channel manifest produces exactly 69 distinct ordered checks and 18 synthetic exemptions. |
| Strict admission | BOM, invalid UTF-8, duplicate keys, nonfinite/overflow/long numeric tokens, trailing JSON and surrogate text reject. Wrong v1 root type, boolean schema version and malformed file declarations reject as v1 errors. |
| API and filesystem | Unsupported path types, string subclasses and generic path-like objects reject; missing/directory/symlink leaves reject; a native parent alias and hardlinked ordinary input are admitted under the shared contract. Cancellation propagates. |
| Report guard branches | Explicitly reduced byte and node limits reject with `report_limit`. These probes qualify failure branches, not a claim that a full 1 MiB report was produced. |
| Real CLI | Actual foreign-current-directory execution, plan exit 3, complete exit 0, missing/abbreviated/unknown/duplicate/empty options exit 2, help exit 0. JSON errors and empty stdout are checked where required. |
| UTF-8 and publication | A real CLI process with `PYTHONIOENCODING=ascii` and `PYTHONUTF8=0` still emits UTF-8 bytes matching the new report file. Existing report, input target, directory and dangling symlink are preserved; missing output parents are not created. Ordinary output cases leave no `.capture-json-*` temporary. |
| Standard streams | Text-only redirected streams work; injected stdout failure after successful publication leaves the complete new report and returns `stream_error`; stderr failure cannot turn rejection into success; help output failure returns nonzero. |

The author harness passed on its first complete execution. During implementation,
before that execution, help output was routed through the same bounded UTF-8
stream writer and stream error messages were given the actual stream label to
match the frozen failure contract. These were development adjustments, not
changes made to hide an independently failing expectation. No failed production
case was observed by this worker's completed harness.

The two source/delivery files were also explicitly checked for valid UTF-8, one
final newline and absence of trailing whitespace. The frozen implementation is
11,247 bytes and the guide is 14,203 bytes. This worker did not rerun unrelated
core/native tests or claim a CMake, installed-package or hosted-platform gate.

## Handoff and limitations

Root should dispatch independent assignment 28 from the frozen guide, accept its
retained test suite and findings, and run the selected suite from the final
integrated source. Any repair must preserve the original rejection and expected
behavior in its test rather than weakening the guide silently. Root then owns
test discovery verification, current-state documentation and guarded publication.

The current implementation uses only the two listed local helper modules and
the Python standard library. A later installed capture-tools component must keep
those imports available beside the executable script. Useful user commands are:

```sh
python3 tools/capture_readiness.py --input data/capture-planned-example.json
python3 tools/capture_readiness.py --input /path/to/capture.json --output /path/to/new-readiness.json
```

The supplied plan's exit 3 is intentional. Keep its unknowns intact. The next
human task is to resolve the relevant declared gaps through the acquisition
protocol and independently review the resulting actual evidence. This reporter
does not check whether a rights statement grants anything, whether a clock or
scale was measured, whether evidence locators are retrievable, whether a raw
stream exists, or whether related takes are independently partitioned.

Native Windows/macOS execution, native Windows reparse behavior, full maximum
report size/depth/node workloads, hostile concurrent filesystem races and
physical acquisition/permission/calibration/fidelity were not qualified here.
Known field text still requires substantive review. The inspector can expose
missing declarations; it cannot establish that present declarations are true.

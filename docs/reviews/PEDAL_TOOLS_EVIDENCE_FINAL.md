# Pedal tools and evidence final audit

Owner: `/root/w09_a51_tools_evidence_audit`

Assignment: 51 of 60, wave 9, session `2026-11-13-pedals`

## Result and source boundary

The focused tools gate passed **173 test methods across nine suites**, with no
failures, errors or skips. Independent review found one concrete Windows bundle
admission defect: directory junctions and other reparse points could retain
ordinary directory or file modes and pass the inventory's existing symlink
checks. The approved repair rejects their metadata before traversal or opening.
The repaired inventory suite passed **20 methods** on Linux. Actual Windows
junction execution remains a separate, pending hosted Windows result.

The reviewed integration baseline was Git tree
`5370890e32045a556cb61a88cdb1f04fb5a18f7e`. All **534 files**, including executable
modes, in its frozen archive were checked against Git blobs before testing and
rehash-checked afterward. The archive remained unchanged. The repair was tested
as two privately frozen file overlays, identified below; it was not represented
as part of the earlier tree or as an already committed source revision.

Root separately reported 71/71 default CTest suites and 8/8 native suites passing
on that tree. Those full gates are integration evidence supplied by root. This
assignment's independently executed gate is the nine-suite table below.

## Contracts examined

| Area | Checks and evidence examined | Limit of the result |
| --- | --- | --- |
| Render schemas | Producer emits schema 3; independent consumer retains exact schema 1/2/3 contracts. Tests cover duplicate keys, exact scalar types, nonfinite values, bounds, canonical event fields, ordered absolute frames and stable ties. The producer and verifier hold independent expectations for pedal maps and matrix identifiers. | A recognized schema and matching hashes do not authenticate a physical measurement. |
| Retained render bundles | Consumer recompiles retained profile JSON, checks compiled profile bytes, exact bundle members, file identities, PCM headers, channel counts and statistics. Semantic mutation tests rehash altered metadata so a checksum mismatch alone cannot explain rejection. The verifier neither invokes a renderer nor executes recorded commands. | Recorded Git/source paths and renderer hashes do not establish which source produced a binary. The explicit `binary_association: "not_established"` boundary remains. |
| Process and publication handling | Producer invokes argument lists without a shell, bounds input/output and process duration, creates a new output directory exclusively, and records incomplete runs. Plot and inventory publishers finish a private file before a no-clobber hard link. Existing destinations, dangling links and competing writers have focused coverage. | Quiescent input is still required. These readers do not claim isolation from arbitrary hostile filesystem mutation. |
| CLI paths and numbers | Shared argument conversion uses strict Windows UTF-16 to UTF-8 conversion and filesystem paths built from UTF-8. Actual compiled Linux CLIs exercised copied executables, Unicode paths, byte limits, numeric rejection and output races. | Linux success does not execute `wmain` or establish native Windows path behavior. |
| Pedal trace and plot | Parser checks the ordered metadata and column contracts, row bounds, clock consistency, contact states, mixture algebra and pedal gain. The plot preserves every exact state transition and uses complete min/max bins for continuous series, including final samples and spikes. It embeds the input hash and metadata, escapes XML and rejects oversized SVG before publication. | A plot does not authenticate its profile, rerun a scenario, establish oscillator recurrence, validate final audio algebra or supply a new physical capture. |
| Retained demo | Tests check retained artifact identities, independently calculate actual PCM statistics and windows, and exercise block partitions using the current coherent executables. | These checks do not require arbitrary cross-compiler bit identity or imply physical-model validation. |
| Session ledger | Checker validates this session, baseline, exactly 60 unique assignments in ten waves, canonical owner/slot pairs, bounded note paths and completed-note structure. Running work stays running; old sessions contribute no current completion credit. | A syntactically valid note cannot prove dispatch, substantive work, test execution or publication. Root must retain those observations separately. |
| Native inventory | Bounded traversal, regular-file admission, same-API stability checks, source identity selection, module header identification and no-clobber output were inspected and tested. The reparse repair below closes the concrete admission gap. | An inventory is a byte record, not a signature, host-load test, SDK license grant or distribution approval. |

The corresponding specifications are [render evidence](../PEDAL_RENDER_EVIDENCE.md),
[Unicode CLI behavior](../CLI_UNICODE.md), [trace plots](../PEDAL_TRACE_PLOTS.md),
[session checks](../PEDAL_SESSION_CHECKS.md) and [native CI](../VST3_CI.md).
Implementation anchors are the independent
[producer](../../tools/render_fixture.py) and
[verifier](../../tools/verify_render.py),
[plotter](../../tools/plot_pedal_trace.py),
[ledger checker](../../tools/check_pedal_session.py) and
[inventory](../../tools/native_bundle_inventory.py).

This review also reread atlas pages 355–360 from the retained text extraction.
Their separation of raw bytes, documentary interpretation, fitted model and
compiled runtime informed the evidence boundaries above. Assignment 51 does not
claim another complete PDF reading or a new visual review of generated plots.

## Reparse admission defect and repair

Before the repair, the root check used `Path.is_symlink()` and `Path.is_dir()`;
tree traversal and file reads accepted ordinary directory or regular-file mode.
Those tests do not express Windows reparse-point rejection. Python documents
[junctions separately from symbolic links](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.is_junction)
and exposes Windows
[file attributes in `stat` results](https://docs.python.org/3.12/library/os.html#os.stat_result.st_file_attributes).
The defect matters because a junction may lead outside the intended bundle
while retaining directory mode.

On the frozen pre-repair tool, three independent Linux probes added Windows
attribute `0x400` to fresh metadata for the root, a descendant directory or a
descendant regular file while preserving their real modes. **All three were
accepted.** These are synthetic Windows metadata probes; they are not evidence
that a Windows junction was created on Linux.

Root authorized changes only to
[the inventory tool](../../tools/native_bundle_inventory.py) and
[its tests](../../tests/test_native_bundle_inventory.py), plus this review and the
assignment note. The tool now checks `st_file_attributes` against
`FILE_ATTRIBUTE_REPARSE_POINT` immediately after fresh `lstat` at root admission,
tree-entry admission and regular-file admission. The last check also protects
the dependency lock, notices and source-manifest reads. Existing bounds,
same-API signatures, final-tree comparison, header recognition, schema and
no-clobber publication remain intact. Inputs must still be quiescent.

The new regression has separate root, directory and file subtests, with guards
that fail if the tagged selected path is traversed or opened. Its expected
negative control against the old production tool failed in all three subtests.
The same regression and the entire inventory suite passed against the repair.
The direct regular-file helper is also exercised, independently of traversal.

On Windows, the method additionally creates two real junctions with `mklink /J`:
a descendant junction to an external sentinel directory and a root bundle
junction. It checks the Windows attribute, confirms the alias is a junction
rather than a symbolic link, requires rejection, removes only the junction and
checks target bytes remain intact. Junction creation failure is a failure,
not a silently skipped Windows test. The platform-specific evidence is explicit:

```text
Linux observed:
reparse probes: root/directory/file metadata; actual Windows junctions not applicable

Required later Windows observation:
reparse probes: root/directory/file metadata and 2 actual Windows junctions
```

## Executed focused gate

Each command was taken from configured CTest JSON and run with that test's
`ENVIRONMENT`, using the frozen source and its matching compiled executables.
The Python interpreter was
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`.
`PYTHONDONTWRITEBYTECODE=1` prevented archive bytecode writes. Direct suite
execution avoided competing writes to root's CTest result directories.

| Frozen W8 suite | Methods | Reported seconds | Result |
| --- | ---: | ---: | --- |
| `test_render_fixture.py` | 28 | 5.048 | Pass |
| `test_verify_render.py` | 35 | 2.160 | Pass |
| `test_pedal_render_evidence.py` | 17 | 1.207 | Pass |
| `test_cli_unicode.py` | 11 | 0.902 | Pass |
| `test_pedal_trace.py` | 13 | 6.981 | Pass |
| `test_plot_pedal_trace.py` | 16 | 15.983 | Pass |
| `test_pedal_session.py` | 24 | 0.532 | Pass |
| `test_pedal_demo.py` | 10 | 1.933 | Pass |
| `test_native_bundle_inventory.py` | 19 | 0.224 | Pass |
| **Total** | **173** | | **No failures, errors or skips** |

The orchestration wall time was 36.528 seconds. The separately frozen repair
ran 20 methods in 0.444 reported seconds, without failures, errors or skips.
Zero skips on Linux does not mean the Windows-only junction operations ran.
The negative control was one method with three expected failing subtests in
0.004 reported seconds; its exit code was 1 as required.

For a later coherent build, CTest supplies the required executable/profile
environment automatically:

```sh
ctest --test-dir BUILD --output-on-failure \
  -R '^python_test_(render_fixture|verify_render|pedal_render_evidence|cli_unicode|pedal_trace|plot_pedal_trace|pedal_session|pedal_demo|native_bundle_inventory)$'
```

That command is a reproduction recipe, not an additional execution claimed by
this assignment. Exact executed paths and evidence hashes are in the
[assignment record](../development/2026-11-13-pedals/51-tools-evidence-audit.md).

## Actual native bundle comparison

Both the frozen original tool and the repaired private copy inventoried the
actual W8 Linux Release bundle. Each recorded four files totaling 444,239 bytes,
and their serialized reports were **byte-identical**:

```text
Report SHA-256:
b8e3d87f54c7ec7146032719476dc2cab7317c26a03b079f859cd5ee80fd01ea

Contents/x86_64-linux/HammondB3.so, 434168 bytes, mode 0755:
d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff
```

Both runs used the same locally observed source-overlay record, explicitly
marked as having no authenticated-build or physical-fidelity claim. Its presence
in the report identifies retained bytes; it does not associate the existing W8
module with the later Python repair. This comparison did not load the module or
repeat a native ABI test.

## Integration handoff

Root should freeze the approved repair in W9, qualify the coherent integrated
source, and inspect the actual hosted Windows junction result before reporting
that branch as passed. Keep its run/commit identity with the CI evidence. The
native CI documentation should explicitly include reparse points and junctions
when its owner updates the admission contract.

No further defect was established in the reviewed scope. Preserve the existing
separations between source identity, binary identity, artifact consistency,
physical evidence and completed-agent accounting. This review supplies no new
DAW, device, MinGW, signing, accessibility or physical-measurement result.

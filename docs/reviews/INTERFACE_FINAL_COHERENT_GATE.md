# Final interface coherent Release gate — A49

## Outcome

**The complete local gate is 146/147, with one workspace-replay assertion failure.**
All 147 freshly discovered tests executed exactly once; none was skipped or timed
out. CTest returned 8 after 525.60 seconds. A49 performed no retry and changed no
product source, fixture, assertion, timeout, CMake rule or workflow. The
[original complete log](../development/2026-11-14-interface-continuation/reports/a49-release-ctest.log),
[original JUnit](../development/2026-11-14-interface-continuation/reports/a49-release-junit.xml)
and [machine result](../development/2026-11-14-interface-continuation/reports/a49-final-result.json)
retain this failure. This is a completed qualification assignment with an open
software gate, not a full-pass claim.

The failing suite is `test_standalone_workspace_replay`, specifically
`test_synthetic_midi_and_ui_owners_survive_pointer_navigation_and_resize`.
Its first copied observation was at **191 ms**, while `assert_commands()` requires
a loaded-state observation before the first **180 ms** sound action. The original
native MIDI replay failure from the earlier UI gate is absent here: all twelve
native MIDI methods and 24 application processes passed in 30.47 seconds.
The distinct earlier [146/147 gate](../development/2026-11-14-interface-continuation/reports/root-ui-coherent-gate.json)
and its [targeted repair closure](../development/2026-11-14-interface-continuation/reports/root-ui-repair-closure.json)
remain unchanged.

## Exact source and protected boundary

The qualified build inputs equal published commit
`cdbb2beaa28bf136f9a8db6213819129514e2ae9`, tree
`b4d71c1f574ab17ba1a3f37b24667c1ff3f9c527`. HEAD retained that identity before and
after the gate. Concurrent README, gallery, assignment and evidence edits were
recorded separately; this was not a claim that the entire documentation worktree
was clean. The 98 production inputs also equal parent
`8673713a484c40e26ac7810c7c4cbc22fa874426`, connecting the final gallery/package
product bytes to this run.

Fresh snapshots were taken
[before configure](../development/2026-11-14-interface-continuation/reports/a49-source-before-configure.json),
[after the full build](../development/2026-11-14-interface-continuation/reports/a49-source-after-build.json),
[immediately before CTest](../development/2026-11-14-interface-continuation/reports/a49-source-before-ctest.json)
and [after CTest](../development/2026-11-14-interface-continuation/reports/a49-source-after-ctest.json).
All recorded qualification inputs and outputs remained byte-identical across
CTest, from 13:07:45 to 13:16:34 UTC on 14 November 2026.

| Inventory | Files | SHA-256 of sorted `path + NUL + file SHA-256 + LF` |
|---|---:|---|
| Source, tests, build rules and workflows | 327 | `f766a3e8fd545d9a8a68d23a54aca3de27f04d0d811138909b51e032bc858a20` |
| Production inputs used by A44/A46 | 98 | `ddf4f7658cfa9ed49ddac87902788c65531697551faab4dadd1dd57709d9e9ad` |
| Protected session boundary | 114 | `2c02e316388264e0e1738463e62762dfd106bb0fcc69eaef323a4a24133d7a49` |
| Supplemental retained-source/install inputs | 31 | `98468918a259b0e2201082df4c49c7c0ac2a0368b04f07136522b92c1d79a44a` |
| Built executable outputs | 82 | `f3272fec43d99d9d03dc2ee020b659b1cc30c8ac723a02ec2ac5848964500c8b` |
| Selected generated, archive and configuration outputs | 21 | `8f3b1663c4c4b04206f17ee4fe5f3a8041d56e5cdf11e0b8d9043a81c4aecbd9` |

The input inventories overlap; they are separate claim boundaries, not additive
product-file counts. The 31 supplemental paths extend the original 327-path set
with the source PDF, reference provenance/art, installed guides/notices and the
protected VST3 files. Selected dependency identities and pinned configure
verification are retained; this is not a universal system dependency graph.

All 114 files independently match both the
[A12 protected inventory](../development/2026-11-14-interface-continuation/reports/a12-boundary-inventory.json)
and baseline `d493e998e5dd7cf44db46854e87309745063ac54`: 44 core files, 29 data
files, six native audio/state files, eleven retained assets, four source/provenance
files and twenty VST3 files. There are zero mismatches in every group. This
preserves the 47-parameter registry, state4 and earlier readers, nominal model
inputs, source material and native VST3 boundary; it is not a new physical-model
qualification.

## Coherent cached build and test inventory

The build reused `../build-native`, pinned SDL2 2.32.10 and RtMidi 6.0.0, with
GCC 14.2.0, CMake/CTest 4.4.4 and Python 3.12.14 on Linux x86-64. Configuration
remained Release, standalone ON, MIDI ON, VST3 OFF and sanitizers OFF. SDL ALSA
was OFF; the separately compiled RtMidi backend retained `__LINUX_ALSA__` and its
existing ALSA development paths. Configure verified both pinned dependencies
without network acquisition or a fresh SDK build.

The [configure/build record](../development/2026-11-14-interface-continuation/reports/a49-prepare-result.json)
retains exact commands, tool versions, durations and raw logs. Configure took
2.13 seconds and the full incremental build took 3.40 seconds with **two workers**.
Nineteen targets were relinked; six test executables changed bytes:
`test_standalone_external_control`, `test_standalone_inspection_acceptance`,
`test_standalone_midi_session`, `test_standalone_projection`,
`test_standalone_workspace_continuity` and `test_standalone_workspaces_author`.
The [independent inventory comparison](../development/2026-11-14-interface-continuation/reports/a49-evidence-check.json)
retains their before/after identities. All 82 observed executable identities were
stable during the subsequent gate.

The application itself remained **3,707,640 bytes**, SHA-256
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`, identical
before configure, after build and after the gate. All 21 selected generated,
archive and configuration records also stayed unchanged through the rebuild.

Fresh [CTest discovery](../development/2026-11-14-interface-continuation/reports/a49-ctest-inventory.json)
contains exactly 147 unique names, and original JUnit contains those same 147
names exactly once:

| Existing suite family | Executed | Passed | Failed |
|---|---:|---:|---:|
| Core C++ | 45 | 45 | 0 |
| Python/offline/tooling | 64 | 64 | 0 |
| Standalone | 38 | 37 | 1 |
| **Complete combined Release** | **147** | **146** | **1** |

All 130 names in A40's separately configured SDK-free inventory are present,
alongside seventeen native-configuration additions. Their execution here belongs
to the combined native-enabled tree; A40 retains its separate SDK-free
configuration evidence.

CTest ran **serially**, matching the existing native CI policy. The earlier
workflow suite consumed 64.69 of its 90 seconds, so a parallel native timing
contract was not assumed. Ordinary workspace/scaled/preset raster limits remain
60/60/30 seconds; native MIDI/workflow/workspace replay limits remain 90 seconds.
There was no command-line timeout override, filtering, assertion change or retry.
The new native workflows result is 65.01 seconds with thirteen methods and 52
application processes.

## Failure evidence and bounded diagnosis

The [failure summary](../development/2026-11-14-interface-continuation/reports/a49-workspace-failure.json)
identifies the unmet fixture precondition without claiming a timing cause:

| Copied observation | Elapsed | Last applied | Resolved | Last submitted | Held notes |
|---|---:|---:|---:|---:|---|
| First retained loaded state | 191 ms | 3 | 3 | 4 | None |
| Final observed script state | 2,783 ms | 13 | 13 | 13 | None |

The first note was scheduled at 180 ms. Its sequence 4 was already submitted when
the first retained loaded applied sequence 3 was copied. The next fixture
assertion also requires the initial submitted sequence to equal the initial
applied sequence. Merely raising the 180 ms bound would therefore still fail
that equality and would not establish the intended startup barrier.

The failing native process returned successfully; schema/lifecycle, complete
control-path, complete held-note-path and exact five-On/five-Off assertions were
reached and passed before this assertion. The raw final replay is acknowledged
at sequence 13 with no held notes. The later ownership-window, MIDI-count,
view-path and saved-state assertions in this method were **not reached**. Their
raw diagnostic values do not substitute for a passing method. No timeout,
source drift or executable drift occurred, and the retained evidence does not
establish a lost note or sound-state mutation.

The original failed case is available without rerunning it:

- [UI input](../development/2026-11-14-interface-continuation/reports/a49-workspace-failed-input.b3ui)
  and [MIDI input](../development/2026-11-14-interface-continuation/reports/a49-workspace-failed-midi.b3midi)
  are copied from the original JUnit failure diagnostic.
- [Copied diagnostics](../development/2026-11-14-interface-continuation/reports/a49-workspace-failed-diagnostics.json)
  is the original reported JSON object, extracted and explicitly reserialized
  for inspection. The original full log and JUnit bytes remain untouched.
- [State from the source fixture](../development/2026-11-14-interface-continuation/reports/a49-workspace-state-from-fixture.b3controls)
  is the exact `FIXED_STATE` byte literal extracted from the identified fixture.
  It is not represented as the private runtime file, which unittest cleanup
  removed.

The original full log SHA-256 is
`0ae23075b4ce349880368ddb37d915ef7b2ecd741098667f0a10799a0f559e6c`;
original JUnit SHA-256 is
`b83a4a4ea597007602cdafd5b18cf48028e6161a136a40d35e79942692db0995`.

## Reproduction and handoff

Working directory was `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
The existing SDL2, RtMidi and ALSA roots named in the checkpoint are prerequisites.
The exact configure invocation is retained in
[a49-configure-process.json](../development/2026-11-14-interface-continuation/reports/a49-configure-process.json).
The essential subsequent commands were:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build ../build-native --parallel 2
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir ../build-native -C Release --show-only=json-v1
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONDONTWRITEBYTECODE=1 \
  /workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir ../build-native -C Release --verbose --output-on-failure \
  --no-tests=error --parallel 1 --output-junit <fresh-evidence-path>/ctest.xml
```

The last placeholder denotes a new evidence path; the preserved A49 outputs
must not be overwritten. The exact executed absolute command and original exit
status are in
[a49-release-ctest-process.json](../development/2026-11-14-interface-continuation/reports/a49-release-ctest-process.json).
The one-shot [A49 recorder](../development/2026-11-14-interface-continuation/reports/a49-coherent-gate.py)
refuses to overwrite its existing reports.

Root transferred the independent startup-baseline diagnosis and fixture-only
repair to A52 after receiving this failure. A49 released CPU and `build-native`
after its post-gate snapshot, supplied the exact retained case, and ran no
additional tests. A subsequent repair needs its own source identity and complete
affected-suite result while preserving command counts, ownership paths, timing
and original failed evidence. A49's complete result remains 146/147; any later
incremental closure is a separate record.

This gate uses dummy SDL and synthetic replay. It does not qualify physical
audio/MIDI devices, DAWs, desktop pointer capture, native semantic accessibility,
callback deadlines, literal image equality, specimen fidelity or a complete M9
release. Native VST3 and hosted platform results retain their separate evidence.
No compiled binary was added to Git; A49 staged and committed nothing.

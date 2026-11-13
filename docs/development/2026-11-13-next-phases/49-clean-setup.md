# Assignment 49 — fresh setup and relocation

- **Agent:** `/root/w09_a49_clean_setup`
- **Wave / actual assignment:** 9 / 49 of 60
- **Date:** 2026-11-13
- **Owned files:** this record and
  [`STANDALONE_CLEAN_SETUP.md`](../../reviews/STANDALONE_CLEAN_SETUP.md).
- **Frozen source:** public `649b12c7d1faa7601fde1019e913347c65a6634a`, tree
  `cf63327d857b02029e8c5c6f406cab3d3c6890d1`; byte-equivalent local commit
  `79094d86316b99a8b3614fb1f41ba81a1a69840f`.

## Work and evidence

Read the standing agent rules, operational handoff, install and dependency
contracts, actual CMake recipes and atlas pages 450–451. Waited for the
coordinator's exact committed checkpoint before creating any source archive or
build. Independently checked all 842 archived Git blobs and executable modes
against that tree before and after the build/test work. The live assignment-47
timing changes were excluded.

Created fresh private source, SDL, SDK-free build, native build, installation,
runtime-input and cwd paths containing spaces plus `é` and `音`. The pinned SDL
2.32.10 checkout came from a fresh non-hardlinked clone of the local cache and
passed the repository's verifier before and after building. Network acquisition
was not tested. Toolchain: GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14,
Make 4.4.1, Git 2.52.0, Linux x86-64/glibc 2.41.

The ordinary default build passed with standalone/VST3 OFF, an empty SDL root,
no configured C compiler and no SDL build directory. Eight selected core,
control, Unicode CLI, renderer, Session and benchmark CTests passed in
**8.39 seconds**. The actual documented renderer produced a valid 96,000-frame
stereo PCM16 WAV with identical dry channels and no clipping. This is a
selected setup gate, not a full 90-suite core result.

The fresh native `hammond_standalone_test_inputs` build passed, followed by the
complete required `^test_standalone_` group: **14/14 in 63.97 seconds**, no
skips or retries. Explicit chapel-catalog and benchmark target recipes work;
the benchmark executable is correctly located in `apps/standalone/`.
The chapel export matches the independent 293-byte literal upper-C# / A-bank /
0.75-expression control expectation. The benchmark records all 500 measured
intervals, exact accounting and the verified 57-input source fingerprint; it
applies no deadline threshold.

Installed exactly nine byte-matching files, then relocated the prefix and
renamed only private source/build/SDL directories so all original paths were
absent. Seven direct installed-executable invocations ran from a new Unicode
cwd with an empty PATH, no inherited HOME or library-path overrides, and
explicit dummy/software SDL drivers. Help, audio listing, default smoke,
keyboard replay, chapel-state smoke, Save/Load and a new-process state reload
all passed. The keyboard case observed the intended upper60/lower74/pedal17
ownership and upper72 continuation, with 4 accepted On / 4 Off commands.
Save/Load wrote the independent 290-byte state expectation; a new process
restored those controls with no held notes. All five window runs had actual
callbacks/frames, zero recorded errors/audio faults/recovery and clean stopped
state. The package remained unchanged.

The selected installed binary is 2,602,864 bytes, SHA-256
`f967f5fdab79e25d366d011b1f5e1fe719a8597f87265aa2d139a5c21079deed`.
ELF inspection shows no SDL shared dependency or RPATH/RUNPATH. It still needs
the system C++/C/math/unwinder libraries and references up to GLIBC 2.38,
GLIBCXX 3.4.32 and CXXABI 1.3.9. The detailed report retains exact commands,
source/package/input identities, actual runtime counts and compatibility
limits. Private raw evidence is under
`/workspace/scratch/5ba97739b54c/a49-clean-setup`.

## Findings and handoff

No source, CMake, test or recipe repair was needed for this Linux Release setup
scope. Only the two assigned reports were edited. No shared repository, shared
SDL directory, other worker build, ledger, commit or publication was modified
by this agent.

The coordinator should accept the report, preserve its exact frozen-source
boundary, update shared handoffs and publish the accepted documentation. The
next code qualification belongs to the completed timing repair and its
retained sanitizer failures; this Release pass does not supersede them. The
final full-core gate and hosted platform results remain with their assigned
owners. Physical-device/window behavior, deadlines, accessibility, network
acquisition, oldest toolchains and measured instrument fidelity remain
unqualified by this task. Use fresh build trees for later source checkpoints;
the intentionally moved CMake builds retain their original absolute paths.

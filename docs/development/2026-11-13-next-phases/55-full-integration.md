# Assignment 55 — final integration and sampled-workflow oracle repairs

- **Actual worker:** `/root/w10_a55_full_integration`
- **Wave:** 10 of 10; actual new assignment 55 of 60.
- **Execution:** 2026-11-13–14 UTC; continuation of the same assigned task.
- **Outcome:** original full Linux Release **105/105 passed**; original native
  ASan/UBSan **13/14 passed, chapel failed**; chapel-only changed-source native
  ASan/UBSan **13/14 passed, workflows failed**; both authorized test repairs
  passed focused Release and sanitizer checks, then the final native group
  passed **14/14** using verified existing instrumented outputs. No leak or
  physical-device claim.

## Ownership and source

Owned paths are `docs/reviews/STANDALONE_FINAL_INTEGRATION.md`, this note,
`apps/standalone/native_tests/test_standalone_chapel.py`,
`docs/CHAPEL_CONTROLS_ACCEPTANCE.md`,
`apps/standalone/native_tests/test_standalone_workflows.py` and
`docs/STANDALONE_WORKFLOWS.md`. Root explicitly extended the original
two-report ownership after the actual chapel and workflow failures. This worker
made no production, CMake, shared-status or ledger edits and no commit or push.

Original local commit `fa6df9d04916da8e23938cc3e85f524e3707e7d8` and public
`0085e338388f2c7516a7d455f11692b94e9451f4` have exact tree
`19c763503f67e1f054d2d27b6ec3d8fca2e36474`. All 894 Git blobs/modes remained
unchanged. The chapel-only repaired snapshot changes the maintained chapel
test (SHA-256 `18c645a30d6909ba331eac1f31abe71d9c8ccfe3c611278998f65f9ee5824323`)
and guide (`334de427be4f57bda85ab54c2181518b1ebd3f515425f29929a323870ccae695`);
its other 892 files and every compiled input are unchanged. Its inventory
SHA-256 is `120a814db7194030be88664d2686ba1f11a052953c2ef8a061b4f74854a86ce1`.
The final snapshot adds only the workflow test
(`982d76999592838689f0918f8bb937d68082514158b64c1c9bcd94eca3856428`) and guide
(`fda4fd6564fb263ee83c4014db730371fbfd33c8403a5ba0686381eeb72524d2`). Its other
890 files match original Git; final inventory SHA-256 is
`9f73fe9599f583692292a16dc2357cb877549819d3322667019913ce883763a0`.

## Executed evidence

The [full review](../../reviews/STANDALONE_FINAL_INTEGRATION.md) records exact
commands, builds, toolchain, artifact identities, all native timings, skip and
failure boundaries, nine installed-file checks, secondary SDL notice text
comparisons, instrumentation audit and next actions. Its private evidence root
is `/workspace/scratch/5ba97739b54c/a55-full-integration`; raw logs and binaries
were not added to Git.

The complete Release gate took 118.19 s; it ran 105 registered suites with no
CTest suite skips and two internal capture-audio Python fixture skips. The
first native sanitizer gate took 104.89 s and failed only the zero-expression
paired chapel case's exact UI-observation list. Later final-empty/Save-byte/
input-preservation assertions were not reached for that failed case, and the
old fixture did not retain full JSON. The original failure is preserved.

The repaired oracle checks literal accepted-command prefixes for every coherent
sample. Two bounded 650 ms paired endpoints require Lower's release to retain
Upper MIDI 60, independently of UI sampling during the original 100 ms release
interval. Original 700/900 ms scripts, complete control/count/acknowledgement/
state-byte assertions and timeouts remain; 22 exports/application runs now
cover all eighteen single rows and four paired cases. Post-invocation failures
retain up to 65,536 diagnostic bytes before cleanup.

Focused chapel Release and ASan checks each passed 2/2 methods and 22 real
application runs, in 19.526 and 23.466 seconds. Its subsequent fresh native
gate failed 13/14 in 115.05 seconds: chapel passed, but unchanged Help and
target/octave workflow methods failed exact sampled hold lists. Each failed
before its explicit final-hold/count/control/saved-byte assertions; those full
JSON records were also absent. Both failures and their assertion boundaries
remain retained.

The second authorized repair preserves original 2000/2600 ms scripts and adds
eight independent bounded endpoints for modal release/suppression/re-press and
all original note owners/releases/fresh octave. Literal command-prefix checks
require one device epoch, exact final acknowledgment, full controls and earliest
command times; bounded diagnostics now cover later assertions. Unaffected
workflow hold/control-path methods remain unchanged. The suite now has 11
methods / 25 actual processes, with its original 9 s/90 s budgets. Focused
Release/ASan runs both passed first, in 38.037/42.775 seconds.

The final complete native gate passed 14/14 in **117.28 s**, exit 0, without
disabled/skipped CTest suites or reported Python skips. Root authorized reuse
of the verified existing instrumented build: 213 objects, five archives, ten
runtime executables and generated inputs matched before/after. An isolated
CTest driver proved all fourteen registered commands/properties identical
except the frozen source substitution and explicitly preserved the originating
1500-second default timeout. No third instrumented build was needed or performed.
The state-file POSIX replacement-after-complete-write fixture remains explicitly
untested. Both instrumented builds verified 213
actual objects (19 core + 18 standalone/test/benchmark + 176 SDL C), five
archives and both linked sanitizer runtimes. No ASan/UBSan diagnostic appeared;
leak detection stayed disabled for assignment 42's established ptrace limit.

An original auxiliary compile-database audit initially resolved SDL output paths
from the wrong base; it failed before CTest. Resolving the actual compiler `-o`
against its working directory and independently checking CMake's build-relative
metadata fixed only that audit. No original build or gate was rerun. Assignment
59 separately reviewed the repair and failure retention; assignment 56 reused
the original Release app/profile/catalog read-only for the actual chapel demo.

## Handoff

Root owns final acceptance, shared status, combined-source checks and commit/
push. It reported publishing the exact final workflow test at
`6214032f3565f9e221fcf3988e33a22a73bb4ea8`. The later calibration advance
`955fc4c` and the separately reported Windows capture CLI/path-fixture repairs
are outside this freeze; assignment 58/root
own their evidence. Preserve the 105/105 and both failed 13/14 records alongside
the final changed 14/14 qualification. No broader Release suite was rerun by
this worker after the test-only repairs. Continue physical/native platform,
device timing, accessibility, leak and distribution gates with named inputs
and explicit acceptance criteria;
the nominal dry SDL dummy run does not close them.

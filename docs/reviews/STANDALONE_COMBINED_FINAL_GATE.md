# Combined standalone and calibration Release gate

## Result and exact source

On 14 November 2026 UTC, the integrator built a fresh, complete native-enabled
source archive and passed **110/110 registered CTest suites**, with zero failed,
disabled or skipped CTest suites. The test command took **130.339 seconds**.
One Python suite reported two internal capability skips; this is not a claim
that every platform-dependent Python method executed. The separate
[capture portability review](STANDALONE_CAPTURE_PORTABILITY.md) names and
retains those admission capabilities and its own executed outcomes.

The tested public revision is
[`183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e),
tree **`c2aee4e8ceb9bb945b255bb67388a7d6bab9f3f2`**. Its exact local equivalent
is `89c7f368660e62b059b763e164f5729565019ec4`, preserved on the local
`standalone-local-final-code-candidate` branch. Root published the same tree
with expected parent `955fc4c41f74ada094f14fbaf386c943811e9050`, fetched it,
compared both trees and verified an empty index before aligning local history.
No force update or deletion of concurrent work was used.

The archive contains **957 tracked regular files**. Every Git blob and executable
mode matched the named commit before and after all commands. The source tar is
SHA-256 `f99f3a2d51587979d4dfb2fe6c09beb34025d5d4fdd0f95960b9f90cffb1acfc`.
Build output, logs and the installed component are outside that source directory.
Every operation below ran once; no unchanged failed gate was retried.

This source preserves the calibration authors' `955fc4c` audio/corpus portability,
file-job, readiness, numerical/schema, study and synthetic-demo work. It adds
assignment 58's Unicode-path/StringIO regression and assignment 55's chapel
literal-prefix/held-endpoint test. The remaining general workflow-oracle repair
was not yet in this frozen source. Its later acceptance belongs to the
[final native integration report](STANDALONE_FINAL_INTEGRATION.md), not this
110-suite result. In particular, this Release pass does not erase either earlier
instrumented 13/14 result or imply a later ASan/UBSan pass.

## Environment and dependency identity

The actual local environment is Linux x86-64, glibc 2.41, GCC 14.2.0,
CMake/CTest 4.4.4, GNU Make 4.4.1 and Python 3.12.14. The generator is
`Unix Makefiles`, configuration Release, with native standalone ON,
VST3 OFF and `BUILD_TESTING=ON`. Global environment explicitly sets
`PYTHONDONTWRITEBYTECODE=1` and `LC_ALL=C.UTF-8`.

SDL is the existing external dependency at
`/workspace/scratch/5ba97739b54c/SDL2`, version 2.32.10, exact commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. Its official repository/version/
clean-tree/primary-license verification passed before configuration. The
application embeds the retained DejaVu 2.37 glyph atlases and nominal profile.
This container's configured native tests explicitly use SDL dummy audio/video;
the result does not establish an ALSA/Pulse/X11/Wayland device or desktop.

The resulting Release executable is byte-identical to the earlier 0085
demonstration executable: SHA-256
`def97cef70b3eafcd108170a985c61215b878c918debde6ff2fb236a2a9c3416`.
That observed equality supports continued use of the named
[actual chapel images](../../examples/demos/standalone-chapel-v1/README.md).
Their original capture source, timings and diagnostic bytes remain unchanged;
no new screen capture is attributed to this build.

## Actual commands and outcomes

The private evidence root is
`/workspace/scratch/5ba97739b54c/final-combined-gate`.
The frozen source and build are its `source` and `release` subdirectories.
The actual CMake/CTest binaries are under
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin`;
this existing toolchain was used read-only. No other checkout was modified.
Every command's working directory was the frozen source.

The following portable shell spelling reproduces the arguments. Replace the
three absolute directory values and use the recorded toolchain when comparing
exact bytes; its `cmake`/`ctest` executables are the commands denoted below.

```sh
HAMMOND_GATE_SOURCE=/absolute/path/to/frozen/source
HAMMOND_GATE_BUILD=/absolute/path/to/new/release-build
HAMMOND_GATE_SDL=/absolute/path/to/pinned/SDL2
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C.UTF-8

python3 -B "$HAMMOND_GATE_SOURCE/tools/acquire_sdl2.py" \
  --verify-existing "$HAMMOND_GATE_SDL"
cmake -S "$HAMMOND_GATE_SOURCE" -B "$HAMMOND_GATE_BUILD" -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_SDL2_ROOT="$HAMMOND_GATE_SDL"
cmake --build "$HAMMOND_GATE_BUILD" --config Release --parallel 2
ctest --test-dir "$HAMMOND_GATE_BUILD" -C Release --show-only=json-v1
ctest --test-dir "$HAMMOND_GATE_BUILD" -C Release --parallel 2 \
  --output-on-failure --no-tests=error -V --output-junit /new/path/release-junit.xml
cmake --install "$HAMMOND_GATE_BUILD" --config Release --component Standalone \
  --prefix /new/path/installed
python3 -B "$HAMMOND_GATE_SOURCE/tools/check_repository.py" \
  --root "$HAMMOND_GATE_SOURCE" --json
```

| Actual operation | Exit | Elapsed seconds |
| --- | ---: | ---: |
| Verify pinned existing SDL | 0 | 0.084 |
| Configure fresh Release | 0 | 21.594 |
| Build every default target | 0 | 137.431 |
| Discover registered tests | 0 | 0.026 |
| Execute all 110 suites | 0 | 130.339 |
| Install explicit Standalone component | 0 | 0.049 |
| Check frozen source integrity | 0 | 1.389 |

The registered test list and JUnit testcase count both equal 110. JUnit contains
no failure or skipped testcase. The source-integrity check passes **554 Markdown
files / 3,066 local links**, 80 atlas chapters, ten research waves and six
complete reader ranges. It verifies the unchanged 500-page, 21,248,265-byte PDF,
SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The repository checker's original sixty-note consistency check belongs to the
original session; it does not certify this new session's completion. Root owns
the separate final `check_standalone_session.py --expected-complete 60` gate.

The installed payload has exactly the documented nine regular files: one
`bin/hammond_standalone` executable plus the app/install/model guides, combined
third-party notices, SDL and DejaVu notices, dependency lock and font-source
manifest under `share/hammond-b3-organ/standalone/`. This install invocation
is distinct from earlier clean-setup/relocation and later actual hosted-artifact
execution. It does not claim a physical audio device or a clean operating system.

## Retained private log identities

The exact command records, source inventories, JUnit, registry and logs remain
in the named evidence root. The table identifies the observed bytes; the commands
above and committed sources permit fresh reproduction without treating an old
log hash as a new test execution.

| Log | Bytes | SHA-256 |
| --- | ---: | --- |
| `01-dependency.log` | 287 | `58329939cb29baad77f1760b2db675e5e334ae0e064d7f253409af16582088a6` |
| `02-configure.log` | 22,976 | `1e2384e85061d32202bd0c1e8b467fcc9747647942f0ece2b6c1fd0cda105756` |
| `03-build.log` | 33,530 | `cd28f1e507b777315bf033336b17511c52a8f029acdeed98aa159306a777ebaa` |
| `04-registry.log` | 123,091 | `1f2016f9cefe013ec011ef140e6ca7403702c37b171538c13814098579c3fb6e` |
| `05-complete-tests.log` | 178,767 | `d4d01aee6b78965d9d4be68e61749cfbba867f81f577edecae652505a422e6c9` |
| `06-install.log` | 1,148 | `ae2f279ba42393313195cc4671783beca27717a90defe109c79f099182ee1d3f` |
| `07-source-integrity.log` | 1,163 | `2b5016eb4192c4c67094d9f481619a86950c7c5f87264b1132357750e642ba15` |

## Remaining acceptance boundary

The exact-source hosted workflows and downloaded artifact audit are independent
platform evidence. The later workflow observation repair requires its own
changed-source focused/native instrumented result and hosted execution. Keep
all original failures and actual capability skips. Physical devices/controllers,
latency/underruns, actual DAWs, native accessibility, signing and measured
Hammond/AO-28/Leslie fidelity remain open product and acquisition gates.

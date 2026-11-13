# Agent 09 — portable build foundation

## Scope and inputs

- Owned only `CMakeLists.txt`, `CMakePresets.json`, `Makefile`,
  `tests/TestSupport.h`, `docs/BUILD.md`, and this note.
- Read AGENTS, README, STATUS, NEXT_STEPS, PLAN, DEVELOPMENT_LOG,
  IMPLEMENTATION_CONTRACT, PROFILE_FORMAT, Types/Profile headers and relevant
  agent06 milestone review. `docs/research/ATLAS_REVIEW.md` was absent.
- Branch was `main`; existing staged and concurrent work was preserved.
- Coordinated compiler CLI with agent08 and helper API with agent10.

## Delivered behavior

- CMake 3.21+, C++20, Python 3.10+; no external dependencies or downloads.
- `hammond_core` is a static library; CONFIGURE_DEPENDS discovers `src/*.cpp`,
  `tests/test_*.cpp`, `tests/test_*.py` and optional `tools/render.cpp`.
- `hammond_profile` invokes the validated authoring compiler and generates
  `<build-directory>/nominal.b3p`. Tests and the optional renderer depend on it.
- Each C++ test has its own main, core link, test includes, quoted profile/source
  path definitions; each Python test script is registered with CTest.
- `check` builds prerequisites and runs CTest, failing if no tests exist.
- GCC/Clang warnings include conversion/sign/shadow checks and are errors;
  MSVC uses /W4 /WX. ASan+UBSan is opt-in with a compile/link support probe;
  unsupported drivers fail clearly. Debug/release/sanitizer presets are separate.
- Make exposes build/test/profile/clean with CMAKE and build-path overrides;
  clean delegates to the selected generated clean target, with no recursive rm.
- CHECK and CHECK_NEAR remain active under NDEBUG, evaluate arguments once,
  print file/line, and terminate with failure. Approximate checks reject
  non-finite inputs and invalid tolerances. Global load_test_profile uses loader.

## Executed evidence

The CMake/CTest executable prefix was
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`.
Environment: Linux, GCC14.2.0, GNU Make4.4.1, Python3.12.14, CMake4.4.4.

1. `cmake --preset debug`: passed.
2. `cmake --build build --target hammond_core hammond_profile --parallel 2`:
   passed; Profile.cpp compiled with strict warnings and profile generation ran.
3. `cmake --preset sanitizers`: ASan+UBSan compile/link probe passed.
4. `cmake --build build-sanitizers --target hammond_core hammond_profile --parallel 2`:
   passed; core instrumentation compiled and linked as a static archive.
5. `make profile CMAKE=<absolute-cmake-path>`: passed, override honored.
6. `ctest --list-presets`: accepted debug, release and sanitizers presets.
7. `git diff --check`: passed on the existing tracked diff.

Generated nominal profile authoring digest:
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
No source data was modified by this agent; agent08's compiler/data unblocked
the build during the assignment.

## Limits and next handoff

- No C++/Python test script existed at initial integration. Agent10 is adding
  test_profile.cpp; the integrator will run CTest after it appears.
- No sanitizer runtime test, Release build, renderer build, macOS/AppleClang,
  Windows/MSVC, unsupported-driver rejection or clean execution is claimed here.
- Engine/TonewheelBank/renderer sources were not present during the build smoke;
  their arrival requires integration compile and runtime verification.
- Python CLI tests needing the renderer should receive an explicit executable
  path (e.g. HAMMOND_RENDER_EXECUTABLE) when that target is introduced.
- No commit, push, host qualification or physical-fidelity claim was made.

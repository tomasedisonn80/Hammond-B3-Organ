# Hosted baseline macOS repair

The documentation checkpoint `70b335480323329c7f5b207d5f58086c5b854960`
kept production code equal to `b79086f`. Its actual macOS standalone job
[132381932020](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43573251561/job/132381932020)
failed while compiling `InstrumentView.cpp` under AppleClang with strict warnings.
The diagnostic identifies an unused private color constant, `kDark`.

The integrator removed that unreferenced declaration. No drawing, input, audio,
parameter or state behavior changes. The separate in-progress preset implementation
was excluded from this repair checkpoint.

## Evidence

```text
2026-11-14T07:56:53.7644120Z [100%] Building CXX object apps/standalone/CMakeFiles/hammond_standalone.dir/InstrumentView.cpp.o
2026-11-14T07:56:53.7648140Z cd /Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/build-standalone/apps/standalone && /usr/bin/clang++ -DSDL_MAIN_HANDLED -I/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/build-standalone/apps/standalone/generated -I/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/apps/standalone -I/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/include -I/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/build-standalone/_sdl2/include -I/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/build-standalone/_sdl2/include/SDL2 -I/Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/build-standalone/_sdl2/include-config-release/SDL2 -O3 -DNDEBUG -std=c++20 -arch arm64 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -MD -MT apps/standalone/CMakeFiles/hammond_standalone.dir/InstrumentView.cpp.o -MF CMakeFiles/hammond_standalone.dir/InstrumentView.cpp.o.d -o CMakeFiles/hammond_standalone.dir/InstrumentView.cpp.o -c /Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/apps/standalone/InstrumentView.cpp
2026-11-14T07:56:55.1328740Z /Users/runner/work/Hammond-B3-Organ/Hammond-B3-Organ/apps/standalone/InstrumentView.cpp:12:19: error: unused variable 'kDark' [-Werror,-Wunused-const-variable]
2026-11-14T07:56:55.1329910Z    12 | constexpr UiColor kDark{16, 17, 15};
2026-11-14T07:56:55.1330510Z       |                   ^~~~~
2026-11-14T07:56:55.1675250Z 1 error generated.
2026-11-14T07:56:55.1721530Z make[3]: *** [apps/standalone/CMakeFiles/hammond_standalone.dir/InstrumentView.cpp.o] Error 1
2026-11-14T07:56:55.1723300Z make[3]: *** Waiting for unfinished jobs....
2026-11-14T07:56:55.7210390Z make[2]: *** [apps/standalone/CMakeFiles/hammond_standalone.dir/all] Error 2
2026-11-14T07:56:55.7242450Z make[1]: *** [apps/standalone/CMakeFiles/hammond_standalone_test_inputs.dir/rule] Error 2
2026-11-14T07:56:55.7269410Z make: *** [hammond_standalone_test_inputs] Error 2
2026-11-14T07:56:55.7484400Z 
2026-11-14T07:56:55.7659800Z ##[error]Process completed with exit code 2.
2026-11-14T07:56:55.8074500Z ##[group]Run actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9
2026-11-14T07:56:55.8074990Z with:
2026-11-14T07:56:55.8075430Z   name: standalone-macos-15-ARM64-midi-ON-release-diagnostics-70b335480323329c7f5b207d5f58086c5b854960-1
2026-11-14T07:56:55.8075970Z   retention-days: 14
```

An initial syntax-only attempt against the changing worktree encountered the
expected temporarily inconsistent 47/45 parameter assertion. It was not a valid
baseline compilation and does not qualify the repair. A fresh source copy from
the published checkpoint then isolated `include/` and `apps/standalone/` with
the unchanged prepared SDL/generated headers. GCC syntax-only checks both returned
zero because that mode did not emit the unused-constant diagnostic. Actual strict
GCC14.2 object compilation with `-Wunused-const-variable=2` reproduced the original
failure, then passed after removal. The [complete command/results](reports/baseline-macos-compile.json)
retain both stages. No older compiled core was linked to changing headers.

The local object check is not a macOS execution claim. The next guarded publication
triggers hosted AppleClang qualification; its observed result must be recorded
before closing the platform failure. The SDK-free and VST3 baseline jobs observed
so far passed; the remaining workflow results retain their own identities.


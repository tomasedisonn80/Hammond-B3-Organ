# Hosted preset concurrency portability repair

The first feature checkpoint `1c06a09fbbac543e521be9c4955cd2e1e06a4197`
reached actual hosted Linux, Windows and macOS builds. All three native VST3
jobs passed. The macOS core and standalone jobs failed before runtime acceptance.
The independently retained [complete core job log](reports/feature-macos-core-build-failure.txt)
identifies unavailable `std::jthread` and `std::stop_token` in
`test_standalone_preset_concurrency.cpp`, followed by their dependent compiler
errors. The supported Apple standard library already has a documented portable
replacement in `test_standalone_concurrency.cpp`.

The new preset test now uses that same local `std::thread`/atomic stop-token
ownership pattern. Destructor stop-and-join remains exception safe, including a
second worker's construction failure. Explicit joining, all release/acquire
operations, control stamps, finite guard, queue recovery, musical continuation
and rejection assertions remain unchanged. No application or core behavior,
timeout, expected result or hosted gate was relaxed.

## Local affected verification

The corrected test was copied to a fresh private path and compiled once with
GNU C++ 14.2 and all existing strict warning flags against the unchanged matching
A31 headers and runtime archives. Compilation and execution both returned zero.
The [command record](reports/feature-portability-local.json),
[compile output](reports/feature-portability-compile.txt) and
[complete test output](reports/feature-portability-test.txt) preserve the run.

The run accepted three rates, 192 controlled pending checks, 3,264 restores,
six queue recoveries, 1,536 discarded restores, 24 rejected calls, and 2,292 exact
nonzero stereo continuation samples. Concurrent callback/reader counts remain
scheduler observations rather than portable equality requirements. This direct
one-test execution is not a complete CTest run or an AppleClang execution.

## Published-platform follow-up

Publish this bounded repair, then inspect the new hosted macOS build and actual
native replay result. The prior modal Escape timeout remains unclassified until
that runtime path executes and its schema-3 completion diagnostics are available.
The first feature run's build failure supplies no new modal result. Keep original
failures and separate source identities when later jobs succeed.

Observed source jobs:

- [Core macOS job 132403276913](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43580266029/job/132403276913)
- [Standalone macOS job 132403276773](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43580266074/job/132403276773)

The complete log was copied after a first transport attempt exceeded the operating
system's command-argument limit; chunked file writes completed without rerunning
or changing any project test. This infrastructure error is not a compiler/test
result.

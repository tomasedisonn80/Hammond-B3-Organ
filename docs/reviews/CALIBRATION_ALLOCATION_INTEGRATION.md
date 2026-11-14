# Metadata allocation integration

## Qualified source

The accepted assignment-43 optimization and assignment-44 independent
acceptance pass **15/15 capture CTest suites in 37.43 seconds** from a fresh,
immutable source archive. The independent acceptance separately passed 357
methods across seven suites without skips. These are distinct counts and runs.

| Identity | Value |
| --- | --- |
| Local frozen commit | `459bfacbda90005d618f12c4513b9c71cb11193d` |
| Exact Git tree | `3325af558b040759c1b432ec0806a80785af9713` |
| Equivalent GitHub source object | `d377fab7a840dc6d7a499fdf576d0dd8bb5dd4c1` |
| Last verified published parent | `3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf` |
| Corpus SHA-256 | `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded` |

Root inspected the minimal production diff, frozen protocol and producer and
independent reviews before accepting assignments 43/44. The source commit records
44 accepted workers and three running workers. It excludes the still-running
graph acceptance and subsequent stdout/stderr delivery repair. The GitHub source
object has the same complete tree and is retained separately from later records
and publication; object creation alone is not a branch update.

## Behavior and retained evidence

After existing descriptor binding and inclusive size admission, the confined
reader requests the observed descriptor size plus one instead of the maximum
allowed byte cap plus one. The extra byte, exact-length check, descriptor and
path/parent stamps, original bytes and cleanup paths remain unchanged. The
independent [acceptance review](CALIBRATION_METADATA_ACCEPTANCE.md) retains reached
growth, truncation, replacement, cancellation and cleanup checks and all outcomes.

The [controlled experiment](CALIBRATION_METADATA_ALLOCATION.md) retains its
predeclared protocol, two complete source inventories, both original reports and
all samples. Its isolated 119,423-byte read peaked at 16,785,861 traced bytes
before and 128,603 after in each of three calls. Complete fresh study replay
peaked near 16.79 million before and 1.305 million after. This is Python traced
allocation on the fixed local workload, not RSS, latency or a universal bound.
The old report under changed sources correctly remains a mismatch; a fresh
same-source replay still matches its failed engineering result. No original
report is rewritten and no public source field is excluded from equality.

## Actual integration gate

The fresh source is `/workspace/scratch/c9f3ead4c910/w8-allocation-source`,
with a separate `/workspace/scratch/c9f3ead4c910/w8-allocation-build`.
CMake/CTest 4.4.4, CPython 3.12.14 and GNU C++ 14.2.0 were observed on Linux
x86_64. The actual configure and filtered execution were:

```sh
cmake -S /workspace/scratch/c9f3ead4c910/w8-allocation-source -B /workspace/scratch/c9f3ead4c910/w8-allocation-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
ctest --test-dir /workspace/scratch/c9f3ead4c910/w8-allocation-build -R '^python_test_capture_' --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w8-allocation-ctest.xml
```

The exact executables were `cmake` and `ctest` under
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin`.
The selected fifteen pure-Python suites need no native target build; their
package fixtures perform their own required configuration and installation.
No unselected C++ executable or native integration is claimed by this gate.
The earlier [103-suite integration](CALIBRATION_INSTALL_REPLAY_INTEGRATION.md)
remains separate source-qualified evidence.

| Log under scratch `checks/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `w8-allocation-configure.log` | 708 | `ead9c70c8801689fa1d1dc680c813f73b01a9b9bf6e78562d20a40f05eea4d2f` |
| `w8-allocation-ctest.log` | 1,975 | `53d2befa708031b99e2740b2b0b13c58692bc1a217730ac429de1d5c4bb5a90f` |
| `w8-allocation-ctest.xml` | 6,013 | `d1111bc3b3d8da2ce33c89b9927fde450bea8ded7751f06f846189f964c88ec8` |

CTest reports zero failing, disabled or skipped suite entries. Nested audio
capability skips remain explicitly disclosed in the admission evidence; a
passed CTest entry does not imply every nested platform capability exists.

## Next dependency

Assignment 46 subsequently reproduced actual closed-pipe CLI finalization
failures. Those are separate from the bounded-reader optimization. Assignment
47 owns a minimal delivery repair under independently frozen exact-exit and
failure-preservation criteria, including legacy validator dependency closure.
Do not attribute its changed sources or future tests to this earlier gate.
Continue the real remaining assignments and publish accepted coherent changes
with guarded updates, preserving all original failures and source identities.

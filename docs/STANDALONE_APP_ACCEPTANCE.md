# Native executable acceptance

[`test_standalone_app.py`](../apps/standalone/native_tests/test_standalone_app.py)
executes the actual linked [`hammond_standalone`](STANDALONE_APP.md). Python uses
only its standard library; SDL, application events, rendering and callback
processing are real. The independent [audio matrix](STANDALONE_AUDIO.md),
[Session](STANDALONE_SESSION.md), [UI](STANDALONE_UI.md) and
[control-file](CONTROL_STATE_FORMAT.md) tests retain their separate coverage.

## Run the required native gate

Acquire the exact [pinned SDL2 checkout](STANDALONE_DEPENDENCY.md), configure
with `HAMMOND_BUILD_STANDALONE=ON` and `BUILD_TESTING=ON`, then build and test:

```sh
cmake --build build-native --config Release --target hammond_standalone --parallel 3
ctest --test-dir build-native -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_app$' -V
```

CTest supplies `HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>`
and the configured Python interpreter. The entry exists only in the enabled
native testing configuration, has `standalone;native` labels and a 60-second
timeout. A direct POSIX invocation is:

```sh
HAMMOND_STANDALONE_EXECUTABLE=/absolute/path/to/hammond_standalone \
  python3 apps/standalone/native_tests/test_standalone_app.py
```

A missing environment variable, missing binary or nonexecutable file fails
setup. There is no optional-binary skip. Every application subprocess explicitly
selects `SDL_AUDIODRIVER=dummy` and `SDL_VIDEODRIVER=dummy`, except the deliberately
invalid driver cases. All state/output paths and working directories belong to
private `TemporaryDirectory` trees. An explicit `--state` keeps these runs away
from user preferences. Individual subprocesses have 3- or 8-second timeouts;
Python kills and joins a subprocess on timeout.

## Maintained cases

The Linux execution currently contains **18 methods / 164 app subprocesses**:

| Cases | Count | Required observation |
| --- | ---: | --- |
| Help and audio listing | 3 | Help succeeds with both drivers invalid; listing succeeds with video invalid; no file changes. Leading decimal zeroes remain accepted. |
| Invalid CLI | 129 | Unknown/combined options, every duplicate and missing/empty value, signed/whitespace/fraction/exponent/hex/partial/non-ASCII integers, overflow and unsupported ranges return 2 before SDL or writes. |
| Successful 600 ms smokes | 8 | Reference/minimum windows, two extreme rate/buffer pairs, all three saved-state versions, malformed-state audition fallback. |
| Runtime failure smokes | 3 | Invalid audio driver, screenshot write failure and diagnostic write failure return 1 within the bound and preserve musical files. |
| Filesystem admission failures | 21 | Direct/lexical/hardlink collisions, absent-leaf parent aliases, state/output symlinks and output directory leaves return 1 without mutation. |

The four configuration runs are default **1280×900 / 48000 Hz / 512 frames**,
**960×700 / 48000 / 512**, **1280×900 / 44100 / 2048**, and
**1280×900 / 96000 / 128**. The separate device suite owns the complete 15-pair
matrix. Unicode and spaces occur in native state, screenshot and JSON paths.

Diagnostics must be complete strict JSON with no duplicate keys, nonfinite
tokens, missing/extra schema-1 fields or Boolean-as-integer substitutions.
Assertions cover the actual frozen nominal profile ID/authoring digest, SDL
version, array dimensions, every control class, requested/obtained native
float32 stereo format, byte size, callbacks, frames and final Session clock.
Copied publication/sequence/discard counters must agree; shutdown is stopped
and has no held notes. Before shutdown the successful device must be open and
running; press, hold and release must all have been observed.

BMP validation checks signature, file/DIB bounds, dimensions, bit depth, row
payload and multiple sampled colors. Successful screenshots must report capture
while held. Tests compare structural/rendered evidence, never golden image bytes
or exact scheduler-dependent callback/image counts. Elapsed time uses a monotonic
clock with broad bounds. A deliberately cancelled saved upper manual stays
silent while its smoke note is still held/released successfully.

Startup fixtures independently specify all retained control classes and v1/v2
migrations. Their noncanonical whitespace remains byte-identical after exit;
missing state stays absent. A late-invalid state preserves the entire file and
the complete proposed audition controls, while reporting the startup error.

Actual hardlinks and a real aliased parent are required. Windows tries a
directory junction if a directory symlink lacks privilege; the output names the
kind used. A Windows file-symlink privilege error explicitly reports those leaf
cases as skipped and leaves that gate unexecuted. No such skip occurred on
Linux. These are stable-filesystem checks, not concurrent path-replacement or
security guarantees.

## Executed evidence and remaining gates

The [assignment report](development/2026-11-13-next-phases/24-app-acceptance.md)
retains actual commands, hashes, passing counts and the repaired alias defect.
The automated event path covers one scancode note and startup restoration.
Native modal navigation, pointer capture/focus/resize, explicit Save/Load,
reopen/hotplug/watchdog interactions, visible desktop and high-DPI operation
remain separate acceptance work. Windows/macOS, physical audio, latency/xruns,
assistive technology, distribution and acoustic fidelity are not established by
dummy-driver execution or BMPs.

# Assignment 14: retained percussion controls and state migration

Agent: `/root/w03_a14_control_migration`; continuation wave 03.
Reviewed working-tree base: `5dcd94292fbd5af61b5bf3bb7e06a1f5f2c4f181`.

## Scope and implementation

Owned changes are `ControlState.h/.cpp`, `ControlStateIO.h/.cpp`,
[CONTROL_STATE_FORMAT.md](../../CONTROL_STATE_FORMAT.md), and this note.
The parent owns shared status, integration, permanent independent tests and
publication. No Engine, event, CMake, parameter registry or old test was edited.

Published the retained API first and notified the engine integrator:

- `ControlSnapshot::percussion` defaults to Off/Second/Normal/Slow.
- `percussion_settings()` returns a copied control value.
- `set_percussion_settings()` validates the complete settings before assignment.
- Whole-snapshot validation and restoration now include every percussion enum.
- Bank selection, Cancel and hidden-bank edits retain percussion controls.

Serialization now emits canonical `B3CONTROLS2`. Its mandatory nine-token
percussion record follows expression and precedes the existing ordered manual
blocks. Booleans are exactly `0`/`1`; enums use their lowercase named tokens.
Version 2 contains 69 tokens. The old `B3CONTROLS1` grammar remains readable
with its original 60 tokens and receives explicit percussion defaults from a
fresh candidate, regardless of the destination's prior settings. Re-saving emits
version 2. Version-1 extensions, missing version-2 settings and future versions
reject rather than silently erasing or inheriting controls.

The 16 KiB inclusive bound, bounded input read, canonical LF, classic-locale
numeric conversion, signed-zero preservation, original stream-error handling,
validation-before-publication and serializer string-alias rule remain intact.
The format contains retained musical controls only. It excludes contacts,
readiness, source phase, keys, clock and every other dynamic DSP history.

These choices implement the separation in atlas pp. 151-156, 389, 394 and 401
and the frozen [console contract](../../CONSOLE_DYNAMICS.md). No physical data,
native-host format or complete instrument patch is claimed.

## Executed checks

A focused independent scratch executable compiled and ran successfully with
GCC 14.2, C++20, optimization and the repository's full strict warning set:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude /workspace/scratch/60e8291da354/agent14-check/control_smoke.cpp src/ControlState.cpp src/ControlStateIO.cpp -o /workspace/scratch/60e8291da354/agent14-check/control_smoke
/workspace/scratch/60e8291da354/agent14-check/control_smoke
```

Observed result: **96 exact round trips**, covering all 16 percussion combinations
and six expression values including negative zero and the smallest subnormal;
**145 atomic malformed-text rejections**; and **nine invalid enum cases** checked
through snapshot validation, restoration, the direct setter and serialization.
The scratch check also confirmed:

- An unchanged historical v1 record loads its old controls and overwrites the
  caller's nondefault percussion with the explicit migration defaults.
- V2 serialization is canonical and stable after parsing; its token count is 69.
- Every strict token-prefix truncation and each individually invalid token reject.
- Missing v2 percussion, v1 with extra percussion, unsupported values and trailing
  data leave the complete destination unchanged.
- Exactly 16,384 bytes including padding are accepted; the next byte rejects.
- Bank selection, Cancel and hidden edits retain percussion settings.
- Invalid serialization preserves prior bytes; aliased strings remain untouched.

`python3 tools/check_repository.py` passed all five archive consistency checks,
and `git diff --check` passed.

The scratch source is intermediate execution evidence, not a new permanent test
suite. Independent retained migration tests belong to assignment 17. Existing
`test_control_io` has historical v1 canonical-output assertions and 60-token
mutation positions. Preserve its v1 fixtures as immutable migration inputs while
adding v2 expected serialization and separate 69-token cases; do not discard the
old malformed-input coverage or weaken it to accept arbitrary versions.

Tested source identities (SHA-256):

| File | Hash |
| --- | --- |
| `include/hammond/ControlState.h` | `88f22e3c6c6ad4a7cca756ba2e29c2822fa344f78cfb9269c1e5090a7fe7c31a` |
| `src/ControlState.cpp` | `7b49116640c1f466f655e166683f84e1561402976ca92c06d01feef88e66607c` |
| `include/hammond/ControlStateIO.h` | `0633183e3944a3932ebf77c5bc1f4512ed05b0de0607a392697ba557014e2fa7` |
| `src/ControlStateIO.cpp` | `3e19506731f7da43f21f91bdb865efc701f40a7dac9c26a34dbaa80bda47b05b` |
| Intermediate smoke source | `1b7bf341ae5ba43bc4e4ff2456041b45a90bf718e807507b1776203f3f2a83ef` |

No combined-engine, full CTest, sanitizer, hosted-platform, host/device or physical
result is claimed by this assignment. Engine restoration preserving live contact
and readiness histories is an independent integration gate. No commit or push
was attempted by this agent.

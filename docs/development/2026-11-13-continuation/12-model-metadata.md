# Assignment 12: compiled console factory metadata

Agent: `/root/w02_a12_model_metadata`; continuation wave 02.

## Owned changes

- `tools/model_info.cpp`: offline `hammond_model_info` exporter using actual
  `make_legacy_console_model()` and `make_nominal_console_model()` values.
- `CMakeLists.txt`: only the new target, its focused test environment variable
  and the `check` target dependency.
- `tests/test_model_info.py`: seven focused methods against the actual executable.
- `docs/MODEL_METADATA.md` and this note: format, provenance, scope and results.

No core, shared status, event, persistence or renderer files were changed by this
assignment. Read the standing instructions, current handoff, full model APIs and
console contract before implementation. The inherited full atlas reviews supply
source coverage; this assignment does not claim another full-PDF reading.

## Format and evidence decisions

Version 1 exports both factories, each with two explicit 61-key arrays and nine
on/off thresholds per key. It reads every threshold, duration and percussion
parameter from the C++ objects; the exporter does not duplicate their numerical
initializers. Defaults come from an actual `PercussionSettings` value. Modes and
algorithm IDs stay distinct from custom parameter identities and live DSP state.

Source-generator tuning, amplitudes, phases and routing are explicitly excluded;
they require the independent `RuntimeProfile`. Contact values are proposed,
percussion RC products derived hypotheses, and gain choices proposed. Units, atlas
pages and explicit missing-evidence explanations accompany these values. Nothing
is labeled measured. The metadata does not establish a complete AO-28 circuit,
physical fidelity, host qualification, runtime behavior or artifact authenticity.

JSON is constructed after factory validation at all three supported rates, with
classic locale, `max_digits10`, stable ordering and final LF. The complete document
must be smaller than 128 KiB before stdout is written. Windows selects binary
stdout to prevent CRT newline translation. Output errors return failure; a shell
redirection does not acquire the renderer's no-clobber guarantee.

## Executed verification

Toolchain: GCC 14.2.0, Python 3.12.14 and CMake/CTest 4.4.4. Build directory was
outside the repository at `../model-info-build`.

```sh
cmake -S . -B ../model-info-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../model-info-build --target hammond_model_info -j 3
ctest --test-dir ../model-info-build -R '^python_test_model_info$' --output-on-failure
```

The initial strict CMake build and focused CTest passed. All seven Python methods
also passed directly: strict schema/no duplicate or nonfinite JSON, the separate
generator boundary, all 1,098 contact positions per factory, units, independently
derived decimal thresholds and RC/gain expectations, actual settings defaults,
repeatable output under three locale environment values, strict CLI arguments,
and a real `/dev/full` output error.

Observed JSON size: **105,377 bytes** for **244 key rows and 2,196 contact
positions** across the two factories. SHA-256 for this GCC build's output:
`22b4b3d01719aae9bdc258498cd3b743dc9345be91fb074f40892fe6b432f364`.
This is a local metadata-byte identity, not a promised cross-compiler hash.

A final full-core rebuild overlapped the next wave's temporary event-enum/Engine
integration state and failed on the then-unhandled `Percussion` enum in
`Engine.cpp`. Those files belong to other agents and were not changed here.
Following integrator coordination, the latest exporter was compiled independently:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -I include tools/model_info.cpp src/ContactBank.cpp \
  src/Percussion.cpp -o ../model-info-direct
HAMMOND_MODEL_INFO_EXECUTABLE=../model-info-direct python3 tests/test_model_info.py -v
python3 tools/check_repository.py
git diff --check
```

The latest direct strict build and all seven methods passed, including LF and output
failure checks. The source-archive checker and whitespace check passed. The three
locale settings are environment tests; no installed foreign C++ locale is claimed.
The Windows-only stdout branch, macOS/Windows execution, sanitizers and combined
staged-tree build remain integration gates. No commit or push was performed.

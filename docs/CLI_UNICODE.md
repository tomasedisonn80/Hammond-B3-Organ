# Offline CLI Unicode boundary

All six offline C++ tools use the same Windows argument boundary in
[`tools/CliArguments.h`](../tools/CliArguments.h). The scope is command-line
decoding and filesystem paths; it does not change the core, audio algorithms,
parameter mappings, host adapters, or native SDK boundary.

| Executable | Filesystem arguments handled as UTF-8 on Windows |
| --- | --- |
| `hammond_render` | `--profile`, `--events`, `--output` |
| `hammond_benchmark` | `--profile` |
| `hammond_console_trace` | `--profile`, `--output` |
| `hammond_pedal_trace` | `--profile`, `--output` |
| `hammond_model_info` | No filesystem arguments; Unicode executable and working-directory names are exercised |
| `hammond_parameter_info` | No filesystem arguments; Unicode executable and working-directory names are exercised |

## Why the boundary is shared

The renderer's earlier Windows failure converted full-width eight to ASCII
eight before the strict drawbar parser inspected the token. The observed failure,
diagnostic follow-up and prior hosted renderer verification are recorded in
[`PEDAL_WINDOWS_UNICODE.md`](reviews/PEDAL_WINDOWS_UNICODE.md). The other offline
tools had the same narrow-argument entry pattern, so the same repair now covers
their flags and paths.

On Windows, each executable enters through `wmain`. The helper measures and
converts each argument with `WideCharToMultiByte(CP_UTF8,
WC_ERR_INVALID_CHARS, ...)`, checks both calls, and keeps the converted strings
alive until the existing tool body returns. There is no normalization, best-fit
substitution, locale switch, or replacement-character fallback. Full-width digits,
signs, option names and enumeration values therefore reach the existing parsers
as their actual UTF-8 bytes and are rejected when the grammar requires ASCII.

Filesystem argument construction uses a `char8_t` string so the Windows
`std::filesystem::path` constructor receives explicit UTF-8. The renderer's
missing-input diagnostic converts the native path back to UTF-8, retaining the
spelling of a Unicode filename. On POSIX, the existing `main` argument bytes and
native path construction remain unchanged.

Relevant platform contracts are Microsoft's
[`wmain` documentation](https://learn.microsoft.com/en-us/cpp/cpp/main-function-command-line-args)
and [`WideCharToMultiByte` documentation](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-widechartomultibyte).

## Existing parser and publication contracts

The helper leaves each tool's parser responsible for its current options and
bounds. Only the renderer retains its pre-existing Windows entry-level count and
byte checks; no new shared limit is imposed on the other tools.

| Tool | Retained bounds and grammar |
| --- | --- |
| Renderer | At most 30 arguments including the executable name; value tokens at most 4096 bytes; integer tokens at most 128 bytes; the existing flag-specific ranges and drawbar grammar |
| Benchmark | At most 15 arguments including the executable name; values 1–4096 bytes; unsigned integer tokens 1–20 ASCII digits; existing workload and frame ceilings |
| Console and pedal trace | All five options exactly once; values 1–4096 bytes; unsigned integer tokens 1–20 ASCII digits; existing scenarios, rates and fixed trace ceilings |
| Model information | No arguments or `--help` alone |
| Parameter information | No arguments, `--help` alone, or `--normalized U`; `U` retains its finite decimal grammar, 128-byte limit and range `[0,1]` |

The renderer's Windows entry additionally checks every non-executable argument
against its existing 4096-byte ceiling before parsing. Its compatibility
diagnostic remains exactly:

```text
Command-line argument is invalid Unicode or oversized (maximum 4096 UTF-8 bytes).
```

Existing profile/score validation, numeric parsing, output collision checks,
temporary-file ownership and hard-link publication are unchanged. Existing files
are never overwritten. The metadata tools retain binary stdout mode on Windows;
their JSON schemas, records and newline bytes are unaffected by argument decoding.
The benchmark's compile-time default profile setting is unchanged; the Unicode
path acceptance exercises an explicit `--profile` argument.

## Executable acceptance

[`test_cli_unicode.py`](../tests/test_cli_unicode.py) requires all six actual
executables and the compiled profile from one build. CTest supplies their paths;
missing binaries are errors. The suite exercises:

- Copied executable names and working directories containing spaces, accented
  Latin characters, CJK characters and a supplementary-plane piano character.
- Absolute and relative Unicode profile, score and output paths, comparing exact
  WAV and CSV bytes with runs using ASCII paths.
- Exact model/parameter JSON and help bytes; the benchmark compares every field
  except its three explicitly nondeterministic timing fields.
- Full-width numeric values and signs for the tools with numeric arguments, plus
  full-width help/enum tokens, preserving rejection and leaving no files behind.
- Exactly 4096 UTF-8 bytes versus 4097 bytes, preserving parser diagnostics;
  accepted 128-byte versus rejected 129-byte normalized decimal tokens.
- A Unicode missing-input diagnostic, preservation of existing Unicode outputs,
  and two competing publishers leaving one complete reference file without
  staging artifacts.

Run the focused acceptance from a coherent build:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel 3 --target hammond_render hammond_benchmark hammond_model_info hammond_parameter_info hammond_console_trace hammond_pedal_trace
ctest --test-dir build --output-on-failure --no-tests=error -R '^python_test_(cli_unicode|render|pedal_render_cli|console_trace|pedal_trace|console_benchmark|model_info|parameter_bridge)$'
```

For a multi-configuration generator, select Release with `--config Release` when
building and `-C Release` for CTest. The normal `check` target also builds the
required executables. MinGW applies `-municode` to these six executables only;
the core library, test executables and optional native plugin do not inherit it.

The assignment's local Linux result and exact frozen inputs are recorded in
[`37-cli-unicode.md`](development/2026-11-13-pedals/37-cli-unicode.md).
A Linux test run exercises POSIX entry points, not Windows `wmain`. Native Windows
CI on the integrated commit remains required to qualify the Windows conversion,
filesystem behavior and startup linkage. MinGW is a separate unexecuted local
configuration. Malformed UTF-16 rejection is implemented by the strict conversion
flags but is not an executed case in this portable suite. Embedded NUL cannot be
an OS argument payload and is not simulated as one. This acceptance does not
establish support for Unicode build-directory literals or plugin/DAW paths.

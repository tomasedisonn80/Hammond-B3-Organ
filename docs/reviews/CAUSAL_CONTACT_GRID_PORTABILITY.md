# Causal contact grid: Windows stdin portability

**A27 (`/root/w05_a27`), wave 5, 16 November 2026. Source-ready correction.**
The guarded setup repairs a source-identified Windows transport risk. It is not
an observed Windows runtime pass; root owns coherent native regression and CI.

## Issue and evidence

The probe promises a maximum of 131072 input bytes and rejects every trailing
non-whitespace token. A17's implementation counted characters returned by
`std::cin.get` without setting the underlying Windows CRT descriptor mode.
Microsoft documents that text input collapses CRLF to LF and interprets Ctrl-Z
(`0x1a`) as EOF; binary mode suppresses these translations. Consequently, text
mode can undercount CRLF-padded input or hide trailing Ctrl-Z/data from the
parser. This is a deduction from the documented CRT behavior, not a locally
reproduced Windows failure. See Microsoft's [translation constants][translation]
and [`_setmode`][setmode] documentation.

A24 already froze relevant checks in `tests/test_causal_contact_grid_cli.py`:
exact 131072-byte acceptance and 131073-byte rejection using CRLF padding,
plus rejection of a valid case followed by `0x1a`. Its recorded Linux pass
cannot exercise Windows text translation. No test, threshold or grammar changes
are needed.

The repository has the same raw-input requirement and fix in
`tools/scanner_line_foh_probe.cpp::read_inputs`: guarded `<fcntl.h>`/`<io.h>` and
`_setmode(_fileno(stdin), _O_BINARY)` before reading. Other tools, including
`source_leakage_probe.cpp`, already include `<cstdio>` with the Windows headers
under `_WIN32`.

## Exact change and compatibility review

`tools/causal_contact_grid_probe.cpp` adds only two `_WIN32`-guarded blocks:

1. Include `<cstdio>`, `<fcntl.h>` and `<io.h>`.
2. After help/argument handling and immediately before `read_input`, obtain an
   `int` descriptor with `_fileno(stdin)` and select `_O_BINARY` with `_setmode`.
   A negative descriptor short-circuits the mode call. A negative descriptor or
   returned `-1` uses the existing `ProbeError` path with the fixed text
   `cannot set stdin to binary mode`: exit 2, no report, at most 60 stderr bytes
   including the prefix and CRLF. No input bytes or system-error text are echoed.

Microsoft specifies `int _fileno(FILE*)` in `<stdio.h>` and
`int _setmode(int, int)` in `<io.h>`, with `_O_BINARY` supplied by `<fcntl.h>`.
The existing project's `<cstdio>` convention supplies the C stream declaration
and global CRT extension on Windows. The `int` descriptor/result require no
narrowing. The underscored names avoid the deprecated POSIX aliases.
`_setmode` must run before stream I/O; this placement does so without making
`--help` depend on stdin. See [`_fileno`][fileno] and [`_setmode`][setmode].

For MinGW compatibility, the [MinGW-w64 `stdio.h` source][mingw-stdio] exposes
`_fileno(FILE*)` returning `int`; the [GNU Windows runtime source][gcc-sysdep]
also uses `_setmode` with an integer handle and `_O_BINARY`. These source
checks and the existing repository convention support the same CRT spelling
under MSVC and MinGW. No hand-written prototypes, MSVC-only `_MSC_VER` guard,
Win32 SDK dependency or alternative entry point is introduced. The complete
MinGW header/build combination remains uncompiled here, as does MSVC.

Both added blocks disappear on Linux/macOS. Removing them reproduces A17's
entire original probe byte-for-byte. `main(int, char*[])`, argument rejection,
parser limits, model calls, JSON schema and exception handling stay intact.

### Stdout

Stdout remains text. The JSON payload contains ASCII structure, decimal numbers,
fixed names and one final LF; Windows may expand that final LF to CRLF. JSON
consumers accept that whitespace and A24 explicitly accepts either diagnostic
newline. The transport does not promise identical physical output bytes across
platforms. Even a loose source-derived ceiling of 200 bytes per maximum 4608
edges, 100 bytes per maximum 4096 blocks and 16 KiB for all snapshot/framing
text, plus the extra CR, is below 2 MiB. No binary stdout change is required for
the raw-input fix. No stream is desynchronized from its C counterpart.

## Source identities and verification

Working overlay over HEAD `4aac394cde4da40906b615573a8779aee2d9a37a`:

| Input | SHA-256 |
| --- | --- |
| A17 probe before this change | `1883f84fe45f342e944836621798daf629e2688b3a5b010fdd100d850e72d8a4` |
| Corrected probe | `265b3c3fd82d8fe5f2a2d09ea235ab54071686a66535f352352a0403d9a0f576` |
| Unchanged CLI suite | `cf286e63d329d2d90814ccdf23bb0af963a160f3ba8c4696f96f5c2b6cd94020` |
| Frozen grid contract | `ba851e6af0601b52aef73d4b9effb64dffac3ef5e230eff7015e10e58a4ecb4e` |
| Prior scanner probe convention | `6c39384dc5235abd84017faf834cece93bb96cabc8882f8e2e1e85168a2c8897` |

From `/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`, GCC 14.2.0:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -fsyntax-only -Iinclude tools/causal_contact_grid_probe.cpp
```

Passed, exit 0, no diagnostics. An in-memory diff/hash check confirmed exactly
the two guarded additions and the original A17 hash after removing them. No
native executable build or runtime test was performed by A27. MSVC, MinGW,
clang-cl and Wine were unavailable in the local command path. Windows compile,
link, raw-byte runtime behavior and mode-failure execution remain unrun.

Root should rebuild the existing native probe and rerun the unchanged CLI and
differential suites, then require their exact-source Windows CI results. This
transport correction supplies no Engine, audio, physical or deadline grade.

[translation]: https://learn.microsoft.com/en-us/cpp/c-runtime-library/file-translation-constants?view=msvc-170
[setmode]: https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/setmode?view=msvc-170
[fileno]: https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/fileno?view=msvc-170
[mingw-stdio]: https://github.com/mirror/mingw-w64/blob/master/mingw-w64-headers/crt/stdio.h
[gcc-sysdep]: https://github.com/gcc-mirror/gcc/blob/master/gcc/ada/sysdep.c

# Pedal renderer Windows Unicode repair

## Observed failure and diagnosis

The input/renderer checkpoint `6bcf35cd0c2a54eeb31fabfde8b40bdfcb5b1f51`
passed all 60 local Release suites. Hosted
[run 43399562616](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43399562616)
passed Linux GCC, macOS AppleClang and Linux ASan/UBSan with leak checking.
The [Windows job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43399562616/job/131798742483)
built successfully and passed 59/60 suites. The new renderer suite failed one
case: the argument `--pedal-drawbars` followed by U+FF18 FULLWIDTH DIGIT EIGHT
and ASCII zero returned success instead of rejecting the non-ASCII value.
The exact existing test remains active.

The renderer's parser already checks each byte against ASCII `0` through `8`.
The code-path diagnosis is conversion before that parser: the Windows narrow
entry point can apply a code-page mapping to the original Unicode command line.
Microsoft documents lossy and best-fit conversions in
[WideCharToMultiByte](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-widechartomultibyte),
and provides [wmain](https://learn.microsoft.com/en-us/cpp/cpp/main-function-command-line-args)
for receiving wide command-line arguments. This explains why the same strict
parser rejected the test on Linux/macOS while the Windows process accepted it.

## Repair

On Windows, the renderer now receives `wmain` arguments and converts them to
UTF-8 with `CP_UTF8` and `WC_ERR_INVALID_CHARS`, checking both conversion calls
and the existing argument-byte bound. Invalid Unicode rejects before rendering.
All platforms then use the same strict option parser. The original non-ASCII
digits remain non-ASCII bytes and cannot silently become numeric controls.

Windows profile, score and output arguments explicitly construct filesystem
paths from `char8_t` strings. This preserves Unicode filenames instead of
feeding UTF-8 through a second ANSI-code-page conversion. The ordinary POSIX
path behavior is unchanged. The MinGW build receives its Unicode-startup link
option; no MinGW execution is claimed by the MSVC matrix.

The regression retains the original failing value, adds full-width digits in
other numeric controls and an infinity character, and exercises actual profile,
score and output paths containing accented, CJK and supplementary characters.
The Unicode-path render must produce exactly the same WAV as its ordinary-path
reference and leave no alternative output or temporary artifact.

## Executed local gate

Frozen tree `73b7bccb70de21c1dbe9e23ed0d1c1cb10fef3a7` contains only the repair's
renderer, test and startup-link changes beyond the published checkpoint.
The unfinished wave-5 trace/metadata/timeline/state work is excluded.

Using GCC 14.2.0, CMake 3.31.6 and Python 3.12.14:

```sh
cmake -S checkpoint-w04-unicode/source -B checkpoint-w04-unicode/build \
  -DCMAKE_BUILD_TYPE=Release
cmake --build checkpoint-w04-unicode/build \
  --target hammond_render hammond_profile -j 4
ctest --test-dir checkpoint-w04-unicode/build --output-on-failure \
  -R '^python_test_(render|pedal_render_cli|pedal_render_evidence|render_fixture|verify_render|console_catalog|console_evidence|partial_key_render)$'
```

**8/8 targeted suites passed, zero failures, in 16.87 seconds.** These cover the
actual renderer and current/historical evidence paths, including the new
Unicode-path comparison. Local Linux execution cannot qualify the Windows
entry point; the repair's exact published MSVC result must be observed before
closing that gate. The first failed job remains part of this record.

No DSP, control registry, profile, score, pedal map or physical-model value
changes in this repair. A later portability audit will review the other offline
entry points separately rather than inheriting this renderer-specific result.


## Native regression observed and diagnostic follow-up

Repair commit `8d0573442ca311c9b5298a955e1b837050b606cf` was fetched and its exact
published tree verified. In [run 43401628824](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43401628824),
Windows compiled the wide entry point and **passed the entire 19-method pedal
renderer suite**, including the original Unicode-digit rejection and actual
Unicode profile/score/output paths. The job nevertheless passed 59/60 suites:
the older renderer suite expected the established substring `oversized` for a
4,097-byte argument, while the new early error said `exceeds 4096 UTF-8 bytes`.
The argument already rejected with status 1 and preserved its destination.

The follow-up restores `oversized` in that Windows-only error string. It changes
no branch, conversion, limit, parser, DSP or test assertion. This literal-only
change is inspected directly; another Linux execution cannot exercise it.
The next exact-commit MSVC run remains the closure gate. The earlier failed
runs are retained, rather than relabelled as fully passing.


## Exact native closure observed

At published commit `a451ebd3ebd3752cef982777a438cf78eda64b36`, root fetched
and verified tree `297325bed036ef40f3c64dd5ca1305abbc9250e4`. Hosted
[run 43402590446](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43402590446)
completed the [Windows MSVC job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43402590446/job/131808878321)
successfully: all 60 suites passed, including the actual wide-entry Unicode
regressions and the older oversized-argument assertion. Linux Release and Linux
ASan/UBSan with leak checking also passed. macOS remained queued at this
observation; this is native closure of the two reported Windows failures, not
a claim that the entire new run had completed. Later platform records retain
the eventual macOS result separately.

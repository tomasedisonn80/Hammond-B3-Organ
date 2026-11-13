# Third-party notices

Reviewed 2026-11-13. These notices identify particular material and its source;
they do not select a project-wide license. No project `LICENSE` file was present
at this review. The [dependency and rights inventory](docs/DEPENDENCIES_AND_RIGHTS.md)
records the source, local-install and CI boundaries and remaining release work.

## SplitMix64 reference adaptation

[`src/TonewheelBank.cpp`](src/TonewheelBank.cpp), function `next_phase_bits`, adapts
Sebastiano Vigna's 2015 fixed-increment SplitMix64 reference for deterministic
phase initialization. It uses caller-owned state instead of the reference's
global state. The increment, two mixing multipliers and three shifts match the
[primary reference](https://prng.di.unimi.it/splitmix.c), inspected 2026-11-13.
The reference file is not separately vendored.

The upstream author dedicates the reference to the public domain worldwide to
the extent permitted by law. The linked primary notice separately permits use,
copying, modification and distribution for any purpose, with or without a fee,
and disclaims warranties and liability. Consult that source for its complete
wording; this is a terms summary and attribution, not a replacement license.

This upstream statement concerns that software; it does not license the supplied
atlas, factory source material, other project files or future dependencies.

## CI actions: fetched by GitHub Actions, not vendored

The [workflow](.github/workflows/ci.yml) references these exact official action
revisions. Their top-level license files were inspected through GitHub on
2026-11-13; each states MIT and `Copyright (c) 2018 GitHub, Inc. and contributors`.

| Action / workflow version comment | Pinned revision and primary license |
| --- | --- |
| `actions/checkout` / `v7.0.1` | [`3d3c42e5aac5ba805825da76410c181273ba90b1` — MIT](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/LICENSE) |
| `actions/setup-python` / `v7.1.0` | [`6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` — MIT](https://github.com/actions/setup-python/blob/6d4fd22b20465ccc0f7354476588e8df7c9ca0e0/LICENSE) |
| `actions/upload-artifact` / `v7.0.2` | [`cf430e030ddbb5b0abf93d22962f4752f3646cd9` — MIT](https://github.com/actions/upload-artifact/blob/cf430e030ddbb5b0abf93d22962f4752f3646cd9/LICENSE) |

The repository contains references to these actions, not their source trees or
bundled JavaScript. The local offline install does not include them. This table
does not assign MIT to their transitive packages, downloaded Python or runner
images. If action code is later redistributed, review that complete payload and
retain its applicable copyright/permission notices; the linked MIT texts require
those notices with copies or substantial portions of the covered software.

## Supplied research material and new factual transcriptions

The pre-existing [500-page atlas](Hammond_B3_Leslie_Research_Atlas_500pp.pdf) remains
unchanged. Its supplier's authorship and publication/derivative permissions,
including underlying pictures, embedded material and quoted sources, remain
unresolved in the [source-rights record](docs/research/RIGHTS_AND_SOURCES.md).
Its presence is not a new permission grant. Its absent companion rights catalogs
and font-notice file have not been recovered or recreated by this notice.

The four Table III CSVs are new factual transcriptions with recorded source,
page locators, independent procedures and frozen hashes in the
[factory comparison](docs/FACTORY_REFERENCE.md). The separately consulted factory
manual and rendered pages are not bundled. No publication permission for that
manual was established by the transcription or this notice.

System compilers, C++ standard libraries, Python and CMake are build/environment
components rather than vendored libraries here. A future binary package must
identify the exact runtime files it includes and preserve their own notices.

## Optional Steinberg VST 3 SDK 3.8.1

The selected SDK is separately acquired for an optional headless VST3 adapter
and SDK validator. Its source tree and built tools are not vendored in this
repository or included in the offline install. The exact root and four required
submodule revisions and primary license hashes are retained in
[data/dependencies/vst3-sdk-lock.json](data/dependencies/vst3-sdk-lock.json).
Root: [v3.8.1_build_84 at the pinned commit](https://github.com/steinbergmedia/vst3sdk/tree/3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96).
Reviewed 2026-11-13. Root, base, cmake, pluginterfaces and public.sdk primary
`LICENSE.txt` files have identical MIT text, reproduced below. A later package
containing this code must retain the applicable notice. This selection grants
no project-wide license and establishes no release packaging or trademark use.

```text
MIT License

Copyright (c) 2026, Steinberg Media Technologies GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Embedded json.h in SDK module-info tooling

The selected `public.sdk` revision contains
[`source/vst/moduleinfo/json.h`](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/moduleinfo/json.h),
from [sheredom/json.h](https://github.com/sheredom/json.h). Its header declares
the following Unlicense notice separately from the SDK's MIT text. File
SHA-256: `098ca68126cb34f7369388d49890d0a5d5ba731b76fbae0c2790377a663e9d41`.
The SDK validator/module-info parser uses it; preserve its provenance and notice
when redistributing that implementation or tool. Disabled SDK samples and their
other dependencies are outside this selected build and require their own
inventory if enabled or copied later.

```text
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>.
```

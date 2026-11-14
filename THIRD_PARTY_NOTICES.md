# Third-party notices

Reviewed 2026-11-13. These notices identify particular material and its source;
they do not select a project-wide license. No project `LICENSE` file was present
at this review. The [dependency and rights inventory](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/DEPENDENCIES_AND_RIGHTS.md)
records the source, local-install and CI boundaries and remaining release work.

## SplitMix64 reference adaptation

[`src/TonewheelBank.cpp`](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/src/TonewheelBank.cpp), function `next_phase_bits`, adapts
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

The [workflow](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/.github/workflows/ci.yml) references these exact official action
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

The pre-existing [500-page atlas](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/Hammond_B3_Leslie_Research_Atlas_500pp.pdf) remains
unchanged. Its supplier's authorship and publication/derivative permissions,
including underlying pictures, embedded material and quoted sources, remain
unresolved in the [source-rights record](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/research/RIGHTS_AND_SOURCES.md).
Its presence is not a new permission grant. Its absent companion rights catalogs
and font-notice file have not been recovered or recreated by this notice.

The four Table III CSVs are new factual transcriptions with recorded source,
page locators, independent procedures and frozen hashes in the
[factory comparison](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/FACTORY_REFERENCE.md). The separately consulted factory
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
[data/dependencies/vst3-sdk-lock.json](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/data/dependencies/vst3-sdk-lock.json).
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


## Optional SDL2 standalone transport

The optional standalone uses explicitly acquired SDL2 **2.32.10**, official
release tag `release-2.32.10`, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`. Source and license identities are
recorded in [the dependency lock](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/data/dependencies/sdl2-lock.json) and verified
by [the acquisition tool](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/tools/acquire_sdl2.py). Configuration does not download
or modify that source. SDL2 source is not vendored in this repository. The native
standalone statically links the selected SDL2 target; any binary distribution
containing it must retain this complete upstream notice and identify separately
included system/runtime dependencies. This does not grant a project-wide license.

The locked `LICENSE.txt` identity (884 bytes, SHA-256
`97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127`).
The full notice below normalizes trailing whitespace only:

```text
Copyright (C) 1997-2025 Sam Lantinga <slouken@libsdl.org>

This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
```

### SDL bundled yuv2rgb notice

The pinned SDL source includes yuv2rgb by Adrien Descamps. The audited Linux
standalone executable contains its conversion implementation. This complete
notice accompanies the binary through the existing installed
`THIRD_PARTY_NOTICES.md`; later payload additions retain this notice unchanged.
[Exact source](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/src/video/yuv2rgb/LICENSE):
1,480 bytes, SHA-256
`f7d74004cc75778cae46c5f0139f244d67c07ef64cf51937e8272352197dcb18`.

```text
Copyright (c) 2016, Adrien Descamps
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of yuv2rgb nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### SDL bundled HIDAPI: selected BSD-style license option

The pinned HIDAPI `LICENSE.txt` expressly offers GPLv3, BSD-style and original
HIDAPI alternatives. This standalone component selects the **BSD-style option**
for any included HIDAPI code. The complete text below is retained without
selecting a license for unrelated project files. Which platform backend is
compiled remains configuration-specific; SDL HIDAPI wrapper symbols alone do
not establish that every upstream backend entered an executable.
[Exact selected source](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/src/hidapi/LICENSE-bsd.txt):
1,534 bytes, SHA-256
`30eb1bef29b46f8ba7ab8b416035dbd93cb034a45481dd97815b944284582cd2`.

```text
Copyright (c) 2010, Alan Ott, Signal 11 Software
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of Signal 11 Software nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

### SDL bundled Sun math fallback notice

SDL's pinned `src/libm` fallback sources carry the following Sun Microsystems /
SunPro notice. It is retained for configurations that include those routines.
The reviewed Linux build compiled the fallback source objects into the SDL
archive, but its final executable uses system math and showed no linked
`SDL_uclibc`, `__kernel` or `__ieee754` fallback symbols. Compilation of an archive
member is not a claim that the linker selected it for that executable.
[Example exact source](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/src/libm/e_pow.c),
SHA-256 `ac26220798ad9f92bc051aa5102ae41a0fe50b1c8750f5f90353252c5a948512`:

```c
/*
 * ====================================================
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 *
 * Developed at SunPro, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 */
```

These additions address the identified bundled-source notices. They do not
constitute a complete inventory of every future platform library, system
runtime or distribution artifact.

## Standalone DejaVu font inputs and generated glyphs

Unmodified DejaVu Sans Book and DejaVu Serif Book **2.37** are retained under
[assets/standalone/fonts](https://github.com/tomasedisonn80/Hammond-B3-Organ/tree/main/assets/standalone/fonts/). Their full source identities,
font metadata, local package provenance and the fixed rasterizer versions are
recorded in [the manifest](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/assets/standalone/fonts/source-manifest.json).
The executable embeds generated glyph alpha data in
[FontData.h](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/apps/standalone/FontData.h); runtime font files, FreeType, Pillow and
SDL_ttf are not linked or required by this implementation.

The complete [LICENSE-DejaVu.txt](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/assets/standalone/fonts/LICENSE-DejaVu.txt)
accompanies the source inputs and is reproduced in the generated header. Packages
containing the source fonts or derived glyph atlas must also ship that complete
notice as an accompanying file. The permission text contains Bitstream notices
and states that DejaVu changes are public domain. The separate Debian packaging
GPL section is not the font license and was not substituted for it. See
[font authoring and rights](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_FONTS.md) for the exact boundary.


## Optional RtMidi input backend

MIDI-enabled standalone builds statically link **RtMidi 6.0.0**, tag `6.0.0`,
commit `1e5b49925aa60065db52de44c366d446a902547b`. Its
[pinned upstream source](https://github.com/thestk/rtmidi/tree/1e5b49925aa60065db52de44c366d446a902547b),
[reviewed dependency lock](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/data/dependencies/rtmidi-lock.json) and
[preparation contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/RTMIDI_BUILD.md) identify the dependency. This addition
was reviewed against the retained local source and lock on 2026-11-14.

The exact upstream [LICENSE](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/assets/standalone/midi/LICENSE-RtMidi.txt) is
1,349 bytes, SHA-256
`7fa091d9c1aa492ebfcafa9f919d27bbce61e4f048ece2dfc3b7f93181e9e364`.
It contains the RtMidi copyright/permission/warranty notice and an expressly
nonbinding request to send modifications upstream. An enabled local installation
retains those exact bytes as `LICENSE-RtMidi.txt`, alongside `rtmidi-lock.json`.
The notice is required for copies or substantial portions of the covered
software; it does not select a license for this project or its artwork.

The separately prepared source applies the identified
`coremidi-zero-initialize-v1` correction to two allocations in `RtMidi.cpp`.
Only `new CoreMidiData;` becomes `new CoreMidiData{};`. This applies to the prepared
copy on every selected platform; the external upstream checkout is unchanged.
The installed `rtmidi-prepared-source.json` retains the complete dependency lock,
prepared file identities and preparation-tool hash; the installed
`rtmidi-coremidi-zero-init.patch` retains the exact 728-byte correction, SHA-256
`80aedddee9affe1c9ab305b605c6ca1f5c2209fd5d23da843c8c3f325426c4ad`.
The prepared C++ source SHA-256 is
`240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a`.

`standalone-capabilities.json` states the configured native API: ALSA, WinMM or
CoreMIDI. It records a compiled capability, not an available device, service or
permission. A MIDI-disabled build identifies its backend as `unavailable` and
contains no linked RtMidi, RtMidi license/lock or preparation payload. This
repository-wide notice describes the optional dependency without implying that
every build includes it. System driver/framework notices and release-runtime
inventories remain platform-specific work.

## Embedded reference decoration

The standalone embeds three decorative pixel regions derived from the supplied
atlas cover/page 409 concept: the cabinet/microphones and two control-free wood
edges. They remain separate from the implemented, dynamic controls. The source
is a user-supplied generated design concept; it is not an actual application
capture, a factory construction drawing or calibrated physical geometry.

The retained source JPEG, [atlas-cover-reference.jpg](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/design/atlas-cover-reference.jpg),
has SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
It is the unchanged embedded JPEG stream from image object 3, appearing on PDF
pages 1 and 409 of `Hammond_B3_Leslie_Research_Atlas_500pp.pdf` (SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`).
The [extraction record](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/design/atlas-reference.json) and
[decoration manifest](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/assets/standalone/reference/manifest.json) retain exact
source/pixel hashes, integer crop rectangles, authoring versions and intended
roles. These local retained identities were inspected on 2026-11-14; no new
external artwork was acquired.

Every standalone installation, with or without MIDI, includes those records as
`atlas-reference.json` and `reference-source-manifest.json`, plus this notice.
The executable embeds the derived pixels; installation does not copy the PDF,
source JPEG or authoring crop files as separate runtime resources.

**Use and publication rights remain unresolved.** Presence in the supplied atlas
and matching hashes establish provenance, not ownership or permission to
redistribute its pictures or derivatives. No new license or publication grant
is created by extraction, embedding, local staging or this notice. The
[source-rights record](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/research/RIGHTS_AND_SOURCES.md) retains the missing
authorship, underlying permission and redistribution evidence. Public release
or broader redistribution of the embedded decoration remains subject to that
existing clearance gate. SDL2, RtMidi and font licenses do not cover this artwork.

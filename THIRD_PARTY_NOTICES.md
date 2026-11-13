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

# A11 — exact reference decoration assets

Actual worker: `/root/w02_a11_reference_assets`; logical wave 2 of the
`2026-11-14-midi-ui` session. Started from `7b36cfa` with concurrent uncommitted
MIDI/layout work preserved. No commits, CMake changes or renderer changes were
made by this worker.

## Delivered

- Three exact source crops as bounded lossless `.rgb.gz` files plus
  [frozen provenance](../../../assets/standalone/reference/manifest.json) and
  authoring-only requirements under `assets/standalone/reference/`.
- [Standard-library compiler](../../../tools/compile_reference_art.py), producing
  a build-tree `ReferenceArtData.h` with native RGB descriptors and arrays.
- [Asset/API/build documentation](../../REFERENCE_ART_ASSETS.md).
- One authorized correction to the [visual contract](../../REFERENCE_UI_DESIGN.md):
  the original `(0,0,72,941)` left region contains baked `BASS` tablet fragments.
  Inspected exact enlarged crops, rejected that region, and admitted its
  control-free `(0,0,24,941)` strip. Cabinet `(1132,174,466,397)` and right cheek
  `(1604,0,68,941)` were also inspected. No source pixels were repainted.

Source JPEG SHA-256:
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
Manifest SHA-256:
`bf1bec09c0dd15d09ab0129f950ccb5370532f92cb9217e347ba69e96d24bc87`.
Executed compiler SHA-256:
`b0e06b4a0e6312300f64d47226875ce7d997759b9d9076eeb4cd049839d5c766`.
Three compressed files total **563,809 bytes**; decoded RGB totals
**814,722 bytes**. Complete per-crop identities and actual decoder versions are
in the manifest. The complete manifest is pinned by the compiler, so jointly
editing pixels and their claimed manifest hash cannot silently change admitted
decoration.

## Executed verification

Working directory:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Python 3.12.14, Pillow 13.0.0, libjpeg-turbo 3.2.0 / JPEG API 6.2,
zlib 1.3.2, Debian GCC 14.2.0.

```sh
python3 -S tools/compile_reference_art.py --verify-only
python3 tools/compile_reference_art.py --verify-source
python3 -S tools/compile_reference_art.py \
  --output /workspace/scratch/cd4bd06ce68f/a11-verification/generated/ReferenceArtData.h
python3 /workspace/scratch/cd4bd06ce68f/a11-verification/verify.py
git diff --check
```

All commands exited 0. The `-S` build path uses no third-party image module.
Direct source comparison matched every byte of all three original crops.
The generated header is **5,093,899 bytes**, SHA-256
`d94cefd9ad69726c267d4674acd66912f4764ee9f88d1c21ecce4ed7befcbac6`.

The temporary verification harness executed **20 focused checks**, retaining
its actual output at
`/workspace/scratch/cd4bd06ce68f/a11-verification/results.json`:

| Check group | Executed result |
| --- | --- |
| Repeat header generation | Identical bytes and unchanged destination mtime. |
| Two fresh `--extract-to` directories | Every gzip blob and manifest matched the admitted files exactly. |
| Relocated asset inputs | Identical generated header. |
| Changed manifest, truncated/changed/missing gzip, corrupt gzip with updated manifest hash, changed source JPEG | All six rejected; existing output header preserved. |
| Symlink destination and source/output alias | Both rejected; input/target preserved. |
| Expanded stream too large, truncated trailer, trailing bytes, second gzip member, short pixels, zero/oversized bounds, invalid gzip | All eight rejected by bounded decoder. |
| Compiled C++ consumer | Strict C++20 compilation succeeded; executable emitted all 814,722 bytes identical to independently decoded original crops. |

The C++ consumer used
`-std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -O2`.
Its combined emitted RGB SHA-256 was
`b8143168a6532a7a99672458dc787b9d2e5a6d4be5c7553dbecb2ed6ac0c7942`.
Temporary inspection images, harness, executable and generated multi-megabyte
headers remain outside the repository; the source assets/compiler and these
observed results are retained here.

## Integration handoff and limits

Root was sent the finalized descriptor API and custom-command dependency list.
Generate `ReferenceArtData.h` in the standalone build's existing generated
include directory, depending on the compiler, manifest, JPEG and three gzip
files. Add that output to `hammond_standalone`. The renderer uses
`reference_art::kCabinet`, `kLeftWoodCheek`, and `kRightWoodCheek`, each exposing
`width`, `height`, `pitch`, `pixels`, `byte_count`; upload with
`SDL_PIXELFORMAT_RGB24` on the main thread. The generated header introduces no
C++ image/compression dependency or runtime file requirement.

This closes asset extraction, provenance, corruption admission and byte transport
for this assignment. SDL texture upload/failure fallback, native interaction,
composition, actual screenshots and measured reference fidelity were not run
by A11; renderer/integration owners retain those acceptance tasks. Cabinet
imagery does not indicate connected rotary processing or measured geometry.

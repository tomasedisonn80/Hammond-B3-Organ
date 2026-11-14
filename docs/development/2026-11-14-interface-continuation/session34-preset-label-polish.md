# A34 — preset labels and title alignment

Actual worker `/root/w06_a34_preset_label_polish`, wave 6 of the requested
60-agent interface continuation. Read the current instructions, plan, contracts,
presets/tests and A27/A28/A32 findings. Root approved the bounded two-line design.
No source edit or build occurred before A31's staged checkpoint release; A35
released the native CPU/build window before compilation. A36 received the source
and build lease only after A34's captures, inspection and hash verification.

Owned production changes are only `UiModel.cpp` preset `label_bounds` and
`InstrumentView.cpp` preset-label painting/header centering. Updated the two
existing UI tests' exact label expectations, expanded the existing preset raster
test, and changed the affected preset/workspace contract paragraphs. The
[review](../../reviews/INTERFACE_PRESET_READABILITY.md) records results and limits.
Root owns shared status, README, staging and publication; this worker performed
none of those operations. No core, state, asset, Drawing, header, main or CMake
production file was changed by A34.

## Identity and reproduction

Before app: `968938196bcf291270e1b1e32e36f08535281a959fb47ea731a216c56486d270`.
After app: `fa58e1245c10ab0282fe6e5b67b3cce708f5fe6e1438e43a499e953702192961`,
preserved at `/workspace/scratch/601951e27dc3/a34-captures/hammond_standalone`.
Instrument source: `920f58ca287eca607632698c52a1e1fa819eb623a0be4828f082b2c6b0701912`.
Model source: `c3aa5756e0edac899d0d608cb451695926d970eedcfaa247948c7ce699077258`.
The unchanged focus-function hash is
`901174fca6cf045720224387a97c9a8ba0b442ff6950416f97b35c7447699dbe`.
[Before](reports/a34-source-before.json) and [after](reports/a34-source-after-build.json)
records pin every inspected source plus the actual probe command. A36's later
main-status change is outside this executable's qualification.

From this checkout, use CMake/CTest in
`/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin` and shared build
`/workspace/scratch/601951e27dc3/build-native`. The exact
[build](reports/a34-build-first.json) and [initial gate](reports/a34-ctest-first.json)
commands are retained. Required CTest selection:

```text
^test_standalone_(ui|preset_ui|preset_raster|scaled_view|workspace_raster)$
```

The initial gate passed four suites; the new glyph oracle failed. Its corrected
[targeted recheck](reports/a34-ctest-glyph-oracle.txt) passed, with
[full native counts](reports/a34-preset-final-output.txt). Production code was
unchanged between those runs. No second full-suite pass is implied.

`reports/a34-capture.py` takes phase, executable, exact SHA and temporary output
directory. `reports/a34-proof.py` verifies/crops its output; both authoring scripts
require Pillow. The retained [result](reports/a34-result.json) links source,
commands, first failures and captures. Only three compact PNGs enter the repository;
full temporary captures and the 3.7 MB executable remain outside it. Continue with
A36, the current gallery refresh and independent final visual acceptance.

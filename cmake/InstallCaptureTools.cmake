# Explicit, source-only capture pipeline installation. Keep this component
# separate from OfflineTools and include after InstallHammondTools.cmake.
# The fixed inventory and failure boundary are frozen in CAPTURE_TOOLS_INSTALL.md.
if(NOT COMMAND hammond_require_relative_install_dir)
    message(FATAL_ERROR "CaptureTools requires InstallHammondTools.cmake first.")
endif()
hammond_require_relative_install_dir(CaptureTools CMAKE_INSTALL_DATADIR)
set(_hammond_capture_destination
    "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/capture-tools")

set(_hammond_capture_modules
    tools/validate_capture.py
    tools/capture_common.py
    tools/capture_audio.py
    tools/capture_corpus.py
    tools/compare_capture.py
    tools/capture_job.py
    tools/capture_readiness.py
    tools/capture_study.py
    tools/make_capture_demo.py
    tools/verify_capture_report.py)
set(_hammond_capture_data
    data/capture.schema.json
    data/capture-corpus.schema.json
    data/capture-policy.schema.json
    data/capture-job.schema.json
    data/capture-study.schema.json
    data/capture-planned-example.json
    data/corpus-planned-example.json
    data/capture-policy-synthetic-example.json)
set(_hammond_capture_documents
    docs/CAPTURE_FORMAT.md
    docs/CAPTURE_PROTOCOL.md
    docs/CAPTURE_VALIDATION.md
    docs/CAPTURE_COMMON.md
    docs/CAPTURE_AUDIO_CONTRACT.md
    docs/CAPTURE_AUDIO.md
    docs/CAPTURE_CORPUS_CONTRACT.md
    docs/CAPTURE_CORPUS.md
    docs/CAPTURE_COMPARISON_CONTRACT.md
    docs/CAPTURE_COMPARISON.md
    docs/CAPTURE_POLICY.md
    docs/CAPTURE_JOB_CONTRACT.md
    docs/CAPTURE_JOB.md
    docs/CAPTURE_READINESS.md
    docs/CAPTURE_STUDY.md
    docs/CAPTURE_DEMO.md
    docs/CAPTURE_REPLAY.md
    docs/CAPTURE_TOOLS_INSTALL.md
    docs/PLAN.md
    docs/CALIBRATION_SCOPE.md
    docs/CAPTURE_JOB_REVIEW.md)
set(_hammond_capture_demo
    examples/capture-demo/README.md
    examples/capture-demo/EXPECTED.json
    examples/capture-demo/study.json
    examples/capture-demo/job-pass.json
    examples/capture-demo/job-inconclusive.json
    examples/capture-demo/job-fail.json
    examples/capture-demo/policy-pass.json
    examples/capture-demo/policy-inconclusive.json
    examples/capture-demo/policy-fail.json
    examples/capture-demo/corpus/corpus.json
    examples/capture-demo/corpus/reference.json
    examples/capture-demo/corpus/quarter.json
    examples/capture-demo/corpus/half.json
    examples/capture-demo/corpus/audio/reference.f32
    examples/capture-demo/corpus/audio/quarter.f32
    examples/capture-demo/corpus/audio/half.f32)

# Fixed relative instructions: neither original checkout paths nor installation
# prefixes are embedded in this payload. The full guide retains platform forms.
set(_hammond_capture_readme [=[# Hammond capture tools

This is the local, movable CaptureTools package. It contains ten Python modules,
five shape schemas, declared examples, operating contracts and the project plan.
It requires Python 3.10 or newer and its standard library. No source checkout,
native binary, package installation, network or audio device is needed to run it.
Read [the installation and relocation guide](docs/CAPTURE_TOOLS_INSTALL.md),
[the M0-M9 plan](docs/PLAN.md), and [the evidence scope](docs/CALIBRATION_SCOPE.md).

Run the following from this package root, using a writable existing directory
for reports. Python -B avoids creating bytecode caches in the copied package.
Absolute script/input paths work from another working directory as well.

```sh
python3 -B tools/validate_capture.py --input data/capture-planned-example.json
python3 -B tools/capture_readiness.py --input data/capture-planned-example.json
python3 -B tools/capture_corpus.py --input data/corpus-planned-example.json
python3 -B tools/capture_corpus.py --input examples/capture-demo/corpus/corpus.json --check-files --check-audio
```

Expected exits are 0, 3, 3 and 0. A planned or inconclusive declaration is not a
failed installation. Run commands separately or retain their expected codes.

The tiny original synthetic demo retains all three engineering outcomes:

```sh
python3 -B tools/capture_job.py --input examples/capture-demo/job-pass.json
python3 -B tools/capture_job.py --input examples/capture-demo/job-inconclusive.json
python3 -B tools/capture_job.py --input examples/capture-demo/job-fail.json
python3 -B tools/capture_study.py --input examples/capture-demo/study.json
```

The expected exits are 0, 3, 1 and 1. The study retains one pass, one inconclusive
and one failed job. These deliberate outcomes must not be changed to obtain an
all-zero sequence. Every completed operation emits a complete UTF-8/LF report;
the original EXPECTED.json remains a literal oracle with execution: not_run.

To retain and replay the failed study, choose fresh filenames under an existing
writable directory; this example creates one such report directory explicitly:

```sh
hammond_reports="$HOME/hammond capture reports"
mkdir -p "$hammond_reports"
python3 -B tools/capture_study.py --input examples/capture-demo/study.json --output "$hammond_reports/study.json"
python3 -B tools/verify_capture_report.py --kind study --input examples/capture-demo/study.json --report "$hammond_reports/study.json" --output "$hammond_reports/study-replay.json"
python3 -B tools/make_capture_demo.py --output "$hammond_reports/new-demo"
```

Run those commands separately: their expected exits are 1, 0 and 0 under the same
coherent sources/runtime. A matching replay still retains the underlying failed
engineering status. New demo creation returns an inventory with execution:
not_run; generation is not analysis. All output destinations must be new, and
their parents must exist. Report publication requires hard-link support.
Use explicit --output rather than shell text redirection to retain exact bytes.

Move the complete package or its containing prefix, then use its new paths.
Keep all ten modules together and keep the package/archive/report quiescent.
Source/runtime changes can cause replay mismatch; a source hash is no signature
or historical authenticity proof. The [replay contract](docs/CAPTURE_REPLAY.md)
defines canonical-byte admission, complete comparison and failure behavior.

Installation preflights every input and requires a new capture-tools leaf. It
does not replace an existing completed package. A failure after copying starts
can leave a partial new directory; no automatic recursive cleanup occurs.
The copy is not a hostile-filesystem sandbox or an atomic multi-file transaction.
See the guide for the exact 57-file inventory, custom data directories, CMake
component/configuration behavior and PowerShell commands.

Synthetic inputs disclose constructed metadata and establish no specimen,
permission, calibrated measurement, untouched holdout, listening result or
physical fidelity. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) is retained
unchanged. The repository has not selected a project-wide license; this local
installation does not clear redistribution, branding or research-source rights.
Some historical links in unchanged source documents require the full repository
at https://github.com/tomasedisonn80/Hammond-B3-Organ and are not runtime inputs.
]=])
set(_hammond_capture_readme_file
    "${CMAKE_CURRENT_BINARY_DIR}/capture-tools-install/README.md")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/capture-tools-install")
file(WRITE "${_hammond_capture_readme_file}" "${_hammond_capture_readme}")

set(_hammond_capture_relative_files
    ${_hammond_capture_modules}
    ${_hammond_capture_data}
    ${_hammond_capture_documents}
    ${_hammond_capture_demo}
    THIRD_PARTY_NOTICES.md)
set(_hammond_capture_inputs "${_hammond_capture_readme_file}")
foreach(_hammond_capture_relative IN LISTS _hammond_capture_relative_files)
    list(APPEND _hammond_capture_inputs
        "${PROJECT_SOURCE_DIR}/${_hammond_capture_relative}")
endforeach()
list(LENGTH _hammond_capture_inputs _hammond_capture_input_count)
if(NOT _hammond_capture_input_count EQUAL 57)
    message(FATAL_ERROR "CaptureTools internal inventory must contain exactly 57 files.")
endif()

set(_hammond_capture_preflight [=[
    if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
       NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
        message(FATAL_ERROR "CaptureTools requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
    endif()
    set(_hammond_capture_inputs "@_hammond_capture_inputs@")
    foreach(_hammond_capture_input IN LISTS _hammond_capture_inputs)
        if(NOT EXISTS "${_hammond_capture_input}" OR
           IS_DIRECTORY "${_hammond_capture_input}" OR
           IS_SYMLINK "${_hammond_capture_input}")
            message(FATAL_ERROR
                "CaptureTools requires every payload input as an existing nonsymlink file: '${_hammond_capture_input}'. Retain the complete source package and configure again before installing.")
        endif()
        file(SIZE "${_hammond_capture_input}" _hammond_capture_input_size)
        if(_hammond_capture_input_size EQUAL 0)
            message(FATAL_ERROR "CaptureTools payload input is empty: '${_hammond_capture_input}'.")
        endif()
    endforeach()
    set(_hammond_capture_leaf
        "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/@_hammond_capture_destination@")
    if(EXISTS "${_hammond_capture_leaf}" OR IS_SYMLINK "${_hammond_capture_leaf}")
        message(FATAL_ERROR
            "CaptureTools destination already exists: '${_hammond_capture_leaf}'. Choose a fresh package root; existing packages are not merged or replaced.")
    endif()
    message(STATUS
        "CaptureTools preflight passed; copying begins. A later failure may retain a partial new package at '${_hammond_capture_leaf}'; no automatic cleanup is performed.")
]=])
string(CONFIGURE "${_hammond_capture_preflight}" _hammond_capture_preflight @ONLY)
install(CODE "${_hammond_capture_preflight}"
    COMPONENT CaptureTools EXCLUDE_FROM_ALL)
install(FILES "${_hammond_capture_readme_file}"
    DESTINATION "${_hammond_capture_destination}"
    COMPONENT CaptureTools EXCLUDE_FROM_ALL)
foreach(_hammond_capture_relative IN LISTS _hammond_capture_relative_files)
    get_filename_component(_hammond_capture_parent "${_hammond_capture_relative}" DIRECTORY)
    install(FILES "${PROJECT_SOURCE_DIR}/${_hammond_capture_relative}"
        DESTINATION "${_hammond_capture_destination}/${_hammond_capture_parent}"
        COMPONENT CaptureTools EXCLUDE_FROM_ALL)
endforeach()

# Test discovery is owned by the root list. Supply the exact selected CMake and
# paths only when the independently authored installation test is present.
if(BUILD_TESTING AND TEST python_test_capture_install)
    set_property(TEST python_test_capture_install APPEND PROPERTY ENVIRONMENT
        "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
        "HAMMOND_TEST_BUILD_DIR=${CMAKE_CURRENT_BINARY_DIR}"
        "HAMMOND_TEST_CONFIG=$<CONFIG>"
        "HAMMOND_INSTALL_DATADIR=${CMAKE_INSTALL_DATADIR}")
    set_tests_properties(python_test_capture_install PROPERTIES TIMEOUT 180)
endif()

# Opt-in, offline verification and preparation of one platform's pinned RtMidi.
# Ordinary configuration never calls the explicit network acquisition operation.
include_guard(GLOBAL)

function(_hammond_check_rtmidi rtmidi_root prepared_root)
    if(NOT IS_DIRECTORY "${rtmidi_root}")
        message(FATAL_ERROR
            "HAMMOND_ENABLE_MIDI requires an existing external HAMMOND_RTMIDI_ROOT. "
            "Run tools/acquire_rtmidi.py explicitly before configuring.")
    endif()
    find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
    get_filename_component(hammond_source_root "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.." ABSOLUTE)
    set(prepare_arguments)
    if(NOT "${prepared_root}" STREQUAL "")
        list(APPEND prepare_arguments --prepare-build-copy "${prepared_root}")
    endif()
    execute_process(
        COMMAND "${Python3_EXECUTABLE}"
            "${hammond_source_root}/tools/acquire_rtmidi.py"
            --verify-existing "${rtmidi_root}"
            --lock "${hammond_source_root}/data/dependencies/rtmidi-lock.json"
            ${prepare_arguments}
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE verify_result
        OUTPUT_VARIABLE verify_output
        ERROR_VARIABLE verify_error
        TIMEOUT 180)
    if(NOT "${verify_result}" STREQUAL "0")
        message(FATAL_ERROR "Pinned RtMidi verification/preparation failed: ${verify_error}")
    endif()
    message(STATUS "Pinned RtMidi verified: ${verify_output}")
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${hammond_source_root}/tools/acquire_rtmidi.py"
        "${hammond_source_root}/data/dependencies/rtmidi-lock.json"
        "${rtmidi_root}/RtMidi.cpp" "${rtmidi_root}/RtMidi.h" "${rtmidi_root}/LICENSE")
    if(NOT "${prepared_root}" STREQUAL "")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
            "${prepared_root}/RtMidi.cpp" "${prepared_root}/RtMidi.h"
            "${prepared_root}/LICENSE" "${prepared_root}/prepared-source.json"
            "${prepared_root}/rtmidi-coremidi-zero-init.patch")
    endif()
endfunction()

function(hammond_verify_rtmidi rtmidi_root)
    _hammond_check_rtmidi("${rtmidi_root}" "")
endfunction()

function(hammond_add_rtmidi target rtmidi_root)
    if(TARGET "${target}")
        message(FATAL_ERROR "RtMidi target already exists: ${target}")
    endif()
    # Do not enter the upstream CMake project: it autodetects additional APIs,
    # exposes extra build/install targets and can silently select a dummy API.
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT ANDROID)
        set(rtmidi_api __LINUX_ALSA__)
        set(rtmidi_backend ALSA)
        find_package(ALSA REQUIRED)
        find_package(Threads REQUIRED)
        set(rtmidi_libraries ALSA::ALSA Threads::Threads)
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(rtmidi_api __WINDOWS_MM__)
        set(rtmidi_backend WinMM)
        set(rtmidi_libraries winmm)
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        set(rtmidi_api __MACOSX_CORE__)
        set(rtmidi_backend CoreMIDI)
        find_library(HAMMOND_RTMIDI_CORESERVICES CoreServices REQUIRED)
        find_library(HAMMOND_RTMIDI_COREAUDIO CoreAudio REQUIRED)
        find_library(HAMMOND_RTMIDI_COREMIDI CoreMIDI REQUIRED)
        find_library(HAMMOND_RTMIDI_COREFOUNDATION CoreFoundation REQUIRED)
        set(rtmidi_libraries
            "${HAMMOND_RTMIDI_CORESERVICES}" "${HAMMOND_RTMIDI_COREAUDIO}"
            "${HAMMOND_RTMIDI_COREMIDI}" "${HAMMOND_RTMIDI_COREFOUNDATION}")
    else()
        message(FATAL_ERROR
            "HAMMOND_ENABLE_MIDI supports Linux ALSA, Windows WinMM and macOS CoreMIDI only; "
            "no alternative or dummy MIDI API will be selected for ${CMAKE_SYSTEM_NAME}.")
    endif()
    set(prepared_root "${CMAKE_CURRENT_BINARY_DIR}/${target}-prepared")
    _hammond_check_rtmidi("${rtmidi_root}" "${prepared_root}")
    add_library(${target} STATIC "${prepared_root}/RtMidi.cpp" "${prepared_root}/RtMidi.h")
    target_compile_features(${target} PRIVATE cxx_std_11)
    target_compile_definitions(${target} PRIVATE ${rtmidi_api})
    target_include_directories(${target} SYSTEM PUBLIC "$<BUILD_INTERFACE:${prepared_root}>")
    target_link_libraries(${target} PRIVATE ${rtmidi_libraries})
    set_target_properties(${target} PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        HAMMOND_RTMIDI_BACKEND "${rtmidi_backend}"
        HAMMOND_RTMIDI_PREPARED_ROOT "${prepared_root}")
    message(STATUS "Optional RtMidi backend: ${rtmidi_backend} (prepared static source)")
endfunction()

# Verification is local/read-only. No CMake path invokes acquisition.
include_guard(GLOBAL)

function(hammond_verify_vst3_sdk sdk_root)
    if(NOT IS_DIRECTORY "${sdk_root}")
        message(FATAL_ERROR
            "HAMMOND_BUILD_VST3 requires an existing external HAMMOND_VST3_SDK_ROOT. "
            "Run tools/acquire_vst3_sdk.py explicitly before configuring.")
    endif()
    execute_process(
        COMMAND "${Python3_EXECUTABLE}"
            "${PROJECT_SOURCE_DIR}/tools/acquire_vst3_sdk.py"
            --verify-existing "${sdk_root}"
            --lock "${PROJECT_SOURCE_DIR}/data/dependencies/vst3-sdk-lock.json"
        RESULT_VARIABLE verify_result
        OUTPUT_VARIABLE verify_output
        ERROR_VARIABLE verify_error
        TIMEOUT 180)
    if(NOT "${verify_result}" STREQUAL "0")
        message(FATAL_ERROR "Pinned VST3 SDK verification failed: ${verify_error}")
    endif()
    message(STATUS "Pinned VST3 SDK verified: ${verify_output}")
endfunction()

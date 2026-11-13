# Verification is local/read-only. No CMake path invokes acquisition.
include_guard(GLOBAL)

function(hammond_verify_sdl2 sdl2_root)
    if(NOT IS_DIRECTORY "${sdl2_root}")
        message(FATAL_ERROR
            "HAMMOND_BUILD_STANDALONE requires an existing external HAMMOND_SDL2_ROOT. "
            "Run tools/acquire_sdl2.py explicitly before configuring.")
    endif()
    find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
    # Resolve beside this module, not the caller's project(): SDL2 declares its
    # own project and this helper is also usable by a separate smoke project.
    get_filename_component(hammond_source_root "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.." ABSOLUTE)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}"
            "${hammond_source_root}/tools/acquire_sdl2.py"
            --verify-existing "${sdl2_root}"
            --lock "${hammond_source_root}/data/dependencies/sdl2-lock.json"
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE verify_result
        OUTPUT_VARIABLE verify_output
        ERROR_VARIABLE verify_error
        TIMEOUT 180)
    if(NOT "${verify_result}" STREQUAL "0")
        message(FATAL_ERROR "Pinned SDL2 verification failed: ${verify_error}")
    endif()
    message(STATUS "Pinned SDL2 verified: ${verify_output}")
endfunction()

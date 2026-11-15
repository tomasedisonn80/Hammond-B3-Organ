# Explicit source-leakage research/audition package. Include after
# InstallHammondTools and test discovery. Existing component inventories stay
# unchanged; no install rule builds an input or downloads a dependency.
if(TARGET hammond_source_leakage_probe)
    if(NOT COMMAND hammond_require_relative_install_dir)
        message(FATAL_ERROR "SourceLeakageTools requires InstallHammondTools.cmake first.")
    endif()
    set(_hammond_leakage_targets
        hammond_render hammond_source_leakage_probe hammond_source_leakage_benchmark)
    foreach(_hammond_leakage_target IN LISTS _hammond_leakage_targets)
        if(NOT TARGET ${_hammond_leakage_target})
            message(FATAL_ERROR "SourceLeakageTools requires target ${_hammond_leakage_target}.")
        endif()
    endforeach()
    if(NOT DEFINED HAMMOND_COMPILED_PROFILE OR HAMMOND_COMPILED_PROFILE STREQUAL "")
        message(FATAL_ERROR "SourceLeakageTools requires HAMMOND_COMPILED_PROFILE.")
    endif()
    hammond_require_relative_install_dir(SourceLeakageTools CMAKE_INSTALL_BINDIR)
    hammond_require_relative_install_dir(SourceLeakageTools CMAKE_INSTALL_DATADIR)
    string(REPLACE "\\" "/" _hammond_leakage_bindir "${CMAKE_INSTALL_BINDIR}")
    string(REPLACE "\\" "/" _hammond_leakage_datadir "${CMAKE_INSTALL_DATADIR}")
    set(_hammond_leakage_package
        "${_hammond_leakage_datadir}/hammond-b3-organ/source-leakage")
    get_filename_component(_hammond_leakage_source "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
    set(_hammond_leakage_files
        tools/compile_source_leakage.py
        data/source-leakage.schema.json
        data/source-leakage/synthetic-pair-demo-v1.json
        data/source-leakage/synthetic-identity-v1.json
        docs/SOURCE_LEAKAGE_INSTALL.md)

    # Target-dependent install code may disappear for an unknown multi-config
    # name; reject it before any unconditional metadata could be copied.
    get_property(_hammond_leakage_multi_config GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(_hammond_leakage_multi_config)
        set(_hammond_leakage_configurations "${CMAKE_CONFIGURATION_TYPES}")
        list(TRANSFORM _hammond_leakage_configurations TOUPPER)
        set(_hammond_leakage_configuration_guard [=[
            string(TOUPPER "${CMAKE_INSTALL_CONFIG_NAME}" _hammond_leakage_selected_configuration)
            set(_hammond_leakage_allowed_configurations [==[@_hammond_leakage_configurations@]==])
            list(FIND _hammond_leakage_allowed_configurations
                "${_hammond_leakage_selected_configuration}" _hammond_leakage_configuration_index)
            if(_hammond_leakage_configuration_index EQUAL -1)
                message(FATAL_ERROR
                    "SourceLeakageTools unknown configuration '${CMAKE_INSTALL_CONFIG_NAME}'; select a configured name: @_hammond_leakage_configurations@.")
            endif()
        ]=])
        string(CONFIGURE "${_hammond_leakage_configuration_guard}"
            _hammond_leakage_configuration_guard @ONLY)
        install(CODE "${_hammond_leakage_configuration_guard}"
            COMPONENT SourceLeakageTools EXCLUDE_FROM_ALL)
    endif()

    set(_hammond_leakage_inputs "${HAMMOND_COMPILED_PROFILE}")
    set(_hammond_leakage_binary_names)
    foreach(_hammond_leakage_target IN LISTS _hammond_leakage_targets)
        list(APPEND _hammond_leakage_inputs "$<TARGET_FILE:${_hammond_leakage_target}>")
        list(APPEND _hammond_leakage_binary_names "$<TARGET_FILE_NAME:${_hammond_leakage_target}>")
    endforeach()
    foreach(_hammond_leakage_relative IN LISTS _hammond_leakage_files)
        list(APPEND _hammond_leakage_inputs
            "${_hammond_leakage_source}/${_hammond_leakage_relative}")
    endforeach()
    set(_hammond_leakage_preflight [=[
        if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
           NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
            message(FATAL_ERROR "SourceLeakageTools requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
        endif()
        set(_hammond_leakage_inputs "@_hammond_leakage_inputs@")
        foreach(_hammond_leakage_input IN LISTS _hammond_leakage_inputs)
            if(NOT EXISTS "${_hammond_leakage_input}" OR
               IS_DIRECTORY "${_hammond_leakage_input}" OR
               IS_SYMLINK "${_hammond_leakage_input}")
                message(FATAL_ERROR
                    "SourceLeakageTools missing or invalid required input '${_hammond_leakage_input}'; require a nonempty nonsymlink file. Build hammond_render, hammond_source_leakage_probe, hammond_source_leakage_benchmark and nominal.b3p for the selected configuration, and retain all five source payload files.")
            endif()
            file(SIZE "${_hammond_leakage_input}" _hammond_leakage_input_size)
            if(_hammond_leakage_input_size EQUAL 0)
                message(FATAL_ERROR "SourceLeakageTools required input is empty: '${_hammond_leakage_input}'.")
            endif()
        endforeach()

        get_filename_component(_hammond_leakage_prefix
            "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}" ABSOLUTE)
        set(_hammond_leakage_destinations
            "${_hammond_leakage_prefix}/@_hammond_leakage_package@")
        set(_hammond_leakage_binary_names "@_hammond_leakage_binary_names@")
        foreach(_hammond_leakage_name IN LISTS _hammond_leakage_binary_names)
            list(APPEND _hammond_leakage_destinations
                "${_hammond_leakage_prefix}/@_hammond_leakage_bindir@/${_hammond_leakage_name}")
        endforeach()
        foreach(_hammond_leakage_destination IN LISTS _hammond_leakage_destinations)
            if(EXISTS "${_hammond_leakage_destination}" OR
               IS_SYMLINK "${_hammond_leakage_destination}")
                message(FATAL_ERROR
                    "SourceLeakageTools destination already exists: '${_hammond_leakage_destination}'. Choose a fresh local prefix; existing executable files and source-leakage packages are never replaced or merged.")
            endif()
            # Reject obstructions and linked ancestors inside the chosen prefix
            # before the first copy. System ancestors outside it are not policed.
            get_filename_component(_hammond_leakage_parent
                "${_hammond_leakage_destination}" DIRECTORY)
            while(1)
                if(IS_SYMLINK "${_hammond_leakage_parent}" OR
                   (EXISTS "${_hammond_leakage_parent}" AND
                    NOT IS_DIRECTORY "${_hammond_leakage_parent}"))
                    message(FATAL_ERROR
                        "SourceLeakageTools destination ancestor must be an ordinary directory: '${_hammond_leakage_parent}'.")
                endif()
                if(_hammond_leakage_parent STREQUAL _hammond_leakage_prefix)
                    break()
                endif()
                get_filename_component(_hammond_leakage_next_parent
                    "${_hammond_leakage_parent}" DIRECTORY)
                if(_hammond_leakage_next_parent STREQUAL _hammond_leakage_parent)
                    break()
                endif()
                set(_hammond_leakage_parent "${_hammond_leakage_next_parent}")
            endwhile()
        endforeach()
        message(STATUS
            "SourceLeakageTools preflight passed; copying begins. A later failure can leave a partial new installation; no automatic cleanup is performed.")
    ]=])
    string(CONFIGURE "${_hammond_leakage_preflight}" _hammond_leakage_preflight @ONLY)
    install(CODE "${_hammond_leakage_preflight}"
        COMPONENT SourceLeakageTools EXCLUDE_FROM_ALL)
    # PROGRAMS preserves executable bytes without RPATH editing or stripping.
    # The package still requires this platform's ordinary C/C++ runtime.
    foreach(_hammond_leakage_target IN LISTS _hammond_leakage_targets)
        install(PROGRAMS "$<TARGET_FILE:${_hammond_leakage_target}>"
            DESTINATION "${_hammond_leakage_bindir}"
            COMPONENT SourceLeakageTools EXCLUDE_FROM_ALL)
    endforeach()
    install(FILES "${HAMMOND_COMPILED_PROFILE}"
        DESTINATION "${_hammond_leakage_package}/profiles" RENAME nominal.b3p
        COMPONENT SourceLeakageTools EXCLUDE_FROM_ALL)
    foreach(_hammond_leakage_relative IN LISTS _hammond_leakage_files)
        get_filename_component(_hammond_leakage_parent "${_hammond_leakage_relative}" DIRECTORY)
        install(FILES "${_hammond_leakage_source}/${_hammond_leakage_relative}"
            DESTINATION "${_hammond_leakage_package}/${_hammond_leakage_parent}"
            COMPONENT SourceLeakageTools EXCLUDE_FROM_ALL)
    endforeach()

    if(BUILD_TESTING AND TEST python_test_source_leakage_install)
        set_property(TEST python_test_source_leakage_install APPEND PROPERTY ENVIRONMENT
            "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
            "HAMMOND_TEST_CMAKE_GENERATOR=${CMAKE_GENERATOR}"
            "HAMMOND_TEST_CMAKE_MAKE_PROGRAM=${CMAKE_MAKE_PROGRAM}"
            "HAMMOND_TEST_CONFIG=$<CONFIG>"
            "HAMMOND_RENDER_EXECUTABLE=$<TARGET_FILE:hammond_render>"
            "HAMMOND_SOURCE_LEAKAGE_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_source_leakage_probe>"
            "HAMMOND_SOURCE_LEAKAGE_BENCHMARK_EXECUTABLE=$<TARGET_FILE:hammond_source_leakage_benchmark>"
            "HAMMOND_TEST_PROFILE=${HAMMOND_COMPILED_PROFILE}")
        set_tests_properties(python_test_source_leakage_install PROPERTIES
            TIMEOUT 180 LABELS "source-leakage;install;offline")
    endif()
endif()

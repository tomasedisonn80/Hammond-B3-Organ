# Explicit local crossover research tools. Include after InstallHammondTools;
# this component does not extend OfflineTools or Standalone's payload.
if(TARGET hammond_crossover_probe)
    if(NOT COMMAND hammond_require_relative_install_dir)
        message(FATAL_ERROR "CrossoverTools requires InstallHammondTools.cmake first.")
    endif()
    hammond_require_relative_install_dir(CrossoverTools CMAKE_INSTALL_BINDIR)
    hammond_require_relative_install_dir(CrossoverTools CMAKE_INSTALL_DATADIR)
    string(REPLACE "\\" "/" _hammond_crossover_bindir "${CMAKE_INSTALL_BINDIR}")
    string(REPLACE "\\" "/" _hammond_crossover_datadir "${CMAKE_INSTALL_DATADIR}")
    set(_hammond_crossover_package
        "${_hammond_crossover_datadir}/hammond-b3-organ/crossover")
    get_filename_component(_hammond_crossover_source "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
    set(_hammond_crossover_files
        tools/crossover_reference.py
        data/crossover/leslie-122-ideal-v1.json
        docs/CROSSOVER_INSTALL.md
        docs/LESLIE_CROSSOVER_CONTRACT.md
        THIRD_PARTY_NOTICES.md)

    # Unknown multi-config names can omit target-dependent install code while
    # still copying unconditional metadata. Reject them before any such rule.
    get_property(_hammond_crossover_multi_config GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(_hammond_crossover_multi_config)
        set(_hammond_crossover_configurations "${CMAKE_CONFIGURATION_TYPES}")
        list(TRANSFORM _hammond_crossover_configurations TOUPPER)
        set(_hammond_crossover_configuration_guard [=[
            string(TOUPPER "${CMAKE_INSTALL_CONFIG_NAME}" _hammond_crossover_selected_configuration)
            set(_hammond_crossover_allowed_configurations [==[@_hammond_crossover_configurations@]==])
            list(FIND _hammond_crossover_allowed_configurations
                "${_hammond_crossover_selected_configuration}" _hammond_crossover_configuration_index)
            if(_hammond_crossover_configuration_index EQUAL -1)
                message(FATAL_ERROR
                    "CrossoverTools unknown configuration '${CMAKE_INSTALL_CONFIG_NAME}'; select a configured name: @_hammond_crossover_configurations@.")
            endif()
        ]=])
        string(CONFIGURE "${_hammond_crossover_configuration_guard}"
            _hammond_crossover_configuration_guard @ONLY)
        install(CODE "${_hammond_crossover_configuration_guard}"
            COMPONENT CrossoverTools EXCLUDE_FROM_ALL)
    endif()

    set(_hammond_crossover_inputs "$<TARGET_FILE:hammond_crossover_probe>")
    foreach(_hammond_crossover_relative IN LISTS _hammond_crossover_files)
        list(APPEND _hammond_crossover_inputs
            "${_hammond_crossover_source}/${_hammond_crossover_relative}")
    endforeach()
    set(_hammond_crossover_preflight [=[
        if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
           NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
            message(FATAL_ERROR "CrossoverTools requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
        endif()
        set(_hammond_crossover_inputs "@_hammond_crossover_inputs@")
        foreach(_hammond_crossover_input IN LISTS _hammond_crossover_inputs)
            if(NOT EXISTS "${_hammond_crossover_input}" OR
               IS_DIRECTORY "${_hammond_crossover_input}" OR
               IS_SYMLINK "${_hammond_crossover_input}")
                message(FATAL_ERROR
                    "CrossoverTools missing or invalid required input '${_hammond_crossover_input}'; require a nonempty nonsymlink file. Build hammond_crossover_probe for the selected configuration and retain all five source payload files before installing.")
            endif()
            file(SIZE "${_hammond_crossover_input}" _hammond_crossover_input_size)
            if(_hammond_crossover_input_size EQUAL 0)
                message(FATAL_ERROR "CrossoverTools required input is empty: '${_hammond_crossover_input}'.")
            endif()
        endforeach()

        get_filename_component(_hammond_crossover_prefix
            "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}" ABSOLUTE)
        set(_hammond_crossover_binary
            "${_hammond_crossover_prefix}/@_hammond_crossover_bindir@/$<TARGET_FILE_NAME:hammond_crossover_probe>")
        set(_hammond_crossover_leaf
            "${_hammond_crossover_prefix}/@_hammond_crossover_package@")
        foreach(_hammond_crossover_destination IN ITEMS
                "${_hammond_crossover_binary}" "${_hammond_crossover_leaf}")
            if(EXISTS "${_hammond_crossover_destination}" OR
               IS_SYMLINK "${_hammond_crossover_destination}")
                message(FATAL_ERROR
                    "CrossoverTools destination already exists: '${_hammond_crossover_destination}'. Choose a fresh local prefix; existing probe files and crossover packages are never replaced or merged.")
            endif()
            # Reject known obstructions before the first copy, including a
            # linked prefix or an output ancestor that would redirect writes.
            # System ancestors outside the caller's prefix are not inspected.
            get_filename_component(_hammond_crossover_parent
                "${_hammond_crossover_destination}" DIRECTORY)
            # Install scripts do not inherit the configure-time policy scope.
            # Numeric truth remains valid when older CMake leaves CMP0012 unset.
            while(1)
                if(IS_SYMLINK "${_hammond_crossover_parent}" OR
                   (EXISTS "${_hammond_crossover_parent}" AND
                    NOT IS_DIRECTORY "${_hammond_crossover_parent}"))
                    message(FATAL_ERROR
                        "CrossoverTools destination ancestor must be an ordinary directory: '${_hammond_crossover_parent}'.")
                endif()
                if(_hammond_crossover_parent STREQUAL _hammond_crossover_prefix)
                    break()
                endif()
                get_filename_component(_hammond_crossover_next_parent
                    "${_hammond_crossover_parent}" DIRECTORY)
                if(_hammond_crossover_next_parent STREQUAL _hammond_crossover_parent)
                    break()
                endif()
                set(_hammond_crossover_parent "${_hammond_crossover_next_parent}")
            endwhile()
        endforeach()
        message(STATUS
            "CrossoverTools preflight passed; copying begins. A later failure can leave a partial new installation; no automatic cleanup is performed.")
    ]=])
    string(CONFIGURE "${_hammond_crossover_preflight}" _hammond_crossover_preflight @ONLY)
    install(CODE "${_hammond_crossover_preflight}"
        COMPONENT CrossoverTools EXCLUDE_FROM_ALL)
    # PROGRAMS preserves the selected executable's bytes without RPATH editing
    # or stripping. No system runtime libraries or source-tree links are copied.
    install(PROGRAMS "$<TARGET_FILE:hammond_crossover_probe>"
        DESTINATION "${_hammond_crossover_bindir}"
        COMPONENT CrossoverTools EXCLUDE_FROM_ALL)
    foreach(_hammond_crossover_relative IN LISTS _hammond_crossover_files)
        get_filename_component(_hammond_crossover_parent "${_hammond_crossover_relative}" DIRECTORY)
        install(FILES "${_hammond_crossover_source}/${_hammond_crossover_relative}"
            DESTINATION "${_hammond_crossover_package}/${_hammond_crossover_parent}"
            COMPONENT CrossoverTools EXCLUDE_FROM_ALL)
    endforeach()

    # The existing root test glob discovers the suite. It uses the selected
    # binary read-only and creates private CMake fixtures and fresh prefixes;
    # it never installs from or changes the shared build tree.
    if(BUILD_TESTING AND TEST python_test_crossover_install)
        set_property(TEST python_test_crossover_install APPEND PROPERTY ENVIRONMENT
            "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
            "HAMMOND_TEST_CMAKE_GENERATOR=${CMAKE_GENERATOR}"
            "HAMMOND_TEST_CMAKE_MAKE_PROGRAM=${CMAKE_MAKE_PROGRAM}"
            "HAMMOND_TEST_CONFIG=$<CONFIG>"
            "HAMMOND_CROSSOVER_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_crossover_probe>")
        set_tests_properties(python_test_crossover_install PROPERTIES
            TIMEOUT 120 LABELS "crossover;install;offline")
    endif()
endif()

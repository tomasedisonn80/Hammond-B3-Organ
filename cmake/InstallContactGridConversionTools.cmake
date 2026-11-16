# Explicit five-file standard-library contact-grid conversion package. Include after
# InstallHammondTools and test discovery. No native target or build is required.
if(NOT COMMAND hammond_require_relative_install_dir)
    message(FATAL_ERROR "ContactGridConversionTools requires InstallHammondTools.cmake first.")
endif()
hammond_require_relative_install_dir(ContactGridConversionTools CMAKE_INSTALL_DATADIR)
string(REPLACE "\\" "/" _hammond_contact_grid_conversion_datadir "${CMAKE_INSTALL_DATADIR}")
set(_hammond_contact_grid_conversion_package
    "${_hammond_contact_grid_conversion_datadir}/hammond-b3-organ/contact-grid-conversion")
get_filename_component(_hammond_contact_grid_conversion_source "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

# Preserve the source-like relative layout used by the CLI's four-module and
# contract provenance. This separate package does not copy fixtures, the native
# probe, Python bytecode, or any of the original reference component's extras.
set(_hammond_contact_grid_conversion_files
    tools/contact_grid_conversion.py
    tools/convert_contact_grid.py
    tools/contact_switching_io.py
    tools/fractional_contact_reference.py
    docs/CONTACT_GRID_CONVERSION_CONTRACT.md)

set(_hammond_contact_grid_conversion_preflight [=[
    if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
       NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
        message(FATAL_ERROR "ContactGridConversionTools requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
    endif()
    set(_hammond_contact_grid_conversion_source [==[@_hammond_contact_grid_conversion_source@]==])
    set(_hammond_contact_grid_conversion_files [==[@_hammond_contact_grid_conversion_files@]==])
    foreach(_hammond_contact_grid_conversion_relative IN LISTS _hammond_contact_grid_conversion_files)
        set(_hammond_contact_grid_conversion_input "${_hammond_contact_grid_conversion_source}/${_hammond_contact_grid_conversion_relative}")
        if(NOT EXISTS "${_hammond_contact_grid_conversion_input}" OR
           IS_DIRECTORY "${_hammond_contact_grid_conversion_input}" OR
           IS_SYMLINK "${_hammond_contact_grid_conversion_input}")
            message(FATAL_ERROR
                "ContactGridConversionTools missing or invalid required input '${_hammond_contact_grid_conversion_input}'; retain all 5 nonempty nonsymlink source payload files before installing.")
        endif()
        file(SIZE "${_hammond_contact_grid_conversion_input}" _hammond_contact_grid_conversion_size)
        if(_hammond_contact_grid_conversion_size EQUAL 0)
            message(FATAL_ERROR "ContactGridConversionTools required input is empty: '${_hammond_contact_grid_conversion_input}'.")
        endif()
        # A nonsymlink leaf must not conceal a linked directory inside the
        # source root. Trust system ancestors outside that root.
        get_filename_component(_hammond_contact_grid_conversion_parent "${_hammond_contact_grid_conversion_input}" DIRECTORY)
        while(1)
            if(IS_SYMLINK "${_hammond_contact_grid_conversion_parent}" OR
               NOT IS_DIRECTORY "${_hammond_contact_grid_conversion_parent}")
                message(FATAL_ERROR
                    "ContactGridConversionTools source ancestor must be an ordinary directory: '${_hammond_contact_grid_conversion_parent}'.")
            endif()
            if(_hammond_contact_grid_conversion_parent STREQUAL _hammond_contact_grid_conversion_source)
                break()
            endif()
            get_filename_component(_hammond_contact_grid_conversion_next_parent
                "${_hammond_contact_grid_conversion_parent}" DIRECTORY)
            if(_hammond_contact_grid_conversion_next_parent STREQUAL _hammond_contact_grid_conversion_parent)
                break()
            endif()
            set(_hammond_contact_grid_conversion_parent "${_hammond_contact_grid_conversion_next_parent}")
        endwhile()
    endforeach()

    get_filename_component(_hammond_contact_grid_conversion_prefix
        "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}" ABSOLUTE)
    get_filename_component(_hammond_contact_grid_conversion_destination
        "${_hammond_contact_grid_conversion_prefix}/@_hammond_contact_grid_conversion_package@" ABSOLUTE)
    if(EXISTS "${_hammond_contact_grid_conversion_destination}" OR
       IS_SYMLINK "${_hammond_contact_grid_conversion_destination}")
        message(FATAL_ERROR
            "ContactGridConversionTools destination already exists: '${_hammond_contact_grid_conversion_destination}'. Choose a fresh local prefix; existing packages are never replaced or merged.")
    endif()
    # Check all ancestors inside the chosen (possibly DESTDIR-staged) prefix,
    # including the prefix itself, before the first destination write.
    # System ancestors outside the caller's prefix are not inspected.
    get_filename_component(_hammond_contact_grid_conversion_parent
        "${_hammond_contact_grid_conversion_destination}" DIRECTORY)
    while(1)
        if(IS_SYMLINK "${_hammond_contact_grid_conversion_parent}" OR
           (EXISTS "${_hammond_contact_grid_conversion_parent}" AND
            NOT IS_DIRECTORY "${_hammond_contact_grid_conversion_parent}"))
            message(FATAL_ERROR
                "ContactGridConversionTools destination ancestor must be an ordinary directory: '${_hammond_contact_grid_conversion_parent}'.")
        endif()
        if(_hammond_contact_grid_conversion_parent STREQUAL _hammond_contact_grid_conversion_prefix)
            break()
        endif()
        get_filename_component(_hammond_contact_grid_conversion_next_parent
            "${_hammond_contact_grid_conversion_parent}" DIRECTORY)
        if(_hammond_contact_grid_conversion_next_parent STREQUAL _hammond_contact_grid_conversion_parent)
            break()
        endif()
        set(_hammond_contact_grid_conversion_parent "${_hammond_contact_grid_conversion_next_parent}")
    endwhile()
    message(STATUS
        "ContactGridConversionTools preflight passed; copying begins. A later failure can leave a partial new installation; no automatic cleanup is performed.")
]=])
string(CONFIGURE "${_hammond_contact_grid_conversion_preflight}" _hammond_contact_grid_conversion_preflight @ONLY)
install(CODE "${_hammond_contact_grid_conversion_preflight}"
    COMPONENT ContactGridConversionTools EXCLUDE_FROM_ALL)
foreach(_hammond_contact_grid_conversion_relative IN LISTS _hammond_contact_grid_conversion_files)
    get_filename_component(_hammond_contact_grid_conversion_parent "${_hammond_contact_grid_conversion_relative}" DIRECTORY)
    install(FILES "${_hammond_contact_grid_conversion_source}/${_hammond_contact_grid_conversion_relative}"
        DESTINATION "${_hammond_contact_grid_conversion_package}/${_hammond_contact_grid_conversion_parent}"
        COMPONENT ContactGridConversionTools EXCLUDE_FROM_ALL)
endforeach()

if(BUILD_TESTING AND TEST python_test_contact_grid_conversion_install)
    set_property(TEST python_test_contact_grid_conversion_install APPEND PROPERTY ENVIRONMENT
        "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
        "HAMMOND_TEST_CMAKE_GENERATOR=${CMAKE_GENERATOR}"
        "HAMMOND_TEST_CMAKE_MAKE_PROGRAM=${CMAKE_MAKE_PROGRAM}"
        "HAMMOND_TEST_CONFIG=$<CONFIG>")
    set_tests_properties(python_test_contact_grid_conversion_install PROPERTIES
        TIMEOUT 180 LABELS "contact;conversion;install;offline")
endif()

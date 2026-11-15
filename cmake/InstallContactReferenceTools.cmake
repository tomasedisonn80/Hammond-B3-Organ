# Explicit standard-library contact-reference package. Include after
# InstallHammondTools and test discovery. No native target or build is required.
if(NOT COMMAND hammond_require_relative_install_dir)
    message(FATAL_ERROR "ContactReferenceTools requires InstallHammondTools.cmake first.")
endif()
hammond_require_relative_install_dir(ContactReferenceTools CMAKE_INSTALL_DATADIR)
string(REPLACE "\\" "/" _hammond_contact_datadir "${CMAKE_INSTALL_DATADIR}")
set(_hammond_contact_package
    "${_hammond_contact_datadir}/hammond-b3-organ/contact-reference")
get_filename_component(_hammond_contact_source "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

# Retain the source-like layout: the study identifies its package root as the
# parent of tools and reads both frozen contracts there. Enumerate every fixed
# input, rather than accepting arbitrary files from a directory glob.
set(_hammond_contact_files
    tools/fractional_contact_reference.py
    tools/contact_switching_io.py
    tools/contact_switching_reference.py
    tools/contact_switching_oracle.py
    tools/contact_switching_study.py
    tools/make_contact_switching_fixtures.py
    docs/FRACTIONAL_CONTACT_REFERENCE.md
    docs/CONTACT_SWITCHING_VALIDATION.md
    docs/CONTACT_SWITCHING_GUIDE.md
    docs/CONTACT_REFERENCE_INSTALL.md)
foreach(_hammond_contact_recipe IN ITEMS 00 01 02 03 04 05 06 07 08 09 10 11)
    foreach(_hammond_contact_rate IN ITEMS 44100 48000 96000)
        list(APPEND _hammond_contact_files
            "data/contact-switching/reference-v1/F${_hammond_contact_recipe}-${_hammond_contact_rate}-v1.json")
    endforeach()
endforeach()
list(APPEND _hammond_contact_files
    data/contact-switching/reference-v1/manifest.json
    data/contact-switching/reference-v1/probes.json)

set(_hammond_contact_preflight [=[
    if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
       NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
        message(FATAL_ERROR "ContactReferenceTools requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
    endif()
    set(_hammond_contact_source [==[@_hammond_contact_source@]==])
    set(_hammond_contact_files [==[@_hammond_contact_files@]==])
    foreach(_hammond_contact_relative IN LISTS _hammond_contact_files)
        set(_hammond_contact_input "${_hammond_contact_source}/${_hammond_contact_relative}")
        if(NOT EXISTS "${_hammond_contact_input}" OR
           IS_DIRECTORY "${_hammond_contact_input}" OR
           IS_SYMLINK "${_hammond_contact_input}")
            message(FATAL_ERROR
                "ContactReferenceTools missing or invalid required input '${_hammond_contact_input}'; retain all 48 nonempty nonsymlink source payload files before installing.")
        endif()
        file(SIZE "${_hammond_contact_input}" _hammond_contact_size)
        if(_hammond_contact_size EQUAL 0)
            message(FATAL_ERROR "ContactReferenceTools required input is empty: '${_hammond_contact_input}'.")
        endif()
        # A nonsymlink leaf must not conceal a linked directory inside the
        # source root. Trust system ancestors outside that root.
        get_filename_component(_hammond_contact_parent "${_hammond_contact_input}" DIRECTORY)
        while(1)
            if(IS_SYMLINK "${_hammond_contact_parent}" OR
               NOT IS_DIRECTORY "${_hammond_contact_parent}")
                message(FATAL_ERROR
                    "ContactReferenceTools source ancestor must be an ordinary directory: '${_hammond_contact_parent}'.")
            endif()
            if(_hammond_contact_parent STREQUAL _hammond_contact_source)
                break()
            endif()
            get_filename_component(_hammond_contact_next_parent
                "${_hammond_contact_parent}" DIRECTORY)
            if(_hammond_contact_next_parent STREQUAL _hammond_contact_parent)
                break()
            endif()
            set(_hammond_contact_parent "${_hammond_contact_next_parent}")
        endwhile()
    endforeach()

    get_filename_component(_hammond_contact_prefix
        "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}" ABSOLUTE)
    get_filename_component(_hammond_contact_destination
        "${_hammond_contact_prefix}/@_hammond_contact_package@" ABSOLUTE)
    if(EXISTS "${_hammond_contact_destination}" OR
       IS_SYMLINK "${_hammond_contact_destination}")
        message(FATAL_ERROR
            "ContactReferenceTools destination already exists: '${_hammond_contact_destination}'. Choose a fresh local prefix; existing packages are never replaced or merged.")
    endif()
    # Check all ancestors inside the chosen (possibly DESTDIR-staged) prefix,
    # including the prefix itself, before the first destination write.
    # System ancestors outside the caller's prefix are not inspected.
    get_filename_component(_hammond_contact_parent
        "${_hammond_contact_destination}" DIRECTORY)
    while(1)
        if(IS_SYMLINK "${_hammond_contact_parent}" OR
           (EXISTS "${_hammond_contact_parent}" AND
            NOT IS_DIRECTORY "${_hammond_contact_parent}"))
            message(FATAL_ERROR
                "ContactReferenceTools destination ancestor must be an ordinary directory: '${_hammond_contact_parent}'.")
        endif()
        if(_hammond_contact_parent STREQUAL _hammond_contact_prefix)
            break()
        endif()
        get_filename_component(_hammond_contact_next_parent
            "${_hammond_contact_parent}" DIRECTORY)
        if(_hammond_contact_next_parent STREQUAL _hammond_contact_parent)
            break()
        endif()
        set(_hammond_contact_parent "${_hammond_contact_next_parent}")
    endwhile()
    message(STATUS
        "ContactReferenceTools preflight passed; copying begins. A later failure can leave a partial new installation; no automatic cleanup is performed.")
]=])
string(CONFIGURE "${_hammond_contact_preflight}" _hammond_contact_preflight @ONLY)
install(CODE "${_hammond_contact_preflight}"
    COMPONENT ContactReferenceTools EXCLUDE_FROM_ALL)
foreach(_hammond_contact_relative IN LISTS _hammond_contact_files)
    get_filename_component(_hammond_contact_parent "${_hammond_contact_relative}" DIRECTORY)
    install(FILES "${_hammond_contact_source}/${_hammond_contact_relative}"
        DESTINATION "${_hammond_contact_package}/${_hammond_contact_parent}"
        COMPONENT ContactReferenceTools EXCLUDE_FROM_ALL)
endforeach()

if(BUILD_TESTING AND TEST python_test_contact_reference_install)
    set_property(TEST python_test_contact_reference_install APPEND PROPERTY ENVIRONMENT
        "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
        "HAMMOND_TEST_CMAKE_GENERATOR=${CMAKE_GENERATOR}"
        "HAMMOND_TEST_CMAKE_MAKE_PROGRAM=${CMAKE_MAKE_PROGRAM}"
        "HAMMOND_TEST_CONFIG=$<CONFIG>")
    set_tests_properties(python_test_contact_reference_install PROPERTIES
        TIMEOUT 180 LABELS "contact;install;offline")
endif()

# Explicit, copy-only registration preparation and proposed starter data.
# Include after InstallHammondTools: its GNUInstallDirs automatic DATADIR
# tracking and shared relative-directory admission remain the single authority.
if(NOT COMMAND hammond_require_relative_install_dir)
    message(FATAL_ERROR "RegistrationTools requires InstallHammondTools.cmake first.")
endif()
hammond_require_relative_install_dir(RegistrationTools CMAKE_INSTALL_BINDIR)
hammond_require_relative_install_dir(StarterRegistrations CMAKE_INSTALL_DATADIR)
string(REPLACE "\\" "/" _hammond_registration_bindir "${CMAKE_INSTALL_BINDIR}")
string(REPLACE "\\" "/" _hammond_registration_datadir "${CMAKE_INSTALL_DATADIR}")
get_filename_component(_hammond_registration_source "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(_hammond_registration_guide "${_hammond_registration_datadir}/hammond/REGISTRATION_GUIDE.md")
set(_hammond_starter_package "${_hammond_registration_datadir}/hammond/registrations/starter-v1")

# These helpers run only inside the selected component's read-only preflight.
# Neither component runs a target, generator, parser, Python interpreter or tool.
set(_hammond_registration_common_preflight [=[
    if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
       NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
        message(FATAL_ERROR "${_hammond_registration_component} requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
    endif()
    function(_hammond_registration_require_input input root)
        if(NOT EXISTS "${input}" OR IS_DIRECTORY "${input}" OR IS_SYMLINK "${input}")
            message(FATAL_ERROR "${_hammond_registration_component} missing or invalid required input '${input}'; retain every nonempty nonsymlink component input before installing.")
        endif()
        file(SIZE "${input}" input_size)
        if(input_size EQUAL 0)
            message(FATAL_ERROR "${_hammond_registration_component} required input is empty: '${input}'.")
        endif()
        get_filename_component(parent "${input}" DIRECTORY)
        while(1)
            if(IS_SYMLINK "${parent}" OR NOT IS_DIRECTORY "${parent}")
                message(FATAL_ERROR "${_hammond_registration_component} source ancestor must be an ordinary directory: '${parent}'.")
            endif()
            if(parent STREQUAL root)
                break()
            endif()
            get_filename_component(next_parent "${parent}" DIRECTORY)
            if(next_parent STREQUAL parent)
                break()
            endif()
            set(parent "${next_parent}")
        endwhile()
        # Read every admitted input before copying any of them. This detects
        # unreadable regular files without parsing or executing their contents.
        file(SHA256 "${input}" input_readability_sha256)
    endfunction()
    get_filename_component(_hammond_registration_prefix "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}" ABSOLUTE)
    function(_hammond_registration_require_destination destination)
        if(EXISTS "${destination}" OR IS_SYMLINK "${destination}")
            message(FATAL_ERROR "${_hammond_registration_component} destination already exists: '${destination}'. Choose a fresh destination; existing files or packages are never replaced or merged.")
        endif()
        # Inspect the effective prefix itself and all ancestors inside it. Trust
        # system ancestors outside the caller's prefix, as other components do.
        get_filename_component(parent "${destination}" DIRECTORY)
        while(1)
            if(IS_SYMLINK "${parent}" OR (EXISTS "${parent}" AND NOT IS_DIRECTORY "${parent}"))
                message(FATAL_ERROR "${_hammond_registration_component} destination ancestor must be an ordinary directory: '${parent}'.")
            endif()
            if(parent STREQUAL _hammond_registration_prefix)
                break()
            endif()
            get_filename_component(next_parent "${parent}" DIRECTORY)
            if(next_parent STREQUAL parent)
                break()
            endif()
            set(parent "${next_parent}")
        endwhile()
    endfunction()
]=])

if(TARGET hammond_registration)
    # Target-dependent rules disappear for unknown multi-config names. Reject
    # such a name before those rules, so a guide-only success is impossible.
    get_property(_hammond_registration_multi_config GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(_hammond_registration_multi_config)
        set(_hammond_registration_configurations "${CMAKE_CONFIGURATION_TYPES}")
        list(TRANSFORM _hammond_registration_configurations TOUPPER)
        set(_hammond_registration_configuration_guard [=[
            string(TOUPPER "${CMAKE_INSTALL_CONFIG_NAME}" selected_configuration)
            set(allowed_configurations [==[@_hammond_registration_configurations@]==])
            list(FIND allowed_configurations "${selected_configuration}" configuration_index)
            if(configuration_index EQUAL -1)
                message(FATAL_ERROR "RegistrationTools unknown configuration '${CMAKE_INSTALL_CONFIG_NAME}'; select a configured name: @_hammond_registration_configurations@.")
            endif()
        ]=])
        string(CONFIGURE "${_hammond_registration_configuration_guard}"
            _hammond_registration_configuration_guard @ONLY)
        install(CODE "${_hammond_registration_configuration_guard}"
            COMPONENT RegistrationTools EXCLUDE_FROM_ALL)
    endif()
    set(_hammond_registration_preflight [=[
        set(_hammond_registration_component RegistrationTools)
        @_hammond_registration_common_preflight@
        _hammond_registration_require_input("$<TARGET_FILE:hammond_registration>" [==[@PROJECT_BINARY_DIR@]==])
        _hammond_registration_require_input([==[@_hammond_registration_source@/docs/REGISTRATION_GUIDE.md]==]
            [==[@_hammond_registration_source@]==])
        get_filename_component(binary_destination
            "${_hammond_registration_prefix}/@_hammond_registration_bindir@/$<TARGET_FILE_NAME:hammond_registration>" ABSOLUTE)
        get_filename_component(guide_destination
            "${_hammond_registration_prefix}/@_hammond_registration_guide@" ABSOLUTE)
        # Each destination is a file; neither can also contain the other.
        foreach(first binary_destination guide_destination)
            foreach(second binary_destination guide_destination)
                if(NOT first STREQUAL second)
                    file(RELATIVE_PATH relative "${${first}}" "${${second}}")
                    if(NOT IS_ABSOLUTE "${relative}" AND NOT relative MATCHES "^\\.\\.(/|$)")
                        message(FATAL_ERROR "RegistrationTools executable and guide destinations conflict.")
                    endif()
                endif()
            endforeach()
        endforeach()
        _hammond_registration_require_destination("${binary_destination}")
        _hammond_registration_require_destination("${guide_destination}")
        message(STATUS "RegistrationTools preflight passed; copying begins. A later failure can leave a partial new installation; no automatic cleanup is performed.")
    ]=])
    string(CONFIGURE "${_hammond_registration_preflight}" _hammond_registration_preflight @ONLY)
    install(CODE "${_hammond_registration_preflight}" COMPONENT RegistrationTools EXCLUDE_FROM_ALL)
    # PROGRAMS copies exact bytes even with --strip; unlike TARGETS, it performs
    # no RPATH rewriting or subprocess execution. System runtime libraries are
    # not bundled and still need to be available on the destination platform.
    install(PROGRAMS "$<TARGET_FILE:hammond_registration>"
        DESTINATION "${_hammond_registration_bindir}" COMPONENT RegistrationTools EXCLUDE_FROM_ALL)
    install(FILES "${_hammond_registration_source}/docs/REGISTRATION_GUIDE.md"
        DESTINATION "${_hammond_registration_datadir}/hammond"
        COMPONENT RegistrationTools EXCLUDE_FROM_ALL)
endif()

# Literal inventory from starter-registration-pack-v1. Do not glob the source
# directory or install it recursively: provenance must stay outside flat entries.
set(_hammond_starter_entries
    "01 Quiet Foundation.b3registration"
    "01 Quiet Foundation.b3performance"
    "02 Warm Comp.b3registration"
    "02 Warm Comp.b3performance"
    "03 Clear Lead.b3registration"
    "03 Clear Lead.b3performance"
    "04 Reed Edge.b3registration"
    "04 Reed Edge.b3performance"
    "05 Bright Ensemble.b3registration"
    "05 Bright Ensemble.b3performance"
    "06 High Shimmer.b3registration"
    "06 High Shimmer.b3performance"
    "07 Percussive Pair.b3registration"
    "07 Percussive Pair.b3performance"
    "08 Slow Accent.b3registration"
    "08 Slow Accent.b3performance"
    "09 Split Dialogue.b3registration"
    "09 Split Dialogue.b3performance"
    "10 Pedal Study.b3registration"
    "10 Pedal Study.b3performance"
    "11 Fixed Contrast.b3registration"
    "11 Fixed Contrast.b3performance"
    "12 Manual Return.b3registration"
    "12 Manual Return.b3performance")
set(_hammond_starter_source "${_hammond_registration_source}/data/registrations/starter-v1")
set(_hammond_starter_preflight [=[
    set(_hammond_registration_component StarterRegistrations)
    @_hammond_registration_common_preflight@
    set(entries [==[@_hammond_starter_entries@]==])
    foreach(entry IN LISTS entries)
        _hammond_registration_require_input("@_hammond_starter_source@/entries/${entry}"
            [==[@_hammond_registration_source@]==])
    endforeach()
    foreach(metadata README.md recipes.json)
        _hammond_registration_require_input("@_hammond_starter_source@/${metadata}"
            [==[@_hammond_registration_source@]==])
    endforeach()
    get_filename_component(destination "${_hammond_registration_prefix}/@_hammond_starter_package@" ABSOLUTE)
    _hammond_registration_require_destination("${destination}")
    message(STATUS "StarterRegistrations preflight passed; copying begins. A later failure can leave a partial new installation; no automatic cleanup is performed.")
]=])
string(CONFIGURE "${_hammond_starter_preflight}" _hammond_starter_preflight @ONLY)
install(CODE "${_hammond_starter_preflight}" COMPONENT StarterRegistrations EXCLUDE_FROM_ALL)
foreach(_hammond_starter_entry IN LISTS _hammond_starter_entries)
    install(FILES "${_hammond_starter_source}/entries/${_hammond_starter_entry}"
        DESTINATION "${_hammond_starter_package}/entries" COMPONENT StarterRegistrations EXCLUDE_FROM_ALL)
endforeach()
install(FILES "${_hammond_starter_source}/README.md" "${_hammond_starter_source}/recipes.json"
    DESTINATION "${_hammond_starter_package}" COMPONENT StarterRegistrations EXCLUDE_FROM_ALL)

# Component-scoped local installation. Include after all targets/tests exist.
# Nothing here builds an input, downloads dependencies, or registers a plugin.
function(hammond_require_relative_install_dir component variable)
    string(REPLACE "\\" "/" normalized "${${variable}}")
    if(IS_ABSOLUTE "${normalized}" OR normalized MATCHES "^[A-Za-z]:" OR
       normalized MATCHES "(^|/)\\.\\.(/|$)" OR normalized MATCHES ";" OR
       normalized STREQUAL "")
        message(FATAL_ERROR
            "${component} requires a nonempty relative ${variable} without parent traversal or list separators.")
    endif()
endfunction()

# GNUInstallDirs substitutes a default for an explicitly empty DATADIR. Reject
# caller-supplied invalid values before that substitution as well as afterwards.
if(TARGET hammond_render)
    foreach(_hammond_directory CMAKE_INSTALL_BINDIR CMAKE_INSTALL_DATADIR)
        if(DEFINED ${_hammond_directory})
            hammond_require_relative_install_dir(OfflineTools ${_hammond_directory})
        endif()
    endforeach()
    # Recent GNUInstallDirs versions may cache an empty DATADIR as a signal to
    # derive it from DATAROOTDIR. Materialize our automatic default below so a
    # second configure can still distinguish it from a caller's explicit empty
    # value, which the relocation contract rejects. Keep automatic defaults
    # following DATAROOTDIR; preserve an independently chosen custom DATADIR.
    set(_hammond_automatic_datadir FALSE)
    if(NOT DEFINED CMAKE_INSTALL_DATADIR OR
       (DEFINED _HAMMOND_LAST_AUTOMATIC_DATADIR AND
        CMAKE_INSTALL_DATADIR STREQUAL _HAMMOND_LAST_AUTOMATIC_DATADIR))
        set(_hammond_automatic_datadir TRUE)
        unset(CMAKE_INSTALL_DATADIR)
        unset(CMAKE_INSTALL_DATADIR CACHE)
    endif()
endif()
if(HAMMOND_BUILD_VST3 AND TARGET HammondB3 AND DEFINED CMAKE_INSTALL_LIBDIR)
    hammond_require_relative_install_dir(NativeVST3 CMAKE_INSTALL_LIBDIR)
endif()
include(GNUInstallDirs)

if(TARGET hammond_render)
    hammond_require_relative_install_dir(OfflineTools CMAKE_INSTALL_BINDIR)
    hammond_require_relative_install_dir(OfflineTools CMAKE_INSTALL_DATADIR)
    if(_hammond_automatic_datadir)
        set(CMAKE_INSTALL_DATADIR "${CMAKE_INSTALL_DATADIR}" CACHE PATH
            "Read-only architecture-independent data (DATAROOTDIR)" FORCE)
        set(_HAMMOND_LAST_AUTOMATIC_DATADIR "${CMAKE_INSTALL_DATADIR}" CACHE INTERNAL
            "Last materialized automatic data directory" FORCE)
    else()
        unset(_HAMMOND_LAST_AUTOMATIC_DATADIR CACHE)
    endif()
    set(_hammond_fixture_files
        "${PROJECT_SOURCE_DIR}/examples/fixtures/catalog-v1.json"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/a4-fundamental-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/two-manual-changes-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/low-fold-coherent-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/held-bank-cancel-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/high-fold-coherent-v1.events")
    set(_hammond_console_fixture_files
        "${PROJECT_SOURCE_DIR}/examples/fixtures/console/console-catalog-v1.json"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/console/console-travel-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/console/console-percussion-legato-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/console/console-routing-mask-v1.events")
    set(_hammond_pedal_fixture_files
        "${PROJECT_SOURCE_DIR}/examples/fixtures/pedals/pedal-catalog-v1.json"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/pedals/pedal-mixtures-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/pedals/pedal-shared-source-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/pedals/pedal-held-routing-v1.events"
        "${PROJECT_SOURCE_DIR}/examples/fixtures/pedals/pedal-phrase-v1.events")
    set(_hammond_offline_preflight [=[
        if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
           NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
            message(FATAL_ERROR "OfflineTools requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
        endif()
        set(_hammond_inputs
            "$<TARGET_FILE:hammond_render>"
            "$<TARGET_FILE:hammond_model_info>"
            "$<TARGET_FILE:hammond_parameter_info>"
            "$<TARGET_FILE:hammond_console_trace>"
            "$<TARGET_FILE:hammond_pedal_trace>"
            "@HAMMOND_COMPILED_PROFILE@"
            "@PROJECT_SOURCE_DIR@/tools/plot_console_trace.py"
            "@PROJECT_SOURCE_DIR@/tools/plot_pedal_trace.py"
            "@_hammond_fixture_files@"
            "@_hammond_console_fixture_files@"
            "@_hammond_pedal_fixture_files@")
        foreach(_hammond_input IN LISTS _hammond_inputs)
            if(NOT EXISTS "${_hammond_input}" OR IS_DIRECTORY "${_hammond_input}")
                message(FATAL_ERROR
                    "OfflineTools missing required file '${_hammond_input}'. Build all five executable targets (hammond_render, hammond_model_info, hammond_parameter_info, hammond_console_trace, hammond_pedal_trace), nominal.b3p and retain both source plot scripts/catalogs/scores for the selected configuration before installing.")
            endif()
        endforeach()
    ]=])
    string(CONFIGURE "${_hammond_offline_preflight}" _hammond_offline_preflight @ONLY)
    # Preflight every input before the first destination file is touched.
    install(CODE "${_hammond_offline_preflight}" COMPONENT OfflineTools)
    install(TARGETS hammond_render hammond_model_info hammond_parameter_info
                   hammond_console_trace hammond_pedal_trace
        RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT OfflineTools)
    install(PROGRAMS "${PROJECT_SOURCE_DIR}/tools/plot_console_trace.py"
                     "${PROJECT_SOURCE_DIR}/tools/plot_pedal_trace.py"
        DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT OfflineTools)
    install(FILES "${HAMMOND_COMPILED_PROFILE}"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ" COMPONENT OfflineTools)
    install(FILES ${_hammond_fixture_files}
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/fixtures" COMPONENT OfflineTools)
    install(FILES ${_hammond_console_fixture_files}
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/fixtures/console" COMPONENT OfflineTools)
    install(FILES ${_hammond_pedal_fixture_files}
        DESTINATION "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/fixtures/pedals" COMPONENT OfflineTools)
    if(BUILD_TESTING AND TEST python_test_install)
        set_property(TEST python_test_install APPEND PROPERTY ENVIRONMENT
            "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}"
            "HAMMOND_TEST_BUILD_DIR=${CMAKE_CURRENT_BINARY_DIR}"
            "HAMMOND_TEST_CONFIG=$<CONFIG>"
            "HAMMOND_MODEL_INFO_EXECUTABLE=$<TARGET_FILE:hammond_model_info>"
            "HAMMOND_PARAMETER_INFO_EXECUTABLE=$<TARGET_FILE:hammond_parameter_info>"
            "HAMMOND_PEDAL_TRACE_EXECUTABLE=$<TARGET_FILE:hammond_pedal_trace>"
            "HAMMOND_INSTALL_BINDIR=${CMAKE_INSTALL_BINDIR}"
            "HAMMOND_INSTALL_DATADIR=${CMAKE_INSTALL_DATADIR}")
        set_tests_properties(python_test_install PROPERTIES TIMEOUT 180)
    endif()
endif()

if(HAMMOND_BUILD_VST3 AND TARGET HammondB3)
    hammond_require_relative_install_dir(NativeVST3 CMAKE_INSTALL_LIBDIR)
    # The pinned SDK owns the platform-specific bundle layout and configuration.
    get_target_property(_hammond_native_bundle HammondB3 SMTG_PLUGIN_PACKAGE_PATH)
    if(NOT _hammond_native_bundle)
        message(FATAL_ERROR "NativeVST3 requires the SDK's HammondB3 bundle path.")
    endif()
    set(_hammond_native_preflight [=[
        if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
           NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
            message(FATAL_ERROR "NativeVST3 requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
        endif()
        set(_hammond_bundle "@_hammond_native_bundle@")
        set(_hammond_binary "$<TARGET_FILE:HammondB3>")
        if(NOT IS_DIRECTORY "${_hammond_bundle}" OR IS_SYMLINK "${_hammond_bundle}")
            message(FATAL_ERROR "NativeVST3 requires a complete built HammondB3.vst3 bundle; build HammondB3 for the selected configuration first.")
        endif()
        file(RELATIVE_PATH _hammond_binary_relative "${_hammond_bundle}" "${_hammond_binary}")
        if(IS_ABSOLUTE "${_hammond_binary_relative}" OR
           _hammond_binary_relative MATCHES "^\\.\\.(/|$)")
            message(FATAL_ERROR "NativeVST3 module must be inside its SDK-generated bundle.")
        endif()
        set(_hammond_required
            "${_hammond_binary}"
            "${_hammond_bundle}/Contents/Resources/moduleinfo.json"
            "${_hammond_bundle}/Contents/Resources/VST3_SDK_LICENSE.txt"
            "${_hammond_bundle}/Contents/Resources/THIRD_PARTY_NOTICES.md")
        if("@APPLE@")
            list(APPEND _hammond_required "${_hammond_bundle}/Contents/Info.plist")
        endif()
        foreach(_hammond_input IN LISTS _hammond_required)
            if(NOT EXISTS "${_hammond_input}" OR IS_DIRECTORY "${_hammond_input}")
                message(FATAL_ERROR "NativeVST3 missing required bundle file '${_hammond_input}'; rebuild HammondB3 before installing.")
            endif()
            file(SIZE "${_hammond_input}" _hammond_input_size)
            if(_hammond_input_size EQUAL 0)
                message(FATAL_ERROR "NativeVST3 bundle file is empty: '${_hammond_input}'.")
            endif()
        endforeach()
        file(GLOB_RECURSE _hammond_payload LIST_DIRECTORIES true "${_hammond_bundle}/*")
        foreach(_hammond_entry IN LISTS _hammond_payload)
            if(IS_SYMLINK "${_hammond_entry}")
                message(FATAL_ERROR "NativeVST3 requires a self-contained bundle without symlinks: '${_hammond_entry}'.")
            endif()
        endforeach()
        get_filename_component(_hammond_bundle_name "${_hammond_bundle}" NAME)
        set(_hammond_destination "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/@CMAKE_INSTALL_LIBDIR@/vst3/${_hammond_bundle_name}")
        if(EXISTS "${_hammond_destination}" OR IS_SYMLINK "${_hammond_destination}")
            message(FATAL_ERROR "NativeVST3 destination bundle already exists: '${_hammond_destination}'. Choose a fresh local prefix; existing bundles are never merged or replaced.")
        endif()
    ]=])
    string(CONFIGURE "${_hammond_native_preflight}" _hammond_native_preflight @ONLY)
    # Explicit component only: ordinary offline installs never stage a plugin.
    install(CODE "${_hammond_native_preflight}" COMPONENT NativeVST3 EXCLUDE_FROM_ALL)
    install(DIRECTORY "${_hammond_native_bundle}"
        DESTINATION "${CMAKE_INSTALL_LIBDIR}/vst3"
        USE_SOURCE_PERMISSIONS COMPONENT NativeVST3 EXCLUDE_FROM_ALL)
endif()
